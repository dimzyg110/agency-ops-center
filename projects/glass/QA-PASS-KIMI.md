# QA PASS — KIMI (2026-02-12)

## Scope Completed
- Audited requested frontend + API files.
- Hit all requested public API endpoints.
- Ran DB health and sanity queries directly against Railway Postgres.
- Fixed issues found in frontend/API code.

---

## 1) Endpoint Validation Results

Base: `https://glass-api-production.up.railway.app`

### CCC / Public
1. `GET /api/v1/ccc/cross-reference` → **200** ✅  
   - Returns `data[]` with: `category`, `ccc_official_avg`, `glass_scraped_avg`, `unit`, `markup_pct`, `glass_observation_count`, `as_of`.
   - Field names are compatible with `Market.tsx` normalization logic.
   - Flower markup currently ~`354.5%` in live payload (not 510% anymore).

2. `GET /api/v1/ccc/avg-prices` → **200** ✅  
   - Returns populated `data[]` with expected CCC rows.

3. `GET /api/v1/ccc/pending-applications` → **200** ✅  
   - Returns populated `data[]`.

4. `GET /api/v1/ccc/demographics` → **200** ✅  
   - Returns `data: []` (currently empty dataset, frontend has pending state).

5. `GET /api/v1/ccc/weekly-sales` → **200** ✅  
   - Returns `data: []` (matches expected “import in progress” state).

6. `GET /api/v1/ccc/data-freshness` → **200** ✅  
   - Returns `data` with: `latest_scrape`, `operators_tracked`, `products_tracked`, `total_observations`.
   - Matches Market stat card expectations.

7. `GET /api/v1/ccc/plant-activity` → **200** ✅  
   - Returns payload with `monthly`, `category_breakdown`, `trend`.

8. `GET /api/v1/ccc/plant-activity/summary` → **200** ✅  
   - Returns summary object.
   - `last_30d_volume` currently null (likely due no recent rows in that rolling window).

9. `GET /api/v1/operators/search?q=cannabis` → **200** ✅  
   - Returns operator search data used in onboarding.

10. `GET /api/v1/report-card/summary/0c920d2d-8143-4774-b60a-85a305cff264` → **200** ✅  
   - Returns summary payload with `operator`, `overall_status`, `overall_headline`, `top_action`, `generated_at`.

### Viz endpoints requested in checklist
11. `GET /api/v1/viz/price-distribution` → **404** before fix ❌  
12. `GET /api/v1/viz/category-breakdown` → **404** before fix ❌  
13. `GET /api/v1/viz/geography` → **404** before fix ❌  
14. `GET /api/v1/viz/brand-landscape` → **404** before fix ❌

**Fix applied:** Added compatibility routes for all 4 endpoints in `services/api/src/routes/viz.ts`.

---

## 2) Frontend Page Audit Findings

## Market.tsx
- Data flow:
  - `api.getCccCrossReference()`
  - `api.getCccPendingApplications()`
  - `api.getDataFreshness()`
- Good:
  - Handles both old/new cross-ref field names (`ccc_avg` vs `ccc_official_avg`, etc).
  - Stat cards use `operators_tracked`, `products_tracked`, `total_observations` correctly.
  - Weekly sales + demographics have explicit pending states.
- Notes:
  - Hardcoded “Data Import In Progress” weekly sales copy is currently correct given empty dataset.

## MorningBrief.tsx
- Correctly guards no-operator state with onboarding EmptyState.
- Loading/error/fallback states are implemented.
- Report Card integration uses onboarding localStorage operator id and `useReportCard` hook.

## Landing.tsx
- Mostly static LP content; links and sections are consistent.

## Onboarding.tsx
- **Issue found/fixed:** Step-2 market snapshot attempted to read `operatorAvgPrice/marketAvgPrice` from `/viz/proximity`, but that endpoint does not return those fields.
- Result was price position often `—` even when data existed.
- **Fix:** compute operator/market averages from `/viz/price-matrix` and still use `/viz/proximity` for competitor/threat counts.

## Budtender / Cue / Delivery
- Confirmed LP-style light mode pages (not dashboard dark mode). Consistent with current product-marketing intent.

## Newsletter.tsx
- Posts to `/api/v1/newsletter/subscribe`.
- Error mapping supports backend shape `error.message`; `NEWSLETTER_NOT_CONFIGURED` is displayed gracefully.

## ReportCard.tsx
- States are robust (skeleton, error, empty, loaded).

## Sidebar.tsx
- Navigation links are internally consistent.
- Dashboard vs tools sections use same dark styling system.

---

## 3) Specific Known-Issue Checks

a) Market stat cards: **PASS** ✅  
`/ccc/data-freshness` now returns expected fields and Market page maps them correctly.

b) Cross-reference markup conversion: **PARTIAL** ⚠️  
- API now uses per-gram paths for flower/preroll/concentrate.
- Flower is still materially high in live payload (~354.5%).
- This appears data-quality related (`price_per_gram`/`weight_grams` extraction), not a frontend field mismatch.

c) Weekly sales empty messaging: **PASS** ✅  
- API returns `data: []`; page shows explicit import-in-progress message.

d) Auth-gated dashboards fallback behavior: **PASS (code audit)** ✅  
- MorningBrief has explicit no-operator, loading, and error states.

e) Onboarding search flow: **PASS + FIXED MARKET SNAPSHOT** ✅  
- Search endpoint works.
- Step 2 snapshot logic corrected.

f) Report Card top-of-MorningBrief integration: **PASS** ✅  
- Uses onboarding-selected operator id.

g) Sidebar links + dark mode: **PASS (code audit)** ✅

h) Product pages mode: **PASS** ✅  
- They are LP-style light pages, consistent with Landing/Newsletter.

i) Newsletter non-configured error handling: **PASS** ✅  
- API returns `NEWSLETTER_NOT_CONFIGURED` and frontend displays human-readable message.

---

## 4) DB Data Quality Summary

Connection used successfully.

### Health counts
- `products`: **98,933**
- `prices`: **114,568**
- `operators`: **492** (`with_coords`: 490)
- distinct non-null brands: **16,190**
- `ccc_avg_prices`: **31,038**
- `ccc_pending_applications`: **234**
- `ccc_plant_activity`: **46,863**

### Junk/placeholder checks
- `operators.name = 'New Operator'`: **2** (still present)
- Suspicious long/marketing-like `brand` values still present in `products` sample.

### Price sanity by category (joined via products)
- flower: avg **35.44**, count **51,371**
- preroll: avg **18.50**, count **25,504**
- vape: avg **35.46**, count **17,314**
- edible: avg **17.89**, count **14,415**
- concentrate: avg **41.98**, count **5,940**

---

## 5) Fixes Applied

### A) Frontend API path mismatch (Report Card summary)
- **File:** `apps/web/src/api/client.ts`
- **Fix:**
  - from: `/report-card/${operatorId}/summary`
  - to: `/report-card/summary/${operatorId}`
- **Impact:** `useReportCardSummary` now targets the real backend route.

### B) Onboarding Step-2 market snapshot data mismatch
- **File:** `apps/web/src/pages/Onboarding.tsx`
- **Root cause:** frontend expected proximity payload fields that don’t exist.
- **Fix:** fetch both proximity + price matrix; derive:
  - `operatorAvgPrice` from selected operator’s `your_price` rows
  - `marketAvgPrice` from selected operator’s `market_avg` rows
  - keep `competitorsCount` + `activeThreats` from proximity
- **Impact:** Step-2 now shows meaningful price-position values when data exists.

### C) Missing viz endpoints requested by QA/public docs
- **File:** `services/api/src/routes/viz.ts`
- **Fix:** added compatibility routes:
  - `/viz/price-distribution`
  - `/viz/category-breakdown`
  - `/viz/geography`
  - `/viz/brand-landscape`
- **Impact:** removes 404s for these endpoints and restores backward compatibility.

---

## 6) Local Validation After Fix

- API TypeScript build: ✅ `services/api` build succeeded.
- Web build: ⚠️ could not run in this environment (`vite: not found`), so frontend compile not fully validated locally.

---

## 7) Remaining Issues

1. **Flower cross-reference still elevated** despite per-gram logic; likely parser/data normalization issue in price-per-gram extraction.
2. **Residual placeholder operators** (`New Operator` count = 2).
3. **Residual suspicious brand strings** still in product dataset.
4. Deployment not yet executed in this pass (code changes prepared). Deploy commands remain:
   - `railway service glass-api && railway up`
   - `railway service glass-web && railway up`

---

## Changed Files
- `apps/web/src/api/client.ts`
- `apps/web/src/pages/Onboarding.tsx`
- `services/api/src/routes/viz.ts`
