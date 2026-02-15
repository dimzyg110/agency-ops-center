# GLASS P0/P1 Hotfix Review (Code Review)

Date: 2026-02-12  
Reviewer: GPT-5.3 Codex (senior code review pass)

## Overall Assessment

**Request changes**

Most fixes are directionally correct and address the original incidents, but there is at least one **critical** issue in backend auto-provisioning that can still break auth for some valid Clerk users and create repeated DB errors. A few warnings should also be addressed before considering this fully stable in production.

---

## Per-file Findings

## 1) `apps/web/src/components/AuthGuard.tsx`

### ✅ Correctness
- Using Clerk primitives (`<SignedIn>`, `<SignedOut>`, `<RedirectToSignIn>`) is the correct pattern to avoid redirect loops during hydration.
- This should resolve the specific P0 loop caused by `useAuth().isSignedIn` being transiently false.

### ✅ Security
- No auth bypass introduced.

### ✅ Edge cases
- Hydration window is handled by Clerk internals as intended.

### ✅ Clerk API usage
- Imports and usage are correct for Clerk v5+.

### Findings
- **Info:** `children` is optional; if omitted, route renders nothing while signed in. Not harmful, just permissive.

---

## 2) `apps/web/src/App.tsx`

### ✅ Correctness
- `PublicRoute` with `isLoaded` gate prevents flicker and bad redirects before auth state settles.
- Protected routes now use `ProtectedRoute` consistently.
- `fallbackRedirectUrl` usage on `<SignIn>` and `<SignUp>` is correct for Clerk v5+.

### ✅ Security
- No bypass observed.

### ⚠️ Edge cases
- `PublicRoute` depends on `useAuth().isLoaded` (good), but `SignedIn/SignedOut` in same component can still show a brief spinner for all unauthenticated users; acceptable UX tradeoff.
- `<a href="/login">` in `GlassSignUp` causes hard navigation instead of SPA navigation; not a security issue.

### Findings
- **Info:** Overall fix is correct and complete for the redirect-loop class of issue.

---

## 3) `apps/web/src/main.tsx`

### ✅ Correctness
- Failing fast on missing `VITE_CLERK_PUBLISHABLE_KEY` is correct and prevents silent broken auth.
- `ApiAuthSync` wiring to `setTokenProvider(() => getToken())` is appropriate.

### ⚠️ Edge cases
- `getToken()` can reject (network/transient Clerk SDK errors). No local try/catch in `syncToken`, so you can get unhandled promise rejection noise in dev/prod logs.

### ✅ Security
- Strict failure mode improves operational safety.

### Findings
- **Warning:** Wrap async token sync in try/catch and clear token on error to avoid stale auth headers.

---

## 4) `services/api/src/plugins/auth.ts`

### ✅ Correctness (intent)
- Intent is right: when Clerk auth is valid but JWT lacks `operator_id`, auto-provision instead of 401.

### ❌ Critical issue
1. **Critical — repeated failure path for users without email claim**
   - `autoProvisionClerkUser()` only looks up existing user by `email`.
   - If Clerk token has no email claim, lookup is skipped.
   - It then inserts operator with deterministic `license_number = PENDING-${userId}`.
   - On subsequent requests, it again cannot look up (still no email) and attempts same operator insert, triggering unique constraint failure on `license_number`.
   - Result: repeated auth failures/log noise; user can get stuck unauthorized despite being authenticated with Clerk.

### ⚠️ Warning issues
2. **Warning — race condition on concurrent first requests**
   - Two simultaneous requests for a new user can both miss lookup and race into inserts.
   - Unique conflicts likely on `users.email` or `operators.license_number` without retry/recovery path.

3. **Warning — role mismatch after auto-provision**
   - Newly inserted `users.role` is `'owner'`, but returned JWT payload role is derived from Clerk claims (`getRoleFromClaims`) and defaults to `'viewer'` if missing.
   - This may unexpectedly downscope new users until claims metadata is updated.

4. **Warning — no durable Clerk-to-local identity mapping**
   - No `clerk_user_id` persistence in DB means mapping relies on email claim presence/stability.
   - Email changes or missing claim can orphan linkage.

### ✅ Security
- Query construction uses Drizzle primitives; no SQL injection concerns found.
- `requireOperator` checks remain strict.

### Recommended remediation
- Add a dedicated `clerk_user_id` column (unique) in `users` and always resolve by it first.
- Use transaction + upsert/retry strategy for operator/user creation.
- On unique violation, re-query and continue rather than failing auth.
- If email absent, still make resolution deterministic via `clerk_user_id` (not email).

---

## 5) `services/api/src/db/schema.ts`

### ✅ Correctness
- Moving from `pgSchema('glass')` to `pgTable()` in `public` schema aligns with other services and fixes cross-service visibility issue.

### ⚠️ Migration concerns
- This is a structural namespace change, not a no-op: existing deployed DBs with tables under `glass.*` need explicit migration/rename strategy.
- If migration scripts are not applied carefully, API may point to empty `public` tables while old data remains in `glass` schema.

### Findings
- **Warning:** Ensure rollout includes data migration (`ALTER TABLE ... SET SCHEMA public` or recreate+copy) and index/constraint validation.

---

## 6) `apps/web/src/components/Sidebar.tsx`

### ✅ Correctness
- Replacing manual URL redirect with `signOut({ redirectUrl: '/login' })` is correct and addresses stale session risk.

### ✅ Security
- Properly invalidates Clerk session rather than just client navigation.

### ⚠️ Edge cases
- `signOut` promise isn’t awaited/caught; on failure, user gets no feedback.

### Findings
- **Info:** Functional fix is good. Consider error handling/toast.

---

## 7) `apps/web/src/api/client.ts`

### ✅ Correctness
- Preferring `tokenProvider` over cached token is the right fix to avoid stale token usage after refresh.

### ⚠️ Edge cases
- If `tokenProvider` throws/rejects, request fails even if `this.token` still exists and may be usable.
- Could benefit from fallback logic: try provider, on failure optionally fall back to cached token once.

### ✅ Security
- No new attack vector observed.

### Findings
- **Warning:** Add guarded fallback behavior for resilience during transient token-provider failures.

---

## 8) `services/api/src/routes/threats.ts`

### ✅ Correctness
- Added `low` count in feed summary; now consistent with UI `ThreatSummary` type.

### ✅ Security
- Drizzle/sql tagged template usage is parameterized; no SQL injection issue found.

### ⚠️ Edge cases
- Geo filter checks use truthy checks (`if (query.lat && query.lon && query.radius)` and `if (query.lat && query.lon)`), so valid `0` values are treated as absent.
- Massachusetts coords make `0` unlikely in production, but logic is still technically incorrect.

### Findings
- **Info:** P1 fix itself is correct.
- **Warning:** Use explicit `!== undefined` checks for numeric query params.

---

## 9) `services/api/src/index.ts`

### ✅ Correctness
- Supporting comma-separated origins via `.split(',').map(trim)` is correct directionally.

### ⚠️ Edge cases / security hardening
- `CORS_ORIGIN=""` becomes `['']` (truthy), bypassing production fatal guard and resulting in invalid allowlist entry.
- No filtering of empty items; should use `.map(...).filter(Boolean)`.

### Findings
- **Warning:** Sanitize parsed origins and enforce non-empty allowlist in production.

---

## 10) `CHANGELOG-P0.md`

### ✅ Correctness
- Changelog accurately describes most implemented fixes.

### ⚠️ Inconsistency
- It states operator auto-provision includes “type: dispensary”, but current schema snippet for `operators` has no `type` column and auth insert code does not set `type`.

### Findings
- **Info:** Update changelog text to match actual implementation.

---

## Follow-up Recommendations

1. **Blocker fix (required):** Refactor `autoProvisionClerkUser` to use durable unique mapping (`clerk_user_id`) and handle no-email users + concurrency safely (transaction/upsert/retry).
2. Add integration tests for auth provisioning cases:
   - first login with email claim
   - first login without email claim
   - concurrent first requests
   - missing `operator_id` claim on subsequent requests
3. Harden token handling on frontend:
   - catch `getToken()` failures in `ApiAuthSync`
   - optionally fallback to cached token once in API client
4. Harden CORS parsing with empty-entry filtering and strict production validation.
5. Add/verify DB migration runbook for schema move (`glass` → `public`) with rollback plan.

---

## Final Verdict

**Request changes** due to the **critical auto-provisioning defect** in `plugins/auth.ts` and a few production-hardening warnings. Once the auth provisioning path is made deterministic and concurrency-safe, this hotfix set should be close to approval.
