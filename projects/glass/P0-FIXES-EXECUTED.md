# P0 Fixes Executed — 2026-02-12

**Executed by:** Subagent (opus-p0-fixes)
**Files modified:** 3 files, 1 DB migration, 1 nav cleanup

---

## Task 1: Report Card Suggestion Text ✅

**File:** `services/api/src/routes/report-card.ts`

**Before:**
```typescript
let status: Status = 'green';
let suggestion = 'On target';

if (diffPct > 15) {
  status = 'red';
  suggestion = `Consider lowering by ${formatCurrency(Math.max(1, yourAvg - marketAvg))}`;
} else if (diffPct > 10) {
  status = 'yellow';
  suggestion = `Consider lowering by ${formatCurrency(Math.max(1, yourAvg - marketAvg))}`;
} else if (diffPct < -15) {
  status = 'red';
  suggestion = `You're likely underpriced. Consider raising by ...`;
} else if (diffPct < -10) {
  status = 'yellow';
  suggestion = `You may have room to raise by ...`;
}
```

**After:**
- Default suggestion: "Competitive pricing. Focus on experience and product mix to differentiate."
- `>20%` above: Yellow — "Premium position" framing with margin/promo options
- `>10%` above: Yellow — "Slightly above market" with demand/volume context
- `<-15%` below: Red — "Leaving money on the table" with weekly dollar impact
- `<-10%` below: Yellow — "Room to earn more" with weekly dollar impact
- Added `absDiffStr`, `weeklyVolumeEstimate`, `weeklyDollarStr` helper variables

**Key tone shift:** Never says "lower your price." Premium is a valid strategy. Underpriced = urgent opportunity.

---

## Task 2: Report Card Action Items ✅

**File:** `services/api/src/routes/report-card.ts`

**Before:**
```typescript
for (const category of rawCategories
  .filter((c) => c.diff_pct > 10)
  .sort((a, b) => b.diff_pct - a.diff_pct)
  .slice(0, 2)) {
  // "Lower your X price by about $Y to match nearby stores."
}
```

**After:**
- **Primary actions:** Underpriced categories (diff_pct < -10), sorted most underpriced first, up to 2
  - Priority: `high` if < -15%, `medium` otherwise
  - Text: "$X/unit below market. Raising could add ~$Y/week. Your customers already chose you."
  - Impact: "+$Y/week"
- **Secondary actions:** Overpriced categories (diff_pct > 15%), sorted most overpriced first, up to 1
  - Priority: always `medium` (premium is a choice, not a problem)
  - Text: "$X/unit above market. If sales strong = premium margin. If slow = consider promo."
  - Impact: "Monitor velocity"

---

## Task 3: Estimated Opportunity Calculation ✅

**File:** `services/api/src/routes/report-card.ts`

**Before:**
```typescript
const moneyOpportunityRaw = over10.reduce((sum, category) => {
  const unitDelta = Math.max(0, category.your_avg - category.market_avg);
  // Calculated money LOST from lowering prices (backwards)
```

**After:**
```typescript
const under10 = rawCategories.filter((c) => c.diff_pct < -10);
const moneyOpportunityRaw = under10.reduce((sum, category) => {
  const perUnitGain = Math.abs(category.your_avg - category.market_avg);
  // Now calculates money GAINED from raising underpriced categories
```

**Impact:** The dollar number now represents actionable upside, not theoretical savings from lowering prices.

---

## Task 4: Frontend Opportunity Label ✅

**File:** `apps/web/src/components/ReportCard.tsx`

**Before:**
- Label: "Estimated opportunity:"
- Colors: `glass-accent` (blue/purple)

**After:**
- Label: "Potential extra margin from underpriced categories:"
- Colors: `emerald-500`/`emerald-400` (green — money = green)

---

## Task 5: Pricing Section Default Expanded ✅

**File:** `apps/web/src/components/ReportCard.tsx`

**Before:** `useState<Record<string, boolean>>({})`
**After:** `useState<Record<string, boolean>>({ pricing: true })`

Pricing section now auto-expands on load since it's the #1 thing operators check.

---

## Task 6: DB Migration — operator_scores Table ✅

**Ran against production:** `turntable.proxy.rlwy.net:18582/railway`

Created table `operator_scores` with:
- `id`, `operator_id` (unique FK to operators), `overall_score`, `pricing_score`, `compliance_score`, `thc_integrity_score`, `assortment_score`, `market_position_score`
- JSONB detail columns for each score component
- `grade`, `calculated_at`, `version`
- Indexes on `overall_score`, `grade`, `calculated_at`

**No migration file existed** — table was defined in `schema.ts` but never created in production. Created directly via SQL.

---

## Task 7: Hide Empty Nav Items ✅

**File:** `apps/web/src/components/Sidebar.tsx`

**Removed from navItems:** `Geography` (no data yet)
**Removed from toolItems:** `Delivery` (not built yet)
**Cleaned up:** Removed unused `Map` and `Car` imports from lucide-react

Routes remain functional if accessed directly via URL.

---

## Task 8: CCC Imports — NOT EXECUTED ⚠️

**Status:** Import scripts for the raw CSV files do NOT exist.

**Existing script:** `scripts/import-ccc-data.ts` reads from **JSON** files in `/data/workspace/projects/internal/newsletter/data/ccc/` — a different data pipeline.

**CSV files available but no importers:**
| CSV File | Target Table | Rows Available |
|----------|-------------|----------------|
| `data/ccc-raw/facility-sales-stats.csv` | `ccc_facility_sales` | Has data (14-column CSV) |
| `data/ccc-raw/commence-ops.csv` | `ccc_licenses` | Has data (40+ column CSV) |
| `data/ccc-raw/avg-monthly-price-oz.csv` | `ccc_monthly_prices` | Has data (3-column CSV) |

**All three target tables exist in production but are empty (0 rows).**

**Recommendation:** Create CSV→DB import scripts for these three datasets. The column mappings are straightforward but need careful field name mapping (CSV headers differ from table columns).

---

## TypeScript Compilation

- **Backend (`services/api`):** ✅ Clean — `npx tsc --noEmit` passes with zero errors
- **Frontend (`apps/web`):** ⚠️ Pre-existing issue — missing `@types/react` and `@types/react-dom` in node_modules (not caused by these edits; Vite handles this at build time)

---

## Summary

| Task | Status | Risk |
|------|--------|------|
| 1. Suggestion Text | ✅ Done | Low — text only |
| 2. Action Items | ✅ Done | Low — text + logic |
| 3. Opportunity Calc | ✅ Done | Low — flipped calculation |
| 4. Frontend Label | ✅ Done | Minimal — text + color |
| 5. Default Expanded | ✅ Done | Minimal — state init |
| 6. DB Migration | ✅ Done | Low — new table, no data migration |
| 7. Nav Cleanup | ✅ Done | Low — hiding items |
| 8. CCC Imports | ⚠️ Skipped | Needs new import scripts |
