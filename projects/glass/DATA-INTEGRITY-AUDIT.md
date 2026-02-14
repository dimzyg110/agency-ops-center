# GLASS Repo Audit — Part 3: Scraper Pipeline & Data Integrity

Date: 2026-02-14 (UTC)
Repo audited: `/data/workspace/projects/glass/src/`

---

## Task 1 — Scraper Code Review

## 1) `scripts/scrape-jane.ts`

### Store discovery (slug source)
- Uses `JaneClient.discoverMAStores()` unless `--skip-discovery` is passed.
- Discovery result is persisted to `scripts/jane-slugs.json` via `saveStores()`.
- With `--skip-discovery`, it loads from `--slugs-file` (default `scripts/jane-slugs.json`).

### Data fetch path (Algolia via browser context)
- `scrape-jane.ts` delegates to `scripts/lib/jane-client.ts`.
- `JaneClient` launches Playwright Firefox and performs Cloudflare warmup by visiting:
  - `https://www.iheartjane.com/`
  - `https://search.iheartjane.com/`
- Algolia requests are then sent through `page.evaluate(fetch(...))` in browser context (`BrowserProxy.browserFetch()`), not raw Node HTTP.
- Queries:
  - `stores-production` for stores
  - `menu-products-production` for per-store products

### Normalize + DB write flow
- Parse: `parseJaneProducts(hits, slug, storeName)`
- Normalize: `normalizeProduct(parsed)`
- SKU/GPID: explicitly re-assigned with `makeSKU(brand, productName, weightGrams, category)`
- Filters out non-positive prices.
- DB writes (when `--db`):
  1. `upsertOperator('jane', ...)`
  2. `upsertSource(..., 'jane')`
  3. `createScrapeJob(...)`
  4. per product: `upsertProduct(...)` + `insertPrice(..., parser_type='jane_algolia_v1')`
  5. `completeScrapeJob(...)`, `completeScrapeRun(...)`

### Current slug count
- `scripts/jane-slugs.json`: **39**

---

## 2) `scripts/scrape-leafly.ts`

### HTTP-based vs browser
- Yes, script path is **HTTP-first**; no Playwright/browser dependency in this script.
- Uses `scripts/lib/leafly-client.ts`:
  - Discovery via HTML fetch and parsing ld+json from listing pages.
  - Product fetch via Leafly API: `consumer-api.leafly.com/.../menu_items`.

### Exponential backoff / Cloudflare behavior
- Implemented in `fetchJson()` in `leafly-client.ts`:
  - Up to **8 attempts**.
  - Retries on `429`, `503`, and retriable network errors.
  - Exponential backoff: `2s * 2^(attempt-1)`, capped at `60s`, with jitter.
- Also has global adaptive throttle state:
  - `penaltyMs` increases on 429, decays on success.
  - Applied before all requests and pagination calls.

### Normalize + DB write flow
- Parse: `parseLeaflyMenuItems(slug, operatorName, rawItems)`
- Normalize: `normalizeProduct`
- DB writes mirror Jane pattern with parser type `leafly_ssr_v1`.

### Current slug count
- `scripts/leafly-slugs.json`: **292**

---

## 3) `scripts/scrape-weedmaps.ts`

### Playwright Firefox + pagination
- Uses Playwright Firefox directly (`firefox.launch({ headless: true })`).
- Has internal `WeedmapsBrowser` wrapper with:
  - tab create/navigate/snapshot/click/scroll
  - browser health checks/re-init
- Pagination logic in `scrapePaginatedMenu()`:
  - Extract product count hint from snapshot text
  - Compute expected pages (24 per page, max 50)
  - Iterate `?page=N`, retry each page up to 3 times with backoff
  - Deduplicate by product href

### Age gate handling
- `dismissWeedmapsInterstitials()` attempts to click:
  - age gate buttons (`Yes, let me in` patterns)
  - cookie accept buttons
- Re-runs interstitial dismissal when snapshot indicates gate/redirect.
- Gate/redirect/rate-limit/no-menu detection is text-heuristic based from snapshots (`isLikelyAgeGateOrRedirect`, `isLikelyRateLimit`, `isLikelyNoMenu`).

### Why high Railway failure ("79%" asked)
Code-level risk factors observed:
1. **No anti-detection layer in script** (plain Playwright Firefox), so more vulnerable to Weedmaps anti-bot/redirect/rate-limit behavior.
2. **Snapshot-text heuristic parsing** can miss products if UI markup/content changes.
3. **Heavy per-store pagination** and long flows increase timeout/failure surface (`STORE_TIMEOUT_MS=300000`, page retries, many navigations).
4. **Frequent no-menu / 0-products outcomes** can be false negatives from blocked or partially rendered pages.
5. **Recovery churn** (`ensureHealthy` and job resets) indicates unstable long-running browser sessions.

Observed DB evidence (recent history) suggests severe failure rates in Railway runs (often >90% in older runs), dominated by failed jobs and "No products found"/no-menu style errors.

### Current slug count
- `scripts/weedmaps-slugs.json`: **282**

---

## 4) `scripts/scrape-dutchie.ts`

### BrowserPool approach
- Uses `scripts/lib/browser-pool.ts` (HTTP client to external browser service), not local Playwright pages directly.
- `BrowserPool` talks to endpoints like:
  - `POST /tabs`
  - `POST /tabs/{id}/navigate`
  - `GET /tabs/{id}/snapshot`
  - `POST /tabs/{id}/scroll`
- Parses products from accessibility snapshot text (`parseProductsFromSnapshot`).

### Railway browser service dependency
- `BrowserPool` base URL defaults to `process.env.CAMOFOX_URL` or `http://localhost:9377`.
- This creates an external runtime dependency on an available browser microservice (Railway roviq-browser style setup).
- Script creates per-process `userId/sessionKey` to avoid stale session collisions.

### Current slug count
- `scripts/dutchie-slugs.json`: **235**

---

## 5) Shared library review: `scripts/lib/`

### What’s in shared lib
- `db.ts`: PG pool + upsert/insert + scrape run/job lifecycle.
- `normalizer.ts`: category normalization, weight parsing, brand normalization, GPID/SKU generation (`makeSKU`).
- `logger.ts`: structured JSON logs.
- `types.ts`: parser/scraper domain types.
- `config.ts`: constants (paths, categories/cities, env defaults).
- Platform clients/parsers:
  - `jane-client.ts`, `jane-parser.ts`
  - `leafly-client.ts`, `leafly-parser.ts`
  - `weedmaps-parser.ts`
  - `browser-pool.ts`, `parser.ts`
  - `brand-filter.ts`

### DB connection parameterization check
- `scripts/lib/db.ts` uses parameterized queries (`$1..$n`) consistently for all dynamic values.
- `Pool` uses `DATABASE_URL` and sets `SET search_path TO public` on connect.
- SSL toggles by `NODE_ENV` (`rejectUnauthorized: false` in production).

### GPID format check (`makeSKU` / `normalizeName`)
- `makeSKU` generates deterministic IDs in format: `GPID-<12 hex>` from SHA-256 hash of:
  - normalized brand
  - normalized name
  - normalized weight
  - normalized category
- `normalizeName` function does **not** exist in current `normalizer.ts`; name normalization is inlined within `makeSKU`.
- Current implementation is internally consistent with hash-based GPID format, but there is interface drift in Railway wrappers (see Task 3) suggesting potential divergence risk if wrappers call a different signature.

---

## Task 2 — Data Integrity Check (Railway Postgres)

DB used:
`postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway`

All sessions executed with:
`SET search_path TO public;`

## Query results

1. **Products with no prices**
- Query: `SELECT COUNT(*) ... LEFT JOIN prices ... WHERE pr.id IS NULL`
- Result: **20**

2. **Prices with no product**
- Query: `SELECT COUNT(*) FROM prices WHERE product_id NOT IN (SELECT id FROM products)`
- Result: **0**

3. **Duplicate SKUs**
- Query: `SELECT sku, COUNT(*) ... HAVING COUNT(*) > 1 ...`
- Result: **none returned (0 rows)**

4. **Products per platform**
- Query by `sources.source_type`
- Results:
  - `dutchie`: **51,412**
  - `jane`: **6,273**
  - `leafly`: **44,730**
  - `menu`: **35**
  - `weedmaps`: **60,206**

5. **Price freshness**
- `dutchie`: newest `2026-02-13 14:35:21+00`, oldest `2026-02-05 15:25:11+00`
- `jane`: newest `2026-02-13 22:53:20+00`, oldest `2026-02-13 14:25:39+00`
- `leafly`: newest `2026-02-14 00:38:32+00`, oldest `2026-02-13 14:24:47+00`
- `menu`: newest `2026-02-12 00:47:04+00`, oldest `2026-02-05 02:31:14+00`
- `weedmaps`: newest `2026-02-14 04:31:42+00`, oldest `2026-02-12 06:45:29+00`

6. **Null/empty brands**
- Query: `SELECT COUNT(*) FROM products WHERE brand IS NULL OR brand = ''`
- Result: **61,707**

7. **Null/empty categories**
- Query: `SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''`
- Result: **0**

8. **Brand authority health**
- Query over `brand_authority`
- Result:
  - `total`: **1,001**
  - `verified`: **1,001**
  - `multi_platform (platform_count>=3)`: **308**

9. **Parsed products status**
- Requested query failed: column `status` does not exist in `parsed_products`.
- Actual status-like column is `validation_status`.
- Alternate result (`validation_status`):
  - `accepted`: **1,419**
  - `needs_review`: **616**
  - `rejected`: **86**

10. **GPID verified count**
- Requested query failed: column `verified` does not exist in `canonical_products`.
- `canonical_products` currently has columns like `gpid`, `confidence_avg`, `is_active`, etc., but no `verified` boolean.

### Schema mismatch note
Queries #9 and #10 in the prompt do not match current public schema names.

---

## Task 3 — Scripts vs Railway `scrapers/{name}/index.ts`

## High-level comparison

### Are they the same code?
- **No.** They are parallel implementations, not identical copies.

### Wrappers around scripts?
- **Partially.** Railway services import some shared parser/normalizer modules from `../scripts-lib/*`, but orchestration/runtime logic is separate and diverged.

### Completely different implementations?
- **For control flow/runtime behavior: yes, significantly different.**

### Source of truth?
- Operationally, `scripts/scrape-*.ts` appears to be the practical source of truth for successful data ingestion.
- `scrapers/*/index.ts` is a separate deployment path with drift and added complexity (run-lock/timeouts/notifications, different browser assumptions).

## Per-platform divergence

### Jane
- Similar algorithm (Algolia via browser-evaluated fetch), but Railway version has embedded proxy + service lifecycle wrappers.
- Notable drift risk: Railway Jane calls `makeSKU(..., 'JANE')` (5 args) while script version uses 4-arg `makeSKU` signature.

### Leafly
- Script: HTTP-first + robust adaptive throttling/backoff in `leafly-client.ts`.
- Railway service: browser-first (CamoFox required) + browser API calls, direct API fallback.
- This is a major strategy divergence.

### Weedmaps
- Script: Playwright Firefox + snapshot parsing + retry/error categorization.
- Railway service: CamoFox-first, different extraction strategy (`page.evaluate` on link selectors), simpler quality metrics.
- Substantially different failure modes/behavior.

### Dutchie
- Script: BrowserPool HTTP service (`browser-pool.ts`) over accessibility snapshots + category traversal.
- Railway service: CamoFox Playwright contexts with shard parallelism and different URL pattern (`embedded-menu/{slug}`), not the same BrowserPool implementation.

---

## Key integrity risks identified

1. **Massive null/empty brand count** in `products` (**61,707**) despite brand authority table health.
2. **Schema drift** between expected analytics queries and live schema (`status` vs `validation_status`, missing `canonical_products.verified`).
3. **Dual implementation drift** between local scripts and Railway service scrapers increases maintenance and correctness risk.
4. **Weedmaps reliability instability** in historical run data (high failed job volume; many "No products found" / no-menu failures).

---

## Quick recommendations

1. **Consolidate source of truth**: pick either `scripts/*` or `scrapers/*` runtime per platform and deprecate the other path.
2. **Fix query contract drift** by updating analytics queries to current schema (or restoring expected columns/views).
3. **Brand backfill pass** for null brands using parser raw payload + authority mapping.
4. **Weedmaps hardening**: improve anti-bot strategy consistency and reduce snapshot-heuristic fragility.
5. **Add parity tests** to ensure Railway wrapper behavior matches script behavior (same slug in, comparable product/price out).
