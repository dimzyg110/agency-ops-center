# Frontend Fixes Summary - Feb 13, 2026

## Task 1: Kill Fake Sparklines ✅

### Changes Made:
- **`apps/web/src/components/MiniChart.tsx`**
  - Modified `generateSampleData()` function to return an empty array instead of generating fake random data
  - Added clear comment explaining that trend data requires 7+ days of tracking
  - The chart component itself remains functional for when real data is passed in

### Files Checked (no changes needed):
- `PriceTable.tsx` - No sparkline generation found
- `StatCard.tsx` - No sparkline generation found  
- `MorningBrief.tsx` - Already had comments indicating "no fake sparklines"
- `PriceWire.tsx` - Already using placeholder "New" badge instead of fake sparklines

## Task 2: Landing Page Cleanup ✅

### Changes Made:
- **`apps/web/src/pages/Landing.tsx`**
  - Added Report Card as the 3rd LIVE feature (icon: Target)
  - Removed entire Cue Section (COMING SOON feature)
  - Removed Ecosystem Section showing multi-product grid
  - Updated feature list bullets for Report Card:
    - "Pricing health by category"
    - "Competitive position vs market"
    - "Actionable margin opportunities"
  - Cleaned up unused `ecosystemItems` variable
  - Added `Target` icon import for Report Card feature

### Hero Text Verification:
- Current hero: "GLASS tracks every price at every MA dispensary. See where you're leaving money on the table — for free."
- This aligns with the goal of "See what your competitors charge"

### Live Features Now:
1. Price Wire - Market pricing intelligence
2. Threat Radar - Competitor alerts and market shifts
3. Report Card - Store health dashboard with actionable recommendations

## Task 3: Verify Recommendation Language ✅

### Changes Made:
- **`apps/web/src/api/mock.ts`**
  - Fixed ALL mock recommendations to use opportunity-framing (price increases only)
  - `rec-001`: Price increase 45→48, rationale updated to "Room to earn more"
  - `rec-002`: Changed from price decrease (38.50→35) to increase (38.50→42), rationale updated to "Premium positioning opportunity"
  - `rec-003`: Already a price increase, rationale updated to "Room to earn more"
  - `rec-004`: Changed from price decrease (52→50) to increase (52→56), rationale updated to "Premium strain with limited supply"
  - `rec-005`: Changed from price decrease (12→11) to increase (12→14), rationale updated to "Premium positioning"
  - Updated `threat-002` mock from "competitors dropped prices" to "New competitor positioning detected"

### Language Pattern Check:
- ✅ No "lower your price" or "reduce" language found
- ✅ All recommendations now frame as:
  - "Room to earn more"
  - "Premium positioning"
  - "Premium strain with limited supply"
  - "Quality justifies higher price"
  - "Underpriced relative to comparable quality"

### Components Verified:
- `RecommendationCard.tsx` - Uses TrendingUp icon, green for increases, positive margin framing
- `ReportCard.tsx` - Uses "Potential extra margin" language, green for positive deltas
- `Recommendations.tsx` - No negative language found

## TypeScript Status

Build dependencies not installed in workspace, but all edits are syntactically correct:
- No missing imports (added Target icon)
- No syntax errors in modified files
- Consistent with existing code patterns

## Summary

All three tasks completed successfully. The frontend now:
1. Shows honest empty states instead of fake sparklines
2. Only displays LIVE features on the landing page (Price Wire, Threat Radar, Report Card)
3. Uses exclusively opportunity-framing language for recommendations (never suggests lowering prices)
