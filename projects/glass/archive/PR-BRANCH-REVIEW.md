# GLASS PR Branch Review — Phase 3 + Phase 5

**Reviewer:** QA Subagent (Opus 4)  
**Date:** 2026-02-12  
**Branches reviewed:** 3  
**Main HEAD:** `96f1a7a` (121 commits)  
**Common merge base:** `11b2021` (branches forked ~109 commits behind main)

---

## Executive Summary

**All three branches have already been merged into main** via earlier commits. The branch code was cherry-picked or independently re-implemented on main, then further hardened with security fixes (LIKE escaping, date serialization, Clerk auth, etc.) and extended with new features (flywheel, viz, report cards, CCC tables). The branches are **fully obsolete** and should be deleted, not merged.

---

## Branch 1: `codex/phase3-pricewire`

**Commits:** 2 ahead of merge base (`d345505`, `1b5cacc`)  
**Files modified (from merge base):**
- `services/api/src/routes/dashboard.ts` — Morning Brief API rewrite with `Promise.all()` parallelization
- `services/api/src/routes/prices.ts` — Enhanced prices endpoint with product/operator joins, `ilike` filtering, sort/order, route reordering
- `services/api/src/routes/watchlists.ts` — Full rewrite with product joins, ownership checks, notification fields

### Comparison to Main

| File | Branch State | Main State | Delta |
|------|-------------|------------|-------|
| `dashboard.ts` | `Promise.all()`, 7-day threat window, anomaly counting | **Identical** + date serialization fix (`toISOString()` for raw SQL) | Main is superset ✅ |
| `prices.ts` | `ilike` filtering, product/operator joins, direction filter | **Identical** + `escapeLike()` security fix, date serialization fix | Main is superset ✅ |
| `watchlists.ts` | Product joins, ownership checks, notification fields | **Identical** — no diff between branch and main | Already merged ✅ |

### Verdict: 🛑 ABANDON

**Rationale:** Every line of new code from this branch already exists on main. Main additionally has security hardening (LIKE injection prevention, date serialization for raw SQL) that the branch lacks. Merging this branch would **regress security fixes**.

---

## Branch 2: `kimi/phase3-morning-brief`

**Commits:** 2 ahead of merge base (`f4f658a`, `8c3bca3`)  
**Files modified (from merge base):**
- `apps/web/src/pages/MorningBrief.tsx` — Complete rewrite: real data hooks, severity badges, sparklines, alert indicators, freshness widget
- `apps/web/src/pages/PriceWire.tsx` — Complete rewrite: real API hooks, sort/filter/pagination, price mover cards, CSV export

### Comparison to Main

| File | Branch State | Main State | Delta |
|------|-------------|------------|-------|
| `MorningBrief.tsx` | 582 lines, uses `recharts` Sparklines, `useMorningBrief` + 4 other hooks | 658 lines, **further evolved**: adds `DataFreshness` component, `BrandTreemap`, `CategorySunburst`, `EconomicIndicators`, `useReportCard`, removes recharts dependency | Main is 14 commits ahead ✅ |
| `PriceWire.tsx` | 486 lines, custom sparklines via recharts, `PriceMoverCard`, inline table | 518 lines, **further evolved**: adds `PricePositionMatrix`, `VolatilityRibbon`, `ProximityRadar`, `PriceChangeCascade`, `PriceTicker`, `FlywheelCTA`, `EmptyState`, onboarding awareness | Main is significantly ahead ✅ |

### Key Observations

1. The branch's core pattern (real API hooks replacing mock data) was adopted into main via commit `d208123` ("phase3: Price Wire + Morning Brief frontend (Kimi K2.5)")
2. Main has since undergone **14 additional commits** touching these files, adding:
   - D3 visualization suite (9 chart components)
   - Premium luxury design reskin
   - Number formatting standardization
   - Flywheel product pages and CTAs
   - Report Card integration
   - Onboarding flow awareness
3. The branch uses `recharts` for sparklines; main has removed the `recharts` dependency in favor of D3-based viz components
4. Merging this branch would **destroy** 14 commits worth of frontend evolution

### Verdict: 🛑 ABANDON

**Rationale:** The branch's core contribution (replacing mock data with real API hooks) was merged into main long ago. Main has evolved far beyond this branch with 14+ additional frontend commits adding visualization suites, design system updates, flywheel integration, and accessibility improvements. The branch is 100% obsolete.

---

## Branch 3: `opus/phase5-margin-engine`

**Commits:** 2 ahead of its merge base `d8da566` (`9220f01`, `4dc1795`)  
**Files modified/added (from merge base):**
- `services/api/src/db/schema.ts` — Added `marginRules` table (+15 lines)
- `services/api/src/engine/elasticity.ts` — **NEW** (136 lines): Price elasticity estimation via historical weekly price/volume correlations
- `services/api/src/engine/generator.ts` — **NEW** (201 lines): Recommendation generation engine — market avg comparison, elasticity, margin rule clamping
- `services/api/src/engine/rules.ts` — **NEW** (97 lines): Rule violation evaluator — checks current prices against category min/max bands
- `services/api/src/routes/margin-rules.ts` — **NEW** (201 lines): Full CRUD + violations endpoint for margin rules
- `services/api/src/routes/recommendations.ts` — Extended: added `POST /generate`, `GET /:id` detail, product joins
- `services/api/src/index.ts` — Added `marginRuleRoutes` import and registration

### Comparison to Main

| File | Branch State | Main State | Delta |
|------|-------------|------------|-------|
| `schema.ts` (marginRules) | 15-line `marginRules` table definition | **Identical** — same table exists on main | Already merged ✅ |
| `engine/elasticity.ts` | 136 lines | **Identical** — `diff` shows no differences | Already merged ✅ |
| `engine/generator.ts` | 201 lines | **Identical** — `diff` shows no differences | Already merged ✅ |
| `engine/rules.ts` | 97 lines | **Identical** — `diff` shows no differences | Already merged ✅ |
| `routes/margin-rules.ts` | 201 lines (CRUD + violations) | **Identical** — `diff` shows no differences | Already merged ✅ |
| `routes/recommendations.ts` | Extended with generate + detail | **Identical** — `diff` shows no differences | Already merged ✅ |
| `index.ts` | Added `marginRuleRoutes` | Main has same import + Clerk auth wrapping, security headers, admin key gating, etc. | Main is superset ✅ |

### Key Observations

1. Main's commit `7df1022` ("Phase 5: Margin Engine v1 — rules, elasticity, recommendations (Opus 4.6T)") incorporated this branch's code verbatim
2. The engine files (`elasticity.ts`, `generator.ts`, `rules.ts`) and `margin-rules.ts` routes are **byte-identical** between branch and main
3. Main's `index.ts` has been substantially extended since (Clerk auth, security headers, admin key validation, protected route sub-scoping)
4. Main's `schema.ts` has been extended with `scrapeRuns`, `clerk_user_id`, `platform`/`platform_slug` columns, and relaxed `license_number` constraints
5. Merging this branch would **regress** main's `index.ts` and `schema.ts` to a pre-Clerk, pre-security state

### Verdict: 🛑 ABANDON

**Rationale:** Every single engine file and route from this branch already exists identically on main. Main's `index.ts` and `schema.ts` have evolved significantly beyond the branch with security, auth, and schema changes. Merging would cause destructive regressions.

---

## Code Quality Assessment (Branch Code — Now on Main)

Since the branch code has been absorbed into main, this section reviews the quality of the contributed code as it exists today.

### Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Correctness | 4/5 | APIs work correctly. Elasticity model is reasonable for MVP. SQL queries are sound. |
| Completeness | 4/5 | All specified features implemented. Minor gap: no COGS integration in margin engine. |
| Quality | 4/5 | Clean Drizzle ORM usage, proper ownership checks, good error handling. Security was subsequently hardened on main. |
| Brief Adherence | 5/5 | Phase 3 (Price Wire, Watchlists, Morning Brief) and Phase 5 (Margin Engine) all delivered per spec. |

### Issues Found in Branch Code (Already Fixed on Main)

1. 🟠 **Major — SQL Injection via LIKE:** `prices.ts` used raw string interpolation in `ilike()` patterns (`%${query.sku}%`). Fixed on main with `escapeLike()` helper. *(Fixed in commit `412806d`)*

2. 🟡 **Minor — Date serialization:** Raw SQL queries passed JavaScript `Date` objects directly; PostgreSQL requires ISO strings for reliable timezone handling. Fixed on main. *(Fixed in commit `d8da566`)*

3. ⚪ **Nit — Type assertions:** Branch uses `request.auth.operator_id` without null check (relies on `onRequest: [fastify.authenticate]`). Acceptable given the middleware guarantee, but `request.auth!.operator_id` is more explicit about the non-null assertion.

---

## Recommended Actions

| Branch | Verdict | Action |
|--------|---------|--------|
| `codex/phase3-pricewire` | **ABANDON** | Delete branch (local + remote) |
| `kimi/phase3-morning-brief` | **ABANDON** | Delete branch (local + remote) |
| `opus/phase5-margin-engine` | **ABANDON** | Delete branch (local + remote) |

### Cleanup Commands

```bash
# Delete local branches
git branch -D codex/phase3-pricewire
git branch -D kimi/phase3-morning-brief
git branch -D opus/phase5-margin-engine

# Delete remote branches
git push origin --delete codex/phase3-pricewire
git push origin --delete kimi/phase3-morning-brief
git push origin --delete opus/phase5-margin-engine
```

---

## Why the 580K+ Line Deletion Appeared

The massive deletion count in the branch diffs was **not** because the branches deleted code — it's because main added ~580K lines since the branches were forked:

- CCC CSV data imports (100K+ products, 117K+ prices)
- Scraper data files
- D3 visualization components (9 chart types)
- Clerk authentication system
- Flywheel system
- Admin dashboard
- Report Card system
- Geocoding data
- Security hardening across all routes
- Newsletter, waitlist, profile routes

The branches simply lacked all of this new content, making them appear to "delete" it in a `main..branch` diff.

---

**Conclusion:** All three branches are historical artifacts. Their contributions have been successfully integrated into main and further hardened. No action needed beyond branch cleanup.
