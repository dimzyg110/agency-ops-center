# GLASS UX & Data Value Review — Plan A

**Reviewer:** Senior Product Strategist (Independent Analysis)  
**Date:** February 12, 2026  
**Verdict:** The data is real and genuinely valuable, but the platform has critical data quality issues, a misleading flagship feature, and is building the wrong things for the audience it claims to serve.

---

## 1. Data Audit — What Do We Actually Have?

### The Good News
| Table | Rows | Verdict |
|-------|------|---------|
| products | 92,586 | ✅ Real, scraped product data from MA dispensaries |
| prices | 107,175 | ✅ Real pricing observations, mostly from today's scrape |
| operators | 492 | ✅ 197 Dutchie + 282 Weedmaps + 13 unknown |
| ccc_avg_prices | 31,038 | ✅ Rich CCC official price data, 2018-2025, 17 categories |
| ccc_pending_applications | 234 | ✅ Real pending license data with types, cities |
| ccc_plant_activity | 46,863 | ✅ Unused but potentially very valuable |
| ccc_weekly_sales | 71 | ❌ Has rows but ALL values are NULL — completely empty |

### Critical Data Quality Issues

#### 🚨 Issue #1: The Cross-Reference "Killer Feature" Is Comparing Apples to Oranges

The public Market page's flagship feature shows CCC vs GLASS pricing and claims a **509% markup on flower**. This is **flat-out wrong** and will destroy credibility with any operator who sees it.

**What's happening:** CCC reports flower at `$5.81/gram`. GLASS shows `$35.39/unit` (which is a typical eighth or 3.5g price). The cross-reference endpoint divides these directly, producing a meaningless "509% markup" number.

The GLASS avg price per gram (from `price_per_gram` column) is actually `$11.96/g` — so the real markup is about 106% over CCC's wholesale-blended average. Still interesting! But the 509% figure is embarrassing if any operator does the math.

**Fix:** The `/ccc/cross-reference` endpoint needs to either (a) use `price_per_gram` for flower/concentrate, or (b) normalize CCC prices to per-unit equivalents, or (c) clearly label units so users understand the comparison.

#### 🚨 Issue #2: 99.9% of Price Data Is From One Day

```
Feb 5-11:  ~15-20 rows each (seed data from 10 test operators)
Feb 12:    107,500 rows (the first real bulk scrape)
```

This means:
- **Price Movers** (showing 24h changes) has almost no data — only ~130 rows from before today
- **Price Volatility** charts are meaningless with 1 day of data
- **Price War Heatmap** shows nothing
- **Price Ticker** / **Price Cascade** have almost nothing to compare against
- **All "trend" language is fiction right now**

The platform shows "7-day sparklines" that are entirely generated from `generateSparklineData()` — a deterministic pseudo-random function in the frontend. **Those sparklines are fake.**

#### 🚨 Issue #3: Massive Brand Parsing Failures

Top "brands" in the database:
1. **"stock. Order soon."** — 3,818 products (parsing error from low-stock badges)
2. **"Unknown"** — 1,824 products
3. **"510"** — 346 products (vape hardware type, not a brand)
4. **"Flower"** — 299 products (category leaking into brand field)
5. **"Gummies"** — 242 products (product type, not a brand)
6. **"Medical patients only"** — 122 products (access restriction text)
7. **"Pre-Roll"** — 114 products (category)
8. **"Disposable"** — 111 products (product type)

Over 7,000 products (~7.6%) have garbage brand data. This pollutes the Brand Treemap visualization that's shown front-and-center on the Morning Brief. **An operator sees "stock. Order soon." as the #1 brand and immediately loses trust.**

#### 🚨 Issue #4: Misclassified Products

The $1,400 "flower" product is a glass rig. The $999 "flower" is an AeroPay fee. Gift cards, rolling papers, pipes, screens, gravity bongs — all classified as flower, preroll, etc. There are at least:
- 18 items over $500 in "flower" that are glass/accessories
- 49 items under $1 in "flower" that are rolling papers/screens
- These outliers distort every average price calculation

#### 🚨 Issue #5: Only 10 Operators Have Geolocation

The proximity radar, geography page, delivery zones, threat network distance calculations — all depend on lat/lon coordinates. Only **10 operators** (the original seed operators) have this data. That's 2% of the 492 operators.

This means:
- The Proximity Radar is useless for 98% of users
- The Geography/Map page shows almost nothing
- Competitor distance calculations fail silently
- Threat scoring based on proximity is essentially random

#### 🚨 Issue #6: Weekly Sales Data Has No Values

All 71 rows in `ccc_weekly_sales` have NULL for `total_sales`, `adult_use_sales`, `medical_sales`, and `transaction_count`. The Market page's weekly sales chart falls back to hardcoded mock data (`FALLBACK_WEEKLY_SALES`) — those beautiful D3 charts are showing fake numbers. The "Massachusetts did $X.XXB in adult-use sales" calculation is based on fabricated data.

#### 🚨 Issue #7: Sparse Data Tables

- `threats`: Only 6 rows — these appear to be manually written, not sourced from any automated system
- `alerts`: 10 rows (looks like test data)
- `recommendations`: 6 rows
- `watchlists`: 0 rows
- `ccc_demographics`: 0 rows
- `margin_rules`: 5 rows
- `users`: 3 users

### What We Actually Have That's Valuable
1. **92K real products with names, brands (mostly), categories** — this is genuinely hard to assemble
2. **107K price observations** — a real snapshot of the MA market as of today
3. **31K CCC official average prices** spanning 7 years and 17 categories — this is gold
4. **234 real pending license applications** with license type and city
5. **46K plant activity records** — we're not using these AT ALL
6. **293 operators with enough price data** to be analytically useful

---

## 2. Current UX Assessment — Page by Page

### Landing Page
**Grade: B+**  
Clean, professional, the design language is genuinely good. The copper accent color, Geist Mono typography, and restrained layout feel trustworthy. The problem is claims: "Track 2,500+ products across all operators" when we track 92K products — undervaluing ourselves. "Join 50+ Massachusetts operators" — are there really 50 users? We have 3 in the DB.

The four-product ecosystem (GLASS → Budtender → Cue → Delivery) is ambitious and well-framed but risks looking like vaporware when 3 of 4 products are "Coming Soon."

### Onboarding
**Grade: A-**  
This is genuinely well-designed. The 4-step flow (Claim → Market Snapshot → Priorities → Toolkit) is fast and makes the operator feel seen. The search-to-claim experience is smart. The market snapshot showing "competitors nearby" and "active threats" creates immediate value.

**Issues:**
- Market snapshot depends on proximity data which requires lat/lon → only 10 operators have this, so most users will see "0 competitors, 0 threats"
- Priority selection doesn't actually change what's shown in the dashboard
- The "We're already tracking [your dispensary]!" message is powerful but misleading if we only have 1 day of price data for them

### Morning Brief
**Grade: C**  
This is trying to be the daily heartbeat for operators. The layout is beautiful. The problem is almost everything on this page is either mock data, empty, or misleading:

- **Hero stats** ("Products Tracked", "Price Changes 24h"): These calculate from brief data but fall back to fabricated numbers like `2847` and `156`
- **Brand Treemap**: Shows "stock. Order soon." as the dominant brand — immediately kills credibility
- **Category Sunburst**: Works but doesn't tell operators anything actionable
- **Economic Indicators**: "Margin Proxy" is calculated as `45 - avg_price` which is completely made up
- **Strain Stream**: Labeled "strain" but actually shows product names, not strains. And with 1 day of data, there are no "trends"
- **Price Wire summary**: The sparklines are fake (generated from a hash function)
- **Threat Radar summary**: Shows 6 manually-written threats, no automated detection
- **Recommendations**: Shows 6 test recommendations
- **Data Freshness Indicator**: Clever concept, but the freshness data comes from the brief API which may not reflect actual scraper health

**What works:** The visual design, the hierarchy of information, the concept of a morning brief. The Flywheel CTA ("Your top products could reach 3x more customers") is a smart upsell pattern.

### Market Page (Public)
**Grade: B- (concept A, execution D)**  
The *concept* of a public SEO page with free market data to drive signups is excellent strategy. The CCC × GLASS cross-reference is the right unique value proposition.

**Critical problems:**
- The "509% markup" headline claim for flower is wrong (unit mismatch)
- Weekly sales chart shows fake data (all NULLs in DB → falls to mock data)
- The "annualized pace" number is calculated from fake weekly sales
- Demographics section uses hardcoded fallbacks (0 rows in `ccc_demographics`)
- News headlines are hardcoded
- Pipeline data is real but limited (234 applications → good)
- The blurred premium dashboard teaser is a smart conversion technique

### Price Wire
**Grade: C-**  
Has the most complex visualization layer of any page. The problem is temporal.

- **Price Movers (24h)**: With only ~130 pre-today price rows, there are essentially no real "movers"
- **Price Position Matrix**: Actually works — shows real operator avg vs market avg by category. This is the best visualization in the product.
- **Volatility Ribbon**: Needs multi-day data to be meaningful. Currently shows one data point.
- **Proximity Radar**: Only works for 10 operators with lat/lon
- **Price Change Cascade**: No historical data = no cascades
- **Price Ticker**: Same — needs time series data
- **Data table**: Works and shows real data. CSV export is a nice touch.

### Threat Radar
**Grade: D**  
6 manually-written threats. No automated detection. The "AI-powered detection" claim in the subtitle is currently false.

- **Threat Network viz**: Shows generic connections between 20 operators and 6 threats
- **CCC Timeline**: Shows the same 6 threats as timeline events
- **License Pipeline**: Uses the threats table to fabricate pipeline stages — not the real `ccc_pending_applications` table which has actual data
- **The configure alerts button does nothing**

### Competitors
**Grade: C-**  
- Operator Comparison: Pulls 4 random operators and compares them. No user-specific context.
- Market Share Flow: Shows Sankey-style flow but "market share" is calculated from SKU count, not actual sales
- Price War Heatmap: Needs time series data to detect wars

### Geography
**Grade: F**  
Only 10 operators have coordinates. The market terrain map will show 10 dots in a state with 500+ dispensaries. The delivery Voronoi zone visualization covers only these 10 points. This page is non-functional.

### Budtender Page
**Grade: B (as a landing page)**  
Well-designed product marketing page. The mock chat conversation is effective. The embed code concept makes sense as a growth lever. But the actual product doesn't exist yet — this is a waitlist page. Not a problem per se, but it's part of the "more marketing than product" pattern.

### Cue Page
**Grade: B (as a landing page)**  
Clean "coming soon" page. $199/mo pricing teaser is good anchoring. The four features (demand forecasting, inventory optimization, dynamic pricing, brand incentives) are the right features for the market.

---

## 3. The Operator's Perspective

Let me be specific. Meet Maria. She runs a dispensary in Worcester. She's been open 2 years. Her average transaction used to be $62, now it's $48. Three new competitors opened within 5 miles in the last year. She's running Google Ads that cost more every month. She heard about GLASS from another operator.

### What Maria Needs (In Order of Urgency)

**1. "Am I pricing too high or too low right now?"**
She needs to see her actual products compared to the same or similar products at nearby competitors. Not category averages — SPECIFIC products. "Your Blue Dream 3.5g is $45. Three competitors within 5 miles sell it between $35-$40. You're 12% above market."

**Currently GLASS shows:** A broad category matrix (useful but not specific enough) and fake sparklines.

**2. "Who just changed their prices and should I react?"**
She needs push notifications or a prominent alert: "Happy Valley Worcester dropped all their flower prices 15% yesterday." Not a dashboard she has to check — an alert.

**Currently GLASS shows:** Almost nothing (no historical data to compare). The alert system exists in the schema but has 10 test rows.

**3. "Is anyone about to open near me?"**
The 234 pending applications are exactly this data. But Maria doesn't want to parse a table of 234 records. She wants: "There are 4 pending Marijuana Retailer applications in Worcester. Here are their names and status."

**Currently GLASS shows:** The pending applications exist but aren't surfaced in a user-specific way. The Threat Radar has manually written threats, not automated detection from this real data.

**4. "What products are selling everywhere that I don't carry?"**
With 92K products across 492 operators, we can identify products/brands that appear at many competitors but NOT at Maria's store. This is a direct revenue opportunity.

**Currently GLASS shows:** Nothing. This analysis doesn't exist.

**5. "Are my margins in line with the market?"**
She wants to know: "Your average flower margin is 28%. The Worcester market average is 33%. You're leaving money on the table." This requires cost data we don't have, but we can approximate by comparing her prices to the CCC wholesale averages.

**Currently GLASS shows:** A "Margin Proxy" that's literally `45 - avg_price`. Not useful.

### The "Aha Moment" Maria Needs

When Maria logs in, the very first thing she should see is: **"GLASS found 3 things you should know today about YOUR dispensary."** Not generic market data. Not pretty charts. Specific, actionable intelligence about HER business.

Example:
> 🔴 **Price Alert:** Happy Valley Worcester dropped Blue Dream 3.5g from $45 to $38 yesterday. Your price: $45. 2 other Worcester competitors are between $39-42.
>
> 🟡 **New Competition:** A Marijuana Retailer application was filed in Worcester by "Debken Corp." on Dec 18, 2025. This would make 5 retailers within 3 miles of you.
>
> 🟢 **Opportunity:** Jeeter pre-rolls appear at 23 competitors in your area but not on your menu. The avg price is $15.50 with high apparent demand.

THAT is what makes Maria tell another operator about GLASS.

---

## 4. Missed Opportunities

### Things We Could Build Today With Data We Already Have

**A. Product Gap Analysis** (Impact: 🔥🔥🔥🔥🔥)
For any operator, compare their product catalog against competitors. "Brands/products you don't carry that appear at 10+ nearby competitors." This is directly actionable — it tells operators what to order.

Query sketch: Compare `products` at operator X vs products at operators in the same city. Find brands/categories present at others but absent at X.

**B. Price Position by Product** (Impact: 🔥🔥🔥🔥🔥)
Instead of showing category-level averages, match specific products (by brand + name + weight) across operators. "Your Bountiful Farms Wedding Cake 3.5g is $48. Market range: $38-52. Your position: 73rd percentile."

This is entirely possible with current data — products have brand, name, and weight_grams (for 60% of them).

**C. CCC Price Trend Analysis** (Impact: 🔥🔥🔥🔥)
We have 31K CCC avg prices spanning 7 years. This is an incredible time series that NO ONE ELSE is visualizing properly. Show:
- "Flower prices have dropped 42% since 2021"
- "Concentrate margins are the most resilient category"
- Category-over-category comparison curves
- Seasonal patterns (does pricing dip in winter? spike in summer?)

**D. Pending License Threat Scoring** (Impact: 🔥🔥🔥🔥)
For each of the 234 pending applications, geocode the city and show operators: "There are X pending retail applications within Y miles of you. Based on typical CCC processing times (~18 months), expect new competition by [date]."

**E. Brand Portfolio Analysis** (Impact: 🔥🔥🔥)
Which brands are "winning"? Appearing at the most stores, commanding premium prices, available in the most categories. This helps operators decide which brands to prioritize relationships with.

**F. Price-to-THC Analysis** (Impact: 🔥🔥🔥)
31K products have THC data. We could show: "For flower between 20-25% THC, the market avg is $X. Your product at 22% THC is priced at $Y." This is the kind of analysis no one else has.

**G. Plant Activity Intelligence** (Impact: 🔥🔥🔥)
We have 46,863 plant activity records we're not using AT ALL. This is supply-side intelligence — what's being grown, harvested, in the pipeline. Operators who know supply trends before they hit the market have an advantage.

**H. Market Saturation Index** (Impact: 🔥🔥🔥)
Combine operators, pending applications, and population data by city/region to show: "Worcester: 34 active operators, 4 pending applications, population 206K. Saturation index: HIGH. Average revenue per operator declining."

---

## 5. New Feature Proposals — Ranked by Impact × Effort

### Tier 1: Ship This Week (High Impact, Low Effort)

**1. Fix the Cross-Reference (1-2 hours)**
- Update `/ccc/cross-reference` to use `price_per_gram` for flower/concentrate
- Add unit labels to the comparison
- This is your marquee public feature and it's currently wrong

**2. Clean the Brand Data (2-4 hours)**  
- SQL script to fix top offenders: `UPDATE products SET brand = 'Unknown' WHERE brand IN ('stock. Order soon.', 'Medical patients only')` etc.
- Add parser-level filtering for "Low stock" / "Order soon" text
- Strip category-as-brand entries (brand='Flower', brand='Gummies')

**3. Pending Applications by City Alert (4-6 hours)**
- New endpoint: given operator city, return pending applications in that city + adjacent cities
- Show as a card on Morning Brief: "4 new licenses pending in your area"
- This uses REAL data we already have (234 applications)

**4. Kill the Fake Sparklines (1 hour)**
- Remove `generateSparklineData()` — replace with "N/A" or "Collecting data" badges
- Better to show nothing than to show fake trends

### Tier 2: Ship This Month (High Impact, Medium Effort)

**5. Product Gap Analysis (1-2 days)**
- Compare operator's product catalog against same-city competitors
- "Brands available nearby that you don't carry"
- Simple query: brands at competitors where brand NOT IN operator's brands

**6. CCC 7-Year Price Trends Page (2-3 days)**
- Standalone public page with D3 visualizations of CCC avg prices over time
- Category comparison, year-over-year, seasonal patterns
- This is SEO gold — no one else has this as interactive charts
- Data exists and is clean (31K records)

**7. Geocode All Operators (1 day + API costs)**
- Use Google Places or Mapbox geocoding API on the 482 operators without lat/lon
- Fixes Geography, Proximity, Threat scoring, Competitor distance
- Unblocks half the platform's features

**8. Operator-Specific Price Comparison (2-3 days)**
- Match products by brand + name across operators
- Show: "How your products compare to the same products at competitors"
- This is the core value proposition

**9. Real-Time Price Drop Alerts (2-3 days)**
- Compare each scrape run to previous prices
- Send notification when a competitor drops prices significantly
- Requires accumulating 2+ days of scrape data (starts working after day 2)

### Tier 3: Ship Next Quarter (Transformative, Higher Effort)

**10. Plant Activity Intelligence Dashboard (1-2 weeks)**
- Surface the 46K plant activity records
- Show supply pipeline: what's being planted, vegetating, flowering
- Leading indicator of future supply and price pressure

**11. AI-Generated Morning Brief Narratives (1 week)**
- Use LLM to generate natural-language summaries from actual data
- "Flower prices across Worcester dropped 3.2% this week, led by..."
- Replace the mock data approach with real, generated intelligence

**12. Interactive Market Map (2 weeks)**
- Full Massachusetts map with all operators plotted
- Color-coded by avg price, category focus, threat level
- Click to compare any operator against your own
- Requires geocoding fix (#7) first

---

## 6. Quick Wins — Live in a Day

| # | Fix | Time | Impact |
|---|-----|------|--------|
| 1 | Fix cross-reference unit mismatch | 1 hour | Prevents credibility damage on public page |
| 2 | Remove fake sparklines | 30 min | Stops showing fabricated data |
| 3 | Filter garbage brands from Brand Treemap | 1 hour | Prevents "stock. Order soon." from being shown |
| 4 | Show pending applications on Threat Radar | 3 hours | Real data instead of 6 manual threats |
| 5 | Add "Collecting data" states to empty visualizations | 2 hours | Honest UX instead of mock data |
| 6 | Fix Price Wire's "24h changes" to say "since last scrape" | 30 min | Accuracy |
| 7 | Use ccc_avg_prices on Market page instead of hardcoded data | 2 hours | Real 7-year CCC trend data |
| 8 | Remove $0 and $500+ outliers from all price calculations | 1 hour | Cleaner averages |
| 9 | License Pipeline viz should use ccc_pending_applications | 2 hours | 234 real records vs 6 threat records |
| 10 | Remove "50+ operators" claim or substantiate it | 5 min | Honesty |

---

## 7. Data Quality Fixes

### Immediate (Before Any More Users See This)

1. **Cross-reference unit normalization** — Use `price_per_gram` for flower and concentrate in the cross-reference endpoint. CCC reports per-gram; GLASS reports per-unit. The 509% flower markup is a bug, not a feature.

2. **Brand cleaning SQL:**
```sql
-- Fix parsing garbage
UPDATE products SET brand = 'Unknown' WHERE brand IN (
  'stock. Order soon.', 'Medical patients only', 
  '510', 'Flower', 'Gummies', 'Disposable', 'Pre-Roll', 
  'Gummy', 'THC', 'Preroll | 1g', 'Infused Pre-Roll',
  '| Smash Hits', '| Assorted Colors'
);

-- Products that are clearly not cannabis
-- Identify and either re-categorize or flag non-cannabis items
UPDATE products SET category = 'merchandise' WHERE 
  price > 200 AND (
    LOWER(name) LIKE '%rig%' OR 
    LOWER(name) LIKE '%bong%' OR 
    LOWER(name) LIKE '%pipe%' OR
    LOWER(name) LIKE '%gift card%' OR
    LOWER(name) LIKE '%aeropay%' OR
    LOWER(name) LIKE '%puffco%' OR
    LOWER(name) LIKE '%stundenglass%' OR
    LOWER(name) LIKE '%gravity%infuser%'
  );
```

3. **Price outlier filtering** — Add WHERE clauses to all viz endpoints: `WHERE price BETWEEN 1 AND 200` (or appropriate per-category ranges). Flower over $100 is almost certainly not flower. Pre-rolls over $50 is suspicious.

4. **Geocode operators** — Run batch geocoding on the 482 operators without lat/lon. Use city + state + name for lookup. This unblocks 50% of the platform.

5. **Fill weekly sales data** — The CCC publishes this. Whatever ingestion process created the 71 rows didn't capture the actual values. Re-run the CCC ingester targeting the sales figures.

6. **Weight normalization** — 33,548 products (36%) have NULL `weight_grams`. For products with weight in the name (e.g., "Blue Dream 3.5g"), parse it out. This enables proper price-per-gram analysis.

7. **Parser improvements** — The Dutchie/Weedmaps parsers are leaking UI text into brand/name fields. "Low stock. Order soon." appears because the scraper is grabbing availability badges as brand text. Fix at the parser level.

8. **Strain type enrichment** — 44,127 products (48%) have no strain_type. Many product names contain indica/sativa/hybrid information. A simple regex could fill 30-40% of these.

### Schema Improvements

9. **Add `is_cannabis` boolean to products** — Flag merchandise, accessories, gift cards
10. **Add `normalized_brand` to products** — Map brand variants (e.g., "Cali-Blaze" and "Cali Blaze" are the same brand)
11. **Add `geocoded_at` timestamp to operators** — Track which operators have been geocoded

---

## 8. The "Holy Shit" Moment

### The Single Most Powerful Thing We Could Show

**"Your Revenue at Risk" — A Dollar Amount, Updated Daily**

Here's the concept: When an operator logs in, the very first number they see is:

> **$4,200/month at risk**
> Based on 3 competitors who undercut you on 12 products

The calculation:
1. Match their products to the same products at nearby competitors (by brand + product name + weight)
2. Identify every product where a competitor's price is lower
3. Estimate the revenue impact: `(your_price - lowest_competitor_price) × estimated_units_per_month`
4. Sum it up into one dollar figure

Why this works:
- It's **personal** — it's about THEIR money, not "the market"
- It's **urgent** — it changes daily as competitors adjust
- It's **actionable** — they can click through to see exactly which products and which competitors
- It's **quantified** — a dollar amount, not a percentage or a trend line
- It's **defensible** — it's derived from real price observations, not speculation
- It creates **FOMO** — operators who don't have GLASS don't know they're losing money

The second-level interaction: Click on that number and see a breakdown:
- Product A: You charge $45, Competitor X charges $38 → $7/unit at risk
- Product B: You charge $22, Competitor Y charges $18 → $4/unit at risk

And then: "Fix it now" → links to price recommendation or adjustment workflow.

**This is the feature that makes someone tell every operator they know about GLASS.** Not because it's beautiful (though it should be). Not because it's technically impressive. Because it answers the question every struggling operator asks themselves every night: *"Am I losing money and I don't even know it?"*

---

## Summary: What We're Building Wrong

We've built a data visualization portfolio. 19 visualizations. Brand treemaps. Sunburst charts. Sankey flow diagrams. Voronoi tessellations. These are impressive technically. They are not what struggling operators need.

What struggling operators need is:
1. **Specific, personal intelligence** — not market averages, YOUR products vs THEIR products
2. **Alerts that save them from bad decisions** — push notifications, not dashboards
3. **Revenue-connected insights** — every insight should connect to a dollar amount
4. **Honesty about data quality** — better to say "we're collecting data" than to show fake sparklines

The platform's data is genuinely valuable. 107K price observations across 293 operators is a real competitive moat. 31K CCC records spanning 7 years is unmatched. 234 pending applications is genuinely useful threat intelligence.

But we're wrapping this valuable data in a layer of mock data, fabricated trends, and unit-mismatched comparisons that would embarrass us if any sophisticated operator dug in. The path forward is: fix the data quality issues, kill the fake visualizations, ship the operator-specific intelligence features, and make every number on the platform trustworthy.

Trust first. Features second. Revenue follows.
