# GLASS Consumer Strategy — THE PLAN

**Date:** February 13, 2026  
**Status:** FINAL — Execute This  
**Synthesized from:** Opus, Codex, and Kimi strategies  
**For:** Randy Torres, Roviq

---

## TL;DR

Ship a mobile-first price comparison site with auto-generated dispensary pages and an automated social content engine in 2 weeks. The social content names real dispensaries with real prices, creating shareable "you're overpaying" moments that pull consumers to the site. The site creates SEO gravity (hundreds of thousands of indexable pages). Consumer traffic creates dispensary FOMO. Dispensaries come to us. GPID gets built underneath it all.

**The wedge is NOT an app. It's a website + social content engine.**  
**The viral unit is NOT a feature. It's a shareable price comparison card.**  
**The moat is NOT the scraping. It's the consumer audience + historical data + SEO.**

---

## 1. THE CONSUMER PRODUCT

### What We're Building: GLASS Prices

**One product, one URL, one mission:** Show every Massachusetts cannabis consumer the best price for what they want, near where they are.

**Name:** `prices.glassintel.xyz` (or `glassintel.xyz/prices`)

This is NOT "The Daily Drop" or "Best Cart" or "Deal Feed" as separate products. It's one unified product with three layers:

#### Layer 1: Search + Compare (the core utility)
Consumer enters what they want + where they are → GLASS returns every dispensary carrying it, sorted by price, with distance.

- Search by product name, strain, category, or brand
- Filter by distance (5/10/25 mi), category (flower/vape/edible/concentrate), price range
- Results show: product name, dispensary name, price, distance, "last updated X hours ago"
- **No login required.** Zero friction. Instant value.

**UX:** Think Google Shopping, not an app. Clean search box → results list → click for details. Mobile-first, fast, ugly-is-fine-if-it-works.

#### Layer 2: Auto-Generated Pages (the SEO machine)
Every dispensary, every product, every city gets an auto-generated page:

- **385+ dispensary pages:** Full menu, price rankings vs. nearby competitors, price history charts, category breakdowns
- **Product pages (GPID-powered):** Same product across all stores, sorted by price, with price history
- **City/category pages:** "Best flower prices in Boston today," "Cheapest vapes near Cambridge"

This creates **hundreds of thousands of indexable URLs** that rank for searches like:
- "GMO Cookies price Boston"
- "[Dispensary name] menu prices"
- "cheap weed near me Massachusetts"
- "best dispensary deals [city]"

Nobody else has this. Dutchie/Weedmaps pages are store-centric, not price-comparison-centric. Google bans cannabis shopping listings. We own this search space.

#### Layer 3: Price Alerts (the retention hook)
After a consumer uses GLASS once, they can set a watch:

- "Tell me when any 1/8 drops below $30 within 10 miles of Somerville"
- "Alert me when [strain] is back in stock near me"
- Delivery: SMS (Twilio, $0.008/text) or email

This turns one-time visitors into repeat users. It's the habit loop.

### Why This Specific Combination

**Decision:** I'm taking Opus's "GreenCheck" site architecture as the base, adding Codex's "Best Cart" optimizer logic to the search results ranking, and using Kimi's alert system as the retention layer. I'm killing the separate product names — consumers don't need to learn a brand vocabulary, they need to search and save money.

**Why not Opus's "Daily Drop" as the lead product?** Because the social content engine is a *distribution channel*, not the product. The product is the website. Social drives traffic to it.

**Why not Codex's "receipt check" in the MVP?** It's clever but it's a post-purchase feature. We need pre-purchase utility first — that's where the money-saving moment happens and where the behavioral change starts. Receipt check is Month 2.

**Why not Kimi's "Deal Feed" as a standalone?** A feed is just one view of the same data. It's a feature of the site, not a separate product.

### The User Journey

```
1. Consumer sees GLASS social post: "The same cart is $28 at Store A 
   and $54 at Store B. They're 3 miles apart."
2. Consumer taps link → lands on GLASS comparison page
3. Searches for their usual products → sees they've been overpaying
4. Sets a price alert for their favorites
5. Gets SMS next week: "Price drop! [Product] now $32 at [Store]"
6. Tells friends: "Use this site before you buy weed"
7. Shares a GLASS price card in group chat
8. Friends visit → loop repeats
```

**The aha moment:** "The dispensary 10 minutes from me charges $15 less for the exact same thing." Once you see it, you can't unsee it.

---

## 2. THE VIRAL LOOP

### Decision: Shareable Price Comparison Cards + Automated Social

All three strategies proposed viral mechanics. Here's what actually works given the constraints (no paid ads, one-person team, cannabis content restrictions, MA-specific):

### The Viral Unit: Price Comparison Cards

A **Price Card** is a single image (optimized for social sharing) that contains:
- A specific product or category
- 2-5 dispensary prices side by side
- A price gap highlighted ("Save $18 by going 2 miles further")
- "glassintel.xyz" watermark
- Timestamp ("prices as of Feb 13, 2026")

These cards are:
1. **Auto-generated** from GLASS data (AI agent builds them daily)
2. **Posted to social** by GLASS accounts (2-3/day across platforms)
3. **Embedded on every GLASS page** with a "Share This" button
4. **Shareable via iMessage/WhatsApp** with rich link previews

### Why Cards Beat Everything Else

- **They work on every platform** — image posts work on X, IG, TikTok (as stills or video), Reddit, group chats
- **They're inherently shareable** — people LOVE sharing "can you believe this?" pricing gaps
- **They're automatable** — no human needed to create them, just to curate
- **They dodge cannabis ad restrictions** — it's market data, not product promotion
- **They tag dispensaries by name** — forcing dispensary attention (the Yelp mechanic)

### Content Formats (All Automatable)

| Format | Example | Frequency |
|--------|---------|-----------|
| **Price Gap Shock** | "Same cart: $28 vs $54, 3 miles apart" | Daily |
| **Best Price by City** | "Best $30 eighth in Boston right now" | Daily |
| **Price Drop Alert** | "[Strain] just dropped from $55→$38 at [Store]" | As they happen |
| **Weekly Roundup** | "Top 10 price drops this week in MA" | Weekly |
| **Category Deep Dive** | "We checked every vape cartridge price in Massachusetts" | Weekly |
| **Data Visualization** | "MA weed prices have dropped 73% since 2020" | Monthly |

### Distribution Channels (Ranked by Viability)

1. **X (Twitter)** — Safest for cannabis content. Explicitly allows informational cannabis content. Start here.
2. **TikTok/Reels** — Use charts, maps, text overlays — NO product imagery. Frame as "data/market analysis." High reach potential.
3. **Reddit (r/bostontrees)** — 32K members, cannabis-obsessed, data-hungry. Post genuine analysis, not promotion.
4. **SEO** — The long game. Every page we build ranks for cannabis price searches. This is the compounding channel.
5. **SMS/Email alerts** — Owned audience. No algorithm dependency.
6. **Instagram** — Riskiest. Use data visualizations only, coded language. Treat as expendable.

### What I'm Killing

- **Kimi's "You Overpaid" receipt scanner** in the MVP — cool but post-purchase, and adds build complexity. Revisit in Month 2.
- **Opus's browser extension** — install friction is too high for a cannabis audience that's mostly mobile.
- **Codex's community receipt panel** — too early. Need core utility first.
- **Gamification/badges/leaderboards** — nice-to-have, not launch material. Don't build social features until you have users.

---

## 3. THE 90-DAY PLAN

### Weeks 1-2: "Ship the Core" (Feb 14 – Feb 27)

**Goal:** Consumer price comparison site live + social content engine running.

| Day | What Ships | Owner |
|-----|-----------|-------|
| 1-2 | Create social accounts: @glassintel on X, TikTok, Instagram, YouTube | Randy |
| 1-3 | Build content generation pipeline: DB query → AI → price card image templates (6 formats) | AI Agent |
| 1-3 | Build consumer MVP: search → price comparison results page, mobile-first, no auth required | AI Agent (Kimi K2.5 for frontend) |
| 4-5 | Generate first 30 social posts from live GLASS data, queue for daily posting | AI Agent |
| 5-6 | Deploy consumer site at `prices.glassintel.xyz` | AI Agent |
| 6-7 | Randy reviews first batch of social posts, calibrates tone | Randy |
| 7 | Begin posting: 2-3 posts/day on X, 1-2/day on TikTok/Reels | Automated (Buffer/custom) |
| 8-10 | Build auto-generated dispensary page template — one page per dispensary, populated from DB | AI Agent |
| 8-10 | SEO: meta tags, Open Graph cards, structured data (Product schema), sitemap for all pages | AI Agent |
| 11-12 | Build auto-generated city/category landing pages ("Best flower deals in Boston") | AI Agent |
| 13 | Seed r/bostontrees with genuine data analysis: "I compared prices at every dispensary in MA" | Randy |
| 14 | **CHECKPOINT:** Measure social engagement, site traffic, first Reddit response | Review |

**Deliverables by Day 14:**
- [ ] Consumer price comparison site live (search → results → store pages)
- [ ] 385+ auto-generated dispensary pages indexed
- [ ] 50+ city/category landing pages indexed
- [ ] Social content pipeline running (2-3 posts/day, Randy approves daily batch)
- [ ] Reddit seeding post published
- [ ] Share cards working (image + deep link)

**Success criteria:** 1,000+ site visitors in Week 2. If we hit this, the thesis has legs. If not, check content quality and Reddit/social distribution before pivoting.

---

### Weeks 3-4: "Add the Hooks" (Feb 28 – Mar 13)

**Goal:** Retention mechanics + dispensary awareness begins.

| Day | What Ships | Owner |
|-----|-----------|-------|
| 15-17 | Build Price Alert system: email + SMS (Twilio), user sets product/category + price threshold + location | AI Agent |
| 18-20 | Build "Claim Your Page" flow on every dispensary page — name, email, verify ownership | AI Agent |
| 18-20 | Add price history charts to product and dispensary pages (we have the time-series data) | AI Agent |
| 21-23 | Launch weekly consumer newsletter: "The MA Weed Report" — top deals, biggest price drops, data highlights | AI Agent + Randy curates |
| 24-26 | Iterate social content based on Week 1-2 performance — double down on formats that got engagement | AI Agent |
| 27-28 | Add "Near Me" mode (geolocation permission → auto-sort by distance) | AI Agent |
| 28 | **CHECKPOINT:** Alert signups, claim requests, newsletter subscribers, social growth rate | Review |

**Deliverables by Day 28:**
- [ ] Price Alert system live (SMS + email)
- [ ] "Claim Your Page" flow live
- [ ] Price history charts on all pages
- [ ] Consumer newsletter launched (first 2 issues sent)
- [ ] "Near Me" mode working
- [ ] Social content optimized based on data

**Key metrics to hit:**
| Metric | Target |
|--------|--------|
| Site monthly visitors | 5,000 |
| Alert subscribers | 200+ |
| Newsletter subscribers | 500+ |
| Social followers (all platforms) | 2,500+ |
| Dispensary claim requests | 5+ |

---

### Month 2: "Build the Flywheel" (Mar 14 – Apr 10)

**Goal:** SEO starts compounding, dispensaries take notice, first revenue-adjacent features.

**Week 5-6:**
- Build GLASS Score algorithm — objective dispensary rating combining: price competitiveness (40%), selection breadth (20%), menu freshness (15%), price stability (10%), THC accuracy vs CCC lab data (15%)
- Display score on every dispensary page (it's public, it's transparent, methodology is published)
- Build premium "Claimed Page" features: analytics dashboard (page views, search appearances, competitive position), menu correction tools, deal highlighting
- Price: $199/month for premium claimed page

**Week 7-8:**
- Repurpose existing Virtual Budtender as consumer-facing "Product Finder" on GLASS — quiz-style: "What are you looking for?" → matches across ALL stores, ranked by price
- Build referral attribution: track when consumers click from GLASS to dispensary menu pages (Dutchie/Weedmaps/direct)
- Launch THC Accuracy Score: cross-reference CCC's 298K-row lab dataset against menu THC claims. Flag discrepancies. This is a **consumer protection feature** that gets press coverage.
- Press pitch to Boston Globe / MassLive: "We analyzed THC labels at every MA dispensary. Here's what we found."

**Deliverables by Day 56:**
- [ ] GLASS Score live on all dispensary pages
- [ ] Premium claimed pages available ($199/mo)
- [ ] Product Finder live
- [ ] Referral attribution tracking
- [ ] THC Accuracy analysis complete
- [ ] At least 1 press pitch sent

**Key metrics to hit:**
| Metric | Target |
|--------|--------|
| Site monthly visitors | 25,000 |
| Alert subscribers | 1,000+ |
| Newsletter subscribers | 2,000+ |
| Social followers (all platforms) | 10,000+ |
| Dispensary pages claimed | 25+ |
| Premium subscriptions | 3-5 |

---

### Month 3: "B2B Gravity Kicks In" (Apr 11 – May 13)

**Goal:** Dispensaries are coming to us. First real revenue.

**Week 9-10:**
- Build Consumer Demand Report for dispensaries (anonymized): "What consumers in your area are searching for, what price points they set alerts at, what categories are trending"
- Price: $299/mo per dispensary
- Launch Brand Placement pilot (Cue lite): brands pay to be "Featured" in Product Finder results and on category pages. Clearly labeled as sponsored.
- Start outreach to dispensaries who've appeared in popular GLASS social posts — but frame as "your page is getting traffic, want to claim it?" not cold sales

**Week 11-12:**
- Build Weekly MA Price Index Report — public data report that media can cite, regulators find useful, operators reference
- Approach CCC with GLASS data: "We found X% of dispensaries list THC percentages exceeding lab-tested results by >5 points." This is the regulatory credibility play.
- Evaluate: what's working, what's not, where do we double down?

**Deliverables by Day 90:**
- [ ] Consumer Demand Reports available
- [ ] Brand Placement (Cue lite) generating first revenue
- [ ] Weekly MA Price Index publishing
- [ ] CCC engagement attempted
- [ ] At least 1 media placement using GLASS data

**Key metrics to hit:**
| Metric | Target |
|--------|--------|
| Site monthly visitors | 50,000-75,000 |
| Alert subscribers | 3,000+ |
| Newsletter subscribers | 5,000+ |
| Social followers (all platforms) | 25,000+ |
| Dispensary pages claimed | 75+ |
| Premium subscriptions | 10-15 |
| Monthly revenue | $3,000-$8,000 |

---

## 4. REVENUE MODEL

### The 3 Revenue Streams That Matter (First 6 Months)

I'm not listing 15 options. Here are the 3 that are realistic for a one-person-plus-AI-agents team:

#### Revenue Stream 1: Premium Claimed Pages ($199/mo per dispensary)

**What the dispensary gets:**
- Analytics dashboard: page views, search appearances, how they rank, what consumers search for
- Menu correction tools: fix prices, add products, update hours
- Deal highlighting: promote specific products on their GLASS page
- Competitive intelligence: how their prices compare to nearby stores

**Why they'll pay:** Their GLASS page exists whether they like it or not (public data). Consumers are viewing it. They need to control the narrative. This is the Yelp/Google Business Profile playbook.

**Projection:** 10 stores × $199/mo = $1,990/mo by Month 6. Conservative. If consumer traffic is strong, this could be 25-50 stores.

#### Revenue Stream 2: Brand Placement / Cue Lite ($500-$2,000/mo per brand)

**What the brand gets:**
- Featured placement in Product Finder results when their products match consumer searches
- Sponsored cards in the social content pipeline ("Featured deal: [Brand] [Product] at [Store]")
- Inclusion in the weekly newsletter

**Why they'll pay:** Brands CANNOT advertise on social media or Google. GLASS is one of the only ways to get their products in front of cannabis consumers with purchase intent. This is enormously valuable.

**Projection:** 5 brands × $800/mo = $4,000/mo by Month 6.

#### Revenue Stream 3: Roviq Agency Upsell (Inbound Only)

**What happens:** A dispensary sees their GLASS Score is 58/100. They see competitors at 82. They see they're ranked #31 out of 36 in their city for pricing. They want to fix it. They don't need a cold call — they come to Roviq because the data already made the case.

Services: pricing strategy, menu optimization, content/social, full marketing retainer ($2,500/mo+).

**Why it works:** The GLASS Score creates the anxiety. Roviq sells the solution. Zero outbound sales.

**Projection:** 2-3 agency clients from GLASS referrals by Month 6 = $5,000-7,500/mo.

#### Combined 6-Month Revenue Projection

| Month | Premium Pages | Brand Placement | Agency Upsell | Total |
|-------|--------------|----------------|---------------|-------|
| 1-2 | $0 | $0 | $0 | $0 |
| 3 | $400 | $0 | $0 | $400 |
| 4 | $1,000 | $800 | $0 | $1,800 |
| 5 | $1,600 | $2,400 | $2,500 | $6,500 |
| 6 | $2,000 | $4,000 | $5,000 | $11,000 |

**This is conservative.** If consumer traffic hits 75K+ monthly visitors, these numbers could 2-3x. The key insight from all three strategies: consumer attention is the product, and it compounds.

### What I'm NOT Including Yet

- Consumer Demand Data reports ($299/mo) — realistic but needs more consumer volume first. Month 4+ add-on.
- Delivery commission (Delivered spoke) — powerful but requires operational integration. Month 6+ play.
- Data licensing to investors/researchers — real money but long sales cycle. Year 1 opportunity.
- GLASS Pass / loyalty — transformative but complex. Year 1 at earliest.

---

## 5. TECH STACK & AUTOMATION

### What Gets Built

| Component | What It Is | Who Builds | Timeline |
|-----------|-----------|------------|----------|
| Consumer site (prices.glassintel.xyz) | Mobile-first search + results + store pages + product pages + city pages | Kimi K2.5 (frontend) + Codex 5.3 (backend/API) | Week 1-2 |
| Price Card Generator | Auto-generates shareable image cards from price data | AI Agent | Week 1 |
| Social Content Pipeline | DB query → AI copy → image/video generation → scheduling | AI Agent + Buffer/custom scheduler | Week 1-2 |
| Alert System | User sets threshold → cron checks daily scrape → Twilio SMS or email | Codex 5.3 | Week 3 |
| Claim Flow | Dispensary owner enters info → verification → basic dashboard | Codex 5.3 | Week 3-4 |
| GLASS Score | Algorithm runs on existing data → score displayed on pages | Codex 5.3 | Week 5-6 |
| Premium Dashboard | Analytics, correction tools for claimed pages | Kimi K2.5 (frontend) + Codex 5.3 (backend) | Week 5-6 |

### Architecture

```
┌─────────────────────────────────────────────┐
│  Existing GLASS Data Pipeline               │
│  (Dutchie, Weedmaps, Leafly, iHeartJane    │
│   scrapers → PostgreSQL + ClickHouse)       │
└───────────────┬─────────────────────────────┘
                │
        ┌───────▼───────┐
        │  GLASS API     │  (NestJS/Fastify)
        │  - Search      │
        │  - Alerts      │
        │  - Scores      │
        │  - Analytics   │
        └───┬───────┬───┘
            │       │
    ┌───────▼──┐ ┌──▼───────────┐
    │ Consumer  │ │ Content      │
    │ Web App   │ │ Pipeline     │
    │ (Next.js/ │ │ (AI gen →    │
    │  React)   │ │  Buffer/X/   │
    │           │ │  TikTok)     │
    └──────────┘ └──────────────┘
```

**Tech choices:**
- Frontend: React + Next.js (SSR for SEO, essential for indexable pages) + Tailwind
- Backend: Existing GLASS API extended with consumer endpoints
- Database: Already have PostgreSQL + ClickHouse — no changes needed
- Auth: Not needed for consumer site MVP. Clerk/Supabase only when we add claimed pages.
- Hosting: Whatever's already in place. Fly.io, Vercel, or AWS.
- SMS: Twilio (~$0.008/text, negligible cost at early scale)

### Content Generation Pipeline (Specific)

**Daily automated flow:**

```
6:00 AM — Scraper data lands in DB (existing pipeline)
    ↓
6:30 AM — AI Agent runs "Daily Content Queries":
    - Top 5 price drops by city (Boston, Worcester, Cambridge, Springfield, Lowell)
    - Biggest price gap for same product across stores
    - New products that appeared overnight
    - Category winners (cheapest flower, vape, edible by city)
    ↓
7:00 AM — AI generates:
    - 6-8 price comparison cards (image templates populated with data)
    - 2-3 short-form video scripts (text overlay + charts, no product imagery)
    - Social copy for each platform (X = data-forward, TikTok = hook-driven, IG = visual)
    ↓
7:30 AM — Queue populated in Buffer (or custom scheduler)
    ↓
8:00 AM — Randy reviews queue (10 min). Approves/rejects/edits.
    ↓
Posts deploy: 9am, 12pm, 5pm (staggered across platforms)
```

**Weekly automated flow:**
- Friday: Generate "Weekly Roundup" (top 10 drops, biggest movers, city rankings)
- Sunday: Generate newsletter content for Monday send
- Monthly: Generate "MA Cannabis Market Report" data visualization

### What Randy Does vs. What AI Does

| Task | Who |
|------|-----|
| Create social accounts, set up profiles, bio, branding | Randy (once) |
| Daily content review/approval (10 min/day) | Randy |
| Reddit posting and community engagement | Randy |
| Press outreach, relationship building | Randy |
| Strategic decisions, pivots | Randy |
| Content generation (cards, copy, video scripts) | AI Agent |
| Site development and deployment | AI Agent (Kimi/Codex) |
| SEO optimization, page generation | AI Agent |
| Alert system, cron jobs, monitoring | AI Agent |
| Data pipeline, scraping, normalization | AI Agent (existing) |
| GLASS Score calculation | AI Agent |
| Analytics tracking, reporting | AI Agent |

**Randy's daily time commitment: ~30 minutes** (10 min content review, 10 min community engagement, 10 min checking metrics). Everything else is automated or agent-built.

---

## 6. RISKS & KILL CRITERIA

### Real Risks (Honest Assessment)

#### Risk 1: Social Accounts Get Banned
**Likelihood:** Medium (Instagram high, TikTok medium, X low)  
**Impact:** High — loses top-of-funnel

**Mitigation:** 
- Frame everything as market data, not product promotion. Charts and text, not product photos.
- X is the primary platform (safest). Instagram is expendable.
- Build email list (newsletter) and SMS list (alerts) immediately — these are algorithm-proof.
- If banned, relaunch with "Massachusetts Market Data" framing.

#### Risk 2: Consumers Don't Come Back
**Likelihood:** Medium  
**Impact:** Fatal

**Mitigation:**
- Alerts are the retention mechanism. If Day 1 visitors don't set alerts, the content isn't compelling enough.
- Test "savings amount" messaging — Codex is right that "you saved $X" is the strongest motivator.
- If 7-day retention is below 15% among alert users, the value prop isn't landing. Pivot content strategy before pivoting product.

#### Risk 3: Data Accuracy Kills Trust
**Likelihood:** Medium (the 94% Weedmaps scraper failure rate is a real problem)  
**Impact:** Very high — one wrong price shared = lost credibility

**Mitigation:**
- Show "last updated" timestamp on EVERY price. Prominently.
- Don't show prices older than 48 hours.
- Add confidence indicators (how recently scraped, how many sources confirm)
- "Report wrong price" button on every listing
- **Fix the Weedmaps scraper before launch.** This is a prerequisite.

#### Risk 4: Dispensary Legal Pushback
**Likelihood:** Low  
**Impact:** Medium

**Mitigation:**
- All data is from public menus. Publishing public prices is not illegal — it's journalism.
- "Claim Your Page" gives dispensaries agency. They can correct data.
- GLASS Score methodology is transparent. No black box.
- Yelp/Google/TripAdvisor legal precedent: ranking businesses using public data is protected.

#### Risk 5: Too Much to Build, Too Small a Team
**Likelihood:** Medium-high  
**Impact:** High

**Mitigation:**
- The 90-day plan is ruthlessly sequenced. If we only ship Weeks 1-2 (site + social), we've tested the thesis.
- AI agents handle 90% of code and content. Randy curates and directs.
- The MVP consumer site is: search box → results list → auto-generated store pages. That's a weekend of AI-assisted dev.
- **Don't over-design. GasBuddy v1 was ugly. The data was useful. That's enough.**

### Kill Criteria — When to Pivot

Be honest about when this isn't working:

| Signal | Timeline | Decision |
|--------|----------|----------|
| <500 visitors after 2 weeks of social posting | Week 3 | Content strategy is wrong. Audit what's not resonating. Try Reddit-only approach. |
| <2,000 visitors after 4 weeks | Week 5 | Consumer thesis may be wrong. Test direct Reddit/forum approach before killing. |
| <5% alert opt-in rate among visitors | Week 4 | Value prop isn't compelling enough. Test different framing (savings vs. deals vs. discovery). |
| 0 dispensary claim requests after 8 weeks | Week 9 | Consumer traffic isn't creating B2B pressure. Either traffic is too low or dispensaries don't care. Reassess. |
| <10,000 monthly visitors after 90 days | Week 13 | Strategy isn't working at needed scale. Consider: (a) different market (CT/RI), (b) pivot to B2B-first with consumer as secondary, (c) different content approach. |
| Social accounts banned on 2+ platforms | Any time | Pivot to SEO + newsletter + SMS as primary distribution. Social was an accelerant, not the foundation. |

### What Would Make This Fail Entirely

- **Scraper data quality is too bad to show consumers.** If we can't show accurate prices, nothing else matters. Fix the data pipeline first.
- **Massachusetts consumers simply don't comparison-shop for cannabis.** Possible but unlikely given how price-sensitive the MA market has become (73% price collapse since 2020).
- **A platform player (Dutchie/Weedmaps) builds this first.** Unlikely due to their structural conflict (their clients don't want price transparency). But if they do, we pivot to being the "honest, independent" alternative.

---

## 7. HOW THIS CONNECTS TO GLASS-PLAN.md

The consumer strategy doesn't replace the existing GLASS product plan. It **accelerates it** by solving the cold-start problem:

| GLASS-PLAN Component | Without Consumer Strategy | With Consumer Strategy |
|---------------------|--------------------------|----------------------|
| **Price Wire** | Operators sign up → see competitor data | Consumers already using the data → operators come to see what consumers see |
| **Threat Radar** | We pitch to operators | Operators find us because their GLASS page shows competitive threats |
| **Margin Engine** | We demo to operators | GLASS Score shows operators they're uncompetitive → they want the fix |
| **Cue (brand incentives)** | Pitch to brands one by one | Brands pay for placement in front of 50K+ consumers with purchase intent |
| **Delivered** | Toggle in operator dashboard | "Get it delivered" button on consumer site → consumer pull, not operator push |
| **AC Toll Processing** | Pitch to cultivators | Consumer demand data shows what products the market wants but can't find |
| **Roviq agency** | Cold outreach to operators | GLASS Score creates anxiety → operators come to Roviq for help |
| **POS integration** | We beg for API access | Dispensaries demand their POS sync with GLASS because consumers are there |
| **GPID** | Technical infrastructure project | Consumer site needs product matching → GPID gets built as a byproduct of consumer utility |

**The consumer layer is the gravity well that makes everything else in GLASS-PLAN.md happen faster and with zero cold sales.**

---

## 8. RESOLVED CONTRADICTIONS

Where the three strategies disagreed, here's what I decided and why:

### Contradiction 1: Lead with social content (Opus) vs. lead with utility product (Codex/Kimi)

**Decision:** Ship both simultaneously in Week 1-2. The site is the product. Social is the distribution. Neither works without the other. Opus was right that social creates awareness, but Codex/Kimi were right that you need a destination worth visiting.

### Contradiction 2: Build community features early (Opus) vs. utility-only (Codex/Kimi)

**Decision:** Utility only for the first 60 days. Codex is right: community features (check-ins, lists, gamification) are retention plays that only matter when you have users to retain. Don't build social features for an audience that doesn't exist yet.

### Contradiction 3: Revenue timeline — Opus says Month 3, Codex says prove thesis first, Kimi says force B2B by Day 46

**Decision:** Kimi's timeline is the most aggressive and closest to right. We should be showing "Claim Your Page" by Week 3 and charging for premium by Week 5-6. We shouldn't wait for 50K visitors to monetize — even 10 claimed pages at $199/mo is signal that the model works. But don't optimize for revenue in Weeks 1-4. Growth only.

### Contradiction 4: GLASS Score complexity — Opus wants 5 components including THC accuracy, Codex wants a "fairness badge," Kimi wants something simpler

**Decision:** Ship Opus's full 5-component score. The THC Accuracy component (using CCC lab data) is the killer differentiator — nobody else has this, it's a consumer protection angle that gets press coverage and regulatory credibility, and it creates urgency for dispensaries to claim their page. Codex's "fairness badge" is just a simpler version of the same idea. Go big.

### Contradiction 5: Newsletter focus — B2B (GLASS-PLAN) vs. consumer (Opus) vs. both (Codex/Kimi)

**Decision:** Consumer newsletter is primary. "The MA Weed Report" — weekly email to consumers with top deals, biggest drops, data highlights. The B2B newsletter ("Operator's Margin Report") still exists but becomes secondary. The consumer list is 100x larger and feeds the social content loop.

---

## 9. WHAT HAPPENS AFTER 90 DAYS

If the 90-day plan works (50K+ monthly visitors, 75+ claimed pages, $3K+ monthly revenue), here's the next phase:

**Months 4-6:**
- Launch Consumer Demand Data product for dispensaries ($299/mo)
- Full Cue integration (brands pay for incentive campaigns targeting GLASS users)
- Delivery integration via Delivered spoke ("Get it delivered" on every product page)
- Expand to Connecticut and Rhode Island (same scraper model, new market)
- GLASS Pass / cross-dispensary loyalty program design (launch Month 6-7)

**Months 7-12:**
- POS integration conversations (from strength, not supplication)
- GPID becomes the industry standard because consumers and dispensaries both use it
- Data licensing to investors, researchers, regulators
- Revenue target: $50-100K/month

---

## 10. TOMORROW MORNING

Randy, here's what you do on Day 1:

1. **Create accounts:** @glassintel on X, TikTok, Instagram, YouTube. Use consistent branding. Bio: "Every cannabis price in Massachusetts. Updated daily. Stop overpaying."
2. **Verify scraper data quality.** Spot-check 20 dispensaries against their live menus. If accuracy is below 90%, fix the pipeline before building anything consumer-facing.
3. **Spin up the AI agents:**
   - Kimi K2.5: Build the consumer site frontend (search → results → store pages). Mobile-first. Fast. Ugly is fine.
   - Codex 5.3: Build the API endpoints for consumer search, price comparison, and auto-generated pages.
   - Content agent: Generate the first batch of 30 price comparison cards from live GLASS data.
4. **Write the r/bostontrees post.** Draft it yourself — it needs to sound like a real person, not a company. "I built a tool that compares prices at every dispensary in Massachusetts. Here's what I found." Include 3-4 genuinely surprising data points.
5. **Set up Buffer or equivalent** for social scheduling.

That's it. Ship the site by end of Week 1. Start posting by Day 7. Learn from what happens in Week 2.

**Don't sell. Build something so good they come to you.**

---

*This strategy was synthesized from three independent analyses (Opus, Codex, Kimi) that all converged on the same core thesis: consumer traffic is the gravity well that makes everything else in GLASS work. The disagreements were on sequencing and naming, not direction. The direction is clear. Execute.*
