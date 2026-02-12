# GLASS Operator Onboarding Design

## Objective
Design a first-run onboarding that gets a new operator invested in <60 seconds, proves immediate value with personalized market data, captures key business intent, and introduces the GLASS ecosystem naturally (Virtual Budtender, Cue, Delivery).

---

## Experience Principles

1. **Value before form** — show “we already track you” immediately.
2. **Fast + mobile-first** — one clear action per screen, thumb-friendly controls.
3. **Personalized by default** — dispensary + local market context in every step.
4. **Natural ecosystem handoff** — recommendations should feel operational, not salesy.
5. **Tone + visual continuity**
   - Onboarding: **Light mode** (white background, low friction)
   - App: **Dark mode** once onboarding completes
   - Primary accent: `glass.accent #C45A3C`
   - Typography: Display moments in `font-display` (Playfair fallback), body in Geist/sans

---

## Flow Overview (4 steps + dashboard entry)

- **Step 1 (10s): Claim Your Dispensary**
- **Step 2 (20s): Your Market at a Glance**
- **Step 3 (15s): What Matters to You?**
- **Step 4 (15s): Your Toolkit**
- **Step 5: Enter Dashboard + lightweight guided tour**

**Progress pattern:** top progress bar + label (`Step 1 of 4`) + optional skip (`Skip for now`) on steps 2–4.

---

## 1) Full Flow with Screen Descriptions + Copy

## Global Onboarding Shell
- Header left: GLASS wordmark
- Header right: `Step X of 4`
- Thin progress bar using copper accent
- Body in single-column on mobile, split layout on desktop
- Primary CTA: rounded-full button, copper/black variant

### Step 1 — Claim Your Dispensary
**Goal:** create immediate trust and personalization anchor.

#### Screen 1A: Search existing operator
**Headline:** `Claim your dispensary in 10 seconds`
**Body:** `We already track 492+ operators in Massachusetts. Find yours to unlock your live market view.`
**Input placeholder:** `Search dispensary name, city, or ZIP`
**Helper text:** `Can’t find it? Add it manually.`
**Primary CTA (after select):** `Claim Dispensary`
**Secondary CTA:** `Add my dispensary`

#### Screen 1B: Match found confirmation
**Headline:** `We’re already tracking {{dispensary_name}}`
**Body:** `Great — we’ve collected pricing, competitor proximity, and threat signals for your market.`
**Info cards (3 chips):**
- `Products tracked: {{count}}`
- `Nearby competitors: {{count}}`
- `Last update: {{relative_time}}`
**Primary CTA:** `See My Market`

#### Screen 1C: Manual add (if not found)
**Headline:** `Add your dispensary`
**Fields:**
- Dispensary name (required)
- City (required)
- Website URL (optional but recommended)
**Body:** `We’ll start tracking your market immediately and personalize your dashboard.`
**Primary CTA:** `Save & Continue`
**Back link:** `Back to search`

---

### Step 2 — Your Market at a Glance
**Goal:** prove concrete value from GLASS data immediately.

**Headline:** `Your market at a glance`
**Subhead:** `This updates daily. Automatically.`

**Three personalized cards:**
1. **Price Position**
   - `Your avg price: ${{operator_avg}}`
   - `Market avg: ${{market_avg}}`
   - Delta badge: `{{+/-percent}} vs market`
2. **Competitors Nearby**
   - `{{count}} competitors within 10 miles`
   - Top 3 nearby names + distance chips
3. **Active Threats**
   - `{{count}} active threats near you`
   - Severity chips: Critical / High / Medium / Low

**Micro-proof line:** `You now have a live baseline to benchmark your store every day.`

**Primary CTA:** `Looks Good`
**Secondary CTA:** `Adjust Location`

---

### Step 3 — What Matters to You?
**Goal:** capture intent for personalization + lifecycle targeting.

**Headline:** `What matters most right now?`
**Body:** `Pick up to 3 priorities. We’ll tailor your dashboard and recommendations.`

**Selectable options (multi-select, max 3):**
- Track competitor prices
- Find new product trends
- Monitor regulatory changes
- Optimize my inventory
- Reach more customers
- Explore delivery

**Interaction details:**
- Minimum 1 required
- If user taps 4th option, toast: `Choose up to 3 priorities`

**Primary CTA:** `Continue`
**Secondary CTA:** `Skip for now`

---

### Step 4 — Your Toolkit
**Goal:** contextual product discovery without hard sell.

**Headline:** `Your toolkit is ready`
**Body:** `Based on your priorities, here’s what to use next.`

Dynamic recommendation modules:

#### If “Reach more customers” selected
- **Card:** `🤖 Virtual Budtender (Free)`
- **Copy:** `Turn your top products into personalized customer recommendations.`
- **CTA:** `Try Virtual Budtender`

#### If “Optimize my inventory” selected
- **Card:** `📦 Cue (Early Access)`
- **Copy:** `Forecast demand and optimize inventory using GLASS market signals.`
- **CTA:** `Join Cue Early Access`

#### If “Explore delivery” selected
- **Card:** `🚗 Delivery (Waitlist)`
- **Copy:** `Help us prioritize your zone for upcoming delivery rollout.`
- **CTA:** `Join Delivery Waitlist`

#### Always include core anchor card
- **Card:** `Morning Brief`
- **Copy:** `Your daily summary is ready with your dispensary highlighted.`
- **CTA:** `Open My Dashboard`

**Primary CTA (footer):** `Go to Dashboard`

---

### Step 5 — Dashboard Entry (Dark mode)
**Trigger:** user exits Step 4 or returns after skipped steps.

#### First-session overlays
1. **Welcome toast:** `You’re all set, {{first_name}}. Your market updates are live.`
2. **One-time tooltip tour (dismissible):**
   - Morning Brief hero (`Daily summary`)
   - Price Wire section (`Monitor competitor pricing`)
   - Threat Radar (`Track local risks`)
   - Tools section in sidebar (`Budtender, Cue, Delivery`)
3. **Email prompt card in Morning Brief (inline):**
   - Headline: `Get your weekly operator report`
   - Body: `A concise weekly summary of margin, threats, and opportunities.`
   - CTA: `Send It Weekly`
   - Secondary: `Not now`

---

## 2) Data Requirements per Step (API + payload)

## Step 1: Claim Your Dispensary
1. `GET /operators/search?q={query}`
   - Returns: id, name, city, state, website, trackedProductCount, lastUpdatedAt
2. `POST /onboarding/claim-operator`
   - Body: `{ userId, operatorId }`
3. `POST /onboarding/manual-operator`
   - Body: `{ userId, name, city, website }`
   - Returns created operator profile + pending verification flag

## Step 2: Market Snapshot
4. `GET /onboarding/market-snapshot?operatorId={id}`
   - Returns:
     - `operatorAvgPrice`
     - `marketAvgPrice`
     - `priceDeltaPercent`
     - `competitorsWithin10Mi[]`
     - `activeThreatCount`
     - `severityBreakdown`
     - `generatedAt`

## Step 3: Priorities
5. `POST /onboarding/priorities`
   - Body: `{ userId, operatorId, priorities: string[] }`

## Step 4: Toolkit Personalization
6. `GET /onboarding/toolkit?userId={id}`
   - Returns ranked tool recommendations + reason tags
7. Optional action routes:
   - `POST /budtender/waitlist`
   - `POST /cue/waitlist`
   - `POST /delivery/waitlist`

## Step 5: Completion + Dashboard personalization
8. `POST /onboarding/complete`
   - Body: `{ userId, operatorId, completedAt, skippedSteps[] }`
9. `GET /dashboard/morning-brief?operatorId={id}&highlight=true`
10. `POST /notifications/weekly-report-optin`

### Event Tracking (must-have)
- `onboarding_started`
- `disp_search_used`
- `disp_claimed`
- `disp_manual_added`
- `market_snapshot_viewed`
- `priorities_selected`
- `toolkit_cta_clicked`
- `onboarding_completed`
- `onboarding_skipped`

---

## 3) Component Breakdown for Developers

## New components
1. `OnboardingLayout`
   - Props: `step`, `totalSteps`, `onBack`, `onSkip`
2. `DispensarySearchSelect`
   - Async search + result list + quick claim
3. `ManualDispensaryForm`
4. `MarketSnapshotCards`
   - Price position, competitors, threats
5. `PriorityPicker`
   - Multi-select with max cap and validation
6. `ToolkitRecommendations`
   - Conditional cards from priorities map
7. `OnboardingProgress`
8. `FirstRunTour` (dashboard tooltip overlay)
9. `WeeklyReportPromptCard`

## Existing integration points
- Routing guard: if `user.onboardingCompleted !== true` then redirect to `/onboarding`
- `MorningBrief` support for highlighted operator context banner
- `Sidebar` tool labels can include subtle badges (Free / Early Access / Waitlist)

## Style tokens to apply
- Light onboarding backgrounds: `#FFFFFF`, `glass.light.*`
- Primary action accent: `glass.accent`
- Typography: `font-display` for headline, `font-sans`/`font-mono` for UI labels
- Button style: rounded full, no heavy gradients, clean editorial spacing

---

## 4) Empty State Designs (New user / no data)

## Morning Brief
**Headline:** `We’re building your first market brief`
**Body:** `Data is syncing for {{dispensary_name}}. You’ll see your first live summary soon.`
**CTA:** `Invite a teammate`
**Secondary:** `Browse sample market insights`

## Price Wire
**Headline:** `No tracked price history yet`
**Body:** `Once your feed updates, you’ll see price movers and competitor shifts here.`
**CTA:** `View sample price movers`

## Threat Radar
**Headline:** `No threats detected yet`
**Body:** `Good news. We’ll alert you when new nearby risks are detected.`
**CTA:** `Set alert preferences`

## Competitors
**Headline:** `No nearby competitors mapped yet`
**Body:** `Confirm your dispensary location to map competitors within 10 miles.`
**CTA:** `Confirm location`

## Geography
**Headline:** `Market map is warming up`
**Body:** `We’re preparing your local density and demand overlays.`
**CTA:** `See statewide map preview`

## Recommendations
**Headline:** `No recommendations yet`
**Body:** `As we learn your priorities and trends, recommendations will appear here.`
**CTA:** `Set priorities`

## Alerts
**Headline:** `You’re all clear`
**Body:** `No alerts right now. We’ll notify you when something needs attention.`
**CTA:** `Manage notification settings`

## Budtender / Cue / Delivery pages (if no signup state)
- Budtender: `Get your free embed code`
- Cue: `Join early access`
- Delivery: `Join priority list`

---

## 5) Progressive Disclosure Strategy

## Phase A — First session (Day 0)
- Core only: Morning Brief + 3 key metrics + basic navigation
- One ecosystem recommendation max in-view

## Phase B — Early usage (Days 1–7)
Unlock after conditions:
- Visits Price Wire 2x → show advanced filters chip
- Opens Threat Radar 2x → show severity trend mini chart
- Clicks Recommendations 1x → enable “explain why” row

## Phase C — Activated operator (Week 2+)
- Unlock strategic modules:
  - competitor benchmark exports
  - weekly trend digests
  - opportunity scoring
- Show deeper prompts for Cue/Delivery only after repeated high-intent behavior

**Rule:** never reveal everything at once; reveal by demonstrated intent.

---

## 6) Re-engagement Email Sequence (No login triggers)

## Day 1 (if signed up but did not complete onboarding)
**Subject:** `Your dispensary data is ready in GLASS`
**Body:**
`You’re one step away from seeing your live market snapshot.
Claim your dispensary and view your local pricing + threats in under a minute.`
**CTA:** `Complete setup`

## Day 3 (if onboarding complete but no return session)
**Subject:** `3 market changes near {{city}} this week`
**Body:**
`Your market moved since you signed up. GLASS detected fresh pricing activity and nearby threat signals.
Open your Morning Brief to see what changed.`
**CTA:** `View my Morning Brief`

## Day 7 (no login)
**Subject:** `How do you compare to operators near you?`
**Body:**
`We prepared your benchmark view: average price position, nearby competitor count, and active threat levels.
Take 60 seconds to check your standing.`
**CTA:** `See my benchmark`

## Day 14 (no login)
**Subject:** `Keep GLASS working for you every week`
**Body:**
`If daily check-ins are hard, enable weekly operator reports.
You’ll get one concise summary with the biggest pricing and risk changes in your market.`
**CTA:** `Enable weekly report`

---

## 7) Upgrade Prompt Triggers + Copy (Cue / Delivery / Budtender)

## Virtual Budtender prompt
**Trigger:** user selected “Reach more customers” OR clicked product trend cards 2+ times.
**Placement:** inline card in Morning Brief and Recommendations.
**Copy:**
- Title: `Turn insights into customer conversations`
- Body: `Use Virtual Budtender (free) to recommend products on your storefront.`
- CTA: `Try Virtual Budtender`

## Cue prompt
**Trigger:** user selected “Optimize inventory” OR visits Recommendations 3+ times in 7 days.
**Copy:**
- Title: `Ready for automated inventory decisions?`
- Body: `Cue uses GLASS signals for forecasting, pricing, and inventory optimization.`
- CTA: `Join Cue Early Access`

## Delivery prompt
**Trigger:** user selected “Explore delivery” OR high threat activity in nearby radius.
**Copy:**
- Title: `Delivery demand is rising near you`
- Body: `Join the waitlist so we can prioritize rollout in your area.`
- CTA: `Join Delivery Waitlist`

**Prompt guardrails:** max 1 ecosystem upsell module per page, dismissible for 7 days.

---

## 8) Mobile Layout Considerations

1. **Single-column first**: all onboarding steps vertically stacked.
2. **Sticky footer CTA** on mobile for consistent progression.
3. **Tap targets** minimum 44px high.
4. **Search UX**
   - Autocomplete opens full-width sheet
   - Top 5 results visible without extra scroll
5. **Market cards** become swipeable carousel on small screens.
6. **Priority picker** as 2-column pills on mobile, 3-column desktop.
7. **Progress visibility** always pinned at top.
8. **Reduce typing**: use suggestions, chips, pre-filled values from Clerk profile where possible.

---

## 9) Success Metrics (What good onboarding looks like)

## Primary activation metrics
- **Onboarding completion rate:** target **>70%**
- **Median completion time:** target **<60 seconds**
- **Step 1 completion (claim/manual add):** target **>85%**
- **Step 2 “value seen” rate (snapshot viewed):** target **>90% of Step 1 completers**

## Quality + retention metrics
- **Day 1 return rate:** target **>35%**
- **Day 7 return rate:** target **>25%**
- **Weekly report opt-in:** target **>30%**
- **At least one ecosystem CTA click in first 7 days:** target **>20%**

## Funnel diagnostics
- Search abandon rate in Step 1
- Manual add rate (measures database coverage gaps)
- Priority distribution (product demand signal)
- First-page dropoff after dashboard entry

---

## 10) Implementation Priority (Build order)

## P0 (must-have for launch)
1. Onboarding route guard + step state model
2. Step 1 dispensary search/claim + manual add fallback
3. Step 2 market snapshot cards from real data
4. Step 3 priorities capture
5. Step 4 toolkit recommendation logic
6. Onboarding complete → Morning Brief highlight + theme switch light→dark

## P1 (improves activation)
7. First-run tooltip tour on dashboard
8. Weekly report prompt + opt-in
9. Empty states across core pages
10. Event tracking pipeline + dashboard funnel metrics

## P2 (growth / optimization)
11. Progressive disclosure unlock rules
12. Smart upgrade prompts with behavior triggers
13. Re-engagement email automation (Day 1/3/7/14)
14. A/B tests on Step 1 copy and Step 2 card order

---

## Priority Mapping Logic (for engineering)

```ts
const toolkitMap = {
  'Reach more customers': ['budtender'],
  'Optimize my inventory': ['cue'],
  'Explore delivery': ['delivery'],
  'Track competitor prices': ['morning_brief', 'price_wire'],
  'Find new product trends': ['morning_brief', 'recommendations'],
  'Monitor regulatory changes': ['threat_radar', 'alerts'],
};
```

Always include `morning_brief` as default destination.

---

## Final UX Notes
- Keep each step emotionally rewarding: “you’re set,” “data is live,” “toolkit is ready.”
- Make Step 1 feel like a reveal, not registration.
- Preserve editorial GLASS tone: precise, calm, operator-first.
- Every onboarding decision should answer: **“Does this make the operator feel more in control of their market right now?”**
