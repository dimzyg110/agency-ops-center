# Verdict: REQUEST CHANGES

## Executive Summary
The scraper is functionally working and successfully loaded real data, but there are several production-hardening gaps that must be addressed before scaling to 235 stores. The most important issue is data quality: brand parsing is materially incorrect for many records (especially NETA), which will poison SKU identity and downstream analytics. The architecture is directionally solid, but idempotency/resume behavior and long-run operational safeguards are not yet at production level.

## Data Quality Assessment

Reviewed snapshots:
- `pure-oasis-dtx.json`: 57 raw rows across 5 categories (7 flower, 30 preroll, 13 vape, 7 edible, 0 concentrate)
- `neta-brookline.json`: 236 raw rows across 5 categories (49 flower, 62 preroll, 32 vape, 65 edible, 28 concentrate)

### Parsing accuracy
- **Price extraction from button text is strong** in these samples:
  - 0/293 missing `$` in button text
  - 0/293 missing parsed price from current regex pattern
- **Weight parsing is strong for flower/preroll/vape/concentrate** and expectedly null for edibles:
  - Pure Oasis: 7/57 missing weight (all edibles)
  - NETA: 65/236 missing weight (all edibles)
  - `price_per_gram` behavior appears aligned with category gating (only meaningful categories use it).

### Major data quality issue: brand extraction
- `parseBrandAndName` currently applies an uppercase regex that often overrides the true brand and incorrectly sets brand to tokens like **"THC"**.
- In sampled rows, this appears frequently:
  - Pure Oasis: ~11/57 suspect brand parses
  - NETA: ~84/236 suspect brand parses
- Root cause: uppercase-brand heuristic is too broad and applied even when safer signals exist.
- Impact:
  - Incorrect `brand`
  - Wrong deterministic SKU generation (`brand` is part of hash key)
  - Product fragmentation and bad dedupe across stores/runs

### Product loss / parsing failures
- In these snapshots, `parsedCount == rawRows` and `normalizedCount == parsedCount`, so pipeline-level loss is low for extracted rows.
- However, **coverage loss exists at category capture level**:
  - Pure Oasis concentrate category returned 0 rows and logged error (`no products found`). Could be true empty category or parser/snapshot drift.
- Current extraction does not explicitly distinguish:
  - true empty category
  - blocked page / partial load / parser drift

### Duplicates
- No duplicate `href` rows observed within each store snapshot.
- But due brand/SKU errors, logical duplicates are likely to fragment in DB even when URL-level duplicates are absent.

## Code Review by File

### 1) `SCRAPER-V2-FINAL.md`
- Plan was pragmatic and correctly scoped to Dutchie-first.
- Several planned safeguards are either partially implemented or missing in code:
  - Idempotent daily upsert for prices (not implemented in `insertPrice`)
  - Auto-resume from incomplete run (currently manual `--resume` only)

### 2) `src/scripts/lib/types.ts`
- Types are clean and readable.
- Minor mismatch risk: script-level types evolve separately from Drizzle schema types (already visible in schema drift below).

### 3) `src/scripts/lib/config.ts`
- Good centralization.
- `CONCURRENCY` defaults to `1` despite BrowserPool being designed around tab pool; okay for safety but may underutilize capacity.
- No global caps for max retries / fail-fast thresholds / per-store timeout budget.

### 4) `src/scripts/lib/db.ts`
- **SQL injection risk: low** (all writes are parameterized placeholders).
- Key issues:
  1. **No idempotency constraint on prices insert**: `insertPrice` always inserts with `NOW()`. Re-runs same day create duplicates despite plan claiming dedup/upsert behavior.
  2. **No transaction boundaries** for per-store load. Partial writes can leave inconsistent store/job state on mid-store failure.
  3. **Pool lifecycle not closed** (`pool.end()` never called), which can leak resources in long-lived process contexts.
  4. `upsertOperator` writes synthetic `license_number` (`DISCOVERY-...`) while migration made nullable; not harmful but contradicts intent and may complicate later reconciliation.

### 5) `src/scripts/lib/parser.ts`
- Biggest correctness risk is in this file.
- `parseBrandAndName` heuristic is brittle and frequently wrong (`brand = THC`, etc.).
- `extractStrainType` misses common forms (`Hybrid-Sativa`, `Hybrid-Indica`) and may collapse nuance.
- `parsePriceButton` only captures first `$` token (usually okay), but no handling for non-dollar formats or range prices.
- `parseProducts` maps every row without validation/guardrails, so parsing quality is not measured beyond row count.

### 6) `src/scripts/lib/normalizer.ts`
- Weight normalization covers many common formats and is decent for initial production.
- `normalizeCategory` defaulting to `'flower'` on unknown categories is risky (silent misclassification).
- SKU generation is deterministic but currently corrupted by upstream brand parsing quality.
- `computePriceMetric` correctly limits `pricePerGram` to relevant categories.

### 7) `src/scripts/lib/browser-pool.ts`
- Wrapper approach is clean and practical.
- Risks:
  1. `maxTabs` constructor arg is not enforced anywhere.
  2. Static `USER_ID`/`SESSION_KEY` can collide across concurrent scraper runs.
  3. `parseProductsFromSnapshot` relies on brittle line-regex against accessibility snapshot formatting (high drift risk).
  4. `ensureHealthy()` only pings `/health`; no automatic tab/session recovery if individual tab state is bad.

### 8) `src/scripts/scrape-dutchie.ts`
- Good orchestration structure (discovery/scrape/load separation, per-store snapshot output, worker pool abstraction).
- Key issues:
  1. **Resume logic is manual**, not automatic detection of incomplete runs from today as planned.
  2. **No retry policy per failed category/store** beyond one pass.
  3. **No backpressure/batching for DB writes**; every product write is sequential and could become bottleneck at scale.
  4. Store success definition can mask quality issues (store marked succeeded even if multiple categories failed, as long as not all fail).
  5. Uses shared mutable `stats` from concurrent workers; in Node this is usually safe event-loop-wise, but still interleaved and hard to reason about under failures.

### 9) `src/scripts/migrations/001-scraper-v2.sql`
- Migration is mostly sane and non-destructive.
- Missing piece for production idempotency: no unique index/constraint supporting daily dedup key for prices.
- `scrape_jobs.run_id` added, good for resume lineage.

### 10) `src/services/api/src/db/schema.ts`
- **Schema drift is significant** relative to migration:
  - `operators.license_number` still marked `.notNull().unique()` in Drizzle model
  - New columns (`platform`, `platform_slug`, `metadata`, `weight_grams`, `strain_type`, `price_per_gram`, `menu_type`, `run_id`) are absent
- This will cause application-level type/query mismatch and future migration pain.

## Architecture Assessment
- Overall pipeline architecture is good for V2: clear phases, per-store snapshots, run/job bookkeeping, and category iteration.
- Weak points for production:
  1. Parser depends on unstable accessibility snapshot text format rather than structured DOM evaluate output.
  2. Idempotency/resume guarantees are weaker than design intent.
  3. Job lifecycle status is not tightly coupled to data quality thresholds (only operational success/failure).
  4. BrowserPool lacks strict resource governance (tab/session cap enforcement and recovery strategy).

## Scaling Assessment
For 235 stores, current implementation will run, but not safely at production reliability without changes.

- **Rate limiting:** current jitter helps, but there is no adaptive throttling on repeated failures/blocks.
- **Memory pressure:** per-store snapshots are manageable now, but retention policy is missing; disk growth will be continuous.
- **DB pool sizing:** default pg pool may be okay at low concurrency; no explicit tuning or shutdown/health handling.
- **Concurrent tab management:** currently effectively limited by top-level concurrency; BrowserPool itself does not enforce max tabs.
- **Error accumulation:** long runs can accumulate silent quality degradation (e.g., parser drift) because no hard alert thresholds are enforced.

## Critical Issues (must fix before scaling)
1. Fix `parseBrandAndName` so brand does not resolve to cannabinoid tokens (`THC`, etc.) and add parser tests with real NETA/Pure Oasis fixtures.
2. Implement true price idempotency/upsert semantics (DB unique key + `ON CONFLICT`) for same product/source/operator/day.
3. Add automatic resume discovery for incomplete runs and ensure reruns do not duplicate data.
4. Resolve schema drift by updating Drizzle schema to match migration columns/constraints.
5. Add robust parser drift detection with failure thresholds that can fail a job/run (not just log warnings).

## Recommended Improvements (nice to have)
1. Add per-store transaction boundaries (or staged writes) to reduce partial-ingest inconsistency.
2. Add retry policy with exponential backoff at category/store level.
3. Introduce per-run quality metrics (brand parse confidence distribution, null-field rates, category coverage deltas vs rolling baseline).
4. Enforce BrowserPool max tab/session limits and generate unique session IDs per run.
5. Add retention/cleanup policy for raw snapshots (e.g., keep 14–30 days, archive/compress older).
6. Add structured observability (run/job metrics, error taxonomy, alert hooks).
7. Expand normalization for strain-type variants and non-standard size formats.

## What's Working Well
- The end-to-end scraper pipeline is operational and already delivering real production inserts.
- Separation of concerns is good: config, parser, normalizer, DB helpers, and orchestrator are cleanly split.
- Parameterized SQL usage is correct and avoids injection risk.
- Raw per-store snapshot capture is a strong decision for reproducibility/debugging.
- Migration strategy is incremental and mostly non-breaking, which lowers deployment risk.
