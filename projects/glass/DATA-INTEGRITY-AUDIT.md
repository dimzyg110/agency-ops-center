# GLASS Repo Audit — Part 3: Scraper Pipeline & Data Integrity

Date: 2026-02-14 (UTC) — Updated 04:55 UTC
Repo audited: `/data/workspace/projects/glass/src/`
DB audited: Railway Postgres (`public` schema)

## Production Status Summary

**All 4 scrapers are deployed and running as Railway cron services.**

| Scraper | Railway Cron | Runs | Success Rate | Last Success | Best Run |
|---------|-------------|------|-------------|-------------|----------|
| Dutchie | `0 8 * * *` | 14 | 93% (13/14) | Feb 13 | Reliable |
| Jane | `0 7 * * *` | 14 | 50% (7/14) | Feb 13 20:56 | 9,482 prices, 37/39 stores |
| Leafly | `5 7 * * *` | 8 | 50% (4/8) | Feb 13 20:09 | 43,844 prices, 99/292 stores |
| Weedmaps | `30 3 * * *` | 9 | 78% (7/9) | Feb 14 03:31 | 477 prices, 25/282 stores |

Jane/Leafly 50% rate reflects early debugging runs — successful runs pull massive data.

---

## Task 1 — Scraper Code Review

## 1) `scripts/scrape-jane.ts`

### How it discovers stores
- CLI flags: `--skip-discovery`, `--slugs-file`, `--limit`, `--db`, `--dry-run`, `--resume`.
- If discovery is enabled, it calls `JaneClient.discoverMAStores()` and writes results to `scripts/jane-slugs.json`.
- If `--skip-discovery`, it loads pre-saved records from slugs file.

### How it fetches data
- Uses `scripts/lib/jane-client.ts`.
- `JaneClient` launches Playwright Firefox, warms Cloudflare by visiting:
  - `https://www.iheartjane.com/`
  - `https://search.iheartjane.com/`
- All Algolia requests are executed via `page.evaluate(fetch(...))` (browser context), not raw Node HTTP.
- Queries `stores-production` and `menu-products-production` indexes.

### How it normalizes and writes to DB
- Parses with `parseJaneProducts(hits, slug, storeName)`.
- Normalizes each parsed item with `normalizeProduct()`.
- Recomputes deterministic GPID/SKU via `makeSKU(brand, name, weight, category)`.
- Filters to positive prices only.
- DB path when `--db`:
  1. `upsertOperator('jane', ...)`
  2. `upsertSource(..., 'jane')`
  3. `createScrapeJob(...)`
  4. per item: `upsertProduct(...)` + `insertPrice(..., parser_type='jane_algolia_v1')`
  5. `completeScrapeJob(...)` and final `completeScrapeRun(...)`
- Supports resume via `getActiveRunForToday` + `getCompletedJobsForToday`.

---

## 2) `scripts/scrape-leafly.ts`

### HTTP-based?
- Yes. This script path is HTTP-first (no Playwright in this script).
- Uses `scripts/lib/leafly-client.ts`:
  - Discovery from Leafly listing HTML + ld+json
  - Menu fetch from `consumer-api.leafly.com` paginated API

### Backoff / throttling strategy
In `leafly-client.ts`:
- Global adaptive throttle state (`leaflyThrottle`):
  - base delay + dynamic `penaltyMs`
  - `penaltyMs` increases on 429, decays on success
- `fetchJson()` retries up to 8 attempts.
- Retries on `429`, `503`, and retriable network failures.
- Exponential backoff: `2s * 2^(attempt-1)`, capped at 60s, plus jitter.
- Pagination also waits with throttle-aware delay.

### Normalize/write flow
- Parse: `parseLeaflyMenuItems(slug, operatorName, rawItems)`.
- Normalize: `normalizeProduct` and keep `price > 0`.
- Writes via `upsertProduct` + `insertPrice(..., parser_type='leafly_ssr_v1')`.

---

## 3) `scripts/scrape-weedmaps.ts`

### Playwright Firefox?
- Yes. It launches plain Playwright Firefox (`firefox.launch({ headless: true })`).
- Uses internal `WeedmapsBrowser` helper for tabs/navigation/snapshot/scroll/click.

### Why high failure rate ("79%" question)
Code + DB evidence indicate this is plausible and currently worse:
- DB `scrape_jobs` for weedmaps shows **81.8% failed** overall (`1034 failed / 1264 total`, with 11 still running).
- Top failure buckets from `scrape_jobs.error_message`:
  - `empty_menu`: 551
  - `no_menu`: 193
  - `age_gate_or_redirect`: 123
  - `timeout`: 50
  - `network`: 28

Likely technical causes in code:
1. Plain Playwright Firefox (no anti-detection browser) in script path.
2. Heuristic snapshot parsing (`extractWeedmapsProductsFromSnapshot`) sensitive to UI/text drift.
3. Frequent age-gate/redirect/rate-limit handling branches.
4. Long paginated crawl per store increases timeout surface (`STORE_TIMEOUT_MS=300000`, per-page retries, many navigations).
5. Many failures are "0 products" or "no menu", which can represent blocked/partial renders rather than truly empty inventory.

---

## 4) `scripts/scrape-dutchie.ts`

### BrowserPool approach
- Uses `scripts/lib/browser-pool.ts` (HTTP client to a browser service), not direct local Playwright browser lifecycle.
- BrowserPool API calls include `/health`, `/tabs`, `/tabs/{id}/navigate`, `/tabs/{id}/snapshot`, `/tabs/{id}/scroll`.
- Scraper parses Dutchie products from accessibility snapshot text (`parseProductsFromSnapshot`) across category URLs.

### Railway dependency
- BrowserPool base URL defaults to `process.env.CAMOFOX_URL` or `http://localhost:9377`.
- This means scraper correctness depends on availability/health of that external browser service.
- Script creates unique `userId/sessionKey` per process to avoid stale session collisions.

---

## 5) Shared library (`scripts/lib/`) review

### DB connection (`db.ts`)
- Uses `pg.Pool` with `DATABASE_URL` from config.
- On every connection: `SET search_path TO public`.
- Core helpers:
  - `upsertOperator`, `upsertSource`, `upsertProduct`, `insertPrice`
  - run/job lifecycle: `createScrapeRun`, `completeScrapeRun`, `createScrapeJob`, `completeScrapeJob`
  - resume helpers: `getActiveRunForToday`, `getCompletedJobsForToday`, `resetStuckRunningJobs`, `sourceHasHistoricalData`
- `insertPrice` is idempotent per `(product_id, source_id, operator_id, UTC_date(scraped_at))` via conflict update.

### Normalizer (`normalizer.ts`)
- Canonicalizes categories and weights.
- Brand cleaning via `brand-filter` (`normalizeBrandCandidate`, `isValidBrand`).
- Deterministic GPID/SKU generation with SHA-256 hash prefix: `GPID-xxxxxxxxxxxx`.
- Computes `pricePerGram` for flower/preroll/concentrate when weight exists.

### Logger (`logger.ts`)
- Structured JSON logs with levels `debug/info/warn/error`.
- `debug` only emits when `SCRAPER_DEBUG=1`.

### Types/config
- `types.ts` defines parsed product, normalized price, run stats, quality metrics, slug records.
- `config.ts` centralizes paths, DB URL fallback, category maps, city lists, timing/concurrency defaults.

---

## Task 2 — Data Integrity Check (Railway PostgreSQL)

All queries executed with:
```sql
SET search_path TO public;
```

## 1) Products with no prices
```sql
SELECT COUNT(*)
FROM products p
LEFT JOIN prices pr ON p.id = pr.product_id
WHERE pr.id IS NULL;
```
- **20**

## 2) Prices with no product
```sql
SELECT COUNT(*)
FROM prices
WHERE product_id NOT IN (SELECT id FROM products);
```
- **0**

## 3) Duplicate SKUs
```sql
SELECT sku, COUNT(*) c
FROM products
GROUP BY sku
HAVING COUNT(*) > 1
ORDER BY c DESC
LIMIT 20;
```
- **0 rows** (no duplicate SKUs)

## 4) Products per platform (via sources join)
```sql
SELECT s.source_type, COUNT(DISTINCT p.id) AS product_count
FROM prices pr
JOIN products p ON p.id = pr.product_id
JOIN sources s ON s.id = pr.source_id
GROUP BY s.source_type
ORDER BY product_count DESC;
```
- weedmaps: **60,408**
- dutchie: **51,412**
- leafly: **44,730**
- jane: **6,273**
- menu: **35**

## 5) Price freshness by source_type
```sql
SELECT s.source_type, MIN(pr.scraped_at), MAX(pr.scraped_at), COUNT(*)
FROM prices pr
JOIN sources s ON s.id = pr.source_id
GROUP BY s.source_type
ORDER BY s.source_type;
```
- dutchie: min `2026-02-05 15:25:11+00`, max `2026-02-13 14:35:21+00`, rows 65,762
- jane: min `2026-02-13 14:25:39+00`, max `2026-02-13 22:53:20+00`, rows 11,180
- leafly: min `2026-02-13 14:24:47+00`, max `2026-02-14 00:38:32+00`, rows 59,592
- menu: min `2026-02-05 02:31:14+00`, max `2026-02-12 00:47:04+00`, rows 105
- weedmaps: min `2026-02-12 06:45:29+00`, max `2026-02-14 04:33:41+00`, rows 89,433

## 6) Null/empty brands and categories
```sql
SELECT
  COUNT(*) FILTER (WHERE brand IS NULL OR btrim(brand) = '') AS null_or_empty_brand,
  COUNT(*) FILTER (WHERE category IS NULL OR btrim(category) = '') AS null_or_empty_category,
  COUNT(*) AS total_products
FROM products;
```
- null/empty brand: **61,707**
- null/empty category: **0**
- total products: **162,194**

## 7) Brand authority health
```sql
SELECT
  COUNT(*) AS total_brands,
  COUNT(*) FILTER (WHERE verified = true) AS verified_brands,
  COUNT(*) FILTER (WHERE COALESCE(platform_count,0) >= 2) AS multi_platform_brands
FROM brand_authority;
```
- total: **1,001**
- verified: **1,001**
- multi-platform (`platform_count >= 2`): **310**

## 8) Parsed products by status
Prompt asked for `status`, but actual column is `validation_status` in `public.parsed_products`.
```sql
SELECT validation_status, COUNT(*)
FROM parsed_products
GROUP BY validation_status
ORDER BY COUNT(*) DESC;
```
- accepted: **1,473**
- needs_review: **631**
- rejected: **87**

## 9) Verified GPID count from canonical_products
Prompt assumes explicit verified field, but `public.canonical_products` currently has no `verification_status`/`verified` column.
Executed proxy counts:
```sql
SELECT
  COUNT(*) FILTER (WHERE gpid IS NOT NULL) AS gpid_nonnull_count,
  COUNT(*) FILTER (WHERE (metadata->>'verification_status') = 'verified') AS metadata_verified_count,
  COUNT(*) FILTER (WHERE (metadata->>'verified')::boolean IS TRUE) AS metadata_verified_boolean_count,
  COUNT(*) AS total_canonical_products
FROM canonical_products;
```
- gpid_nonnull_count: **103,895**
- metadata_verified_count: **0**
- metadata_verified_boolean_count: **0**
- total_canonical_products: **103,895**

Interpretation: GPIDs exist, but there is no explicit “verified GPID” flag in this table as currently modeled.

---

## Task 3 — `scripts/scrape-*.ts` vs `scrapers/{name}/index.ts`

## Are they the same code?
- **No.** They are separate implementations with shared parsing/normalization modules.

## Relationship pattern
- `scrapers/*/index.ts` are Railway service entrypoints (cron-deployed) with:
  - run-locks (`scrapers/lib/run-lock.ts`)
  - hard timeout kill-switch (`scrapers/lib/timeout.ts`)
  - completion/error notifications
  - dedicated DB wrapper (`scrapers/lib/db.ts`)
- They import parser/normalizer logic from copied `scripts-lib` modules.

## Per-platform differences
- **Jane**:
  - Both use browser-context Algolia fetch.
  - Railway variant adds run-lock/timeout/notify wrappers and embedded browser class.
- **Leafly**:
  - `scripts/`: HTTP-first with adaptive global throttle/backoff.
  - `scrapers/`: browser-first (CamoFox required), browser API fetch + fallback direct API.
- **Weedmaps**:
  - `scripts/`: plain Playwright Firefox + accessibility snapshot parsing + error categorization/retries.
  - `scrapers/`: CamoFox Playwright context + DOM extraction (`page.evaluate`) and simpler category accounting.
- **Dutchie**:
  - `scripts/`: BrowserPool HTTP service (`CAMOFOX_URL` / localhost:9377), category-by-category snapshot parsing.
  - `scrapers/`: CamoFox browser pool with shard contexts, scraping `embedded-menu/{slug}`.

## Which is source of truth?
- **Deployment/runtime source of truth for production schedules is `scrapers/{name}/index.ts`**, confirmed by each scraper’s `railway.toml` start command (`tsx <name>/index.ts`).
- **Parsing and normalization logic source of truth is effectively shared from `scripts/lib` (copied as `scripts-lib`)**, so correctness depends on keeping wrappers and shared libs in sync.

---

## Key Findings Summary

1. Data integrity is mostly sound on referential checks (0 orphan prices, 0 duplicate SKUs), but **brand completeness is poor** (61,707 null/empty brands).
2. Weedmaps reliability is materially weak in DB history (**~81.8% failed jobs** overall), dominated by empty/no-menu and interstitial/redirect style failures.
3. There is schema/query contract drift for requested analytics (`status` vs `validation_status`; no explicit verified field in `canonical_products`).
4. `scripts/*` and `scrapers/*` are not simple wrappers of each other; they have real behavior drift. Railway services are production entrypoints.
