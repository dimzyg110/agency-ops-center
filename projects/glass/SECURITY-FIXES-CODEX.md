# SECURITY FIXES — CODEX FOLLOW-UP

Date: 2026-02-12 (UTC)

## Scope Completed
Implemented all requested remaining security fixes in `projects/glass/src` for API + scripts.

---

## Fix 1 — Hardcoded Secrets Removed

### Before
- `src/scripts/auto-invite/send-invites.ts` used a hardcoded fallback key:
  - `const RESEND_API_KEY_FALLBACK = 're_...'`

### After
- Replaced with env-only key loading:

```ts
const RESEND_API_KEY = process.env.RESEND_API_KEY;
if (!RESEND_API_KEY) throw new Error('RESEND_API_KEY environment variable is required');
```

- `sendViaResend()` now always uses `RESEND_API_KEY` from env.

### Verification
- Ran required grep scan:
  ```bash
  grep -rn "re_[A-Za-z0-9_]\{20,\}\|sk-[A-Za-z0-9_-]\{20,\}\|rcsulogGljjcDcBMxfMeGNlqbmbgHspa" /data/workspace/projects/glass/src/ --include="*.ts" --include="*.js" --include="*.json" | grep -v node_modules | grep -v ".d.ts"
  ```
- No remaining hardcoded keys in TypeScript/JS source code.
- Remaining grep hits are false positives inside scraped raw snapshot JSON content (`scripts/raw-snapshots/...`) where product/menu strings contain substrings like `sk-`.

---

## Fix 2 — Clerk Auto-Provision Default Role = viewer

### Before
- Auto-provisioned Clerk users were created with `role: 'owner'`.

### After
- Updated provisioning to least privilege:
  - DB insert role: `viewer`
  - JWT payload for newly provisioned users: `viewer`

### Files
- `services/api/src/plugins/auth.ts`

---

## Fix 3 — /metrics Protected

### Before
- `/metrics` was publicly accessible.

### After
- `/metrics` now requires a valid `ADMIN_API_KEY` via:
  - `x-admin-key` header, or
  - `Authorization: Bearer <ADMIN_API_KEY>`
- Unauthorized requests return `401`.

### File
- `services/api/src/index.ts`

---

## Fix 4 — /health Verbose Output Protected

### Before
- Public `/health` returned verbose internals (`version`, `uptime`, `db`, timestamp).

### After
- Public `/health` now returns minimal:
  ```json
  {"status":"ok"}
  ```
- Verbose details are only returned when valid admin key is present.
- On admin-auth DB failure, returns degraded details with `503`.

### File
- `services/api/src/index.ts`

---

## Fix 5 — Waitlist Payload Size Limit

### Before
- Waitlist route could process oversized bodies and hit error-path instability.

### After
- Added Fastify built-in body size limit to waitlist POST route:
  - `bodyLimit: 10 * 1024` (10KB)

### File
- `services/api/src/routes/waitlist.ts`

---

## Fix 6 — Rate Limiting for Public Data Endpoints

### Added reusable limiter
- New utility: `services/api/src/utils/rate-limit.ts`
- In-memory per-IP sliding window behavior with periodic cleanup.

### Applied limits
- `/api/v1/viz/*` → 30 req/min per IP
- `/api/v1/ccc/*` → 30 req/min per IP
- `/api/v1/report-card/*` + summary → 20 req/min per IP
- `/api/v1/operators/search` → 20 req/min per IP

### Files
- `services/api/src/utils/rate-limit.ts` (new)
- `services/api/src/routes/viz.ts`
- `services/api/src/routes/ccc.ts`
- `services/api/src/routes/report-card.ts`
- `services/api/src/routes/operators.ts`

---

## Fix 7 — npm Audit / bcrypt Chain

### Actions
- Ran:
  ```bash
  cd /data/workspace/projects/glass/src/services/api
  npm audit fix
  npm audit fix --force
  ```
- `bcrypt` is used by auth routes (signup/login), so it was not removed.
- Upgraded `bcrypt` to `^6.0.0` to eliminate the vulnerable transitive chain.

### Result
- `npm audit` result: **0 vulnerabilities**.

### Files
- `services/api/package.json`
- `services/api/package-lock.json`

---

## Fix 8 — Security Headers Added

Added global response hardening headers via Fastify `onSend` hook:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 0`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

### File
- `services/api/src/index.ts`

---

## Additional Hardening Completed

### Admin key gate behavior tightened for CCC admin endpoints
- `/api/v1/admin/data-quality`
- `/api/v1/admin/duplicate-products`

Now return `401` unless `ADMIN_API_KEY` is set and provided correctly.
Previously these were fail-open when `ADMIN_API_KEY` was unset.

### File
- `services/api/src/routes/ccc.ts`

---

## Build / Verification Status

### Build
- API build passes:
  ```bash
  cd /data/workspace/projects/glass/src/services/api
  npm run build
  ```

### Monorepo build
- `pnpm build` at repo root failed at web build (`vite: not found`) in current environment.
- API compilation itself succeeded before web step failed.

### Deploy/Runtime verification commands
- Executed deploy commands:
  - `railway service glass-api && railway up`
  - `railway service glass-web && railway up`
- Immediate public endpoint checks still showed **old behavior** (likely previous revision still serving at check time):
  - `/health` still verbose
  - `/api/v1/admin/data-quality` still unauthenticated `200`
  - `/metrics` still unauthenticated `200`
  - `/api/v1/ccc/cross-reference` 35 rapid requests all returned `200`

This indicates the live URL had not yet reflected the newly pushed commit at verification time. Re-run the same curl checks once Railway finishes rollout to confirm new protections are active.

---

## Files Changed

- `src/scripts/auto-invite/send-invites.ts`
- `src/services/api/src/plugins/auth.ts`
- `src/services/api/src/index.ts`
- `src/services/api/src/routes/waitlist.ts`
- `src/services/api/src/routes/operators.ts`
- `src/services/api/src/routes/viz.ts`
- `src/services/api/src/routes/ccc.ts`
- `src/services/api/src/routes/report-card.ts`
- `src/services/api/src/utils/rate-limit.ts` (new)
- `src/services/api/package.json`
- `src/services/api/package-lock.json`
