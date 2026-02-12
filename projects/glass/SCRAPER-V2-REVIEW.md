REJECT — The plan is directionally good, but it materially underestimates operational complexity, duplicates parts of the current schema, and will likely fail cost/reliability targets in Railway as written.

## 1) Architecture Gaps (what will break at scale)

### 1.1 No durable queue, idempotency strategy, or retry model
You describe 3 workers and a circuit breaker, but not a durable task queue with lease/ack semantics. If the process crashes at hour 3.5, you risk duplicate inserts or partial runs without clean resume.

Missing:
- Per-store/per-category job state machine (queued/running/succeeded/failed/retry_exhausted)
- Deterministic idempotency key for a scrape observation (`source_id + product_fingerprint + scraped_at_bucket`)
- Retry backoff policy by failure class (403 vs timeout vs parser error)
- Safe resume from checkpoint

### 1.2 Single shared browser context is a reliability bottleneck
One CamoFox instance with shared cookies is efficient, but a single point of failure. If browser crashes, all workers die. Also shared context can leak anti-bot fingerprint correlations across stores.

### 1.3 No clear separation of concerns for ingest vs analytics
Plan chains scrape → load → compute MVs in one daily job. If MV refresh fails, ingest run is “done but not done.” You need separate, independently retryable jobs and freshness SLAs per dataset.

### 1.4 No observability baseline
You mention `scrape_runs` but no metrics/alerts stack definition. Production needs:
- success rate by platform/source/category
- p50/p95 scrape latency
- parser drift detection (field-null rate spikes)
- insertion error rate
- stale data alarm (per source freshness SLA)

### 1.5 Legal/compliance is hand-waved
"ToS review" is listed as mitigation, not as a gate. For production, this is a deployment gate with explicit allow/deny matrix by platform and jurisdiction.

## 2) Schema Issues (conflicts, duplication, practicality)

### 2.1 `prices_normalized` duplicates existing `prices` + `products`
Current schema already has:
- `prices`: price, promo_flag, raw_data, availability, scraped_at, source/operator/product linkage
- `products`: thc_percent/cbd_percent/category/quantity/unit

`prices_normalized` duplicates core fields and introduces synchronization risk. You will spend time reconciling two truths.

Better pattern:
- Keep `prices` as immutable fact table
- Add computed columns where justified OR a derived table keyed 1:1 by `price_id` for normalization outputs only
- Do not copy operator/source/product/category unless denormalization is proven necessary

### 2.2 Proposed `scrape_runs` overlaps existing `scrape_jobs`
You already have `scrape_jobs` with source-level status/timing/records. If you add `scrape_runs`, define hierarchy explicitly:
- `scrape_runs`: run-level envelope (daily job)
- `scrape_jobs`: child jobs per source/category
Without this, you create two partially overlapping tracking systems.

### 2.3 `operators` constraints conflict with discovery reality
`operators.license_number` is currently `NOT NULL UNIQUE`. Your own plan says early discovery from Dutchie/Weedmaps before CCC reconciliation. Many discovered stores won’t have clean license IDs immediately. Ingest will fail or force fake license values.

### 2.4 Product identity model is too weak for cannabis catalog variance
`sha256(brand|normalized_name|weight)` is not enough. You will collide or split:
- Same strain with multiple package types/lineages
- Brand aliases and white-label products
- Infused vs non-infused variants
Need explicit canonical entity tables and confidence-scored matching, not just hash keying.

### 2.5 Materialized view definitions are not production-ready
Issues:
- `PERCENTILE_CONT(0.25)` in `category_benchmarks` is missing `WITHIN GROUP (ORDER BY ...)`
- `price_movers` relies on undefined `latest_prices` and `previous_prices`
- No refresh strategy (`CONCURRENTLY` requirements + unique index)
- No partitioning strategy for large `prices` table

### 2.6 “Zero raw SQL” conflicts with your own MV/analytics plan
Drizzle can’t cleanly abstract all advanced PG ops (MVs, concurrent refresh, percentile heavy analytics) without SQL. This success metric is unrealistic and should be removed.

## 3) Speed/Cost Estimates (Railway realism)

### 3.1 Runtime estimate is optimistic
Assumed 20s/category is best-case stable DOM + no anti-bot friction. Real-world p95 on dynamic menu pages often 35–90s with retries. With 2,000 loads/day:
- At 20s avg: ~11.1h serial work / 3 workers ≈ 3.7h (your estimate)
- At 45s avg realistic: ~25h serial / 3 ≈ 8.3h plus retries => 9–12h

### 3.2 Cost estimate likely low by 2–4x
You cost 2 vCPU + 2GB for ~4h/day (~$10/mo). If runtime is 9–12h and memory needs 3–6GB (browser + Node + JSON payloads), monthly cost climbs materially. Also include failed runs/retries and network overhead.

### 3.3 Railway cron behavior and cold start overhead not accounted for
Image pull + browser init + warmup can consume nontrivial runtime and memory spikes. Plan ignores this overhead.

## 4) Data Quality Risks

### 4.1 Entity resolution will drift quickly
Name normalization alone is brittle. Cannabis menus have noisy names, emojis, potency variants, vendor-specific formatting, and batch-level changes.

Need:
- deterministic parser output schema versioning
- fuzzy matching with confidence thresholds
- manual adjudication queue for low-confidence merges/splits
- audit trail of entity merge decisions

### 4.2 Weight normalization is under-specified
You mention 1/8, 1/2, 1g only. Real menus include packs and mixed units:
- `10x0.5g`, `3.5g x 2`, `100mg`, `200mg gummies (20x10mg)`, `1ml`, `0.5ml`
Price-per-gram is invalid for many categories (edibles, vapes, concentrates measured in mg/ml/units). Need category-specific normalization and comparability metrics.

### 4.3 Price parsing/promo logic is fragile
Crossed-out price parsing from DOM text is brittle and locale/markup dependent. Also taxes and pre-tax vs post-tax differences can corrupt comparisons.

### 4.4 Availability/in-stock assumptions are dangerous
Default `in_stock=true` in normalized table is wrong when menu cards persist for OOS items. Need explicit availability parse and confidence scores.

## 5) Deployment Concerns (Dockerfile.scraper + CamoFox on Railway)

### 5.1 CamoFox compatibility is not validated for Railway runtime
The plan assumes "baked in" works, but doesn’t specify:
- required system libraries/fonts/sandbox flags
- seccomp/cgroup constraints
- `/dev/shm` sizing (critical for Chromium-based stability)
- headless GPU/software rendering settings

### 5.2 Memory/CPU budget is risky
3 active tabs + JS-heavy pages + extraction buffers can exceed 2GB. OOM kill risk is high without strict memory controls and tab lifecycle management.

### 5.3 No fallback execution environment
If Railway blocks/limits headless stack, there is no fallback (secondary worker environment, self-hosted VM, or split pipeline).

## 6) Missing Pieces

- Data retention/partition policy for `prices` and raw snapshots (this table will explode)
- Backfill strategy and replay controls
- Schema/version migration plan for parser changes
- Exactly-once semantics for load stage
- Source-specific parser contract tests + synthetic fixtures
- Anti-bot incident playbook (rotate fingerprints/proxies if legally allowed)
- SLA definitions by endpoint/feature (Price Wire vs Recommendations freshness)
- Security hardening for scraper secrets and outbound egress policy

## 7) Prioritization Review

Current sequence is not optimal.

### What should move earlier
1. **Data model decisions first** (identity, normalization, run/job hierarchy) before scraper coding.
2. **Observability + run control** before scale-up.
3. **Railway proof-of-runtime** before full implementation.

### What should be deferred
- Weedmaps + multi-platform expansion before Dutchie pipeline is stable at 95%+ success
- Materialized views breadth (start with 1–2 critical derived tables)
- API endpoints for analytics until data quality is trustworthy

### What should be cut now
- “Zero raw SQL” objective
- Full cross-platform in 4 weeks target (not credible with required data quality controls)

## Recommended Changes

1. Define and implement a two-level job model: `scrape_runs` (daily envelope) + `scrape_jobs` (store/category units) with durable state and retry metadata.
2. Keep `prices` as immutable source-of-truth; add a `price_normalizations` table keyed by `price_id` instead of cloning full rows in `prices_normalized`.
3. Relax operator identity constraints for discovery (`license_number` nullable initially), then enforce after CCC reconciliation via a verified status flow.
4. Replace simple SKU hash with an entity resolution pipeline: deterministic keys + fuzzy matcher + confidence + human review queue for low-confidence matches.
5. Implement category-specific normalization metrics (e.g., $/g flower, $/mg THC edibles, $/ml vape) and prohibit invalid cross-category price-per-gram comparisons.
6. Add parser contract tests with fixture snapshots per platform and alerting on extraction drift (null/empty field thresholds).
7. Validate CamoFox on Railway with a dedicated spike: prove browser stability, memory profile, `/dev/shm` behavior, and required launch flags before committing architecture.
8. Re-estimate runtime/cost using p95 timings from a 50-store pilot; budget for retries and failure days. Update financial model to realistic bands, not point estimate.
9. Split pipeline into independently retryable stages: ingest, normalize, analytics refresh, alert generation—each with its own success/failure signals.
10. Implement storage lifecycle controls now: partition `prices` by date, retention policy for raw snapshots, and replay tooling for parser upgrades.
11. Start with Dutchie-only production hardening (success rate, quality, observability), then add Weedmaps only after objective readiness gates are met.
12. Drop the “zero raw SQL” requirement and explicitly allow SQL for MVs, percentile queries, concurrent refreshes, and performance-critical operations.