# GLASS Strategic Review — February 12, 2026

**To:** Randy Torres, Founder  
**From:** Chief Strategy Officer  
**Classification:** Internal — Brutally Honest  
**Written after reading:** 3 independent platform reviews, QA pass, tech fix plan, product specs, memory log, and every plan doc in the repo.

---

## PART 1: HONEST ASSESSMENT

### What We ACTUALLY Have That's Ready to Show a Paying Customer

**Ready today:**
1. **The Store Report Card** — Green/yellow/red scoring by category with plain-English actions. This is the single best thing we built today. It's specific, personal, and immediately understandable. An operator sees "🔴 Your flower is $4 above market" and knows what to do.

2. **The raw price intelligence** — 100,849 products from 517 dispensaries. This is genuinely hard to assemble. No one else has a same-day snapshot of every Dutchie and Weedmaps menu in Massachusetts cross-referenced against CCC official prices. The data table on Price Wire with CSV export — that's real, usable, and unique.

3. **The CCC regulatory data** — 234 pending license applications, 31,038 historical price records spanning 7 years, 46,863 plant activity records. This is gold that nobody else is surfacing.

4. **The onboarding flow** — Clean 4-step claim-your-store experience. Operator types their name, sees "we already track 238 products on your menu," and gets a market snapshot. When it works, the dopamine hit is real.

5. **The public Market page** — SEO-friendly, free value, credible (after fixes). This is the right funnel: free intelligence → signup → paid tools.

**That's it.** Five things. Not nineteen visualizations. Not four product ecosystem pages. Five things that a real operator would look at and say "this is useful."

### What's Still Broken or Would Embarrass Us

I'm going to be direct. Three independent reviews converged on the same findings:

1. **The cross-reference "killer feature" showed a 509% flower markup.** It was a unit mismatch (per-gram vs per-unit). The QA pass says it's now ~354%, which is still probably wrong because it's comparing CCC wholesale transfer prices to retail shelf prices without explaining the difference. Fixed but needs contextual labeling.

2. **Sparklines are fake.** `generateSparklineData()` creates deterministic pseudo-random data from a hash of the product name. Every "price trend" line on the platform is a lie. The QA pass notes these were partially addressed but any remaining fake visualizations are credibility poison.

3. **"stock. Order soon." was the #1 brand.** 4,149 products had parsing garbage as their brand. Brand cleanup SQL was written but the underlying parser still leaks UI text into brand fields.

4. **99.9% of price data is from one day.** All "24h change," "WoW trend," and "price mover" features are meaningless with one day of data. The scraper completed its first bulk run today. We need 7+ days before any time-series visualization has integrity.

5. **Weekly sales chart showed fabricated numbers.** All 71 rows in `ccc_weekly_sales` have NULL values. The frontend fell back to hardcoded fake data showing $28-34M weekly sales. Fixed with "Data Import In Progress" state.

6. **490 of 492 operators now geocoded** (up from 10). This was critical — Geography, Proximity Radar, and competitor distance calculations were all broken.

7. **The Morning Brief hero stats were fabricated.** `totalProducts = movers.length * 150`. That's literally making up a number. Multiple mock/fallback objects existed across every page.

8. **Three of four ecosystem products don't exist yet.** Budtender, Cue, and Delivery are landing pages. The platform shows "GLASS → Budtender → Cue → Delivery" as if they're products. They're concepts.

### The Gap Between "Impressive Demo" and "Product Someone Pays For"

The gap is **trust and specificity**.

The demo is impressive. The design language is genuinely premium — copper accent, Geist Mono, black luxury palette. 19 D3/Three.js visualizations. The Store Report Card is beautiful. The onboarding flow is smooth.

But when a Worcester dispensary owner opens this and sees that her Blue Dream is priced $7 above the competitor across the street — and then checks and finds the data is from 6 hours ago and she can verify it on the competitor's Dutchie menu — THAT is when she becomes a customer.

The gap:
- **From "market averages" → specific product-to-product comparison.** Maria doesn't care that "flower averages $35.44." She cares that *her* Blue Dream 3.5g at $45 is higher than 3 competitors within 5 miles selling it between $35-40.
- **From "pretty dashboard" → push alerts.** Maria doesn't log into dashboards every morning. She needs a text: "Happy Valley just dropped flower 15%. 3 stores near you already matched."
- **From "fake trends" → honest states.** Better to show "Collecting data — trends available in 7 days" than fake sparklines that destroy trust the moment anyone digs in.
- **From "19 visualizations" → 3 answers.** Am I priced right? What should I worry about? What should I do? Everything else is noise.

### Are We Spread Too Thin? What Should We KILL?

**Yes, we are dangerously spread thin.** Here's what to kill or pause:

| Kill/Pause | Why |
|---|---|
| **Virtual Budtender development** | Don't build until GLASS core is trusted and has 50+ active operators. It's a demand-signal product that needs operator density to work. The landing page is fine — leave it as a future teaser. |
| **Delivery intelligence** | No deal closed with Delivered Inc. License expires 3/5/2026. Don't build a product around a partnership that doesn't exist. |
| **SIGNAL as a standalone product** | Keep as internal capability for client work. Don't try to sell it as SaaS while GLASS needs all focus. |
| **Brand Marketplace (Sprint 6)** | Two-sided marketplace with zero liquidity on either side. Year 2+ play. |
| **Complex D3 visualizations that need time-series data** | Volatility Ribbon, Price War Heatmap, Price Cascade, Price Ticker, Market Terrain Map, Delivery Voronoi, Threat Network. These are beautiful and useless until we have 30+ days of data. Hide them or show "Coming soon — collecting data." |
| **AC toll processing blast** | Randy hasn't approved it. It's a different business. Focus on GLASS revenue. |

**What to KEEP and double down on:**
1. GLASS Store Report Card (done — refine and polish)
2. Weekly newsletter ("The Operator's Margin Report") — this is the distribution channel
3. Email outreach pipeline — this is how operators find GLASS
4. Daily scraping — this is the foundation of everything
5. Cue Dynamic Pricing alerts (Sprint 5, but move it up) — this is the $199/mo product

---

## PART 2: THE 30-DAY REVENUE PATH

### Fastest Path to First Paying Customer

**The first paying customer will NOT come from a self-serve signup.** It will come from Randy personally onboarding someone he knows or meets at a CCC networking event, showing them their Store Report Card, and saying "we found $400/month in pricing opportunities for your store."

Specific sequence:
1. Fix remaining data quality issues (this week)
2. Get daily scraping running reliably (this week)
3. Send the first 100 outreach emails (next week)
4. 10-15 operators sign up for free GLASS
5. Randy personally demos Store Report Card to 3-5 of them
6. 1-2 say "what else can you do?"
7. Offer Cue Dynamic Pricing at $199/mo — 14-day free trial
8. First paying customer by day 21-25

**The path is: free value → trust → personal relationship → paid upgrade.**

### What Gets Us to $10K MRR

$10K MRR = 50 operators at $199/mo. That's the math.

But we won't get 50 paid operators in 30 days. Here's the realistic 90-day path:

| Month | Free Operators | Paid (Cue) | MRR | Notes |
|-------|---------------|------------|-----|-------|
| 1 (Mar) | 30-50 | 3-5 | $600-$1,000 | First emails + Randy's network |
| 2 (Apr) | 80-120 | 10-15 | $2,000-$3,000 | Newsletter driving signups, word of mouth |
| 3 (May) | 150-200 | 25-35 | $5,000-$7,000 | Product-market fit confirmed, referrals |
| 4 (Jun) | 200+ | 50+ | $10,000+ | Network effects kicking in |

**Parallel revenue streams to accelerate:**
- Newsletter sponsorships: $500-1,500/mo from brands wanting operator eyeballs (Month 2+)
- Agency sprints: $3K per operator who wants deeper help (1-2/month = $3-6K)
- SIGNAL SEO pilot: $1,500-2K/mo if Randy has bandwidth for 1 client (Month 2)

**Realistic 30-day target: $1,500-3,000 MRR** (5-15 paid Cue subs + 1 agency sprint)

### THIS WEEK (Feb 12-18)

| Day | Action | Owner |
|---|---|---|
| Wed-Thu | Get daily scraping running and stable. One successful run = foundation. | Dev agent |
| Wed-Thu | Deploy all QA fixes (brand cleanup, cross-ref labels, honest empty states) | Dev agent |
| Thu-Fri | Set up GA4 on GLASS web (before sending any emails) | Dev agent |
| Thu-Fri | Configure Resend domain (`glass@mail.roviqai.xyz`) and test email delivery | Randy (DNS) + Dev |
| Fri | Write outreach email v1 (see Part 3) | Randy + COO |
| Fri | Build email tracking (UTM params, custom landing for email recipients) | Dev agent |
| Sat-Sun | Test outreach email on 5 friendly operators (Randy's network) | Randy |

### NEXT WEEK (Feb 19-25)

| Action | Owner |
|---|---|
| Send first batch of 25 emails (not 100 — test first) | System (Randy approves) |
| Monitor: opens, clicks, signups | COO |
| Randy demos Store Report Card to any operator who signs up | Randy |
| Build Cue Dynamic Pricing MVP (alert layer on existing data) | Dev agent |
| Launch newsletter Issue #1 to Beehiiv list | Content agent |

### WEEK 3-4 (Feb 26 - Mar 11)

| Action | Owner |
|---|---|
| Send remaining 75 emails (if first batch metrics are good) | System |
| Activate Cue free trial for engaged operators | Randy |
| First LinkedIn post showing GLASS market insight (not product pitch) | Randy |
| Set up Stripe for Cue billing | Randy |
| Publish CCC 7-year price trend page (SEO play) | Dev agent |
| First paying customer target | Randy |

### Minimum Viable Product Worth $199/mo

An operator pays $199/mo for **Cue Starter** when it delivers:

1. **Daily competitor price alerts via SMS/email** — "Happy Valley dropped flower 15%. Your Blue Dream is now $7 more than theirs."
2. **Weekly pricing report** — PDF/email showing their price position vs market by category, with specific product comparisons
3. **Monthly opportunity summary** — "You left an estimated $800 on the table this month in pre-roll pricing"
4. **Store Report Card updated daily** — their green/yellow/red status always current

That's it. No dashboards required. No visualizations. Just alerts + reports + a dollar amount at risk. The operator gets a text, opens a link, sees the recommendation, and either adjusts their price or doesn't. One-tap value.

**Cost to deliver:** ~$0.50/mo in compute + ~$0.05/SMS. 99.7% margin.

---

## PART 3: OUTREACH STRATEGY

### The First 100 Emails

**Who to target (in order of priority):**
1. **Independent operators in high-competition cities** (Worcester, Springfield, Boston, Lowell) — they feel the pain most
2. **Operators with 100+ products on their Dutchie menu** — they're serious businesses with complex pricing decisions
3. **Operators we can identify a named contact for** — 52 of our 180+ leads have names
4. **NOT multi-state chains** (Curaleaf, Columbia Care) — they have internal analytics teams

### What the Email Should Say

Randy hates salesy. The email should feel like a friend forwarding useful data. Here's the template:

---

**Subject:** Your flower is priced 8% above Worcester average

**Body:**

Hey [First Name],

I'm building a market intelligence tool for MA dispensary operators and your store caught my eye.

We track every dispensary menu in Massachusetts — all 517 of them — and cross-reference with CCC data going back 7 years.

Here's what we found for [Store Name]:

- Your avg flower price: $[X] (market avg in [City]: $[Y])
- [City] has [N] active dispensaries and [M] pending license applications
- Your top category by SKU count: [Category] ([N] products)

I'm not selling anything. GLASS is free for operators. We built it because we think dispensary owners deserve the same market intelligence that every other industry gets.

If you want to see your full store report card — pricing position, competitor comparison, and what's coming in your market — it takes 10 seconds to set up: [link]

— Randy Torres
Roviq | glass.roviq.com

P.S. — [One personalized detail: "I noticed you carry Bountiful Farms — they're in 23% of Worcester stores now" or "You're one of 3 stores in your zip code without vape inventory — that's either strategic or an opportunity"]

---

**Key principles:**
- Lead with THEIR data, not our product
- The P.S. is the hook — it proves we actually know their business
- "I'm not selling anything" must be TRUE — GLASS core is free
- The link goes to their personalized Store Report Card (auto-generated from their operator ID)

### Landing Experience When They Click

**DO NOT send them to the generic landing page.** Send them to a personalized URL:

`glass.roviq.com/report/[operator-slug]`

This page shows:
1. Their Store Report Card (green/yellow/red by category)
2. Competitor count within 5 miles
3. Pending license applications in their city
4. One specific pricing opportunity with a dollar amount
5. "Want daily alerts like this? Sign up free." → Clerk auth

**Critical:** This page must work WITHOUT signing in. The Report Card API already supports public access by operator ID. Build a thin wrapper page that renders it beautifully.

### Analytics/Tracking Before Sending

**Must have before any email goes out:**

| Tracking | How |
|---|---|
| GA4 on GLASS web | Google tag in `<head>` — track page views, sign-ups, feature usage |
| UTM parameters on all email links | `?utm_source=email&utm_medium=outreach&utm_campaign=batch1&utm_content=[operator-slug]` |
| Email open tracking | Resend provides this natively |
| Click tracking | Resend + UTM params |
| Signup attribution | Store UTM params in Clerk user metadata on signup |
| Report Card view tracking | Log `operator_id` + `timestamp` on every public report card view |

**Nice to have:**
- Heatmap on landing page (PostHog free tier)
- Session recording for first 50 visitors (PostHog)

### Success Metrics

| Metric | Target | "Great" |
|---|---|---|
| Email open rate | 35% | 50%+ |
| Click-through rate | 8% | 15%+ |
| Report card views | 20% of opens | 30%+ |
| Free signup rate | 5% of clicks | 10%+ |
| Day-7 return rate | 20% of signups | 40%+ |

For the first batch of 25: we need **at least 2 signups** to validate the approach. If we get 0, the email or the landing experience is wrong.

### LinkedIn Strategy

**What to post (1-2x/week):**
- Real market data, not product announcements
- "Massachusetts dispensary flower prices dropped 3% this week. Here's what's driving it." + chart
- "There are 234 pending license applications in MA right now. Worcester alone has 4. If you're an operator in a saturated city, here's what to watch."
- "We analyzed 100K cannabis products across 517 MA dispensaries. The #1 brand by SKU count surprised us."

**Format:** Short text + one simple chart/image + link to free Market page

**Who to connect with:**
- MA dispensary owners/GMs (search LinkedIn for "dispensary" + "Massachusetts")
- MCC/MassCBA board members (industry influencers)
- Cannabis attorneys and consultants (they refer operators to tools)
- Cannabis journalists (Boston Globe cannabis beat, Leafly news, MJBizDaily)
- NOT investors or VCs (not the audience right now)

**Tone:** Expert peer, not vendor. Randy sharing insights from data he built, not selling a product.

---

## PART 4: WHAT TO BUILD NEXT (PRIORITIZED)

### Current Sprint Order vs. Recommended Order

**Current plan:**
1. ✅ Store Report Card (done)
2. Plain English Dashboard
3. Weekly Tape / Newsletter
4. Budtender MVP
5. Cue Pricing Alerts
6. Brand Marketplace

**Recommended revision:**

| Priority | Sprint | Why This Order |
|---|---|---|
| 1 ✅ | Store Report Card | Done. Ship it. |
| **2 (MOVE UP)** | **Cue Dynamic Pricing Alerts** | This is the $199/mo product. It's just an alert layer on existing data. No new data sources needed. Ship it BEFORE the newsletter because it's what converts free users to paid. |
| 3 | Weekly Tape / Newsletter | Distribution channel. Drives signups. But worthless if there's nothing to convert them to. Cue must exist first. |
| 4 | Public Report Card Landing Pages | For email outreach. Personalized URLs that work without auth. Critical for conversion. |
| 5 | Plain English Dashboard | Polish. Important for retention but not for first revenue. |
| **PAUSE** | **Budtender MVP** | Don't build until 50+ operators are active on GLASS. It needs menu density and operator trust to deliver value. |
| **KILL** | **Brand Marketplace** | Year 2. Zero liquidity on either side. Don't distract. |

### Reasoning

The core insight: **we need the monetization layer (Cue) BEFORE we do broad outreach.** Otherwise we drive 100 operators to a free tool with no way to convert them. The newsletter amplifies whatever exists — make sure what exists includes a paid product.

### What Cue MVP Actually Is

Strip it to the bone:
- Nightly job compares each operator's prices to nearby competitors (data we already have)
- When gap exceeds threshold, generate a recommendation
- Send SMS/email alert with: product, your price, competitor price, suggested action
- Weekly PDF summary emailed to subscriber
- Apply/Skip tracking in the dashboard (existing recommendations UI)

**Build time: 1 week.** Most of the infrastructure exists. The `recommendations` table, `alerts` table, `margin_rules` table, and price comparison queries are all in the codebase.

---

## PART 5: COMPETITIVE MOAT

### What We Have That Nobody Else Does

1. **Real-time shelf pricing for every MA dispensary cross-referenced with 7 years of CCC data.** Headset has POS sales data but not shelf pricing. BDSA has market reports but not real-time. LeafLink has wholesale but not retail. Nobody else has scraped 517 dispensary menus and cross-referenced against CCC's per-gram historical averages.

2. **100K products with brand, category, THC%, price, weight — from a single market.** This density enables product-to-product matching, not just category averages. "Your Blue Dream vs their Blue Dream" — not "your flower average vs the market."

3. **234 pending license applications as a threat intelligence layer.** This is public CCC data but nobody else is surfacing it to operators in a personalized way ("4 new applications in YOUR city").

4. **46,863 plant activity records.** This is supply-side intelligence — what's being grown, harvested, moving through the pipeline. We're not even using it yet. When we do, it's a leading indicator of supply gluts and shortages that no competitor has.

5. **The Store Report Card format.** Green/yellow/red with plain-English actions is a UX innovation for this space. Competitors show dashboards. We show "here are 3 things to do today."

6. **Operator-specific personalization from day zero.** When an operator types their store name, we already have their data. No POS integration required. No data sharing needed. We know their menu, their prices, their competitors, and their city's license pipeline before they sign up.

### What It Would Take for a Competitor to Replicate

**6-12 months of focused effort:**
- Building the scraper infrastructure (2-3 months)
- Accumulating daily price history (minimum 30 days before any time-series value)
- Integrating CCC data (1 month)
- Building the cross-reference and report card layer (1-2 months)
- Getting the first 50 operators to trust and use it (3-6 months)

The real moat is **time-series depth.** Every day our scraper runs, the moat gets deeper. In 90 days, we'll have 90 days of price history that a new entrant would need 90 days to replicate. In a year, we'll have seasonal patterns they can't match without waiting a year.

### Where We're Actually Vulnerable

1. **Dutchie could block our scraper and cut off 60% of supply.** We're scraping their menus without permission. If they detect and block us, we lose 235 stores overnight. Mitigation: diversify sources, respect rate limits, build relationships with operators who can share their own data.

2. **Headset or BDSA could build this.** They already have POS-level sales data (which we don't). If they added a free competitor pricing layer, their sales velocity data + our pricing data would be strictly superior. Mitigation: move fast, own the operator relationship before they notice our space.

3. **A single bad data quality incident could destroy trust.** If we tell an operator their flower is $7 above market and they check and it's wrong, they'll never come back. And they'll tell other operators. Mitigation: fix every data quality issue before outreach, add confidence indicators, build the "report an error" feedback loop.

4. **We have no POS data.** We know shelf prices but not sell-through rates. Our "estimated impact" numbers are educated guesses. A competitor with actual sales data can make stronger claims. Mitigation: Budtender demand signals (future), operator self-reported data, CCC plant activity as proxy.

5. **Randy is a single point of failure.** He's the only person operators will talk to, the only person who can do demos, the only person who approves outreach. The business can only grow as fast as Randy's calendar allows. Mitigation: automate everything possible, use the newsletter as a scalable touch point, build the product so operators self-serve after initial demo.

---

## PART 6: THE REAL STRATEGIC QUESTION

The question isn't "what should we build next." The question is: **Are we building an intelligence product or a relationship business?**

If GLASS is an **intelligence product**, the priority is:
- Self-serve onboarding that works perfectly
- Automated alerts that deliver value without human interaction
- Content marketing (newsletter, LinkedIn) that scales
- Product-led growth (free → paid conversion)

If GLASS is a **relationship business**, the priority is:
- Randy personally demoing to 20 founding operators
- White-glove onboarding with phone calls
- Custom report generation
- Agency sprints ($3K) as the main revenue driver

**My recommendation: it's both, in sequence.**

Months 1-3: Relationship business. Randy personally onboards 20-50 operators. Learns exactly what they need. Closes 10-20 Cue subscribers. Charges for sprints.

Months 4-6: Transition to product. Everything Randy learned gets baked into the automated experience. Newsletter takes over distribution. Self-serve conversion funnel works. Randy stops being required for every signup.

Months 7-12: Scale as a product. 200+ operators. Network effects compound. Brand marketplace becomes viable. State expansion starts.

**The worst thing we can do is try to be a product company on day one.** We don't have enough data history, enough trust, or enough users to make self-serve work. We need Randy's relationships to bootstrap the first 50 users. Then the product takes over.

---

## ACTION ITEMS — THE NEXT 72 HOURS

1. **Deploy all QA fixes and data cleanup** — brand parsing, cross-reference labels, honest empty states, number formatting. Everything from the tech fix plan that's already coded.

2. **Get daily scraping running** — confirm Railway deployment, verify scheduler is active, monitor first 3 automated runs. Without this, nothing else matters.

3. **Set up GA4** — one script tag. Before ANY email goes out. Non-negotiable.

4. **Build public Report Card landing page** — `/report/[operator-slug]` that works without auth. This is the outreach email's destination.

5. **Write outreach email final copy** — Randy reviews and approves. Personalized data points for first 25 recipients.

6. **Set up Resend email pipeline** — verify domain, test delivery to 5 friendly contacts.

7. **Start building Cue MVP** — alert engine on existing price comparison data. Target: working prototype by Feb 21.

---

## THE ONE THING

If you read nothing else in this memo:

**GLASS has genuine competitive advantage in data nobody else has assembled. The Store Report Card is the right product for the right market. The technical foundation is sound. But we are 7 days of reliable daily scraping, one round of data quality fixes, and one good outreach email away from our first paying customer. Everything else — Budtender, Brand Marketplace, Delivery, SIGNAL — is a distraction until we prove someone will pay $199/mo for competitive pricing alerts. Prove that first. Everything else follows.**

---

*Strategic Review completed February 12, 2026. Next review: February 26, 2026.*
