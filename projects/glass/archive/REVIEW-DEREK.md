# GLASS Platform Review — Multi-Location Operator Perspective

**Reviewer:** Derek, 35 | Owner/Operator, 4 MA Dispensaries (Boston, Worcester, Springfield, Pittsfield)  
**Team:** 45 employees | **Current tech spend:** $18K/mo (Dutchie, Leafly, POS, payroll)  
**Review date:** February 12, 2026  
**Status:** Just signed up. Walked through the full experience — landing page, market page, logged-in dashboard, Report Card, Price Wire, Threat Radar, Recommendations. Reviewed all data assets.

---

## TL;DR Verdict

**GLASS has the best raw cannabis market dataset I've ever seen assembled in one place.** 511K+ rows, 7 years of CCC data, 100K+ products across 490+ dispensaries, 147K lab tests, pending license applications — nobody else has this in Massachusetts. The Store Report Card showing my price position by category with color-coded status and dollar-value opportunities is the single most useful thing I've seen in cannabis tech. The CCC-vs-shelf cross-reference on the public Market page is genuinely impressive data work.

**But it's not ready for a multi-location operator like me yet.** There's no portfolio view — I can only claim one dispensary during onboarding. The daily scraping literally started today (every WoW column says "New" with dashes). Three of four headline features on the landing page say "COMING SOON." The Recommendations page still tells operators to *lower* prices, which contradicts the Report Card's smarter framing. And there are no integrations with the tools I already use.

**I'd pay for this in 60-90 days if they nail the multi-store experience and prove the daily data is reliable.** The Report Card is close to a "shut up and take my money" moment — it just needs time-series data behind it and multi-location support in front of it.

**Rating: 7.5/10 on potential. 4.5/10 on readiness for my use case today.**

---

## The Walkthrough: What I Actually Saw

Before I get into the 8 questions, here's what I experienced walking through the product. This matters because my first impression shapes whether I bring this to my ops team or delete the bookmark.

### Landing Page (glassintel.xyz)

**The headline nails it:** "See what your competitors charge." Six words. That's exactly what I'm trying to do. The subtext — "GLASS tracks every price change across Massachusetts dispensaries" — is clean and credible. No weed leaves, no neon green, no stoner vibes. It looks like a finance product. Good.

**The problem:** I scroll down and I see four feature sections — Price Wire ("Every price. Every dispensary. Updated daily."), Threat Radar, Morning Brief, and Cue. Three of the four say "COMING SOON." That's a credibility hit. You led with a strong promise and immediately told me most of the product doesn't exist yet. For a single-location operator checking this out casually, maybe they shrug. For me evaluating whether to roll this out across 4 stores? It tells me I'm early. Maybe too early.

The bottom of the page shows the "ecosystem" — GLASS (LIVE), Virtual Budtender (LIVE), Cue (COMING SOON). I appreciate the honesty about what's live and what's not. But the Cue positioning as "Train, Motivate, and Reward Your Budtenders" with "$200-500/month for budtenders" — that's a completely different pitch from the pricing intelligence that hooked me. Pick a lane. Am I here for competitive pricing intel or budtender incentives? The landing page tries to be both.

### Market Page (glassintel.xyz/market)

**This is the best page on the entire site.** The public Market page shows:

- **301 operators tracked, 100.8K products, 117K price observations** — credible scale
- **CCC × GLASS cross-reference table** — This is the moment where I sat up in my chair:

| Category | CCC Transfer Avg | GLASS Shelf Avg | Retail Premium |
|----------|-----------------|-----------------|----------------|
| Concentrate | $17.35 | $41.98 | +142% |
| Edible | $3.55 | $17.89 | +404% |
| Flower | $4.04 | $10.08 | +149.5% |
| Vape | $26.64 | $35.48 | +33.2% |

This table tells me something I've never seen anywhere else: the gap between what dispensaries pay (CCC transfer prices) and what they charge (real shelf prices from 490+ menus). The fact that edible markup is 404% while vape is only 33% — that's the kind of insight that changes how I think about my product mix. I can see immediately which categories have margin room and which are getting squeezed.

**What's missing:** It's statewide. I don't care about the Massachusetts average. I need this for the Boston market specifically, or better yet, for the 15 dispensaries within 5 miles of my East Boston store. The "Want these insights for YOUR store?" CTA at the bottom is the right move — but I shouldn't have to sign up to see neighborhood-level data. Show me a teaser. "In your area, flower markup is 165% vs. the state average of 149%." That would get me to sign up in 5 seconds.

### Logged-In Dashboard — The Report Card

This is where GLASS earns its keep. After onboarding (claim your dispensary, see your market snapshot, pick priorities), the Morning Brief shows a **Store Report Card**. Using Cannabis Healing as the example operator:

| Category | Your Avg | Market Avg | Diff | Status |
|----------|----------|------------|------|--------|
| Flower | $31.99 | $35.30 | -9.4% | 🟡 Priced below market — room to earn more |
| Preroll | $15.55 | $18.57 | -16.3% | 🔴 Leaving money on the table |
| Vape | $48.52 | $35.45 | +36.9% | 🟡 Premium position — monitor velocity |
| Edible | $22.90 | $17.89 | +28.0% | 🟡 Premium position — monitor velocity |
| Concentrate | $45.00 | $41.98 | +7.2% | 🟢 Healthy positioning |

**This is excellent.** Green/yellow/red with plain-English explanations. The framing is smart — it never says "lower your prices." When you're below market, it says "room to earn more." When you're above market, it says "premium position — monitor velocity." That's how an operator thinks. I don't want a tool that tells me to cut prices. I want a tool that tells me where I'm leaving money on the table.

The Report Card also shows:
- **Estimated opportunity:** "Potential extra margin from underpriced categories: $XXX/week" — Dollar amounts. Not percentages. This is how to talk to operators.
- **Actions:** "Your prerolls are priced 16.3% below market average. Raising to market rate could add ~$X/week in margin." Actionable, specific, dollar-denominated.
- **Competition context:** Nearby competitor count, nearest competitor, new threats
- **Market position:** Percentile ranking among all tracked operators

For a single-store operator, this Report Card is worth $199/mo by itself. The question for me is: can I see this for all 4 of my stores?

### The Contradiction: Report Card vs. Recommendations Page

Here's something that would piss me off as a subscriber. The Report Card tells me "your prerolls are below market — room to earn more" (implying: raise prices). But the Recommendations page — which should be the action layer on top of the Report Card — still uses the OLD framing from seed data:

- "2-pack preroll bundle: $19 → $17" (reduce price)
- "1g vape cart: $72 → $68" (reduce price)
- "Gummy: $34 → $31" (reduce price)

Every single recommendation says to LOWER prices. That directly contradicts the Report Card, which just told me I'm underpriced on prerolls. The demo brief itself flags this as a "P1 fix" — the recommendations seed data wasn't updated to match the new framing.

This is the kind of inconsistency that would make me close the tab. If the tool can't agree with itself on whether I should raise or lower prices, why would I trust either recommendation? **Fix this before any real operator sees it.** Every recommendation needs to match the Report Card's "opportunity" framing: "Your prerolls at $15.55 are 16.3% below your local market. Matching the market at $18 could add $X/week."

### Price Wire

Searchable table of all 100,849 products with prices. Filter by category, brand, operator. This is the raw competitive data — every product, every price, every dispensary. The "Watch" button to track specific products/competitors is a nice touch.

For my analyst, this replaces the Monday morning manual data-entry session. Instead of opening 20 Dutchie pages and copying prices into Excel, she can search "flower, Worcester, within 5 miles" and get everything instantly with CSV export. That alone saves 3 hours/week.

**What I'd improve:** The Price Wire needs saved views. Let me save "Worcester competitors — flower" as a bookmark I can check every morning without re-entering filters. And it needs a "compare to my price" column that shows the delta, not just the raw competitor number.

### Threat Radar

Shows 6 active threats with severity ratings:

1. 🔴 **New Adult-Use Retail Applicant — Kendall Square** (HIGH) — Host community agreement filed
2. 🔴 **Worcester Cluster** (CRITICAL) — Three stores dropped eighth pricing below $32
3. 🟡 **MA Cannabis Control Commission** (MEDIUM) — Tighter packaging disclosure enforcement
4. 🔴 **Berkshire Distribution Lane** (HIGH) — Weather delays reducing concentrate shipments
5. 🟡 **Boston Metro Compliance Sweep** (MEDIUM) — Increased spot checks on promo claims
6. 🟢 **Lowell/North Shore Value Segment** (LOW) — Sustained bundle discounts pressuring margins

The Worcester Cluster alert is exactly the kind of intelligence that would get me to open this at 6 AM. If three competitors near my Worcester store just dropped below $32 for eighths, I need to know NOW, not next Tuesday when my analyst finishes her spreadsheet.

**But here's the catch:** These are seed data. They're realistic-looking examples, not live intelligence from today's scraping. The threats are well-constructed (severity, proximity, competitive impact) but they're preloaded demonstrations. When the daily scraper is stable and generating real alerts from actual price changes detected overnight, this feature becomes a morning must-check. Until then, it's a mockup.

### Nearby Competitor Intelligence

The demo shows 15+ dispensaries in the Cannabis Healing area (East Boston), each with product counts (390-483 products) and average pricing. Price range spans from $19.73 avg (quincy-cannabis) to $35.41 avg (native-sun), with Cannabis Healing at $31.99 avg flower sitting in the upper-middle.

**This is the data I'd use daily.** Knowing that there are 15 dispensaries nearby and exactly where my pricing falls in that range — that's the core value proposition delivered. For my 4 locations, I'd want this view for each store: "Here are your 8-15 closest competitors and where you rank."

---

## Question 1: Multi-Location — Can I See All 4 Stores on One Dashboard?

### The Short Answer: No. And That's a Problem.

GLASS currently operates on a single-operator model. During onboarding, you claim ONE dispensary. Your Morning Brief, Report Card, Price Wire, and Threat Radar are all scoped to that one location. There's a "location selector" in the top bar, but the underlying architecture is one-user-to-one-operator. I'd need to log in/out or switch contexts to see each store.

For a single-location operator? Fine. For me running Boston, Worcester, Springfield, and Pittsfield? Dealbreaker territory.

### What the Ideal Multi-Store View Looks Like

Here's exactly what I need — and what would make me a customer tomorrow:

**Portfolio Dashboard (the "Command Center")**

```
┌──────────────────────────────────────────────────────────────┐
│  PORTFOLIO OVERVIEW — Derek's Dispensaries                   │
│  February 12, 2026 | 6:12 AM                                │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ BOSTON    │ │ WORCESTER│ │SPRINGFLD │ │PITTSFIELD│       │
│  │ 🟢 A-    │ │ 🟡 B+    │ │ 🔴 C     │ │ 🟢 B+    │       │
│  │ +2% mkt  │ │ -4% mkt  │ │ -11% mkt │ │ +1% mkt  │       │
│  │ 0 threats│ │ 2 threats│ │ 1 threat │ │ 0 threats│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
│  🔴 URGENT: Springfield flower is 11% above market.          │
│     3 competitors dropped prices this week.                  │
│     Suggested action: Review 4 SKUs → [See Details]          │
│                                                              │
│  🟡 WATCH: Worcester has 2 pending license apps within       │
│     3 miles. Both are retail. Expected opening: Q3 2026.     │
│                                                              │
│  📊 PORTFOLIO TOTAL: 847 products tracked | Avg position:    │
│     12th percentile (competitive) | Est. weekly opportunity:  │
│     $1,200 across all locations                              │
└──────────────────────────────────────────────────────────────┘
```

**What I actually need:**
1. **One login, all stores.** Drop-down to drill into any one store, but the default view shows the portfolio.
2. **Comparative Report Cards.** Side-by-side green/yellow/red for each location, same categories.
3. **Cross-location pricing consistency check.** Am I charging $45 for Blue Dream in Boston and $38 in Worcester? I need to know — and I need to know if that's intentional (market-appropriate) or a mistake.
4. **Aggregated threat radar.** Show me ALL pending applications near ALL my stores on one map.
5. **Rolled-up opportunity dollars.** "You're leaving an estimated $4,800/month across your 4 locations." That number gets my attention.
6. **Per-store drill-down.** Click any store → full Store Report Card, Price Wire, competitor view.

### Gap Assessment

The data model supports this — operators are already in the database with lat/lon and products. The Report Card API already calculates per-operator scores. What's missing is:

- A `user_operators` join table (one user → many operators)
- A portfolio aggregation endpoint
- A multi-store UI component
- Cross-location consistency checks

This isn't a massive engineering lift. It's a product decision they haven't made yet because they're still chasing single-location operators for PMF. But for operators like me who represent 35+ of those 180+ leads in their contact database? Multi-location support is the difference between a free user who checks occasionally and a $499-999/mo enterprise subscriber.

**My ask: Make multi-location a P0 for the Enterprise tier. I'll be the design partner.**

---

## Question 2: ROI Justification — Show Me the Math

### What I Currently Spend on Market Intelligence

| Line Item | Monthly Cost | Annual Cost |
|-----------|-------------|-------------|
| Analyst checking competitor menus (15 hrs/wk × $25/hr) | $1,625 | $19,500 |
| My own time building Excel pricing sheets (5 hrs/wk) | ~$2,500 (opportunity cost at my rate) | ~$30,000 |
| Leafly listing fees (4 locations) | ~$1,200 | ~$14,400 |
| Dutchie fees (4 locations) | ~$2,400 | ~$28,800 |
| Ad hoc market research (quarterly reports, consultants) | ~$500 | ~$6,000 |
| **Total intelligence/decision-support spend** | **~$8,225** | **~$98,700** |

### What GLASS Could Replace or Reduce

**Scenario A: GLASS at $199/mo (Cue Starter)**

| Saves | How | Monthly Value |
|-------|-----|---------------|
| Analyst hours: menu checking | Price Wire replaces manual competitor checks. 490+ dispensaries scraped daily vs. my analyst checking 20-30 manually. | $1,000 (cuts analyst from 15 hrs → 5 hrs/wk) |
| My spreadsheet time | Report Card + Morning Brief replaces my Sunday pricing review sessions | $1,000 (saves ~2 hrs/wk of my time) |
| Missed pricing opportunities | The Report Card found I'm 11% above market in Springfield flower. If I adjust and sell even 10 more units/week at $35, that's $350/wk | $1,400 |
| **Total monthly value** | | **$3,400** |
| **GLASS cost** | | **-$199** |
| **Net ROI** | | **$3,201/mo (16:1 return)** |

**Scenario B: GLASS at $999/mo (Enterprise, with multi-store)**

| Saves | How | Monthly Value |
|-------|-----|---------------|
| Everything in Scenario A | | $3,400 |
| Analyst fully replaced | All 4 stores covered by automated alerts. Analyst reassigned to in-store operations. | +$625 (remaining 5 hrs/wk) |
| Cross-location pricing optimization | Consistency checks + market-appropriate pricing per location | +$800 (conservative) |
| Threat intel preventing surprises | Knowing about new competitors 6 months before they open | Hard to quantify — call it peace of mind |
| Brand incentive capture (Cue Enterprise) | If even one brand spiff at $2/unit × 200 units/mo | +$400 |
| **Total monthly value** | | **$5,225** |
| **GLASS cost** | | **-$999** |
| **Net ROI** | | **$4,226/mo (5.2:1 return)** |

### The Honest Assessment

The $199/mo tier is a no-brainer IF the data is accurate and updated daily. Even if GLASS only replaces half my analyst's menu-checking hours, it pays for itself 5x over.

The $999/mo Enterprise tier is worth it IF multi-location is real and the pricing recommendations actually work. At $999/mo across 4 stores, that's $250/store/month. My average store does $80-120K/month in revenue. If GLASS finds me even a 0.5% revenue improvement per store through better pricing, that's $400-600/month per store. Easy math.

**The risk:** The data has been collecting for ONE DAY as of this review. The Price Index on the Market page literally shows "Tracking started February 12, 2026" and every WoW column says "New" with dashes. The Report Card comparison (your avg vs. market avg) is based on a single-day snapshot of 117K price observations. That's a good start — it's a wide snapshot — but it's not a trend. If Cannabis Healing's flower is $31.99 vs. market $35.30 today, is that consistent, or did the market just have an unusual day? I need 30+ days of stable daily scraping before I trust any "your price vs. market" comparison enough to actually change prices.

There's also the Recommendations contradiction I flagged in my walkthrough — the Report Card says "you're underpriced, room to earn more" while the Recommendations page says "lower your price." If I'm paying $999/mo and my GM in Springfield sees conflicting advice, that's a support call I don't want to make.

**My verdict: I'd sign a $999/mo annual contract on day 30 of proven daily data delivery, after the Recommendations framing is fixed to match the Report Card. Not before.**

---

## Question 3: Data Depth — Lab Tests and Facility Sales

### The 147K Lab Tests

This is where GLASS could go from "useful" to "holy shit."

Here's what I know as an operator: **THC percentages on menus are often bullshit.** Brands push cultivators for higher numbers. Cultivators test multiple batches and cherry-pick results. Some brands post the top-end THC% from a range. Customers walk in asking for "the strongest" and we point them to whatever says 30%+ on the label.

GLASS has 147,649 actual CCC lab test results with THC and THCA values, linked by Metrc tags to specific product batches. The total THC formula is `THC + (THCA × 0.877)`.

**What would make me say "holy shit":**

1. **Menu Claim vs. Lab Reality Score.** Match a product's menu-listed THC% against the actual CCC lab test for the same product/batch. Show the delta. "Brand X's Wedding Cake claims 32% THC on the menu. Average CCC lab result for their last 5 batches: 24.8%. Inflation score: +29%." 

   I would use this DAILY. When a customer asks why our Blue Dream says 22% and the competitor says 28%, I want to pull up GLASS and show them: "Their lab tests average 21%. Ours average 22%. They're inflating."

2. **Brand Reliability Index.** Across all lab tests for a brand, how consistent are their THC numbers? A brand that ranges from 18-32% across batches has quality control problems. A brand that consistently hits 22-25% is reliable. I want to stock reliable brands.

3. **Category Potency Benchmarks.** What's the ACTUAL average THC% for flower in Massachusetts based on lab tests? Not menu claims — lab tests. If the real average is 21% and everyone's menus say 25-30%, the entire market is inflated. That's a story I can use in marketing: "We post real numbers."

4. **Lab-to-Shelf Tracking.** Can I see which products in my current inventory have lab tests on file, and whether my listed THC% matches? Quality assurance for my own stores.

### The 67K Facility Sales Records

Seven years of CCC-reported actual revenue by product category, by facility type. 2018-2025. Nobody else has assembled this.

**What would make me say "holy shit":**

1. **Market Trajectory by Location.** Show me the total cannabis revenue trend for each of my 4 cities over 7 years. Is Boston growing, flat, or declining? Is Springfield saturated? Is Pittsfield an underserved market? I make capital allocation decisions based on this.

2. **Category Revenue Shift.** In 2018, flower was 70% of revenue. Now what? Show me the migration toward edibles, vapes, concentrates. If I can see that edibles went from 10% to 25% of revenue over 7 years, that changes my inventory allocation TODAY.

3. **Revenue per License.** Total market revenue ÷ number of active licenses per year. Is the pie growing faster or slower than the number of players? If revenue is flat but licenses doubled, each store's share got cut in half. That's the compression story I tell my investors.

4. **Seasonal Patterns.** 7 years of data should show clear seasonal trends. Does flower sell more in winter? Do edibles spike before holidays? I currently guess at this. Historical data would let me plan.

5. **The 73% Flower Collapse Story.** $14.68/g to $4.01/g over 71 months. Show this as an interactive timeline with annotations: "New licenses granted here," "COVID impact here," "Market saturation inflection point here." Let me scrub through it. This is the kind of chart I'd screenshot and send to my operations team every quarter.

### How to Surface These Insights

**Don't bury them in tables.** My team won't query a database. Surface them as:

- **Morning Brief "Market Context" card:** "MA flower revenue dropped 8% YoY. Your Springfield store's market has 40% more licenses than 2022."
- **Report Card "Market Position" section:** "Based on 7 years of CCC data, your city's cannabis market peaked in 2023. Current trajectory suggests 15% more compression before stabilization."
- **Exportable quarterly market report:** PDF I can hand to my operations team and my accountant that shows market trends, my position in them, and what to expect next.

---

## Question 4: Integration — Does This Connect to My Existing Stack?

### Dutchie Integration

**Current state: No.** GLASS scrapes Dutchie menus externally (235 stores via Dutchie slugs in the database). There's no Dutchie API integration, no POS sync, no two-way data flow. The Product Specs mention a future React component for Dutchie-embedded sites, but that's vapor right now.

**What I need:**
- **Menu price sync.** When GLASS recommends I change a price, I don't want to open Dutchie separately and manually update it. I need a "push to Dutchie" button or at minimum an export format Dutchie can import.
- **Sales velocity data.** GLASS knows my menu prices but not how fast things sell. If I could connect Dutchie sales data to GLASS competitive intelligence, the recommendations would go from "you're priced high" to "you're priced high AND selling slow — here's the optimal price point." That's 10x more valuable.
- **Inventory sync.** GLASS currently assumes everything on my Dutchie menu is "in stock." Real inventory levels would make recommendations much smarter.

**Realistic assessment:** Dutchie doesn't have a public API for this. Integration would require either a Dutchie partnership or operators manually exporting data. This is a Year 2 feature, not a launch feature. I can live without it for now if the scraping data is good enough.

### Excel Export

**Current state: Partial.** The Price Wire has CSV export for the price observation table. That's a start. But I need:
- **Report Card as Excel/PDF.** My ops meetings are every Monday. I want to export each store's Report Card, print it, and discuss with my GMs.
- **Competitor price comparison as Excel.** My analyst currently builds these manually. If GLASS can export "My Store vs. Top 5 Competitors — Product by Product," I can stop building spreadsheets.
- **Bulk data export.** All 4 stores' data in one workbook with separate tabs. I'm an Excel guy. Give me the raw data and I'll build my own models on top.
- **Scheduled email reports.** The Cue product promises weekly PDFs via email. That's exactly right. But it doesn't exist yet.

### Sharing with My Team

**Current state: Not built for teams.** The auth model is one-user-one-operator. I need:
- **Role-based access.** I see everything. My 4 GMs see their store only. My operations director sees all 4 stores read-only.
- **Shareable report links.** Public Report Card pages exist (mentioned in the outreach strategy), but team-specific sharing with different permission levels doesn't.
- **Slack/Teams integration.** When GLASS detects a competitor price drop, ping my #pricing Slack channel. My team lives in Slack, not in dashboards.

### Integration Summary

| Integration | Status | Priority for Me |
|-------------|--------|-----------------|
| Dutchie menu sync | Not built, unlikely near-term | High (Year 2) |
| Dutchie sales data | Not built | Very high (would 3x the product value) |
| Excel/CSV export | Partial (Price Wire only) | High |
| PDF Report Card export | Not built | High |
| Weekly email reports | Planned (Cue), not built | Critical |
| Team roles/sharing | Not built | Critical for Enterprise |
| Slack alerts | Not built | Nice-to-have |
| API access for custom tools | Planned for Enterprise tier | Medium |

**The integration story is weak right now.** GLASS is a standalone dashboard. For a single-location owner who checks it each morning, that might be fine. For a multi-location operator with a team, it needs to plug into how we already work. Email reports and Excel exports are table stakes. Without them, I'm adding GLASS as the 7th tab I need to check instead of the 1 tool that consolidates everything.

---

## Question 5: THC Accuracy Score — Would I Pay Extra?

### Absolutely Yes. This Is GLASS's Killer Feature They Don't Realize They Have.

Here's why: every operator in Massachusetts is dealing with THC inflation. Consumers have been trained to buy by the number. Brands compete by posting the highest possible THC percentages. Many operators know the numbers are inflated but feel trapped — if you post honest numbers, you look weaker than competitors who inflate.

GLASS has 147,649 actual lab results from the CCC. They can build a **THC Accuracy Score** by matching menu-listed percentages against real lab data:

**THC Accuracy Score = (Menu-Listed THC% − Lab-Tested THC%) / Lab-Tested THC% × 100**

- **Score of 0%:** Perfect accuracy. Menu matches lab.
- **Score of +15%:** Menu claims are 15% higher than lab tests. Moderate inflation.
- **Score of +30%+:** Significant inflation. Potentially misleading customers.

### What I'd Use This For

1. **Vendor selection.** I want to stock brands with Accuracy Scores under 10%. That's a quality signal. "We only carry brands that post honest numbers" is a marketing differentiator.

2. **Competitive intelligence.** If I can show that Competitor X's top-selling flower has a +28% inflation score, that's powerful information. Not for public slander — but for internal strategy. Their "30% THC" product tests at 23%. My 24% product is actually stronger.

3. **Consumer education.** If GLASS can give me a printable "Lab Verified" badge for products where my menu THC% matches the lab within 5%, I'd put that on my shelf cards. "Lab Verified Accuracy" is a trust signal that no other dispensary in the state is offering.

4. **Regulatory compliance preparation.** The CCC has been making noise about THC testing standards. If/when they crack down on inflated claims, operators using GLASS's accuracy scores will already be compliant. First-mover advantage.

### What I'd Pay

- **Included in the $199/mo tier for my own products.** I need to know if MY listed percentages match lab tests.
- **$99/mo add-on for competitor accuracy scores.** Seeing competitors' inflation is competitive intel worth paying for.
- **Premium version at $299/mo** that includes brand-level accuracy rankings, trending over time, and alerts when a brand I carry has a batch that tested significantly different from their posted number.

### Implementation Complexity

Low to medium. The lab test data is already in the database (147K rows with THC, THCA, product category, strain, Metrc tag). The menu data has THC percentages for many products. The matching algorithm is the challenge — connecting a "Blue Dream 3.5g" on a Dutchie menu to the correct Metrc-tagged lab test requires fuzzy matching on brand + strain + date proximity. But even an imperfect match (say, matching 60% of products with reasonable confidence) would be valuable.

**This feature alone could be GLASS's differentiator.** In a market where every dashboard shows prices and competitors, NOBODY is showing "who's lying about their THC." That's a headline. That's PR. That's the feature that makes operators say "I NEED this."

---

## Question 6: Pricing Intelligence That Replaces My Analyst

### What My Analyst Currently Does (15 hrs/week)

1. **Monday (3 hrs):** Opens Dutchie/Leafly/Weedmaps for 15-20 competitors near each of my 4 stores. Screenshots current menus. Copies flower, vape, and edible prices into our master Excel sheet.

2. **Tuesday-Wednesday (4 hrs):** Compares competitor prices against our prices. Flags where we're >10% above or below market for the same product. Builds a "price action" list for each store.

3. **Thursday (3 hrs):** Researches new product launches from brands we carry. Checks if competitors are running deals or promotions we should match. Looks at Leafly/Weedmaps reviews for signals.

4. **Friday (3 hrs):** Updates the master pricing sheet. Sends each GM a "Weekly Pricing Brief" email with recommended changes. Follows up on last week's changes.

5. **Ongoing (2 hrs):** Ad hoc requests. "What's the cheapest ounce in Worcester right now?" "Who else carries Fernway in Springfield?" "What's the average preroll price within 5 miles of Pittsfield?"

### What GLASS Needs to Replace This

For me to fire my analyst (or more accurately, reassign them to higher-value work), GLASS needs to deliver:

1. **Automated competitor monitoring for ALL my locations.** Not just "market average" — specific competitor-by-competitor pricing for the 15-20 dispensaries near each of my 4 stores. The Price Wire covers 490+ dispensaries, which is great, but I need it filtered and organized per-store. "Here are your 8 closest Worcester competitors and what they're charging for flower today, sorted by product."

2. **Product-to-product matching, not just category averages.** I don't care that "average flower in Worcester is $38." I care that MY Blue Dream 3.5g is $45 and THREE competitors within 5 miles sell Blue Dream 3.5g for $38-40. That's the level of specificity that drives a pricing decision.

3. **Automatic "Price Action" recommendations.** GLASS's Cue product describes this exactly: "Your Blue Dream is at $46. Median in 5-mile radius: $41.50. Recommended: $42." If that recommendation arrives in my inbox every morning with a list of 3-5 SKUs per store that need attention, my analyst's Monday-Wednesday workflow is automated.

4. **Weekly PDF report per store.** "Here's your store's pricing position this week. Here's what changed. Here's what we recommend." My analyst currently builds this manually. GLASS should generate it automatically and email it to each GM.

5. **Promotion/deal tracking.** When a competitor runs a "20% off all vapes" promo, I need to know about it. Scraping should detect price drops that look like promotions vs. permanent price changes. This is hard to automate but critical.

6. **"Who carries X?" instant lookup.** My analyst gets asked this weekly. "Who carries Fernway in Springfield?" GLASS already has this data — 100K products with brand attribution across 490+ stores. Build a search: `brand: Fernway, city: Springfield` → instant results with prices.

### The Gap

Right now, GLASS can replace maybe 40% of my analyst's work — the bulk data collection (Price Wire) and the market positioning (Report Card). The remaining 60% — product-level matching, per-store filtering, weekly reports, promotion detection — either doesn't exist yet or isn't exposed in a way that matches my workflow.

**GLASS doesn't need to be perfect to replace my analyst. It needs to be good enough that my analyst spends 3 hours/week on GLASS-powered work instead of 15 hours on manual work.** That's a realistic near-term goal.

### Specific Feature Requests

1. **"My Competitors" saved list per store.** Let me tag 8-10 dispensaries near each of my locations as "watched competitors." Then surface only those in my daily brief.
2. **Product matching engine.** When I carry Blue Dream 3.5g and three competitors do too, show me the exact comparison. Name-to-name, gram-to-gram.
3. **Price change alerts by store.** "2 competitors near your Worcester store dropped vape prices today." Push to email/SMS.
4. **Weekly PDF export.** Per-store or portfolio-wide. Auto-generated, auto-delivered.
5. **Brand search.** "Show me everywhere Fernway is sold and at what price." Instant.

---

## Question 7: Missing Features — Must-Have vs. Nice-to-Have

### Must-Haves to Reach "Shut Up and Take My Money" Status

| Feature | Why | Impact |
|---------|-----|--------|
| **Multi-location portfolio view** | I run 4 stores. Without this I'm a tourist, not a customer. | Dealbreaker |
| **30+ days of daily scraping data** | One day of data is a snapshot, not intelligence. I need trends. | Foundation |
| **Weekly email reports (PDF)** | I don't log into dashboards. Bring the insight to me. | Retention |
| **Team roles & sharing** | My GMs need access to their store's data. My ops director needs all 4. | Enterprise requirement |
| **Excel/CSV bulk export** | I build my own models. Give me the raw data. | Power user requirement |
| **"My Competitors" watchlist** | 490 dispensaries is noise. The 30-40 near my 4 stores is signal. | Usability |
| **Product-level price comparison** | Category averages aren't actionable. Product-to-product matching is. | Value driver |

### Nice-to-Haves That Would Make Me an Evangelist

| Feature | Why | Impact |
|---------|-----|--------|
| **THC Accuracy Score** | Nobody else has this. It's a differentiator and a marketing tool. | Brand value |
| **Dutchie sales data integration** | Combining menu intel with sell-through = pricing optimizer | 3x product value |
| **Historical seasonal patterns** | 7 years of data should reveal seasonal trends for planning | Strategic |
| **Slack/webhook alerts** | Real-time competitive intel in the channel my team already uses | Workflow integration |
| **Mobile app** | Check portfolio status from my phone between store visits | Convenience |
| **Custom alerting rules** | "Alert me when any competitor within 5mi of Worcester drops flower below $30" | Proactive |
| **Brand velocity tracking** | Which brands are gaining or losing shelf space across the market? | Vendor negotiations |

### Features I Don't Need (Kill These or Deprioritize)

| Feature | Why I Don't Care |
|---------|-----------------|
| **Virtual Budtender** | I have budtenders. 45 of them. I need market intel, not a chatbot. Maybe later for my website. |
| **Brand Marketplace / Cue Enterprise incentives** | Two-sided marketplace with zero liquidity. Don't waste engineering time. |
| **Delivery intelligence** | The delivery license expires March 2026. No partnership exists. Don't build on a foundation that doesn't exist. |
| **19 D3/Three.js visualizations** | Pretty, but most need 30+ days of data to have any meaning. Ship 3 great ones, not 19 half-baked ones. |
| **Complex geographic maps** | The Market Terrain Map and Delivery Voronoi sound cool. Give me a simple distance-to-competitor table instead. |

---

## Question 8: The 7-Year Facility Sales Data

### This Is GLASS's Secret Weapon. Here's How to Weaponize It.

67,333 facility sales records spanning 2018-2025. Revenue by product category, by facility type. 71 months of price trend data showing flower collapsed 73%. Nobody else has assembled this into a single queryable dataset.

### How to Present It for Each of My Locations

**I need city-level or county-level market trajectory, not just statewide.**

**View 1: My Markets Over Time (the "investor deck" view)**

For each of my 4 cities, show:
- **Total cannabis revenue** by year (bar chart, 2018-2025)
- **Number of active licenses** by year (line overlay)
- **Revenue per license** by year (derived — this is the "is the market getting better or worse per operator" metric)
- **Category mix shift** (stacked area: flower → edibles → vapes → concentrates → pre-rolls as % of total)

I want to see at a glance: "Boston's market grew 40% but licenses tripled, so revenue per store dropped 50%." That tells me Boston is saturated and my investment should go to Pittsfield, where the market grew 30% but only added 2 new licenses.

**View 2: The Compression Timeline (the "how bad is it, really" view)**

An interactive timeline from 2018 to present:
- **Y-axis:** Average price per gram (flower)
- **X-axis:** Time
- **Annotations on the chart:**
  - "Jan 2020: 150 active licenses"
  - "Mar 2020: COVID lockdowns"
  - "Jul 2021: Delivery licenses approved"
  - "Dec 2022: Market saturation inflection point"
  - "Jun 2024: Price floor discussions at CCC"
  - "Dec 2025: Current state — $4.01/g"

Let me scrub through this. Let me zoom into specific periods. Let me overlay the number of licenses on the same chart. The story this tells is: "Every time the CCC granted more licenses, prices dropped. Here's the correlation coefficient. Here's where it stabilizes."

I would literally print this chart and hang it in my office.

**View 3: Category Opportunity Map (the "where should I invest" view)**

For each product category across 7 years:
- **Total revenue** (is this category growing or dying?)
- **Number of competitors** (is it getting crowded?)
- **Average price** (is pricing holding or collapsing?)
- **Revenue per SKU** (are stores over-assorted?)

The insight I'm looking for: "Edibles grew 300% in revenue over 7 years while flower grew 20%. But edible pricing held at $25/unit while flower collapsed. Edibles have better revenue per SKU. Shift inventory from flower to edibles."

I already *believe* this is true from running my stores. But I don't have the data to prove it to my team or make a confident capital decision. GLASS's 7-year dataset would give me proof.

**View 4: Delivery vs. Storefront Trajectory (the "should I go delivery" view)**

The plant activity data (46,863 records) tracks delivery vs. storefront sales:
- What % of revenue is delivery today?
- Is that percentage growing?
- Which product categories are moving to delivery fastest?
- What's the revenue per delivery operator vs. per storefront operator?

If delivery is capturing 8% of vape sales and growing 2% per quarter, I need to know that NOW. It changes whether I pursue delivery licenses for my locations.

### The Presentation Format

**Don't build a complex interactive dashboard for this data.** That's overkill and I won't use it.

Build instead:
1. **Quarterly Market Report** — automated PDF, 4-6 pages, with the 4 views above tailored to my 4 cities. Email it to me on the 1st of every quarter. I'd pay $99/quarter for this alone.
2. **Morning Brief "Market Context" widget** — one sentence: "MA flower revenue is down 8% YoY. Your Springfield market has 3 more licenses than last year."
3. **Export the raw data as Excel.** Let me build my own models. Give me the data in a clean workbook and I'll handle the analysis.

The 7-year data is the reason I'd sign an annual contract. It's irreplaceable. But only if it's accessible and relevant to MY markets, not just statewide averages.

---

## What Makes GLASS Different From Everything Else I've Seen

### The Honest Answer

I've evaluated Headset (POS analytics), BDSA (market reports), LeafLink (wholesale), and a dozen cannabis CRMs. Here's where GLASS is genuinely different:

1. **It has retail shelf prices for the entire state.** Nobody else is scraping 490+ dispensary menus and building a competitive pricing database. Headset sees what's sold (from POS data), but doesn't see what competitors are charging. GLASS sees what everyone charges but not what sells. GLASS is more useful for pricing decisions; Headset is more useful for inventory planning. Ideally, I'd have both.

2. **The CCC data integration is unique.** 7 years of facility sales, 147K lab tests, pending license applications, plant activity — all cross-referenced against real-time shelf prices. Nobody else has built this bridge. The strategic value of correlating "CCC says average flower was $4.01/g last month" with "GLASS sees retail shelves at $8-12/eighth" is enormous.

3. **The Store Report Card is the right product.** Green/yellow/red, plain English, 3 actions to take. That's what an operator wants at 6 AM. Not a 19-visualization dashboard. Not a data warehouse. A traffic light and a to-do list.

4. **The price trend is the compound moat.** Every day the scraper runs, the historical dataset gets more valuable. In 90 days, GLASS will have 90 days of daily pricing data that a new competitor would need 90 days to replicate. In a year, it'll have seasonal patterns nobody can copy without waiting a year. Time is the moat.

5. **It's Massachusetts-focused.** National tools treat MA as a footnote. GLASS treats it as the entire universe. For someone operating only in Massachusetts, depth beats breadth every time.

### What's Overpromised

1. **The landing page promises four features; one is live.** Price Wire is real. Threat Radar, Morning Brief, and Cue all say "COMING SOON." That's a 25% delivery rate on your own homepage. For me, it signals "beta product." For a less technical operator? It signals "vaporware." The fix is simple: lead with what's live, tease what's coming without making it a headline feature.

2. **The Recommendations page contradicts the Report Card.** The Report Card smartly tells operators they're "leaving money on the table" and frames everything as opportunity. The Recommendations page tells them to lower every price. These cannot coexist. A Cannabis Healing operator who sees "your prerolls are 16.3% below market — room to earn more" and then clicks Recommendations and sees "2-pack preroll: $19 → $17" would think the product is broken. It IS broken on that page.

3. **"AI-powered pricing."** The Margin Engine is described as XGBoost. But with one day of pricing data, there's no model to train. Call it "data-driven pricing recommendations" and earn the "AI" label after 90 days of training data.

4. **The flywheel.** "More operators → better data → better recommendations → more operators." This is true in theory, but GLASS has zero paying operators right now. The flywheel hasn't even started spinning. Don't sell the flywheel — sell the Report Card. It's the one thing that works today and delivers immediate value.

5. **The premium data teasers on the Market page show empty boxes.** Three blurred cards — "Price Positioning Matrix," "Brand Treemap," "Market Terrain Map" — all say "No data available for this view." You're teasing premium features that have no data behind them. That's worse than not showing them. It makes the paid product look empty before I've even signed up.

6. **Real-time everything.** The scraper runs daily, not in real-time. The landing page says "Updated daily" which is honest. But the product positioning keeps implying real-time alerting. Daily is fine. Own it.

---

## Final Recommendations for the GLASS Team

I'm writing this as an operator who WANTS this product to succeed. Here's my blunt advice:

### Do This Week (Seriously, This Week)
1. **Fix the Recommendations page to match Report Card framing.** This is not optional. The Report Card says "room to earn more" while the Recommendations page says "reduce price from $19 to $17." An operator seeing both will think the product is broken. Every recommendation should use the opportunity frame: "Your prerolls at $15.55 are below the $18.57 market — adjusting up could add $X/week."
2. **Remove or hide the premium data teasers that show "No data available."** Three blurred cards with empty states look like the paid product has no data. Better to not show them at all than to show empty boxes behind a paywall tease.

### Do This Month
1. **Get 30 days of stable daily scraping.** Nothing else matters until the data is reliable. Every WoW column currently says "New" — that needs to show real deltas.
2. **Ship weekly email reports.** PDF, per-store, automated. This is your retention mechanism. Operators don't log into dashboards — bring the Report Card to their inbox.
3. **Add CSV export for everything.** Report Card, competitor comparison, price history. Power users need raw data.
4. **Fix remaining data quality issues.** "stock. Order soon." as a brand name? Any remaining fake sparklines? These destroy credibility with operators who will verify your data against their own Dutchie menus.
5. **Rethink the landing page feature hierarchy.** Lead with Price Wire (LIVE) and Report Card (LIVE). Move COMING SOON features below the fold or into a "roadmap" section. Three out of four headline features being unavailable is a trust problem.

### Do Next Quarter
1. **Build multi-location support.** One login, portfolio view, per-store drill-down. This unlocks your Enterprise tier.
2. **Build THC Accuracy Scoring.** Match menu claims to lab tests. This is your PR story and your differentiation.
3. **Build the quarterly Market Report.** 7-year CCC data + daily scraping data = the definitive Massachusetts cannabis market report. Sell it for $99/quarter standalone.
4. **Ship product-level price matching.** Not just category averages — "Your Blue Dream vs. their Blue Dream."

### Do This Year
1. **Dutchie integration.** Even if it's just export-to-import, not a live sync.
2. **Team roles and permissions.** Owner/admin/viewer with store-level scoping.
3. **API access.** Let power users like me build on top of your data.
4. **Slack/webhook alerts.** Meet operators where they work.

### Never Do
1. **Don't build brand marketplace before you have 100+ paying operators.** Zero liquidity.
2. **Don't build delivery intelligence without a delivery partnership.** Vapor.
3. **Don't add more visualizations before the data behind them is solid.** 3 great charts > 19 fake ones.

---

## Summary Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Data breadth** | 9/10 | 511K+ rows, 490+ dispensaries, 7 years of CCC data. The CCC × GLASS cross-reference on the Market page is something nobody else has. 147K lab tests + 67K facility sales = irreplaceable. |
| **Data depth** | 7/10 | Lab tests + facility sales are gold. But daily scraping started Feb 12, 2026 — literally today. Every WoW column says "New." No trend data exists yet. |
| **Data quality** | 5/10 | Known issues: brand parsing garbage, fake sparklines replaced but underlying data is 1 day old, Recommendations page contradicts Report Card framing. The 117K price observations from today are solid; it's the time-series that doesn't exist yet. |
| **Report Card** | 8.5/10 | The best feature. Green/yellow/red by category with dollar-denominated opportunity. "Leaving money on the table" framing is exactly right. Cannabis Healing example shows $31.99 flower vs $35.30 market = 🟡 "room to earn more." This is how you talk to operators. |
| **Multi-location support** | 2/10 | Not built. One user → one operator model. My biggest need and their biggest gap. The Enterprise tier literally depends on this. |
| **Actionability** | 5.5/10 | Report Card is excellent. Threat Radar categories are well-designed. But: no push alerts, no weekly reports, recommendations still use "lower your price" framing, no per-product matching. The gap between "good data" and "data I act on" is still wide. |
| **Landing page / trust** | 5/10 | Headline is perfect. Design is premium. But 3/4 features say COMING SOON, premium teasers show empty boxes, zero social proof from real operators. "Who is Roviq?" would be my team's first question. |
| **Integration** | 3/10 | No Dutchie sync, limited export (Price Wire CSV only), no team sharing, no Slack, no PDF reports. Standalone dashboard. |
| **UX/Design** | 8/10 | Bloomberg-meets-Apple dark aesthetic. Copper accent is distinctive. Onboarding is smooth. Report Card UI with animated number counters and expandable sections is genuinely impressive. |
| **Pricing/Value** | 8/10 | $199/mo is a steal IF it works and scraping is reliable. $999/mo Enterprise would be fair with multi-store + reports + THC accuracy. |
| **Competitive moat** | 9/10 | Nobody else has this dataset assembled. The CCC × shelf price cross-reference is unique. Time-series depth compounds daily — but the clock started today. |
| **Readiness** | 4.5/10 | Impressive prototype with one genuinely great feature (Report Card). Not yet a production tool I'd bet my morning routine on. The contradiction between Report Card and Recommendations is a credibility risk if an operator sees both. |

**Overall: 6.3/10 today. 9/10 in 90 days if they execute.**

### What Gets This to a 9

In priority order:
1. **30 days of stable daily scraping** → unlocks real trends, makes all "vs. market" comparisons trustworthy
2. **Fix Recommendations to match Report Card framing** → no operator should see "lower your price" when the Report Card says "room to earn more"
3. **Multi-location portfolio view** → unlocks Enterprise tier and operators like me
4. **Weekly email reports (PDF)** → the feature that drives daily engagement without requiring login
5. **THC Accuracy Score** → the feature nobody else can build, using 147K lab tests
6. **Kill the "COMING SOON" from the landing page** → lead with what works (Price Wire, Report Card), tease the rest subtly

---

## My Offer to the GLASS Team

I'll be your multi-location design partner. I've been through the full experience — landing page, market page, onboarding, Report Card, Price Wire, Threat Radar, Recommendations. I've seen what works (Report Card framing, CCC × shelf cross-reference, competitor proximity data) and what doesn't (Recommendations contradicting Report Card, COMING SOON everywhere, no multi-store).

Give me early access to new features. Let me beta test multi-store with my 4 locations as the proving ground. Let me break things and tell you what's wrong. In return, I expect:

1. **Recommendations framing fixed to match Report Card** — by end of February. This is a P0, not a P1. No operator should see conflicting advice.
2. **Weekly email reports by March 2026** — PDF, per-store, with the Report Card data + competitor highlights. This is the retention mechanism.
3. **Multi-location portfolio view by Q2 2026** — One login, 4 stores, portfolio dashboard with per-store drill-down.
4. **Excel export for everything by March 2026** — Report Card, competitor comparison, price history, raw data.
5. **Stable daily scraping for 30 consecutive days** — before I sign a paid contract. I need to see WoW trends that are real, not columns that say "New."
6. **THC Accuracy Score by Q2 2026** — Match the 147K lab tests against menu claims. This is the PR story and the differentiation.

If you deliver those 6 things, I'll sign a $999/mo annual Enterprise contract for all 4 locations and bring 3 other multi-location operators I know with me. That's $48K ARR from my stores plus potentially $100K+ from referrals.

**The Cannabis Healing Report Card demo convinced me the product thinking is right. The CCC × shelf data on the Market page convinced me nobody else has this dataset. Now execute on the 6 things above and you have a customer.**

One more thing: whoever wrote "Leaving money on the table" instead of "Lower your price" — give them a raise. That single framing decision is the difference between a product operators love and a product operators resent. Now make sure the *entire* product speaks that language, not just the Report Card.

— Derek  
*February 12, 2026*  
*4 stores, 45 employees, $18K/mo in tech, looking for the one tool that actually helps me make money instead of just organizing data I already had*
