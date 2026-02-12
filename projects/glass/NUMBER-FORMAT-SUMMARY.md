# Number Formatting Standardization Summary

## Completed
Implemented shared number/date formatting and applied it across all requested GLASS frontend files.

### New shared utility
Created:
- `apps/web/src/utils/format.ts`

Functions added:
- `formatPrice(value)`
- `formatCount(value)`
- `formatCompactCount(value)`
- `formatPercent(value, showSign)`
- `formatDate(dateStr)`
- `formatRelativeDate(dateStr)`

All include safe fallback handling for invalid/null values to prevent `NaN`, `null`, or `undefined` rendering.

## Files Updated
- `apps/web/src/pages/Market.tsx`
- `apps/web/src/pages/MorningBrief.tsx`
- `apps/web/src/pages/Landing.tsx`
- `apps/web/src/pages/Onboarding.tsx`
- `apps/web/src/pages/Cue.tsx`
- `apps/web/src/pages/Delivery.tsx`
- `apps/web/src/pages/Newsletter.tsx`
- `apps/web/src/components/ReportCard.tsx`
- `apps/web/src/components/DataFreshness.tsx`

(Reviewed `Budtender.tsx` and `Sidebar.tsx`; no dynamic financial/count/date formatting issues required there.)

## Key Fixes Applied

### Market page
- Fixed CCC × GLASS cross-reference money formatting to always show proper USD currency format.
- Retail premium now uses one-decimal percent formatter with sign support.
- Observation counts now comma-formatted.
- Snapshot cards now use formatted AnimatedNumber output:
  - Operators: full count
  - Products/Observations: compact count
- License pipeline totals/counts now comma-formatted.

### Morning Brief
- Replaced all raw `toFixed`/manual `$` output in recommendation cards and movers.
- Percent change now consistently formatted with one decimal and sign.
- Prices now consistently use USD formatter.
- Top stat cards now use count formatting.
- Alert dates now human-readable via shared date formatter.
- Estimated margin strings now use shared price formatter.

### Onboarding
- Market snapshot prices now use shared price formatting.
- Competitor/threat counts now use shared count formatting.
- Prevented falsey-zero formatting issues by checking `!= null` for prices.

### ReportCard
- Category pricing now uses shared price formatter.
- Category diff percentages now use shared percent formatter.
- Money opportunity now formatted as `~$X.XX/week`.
- Product and competitor counts now comma-formatted.
- `generated_at` now shown as relative date (`Updated Xh ago`) with fallback.

### DataFreshness
- Replaced raw date/count rendering with shared formatters.
- Now shows relative recency (`Updated ... ago`) + human date + formatted counts.

### Landing / Cue / Delivery / Newsletter
- Standardized visible numeric stats and pricing teaser strings using shared formatters where applicable.

## Validation Notes
- Searched targeted files for leftover raw `toFixed`, `toLocaleString`, and date-formatting patterns and replaced where they were rendering user-facing values.
- Added fallback behavior to avoid rendering `NaN`, `undefined`, or `null`.

## Build/Run Note
Attempted build:
- `npm run build:web`
- Failed due to missing `vite` binary in current environment (`sh: vite: not found`).

## Git/Deploy
Code changes are staged in working tree but commit/push/deploy were **not executed** in this run.
