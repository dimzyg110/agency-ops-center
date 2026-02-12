# PHASE 1 — Data Foundation Fix Summary

Date: 2026-02-12 (UTC)
Commit: `45ed1cf` (pushed to `origin/main`)

## 1) Brand Cleanup

### What I did (DB)
Ran production cleanup SQL against `products.brand`:
- Nullified stock/UI/artifact brands (e.g., `stock. Order soon.`, `Medical patients only`, pipe fragments, category/format junk)
- Nullified numeric-only and short invalid brands
- Nullified brands containing pipe artifacts (`%|%`)
- Normalized `Cali-Blaze` + `Cali Blaze` -> `Cali Blaze`

### Rows affected
- `brand_nullified`: **17,588**
- extra pipe/weight artifact null pass: **5,695**
- `Cali Blaze` normalization: **250**

### Verification
- Garbage pattern count after cleanup: **0**
- Top brands no longer include stock/UI strings
- Current brand distribution query shows real brands at top

## 1b) Dutchie scraper guardrails (code)

Updated brand filtering so garbage does not re-import:
- `services/scrape/src/parsers/dutchie.ts`
  - Added `GARBAGE_BRAND_PATTERNS`
  - Added `normalizeBrandValue()`
  - Applied filter in both LD+JSON and state blob parsers
- `services/scrape/src/normalizer.ts`
  - Added strict brand normalization/filters (stock warnings, category words, numeric, pipe junk)
- `scripts/scrape-dutchie-ma.ts`
  - Added `sanitizeBrand()` to reject stock/UI/category artifact brands
  - Ensured rejected brands persist as `NULL` in generated SQL

---

## 2) Category Normalization

### What I did (DB)
Normalized category values to canonical lowercase singular forms:
- `products.category`
- `margin_rules.category`

Canonical set enforced:
- `flower, edible, vape, concentrate, preroll, tincture, topical`

### Verification
`products` categories now:
- flower 42522
- preroll 21244
- vape 14527
- edible 12693
- concentrate 4992
- tincture 3
- topical 3

`margin_rules` categories now canonical as well.

### Code alignment
- `services/api/src/routes/ccc.ts` cross-reference now queries `preroll` (not `pre-roll`) on GLASS side.
- `services/scrape/src/normalizer.ts` category map now normalizes pre-roll variants to `preroll`.
- `services/scrape/src/types.ts` updated category union to include `preroll`.

---

## 3) Kill Fake Review Scores

### What I did
In `services/api/src/routes/viz.ts`, removed fabricated random score:
- Replaced `3.8 + RANDOM() * 1.1`
- Now returns `NULL::float8 AS review_score`

### Verification
SQL in route no longer contains random score generation.

---

## 4) CCC Weekly Sales NULL issue

### Root cause found
`scripts/import-ccc-data.ts` was inserting weekly rows with all value columns hardcoded to `NULL`.
The source file `/data/workspace/projects/internal/newsletter/data/ccc/weekly_sales.json` currently contains `YearMonth + AverageRetailPriceperGm` (monthly avg retail price per gram), not weekly sales dollars/transactions.

### What I changed
- Updated importer to only upsert weekly rows when real value columns exist (`TotalSales`, `AdultUseSales`, `MedicalSales`, `TransactionCount` variants).
- Added proper conflict update for value columns.
- Deleted existing null-only placeholder rows from `ccc_weekly_sales`.

### Verification
- `ccc_weekly_sales` row count now: **0**
- Prevents continued insertion of null-only fake weekly series.

### Manual intervention still needed
Need correct CCC source endpoint/file for true weekly (or monthly sales) totals and transaction counts before reimport.

---

## 5) Plant Activity API surfaced

Added new endpoints in `services/api/src/routes/ccc.ts`:
- `GET /api/v1/ccc/plant-activity`
  - returns aggregated payload:
    - `monthly`
    - `category_breakdown`
    - `trend`
- `GET /api/v1/ccc/plant-activity/summary`
  - returns headline totals/date range/volume averages

### Verification (DB basis)
`ccc_plant_activity`:
- rows: **46,863**
- date range: **2018-11-20** to **2025-12-21**
- summed metric volume: **6,532,405,689.86**

---

## 6) Threats NOT NULL constraint on lat/lon

### What I did (DB)
Relaxed schema to support pending applications without coordinates:
- `ALTER TABLE threats ALTER COLUMN lat DROP NOT NULL;`
- `ALTER TABLE threats ALTER COLUMN lon DROP NOT NULL;`

### Verification
`information_schema.columns` now reports:
- `lat` -> `is_nullable = YES`
- `lon` -> `is_nullable = YES`

---

## Additional ccc cross-reference hardening

Updated `/ccc/cross-reference` query to:
- compare like-for-like units (`g` vs `ea`)
- use `price_per_gram` for `flower/preroll/concentrate`
- include `unit` in response
- keep only valid categories (`flower, preroll, vape, edible, concentrate`)

DB verification query returns all expected categories including `preroll`.

---

## Files changed

- `scripts/import-ccc-data.ts`
- `scripts/scrape-dutchie-ma.ts`
- `services/api/src/routes/ccc.ts`
- `services/api/src/routes/viz.ts`
- `services/scrape/src/normalizer.ts`
- `services/scrape/src/parsers/dutchie.ts`
- `services/scrape/src/types.ts`

---

## Issues encountered

1. `prices` table has no `category` column (category lives in `products`), so category normalization for prices is handled via product join semantics/API queries.
2. Existing `weekly_sales.json` source does not contain weekly sales totals/transactions — only monthly avg retail price per gram.
3. Local API TypeScript build command failed because `tsc` is missing in current environment path (`sh: 1: tsc: not found`), so route compilation was validated by diff/query logic rather than successful local build.

---

## Still needs manual intervention

1. **CCC weekly sales source correction**: wire importer to a true weekly/monthly sales revenue dataset with totals and transaction counts.
2. **Frontend handling for empty weekly-sales**: ensure dashboard displays honest "data unavailable/importing" state until source is fixed.
3. **Review pre-existing unstaged frontend modifications** in `apps/web` (not part of this commit):
   - `apps/web/src/api/client.ts`
   - `apps/web/src/pages/Market.tsx`
   - `apps/web/src/pages/MorningBrief.tsx`
   - `apps/web/src/components/DataFreshness.tsx` (untracked)
