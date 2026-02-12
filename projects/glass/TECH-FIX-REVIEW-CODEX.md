# TECH-FIX-REVIEW-CODEX

Date: 2026-02-12  
Reviewer: Senior Systems Architect / Technical Lead (independent review + DB verification)

---

## Overall Assessment: **ADEQUATE plan, but with critical correctness gaps**

The plan identifies most major trust-killers correctly (unit mismatch, fake data fallbacks, bad brand parsing, missing geocodes, no time-series depth). That said, several proposed fixes are either incomplete, risky, or not executable as written against the current schema/code.

If executed exactly as written, you will improve optics quickly, but you may still ship broken logic in Threats, mixed-unit CCC comparisons, and long-term history architecture.

---

## What I verified directly (DB + code)

### Live DB facts (as of review)
- `products`: **95,984**
- `prices`: **110,965**
- `operators`: **492**
- `ccc_avg_prices`: **31,038**
- `ccc_weekly_sales`: **71** (all value columns NULL)
- `ccc_pending_applications`: **234**
- `ccc_plant_activity`: **46,863**
- `threats`: **6**

### Data quality checks
- Price history is effectively one day:
  - 2026-02-12: **110,848** rows
  - prior days: 14–20/day
- Operators geocoded: **10 / 492**
- Weekly sales table: values all NULL; dates are month-end (`2020-01-31` → `2025-11-30`) not weekly.
- Brand contamination is severe:
  - `stock. Order soon.` = **4,171**
  - `Unknown` = **2,092**
  - obvious garbage classes are material.
- Cross-reference endpoint currently excludes prerolls due to `pre-roll` vs `preroll` mismatch in `ccc.ts`.

---

## Section-by-section feedback on the plan

## 1) Plan accuracy

### What is correct
- Root causes are mostly accurate.
- Fake-data fallback diagnosis is correct and code-referenced.
- Category mismatch (`pre-roll` vs `preroll`) is real and currently breaks cross-reference completeness.
- Weekly sales ingestion issue is real (confirmed ingest run failure + null table state).
- Scrape-history insufficiency diagnosis is correct.

### What is wrong/incomplete
1. **Threat conversion fix is not schema-safe**
   - `threats.lat` and `threats.lon` are `NOT NULL` in schema.
   - Proposed application→threat inserts omit lat/lon, so inserts will fail.
2. **`onConflictDoNothing()` for application-threat sync is not enough**
   - There is no obvious unique constraint in `threats` to stop duplicates; recurring sync will duplicate unless you define a deterministic id/unique index.
3. **CCC unit handling still too naive**
   - CCC has units `g`, `ea`, `mg`, `oz`, `l` in last 365d. Plan filters mostly to `g` and `ea` without explicit canonicalization rules per category+pack.
4. **Price history proposal risks duplicated semantics**
   - Existing `prices` already has daily uniqueness by `(product_id, source_id, operator_id, date(scraped_at UTC))` via `idx_prices_daily_product_source_operator`.
   - Proposed summary tables are useful, but design should align with this uniqueness and with query access patterns.

---

## 2) Missing issues

1. **Randomized fake metric still in production API**
   - `viz.ts /viz/operator-compare` computes `review_score = 3.8 + RANDOM() * 1.1`.
   - This is fabricated data presented as real.
2. **Threat endpoint semantics are disconnected from actual `threats.type` values**
   - `license-pipeline` query uses types (`new_license`, `competitor_opening`, `regulatory_change`) not present in current `threats` values (`price_war`, `supply_disruption`, etc.).
3. **No explicit data lineage/confidence layer**
   - After removing fake data, users still need “why is this empty / confidence grade / last successful run”.
4. **Performance indexing not addressed for proposed new queries**
   - Cross-reference + trend queries need targeted indexes (`prices(scraped_at, product_id)`, `products(category,id)`, derived summary indexes).
5. **No migration/backfill runbook**
   - Plan lacks rollback strategy and dry-run/validation steps per migration.

---

## 3) Priority disagreements (my ranking)

## P0 (must ship first)
1. **Kill fabricated data in UI + API** (includes random review_score)
2. **Fix CCC cross-reference with canonical units + explicit labels + caveats**
3. **Fix category canonicalization (`preroll`) everywhere**
4. **Stabilize scraper ops + expose scrape health endpoint and banner**

## P1
5. Weekly sales: hide now, re-import correctly later
6. Brand parsing + normalization repair
7. Geocode operators (batch + incremental)

## P2
8. Plant activity surfacing
9. Pending applications -> threat model (after geo + schema-safe threat design)
10. Long-term summary tables / market history materializations

I would move “Pending Apps → Threats” down until threat schema and geospatial mapping are fixed.

---

## 4) Technical risks (risk register)

| Risk | Likelihood | Impact | Notes / Mitigation |
|---|---:|---:|---|
| Threat sync inserts fail due to missing lat/lon | High | High | Add nullable threat location or geocode pending apps before insert |
| Duplicate threat generation over time | High | Medium | Add unique key (e.g., source_system + external_app_id) |
| Unit mismatch persists in edge categories | Medium | High | Create canonical unit normalization table and tests |
| Removing fallbacks creates empty UX shock | Medium | Medium | Replace with staged “collecting baseline” UX + confidence badges |
| Scraper cadence not truly running despite cron code | Medium | High | Health endpoint + SLO alerting + runbook |
| Brand cleanup nulls valid brands | Medium | Medium | Run UPDATE via staged candidate table + manual sample review |
| Summary table drift vs source-of-truth prices | Medium | Medium | Rebuild job idempotency + reconciliation query |

---

## 5) Architecture concerns

1. **Daily scraping approach is directionally right**, but currently “configured” != “operational.” You need observability and SLOs before trusting outputs.
2. **History schema should be materialized, not duplicate logic-heavy ETL**
   - Prefer:
     - `price_daily_summary` as materialized aggregate keyed by `(product_id, operator_id, source_id, date)`
     - optional `market_daily_summary` by `(category, city, date)`
3. **Unit normalization requires first-class modeling**
   - Don’t bury in endpoint SQL CASE blocks.
   - Create canonical measurement strategy (`canonical_price_value`, `canonical_unit`) at ingest/normalize stage.

---

## 6) Alternative approaches (better/simpler)

1. **Cross-reference**: introduce a small mapping table:
   - `category_unit_policy(category, glass_metric_unit, ccc_allowed_units, conversion_rule)`
   - Then queries join policy instead of hard-coded CASE logic.
2. **Fake data removal**: two-tier UX states:
   - `No data` (never collected),
   - `Insufficient baseline` (e.g., need 7 days),
   - `Degraded` (pipeline failure).
3. **Brand cleanup**:
   - Build `brand_cleanup_candidates` table first, validate sample, then apply UPDATE.
4. **Threat pipeline**:
   - Start with a separate `competitive_signals` table from pending apps;
   - only promote to `threats` after geo + severity rules are stable.

---

## 7) CCC cross-reference fix (most important)

### Is per-unit->per-gram conversion the right approach?
**Partially.** It is correct for weight-based categories (flower, concentrate) where reliable grams exist. It is **not universally valid** for count-based packs (edibles, prerolls multipacks, vapes with volume distinctions).

### Recommended model
- **Flower / Concentrate**: compare per-gram only.
- **Vape / Edible**: compare per-each only, but clearly define “each” (cart, pack, unit) and avoid mixed pack-size averages.
- **Preroll**: split single vs multipack; either normalize to per-gram where weight exists, else per-stick with separate cohorts.

### Mixed-unit handling rule
- Never aggregate mixed units into one avg without conversion.
- If conversion impossible, keep separate rows per unit/cohort and label as non-comparable.

### SQL correction notes
The plan SQL is close, but add:
- explicit prereq filter for unit cohorts,
- pack-size/quantity normalization guardrails,
- and include `comparison_basis` field in API response (`per_g`, `per_each_single`, `per_each_pack`, `not_comparable`).

---

## 8) “Kill fake data” without killing UX

Replacing fake data with blank panels alone is not enough.

### Better transition UX
1. **Transparent placeholders**: “Collecting baseline: Day 1 of 7.”
2. **Show what is real now**: current snapshot tables and distributions.
3. **Progressive unlocks**:
   - Day 0-2: snapshot metrics only
   - Day 3-7: short-horizon deltas
   - Day 8+: trend charts
4. **Data provenance footers** per card:
   - last update time,
   - source count,
   - confidence grade.

---

## 9) Effort estimate realism

The plan underestimates several items:
- Threat integration (schema + geo + dedupe + severity logic): **5h -> 12-16h**
- Weekly sales proper re-import with source validation: **4-6h -> 1-2 days**
- History architecture + API cutover + reconciliation: **7h -> 12-20h**
- Frontend fake-data purge across all pages/tests: **11h plausible** if scoped tightly.

---

## 10) What’s still missing before operator trust

Even after all listed fixes, trust still requires:
1. **Data quality scoring and publishable methodology**
2. **Per-metric confidence and comparability labels**
3. **Operator-specific relevance layer (not generic market dashboards)**
4. **Alerting/incident response for scrape failures**
5. **Audit trail for corrected values and backfills**

---

## Specific technical corrections to proposed SQL/code

1. **Threat sync insertion must include lat/lon or schema change**
   - Current schema requires both NOT NULL.
2. **Add uniqueness for threat upsert**
   - e.g., `UNIQUE(source_system, entity_name, published_at, type)` or better external app id.
3. **Fix `license-pipeline` semantics**
   - Should query `ccc_pending_applications` directly (current threat-type stages don’t map to actual types).
4. **Cross-reference should include preroll via canonical category**
   - replace `'pre-roll'` filter with `'preroll'` in current code.
5. **Remove random review score in `/viz/operator-compare`**
   - return null if unavailable.
6. **Weekly sales table naming/data contract**
   - if source is monthly, either rename table/endpoint or ingest true weekly source.

---

## Recommended execution order (revised)

### Day 1
- Remove fabricated UI/API values (including random SQL)
- Fix cross-reference categories/units and labels
- Add scrape health endpoint + global freshness banner

### Day 2
- Weekly sales: disable fake chart, add truthful state
- Brand cleanup (staged + parser guardrails)
- Canonical category migration (`preroll`)

### Day 3
- Geocode batch + geo validation
- Expose plant activity quick wins
- Stand up `competitive_signals` from pending apps (not full threat merge yet)

### Day 4+
- Threat system refactor with schema-safe model
- Price summary materializations + endpoint migration

---

## If I had 3 days to make this platform trustworthy, exactly what I’d do

## Day 1 — Stop lying
- Delete all frontend fallbacks that fabricate numeric business data.
- Kill randomized API fields (`review_score RANDOM()`).
- Ship cross-reference v2 with unit-safe cohorts + explicit disclaimers.
- Add “data as-of + baseline status” on every primary card.

## Day 2 — Make data coherent
- Canonicalize categories (`preroll`) and unit policies.
- Run staged brand cleanup + parser blocklist.
- Hide weekly sales chart and replace with source-status module.

## Day 3 — Make operations dependable
- Verify scraper job cadence operationally (not just code config).
- Publish scrape health endpoint + alert thresholds.
- Batch geocode operators and unlock geo features.
- Deliver one operator-specific insight card that is fully trustworthy.

That 3-day sequence won’t make the platform complete, but it will make it honest, inspectable, and materially more credible to a real operator.

---

## Final verdict
The plan is directionally good and catches most core issues, but it needs schema-aware corrections (especially Threats), stronger unit normalization discipline, and a trust-oriented UX transition model. With those changes, execution can materially improve platform credibility within 72 hours.