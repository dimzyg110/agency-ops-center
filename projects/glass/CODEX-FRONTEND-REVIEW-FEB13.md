# GLASS Frontend Review — Feb 13

## Scope Reviewed
1. `apps/web/src/components/MiniChart.tsx`
2. `apps/web/src/pages/Landing.tsx`
3. `apps/web/src/api/mock.ts`

Also ran required repo-wide searches.

---

## Search Results

### Command 1
```bash
grep -rn "generateSparkline\|generateSample\|COMING SOON\|Coming Soon\|coming soon" apps/web/src/ --include="*.tsx" --include="*.ts" | grep -v node_modules
```
Matches:
- `apps/web/src/components/Sidebar.tsx:160` → `Coming Soon`
- `apps/web/src/components/MiniChart.tsx:78` → `generateSampleData`
- `apps/web/src/pages/Landing.tsx:222` → `feature.status === 'Coming Soon'`
- `apps/web/src/pages/Landing.tsx:224` → `Coming Soon`
- `apps/web/src/pages/Onboarding.tsx:168` → `Cue (Coming Soon)`

### Command 2
```bash
grep -rn "lower.*price\|reduce.*price\|decrease.*price\|Consider lowering\|consider lowering" apps/web/src/ --include="*.tsx" --include="*.ts" | grep -v node_modules
```
Matches:
- `apps/web/src/pages/Market.tsx:556` → technical copy about unit conversion (`Flower prices converted to per-gram...`) — **not recommendation language**.
- `apps/web/src/api/mock.ts:275` → comment includes "lowering prices" in a negation statement.

### Command 3
```bash
grep -rn "lower.*price\|reduce.*price\|decrease.*price\|Consider lowering\|consider lowering" services/api/src/ --include="*.ts" | grep -v node_modules
```
Matches:
- `services/api/src/routes/ccc.ts:131,163,306` → price/unit conversion logic only — **not recommendation language**.

---

## File-by-File Review

## 1) `apps/web/src/components/MiniChart.tsx`
**Verdict: APPROVE WITH CHANGES**

### What’s correct
- Fake/sample sparkline generation is removed functionally (`generateSampleData` returns `[]`, line 81).

### Issues
1. **Poor empty state UX (line 30–71)**
   - With empty `data`, chart area renders blank with no user message.
   - Recommendation: render an explicit empty-state label (e.g., “Trend data available after 7 days”).

2. **Dead/legacy API remains (line 78)**
   - `generateSampleData(days = 7)` still exported though unused and no longer generates data.
   - `days` parameter is unused (potential lint failure depending on config).
   - Recommendation: remove function entirely, or rename to `getEmptyTrendData()` without unused args.

---

## 2) `apps/web/src/pages/Landing.tsx`
**Verdict: APPROVE WITH CHANGES**

### What’s correct
- Cue/Ecosystem “coming soon vaporware” sections appear removed from this page.
- Report Card is now included as a live feature (`features` entry #03, lines 31–40).
- Page structure still reads coherently without the removed ecosystem block.

### Issues
1. **Residual “Coming Soon” logic still present (lines 222–225)**
   - Conditional badge rendering remains: `feature.status === 'Coming Soon'` and badge text.
   - Currently dormant because all statuses are `'Live'`, but this is incomplete cleanup and keeps prohibited language in source.
   - Recommendation: remove the conditional block entirely and simplify feature model if all items are live.

---

## 3) `apps/web/src/api/mock.ts`
**Verdict: APPROVE**

### What’s correct
- Recommendation payloads are framed around upside/premium opportunity.
- No recommendation entries suggest lowering/reducing/decreasing price.

### Minor note
- Comment at line 275 contains phrase “lowering prices” in a negated policy sentence. Not harmful functionally, but if strict phrase bans are desired, reword to avoid keyword triggers.

---

## Completeness / Missed Files

If the objective is to remove “Coming Soon” vaporware and price-lowering language across `apps/web/src`, additional files still contain relevant text:

1. `apps/web/src/components/Sidebar.tsx:160`
   - `Coming Soon` label still present.

2. `apps/web/src/pages/Onboarding.tsx:168`
   - `Cue (Coming Soon)` still present.

3. `apps/web/src/pages/Landing.tsx:222,224`
   - Residual Coming Soon conditional and string.

4. `apps/web/src/components/MiniChart.tsx:78`
   - Legacy `generateSampleData` function still exists (even though it returns empty array).

---

## Regression Check
- No import breakages observed in reviewed files.
- `MiniChart` / `generateSampleData` appears unreferenced elsewhere (grep found only definitions), so no dangling external references from this change.
- Landing page renders logically with current live-feature framing.

---

## Final Summary
- `MiniChart.tsx`: **APPROVE WITH CHANGES**
- `Landing.tsx`: **APPROVE WITH CHANGES**
- `mock.ts`: **APPROVE**

Primary blockers to full approval are **incomplete cleanup** (residual Coming Soon strings/logic) and **missing empty-state UX** for sparklines.
