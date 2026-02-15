# GLASS Backend Review

_Date: 2026-02-15 (UTC)_
_Scope: backend/data layer only — API routes, DB schema/views, scrapers, data quality, GTM readiness_

## Current State (what’s built and working)

### 1) Core data platform is live and materially populated
- **Postgres (Railway, `public` schema) is live** with substantial scale:
  - `products`: **174,504**
  - `prices`: **308,833**
  - `operators`: **1,322**
  - `sources`: **1,103**
  - `parsed_products`: **8,889**
  - `verified_gpids`: **5,293**
  - `product_verified_gpids`: **5,109**
- Freshness is strong in raw prices:
  - **188,794** price rows in last 48h
  - **308,783** in last 7d

### 2) Scraper infrastructure is deployed and writing data
- 4 Railway scraper services exist (`dutchie`, `jane`, `leafly`, `weedmaps`) with production entrypoints and DB run/job tracking.
- `scrape_runs` shows active historical execution:
  - Dutchie: 15 completed / 2 failed
  - Jane: 10 completed / 7 failed / 1 running
  - Leafly: 5 completed / 6 failed
  - Weedmaps: 8 completed / 1 running
- Recent high-yield runs confirm ingestion is real (e.g., Dutchie 60k+ prices, Jane 10k+).

### 3) GPID pipeline exists and is producing usable output
- Brand authority exists and is complete enough for top-brand strategy:
  - `brand_authority`: **1001 total**, **1001 verified**, **308 at 3+ platforms**
- Parsing + validation pipeline is active:
  - `parsed_products`: accepted **6,630**, needs_review **2,116**, rejected **143**
- Deterministic lock script and mapping tables are in place (`verified_gpids`, `product_verified_gpids`).

### 4) Consumer query backend architecture is in place
- `consumer_prices_view` and `price_history_30d` exist in DB.
- Consumer routes implemented (`/consumer/search`, `/consumer/gpid/:gpid`, `/consumer/brands/top`, etc.) and mounted under both `/api/v1` and `/v1`.
- API service compiles (`npm run build` passes in `src/services/api`).

---

## Issues & Blockers

## P0 (Launch-blocking)

1) **Production consumer API currently returns 503 (GTM blocker)**
- `https://glass-api-production.up.railway.app/v1/consumer/stats` and `/v1/consumer/search` currently return:
  - `CONSUMER_VIEW_UNAVAILABLE`
- This blocks the public comparison product, regardless of DB quality.

2) **Consumer availability cache can latch false indefinitely**
- In `services/api/src/routes/consumer.ts`, `consumerViewAvailability` is global cached.
- On view/contract error, it is set to `false` and then reused.
- There is no automatic re-check path; one transient failure can effectively keep consumer endpoints down until restart.

3) **SQL bugs in consumer route likely breaking specific endpoints**
- `deal-of-the-day` query has duplicate `HAVING` clauses (invalid SQL form).
- Multiple queries use `CONCAT_WS(cpv.store_name, ...)` (first arg is separator, likely unintended) instead of `CONCAT_WS('|', ...)`.
- These are correctness/reliability risks in live endpoints.

4) **Consumer freshness policy mismatch from strategy docs**
- Current consumer queries hard-filter to **48h**, while sprint/gameplan policy references **7-day** freshness with status tiers.
- This likely reduces available coverage and can produce empty/503-like UX under normal scraper variance.

## P1 (Serious quality/reliability gaps)

5) **Major brand completeness gap remains**
- Products missing brand: **67,209** (~38% of catalog).
- This is still the largest data quality risk to GPID expansion and comparison trust.

6) **Scraper reliability is uneven across platforms**
- Jane and Leafly failure rates remain high relative to Dutchie.
- Weedmaps still shows low store coverage relative to known source count in prior reports.
- Net effect: consumer view volatility and platform bias.

7) **POS API integration route is mostly scaffolding**
- `pos-api-integration.ts` has multiple TODO stubs (provider calls, credential validation, product upsert logic).
- Trojan-horse transition away from scrapers is not production-ready yet.

8) **Health-source telemetry has correctness issues**
- `health-sources.ts` uses `failure_count` as product count proxy (incorrect metric semantics).
- Also performs per-source query loops (N+1), which will degrade with scale.

## P2 (Structural debt / future risk)

9) **Schema source-of-truth drift risk**
- Drizzle `schema.ts` does not model several critical runtime tables/views used by raw SQL paths (e.g., GPID/consumer view structures).
- Migrations include overlapping numbering patterns (`015-*`, etc.), increasing operational ambiguity.

10) **No meaningful automated test safety net in API**
- `npm test` is placeholder (`No tests configured yet`).
- SQL-heavy consumer routes and GPID logic are largely unguarded against regressions.

11) **Claim flow has token lifecycle bug risk**
- In `consumer-claim.ts`, verify endpoint marks token used, but dashboard endpoint requires `usedAt IS NULL` on token.
- This can break post-verification dashboard access flow.

---

## Next Steps (priority-ordered with rationale)

## 1) Restore consumer API availability in production (**P0, immediate**)
**Why first:** GTM cannot proceed if `/v1/consumer/*` is down.

- Debug prod API DB binding and view visibility (is it pointing to same DB/schema as validated data?).
- Patch `consumerViewAvailability` behavior:
  - add retry/backoff revalidation,
  - avoid permanent false latching on transient errors,
  - expose diagnostics in admin-only health.
- Validate with smoke checks:
  - `/v1/consumer/stats`
  - `/v1/consumer/search?limit=3`
  - `/v1/consumer/gpid/:gpid` on known mapped GPID.

## 2) Fix consumer SQL correctness bugs + stabilize contract (**P0**)
**Why:** even after availability restore, incorrect SQL will create silent bad results/500s.

- Fix duplicate `HAVING` in deal-of-day queries.
- Standardize all store-uniqueness `CONCAT_WS('|', ...)` usages.
- Add a minimal integration test set for core consumer endpoints using fixture data.

## 3) Align freshness policy with product contract (**P0/P1**)
**Why:** current 48h hard filter may be too strict for launch reliability.

- Move to 7-day inclusion policy for search/detail with freshness labeling (`fresh`, `aging`, hide stale >7d) per gameplan.
- Keep 48h as ranking boost, not hard exclusion.

## 4) Triage scraper reliability by platform with SLOs (**P1**)
**Why:** ingestion instability directly causes consumer holes and inconsistent comparisons.

- Set explicit platform SLOs (success %, store coverage %, rows/run).
- Start with Leafly/Jane failure modes and Weedmaps coverage depth.
- Add run-level alerting thresholds for “0 stores/0 prices” completed runs.

## 5) Close Brand Fill gap (67k no-brand products) (**P1**)
**Why:** this is the biggest remaining data-quality bottleneck for scaling GPIDs.

- Execute a two-lane plan:
  1. scraper capture fixes where available,
  2. controlled LLM brand inference for missing-brand cohort with review queue.
- Track precision separately for inferred brand vs parsed structured fields.

## 6) Harden GPID parsing/locking pipeline operations (**P1/P2**)
**Why:** GPID quality is core moat; pipeline has implementation drift risk.

- Ensure parser actually uses fallback model chain in runtime path (currently fallback helper exists but is not used in main loop).
- Add idempotent run manifests + run audit tables for reproducibility.
- Enforce schema and contract checks before lock step.

## 7) Convert POS API integration from scaffold to production path (**P2 but strategic)**
**Why:** reduces long-term scraper fragility and improves freshness quality.

- Implement at least one real provider (Dutchie or Jane) end-to-end:
  credential validation → product fetch → normalized upsert → sync metrics.
- Keep scraper fallback with source-priority arbitration.

## 8) Establish schema/migration governance + tests (**P2**)
**Why:** reduce breakage as velocity increases.

- Unify migration numbering/versioning and maintain one canonical schema definition.
- Add CI gates:
  - API typecheck/build
  - migration smoke apply
  - consumer endpoint integration tests.

---

## Bottom Line

Backend/data foundation is **real and substantial**: large live dataset, active scrapers, working GPID pipeline, and consumer-view architecture. 

But **GTM readiness is currently blocked by production consumer API availability and query correctness issues**. Once those P0 items are fixed, GLASS can move from “data-rich backend” to a reliably consumable public price-comparison product.