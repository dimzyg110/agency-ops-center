# Store Report Card UI — Build Summary

**Date:** 2026-02-12  
**Commit:** `888befd` on `main`  
**Branch:** `main` (pushed)

---

## What Was Built

### 1. `apps/web/src/types/report-card.ts` — Type Definitions
- Full TypeScript interfaces matching the API contract for `GET /api/v1/report-card/:operator_id`
- `ReportCard` — full response type with operator, grades, sections (pricing, competition, assortment, market position), and actions
- `ReportCardSummary` — lightweight summary type for quick loads
- Status types (`green | yellow | red`) and grade types (`A-F`) exported for reuse

### 2. `apps/web/src/components/ReportCard.tsx` — Main Component (612 lines)
Four exported components:

#### `<ReportCard data={...} />`
- **Overall Health Card** — Large status dot (green/yellow/red) with conversational headline in quotes. Shows grade, operator-facing label ("Looking Good" / "Some Things to Watch" / "Needs Your Attention"), and `generated_at` timestamp.
- **Section Cards** — 4 expandable sections (Pricing, Competition, Your Menu, Market Position):
  - **Pricing** — Tap to expand category breakdown with animated price counters (your avg vs market avg), status per category, diff percentages, and money opportunity callout ($X/week in copper accent)
  - **Competition** — Competitor count, new application count, threat suggestion in conversational tone
  - **Your Menu (Assortment)** — Product count vs market avg, missing categories highlighted, suggestion text
  - **Market Position** — Percentile bar that animates on scroll, "Top X%" display
- **Top Actions** — Priority-colored action cards (high=red, medium=yellow, low=green) with estimated impact in dollar amounts. Links to /recommendations for more.

#### Design Implementation
- **Dark mode** — Uses existing `glass-*` design tokens
- **Status colors** — `#22c55e` (green), `#eab308` (yellow), `#ef4444` (red) with 10% opacity backgrounds and 25% opacity borders
- **Typography** — `font-display` (Playfair) for headings, `font-sans` (Geist) for body, `font-mono` (Geist Mono) for all numbers/prices/labels
- **Copper accent** (`#C45A3C`) — Used for money opportunity callouts and action CTAs
- **Animated number counters** — `useCountUp` hook with ease-out cubic easing, triggered by IntersectionObserver (only animates when visible)
- **Expandable sections** — `animate-slide-down` with chevron rotation
- **Staggered fade-in** — Overall, sections, and actions cards fade in with `translate-y` transitions at increasing delays
- **Mobile-first** — All layouts are single-column by default, grid on `sm:` breakpoint

#### `<ReportCardSkeleton />`
- Matches report card layout exactly: header block, 4 section rows, action area
- Uses `animate-pulse` shimmer on `bg-glass-elevated` blocks

#### `<ReportCardError onRetry={fn} />`
- Calm, non-scary messaging: "Couldn't load your report card. We're on it."
- Retry button with RefreshCw icon

#### `<ReportCardEmpty />`
- For operators who haven't completed onboarding
- "Complete onboarding to see how your store stacks up against the market — in plain English."
- CTA links to `/onboarding`

### 3. `apps/web/src/api/client.ts` — API Methods Added
```typescript
getReportCard(operatorId: string): Promise<ReportCard>
getReportCardSummary(operatorId: string): Promise<ReportCardSummary>
```
- Routes to `GET /api/v1/report-card/:operator_id` and `GET /api/v1/report-card/:operator_id/summary`

### 4. `apps/web/src/api/hooks.ts` — React Query Hooks Added
```typescript
useReportCard(operatorId: string | null)     // 10min refetch, 5min stale, 2 retries
useReportCardSummary(operatorId: string | null) // 5min stale
```
- Both hooks skip fetching when `operatorId` is null (no operator selected)

### 5. `apps/web/src/pages/MorningBrief.tsx` — Integration
- Reads `operatorId` from onboarding localStorage state
- **Report Card renders at the TOP** of the Morning Brief, above all existing content
- Conditional rendering:
  - Operator selected + loading → `<ReportCardSkeleton />`
  - Operator selected + error → `<ReportCardError />` with retry
  - Operator selected + data → `<ReportCard />`
  - No operator → `<ReportCardEmpty />`
- All existing dashboard content (stats, visualizations, Price Wire, Threat Radar, etc.) remains below unchanged

### 6. `apps/web/tailwind.config.ts` — Animation Additions
- `fade-in` keyframe — opacity 0→1 + translateY 8px→0, 0.4s ease-out
- `slide-down` keyframe — opacity 0→1 + maxHeight 0→500px, 0.3s ease-out
- `shimmer` keyframe — backgroundPosition sweep for skeleton loaders

---

## Copy Rules Followed (Maria Review)
- ✅ No jargon — "On Track", "Watch", "Needs Attention" instead of technical terms
- ✅ No percentages in headlines — only in expanded detail views
- ✅ Dollar amounts in opportunities — "$X/week" format
- ✅ Conversational tone — All headlines are wrapped in quotes as conversational snippets
- ✅ Action items start with verbs — Matches the `actions` array from API
- ✅ Every suggestion includes the WHY — Built into the data structure

## Dependencies on Backend
- **API route needed:** `GET /api/v1/report-card/:operator_id` returning `ReportCard` type
- **API route needed:** `GET /api/v1/report-card/:operator_id/summary` returning `ReportCardSummary` type
- Backend agent should build these endpoints matching the types in `types/report-card.ts`

## What's NOT in This PR
- No mock/demo data — component renders only when API returns real data
- No navigation link in Sidebar (the report card is embedded in Morning Brief, not a separate page)
- No SMS/notification integration (separate feature)
