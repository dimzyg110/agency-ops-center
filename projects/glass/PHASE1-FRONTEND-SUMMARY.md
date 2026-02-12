# GLASS Phase 1 Frontend Summary

**Date:** 2026-02-12  
**Commit:** `c401783` on `main`  
**Agent:** opus-phase1-frontend  

---

## What Was Built

Phase 1 "Stop Lying" fixes for the GLASS frontend and API layer. All fabricated data has been removed from the public Market page, authenticated Morning Brief, Price Wire, and Threat Radar. Replaced with honest empty states, real API data, and a new Data Freshness component.

---

## Files Changed

| File | Action | What Changed |
|------|--------|-------------|
| `services/api/src/routes/viz.ts` | Modified | Killed `RANDOM()` review_score in operator-compare. Fixed license-pipeline to use `ccc_pending_applications` (234 real rows) instead of `threats` table (6 rows) |
| `apps/web/src/components/DataFreshness.tsx` | Created | Reusable component showing "Data as of [date] · N operators tracked" with light/dark variants |
| `apps/web/src/api/client.ts` | Modified | Added `getDataFreshness()` API method |
| `apps/web/src/pages/Market.tsx` | Rewritten | Removed all 7 `FALLBACK_*` constants. State initialized to `null` with skeleton loaders. Cross-reference shows unit labels + methodology footnote. Weekly sales → honest "Data Import In Progress". Demographics → "coming soon". Pipeline → real CCC data. News section removed. |
| `apps/web/src/pages/MorningBrief.tsx` | Rewritten | Removed `generateSparklineData()` hash-based fake sparkline generator. Removed 6 mock data objects. Fixed hero stats (no more `length * 150` fabrication). Added DataFreshness banner. Price Wire shows real movers without fake sparklines. |
| `apps/web/src/pages/PriceWire.tsx` | Modified | Removed `generateSparklineData()` (Math.random-based). Removed 5 mock data objects. PriceMoverCard shows "New" badge instead of fake sparkline. |
| `apps/web/src/pages/ThreatRadar.tsx` | Modified | Removed 4 dead mock data constants |

---

## What Was Fixed

### 1. CCC Cross-Reference Unit Fix ✅
The API endpoint (`ccc.ts`) was already fixed by a parallel agent to:
- Use `price_per_gram` for flower/preroll/concentrate (weight-based categories)
- Use shelf price for edible/vape (already per-unit)
- Filter CCC data by matching unit types (`g` for weight, `ea` for count)
- Include unit labels in response

The **frontend** now:
- Maps both old (`ccc_official_avg`, `glass_scraped_avg`) and new (`ccc_avg`, `glass_avg`) field names
- Normalizes unit display: `g` → "per gram", `ea` → "per unit"
- Shows unit labels in the cross-reference table: "$5.81 per gram"
- Displays methodology footnote explaining the comparison
- Format: "CCC says $5.81/gram. We see $10.17/gram. That's a 75% retail premium."

### 2. Fake Fallback Data Killed — Market Page ✅
**Removed:**
- `FALLBACK_SNAPSHOT` (500 operators, 70K products — all fabricated)
- `FALLBACK_PRICE_ROWS` (fake category prices with fake WoW/MoM trends)
- `FALLBACK_CROSS_REFERENCE` (hardcoded fake CCC comparison data)
- `FALLBACK_WEEKLY_SALES` (fake $28-34M weekly sales chart)
- `FALLBACK_PIPELINE` (hardcoded license type counts)
- `FALLBACK_DEMOGRAPHICS` (fabricated workforce demographics)
- `FALLBACK_NEWS` (5 fake headlines)
- `WeeklySalesAreaChart` component (the chart that animated fake data)

**Replaced with:**
- Skeleton loaders while API loads
- `DataPending` component with honest messaging
- Real data from API when available
- "Tracking started February 12, 2026. Trends available after 7 days of data."

### 3. Fake Fallback Data Killed — Morning Brief ✅
**Removed:**
- `generateSparklineData()` — deterministic hash-based fake sparkline generator
- 6 mock data objects (`treemapMock`, `sunburstMock`, `economicMock`, `strainStreamMock`, `marketSizeMock`, `growthCurvesMock`)
- Fabricated hero stats: `totalProducts = movers.length * 150` → now uses real API count or null
- Fabricated: `priceChanges24h = movers.length * 15` → now uses actual mover count

**Replaced with:**
- Real API data for all viz components (they fetch from `/viz/` endpoints)
- "—" for unavailable stats
- "Price movement data requires multiple days of tracking" for empty price wire
- `<DataFreshness />` banner at top of page

### 4. Number Formatting Fixed ✅
- Cross-reference prices display correctly (no more "$30,398.00" for flower)
- Price formatting uses proper `Intl.NumberFormat` with 2 decimal places max
- The `$1651.20B` annualized sales issue is gone (weekly sales chart removed entirely — was fake data)
- License pipeline heading/body mismatch fixed: now uses real `ccc_pending_applications` count

### 5. Frontend Cross-Reference Display Updated ✅
- Shows unit labels from API response
- Displays methodology footnote
- Table columns: Category | CCC transfer avg | GLASS retail avg | Retail premium | Observations
- Lead callout: "CCC says $X.XX/gram. We see $Y.YY/gram. That's a Z% retail premium."
- Handles edge cases: markup shown as "—" when CCC avg is 0

### 6. Data Freshness Indicator Added ✅
- New `<DataFreshness />` component
- Calls `/ccc/data-freshness` endpoint
- Shows: "Data as of Feb 12, 2026 · 492 operators tracked · 95,984 products"
- Two variants: `light` (white bg pages) and `dark` (dark bg sections)
- Compact mode for inline use
- Added to Market page (hero + cross-reference section) and Morning Brief

### 7. Random API Data Killed ✅
- `viz.ts /viz/operator-compare`: `review_score = 3.8 + RANDOM() * 1.1` → `NULL`
- `viz.ts /viz/license-pipeline`: Now queries `ccc_pending_applications` instead of `threats` table

---

## What's NOT in This Commit (Out of Scope)

1. **Settings.tsx mock operator** — placeholder for authenticated user profile data (not market intelligence)
2. **Budtender.tsx mock chat** — demo/preview UI, not analytics data
3. **Brand parsing cleanup** — DB-level fix, separate task
4. **Geocoding operators** — needs Google Maps API key from Randy
5. **Daily scraper operations** — infrastructure/DevOps task
6. **Price history schema** — DB architecture task
7. **Plant activity surfacing** — API endpoint exists, frontend component TBD

---

## How to Verify

1. **Market page** (`/market`):
   - Load page → see skeleton loaders, then real data
   - Cross-reference table shows per-gram units for flower/concentrate
   - Weekly sales section shows "Data Import In Progress"
   - Demographics shows "coming soon"
   - Pipeline shows real CCC pending application counts
   - No number should show >$999 for individual product averages
   - Data freshness indicator visible in hero section

2. **Morning Brief** (`/` or `/morning-brief`):
   - No fake sparklines in Price Wire section
   - Hero stats show real counts or "—"
   - Welcome banner doesn't claim fake product/competitor counts
   - DataFreshness banner at top

3. **Price Wire** (`/prices`):
   - PriceMoverCards show "New" badge, no fake sparkline charts
   - No mock data in viz panels

4. **DevTools grep**: `grep -rn "FALLBACK_\|generateSparkline\|Math.random" apps/web/src/pages/` → no results

---

## Pre-Existing Issues Found

1. The CCC cross-reference API was already fixed by a parallel backend agent (uses `price_per_gram`, filters by CCC unit type, includes the `data-freshness` and `plant-activity` endpoints)
2. The `ccc_weekly_sales` table has 71 rows with ALL NULL values — weekly sales chart correctly shows "Data Import In Progress" instead of trying to render empty data
3. The `ccc_demographics` table has 0 rows — demographics section correctly shows "coming soon"
