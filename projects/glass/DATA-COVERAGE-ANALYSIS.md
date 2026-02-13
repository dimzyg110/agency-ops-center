# GLASS Data Coverage Analysis

**Date:** February 13, 2026  
**Author:** Automated Analysis (Opus subagent)  
**Purpose:** Cross-reference scraped data sources, quantify coverage gaps, and identify the best additional data sources for MA cannabis pricing.

---

## Executive Summary

GLASS currently tracks **1,051 operators** in its database, of which **487 have at least one data source** and **385 have been successfully scraped** (have price data). Against the CCC's **418 licensed Marijuana Retailers** (397 active), our effective coverage is **~385 operators with prices / 418 licensed retailers = ~92% by operator match**, but only **~256 operators had prices scraped TODAY**, meaning daily active coverage is closer to **61%**.

The biggest wins come from:
1. **Fixing Weedmaps scraper reliability** (163/173 stores failed on last run)
2. **Adding iHeartJane** (~100-150 MA stores, many not on Dutchie/Weedmaps)
3. **Adding Leafly** (~160+ MA listings with menu data)
4. **Fixing Dutchie scraper failures** (40/235 failed on last full run)

---

## Part 1: Platform Coverage Breakdown

### 1.1 Slug Files (Discovery Layer)

| Platform | Total Slugs | Notes |
|----------|------------|-------|
| Dutchie | 235 | Unique dispensary slugs discovered |
| Weedmaps | 282 | ~119 confirmed with active menus |

**38 slugs are shared** between platforms (exact slug match), meaning these 38 dispensaries are listed on both Dutchie and Weedmaps with the same slug identifier.

### 1.2 Database: Operators Table

| Platform | Operators | Has Source | Has Prices (ever) |
|----------|-----------|------------|-------------------|
| Dutchie | 235 | 235 | 200 |
| Weedmaps | 244 | 244 | 177 |
| (none/CCC-only) | 572 | 8 | 8 |
| **Total** | **1,051** | **487** | **385** |

**Key insight:** 572 operators have NO platform assignment — these are CCC-licensed businesses loaded from the license registry but not yet matched to any scraping source.

### 1.3 Operator Overlap Analysis

| Category | Count | Notes |
|----------|-------|-------|
| **Both Dutchie + Weedmaps** | 38 | Operators with sources on both platforms |
| **Dutchie-only** | 203 | Have Dutchie source, no Weedmaps |
| **Weedmaps-only** | 244 | Have Weedmaps source, no Dutchie |
| **Other sources only** | 8 | Have iHeartJane, website, or other menu sources |
| **No sources at all** | 564 | In DB but no scraping source configured |
| **Total unique with sources** | 487 | |

The 8 "other sources" operators include stores like:
- **Theory Wellness Great Barrington** — Dutchie menu + website
- **INSA Springfield** — iHeartJane menu
- **The Heirloom Collective Northampton** — iHeartJane menu
- **Happy Valley Worcester** — Dutchie menu + website
- **Pure Oasis** — Dutchie menu + website
- **Revolutionary Clinics Cambridge** — Dutchie menu + website
- **Union Twist Somerville** — Dutchie menu + website
- **CommCan Lowell** — Dutchie menu

### 1.4 Today's Scrape Performance (Feb 13, 2026)

| Platform | Operators with Prices Today | Sources Scraped | Prices Inserted |
|----------|---------------------------|----------------|----------------|
| Dutchie | 79 | 87 | 11,103 |
| Weedmaps | 177 | 177 | 22,337 |
| **Total** | **256** | **264** | **33,440** |

**Critical issue:** Dutchie only scraped 79/235 operators today (34% success rate). Looking at recent scrape runs:
- **Dutchie** (Feb 12): 235 attempted → 195 succeeded → **40 failed (17%)**
- **Weedmaps** (Feb 12): 173 attempted → 10 succeeded → **163 failed (94% failure rate!)**
- **Weedmaps** (Feb 13): Run failed entirely

The Weedmaps scraper has a severe reliability problem — 94% failure rate on the last successful run. This is likely the single biggest bottleneck in data coverage.

### 1.5 Historical Data Totals

| Metric | Count |
|--------|-------|
| Total prices in DB | 150,431 |
| Distinct products | 118,392 |
| Distinct sources with prices | 416 |
| Operators ever scraped | 385 |

---

## Part 2: CCC Licensed Retailer Coverage

### 2.1 CCC License Data Summary

From `commence-ops.csv` (772 rows, all at "Commence Operations" stage):

| License Type | Total | Active |
|-------------|-------|--------|
| Marijuana Retailer | 418 | 397 |
| Marijuana Cultivator | 145 | — |
| Marijuana Product Manufacturer | 127 | — |
| Marijuana Delivery Operator | 19 | ~15 |
| Marijuana Microbusiness | 17 | 13 |
| Independent Testing Laboratory | 16 | — |
| Marijuana Courier | 13 | ~12 |
| Medical Marijuana Treatment Center | 8 | 8 |
| Other (Transporter, etc.) | 9 | — |

**Customer-facing retail locations: 418 retailers + 8 RMDs + 17 microbusinesses = 443 total**  
**Active customer-facing: 397 retailers + 8 RMDs + 13 microbusinesses = 418 active**

### 2.2 CCC → Operator Matching

The `ccc_licenses` table has **772 records**, of which **770 are matched** to operators (99.7% match rate). Only 2 licenses remain unmatched.

### 2.3 Coverage Gap

| Metric | Count |
|--------|-------|
| Active CCC Retailers + RMDs + Microbusiness | 418 |
| GLASS operators with ANY price data (ever) | 385 |
| GLASS operators with prices TODAY | 256 |
| **Estimated uncovered active retailers** | **~33-60** |

**Coverage rate: 385/418 = 92% (ever scraped) or 256/418 = 61% (today)**

The gap between "ever scraped" (385) and "today" (256) represents scrapers that aren't running reliably. The 33 never-scraped retailers likely have custom menu systems not on Dutchie or Weedmaps.

### 2.4 Top 10 Cities by Retailer Count (CCC)

| City | Retailers |
|------|-----------|
| Boston | 36 |
| Northampton | 13 |
| Worcester | 13 |
| Brockton | 11 |
| Fall River | 10 |
| Holyoke | 10 |
| Lynn | 9 |
| Cambridge | 9 |
| Pittsfield | 7 |
| Fitchburg | 7 |

---

## Part 3: Additional Data Source Research

### 3.1 iHeartJane (jane.co) — **HIGH PRIORITY** ⭐

**What it is:** iHeartJane is an embedded e-commerce menu platform used by dispensaries. Unlike Dutchie (which has its own marketplace), Jane provides embedded menus on dispensary websites and also has its own storefront at iheartjane.com.

**MA Coverage:** Estimated **100-150 MA dispensaries**. We already have 2 stores using iHeartJane sources (INSA Springfield, The Heirloom Collective), proving the concept works.

**How menus work:**
- Dispensaries embed Jane's menu widget (iframe or "Jane Boost" iframeless) on their own websites
- Jane also hosts a storefront at `iheartjane.com/stores/{store-slug}`
- The backend uses a REST API: `api.iheartjane.com/v1/stores/{store_id}/`
- Products are accessible via the API (confirmed by existing open-source scrapers on GitHub)
- **Swagger API docs are public:** `api.iheartjane.com/jane-api-docs/index.html`

**URL Patterns:**
- Store listing: `https://www.iheartjane.com/stores`
- Individual store: `https://www.iheartjane.com/stores/{store-slug}`
- API embed: `https://api.iheartjane.com/v1/stores/{store_id}/embed.js`
- Products API: `https://api.iheartjane.com/v1/stores/{store_id}/products`

**Access Method:** Scraping (API is semi-public; no auth needed for menu read) or Partnership (`partnersuccess@iheartjane.com`)

**Difficulty:** ⭐⭐ (Medium-Low) — API is well-documented, existing scrapers prove feasibility  
**Estimated Coverage Gain:** +50-80 NEW stores not already on Dutchie/Weedmaps

### 3.2 Leafly — **MEDIUM PRIORITY**

**What it is:** One of the largest cannabis marketplace platforms. Leafly has dispensary listings with menus, reviews, and ordering.

**MA Coverage:** Leafly claims "over 160" licensed dispensaries in Massachusetts. However, reports indicate Leafly has **fewer MA shops with regularly updated menus** compared to Weedmaps.

**How menus work:**
- Dispensary pages at `leafly.com/dispensaries/massachusetts-us`
- Individual stores: `leafly.com/dispensary/{dispensary-slug}`
- Menus are POS-integrated — Leafly has integrations with Dutchie POS, Cova, Jane, and others
- Menu data is synced from POS systems, not manually entered

**Access Method:** Web scraping (complex JavaScript-rendered pages) or API partnership
- Leafly has a business API but it's partner-only
- POS integration docs suggest API credentials are available to partners

**Difficulty:** ⭐⭐⭐ (Medium-High) — React SPA, aggressive anti-scraping, would need Camoufox  
**Estimated Coverage Gain:** +20-40 new stores (significant overlap with Dutchie/Weedmaps)

### 3.3 Google Maps/Places API

**What it is:** Google's business listing data including dispensary locations, hours, reviews.

**MA Coverage:** Essentially all operational dispensaries have Google listings.

**Menu Data:** ❌ **No menu/pricing data.** Google Places provides:
- Business name, address, phone, hours
- Reviews and ratings
- Photos
- Place ID for matching

**Use Case:** Not useful for pricing data, but excellent for:
- Discovering unlisted dispensaries
- Enriching operator data (hours, ratings, photos)
- Verifying which dispensaries are actually open

**Difficulty:** ⭐ (Easy) — We already have Google Places API active  
**Estimated Coverage Gain:** 0 new pricing data, but useful for operator enrichment

### 3.4 POS Systems with APIs

#### 3.4.1 Dutchie POS (separate from Dutchie marketplace)

**What it is:** Dutchie acquired LeafLogix and GreenBits, combining them into "Dutchie POS." This is separate from the dutchie.com marketplace we already scrape.

**MA Relevance:** Many MA dispensaries use Dutchie POS but may not list on dutchie.com marketplace. The POS system powers the marketplace, but operators can opt out of the marketplace listing.

**API Access:**
- API keys are available to third-party integrators
- Process: Authorized account administrators request API keys through Dutchie Help Center
- Docs: `support.dutchie.com/hc/en-us/articles/27660267271187`
- Keys are per-dispensary (each operator must authorize access)

**Application Process:** Contact Dutchie's partnerships team. Need a valid business use case. Per-dispensary authorization required.  
**Difficulty:** ⭐⭐⭐⭐ (High) — Need dispensary-by-dispensary authorization  
**Verdict:** Not practical for broad data collection; better to use the marketplace scraper

#### 3.4.2 Treez

**What it is:** Cannabis retail POS with inventory management, compliance, and e-commerce.

**MA Relevance:** Treez has presence in MA but is stronger in CA, CO, MI. Estimated 10-30 MA dispensaries.

**API Access:**
- **Open API documented at `code.treez.io`**
- Developer Portal with full reference documentation
- API covers inventory, products, pricing, transactions
- Partner network available

**Application Process:**
1. Visit `code.treez.io` for documentation
2. Contact Treez partnership team
3. Complete integrator agreement
4. Receive sandbox access, then production keys

**Difficulty:** ⭐⭐⭐ (Medium) — Well-documented API, but requires partnership agreement  
**Estimated Coverage Gain:** +10-20 stores

#### 3.4.3 Flowhub

**What it is:** Cannabis POS and payments platform. Strong in CO, expanding to other states.

**MA Relevance:** Flowhub operates in Massachusetts (confirmed on their markets page). They were the first Metrc integrator. Estimated 15-30 MA dispensaries.

**API Access:**
- **Open API** — explicitly advertised ("build your own with our open API")
- 50+ existing integrations
- Partner with Jane/iHeartJane for menu embedding

**Application Process:**
1. Contact Flowhub partnerships team through `flowhub.com`
2. Describe integration use case
3. Complete partner agreement
4. Receive API credentials

**Difficulty:** ⭐⭐⭐ (Medium) — Open API philosophy, but need partnership  
**Estimated Coverage Gain:** +10-20 stores

#### 3.4.4 BLAZE

**What it is:** Cannabis POS system designed for dispensaries and delivery services. Award-winning.

**MA Relevance:** We know Delivered Inc. uses BLAZE. Estimated 10-20 MA dispensaries.

**API Access:**
- **Full API documentation at `apidocs.blaze.me`**
- Developer API guide: `apidocs.blaze.me/blaze-developer-api/guides/Introduction`
- BLAZE Partner Network (BPN) for third-party integrators
- API keys generated from BLAZE Retail backend
- Supports creating members, orders, reading inventory/products

**Application Process:**
1. Apply to BLAZE Partner Network (BPN) at `blaze.me/bpn/`
2. Describe your integration/use case
3. For existing BLAZE customers: generate API key directly from backend
4. For partners: receive sandbox access after approval

**Difficulty:** ⭐⭐ (Medium-Low) — Best-documented cannabis POS API  
**Estimated Coverage Gain:** +5-15 stores

#### 3.4.5 Cova

**What it is:** Cannabis POS with compliance focus. 500+ partner integrations. Two-way Metrc integration.

**MA Relevance:** Active in MA. Estimated 20-40 MA dispensaries. Strong in compliance-focused markets.

**API Access:**
- Open API with partner integrations
- Integrates with Leafly, Jane, and major e-commerce platforms
- Two-way Metrc integration

**Application Process:**
1. Contact Cova through `covasoftware.com`
2. Partner integration request
3. Complete API agreement

**Difficulty:** ⭐⭐⭐ (Medium)  
**Estimated Coverage Gain:** +10-25 stores (high overlap with existing aggregators)

#### 3.4.6 Meadow

**What it is:** Cannabis POS & delivery software, originally California-focused but now active in MA, MI, NY, NJ, DC.

**MA Relevance:** Confirmed active in Massachusetts. Estimated 5-15 MA dispensaries.

**API Access:** Integrates with Metrc, Onfleet, QuickBooks. API access likely through partnership.

**Application Process:** Contact `getmeadow.com` partnership team.  
**Difficulty:** ⭐⭐⭐ (Medium)  
**Estimated Coverage Gain:** +5-10 stores

#### 3.4.7 BioTrack/BioTrackTHC

**What it is:** Seed-to-sale cannabis tracking platform. Both a government traceability system AND a commercial POS.

**MA Relevance:** BioTrack has a specific Massachusetts page. Used for both POS and compliance. Estimated 10-20 MA dispensaries use BioTrack POS.

**API Access:**
- Commercial API available
- Integrates with Flowhub and other platforms
- API key-based authentication

**Application Process:** Contact BioTrack through `biotrack.com`. Complete integrator agreement.  
**Difficulty:** ⭐⭐⭐ (Medium)  
**Estimated Coverage Gain:** +5-15 stores

#### 3.4.8 METRC (Massachusetts State Tracking)

**What it is:** The state-mandated seed-to-sale tracking system for Massachusetts cannabis. ALL licensed operators must report to Metrc.

**MA Relevance:** 100% of licensed operators report to Metrc. Contains sales data, inventory, pricing.

**API Access:**
- **Confidential** — requires licensee-specific API keys
- Licensees sign a confidentiality agreement with CCC
- API documentation available after completing training webinar
- Sandbox available: email `api@metrc.com`
- **Data is NOT public** — only licensees can access their own data

**Application Process:**
1. Request API developer documents from `api@metrc.com`
2. Complete CCC API Confidentiality Agreement
3. Attend training webinar
4. Receive sandbox access
5. Each licensee must authorize access to their data

**Difficulty:** ⭐⭐⭐⭐⭐ (Very High) — Per-licensee authorization, confidentiality agreements, state oversight  
**Verdict:** Not practical for third-party data collection unless partnering with operators individually

### 3.5 Direct Dispensary Websites

**What it is:** Some dispensaries host their own menu systems, not powered by any aggregator platform.

**MA Relevance:** Estimated 15-30 MA dispensaries have custom/independent menu systems. These are typically:
- Larger MSOs with custom tech stacks
- Dispensaries using lesser-known e-commerce platforms (Carrot, Mosaic, Rank Really High, Breadstack)
- Stores with WordPress/Shopify-based menu pages

**How to identify them:** Cross-reference CCC retailer list against known Dutchie/Weedmaps/Jane operators. The remainder are either:
1. Not selling online at all (walk-in only)
2. Using a custom/niche menu system

**Access Method:** Per-site web scraping (each site is different)  
**Difficulty:** ⭐⭐⭐⭐ (High) — Each site requires custom scraping logic  
**Estimated Coverage Gain:** +10-20 stores (but high effort per store)

### 3.6 Headset

**What it is:** Leading cannabis data & market intelligence platform. Combines POS data from 3,500+ retailers with e-commerce/menu data.

**MA Coverage:** Massachusetts is a confirmed tracked market. Headset has direct POS integrations giving them the "most complete market picture of any cannabis data provider."

**What they offer:**
- POS-level sales data (actual transaction data, not just menu prices)
- E-commerce menu & sales data (NEW product combining POS + online data)
- Daily visibility into pricing, availability, performance
- Brand performance, category trends, basket analytics

**Pricing:** Enterprise subscription model. Not publicly listed. Industry estimates:
- **$15,000-$50,000+/year** depending on markets and data depth
- Single-state access may be on the lower end (~$15-25K/year)
- E-commerce data is a premium add-on

**Application Process:**
1. Request demo at `headset.io`
2. Sales consultation to scope needs
3. Enterprise agreement

**Difficulty:** ⭐⭐ (Low — just buy it) but ⭐⭐⭐⭐⭐ (Cost)  
**Verdict:** Expensive but would give us actual POS sales data (not just menu prices). Could be a competitive data source for GLASS premium tier. Worth exploring for ROI.

### 3.7 BDSA

**What it is:** Cannabis industry data analytics and business intelligence. Provides retail sales tracking, pricing data, market forecasts.

**MA Coverage:** Confirmed MA market coverage. Daily insights product includes menu-listed and post-discounted pricing.

**What they offer:**
- Retail Sales Tracking: what's selling, where, when, at what price
- Pricing & Promotion Strategy data
- Five levels of product categories + attributes (THC, CBD, CBN, pack size, flavor, strain)
- Daily Insights: pricing, out-of-stock, basket analytics
- Consumer insights and market forecasts

**Pricing:**
- BDSA Store (`store.bdsa.com`) sells individual reports
- GreenEdge™ subscription platform
- Through NCIA membership: Market Dashboards free ($3,000 annual value)
- Full subscription: Estimated **$20,000-$75,000+/year** (enterprise)

**Application Process:**
1. Contact BDSA through `bdsa.com`
2. Or join NCIA for basic dashboard access
3. Purchase individual reports from BDSA Store

**Difficulty:** ⭐⭐ (Low — just buy it) but ⭐⭐⭐⭐⭐ (Cost)  
**Verdict:** Similar to Headset. The NCIA membership path could give basic market dashboards at low cost.

### 3.8 CCC Public Data — What We Have vs. What's Available

**Currently Ingesting (7 datasets):**

| Dataset | File | Description |
|---------|------|-------------|
| Licensed operators | `commence-ops.csv` | 772 licensed operators at commence-ops stage |
| Avg monthly price/oz | `avg-monthly-price-oz.csv` | Statewide average retail price per gram |
| Facility sales stats | `facility-sales-stats.csv` | Per-facility sales data |
| Adult market by county | `adult-market-data-counties.csv` | County-level market data |
| Retail/delivery sales | `itd-retail-delivery-sales.csv` | Inception-to-date sales by category |
| Medical facility stats | `medical-facility-stats.csv` | Medical dispensary data |
| THC/THCA testing | `testing-thc-thca.csv` | Lab testing results (29MB!) |

**Potentially Missing CCC Data Sources:**

1. **Weekly Sales Reports** — CCC publishes weekly sales figures (we may already have this in `ccc_weekly_sales` table)
2. **Pending Applications** — Track upcoming dispensaries before they open (in `ccc_pending_applications`)
3. **Plant Activity Data** — Cultivation tracking (in `ccc_plant_activity`)
4. **Demographics Data** — Equity and workforce data (in `ccc_demographics`)
5. **Data Catalog CSVs** — CCC has downloadable CSVs at `masscannabiscontrol.com/open-data/data-catalog/`
6. **Sales & Product Distribution** — Detailed breakdown at `masscannabiscontrol.com/open-data/sales-and-product-distribution/`

**Assessment:** We appear to have good CCC coverage. The main gap is that CCC data is **aggregate/historical** — it tells us what happened last month/quarter, not today's live menu prices. CCC data complements but doesn't replace live scraping.

---

## Part 4: Coverage Gap Analysis & Recommendations

### 4.1 Current Coverage Summary

| Metric | Count | % of Active Retailers (418) |
|--------|-------|---------------------------|
| Operators with ANY price data (ever) | 385 | 92% |
| Operators with prices TODAY | 256 | 61% |
| Dutchie-only operators | 203 | 49% |
| Weedmaps-only operators | 244 | 58% |
| Both platforms | 38 | 9% |
| Other sources only | 8 | 2% |
| **Not covered (no sources)** | **564** | — |
| Not covered (active retailers specifically) | ~33 | 8% |

### 4.2 Top 5 Data Sources by Coverage Gain Potential

| Rank | Source | Est. New Stores | Difficulty | Priority |
|------|--------|----------------|-----------|----------|
| **1** | **Fix Weedmaps scraper** | +100-150 (recovery) | ⭐⭐ | 🔴 CRITICAL |
| **2** | **iHeartJane** | +50-80 new | ⭐⭐ | 🟡 HIGH |
| **3** | **Fix Dutchie failures** | +35-40 (recovery) | ⭐⭐ | 🟡 HIGH |
| **4** | **Leafly** | +20-40 new | ⭐⭐⭐ | 🟢 MEDIUM |
| **5** | **BLAZE API** (via BPN) | +5-15 new | ⭐⭐ | 🟢 MEDIUM |

### 4.3 Recommended Next Actions

#### Immediate (This Week)
1. **🔴 FIX WEEDMAPS SCRAPER** — 94% failure rate is catastrophic. This is 177 operators with no fresh data. Debug and fix immediately.
2. **🔴 FIX DUTCHIE SCRAPER** — 40/235 failures (17%). Identify which stores fail and why.

#### Short-Term (Next 2 Weeks)
3. **Build iHeartJane scraper** — API is semi-public with Swagger docs. URL pattern is `api.iheartjane.com/v1/stores/{id}/products`. Start by discovering all MA stores on iHeartJane, then scrape menus.
4. **Cross-reference uncovered retailers** — Take the 33+ CCC-licensed retailers with no price data. Google each one to identify their menu platform (Jane? Leafly? Custom?).

#### Medium-Term (Next Month)
5. **Build Leafly scraper** — Requires Camoufox for JS rendering. ~160 MA listings with menu data.
6. **Apply to BLAZE Partner Network** — Easy API access for delivery-focused operators.
7. **Apply to Treez Open API** — Good documentation at `code.treez.io`.

#### Long-Term (Next Quarter)
8. **Evaluate Headset/BDSA** — If GLASS needs actual POS transaction data (not just menu prices), explore enterprise data subscriptions. Could be valuable for premium tier pricing.
9. **NCIA Membership** — Get free BDSA Market Dashboard access ($3,000 value) for market-level data.
10. **POS partnership strategy** — Pick 2-3 POS systems (Treez, Flowhub, Cova) and formalize API partnerships for deeper data access.

### 4.4 Coverage Projection (If All Actions Completed)

| Phase | Additional Operators | Cumulative Coverage |
|-------|---------------------|-------------------|
| Current (today) | 256 | 61% of 418 |
| Fix scrapers (Week 1) | +100-150 | ~85-95% |
| Add iHeartJane (Week 2-3) | +50-80 | ~95-100%+ |
| Add Leafly + BLAZE (Month 2) | +20-40 | ~100%+ |
| **Total potential** | **418+** | **>100% coverage** |

With scraper fixes alone (no new sources), we should reach 85-95% daily coverage. Adding iHeartJane would push us to near-complete coverage of all active MA retailers.

---

## Appendix A: Database Schema Quick Reference

| Table | Records | Notes |
|-------|---------|-------|
| operators | 1,051 | All known MA cannabis operators |
| sources | 532 | Scraping sources (235 Dutchie, 282 Weedmaps, 15 other) |
| prices | 150,431 | All scraped price data points |
| products | 118,392 | Unique products |
| ccc_licenses | 772 | CCC licensed operators (770 matched to operators) |
| scrape_runs | many | Scrape job history |

## Appendix B: Key API Endpoints for New Sources

| Source | Endpoint | Auth Required |
|--------|---------|---------------|
| iHeartJane API Docs | `api.iheartjane.com/jane-api-docs/index.html` | No (read) |
| iHeartJane Products | `api.iheartjane.com/v1/stores/{id}/products` | No |
| BLAZE API Docs | `apidocs.blaze.me` | Partner key |
| Treez API Docs | `code.treez.io` | Partner key |
| Flowhub API | Contact flowhub.com | Partner key |
| Metrc MA API | `api@metrc.com` | Licensee key |
| CCC Open Data | `masscannabiscontrol.com/open-data/data-catalog/` | No |

## Appendix C: POS System Application Process Summary

| POS System | API Docs Public? | Application Path | Est. Timeline |
|-----------|-----------------|------------------|---------------|
| Dutchie POS | Partial | Per-dispensary API key request | Weeks (per-store) |
| Treez | ✅ Yes (`code.treez.io`) | Partner agreement | 2-4 weeks |
| Flowhub | No (but "open API") | Partnership team contact | 2-4 weeks |
| BLAZE | ✅ Yes (`apidocs.blaze.me`) | BPN application at `blaze.me/bpn/` | 1-2 weeks |
| Cova | No | Partner request | 2-4 weeks |
| Meadow | No | Partnership team contact | 2-4 weeks |
| BioTrack | Partial | Integrator agreement | 2-4 weeks |
| METRC | Restricted | State-level application + per-licensee auth | Months |
