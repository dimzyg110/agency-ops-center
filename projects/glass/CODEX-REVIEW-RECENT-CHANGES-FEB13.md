# CODEX Review — Recent GLASS Changes (b9536a8..196fb31)

Date: 2026-02-13 (UTC)
Reviewer: GPT 5.3 Codex (QA role)

## Executive Summary

**Overall verdict: REQUEST CHANGES**

I found multiple ship-blocking issues: an exposed hardcoded database credential, missing API key validation (auth bypass), a SQL syntax error in an admin endpoint, and schema/table-column drift between ETL/API queries and Drizzle schema for `ccc_monthly_prices`.

---

## 1) `scripts/etl/match-operators.ts` — **REQUEST CHANGES**

### 🔴 Critical — Security: hardcoded production DB credential in source
- **Location:** lines **3–6**
- **Snippet:**
```ts
const DEFAULT_DATABASE_URL =
  'postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway';
const DATABASE_URL = process.env.DATABASE_URL ?? DEFAULT_DATABASE_URL;
```
- **Risk:** Secret exposure in git history + accidental writes to production when env var is missing.
- **Fix:** Remove fallback entirely; require `DATABASE_URL` and fail fast.

### 🟠 Major — Correctness/Production safety: probable column-name mismatch vs current schema
- **Location:** lines **92, 131–132, 175–180, 193–194, 216–220**
- **Snippet examples:**
```sql
l.establishment_city
l.latitude / l.longitude
l.business_email / l.business_phone
l.commence_operations_date
```
- **Why:** In `schema.ts`, `ccc_licenses` uses `city/state/commence_date` (not `establishment_city/establishment_state/commence_operations_date`) and does not define `latitude/longitude/business_email/business_phone`. If DB matches schema, this script will fail at runtime.
- **Fix:** Align SQL to canonical column names or explicitly document/introduce migration for these columns.

### 🟡 Minor — Production safety: extension creation in app script
- **Location:** line **64**
- **Snippet:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm
```
- **Risk:** may fail under restricted DB roles on Railway.
- **Fix:** move extension enablement to controlled migration/runbook, or guard with clear preflight check.

---

## 2) `scripts/import-ccc-data.ts` — **REQUEST CHANGES**

### 🔴 Critical — Schema mismatch: writes columns not present in Drizzle `ccc_monthly_prices`
- **Location:** lines **187–195**
- **Snippet:**
```sql
INSERT INTO ccc_monthly_prices (
  year_month, avg_price_per_gram, avg_price_per_oz, avg_price_per_eighth, mom_change_pct, yoy_change_pct, source
)
ON CONFLICT (year_month) DO UPDATE ...
```
- **Why:** `schema.ts` defines `ccc_monthly_prices` as:
  - `report_month`, `category`, `license_type`, `avg_price`, `unit`, `sample_size` (lines 354–367 area)
  - no `year_month`/`avg_price_per_gram` etc.
- **Impact:** insert/upsert will fail on deployment if DB reflects Drizzle schema.
- **Fix:** choose one canonical table contract and update ETL + API + migrations together.

### 🟠 Major — Correctness: misleading ingest metrics
- **Location:** `bulkUpsert` return semantics + `recordsInserted` accumulation (e.g., lines 185–197)
- **Issue:** `bulkUpsert` returns processed row count, not true inserted vs updated rows. `recordsUpdated` is never incremented.
- **Fix:** rename counters to `rowsProcessed`, or capture insert/update counts via `RETURNING`/CTE strategy.

---

## 3) `scripts/migrations/006-ecosystem-integration.sql` — **APPROVE WITH CHANGES**

### 🟠 Major — Production safety: `gen_random_uuid()` dependency not ensured in migration
- **Location:** lines **5, 24, 40, 58**
- **Snippet:**
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```
- **Risk:** migration fails if `pgcrypto` extension is not enabled in target DB.
- **Fix:** add `CREATE EXTENSION IF NOT EXISTS pgcrypto;` in bootstrap migration or prerequisite step.

### ✅ Notes
- Drizzle definitions for the 4 new tables appear aligned with this SQL (types, defaults, indexes).

---

## 4) `services/api/src/db/schema.ts` — **APPROVE WITH CHANGES**

### 🟠 Major — Schema consistency drift with ETL/API CCC monthly prices
- **Location:** lines **354–367** (cccMonthlyPrices definition)
- **Issue:** This table contract conflicts with both:
  - `scripts/import-ccc-data.ts` (`year_month`, `avg_price_per_gram`, ...)
  - `routes/ccc.ts` (`SELECT year_month, avg_price_per_gram, ...`)
- **Fix:** unify the schema and update all consumers in one migration set.

### ✅ Notes
- New ecosystem tables (`budtender_sessions`, `budtender_queries`, `demand_signals`, `ecosystem_events`) match migration 006 well.

---

## 5) `services/api/src/index.ts` — **APPROVE WITH CHANGES**

### 🟠 Major — Security architecture: route registered as public while relying on weak in-route key check
- **Location:** lines **186–194** (public route registration includes `catalogRoutes`)
- **Issue:** `catalogRoutes` is public and currently only checks that header exists/non-empty, not that it matches server secret.
- **Fix:** enforce key validation in route (or global plugin) and consider moving under protected/authenticated group if appropriate.

---

## 6) `services/api/src/routes/catalog.ts` — **REQUEST CHANGES**

### 🔴 Critical — Auth bypass: API key presence check only (no value validation)
- **Location:** lines **18–26**
- **Snippet:**
```ts
const apiKey = request.headers['x-roviq-api-key'];
if (typeof apiKey !== 'string' || apiKey.trim().length === 0) {
  return reply.status(401)...
}
```
- **Risk:** any non-empty string grants access to operator catalog feed.
- **Fix:** compare against `process.env.ROVIQ_API_KEY` (constant-time compare preferred), reject otherwise.

### 🟡 Minor — Performance: potential expensive lateral lookup at scale
- **Location:** lines **45–57**
- **Issue:** LATERAL latest-price lookup per product can degrade with large product table.
- **Fix:** ensure composite index `(operator_id, product_id, scraped_at DESC)` on `prices`, or precompute latest price view.

---

## 7) `services/api/src/routes/ccc.ts` — **REQUEST CHANGES**

### 🔴 Critical — SQL syntax error in `/admin/data-quality` cross-reference query
- **Location:** lines **256–281**
- **Snippet:**
```sql
WITH cross_ref AS (
  ccc AS (...),
  glass AS (...)
  SELECT ...
)
SELECT ... FROM cross_ref
```
- **Why:** invalid CTE nesting syntax. Should be `WITH ccc AS (...), glass AS (...), cross_ref AS (...) SELECT ...` (or fold without `cross_ref`).
- **Impact:** endpoint fails at runtime.

### 🟠 Major — Schema drift with `ccc_monthly_prices`
- **Location:** lines **35–47**, **95–103**, **260–263**
- **Issue:** queries use `year_month`, `avg_price_per_gram`, etc., conflicting with Drizzle schema’s `report_month`, `avg_price`, etc.
- **Impact:** runtime query failures if deployed schema follows current Drizzle model.

### 🟡 Minor — Security hygiene: admin key accepted via query string
- **Location:** admin routes (around lines 206–213 and duplicate-products block)
- **Issue:** `?key=` can leak through logs/history.
- **Fix:** require header-based key only (`x-admin-key`/Bearer), deprecate query param.

---

## Final Decision by File

1. `scripts/etl/match-operators.ts` — **REQUEST CHANGES**
2. `scripts/import-ccc-data.ts` — **REQUEST CHANGES**
3. `scripts/migrations/006-ecosystem-integration.sql` — **APPROVE WITH CHANGES**
4. `services/api/src/db/schema.ts` — **APPROVE WITH CHANGES**
5. `services/api/src/index.ts` — **APPROVE WITH CHANGES**
6. `services/api/src/routes/catalog.ts` — **REQUEST CHANGES**
7. `services/api/src/routes/ccc.ts` — **REQUEST CHANGES**

---

## Must-fix before Railway deploy

1. Remove hardcoded DB URL/credential from `match-operators.ts`.
2. Implement real API key validation in `catalog.ts` (and rotate key if exposed anywhere).
3. Fix invalid SQL CTE syntax in `routes/ccc.ts` admin query.
4. Resolve `ccc_monthly_prices` contract drift across migration/schema/ETL/API in one coherent migration.
5. Ensure `gen_random_uuid()` prerequisites (`pgcrypto`) are guaranteed in target environments.
