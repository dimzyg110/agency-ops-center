# GLASS Frontend Redesign Plan — Review

**Reviewer:** Senior Product Strategist / UX Architect  
**Date:** 2026-02-13  
**Document Reviewed:** `FRONTEND-REDESIGN-PLAN.md` v2.0  
**Verdict:** **Strong foundation, wrong entry point, needs re-phasing for revenue**

---

## TL;DR

The plan correctly identifies the core shift — from "explore dashboards" to "fix your prices" — and the component strategy is sound. But it has three critical problems:

1. **It ignores the `/market`-as-homepage mandate entirely.** The plan never mentions `/market`. The founder explicitly wants the market data page — CCC cross-reference, license pipeline, weekly sales, data freshness — as the public-facing homepage at `/`, with an email signup hero. This is the sales funnel. It's not in the plan.

2. **Phase A starts with a feature that requires a backend endpoint that doesn't exist yet** (`competitive-context`), which itself requires per-operator product matching — a hard data problem. Meanwhile, the `/market` page is already built, already has real data, and could be shipping as the homepage tomorrow.

3. **The action buttons (Match / Undercut / Hold) are a fiction.** GLASS doesn't control operator menus. There's no POS integration, no write-back API. These buttons would need to generate a "recommended action" that the operator manually executes in their own system. The plan treats these as functional buttons. They're not.

---

## 1. Information Architecture — 7/10

### What's Right
- Collapsing `/prices`, `/threats`, `/recommendations` into `/products` + `/alerts` is correct. The old IA had too many concepts for the same user intent.
- Killing Geography, Morning Brief as standalone pages is correct.
- The four-item nav (Products, Alerts, Report Card, Competitors) is clean.

### What's Wrong

**Missing: `/market` as `/` (homepage)**

The plan maps `/ → /products` for signed-in users and presumably keeps the old `Landing.tsx` for signed-out users. The founder explicitly wants:

```
/               → Market Intelligence page (public, with email signup hero)
                  Signed-in users → redirect to /products
/market         → Redirect to / (or remove entirely)
/landing        → KILL (or redirect to /)
```

The current `App.tsx` already has `<SignedOut><Landing /></SignedOut>` at `/`. The plan should replace `Landing` with an enhanced `Market` page. This is the #1 architectural change and it's completely absent.

**Missing: `/pricing` page**

If you're charging $199/mo, where does the operator see that? Where do they upgrade? The plan has no pricing page, no trial gate, no paywall touchpoint. Right now the system has `subscription_status` on users and Stripe fields, but no frontend UI for it.

**Over-engineered: SKU detail at `/products/:id`**

Having a deep-dive per-SKU is nice in theory. In practice, for Phase 1, this is a luxury. Operators care about the table. The SKU detail can be a slide-out panel or modal — it doesn't need its own route yet. Save the route for when you have enough data to fill it.

### Recommended Route Structure

```
/                   → Market Intelligence (public homepage + email signup)
/login              → Clerk sign-in
/signup             → Clerk sign-up  
/onboarding         → Operator claim (keep existing)
/products           → Product Intelligence Table (auth required) — THE CORE
/products/:id       → SKU Detail (Phase 2 — slide-out first, route later)
/alerts             → Action Queue (auth required)
/report-card        → Executive Summary (auth required)  
/competitors        → Competitor view (auth required)
/settings           → Settings + billing (auth required)
/pricing            → NEW — Pricing page (public, drives conversion)
/report/:slug       → Public report card (keep existing)
```

---

## 2. Prioritization — 5/10 — NEEDS REORDER

### Current Phasing (from plan)
```
Phase A: Product Table + Filters (2-3 weeks)
Phase B: SKU Detail + Competitor View (2 weeks)
Phase C: Alert Engine + Action Queue (2 weeks)
Phase D: Report Card v2 (1-2 weeks)
Phase E: Polish + Mobile (1 week)
```

### The Problem

Phase A requires a brand-new backend endpoint (`competitive-context`) that computes per-operator market position across their entire catalog. This is the hardest query in the entire plan — it needs:

1. Product identity matching (is "Cookies Gelato 3.5g" at Store A the same as "Cookies - Gelato Flower 1/8th" at Store B?)
2. Geospatial competitor filtering
3. Percentile aggregation across matched products
4. Per-operator auth context

You're building the hardest feature first. Meanwhile, you have a working `/market` page that could be the homepage in a day. **Ship what you have. Build what you need.**

### Recommended Phasing

```
Phase 0: Market-as-Homepage (2-3 days) ← SHIP IMMEDIATELY
  - Move /market content to / for signed-out users
  - Add email signup form in hero (Beehiiv embed or waitlist table)
  - Signed-in redirect to /products (stub page initially)
  - Kill Landing.tsx
  - Update nav, SEO, meta tags
  
  WHY FIRST: This is the sales funnel. You have 24 emails to send.
  The market page IS the pitch. Ship it before anything else.

Phase 1: Product Intelligence MVP (2-3 weeks)  
  - Build /products table using EXISTING endpoints
  - Use GET /api/v1/catalog/:operator_id/products for "your products"
  - Use GET /api/v1/products + price aggregation for market context
  - Start with simplified market stats (avg price by category in state)
  - Position badges based on operator's price vs category average
  - No radius-based competitor matching yet (that's Phase 2)
  - Add /pricing page (static, links to Stripe checkout)
  
  WHY: Gets the core screen live with real data. Imperfect but shippable.
  Operators can see their products with at least category-level benchmarks.

Phase 2: Competitive Context API + Enrichment (2 weeks)
  - Build GET /api/v1/products/competitive-context endpoint
  - Add radius-based filtering
  - Product identity matching improvements
  - Upgrade /products table with real competitive stats
  - SKU detail as slide-out panel (not separate route)
  
  WHY: Now you have operators using the product. You know what data 
  they actually look at. You build the hard query with real feedback.

Phase 3: Alert Engine (1-2 weeks)
  - Rewrite /alerts with plain English cards
  - Alert generation service (backend)
  - Action payloads on alerts
  
  WHY: By now operators are trained on /products. Alerts are the 
  retention mechanism — "come back because something changed."

Phase 4: Report Card v2 + Export (1-2 weeks)
  - Reprice queue table
  - Missing SKU analysis  
  - CSV/PDF export
  
Phase 5: Polish + Mobile (1 week)
  - Same as original Phase E
```

**Key difference:** Phase 0 ships in days, not weeks. You can send those 24 outreach emails pointing to a homepage that shows real data, not a marketing page.

---

## 3. API Feasibility — 6/10

### Realistic Assessments

| Proposed Endpoint | Feasibility | Notes |
|---|---|---|
| `GET /products/competitive-context` | **HARD** | Requires solved product matching + geo queries. The SQL in the plan assumes `product_id` matches across operators — it doesn't. Two stores might stock "the same product" but with different `product_id`s because they were scraped from different menus. You need fuzzy matching on (brand + name + weight + category). |
| `GET /products/:id/competitive-landscape` | **MEDIUM** | Easier once competitive-context works — same data, single product filter. |
| `POST /alerts/:id/action` | **EASY** | Alert actions are metadata updates. But "set_price" actions are meaningless without POS integration. |
| `GET /report-card/:id/v2` | **MEDIUM** | Existing report card endpoint exists. Enhancement is straightforward. |
| `POST /prices/bulk-update` | **FICTION** | GLASS doesn't control operator pricing. Remove this. |
| `GET /export/pricing` | **EASY** | CSV generation from existing queries. |

### The Product Matching Problem

The SQL in Section 2.2 assumes:
```sql
LEFT JOIN prices pr ON pr.product_id = op.id
```

This only works if competitor stores stock the exact same `product_id`. But `products` are created during scraping — Store A's "Cookies Gelato 3.5g" creates one product row, Store B's "COOKIES - Gelato Premium Flower" creates another. They're the same SKU to a human, but different `product_id`s in the DB.

The `products.sku` field exists but its uniqueness depends on normalization quality during scraping. This is the hardest unsolved problem in the plan and it's treated as a given.

**Recommendation:** For Phase 1, skip per-SKU competitive matching entirely. Show category-level benchmarks: "Your average flower price is $42/unit. Market average is $38/unit. You're 10% above." This requires zero product matching and uses data you already have.

### Existing Endpoints You Should Use More

The plan doesn't mention several existing endpoints that could power Phase 1:

- `GET /api/v1/prices/movers` — already detects price changes
- `GET /api/v1/scores/leaderboard` — already computes operator rankings
- `GET /api/v1/threats/feed` — already generates threat intel
- `GET /api/v1/recommendations` — already generates price recommendations

These could populate the alerts page and report card with minimal new backend work. The plan proposes rebuilding alert generation from scratch — use what exists first.

---

## 4. Component Strategy — 8/10

### Agree: Kill List
The deprecation list is correct. All 15 viz components identified for deprecation are over-engineered for the target user. Operators don't read Sankey diagrams or Voronoi tessellations. Good call.

### Agree: Keep List
Keeping `Sidebar`, `TopBar`, `DashboardLayout`, `EmptyState`, `DataFreshness`, `ErrorBoundary` is correct. These are structural.

### Disagree: New Component Count

The plan proposes **16 new components**. That's too many for Phase 1. Prioritize:

**Must Build (Phase 1):**
1. `ProductIntelligenceTable` — the core
2. `PricePositionBadge` — visual indicator
3. `FilterBar` — essential for dense tables
4. `ExportButton` — operators need CSV day one

**Build Later:**
5. `AlertFeed` + `AlertActionCard` — Phase 3
6. `RepriceQueueTable` + `MissingSKUTable` + `MarginLeakTable` — Phase 4
7. `SKUDetailView` + `CompetitorPriceTable` + `PriceHistoryChart` — Phase 2

**Probably Never Build:**
8. `ActionRail` — nice idea, but a sticky sidebar on desktop for 3-5 items is over-engineered. Badge count on nav is sufficient.
9. `MobileActionQueue` — solve mobile with responsive tables, not a separate component
10. `QuickActionButtons` (Match/Undercut/Hold) — see next section

### The Action Button Problem

The `QuickActionButtons` component (Match / Undercut / Hold) is the plan's biggest UX fiction. GLASS is a read-only intelligence platform. It scrapes menus. It doesn't write to menus.

When an operator clicks "Match $42," what happens? The plan shows:
```typescript
matchMedian: () => void;      // "Match $42" (sets to market median)
```

Sets it WHERE? GLASS doesn't have POS integration. It can't change the operator's Dutchie menu or Jane menu.

**What these buttons should actually do:**
1. **Log the intent** — "Operator acknowledged this recommendation"
2. **Generate a task** — "Change Cookies Gelato to $42 on your menu" (plain text)
3. **Track follow-through** — Next scrape: did the price actually change?

Rename them from action verbs to decision verbs:
- "Match $42" → "Target $42" (logs the intent)
- "Undercut $1" → "Target $41" 
- "Hold Premium" → "Keep $45"

And add a "Copy to clipboard" for the action item they can paste into their POS workflow.

---

## 5. The `/market`-as-Homepage Pivot — CRITICAL

This is the most important change and it's completely missing from the plan.

### Current State (from `App.tsx`)
```tsx
<Route path="/" element={
  <>
    <SignedOut><Landing /></SignedOut>
    <SignedIn><DashboardEntry /></SignedIn>
  </>
} />
<Route path="/market" element={<Market />} />
```

### What the Founder Wants
```tsx
<Route path="/" element={
  <>
    <SignedOut><MarketHomepage /></SignedOut>  // Market data + email signup
    <SignedIn><Navigate to="/products" /></SignedIn>  // Redirect to dashboard
  </>
} />
// Remove /market as separate route (or redirect to /)
// Remove /landing
```

### What MarketHomepage Should Be

The existing `Market.tsx` (610 lines) is 90% there. It already has:
- ✅ CCC × GLASS cross-reference table
- ✅ Price index by category
- ✅ Weekly sales chart
- ✅ License pipeline
- ✅ Data freshness indicators
- ✅ SEO structured data
- ✅ Responsive layout

What it needs:
1. **Email signup form in the hero section** — Replace the current CTA buttons with an inline email capture form. Use the existing `waitlist` table or Beehiiv embed.
2. **Stronger value proposition copy** — Current hero says "Market intelligence that operators can trust." Should say something more like "The most complete picture of Massachusetts cannabis pricing. Updated daily."
3. **Remove the blurred dashboard teaser** — The "Premium Data Teaser" section with blurred `PricePositionMatrix` / `BrandTreemap` / `MarketTerrainMap` should go. Those viz components are being deprecated. Replace with a clear CTA: "See how YOUR store stacks up → Sign up free"
4. **Remove Demographics section** — Donut charts of gender/race data don't help operators make pricing decisions. Cut it.
5. **Add social proof** — Once you have any customers, add testimonial or usage stats.

### Implementation (this is a 2-3 day task)

```tsx
// App.tsx changes
<Route path="/" element={
  <>
    <SignedOut><MarketHomepage /></SignedOut>
    <SignedIn><Navigate to="/products" replace /></SignedIn>
  </>
} />
<Route path="/market" element={<Navigate to="/" replace />} />
<Route path="/landing" element={<Navigate to="/" replace />} />
```

The `MarketHomepage` component is a modified `Market.tsx` with:
- Email signup form in hero (before the stats grid)
- Removed demographics section
- Removed blurred dashboard teaser (replace with clean CTA)
- Updated CTAs to point to `/signup` or `/pricing`

This is the highest-ROI change in the entire plan. Ship it first.

---

## 6. What's Missing

### 6.1 Pricing Page
No pricing page anywhere. You're charging $199/mo. Where does the operator see this? Where do they enter a credit card?

**Needed:** A simple `/pricing` page with:
- One tier: $199/mo
- Feature list (what free vs paid includes)
- "Start 14-day free trial" button → Stripe Checkout
- FAQ about billing

The `users` table already has `stripe_customer_id`, `stripe_subscription_id`, `subscription_status`. The billing route exists (`routes/billing.ts`). The frontend just doesn't have a page for it.

### 6.2 Trial Experience / Paywall
The plan doesn't address: what do free users see vs paid users? Currently everything behind `<ProtectedRoute>` requires Clerk auth but there's no subscription gate.

**Recommendation:** 
- Free: Market homepage (public), limited product view (top 10 SKUs, no export)
- Paid: Full product table, alerts, report card, export, competitor deep-dive
- Gate: Soft paywall on page load with "Upgrade to see all N products"

### 6.3 Settings Page
The plan mentions `/settings (keep)` but doesn't describe what's in it. For $199/mo customers, settings needs:
- Operator profile (name, location, claimed store)
- Competitor set management (which stores to track)
- Alert preferences (email frequency, severity threshold)
- Billing management (Stripe portal link)
- Radius preference (default competitor radius)

### 6.4 Email Notification System
The alerts page has no mention of email delivery. For operators who aren't logging in daily, email is the primary channel. The `alerts` table has `delivered_email_at` and `delivered_push_at` fields — but the plan doesn't describe when/how alerts get emailed.

### 6.5 Onboarding Updates
The existing onboarding (`Onboarding.tsx`) asks operators to claim their store and pick priorities. The new plan changes the post-onboarding destination from `/` (Morning Brief) to `/products`. This needs updating but isn't mentioned.

### 6.6 Data Quality / Confidence Indicators
The `prices` table has a `confidence` field. The plan's competitive context endpoints don't surface this. If you're showing "Market Median: $42" but it's based on 2 low-confidence scrapes, the operator is getting bad data. Surface confidence and sample size in the UI.

---

## 7. Biggest Risks

### Risk 1: Product Matching (HIGH)
The entire product intelligence table depends on knowing that "Product X at Store A" is the same as "Product Y at Store B." The current `products` table doesn't guarantee this. If matching is poor, the competitive stats will be wrong, and operators will lose trust immediately.

**Mitigation:** Start with category-level benchmarks (no matching needed). Ship per-SKU matching as a progressive enhancement.

### Risk 2: Stale Data Appearance (HIGH)
If a scrape fails for a store and prices are 3+ days old, the competitive context is stale. The plan doesn't address staleness in the product table.

**Mitigation:** Add a "last updated" column to the product table. Dim/badge rows where competitor data is >48h old. Use the `scraped_at` timestamps already in the prices table.

### Risk 3: Action Buttons Create False Expectations (MEDIUM)
"Match $42" implies GLASS will change the price. It won't. Operators will click it and wonder why nothing happened.

**Mitigation:** Rename to "Target $42" and show a workflow tooltip: "Log into your menu platform and update this SKU to $42. We'll verify the change on next scan."

### Risk 4: Over-Scoping Phase A (MEDIUM)
The current Phase A has 8 tasks including a new API endpoint and a new SQL query architecture. For a team where agents are doing the coding, this is 3+ weeks of work before anything ships.

**Mitigation:** Phase 0 (market homepage) ships in days. Phase 1 uses existing endpoints. New backend work starts in Phase 2 after the frontend is live.

### Risk 5: No Customers During Build (HIGH)
If you spend 8-10 weeks building all 5 phases before anyone signs up, you'll have built the wrong thing. The /market-as-homepage with email capture should be live NOW so you can start collecting leads while building the paid product.

**Mitigation:** Phase 0 first. Always.

### Risk 6: Mobile is an Afterthought (LOW-MEDIUM)
Phase E puts mobile last. For operators who check prices from the shop floor (their phone), this matters. But the plan correctly identifies that the full product table is desktop-only — mobile should show alerts.

**Mitigation:** Build `/alerts` and `/products` with responsive tables from the start. Don't build a separate `MobileActionQueue` component — use responsive breakpoints on the same components.

---

## 8. Specific Line-Item Feedback

### SQL Queries
The SQL in Section 2.2 and Section 8.3 won't work as written:
- `PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY UNNEST(competitor_prices))` — you can't use `UNNEST` inside `WITHIN GROUP`. You'd need a subquery or lateral join.
- The `earth_distance` function requires the `earthdistance` extension. Confirm it's installed.
- `est_weekly_volume` in the reprice queue query (Section 8.3, Query 3) is referenced but never defined.

These are implementation details, but they signal that the queries weren't tested. The implementation agent should treat these as pseudocode, not production SQL.

### The "Process All" Button
The Action Rail has a `[Process All]` button that would bulk-execute all alert actions. This is dangerous even as a concept — an operator shouldn't be able to "process all" pricing changes with one click, especially when GLASS can't actually execute them. Remove this.

### Export Strategy
The plan mentions CSV export but not what columns are exported, or whether the export respects current filters. Specify: "Export exports the current filtered view as CSV with all visible columns."

### Success Metrics
The "Price action rate" target of >30% is ambitious. In B2B SaaS, feature adoption rates of 15-20% are strong. Set the target at >15% for first quarter.

---

## 9. Summary of Recommended Changes

| # | Change | Priority | Effort |
|---|--------|----------|--------|
| 1 | Add Phase 0: Market-as-homepage with email signup | **P0** | 2-3 days |
| 2 | Reorder phases: 0 → 1 → 2 → 3 → 4 → 5 | **P0** | Plan change only |
| 3 | Rename action buttons from "Match/Undercut" to "Target" + workflow copy | **P0** | Design change |
| 4 | Remove `POST /prices/bulk-update` — GLASS can't write to menus | **P0** | Remove from plan |
| 5 | Add `/pricing` page to plan | **P1** | 1-2 days |
| 6 | Address product matching problem explicitly | **P1** | Plan section |
| 7 | Phase 1 uses existing API endpoints, not new ones | **P1** | Plan change |
| 8 | Add data staleness handling to product table design | **P1** | Design detail |
| 9 | Kill `ActionRail` and `MobileActionQueue` — use responsive design | **P2** | Simplification |
| 10 | Kill demographics section from market page | **P2** | Simplification |
| 11 | Add settings page specification | **P2** | Plan section |
| 12 | Fix SQL pseudocode (UNNEST, est_weekly_volume) | **P2** | Correction |

---

## 10. Final Verdict

**The plan's vision is right. The execution order is wrong.**

The founder has a working `/market` page with real CCC data, a database of 100K+ products and 117K prices, and 24 outreach emails ready to send. The plan proposes spending 2-3 weeks building a new product table and new API endpoint before shipping anything.

**Ship the homepage. Collect emails. Build the dashboard in parallel.**

The plan should be updated with:
1. Phase 0 (market homepage) as the immediate deliverable
2. `/pricing` page for conversion
3. Realistic action button behavior (log intent, not execute changes)
4. Product matching as a known hard problem with a phased solution
5. Existing endpoints as the Phase 1 data source

Once these changes are integrated, hand Phase 0 to the frontend agent immediately. It's a 2-3 day task using existing code. The 24 outreach emails should point to the new homepage, not the current marketing landing page.

---

*Review complete. Ready for plan revision and implementation handoff.*
