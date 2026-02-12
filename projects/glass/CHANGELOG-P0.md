## Review Round 2 — 2026-02-12

### What changed
- Added durable Clerk identity linkage for users via `clerk_user_id`.
  - `services/api/src/db/schema.ts`:
    - Added `users.clerk_user_id` as `varchar(255).unique()` (nullable).
    - Added index `idx_users_clerk_user_id`.
  - `infra/schema.sql`:
    - Added `clerk_user_id VARCHAR(255) UNIQUE` to `users` table.
    - Added `CREATE INDEX idx_users_clerk_user_id ON users (clerk_user_id);`.

- Hardened Clerk auto-provisioning in `services/api/src/plugins/auth.ts`:
  - `autoProvisionClerkUser()` now:
    1. Looks up existing user by `clerk_user_id` first.
    2. Falls back to email lookup.
    3. Backfills `clerk_user_id` on email-matched legacy users when missing.
    4. Wraps auto-provision insert path in `try/catch`; on Postgres unique violation (`code === '23505'`), re-queries by `clerk_user_id` and returns existing operator to handle first-request races.
    5. Always sets `clerk_user_id` on newly inserted user records.
  - Newly auto-provisioned JWT payload now returns `role: 'owner'` explicitly (instead of claim-derived fallback).

- Fixed CORS origin parsing in `services/api/src/index.ts`:
  - Added `.filter(Boolean)` after split/trim.
  - Empty filtered results are treated as `undefined`, preserving production fatal guard behavior.

- Corrected changelog accuracy in `src/CHANGELOG-P0.md`:
  - Removed invalid reference to operator `type: dispensary` (no such column exists).
  - Entry now reflects actual provisioning fields (`status: 'pending'`, `state: 'MA'`).

### Why
- Prevent repeated 401 failures for Clerk users lacking email claims.
- Ensure idempotent first-login provisioning keyed by immutable Clerk `userId`.
- Eliminate race-condition failures on concurrent first API requests.
- Avoid invalid CORS entries from malformed env strings.
- Keep documentation consistent with implemented schema and runtime behavior.
