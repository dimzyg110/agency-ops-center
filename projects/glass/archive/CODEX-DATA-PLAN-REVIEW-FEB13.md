# CODEX Data Integration Plan Review
**Date:** February 13, 2026  
**Analyst:** Subagent (Deep Dive Review)  
**Focus:** GLASS codebase vs. proposed plan — actionable recommendations

---

## Executive Summary

**Bottom line:** The plan proposes ~$82MB of new data infrastructure, but **~70% of the schema and ~50% of the ETL scripts already exist in the codebase**. The critical gap is **data population** (scores are empty) and **operator matching** (the 3-tier strategy is not implemented).

**Revenue-enabling items (P0):** Complete operator matching → populate `operator_scores` → build report card API
**Deferrable (P2):** County metrics, strain database, Google reviews, enforcement actions

---

## 1. What Already Exists vs. What's New

### 1.1 Schema — MOSTLY DONE ✅

| Plan Table | Schema Exists? | Migration Status | Notes |
|------------|----------------|-------------------|-------|
| `ccc_lab_tests` | ✅ Yes | Migration 002 ✅ | 147,649 rows in prod |
| `ccc_facility_sales` | ✅ Yes | Migration 002 ✅ | 67,333 rows in prod |
| `ccc_monthly_prices` | ✅ Yes | Migration 002 ✅ | 71 rows in prod |
| `ccc_licenses` | ✅ Yes | Migration 002/003 ✅ | 772 rows in prod |
| `operator_scores` | ✅ Yes | Migration 002/003 ✅ | **0 ROWS — NOT POPULATED** |
| `google_reviews` | ✅ Yes | Migration 002 ✅ | Schema only, no data |
| `enforcement_actions` | ❌ No | Not in migrations | Future feature |
| `strains` | ❌ No | Not in migrations | Future feature |
| `ccc_county_metrics` | ❌ No | Not in migrations | Future feature |
| `etl_runs` | ✅ Yes | Migration 003 ✅ | 4 rows in prod |

**Key finding:** Schema is ~80% complete. The missing tables are all "future" features.

### 1.2 ETL Scripts — PARTIALLY DONE ⚠️

| Plan ETL Script | Status | Location |
|-----------------|--------|----------|
| Lab Tests Import | ✅ Implemented | `/src/scripts/import/import-lab-tests.ts` (235 lines, production-ready) |
| Facility Sales Import | ✅ Implemented | `/src/scripts/import/import-facility-sales.ts` |
| Monthly Prices Import | ✅ Implemented | `/src/scripts/import/import-monthly-prices.ts` |
| Licenses Import | ✅ Implemented | `/src/scripts/import/import-licenses.ts` (18K lines, most comprehensive) |
| Commence Ops Import | ✅ Implemented | `/src/scripts/import/import-commence-ops.ts` |
| Composite Score Compute | ⚠️ Partial | Migration 003 has `refresh_health_scores()` function but **NOT CALLED** |

**Key finding:** All CSV import scripts exist. What's missing:
1. Running the imports (data is already in DB per STATUS-AUDIT)
2. Actually calling `refresh_health_scores()` to populate `operator_scores`

### 1.3 Materialized Views — DONE ✅

From `migrations/003_composite_scores.sql`:
- `mv_operator_health` — Composite health scores (weights: pricing 25%, compliance 20%, THC integrity 20%, assortment 20%, market position 15%)
- `mv_thc_integrity` — Lab vs. menu THC accuracy
- Function `refresh_health_scores()` — Refreshes MVs and upserts to `operator_scores`

**Issue:** These exist in migration but may not have been run against production. Status audit shows `operator_scores` is **EMPTY (0 rows)**.

---

## 2. What's Already Been Done

### 2.1 Data Population (Per STATUS-AUDIT-FEB13.md)

| Table | Row Count | Status |
|-------|-----------|--------|
| `ccc_lab_tests` | 147,649 | ✅ Populated (Feb 12) |
| `ccc_facility_sales` | 67,333 | ✅ Populated |
| `ccc_monthly_prices` | 71 | ✅ Populated |
| `ccc_licenses` | 772 | ✅ Populated |
| `operator_scores` | **0** | ❌ **CRITICAL GAP** |

### 2.2 API Routes

From `/src/services/api/src/routes/scores.ts`:
- `GET /operators/me/scores` — Authenticated user's scores
- `GET /operators/:id/health-score` — Full 5-component breakdown
- `GET /operators/:id/thc-integrity` — Lab vs. menu accuracy
- `GET /market/health-leaders` — Top 10 by score (public)
- `POST /admin/scores/recalculate` — Trigger refresh

**Routes exist but return fallback data** when `operator_scores` is empty (see lines 55-70 in scores.ts).

### 2.3 Intelligence Service

From `/src/services/intelligence/src/workers/ccc-ingest.ts`:
- Fetches CCC data via API + scraper
- Extracts threat events (new licenses, violations, opportunities)
- Geocodes addresses
- Scores threats against operators
- Creates alerts for critical/high severity

**This is a separate pipeline** from the CSV imports. It handles:
- Licenses
- Applications
- Board actions
- Meeting minutes

---

## 3. Priority Ranking by Revenue Impact

### P0 — Revenue-Blocking (Build NOW)

| Item | Impact | Status |
|------|--------|--------|
| **Populate operator_scores** | Report cards need this | ❌ Empty |
| **Build public report card API** | Core product feature | ⚠️ Partial |
| **Fix operator matching** | Link CCC licenses → scraped operators | ⚠️ Partial |

### P1 — Core Features (Build Next)

| Item | Impact | Status |
|------|--------|--------|
| **Daily/weekly score refresh cron** | Keep scores current | ❌ Not implemented |
| **Health leaders endpoint** | Competitive analysis | ✅ Done |
| **THC integrity detail** | Compliance selling point | ✅ Done |

### P2 — Nice-to-Have (Defer)

| Item | Impact | Status |
|------|--------|--------|
| `ccc_county_metrics` | County-level analytics | ❌ Not implemented |
| `google_reviews` | Review sentiment | ❌ Not implemented |
| `enforcement_actions` | Compliance tracking | ❌ Not implemented |
| `strains` database | Strain intelligence | ❌ Not implemented |

---

## 4. What to Defer (Brutal Assessment)

### 4.1 Over-Engineered for Pre-Revenue Stage

1. **`ccc_county_metrics`** — Plan proposes aggregation by county with saturation scores. At 473 operators and 1 target customer, this is premature. The county data exists in `ccc_licenses`; can query ad-hoc.

2. **Strain database (`strains`)** — Requires Otreeba API integration. Strains in lab tests are anonymized (`Strain_01`). No value until METRC cross-reference exists.

3. **Google reviews scraping** — Schema exists but no data. Requires Places API + scraping. Nice-to-have for "review_score" component, but can use placeholder (50) until operational.

4. **Enforcement actions** — CCC board actions are already scraped by `ccc-ingest.ts`. A separate table adds complexity without immediate revenue impact.

5. **Composite score version tracking** — Plan has `computation_version` field. Over-engineering for v1.

### 4.2 What CAN Wait Until After $199/mo Subscription

- Any advanced analytics dashboards
- Multi-operator comparison features
- Export functionality
- API rate limiting refinements
- Mobile optimizations

---

## 5. Red Flags

### 5.1 Schema Design Issues

| Issue | Location | Severity |
|-------|----------|----------|
| **`ccc_lab_tests.operator_id` is nullable** | Schema line 250 | ⚠️ **No linkage** — Lab tests cannot be joined to operators because METRC tags don't map to operator IDs. Need license number cross-reference. |
| **Materialized view references non-existent table** | Migration 003, line 78 | 🔴 **BUG** — `ccc_avg_prices` referenced in MV but not defined in migration 002. Should be `ccc_monthly_prices`. |
| **`ccc_facility_sales` missing unique constraint** | Schema line 277 | ⚠️ **Potential duplicates** — No unique constraint on (sale_date, market_type, delivery_type, product_category, unit_of_measure) in Drizzle schema (exists in raw SQL). |

### 5.2 ETL Bugs

| Issue | Location | Severity |
|-------|----------|----------|
| **Batch upsert uses wrong column order** | `import-lab-tests.ts` line 180 | 🔴 **BUG** — INSERT columns list doesn't match VALUES placeholders. Columns: `(metrc_tag, product_category, strain_code, thc_percent, thca_percent, total_thc_percent, testing_lab, test_date, test_comment, source_file)` but code pushes in different order. |
| **Pivot map key collision** | `import-lab-tests.ts` line 107 | ⚠️ **Potential data loss** — If two different METRC tags truncate to same 30-char string, later entry overwrites earlier. |
| **Date parsing edge cases** | `etl-base.ts` parseCccDate | ⚠️ **Verbose JS dates** — Plan notes "Thu Oct 12 2023 04:00:00 GMT-0400" format needs handling. Current parser may fail on this. |

### 5.3 Missing Indexes

| Table | Missing Index | Impact |
|-------|--------------|--------|
| `ccc_lab_tests` | `(operator_id, product_category)` | Slow joins in score calculation |
| `ccc_licenses` | `(license_number, operator_id)` | Slow matching |
| `prices` | `(operator_id, category, scraped_at)` | Score MV is slow |

### 5.4 Architectural Concerns

1. **Score calculation depends on data that may not exist:**
   - `ccc_avg_prices` table referenced in MV doesn't exist (typo: should be `ccc_monthly_prices`)
   - Lab tests can't join to operators (no foreign key path)

2. **No operator matching pipeline:**
   - Plan proposes 3-tier matching (license number → fuzzy name → geo-proximity)
   - No code implements this
   - `ccc_licenses.operator_id` is mostly NULL (need to populate)

3. **No daily score refresh:**
   - `refresh_health_scores()` function exists but not called
   - No cron job scheduled

---

## 6. Implementation Estimates

### P0 Items (Revenue-Blocking)

| Task | Estimate | Dependencies |
|------|----------|---------------|
| **Fix operator matching** — Populate `ccc_licenses.operator_id` using license number + fuzzy name + geo | 8-12 hrs | None |
| **Run score refresh** — Execute `refresh_health_scores()` and verify `operator_scores` populated | 2-4 hrs | Operator matching |
| **Fix MV bug** — Correct `ccc_avg_prices` → `ccc_monthly_prices` reference in migration 003 | 1 hr | None |
| **Fix batch upsert bug** — Correct column order in `import-lab-tests.ts` | 2 hrs | None |
| **Schedule daily cron** — Run `refresh_health_scores()` daily | 2-3 hrs | Scores populated |

**Total P0: ~15-21 hours**

### P1 Items (Core Features)

| Task | Estimate | Dependencies |
|------|----------|---------------|
| **Public report card endpoint** — Already exists in code, needs testing | 2 hrs | Scores populated |
| **Health leaders caching** — Add cache layer for `/market/health-leaders` | 3 hrs | None |
| **Date parsing fix** — Handle verbose JS dates in `etl-base.ts` | 2 hrs | None |

**Total P1: ~7 hours**

### P2 Items (Defer)

| Task | Estimate | Rationale |
|------|----------|-----------|
| County metrics | 8-10 hrs | Premature at 473 operators |
| Google reviews | 12-16 hrs | No revenue impact yet |
| Strain database | 10-12 hrs | Data is anonymized |
| Enforcement actions | 6-8 hrs | Already in `threats` table |

---

## 7. Specific File References

### Already Done (Don't Rebuild)

- Schema definitions: `/src/services/api/src/db/schema.ts` (lines 249-380)
- Migration 002: `/migrations/002_ccc_tables.sql` (full schema)
- Migration 003: `/migrations/003_composite_scores.sql` (MVs + function)
- Lab test import: `/src/scripts/import/import-lab-tests.ts` (needs bug fix)
- Facility sales import: `/src/scripts/import/import-facility-sales.ts`
- Monthly prices import: `/src/scripts/import/import-monthly-prices.ts`
- Licenses import: `/src/scripts/import/import-licenses.ts`
- ETL base lib: `/src/scripts/import/lib/etl-base.ts`
- Score routes: `/src/services/api/src/routes/scores.ts`
- CCC ingest worker: `/src/services/intelligence/src/workers/ccc-ingest.ts`

### Needs Work

- **Operator matching:** No existing code — needs new script
- **Score refresh:** Function exists but never called
- **MV bug:** Line 78 in `migrations/003_composite_scores.sql`
- **Batch upsert bug:** Line ~180 in `import-lab-tests.ts`

---

## 8. Actionable Recommendations

### This Week (Revenue-Blocking)

1. **Run this SQL immediately:**
   ```sql
   -- Fix the MV bug first
   -- Then refresh scores
   SELECT refresh_health_scores();
   ```

2. **Build operator matching script** — Priority. Without linking `ccc_licenses.operator_id`, scores can't compute compliance component.

3. **Test report card endpoint** — `GET /api/v1/public/operators/:id/report-card`

### Next Sprint

4. **Schedule daily cron** for score refresh
5. **Fix bugs** in import scripts
6. **Add missing indexes**

### Defer

- County metrics
- Google reviews
- Strain database
- Any "advanced" features

---

## Summary: Build vs. Skip

| Build (P0) | Skip/Defer (P2) |
|------------|-----------------|
| Operator matching + linking | County metrics |
| Score population (run function) | Google reviews |
| Fix MV bug | Strain database |
| Fix batch upsert bug | Enforcement actions table |
| Daily cron for scores | Version tracking |
| Test report card API | Advanced dashboards |

**Total immediate work: ~15-21 hours to get revenue-blocking features working.**
