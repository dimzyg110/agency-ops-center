# GLASS Public Market Intelligence Page Plan

**Proposed route:** `/market` (primary) with `/intelligence` as canonical alias/redirect if desired  
**Positioning:** The public source of truth for Massachusetts cannabis market data  
**Primary goals:** authority/backlinks + newsletter signups + premium GLASS conversions

---

## 1) Product Strategy Summary

The public page should act as a **free, citation-worthy data hub** with enough depth to prove GLASS quality while clearly preserving premium value.

### Strategic split
- **Free (indexable, shareable):** headline market stats, MA price index by category + trend, weekly CCC sales trend, selective market activity, curated news/events.
- **Teaser/Locked (conversion):** deeper competitor-level analytics, full regional drilldowns, downloadable exports, full historical and operator-level comparison tools.

### North-star outcomes
1. Rank for “Massachusetts cannabis market data” and related terms.
2. Be link-worthy for journalists/bloggers (daily updated timestamp + clear methodology).
3. Convert traffic into:
   - Newsletter signup (“Get this weekly report”)
   - GLASS premium signup (“Unlock full dashboard”)

---

## 2) Information Architecture & Page Wireframe

## Proposed page flow

1. **Market Snapshot Hero**
2. **MA Price Index (core hook)**
3. **Market Activity (openings + licensing + CCC highlights)**
4. **Weekly Sales Tracker (CCC)**
5. **Industry News Feed**
6. **Premium Data Teaser (blurred/locked cards)**
7. **Newsletter Signup block**
8. **FAQ (SEO)**
9. **Internal link rail + footer trust signals**

## Wireframe (desktop)

```text
┌──────────────────────────────────────────────────────────────┐
│ Nav (Landing style)                                        │
├──────────────────────────────────────────────────────────────┤
│ HERO: "Massachusetts Cannabis Market Intelligence"          │
│ [Stat pill] Operators [Stat pill] Products [Stat pill] Obs │
│ Data as of {date}   Updated: daily/weekly per dataset      │
│ CTA1: Get Weekly Report  CTA2: Unlock Full Dashboard       │
├──────────────────────────────────────────────────────────────┤
│ PRICE INDEX (signature section)                            │
│ Category cards: Flower / Edibles / Vapes / Conc / Pre-roll │
│ Each: current avg, WoW arrow, MoM arrow, sparkline         │
│ Regional tabs/chips: Boston | Western MA | Cape | Central  │
│ Methodology link + Last updated                            │
├──────────────────────────────────────────────────────────────┤
│ MARKET ACTIVITY                                             │
│ Left: New dispensaries this month                          │
│ Mid: Pending license apps pipeline                         │
│ Right: CCC meeting highlights                               │
├──────────────────────────────────────────────────────────────┤
│ WEEKLY SALES TRACKER                                        │
│ Line chart total MA sales + stacked/category mix            │
│ YoY/WoW badges + source: CCC                                │
├──────────────────────────────────────────────────────────────┤
│ INDUSTRY NEWS FEED (5-10 curated links)                     │
│ + Upcoming events strip                                     │
├──────────────────────────────────────────────────────────────┤
│ PREMIUM TEASER (3 locked visual cards)                      │
│ [blurred chart] [blurred map] [blurred competitor panel]    │
│ CTA: Unlock full dashboard                                  │
├──────────────────────────────────────────────────────────────┤
│ NEWSLETTER SIGNUP                                            │
│ "Get this data every week" + embedded form                 │
├──────────────────────────────────────────────────────────────┤
│ FAQ (SEO intent questions)                                  │
├──────────────────────────────────────────────────────────────┤
│ Internal links: /newsletter / (main LP) /signup            │
└──────────────────────────────────────────────────────────────┘
```

## Mobile wireframe
- Single-column stacked modules.
- Hero stat pills become 2x2 grid cards.
- Price index category cards become horizontal snap carousel.
- Regional breakdown becomes segmented control with accordion detail.
- Teaser cards stack vertically with one CTA repeated after card #2.
- Sticky bottom mobile CTA: `Get Weekly Report`.

---

## 3) Data Mapping by Section (sources + rendering)

## A. Market Snapshot (Hero)
**Purpose:** prove scale and freshness quickly.

**Displayed metrics**
- Operators tracked (e.g., 492)
- MA dispensaries tracked daily (500+)
- Products tracked (20,000+)
- Price observations (21,000+ and growing)
- Data freshness label: `Data as of {date}`

**Sources**
- GLASS internal aggregate endpoint (recommended new endpoint):
  - `GET /api/public/market/snapshot`
- Fallback static references from platform totals if API not ready.

**Update frequency**
- Daily (or near-real-time if pipeline supports it)

---

## B. Price Index (Signature Hook)
**Purpose:** unique public moat + backlink magnet.

**Displayed content**
- Category average prices:
  - Flower, Edibles, Vapes, Concentrates, Pre-rolls
- Trend badges:
  - WoW: up/down/flat
  - MoM: up/down/flat
- Mini sparkline for each category
- Regional breakdown:
  - Boston, Western MA, Cape Cod, Central MA, North Shore/South Shore (final region taxonomy from ops)

**Sources**
- Newsletter CCC data:
  - `/projects/internal/newsletter/data/ccc/average_price.json`
- Optional supplemental GLASS endpoint for regional modeling:
  - `GET /api/public/market/price-index?region=...&range=...`

**Computation notes**
- Normalize per comparable units before averaging.
- For trend arrows:
  - WoW = latest period vs prior period
  - MoM = latest month vs prior month
- Define “flat” threshold (e.g., +/-0.5%).

**Update frequency**
- Weekly (aligned to CCC cadence); region estimates can refresh daily if GLASS supports.

---

## C. Market Activity
**Purpose:** show market movement (openings + licensing + regulator context).

**Subsections & sources**
1. **New dispensaries opened this month**
   - GLASS internal openings tracker endpoint (recommended):
     - `GET /api/public/market/activity/openings?month=YYYY-MM`
2. **License applications in pipeline**
   - `/projects/internal/newsletter/data/ccc/pending_applications.json`
3. **CCC meeting highlights**
   - Derived from newsletter curation pipeline and CCC notes ingest:
     - `news_weekly.json` + CCC-specific filtered stories

**Update frequency**
- Openings: daily/weekly
- Pending applications: weekly
- Highlights: weekly (post-curation)

---

## D. Weekly Sales Tracker
**Purpose:** broad market demand signal + trusted public source citation.

**Displayed content**
- Total MA cannabis sales line chart over time
- Optional rolling 4-week average
- Category mix stacked area/bar (if data shape allows)
- YoY/WoW badges

**Sources**
- `/projects/internal/newsletter/data/ccc/weekly_sales.json`
- Optional category split helper:
  - `/projects/internal/newsletter/data/ccc/facility_sales.json` (validate semantic mapping in implementation)

**Update frequency**
- Weekly

---

## E. Industry News Feed
**Purpose:** keep page fresh and return-worthy.

**Displayed content**
- 5–10 curated headlines with source, date, and external link
- Optional “Upcoming Events” mini-list

**Sources**
- `/projects/internal/newsletter/data/news_weekly.json`
- `/projects/internal/newsletter/data/events_upcoming.json`

**Update frequency**
- Weekly (or twice weekly if editor process permits)

---

## F. Premium Data Teaser (Locked)
**Purpose:** convert curiosity to signup.

**Displayed content**
- 2–3 blurred/locked cards based on premium viz roadmap:
  - Competitive price undercut heatmap
  - Brand shelf-share movers
  - Threat radar / license-proximity model

**Sources**
- Use static snapshot images or server-rendered chart previews from premium datasets.
- Reference visuals from `VISUALIZATION-PLAN.md` style language.

**Update frequency**
- Weekly refresh for credibility

---

## G. Newsletter Signup
**Purpose:** primary low-friction conversion.

**Displayed content**
- Embedded form + social proof line
- Copy: “Get MA cannabis market data every week.”

**Source/Integration**
- Beehiiv embed/API (implementation detail in app)
- Trigger event tracking on submit for funnel attribution

**Update frequency**
- Real-time

---

## 4) Free vs Locked Content Matrix

| Section | Public Free | Locked/Teaser |
|---|---|---|
| Snapshot | Full top-level counts | Deep operator drilldown |
| Price Index | Category averages + WoW/MoM + limited regions | Store-level, SKU-level, downloadable historical views |
| Market Activity | Monthly openings count + pending apps totals + select highlights | Entity-level competitor alerts, geofenced threat model |
| Sales Tracker | MA total trend + basic mix | Advanced cohorts, custom date range exports |
| News Feed | 5–10 headlines + events strip | Full intelligence brief + annotated implications |
| Premium Teasers | Blurred previews only | Full interactive visualizations |

**Rule of thumb:** give **answers** publicly, keep **decision systems/workflows** premium.

---

## 5) SEO Strategy

## Core keyword clusters
- Primary:
  - massachusetts cannabis market data
  - massachusetts cannabis market intelligence
  - ma dispensary prices
- Secondary:
  - ma cannabis price index
  - massachusetts marijuana sales data
  - cannabis operator intelligence
  - ccc cannabis data massachusetts

## On-page SEO plan
- **URL:** `/market` (short, memorable)
- **Title tag:** `Massachusetts Cannabis Market Data & Price Index | GLASS`
- **Meta description:** `Track MA dispensary prices, weekly cannabis sales, license pipeline activity, and market intelligence updates from GLASS.`
- **H1:** `Massachusetts Cannabis Market Intelligence`
- Structured H2s per section for snippet eligibility.
- Add “Last updated” in crawlable HTML near top.

## Schema markup (JSON-LD)
1. **WebPage**
2. **Dataset** (for public price index + sales tracker)
3. **Organization** (GLASS entity)
4. **FAQPage** for FAQ section

### Dataset schema must include
- name, description
- temporalCoverage
- spatialCoverage: Massachusetts
- creator/publisher: GLASS
- dateModified
- license and citation guidance

## FAQ targets (example questions)
- What is the current average dispensary price in Massachusetts?
- How large is the Massachusetts cannabis market?
- Where can I find MA cannabis sales data by week?
- How many cannabis operators are active in Massachusetts?
- How often does GLASS update market data?

## Internal linking
- Link to `/newsletter` (“Get weekly MA market report”)
- Link to main LP (`/`) and `/signup`
- Optional future links to methodology page `/market/methodology`

---

## 6) Design & Frontend System Alignment

From current code/design tokens:
- Continue the GLASS visual language:
  - Black/white luxury + copper accent (`glass.accent #C45A3C`)
  - Typography stacks from tailwind config (`display`, `sans`, `mono`)
- Reuse existing layout rhythm from `Landing.tsx`:
  - alternating high-contrast sections
  - strong editorial headlines
  - compact mono metadata labels

### UX rules
- Every chart block includes:
  - title
  - one-sentence takeaway
  - source + update time
- Tooltips should be concise and mobile-safe.
- All locked states visually distinct but still informative.

---

## 7) Component Breakdown (Developer-Facing)

## Page-level
- `MarketIntelligencePage.tsx` (route container)
- `MarketSEO.tsx` (meta + JSON-LD injectors)

## Section components
- `MarketHeroSnapshot.tsx`
- `PriceIndexSection.tsx`
  - `PriceCategoryCard.tsx`
  - `PriceTrendBadge.tsx`
  - `RegionSelector.tsx`
- `MarketActivitySection.tsx`
  - `OpeningsCard.tsx`
  - `LicensePipelineCard.tsx`
  - `CCCHighlightsCard.tsx`
- `WeeklySalesSection.tsx`
  - `SalesLineChart.tsx`
  - `CategoryMixChart.tsx`
- `IndustryNewsSection.tsx`
  - `HeadlineList.tsx`
  - `EventsMiniList.tsx`
- `PremiumTeaserSection.tsx`
  - `LockedVizCard.tsx`
- `NewsletterSignupSection.tsx`
- `MarketFAQSection.tsx`
- `MethodologyDisclosure.tsx` (reusable below charts)

## Data/hooks layer
- `useMarketSnapshot()`
- `usePriceIndex(region, range)`
- `useMarketActivity(month)`
- `useWeeklySales(range)`
- `useIndustryNews(limit)`

## API endpoints (recommended public namespace)
- `GET /api/public/market/snapshot`
- `GET /api/public/market/price-index`
- `GET /api/public/market/activity`
- `GET /api/public/market/weekly-sales`
- `GET /api/public/market/news`

(Implementation can initially proxy newsletter JSON files, then migrate to DB-backed services.)

---

## 8) Newsletter Pipeline Connection

The page should consume the same weekly intelligence outputs as newsletter generation to ensure consistency:

- CCC datasets:
  - `ccc/weekly_sales.json`
  - `ccc/average_price.json`
  - `ccc/facility_sales.json`
  - `ccc/pending_applications.json`
  - `ccc/industry_demographics.json`
  - `ccc/plant_activity.json`
- Editorial feeds:
  - `news_weekly.json`
  - `events_upcoming.json`
  - `tools_weekly.json` (optional sidebar)

### Operational recommendation
- Add a normalization step that writes a clean `public_market_payload.json` each run.
- Web app consumes this normalized payload to avoid coupling UI to raw CCC schema changes.

---

## 9) Update Frequency & Freshness Labels

| Section | Refresh cadence | UI freshness label |
|---|---|---|
| Snapshot | Daily | “Updated daily” |
| Price Index | Weekly (CCC), optionally daily regional estimate | “Updated weekly” |
| Market Activity | Daily/weekly mixed | “Updated as new filings arrive” |
| Weekly Sales Tracker | Weekly | “Updated weekly” |
| News Feed | Weekly | “Updated weekly” |
| Premium Teasers | Weekly | “Preview refreshed weekly” |

Always show a top-level timestamp: `Data as of {Month Day, Year}`.

---

## 10) Implementation Priority Roadmap

## Phase 1 (P0) — Launch the authority page fast
1. Route + skeleton sections
2. Hero Snapshot with real counters
3. Price Index (category averages + WoW/MoM + simple region switch)
4. Weekly Sales tracker basic line chart
5. Newsletter signup embed
6. Core SEO tags + schema + FAQ

## Phase 2 (P1) — Add depth and conversion power
1. Market Activity full cards
2. Industry News + events feed
3. Premium blurred teaser cards
4. Methodology block + citation language
5. Analytics instrumentation (CTA + signup events)

## Phase 3 (P2) — Differentiate and scale backlinks
1. Advanced regional price map
2. Public “Data Notes / Methodology” subpage
3. Shareable chart links and downloadable press snapshots
4. Quarterly “State of MA Cannabis Market” roundup page for link campaigns

---

## 11) Conversion Strategy & CTA Placement

- **Primary CTA:** `Get Weekly Report` (newsletter) in hero + mid-page + footer.
- **Secondary CTA:** `Unlock Full Dashboard` at end of Price Index and inside teaser cards.
- **Intent-based copy:**
  - Price section CTA: “Need store-level pricing and alerts?”
  - Activity section CTA: “Track competitors before they open nearby.”

---

## 12) Risks & Mitigations

1. **Data schema drift in CCC files**
   - Mitigate with normalization layer and schema validation.
2. **Perceived paywall frustration**
   - Keep public value genuinely useful; lock depth, not basics.
3. **Stale page risk**
   - Visible freshness labels + fail-safe fallback text when a feed is delayed.
4. **Regional data quality inconsistencies**
   - Add methodology note and confidence flag where needed.

---

## 13) Final Recommendation

Build `/market` as a **public intelligence product**, not just a marketing page. Lead with the Price Index + Weekly Sales as the recurring backlink asset, then use locked premium visuals and newsletter embed to convert research traffic into owned audience and paid GLASS users.
