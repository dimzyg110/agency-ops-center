# RELIABILITY FIXES SUMMARY

Date: 2026-02-12 UTC
Commit: `ea9daa0`

## Completed

### 1) P0 — Duplicate operator merge (live DB executed)
- Added migration: `src/scripts/migrations/004-merge-duplicate-operators.sql`
- Logic implemented:
  - Normalizes names with `lower(replace(name, '-', ' '))`
  - Selects keeper per duplicate group by:
    1. highest `prices` count
    2. proper-name heuristic (contains uppercase, no hyphen)
    3. name/id stable tiebreak
  - Repoints all FK references to keeper dynamically (all public tables referencing `operators.id`)
  - Explicitly checks/updates `products.operator_id` if such column exists
  - Deletes duplicate operator rows
  - Logs row updates and per-merge notices

- Executed against Railway production DB:
  - Duplicate merge plan rows: **19**
  - `prices.operator_id` updated: **2015**
  - `sources.operator_id` updated: **19**
  - `users.operator_id` updated: **1**
  - `recommendations.operator_id` updated: **6**
  - `alerts.operator_id` updated: **10**
  - `margin_rules.operator_id` updated: **5**
  - Duplicates deleted from `operators`: **19**
  - Remaining duplicate groups by normalization: **0**

### 2) P0 — `/admin/data-quality` SQL reserved word check
- Verified route uses `cross_ref` CTE in `services/api/src/routes/ccc.ts`.
- Ran equivalent SQL directly against production DB successfully (no reserved word failure).

### 3) P1 — Error handling hardening
- Global error handler updated in `services/api/src/index.ts` to structured JSON format:
  - `error`, `message`, `statusCode`
  - Validation errors return 400 with `details`
  - Production-safe message behavior as requested
- Added endpoint-level try/catch in high-risk routes:
  - `report-card` endpoints
  - `viz` expensive endpoints (`price-matrix`, `proximity`)

### 4) P1 — Timeout protection + UUID guardrails
- Added query timeout wrapper (`Promise.race`) to:
  - `/viz/price-matrix` (15s)
  - `/viz/proximity` (15s)
  - `/report-card/:operator_id` (20s)
  - `/report-card/summary/:operator_id` (20s)
- Added runtime UUID validation (400 response) before DB work for `operator_id` inputs in those endpoints.

### 5) P1 — API performance indexes
- Added migration: `src/scripts/migrations/005-performance-indexes.sql`
- Executed on production:
  - Created/ensured:
    - `idx_prices_operator_id`
    - `idx_prices_product_id`
    - `idx_prices_scraped_at` (already existed)
    - `idx_products_category` (already existed)
    - `idx_products_brand` (already existed)
    - `idx_operators_name`
    - `idx_operators_city`

### 6) P1 — Health endpoint for Railway
- Updated `/health` in `services/api/src/index.ts` (no prefix/auth) to return:
  - `status`, `version`, `uptime`, `db`, `timestamp`
- Includes live DB connectivity probe (`SELECT 1`), returns degraded/503 if DB unavailable.

### 7) P1 — Waitlist input validation + rate limiting
- Updated `services/api/src/routes/waitlist.ts`:
  - Email validation via basic regex
  - Product validation against allowed set:
    - `budtender`, `cue`, `delivery`, `glass`, `newsletter`
  - In-memory per-IP rate limit: max **10/hour**
  - Returns 400 for invalid email/product
  - Returns 429 when rate-limited
  - Structured responses for 200/400/429

## Build / Validation
- API TypeScript build passed:
  - `pnpm build` in `src/services/api`

## Git + Deploy
- Pushed to `main`:
  - `fix: reliability — merge duplicate operators, error handling, indexes, health check, input validation`
- Railway deploy triggered:
  - `railway service glass-api && railway up`

## Files changed
- `src/services/api/src/index.ts`
- `src/services/api/src/routes/report-card.ts`
- `src/services/api/src/routes/viz.ts`
- `src/services/api/src/routes/waitlist.ts`
- `src/scripts/migrations/004-merge-duplicate-operators.sql`
- `src/scripts/migrations/005-performance-indexes.sql`
- `src/services/api/src/routes/ccc.ts` (already contained `cross_ref`; included in commit state)
