# GLASS UX & Data Value Review — Independent Analysis

**Reviewer:** Senior Product Strategist / UX Perspective  
**Date:** February 12, 2026  
**Status:** Complete — Brutally Honest

---

## Executive Summary

GLASS has the bones of something genuinely powerful. 92K products, 492 operators, 31K CCC price records spanning 7 years — that's a real moat. But right now, **the platform is showing operators a beautiful dashboard built on a foundation of sand.** The price data is essentially a single-day snapshot with no history. The CCC weekly sales data has 71 rows of NULL values. Brand names are polluted with parsing artifacts. And the cross-reference feature — the one you're calling a "killer feature" — is comparing apples to oranges because CCC reports per-gram prices while GLASS shows per-unit shelf prices.

The UI is polished. The design language is sharp. But an operator in Worcester doesn't care about a pretty sparkline. They care about: "Am I about to lose my shirts on flower?" Right now, GLASS can't reliably answer that question.

The good news: the fixes are mostly data pipeline problems, not architecture problems. And with the data you DO have, there are several "holy shit" moments hiding in plain sight that nobody else in this market can deliver.

---

## 1. Data Audit — What We Actually Have

### The Good

| Dataset | Count | Quality | Notes |
|---------|-------|---------|-------|
| Products | 92,586 | ⚠️ Medium | Good category coverage; brand data is polluted |
| Price observations | 107,175 | 🔴 Critical issue | 99.9% from a single day (Feb 12) |
| Operators | 492 | ⚠️ Medium | Only 10 have lat/lon coordinates |
| CCC avg prices | 31,038 | ✅ Strong | 7+ years of medical price history (2018–2025) |
| CCC pending apps | 234 | ✅ Good | Real application data with cities |
| CCC plant activity | 46,863 | ✅ Unused gold | Volume data by category/channel — not surfaced anywhere |
| CCC weekly sales | 71 | 🔴 Broken | All 71 rows have NULL for every sales column |
| Threats | 6 | 🟡 Seed data | Hand-crafted, not from automated detection |
| Alerts | 10 | 🟡 Seed data | Hand-crafted |
| Recommendations | 6 | 🟡 Seed data | Hand-crafted |
| Users | 3 | n/a | Dev accounts only |

### Critical Data Issues

#### 🔴 Issue #1: NO HISTORICAL PRICE DATA
This is the biggest problem. Of 107,175 price observations:
- **107,058** are from February 12, 2026 (today)
- The other 117 are from Feb 5–11 (a trickle of 14–20/day)

This means:
- **No week-over-week price trends** — the WoW% shown on Market page is fabricated via fallback data
- **No price change detection** — `price-cascade` and `price-ticker` queries depend on `LAG()` over time, but there IS no time series
- **No volatility calculation** — the volatility ribbon is showing one day's distribution, not volatility
- **"Price Movers (24h)" is meaningless** — there are no previous prices to compare against
- **Sparkline charts are fake** — `generateSparklineData()` creates deterministic pseudo-random data, not real trends

**Impact:** The core value proposition — "know when competitors change prices" — literally cannot work yet. An operator logging in sees charts that look like real data but are actually generated noise.

#### 🔴 Issue #2: CCC Weekly Sales = 71 Empty Rows
The `ccc_weekly_sales` table has 71 rows where every data column (`total_sales`, `adult_use_sales`, `medical_sales`, `transaction_count`) is NULL. The scraper created the rows but never populated them. The frontend falls back to hardcoded fake data (`FALLBACK_WEEKLY_SALES`).

**Impact:** The "Massachusetts total cannabis sales" chart on the Market page shows made-up numbers. The "2025 annualized pace" calculation is fiction.

#### 🔴 Issue #3: CCC Cross-Reference Compares Incompatible Units
The cross-reference "killer feature" shows:
- Flower: CCC official = **$5.81** vs GLASS scraped = **$35.39** → **"509% markup"**

This is nonsense. CCC reports **per-gram** average prices (medical dispensary wholesale/transfer pricing). GLASS tracks **per-unit shelf prices** (eighths at $35-50). Comparing $5.81/gram to a $35 eighth isn't a "markup" — it's a unit mismatch. The cross-reference query tries to map categories but doesn't normalize units.

**Impact:** The headline number on the public Market page — the one meant to make operators go "wow" — is misleading. An informed operator would see "509% markup on flower" and immediately distrust the platform.

#### ⚠️ Issue #4: Brand Data Pollution
Top "brands" in the database:
1. **"stock. Order soon."** — 3,839 products (parsing artifact from low-stock badges)
2. **"Unknown"** — 1,871 products
3. **"510"** — 346 (vape cartridge format, not a brand)
4. **"Flower"** — 299 (category leaked into brand field)
5. **"Gummies"** — 242 (category, not brand)
6. **"Medical patients only"** — 122 (access restriction text)
7. **"Pre-Roll"** — 114 (category)
8. **"Disposable"** — 111 (format)

~7,239 products (~7.8%) have garbage brand values. The Brand Treemap visualization proudly shows "stock. Order soon." as the #1 brand.

#### ⚠️ Issue #5: Category Misclassification
Products like "C.C. Batter" (live rosin concentrate) are classified as `flower`. Products with 72-88% THC are obviously concentrates, not flower. The parser is categorizing by what section of the menu they appeared in, not by what the product actually is.

#### ⚠️ Issue #6: Only 10/492 Operators Have Coordinates
The Geography page, Proximity Radar, and delivery zone features all depend on lat/lon. Only **10 operators** (2%) have coordinates populated. This makes:
- Market Terrain Map: shows 10 dots instead of 500
- Proximity Radar: broken for 98% of operators
- Delivery Voronoi: essentially empty

#### ⚠️ Issue #7: Non-Cannabis Products in the Database
The "flower" category includes dab rigs ($1,400), gift cards ($1,000), AeroPay fees ($999), stickers ($0.22), and rolling papers ($0.25). These inflate outlier counts (1,453 flower items over $100) and skew averages.

#### ✅ Hidden Gold: CCC Plant Activity (46,863 rows)
This table contains actual **sales volume data** by category, broken out by Retail vs Delivery vs Courier. This is the closest thing to demand/velocity data in the entire system and it's NOT surfaced ANYWHERE in the frontend. Example: "Retail | Retail | Buds" = 176 units, "Retail | Retail | Raw Pre-Rolls" = 565,430 units. This is real CCC-reported transaction volume.

#### ✅ Hidden Gold: CCC Avg Prices = 7-Year Price History
2,584 distinct dates from Nov 2018 to Dec 2025. This is a legitimate **7-year price trend** for medical cannabis by category. You could show operators how per-gram prices have declined over time — and where they're heading. Nobody else has this visualized.

---

## 2. Current UX Assessment — Page by Page

### Landing Page ✅ (Good)
Clean, compelling, appropriately aggressive copy. "See what your competitors charge" is the right hook. The feature breakdown (Price Wire, Threat Radar, Morning Brief) is clear. The ecosystem section creates a vision.

**Problems:**
- "Join 50+ Massachusetts operators" — there are 3 users. This is misleading.
- Feature placeholder boxes show "PRICE WIRE Preview" with just an icon — should show actual live data teasers from the API

### Market Page (Public) ⚠️ (Promising but Broken)
This is the SEO/lead-gen page. Good structure. CCC cross-reference is the right idea for a "killer feature." But:

- **509% flower markup** destroys credibility (unit mismatch)
- **Weekly sales chart shows fake data** (all NULLs → fallback)
- **Price index WoW/MoM percentages are hardcoded fallbacks** — not calculated from real data
- **Demographics section uses fallback data** (ccc_demographics table is empty)
- **News feed is hardcoded fake headlines** ("GLASS Desk" and "Operator Briefing" don't exist)

**Verdict:** This page makes promises the data can't keep. An operator who clicks through and compares the public page data to their own knowledge will find discrepancies.

### Onboarding ✅ (Well Designed)
The 4-step flow is clean. "Claim your dispensary in 10 seconds" is perfect framing. The operator search works against real data. Priority selection personalizes the experience.

**Problems:**
- Step 2 "Market at a Glance" shows competitors within 10 miles — but since only 10 operators have lat/lon, most users will see "0 competitors, 0 threats"
- Manual mode works but provides no market context (no way to derive proximity without coordinates)

### Morning Brief ⚠️ (Beautiful Shell, Hollow Inside)
This is the most impressive-looking page. Sparklines, severity badges, recommendations, freshness indicator — it feels like a Bloomberg terminal. But:

- **"Products Tracked: 2,847"** — calculated as `top_movers.length * 150`, literally making up a number
- **"Price Changes 24h: 156"** — same made-up multiplication
- **Sparklines are pseudo-random** — `generateSparklineData()` hashes the SKU name to create deterministic noise, not real trends
- **Brand Treemap shows "stock. Order soon." as #1** — immediately signals data quality problems
- **Economic Indicators** are calculated but based on 8 days of data, so MoM and trend data is meaningless
- **Strain Stream and Category Growth** — queries return minimal data (all observations are within one week)
- **"$XXX est. margin"** from recommendations — there are 6 hand-crafted recommendations with no model behind them
- **Market Size chart** — based on `COUNT(DISTINCT product_id)` which isn't market size, it's scrape coverage

**Verdict:** Looks incredible, feels like it's lying. An operator who looks closely will realize the numbers don't add up.

### Price Wire ⚠️ (Right Idea, Wrong Execution)
Good filter/sort/pagination UX. Export CSV is a great touch. The data table showing actual prices from the scrape is the most honest part of the platform.

**Problems:**
- **Price Movers (24h) is empty or nonsensical** — with only 1 day of substantive data, `LAG()` over time returns almost nothing
- **Price Position Matrix** — shows operator vs market avg, but "your_price" is just the operator's average, not the logged-in user's
- **Volatility Ribbon** — showing distribution within one day, not actual volatility
- **Proximity Radar** — broken for 98% of operators (no lat/lon)
- **Mock data objects** (`matrixMock`, `volatilityMock`, etc.) are defined but the API calls try real data first — good fallback strategy, but users may not know what's real vs mock

### Threat Radar 🟡 (Good Structure, No Engine)
The page looks professional. Filters work. Severity badges are clear.

**Problems:**
- Only 6 threats exist, all hand-written
- No automated threat detection system exists
- The Threat Network visualization creates fake links between threats and operators
- License Pipeline stages are derived from the `threats` table which has 6 rows — the stages show counts like "2 submitted, 1 under review"
- The CCC Timeline shows the same 6 hand-crafted threats
- Meanwhile, `ccc_pending_applications` has 234 REAL applications that could feed this — they're just not connected

### Competitors 🟡 (Needs Operator Context)
- Operator Comparison loads 4 random operators — should compare against the user's operator
- Market Share Flow is based on SKU count not actual sales — misleading
- Price War Heatmap depends on time-series data that doesn't exist yet
- `review_score` field is literally `3.8 + RANDOM() * 1.1` — random numbers presented as review scores

### Geography 🔴 (Essentially Broken)
- Market Terrain Map shows 10 dots (only operators with coordinates)
- Delivery Voronoi shows same 10 dots
- 482 operators are invisible because they lack lat/lon

### Budtender ✅ (Good Landing Page)
Well-crafted coming-soon page. The mock conversation is convincing. Waitlist form is clear.

**No problems** — it's a marketing page and does its job.

### Cue ✅ (Good Landing Page)
Same as Budtender. Clean "coming soon" with features and waitlist.

**$199/mo pricing** is aggressive for a product that doesn't exist yet — but establishing an anchor price early is smart.

---

## 3. The Operator's Perspective — What a Struggling Operator Actually Needs

Let me be Maria. I run a dispensary in Worcester. I have 8 employees. My flower margins were 45% in 2023 and now they're under 30%. Three new shops opened within 5 miles last year. I'm paying $8,200/month rent and some weeks I'm not sure I'll make it.

### What Maria Needs When She Opens GLASS

**1. "Am I priced right?" — RIGHT NOW, not last month**

Maria doesn't need a WoW trend. She needs: "Your Blue Dream eighth is at $45. Three competitors within 5 miles are at $38, $39, $40. You are the most expensive. 62% of Worcester flower is priced under $40."

This is a **price position snapshot** — and it's the one thing the data CAN support right now even with one day of scrape data. You have 107K observations from TODAY. That's enough for a market-wide price position comparison.

**2. "Who's undercutting me?"**

"Canna Provisions dropped their average flower price to $26.60 — that's $9 below market average. They have 1,032 flower SKUs. They're the price leader and they're 12 miles from you."

This is derivable from the current data. The price-matrix API already returns this. It's just not framed from the operator's perspective.

**3. "What's coming?"**

"4 new retailer applications are pending in Worcester. 23 in Boston. 16 in Holyoke. If all approved, Worcester gets 11% more competition."

This is derivable from `ccc_pending_applications` + `operators`. Just overlay pending apps against existing operators by city.

**4. "What should I stock more/less of?"**

The CCC plant activity data shows actual transaction volumes by category. If pre-rolls are 565K transactions while kief is 977, Maria should know "Pre-rolls are 579x more popular than kief by transaction volume."

**5. "Where is the market going?"**

The 7-year CCC avg price dataset could show: "Medical buds have dropped from $12.50/g in 2019 to $5.81/g in 2025 — a 54% decline. The rate of decline is accelerating."

That terrifying trend line is exactly the kind of thing that makes an operator say "I need to understand this better" — and keep paying for GLASS.

### What Maria Does NOT Need

- Deterministic pseudo-random sparklines pretending to be price trends
- A "Brand Treemap" where the #1 brand is "stock. Order soon."
- A "509% markup" headline that she knows is wrong
- Mock chat conversations about relaxation gummies
- Random review scores presented as real data
- A volatility ribbon for one day of data

---

## 4. Missed Opportunities — Data Features We Should Be Building

### 4.1 Price Position Index (POSSIBLE TODAY)
With 107K+ observations from 492 operators across 7 categories, we can compute:
- **Percentile ranking** for every operator in every category
- "You're in the 73rd percentile for flower pricing" — specific, actionable, immediately understandable
- Operators priced above the 80th percentile in competitive markets are at risk

### 4.2 CCC × GLASS Price Convergence (POSSIBLE TODAY — needs unit fix)
The CCC avg_prices table has 7 years of per-gram medical prices. If we normalize GLASS prices to per-gram (using `weight_grams` which 64% of products have), we can show:
- "The gap between wholesale CCC and retail shelf pricing is narrowing"
- "Your category is converging faster than others"
- This is a **margin compression signal** that nobody else in the market can provide

### 4.3 SKU Proliferation as Demand Signal (POSSIBLE TODAY)
When operators add more SKUs in a category, it signals growing demand. With 92K products across 492 operators:
- Which categories are seeing the most new products?
- Which brands are expanding their footprint?
- Where are operators contracting their menus? (That's a warning sign)

### 4.4 New Competitor Threat Scoring (POSSIBLE TODAY)
234 pending applications with city data. Cross-reference with existing operator density:
- "Worcester has 34 existing operators and 4 pending applications = 12% potential growth"
- "Holyoke has 35 operators and 16 pending applications = 46% potential growth — HIGH THREAT"
- This is a real, data-driven alert system that writes itself

### 4.5 Category Volume Intelligence (POSSIBLE TODAY — uses plant_activity)
46,863 CCC plant activity records show actual retail and delivery transaction volumes. This data is:
- Segmented by Retail vs Delivery vs Courier
- Segmented by product category
- Has date ranges for trending
- **Nobody on the frontend knows this table exists**

### 4.6 Historical Price Trends (NEEDS DATA PIPELINE FIX)
Once scraping runs daily for 2+ weeks, every time-series visualization becomes real. The architecture already supports it — the queries use `LAG()`, `DATE_TRUNC()`, and time windows. The data just isn't there yet.

### 4.7 Price Clustering Analysis (POSSIBLE TODAY)
With 46K flower price observations:
- What are the natural price tiers? ($25-30, $35-40, $45-50?)
- How many operators cluster at each tier?
- "78% of flower is priced between $28-$42 — pricing above $42 puts you in a shrinking premium segment"

### 4.8 Brand Geography (NEEDS LAT/LON FIX)
Which brands are everywhere vs. which are regional? Once operators have coordinates:
- "Happy Valley is concentrated in western MA with 144 products"
- "Bountiful Farms has 226 products spread across 15+ cities"
- Helps operators understand brand competitive dynamics

### 4.9 Seasonal CCC Patterns (POSSIBLE TODAY)
71 months of CCC avg price data. Medical price seasonality:
- Do prices dip in Q1 after holiday demand?
- Summer concentration demand?
- This is immediately analyzable.

---

## 5. New Feature Proposals — Ranked by Impact × Effort

### Tier 1: Ship This Week (High Impact, Low Effort)

**1. Price Position Report Card** ⭐⭐⭐⭐⭐
- Impact: 10/10 | Effort: 2/10
- For each operator: their average price by category vs market average, with percentile rank
- "Your flower avg ($43.62) is in the 81st percentile. 4 out of 5 operators price lower."
- Data: Already in `price-matrix` endpoint, just needs a "your operator" overlay
- Wireframe: Single card at top of Morning Brief. Big number (percentile), category breakdown below, color-coded (green = competitive, red = expensive)

**2. Competition Density Alert** ⭐⭐⭐⭐⭐
- Impact: 9/10 | Effort: 2/10
- Cross-reference `ccc_pending_applications` city data with `operators` city data
- "4 new retailer applications filed in your city. If approved, competition increases 12%."
- Wireframe: Alert card on Morning Brief and Threat Radar. City name, count of pending, delta %

**3. Fix CCC Cross-Reference Units** ⭐⭐⭐⭐⭐
- Impact: 10/10 | Effort: 3/10
- Normalize GLASS prices to per-gram using `weight_grams` (available for 64% of products)
- Or: clearly label that CCC = per-gram wholesale, GLASS = per-unit retail
- The "509% markup" headline is actively harming credibility

**4. Category Volume Leaderboard** ⭐⭐⭐⭐
- Impact: 8/10 | Effort: 2/10
- Surface `ccc_plant_activity` data in a simple ranked list
- "Pre-rolls: 565K transactions. Edibles: 205K. Vape: 9K via delivery."
- Wireframe: Bar chart on Market page, sortable by Retail/Delivery/Courier

**5. CCC 7-Year Price Trend** ⭐⭐⭐⭐
- Impact: 8/10 | Effort: 2/10
- Line chart of CCC avg_prices over time by category
- "Medical buds: $12/g → $5.81/g since 2019"
- Show the secular decline. It's terrifying and operators NEED to see it.
- Wireframe: Full-width area chart on Market page, category toggle

### Tier 2: Ship This Month (High Impact, Medium Effort)

**6. Geocode All Operators** ⭐⭐⭐⭐
- Impact: 9/10 | Effort: 4/10
- Batch geocode 482 operators using city + name via Google Places or Mapbox
- Unlocks: Geography page, Proximity Radar, delivery zones, proximity alerts
- One-time script, ~$5 in API costs

**7. Brand Data Cleanup Pipeline** ⭐⭐⭐⭐
- Impact: 7/10 | Effort: 4/10
- Filter rules: if brand = "stock. Order soon." → set brand = NULL
- Map "510" → NULL, "Flower" → NULL, "Gummies" → NULL, etc.
- Deduplicate "Cali-Blaze" / "Cali Blaze"
- Reclassify products with 60%+ THC in "flower" → "concentrate"

**8. Price Position Over Time Tracker** ⭐⭐⭐⭐
- Impact: 9/10 | Effort: 5/10 (requires daily scraping working first)
- Weekly snapshot of each operator's percentile position
- "You were 73rd percentile last week, now 68th — the market is catching up to you"
- Needs: 2+ weeks of consistent daily scraping

**9. Automated Threat Detection from CCC Data** ⭐⭐⭐⭐
- Impact: 8/10 | Effort: 5/10
- Auto-generate threats when:
  - New pending application filed in your city
  - CCC avg price drops >5% in your top category
  - Plant activity shows volume shift in your category
- Replaces the 6 hand-crafted threats with real ones

**10. "What If" Pricing Simulator** ⭐⭐⭐
- Impact: 7/10 | Effort: 6/10
- "If you dropped flower to $35, you'd move from 81st to 55th percentile"
- Uses current price distribution data
- Wireframe: Slider on Price Wire page, real-time percentile update

### Tier 3: Ship Next Quarter (High Impact, High Effort)

**11. POS Integration for Actual Sales Data** ⭐⭐⭐⭐⭐
- Impact: 10/10 | Effort: 9/10
- Connect to Dutchie, Treez, Flowhub APIs
- Know actual sell-through rates, not just shelf prices
- Transforms GLASS from "intelligence" to "operations"

**12. Predictive Price Movement Model** ⭐⭐⭐
- Impact: 8/10 | Effort: 8/10
- Use historical price data + CCC trends + competitor behavior
- "Based on market trajectory, flower prices in your area will drop 5-8% by April"
- Requires: 3+ months of historical scrape data

---

## 6. Quick Wins — Live in a Day

### Quick Win 1: Kill the Fake Data (2 hours)
Remove all `FALLBACK_*` constants from Market.tsx. If data is NULL, show "Data loading — check back tomorrow" instead of fake numbers. Honesty > aesthetics.

### Quick Win 2: Brand Treemap Cleanup (1 hour)
Add a SQL `WHERE` filter: `WHERE brand NOT IN ('stock. Order soon.', 'Unknown', '510', 'Flower', 'Gummies', 'Pre-Roll', 'Disposable', 'Medical patients only', 'THC', 'Infused Pre-Roll', 'Preroll | 1g', 'Cones 1 1/4')` to the `brand-share` endpoint.

### Quick Win 3: Add CCC Plant Activity Endpoint (2 hours)
New API route: `/ccc/plant-activity` returning aggregated volume by category and channel. Immediately usable on Market page.

### Quick Win 4: Competition Density Map (3 hours)  
Simple SQL: `SELECT city, COUNT(*) as existing_operators FROM operators GROUP BY city` merged with `SELECT city, COUNT(*) as pending_apps FROM ccc_pending_applications WHERE license_type LIKE '%Retail%' GROUP BY city`. Show as table on Threat Radar.

### Quick Win 5: Honest Data Freshness Banner (30 minutes)
Replace `generateSparklineData()` fake sparklines with a "Data as of Feb 12, 2026 — first scrape. Historical trends available after 14 days of data collection." banner. Sets expectations correctly.

### Quick Win 6: Non-Cannabis Product Filter (1 hour)
Add to scrape pipeline: filter out products where price > $200 and name contains "rig", "bong", "gift card", "aeropay", "sticker", "rolling paper", "screen", "merch".

### Quick Win 7: Fix CCC Cross-Reference Label (15 minutes)
Change "markup" to show: "CCC reports per-gram medical transfer prices. GLASS tracks retail shelf prices. These are different metrics." Or better: calculate per-gram GLASS prices where weight_grams is available.

---

## 7. Data Quality Fixes — Specific Issues

| # | Issue | Table | Fix | Priority |
|---|-------|-------|-----|----------|
| 1 | 99.9% of prices from single day | prices | Fix daily scrape cron to run reliably every 24h | 🔴 P0 |
| 2 | Weekly sales all NULL | ccc_weekly_sales | Fix CCC scraper to actually parse sales figures from source | 🔴 P0 |
| 3 | Cross-ref unit mismatch | ccc cross-ref query | Normalize to per-gram or label clearly | 🔴 P0 |
| 4 | 482/492 operators missing lat/lon | operators | Batch geocode using city+name | 🔴 P1 |
| 5 | "stock. Order soon." = top brand | products.brand | Scraper: strip stock warnings before storing | 🔴 P1 |
| 6 | Category misclassification | products.category | If thc_percent > 60%, recategorize as concentrate | 🟡 P2 |
| 7 | Non-cannabis products in DB | products/prices | Filter by name patterns (rig, bong, gift card, etc.) | 🟡 P2 |
| 8 | Brand name duplication | products.brand | Normalize "Cali-Blaze"/"Cali Blaze", case normalization | 🟡 P2 |
| 9 | Subcategory always NULL | products.subcategory | Parse from product name/description during scrape | 🟡 P3 |
| 10 | ccc_demographics empty | ccc_demographics | Fix or remove scraper; demographics data exists on CCC site | 🟡 P3 |
| 11 | Promo flag nearly unused | prices.promo_flag | Only 28 of 107K flagged — parser likely missing promo detection | 🟡 P3 |
| 12 | Random review scores in SQL | viz operator-compare | Remove `3.8 + RANDOM() * 1.1` — show no score if none exists | 🔴 P1 |

---

## 8. The "Holy Shit" Moment

Here's what makes an operator never leave:

### **The Market Compression Timeline**

One visualization. Full screen. Here's what it shows:

**Top half:** A 7-year line chart using CCC avg_prices data. Every product category, declining. Buds from $12/g to $5.81/g. Pre-rolls from $10/g to $5.76/g. The lines all slope down and to the right. It's undeniable. It's terrifying. And it's REAL data.

**Bottom half:** A bar chart of `ccc_pending_applications` by city, stacked against existing operator count. "Your city has 34 operators now. 4 more are applying. And every year, the price everyone can charge goes down."

**Overlay:** A single operator's current price position (from today's scrape) plotted against the declining market trend. "You're here. The market is moving this way. Here's how long you have at your current pricing."

**The hook:** Nobody else can show this. Not Headset. Not BDSA. Not LeafLink. They have sales data but they don't cross-reference CCC 7-year trends with real-time shelf pricing across 500 dispensaries with pending license pipeline data.

This is the view that makes Maria put down her coffee and call her business partner. "You need to see this."

It combines:
- `ccc_avg_prices` (7 years, 31K records) ✅ Available now
- `ccc_pending_applications` (234 records) ✅ Available now  
- `prices` + `products` (107K observations from TODAY) ✅ Available now
- `ccc_plant_activity` (46K records of actual volume) ✅ Available now

No fake data. No fallbacks. No pseudo-random sparklines. Just the truth about where this market is heading, personalized to your city, your categories, and your price position.

**That's the "holy shit" moment.** It doesn't require new data collection, new integrations, or new models. It requires someone to connect the dots that are already in the database.

---

## Summary: What to Do First

### This Week (in order)
1. **Fix daily scraping** — nothing else matters if you don't have time-series data
2. **Fix CCC cross-reference units** — your credibility on the Market page depends on it
3. **Kill fake data fallbacks** — replace with honest "collecting data" states
4. **Clean brand names** — filter top 10 garbage brands from all viz queries
5. **Surface CCC plant activity** — free value that nobody's seen yet
6. **Build the Market Compression Timeline** — your "holy shit" moment
7. **Add competition density alert** — pending apps × operator count by city

### This Month
8. Geocode all operators (unlocks Geography + Proximity)
9. Automate threat generation from CCC data
10. Build Price Position Report Card for onboarded operators

### Stop Building
- Don't work on Virtual Budtender until the core intelligence is trustworthy
- Don't work on Cue pricing features until you have 30+ days of price history
- Don't work on delivery features until you have geographic coverage
- Don't add more visualizations — fix the data feeding the existing ones

The platform's design and UX are genuinely excellent. The architecture is sound. The data moat is real. But right now you're putting lipstick on a data pipeline that needs plumbing. Fix the plumbing first, then the lipstick will actually mean something.
