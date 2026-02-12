# Market Data Wire-up Summary

## Completed
- Wired real CCC weekly sales + demographics data into `apps/web/src/pages/Market.tsx`.
- Added API fetches for:
  - `api.getCccWeeklySales()`
  - `api.getCccDemographics()`
- Updated API client methods in `apps/web/src/api/client.ts` to return `r.data || []`.

## Market Page Changes

### 1) Weekly Sales section (`Massachusetts total cannabis sales`)
- Replaced placeholder empty-state with a real D3 area chart component (`WeeklySalesAreaChart`).
- Chart uses:
  - Black card background
  - Copper accent `#C45A3C`
  - Weekly `total_sales` across time
  - Year ticks on X-axis
  - `$M` ticks on Y-axis
- Added hover interaction displaying:
  - Week ending date
  - Total sales
  - Transaction count
- Added required headline stats in-chart:
  - `$8.8B` total adult-use sales since 2018
  - `$1.65B in 2025 — a new annual record`
- Added loading skeleton and graceful empty fallback.

### 2) Demographics section (`Workforce profile`)
- Replaced placeholder with real data-driven visuals.
- Added two responsive donut cards (stack on mobile, side-by-side on desktop):
  - `Gender Distribution`
  - `Race & Ethnicity`
- Uses D3 pie/arc rendering.
- Added workforce headline from live data:
  - `{formatCount(workforceTotal)} licensed cannabis agents in Massachusetts`
- Added loading skeletons and graceful fallback state.

## Data Handling
- Weekly sales rows normalized and sorted ascending by `week_ending`.
- Demographics normalized and split by category:
  - `gender`
  - `race_ethnicity`

## Notes
- Existing workspace had unrelated modified files before this task.
- Lint command could not run fully because local `eslint` binary/deps are missing in this environment.
