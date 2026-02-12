# GLASS → Product Ecosystem Flywheel UI Plan

## 1) Flywheel Diagram (Text-Based)

```text
[Free Newsletter]
  ↓  (operator opts in, intent + topic signals)
[Free GLASS Dashboard]
  ↓  (proves value with live local data)
[Virtual Budtender — Free Tool]
  ↓  (embedded on operator site; captures shopper preference data)
[Cue — Paid AI Commerce]
  ↓  (turns insight into automated pricing, incentives, forecasting)
[Delivery — Paid Revenue Layer]
  ↓  (captures geo-demand + order behavior)
[Data Feedback Loop]
  └──> Returns to GLASS intelligence models, improving all recommendations
        and making Newsletter + Dashboard more useful (stronger acquisition)
```

**Flywheel logic:** each step is a natural "next capability" from the previous one, not a hard upsell.

---

## 2) Page-by-Page CTA Placement Map (Exact Copy + Placement)

## Design principle for all CTAs
- **Format:** inline feature module (not modal, not popup)
- **Visual:** `rounded-xl border border-glass-border bg-glass-elevated/30 p-4`
- **Accent:** copper left rule `border-l-2 border-glass-accent`
- **Hierarchy:** 1 line value prop + 1 line action link
- **Frequency cap:** max 1 ecosystem CTA block per page

### A. `MorningBrief.tsx`
**Placement:** Immediately **after Price Wire Summary card block**, before Threat Radar summary.

**Copy Option A (Budtender-first):**
- Headline: `Sell faster with AI recommendations`
- Body: `Turn today’s top movers into personalized product picks for your customers.`
- CTA: `Try Virtual Budtender (Free) →`
- Link: `/budtender`

**Copy Option B (Cue-first, conditional if recommendations pending > 5):**
- Headline: `Your top products could reach 3x more customers`
- Body: `Cue turns GLASS signals into automated merchandising and pricing actions.`
- CTA: `Learn about Cue →`
- Link: `/cue`

### B. `PriceWire.tsx`
**Placement:** Directly below **Price Movers (24h)** section and above visualization grid.

**Copy:**
- Headline: `Want this to adjust automatically?`
- Body: `Cue Dynamic Pricing can apply market-based price moves in real-time.`
- CTA: `See Cue Dynamic Pricing →`
- Link: `/cue`

### C. `ThreatRadar.tsx`
**Placement:** Below threat severity chips and above filters. Show only when `critical + high > 0`.

**Copy:**
- Headline: `Beat new competition to delivery coverage`
- Body: `Launch in-demand delivery zones before nearby operators do.`
- CTA: `Join Delivery waitlist →`
- Link: `/delivery`

### D. `Competitors.tsx`
**Placement:** Below `OperatorComparison` and before `MarketShareFlow / PriceWarHeatmap`.

**Copy:**
- Headline: `Outperform them with AI`
- Body: `Cue can optimize pricing, inventory, and incentives against competitor pressure.`
- CTA: `Get early access to Cue →`
- Link: `/cue`

### E. `Market.tsx` (public)
**Placement:** Immediately below the **Price Index — Free** table section.

**Copy:**
- Headline: `Put this data to work in your store`
- Body: `Deploy Virtual Budtender for free and turn market intel into customer recommendations.`
- CTA: `Try Virtual Budtender (Free) →`
- Secondary CTA: `Unlock full GLASS dashboard →` (existing)
- Link: `/budtender`

### F. `Geography.tsx`
**Placement:** Between `MarketTerrainMap` and `DeliveryVoronoi`.

**Copy:**
- Headline: `Delivery demand near you is rising`
- Body: `Delivery is coming to your area — {X} operators interested within {Y} miles.`
- CTA: `Add your location to priority rollout →`
- Link: `/delivery`

### G. `Newsletter.tsx`
**Placement:** In final CTA section, small secondary text under subscribe form.

**Copy:**
- Supporting line: `Want tools, not just reports?`
- CTA: `Use GLASS + Virtual Budtender for free →`
- Link: `/signup` then `/budtender` onboarding step

---

## 3) Virtual Budtender Product Spec (Free Lead Magnet)

## Product definition
A free embedded AI recommender operators place on their ecommerce/site. Powered by GLASS intelligence and store preferences.

## Positioning
- **For operator:** "Increase conversion and basket quality without extra budtender labor."
- **For GLASS:** product-level dependency loop (higher retention than newsletter-only relationship).

## Route + IA
- Public/product page: `/budtender`
- Optional dashboard route alias: `/tools/budtender`
- In-app onboarding entry: from Morning Brief CTA + Sidebar Tools section

## Core user flow
1. Operator discovers Budtender via dashboard/public CTA.
2. Clicks `Get Free Embed`.
3. Completes setup:
   - Store name
   - Website URL
   - Primary objectives (conversion / AOV / education)
   - Top categories
4. Receives:
   - Script tag snippet
   - Theme controls (light/dark, button label)
   - Placement options (floating widget / product page inline)
5. Uses preview panel with demo conversation.
6. Publishes and sees analytics in GLASS.

## MVP features
- Embed code generator
- Recommendation engine seeded from GLASS category/price trends
- Basic controls: tone, category weighting, promoted products
- Analytics mini-dashboard:
  - sessions
  - recommendation click-through rate
  - add-to-cart influence (if available)
  - top recommended SKUs

## Data feedback events (must track)
- `budtender_widget_loaded`
- `budtender_query_submitted`
- `budtender_recommendation_served`
- `budtender_product_clicked`
- `budtender_add_to_cart_attributed`

These feed:
- GLASS demand signals
- Cue forecasting features
- Newsletter insights (category intent trendlines)

---

## 4) Delivery Waitlist Flow (Lead Gen + Location Intelligence)

## Route
`/delivery`

## Form fields (minimum viable)
- Operator/store name
- Work email
- Phone (optional)
- License type
- Address / ZIP / city (required)
- Avg weekly order volume bucket
- Current delivery status (none / in-house / third-party)
- Checkbox: `Notify me when Delivery launches in my zone`

## Post-submit UX
- Success state:
  - `You’re on the list. {N} operators near {City} have requested Delivery.`
  - CTA1: `View Geography demand map`
  - CTA2: `Invite another operator`

## Intelligence outputs
- Convert location to geocode + county + distance clusters
- Build **Delivery Demand Score** per region:
  - weighted by operator volume + density + competitor threat
- Push to dashboard:
  - Geography heatmap layer: `delivery_interest_density`
  - Card: `Delivery coming to your area — X operators interested near you`

## Events to track
- `delivery_waitlist_viewed`
- `delivery_waitlist_started`
- `delivery_waitlist_submitted`
- `delivery_waitlist_geo_clustered`

---

## 5) “Sell Faster” Contextual CTA System Design

## Goal
Inline prompts that feel like intelligence actions.

## Component: `ContextualActionRail`
Single reusable component rendered in-page where context exists.

**Structure:**
- Triggered by page + data condition
- Shows 1 recommendation at a time
- Dismissible for 7 days per user per context
- `Learn more` opens relevant route (no modal)

## Trigger matrix (MVP)
1. **Slow-moving inventory** (Recommendations page)
   - Condition: velocity below threshold
   - Copy: `Cue can auto-discount these SKUs before they stall further.`
   - CTA: `Enable dynamic markdown logic → /cue`

2. **Price comparison active** (PriceWire)
   - Condition: user filtered category + viewed movers
   - Copy: `Dynamic pricing can respond to these market shifts in real-time.`
   - CTA: `/cue`

3. **Brand pressure rising** (Competitors)
   - Condition: price wars + share flow change
   - Copy: `Brand incentives through Cue can offset margin pressure.`
   - CTA: `/cue`

4. **Threat severity high** (ThreatRadar)
   - Condition: high/critical threats present
   - Copy: `Protect local share with Delivery rollout priority.`
   - CTA: `/delivery`

5. **Public market visitor high-intent** (Market)
   - Condition: scrolled past price index + 45s dwell
   - Copy: `Turn these trends into live customer recommendations.`
   - CTA: `/budtender`

## UX constraints
- No more than one contextual rail per viewport section
- No interrupts (no modal/pop-up)
- 12px mono metadata + clean editorial headline + subtle copper indicator

---

## 6) New Pages Needed (`/cue`, `/delivery`, `/budtender`)

## A. `/budtender` (Free Tool + Demo)
Sections:
1. Hero: `Virtual Budtender — Free AI recommendations for your storefront`
2. Live demo widget mock
3. "How it works" (3 steps)
4. Embed code generator teaser
5. Signup / activate form
6. Trust proof: powered by GLASS market data

Primary CTA: `Get Free Embed Code`

## B. `/cue` (Paid Waitlist)
Sections:
1. Hero: `Cue — AI commerce engine for cannabis operators`
2. Capability cards:
   - Demand forecasting
   - Inventory optimization
   - Dynamic pricing
   - Brand incentives
3. Outcomes section (sell-through, margin, stockout reduction)
4. Early access form

Primary CTA: `Join Cue Early Access`

## C. `/delivery` (Interest + geo capture)
Sections:
1. Hero: `Delivery-as-a-Service for cannabis operators`
2. Rollout map teaser
3. Why join now (priority zones, launch cohort)
4. Interest form (location required)
5. Data privacy line

Primary CTA: `Join Delivery Priority List`

---

## 7) Sidebar Navigation Updates

Current sidebar is clean and should remain minimal. Add a **Tools** group only.

## Proposed nav structure
- Morning Brief
- Price Wire
- Threat Radar
- Competitors
- Geography
- Recommendations
- Alerts

**Tools (new section label, mono small):**
- Virtual Budtender (`/budtender` or `/tools/budtender`) — free
- Cue (`/cue`) — badge `Early Access`
- Delivery (`/delivery`) — badge `Waitlist`

## Rules
- Badges muted by default; copper on hover/active
- No flashing/new badges
- Keep same spacing rhythm as existing nav items

---

## 8) Component Specs for Developers

## A. `EcosystemInlineCTA.tsx`
Reusable subtle CTA strip.

**Props**
- `title`
- `body`
- `ctaLabel`
- `href`
- `product: 'budtender' | 'cue' | 'delivery'`
- `condition?: boolean`
- `onView`, `onClick`, `onDismiss`

**Style tokens**
- BG: `bg-glass-elevated/30`
- Border: `border-glass-border`
- Accent: `text-glass-accent`
- Type: headline `font-display`, metadata `font-mono`

## B. `ContextualActionRail.tsx`
Condition-driven action recommender.

**Props**
- `contextKey`
- `rules[]`
- `userState`
- `pageMetrics`

Outputs top-ranked suggestion based on rule score.

## C. `BudtenderEmbedBuilder.tsx`
- Inputs for brand/theme/placement
- Script snippet output with copy button
- Preview pane

## D. `DeliveryInterestForm.tsx`
- Geocoding on submit
- Region scoring hooks
- Success panel with local operator count

## E. `FlywheelAttribution.ts`
Event taxonomy helper with standardized payload fields:
- `source_page`
- `source_module`
- `next_product`
- `operator_id`
- `geo_cluster`

---

## 9) What to Build First (Priority Order)

## Phase 1 (fastest impact, lowest clutter)
1. `EcosystemInlineCTA` component
2. Inject one CTA each into MorningBrief, PriceWire, ThreatRadar, Competitors, Market
3. Create `/cue`, `/delivery`, `/budtender` lightweight pages with forms
4. Sidebar Tools section update

## Phase 2 (data loop instrumentation)
5. Event tracking + attribution schema
6. Delivery geocoding + geography heatmap layer (`delivery_interest_density`)
7. Budtender embed builder MVP

## Phase 3 (optimization)
8. ContextualActionRail scoring rules + dismiss logic
9. Personalization by operator behavior
10. Funnel reporting dashboard (Newsletter → GLASS → Budtender → Cue → Delivery)

---

## 10) How Each Touchpoint Feeds Data Back Into the Flywheel

## Newsletter touchpoints
- Captures intent topics and geography
- Feeds segmentation for dashboard onboarding and CTA relevance

## Dashboard CTA interactions
- Clickstream reveals operator maturity stage (curious vs ready to automate)
- Routes operators to right product next

## Virtual Budtender usage
- Customer query/reco/click behavior feeds demand signals
- Improves GLASS category trends and Cue forecasting priors

## Cue waitlist + product actions
- Captures high-intent automation needs (pricing, inventory, incentives)
- Prioritizes commercial roadmap and packaging

## Delivery waitlist
- Captures exact location demand and market density
- Informs where to launch delivery operations first
- Creates Geography intelligence products for all users

## Geography + Threat integrations
- Delivery interest overlays strengthen threat response recommendations
- Makes GLASS more predictive, improving morning brief quality

## Net result
Each feature acts as both user value and data acquisition. That dual role is the flywheel advantage: **every conversion improves the core intelligence product**.

---

## Appendix: Copy Tone Guardrails
- Sound like operator tooling, not marketing funnel copy.
- Prefer: `Enable`, `Use`, `Apply`, `Preview`.
- Avoid: `Buy now`, `Limited time`, `Don’t miss out`.
- Keep ecosystem mentions contextual to what the user is already analyzing.
