# PHASE 1 DB Review

Date: 2026-02-12 (UTC)
Reviewer: QA (senior code review + live DB verification)

## Scope Reviewed

- `/data/workspace/projects/glass/PHASE1-DB-SUMMARY.md`
- `/data/workspace/projects/glass/TECH-FIX-PLAN.md`
- `/data/workspace/projects/glass/TECH-FIX-REVIEW-CODEX.md`
- Code:
  - `src/services/api/src/routes/ccc.ts`
  - `src/services/api/src/routes/viz.ts`
  - `src/services/scrape/src/parsers/dutchie.ts`
  - `src/services/scrape/src/normalizer.ts`
  - `src/scripts/scrape-dutchie-ma.ts`
  - `src/scripts/import-ccc-data.ts`
- Live DB: `postgresql://postgres:***@turntable.proxy.rlwy.net:18582/railway`

---

## Verification Query Results

### 1) Brand cleanup (top brands)
Query: `SELECT brand, COUNT(*) FROM products WHERE brand IS NOT NULL GROUP BY brand ORDER BY COUNT(*) DESC LIMIT 30;`

Top results now look mostly real (e.g. Cali Blaze 250, Bountiful Farms 231, Happy Valley 145, etc.).

### 2) Remaining stock/UI text brands
Query:
```sql
SELECT COUNT(*)
FROM products
WHERE brand ILIKE '%stock%'
   OR brand ILIKE '%order%'
   OR brand ILIKE '%sold out%'
   OR brand ILIKE '%limited%';
```
Result: **55** (NOT zero)

Examples still present:
- `ONE PER ORDER`
- `SHATTER Overstock Shatter`
- multiple long promo/banner strings containing `Limited Edition`, `Save 10%`, etc.

### 3) Category normalization (canonical set)
Products query:
```sql
SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY category;
```
Result:
- concentrate: 4,992
- edible: 12,693
- flower: 42,522
- preroll: 21,244
- tincture: 3
- topical: 3
- vape: 14,527

Prices query requested in prompt:
```sql
SELECT category, COUNT(*) FROM prices GROUP BY category ORDER BY category;
```
Result: **fails** (`prices.category` does not exist). This matches Phase-1 summary note.

### 4) CCC cross-reference (preroll match)
Cross-reference query (same logic as route) returns all expected categories including **Preroll**:
- Concentrate: CCC 17.35 vs GLASS 32.08 (g), +84.9%
- Edible: CCC 18.56 vs GLASS 17.9 (ea), -3.6%
- Flower: CCC 4.04 vs GLASS 18.13 (g), +348.8%
- Preroll: CCC 10.21 vs GLASS 11.2 (g), +9.7%
- Vape: CCC 26.64 vs GLASS 35.5 (ea), +33.3%

### 5) Weekly sales empty
Query: `SELECT COUNT(*) FROM ccc_weekly_sales;`
Result: **0** ✅

### 6) Plant activity table
Queries:
- `SELECT COUNT(*) FROM ccc_plant_activity;` → **46,863** ✅
- `SELECT * FROM ccc_plant_activity LIMIT 3;` → returns valid rows with expected `metric_name` pipe format and numeric values.

### 7) Threats lat/lon nullable
Query:
```sql
SELECT column_name, is_nullable
FROM information_schema.columns
WHERE table_name = 'threats' AND column_name IN ('lat', 'lon');
```
Result:
- lat: YES
- lon: YES

### 8) Fake review scores removed
Code check in `viz.ts`:
- `/viz/operator-compare` now returns `NULL::float8 AS review_score`.
- No random `RANDOM()` score remains in this route.

---

## Code Review Findings

## `src/services/api/src/routes/ccc.ts`
- ✅ Cross-reference category fix to `preroll` is in place.
- ✅ Uses parameterized SQL templates (no direct string interpolation of user input in these routes).
- ✅ Plant activity endpoints added and functional.
- ⚠️ `plant-activity` returns full aggregated JSON with no range/filter controls; can become heavy as data grows.
- ⚠️ No explicit try/catch around route handlers (Fastify global handling may catch errors, but no route-level context/logging).

## `src/services/api/src/routes/viz.ts`
- ✅ Fake review score removed (`NULL`).
- ✅ `license-pipeline` now reads from `ccc_pending_applications` (better semantic alignment).
- ✅ Query params (`days`, `radius`) are bounded and typed.
- ⚠️ `operator-compare` `ids` list is capped at 15 but not validated as UUIDs before query (TypeBox only says string). Not a direct injection issue with parameterized SQL, but weak input validation.

## `src/services/scrape/src/parsers/dutchie.ts`
- ✅ Introduced brand garbage patterns and normalization.
- ✅ Applied brand filtering in both LD+JSON and state blob parsing paths.
- ⚠️ Pattern list still misses many promo/banner artifacts seen in DB (e.g., `limited edition`/`save xx%` marketing strings that do not match current exact guards).

## `src/services/scrape/src/normalizer.ts`
- ✅ Category canonicalization to `preroll` implemented.
- ✅ Brand normalizer rejects pipe junk, numeric-only, and common UI strings.
- ⚠️ Over-aggressive possibility: rejects any brand containing `|` globally. Usually correct, but if a legitimate brand includes a separator pattern, it will be nulled.

## `src/scripts/scrape-dutchie-ma.ts`
- ✅ `sanitizeBrand()` exists and writes rejected brand as NULL in SQL output.
- ⚠️ Filtering still not strict enough for long promotional strings (seen live in residual garbage set).
- ⚠️ Script uses generated SQL inserts from scraped text without a secondary server-side normalization pass guarantee in this file itself.

## `src/scripts/import-ccc-data.ts`
- ✅ Weekly rows now skipped if all metrics are null (prevents null-only inserts).
- ✅ Deletes root behavior of placeholder weekly rows by only inserting valid-value rows.
- ✅ Bulk upsert patterns use placeholders (safe from injection).
- ⚠️ `recordsUpdated` is never incremented (always 0), so ingest run stats are inaccurate.

---

## Security / Injection Review

- **SQL injection:** No critical SQL injection found in reviewed files. Query construction is primarily parameterized via `drizzle-orm` template SQL or pg placeholders.
- **Risk note:** `operator-compare` accepts freeform comma-separated IDs; this should be UUID-validated for correctness and safer behavior.

---

## Issues Found (P0/P1/P2)

1. **P1 — Brand cleanup incomplete (data quality regression risk):**
   55 suspicious brands remain, including clear promo/UI text artifacts. This is material if brand analytics are customer-facing.
   - Fix: strengthen parser + normalizer blocklist/patterns for promo phrases (`limited edition`, `save xx%`, `one per order`, etc.) and run one more DB cleanup pass.

2. **P1 — Ingest observability bug:**
   `recordsUpdated` in `import-ccc-data.ts` is not tracked; ingest metrics are misleading.
   - Fix: capture row counts from upsert/update paths or rename metric to avoid false precision.

3. **P2 — API robustness/perf:**
   `plant-activity` endpoint has no query filters/pagination and may become large over time.
   - Fix: add optional `days`, `channel`, and response limits.

4. **P2 — Input validation gap:**
   `viz/operator-compare` does not enforce UUID shape on each ID entry.
   - Fix: validate IDs are UUID format before query.

---

## Overall Verdict

**Major Issues**

Why: Core Phase-1 goals are mostly implemented correctly (cross-reference fixed, weekly empty fixed, plant activity present, threats lat/lon nullable, fake review score removed), but **brand data quality is not yet clean enough** to claim the cleanup is fully complete, and residual garbage is still visible in live DB.

---

## Must-fix Before Deploy

1. Run a second targeted brand cleanup + parser/normalizer hardening to eliminate remaining promo/UI garbage brands.
2. Re-run verification query #2 and require result = 0 (or documented allowlist exceptions).
3. Add basic UUID validation for `/viz/operator-compare` IDs.

## Can ship with follow-up

- `plant-activity` filter/pagination improvements.
- `recordsUpdated` accounting cleanup in importer logs.
