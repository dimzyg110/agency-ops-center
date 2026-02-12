# Data Quality Infrastructure Summary

Date: 2026-02-12 UTC

## Quality score (first run)

Using the new scoring logic wired for `/api/v1/admin/data-quality`, current baseline is:

- **overall_score: 60/100**
- price_sanity: 100
- brand_quality: 0 (1,130 suspicious brand strings still detected)
- category_coverage: 100
- operator_data: 0 (181 operators with no price observations + 181 stale >7 days)
- ccc_cross_reference: 100

## Specific issues found and fixed

### 1) CCC cross-reference unit mismatch (P0)
Updated `GET /api/v1/ccc/cross-reference` to normalize comparison basis by category:

- flower: GLASS avg converted from per-unit to per-gram (`price / 3.5`)
- concentrate: compared per-gram (`price / 1.0`)
- edible/vape/preroll: compared per-unit
- added `comparison_basis` (`per_gram` or `per_unit`)
- added `methodology_note`

### 2) Data quality dashboard endpoint
Added `GET /api/v1/admin/data-quality` with:

- overall score
- timestamp
- check-level scores/issues for price sanity, brand quality, category coverage, operator data, CCC cross-reference

### 3) Price sanity utility
Created `services/api/src/utils/data-quality.ts` with:

- category price limits
- `isPriceSane(price, category)`
- standardized invalid-price reasons

### 4) Data freshness expansion
Extended `GET /api/v1/ccc/data-freshness` to include:

- operator coverage metrics
- sample operators with no observed prices

## CCC cross-reference before/after (flower)

Based on live DB verification query:

- CCC flower avg (per gram): **$4.04/g**
- GLASS flower avg old comparison (per unit): **$35.26**
- **Old markup:** **772.8%** (unit mismatch)

After conversion to per-gram using 3.5g baseline:

- GLASS flower avg converted: **$10.08/g**
- **New markup:** **149.5%**

## Bad prices removed

Ran DB cleanup:

- `DELETE FROM prices WHERE price = 0;` → 0 rows
- `DELETE FROM prices WHERE price > 500;` → **26 rows removed**

Post-check:

- prices = 0: 0
- prices > 500: 0

## Infrastructure created

### Code
- `services/api/src/routes/ccc.ts`
  - fixed cross-reference methodology
  - added `/admin/data-quality`
  - expanded `/ccc/data-freshness`
- `services/api/src/utils/data-quality.ts`
  - sanity-check utility
- `scripts/daily-scrape.ts`
  - daily orchestrator stub for Dutchie + Weedmaps runs
  - logs to `scrape_runs`
  - computes quality score and alerts below threshold

### SQL / DB
Applied `scripts/migrations/003-data-quality-infra.sql`:

- created/extended `scrape_runs` fields (`source`, `products_upserted`, `errors`, `quality_score`)
- created index `idx_prices_operator_product_date`
- created view `daily_price_averages`

## What still needs daily cron (Randy approval)

1. Add scheduler entry to run `scripts/daily-scrape.ts` once per day.
2. Confirm runtime env vars in cron context:
   - `DATABASE_URL`
   - `QUALITY_ALERT_THRESHOLD` (optional)
3. Wire low-quality alert destination (Slack/email/SMS) from the script warning path.
4. Validate scraper execution time windows and retries before production cron rollout.
