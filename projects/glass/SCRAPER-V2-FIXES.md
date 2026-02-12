# SCRAPER V2 Critical Fixes (2026-02-12)

Implemented all 5 requested critical fixes across scraper/runtime, DB persistence, and Drizzle schema alignment.

## 1) `src/scripts/lib/parser.ts` — **C1 Brand Parsing + C5 Brand Quality Signals**

### What changed
- Added `NON_BRAND_TOKENS` blocklist for known non-brand cannabinoid markers:
  - `THC, CBD, TAC, THCA, CBN, CBG, CBC, CBDA, CBGA, DELTA 8, DELTA 9`
- Reworked `parseBrandAndName` logic:
  1. First tries Dutchie pipe format (`Brand | Product Name | Details`) and uses first segment if valid.
  2. Falls back to contextual extraction around weight + strain/cannabinoid markers (captures real brands like `Float` in NETA rows).
  3. Uses uppercase fallback only as final fallback, filtered by blocklist.
- Added brand validation helper `isInvalidBrandCandidate` to prevent cannabinoid tokens from being accepted as brands.
- Added `brandParseFailed` output flag from parser.
- Expanded strain extraction to include `Hybrid-Sativa` and `Hybrid-Indica` forms.

### Why
- Fixes incorrect brand assignment to cannabinoid tokens (e.g. THC/CBD/TAC), the highest-priority data quality issue.
- Improves SKU stability because SKU key depends on brand.

---

## 2) `src/scripts/lib/db.ts` — **C2 Price Idempotency + C3 Auto-Resume Helpers + C5 Job Metrics**

### What changed
- `insertPrice` now uses idempotent upsert behavior:
  - `ON CONFLICT (product_id, source_id, operator_id, (scraped_at::date)) DO UPDATE`
  - Updates latest price snapshot fields (`price`, `price_per_gram`, `weight_grams`, `confidence`, `raw_data`, etc.)
- Added `getActiveRunForToday(platform)`:
  - Finds most recent `scrape_runs` row for today where `status <> 'completed'`.
- Added `sourceHasHistoricalData(sourceId)`:
  - Used by quality guardrails to detect suspicious category coverage against stores with prior data.
- Extended `completeScrapeJob`:
  - Adds `quality_metrics` JSON persistence on scrape job completion.

---

## 3) `src/scripts/scrape-dutchie.ts` — **C3 Auto-Resume + C5 Fail-Fast Guardrails**

### What changed
- Auto-resume behavior implemented (no flag required):
  - If DB mode is enabled, startup now checks for today’s non-completed run and reuses it.
  - Loads completed source IDs from that run and skips already-succeeded stores.
  - `--resume` remains supported as explicit override.
- Added per-store historical-data lookup (`sourceHasHistoricalData`) and task propagation.
- Added parser quality tracking:
  - Counts `brandParseFailures` based on parser confidence signal (`brandParseFailed`, empty/unknown brand).
- Added quality guardrails and job metrics:
  - `quality_metrics` now computed and persisted per job:
    - `categoriesAttempted`
    - `categoriesWithProducts`
    - `totalProducts`
    - `brandParseFailures`
  - If **0 products across all categories**, job is marked `failed` (fail-fast).
  - If **>50% categories return 0 products** and store has historical prior data, marks run as suspicious via error log message.

---

## 4) `src/services/api/src/db/schema.ts` — **C4 Schema Drift Fix**

### What changed
Aligned Drizzle schema to migration reality + missing scraper columns:

- `operators`
  - `license_number` is now nullable (removed `.notNull()`).
  - Added missing columns: `platform`, `platform_slug`, `metadata`.
- Added `scrape_runs` table definition.
- `scrape_jobs`
  - Added `run_id` FK to `scrape_runs`.
  - Added `quality_metrics` JSONB.
- `products`
  - Added `weight_grams`, `strain_type`, `subcategory`.
- `prices`
  - Added `run_id`, `price_per_gram`, `weight_grams`, `menu_type`.
  - Added scraper-aligned indexes for time-series access patterns.

---

## 5) `src/scripts/migrations/002-price-idempotency.sql` — **C2 Migration (plus required C5 schema support)**

### New migration created
- Added unique daily idempotency index:
  - `idx_prices_daily_product_source_operator` on `(product_id, source_id, operator_id, (scraped_at::date))`
- Added `scrape_jobs.quality_metrics JSONB` column.
- Added `prices.run_id` FK column for schema parity with Drizzle and run lineage.

---

## 6) `src/scripts/lib/types.ts` — **Type Updates for Guardrails**

### What changed
- Added `brandParseFailed?: boolean` to `ParsedProduct`.
- Added `ScrapeQualityMetrics` type used in DB + scraper orchestration.

---

## Notes
- The new brand parsing approach prioritizes Dutchie’s pipe format and only falls back to regex heuristics when needed.
- Price insertions are now idempotent per product/source/operator/day, preventing duplicate rows on same-day reruns.
- Auto-resume now activates by default in DB mode, matching V2 design intent.
