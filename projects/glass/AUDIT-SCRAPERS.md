# GLASS Infrastructure Audit — Part 2: Scraper Pipeline + Parsers

Date: 2026-02-13 (UTC)
Scope audited:
- Scrapers: `scrape-dutchie.ts`, `scrape-weedmaps.ts`, `scrape-leafly.ts`, `scrape-jane.ts`
- Orchestration/wrappers: `daily-scrape.ts`, `run-daily-dutchie.sh`, `run-scrapers-sequential.ts`
- Parser/client libs: `parser.ts`, `weedmaps-parser.ts`, `leafly-client.ts`, `leafly-parser.ts`, `jane-client.ts`, `jane-parser.ts`, `browser-pool.ts`, `normalizer.ts`, `brand-filter.ts`, `config.ts`, `types.ts`, `db.ts`
- Legacy service: `src/services/scrape/`
- Docs: `scripts/SCRAPER-ARCHITECTURE.md`, `GLASS-MASTER-STRATEGY.md`

---

## Executive Summary

The current scraper stack is partially functional but not strategy-ready for a consumer-grade “Top 500 verified GPID” launch. The most important issues are:

1. **Cross-platform product matching is structurally broken** (operator and product identity model mismatch with strategy requirements).
2. **Weedmaps resume/snapshot skip logic can suppress entire runs** (observed `totalAttempted: 0`).
3. **Category normalization silently misclassifies Weedmaps wellness/accessories as flower**.
4. **Coverage gaps in source/category capture** (Dutchie scraper omits tinctures/topicals entirely).
5. **CamoFox failure handling is weak for mid-run outage scenarios** (health checks are non-blocking and not recovery-driving).
6. **Run orchestration files are stale/inconsistent with active pipeline**.

---

## Findings

### 1) Weedmaps snapshot skip can zero out runs and hide unfinished work
- **Severity**: Critical
- **Description**: `scrape-weedmaps.ts` uses `hasSnapshotData()` before enqueueing tasks. It treats any existing snapshot with parsed/normalized > 0 or `noMenu: true` as “done”, independent of run/job status.
- **Impact**: Entire runs can show `totalAttempted: 0` and silently skip stores that still need DB writes/retries. This directly compromises freshness and coverage.
- **Fix**:
  1. Make snapshot cache advisory only; DB job state should be source of truth.
  2. Gate skipping on successful scrape_job completion for current run (or explicit checkpoint table), not raw snapshot existence.
  3. Separate “no menu known” TTL cache from “already scraped in this run”.
- **Effort**: 4–8 hours

### 2) GPID strategy mismatch: current identity is hash-based and not strategy canonical
- **Severity**: Critical
- **Description**: `normalizer.ts::makeSKU()` generates `GPID-<hash>` from brand/name/weight/category. Strategy requires canonical, auditable GPIDs (`brand_slug_strain_weight_category`) + verification workflow. Current hash ID is opaque and not hand-verification-friendly.
- **Impact**: Cannot operationalize Top-500 hand-verified GPIDs, difficult QA/debug, weak explainability for consumer trust.
- **Fix**:
  1. Introduce explicit `gpid` model separate from technical `sku`.
  2. Add `products.gpid` + `gpid_verified` table and verifier metadata (`verified_by`, `verified_at`, confidence tier).
  3. Keep legacy SKU for backward compatibility; make GPID primary for comparison views.
- **Effort**: 12–24 hours

### 3) Operator deduplication across platforms does not exist
- **Severity**: Critical
- **Description**: `upsertOperator()` keys by synthetic `license_number = DISCOVERY-<slug>`, causing each platform slug to create separate operators for same business.
- **Impact**: Cross-platform matching and “same product across stores/platforms” logic is degraded; strategy objective (“consumer-side cross-platform GPID”) is blocked.
- **Fix**:
  1. Add canonical operator identity (license, normalized name+address, geocode).
  2. Build operator matching pipeline + manual override table.
  3. Refactor upsert to use canonical operator ID, platform slugs in child mapping table.
- **Effort**: 16–32 hours

### 4) Dutchie category coverage incomplete vs required taxonomy
- **Severity**: High
- **Description**: `DUTCHIE_CATEGORIES` only includes flower/preroll/vape/edible/concentrate. Required categories include tinctures/topicals.
- **Impact**: Missing product classes reduce consumer completeness and bias pricing intelligence.
- **Fix**:
  1. Add tincture/topical category routes for Dutchie where available.
  2. Track per-source category availability and explicit “not present” outcomes.
  3. Add coverage KPI by category.
- **Effort**: 6–12 hours

### 5) Weedmaps category normalization bug: wellness/accessories become flower
- **Severity**: High
- **Description**: `weedmaps-parser.ts` emits categories like `wellness`, `accessories`, `drink`; `normalizer.normalizeCategory()` lacks wellness/accessories mappings and defaults to `flower`.
- **Impact**: Wrong category analytics, wrong filters, possible false GPID clustering.
- **Fix**:
  1. Expand canonical taxonomy and map all scraper outputs explicitly.
  2. Replace default-to-flower with `unknown` + alert metric.
  3. Backfill recent records for corrected categories.
- **Effort**: 4–8 hours

### 6) CamoFox outage handling is detection-only, not self-healing
- **Severity**: High
- **Description**: `BrowserPool.ensureHealthy()` returns boolean but callers ignore result for recovery; if `localhost:9377` dies mid-run, errors cascade store-by-store.
- **Impact**: Large failure batches (`fetch failed`) and degraded run completion.
- **Fix**:
  1. On unhealthy status, short-circuit run or trigger controlled retry loop with circuit breaker.
  2. Add centralized restart/reinit hook and progressive backoff.
  3. Emit distinct outage event and halt after threshold.
- **Effort**: 6–10 hours

### 7) Jane browser tab leak on early fatal path
- **Severity**: High
- **Description**: `scrape-jane.ts` closes `JaneClient` only in successful tail of `main()`. If `main` throws early, finalizer only closes DB pool; tab is left for idle timeout.
- **Impact**: Resource leakage and potential session exhaustion on repeated failures.
- **Fix**: Wrap `JaneClient` lifecycle in `try/finally` inside `main()` and always call `jane.close()`.
- **Effort**: 1–2 hours

### 8) Resume logic inconsistent across scrapers
- **Severity**: High
- **Description**:
  - Dutchie resets stuck running jobs (`resetStuckRunningJobs`) and resumes robustly.
  - Weedmaps has retry + resume but conflicting snapshot skip.
  - Leafly/Jane do not reset stuck running jobs.
- **Impact**: Non-uniform recovery behavior and orphaned running jobs after crashes.
- **Fix**: Standardize run state machine and shared recovery utilities across all 4 scrapers.
- **Effort**: 6–12 hours

### 9) Orchestrator `daily-scrape.ts` is stale/broken versus active scripts
- **Severity**: High
- **Description**: Calls deleted `scripts/scrape-dutchie-ma.ts`; uses schema fields (`source`, `products_upserted`) inconsistent with current DB helper model (`platform`, `productsFound`).
- **Impact**: If used, daily orchestration will fail or write invalid run metadata.
- **Fix**:
  1. Either retire file and document as deprecated, or fully migrate to current script names/schema.
  2. Add smoke test in CI for orchestrator entrypoint.
- **Effort**: 3–6 hours

### 10) `run-scrapers-sequential.ts` targets non-existent build outputs
- **Severity**: Medium
- **Description**: Executes `./dist/scripts/scrape-dutchie.js` and `./dist/scripts/scrape-weedmaps.js`; `dist/scripts` not present.
- **Impact**: Runner fails if invoked.
- **Fix**: Use `tsx scripts/*.ts` or establish real build pipeline that emits these files.
- **Effort**: 1–2 hours

### 11) Leafly parser/category model still coarse for consumer-first product UX
- **Severity**: Medium
- **Description**: Leafly maps drink/beverage into `edible`; may be acceptable internally but conflicts with user-facing category specificity.
- **Impact**: Reduced filter precision and less trustworthy product grouping on consumer pages.
- **Fix**: Split `drink` as first-class category and keep crosswalk layer for analytics rollups.
- **Effort**: 2–4 hours

### 12) Weight extraction misses critical synonyms (e.g., “eighth”)
- **Severity**: Medium
- **Description**: `normalizeWeight()` covers `1/8 oz` but not textual synonym `eighth`; strategy explicitly cares about exact form-factor matching.
- **Impact**: Weight nulls inflate false matches and degrade price-per-gram consistency.
- **Fix**: Add normalized synonyms (`eighth`, `quarter`, `half`, etc.) + test fixtures for all required forms (`3.5g`, `1/8 oz`, `eighth`, `1g`, `0.5g`).
- **Effort**: 2–4 hours

### 13) Price extraction does not model sale/range/tier semantics consistently
- **Severity**: Medium
- **Description**:
  - Dutchie fallback extracts first `$` (may miss best tier).
  - Weedmaps captures first displayed price only.
  - Leafly/Jane rely on single fields per variant, limited promo semantics.
- **Impact**: “Cheapest price” can be wrong; undermines consumer trust and social cards.
- **Fix**:
  1. Add structured price model: list price, sale price, tier quantity, effective unit price.
  2. Preserve and surface promo flags + source evidence in raw_data.
  3. Rank by post-tax effective price per purchasable option.
- **Effort**: 10–20 hours

### 14) Brand cleaning can null out brands at DB layer
- **Severity**: Medium
- **Description**: `upsertProduct()` applies `cleanBrand()` and may persist `null` for invalid brands even when parser had a usable string.
- **Impact**: Brand-level analytics/matching suffer; GPID quality worsens.
- **Fix**: Persist both `raw_brand` and `normalized_brand`; avoid destructive nulling unless truly empty.
- **Effort**: 3–6 hours

### 15) CamoFox session collision risk (Weedmaps/Jane fixed user IDs)
- **Severity**: Medium
- **Description**: Weedmaps uses static `userId=glass-weedmaps` + day-based session key; Jane uses static `userId=jane-scraper`. Concurrent runs can interfere.
- **Impact**: Cross-run tab/session contamination and flaky failures.
- **Fix**: Include process/run-scoped session key and user namespace per invocation.
- **Effort**: 2–4 hours

### 16) Architecture doc is materially out of date
- **Severity**: Medium
- **Description**: `SCRAPER-ARCHITECTURE.md` says iHeartJane needs no browser and Leafly is CamoFox-first future work; actual implementation is opposite (Jane uses browser-proxied Algolia, Leafly already API-based).
- **Impact**: High operator confusion; wrong debugging/runbook actions.
- **Fix**: Update architecture doc to match code paths and failure playbooks.
- **Effort**: 2–3 hours

### 17) TypeScript compile hygiene for scripts package is weak
- **Severity**: Low
- **Description**: No dedicated scripts TS project setup; direct typecheck surfaces Node type config gaps (`@types/node` scope/config mismatch).
- **Impact**: Regressions can slip through until runtime.
- **Fix**: Add `scripts/tsconfig.json` + `npm run typecheck:scrapers` CI step.
- **Effort**: 2–4 hours

### 18) Legacy `services/scrape/` appears operationally dead for current stack
- **Severity**: Low
- **Description**: Current top-level Railway deploy points to `services/api/Dockerfile`. Active scraping flow is in `scripts/*`. `services/scrape/` has its own package, dist, and Railway file but no active integration in current app deployment path.
- **Impact**: Maintenance confusion, duplicate logic risk, stale assumptions (Firecrawl/queue model).
- **Fix**: Formally deprecate/archive or clearly label as legacy/experimental; remove from active docs.
- **Effort**: 2–6 hours

---

## Scraper-by-Scraper Health Notes

## Dutchie
- Runtime resilience: good attempts at timeout + per-store cleanup.
- Weakness: catastrophic CamoFox outage handling still causes long failure streaks.
- Resume: strongest implementation among four (`resetStuckRunningJobs`).
- DB writes: generally correct through `db.ts` with `search_path` set on pool connect.

## Weedmaps
- Strong retry/categorized errors and interstitial handling.
- Critical flaw: snapshot-based skip can bypass actual work and corrupt run semantics.
- DB writes: robust when task runs, but run may enqueue nothing due to skip logic.

## Leafly
- HTTP API path is simple and stable.
- Failure handling: store-level try/catch present, but no stuck-job reset.
- Category/price modeling too shallow for consumer-grade comparisons.

## Jane
- Browser-proxied Algolia approach is workable.
- Good throughput.
- Needs guaranteed browser cleanup and stronger retry/backoff around proxy evaluate.

---

## makeSKU()/GPID Specific Analysis

Current `makeSKU()` behavior:
- Generates deterministic hash key from `normalizeBrand + normalized name + weight + category`.
- `_platform` arg exists but is currently unused.

What to change for cross-platform GPID:
1. **Do not use platform in canonical identity** (already effectively true in current `makeSKU` implementation).
2. Introduce explicit `gpid` string format aligned with strategy (`brand_slug_strain_slug_weight_category`) and make it human-auditable.
3. Keep existing hash SKU as `legacy_sku` to avoid breaking historical foreign key joins.

What breaks if SKU format changes immediately:
- `products.sku` unique keys and all existing references will fragment.
- Historic `prices.product_id` linkage continuity can be lost if re-upsert creates new product rows.
- Downstream reports keyed by SKU will bifurcate.

Safe migration path:
- Add `gpid` column + backfill mapping table from old SKU.
- Keep SKU immutable for old records; gradually re-key app logic to GPID for comparisons.
- Add reconciliation job for candidate duplicates before consumer exposure.

---

## Data Pipeline Gaps vs Strategy

Relative to `GLASS-MASTER-STRATEGY.md` Top-500 consumer-first plan, pipeline is missing:

1. **Verified GPID workflow** (review queue, confidence tiers, human verification metadata).
2. **Operator canonicalization across platforms** (same business unification).
3. **Strict matching constraints enforcement** (weight/category exactness in published comparisons).
4. **Post-tax normalization pipeline** (strategy mandates out-the-door pricing).
5. **Freshness tiering and adaptive scrape cadence** (4h/8h/12h tiers by traffic/watchlist).
6. **Consumer feedback ingestion loop** (“Not same product?”, “Out of stock?” signals).
7. **Automated store discovery/matching** beyond static slug JSONs.

---

## Prioritized Action List

1. **Fix Weedmaps skip/resume semantics** (Critical)
2. **Implement canonical operator identity + cross-platform mapping** (Critical)
3. **Introduce explicit GPID model + verification workflow** (Critical)
4. **Fix category normalization defaults (`unknown` instead of `flower`) + backfill** (High)
5. **Harden CamoFox outage circuit breaker/recovery behavior** (High)
6. **Standardize resume/stuck-job handling across Leafly/Jane** (High)
7. **Close Jane browser tab in guaranteed finally path** (High)
8. **Expand category and weight extraction coverage (tincture/topical/eighth/etc.)** (High/Medium)
9. **Modernize orchestrators; remove stale runners** (High/Medium)
10. **Update architecture docs and formally deprecate legacy scrape service** (Medium/Low)

---

## Bottom Line

The system can scrape and insert data today, but it is not yet aligned with the strategy’s core promise: **high-trust, consumer-safe, cross-platform verified pricing for Top 500 products**. The highest-risk blockers are identity (operator + GPID), skip/resume correctness, and category/weight normalization precision.