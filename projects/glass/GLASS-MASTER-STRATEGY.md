# GLASS MASTER STRATEGY — THE WAR PLAN

**Date:** February 13, 2026  
**Status:** DEFINITIVE — Single Source of Truth  
**Replaces:** GLASS-PLAN.md (product), CONSUMER-STRATEGY-FINAL.md (consumer), COMPETITIVE-INTELLIGENCE.md (competitive), HOODIE-ANALYTICS-DEEP-DIVE.md (threat analysis)  
**For:** Randy Torres, Roviq  
**Anti-Hoodie Filter:** Every decision in this document answers: *"How does this beat Hoodie?"*  
**Advisor Review:** Incorporates external strategic advisor feedback (Feb 13, 2026) — see ADVISOR-FEEDBACK.md

---

## ⚠️ STEP 0 — DATA INTEGRITY (BEFORE ANYTHING ELSE)

**The advisor's brutal truth: if the data is wrong, nothing else matters. Three landmines that kill consumer trust on Day 1:**

### Landmine 1: GPID Must Launch as a Curated Catalog, Not a Fuzzy Matching Engine

A price comparison site IS a product matching engine. If we match a 1g pre-roll with a 3.5g flower, r/bostontrees will crucify us publicly on Day 1 and we'll never recover.

**FIX: The Top 500.**
- Query the DB for the 500 most ubiquitous SKUs across MA (appear at most stores, highest scrape frequency)
- Hand-verify every match: same brand, same strain, same weight, same product type
- Launch consumer site with ONLY these 500 verified products for price comparison
- Positioning: *"We track the 500 most popular cannabis products in Massachusetts"*
- This is a feature, not a limitation — curated accuracy beats noisy breadth
- Expand by 100-200 products per month as matching improves and community validation kicks in

**Why this beats Hoodie:** Hoodie claims 30M product variants. Most are unverified. 500 hand-verified products with 100% accuracy beats 30M with unknown accuracy for the consumer who needs to trust the price they see.

### Landmine 2: Pre-Tax vs Post-Tax Price Normalization

MA dispensaries inconsistently show pre-tax vs tax-included prices on their menus. MA effective cannabis tax is ~20% (state excise 10.75% + state sales 6.25% + local up to 3%). A "Store A is $10 cheaper" social card that's wrong after tax = instant credibility death. One wrong card shared on Reddit and we're "that site that doesn't understand taxes."

**FIX: All prices normalized to post-tax (out-the-door) pricing.**
- **Week 1 task:** Build tax detection pipeline:
  1. Scrape Dutchie store profiles for `tax_included` flag (Dutchie exposes this)
  2. For Weedmaps/Jane/Leafly: compare menu price to cart simulation price (add to cart, check total)
  3. For ambiguous stores: flag as "price may not include tax" until verified
  4. Maintain per-store `tax_inclusion_status` field: `confirmed_inclusive`, `confirmed_exclusive`, `unknown`
- **Display logic:** Always show post-tax price. If store is `confirmed_exclusive`, apply MA tax formula. If `unknown`, show pre-tax with visible warning: "⚠️ Tax not included — estimated total: $XX.XX"
- **Social content rule:** NEVER post a price comparison card unless BOTH stores have confirmed tax status. One wrong comparison = permanent credibility damage.

### Landmine 3: Data Freshness — The "Drive of Shame" Problem

Cannabis inventory moves fast. Daily deals sell out in 3 hours. Consumer drives 30 minutes to a store based on a GLASS price, product is sold out or price changed. Consumer blames GLASS. Tells friends. We're done.

**FIX: Aggressive freshness signals and staleness controls.**
- **"Verified X hours ago"** timestamp on EVERY price, prominently displayed (not small gray text — this is a trust signal)
- **"🔴 Report Out of Stock"** button next to every product listing (one-tap, no login required, immediately flags for re-scrape)
- **Auto-hide prices older than 24 hours** from consumer-facing search results (still available in operator dashboard with "stale" warning)
- **Freshness tiers in UI:**
  - 🟢 Verified < 4 hours ago (high confidence)
  - 🟡 Verified 4-12 hours ago (moderate confidence)
  - 🟠 Verified 12-24 hours ago (use with caution)
  - Hidden if > 24 hours (not shown to consumers)
- **Social content rule:** Price comparison cards MUST use data verified within the last 6 hours. No exceptions.
- **Scraper priority queue:** Stores featured in social content get scraped 30 minutes before the post goes live

---

## THE SITUATION IN 60 SECONDS

Hoodie Analytics is our #1 threat. $9.4M raised. 36 employees. 10,000 dispensaries tracked. 3 billion daily observations. 30 million product variants cataloged. 6 years of historical data. IRI/Nielsen/NPD alumni. CEO Wes Shepherd built and sold Channel IQ (same exact business model) to Numerator in 2016. He's done this before.

In December 2025, Hoodie partnered with High Times — 50+ years of cannabis brand recognition, millions of monthly readers — to launch consumer-facing product discovery and e-commerce across all 10,000 dispensaries. "Hoodie Connect" gives retailers free listings and order referrals. They're calling it "the Amazon of marijuana."

We have: one person, AI agents, zero dollars allocated to GLASS specifically, 385 scraped Massachusetts dispensaries, 150K price data points, and a 6-12 month window before Hoodie could enter MA seriously.

**This is a David vs Goliath fight. But David had a sling. Ours is called GPID.**

---

## TABLE OF CONTENTS

1. [Kill Shots — Our 5 Structural Advantages](#1-kill-shots--our-5-structural-advantages)
2. [Battle Plan: GLASS vs Hoodie Feature-by-Feature](#2-battle-plan-glass-vs-hoodie-feature-by-feature)
3. [GPID — The Nuclear Weapon](#3-gpid--the-nuclear-weapon)
4. [Consumer Strategy (Hoodie-Aware)](#4-consumer-strategy-hoodie-aware)
5. [Community Data Moat (Anti-Hoodie)](#5-community-data-moat-anti-hoodie)
6. [Vertical Integration — Their Blind Spot](#6-vertical-integration--their-blind-spot)
7. [The 6-12 Month Window](#7-the-6-12-month-window)
8. [Revenue That Survives Hoodie](#8-revenue-that-survives-hoodie)
9. [Execution Plan — Week by Week, First 90 Days](#9-execution-plan--week-by-week-first-90-days)
10. [Win Conditions & Kill Criteria](#10-win-conditions--kill-criteria)
11. [If Hoodie Enters MA — Emergency Playbook](#11-if-hoodie-enters-ma--emergency-playbook)

---

## 1. KILL SHOTS — OUR 5 STRUCTURAL ADVANTAGES

These aren't feature gaps Hoodie can close by hiring engineers. These are structural positions rooted in our business model, geography, and architecture. Hoodie would have to fundamentally change what they are to compete on these dimensions.

### Kill Shot #1: FREE vs $1,000-$5,000/month

Hoodie's entire revenue model depends on enterprise pricing. They have $9.4M in VC debt that demands returns. Every dollar they discount to compete with us is a dollar their investors lose. Their cost structure (36 employees × ~$100K avg = $3.6M/yr in payroll alone) makes a free tier for operators economically suicidal.

GLASS is free because operators aren't the customer — they're the network. Revenue comes from brands (Cue), delivery (Delivered), toll processing (AC), and agency upsells (Roviq). Hoodie can't copy this model without abandoning their existing revenue, firing most of their team, and telling their investors the business model changed. They won't.

**The play:** Launch free. Stay free. Make "free" the first word every MA operator associates with GLASS.

### Kill Shot #2: LOCAL vs NATIONAL

Hoodie tracks 10,000 dispensaries across 50 states. Massachusetts is ~400 of those — a 4% rounding error. They will never build MA-specific features because the ROI doesn't justify it for one state.

We know which CCC meetings matter. We know which license applications are pending in which towns. We know MA's unique pricing dynamics (73% wholesale collapse). We know the 120 independent operators fighting MSO competition. We know which dispensaries are 2 miles apart and competing on the same product mix.

Hoodie knows MA has dispensaries. That's it.

**The play:** Go so deep in MA that Hoodie's national data looks like a Wikipedia summary next to our encyclopedia entry. Integrate CCC regulatory data, local lab testing results, municipal meeting minutes, and neighborhood-level competitive analysis. None of this has ROI for a national platform.

### Kill Shot #3: OPERATOR-FIRST vs BRAND-FIRST

Hoodie's paying customers are brands and MSOs — Curaleaf, PharmaCann, 1906, Good Day Farm. Their entire product suite is designed for brands asking "where is my product stocked and at what price?" The operator is the data source, not the customer.

GLASS is built for the operator asking "how do I survive this margin compression?" We show them what to do, not just what's happening. Margin Engine gives pricing recommendations. Threat Radar warns about new competitors. The spokes (delivery, incentives, toll processing) are actions operators can take immediately.

Hoodie shows data. GLASS drives action.

**The play:** Every GLASS feature ends with a verb, not a chart. "Lower this price." "Watch this competitor." "Turn on delivery." "Launch this incentive."

### Kill Shot #4: CROSS-PLATFORM PRODUCT MATCHING (GPID)

Nobody — not Hoodie, not Headset, not BDSA, not anyone — matches the same product across Dutchie, Weedmaps, iHeartJane, and Leafly to find price discrepancies. Hoodie's "Product Catalog" (30M variants) matches brand products to menus from the brand side. Our GPID matches from the consumer side — the same physical product listed differently on different platforms at the same store or across stores.

This creates price comparison that is structurally impossible without cross-platform scraping + fuzzy matching. Hoodie scrapes too, but they don't cross-reference. They can't tell you "Your Blue Dream is $45 on Dutchie and $38 on Weedmaps at the same store." We can.

**The play:** Make GPID the centerpiece, not a backend feature. (See Section 3.)

### Kill Shot #5: INTEGRATED FULFILLMENT

Hoodie's value chain ends at intelligence. They show you the problem and walk away. GLASS goes from intelligence → recommendation → action → fulfillment:

- See the problem (Price Wire) → Get the recommendation (Margin Engine) → Act on it (price change)
- Inventory isn't moving (Price Wire) → Launch brand-funded incentive (Cue) → Budtender pushes it
- Competitor offers delivery (Threat Radar) → Toggle delivery on (Delivered, license MD1303)
- Margin gap in a category (Margin Engine) → White-label manufacturing to fill it (AC Toll Processing)

Hoodie has no delivery network. No brand incentive platform. No manufacturing. No agency services. These aren't features — they're businesses that took years to build.

**The play:** Position GLASS not as "data" but as "the operating system." Data + action + fulfillment. One dashboard.

---

## 2. BATTLE PLAN: GLASS vs HOODIE FEATURE-BY-FEATURE

For every GLASS initiative, here's the explicit competitive calculus:

### 2.1 Price Wire vs Hoodie's Competitive Intelligence

| Dimension | Hoodie | GLASS | Who Wins |
|-----------|--------|-------|----------|
| Scale | 10,000+ dispensaries nationwide | 385+ MA dispensaries (target: 418) | Hoodie nationally, GLASS in MA |
| Data Sources | Menu scraping + POS/ERP partnerships + foot traffic | Cross-platform scraping (Dutchie + WM + Jane + Leafly) + CCC | Different — we cross-reference platforms, they supplement with POS |
| Update Frequency | "Next-day" | Hourly delta checks for watched items, daily full refresh | GLASS faster |
| Price | $1,000-5,000+/mo | Free | GLASS |
| AI Recommendations | None — shows data only | Margin Engine: "Lower Sour D by $3 to gain 12 units/week" | GLASS |
| Cross-Platform Matching | No | Yes (GPID) | GLASS |
| Foot Traffic | Yes (cellphone geofencing) | No | Hoodie |
| Historical Data | 6+ years | Weeks (growing daily) | Hoodie |

**Where we're ahead:** Free, cross-platform matching, AI recommendations, faster updates.  
**Where they're ahead:** Scale, foot traffic, historical depth, POS integrations.  
**How we close the gap:** We don't need national scale — we need 100% MA coverage. Fix the Weedmaps scraper (94% failure rate is catastrophic), add iHeartJane (+50-80 stores), and we hit 95%+ MA coverage. Historical data gap closes by 1 day every day — it's a diminishing advantage.  
**Timeline pressure:** Price Wire must be consumer-facing within 2 weeks. Every day without a live product is a day we're not building the historical data moat.

### 2.2 Threat Radar vs Nothing

Hoodie has zero regulatory intelligence. No CCC filings, no license tracking, no enforcement actions, no municipal meeting parsing. This feature has no Hoodie equivalent and never will — it's MA-specific with no national ROI.

**Structural advantage:** Permanent. CCC data integration is our unfair advantage that Hoodie will never build.  
**Timeline pressure:** Ship within 6 weeks. This is the feature that makes GLASS indispensable to MA operators and has zero competitive response available.

### 2.3 Margin Engine vs Nothing

Hoodie shows data. They don't recommend actions. Their customers (brands) don't need pricing recommendations — they set MSRP. Operators need recommendations. Hoodie's brand-first structure means they'll never build an operator-facing pricing AI because it could recommend pricing that hurts their brand clients' margins.

**Structural advantage:** Semi-permanent. Even if they wanted to build this, recommending lower prices conflicts with their brand customers' interests.  
**Timeline pressure:** Rules-based V1 by Week 12. ML-based V2 by Month 6. The Margin Engine is what converts free users to believers.

### 2.4 Consumer Platform (GLASS Prices) vs High Times E-Commerce

| Dimension | Hoodie/High Times | GLASS Prices | Who Wins |
|-----------|------------------|-------------|----------|
| Consumer Value Prop | "Discover products through editorial content" | "Find the cheapest price near you" | GLASS — clearer, higher intent |
| Business Model | Brand-driven (brands pay for visibility) | Consumer-driven (best price wins) | GLASS for consumers |
| Content Strategy | Editorial articles → embedded product links | Automated price cards + SEO pages + social | Different models |
| Brand Recognition | High Times (50+ years) | Zero (building from scratch) | Hoodie/HT massively |
| MA Depth | National, generic | Every dispensary, every product, every city | GLASS |
| Price Comparison | No explicit price comparison | Core feature — Kayak for cannabis | GLASS |
| Delivery | Pickup only | Delivered integration (license MD1303) | GLASS |
| SEO | Starting from scratch (HT relaunched July 2025) | 385+ dispensary pages + city/category pages from Day 1 | GLASS faster to rank in MA |

**Where we're ahead:** Price comparison (they don't do it), MA depth, delivery, SEO for MA-specific searches, clearer consumer value prop.  
**Where they're ahead:** Brand recognition (High Times is 50 years old), national coverage, content-commerce model is proven.  
**How we close the gap:** We don't fight them on brand. We fight on utility. High Times readers browse. GLASS users search with purchase intent. Different audiences, different moments. We own "cheapest weed near me" searches; they own "what should I try" discovery.  
**What High Times gives them that we need an answer for:** Distribution. 20M+ monthly readers pointed at their platform. Our answer: SEO + social content engine + r/bostontrees community + local press coverage. We build our own audience channel by channel.  
**Timeline pressure:** Consumer site live within 2 weeks. Social content engine running within 1 week. SEO pages generating within 2 weeks. Every day Hoodie/HT doesn't have MA-specific consumer pages is a day we can rank ahead of them.

### 2.5 GPID vs Hoodie's Product Catalog

| Dimension | Hoodie Product Catalog | GLASS GPID | Who Wins |
|-----------|----------------------|-----------|----------|
| Approach | Brand uploads product data → Hoodie matches to menus (brand-side) | Cross-platform fuzzy matching across Dutchie/WM/Jane/Leafly (consumer-side) | Different — complementary approaches |
| Scale | 30M product variants | ~60K prices / ~118K products (growing) | Hoodie by 250x |
| Unique Value | Brands ensure menu accuracy | Consumers compare the same product across stores and platforms | GLASS — nobody else does this |
| Data Quality | ML + human analysts (6 years of refinement) | Fuzzy matching + community validation (brand new) | Hoodie (maturity) |
| Consumer Benefit | "Find this brand near you" | "Find this product at the cheapest price" | GLASS |

**Where we're ahead:** Cross-platform matching (they don't do it), consumer-facing utility.  
**Where they're ahead:** Scale, maturity, brand relationships feeding data.  
**How we close the gap:** Community-powered matching (Section 5). Every user vote on "same product? / different product?" trains our model. Brand data ingestion — let MA brands upload product info to improve GPID. This is a flywheel: more matches → better comparisons → more users → more votes → better matches.  
**Timeline pressure:** GPID V1 (basic fuzzy matching) must ship with the consumer site in Week 2. GPID V2 (community-assisted) by Month 2. GPID V3 (ML-trained on community data) by Month 4.

### 2.6 Hoodie Connect vs GLASS Free Tier

Hoodie Connect is their free retailer program: enhanced exposure and order referrals through High Times. It's their Trojan horse for retailer acquisition.

GLASS's free tier is: full competitive intelligence, AI pricing recommendations, CCC alerts, and consumer traffic.

**Hoodie Connect gives retailers:** Advertising (exposure on High Times).  
**GLASS gives operators:** Intelligence (what to do about your prices, your competitors, your market).

**This is advertising vs analytics. The operator who gets both will value the analytics more.** Exposure is nice. Knowing your competitor dropped prices on your top seller 2 hours ago and getting a recommendation on how to respond — that's survival.

**Timeline pressure:** Monitor Hoodie Connect uptake in MA immediately. If MA dispensaries start signing up, we need to be live with a counter-offer. Set up Google Alerts for "Hoodie Connect Massachusetts" and "High Times Massachusetts dispensary."

---

## 3. GPID — THE NUCLEAR WEAPON

This section exists because GPID is the single most important technical advantage GLASS has. It's not a background feature. It's the centerpiece.

### 3.1 What GPID Actually Is

GPID (GLASS Product ID) is a canonical identifier for every cannabis product in Massachusetts, regardless of how it's listed on any platform. When "Sour Diesel 3.5g by XYZ Brand" appears as:
- "Sour D 1/8th - XYZ" on Dutchie  
- "XYZ Sour Diesel Flower 3.5 grams" on Weedmaps  
- "Sour Diesel (eighth) by XYZ Brand" on iHeartJane  
- "XYZ - Sour Diesel $45" on the dispensary's custom website  

GPID recognizes these as the same product and assigns one ID. This enables:
- **Price comparison across stores** (Kayak for cannabis)
- **Price comparison across platforms at the same store** (catch platform-specific pricing)
- **Product tracking over time** (price history for a product, not a listing)
- **Accurate category/brand/strain analytics** (cleaned data, not raw scraper noise)

### 3.2 Why Nobody Else Has This

**Hoodie's Product Catalog** works from the brand side — brands upload canonical product data, and Hoodie matches it to menu listings. This requires brand cooperation and doesn't catch listings the brand doesn't know about or hasn't claimed.

**GPID works from the platform side** — we scrape every platform, normalize the data, and match algorithmically + with community validation. No brand cooperation required. No single platform dependency.

**Headset** has POS transaction data, which is already normalized by the POS system. They don't need to match across platforms because they're inside the POS.

**Dutchie, Weedmaps, Leafly, iHeartJane** each only see their own listings. They have no incentive to cross-reference with competitors.

**The gap exists because nobody else scrapes ALL platforms and matches products across them.** This is uniquely possible for GLASS because cross-platform scraping is our core architecture.

### 3.3 How GPID Compounds

**The Top 500 → Total Catalog progression:**

```
Week 1: Top 500 hand-verified SKUs across Dutchie + WM
  → 100% match accuracy (human-verified, zero false positives)
  → 500 products × ~200 stores = ~5,000 price comparison data points
  → Enough for compelling social content and MVP search
  → Positioning: "We track the 500 most popular products in MA"

Month 2: Top 500 + 200 community-verified expansions = 700 products
  → Community votes ("Same product?") validate new matches
  → Operator corrections add high-confidence labels
  → False positive rate: <2% on verified catalog
  → Fuzzy matching runs in BACKGROUND on remaining ~117K products
  → Matches above 95% confidence auto-added to catalog; rest queued for human/community review

Month 3-4: 1,000+ verified products, fuzzy matching pipeline maturing
  → Brand data ingestion adds canonical product info (brand-confirmed matches)
  → Every community vote = training data for the ML model
  → ~80% auto-match rate on new products entering the system

Month 6: 2,500+ verified products covering ~85% of consumer searches
  → ML model trained on 5,000+ labeled pairs
  → New products auto-matched with >92% confidence
  → GPID IS the canonical product catalog for MA cannabis

Month 12: Full catalog (5,000+ products), continuous auto-expansion
  → Brands reference GPIDs in marketing
  → Operators use GPIDs in inventory management
  → Consumers search by GPID without knowing it
  → New products auto-matched within hours of appearing on any platform
```

Each new platform added increases the value exponentially: 2 platforms = 1 comparison axis. 3 platforms = 3 axes. 4 platforms = 6 axes. The matching gets better because more data points per product = more features for the model.

**Why Top 500 first instead of "match everything":** A consumer who sees one bad match (1g pre-roll matched with 3.5g flower) loses trust permanently. A consumer who searches for a product not yet in the catalog sees "We don't track this product yet — suggest it?" and feels the platform is honest. **Curated accuracy > noisy breadth.** Every day.

### 3.4 How GPID Creates Lock-In Hoodie Can't Replicate

1. **Community training data is proprietary.** Every "same product" / "different product" vote from MA users is training data. Hoodie would need to build their own community feedback system, get MA users to use it, and accumulate months of votes. By then, our model is 6+ months ahead.

2. **Operator corrections create truth labels.** When a dispensary claims their GLASS page and corrects product names/categories, that's gold-standard training data. Hoodie Connect doesn't give operators a correction mechanism — it's a listing, not an intelligence tool.

3. **GPID becomes the lingua franca.** If operators, brands, and consumers in MA all reference the same GPID for a product, switching to any other system means losing that shared vocabulary. This is the HTTP protocol effect — it's valuable because everyone uses it.

4. **Cross-platform is the architecture, not a feature.** To replicate GPID, you need to scrape all platforms. Hoodie could do this technically, but their Product Catalog is built on brand-side ingestion. Retrofitting cross-platform matching onto a brand-ingestion system is a fundamental architecture change.

### 3.5 GPID → Consumer Experience

Consumers don't know or care about GPIDs. They care about:

- **"Is this the same product?"** — Yes, GPID confirmed. Same brand, same strain, same weight. Different price.
- **"Where's the cheapest?"** — GPID shows the same product at every store that carries it, sorted by price + distance.
- **"Has the price changed?"** — GPID tracks the product, not the listing. Price history is for the actual product, not a string on a menu.
- **"Is the THC% accurate?"** — GPID links to CCC lab testing data. The menu says 32%. The lab says 24%. GLASS shows both.
- **"What's similar?"** — GPID clusters related products (same strain, different brands). "You searched for Blue Dream — here are all Blue Dreams in MA, cheapest first."

**The GPID-powered consumer experience is what makes GLASS Prices fundamentally different from Weedmaps/Leafly/High Times.** They show menus. We show product truth.

### 3.6 GPID Development Sequence

| Phase | What | When | Catalog Size | False Positive Rate |
|-------|------|------|-------------|-------------------|
| **V0** | **Top 500 hand-verified SKUs** — query DB for most ubiquitous products, manually verify every cross-platform match | **Week 1 (STEP 0)** | **500 products** | **0% (human-verified)** |
| V1 | Fuzzy matching pipeline running in BACKGROUND on remaining ~117K products. High-confidence matches (>95%) queued for quick human review. Low-confidence matches held. | Week 2-3 | 500 verified + pipeline building | 0% on verified catalog |
| V1.5 | + Rule-based overrides (known brand aliases, weight format standardization). Community "Suggest a product" flow for unlisted items. | Week 3-4 | 600-700 | <1% |
| V2 | + Community "Same product? / Different product?" voting. Operator corrections. Pipeline auto-promotes high-confidence matches reviewed by community. | Month 2 | 1,000+ | <2% |
| V2.5 | + Brand data ingestion (MA brands upload canonical product info) | Month 3 | 1,500+ | <2% |
| V3 | + ML model trained on community + operator + brand labeled pairs | Month 4-5 | 2,500+ | <2% |
| V4 | + Auto-matching for new products, continuous retraining | Month 6+ | 5,000+ | <1% |

**Critical rule: The consumer-facing catalog only shows verified matches.** Fuzzy matching runs in the background to SUGGEST matches, never to DISPLAY them. Every consumer-visible price comparison has been verified by human, operator, or high-confidence community consensus.

---

## 4. CONSUMER STRATEGY (HOODIE-AWARE)

### 4.1 The Core Thesis: We Win on Utility, They Win on Brand

Hoodie/High Times consumer play: "Read about cannabis → discover products → buy from a nearby store."  
GLASS consumer play: "Search for a specific product → find the cheapest price → buy from the closest/cheapest store."

These serve different consumer moments:
- **Discovery moment** (I don't know what I want): High Times wins — editorial content, brand storytelling, curated selections.
- **Purchase moment** (I know what I want, I want the best price): GLASS wins — cross-platform price comparison, distance-optimized results, price alerts.

**We don't fight for the discovery moment.** We own the purchase moment. The purchase moment is higher-intent, higher-conversion, and more defensible through data (GPID, price history, accuracy scoring).

### 4.2 What We Build (Consumer Product)

**GLASS Prices** — one product, one URL, one mission.

**Layer 1: Search + Compare** (the core utility)
- Consumer enters product + location → every store carrying it, sorted by price + distance
- Powered by GPID for cross-platform matching
- No login. Zero friction. Mobile-first.
- **Anti-Hoodie:** Hoodie/HT doesn't do explicit price comparison. They show products from stores. We compare prices across stores. Fundamentally different UX.

**Layer 2: Auto-Generated SEO Pages** (the traffic machine)
- 385+ dispensary pages with full menus, price rankings, competitor comparisons
- Product pages (GPID-powered): same product across all stores, sorted by price
- City/category pages: "Best flower prices in Boston today"
- **Anti-Hoodie:** High Times just relaunched July 2025. Their SEO authority is rebuilding. We can rank for MA-specific searches faster than they can because we're creating hundreds of thousands of hyperlocal, data-rich pages that Google loves. They're creating editorial. We're creating structured data.

**Layer 3: Price Alerts** (the retention hook)
- "Tell me when any 1/8 drops below $30 within 10 miles of Somerville"
- SMS + email delivery
- **Anti-Hoodie:** Hoodie doesn't offer consumer price alerts. Their consumer product is browse-based, not alert-based.

### 4.3 Social Content Engine (Hoodie-Aware)

Hoodie hasn't invested in social content or SEO for consumer acquisition. Their consumer distribution is High Times editorial → embedded shopping links. This is a massive gap we can exploit.

**What we produce (automated daily):**

| Format | Example | Anti-Hoodie Angle |
|--------|---------|-------------------|
| Price Gap Cards | "Same cart: $28 vs $54, 3 miles apart" | Hoodie doesn't produce shareable consumer content |
| City Rankings | "Best $30 eighth in Boston right now" | Hoodie has no city-specific MA content |
| Price Drop Alerts | "[Strain] dropped from $55→$38 at [Store]" | Hoodie doesn't track or share price drops |
| Weekly Roundups | "Top 10 price drops this week in MA" | Hoodie publishes enterprise reports, not consumer content |
| THC Accuracy Exposés | "We checked THC labels at every MA dispensary" | Hoodie has NO lab data integration |
| Data Visualizations | "MA weed prices dropped 73% since 2020" | Hoodie doesn't produce MA-specific data journalism |

**Distribution channels ranked by priority:**
1. **X (Twitter)** — safest for cannabis, data-forward audience
2. **SEO** — long game, compounding, algorithm-proof
3. **Reddit (r/bostontrees)** — 32K cannabis consumers, data-hungry
4. **TikTok/Reels** — high reach, frame as market data not product promotion
5. **SMS/Email** — owned audience, no algorithm dependency
6. **Instagram** — riskiest for cannabis content, treat as expendable

**What Hoodie can't replicate from a national VC position:**
- **Local voice.** We can say "that dispensary on Main Street in Worcester" and consumers know exactly which one. Hoodie is a Chicago company talking about 10,000 dispensaries.
- **Shareable local content.** A price comparison card for Boston dispensaries goes viral in Boston group chats. A national product listing doesn't.
- **Reddit credibility.** r/bostontrees knows locals. A post from "@glassintel" that names specific stores and prices is credible. A post from "Hoodie Analytics, Chicago" is advertising.

### 4.4 How We Answer the High Times Advantage

High Times gives Hoodie: brand recognition, editorial content driving commerce, millions of monthly readers.

Our answer is not to replicate High Times. It's to build something High Times can't be:

| High Times Advantage | Our Counter |
|---------------------|-------------|
| 50 years of brand recognition | MA-specific data authority + grassroots trust from day 1 |
| Millions of monthly readers | SEO: 100K+ indexable MA-specific pages that rank for purchase-intent searches HT doesn't optimize for |
| Editorial → commerce model | Search → compare → buy model (higher intent, higher conversion) |
| Content distribution at scale | Social content engine: 2-3 automated posts/day + weekly newsletter + Reddit |
| High Times Local (Denver, Phoenix, Chicago planned) | If/when they add Boston: we're already the local MA source with 6+ months of data and community trust |

**Key timing:** High Times Local launches in Denver, Colorado Springs, and Phoenix in March 2026, with plans for Chicago, LA, NYC, Detroit. **Boston is not on the list yet.** This gives us time. But it's coming. We need to be the unassailable MA cannabis data source before High Times Local reaches Boston.

---

## 5. COMMUNITY DATA MOAT (ANTI-HOODIE)

### 5.1 The Wikipedia vs Encyclopedia Britannica Play

Hoodie's data is Encyclopedia Britannica: expert-curated, brand-ingested, expensive, authoritative, centrally controlled, and updated on their schedule.

GLASS's data becomes Wikipedia: community-corrected, operator-verified, free, transparent, continuously updated, and improving every time someone uses it.

**Wikipedia won.** Not because it was more accurate on day 1 (it wasn't), but because community corrections compound and centralized editorial doesn't scale.

### 5.2 What Community Data Looks Like

**Consumer corrections:**
- "Wrong price" reports (the #1 use case — consumer at the store sees $35, GLASS shows $45)
- "Product doesn't exist anymore" (stale listings)
- "Wrong category" (parser misread)
- "Same product / Different product" votes (GPID training)
- "Was this helpful?" implicit quality signals

**Operator corrections (after claiming their page):**
- Inline price editing (one-click fix)
- Bulk menu upload (CSV/Excel → diff → apply)
- Store info updates (hours, address, status)
- "Product discontinued" toggles
- "Request immediate re-scrape" button

**Why Hoodie can't buy this data:**
1. It requires a consumer audience submitting corrections. Hoodie doesn't have MA consumers using their platform.
2. It requires operators engaging with their pages. Hoodie Connect is a listing, not a dashboard with correction tools.
3. The trust scoring system (T0–T4 tiers, accuracy tracking, confidence algorithms) takes months to calibrate with real human behavior data.
4. Community-labeled GPID pairs are training data for our product matching model. This is proprietary and cumulative.

### 5.3 Moat Maturation Timeline

| Timeframe | Moat Strength | What's Happening | Hoodie's Position |
|-----------|---------------|-------------------|-------------------|
| Month 1-2 | **Weak** | Few corrections, manual review. Data quality = scraper quality. | Not paying attention to MA. |
| Month 3-6 | **Growing** | 500+ corrections, auto-apply live. 10+ operators claiming pages. Error rate dropping. Scraper frequency optimized from feedback. | Still not paying attention. |
| Month 6-12 | **Moderate** | 2,000+ corrections. 50+ claimed pages. GPID model trained on 500+ community-labeled pairs. Consumer trust visibly higher than alternatives. | Might notice us. Can't replicate 6 months of community data. |
| Year 1-2 | **Strong** | Community corrections exceed scraper errors. GPID model trained on thousands of pairs. Dispensaries depend on GLASS for pricing narrative. | Would need 12+ months to replicate even if they tried. |
| Year 2+ | **Very Strong** | Self-reinforcing. Data quality gap widens over time. | Moat is permanent. |

### 5.4 When Is the Moat Deep Enough?

The moat becomes meaningful when:
- **50+ operators have claimed pages** — they're invested in the platform and won't switch easily
- **GPID accuracy exceeds 90%** — consumer-facing price comparison is trustworthy
- **Community corrections > scraper errors** — the community is a data source, not just a correction layer
- **Local brands reference GLASS data** — "Check our prices on GLASS" appears in dispensary marketing

**Estimated timeline to meaningful moat: 6-9 months.** This aligns perfectly with the Hoodie threat window. If we build meaningful community engagement in 6 months, Hoodie can't replicate it by entering MA in month 7.

---

## 6. VERTICAL INTEGRATION — THEIR BLIND SPOT

Hoodie Analytics is a data company. They sell intelligence. That's it. The value chain ends at "here's what's happening." GLASS is a data company connected to an action layer connected to a fulfillment layer. This integration is our biggest structural advantage after GPID.

### 6.1 The Integration Map

```
INTELLIGENCE          RECOMMENDATION         ACTION              FULFILLMENT
─────────────         ──────────────         ──────              ──────────
Price Wire      →     Margin Engine     →    Price Change    →   (operator does it)
Threat Radar    →     Competitive Alert →    Strategic Move  →   Roviq Agency ($2,500/mo)
Slow Inventory  →     Incentive Rec     →    Launch Spiff    →   Cue (brand-funded, $0 to operator)
No Delivery     →     Delivery Rec      →    Toggle On       →   Delivered (MD1303, 15% GMV)
Margin Gap      →     Product Rec       →    New Product     →   AC Toll Processing (per-unit)
Consumer Demand →     Demand Report     →    Menu Adjust     →   (operator does it)
```

Hoodie can do the first column. They have pieces of the second. They have nothing in columns 3 and 4.

### 6.2 How We Weaponize Each Integration

**Delivered (Delivery-as-a-Service)**
- License MD1303 is exclusive social equity until 2029
- Only ~27 delivery operators in all of MA — extremely limited licensing
- "Toggle Delivery" from GLASS dashboard for specific zip codes
- **Anti-Hoodie weapon:** Hoodie's consumer platform is pickup-only. When a GLASS consumer finds the best price AND can get it delivered, Hoodie's pickup-only experience loses. This is especially powerful for price-sensitive consumers who won't drive 30 minutes to save $10 but will pay $5 for delivery.
- **Revenue:** 15% of GMV through delivery

**Cue (Brand-Funded Budtender Incentives)**
- Brands pay to incentivize dispensary staff to recommend their products
- Operators pay $0 — it's free revenue for them
- Creates a data stream Hoodie doesn't have: which products are being promoted, how staff responds, what consumers buy when recommended
- **Anti-Hoodie weapon:** Hoodie sells intelligence TO brands. Cue sells brand access TO operators' staff. We're on the opposite side of the same transaction — and our side is where the shelf decisions happen.
- **Revenue:** Brand subscriptions ($500-5,000/mo) + per-spiff fees

**AC Toll Processing (White-Label Manufacturing)**
- Operators with margin gaps in specific categories can fill them with white-label products
- "Your edible margins are 15% below market. AC can produce a white-label edible at $X/unit."
- **Anti-Hoodie weapon:** Hoodie identifies problems. GLASS identifies problems AND manufactures solutions. Literally.
- **Revenue:** Per-unit processing fee + referral commission

**Roviq (Agency Services)**
- GLASS Score creates the anxiety ("you're a 58/100"). Roviq sells the fix.
- Pricing strategy, menu optimization, content, social, full marketing retainer
- **Anti-Hoodie weapon:** Hoodie has "Managed Services" — embedded analysts for MSOs at enterprise prices. Roviq serves independent operators at $2,500/mo. Different market.
- **Revenue:** Retainer ($2,500+/mo per client)

### 6.3 The Combined Anti-Hoodie Pitch

To an MA operator:

> "Hoodie shows you data and charges $1,000+ a month. GLASS shows you data for free, tells you what to do about it, and lets you act on it from one dashboard — turn on delivery, launch a brand-funded incentive, get white-label products manufactured, or hire us to fix your marketing. What does Hoodie do after they show you the problem?"

This pitch is devastatingly effective because it's true. Hoodie's strength (data breadth) becomes a weakness when compared to GLASS's depth + action.

---

## 7. THE 6-12 MONTH WINDOW

### 7.1 Why We Have 6-12 Months

Hoodie will not enter MA seriously in the near term because:

1. **VC pressure is on national growth.** Their Series A ($5M, Measure 8 Partners) demands scaling across all legal states, not going deep in one.
2. **High Times partnership just launched (Dec 2025).** Their focus for Q1-Q2 2026 is making the High Times integration work nationally.
3. **High Times Local is launching in Denver/Phoenix/Chicago first.** Boston isn't on the announced list.
4. **MA is ~4% of their coverage.** Building MA-specific features (CCC integration, local alerts) has zero ROI at their scale.
5. **They have no MA team member.** No boots on the ground means no local relationships.
6. **Their CEO's playbook is national.** Wes Shepherd built Channel IQ as a national e-commerce intelligence platform. He sold it to Numerator (national). The playbook is breadth, not depth.

### 7.2 What Could Accelerate Their MA Entry

**Watch for these trigger signals:**
- Hoodie hires someone in Boston/MA (LinkedIn alert: set it up)
- Hoodie starts marketing specifically to MA operators (Google Alerts)
- High Times Local announces a Boston/MA edition
- Hoodie Connect starts signing up MA dispensaries aggressively
- Hoodie publishes MA-specific reports or data
- Hoodie attends NECANN or MA-specific cannabis events
- A major MA MSO becomes a visible Hoodie client

**If any of these happen: execute the Emergency Playbook (Section 11).**

### 7.3 The Timeline — What We Must Build and When

#### Month 0-3: ESTABLISH (Before Hoodie Notices Us)

The goal is to be invisible to Hoodie and indispensable to MA.

**Irreversible advantages to build:**
1. Consumer site live with 385+ dispensary pages indexed by Google
2. Social following of 10K+ across platforms (audience Hoodie can't poach)
3. 25+ operators using GLASS free tier weekly
4. 5+ dispensaries claimed their page (switching cost created)
5. GPID V1 matching 60%+ of cross-platform products
6. Newsletter with 2,000+ MA operator/consumer subscribers
7. First community corrections flowing → data quality flywheel started
8. r/bostontrees recognizes GLASS as the price comparison source

**Revenue target:** $0-$400/mo (growth mode, not revenue mode)

#### Month 3-6: ENTRENCH (Build Switching Costs)

The goal is to make GLASS the default that operators check every morning.

**Irreversible advantages to build:**
1. 75+ operators on free tier, 10+ paying for premium ($199/mo claimed pages)
2. 25+ dispensaries claimed pages with correction history
3. GPID accuracy at 80%+ with community validation
4. Consumer site at 25K+ monthly visitors
5. 3-5 Cue brand pilots live (revenue + data moat)
6. Delivered integration tested (delivery toggle functional)
7. THC Accuracy Score published → press coverage → CCC credibility
8. First Roviq agency clients from GLASS referrals (2-3 at $2,500/mo)

**Revenue target:** $6,500-$11,000/mo

**What "winning" looks like at Month 6:**
- GLASS is the first place 50+ MA operators check pricing data
- Consumers in Boston/Worcester/Cambridge associate GLASS with cannabis prices
- 5+ MA brands are paying through Cue or premium listings
- Hoodie Connect has minimal MA traction because GLASS already has the operators
- Our community correction data gives us higher accuracy than any scraper-only competitor

#### Month 6-12: DOMINATE (Make the Moat Uncrossable)

The goal is to make it too late for Hoodie to compete in MA.

**Irreversible advantages to build:**
1. 100+ operators on free tier, 20+ paying for premium
2. 50+ claimed pages with months of correction history
3. GPID accuracy at 92%+ (community + ML model)
4. Consumer site at 50K-75K+ monthly visitors
5. 10+ Cue brands active
6. Delivery operational through Delivered spoke
7. GLASS Score is referenced by operators and consumers as THE quality metric
8. First expansion planning: CT, ME, or RI

**Revenue target:** $15,000-$25,000/mo

**What "winning" looks like at Month 12:**
- GLASS is synonymous with cannabis pricing in MA (like Zillow for homes)
- 100+ operators would actively resist switching to Hoodie because of accumulated data, corrections, community trust
- GPID is the de facto product catalog for MA cannabis
- Revenue is diversified across 4+ streams (premium pages, brand placement, Cue, agency)
- We're expanding to adjacent states using the same playbook
- If Hoodie enters MA now, they're 12 months of community data behind and facing entrenched relationships

### 7.4 Milestone Check-Ins (Are We On Track?)

| Week | Milestone | On Track Signal | Off Track Signal |
|------|-----------|-----------------|------------------|
| 2 | Consumer site live | Live, 1K visitors | Not shipped, 0 visitors |
| 4 | Social engine running | 2,500 followers, 5K visitors | <500 followers, <1K visitors |
| 8 | Operator engagement | 25+ free users, 5 claimed pages | <10 users, 0 claims |
| 12 | Revenue signal | $1,800/mo, 15+ claimed pages | $0, <5 claims |
| 16 | Community data | 500+ corrections, auto-apply working | <100 corrections |
| 20 | Brand revenue | 3+ Cue pilots, $4K/mo | 0 Cue brands |
| 24 | Market position | 50K visitors, 75+ operators, $11K/mo | <10K visitors, <25 operators |
| 36 | Dominance | 100+ operators, $20K/mo, CT expansion planned | <50 operators, <$10K/mo |
| 48 | Moat built | GPID at 92%+, community corrections > scraper errors | GPID stalled, no community |

---

## 8. REVENUE THAT SURVIVES HOODIE

### 8.1 Revenue Streams Rated by Hoodie-Resistance

| Revenue Stream | Annual Potential | Can Hoodie Undercut? | Hoodie-Proof Rating |
|---------------|-----------------|---------------------|-------------------|
| **Cue (brand incentives)** | $115K+ | No — they have no incentive platform and no in-store relationships | ⭐⭐⭐⭐⭐ |
| **Delivered (delivery)** | $90K+ | No — they have no delivery license, no fulfillment capability | ⭐⭐⭐⭐⭐ |
| **AC Toll Processing** | $250K+ | No — they have no manufacturing capability | ⭐⭐⭐⭐⭐ |
| **Roviq Agency** | $120K+ | No — they do "embedded analysts" for MSOs, not SMB agency work | ⭐⭐⭐⭐ |
| **Premium Claimed Pages** | $24K+ | Yes — they could offer free or cheap store dashboards through Hoodie Connect | ⭐⭐⭐ |
| **Brand Placement (Cue Lite)** | $48K+ | Partially — High Times already offers brand visibility. But ours targets MA specifically. | ⭐⭐⭐ |
| **Consumer Demand Reports** | $36K+ | Yes — if they have MA consumer traffic, they have demand data too | ⭐⭐ |
| **Margin Engine Pro** | $48K+ | Yes — if they ever build AI recommendations (unlikely with brand-first model) | ⭐⭐⭐ |

### 8.2 If Hoodie Enters MA Aggressively — What Survives

**Survives (Hoodie-proof):**
- Cue ($115K) — requires physical in-store relationships and a brand incentive platform Hoodie doesn't have
- Delivered ($90K) — requires MA delivery license Hoodie doesn't have
- AC Toll Processing ($250K) — requires manufacturing Hoodie doesn't have
- Roviq Agency ($120K) — SMB-focused, relationship-driven, local

**Total Hoodie-proof revenue potential: $575K/yr**

**At risk (Hoodie could compete):**
- Premium Claimed Pages ($24K) — Hoodie Connect offers something similar for free
- Brand Placement ($48K) — High Times offers national brand visibility
- Consumer Demand Reports ($36K) — if they have consumer traffic, they have demand data

**Total at-risk revenue: $108K/yr**

**Survival rate: $575K / $683K = 84% of revenue is Hoodie-proof.**

### 8.3 Revenue Sequencing (Optimized for Hoodie Defense)

Build Hoodie-proof revenue first:

| Priority | Revenue Stream | When | Why This Order |
|----------|---------------|------|----------------|
| 1 | Premium Claimed Pages ($199/mo) | Month 2-3 | Fastest to ship, creates operator lock-in, builds claimed-page moat |
| 2 | Brand Placement / Cue Lite ($500-2K/mo) | Month 3-4 | Requires consumer traffic (built in Month 1-2) |
| 3 | Roviq Agency ($2,500+/mo) | Month 3-4 | Inbound from GLASS Score anxiety, zero outbound sales |
| 4 | Cue Full ($500-5K/mo per brand) | Month 5-6 | Requires operator network + brand relationships |
| 5 | Delivered Integration (15% GMV) | Month 6-8 | Requires technical integration + operational readiness |
| 6 | AC Toll Processing (per-unit) | Month 8-12 | Requires operator demand + manufacturing pipeline |

---

## 9. EXECUTION PLAN — WEEK BY WEEK, FIRST 90 DAYS

Every task has an owner: **Randy** (human decisions, relationships, community, review) or **AI** (code, content, data, automation).

### WEEK 1 (Feb 14-20): FOUNDATION

| Day | Task | Owner | Anti-Hoodie Purpose |
|-----|------|-------|---------------------|
| 1 | Create @glassintel accounts on X, TikTok, Instagram, YouTube | Randy | Claim namespace before anyone else |
| 1 | Set up Google Alerts: "Hoodie Analytics Massachusetts," "Hoodie Connect dispensary," "High Times Boston dispensary" | Randy | Early warning system |
| 1-2 | Fix Weedmaps scraper (94% failure rate) | AI | Need 95%+ MA coverage to beat Hoodie's generic national view |
| 1-3 | Build consumer search MVP: search → price comparison results, mobile-first | AI (Kimi K2.5 frontend, Codex 5.3 backend) | Ship before Hoodie has any MA-specific consumer presence |
| 1-3 | Build content generation pipeline: DB → price card image templates (6 formats) | AI | Automated content engine Hoodie doesn't have |
| 2-3 | GPID V1: fuzzy matching across Dutchie + Weedmaps | AI (Codex 5.3) | The nuclear weapon — nobody else has cross-platform matching |
| 3-5 | Generate first 30 social posts from live GLASS data | AI | Fill the MA cannabis content vacuum before Hoodie's social team wakes up |
| 5-7 | Deploy consumer site at prices.glassintel.xyz | AI | Plant the flag |
| 7 | Randy reviews first content batch, calibrates tone | Randy | Quality gate |
| 7 | Begin posting: 2-3/day X, 1-2/day TikTok/Reels | AI (automated scheduling) | Start building the audience moat |

**Week 1 Exit Criteria:**
- [ ] Consumer site live
- [ ] Weedmaps scraper at <20% failure rate
- [ ] GPID V1 running (even if noisy)
- [ ] Social accounts posting daily
- [ ] Google Alerts monitoring Hoodie

### WEEK 2 (Feb 21-27): SEO MACHINE

| Day | Task | Owner | Anti-Hoodie Purpose |
|-----|------|-------|---------------------|
| 8-10 | Generate 385+ auto-dispensary pages (full menu, competitor comparison, price ranking) | AI | Create 385 pages Hoodie doesn't have — each one a potential Google landing |
| 8-10 | SEO: meta tags, Open Graph, structured data (Product schema), sitemap | AI | Rank for MA cannabis searches before High Times Local even considers Boston |
| 11-12 | Generate 50+ city/category landing pages | AI | "Best flower prices in Boston" → GLASS, not Hoodie |
| 13 | Seed r/bostontrees: "I compared prices at every dispensary in MA — here's what I found" | Randy | Community trust that Hoodie can never fake from Chicago |
| 14 | Fix Dutchie scraper failures (40/235 failing) | AI | Coverage completeness |
| 14 | CHECKPOINT: social engagement, site traffic, Reddit response | Randy | Validate thesis |

**Week 2 Exit Criteria:**
- [ ] 385+ dispensary pages indexed
- [ ] 50+ city/category pages indexed
- [ ] 1,000+ site visitors
- [ ] Reddit post live and engaging
- [ ] Dutchie scraper at <10% failure rate

### WEEK 3-4 (Feb 28 - Mar 13): HOOKS + iHEARTJANE

| Day | Task | Owner | Anti-Hoodie Purpose |
|-----|------|-------|---------------------|
| 15-17 | Build Price Alert system (email + SMS via Twilio) | AI | Retention mechanism Hoodie doesn't offer consumers |
| 18-20 | Build "Claim Your Page" flow for dispensary operators | AI | Create switching costs — once claimed, operator invested in GLASS |
| 18-20 | Add price history charts to all pages | AI | Historical data moat starts growing every day |
| 18-20 | Build iHeartJane scraper (API is semi-public, +50-80 new stores) | AI | Push to 95%+ MA coverage, more cross-platform GPID matches |
| 21-23 | Launch "The MA Weed Report" consumer newsletter | AI + Randy curates | Owned audience channel, algorithm-proof |
| 24-26 | Deploy "⚑ Wrong price?" feedback button on all prices | AI | Begin community correction flywheel (anti-Hoodie moat) |
| 27-28 | Add "Near Me" geolocation mode | AI | Mobile UX advantage |
| 28 | CHECKPOINT: alerts, claims, newsletter subs, social growth | Randy | Validate retention |

**Week 4 Exit Criteria:**
- [ ] Price Alerts live (200+ subscribers)
- [ ] "Claim Your Page" flow live (5+ claim requests)
- [ ] iHeartJane scraper running (+50 new stores)
- [ ] Newsletter launched (500+ subscribers)
- [ ] Feedback system collecting corrections (20+ in first week)
- [ ] Social followers: 2,500+

### MONTH 2 (Mar 14 - Apr 10): MONETIZE + GPID V2

| Week | Task | Owner | Anti-Hoodie Purpose |
|------|------|-------|---------------------|
| 5-6 | Build GLASS Score (5-component: price competitiveness, selection, freshness, stability, THC accuracy) | AI | Unique metric — Hoodie has nothing like this. Creates dispensary FOMO. |
| 5-6 | Build premium "Claimed Page" features: analytics, corrections, deal highlighting ($199/mo) | AI | First revenue stream + operator lock-in |
| 5-6 | GPID V2: add community "Same product? / Different product?" voting | AI | Nuclear weapon gets community fuel |
| 7-8 | Build Product Finder (Virtual Budtender) — quiz → matches across ALL stores by price | AI | Consumer experience Hoodie can't match (requires GPID) |
| 7-8 | Launch THC Accuracy Score: CCC lab data vs menu claims | AI | **THE PRESS PLAY.** Consumer protection angle gets Boston Globe/MassLive coverage. Hoodie has no lab data. |
| 7-8 | Press pitch: "We analyzed THC labels at every MA dispensary. Here's what we found." | Randy | Earned media = free audience, positions GLASS as trusted data authority |
| 8 | CHECKPOINT: premium subs, GLASS Score reception, GPID V2 accuracy | Randy | Validate monetization |

**Month 2 Exit Criteria:**
- [ ] GLASS Score live on all dispensary pages
- [ ] Premium claimed pages: 3-5 paying ($199/mo)
- [ ] GPID V2 collecting community votes
- [ ] THC Accuracy analysis complete and published
- [ ] At least 1 press pitch sent
- [ ] Site: 25K monthly visitors
- [ ] Social: 10K followers
- [ ] Newsletter: 2K subscribers

### MONTH 3 (Apr 11 - May 13): BRAND REVENUE + MOAT DEEPENING

| Week | Task | Owner | Anti-Hoodie Purpose |
|------|------|-------|---------------------|
| 9-10 | Launch Brand Placement pilot (Cue Lite): featured products in search results ($500-2K/mo) | AI + Randy outreach | Revenue stream Hoodie can't undercut (they don't have MA consumer traffic) |
| 9-10 | Build Consumer Demand Report for dispensaries ($299/mo) | AI | Data product only possible with consumer audience |
| 9-10 | Outreach to dispensaries in popular GLASS posts: "Your page gets X visitors, claim it" | Randy | Convert attention into engagement |
| 11-12 | Build Weekly MA Price Index (public data, media-citable) | AI | Become the source media cites. Hoodie doesn't produce MA-specific reports. |
| 11-12 | Approach CCC with THC accuracy findings | Randy | Regulatory credibility play. Positions GLASS as data partner to MA regulators. Hoodie won't bother with one state's regulator. |
| 11-12 | GPID V2.5: Brand data ingestion — let MA brands upload canonical product info | AI | Brands feed GPID accuracy, creating investment and lock-in |
| 12 | Begin Cue full-stack design: brand portal, budtender interface, reporting | AI | Hoodie-proof revenue stream in development |
| 13 | FINAL 90-DAY CHECKPOINT | Randy | Go/no-go on Month 4-6 plan |

**Month 3 Exit Criteria:**
- [ ] Brand Placement generating first revenue ($800+/mo from 1-2 brands)
- [ ] 75+ dispensaries claimed pages
- [ ] 10-15 premium subscribers
- [ ] Weekly Price Index publishing
- [ ] CCC engagement attempted
- [ ] At least 1 media placement
- [ ] Site: 50K-75K monthly visitors
- [ ] Revenue: $3,000-$8,000/mo
- [ ] GPID accuracy: 80%+

---

## 10. WIN CONDITIONS & KILL CRITERIA

### 10.1 What Victory Looks Like

**6-Month Victory:** GLASS is the default pricing intelligence tool for 50+ MA operators. Consumers search "best weed prices near me" and find GLASS. 5+ brands pay for placement or Cue. Revenue covers operating costs. Hoodie Connect has minimal MA traction. Local press cites GLASS data.

**12-Month Victory:** GLASS is synonymous with MA cannabis pricing. 100+ operators. 50K+ monthly consumer visitors. $20K+/mo revenue. GPID is the de facto product catalog. Community corrections exceed scraper errors. Expansion to CT or ME in progress. If Hoodie enters MA, they face 12 months of accumulated community data, operator relationships, and consumer trust.

**Endgame (18+ months):** Three scenarios:
1. **MA Fortress → Regional Expansion (preferred):** Dominate MA, replicate playbook in CT/ME/NH/NJ/NY. Each state gets local depth. GLASS becomes "the local operator intelligence platform." Acquisition target at $5-15M.
2. **Consumer Platform Wins:** Consumer traffic becomes the moat. Brands pay for visibility. National expansion of consumer play. Direct competition with Hoodie/HT at scale.
3. **Data Partnership:** Hoodie provides national benchmarks through GLASS's interface. GLASS provides MA depth Hoodie doesn't have. Co-branded product. Best of both worlds.

### 10.2 Kill Criteria — When to Pivot

| Signal | Timeline | Decision |
|--------|----------|----------|
| <500 site visitors after 2 weeks of social posting | Week 3 | Content strategy is wrong. Audit and try Reddit-only. |
| <2,000 visitors after 4 weeks | Week 5 | Consumer thesis may be wrong. Test B2B-first pivot. |
| <5% alert opt-in rate among visitors | Week 4 | Value prop isn't compelling. Test different framing. |
| 0 dispensary claims after 8 weeks | Week 9 | Consumer traffic isn't creating B2B pressure. Reassess. |
| <10,000 monthly visitors after 90 days | Week 13 | Strategy isn't working at needed scale. Consider different market or B2B-first. |
| Hoodie Connect signs 50+ MA dispensaries before Month 6 | Any time | Execute Emergency Playbook (Section 11) immediately. |
| Data accuracy below 85% (consumer reports) | Any time | Fix pipeline before adding features. Trust is everything. |

### 10.3 What Would Kill GLASS Entirely

1. **Scraper data is too inaccurate for consumers.** If we can't show accurate prices, nothing else matters. The Weedmaps 94% failure rate must be fixed before launch.
2. **MA consumers don't comparison-shop for cannabis.** Unlikely given 73% price collapse and thin margins, but possible.
3. **Hoodie launches a free MA-specific operator tier with CCC integration.** Extremely unlikely (wrong economics, wrong strategy) but would be devastating.
4. **Dutchie or Weedmaps build cross-platform price comparison.** They won't — it exposes their platform's pricing disadvantages.

---

## 11. IF HOODIE ENTERS MA — EMERGENCY PLAYBOOK

### Trigger Signals (Monitor Weekly)

- [ ] Hoodie hires someone in Boston/MA (LinkedIn)
- [ ] Hoodie markets to MA operators specifically (Google Alerts, industry newsletters)
- [ ] High Times Local announces Boston edition
- [ ] Hoodie Connect signs 20+ MA dispensaries
- [ ] Hoodie publishes MA-specific report
- [ ] Hoodie attends NECANN or MA cannabis event
- [ ] Major MA MSO becomes visible Hoodie client

### Response Protocol

**Immediate (Week 1 after trigger):**
1. Audit Hoodie Connect MA uptake — how many dispensaries signed up?
2. Accelerate outreach to remaining unclaimed operators
3. Publish "GLASS vs Hoodie for MA Operators" comparison: free vs paid, CCC data vs none, delivery vs none, local vs national
4. Contact all claimed operators: "We've been your pricing partner for X months. Here's what Hoodie doesn't offer."

**Short-term (Month 1 after trigger):**
1. Offer "Founding Partner" benefits to operators who commit to GLASS (exclusive data, priority features)
2. Accelerate Cue launch — brand relationships create switching costs
3. Lock in exclusive data-sharing agreements with key operators
4. Double social content output — flood MA cannabis conversation with GLASS data
5. Press push: "Local startup vs VC-backed national platform" narrative (media loves David vs Goliath)

**Medium-term (Month 3-6 after trigger):**
1. Double down on features Hoodie can't match: THC Accuracy, Threat Radar, Delivery Toggle, GPID-powered price comparison
2. Build operator community (Discord/Slack) — social network switching costs
3. Pursue CCC partnership/endorsement (Hoodie won't court one state's regulator)
4. Consider temporary "free premium" offer to prevent operator defection

**Nuclear Option (if Hoodie launches free tier for MA operators):**

Our response: "We've been free. They just got here. We have X months of your pricing history, X community corrections on your page, X consumers searching for your products, and CCC enforcement alerts that Hoodie doesn't track. They know your menu price. We know your market."

**The deeper truth:** Hoodie entering MA validates our market. It means there's real money in MA cannabis intelligence. At that point, we're an acquisition target — either for Hoodie (they buy MA depth) or for a competitor who wants to counter Hoodie's expansion.

---

## APPENDIX A: FINANCIAL PROJECTIONS (HOODIE-ADJUSTED)

### Conservative Scenario (Hoodie ignores MA)

| Month | Premium Pages | Brand Placement | Roviq Upsell | Cue | Delivered | Total |
|-------|-------------|----------------|-------------|-----|-----------|-------|
| 1-2 | $0 | $0 | $0 | $0 | $0 | **$0** |
| 3 | $400 | $0 | $0 | $0 | $0 | **$400** |
| 4 | $1,000 | $800 | $0 | $0 | $0 | **$1,800** |
| 5 | $1,600 | $2,400 | $2,500 | $0 | $0 | **$6,500** |
| 6 | $2,000 | $4,000 | $5,000 | $0 | $0 | **$11,000** |
| 7-8 | $3,000 | $4,000 | $5,000 | $2,000 | $0 | **$14,000** |
| 9-12 | $4,000 | $4,000 | $7,500 | $4,000 | $2,000 | **$21,500** |

**Year 1 Total: ~$120,000-$150,000**

### Aggressive Scenario (Hoodie enters MA at Month 8)

| Revenue Stream | Pre-Hoodie (Mo 1-8) | Post-Hoodie (Mo 9-12) | Impact |
|---------------|---------------------|----------------------|--------|
| Premium Pages | $8,000 | $4,000 (some churn) | -50% |
| Brand Placement | $11,200 | $8,000 (brands hedge) | -29% |
| Roviq Agency | $12,500 | $15,000 (more anxiety = more clients) | +20% |
| Cue | $2,000 | $4,000 (Hoodie-proof) | No impact |
| Delivered | $0 | $2,000 (Hoodie-proof) | No impact |
| **Total** | **$33,700** | **$33,000** | **-2%** |

**Key insight: Hoodie entering MA barely hurts revenue** because 84% of our revenue streams are Hoodie-proof (Cue, Delivered, AC, Roviq). Premium pages might churn, but the fulfillment-integrated streams don't depend on being the only data provider.

---

## APPENDIX B: DAILY OPERATING RHYTHM

### Randy's Daily Time: ~30-45 Minutes

| Time | Task | Duration |
|------|------|----------|
| 8:00 AM | Review GLASS dashboard (check own data quality) | 5 min |
| 8:05 AM | Review AI-generated social content queue, approve/reject | 10 min |
| 8:15 AM | Check Hoodie monitoring alerts (Google Alerts) | 2 min |
| 8:17 AM | Review feedback/corrections queue (if any need manual review) | 5 min |
| 12:00 PM | Community engagement: reply to r/bostontrees, X mentions | 10 min |
| 5:00 PM | Check daily metrics: traffic, signups, social growth | 5 min |

### AI Agent Daily Rhythm

| Time | Task |
|------|------|
| 4:00 AM | Full scrape refresh (Dutchie, Weedmaps, iHeartJane, Leafly) |
| 5:00 AM | GPID matching on new/changed products |
| 6:00 AM | Dashboard data refresh, GLASS Scores recalculated |
| 6:30 AM | Content generation: price cards, comparison data, social copy |
| 7:00 AM | Content queued for Randy's review |
| Hourly | Delta checks on "watched" items |
| Hourly | Process community corrections (auto-apply high confidence) |
| Daily | Scraper error rate analysis → frequency adjustments |
| Weekly | GPID model evaluation, newsletter generation |

---

## APPENDIX C: KEY MONITORING DASHBOARD

Track these metrics weekly to gauge competitive position:

### Consumer Metrics (Anti-Hoodie Indicators)
- MA cannabis search rankings (GLASS vs High Times for key terms)
- r/bostontrees mentions of GLASS vs Hoodie
- Consumer site traffic and growth rate
- Alert subscriber growth
- Social follower growth and engagement rate

### Operator Metrics (Lock-In Indicators)
- Total operators on free tier
- Claimed pages count
- Operator return rate (how often do they check GLASS?)
- Community corrections submitted
- Premium conversion rate

### Data Quality Metrics (Moat Indicators)
- GPID match accuracy
- Cross-platform coverage (% of products matched across 2+ platforms)
- Community corrections vs scraper errors ratio
- Overall data accuracy (user-reported)

### Hoodie Watch (Threat Indicators)
- Hoodie Connect MA dispensary count (check monthly)
- High Times Local city expansion announcements
- Hoodie job postings with "Massachusetts" or "Boston"
- Hoodie social media mentions of MA
- MA operator mentions of Hoodie in conversation

---

## FINAL NOTE

This is a war plan. Hoodie Analytics has $9.4M, 36 employees, and a CEO who built and sold this exact business before. We have one person, AI agents, and zero allocated dollars.

But we have something Hoodie doesn't: the ability to go deep in one market before they notice, to be free because our revenue comes from a different layer, to integrate intelligence with fulfillment, and to build the only cross-platform product matching system in cannabis.

Hoodie's strength is national breadth. National breadth is a weakness when you're competing against someone who knows every CCC filing, every dispensary owner's name, every price discrepancy between Dutchie and Weedmaps, and every lab test result that contradicts a menu claim — in one state.

They know the market. We know the market AND the operators AND the consumers AND the products AND the regulations AND the delivery routes AND the brand incentive ecosystem AND the manufacturing pipeline.

The next 6 months determine whether GLASS becomes the MA cannabis operating system or a nice idea that got outrun by a VC-funded competitor.

**Move fast. Ship ugly. Fix forward. Build the moat before they see the castle.**

---

*Last updated: February 13, 2026*  
*This document is the single source of truth for GLASS strategy. All previous strategy documents are superseded.*
