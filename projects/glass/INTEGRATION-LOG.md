
## Scraper Service Integration (2026-02-11)

### Required API Keys & Services

The scraper service (`src/services/scrape`) requires the following external services:

| Service | Env Var | Purpose | Notes |
|---------|---------|---------|-------|
| **Redis** | `REDIS_URL` | Job Queue (BullMQ) | Required for all workers. |
| **Postgres** | `DATABASE_URL` | Data Persistence | Stores scrape jobs and product data. |
| **Firecrawl** | `FIRECRAWL_API_KEY` | Fallback Scraping | **CRITICAL**: Used when Playwright is blocked. API Key must be set in deployment environment. |
| **Proxies** | `HTTPS_PROXY` | IP Rotation | Optional but recommended for high volume. Playwright respects this env var. |

### Configuration Notes
- **Firecrawl**: Get API key from Firecrawl dashboard. Free tier has limits.
- **Playwright**: Requires `npx playwright install` in the deployment environment (Docker/Railway).
- **Concurrency**: Adjust `SCRAPE_FULL_CONCURRENCY` based on available RAM (Playwright is memory hungry).

## Frontend Auth + API Integration Fix (2026-02-11)

### Changes implemented
- Set Railway web service variable: `VITE_USE_MOCK=false` on `glass-web`.
- Removed mock-mode branches from `apps/web/src/api/hooks.ts`; hooks now call live API client methods directly.
- Updated `apps/web/src/api/client.ts` to support Clerk JWT integration:
  - `setToken(token: string | null)`
  - `setTokenProvider(() => Promise<string | null>)`
  - Request pipeline now resolves token from provider when needed and sends `Authorization: Bearer <jwt>`.
- Added `ApiAuthSync` in `apps/web/src/main.tsx`:
  - Uses Clerk `useAuth()`
  - Registers `api.setTokenProvider(() => getToken())`
  - Syncs token on auth state changes (`api.setToken(token)` / clear on sign-out).

### Expected behavior after deploy
- Frontend should stop rendering mock user data (e.g., "Alex Johnson") in production.
- API requests should include Clerk bearer token in the `Authorization` header when user is signed in.

## Backend Clerk JWT Verification Setup (2026-02-11)

### Package + server integration
- Installed backend SDK: `@clerk/fastify` in `services/api`.
- Registered `clerkPlugin` in `services/api/src/index.ts` with:
  - `secretKey: process.env.CLERK_SECRET_KEY`
  - `hookName: 'onRequest'` so Clerk auth state is available before route `onRequest` guards run.
- Kept `@fastify/jwt` and `JWT_SECRET` support for backward compatibility with existing internal/custom JWT flows.

### Auth plugin behavior
- Updated `services/api/src/plugins/auth.ts`:
  - `authenticate` now checks Clerk auth first (`getAuth(request, { acceptsToken: 'any' })`).
  - Maps Clerk session claims to existing `request.auth`/`request.jwtUser` interface (`sub`, `operator_id`, `role`, `iat`, `exp`).
  - Supports `operator_id` and `role` from top-level claims plus nested metadata (`metadata`, `public_metadata`, `unsafe_metadata`).
  - Falls back to legacy `request.jwtVerify()` if Clerk claims are absent or token is non-Clerk.
- Result: protected endpoints can accept Clerk bearer tokens without breaking existing JWT routes.

### Railway environment updates required
Add this variable to the **api service** in Railway:
- `CLERK_SECRET_KEY=<from Clerk dashboard>`

Keep existing:
- `JWT_SECRET=<existing value>` (legacy token compatibility)

### Verification notes
- Local compile check passed: `npm run typecheck` in `services/api`.
- Deployment/remote endpoint validation command to run from project root:
  - `railway up --detach`
- Post-deploy checks:
  1. `GET /health` should return 200 without auth.
  2. Protected routes (e.g., `/api/v1/auth/me`) should accept `Authorization: Bearer <clerk_jwt>` when token contains `operator_id` claim.
