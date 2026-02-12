# Newsletter Pipeline Audit — The Operator's Margin Report

**Audit Date:** February 12, 2026  
**Auditor:** Senior Marketing Operations Strategist (Subagent)  
**Scope:** Full pipeline health, content quality, GLASS integration plan, landing page, growth strategy  
**Last Pipeline Run:** February 8, 2026 (4 days ago)

---

## Executive Summary

The newsletter pipeline is **technically functional but operationally immature**. All 9 stages ran on Feb 8, but the validation stage returned **150 issues (101 errors, 49 warnings)** and the quality checker never ran. The content produced is decent editorially but riddled with data quality problems — past events listed as upcoming, news articles misidentified as events, and a top story sourced from a *Rockland County* (New York) business journal presented as MA news.

The biggest opportunity is **GLASS integration**. GLASS already scrapes 500+ MA dispensaries daily with 70K+ product price observations. This transforms the newsletter from a news aggregator into the only **data-first intelligence brief** in MA cannabis. No competitor has this. Properly integrated, GLASS data makes the newsletter indispensable rather than optional.

**Overall Grade: C+** — Good foundation, poor execution, massive untapped potential.

---

## 1. Pipeline Health Assessment

### 1.1 End-to-End Status: ⚠️ RUNS BUT FAILS VALIDATION

The pipeline ran all 9 stages on 2026-02-08. Stage results:

| Stage | Status | Duration | Records | Issues |
|-------|--------|----------|---------|--------|
| News | ✅ Success | 6.3s | 28 articles | 5 missing `why_ma_impact` |
| Events | ✅ Success | 5.3s | 54 events | **49 TBD dates, 4 past events** |
| Social | ✅ Success | 5.5s | 14 posts | None |
| Tools | ✅ Success | 5.8s | 43 tools | **43 missing `why_ma_impact`** |
| CCC Ingest | ✅ Success | 152s | 14 datasets | None |
| Market | ✅ Success | 0.1s | 4 pulses | None |
| Validate | ❌ FAIL (exit 1) | 0.06s | — | **150 issues** |
| Compose | ✅ Success | 0.05s | — | — |
| Quality | ❌ FAIL (exit 1) | — | — | Link/section checks failed |

**Critical finding:** The pipeline has **no gate stages** (`GATE_STAGES = set()`). Validation and quality checks run but cannot block composition or distribution. The pipeline happily produces a draft even when validation reports 101 errors.

### 1.2 Scraper Health

| Scraper | Working? | Quality | Key Issue |
|---------|----------|---------|-----------|
| **News** (Brave Search) | ✅ Yes | 🟡 Medium | Top story was from a NY publication. MA-local scoring works but Brave results are imprecise. |
| **Events** (Brave Search) | ⚠️ Broken | 🔴 Poor | 49 of 54 events have TBD dates. Scraper returns **news articles** as events. "Cannabis Cafes Are Legal In Massachusetts" is not an event. Events scraper is fundamentally flawed. |
| **Social** (Reddit API) | ✅ Yes | 🟢 Good | 14 relevant posts from r/bostontrees, r/mainetrees, r/cannabiscultivation. Operator relevance filtering works. |
| **Tools** (Brave Search) | ✅ Yes | 🟡 Medium | 43 results, but all geo_scope=national with no `why_ma_impact` notes. Many are generic SaaS listings, not actionable tools. |
| **CCC Ingest** | ✅ Yes | 🟢 Good | Successfully fetches 14 CCC datasets. Takes 2.5 minutes (longest stage). Demographic trend card generated. |
| **Market Data** | ✅ Yes | 🟢 Good | Pulls from lead-tool signals, CCC snapshots, hiring data. THE NUMBER rotation works well. |

### 1.3 Beehiiv Integration: ❌ NOT CONFIGURED

From MEMORY.md: "Beehiiv (newsletter): Partially set up." There is **no Beehiiv API integration** in the codebase. The pipeline generates `.md` and `.html` files but has no automated send path. Distribution is entirely manual.

The Beehiiv SKILL.md references a different newsletter structure entirely ("Market Intel / Operator Tips / Roviq Updates") that doesn't match the current pipeline output ("Top Story / THE NUMBER / Market Pulse / etc."). These two docs are **out of sync**.

### 1.4 Publication Cadence: IRREGULAR

- The only datestamped draft is from **Feb 8, 2026**
- The landing page promises "every tuesday"
- No evidence of regular weekly sends
- No subscriber data accessible from the codebase
- **Verdict:** The newsletter has been prototyped but not regularly published

### 1.5 Manual Steps Remaining

1. ❌ Triggering pipeline run (no cron/scheduler)
2. ❌ Reviewing draft quality (no automated human-review gate)
3. ❌ Fixing validation errors before send
4. ❌ Pasting content into Beehiiv manually
5. ❌ Scheduling and sending via Beehiiv
6. ❌ Monitoring open/click rates

---

## 2. Content Quality Review

### 2.1 Latest Draft Review: `newsletter_2026-02-08.md`

**Overall: 🟡 Passable but not good enough to build a subscriber base.**

#### What's Working
- **LLM editorial rewrite** of the top story is genuinely good. The social consumption analysis reads like a human wrote it, includes operator-specific implications, and ends with a clear action item
- **THE NUMBER** (934 operators) is concrete and sourced
- **Margin Tip** (eye-level product placement) is specific, actionable, and MA-relevant
- **Compliance Reminder** (purchase limit math) is useful and well-written
- **Voice consistency** — mostly maintains the direct, insider tone from BRANDING.md

#### What's Broken
- **Top story sourced from wrong state**: "Breaking News; Dispensary Openings; Legal Wrangling; Cannabis Licensing - Rockland County Business Journal" — this is a *Hudson Valley, NY* publication. The editorial rewrites it to sound MA-relevant, but the source article is about NY. This is misleading.
- **Events section is catastrophically bad**: Lists past events (Jan 5, Jan 19, Jan 28, Feb 3) and news articles as "events" (masslive.com article, masscannabiscontrol.com press release). None of these are upcoming events.
- **Quick Hits include a dubious source**: "dontlegalizedrugs.com" is not a credible news source. Including it damages newsletter credibility.
- **Market Pulse is thin**: Only 3 bullets, two are hiring/review data. Missing: wholesale price trends, license activity detail, retail foot traffic signals.
- **Demographic signal is raw data**: "applications_rollup is up 58.0% (9/9/2024 12:00:00 AM -> 9/9/2025 12:00:00 AM) for StrainActiveCount" — this is database output, not editorial content. No operator would understand or care about "StrainActiveCount."
- **No pricing data anywhere**: The BRANDING.md promises a "Local Price Index" and the LP shows "$14.20/eighth." The actual newsletter has zero pricing data.
- **No border intel**: Landing page promises "NY/CT/RI competitive border intel" but the newsletter doesn't deliver it.
- **Missing sections from LP promise**: No "This Week's Prep," no "Customer Corner," no "Border Patrol."

#### AI Detection Risk: 🟡 Medium

The LLM-rewritten top story is well-humanized. However, the Market Pulse bullets and Demographic Signal read like raw data output. The margin tips and compliance reminders are pre-written templates (good quality, but static across weeks). An attentive reader would notice the editorial analysis is sophisticated while the data sections are mechanical.

### 2.2 What Sections Exist vs. What Should Exist

| Section | In Current Draft | In LP Promise | In BRANDING.md | Assessment |
|---------|-----------------|---------------|----------------|------------|
| Top Story | ✅ | — | ✅ | Working but source quality issue |
| THE NUMBER | ✅ | — | ✅ | Good |
| Market Pulse | ✅ | — | ✅ | Too thin, needs GLASS data |
| Demographic Signal | ✅ | — | ✅ | Raw data, unusable as-is |
| License Watch | ✅ | — | ✅ | Only 1 item, same as top story |
| Tool of the Week | ✅ | — | ✅ | OK but generic |
| Events | ✅ (broken) | — | ✅ | Catastrophically broken |
| Quick Hits | ✅ | — | ✅ | Working, needs source quality filter |
| Margin Tip | ✅ | — | ✅ | Good, rotating library |
| Compliance Reminder | ✅ | — | ✅ | Good, rotating library |
| This Week's Prep | ❌ | ✅ | — | **Missing — LP promises it** |
| CCC Watchlist | ❌ | ✅ | — | **Missing — LP promises it** |
| Border Patrol | ❌ | ✅ | — | **Missing — LP promises it** |
| Local Price Index | ❌ | ✅ | — | **Missing — LP promises it** |
| Customer Corner | ❌ | ✅ | — | **Missing — LP promises it** |

**Gap: 5 sections promised on the landing page are completely absent from the newsletter.** This is a credibility problem — subscribers who sign up expecting CCC Watchlist updates and a Local Price Index will be disappointed.

---

## 3. GLASS Data Integration Plan

### 3.1 The Opportunity

GLASS is already scraping 500+ MA dispensaries daily via Dutchie and Weedmaps. Current data:
- **70K+ product price observations** per full run
- **912+ products per store** (average ~300)
- **5 product categories**: flower, pre-rolls, vaporizers, edibles, concentrates
- **Brand/strain data** per product
- **Operator information** from CCC database
- **Threat intelligence** (new dispensaries, closures, license changes)

No other MA cannabis newsletter has access to this data. This is the unfair advantage.

### 3.2 Proposed GLASS-Powered Sections

#### 📊 PRICE WIRE (NEW — replaces thin Market Pulse)
**Data Source:** `prices` table — weekly aggregation of price observations  
**Frequency:** Every issue  
**Auto-generatable:** ✅ Yes, fully automated

Content template:
```
📊 PRICE WIRE — This Week in MA Prices

MA Avg Flower 1/8th: $XX.XX (↑/↓ X.X% WoW)
MA Avg Pre-Roll 1g:  $XX.XX (↑/↓ X.X% WoW)  
MA Avg Edible 10mg:  $XX.XX (↑/↓ X.X% WoW)

💥 BIGGEST DROPS THIS WEEK:
• [Brand] [Product] at [Dispensary]: $XX → $XX (-XX%)
• [Brand] [Product] at [Dispensary]: $XX → $XX (-XX%)
• [Brand] [Product] at [Dispensary]: $XX → $XX (-XX%)

📈 BIGGEST INCREASES:
• [Brand] [Product] at [Dispensary]: $XX → $XX (+XX%)

YOUR POSITION: If you're selling flower above $XX/eighth, 
you're in the top 30% of MA pricing. Below $XX, you're in a race to the bottom.
```

**Technical Implementation:**
- SQL query: `SELECT category, AVG(price_per_unit), percentile_cont(0.3) WITHIN GROUP (ORDER BY price_per_unit) FROM prices WHERE observed_at > NOW() - INTERVAL '7 days' GROUP BY category`
- Compare against prior week's snapshot
- Auto-generate markdown section via template
- Include percentile context so operators know where they sit

#### 🏷️ BRAND MOVERS (NEW)
**Data Source:** `products` + `prices` tables — brand shelf presence and pricing trends  
**Frequency:** Every issue  
**Auto-generatable:** ✅ Yes, fully automated

Content template:
```
🏷️ BRAND MOVERS — Who's Gaining & Losing Shelf Space

GAINING:
• [Brand] — now in XX dispensaries (was XX last week). Avg price: $XX
• [Brand] — +XX new products listed this week

LOSING:
• [Brand] — dropped from XX to XX dispensaries
• [Brand] — XX products delisted this week

HOT PRODUCT: [Product name] by [Brand] — listed at XX stores, 
avg $XX, most popular in [region]
```

**Technical Implementation:**
- Weekly snapshot of `COUNT(DISTINCT dispensary_id)` per brand
- Delta against prior week
- New product listings = first appearance in `prices` table
- Delistings = product present last week, absent this week

#### 🔴 THREAT RADAR (NEW)
**Data Source:** `threats` table + CCC license data + new store detection  
**Frequency:** Every issue  
**Auto-generatable:** ✅ Partially (new stores auto-detected, analysis needs LLM)

Content template:
```
🔴 THREAT RADAR

NEW STORES DETECTED:
• [Store name] opened in [city] — [distance] from [existing competitors]
• [Store name] license approved for [city] — expected opening [date]

PRICE WAR ALERT:
• [City/Region]: 3+ stores now pricing flower below $XX/eighth
• [Store] cut prices XX% across XX products this week

LICENSE ACTIVITY:
• XX new applications submitted to CCC this week
• XX licenses approved | XX surrendered | XX under review
```

**Technical Implementation:**
- New stores = first appearance in `dispensaries` table
- Price war detection = region-level price compression analysis
- License activity from CCC ingest (already working)
- LLM adds operator implications for each threat

#### 📈 DATA SPOTLIGHT (NEW — rotating deep dive)
**Data Source:** Full GLASS dataset — one focused analysis per issue  
**Frequency:** Every issue (rotating topic)  
**Auto-generatable:** 🟡 Data auto-pulled, editorial needs LLM

Rotation cycle (8-week):
1. **Regional Price Map** — price differences by MA region (Boston vs. Valley vs. Cape vs. Berkshires)
2. **Category Trends** — which product categories are growing/shrinking
3. **Brand Concentration** — how many brands dominate MA shelves
4. **Price Floor Analysis** — what's the cheapest product in each category and who's selling it
5. **New vs. Established** — how new store pricing compares to established operators
6. **Weekend vs. Weekday** — price and availability patterns
7. **THC Pricing Curve** — does higher THC command higher prices in MA?
8. **Delivery vs. Storefront** — price comparison for delivery operators

**Technical Implementation:**
- Pre-built SQL queries for each topic
- LLM generates 150-200 word analysis from data results
- Include one simple chart/visualization (or link to GLASS dashboard)

#### 📋 CCC WATCHLIST (fulfills LP promise)
**Data Source:** CCC open data (already ingested) + Brave Search for CCC news  
**Frequency:** Every issue  
**Auto-generatable:** 🟡 Partially

This section is **already promised on the landing page** but doesn't exist. Combine:
- CCC ingest demographic/trend data (already working, needs better editorial)
- CCC meeting dates and agendas (add to news scraper queries)
- License approval/denial activity (from GLASS + CCC ingest)

### 3.3 GLASS → Newsletter Data Pipeline

```
GLASS Database (Railway/Neon)
    │
    ├── prices table ──────→ Price Wire (weekly aggregation)
    ├── products table ────→ Brand Movers (shelf presence delta)
    ├── dispensaries table ─→ Threat Radar (new store detection)
    ├── threats table ─────→ Threat Radar (competitive alerts)
    ├── alerts table ──────→ Data Spotlight (rotating deep dive)
    │
    └── SQL query layer ───→ glass_newsletter_processor.py (NEW)
                                  │
                                  ├── glass_data.json (pre-computed sections)
                                  │
                                  └── composer.py reads glass_data.json
                                        │
                                        └── Newsletter draft with GLASS sections
```

**New file needed: `scrapers/glass_data_processor.py`**
- Connects to GLASS database (Railway PostgreSQL)
- Runs pre-built aggregation queries
- Outputs `data/glass_data.json` with:
  - `price_wire`: category averages, biggest movers, percentiles
  - `brand_movers`: shelf presence changes, hot products
  - `threat_radar`: new stores, price war zones, license activity
  - `data_spotlight`: rotating deep-dive data for the week

### 3.4 Integration Priority

| Section | Value to Reader | Build Effort | Data Available | Priority |
|---------|----------------|-------------|----------------|----------|
| Price Wire | 🔥🔥🔥 Highest | Low (SQL + template) | ✅ Now | **P0 — Build first** |
| Threat Radar | 🔥🔥🔥 Highest | Medium (detection logic) | ✅ Now | **P0 — Build first** |
| Brand Movers | 🔥🔥 High | Low (SQL + delta) | ✅ Now | **P1 — Build second** |
| Data Spotlight | 🔥🔥 High | Medium (8 queries + LLM) | ✅ Now | **P1 — Build second** |
| CCC Watchlist | 🔥 Medium | Low (reformat existing) | ✅ Now | **P1 — Quick win** |

---

## 4. Landing Page Assessment

### 4.1 What's Working

- **Design quality is high**: Dark mode, Space Grotesk + Inter + Gloria Hallelujah fonts, film grain overlay. Looks premium and anti-AI. This is genuinely better than most cannabis industry LPs.
- **Voice is excellent**: "Written in MA, not generated in CA" — perfect positioning. The testimonials feel authentic (role/location only, no names).
- **MA-specific framing**: "From the Berkshires to Boston" — signals local knowledge.
- **Content preview is compelling**: The sample issue (#47) with "Feb Break + Flower Expo Strategy + Border Watch" is exactly what operators would want.
- **Social proof numbers**: "520+ MA operators" and "62% open rate" are strong (if real).

### 4.2 What's Not Working

- **Signup form goes nowhere**: `action="#"` — the form doesn't submit. There's no Beehiiv integration. Subscribers literally cannot sign up.
- **Fake social proof numbers**: "520+ MA operators" and "62% open rate" are likely aspirational/fabricated. If real, they're not connected to any tracking.
- **Content mismatch**: LP promises "This Week's Prep," "CCC Watchlist," "Border Patrol," "Local Price Index," "Customer Corner" — **none of which exist in the actual newsletter**. This is a credibility bomb when subscribers get their first issue.
- **"About" section has placeholder**: "— Jake" signature with a 👤 placeholder avatar. Who is Jake? This doesn't match Roviq's brand.
- **Cross-link broken**: "→ Check out The MA Market Intel Brief" links to `../intel.html` which likely doesn't exist.
- **No GLASS connection**: Zero mention of price intelligence, market data, or the data advantage GLASS provides.

### 4.3 Comparison to GLASS Design Language

The LP uses a warm dark palette (`#1a1a1a` background, `#d4a853` gold accent, `#9caea0` muted green) with handwritten font accents.

GLASS uses a premium black & white palette (`#000000` background, `#C45A3C` copper accent, Playfair Display + Geist Mono).

**These are different but complementary.** The newsletter LP is warmer and more editorial; GLASS is colder and more data-driven. Recommendation: keep the LP's warm editorial tone but add a "Powered by GLASS" data preview section showing a price chart or market snapshot. This creates a bridge between the newsletter and GLASS signups.

---

## 5. Distribution & Growth

### 5.1 Current Subscriber Count: UNKNOWN (likely 0)

There's no evidence of any subscribers. The signup form doesn't work. Beehiiv is "partially set up" per MEMORY.md. The newsletter has been built as a prototype, not launched.

### 5.2 Growth Strategy Recommendations

#### Phase 1: Launch (Weeks 1-4)
1. **Fix the signup form** — Connect to Beehiiv API or embed Beehiiv form
2. **Publish the first real issue** — With GLASS Price Wire + Threat Radar
3. **Seed with existing contacts** — AC, CH, HOP, Delivered, and their networks
4. **Send to CCC mailing list** — CCC has public meeting attendee lists

#### Phase 2: Growth (Weeks 5-12)
1. **GLASS signup → Newsletter auto-enroll** — Every GLASS free-tier user gets the newsletter automatically (opt-out, not opt-in)
2. **Newsletter → GLASS upsell** — Each issue includes a "Want the full data? →" CTA linking to GLASS
3. **Price Wire teasers** — Show 2-3 price data points in the newsletter, gate the full dashboard behind GLASS signup
4. **Reddit seeding** — Post weekly data highlights from Price Wire to r/bostontrees
5. **AC wholesale outreach** — Include newsletter CTA in AC's toll-processing outreach (85 emails already ready)

#### Phase 3: Monetization (Weeks 13+)
1. **Premium tier** — Full GLASS data access + exclusive weekly deep dives
2. **Sponsored tool/brand features** — "Tool of the Week" can become sponsored ($500-1K/week)
3. **Lead gen for Roviq** — Newsletter readers become Roviq consulting prospects

### 5.3 Newsletter → GLASS Funnel

```
Newsletter Landing Page
    ↓ (free signup)
Weekly Newsletter (free)
    ↓ (Price Wire teaser → "Get full data")
GLASS Free Tier (Price Wire + Threat Radar)
    ↓ (margin engine, alerts → "Unlock premium")
GLASS Premium ($49-99/mo)
    ↓ (consulting CTA)
Roviq Agency Services ($3K+ sprints)
```

This funnel is the **core Roviq customer acquisition engine**. The newsletter is not a standalone product — it's the top of a $0 → $49/mo → $3K+ pipeline.

---

## 6. Automation Gaps

### 6.1 What Could Be Fully Automated

| Component | Current State | Can Automate? | How |
|-----------|--------------|---------------|-----|
| Pipeline trigger | Manual `python pipeline.py` | ✅ Yes | Cron job or GitHub Actions |
| News scraping | Automated via Brave | ✅ Already done | — |
| Social scraping | Automated via Reddit | ✅ Already done | — |
| CCC data ingest | Automated via API | ✅ Already done | — |
| GLASS data pull | ❌ Doesn't exist | ✅ Yes | New `glass_data_processor.py` |
| Price Wire section | ❌ Doesn't exist | ✅ Yes | SQL templates + formatter |
| Brand Movers section | ❌ Doesn't exist | ✅ Yes | SQL delta + formatter |
| Threat Radar section | ❌ Doesn't exist | ✅ Yes | Detection logic + formatter |
| Newsletter composition | Automated via composer.py | ✅ Already done | — |
| HTML generation | Automated via markdown_to_html | ✅ Already done | Needs BRANDING.md colors |
| Beehiiv publishing | ❌ Manual | ✅ Yes | Beehiiv API integration |

### 6.2 What Needs Human Review

| Component | Why Human Review? |
|-----------|------------------|
| Top story selection | Verify source credibility, check for misleading framing |
| Editorial analysis (LLM) | Catch hallucinations, verify claims |
| Event listings | Verify dates and relevance (current scraper is broken) |
| Quick Hits source quality | Filter out dubious sources like dontlegalizedrugs.com |
| Final draft quality | Overall tone, coherence, newsletter-worthiness |

### 6.3 Recommended Publication Cadence

**Weekly, every Tuesday at 7:00 AM ET** (as promised on LP)

- **Sunday night**: Automated pipeline run (cron)
- **Monday morning**: Human review of draft (~15 minutes)
- **Monday afternoon**: Fixes applied, draft finalized
- **Tuesday 7:00 AM**: Auto-publish via Beehiiv API

### 6.4 GLASS Auto-Generated Sections

**Sections that can be 100% automated with GLASS data:**
1. Price Wire — SQL aggregation → template → markdown
2. Brand Movers — SQL delta → template → markdown
3. Threat Radar (new stores/price wars) — detection logic → template → markdown
4. THE NUMBER — already automated, can add GLASS metrics to rotation
5. CCC Watchlist — already have CCC data, needs reformatting

**Sections that need LLM + human:**
1. Top Story editorial analysis
2. Data Spotlight deep dive
3. Quick Hits curation
4. Margin Tip (currently rotating library — fine)

---

## 7. Prioritized Fix List

### P0 — Must Fix Before Next Issue (this week)

| # | Issue | Effort | Impact |
|---|-------|--------|--------|
| P0-1 | **Fix events scraper** — returns news articles as events, 49/54 have TBD dates. Either fix date extraction or switch to a dedicated events source (Eventbrite API, CCC calendar scraping) | 4-6 hours | High — broken section embarrasses the whole newsletter |
| P0-2 | **Connect signup form to Beehiiv** — form currently goes nowhere (`action="#"`). Add Beehiiv embed or API integration | 1-2 hours | Critical — can't grow without working signup |
| P0-3 | **Build `glass_data_processor.py`** — new scraper stage that queries GLASS DB for Price Wire, Brand Movers, and Threat Radar data | 6-8 hours | High — this is the differentiation |
| P0-4 | **Add Price Wire section to composer** — consume `glass_data.json` and generate the Price Wire markdown section | 2-3 hours | High — delivers on "Local Price Index" LP promise |
| P0-5 | **Filter dubious news sources** — add source quality check. Block `dontlegalizedrugs.com` and similar non-credible domains | 30 min | Medium — credibility protection |
| P0-6 | **Fix top story geo-scoring** — current scoring let a Rockland County (NY) article become the top story. Tighten MA-local requirement | 1-2 hours | High — misleading content |

### P1 — Fix Within 2 Weeks

| # | Issue | Effort | Impact |
|---|-------|--------|--------|
| P1-1 | **Add Threat Radar section** — new store detection, price war alerts, license activity from GLASS + CCC | 4-6 hours | High — operators crave competitive intelligence |
| P1-2 | **Add Brand Movers section** — shelf presence tracking from GLASS data | 3-4 hours | Medium — interesting but less urgent |
| P1-3 | **Fix Demographic Signal editorial** — rewrite the raw database output ("applications_rollup is up 58.0%") into human-readable insight | 1-2 hours | Medium — currently unreadable |
| P1-4 | **Add CCC Watchlist section** — combine CCC ingest data + CCC meeting scraping into the section promised on LP | 3-4 hours | Medium — fulfills LP promise |
| P1-5 | **Update HTML template to match BRANDING.md** — current HTML uses green (#1a5f2a) instead of brand colors (navy #1A2332, green #22C55E, orange #F97316) | 2-3 hours | Medium — brand consistency |
| P1-6 | **Add Beehiiv API send integration** — automate publishing, not just draft generation | 4-6 hours | High — removes manual step |
| P1-7 | **Add cron/scheduler** — automate Sunday night pipeline runs | 1 hour | High — reliability |
| P1-8 | **Add gate stages back** — make validation errors block composition. Currently `GATE_STAGES = set()` | 30 min | Medium — quality enforcement |
| P1-9 | **Fix "About" section on LP** — remove "Jake" placeholder, use Randy's info or Roviq brand | 30 min | Low — but currently confusing |
| P1-10 | **Tools scraper: auto-generate `why_ma_impact`** — all 43 tools fail validation because they're national with no MA context note | 1-2 hours | Low — noisy validation errors |

### P2 — Fix Within Month

| # | Issue | Effort | Impact |
|---|-------|--------|--------|
| P2-1 | **Add Data Spotlight rotating section** — 8-topic deep dive using GLASS data | 8-12 hours | Medium — premium content |
| P2-2 | **Add "This Week's Prep" section** — MA holidays, staffing alerts, weather. Promised on LP | 4-6 hours | Medium — fulfills LP promise |
| P2-3 | **Add "Customer Corner" section** — scripts for common scenarios. Promised on LP | 3-4 hours | Low — nice-to-have |
| P2-4 | **Add "Border Patrol" section** — NY/CT/RI competitive intel. Promised on LP | 4-6 hours | Medium — fulfills LP promise |
| P2-5 | **Interactive charts in email** — embed sparkline SVGs or link to GLASS dashboard | 6-8 hours | Medium — visual differentiation |
| P2-6 | **Add subscriber tracking** — Beehiiv webhook for open/click analytics | 3-4 hours | Medium — growth measurement |
| P2-7 | **Align SKILL.md with pipeline** — newsletter SKILL.md describes a completely different structure than what the pipeline produces | 1 hour | Low — documentation hygiene |
| P2-8 | **Remove LP social proof until real** — "520+ operators" and "62% open rate" are unverifiable. Replace with "Join MA operators who…" | 15 min | Low — integrity |

---

## 8. Proposed New Newsletter Structure

### New Issue Format (with GLASS integration)

```
─────────────────────────────────────────────
THE OPERATOR'S MARGIN REPORT
Week of [DATE] · Issue #[N] · Read time: 7 min
─────────────────────────────────────────────

📊 PRICE WIRE                          ← NEW (GLASS)
MA average prices by category with WoW trends.
Biggest price drops and increases.
Your positioning context.

🔥 TOP STORY                           ← EXISTING (improved)
LLM editorial analysis of #1 MA cannabis story.
What it means for your margins.
What to do about it.

📊 THE NUMBER                           ← EXISTING (expanded)
Rotates through: operators, licenses, GLASS price data,
hiring, distress signals, new store count.

🔴 THREAT RADAR                         ← NEW (GLASS)
New stores detected. Price war zones.
License applications and approvals.
Competitive moves in your region.

🏷️ BRAND MOVERS                        ← NEW (GLASS)
Who's gaining shelf space. Who's losing it.
Hot products this week.

🏛️ CCC WATCHLIST                        ← NEW (fulfills LP promise)
Commission meeting updates.
Regulatory changes.
License activity summary.

📈 DATA SPOTLIGHT                        ← NEW (GLASS, rotating)
One deep-dive metric per issue.
Regional price maps, category trends, THC pricing curves.

⚡ QUICK HITS                           ← EXISTING
3 additional news items with source links.

🛠️ TOOL OF THE WEEK                     ← EXISTING
Featured cannabis industry tool.

💡 MARGIN TIP                           ← EXISTING
MA-specific, actionable margin improvement advice.

📋 COMPLIANCE REMINDER                   ← EXISTING
CCC compliance tips, rotating library.

📬 THAT'S THE REPORT
Reply CTA. GLASS upsell CTA.
─────────────────────────────────────────────
```

**Key changes:**
1. Price Wire leads — operators open for pricing data
2. Threat Radar is the "sticky" section — fear of missing competitive moves
3. Brand Movers gives them buyer intelligence
4. CCC Watchlist fulfills LP promise
5. Data Spotlight provides premium-feel content
6. GLASS CTAs woven throughout (not just at the end)

### Section Source Mapping

| Section | Primary Source | GLASS Data? | LLM Required? |
|---------|---------------|-------------|---------------|
| Price Wire | GLASS `prices` table | ✅ Yes | ❌ No (template) |
| Top Story | Brave Search + LLM | ❌ No | ✅ Yes |
| THE NUMBER | CCC + Lead Tool + GLASS | ✅ Partial | ❌ No |
| Threat Radar | GLASS `threats`/`dispensaries` + CCC | ✅ Yes | 🟡 Partial |
| Brand Movers | GLASS `products`/`prices` | ✅ Yes | ❌ No (template) |
| CCC Watchlist | CCC ingest + Brave | ❌ No | 🟡 Partial |
| Data Spotlight | GLASS all tables | ✅ Yes | ✅ Yes |
| Quick Hits | Brave Search | ❌ No | 🟡 Partial |
| Tool of Week | Brave Search | ❌ No | 🟡 Partial |
| Margin Tip | Static library | ❌ No | ❌ No |
| Compliance | Static library | ❌ No | ❌ No |

**Result: 5 of 11 sections powered by GLASS data.** The newsletter becomes a GLASS distribution channel, not just a news aggregator.

---

## 9. Recommended Tech Changes

### 9.1 New Files Needed

```
newsletter/
├── scrapers/
│   ├── glass_data_processor.py    ← NEW: Queries GLASS DB, outputs glass_data.json
│   └── ccc_calendar_scraper.py    ← NEW: Scrapes CCC meeting calendar
├── data/
│   └── glass_data.json            ← NEW: Pre-computed GLASS sections
├── beehiiv_publisher.py           ← NEW: Beehiiv API integration for automated sends
├── schedule.py                    ← NEW: Cron wrapper for scheduled runs
└── source_blocklist.txt           ← NEW: Blocked domains for news quality
```

### 9.2 Pipeline Changes

```python
# Updated STAGES in pipeline.py
STAGES = [
    ("news", "scrapers/news_scraper.py", ["--days", "7"]),
    ("events", "scrapers/events_scraper.py", ["--days", "30"]),   # Needs major fix
    ("social", "scrapers/social_scraper.py", ["--limit", "20"]),
    ("tools", "scrapers/tools_scraper.py", []),
    ("ccc_ingest", "scrapers/ccc_ingest.py", []),
    ("glass", "scrapers/glass_data_processor.py", []),            # NEW
    ("market", "scrapers/market_data_processor.py", []),
    ("validate", "content_validator.py", []),
    ("compose", "composer.py", []),
    ("quality", "quality_checker.py", []),
    ("publish", "beehiiv_publisher.py", []),                       # NEW
]

# Re-enable gate stages
GATE_STAGES = {"validate"}  # Block composition if validation fails
```

### 9.3 Environment Variables Needed

```
# GLASS database connection
GLASS_DATABASE_URL=postgresql://...@turntable.proxy.rlwy.net:18582/railway

# Beehiiv API
BEEHIIV_API_KEY=...
BEEHIIV_PUBLICATION_ID=...

# Already configured
BRAVE_API_KEY=...
OPENAI_API_KEY=...
```

### 9.4 Dependencies to Add

```
# requirements.txt additions
psycopg2-binary>=2.9.0,<3.0.0    # PostgreSQL for GLASS queries
```

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GLASS data staleness (scraper fails) | Medium | High | Fallback to "Price data unavailable this week" with CTA to check GLASS directly |
| Events scraper continues to return garbage | High | Medium | Replace Brave-based events scraper with dedicated sources (Eventbrite API, CCC calendar) |
| Top story from wrong state (again) | Medium | High | Add strict MA-origin validation: require domain in MA-trusted list OR explicit MA mention in title |
| Newsletter fatigue (operators stop reading) | Low | High | GLASS data makes it indispensable — no substitute for price intel |
| Beehiiv API changes or rate limits | Low | Low | Simple REST API, well-documented, unlikely to break |
| GLASS database schema changes break newsletter queries | Medium | Medium | Pin queries to specific columns; add schema version check |

---

## 11. Success Metrics

### Launch Metrics (Week 1-4)
- [ ] First issue sent via Beehiiv
- [ ] Signup form functional
- [ ] Price Wire section populated with GLASS data
- [ ] 50+ subscribers (from existing network)

### Growth Metrics (Month 2-3)
- [ ] 200+ subscribers
- [ ] 45%+ open rate (industry avg is 21%)
- [ ] 10%+ click rate on GLASS CTAs
- [ ] Weekly publication cadence maintained

### Revenue Metrics (Month 3-6)
- [ ] 500+ subscribers
- [ ] 10+ GLASS signups attributed to newsletter
- [ ] 2+ Roviq consulting leads from newsletter readers
- [ ] First sponsored Tool of the Week ($500+)

---

*This audit covers all files read, all data analyzed, all gaps identified. The single biggest ROI action is building `glass_data_processor.py` (P0-3) and the Price Wire section (P0-4). Everything else is incremental improvement. GLASS data is the moat.*
