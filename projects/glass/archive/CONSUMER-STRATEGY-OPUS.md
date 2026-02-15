# GLASS Consumer-First Strategy

**Date:** February 13, 2026  
**Author:** Strategic Analysis (Opus)  
**Status:** Draft for Randy's Review

---

## 1. Executive Summary

GLASS has the most comprehensive cannabis price database in Massachusetts — 150K+ prices, 385 operators, 92% coverage — and the current plan buries this treasure behind a B2B adoption wall that requires busy, skeptical dispensary owners to sign up, learn a dashboard, and change their behavior. That's backwards. The play is to weaponize this data for consumers *first* — starting with automated social content and a dead-simple price comparison site — so that tens of thousands of Massachusetts cannabis buyers are checking GLASS prices before they walk into a dispensary. When a dispensary owner sees their store name appearing in 50K monthly searches and price comparisons they didn't control, they don't need a cold call. They need GLASS. This is the GasBuddy / Yelp / Vivino playbook, adapted for a market with $1.65B in annual sales, 650+ retailers, and zero existing consumer price transparency tool. The consumer layer doesn't replace the GPID / data infrastructure vision — it *funds and accelerates it* by creating the demand gravity that makes dispensaries, brands, and POS systems come to GLASS on their own terms.

---

## 2. Consumer Product Ideas (Ranked by Impact × Feasibility)

### Tier 1: Ship in 2 Weeks (Highest Impact, Lowest Effort)

#### 2.1 🏆 "The Daily Drop" — Automated Social Content Engine
**Impact: 10/10 | Feasibility: 10/10 | Ship: Week 1**

What it is: AI-generated short-form content posted daily to TikTok, Instagram Reels, YouTube Shorts, and X, using real GLASS price data. Not promotional content *for* dispensaries — **informational content *about* the market** that happens to feature dispensary names, prices, and deals.

Content formats (all automatable):
- **"Best $30 eighth in [City] right now"** — ranked list with prices and store names
- **"Price Drop Alert: [Strain] just went from $55→$40 at [Store]"** — real-time price change alerts
- **"How much does an ounce cost in Massachusetts? We checked 385 stores."** — data visualization posts
- **"[Store A] vs [Store B]: Who's cheaper?"** — head-to-head comparisons
- **"The most expensive dispensary in Boston charges $X for [product]. The cheapest charges $Y. They're 2 miles apart."** — shock-value pricing gaps
- **"Friday Deal Roundup: Top 10 drops this week"** — weekly digest
- **"New strain alert: [Strain] just appeared at [X] stores in MA"** — product discovery
- **"Massachusetts weed prices have dropped 73% since 2020. Here's the data."** — educational/viral

Why it works:
- Cannabis content is *starving* on social media because brands can't advertise. An objective, data-driven account that talks about prices (not about getting high) occupies a massive vacuum.
- It's GasBuddy's model: consumers don't go to GasBuddy because they love the app — they go because they want to save money. Same energy.
- Every post names real dispensaries and real prices, which means dispensary owners WILL see their store mentioned (by customers, by Google Alerts, by competitors tagging them).
- The "aha moment" is instant: "Wait, the dispensary 10 minutes away charges $15 less for the same thing?"

Compliance angle:
- GLASS is not a dispensary. It's a data/media company publishing public price information.
- No health claims, no "buy this" CTAs, no age-gated product promotion — just market data.
- Position as journalism/consumer advocacy, not advertising.
- X (Twitter) explicitly allows cannabis informational content.
- TikTok bans cannabis promotion but allows educational/informational content about the industry. Avoid showing products, use charts/maps/text instead.
- Instagram is riskiest — use coded language, focus on data visualizations, avoid product imagery.

Automation stack:
1. GLASS DB → daily query for top movers, price drops, new products, cheapest by category/city
2. GPT-4 → generate script/copy for each format
3. AI video tools (HeyGen, Runway, CapCut auto-edit) → produce short-form video with text overlays, maps, charts
4. Buffer/Later/custom script → schedule and post across platforms
5. Randy curates (10 min/day review) → approve/reject queue

**Revenue play:** Once the accounts have followers, dispensaries will *pay* to be featured, promoted, or to correct their listing. But that comes later — first, build the audience.

---

#### 2.2 🏆 GreenCheck — Consumer Price Comparison Website
**Impact: 9/10 | Feasibility: 9/10 | Ship: Week 2**

What it is: A clean, fast, mobile-first website where any MA consumer can search for a cannabis product and instantly see every dispensary's price, sorted by cheapest to most expensive, with distance from their location.

Think: **GasBuddy for weed**, but also **Google Shopping for cannabis** (which literally doesn't exist because Google bans cannabis ads and shopping listings).

Core features (MVP):
- **Search by product/strain/category** → results show every store carrying it with price + distance
- **"Near Me" mode** → show cheapest options within 5/10/25 miles
- **Category browse** → Flower, Vapes, Edibles, Concentrates, Pre-rolls → sorted by $/unit
- **Price history** → "This product was $45 last week, now $38" (we have the time-series data)
- **Store pages** → every dispensary gets a page showing their full menu + how their prices rank vs. nearby competitors
- **No login required** → zero friction, instant value

Why a website first (not an app):
- No app store review risk (Google Play bans cannabis sales apps; Apple is case-by-case)
- SEO-friendly — every store page, every product page is indexable by Google
- Cannabis consumers search "dispensary near me" and "[strain] price" on Google millions of times — there's NO good answer for these searches right now
- Mobile web is 85%+ of cannabis consumer browsing
- PWA (installable web app) gives app-like experience without store approval

SEO moat:
- We'd have a unique page for every product × every store × every city. That's potentially **hundreds of thousands of indexable pages** with real pricing data no other site has.
- "GMO Cookies price Boston" → GLASS page ranks #1 because no one else has this data in a structured, indexable format.
- Dutchie/Weedmaps have some of this, but their pages are store-centric, not product/price-centric. They don't let you compare prices across stores.

Store-level "claim your page" flywheel:
- Every dispensary gets a GLASS page whether they want one or not (public price data).
- Page shows: prices, price rank, product selection breadth, "last updated X hours ago."
- Bottom of page: "Are you the owner? Claim this page to update your info, respond to comparisons, and get analytics."
- This is the Yelp/Google Business Profile playbook — business owners MUST engage because their customers are already there.

**Revenue play:** The "claim your page" flow is the bridge to B2B. Claimed pages get analytics (who's viewing, what they search for, how you rank). Premium pages get featured placement, correction tools, and the full GLASS dashboard.

---

### Tier 2: Ship in 30 Days (High Impact, Medium Effort)

#### 2.3 "PriceWatch" — SMS/Push Deal Alerts
**Impact: 8/10 | Feasibility: 7/10 | Ship: Week 3-4**

What it is: Consumers set up alerts for specific products, strains, price thresholds, or stores. When the price drops or a new product appears, they get a text or push notification.

Examples:
- "Alert me when any 1/8 of GMO drops below $35 within 10 miles of Somerville"
- "Tell me when [Store] adds new concentrates"
- "Notify me of any price drop over 15% near me"

Why it matters:
- **Daily engagement**: People open price alerts. Honey's entire business was built on this — "we'll find you a better price" at the moment of intent.
- **Data goldmine**: Alert sign-ups tell us exactly what consumers want, where they are, and what their price sensitivity is. This data is *enormously* valuable to sell back to dispensaries (anonymized).
- **Retention mechanism**: Social content is top-of-funnel discovery; alerts are the habit loop.

Technical simplicity:
- Twilio SMS ($0.0079/text) or web push notifications (free)
- GLASS DB already has the data; just need a trigger system
- User sets criteria → cron job checks daily scrape → matches → sends alert

**Revenue play:** Consumer demand data (anonymized) is a product we sell to dispensaries. "42% of GLASS users in your area are searching for concentrates under $40. You don't carry any."

---

#### 2.4 "Strain Finder" / Product Matcher
**Impact: 7/10 | Feasibility: 7/10 | Ship: Week 3-4**

What it is: A conversational or quiz-style tool that helps consumers find the right product. "I want something relaxing but not sleepy, under $40, within 15 minutes of me." GLASS recommends the best match with prices and store locations.

This is the **Virtual Budtender** we already have (deployed at CH), repurposed for consumers instead of embedded in dispensary sites.

Twist: Unlike dispensary-embedded budtenders that only recommend *that store's* products, GLASS recommends across ALL stores. This is genuinely more useful for consumers and exactly the kind of cross-store intelligence no dispensary can offer.

**Revenue play:** Affiliate/referral model. When a consumer clicks through to a store from a recommendation, the store sees the referral. At scale, this becomes a paid placement channel (like Google Shopping ads).

---

### Tier 3: Ship in 60 Days (Medium Impact, Higher Effort)

#### 2.5 "The GLASS Score" — Dispensary Ratings (Beyond Reviews)
**Impact: 8/10 | Feasibility: 5/10 | Ship: Week 5-8**

What it is: An objective, data-driven dispensary score that combines pricing competitiveness, selection breadth, price stability, new product velocity, and (eventually) consumer ratings. Think: **a credit score for dispensaries, visible to consumers.**

Components:
- **Price Score** (40%): How do your prices compare to the market? Are you in the cheapest 20% or the most expensive?
- **Selection Score** (20%): How many unique products/strains? Category breadth?
- **Freshness Score** (15%): How often do you add new products? How current is your menu?
- **Stability Score** (10%): Do your prices swing wildly or are they consistent?
- **THC Accuracy Score** (15%): Cross-reference lab-tested THC% (CCC's 298K-row dataset) vs. menu claims. Catches label inflation — a genuine consumer protection feature.

Why it's powerful:
- Nobody else has this. Weedmaps/Leafly have user reviews (easily gamed). Google has star ratings (doesn't reflect pricing). GLASS would have the only **objective, data-backed dispensary score** in the market.
- It creates urgency for dispensaries to claim their GLASS page and optimize their listing.
- It's inherently shareable — "My dispensary has a 92 GLASS Score" becomes bragging rights. A low score becomes motivation to improve (and to pay GLASS for consulting/tools).
- The THC Accuracy Score is a regulatory compliance angle — CCC cares about label accuracy. GLASS becomes a quasi-regulatory watchdog, which builds massive credibility.

**Revenue play:** Dispensaries pay to see the detailed breakdown of their score, get improvement recommendations, and access tools to improve it (Margin Engine, Cue, etc.).

---

#### 2.6 "GLASS Deals" — Browser Extension / Overlay
**Impact: 7/10 | Feasibility: 5/10 | Ship: Week 6-8**

What it is: A lightweight browser extension or mobile bookmark that, when a consumer is browsing a dispensary menu on Dutchie/Weedmaps/Leafly, shows a small overlay: "This product is $8 cheaper at [Store] (3.2 miles away)" or "This is the best price in your area ✓."

This is literally **Honey for cannabis** — and it's the same mechanic that got Honey acquired by PayPal for $4 billion.

Why it could be huge:
- Intercepts consumers at the *exact moment of purchase intent*
- Creates price transparency pressure that forces dispensaries to compete
- Generates massive data about consumer shopping behavior across platforms
- Every time someone uses it, they think about GLASS

Risks:
- Lower install base than a website (extensions require active install)
- Dutchie/Weedmaps might not appreciate it
- Cannabis consumers might not install browser extensions (mobile-heavy demographic)

Alternative approach: Instead of a browser extension, build a **"Price Check" feature** on the GLASS website where consumers paste a Dutchie/Weedmaps URL and get an instant comparison. Lower friction, same value.

---

#### 2.7 Community / Social Layer — "GLASS Picks"
**Impact: 6/10 | Feasibility: 6/10 | Ship: Week 6-8**

What it is: Let consumers save favorites, create "collections" (my go-to strains, my budget picks, my top dispensaries), and share them publicly. Think: Spotify playlists but for cannabis.

Elements:
- **Lists**: "Best $30 eighths in Boston (updated weekly)" — curated by GLASS or by users
- **Check-ins**: "I just bought [product] at [store] for $[price]" — Untappd-style
- **Comments/Tips**: "The GMO at [Store] is fire but go before noon, they sell out"
- **Leaderboard**: Most helpful reviewers, most active contributors

Why it matters:
- User-generated content creates lock-in and defensibility
- Check-in data gives GLASS real *purchase* confirmation (not just menu scraping)
- Community features give consumers a reason to return daily
- It's the Untappd/Vivino playbook — social features around a commodity product create stickiness

Risk: Cannabis users might be privacy-sensitive about tracking their purchases. Make everything opt-in, allow anonymous contributions.

---

### Tier 4: Longer-Term (90+ Days)

#### 2.8 "GLASS Pass" — Loyalty/Savings Program
**Impact: 9/10 | Feasibility: 4/10 | Ship: Post-90-day**

What it is: A cross-dispensary loyalty program. Consumers earn "GLASS Points" when they shop at any GLASS-listed dispensary (tracked via receipt upload, check-in, or eventually POS integration). Points unlock perks, exclusive deals, or cash back.

This is the **Pay with GasBuddy** equivalent — GasBuddy's most successful monetization play. But even simpler: no payment integration needed initially. Just receipt scanning + points.

Why it would be transformative:
- Cross-store loyalty doesn't exist in cannabis (every dispensary has their own, incompatible program)
- It gives GLASS *actual purchase data*, not just menu data — the holy grail
- It creates a consumer habit loop: buy → scan receipt → earn points → check GLASS for deals → buy
- At scale, brands would PAY to offer bonus points on their products (this is Cue, repackaged for consumers)

Complexity: Receipt scanning AI, point redemption infrastructure, dispensary partnerships. Not trivial, but not impossible.

---

#### 2.9 Delivery Marketplace Layer
**Impact: 8/10 | Feasibility: 4/10 | Ship: Post-90-day**

What it is: When a consumer finds their ideal product on GLASS, offer one-click delivery (powered by Delivered Inc.'s MD1303 license). GLASS becomes not just where you *find* the best price, but where you *buy* at the best price.

This is the ultimate consumer value: discover → compare → order → deliver. End-to-end.

Connection to existing plans: This is already in the GLASS-PLAN.md as the "Delivered" spoke. The consumer-first strategy just reframes the entry point: instead of the dispensary toggling delivery ON, the consumer pulls delivery into existence by demanding it.

---

## 3. Viral/Growth Mechanics

### 3.1 The Core Viral Loop

```
Consumer sees GLASS content on social media (TikTok, IG, X)
    → "Wait, the dispensary near me charges HOW much more?"
    → Visits GLASS website to check prices
    → "Holy shit, I've been overpaying by $15/eighth"
    → Tells friends ("use this site before you buy weed")
    → Shares a GLASS comparison or deal on their story/group chat
    → Friends check GLASS → loop repeats
```

**Aha moment:** The first time a consumer sees a side-by-side comparison of two dispensaries 5 miles apart with a >20% price gap on the same product. That's the "I can never go back" moment.

### 3.2 Specific Growth Mechanics

**A. Social Content → Website Traffic (Top of Funnel)**
- Every social post ends with: "Check all prices at glassintel.xyz"
- Every post tags the dispensaries mentioned → dispensary followers see it → their customers see it
- Weekly "most expensive dispensary" and "best value dispensary" posts create controversy and sharing
- Price comparison posts are inherently shareable — people LOVE sharing "can you believe this?"

**B. SEO → Organic Discovery (Sustainable Growth)**
- Product pages rank for "[strain] price [city]" searches
- Store pages rank for "[dispensary name] menu prices" searches
- Category pages rank for "cheap weed near me", "best edible deals Massachusetts"
- Blog/data content ranks for "Massachusetts cannabis market", "weed prices dropping"
- **This is the long-term growth engine.** Social is the spark; SEO is the fire.

**C. Word of Mouth → Group Chat Sharing (Organic Viral)**
- Cannabis purchases are social — people ask friends "where should I go?" in group chats
- GLASS links are the answer: "Just check GLASS, here's the link"
- "Share this deal" button on every product comparison
- WhatsApp/iMessage share cards with preview (product, price, store, distance)

**D. Reddit / Cannabis Forums (Community Seeding)**
- r/bostontrees (32K+ members) is the primary MA cannabis community
- Posting genuine GLASS data analysis (not promotion) builds credibility
- "I scraped every dispensary in Massachusetts. Here's what I found." → guaranteed viral on cannabis Reddit
- Not spamming — providing genuinely useful data that the community craves

**E. Gamification (Retention)**
- "You've saved $X by using GLASS this month" counter (like Honey's "You've saved $312")
- "Price Drop Streak" — X days in a row checking prices
- "Deal Hunter" badges for finding the best deals
- Leaderboard for most helpful community members

### 3.3 The "Dispensary Tag" Mechanic

This is the secret weapon for forcing B2B attention:

Every piece of GLASS content — social posts, website pages, comparison cards — **tags or names the dispensary by name**. Not maliciously. Factually. "The average price of a top-shelf eighth at [Store] is $47.50, ranking them #18 of 36 dispensaries in Boston."

Effects:
1. Dispensary staff/owners see the posts (they all monitor social for their store name)
2. Dispensary customers see the posts and mention them to budtenders
3. Dispensaries with good scores celebrate and share → free distribution
4. Dispensaries with bad scores get anxious → come to GLASS to understand and improve
5. Neither group can ignore GLASS

This is exactly how Yelp grew — businesses HAD to pay attention because their customers were already there rating them.

---

## 4. B2B Forcing Function

### 4.1 The Gravity Model

The current plan asks dispensaries to come to GLASS voluntarily. The consumer-first strategy creates **gravitational pull**:

```
Phase 1 (Month 1-2): Consumers discover GLASS
    → 5,000-10,000 monthly visitors
    → Dispensaries start hearing their name
    → "What is this GLASS thing my customers keep mentioning?"

Phase 2 (Month 3-4): Critical mass
    → 25,000-50,000 monthly visitors
    → GLASS pages start ranking on Google
    → Dispensary owners search their own store and find a GLASS page
    → "I need to claim this page and make sure my info is right"

Phase 3 (Month 5-6): Network effects
    → 100,000+ monthly visitors
    → GLASS is the go-to price comparison for MA consumers
    → Dispensaries who AREN'T on GLASS are invisible
    → Dispensary demand: "How do I get featured? How do I improve my score?"
    → GLASS sells the tools (Margin Engine, Cue, analytics)

Phase 4 (Month 7-12): Infrastructure
    → POS systems approach GLASS for integration (not the other way around)
    → Brands pay for placement (Cue model)
    → Delivery integration (Delivered spoke)
    → GPID becomes the standard because consumers and dispensaries both use it
```

### 4.2 At What Scale Do Dispensaries HAVE to Pay Attention?

Based on GasBuddy/Yelp/Google Business precedent:

- **1,000 visits/month to a dispensary's GLASS page:** Owner is curious
- **5,000 visits/month:** Owner claims their page
- **10,000 visits/month:** Owner asks about premium features
- **25,000+ visits/month:** Owner can't afford to NOT be on GLASS

For the overall platform:
- **10K monthly visitors:** Interesting novelty
- **50K monthly visitors:** Industry chatter starts ("have you seen GLASS?")
- **100K monthly visitors:** Dispensaries proactively reach out
- **250K+ monthly visitors:** POS systems want to integrate

Massachusetts has ~1.5M+ regular cannabis consumers (extrapolating from $1.65B annual sales, ~$1,100/consumer/year). Capturing just 5% as monthly active users = 75K MAU. That's achievable within 6 months with a strong social + SEO strategy.

### 4.3 Leverage Over POS Systems

Currently, GLASS is applying to POS systems for API access. The consumer-first strategy **inverts this power dynamic:**

- **Before:** "Hi Dutchie, we'd like API access to build a tool for operators" (they have all the leverage)
- **After:** "Hi Dutchie, 200K cannabis consumers use GLASS to compare prices. We're driving traffic to your client stores. Want to integrate so your clients can manage their GLASS presence from your dashboard?" (GLASS has the leverage)

POS systems serve dispensaries. If dispensaries demand GLASS integration because their customers are on GLASS, POS systems have to comply. This is how Yelp forced OpenTable integration, how Google forced business owners to claim their Maps listing.

---

## 5. Revenue Model (Without Charging Consumers)

### 5.1 Revenue Streams (Ordered by Timeline)

#### Immediate (Month 1-3): Zero-Revenue Growth Phase
- No revenue from consumers. All investment in audience growth.
- Existing Roviq agency revenue subsidizes development.
- Cost to run: ~$200/month (hosting, scraping proxies, Twilio, AI APIs)

#### Short-Term (Month 3-6): Dispensary Advertising & Claiming

| Stream | Model | Estimated Revenue |
|--------|-------|-------------------|
| **Claimed Pages (Free → Premium)** | Freemium. Claim = free. Premium features = $199/mo | $2K-5K/mo (10-25 premium stores) |
| **Featured Placement** | Dispensaries pay to be "Recommended" in search results | $500-1K/mo per store |
| **Sponsored Content** | "This week's deals at [Store]" — native content on GLASS social accounts | $250-500/post |

#### Medium-Term (Month 6-12): Data & Intelligence Products

| Stream | Model | Estimated Revenue |
|--------|-------|-------------------|
| **Consumer Demand Data** | Anonymized: "What consumers in your area search for" | $299/mo per dispensary |
| **GLASS Score Improvement** | "Your GLASS Score is 62. Here's how to get to 85." → Margin Engine upsell | $399/mo per store |
| **Brand Placement (Cue)** | Brands pay to be recommended in Strain Finder / Product Matcher | $500-5K/mo per brand |
| **Referral Attribution** | "GLASS sent 847 customers to your site this month" → CPA model | $1-3/referral |

#### Long-Term (Month 12+): Platform Monetization

| Stream | Model | Estimated Revenue |
|--------|-------|-------------------|
| **GLASS Pass / Loyalty** | Brands fund rewards; GLASS takes % of redemptions | Significant at scale |
| **Delivery Commission** | Consumer orders delivery through GLASS → 15% of GMV | Via Delivered spoke |
| **POS Integration Fee** | POS systems pay for GLASS data feed | $5-25K/yr per POS |
| **Toll Processing Referral** | "Can't find this product? We'll make it for you." → AC Toll | Commission per unit |
| **Data Licensing** | Sell anonymized pricing + demand data to investors, researchers, regulators | $10-50K/yr per client |

### 5.2 Revenue Projection (Consumer-First Path)

| Month | Consumers (MAU) | Dispensaries Claimed | Monthly Revenue |
|-------|-----------------|---------------------|-----------------|
| 3 | 5,000 | 10 | $0 (growth phase) |
| 6 | 25,000 | 50 | $5-10K |
| 9 | 75,000 | 150 | $20-40K |
| 12 | 150,000 | 300 | $50-100K |

These are conservative estimates. GasBuddy reached 1M users before seriously monetizing. The key insight: **consumer attention is the product, and it's worth more than any SaaS subscription.**

### 5.3 How Spokes Plug In

The existing GLASS spoke model (Cue, Delivered, AC, Roviq) actually gets *stronger* with consumer traffic:

- **Cue**: Instead of convincing brands to pay for budtender incentives at a few stores, brands pay for featured placement/recommendations to *150K monthly consumers*. Much bigger TAM, much easier sell.
- **Delivered**: Instead of a toggle in an operator dashboard, it's a "Get it delivered" button on every product comparison. Consumer pull > operator push.
- **AC Toll Processing**: When consumers search for a product type that doesn't exist in MA (or is underpriced everywhere), GLASS has data to tell AC exactly what to manufacture. Consumer demand shapes supply.
- **Roviq**: Dispensaries who see their GLASS Score and want to improve become agency clients. No cold outreach — they come to you because their customers are already judging them on GLASS.

---

## 6. What We're Missing (Blind Spots & Contrarian Ideas)

### 6.1 The Regulatory Weapon

**Massachusetts CCC is actively looking for consumer protection tools.** The 2026 regulatory push includes expanded access and reduced burdens. GLASS's THC Accuracy Score (cross-referencing lab data vs. menu claims) positions GLASS as a *regulatory ally*, not just a commercial tool.

Play: Present GLASS data to the CCC. "We found that X% of dispensaries list THC percentages that exceed lab-tested results by >5 points." This gets GLASS media coverage, regulatory credibility, and consumer trust. It also makes dispensaries terrified of having bad data — which drives them to claim their GLASS page and correct their listings.

**Nobody is doing this.** Leafly, Weedmaps, Dutchie — none of them have the incentive to call out menu inaccuracies because they're funded by dispensaries. GLASS, funded by consumers, can be the honest broker.

### 6.2 The 2026 Ballot Threat = GLASS Growth Catalyst

Smart Approaches to Marijuana has funded a 2026 ballot proposal to *end adult-use cannabis sales* in Massachusetts. This will dominate cannabis media in MA for the rest of 2026.

GLASS play: Become the data source for the "keep it legal" side. "Legal cannabis saved Massachusetts consumers $X vs. street prices" — backed by GLASS data. This gets GLASS into every news story about the ballot measure, every advocacy group's toolkit, every dispensary's counter-campaign.

This is a once-in-a-cycle opportunity for brand awareness that has nothing to do with advertising.

### 6.3 The "Anti-Yelp" Positioning

Yelp is hated by businesses because it's perceived as extortionate — "pay us or we'll bury your bad reviews." GLASS should deliberately position as the anti-Yelp:

- **Transparent methodology**: The GLASS Score formula is public. No black box.
- **No "pay to suppress"**: Premium pages get more features, not better scores.
- **Dispensary-friendly framing**: "We're here to help you compete, not shame you."

This positioning earns trust with both consumers (it's honest) and dispensaries (it's fair). Long-term, this trust is the moat.

### 6.4 Cross-Industry Parallel: Vivino for Cannabis

Vivino's killer feature was **label scanning** — point your phone at a wine bottle, get instant ratings, reviews, and price comparisons. Cannabis equivalent:

- Point phone at a dispensary menu board → GLASS identifies products → shows price comparisons with nearby stores
- Scan a product label/barcode → GLASS shows price history, THC accuracy score, and where to find it cheaper
- This requires the GPID system to work well — another forcing function for the data layer

This is a Tier 4 feature (needs mature GPID), but it's the long-term "magic moment."

### 6.5 The Newsletter Pivot

The current plan has a B2B newsletter ("The Operator's Margin Report"). With the consumer-first strategy, the newsletter becomes **consumer-facing**:

- **"The MA Weed Report"** — weekly email with top deals, new strains, price trends, dispensary rankings
- Target: cannabis consumers, not operators
- Much larger addressable audience (1.5M consumers vs. ~400 operators)
- Monetizable via native dispensary ads ("This week's featured deal")
- Feeds social content (newsletter → social excerpts)
- Builds an owned audience independent of social media algorithms

The B2B newsletter still exists, but it's secondary — and it uses the same data.

### 6.6 Distribution Channels We're Ignoring

- **Budtenders**: There are ~3,000-5,000 budtenders in MA. They ALL want to know what competitors charge (for their own shopping, and to answer customer questions). A budtender-specific GLASS feature ("see what your store charges vs. the market") makes every budtender a GLASS evangelist.
- **Cannabis tourism**: Boston is a tourism hub. "Best dispensaries for tourists" content performs well on Google. GLASS tourist guides → high SEO value.
- **Cannabis events**: MA has dozens of cannabis events annually. GLASS data displayed at events (live price tickers, "best deals right now" screens) builds awareness fast.
- **Delivery drivers**: Delivered Inc. drivers interact with consumers daily. GLASS referral cards in every delivery bag.
- **Local media**: Boston Globe, MassLive, Boston.com all cover cannabis regularly and need data sources. Position GLASS as the go-to data citation.
- **Universities**: MA has the highest concentration of universities in the US. College-age consumers are heavy cannabis users AND heavy social media users. Campus-specific "cheapest weed near [University]" content.

### 6.7 The Data Moat Nobody Can Replicate

Once GLASS has 6+ months of historical price data across 385+ dispensaries, that dataset becomes **irreplaceable**:

- **Price elasticity models**: How does Store A's price change affect Store B's sales? Only possible with longitudinal data.
- **Market timing**: When do prices drop? (Post-harvest September/October). When do they spike? (4/20, holidays). 
- **Predictive pricing**: "Based on historical patterns, expect a 12% price drop on concentrates in March"
- **Category trends**: Which product categories are growing/shrinking? What's the price trajectory?
- **Dispensary health signals**: Consistent price cutting = distress. Stable premium pricing = healthy. Price volatility = management changes.

This data compounds in value. Even if a competitor starts scraping today, they're 6+ months behind. By then, GLASS has the consumer audience and the historical depth.

### 6.8 The Contrarian Take: Don't Build an App

Every cannabis startup wants to build an app. Don't.

- App stores are hostile to cannabis (Google Play explicitly bans, Apple is unpredictable)
- App install is high-friction (vs. visiting a website)
- SEO doesn't work for apps (you need the web pages for Google ranking)
- PWA (Progressive Web App) gives you 90% of app features with zero store risk
- If GLASS needs push notifications, web push works on Android and can be prompted on iOS

Build a best-in-class mobile web experience. Let the app come later when consumer demand is overwhelming and the regulatory landscape is clearer.

---

## 7. 90-Day Action Plan

### Week 1-2: "The Spark" (Content Engine + MVP Site)

**Goal:** Launch automated social content and a basic consumer price comparison page.

| Day | Action | Owner |
|-----|--------|-------|
| 1-2 | Build content generation pipeline: DB query → GPT-4 → social post templates (10 formats) | AI agent |
| 1-2 | Create social accounts: @glassintel on TikTok, Instagram, X, YouTube | Randy |
| 3-4 | Build consumer MVP: simple search → price comparison results page, mobile-first | AI agent |
| 3-4 | Generate first 30 social posts from GLASS data (queue for daily posting) | AI agent |
| 5 | Deploy consumer site at glassintel.xyz/prices (or prices.glassintel.xyz) | AI agent |
| 5 | Randy reviews first 10 social posts, provides feedback on tone/style | Randy |
| 6-7 | Begin posting: 2-3 posts/day across platforms | Automated |
| 8-10 | Build "store page" template — auto-generated page for every dispensary | AI agent |
| 8-10 | SEO: meta tags, structured data, sitemap for all store/product pages | AI agent |
| 11-14 | Seed r/bostontrees with genuine data analysis post | Randy |
| 14 | **Checkpoint:** Measure social engagement, site traffic, first signals | Review |

**Deliverables:**
- [ ] Social content pipeline running (2-3 posts/day automated, Randy approves)
- [ ] Consumer price comparison site live (search → results → store pages)
- [ ] 385+ auto-generated dispensary pages indexed
- [ ] Reddit seeding post published

### Week 3-4: "The Hook" (Alerts + Strain Finder)

**Goal:** Add retention mechanics and deeper product discovery.

| Day | Action | Owner |
|-----|--------|-------|
| 15-17 | Build PriceWatch alert system (SMS + web push) | AI agent |
| 15-17 | Repurpose Virtual Budtender as consumer-facing Strain Finder on GLASS | AI agent |
| 18-20 | Build "Claim Your Page" flow for dispensary owners | AI agent |
| 21-23 | Launch consumer newsletter ("The MA Weed Report" — weekly email) | AI agent + Randy |
| 24-28 | Iterate social content based on Week 1-2 performance data | AI agent |
| 28 | **Checkpoint:** Alert sign-ups, claim requests, newsletter subscribers | Review |

**Deliverables:**
- [ ] PriceWatch alerts live (SMS + push)
- [ ] Strain Finder / Product Matcher on consumer site
- [ ] "Claim Your Page" flow live
- [ ] Consumer newsletter launched

### Week 5-8: "The Flywheel" (Score + Community + Premium)

**Goal:** Build dispensary engagement tools and early monetization.

| Day | Action | Owner |
|-----|--------|-------|
| 29-35 | Build GLASS Score algorithm and display on every dispensary page | AI agent |
| 36-42 | Build premium "Claimed Page" features (analytics, correction tools) | AI agent |
| 43-49 | Launch THC Accuracy Score (CCC lab data cross-reference) | AI agent |
| 50-56 | Outreach to dispensaries who've been tagged in popular GLASS social posts | Inbound (they come to us) |
| 56 | **Checkpoint:** Claimed pages, premium conversions, social growth rate | Review |

**Deliverables:**
- [ ] GLASS Score live on all dispensary pages
- [ ] Premium claimed page ($199/mo) available
- [ ] THC Accuracy Score launched (with CCC data PR angle)
- [ ] First premium page conversions

### Week 9-12: "The Lock-In" (Data Products + Scale)

**Goal:** Launch B2B data products powered by consumer traffic.

| Day | Action | Owner |
|-----|--------|-------|
| 57-63 | Build Consumer Demand Report for dispensaries (anonymized search data) | AI agent |
| 64-70 | Launch Brand Placement (Cue lite) — brands pay for featured recommendations | AI agent |
| 71-77 | Press outreach: "GLASS data shows [headline insight about MA cannabis market]" | Randy |
| 78-84 | Build referral attribution system (track clicks from GLASS → dispensary menus) | AI agent |
| 84-90 | Evaluate: delivery integration timeline, POS outreach (from strength), GLASS Pass design | Strategic review |

**Deliverables:**
- [ ] Consumer Demand Reports available ($299/mo per dispensary)
- [ ] Brand Placement (Cue) generating first revenue
- [ ] At least one media placement using GLASS data
- [ ] Referral attribution system live

### Key Metrics to Track

| Metric | Week 2 | Week 4 | Week 8 | Week 12 |
|--------|--------|--------|--------|---------|
| Social followers (all platforms) | 500 | 2,500 | 10,000 | 25,000 |
| Website monthly visitors | 1,000 | 5,000 | 25,000 | 75,000 |
| Alert subscribers | 0 | 200 | 1,000 | 3,000 |
| Newsletter subscribers | 0 | 500 | 2,000 | 5,000 |
| Dispensary pages claimed | 0 | 5 | 25 | 75 |
| Premium subscriptions | 0 | 0 | 5 | 15 |
| Monthly revenue | $0 | $0 | $1-2K | $5-10K |

---

## 8. Risks & Mitigations

### 8.1 Platform Risk: Social Accounts Get Banned

**Risk:** TikTok/Instagram shut down GLASS accounts for cannabis-related content.  
**Likelihood:** Medium (Instagram higher, TikTok lower for data/educational content)  
**Impact:** High (loses top-of-funnel)

**Mitigations:**
- Frame all content as *market data and consumer education*, not product promotion. No product images, no consumption imagery, no purchase CTAs.
- Diversify across 4+ platforms (TikTok, IG, X, YouTube). X is safest — explicitly allows cannabis informational content.
- Build email list (newsletter) and SEO presence as platform-independent channels.
- If an account is banned, pivot that platform's content to a more conservative style and relaunch under a slightly different framing (e.g., "Massachusetts Market Data" vs. "Cannabis Price Comparison").
- Use coded/creative language on riskier platforms while maintaining clarity on safer ones.

### 8.2 Legal Risk: Dispensaries Object to Being Listed/Scored

**Risk:** A dispensary sends a cease-and-desist claiming GLASS is using their data without permission.  
**Likelihood:** Low-Medium  
**Impact:** Medium

**Mitigations:**
- All scraped data is from *public menus* — no different from a newspaper publishing store prices.
- The "Claim Your Page" feature gives dispensaries agency over their listing.
- GLASS Score methodology is transparent and objective — not defamatory.
- Legal precedent: Yelp, Google, TripAdvisor all rank/rate businesses using public data and have survived legal challenges.
- Have a clear "dispute" process: if a dispensary claims data is wrong, GLASS corrects it promptly.

### 8.3 Data Accuracy Risk: Wrong Prices Erode Consumer Trust

**Risk:** Scraper errors, stale data, or mismatched products show incorrect prices.  
**Likelihood:** Medium (94% Weedmaps failure rate is a real problem today)  
**Impact:** Very High (consumer trust is everything)

**Mitigations:**
- Fix Weedmaps scraper (Priority 1 from DATA-COVERAGE-ANALYSIS.md)
- Show "last updated" timestamp prominently on every price
- Confidence scores on product matches (only show high-confidence matches)
- "Report wrong price" button on every listing
- Data quality threshold: don't show prices older than 48 hours
- Consider showing price *ranges* instead of exact prices when confidence is lower

### 8.4 Competition Risk: Dutchie/Weedmaps Build This

**Risk:** An established player launches their own price comparison tool.  
**Likelihood:** Low (they're funded by dispensaries, not consumers — conflicting incentives)  
**Impact:** Medium

**Mitigations:**
- Dutchie/Weedmaps/Leafly have a structural conflict: their paying customers (dispensaries) don't *want* price transparency. They'd be building a tool that hurts their clients.
- GLASS, as a consumer-funded platform, has no such conflict — we *want* transparency because consumers want it.
- First-mover advantage: 6+ months of historical data, brand recognition, SEO rankings
- Even if a competitor launches, GLASS differentiates on: cross-platform comparison (no platform shows prices from ALL OTHER platforms), GLASS Score, THC Accuracy, CCC regulatory data integration.

### 8.5 Execution Risk: Too Much To Build, Too Small a Team

**Risk:** Randy + AI agents can't ship all of this in 90 days.  
**Likelihood:** Medium-High  
**Impact:** High

**Mitigations:**
- The 90-day plan is sequenced by priority. If we only ship Weeks 1-2 (social content + price comparison site), we've still tested the core consumer thesis.
- AI agents handle 90% of code, content generation, and data processing.
- Randy's role is curation and creative direction, not execution.
- Scope aggressively: the MVP consumer site is a search box, a results list, and auto-generated store pages. That's a weekend of AI-assisted development.
- Don't over-design. GasBuddy v1 was ugly. It worked because the data was useful.

### 8.6 Revenue Risk: Consumer Attention Doesn't Convert to B2B Revenue

**Risk:** We get 100K consumers but dispensaries still don't pay.  
**Likelihood:** Low (every precedent shows businesses pay for consumer attention)  
**Impact:** High

**Mitigations:**
- Multiple revenue paths that don't all depend on dispensary willingness to pay:
  - Brands pay for placement (Cue) — brands are ALWAYS willing to pay for consumer attention
  - Data licensing to investors/researchers — doesn't require dispensary cooperation
  - Affiliate/referral attribution — performance-based, easy sell
  - Consumer newsletter sponsorship — standard media monetization
- If dispensaries don't pay for premium pages, they WILL pay for fixing a low GLASS Score (via Roviq agency services). The score creates the anxiety; Roviq sells the solution.

### 8.7 The 2026 Ballot Wildcard

**Risk:** The ballot measure to end adult-use cannabis in MA passes, killing the market.  
**Likelihood:** Very Low (cannabis has strong public support in MA)  
**Impact:** Existential

**Mitigations:**
- The ballot measure is unlikely to pass — MA voted 53-47% to legalize in 2016, and support has only grown.
- Even in the unlikely event it passes, medical cannabis remains, and the GLASS model works for medical dispensaries too.
- The fight over the ballot measure will drive *more* interest in cannabis market data, not less — GLASS benefits from the attention regardless of outcome.
- Diversify to other states (CT, RI, NY) as a hedge — the model is replicable.

---

## Appendix: Why Consumer-First Beats B2B-First for GLASS

| Factor | B2B-First | Consumer-First |
|--------|-----------|----------------|
| **Speed to adoption** | Slow (operators are busy, skeptical) | Fast (consumers are eager for deals) |
| **Sales effort** | High (demos, onboarding, hand-holding) | Zero (content → website → self-serve) |
| **Data network effect** | Weak (each operator only cares about their data) | Strong (more consumers → more data → better product) |
| **Revenue timeline** | 6-12 months to first dollar | 3-6 months via sponsored content/claimed pages |
| **POS integration leverage** | We ask them nicely | They come to us because dispensaries demand it |
| **Defensibility** | Low (any tool can build a dashboard) | High (consumer audience + SEO + brand + historical data) |
| **Randy's involvement** | Must do sales/demos (hates it) | Curate content, build cool things (loves it) |
| **Aligns with Randy's values** | "Let me show you what GLASS can do" | "Build something so good they come to you" |

The consumer-first strategy doesn't abandon the B2B model. It *supercharges* it by creating the demand that makes B2B adoption inevitable. Every dispensary that sees their store being compared, rated, and discussed by 50K consumers will eventually walk through the door on their own.

**Don't sell. Build things so good people come to you.** That's literally in OPS.md. The consumer-first strategy is the purest expression of that principle.
