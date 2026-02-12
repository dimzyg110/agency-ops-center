# GLASS Code Review & Fix Plan

## Executive Summary

GLASS is a well-architected cannabis intelligence platform with solid domain modeling, but it is currently broken in production due to three cascading failures: (1) a Clerk auth redirect loop on the frontend that prevents any user from reaching the dashboard, (2) a backend auth plugin that requires `operator_id` in JWT claims which new Clerk users never have, making all API calls return 401 even if the redirect loop is fixed, and (3) zero data in the database because the scraper and intelligence services were never deployed. The frontend code is polished and production-ready pending auth fixes; the backend is robust but has a critical schema mismatch between the API service (which uses a `glass` Postgres schema prefix) and the scraper/intelligence services (which use the default `public` schema). Until the auth chain and schema alignment are fixed, no user can access any functionality.

---

## Critical Issues (Must Fix Before Launch)

### Issue 1: Auth Redirect Loop — Race Condition Between Clerk Loading and AuthGuard

**File(s):** `apps/web/src/App.tsx`, `apps/web/src/components/AuthGuard.tsx`, `apps/web/src/main.tsx`

**Problem:** After Clerk signup/signin completes, users get trapped in a redirect loop between `/` and `/login`. The `App` component calls `useAuth()` at the top level and reads `isSignedIn` to decide whether to show `/login` or redirect away from it. Simultaneously, `AuthGuard` does the same check. The problem: `useAuth()` returns `isSignedIn = false` briefly during Clerk's session hydration even after a successful sign-in. During that window:

1. User completes Clerk signin, gets redirected to `/`
2. `AuthGuard` on `/` sees `isLoaded = true, isSignedIn = false` (session still hydrating)
3. `AuthGuard` redirects to `/login`
4. `/login` route checks `isSignedIn` — still `false` — renders sign-in page
5. Clerk finishes hydration, `isSignedIn` flips to `true`
6. `/login` route's `isSignedIn` check redirects to `/`
7. GOTO step 2

**Root Cause:** The `AuthGuard` correctly checks `isLoaded` before acting, but `isLoaded` becomes `true` before the session token is fully available. Clerk's `isLoaded` means "Clerk.js has initialized," not "the session is fully established." After a fresh sign-in, there's a ~100-500ms gap where `isLoaded = true` but `isSignedIn = false`.

The `App` component also reads `isSignedIn` directly (line: `const { isSignedIn } = useAuth()`) to guard `/login` and `/signup` routes, creating a second redirect trigger during the same race window.

Additionally, `redirectUrl="/"` on `<SignIn>` and `<SignUp>` is a deprecated Clerk prop. The current Clerk API uses `afterSignInUrl` / `afterSignUpUrl` or `forceRedirectUrl`.

**Fix:**

```tsx
// AuthGuard.tsx — BEFORE
export function AuthGuard({ children }: AuthGuardProps) {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return (/* loading spinner */);
  }

  if (!isSignedIn) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// AuthGuard.tsx — AFTER
export function AuthGuard({ children }: AuthGuardProps) {
  const { isLoaded, isSignedIn } = useAuth();
  const { session } = useSession(); // from @clerk/clerk-react

  // Wait for BOTH Clerk to load AND session to be established
  // After sign-in, isLoaded=true but session may still be null briefly
  if (!isLoaded || (isLoaded && isSignedIn === undefined)) {
    return (/* loading spinner */);
  }

  if (!isSignedIn) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
```

Better yet, replace `AuthGuard` entirely with Clerk's built-in components:

```tsx
// App.tsx — Use Clerk's own components to avoid the race condition
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react';

function ProtectedRoute({ children }: { children: ReactNode }) {
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut><RedirectToSignIn /></SignedOut>
    </>
  );
}
```

Also fix the deprecated props:
```tsx
// BEFORE
<SignIn redirectUrl="/" signUpUrl="/signup" ... />
<SignUp redirectUrl="/" signInUrl="/login" ... />

// AFTER  
<SignIn afterSignInUrl="/" signUpUrl="/signup" ... />
<SignUp afterSignUpUrl="/" signInUrl="/login" ... />
```

And remove the premature `isSignedIn` check in `App`:
```tsx
// BEFORE — App component top level
const { isSignedIn } = useAuth();
// ...
<Route path="/login" element={isSignedIn ? <Navigate to="/" replace /> : <GlassSignIn />} />

// AFTER — Let Clerk handle it, or add isLoaded guard
const { isLoaded, isSignedIn } = useAuth();
// Only redirect if we're SURE the user is signed in
<Route path="/login" element={isLoaded && isSignedIn ? <Navigate to="/" replace /> : <GlassSignIn />} />
```

**Priority:** P0 — Blocks all users from accessing the app.

---

### Issue 2: Backend Auth Requires `operator_id` in JWT Claims — New Clerk Users Don't Have It

**File(s):** `services/api/src/plugins/auth.ts`

**Problem:** The `buildJwtPayloadFromClerkAuth()` function on lines 63-92 searches for `operator_id` in multiple claim locations (`sessionClaims.operator_id`, `metadata.operator_id`, `public_metadata.operator_id`, `unsafe_metadata.operator_id`). If it doesn't find one, it returns `null`, which causes the `authenticate` decorator to fall through to JWT verification (which also fails for Clerk tokens), resulting in a 401.

New Clerk users have **no** operator_id in their metadata because:
1. User signs up via Clerk (client-side)
2. Clerk creates the user record in its own system
3. No webhook or server-side process sets `operator_id` in Clerk metadata
4. User's first API call fails with 401

**Root Cause:** The architecture assumes a parallel registration flow: Clerk handles identity, the GLASS API handles operator provisioning, and `operator_id` gets synced into Clerk metadata. But no such sync mechanism exists. The `/auth/signup` route creates an operator and user in the GLASS DB with its own JWT flow, but users signing up via the Clerk UI widget bypass this entirely.

**Fix (multi-step):**

**Option A: Auto-provisioning (recommended for MVP)**

Add a "first-login" flow: if Clerk auth succeeds but no `operator_id` is found, create a pending operator + user record and set the metadata via Clerk's backend API.

```typescript
// auth.ts — modify authenticate decorator
fastify.decorate('authenticate', async (request: FastifyRequest, reply: FastifyReply) => {
  try {
    const clerkAuth = getAuth(request, { acceptsToken: 'any' });
    const clerkPayload = buildJwtPayloadFromClerkAuth(clerkAuth);

    if (clerkPayload) {
      request.jwtUser = clerkPayload;
      request.auth = clerkPayload;
      return;
    }

    // Clerk auth succeeded (userId present) but no operator_id
    if (isRecord(clerkAuth) && typeof clerkAuth.userId === 'string') {
      // Auto-provision: look up or create operator for this Clerk user
      const operatorId = await autoProvisionOperator(clerkAuth.userId, clerkAuth);
      if (operatorId) {
        request.jwtUser = {
          sub: clerkAuth.userId,
          operator_id: operatorId,
          role: 'owner',
          iat: Math.floor(Date.now() / 1000),
          exp: Math.floor(Date.now() / 1000) + 900,
        };
        request.auth = request.jwtUser;
        return;
      }
    }
  } catch (err) {
    request.log.debug({ err }, 'Clerk auth parse failed');
  }

  // ... existing JWT fallback ...
});
```

**Option B: Clerk webhook + onboarding page**

1. Set up a Clerk webhook (`user.created`) that creates a pending operator record and updates Clerk `publicMetadata` with `operator_id`.
2. Add an `/onboarding` page in the frontend for new users to provide their license number, city, etc.
3. `AuthGuard` checks for `operator_id` — if missing, redirects to `/onboarding` instead of the dashboard.

**Priority:** P0 — Even if the frontend redirect loop is fixed, all API calls will 401 without this.

---

### Issue 3: Database Schema Mismatch — API Uses `glass` Schema, Scrapers/Intelligence Use `public`

**File(s):**
- `services/api/src/db/schema.ts` — uses `pgSchema('glass')` → tables are `glass.operators`, `glass.prices`, etc.
- `services/scrape/src/db.ts` — uses `pgTable()` → tables are `public.sources`, `public.products`, etc.
- `services/intelligence/src/db.ts` — uses `pgTable()` → tables are `public.threats`, `public.alerts`, etc.
- `infra/schema.sql` — creates tables in `public` schema (no `CREATE SCHEMA glass`)
- `services/scrape/src/registry.ts` — raw SQL queries reference `sources` without schema prefix

**Problem:** The API service defines all tables under a `glass` Postgres schema via `pgSchema('glass')`, but:
1. The `infra/schema.sql` DDL creates all tables in the `public` schema
2. The scraper service defines its own Drizzle schema using `pgTable()` (public schema)
3. The intelligence service does the same
4. Raw SQL in the scraper's `registry.ts` references unqualified table names

This means if the API runs migrations, tables land in `glass.*`. If `schema.sql` is used, tables land in `public.*`. The scraper would write to `public.prices` while the API reads from `glass.prices`. Data is invisible across services.

**Root Cause:** The API was written with a namespaced schema pattern, but the other services and the DDL were written without it. Nobody coordinated the schema namespace.

**Fix:** Standardize on ONE approach. The simplest fix is to remove the `glass` schema prefix from the API service since the DDL and other services all use `public`:

```typescript
// services/api/src/db/schema.ts — BEFORE
const glassSchema = pgSchema('glass');
export const operators = glassSchema.table('operators', { ... });

// services/api/src/db/schema.ts — AFTER
export const operators = pgTable('operators', { ... });
```

Change every `glassSchema.table(...)` call to `pgTable(...)` and remove the `pgSchema` import.

Alternatively, update `schema.sql` to use `CREATE SCHEMA IF NOT EXISTS glass;` and prefix all table creation, and update the scraper/intelligence Drizzle schemas to use `pgSchema('glass')`. This is more work and more error-prone.

**Priority:** P0 — Data written by scrapers will be invisible to the API (and vice versa).

---

### Issue 4: Missing `name` Field in Profile Response — Frontend Expects `user.name`

**File(s):** `services/api/src/routes/profile.ts`, `apps/web/src/types/index.ts`, `apps/web/src/layouts/DashboardLayout.tsx`

**Problem:** The frontend `Profile` type expects `user.name` (a string), and `DashboardLayout` renders `profile?.user?.name || 'User'`. But the profile route returns `{ user: { id, email, role }, operator: {...} }` — no `name` field. The users table has no `name` column either.

**Root Cause:** The users table schema only has `id, email, password_hash, operator_id, role`. There's no `name` column. The frontend type definition includes `name` in the `User` type, but it was never added to the database or API.

**Fix:**

1. Add `name` column to users table: `ALTER TABLE users ADD COLUMN name VARCHAR(255);`
2. Update Drizzle schema: add `name: varchar('name', { length: 255 })` to the users table
3. Update profile route to include the name:
```typescript
const user = {
  id: request.auth.sub,
  name: operatorUser?.name ?? request.auth.email?.split('@')[0] ?? 'User',
  email: request.auth.email ?? operatorUser?.email ?? '',
  role: request.auth.role ?? operatorUser?.role ?? 'viewer',
};
```

For Clerk-authenticated users, you can pull the name from Clerk's session claims (`first_name`, `last_name`).

**Priority:** P1 — UI renders "User" instead of actual name; cosmetic but affects user experience.

---

### Issue 5: Sidebar Logout Button Doesn't Use Clerk SignOut

**File(s):** `apps/web/src/components/Sidebar.tsx`

**Problem:** The logout button does `window.location.href = '/login'` — a hard redirect that doesn't sign the user out of Clerk. The user's Clerk session persists, so:
1. User clicks "Sign Out"
2. Page navigates to `/login`
3. Clerk still has an active session, so `isSignedIn = true`
4. The login route redirects back to `/`
5. User can never sign out

**Root Cause:** The logout handler bypasses Clerk's sign-out flow.

**Fix:**
```tsx
import { useClerk } from '@clerk/clerk-react';

// Inside Sidebar component:
const { signOut } = useClerk();

// Replace the onClick handler:
<button
  onClick={() => signOut({ redirectUrl: '/login' })}
  className="..."
>
  <LogOut size={18} />
  Sign Out
</button>
```

**Priority:** P1 — Users cannot sign out.

---

### Issue 6: `ApiAuthSync` Token Caching Creates Stale Token Bug

**File(s):** `apps/web/src/main.tsx`, `apps/web/src/api/client.ts`

**Problem:** `ApiAuthSync` calls `api.setToken(token)` with the initial token, and `api.setTokenProvider(() => getToken())` for future refreshes. But the `request()` method in `client.ts` checks `this.token` first (line: `let authToken = this.token`), and only falls back to the provider if `this.token` is null. Since `syncToken` sets `this.token` eagerly, the token provider is rarely called. After 15 minutes (JWT expiry), the cached token expires, requests fail with 401, and the token provider is finally called, but only once — then the stale pattern repeats.

**Root Cause:** The two-layer token strategy (cached + provider) has a design flaw: once a token is set, it's never refreshed until it's explicitly nulled or a 401 response occurs.

**Fix:** Always use the token provider, or add 401 retry logic:

```typescript
// client.ts — request method
private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  // Always get fresh token from provider
  let authToken: string | null = null;
  if (this.tokenProvider) {
    authToken = await this.tokenProvider();
  } else {
    authToken = this.token;
  }
  // ... rest of request
}
```

Or add automatic retry on 401:
```typescript
if (response.status === 401 && this.tokenProvider) {
  // Token expired, get a fresh one
  const freshToken = await this.tokenProvider();
  this.token = freshToken;
  // Retry the request once
  headers['Authorization'] = `Bearer ${freshToken}`;
  const retryResponse = await fetch(url, { ...options, headers });
  if (!retryResponse.ok) throw new Error(`HTTP ${retryResponse.status}`);
  return retryResponse.json();
}
```

**Priority:** P1 — API calls will silently fail after 15 minutes of user activity.

---

### Issue 7: Threat Feed Summary Missing `low` Count

**File(s):** `services/api/src/routes/threats.ts` (line ~100)

**Problem:** The `/threats/feed` endpoint constructs its summary object manually but omits the `low` severity count:
```typescript
const summary = {
  critical: threats.filter(t => t.severity === 'critical').length,
  high: threats.filter(t => t.severity === 'high').length,
  medium: threats.filter(t => t.severity === 'medium').length,
  total: threats.length,
};
```

The frontend `ThreatSummary` type and `ThreatRadar.tsx` page expect `summary.low` to exist.

**Root Cause:** Simple omission during implementation.

**Fix:** Add `low: threats.filter(t => t.severity === 'low').length,` to the summary object.

**Priority:** P2 — Frontend shows 0 for low severity count instead of actual count.

---

### Issue 8: `operator_id` Bug in Operators Route Resource Check

**File(s):** `services/api/src/plugins/auth.ts` (line ~114)

**Problem:** In the `requireOperator` decorator, the `'operators'` resource case reads:
```typescript
case 'operators': {
  const [row] = await db.select({ operator_id: schema.operators.id })
    .from(schema.operators)
    .where(eq(schema.operators.id, resourceId))
    .limit(1);
  if (!row) { ... }
  targetOperatorId = row.operator_id; // This IS the operator ID, comparison is correct
  break;
}
```
This selects `schema.operators.id` aliased as `operator_id`, then compares it to `jwtOperatorId`. Since this checks "does the operator in the URL match the JWT operator", this is actually correct. No bug here — but the alias naming is confusing. Minor code clarity issue.

**Priority:** P3 — Code clarity only, not a functional bug.

---

### Issue 9: Recommendations Route Imports Non-Existent Module

**File(s):** `services/api/src/routes/recommendations.ts`

**Problem:** Line 5 imports `import { generateRecommendations } from '../engine/generator.js';`. While the file `engine/generator.ts` exists, it was not included in the review files. If this module has unresolved dependencies or doesn't export `generateRecommendations`, the API will crash when the recommendations route is loaded.

**Root Cause:** The engine modules (generator.ts, rules.ts, elasticity.ts) were built but may not be fully connected.

**Fix:** Verify that `engine/generator.ts` exports a `generateRecommendations(operatorId: string)` function. If not, stub it:
```typescript
export async function generateRecommendations(operatorId: string) {
  return { generated: 0, skipped: 0 };
}
```

Similarly, `routes/margin-rules.ts` imports `import { evaluateRules } from '../engine/rules.js';`.

**Priority:** P1 — Could crash the API server at startup.

---

### Issue 10: CORS Configuration — Single Origin String Instead of Array

**File(s):** `services/api/src/index.ts`

**Problem:** `CORS_ORIGIN` is set as a single string (`http://localhost:5173` or from env). In production, the frontend is at `https://glass-web-production.up.railway.app` (or similar), but the API needs to also accept requests from `localhost` during development. The current setup only allows one origin.

More critically, `railway-web.toml` hardcodes the API URL as `https://glass-api-production.up.railway.app/api/v1`, but if the actual Railway domain is different, all API calls will fail due to CORS or wrong URL.

**Root Cause:** CORS_ORIGIN is a single string, not an array. And the API URL is hardcoded in the Railway build config.

**Fix:**
```typescript
const CORS_ORIGIN = process.env.CORS_ORIGIN?.split(',').map(s => s.trim()) || 
  (isDev ? ['http://localhost:5173'] : undefined);
```

And ensure CORS_ORIGIN env var in Railway includes the actual web app domain.

**Priority:** P1 — Production API will reject requests from the frontend if origins don't match exactly.

---

### Issue 11: ClerkProvider Initialized with Empty String When Key Missing

**File(s):** `apps/web/src/main.tsx`

**Problem:** Line: `<ClerkProvider publishableKey={clerkPubKey || ''}>` — if `VITE_CLERK_PUBLISHABLE_KEY` is not set, Clerk initializes with an empty string. This won't crash immediately but will cause Clerk to silently fail, with `isLoaded` never becoming `true`, meaning the entire app is stuck on a loading spinner forever.

**Root Cause:** Defensive fallback is wrong — an empty string is not a valid fallback.

**Fix:** Fail fast with a clear error:
```tsx
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
if (!clerkPubKey) {
  throw new Error(
    'VITE_CLERK_PUBLISHABLE_KEY is not set. Add it to your .env file or Railway build args.'
  );
}
```

**Priority:** P1 — Fails silently in production if env var is misconfigured.

---

### Issue 12: Settings Page Uses Hardcoded Mock Data, Not API

**File(s):** `apps/web/src/pages/Settings.tsx`

**Problem:** The Settings page uses hardcoded `mockOperator` and `mockWatchlist` arrays. It doesn't call any API endpoints or use React Query hooks. Changes to settings (notifications, watchlist) are local state only and don't persist.

**Root Cause:** Page was scaffolded with mock data and never connected to the API.

**Fix:** Replace mock data with actual API calls using existing hooks (`useProfile()`, `useWatchlists()`). Wire up notification preferences to a new API endpoint or Clerk metadata.

**Priority:** P2 — Non-functional page, but doesn't block core workflows.

---

### Issue 13: Alerts Page Makes Two Simultaneous Unread Alert Queries

**File(s):** `apps/web/src/pages/Alerts.tsx`

**Problem:** The Alerts page calls `useAlerts(queryParams)` for the filtered list AND `useAlerts({ read: false, limit: 100 })` for the unread count. That's two API calls on every render, and the DashboardLayout ALSO calls `useAlerts({ read: false, limit: 100 })`. So loading the Alerts page triggers 3 parallel alert API calls.

**Root Cause:** No dedicated "unread count" endpoint. Each component fetches the full unread list just to get `.length`.

**Fix:** Add a `/alerts/count` endpoint that returns `{ unread: number, critical_unread: number }`, or consolidate the unread count into the morning brief data (which already includes it).

**Priority:** P2 — Performance issue, 3x API load for alerts.

---

### Issue 14: `markAllAsRead` in Alerts Page — N+1 API Call Pattern

**File(s):** `apps/web/src/pages/Alerts.tsx`

**Problem:** `markAllAsRead` does:
```typescript
await Promise.all(unreadAlerts.map(alert => markReadMutation.mutateAsync({ id: alert.id, read: true })));
```
With 50 unread alerts, this fires 50 parallel PATCH requests. Each one also invalidates the React Query cache, triggering re-fetches.

**Root Cause:** No batch "mark all read" API endpoint.

**Fix:** Add `POST /alerts/mark-all-read` endpoint on the backend, call it from the frontend.

**Priority:** P2 — Performance issue at scale.

---

## Architecture Issues

### Dual Auth System (Clerk + Custom JWT) Creates Confusion

The system has TWO auth mechanisms: Clerk (for frontend) and a custom JWT flow with `bcrypt` passwords, refresh tokens, etc. (in `/auth/signup`, `/auth/login`, `/auth/refresh`). The custom flow creates users in the `users` table with `password_hash`. The Clerk flow doesn't create users in the GLASS DB at all.

**Recommendation:** Choose one. For an MVP, Clerk should be the sole auth provider. Remove the custom signup/login/refresh routes OR keep them as a fallback for API-only clients. The critical missing piece is the Clerk → GLASS DB bridge (webhook or auto-provision, as described in Issue 2).

### No Database Migrations System

The project has `infra/schema.sql` for initial setup but no migration tool (no Drizzle Kit config, no `drizzle.config.ts`). Schema changes require manual SQL execution, which is error-prone in production.

**Recommendation:** Add `drizzle-kit` and configure it. Use `drizzle-kit generate` for migrations.

### Scraper Watchlist Schema Mismatch

The scraper's `db.ts` defines watchlists with a `competitor_operator_id` column that doesn't exist in the API's `schema.ts` or `infra/schema.sql`. The delta scraper joins `watchlists w INNER JOIN sources s ON s.operator_id = w.competitor_operator_id` — this will fail because the main schema's watchlists table has `(operator_id, product_id)` but no `competitor_operator_id`.

**Recommendation:** Align the watchlist schemas. The scraper's delta worker concept (watching competitor prices for products on your watchlist) needs a `competitor_operator_id` column added to the canonical schema, or the scraper needs to derive competitor sources differently.

### No API Rate Limiting

The Fastify API has no rate limiting. Any unauthenticated endpoint (like `/auth/login`) is vulnerable to brute force. Even authenticated endpoints have no per-user throttling.

**Recommendation:** Add `@fastify/rate-limit` with sensible defaults (e.g., 100 req/min per IP for auth endpoints, 1000 req/min for authenticated endpoints).

### Frontend Uses `<a href>` Instead of `<Link>` for Internal Navigation

Multiple pages (MorningBrief, PriceWire, ThreatRadar) use `<a href="/prices">` for navigation instead of React Router's `<Link to="/prices">`. This causes full page reloads instead of SPA navigation, losing all React Query cache and component state.

**Recommendation:** Replace all internal `<a href>` with `<Link to>` from react-router-dom.

### No Error Boundaries

The React app has no error boundaries. If any component throws during rendering (e.g., accessing a property on `undefined` data), the entire app crashes to a white screen.

**Recommendation:** Add a root `<ErrorBoundary>` component wrapping `<App />`.

---

## Missing Deployments

### Scraper Service

**Status:** Code exists at `services/scrape/`, no Railway service deployed.

**Required Railway setup:**
1. Create new Railway service: `glass-scraper`
2. Set build config to use a new `railway-scrape.toml`:
   ```toml
   [build]
   builder = "DOCKERFILE"
   dockerfilePath = "services/scrape/Dockerfile"  # Needs to be created
   ```
3. **No Dockerfile exists** for the scraper. It needs one:
   ```dockerfile
   FROM node:22-alpine
   RUN apk add --no-cache chromium
   WORKDIR /app
   COPY services/scrape/package.json ./
   RUN npm install
   COPY services/scrape/ ./
   RUN npx tsc -p tsconfig.json
   ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser
   CMD ["node", "dist/index.js"]
   ```

**Environment variables needed:**
- `DATABASE_URL` — same Postgres as API
- `REDIS_URL` — Redis instance (needs a Railway Redis service or add-on)
- `FIRECRAWL_API_KEY` — Firecrawl API key for web scraping
- `SCRAPE_USER_AGENT` — optional
- `FULL_SCRAPE_CRON` — default `0 */6 * * *`
- `DELTA_SCRAPE_CRON` — default `0 * * * *`
- `PLAYWRIGHT_MAX_RETRIES` — default 3

**Missing dependency:** No Redis service is deployed on Railway. BullMQ requires Redis.

### Intelligence Service

**Status:** Code exists at `services/intelligence/`, no Railway service deployed.

**Required Railway setup:**
1. Create new Railway service: `glass-intelligence`
2. Set build config with a new `railway-intelligence.toml`
3. **No Dockerfile exists** for intelligence. Needs one similar to the API Dockerfile.

**Environment variables needed:**
- `DATABASE_URL` — same Postgres
- `REDIS_URL` — same Redis as scraper
- `CCC_APP_TOKEN` — optional, Socrata API app token for higher rate limits

### Redis Service

**Status:** Not deployed on Railway. Both scraper and intelligence services require Redis for BullMQ job queues.

**Required:** Add Railway Redis add-on or provision a Redis instance. Set `REDIS_URL` env var for both scraper and intelligence services.

---

## Data Pipeline Issues

### No Seed Data Script

The `scripts/init-scrapers.mjs` references a non-existent `scrape/seed-dispensaries.json` file. Without seed data (operator records with dispensary URLs), scrapers have nothing to scrape.

**Fix:** Create the seed dispensary JSON with actual MA dispensary URLs (Dutchie, Leafly pages for known operators). At minimum, seed 5-10 dispensaries for MVP testing.

### Scraper Parsers Import Non-Standard `base.ts`

The Dutchie and generic parsers import from `./base.js` which exports `clampConfidence`, `priceFromUnknown`, and `ProductParser` type. This file exists but was not reviewed. If it has issues, all parsing fails.

### Scraper Metrics Module

The scraper imports `setGauge` and `incrementCounter` from `./metrics.js`. This file exists but wasn't reviewed. If it has side effects (like trying to bind to a Prometheus port), it could crash the service.

### Intelligence Service CCC API Assumptions

The CCC API client uses Socrata dataset IDs (`hmwt-yiqy`, `piib-tj3f`, `albs-all`). These are real Socrata identifiers, but:
1. The `albs-all` dataset ID for board actions looks fake/placeholder
2. CCC may have changed their Socrata instance or dataset IDs
3. The base URL uses `/resource` which is the SODA 2.0 endpoint — correct for Socrata

**Recommendation:** Verify these dataset IDs are current by hitting the CCC Socrata API.

### Threat Dedup Constraint Issues

The intelligence service's `ccc-ingest.ts` uses `onConflictDoNothing({ target: [threats.type, threats.entity_name, threats.published_at] })` for dedup. But the intelligence service's `db.ts` defines the unique constraint as `unique('uq_threats_event').on(table.type, table.entity_name, table.published_at)`. The API service's schema in `schema.ts` does NOT have this unique constraint on the threats table. If the intelligence service uses the API's database, the `onConflictDoNothing` will fail (no unique index to match against).

**Fix:** Add the unique constraint to the API's threats table definition or to `schema.sql`:
```sql
ALTER TABLE threats ADD CONSTRAINT uq_threats_event UNIQUE (type, entity_name, published_at);
```

---

## Recommended Fix Order

1. **Fix auth redirect loop (Issue 1)** — 30 minutes. Replace `AuthGuard` with Clerk's `<SignedIn>/<SignedOut>` components, fix deprecated `redirectUrl` props, add `isLoaded` guard in `App`.

2. **Fix backend auth for Clerk users (Issue 2)** — 2-3 hours. Implement auto-provisioning in the auth plugin: if Clerk auth succeeds but no `operator_id`, create a pending operator record, or add a Clerk webhook to handle `user.created`.

3. **Fix database schema mismatch (Issue 3)** — 1 hour. Remove `pgSchema('glass')` from `services/api/src/db/schema.ts`, change all `glassSchema.table()` to `pgTable()`. This aligns with the DDL and other services.

4. **Fix Sidebar sign-out (Issue 5)** — 10 minutes. Use Clerk's `signOut()`.

5. **Fix token caching bug (Issue 6)** — 30 minutes. Always use token provider in API client.

6. **Fix ClerkProvider empty key (Issue 11)** — 5 minutes. Throw on missing key.

7. **Fix threat feed summary (Issue 7)** — 5 minutes. Add `low` count.

8. **Fix frontend `<a>` tags to `<Link>` (Architecture)** — 30 minutes. Replace across all pages.

9. **Verify engine modules exist and export correctly (Issue 9)** — 30 minutes.

10. **Deploy Redis on Railway** — 15 minutes. Add Railway Redis add-on.

11. **Create and deploy scraper Dockerfile + Railway service** — 1-2 hours.

12. **Create and deploy intelligence Dockerfile + Railway service** — 1-2 hours.

13. **Create seed dispensary data** — 1 hour. Build `seed-dispensaries.json` with real MA dispensary URLs.

14. **Run first scrape** — 30 minutes. Trigger manual scrape, verify data flows through pipeline.

15. **Connect Settings page to real API (Issue 12)** — 2 hours.

16. **Add batch mark-all-read endpoint (Issue 14)** — 30 minutes.

17. **Add error boundaries, rate limiting (Architecture)** — 1-2 hours.

---

## Environment Variables Needed

### API Service (Railway `glass-api`)
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET` | Yes (prod) | Secret for signing JWTs |
| `CLERK_SECRET_KEY` | Yes | Clerk backend secret key |
| `CLERK_PUBLISHABLE_KEY` | Yes | Clerk frontend publishable key |
| `CORS_ORIGIN` | Yes (prod) | Frontend URL(s), comma-separated |
| `PORT` | No | Default 3000 |
| `HOST` | No | Default 0.0.0.0 |
| `NODE_ENV` | Recommended | `production` |
| `LOG_LEVEL` | No | Default `info` |

### Web Frontend (Railway `glass-web`)
| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Full API URL including `/api/v1` |
| `VITE_CLERK_PUBLISHABLE_KEY` | Yes | Clerk frontend publishable key |

### Scraper Service (Railway `glass-scraper` — NEW)
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Same PostgreSQL as API |
| `REDIS_URL` | Yes | Redis connection string |
| `FIRECRAWL_API_KEY` | Yes | Firecrawl API key |
| `FULL_SCRAPE_CRON` | No | Default `0 */6 * * *` |
| `DELTA_SCRAPE_CRON` | No | Default `0 * * * *` |
| `SCRAPE_SCHEDULE_TZ` | No | Default `America/New_York` |
| `PLAYWRIGHT_MAX_RETRIES` | No | Default 3 |
| `SCRAPE_USER_AGENT` | No | Default `GLASS-ScrapeBot/1.0` |
| `SCRAPE_FULL_CONCURRENCY` | No | Default 2 |
| `PARSE_WORKER_CONCURRENCY` | No | Default 5 |

### Intelligence Service (Railway `glass-intelligence` — NEW)
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Same PostgreSQL as API |
| `REDIS_URL` | Yes | Same Redis as scraper |
| `CCC_APP_TOKEN` | No | Socrata API app token for higher limits |

### Shared Infrastructure
| Variable | Required | Description |
|----------|----------|-------------|
| PostgreSQL | Yes | Railway Postgres add-on |
| Redis | Yes | Railway Redis add-on (NEW — needs to be created) |

---

## Estimated Effort

| Category | Effort | Notes |
|----------|--------|-------|
| **Auth fixes (Issues 1, 2, 5, 6, 11)** | 4-6 hours | P0 blockers, must be done first |
| **Schema alignment (Issue 3)** | 1-2 hours | Straightforward find-and-replace |
| **Frontend polish (Issues 4, 7, 8, 12, 13, 14)** | 4-6 hours | Lower priority, incremental |
| **Backend verification (Issue 9, engine modules)** | 1-2 hours | Check imports, stub if needed |
| **Infrastructure (Redis, Dockerfiles, Railway configs)** | 3-4 hours | New services, deployment |
| **Data seeding + first scrape** | 2-3 hours | Seed data, verify pipeline |
| **Architecture improvements (error boundaries, rate limiting, Link components)** | 2-3 hours | Quality of life |
| **TOTAL** | **17-26 hours** | ~3-4 days of focused work |

---

## Security Issues

1. **No rate limiting on auth endpoints** — `/auth/login` and `/auth/signup` are vulnerable to brute force.
2. **Refresh tokens stored without user-agent/IP binding** — Stolen refresh tokens can be used from any device.
3. **SQL injection risk in sort_by parameter** — `operators.ts` line 33 uses `sql.identifier(pagination.sort_by!)` and `sql.raw(pagination.order!)`. The `sort_by` value is validated against an allowlist by `parsePagination`, so this is safe as long as `parsePagination` is always called first. But `sql.raw(pagination.order!)` for `asc`/`desc` is risky — if the order validation in `parsePagination` is bypassed, raw SQL injection is possible. Use a ternary instead: `pagination.order === 'asc' ? sql`asc` : sql`desc``.
4. **CSP headers not configured** — E2E tests reported CSP warnings. The `serve` static server used in the web Dockerfile doesn't set Content-Security-Policy headers. Add CSP headers either via serve config or a Cloudflare/Railway middleware.
5. **Clerk publishable key in Railway build args** — `VITE_CLERK_PUBLISHABLE_KEY` is a build arg in `railway-web.toml`. This is fine since it's a *publishable* key (meant to be public), but ensure the *secret* key is only in runtime env vars.

---

## Additional Minor Issues

- **TopBar `title` prop is hardcoded** — `DashboardLayout` always passes `title="Dashboard"`. It should pass the current page title (e.g., "Price Wire", "Threat Radar").
- **`MorningBrief` stats are partially fabricated** — Lines calculating `totalProducts` and `priceChanges24h` use suspicious math: `briefData.price_wire.top_movers.length * 150` and `* 15`. These should come from the API or be removed.
- **PriceWire Sparkline gradient IDs collide** — Both `MorningBrief` and `PriceWire` define SVG gradients with IDs like `spark-up` and `spark-down`. Since these are in the same DOM, the IDs collide. Use unique IDs per instance.
- **`docker-compose.yml` references non-existent files** — `./scripts/init-db.sh` and `./scripts/init-clickhouse.sh` are mounted but these scripts don't exist in the repo.
- **ClickHouse is in docker-compose but never used** — No service reads from or writes to ClickHouse. Remove it to simplify the local dev setup, or document its intended use.
- **`package.json` workspaces only includes `apps/*`** — Services under `services/*` are not in the workspace, meaning `npm install` at root won't install their dependencies. Either add `services/*` to workspaces or document that each service needs separate `npm install`.
