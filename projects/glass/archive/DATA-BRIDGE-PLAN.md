# DATA-BRIDGE-PLAN: Newsletter ↔ GLASS Integration

**Author:** Senior Data Engineer & Content Strategist  
**Date:** 2026-02-12  
**Status:** PROPOSED — awaiting review  

---

## 1. Executive Summary

GLASS and the Newsletter Pipeline are two halves of the same intelligence system. GLASS has **real-time dispensary pricing** (492 operators, 20K+ products, 24K+ weekly price observations across 5 categories). The Newsletter Pipeline has **regulatory data** (CCC weekly sales since 2020, 50K+ average-price records, 234 pending license applications, plant activity, demographics). Neither system has what the other has. Connecting them creates the **only vertically-integrated cannabis market intelligence platform in Massachusetts**.

This plan defines exactly what data moves where, in what schema, through what APIs, with what access controls.

---

## 2. Architecture: Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                                 │
├─────────────────────┬───────────────────────────────────────────────┤
│                     │                                               │
│  ┌──────────────┐   │   ┌──────────────────┐   ┌────────────────┐  │
│  │ Dutchie API  │   │   │ CCC Open Data    │   │ Brave Search   │  │
│  │ (235 stores) │   │   │ (14 endpoints)   │   │ (news/events)  │  │
│  └──────┬───────┘   │   └───────┬──────────┘   └──────┬─────────┘  │
│         │           │           │                      │            │
│  ┌──────┴───────┐   │   ┌───────┴──────────┐   ┌──────┴─────────┐  │
│  │ Weedmaps API │   │   │ Reddit API       │   │ Eventbrite     │  │
│  │ (263 stores) │   │   │ (social posts)   │   │ (future)       │  │
│  └──────┬───────┘   │   └───────┬──────────┘   └──────┬─────────┘  │
│         │           │           │                      │            │
├─────────┼───────────┼───────────┼──────────────────────┼────────────┤
│         │ SCRAPERS  │           │                      │            │
│         ▼           │           ▼                      ▼            │
│  ┌──────────────┐   │   ┌──────────────────────────────────────┐   │
│  │ GLASS        │   │   │ Newsletter Pipeline                  │   │
│  │ Scraper      │   │   │ (pipeline.py)                        │   │
│  │ (TypeScript) │   │   │ - ccc_ingest.py → CCC data           │   │
│  └──────┬───────┘   │   │ - news_scraper.py → News             │   │
│         │           │   │ - social_scraper.py → Reddit          │   │
│         │           │   │ - glass_data_processor.py → DB read   │   │
│         │           │   └──────────┬───────────────────────────┘   │
│         │           │              │                                │
├─────────┼───────────┼──────────────┼────────────────────────────────┤
│         │ DATABASE  │              │                                │
│         ▼           │              ▼                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              GLASS PostgreSQL (Railway)                      │   │
│  │                                                              │   │
│  │  EXISTING TABLES         │  NEW CCC TABLES (this plan)      │   │
│  │  ─────────────────       │  ──────────────────────────       │   │
│  │  operators (492)         │  ccc_weekly_sales (71 rows)      │   │
│  │  products (20K+)         │  ccc_avg_prices (50K+ rows)      │   │
│  │  prices (21K+)           │  ccc_pending_apps (234 rows)     │   │
│  │  threats                 │  ccc_plant_activity (50K+ rows)  │   │
│  │  recommendations         │  ccc_demographics (snapshot)     │   │
│  │  alerts                  │  ccc_ingest_runs (audit log)     │   │
│  │  sources / scrape_jobs   │                                  │   │
│  │  users / watchlists      │                                  │   │
│  │  margin_rules            │                                  │   │
│  └──────────────────────────┴──────────────────────────────────┘   │
│                              │                                      │
├──────────────────────────────┼──────────────────────────────────────┤
│  CONSUMERS                   │                                      │
│         ┌────────────────────┼────────────────────┐                 │
│         ▼                    ▼                    ▼                 │
│  ┌──────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │
│  │ GLASS        │  │ Newsletter      │  │ Public Intel Page   │   │
│  │ Dashboard    │  │ (Beehiiv)       │  │ (glass.roviq.com    │   │
│  │ (premium)    │  │ (weekly email)  │  │  /intel)            │   │
│  └──────────────┘  └─────────────────┘  └─────────────────────┘   │
│  Auth required      glass_data.json      Public + gated API       │
│  Full operator      pre-computed         Aggregates = free        │
│  level data         sections             Per-operator = premium   │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

| Flow | Direction | What Moves | Frequency |
|------|-----------|-----------|-----------|
| CCC → GLASS DB | Newsletter → Postgres | Weekly sales, avg prices, pending apps, plant activity, demographics | Weekly (pipeline run) |
| GLASS DB → Newsletter | Postgres → glass_data.json | Price Wire, Threat Radar, Brand Movers, Market Stats | Weekly (pipeline run) |
| GLASS DB → Public Page | Postgres → REST API | Aggregated CCC + GLASS data (free tier) | On-demand (API) |
| GLASS DB → Dashboard | Postgres → REST API | Full operator-level data (premium) | On-demand (API) |

---

## 3. Schema Additions: CCC Tables in GLASS Postgres

### 3.1 `ccc_weekly_sales`

Official CCC statewide weekly sales data. Monthly averages from 2020-present.

```sql
-- Migration: 0001_ccc_tables.sql

CREATE TABLE glass.ccc_weekly_sales (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  year_month      varchar(7) NOT NULL,           -- '2020-01', '2025-12'
  avg_retail_price_per_gm  numeric(6, 2) NOT NULL,  -- 14.68
  unit            varchar(10) NOT NULL DEFAULT 'Grams',
  source_endpoint varchar(20) NOT NULL DEFAULT 'rqtv-uenj',
  ingested_at     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ccc_weekly_sales_month_unique UNIQUE (year_month)
);

CREATE INDEX idx_ccc_weekly_sales_month ON glass.ccc_weekly_sales (year_month);
```

**Source:** `data/ccc/weekly_sales.json` → 71 rows  
**Update frequency:** Weekly (CCC updates monthly; we check weekly)  
**Value:** Official statewide price trend. Combined with GLASS scraped prices, gives both the "official" and "street" price — the delta is the story.

### 3.2 `ccc_avg_prices`

CCC per-category, per-day average prices by industry (Medical vs Adult-use). Massive historical dataset.

```sql
CREATE TABLE glass.ccc_avg_prices (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  sale_date           date NOT NULL,
  industry            varchar(20) NOT NULL,        -- 'Medical', 'Adult-use'
  product_category    varchar(50) NOT NULL,         -- 'Buds', 'Concentrate (Each)', 'Vape Product', etc.
  unit_of_measure     varchar(10) NOT NULL,         -- 'g', 'ea'
  quantity            numeric(12, 2) NOT NULL,
  units               integer NOT NULL,
  weight_based_total  numeric(14, 2) NOT NULL DEFAULT 0,
  dollar_weight_total numeric(14, 2) NOT NULL DEFAULT 0,
  count_based_total   numeric(14, 2) NOT NULL DEFAULT 0,
  dollar_count_total  numeric(14, 2) NOT NULL DEFAULT 0,
  total_dollars       numeric(14, 2) NOT NULL,
  source_endpoint     varchar(20) NOT NULL DEFAULT 'g5mj-5pg3',
  ingested_at         timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ccc_avg_prices_unique UNIQUE (sale_date, industry, product_category)
);

CREATE INDEX idx_ccc_avg_prices_date ON glass.ccc_avg_prices (sale_date);
CREATE INDEX idx_ccc_avg_prices_category ON glass.ccc_avg_prices (product_category);
CREATE INDEX idx_ccc_avg_prices_industry ON glass.ccc_avg_prices (industry);
CREATE INDEX idx_ccc_avg_prices_date_cat ON glass.ccc_avg_prices (sale_date, product_category);
```

**Source:** `data/ccc/average_price.json` → 50K rows (paginated; CCC caps at 50K)  
**Update frequency:** Weekly  
**Value:** Historical price context. "CCC says average Buds were $X/g last month. GLASS sees actual shelf prices at $Y/g. The gap is Z%." This is the single most powerful cross-reference in the system.

### 3.3 `ccc_pending_applications`

Active license applications pending before the CCC. Critical for threat detection.

```sql
CREATE TABLE glass.ccc_pending_applications (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  application_number    varchar(20) NOT NULL,
  license_number        varchar(20),
  business_name         varchar(255) NOT NULL,
  license_type          varchar(100) NOT NULL,       -- 'Marijuana Delivery Operator', 'Marijuana Retailer', etc.
  application_status    varchar(30) NOT NULL,         -- 'PENDING'
  review_type           varchar(50),                  -- 'Expedited', 'General Applicant'
  review_priority       varchar(100),                 -- 'Social Equity Participant', 'General Applicant'
  dbe_status            varchar(50),                  -- 'Not a DBE', 'Minority-Owned', etc.
  establishment_city    varchar(100),
  establishment_state   varchar(2) DEFAULT 'MA',
  establishment_zip     varchar(10),
  county                varchar(50),
  lat                   numeric(10, 8),
  lon                   numeric(11, 8),
  submitted_date        date,
  approved_date         date,
  commence_ops_date     date,
  fee_waiver_request    boolean DEFAULT false,
  cultivation_tier      varchar(50),
  cultivation_env       varchar(50),
  source_endpoint       varchar(30) NOT NULL DEFAULT 'l_applications_pending',
  ingested_at           timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ccc_pending_apps_appnum_unique UNIQUE (application_number)
);

CREATE INDEX idx_ccc_pending_apps_city ON glass.ccc_pending_applications (establishment_city);
CREATE INDEX idx_ccc_pending_apps_type ON glass.ccc_pending_applications (license_type);
CREATE INDEX idx_ccc_pending_apps_status ON glass.ccc_pending_applications (application_status);
CREATE INDEX idx_ccc_pending_apps_location ON glass.ccc_pending_applications (lat, lon);
CREATE INDEX idx_ccc_pending_apps_county ON glass.ccc_pending_applications (county);
CREATE INDEX idx_ccc_pending_apps_submitted ON glass.ccc_pending_applications (submitted_date);
```

**Source:** `data/ccc/pending_applications.json` → 234 rows  
**Update frequency:** Weekly  
**Value:** This IS the License Pipeline visualization data source. Currently `viz/license-pipeline` fakes it from the `threats` table. This table gives real data: 234 actual pending applications with geo-coordinates, dates, license types, and DBE status. Also powers Threat Radar: "3 new delivery operators applied in your county this week."

### 3.4 `ccc_plant_activity`

CCC sales data by delivery type, product category, and date. Captures delivery vs storefront vs microbusiness splits.

```sql
CREATE TABLE glass.ccc_plant_activity (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  sale_date           date NOT NULL,
  data_type           varchar(50) NOT NULL,         -- 'Delivery and MBs'
  delivery_type       varchar(50) NOT NULL,         -- 'Delivery Operators', 'Delivery Couriers', 'Microbusiness'
  product_category    varchar(50) NOT NULL,         -- 'Infused Beverage', 'Vape Product', 'Buds', etc.
  unit_of_measure     varchar(10) NOT NULL,
  quantity            numeric(12, 2) NOT NULL,
  units               integer NOT NULL,
  count_based_total   numeric(14, 2) NOT NULL DEFAULT 0,
  dollar_count_total  numeric(14, 2) NOT NULL DEFAULT 0,
  weight_based_total  numeric(14, 2) NOT NULL DEFAULT 0,
  dollar_weight_total numeric(14, 2) NOT NULL DEFAULT 0,
  total_dollars       numeric(14, 2) NOT NULL,
  source_endpoint     varchar(20) NOT NULL DEFAULT 'fren-z7jq',
  ingested_at         timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ccc_plant_activity_unique UNIQUE (sale_date, delivery_type, product_category)
);

CREATE INDEX idx_ccc_plant_activity_date ON glass.ccc_plant_activity (sale_date);
CREATE INDEX idx_ccc_plant_activity_delivery ON glass.ccc_plant_activity (delivery_type);
CREATE INDEX idx_ccc_plant_activity_category ON glass.ccc_plant_activity (product_category);
```

**Source:** `data/ccc/plant_activity.json` → 50K rows  
**Update frequency:** Weekly  
**Value:** Delivery vs storefront market share trends. "Delivery operators now account for X% of vape product sales, up from Y% last quarter." Critical for operators deciding whether to add delivery.

### 3.5 `ccc_demographics`

Snapshot tables for industry workforce demographics, DBE breakdown, and testing/race data.

```sql
CREATE TABLE glass.ccc_demographics (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_key     varchar(50) NOT NULL,          -- 'facility_sales', 'total_dbe', 'testing_results'
  category        varchar(100) NOT NULL,          -- 'Male', 'Female', 'Minority-Owned Business', etc.
  total           integer NOT NULL,
  pct_total       numeric(5, 3) NOT NULL,
  sum_of_all      integer,                        -- only in facility_sales
  source_endpoint varchar(20),
  ingested_at     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ccc_demographics_unique UNIQUE (dataset_key, category)
);

CREATE INDEX idx_ccc_demographics_dataset ON glass.ccc_demographics (dataset_key);
```

**Source:** `data/ccc/facility_sales.json` (4 rows), `total_dbe.json` (6 rows), `testing_results.json` (79 rows)  
**Update frequency:** Weekly  
**Value:** "36.3% of MA cannabis workers are female." "35.6% of licensees are minority-owned." Powers newsletter demographic signals and public intel page diversity metrics.

### 3.6 `ccc_ingest_runs`

Audit log tracking each CCC data ingestion into the GLASS database.

```sql
CREATE TABLE glass.ccc_ingest_runs (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at      timestamptz NOT NULL DEFAULT now(),
  completed_at    timestamptz,
  status          varchar(20) NOT NULL DEFAULT 'running',  -- 'running', 'success', 'partial', 'failed'
  datasets_attempted  integer DEFAULT 0,
  datasets_succeeded  integer DEFAULT 0,
  datasets_failed     integer DEFAULT 0,
  rows_inserted   integer DEFAULT 0,
  rows_updated    integer DEFAULT 0,
  error_log       jsonb DEFAULT '[]'::jsonb,
  source_json_dir text,                          -- path to JSON source files
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_ccc_ingest_runs_status ON glass.ccc_ingest_runs (status);
CREATE INDEX idx_ccc_ingest_runs_started ON glass.ccc_ingest_runs (started_at);
```

**Value:** Operational visibility. "Last CCC ingest: 2026-02-08, 14 datasets, 100K+ rows. Next expected: 2026-02-15."

---

## 4. What Data Powers What

### 4.1 Newsletter Sections → Data Sources

| Newsletter Section | Primary Source | CCC Table? | GLASS Table? | Auto-gen? |
|---|---|---|---|---|
| **Price Wire** | GLASS `prices` + `products` | `ccc_avg_prices` (for official context) | ✅ `prices`, `products` | ✅ Fully |
| **Threat Radar** | GLASS `threats` + CCC pending apps | ✅ `ccc_pending_applications` | ✅ `threats`, `operators` | 🟡 Partial |
| **Brand Movers** | GLASS `products` + `prices` | — | ✅ `products`, `prices` | ✅ Fully |
| **CCC Watchlist** | CCC ingest data | ✅ `ccc_pending_applications`, `ccc_demographics` | — | 🟡 Partial |
| **THE NUMBER** | Rotating metric | ✅ `ccc_weekly_sales` | ✅ `operators`, `products` | ✅ Fully |
| **Data Spotlight** | Rotating deep-dive | ✅ `ccc_avg_prices`, `ccc_plant_activity` | ✅ All tables | 🟡 Needs LLM |
| **Top Story** | Brave Search + LLM | — | — | 🟡 Needs LLM |
| **Quick Hits** | Brave Search | — | — | 🟡 Needs LLM |
| **Market Pulse** | Multiple | ✅ `ccc_weekly_sales` | ✅ `prices` | ✅ Fully |
| **Margin Tip** | Static library | — | — | ✅ Template |
| **Compliance** | Static library | — | — | ✅ Template |

### 4.2 New Cross-Reference Queries (the real value)

These queries become possible **only** when CCC data and GLASS data live in the same database:

```sql
-- 1. Official vs Street Price Gap
-- "CCC says avg retail is $X.XX/g. GLASS sees dispensaries actually pricing at $Y.YY/g."
SELECT 
  cws.year_month,
  cws.avg_retail_price_per_gm AS ccc_official_price,
  ROUND(AVG(pr.price / NULLIF(p.weight_grams, 0))::numeric, 2) AS glass_actual_per_gm,
  ROUND(((AVG(pr.price / NULLIF(p.weight_grams, 0)) - cws.avg_retail_price_per_gm) 
    / cws.avg_retail_price_per_gm * 100)::numeric, 1) AS pct_gap
FROM ccc_weekly_sales cws
JOIN LATERAL (
  SELECT pr.price, p.weight_grams
  FROM prices pr
  JOIN products p ON pr.product_id = p.id
  WHERE p.category = 'flower'
    AND p.weight_grams > 0
    AND pr.scraped_at >= (cws.year_month || '-01')::date
    AND pr.scraped_at < (cws.year_month || '-01')::date + INTERVAL '1 month'
) sub ON true
GROUP BY cws.year_month, cws.avg_retail_price_per_gm
ORDER BY cws.year_month DESC;

-- 2. Pending Applications Near Existing Operators (Threat Detection)
-- "3 new retailer applications within 5 miles of your location"
SELECT 
  cpa.business_name,
  cpa.license_type,
  cpa.establishment_city,
  cpa.submitted_date,
  o.name AS nearby_operator,
  o.city AS operator_city,
  ROUND((3959 * acos(
    cos(radians(o.lat::float8)) * cos(radians(cpa.lat::float8)) *
    cos(radians(cpa.lon::float8) - radians(o.lon::float8)) +
    sin(radians(o.lat::float8)) * sin(radians(cpa.lat::float8))
  ))::numeric, 2) AS distance_miles
FROM ccc_pending_applications cpa
JOIN operators o ON o.lat IS NOT NULL 
  AND (3959 * acos(
    cos(radians(o.lat::float8)) * cos(radians(cpa.lat::float8)) *
    cos(radians(cpa.lon::float8) - radians(o.lon::float8)) +
    sin(radians(o.lat::float8)) * sin(radians(cpa.lat::float8))
  )) <= 10
WHERE cpa.submitted_date > CURRENT_DATE - INTERVAL '30 days'
ORDER BY distance_miles ASC;

-- 3. Delivery Market Share Trend (storefront operators: should you add delivery?)
SELECT 
  DATE_TRUNC('month', pa.sale_date) AS month,
  pa.delivery_type,
  SUM(pa.total_dollars) AS total_revenue,
  ROUND(SUM(pa.total_dollars) / SUM(SUM(pa.total_dollars)) 
    OVER (PARTITION BY DATE_TRUNC('month', pa.sale_date)) * 100, 1) AS market_share_pct
FROM ccc_plant_activity pa
GROUP BY DATE_TRUNC('month', pa.sale_date), pa.delivery_type
ORDER BY month DESC, market_share_pct DESC;

-- 4. Category Price Divergence: CCC official vs GLASS real-time
SELECT 
  cap.product_category AS ccc_category,
  ROUND(AVG(cap.total_dollars / NULLIF(cap.quantity, 0))::numeric, 2) AS ccc_avg_price_per_unit,
  p.category AS glass_category,
  ROUND(AVG(pr.price)::numeric, 2) AS glass_avg_price,
  COUNT(DISTINCT pr.operator_id) AS glass_operator_count
FROM ccc_avg_prices cap
JOIN LATERAL (
  SELECT * FROM (VALUES 
    ('Buds', 'flower'),
    ('Raw Pre-Rolls', 'preroll'),
    ('Vape Product', 'vape'),
    ('Infused (edible)', 'edible'),
    ('Concentrate (Each)', 'concentrate')
  ) AS m(ccc_cat, glass_cat)
  WHERE m.ccc_cat = cap.product_category
) mapping ON true
JOIN products p ON p.category = mapping.glass_cat
JOIN prices pr ON pr.product_id = p.id
  AND pr.scraped_at > NOW() - INTERVAL '7 days'
WHERE cap.sale_date > CURRENT_DATE - INTERVAL '30 days'
GROUP BY cap.product_category, p.category;
```

---

## 5. Public vs Premium Data Access

### 5.1 Access Tiers

| Data | Public Intel Page | Newsletter (Free) | GLASS Dashboard (Premium) |
|---|---|---|---|
| **CCC Weekly Sales** (official statewide prices) | ✅ Full history | ✅ Latest + trend | ✅ Full + analysis |
| **CCC Avg Prices** (category breakdowns) | ✅ Aggregated monthly | ✅ Top-line in Price Wire | ✅ Full daily granularity |
| **CCC Pending Applications** (license pipeline) | ✅ Count + types only | ✅ Count + city breakdown | ✅ Full table w/ geocoding |
| **CCC Plant Activity** (delivery/storefront split) | ✅ Monthly totals | ✅ Trend summary | ✅ Full daily + by category |
| **CCC Demographics** (workforce, DBE) | ✅ Full (public data) | ✅ Selected highlights | ✅ Full + trends |
| **GLASS Price Averages** (category-level) | ✅ Category averages | ✅ Full Price Wire | ✅ Full + percentiles |
| **GLASS Price Movers** (specific products) | ❌ Locked (teaser: "3 products dropped >50%") | ✅ Top 3 drops/increases | ✅ Full list, all operators |
| **GLASS Brand Rankings** (shelf presence) | ✅ Top 5 brands | ✅ Top 10 + movers | ✅ Full brand analytics |
| **GLASS Operator Count** (market size) | ✅ Total count | ✅ Total + regional | ✅ Per-operator details |
| **GLASS New Operators** (threat detection) | ❌ Locked (teaser: "X new stores this week") | ✅ Names + cities | ✅ Full geo + proximity |
| **GLASS Per-Operator Prices** | ❌ Locked entirely | ❌ Locked | ✅ Full access |
| **GLASS Recommendations** | ❌ Locked | ❌ Locked | ✅ Personalized |

### 5.2 Rationale

- **CCC data is public** — the Massachusetts Cannabis Control Commission publishes all of it. No reason to gate it. Showing it freely builds trust and SEO.
- **GLASS aggregates are free teasers** — category averages, brand rankings, and market size numbers are interesting but not actionable alone. They pull people in.
- **GLASS specifics are premium** — which exact product at which exact store dropped 50% in price? That's the margin-protecting intelligence operators will pay for.
- **Newsletter sits in the middle** — more specific than the public page (shows actual product names and movers), but less than the dashboard (doesn't show all operators, no personalized recs).

---

## 6. API Endpoints for Public Intelligence Page

These endpoints require NO authentication (public tier) or optional auth (premium upgrade).

### 6.1 New Public Routes (no auth)

```typescript
// File: src/routes/public-intel.ts

// GET /public/market-summary
// Returns: statewide market stats combining CCC + GLASS
{
  "ccc_official": {
    "latest_month": "2025-12",
    "avg_retail_price_per_gm": 8.19,
    "price_trend_6m": [/* 6 data points */],
    "trend_direction": "declining"
  },
  "glass_realtime": {
    "total_operators": 492,
    "active_operators_7d": 245,
    "total_products": 20000,
    "price_observations_7d": 24485,
    "category_averages": [
      { "category": "flower", "avg_price": 38.95, "median_price": 30.00 },
      // ... other categories
    ]
  },
  "pending_applications": {
    "total_pending": 234,
    "by_type": { "Retailer": 45, "Delivery": 38, "Cultivator": 22, /* ... */ },
    "submitted_last_30d": 12
  },
  "demographics": {
    "total_workforce": 20694,
    "female_pct": 36.3,
    "dbe_total": 475,
    "minority_owned_pct": 35.6
  },
  "updated_at": "2026-02-12T07:33:00Z"
}

// GET /public/price-trends
// Returns: historical price trends (CCC + GLASS combined)
// Query params: ?months=12&category=flower
{
  "ccc_monthly": [/* official CCC avg retail prices by month */],
  "glass_weekly": [/* GLASS observed category averages by week */],
  "categories": ["flower", "preroll", "vape", "edible", "concentrate"]
}

// GET /public/license-pipeline
// Returns: CCC pending applications aggregated (no individual details)
{
  "pipeline_stages": [
    { "stage": "Pending Applications", "count": 234 },
    { "stage": "Social Equity / Expedited", "count": 87 },
    { "stage": "General Applicant", "count": 147 },
    // ...
  ],
  "by_type": [
    { "license_type": "Marijuana Retailer", "count": 45 },
    { "license_type": "Marijuana Delivery Operator", "count": 38 },
    // ...
  ],
  "by_county": [
    { "county": "Suffolk County", "count": 28 },
    { "county": "Worcester County", "count": 22 },
    // ...
  ],
  "dbe_breakdown": [
    { "category": "Minority-Owned Business", "count": 169, "pct": 0.356 },
    // ...
  ]
}

// GET /public/brand-rankings
// Returns: top brands by shelf presence (public tier = top 5)
{
  "top_brands": [
    { "brand": "Brand A", "store_count": 45, "avg_price": 35.50 },
    // ... (5 brands for public, 15 for auth'd users)
  ],
  "total_brands_tracked": 850,
  "premium_locked": true,  // signals "sign up for full list"
  "upgrade_cta": "See all 850 brands →"
}

// GET /public/delivery-trends
// Returns: delivery vs storefront market share from CCC plant activity
{
  "monthly_share": [
    { "month": "2025-12", "delivery_pct": 8.2, "storefront_pct": 91.8 },
    // ...
  ],
  "delivery_categories": [
    { "category": "Vape Product", "delivery_revenue": 123456 },
    // ...
  ]
}
```

### 6.2 Gated Endpoints (auth required, premium tier)

```typescript
// These already exist but should be extended:

// GET /prices/movers → already exists (auth required) — this is the premium version of Price Wire
// GET /viz/proximity → already exists (auth required) — premium threat intelligence
// GET /viz/operator-compare → already exists — premium competitive analysis

// NEW: GET /intel/application-threats (auth required)
// Returns: pending applications near the operator's location
// This is the premium version of license-pipeline — shows actual business names,
// addresses, proximity calculations specific to the logged-in operator
```

---

## 7. Newsletter Pipeline Updates

### 7.1 Update `ccc_ingest.py` to Write to GLASS DB

Currently `ccc_ingest.py` writes JSON files to `data/ccc/`. It should **also** write to the GLASS database.

```python
# Add to scrapers/ccc_ingest.py after JSON file generation:

def write_to_glass_db(data_dir: Path) -> dict:
    """Write CCC data from JSON files into GLASS PostgreSQL tables."""
    import psycopg2
    from psycopg2.extras import execute_values
    
    conn = psycopg2.connect(GLASS_DATABASE_URL)
    stats = {"inserted": 0, "updated": 0, "errors": []}
    
    try:
        # 1. Weekly sales
        weekly = json.loads((data_dir / "weekly_sales.json").read_text())
        if weekly.get("status") == "success":
            _upsert_weekly_sales(conn, weekly["rows"], stats)
        
        # 2. Average prices
        avg_prices = json.loads((data_dir / "average_price.json").read_text())
        if avg_prices.get("status") == "success":
            _upsert_avg_prices(conn, avg_prices["rows"], stats)
        
        # 3. Pending applications
        pending = json.loads((data_dir / "pending_applications.json").read_text())
        if pending.get("status") == "success":
            _upsert_pending_apps(conn, pending["rows"], stats)
        
        # 4. Plant activity
        plant = json.loads((data_dir / "plant_activity.json").read_text())
        if plant.get("status") == "success":
            _upsert_plant_activity(conn, plant["rows"], stats)
        
        # 5. Demographics (facility_sales + total_dbe + testing_results)
        for demo_file in ["facility_sales.json", "total_dbe.json", "testing_results.json"]:
            demo = json.loads((data_dir / demo_file).read_text())
            if demo.get("status") == "success":
                _upsert_demographics(conn, demo["dataset_key"], demo["rows"], stats)
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        stats["errors"].append(str(e))
    finally:
        conn.close()
    
    return stats
```

### 7.2 Update `glass_data_processor.py` to Include CCC Cross-References

The existing `glass_data_processor.py` already connects to the DB and outputs `glass_data.json`. Extend it to include CCC cross-reference data:

```python
# Add to glass_data_processor.py:

def fetch_ccc_context(conn) -> Dict[str, Any]:
    """Fetch CCC context data to enrich newsletter sections."""
    cur = conn.cursor()
    result = {}
    
    try:
        # Latest official price
        cur.execute("""
            SELECT year_month, avg_retail_price_per_gm 
            FROM ccc_weekly_sales 
            ORDER BY year_month DESC LIMIT 1
        """)
        row = cur.fetchone()
        if row:
            result["official_price"] = {
                "month": row[0],
                "price_per_gm": float(row[1])
            }
        
        # Pending applications summary
        cur.execute("""
            SELECT license_type, COUNT(*) 
            FROM ccc_pending_applications 
            GROUP BY license_type 
            ORDER BY COUNT(*) DESC
        """)
        result["pending_apps_by_type"] = [
            {"type": r[0], "count": r[1]} for r in cur.fetchall()
        ]
        
        # New applications in last 30 days
        cur.execute("""
            SELECT COUNT(*) 
            FROM ccc_pending_applications 
            WHERE submitted_date > CURRENT_DATE - INTERVAL '30 days'
        """)
        result["new_apps_30d"] = cur.fetchone()[0]
        
        # Delivery market share trend
        cur.execute("""
            SELECT 
              DATE_TRUNC('month', sale_date)::date AS month,
              delivery_type,
              SUM(total_dollars) AS revenue
            FROM ccc_plant_activity
            WHERE sale_date > CURRENT_DATE - INTERVAL '6 months'
            GROUP BY DATE_TRUNC('month', sale_date), delivery_type
            ORDER BY month DESC
        """)
        result["delivery_trends"] = [
            {"month": str(r[0]), "type": r[1], "revenue": float(r[2])} 
            for r in cur.fetchall()
        ]
        
    except Exception as exc:
        print(f"WARNING: CCC context query failed: {exc}", file=sys.stderr)
    finally:
        cur.close()
    
    return result
```

### 7.3 Updated Pipeline Stage Order

```python
# pipeline.py STAGES update:
STAGES = [
    # --- Data Collection ---
    ("news",        "scrapers/news_scraper.py",          ["--days", "7"]),
    ("events",      "scrapers/events_scraper.py",        ["--days", "30"]),
    ("social",      "scrapers/social_scraper.py",        ["--limit", "20"]),
    ("tools",       "scrapers/tools_scraper.py",         []),
    ("ccc_ingest",  "scrapers/ccc_ingest.py",            []),           # Scrapes CCC + writes to GLASS DB
    ("glass",       "scrapers/glass_data_processor.py",  []),           # Reads GLASS DB (incl CCC tables)
    ("market",      "scrapers/market_data_processor.py", []),
    # --- Quality Gates ---
    ("validate",    "content_validator.py",              []),
    ("compose",     "composer.py",                       []),
    ("quality",     "quality_checker.py",                []),
]

# Re-enable validation gate:
GATE_STAGES = {"validate"}
```

**Key change:** `ccc_ingest` now writes to the GLASS DB **before** `glass_data_processor` reads from it. This means `glass_data_processor.py` sees the freshest CCC data alongside the scraped price data in a single query context.

### 7.4 Updated Data Contract

```python
# data_contract.py additions:

GLASS_SCHEMA = {
    "price_wire": {
        "required_keys": ["category_averages", "biggest_drops", "biggest_increases", "total_observations"],
        "description": "Price data by category with biggest movers",
    },
    "threat_radar": {
        "required_keys": ["new_operators", "new_operator_count", "active_threats", "active_threat_count"],
        "description": "New competitor detection and active threat intelligence",
    },
    "brand_movers": {
        "required_keys": ["top_brands", "total_brands_tracked"],
        "description": "Top brands by shelf presence across MA dispensaries",
    },
    "market_stats": {
        "required_keys": ["total_operators", "total_products", "total_price_observations"],
        "description": "Overall market statistics from GLASS database",
    },
    # NEW: CCC context enrichment
    "ccc_context": {
        "required_keys": ["official_price", "pending_apps_by_type"],
        "description": "CCC regulatory data cross-referenced with GLASS market data",
    },
}
```

---

## 8. Migration Plan: Import Existing CCC JSON into GLASS DB

### Phase 1: Schema Creation (Day 1)

```bash
# Run migration SQL against Railway Postgres
psql $GLASS_DATABASE_URL -f migrations/0001_ccc_tables.sql
```

### Phase 2: Backfill from Existing JSON Files (Day 1)

Create `scripts/backfill_ccc.py`:

```python
#!/usr/bin/env python3
"""One-time backfill: Import existing CCC JSON data into GLASS PostgreSQL."""

import json
import psycopg2
from pathlib import Path
from datetime import datetime

CCC_DIR = Path("/data/workspace/projects/internal/newsletter/data/ccc")
DB_URL = "postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway"

def backfill():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Set schema
    cur.execute("SET search_path TO glass, public")
    
    # 1. Weekly sales (71 rows)
    ws = json.loads((CCC_DIR / "weekly_sales.json").read_text())
    for row in ws.get("rows", []):
        cur.execute("""
            INSERT INTO ccc_weekly_sales (year_month, avg_retail_price_per_gm, unit)
            VALUES (%s, %s, %s)
            ON CONFLICT (year_month) DO UPDATE SET avg_retail_price_per_gm = EXCLUDED.avg_retail_price_per_gm
        """, (row["YearMonth"], row["AverageRetailPriceperGm"], row.get("Unit", "Grams")))
    print(f"  Weekly sales: {len(ws.get('rows', []))} rows")
    
    # 2. Average prices (50K rows — batch insert)
    ap = json.loads((CCC_DIR / "average_price.json").read_text())
    batch = []
    for row in ap.get("rows", []):
        try:
            sale_date = datetime.strptime(row["SaleDate"], "%m/%d/%Y").date()
        except (ValueError, KeyError):
            continue
        batch.append((
            sale_date, row.get("Industry", "Unknown"), row.get("ProductCategoryName", "Unknown"),
            row.get("UnitOfMeasureName", "ea"), float(row.get("Quantity", 0)),
            int(float(row.get("Units", 0))), float(row.get("WeightBasedTotal", 0)),
            float(row.get("DollarWeightBasedTotal", 0)), float(row.get("CountBasedTotal", 0)),
            float(row.get("DollarCountBasedTotal", 0)), float(row.get("TOTAL_$", 0))
        ))
    # Batch insert with ON CONFLICT
    from psycopg2.extras import execute_values
    execute_values(cur, """
        INSERT INTO ccc_avg_prices 
        (sale_date, industry, product_category, unit_of_measure, quantity, units,
         weight_based_total, dollar_weight_total, count_based_total, dollar_count_total, total_dollars)
        VALUES %s
        ON CONFLICT (sale_date, industry, product_category) DO UPDATE 
        SET total_dollars = EXCLUDED.total_dollars,
            quantity = EXCLUDED.quantity
    """, batch, page_size=1000)
    print(f"  Average prices: {len(batch)} rows")
    
    # 3. Pending applications (234 rows)
    pa = json.loads((CCC_DIR / "pending_applications.json").read_text())
    for row in pa.get("rows", []):
        submitted = None
        if row.get("SUBMITTED_DATE"):
            try:
                submitted = datetime.strptime(row["SUBMITTED_DATE"], "%m/%d/%Y").date()
            except ValueError:
                pass
        cur.execute("""
            INSERT INTO ccc_pending_applications 
            (application_number, license_number, business_name, license_type,
             application_status, review_type, review_priority, dbe_status,
             establishment_city, establishment_state, establishment_zip, county,
             lat, lon, submitted_date, fee_waiver_request)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (application_number) DO UPDATE SET
              application_status = EXCLUDED.application_status,
              updated_at = now()
        """, (
            row.get("APPLICATION_NUMBER"), row.get("LICENSE_NUMBER"),
            row.get("BUSINESS_NAME", "Unknown"), row.get("LICENSE_TYPE", "Unknown"),
            row.get("APPLICATION_STATUS", "PENDING"), row.get("REVIEW_TYPE"),
            row.get("REVIEW_PRIORITY"), row.get("DBE"),
            row.get("ESTABLISHMENT_CITY"), row.get("ESTABLISHMENT_STATE", "MA"),
            row.get("ESTABLISHMENT_ZIP_CODE"), row.get("COUNTY"),
            row.get("latitude"), row.get("longitude"),
            submitted, row.get("FEE_WAIVER_REQUEST", "").lower() == "yes"
        ))
    print(f"  Pending applications: {len(pa.get('rows', []))} rows")
    
    # 4. Plant activity (50K rows — batch)
    plant = json.loads((CCC_DIR / "plant_activity.json").read_text())
    batch2 = []
    for row in plant.get("rows", []):
        try:
            sale_date = datetime.strptime(row["SaleDate"], "%m/%d/%Y").date()
        except (ValueError, KeyError):
            continue
        batch2.append((
            sale_date, row.get("DataType", ""), row.get("DeliveryType", ""),
            row.get("ProductCategoryName", ""), row.get("UnitOfMeasureName", ""),
            float(row.get("Quantity", 0)), int(float(row.get("Units", 0))),
            float(row.get("CountBasedTotal", 0)), float(row.get("DollarCountBasedTotal", 0)),
            float(row.get("WeightBasedTotal", 0)), float(row.get("DollarWeightBasedTotal", 0)),
            float(row.get("TOTAL_$", 0))
        ))
    execute_values(cur, """
        INSERT INTO ccc_plant_activity
        (sale_date, data_type, delivery_type, product_category, unit_of_measure,
         quantity, units, count_based_total, dollar_count_total,
         weight_based_total, dollar_weight_total, total_dollars)
        VALUES %s
        ON CONFLICT (sale_date, delivery_type, product_category) DO UPDATE
        SET total_dollars = EXCLUDED.total_dollars
    """, batch2, page_size=1000)
    print(f"  Plant activity: {len(batch2)} rows")
    
    # 5. Demographics (3 files, ~89 rows total)
    for fname, dataset_key in [
        ("facility_sales.json", "facility_sales"),
        ("total_dbe.json", "total_dbe"),
        ("testing_results.json", "testing_results"),
    ]:
        demo = json.loads((CCC_DIR / fname).read_text())
        if demo.get("status") != "success":
            continue
        for row in demo.get("rows", []):
            category = row.get("GENDER") or row.get("DBE_CATEGORY") or row.get("RACE_ETHNICITY") or "Unknown"
            cur.execute("""
                INSERT INTO ccc_demographics (dataset_key, category, total, pct_total, sum_of_all, source_endpoint)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (dataset_key, category) DO UPDATE SET
                  total = EXCLUDED.total, pct_total = EXCLUDED.pct_total
            """, (
                dataset_key, category,
                int(row.get("TOTAL", 0)), float(row.get("%_TOTAL", 0)),
                int(row.get("SUM OF ALL", 0)) if row.get("SUM OF ALL") else None,
                demo.get("endpoint")
            ))
        print(f"  Demographics ({dataset_key}): {len(demo.get('rows', []))} rows")
    
    conn.commit()
    print("✅ Backfill complete!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    backfill()
```

### Phase 3: Verify Backfill (Day 1)

```sql
-- Verification queries
SELECT 'ccc_weekly_sales' AS table_name, COUNT(*) FROM glass.ccc_weekly_sales
UNION ALL SELECT 'ccc_avg_prices', COUNT(*) FROM glass.ccc_avg_prices
UNION ALL SELECT 'ccc_pending_applications', COUNT(*) FROM glass.ccc_pending_applications
UNION ALL SELECT 'ccc_plant_activity', COUNT(*) FROM glass.ccc_plant_activity
UNION ALL SELECT 'ccc_demographics', COUNT(*) FROM glass.ccc_demographics;
```

### Phase 4: Update ccc_ingest.py (Day 2)

Add DB write step to existing `ccc_ingest.py` so future runs maintain the tables.

### Phase 5: Update glass_data_processor.py (Day 2)

Add `fetch_ccc_context()` to the pipeline so newsletter sections can reference CCC data.

### Phase 6: Add Public API Routes (Day 3)

Create `src/routes/public-intel.ts` with the unauthenticated endpoints.

### Phase 7: Update Newsletter Composer (Day 3-4)

Update `composer.py` to consume the enriched `glass_data.json` (which now includes `ccc_context`) and render the CCC Watchlist section and CCC cross-references in Price Wire.

---

## 9. What This Enables: The Complete Picture

### Before (Current State — Two Isolated Systems)

```
Newsletter Pipeline ──→ JSON files ──→ Newsletter draft ──→ Manual Beehiiv
     (CCC data only)       (flat files)    (no price intel)

GLASS Scraper ──→ Railway Postgres ──→ Dashboard ──→ Premium users only
     (dispensary prices)   (no CCC data)  (no public page)
```

**Problems:**
- Newsletter has no pricing data (promised on LP, never delivered)
- GLASS has no regulatory context (CCC sales trends, license pipeline)
- Public page doesn't exist (no free-tier content to attract users)
- No funnel: newsletter doesn't drive GLASS signups
- License Pipeline viz is faked from threats table

### After (Unified Data Bridge)

```
                    ┌─────────────────────────────────────┐
                    │        GLASS PostgreSQL              │
                    │  (single source of truth)            │
                    │                                     │
                    │  Scraped Data + CCC Regulatory Data  │
                    │  Cross-referenced, queryable         │
                    └──┬──────────┬────────────┬──────────┘
                       │          │            │
              ┌────────┘          │            └────────┐
              ▼                   ▼                     ▼
    ┌─────────────────┐  ┌───────────────┐   ┌──────────────────┐
    │ Newsletter       │  │ Public Intel  │   │ GLASS Dashboard  │
    │ (weekly email)   │  │ Page (free)   │   │ (premium)        │
    │                  │  │               │   │                  │
    │ Price Wire ✅     │  │ Market stats  │   │ Full per-operator│
    │ Threat Radar ✅   │  │ CCC trends    │   │ Personalized     │
    │ Brand Movers ✅   │  │ License count │   │ Margin engine    │
    │ CCC Watchlist ✅  │  │ Brand top-5   │   │ Proximity alerts │
    │ Official vs      │  │ Demographics  │   │ All CCC data     │
    │  Street Price ✅  │  │               │   │                  │
    └────────┬─────────┘  └───────┬───────┘   └────────┬─────────┘
             │                    │                     │
             └────────────────────┼─────────────────────┘
                                  │
                         THE FUNNEL:
                    Newsletter (free, weekly)
                         ↓ CTA: "See full data"
                    Public Intel Page (free, always-on)
                         ↓ CTA: "Unlock your store's data"
                    GLASS Dashboard ($49-99/mo)
                         ↓ CTA: "Need help executing?"
                    Roviq Agency Services ($3K+)
```

### Specific Unlocks

| Unlock | Before | After |
|--------|--------|-------|
| **Official vs Street Price** | Not possible | "CCC says $8.19/g. We see dispensaries at $11.13/g avg. That's a 36% markup." |
| **Real License Pipeline** | Faked from threats | 234 actual pending apps with geo, dates, types, DBE status |
| **Pending App Proximity Alerts** | Not possible | "3 new delivery apps within 5 miles of your store this month" |
| **Delivery Market Share** | Not tracked | "Delivery operators now capture 8.2% of vape revenue, up 2.1% QoQ" |
| **Category Price Divergence** | Not possible | CCC says Buds avg $X. GLASS sees actual shelf at $Y. Gap = story. |
| **Newsletter Price Wire** | Missing (promised) | Real-time from 24K+ observations: avg, median, movers, percentiles |
| **Public Intel Page** | Doesn't exist | CCC data + GLASS aggregates = SEO + lead gen engine |
| **Workforce Demographics** | Raw JSON | Curated: "36.3% female, 35.6% minority-owned" on public page |
| **Newsletter → GLASS funnel** | Broken (no data to tease) | Every issue has 5 sections showing GLASS data with "Get full data →" |

### Revenue Impact

| Metric | Current | With Bridge | How |
|--------|---------|-------------|-----|
| Newsletter subscribers | ~0 | 500+ (6-month target) | Free, valuable, data-differentiated |
| GLASS free-tier signups | Low | 10%+ of newsletter readers | Funnel from Price Wire teasers |
| GLASS premium conversions | ? | 5-10% of free tier | Per-operator data is the hook |
| Public page SEO traffic | 0 | 2K+ monthly visitors (3-month) | CCC data + GLASS aggregates = unique content |
| Roviq consulting leads | Sporadic | 2+/month from newsletter | Bottom-of-funnel CTA in every issue |

---

## 10. Implementation Timeline

| Day | Task | Owner | Depends On |
|-----|------|-------|-----------|
| 1 | Run migration SQL (create 6 CCC tables) | Backend | DB access |
| 1 | Run `backfill_ccc.py` (import existing JSON) | Backend | Migration |
| 1 | Verify backfill counts match JSON row counts | Backend | Backfill |
| 2 | Update `ccc_ingest.py` to write to DB after JSON | Backend | Migration |
| 2 | Update `glass_data_processor.py` with `fetch_ccc_context()` | Backend | Migration |
| 2 | Update `data_contract.py` with `ccc_context` schema | Backend | — |
| 3 | Create `src/routes/public-intel.ts` (5 public endpoints) | Backend | Migration |
| 3 | Add Drizzle schema definitions for CCC tables | Backend | Migration |
| 3-4 | Update `composer.py` to render CCC Watchlist + enriched Price Wire | Backend | Day 2 |
| 4 | Update `viz/license-pipeline` to use real `ccc_pending_applications` | Frontend | Migration |
| 5 | End-to-end test: pipeline run → DB write → newsletter draft | QA | Days 1-4 |

**Total effort: ~5 engineering days, no new infrastructure, no new dependencies beyond `psycopg2-binary`.**

---

## 11. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CCC API down during ingest | Medium | Low | JSON files are the fallback. DB write fails gracefully; newsletter still uses JSON. |
| CCC data format changes | Low | Medium | Validation in backfill script. Log schema mismatches. |
| 50K row cap on CCC endpoints | Already happening | Medium | Pagination or date-range queries. Track last-imported date. |
| Public endpoints abused (scraping) | Medium | Low | Rate limit (100 req/min). No auth = no operator data. |
| DB size growth from CCC data | Low | Low | ~100K rows total for CCC. Negligible vs GLASS prices table. |
| Cross-reference queries slow | Low | Medium | Pre-compute in `glass_data_processor.py`, not in API. Materialized views if needed. |

---

*This plan transforms two isolated data systems into a unified intelligence platform. The newsletter becomes the distribution channel. The public page becomes the acquisition channel. The dashboard becomes the retention product. GLASS data is the moat. CCC data is the bridge.*
