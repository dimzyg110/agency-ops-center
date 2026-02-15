# GLASS MASTER STRATEGY — THE WAR PLAN

**Version 1.0 | February 13, 2026**  
**Status: EXECUTE THIS. Nothing else matters.**  
**Owner: Randy Torres / Roviq**

---

## 1. Executive Summary

GLASS is a consumer price comparison engine for Massachusetts cannabis that creates an inescapable gravity well for dispensaries, brands, and the entire supply chain. We launch with the Top 500 hand-verified products — not 118,000 messy scraped SKUs — and we ship a mobile-first site alongside an automated social content engine that tags dispensaries by name with real prices. The social posts create FOMO. The site captures intent. The dispensaries come to us. Revenue follows attention. Hoodie Analytics has $9.4M and 36 employees but they're building Nielsen for cannabis — national, enterprise-priced, brand-first. We're building GasBuddy for weed — local, free, consumer-first. They can't go free (VC needs revenue). They can't go local (national focus). They can't move fast (committee decisions). We have a 6-12 month window before their High Times play reaches MA with any depth. He who owns the consumer demand, owns the industry.

---

## 2. Step 0: The Top 500

**GPID is not a byproduct. It is the foundation. Without accurate product matching, every comparison is a liability.**

A consumer who drives 20 minutes because GLASS matched a 1g pre-roll to a 3.5g flower will roast us on Reddit and never come back. One bad viral screenshot kills us faster than Hoodie ever could.

### Why 500 and Not 118,000

We have 118,392 products in the database. Most are unverified, inconsistently named, and cross-platform matched by fuzzy logic alone. Publishing all of them as "comparable" is a credibility time bomb.

500 products, hand-verified, is enough to:
- Cover what 80% of consumers actually search for
- Demonstrate the comparison value prop on social content
- Generate hundreds of price comparison cards
- Power city/category landing pages for SEO
- Prove the thesis without risking trust

### How to Build the Top 500

**Week 1 — Query & Select (Day 1-3):**

```sql
-- Find the most ubiquitous products across MA dispensaries
SELECT 
  normalized_name,
  brand,
  category,
  weight,
  COUNT(DISTINCT operator_id) as store_count,
  COUNT(DISTINCT source_platform) as platform_count,
  AVG(price) as avg_price,
  MIN(price) as min_price,
  MAX(price) as max_price
FROM prices p
JOIN products prod ON p.product_id = prod.id
WHERE p.scraped_at > NOW() - INTERVAL '7 days'
GROUP BY normalized_name, brand, category, weight
HAVING COUNT(DISTINCT operator_id) >= 5
ORDER BY store_count DESC
LIMIT 600;  -- Pull 600, verify down to 500
```

**Week 1 — Hand Verification (Day 2-5):**

For each of the top 600 candidates:
1. Confirm the product actually exists on 2+ platforms (spot-check Dutchie + Weedmaps live menus)
2. Verify that cross-platform matches are the SAME product (same brand, same strain, same weight, same form factor)
3. Assign a canonical GPID: `{brand_slug}_{strain_slug}_{weight}_{category}` (e.g., `pax_era_blue_dream_0.5g_vape`)
4. Flag any product where the match is ambiguous — cut it. Better to have 450 perfect matches than 500 with 50 questionable ones.
5. Document the verification in a `gpid_verified` table with `verified_by`, `verified_at`, `confidence_level`

**The messaging:** "We track the 500 most popular cannabis products in Massachusetts. Every match is verified. Every price is real."

This is not a limitation — it's a trust signal. It says: "We don't show you bullshit data. We show you verified data." Expand by 50-100 products per week as matching improves.

### How This Beats Hoodie

Hoodie has 30M product variants in their catalog. But their matching is brand-side (brands upload data). They don't cross-reference the same product across Dutchie, Weedmaps, and Jane to find price discrepancies at the store level. **We do.** Our 500 verified GPIDs are more useful to a Massachusetts consumer than their 30 million unmatched national variants.

---

## 3. The Consumer Product

### What We Ship: GLASS Prices

**One product. One URL. One mission:** Show every Massachusetts cannabis consumer the best price for what they want, near where they are.

**Domain:** `glassintel.xyz/prices` (or `prices.glassintel.xyz`)

### Layer 1: Search + Compare (Core Utility)

Consumer enters what they want + where they are → GLASS returns every dispensary carrying it, sorted by price with distance.

- Search by product name, strain, category, or brand
- Filter by distance (5/10/25 mi), category, price range
- Results show: product name, dispensary name, **post-tax out-the-door price**, distance, **"Verified X hours ago"**
- **Prices older than 24 hours are auto-hidden** from default results (expandable with "Show older prices" toggle)
- **"Report Out of Stock" button** on every listing
- **No login required.** Zero friction. Instant value.

### Layer 2: Auto-Generated Pages (SEO Machine)

Every dispensary, every verified product, every city gets a page:

- **385+ dispensary pages:** Full menu (Top 500 verified products first, then unverified with disclaimer), price rankings vs. nearby competitors, price history charts
- **500+ product pages (GPID-powered):** Same product across all stores, sorted by post-tax price, with price history
- **City/category pages:** "Best flower prices in Boston today," "Cheapest vapes near Cambridge"
- **Each page contains unique synthesized data** that Google can't find elsewhere: price history charts, distance calculations from population centers, THC accuracy scores, price volatility indices

### Layer 3: Price Alerts (Retention Hook)

After first use, consumer can set a watch:
- "Tell me when any 1/8 drops below $30 within 10 miles of Somerville"
- "Alert me when [strain] is back in stock near me"
- Delivery: SMS (Twilio) or email
- These alerts are our insurance policy against social platform bans — owned audience.

### The User Journey

```
1. Consumer sees GLASS social post on X/Reddit/TikTok:
   "Same cart: $52 at Store A, $31 at Store B. 
   They're 3 miles apart. Out-the-door price, tax included."
   
2. Taps link → lands on GLASS comparison page for that product
   
3. Sees "Verified 4 hours ago" timestamps on every price
   
4. Searches for their usual products → discovers they've been overpaying
   
5. Sets a price alert for their top 3 products
   
6. Next week, gets SMS: "Price drop! Blue Dream 1/8 now $32 at [Store]"
   
7. Screenshots the comparison → sends to group chat
   
8. Friends visit → loop repeats
```

### How This Beats Hoodie

Hoodie's High Times consumer play is "discover this brand's product near you" — driven by brand marketing budgets. GLASS is "find the cheapest verified price near you" — driven by consumer intent. Their model: brand pays, consumer discovers. Our model: consumer searches, dispensary competes. Different economics, different winners. When a consumer Googles "cheapest Blue Dream near Worcester," GLASS comes up. High Times doesn't — because they're not optimizing for price comparison.

---

## 4. The Four Landmines

### Landmine 1: GPID False Matches → "Drive of Shame"

**The risk:** We match a 1g pre-roll with a 3.5g flower. Consumer drives 20 minutes. Consumer roasts us on Reddit. We're dead.

**Engineering solution:**

1. **Launch with Top 500 only.** Every cross-platform match hand-verified before it goes live. No algorithmic matches shown to consumers until accuracy exceeds 98%.

2. **Hard constraints in matching algorithm:**
   - Weight MUST match exactly (no 1g ↔ 3.5g)
   - Category MUST match exactly (no flower ↔ pre-roll)
   - Brand MUST match (fuzzy OK: "Pax Era" = "PAX - Era")
   - Strain must be semantically equivalent (allow "Blue Dream" = "Blue Dream #3", reject "Blue Dream" ≠ "Blue Dream CBD")

3. **Confidence tier display:**
   - ✅ **Verified Match** (hand-checked) — shown in default comparison
   - ⚠️ **Likely Match** (algorithmic, >95% confidence) — shown with disclaimer: "This appears to be the same product. [Report if wrong]"
   - Hidden: anything below 95% confidence never shown to consumers

4. **"Not the same product?" button** on every comparison. One-tap correction feeds GPID model.

5. **GPID expansion process:** Add 50-100 products/week. Each batch is verified before going live. Never sacrifice accuracy for breadth.

### Landmine 2: Pre-Tax vs. Post-Tax Price Chaos

**The risk:** MA dispensaries inconsistently show pre-tax vs. tax-included prices. A "Store A is $10 cheaper" card that's wrong after tax = instant credibility death.

**Engineering solution:**

1. **All displayed prices are post-tax, out-the-door.** This is non-negotiable.

2. **MA cannabis tax calculation:**
   - State excise tax: 10.75%
   - State sales tax: 6.25%
   - Local option tax: up to 3%
   - Total: 17% - 20% depending on municipality
   
3. **Tax detection per store:**
   - Build a `store_tax_profile` table: `{operator_id, municipal_tax_rate, prices_include_tax: boolean}`
   - For Dutchie stores: Dutchie's API/cart simulation reveals whether listed prices include tax
   - For Weedmaps stores: Cart simulation at checkout reveals tax handling
   - For each store, run a one-time cart test: add item, proceed to checkout, observe if tax is added. Store the result.
   - Default assumption: prices are PRE-tax (safer — we'll show a higher out-the-door price, which under-promises)

4. **Display format:**
   ```
   Blue Dream 1/8 — Green Thumb Dispensary
   $38.00 out the door (incl. tax)
   ├── Menu price: $32.00 + $6.00 tax
   └── Verified 3 hours ago
   ```

5. **Municipal tax rate database:** Build from CCC data and MA DOR. 351 municipalities, each with a known local option tax rate (0%, 1%, 2%, or 3%). This is public data.

6. **Social card format always says "out-the-door price, tax included."** Every card. Every time. This becomes our brand — the honest price.

### Landmine 3: Data Freshness → "Sold Out Rage"

**The risk:** Cannabis deals sell out in 3 hours. Our scraper runs daily. Consumer drives to store for a deal that's gone. GLASS takes blame.

**Engineering solution:**

1. **"Verified X hours ago" on every single price.** Not hidden in metadata — displayed prominently next to the price. Color-coded:
   - 🟢 Verified < 4 hours ago
   - 🟡 Verified 4-12 hours ago  
   - 🔴 Verified 12-24 hours ago
   - ⬛ **Hidden by default** > 24 hours (expandable: "Show older prices — may be outdated")

2. **"Report Out of Stock" button** on every listing. One tap, no login required. When 2+ reports come in → auto-flag the listing with "⚠️ May be out of stock (reported by shoppers)."

3. **Scraper frequency tiers:**
   - **Top 50 dispensaries** (by consumer traffic on GLASS): scrape every 4 hours
   - **Next 150:** scrape every 8 hours
   - **Remaining:** scrape every 12-24 hours
   - **"Watched" products** (products with active price alerts): scrape stores carrying them every 4 hours
   - **Deals/promotions:** when a price drops >20%, trigger a re-scrape 4 hours later to verify it's still active

4. **Consumer expectations management:**
   - Site-wide banner: "Prices are verified throughout the day. Always confirm with the dispensary before making a trip."
   - On social cards: "Prices as of [timestamp]. Call ahead to confirm."
   - In alerts: "Price verified [X] hours ago. Deals move fast — call [phone] to hold."

5. **Adaptive frequency from feedback:** If a store's prices get reported wrong frequently (via feedback system), auto-increase scrape frequency for that store. (See Feedback System Plan §5.4.)

### Landmine 4: SEO Sandbox → Social-First for 3-6 Months

**The risk:** Google sandboxes new domains for 3-6 months. Month 1-2 organic search traffic = near zero. If we depend on SEO for traffic, we starve.

**Engineering solution:**

1. **Month 1-3 traffic strategy: 100% Social + Reddit + Direct.**
   - Zero expectation of Google traffic. Plan for it, don't depend on it.
   - All traffic comes from: X posts, Reddit (r/bostontrees 32K members), TikTok, group chats, word of mouth, newsletter

2. **Build for SEO from Day 1 anyway** — so when the sandbox lifts, we're ready:
   - Every page has unique synthesized data Google can't find elsewhere:
     - Price history charts (we're the only source of historical cross-platform cannabis pricing in MA)
     - Distance calculations from major population centers
     - THC Accuracy Score (cross-referenced CCC lab data — unique to us)
     - Price volatility index (how much this product's price swings)
     - Store comparison tables with post-tax normalization
   - Server-side rendering (Next.js SSR) for all pages — Google can crawl them
   - Proper meta tags, Open Graph cards, structured data (Product schema)
   - Sitemap submitted to Google Search Console on Day 1
   - Internal linking structure: every product page links to dispensary pages, every dispensary page links to city pages, every city page links to category pages

3. **Content that escapes the sandbox faster:**
   - "30% of MA Dispensaries Inflate THC Numbers" → long-form data journalism piece → if Boston Globe or MassLive links to it, that backlink accelerates indexing
   - Weekly "MA Cannabis Price Index" → the kind of original research Google's Helpful Content algo rewards
   - Reddit posts that link to GLASS pages → organic backlinks from a high-DA domain

4. **Email + SMS list = algorithm-proof audience:**
   - Newsletter subscribers from Day 1 ("The MA Weed Report" — weekly deals, data)
   - SMS alert subscribers from Week 3
   - These are OUR audience. No algorithm can take them away. By Month 3, target: 2,000+ newsletter, 500+ SMS.

### How Solving These Beats Hoodie

Hoodie doesn't solve any of these for Massachusetts consumers. Their High Times integration shows menu prices without post-tax normalization, without freshness indicators, without product match verification. They're a national directory. We're a precision instrument. When a consumer trusts that GLASS's $38 out-the-door price is real and verified 3 hours ago, and Hoodie/High Times shows a $32 price that might not include tax and was scraped who-knows-when — we win.

---

## 5. The Social Content Engine

### Why Social Is the Entire Distribution Strategy

1. **SEO is dead for 3-6 months** (sandbox)
2. **Paid ads are illegal** for cannabis on every major platform
3. **Cannabis consumers live on Reddit and social media** — r/bostontrees has 32K members actively discussing dispensary prices
4. **Price comparison cards are inherently viral** — people love sharing "can you believe this?" moments
5. **Tagging dispensaries forces engagement** — dispensary owners are vain and paranoid about competitors

### The Viral Unit: Price Comparison Cards

A single image, optimized for social sharing:
- A specific product (from the verified Top 500)
- 2-5 dispensary prices side by side
- Price gap highlighted: "Save $18 by going 2 miles further"
- **"Out-the-door price, tax included"** (always)
- **"Verified [timestamp]"** (always)
- `glassintel.xyz` watermark
- Designed for screenshot sharing — works without clicking the link

### The Dispensary Tag Mechanic

**This is the B2B acquisition engine disguised as consumer content.**

Every social post that names a dispensary with a price:
1. Gets noticed by the dispensary (owners vanity-search their business name)
2. Gets noticed by their competitors (paranoia)
3. If the dispensary is the cheapest → they share it (free promotion)
4. If they're the most expensive → they panic and come to claim their page
5. Either way: the dispensary is now aware of GLASS and engaging with it

**Execution:**
- Tag the dispensary's social account when possible (X, Instagram)
- Use the dispensary's exact name in the post text (shows up in name searches)
- Rotate which dispensaries appear in posts — no store should feel targeted, but every store should see themselves eventually

**The "Claim Your Page" hook:**
- Every dispensary page on GLASS has: "Own this dispensary? Claim your page to update info, correct prices, and see analytics."
- After a social post names a dispensary, their page gets traffic
- The dispensary sees the traffic (or hears about it) and claims the page
- Claiming the page = first engagement with GLASS = funnel entry

### Content Calendar (Automated)

| Format | Example | Frequency | Platform |
|--------|---------|-----------|----------|
| **Price Gap Shock** | "Same cart: $28 vs $54, 3 miles apart" | Daily | X, Reddit, TikTok |
| **Best Price by City** | "Best $30 eighth in Boston right now" | Daily | X, Instagram |
| **Price Drop Alert** | "[Strain] just dropped $55→$38 at [Store]" | As they happen | X, SMS |
| **Weekly Roundup** | "Top 10 price drops this week in MA" | Weekly | Newsletter, X, Reddit |
| **Category Deep Dive** | "We checked every vape cartridge price in Massachusetts" | Weekly | Reddit, Blog |
| **THC Accuracy Exposé** | "These 5 dispensaries inflate THC numbers the most" | Monthly | Reddit, Blog, Press pitch |
| **MA Price Index** | "Average flower price fell 4% this month — here's the data" | Monthly | Newsletter, Blog, Press |

### Automated Pipeline

```
6:00 AM — Scraper data lands in DB (existing pipeline)
    ↓
6:30 AM — Content Agent runs queries:
    - Top 5 price gaps by city (verified Top 500 products only)
    - Biggest price drop overnight
    - New products added to stores
    - Category price leaders
    ↓
7:00 AM — AI generates:
    - 6-8 price comparison cards (image templates + data)
    - Social copy per platform (X = data-forward, TikTok = hook-driven)
    ↓
7:30 AM — Queue in scheduler
    ↓
8:00 AM — Randy reviews (10 min). Approves/rejects/edits.
    ↓
Posts deploy: 9am, 12pm, 5pm (staggered across platforms)
```

### Distribution Channels (Priority Order)

1. **X (Twitter)** — Safest for cannabis content. Start here. 2-3 posts/day.
2. **Reddit (r/bostontrees)** — 32K members. Post genuine data analysis, not promotion. Weekly deep dives.
3. **TikTok/Reels** — Charts, maps, text overlays. NO product imagery. "Data storytelling." 1-2/day.
4. **Newsletter** — "The MA Weed Report" — weekly deals, data highlights, price index. Owned audience.
5. **SMS alerts** — Price drops on watched products. Highest engagement channel.
6. **Instagram** — Riskiest. Data visualizations only. Treat as expendable.

### How This Beats Hoodie

Hoodie's consumer distribution is through High Times editorial content → embedded shopping links. That's a low-intent discovery model. Our model is high-intent: consumer sees a price comparison that makes them angry about overpaying → clicks through to search for their products → sets alerts → becomes a repeat user. High Times hopes readers casually shop. We make consumers actively hunt for deals. Intent beats discovery.

---

## 6. The THC Accuracy Score — The Nuclear Moat

### What It Is

Cross-reference CCC's 298,000-row lab testing dataset (actual tested THC/THCA levels from licensed labs) against live dispensary menu claims. Flag every discrepancy.

### Why This Is Devastating

- **Nobody else has this.** Hoodie doesn't integrate state lab data. Lit Alerts doesn't. Headset doesn't. Weedmaps and Leafly show whatever the dispensary claims.
- **It's a consumer protection story.** "30% of MA dispensaries inflate THC numbers" is a headline that writes itself.
- **It gets press coverage.** Boston Globe, MassLive, WGBH — they all want data-driven cannabis stories. This is investigative journalism powered by public data.
- **It builds regulatory credibility.** CCC cares about label accuracy. GLASS becomes the watchdog they never had the resources to build.
- **It forces dispensaries to claim their page.** A dispensary that sees their THC Accuracy Score is 72/100 will immediately claim their page to see the details and contest/correct it.

### How to Build It

**Data sources:**
1. CCC `testing-thc-thca.csv` — 298K rows of lab test results (product name, brand, tested THC%, tested THCA%, lab name, test date)
2. Live menu data from scrapers — menu-listed THC% for each product

**Matching process:**
1. Match CCC lab records to GPID products using brand + product name fuzzy matching
2. For each matched product, compare: `lab_tested_thc` vs. `menu_claimed_thc`
3. Flag discrepancies:
   - **Green:** Menu claim within ±2% of lab result (reasonable batch variation)
   - **Yellow:** Menu claim 2-5% higher than lab result (questionable)
   - **Red:** Menu claim >5% higher than lab result (likely inflated)

**Dispensary-level score:**
```
THC_Accuracy_Score = (products_within_2pct / total_matched_products) × 100
```
A dispensary where 85% of products match lab data within 2% scores 85.

**Display:**
- On every dispensary page: "THC Accuracy Score: 85/100 — 85% of this store's THC claims match lab testing data within 2 percentage points."
- On product pages: "Menu says 28% THC. Lab tested: 24.3% THC. Difference: +3.7%"
- Methodology page: fully transparent. How we calculate, what data we use, caveats (batch variation, testing date gaps).

### The Press Play

**Target:** Boston Globe (cannabis beat reporter), MassLive, CommonWealth Beacon, WGBH

**Pitch:** "We analyzed 298,000 lab test results from the CCC and cross-referenced them with live dispensary menus. Here's what we found." Provide:
1. The headline stat: "X% of MA dispensaries list THC percentages that exceed lab-tested results by more than 5 points"
2. The worst offenders (anonymized in the pitch, named in the data)
3. Interactive tool: link to GLASS where consumers can check any dispensary
4. Expert context on why THC inflation matters (consumer gets a weaker product than advertised)

**Timing:** Month 2 (after site is live and stable). Not before.

**Expected result:** One article in a major MA outlet → 10,000-50,000 visits in a week → GLASS goes from "some new website" to "the cannabis watchdog." This is the kind of press Hoodie can't buy because they don't have state-level lab data integration.

### How This Beats Hoodie

Hoodie's entire model is built on serving brands. They would NEVER publish data showing that brands inflate THC numbers — their clients would leave. GLASS has no brand clients to lose. We can be the honest broker because our revenue comes from consumer attention, not brand subscriptions. This is a structural advantage that gets stronger the more data we publish.

---

## 7. Battle Plan: Hoodie

### Know the Enemy

| Dimension | Hoodie | GLASS |
|-----------|--------|-------|
| **Funding** | $9.4M, 15 investors | $0 for GLASS |
| **Team** | 36 employees, IRI/Nielsen alumni | 1 person + AI agents |
| **Data** | 10K+ dispensaries, 30M variants, 6yr history | ~385 MA dispensaries, 118K products, weeks of data |
| **Consumer play** | High Times partnership (Dec 2025) | Social content engine + Reddit |
| **Revenue model** | Enterprise $1K-5K+/mo | Free core, spoke revenue |
| **Local depth** | National, generic | MA-specific, CCC-integrated |
| **Product matching** | Brand-side catalog | Consumer-side cross-platform GPID |
| **Fulfillment** | None | Delivered (delivery), Cue (incentives), AC (processing) |

### Feature-by-Feature: How We Win

| Their Strength | Our Counter | Why We Win |
|---------------|-------------|-----------|
| **30M product catalog** | Top 500 hand-verified GPIDs | Their 30M are unverified variants. Our 500 are guaranteed accurate matches. Consumer trusts accuracy over volume. |
| **High Times partnership** | Social Content Engine + Reddit | High Times = low-intent discovery. GLASS = high-intent price comparison. When consumer Googles "cheapest Blue Dream near me," we win. |
| **Hoodie Connect (free retailer program)** | Free operator intelligence + consumer traffic | Hoodie Connect gives retailers "enhanced exposure." We give retailers FREE competitive intelligence + 25K consumers already comparing their prices. More valuable. |
| **10,000+ dispensary coverage** | 385 MA dispensaries, deep | A Massachusetts consumer doesn't need 10,000 stores. They need every store within 25 miles with accurate, tax-included, timestamped prices. Depth beats breadth. |
| **Foot traffic data** | Consumer search intent data | They know who walks in. We know what consumers WANT before they walk in. Search intent > foot traffic for operator pricing decisions. |
| **6 years of data history** | Price history from Day 1 (grows over time) | We can't replicate their history. But for a consumer checking today's price, freshness matters more than history. Our "verified 3 hours ago" beats their undated listing. |
| **POS/ERP integrations** | Community feedback system + operator claims | They get data from POS systems (voluntary). We get corrections from consumers and operators (incentivized by accuracy). Two paths to the same goal — ours is cheaper and builds community. |
| **Enterprise pricing models** | AI Margin Engine (free in core tier) | They show you data. We tell you what to DO. "Lower Sour Diesel by $3 to gain +12 units/week" is more valuable than a dashboard. |

### Timeline Pressure: What We Must Ship Before Hoodie Notices

| Deadline | What | Why |
|----------|------|-----|
| **Week 2** | Consumer site live with Top 500 products | Establish presence before Hoodie Connect reaches MA |
| **Week 4** | 25+ dispensary pages claimed | Create switching costs — once operators are managing their GLASS page, they won't switch to Hoodie Connect |
| **Month 2** | THC Accuracy Score live + press coverage | Establish watchdog credibility Hoodie can't touch |
| **Month 3** | 50K+ monthly consumers | Consumer traffic makes us un-ignorable. Dispensaries NEED to be on GLASS. |
| **Month 4** | First Cue brand deals | Revenue from spoke that Hoodie can't replicate |
| **Month 6** | 100+ claimed dispensaries, 25K+ newsletter | At this point, even if Hoodie launches a free MA product, we've locked in the operator relationships and consumer habit |

### If Hoodie Enters MA Aggressively

**Trigger signals to monitor:**
- Hoodie hires someone in Boston/MA
- High Times Local launches a Boston/MA edition (they're planning Denver, Phoenix, Chicago for March 2026)
- Hoodie Connect starts signing up MA dispensaries (check monthly)
- Hoodie publishes MA-specific reports

**Response playbook:**
1. **Immediate:** Publish "GLASS vs. Hoodie for MA operators" comparison: free vs. paid, CCC integration, delivery integration, local depth, THC Accuracy Score
2. **Week 1:** Accelerate outreach to remaining unclaimed dispensaries. "Lock in your free Founding Partner status before the national players arrive."
3. **Month 1:** Double down on features Hoodie can't match: THC Accuracy Score, Threat Radar, Delivery Toggle, local regulatory alerts
4. **Nuclear:** "Hoodie charges $1,000+/month for data. GLASS is free. We integrate with CCC. We verify every price. They don't." Repeat on every channel.

---

## 8. Community Data Moat

### The Feedback System

GLASS's accuracy improves with every user interaction. This is the Wikipedia play for cannabis pricing.

**Core loop:**
```
Scraper collects data → Consumer/Operator spots error → Submits correction
    → Correction validated (trust scoring + cross-reference) → Data improves
    → Scraper learns (frequency adjustments, parser fixes) → Fewer errors
    → Users trust GLASS more → More users → More corrections → Better data
```

### Consumer Feedback (Frictionless)

- **"⚑ Wrong price?"** on every price listing. One tap → enter correct price → done. No login required.
- **"Report Out of Stock"** button. One tap. No login.
- **"Not the same product?"** on comparison pages. One tap.
- **"Was this helpful?"** thumbs up/down after using a comparison.

### Operator Feedback (Powerful)

Once a dispensary claims their page:
- **Inline price editing** — click any price, type the correct one, save. Auto-applies immediately.
- **Bulk menu upload** — CSV/Excel with our template, or paste Dutchie/WM admin URL for auto-pull.
- **"Flag as discontinued"** — one-tap removal of stale products.
- **"Request re-scrape"** — trigger a priority scrape within 30 minutes.

### Trust Scoring

| Tier | Who | Auto-Apply? |
|------|-----|-------------|
| **T0: Anonymous** | No account | Never — stored for pattern analysis |
| **T1: Authenticated** | Logged in user | After 3+ agreeing reports |
| **T2: Verified Consumer** | 5+ accurate corrections, >80% accuracy rate | After 2+ agreeing reports |
| **T3: Claimed Operator** | Verified dispensary owner/manager | Immediate (own store), standard review (other stores) |

### GPID Crowdsourcing

Community product match voting becomes GPID training data:
- After 500+ labeled pairs → retrain matching model
- User votes that "Blue Dream 3.5g" at Store A = "Blue Dream 1/8" at Store B are high-signal positive pairs
- User votes that "Blue Dream" ≠ "Blue Dream CBD" are high-signal negative pairs
- Model improves → expand verified catalog from 500 → 1000 → 5000

### Moat Timeline

| Month | Moat Strength | What's Happening |
|-------|---------------|-----------------|
| 1-2 | Weak | Few corrections, manual review. Data quality = scraper quality. |
| 3-6 | Growing | Auto-apply working. Operators claiming pages. Error rate dropping. |
| 6-12 | Moderate | GPID model trained on user data. Scraper frequency optimized per store. |
| 12+ | Strong | Community corrections > scraper volume for some data. Self-reinforcing. |

### How This Beats Hoodie

Hoodie has 36 employees maintaining their data. We have (eventually) 50,000 consumers and 100+ operators maintaining ours. Community-verified data at scale beats any internal team. And it gets better every day, not just when they hire.

---

## 9. Vertical Integration Weapons

These are the spokes that generate revenue and create lock-in that Hoodie, Headset, Lit Alerts — nobody — can replicate. Intelligence without action is a report. Intelligence with action is a platform.

### Delivered — Delivery-as-a-Service

**What:** Delivered Inc. holds license MD1303 (exclusive social equity delivery license until 2029). GLASS operators can toggle delivery on/off from their dashboard.

**Consumer integration:** "Get it delivered" button on every product page. Consumer clicks → order routed to Delivered → delivered from nearest carrying dispensary.

**Why it matters:** Hoodie can't do delivery. Lit Alerts can't do delivery. No data platform has fulfillment. This converts GLASS from "nice data" to "revenue channel" for operators.

**Revenue:** 15% of GMV through Delivered.

**Timeline:** Month 4-5 integration (after consumer traffic justifies it).

### Cue — Brand-Funded Budtender Incentives

**What:** Brands pay to incentivize dispensary staff to recommend their products. Operators pay $0. Brands get data on redemptions.

**Consumer integration:** "Featured" products in search results and on category pages. Clearly labeled as sponsored.

**Why it matters:** Brands CANNOT advertise cannabis on social media or Google. GLASS is one of the only channels to reach high-intent cannabis consumers. Enormously valuable.

**Revenue:** $500-$2,000/month per brand. Target: 5 brands by Month 6 = $4,000/mo.

**Timeline:** Month 3-4 pilot with AC (Advanced Cultivators, existing Roviq client).

### AC Toll Processing — White-Label Manufacturing

**What:** Consumer demand data from GLASS reveals what products the market wants but can't find. AC Toll Processing fills the gap — cultivators send biomass, AC produces white-label products.

**Why it matters:** GLASS data tells cultivators "the market wants more $30 eighths of indica flower" → AC produces them → Delivered distributes them. Full vertical integration.

**Revenue:** Per-unit fee + referral commission.

**Timeline:** Month 6+ (needs consumer demand data to be meaningful).

### Roviq — Agency Upsell (Zero Outbound)

**What:** The GLASS Score creates the anxiety. Roviq sells the solution. A dispensary sees their score is 58/100 and competitors are at 82. They want to fix it. They come to us — no cold call required.

**Services:** Pricing strategy, menu optimization, content/social, full marketing retainer ($2,500/mo+).

**Revenue:** 2-3 agency clients from GLASS by Month 6 = $5,000-7,500/mo.

### How This Ecosystem Beats Hoodie

Hoodie sells data. We sell outcomes. A Hoodie dashboard tells you "competitor prices dropped." GLASS tells you "lower Sour D by $3" (Margin Engine) → "brand X will pay $2/unit to offset the margin hit" (Cue) → "turn on delivery to capture the customer who won't drive to you" (Delivered). Data → Recommendation → Incentive → Fulfillment. One platform. Nobody else has this pipeline.

---

## 10. Revenue Model

### What Survives Hoodie Competition

Revenue streams ranked by defensibility against a well-funded competitor entering our market:

| Stream | Price | Defensibility vs. Hoodie | Why |
|--------|-------|------------------------|-----|
| **Cue (brand incentives)** | $500-2K/mo per brand | 🟢 Very High | Hoodie serves brands as CLIENTS — they can't also run a brand incentive marketplace. Structural conflict. |
| **Delivered (delivery)** | 15% GMV | 🟢 Very High | License MD1303 is exclusive until 2029. Can't be replicated without a license. |
| **AC Toll (processing)** | Per-unit fee | 🟢 Very High | Physical manufacturing. Hoodie is software-only. |
| **Roviq (agency)** | $2,500+/mo | 🟢 High | Relationship-based. Our clients know us. |
| **Premium Claimed Pages** | $199/mo | 🟡 Medium | Hoodie Connect offers free exposure. But our page includes analytics + competitive intelligence + consumer traffic metrics they don't provide. |
| **Consumer Demand Reports** | $299/mo | 🟡 Medium | Hoodie has foot traffic data. But we have search intent data from consumers actively looking to buy. Different signal, arguably more actionable. |
| **Brand Placement** | $500-2K/mo | 🟡 Medium | Hoodie/High Times also sells brand visibility. Differentiate with local audience + verified price data context. |

### 6-Month Revenue Projection (Conservative)

| Month | Premium Pages | Brand Placement/Cue | Delivered | Roviq Upsell | Total |
|-------|-------------|---------------------|-----------|-------------|-------|
| 1 | $0 | $0 | $0 | $0 | **$0** |
| 2 | $0 | $0 | $0 | $0 | **$0** |
| 3 | $600 | $0 | $0 | $0 | **$600** |
| 4 | $1,200 | $1,500 | $0 | $0 | **$2,700** |
| 5 | $2,000 | $3,000 | $1,500 | $2,500 | **$9,000** |
| 6 | $3,000 | $4,500 | $3,000 | $5,000 | **$15,500** |

**Month 6 MRR target: $15,500.** If consumer traffic exceeds 75K monthly, these numbers 2-3x.

### Year 1 Projection (Aggressive but Possible)

- 50+ operators on free tier, 15+ on premium
- 10+ brands on Cue
- Delivered integrated with 10+ stores
- 3-5 Roviq agency clients from GLASS
- **Year 1 total: $120,000-$200,000**

### Revenue Stream NOT Dependent on Consumer Traffic

If the consumer thesis fails (kill criteria hit), we still have:
- Roviq agency revenue (existing)
- AC toll processing (existing relationship)
- Delivered delivery (existing partnership)
- B2B operator intelligence (pivot to GLASS-PLAN.md original model)

The consumer layer accelerates everything but isn't the only path to revenue.

---

## 11. 90-Day War Plan

### Phase 1: "The Foundation" — Weeks 1-2 (Feb 14 – Feb 27)

**Goal:** Consumer site live with Top 500 verified products. Social content engine running.

| Day | Deliverable | Owner |
|-----|------------|-------|
| 1 | Create @glassintel accounts on X, TikTok, Instagram, Reddit | Randy |
| 1 | **FIX WEEDMAPS SCRAPER** (94% failure rate is catastrophic) | AI Agent (Codex 5.3) |
| 1-3 | Build Top 500 GPID catalog: query, select, hand-verify | Randy + AI Agent |
| 1-3 | Build tax normalization layer: municipal tax rates + store tax profiles | AI Agent (Codex 5.3) |
| 1-3 | Build consumer MVP frontend: search → post-tax results → store pages | AI Agent (Kimi K2.5) |
| 1-3 | Build consumer API endpoints: search, compare, store pages | AI Agent (Codex 5.3) |
| 3-5 | Build price card generator: DB query → image template → social-ready cards | AI Agent |
| 4-5 | Generate first 30 social posts from Top 500 data. All cards show post-tax prices + timestamps. | AI Agent |
| 5-6 | Deploy consumer site at glassintel.xyz/prices | AI Agent |
| 6-7 | Randy reviews first social batch, calibrates tone | Randy |
| 7 | Begin posting: 2-3/day on X, daily on TikTok | Automated |
| 8-10 | Build auto-generated dispensary page template (385+ pages) | AI Agent |
| 8-10 | SEO setup: meta tags, OG cards, structured data, sitemap | AI Agent |
| 10-12 | Build city/category landing pages (50+ pages) | AI Agent |
| 12-13 | Fix Dutchie scraper failures (40/235 failing) | AI Agent (Codex 5.3) |
| 13 | Seed r/bostontrees: "I compared prices at every dispensary in MA. Here's the data." | Randy |
| 14 | **CHECKPOINT** | Review |

**Week 2 Success Criteria:**
- [ ] Consumer site live with Top 500 verified products
- [ ] All prices displayed post-tax with "Verified X hours ago"
- [ ] Weedmaps scraper fixed (>80% success rate)
- [ ] 385+ dispensary pages indexed
- [ ] Social posting active (2-3/day)
- [ ] Reddit seed post published
- **Target: 1,000+ site visitors in Week 2**

### Phase 2: "The Hooks" — Weeks 3-4 (Feb 28 – Mar 13)

**Goal:** Retention mechanics live. Dispensaries start noticing.

| Day | Deliverable | Owner |
|-----|------------|-------|
| 15-17 | Price Alert system: email + SMS (Twilio) | AI Agent (Codex 5.3) |
| 15-17 | "Report Wrong Price" + "Report Out of Stock" buttons on all listings | AI Agent |
| 18-20 | "Claim Your Page" flow: name, email, phone verification, basic dashboard | AI Agent |
| 18-20 | Price history charts on product and dispensary pages | AI Agent |
| 20-22 | iHeartJane scraper (semi-public API, +50-80 new stores) | AI Agent (Codex 5.3) |
| 21-23 | Launch "The MA Weed Report" weekly newsletter (consumer-focused) | Randy + AI Agent |
| 24-26 | Iterate social content: double down on formats that got engagement | AI Agent |
| 27-28 | "Near Me" geolocation mode + distance sorting | AI Agent |
| 28 | **CHECKPOINT** | Review |

**Week 4 Success Criteria:**
| Metric | Target |
|--------|--------|
| Site monthly visitors | 5,000 |
| Alert subscribers (email + SMS) | 200+ |
| Newsletter subscribers | 500+ |
| Social followers (all platforms) | 2,500+ |
| Dispensary claim requests | 5+ |
| Feedback reports (wrong price, out of stock) | 50+ |

### Phase 3: "The Moat" — Month 2 (Mar 14 – Apr 10)

**Goal:** THC Accuracy Score launches. Press coverage. SEO data unique enough to escape sandbox.

| Week | Deliverable | Owner |
|------|------------|-------|
| 5-6 | GLASS Score: price competitiveness (40%), selection breadth (20%), menu freshness (15%), price stability (10%), THC accuracy (15%) | AI Agent (Codex 5.3) |
| 5-6 | Premium Claimed Page: analytics dashboard, menu correction tools, deal highlighting ($199/mo) | AI Agent (Kimi K2.5 frontend, Codex 5.3 backend) |
| 7 | THC Accuracy Score: match CCC 298K lab rows against menu claims. Build scoring methodology. | AI Agent (Codex 5.3) |
| 7 | Publish THC Accuracy analysis: "X% of MA dispensaries list THC exceeding lab results" | Randy + AI Agent |
| 7-8 | Press pitch to Boston Globe / MassLive with THC accuracy data | Randy |
| 7-8 | Leafly scraper (Camoufox, +20-40 new stores) | AI Agent (Codex 5.3) |
| 8 | Product Finder / Virtual Budtender: quiz → match across all stores, ranked by price | AI Agent |
| 8 | Referral attribution: track clicks from GLASS → dispensary menu pages | AI Agent |

**Month 2 Success Criteria:**
| Metric | Target |
|--------|--------|
| Site monthly visitors | 25,000 |
| Alert subscribers | 1,000+ |
| Newsletter subscribers | 2,000+ |
| Social followers (all) | 10,000+ |
| Dispensary pages claimed | 25+ |
| Premium subscriptions ($199/mo) | 3-5 |
| Press placements | 1+ |

### Phase 4: "The Gravity" — Month 3 (Apr 11 – May 13)

**Goal:** Dispensaries come to us. First real revenue. Cue pilot.

| Week | Deliverable | Owner |
|------|------------|-------|
| 9-10 | Consumer Demand Report for dispensaries: "what consumers in your area search for, what price alerts they set" ($299/mo) | AI Agent |
| 9-10 | Cue pilot: AC (existing client) pays for featured placement in search results + social content | Randy (relationship) + AI Agent (implementation) |
| 10-11 | Weekly MA Price Index Report: public data report, citable by press | AI Agent |
| 11 | Approach CCC with THC accuracy findings | Randy |
| 11-12 | Begin outreach to dispensaries in popular social posts: "Your page is getting traffic. Want to claim it?" | Randy |
| 12 | Expand Top 500 → Top 1000 verified GPIDs based on community feedback data | AI Agent |
| 12 | **90-DAY CHECKPOINT** | Full review |

**Month 3 Success Criteria:**
| Metric | Target |
|--------|--------|
| Site monthly visitors | 50,000-75,000 |
| Alert subscribers | 3,000+ |
| Newsletter subscribers | 5,000+ |
| Social followers (all) | 25,000+ |
| Dispensary pages claimed | 75+ |
| Premium subscriptions | 10-15 |
| Cue brand deals | 1-3 |
| Monthly revenue | $3,000-$8,000 |

---

## 12. Kill Criteria

Honest signals that we're wrong. If these hit, pivot — don't double down on a losing hand.

| Signal | When | Decision |
|--------|------|----------|
| <500 visitors after 2 weeks of social posting | Week 3 | Content strategy is broken. Audit formats. Try Reddit-only. Try different price gap thresholds. |
| <2,000 visitors after 4 weeks | Week 5 | Consumer thesis may be wrong for this market. Test: is it the product or the distribution? Try direct Reddit/forum approach before killing. |
| <5% alert opt-in rate among visitors | Week 4 | Value prop isn't compelling. Test different framing: savings calculator vs. deal alerts vs. price drops. |
| 0 dispensary claim requests after 8 weeks | Week 9 | Consumer traffic isn't creating B2B pressure. Either traffic is too low or dispensaries genuinely don't care about their public pricing. Reassess. |
| <10,000 monthly visitors after 90 days | Week 13 | Strategy isn't working at needed scale. Options: (a) different market (CT/RI), (b) pivot to B2B-first, (c) different content approach, (d) shut down GLASS consumer and focus on Roviq agency. |
| Social accounts banned on 2+ platforms simultaneously | Any time | Pivot to SEO + newsletter + SMS only. Social was accelerant, not foundation. |
| GPID accuracy complaints > 5% of feedback | Any time | Tighten matching criteria. Reduce verified catalog size. Accuracy > breadth. |
| Hoodie launches free MA operator tier | Any time | Activate response playbook (§7). Emphasize: CCC integration, delivery license, THC accuracy, local depth. |

### What Would Kill This Entirely

1. **Scraper data quality is too bad to show consumers.** If we can't show accurate post-tax prices with timestamps, nothing else matters. **Fix the Weedmaps scraper before ANYTHING consumer-facing launches.**
2. **MA consumers simply don't comparison-shop for cannabis.** Possible but unlikely — 73% price collapse since 2020 has made this market extremely price-sensitive.
3. **A platform player (Dutchie/Weedmaps) builds consumer price comparison.** Structurally unlikely — their dispensary clients pay NOT to have price transparency. But if they do, we pivot to being the "independent, honest" alternative.

---

## 13. Day 1 Action List — Monday Morning

Randy, here's what you do when you sit down Monday:

### Hour 1: Accounts & Scraper Triage
- [ ] **Create social accounts:** @glassintel on X, TikTok, Instagram, Reddit. Bio: "Every cannabis price in Massachusetts. Tax included. Verified daily. Stop overpaying."
- [ ] **Check Weedmaps scraper status.** Run it. If >50% failure rate → this is the #1 priority for the day. Spawn Codex 5.3 agent to debug and fix. Nothing consumer-facing ships until this works.

### Hour 2: Top 500 Catalog
- [ ] **Run the Top 500 query** (§2). Pull the 600 most ubiquitous products from the database.
- [ ] **Start hand-verifying.** Open Dutchie and Weedmaps side by side. For each product: same brand? Same strain? Same weight? Same form factor? Mark as verified or cut.
- [ ] **Target: verify 100 products today.** Continue over the next 3 days to reach 500.

### Hour 3: Spawn Build Agents
- [ ] **Spawn Codex 5.3:** "Build tax normalization layer. Create `store_tax_profile` table with `{operator_id, municipal_tax_rate, prices_include_tax}`. Build municipal tax rate database for all 351 MA municipalities. Default all stores to pre-tax assumption. Implement post-tax calculation in the price API."
- [ ] **Spawn Kimi K2.5:** "Build consumer search frontend. Mobile-first. Search box → results list showing: product name, store name, post-tax price (bold), 'Verified X hours ago' timestamp (color-coded green/yellow/red), distance. Filter by distance, category, price range. No auth required. Server-side rendered with Next.js for SEO."
- [ ] **Spawn Content Agent:** "Generate 30 price comparison card templates. Each card shows: specific product name, 2-5 store prices side by side, price gap highlighted, 'Out-the-door price, tax included' label, 'Verified [date]' stamp, glassintel.xyz watermark. Output as image files + social copy for X and TikTok."

### Hour 4: Reddit Strategy
- [ ] **Draft the r/bostontrees post.** It must sound like a real person, not a company: "I've been tracking every dispensary price in Massachusetts for the past few weeks. Here's what I found." Include 3-4 genuinely surprising data points from the Top 500 analysis (biggest price gap, most vs least expensive city, average savings from shopping around).
- [ ] **Do NOT post yet.** Post on Day 13 when the site is live so there's somewhere to send traffic.

### Before You Close the Laptop
- [ ] **Set up Buffer** (or equivalent) for social scheduling
- [ ] **Verify scraper data quality:** Spot-check 20 dispensaries against their live menus. If accuracy is below 85%, fix the pipeline before building anything consumer-facing.
- [ ] **Write a 2-line brief for the MA Weed Report newsletter** (Week 3 launch). Sign up for Beehiiv or Substack. Reserve the name.

---

## Appendix: Key Numbers

| Metric | Current Value | Source |
|--------|--------------|--------|
| Licensed MA retailers | 418 (397 active) | CCC |
| GLASS operators with price data | 385 | Database |
| Daily active scrape coverage | 256 operators (61%) | Scraper logs |
| Total prices in DB | 150,431 | Database |
| Distinct products | 118,392 | Database |
| CCC lab test rows | 298,000 | CCC testing-thc-thca.csv |
| Weedmaps scraper success rate | 6% (CRITICAL) | Last run |
| Dutchie scraper success rate | 83% | Last run |
| r/bostontrees members | 32,000 | Reddit |
| Hoodie funding | $9.4M | PitchBook |
| Hoodie employees | 36 | PitchBook |
| Hoodie dispensaries tracked | 10,000+ | Hoodie website |
| Lit Alerts pricing | $500/mo/market | Lit Alerts website |
| MA cannabis tax range | 17-20% | MA DOR |
| Delivered license | MD1303 (exclusive to 2029) | CCC |

---

## Appendix: The Thesis in One Sentence

**We give Massachusetts cannabis consumers the one thing nobody else does — verified, tax-included, timestamped prices for the same product across every dispensary — and the consumer traffic this creates becomes the gravitational force that pulls dispensaries, brands, and revenue into our orbit.**

---

*This document supersedes all previous strategy documents. When in doubt, execute what's in this document. Everything else is context.*

*Last updated: February 13, 2026*
