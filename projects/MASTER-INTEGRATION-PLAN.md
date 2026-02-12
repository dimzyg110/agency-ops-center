# ROVIQ ECOSYSTEM — MASTER INTEGRATION PLAN

**Version:** 1.0 FINAL  
**Date:** February 12, 2026  
**Status:** DEFINITIVE — Build from this document  
**Synthesized from:** Ecosystem Plan (Opus), Data Integration Plan (Codex/Kimi), Data Architecture Plan (Opus)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Unified Database Schema](#2-unified-database-schema)
3. [Composite Intelligence Scores](#3-composite-intelligence-scores)
4. [Product Integration Matrix](#4-product-integration-matrix)
5. [API Design](#5-api-design)
6. [ETL & Data Pipeline](#6-etl--data-pipeline)
7. [Unified Auth Strategy](#7-unified-auth-strategy)
8. [CH Driver Program](#8-ch-driver-program)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Risk Assessment](#10-risk-assessment)

---

## 1. Architecture Overview

### 1.1 The Core Thesis

GLASS is the **data gravity well**. Every product in the Roviq ecosystem either feeds data into GLASS or consumes data from GLASS. The integration strategy is **hub-and-spoke**: GLASS as single source of truth for product/pricing/regulatory data, with purpose-built APIs connecting each spoke.

**Why hub-and-spoke, not monolith:**

| Approach | Verdict |
|----------|---------|
| **Full merge** (everything in Railway PG) | ❌ Schema conflicts, migration hell, coupling, single point of failure |
| **Full separation** (current state) | ❌ No data sharing, duplicate products, stale VB data, no ecosystem analytics |
| **Hub-and-spoke** | ✅ Shared product/pricing truth via API. Domain isolation. Independent deploy. Gradual migration path. |

### 1.2 Current State

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT STATE (3 Isolated Islands)            │
│                                                                  │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │ GLASS PostgreSQL │  │ Virtual Budtender│  │ Cue PostgreSQL │  │
│  │ (Railway)        │  │ (Firebase)       │  │ (Neon)         │  │
│  │                  │  │                  │  │                │  │
│  │ • 492 operators  │  │ • ~300 CH        │  │ • users        │  │
│  │ • 100K+ products │  │   products       │  │ • brands       │  │
│  │ • 117K+ prices   │  │ • 0 sessions     │  │ • missions     │  │
│  │ • 6 CCC tables   │  │   tracked        │  │ • submissions  │  │
│  │ • scrape_runs    │  │                  │  │ • rewards      │  │
│  │ • threats/alerts │  │                  │  │ • courses      │  │
│  └─────────────────┘  └──────────────────┘  └────────────────┘  │
│                                                                  │
│  NO data flows between them today.                               │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Target State

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        TARGET STATE (Hub-and-Spoke)                          │
│                                                                              │
│           ┌───────────────────────────────────────────┐                       │
│           │          GLASS PostgreSQL (Railway)        │                       │
│           │              THE HUB                       │                       │
│           │                                            │                       │
│           │  EXISTING:                                 │                       │
│           │  • operators, products, prices              │                       │
│           │  • sources, scrape_runs, scrape_jobs        │                       │
│           │  • threats, alerts, recommendations         │                       │
│           │  • margin_rules, watchlists, waitlist       │                       │
│           │  • users, refresh_tokens                    │                       │
│           │                                            │                       │
│           │  NEW — CCC Regulatory Data:                │                       │
│           │  • ccc_lab_tests (149K pivoted)             │                       │
│           │  • ccc_facility_sales (182K unified)        │                       │
│           │  • ccc_monthly_prices (71 months)           │                       │
│           │  • ccc_licenses (772+1753 merged)           │                       │
│           │  • ccc_county_metrics (aggregated)          │                       │
│           │                                            │                       │
│           │  NEW — Ecosystem Integration:              │                       │
│           │  • budtender_sessions                       │                       │
│           │  • budtender_queries                        │                       │
│           │  • demand_signals (nightly batch)           │                       │
│           │  • ecosystem_events (cross-product stream)  │                       │
│           │                                            │                       │
│           │  NEW — Intelligence:                       │                       │
│           │  • operator_scores (computed cache)         │                       │
│           │  • google_reviews + google_place_stats      │                       │
│           │  • census_demographics                      │                       │
│           │  • enforcement_actions                      │                       │
│           │  • strains (Otreeba)                        │                       │
│           │  • etl_runs (audit log)                     │                       │
│           └───────┬──────────┬──────────┬─────────────┘                       │
│                   │          │          │                                      │
│        ┌──────────┘          │          └──────────┐                           │
│        ▼                     ▼                     ▼                           │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐                  │
│  │ Virtual       │  │ Cue (Neon)    │  │ Delivery         │                  │
│  │ Budtender     │  │              │  │ (Blaze POS)      │                  │
│  │               │  │ OWN DOMAIN:  │  │                  │                  │
│  │ Firestore     │  │ • participants│  │ Reads from Cue:  │                  │
│  │ → ELIMINATED  │  │ • missions   │  │ • driver missions│                  │
│  │               │  │ • submissions│  │ • incentive rules│                  │
│  │ READS GLASS:  │  │ • rewards    │  │                  │                  │
│  │ • products    │  │ • courses    │  │ WRITES to Cue:   │                  │
│  │ • prices      │  │ • admin_auth │  │ • delivery counts│                  │
│  │               │  │   _mappings  │  │ • ratings        │                  │
│  │ WRITES GLASS: │  │              │  │                  │                  │
│  │ • sessions    │  │ READS GLASS: │  └──────────────────┘                  │
│  │ • queries     │  │ • products   │                                         │
│  │ • demand      │  │ • prices     │    ┌──────────────┐  ┌────────────┐    │
│  │   signals     │  │ • operators  │    │ Newsletter   │  │ SIGNAL     │    │
│  │               │  │ • demand     │    │              │  │ (SEO)      │    │
│  │               │  │   signals    │    │ READS GLASS: │  │            │    │
│  └───────────────┘  │              │    │ • all scores │  │ READS:     │    │
│                     │ WRITES GLASS:│    │ • all CCC    │  │ • trends   │    │
│                     │ • ecosystem_ │    │ • all trends │  │ • strains  │    │
│                     │   events     │    │ • demand     │  │ • prices   │    │
│                     └──────────────┘    └──────────────┘  └────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 What Goes Where

| Database | Owns | Reads From |
|----------|------|------------|
| **GLASS PostgreSQL (Railway)** | Products, Prices, Operators, CCC data, Threats, Recommendations, Alerts, Margin Rules, Demand Signals, Ecosystem Events, Budtender Sessions, Operator Scores, Google Reviews, Census, Enforcement, Strains, ETL Runs | Scrapers (write), VB (write sessions), Cue (write events) |
| **Cue PostgreSQL (Neon)** | Users/Participants, Brands, Dispensaries, Missions, Submissions, Rewards, Redemptions, Courses, Certifications, Audit Logs, `admin_auth_mappings` | GLASS API (product catalog, demand signals, underperforming products) |
| **Virtual Budtender** | **Nothing** (stateless!) | GLASS API (product catalog). Firebase Firestore → **ELIMINATED** |
| **Delivery** | Nothing own (Blaze POS owns order data) | Cue (driver missions), GLASS API (product catalog for driver training) |

### 1.5 Data Flow Summary

| Data | Source → Destination | Mechanism | Frequency |
|------|---------------------|-----------|-----------|
| Product catalog (100K+) | GLASS scrapers → GLASS DB → VB, Cue | REST API | On request (daily freshness) |
| Price observations | Dutchie/Weedmaps → GLASS DB | CamoFox scrapers | Daily (3AM + 10PM ET) |
| CCC regulatory data | CCC CSV → GLASS DB | ETL import scripts | Monthly |
| Budtender queries | Customer → VB → GLASS | VB backend → GLASS API (fire-and-forget) | Per conversation |
| Demand signals | Aggregated from VB queries | Nightly batch job in GLASS | Daily |
| Mission performance | Cue submissions → GLASS | Cue → GLASS ecosystem events API | Per submission |
| Conversion tracking | VB recommendation → click | Redirect click tracking | Per click |
| Driver delivery data | Blaze POS → Cue | Manual submission or Blaze webhook | Per delivery or daily |
| Gift card redemptions | Tremendous API → Cue | Tremendous webhook | Per redemption |
| Google Reviews | Google Places API → GLASS | Scraper cron | Weekly |
| Census demographics | Census API → GLASS | ETL script | Annually |
| Enforcement actions | CCC website → GLASS | Scraper cron | Weekly |

---

## 2. Unified Database Schema

### 2.1 Design Decisions

Where plans conflicted, here's what won and why:

| Conflict | Resolution | Rationale |
|----------|-----------|-----------|
| **Lab tests: 2 rows per tag vs. pivoted** | **Pivoted (1 row per METRC tag)** — Codex plan | More efficient storage, easier THC calculations. Compute `total_thc = thc + (thca × 0.877)` at import time. |
| **Licenses: 2 tables vs. 1 merged** | **1 merged table (`ccc_licenses`)** — Codex plan | commence-ops + adult-market share license_number. Merge with ON CONFLICT COALESCE. Counties file enriches with region/town. |
| **Market sales: separate adult/medical vs. unified** | **Unified with `market_type` discriminator** — all plans agree | Medical = Retail delivery type, `market_type = 'medical'`. Single table, easier queries. |
| **Operator scores: materialized view vs. table** | **Table (`operator_scores`)** — Codex plan | Materialized views can't have partial updates. Table allows incremental recompute per operator. Add `computation_version` for schema evolution. |
| **Google reviews: single vs. split table** | **Split: `google_reviews` + `google_place_stats`** — Opus data plan | Aggregate stats (rating, total) update frequently. Individual reviews are append-only. Different access patterns. |
| **CCC licensed operators: separate table vs. merged into operators** | **Separate `ccc_licenses` table linked via FK** — Codex plan | CCC data is regulatory truth (all 772+ licenses). Operators table is scraped truth (Dutchie/WM presence). Different concerns, linked by `operator_id`. |

### 2.2 New Tables — Drizzle ORM (GLASS PostgreSQL)

All new tables added to `services/api/src/db/schema.ts`:

```typescript
import { pgTable, uuid, varchar, text, timestamp, boolean, integer, decimal, jsonb, unique, index } from 'drizzle-orm/pg-core';

// ============================================================
// CCC LAB TESTS — Pivoted: one row per METRC tag with THC + THCA
// Source: testing-thc-thca.csv (298K raw → ~149K pivoted)
// ============================================================
export const cccLabTests = pgTable('ccc_lab_tests', {
  id: uuid('id').primaryKey().defaultRandom(),
  metrc_tag: varchar('metrc_tag', { length: 30 }).notNull(),
  product_category: varchar('product_category', { length: 30 }).notNull(),
  strain_code: varchar('strain_code', { length: 30 }).notNull(),
  thc_percent: decimal('thc_percent', { precision: 6, scale: 3 }),
  thca_percent: decimal('thca_percent', { precision: 6, scale: 3 }),
  total_thc_percent: decimal('total_thc_percent', { precision: 6, scale: 3 }), // THC + (THCA × 0.877)
  testing_lab: varchar('testing_lab', { length: 10 }).notNull(),
  test_date: timestamp('test_date', { withTimezone: true }).notNull(),
  test_comment: text('test_comment'),
  operator_id: uuid('operator_id').references(() => operators.id, { onDelete: 'set null' }),
  source_file: varchar('source_file', { length: 100 }),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('ccc_lab_tests_metrc_tag_unique').on(table.metrc_tag),
  index('idx_lab_tests_category').on(table.product_category),
  index('idx_lab_tests_strain').on(table.strain_code),
  index('idx_lab_tests_date').on(table.test_date),
  index('idx_lab_tests_lab').on(table.testing_lab),
  index('idx_lab_tests_thc').on(table.total_thc_percent),
  index('idx_lab_tests_operator').on(table.operator_id),
  index('idx_lab_tests_category_thc').on(table.product_category, table.total_thc_percent),
  index('idx_lab_tests_date_category').on(table.test_date, table.product_category),
]);

// ============================================================
// CCC FACILITY SALES — Unified adult + medical + delivery
// Sources: facility-sales-stats.csv, itd-retail-delivery-sales.csv, medical-facility-stats.csv
// ============================================================
export const cccFacilitySales = pgTable('ccc_facility_sales', {
  id: uuid('id').primaryKey().defaultRandom(),
  sale_date: timestamp('sale_date', { withTimezone: true }).notNull(),
  market_type: varchar('market_type', { length: 15 }).notNull(), // 'adult' or 'medical'
  delivery_type: varchar('delivery_type', { length: 25 }).notNull(), // 'Retail', 'Delivery Operators', 'Delivery Couriers', 'Medical'
  product_category: varchar('product_category', { length: 50 }).notNull(),
  unit_of_measure: varchar('unit_of_measure', { length: 10 }).notNull(), // 'ea' or 'g'
  quantity: decimal('quantity', { precision: 14, scale: 3 }).notNull(),
  units: integer('units').notNull(),
  count_based_total: decimal('count_based_total', { precision: 14, scale: 3 }),
  dollar_count_based: decimal('dollar_count_based', { precision: 14, scale: 2 }),
  weight_based_total: decimal('weight_based_total', { precision: 14, scale: 3 }),
  dollar_weight_based: decimal('dollar_weight_based', { precision: 14, scale: 2 }),
  total_dollars: decimal('total_dollars', { precision: 14, scale: 2 }).notNull(),
  source_file: varchar('source_file', { length: 100 }),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('ccc_facility_sales_dedup').on(
    table.sale_date, table.market_type, table.delivery_type,
    table.product_category, table.unit_of_measure
  ),
  index('idx_facility_sales_date').on(table.sale_date),
  index('idx_facility_sales_market').on(table.market_type),
  index('idx_facility_sales_delivery').on(table.delivery_type),
  index('idx_facility_sales_category').on(table.product_category),
  index('idx_facility_sales_date_market_cat').on(table.sale_date, table.market_type, table.product_category),
  index('idx_facility_sales_date_delivery').on(table.sale_date, table.delivery_type),
]);

// ============================================================
// CCC MONTHLY PRICE BENCHMARK — Official state avg price/gram
// Source: avg-monthly-price-oz.csv (71 rows, Jan 2020 – Nov 2025)
// ============================================================
export const cccMonthlyPrices = pgTable('ccc_monthly_prices', {
  id: uuid('id').primaryKey().defaultRandom(),
  year_month: varchar('year_month', { length: 7 }).notNull(), // 'YYYY-MM'
  avg_price_per_gram: decimal('avg_price_per_gram', { precision: 6, scale: 2 }).notNull(),
  avg_price_per_oz: decimal('avg_price_per_oz', { precision: 8, scale: 2 }),
  avg_price_per_eighth: decimal('avg_price_per_eighth', { precision: 7, scale: 2 }),
  mom_change_pct: decimal('mom_change_pct', { precision: 6, scale: 2 }),
  yoy_change_pct: decimal('yoy_change_pct', { precision: 6, scale: 2 }),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('ccc_monthly_prices_month_unique').on(table.year_month),
  index('idx_monthly_prices_month').on(table.year_month),
]);

// ============================================================
// CCC LICENSES — Merged from commence-ops.csv + adult-market-data-counties.csv
// One row per license_number. A business may hold multiple licenses.
// ============================================================
export const cccLicenses = pgTable('ccc_licenses', {
  id: uuid('id').primaryKey().defaultRandom(),
  license_number: varchar('license_number', { length: 30 }).notNull(),
  business_name: varchar('business_name', { length: 500 }).notNull(),
  license_type: varchar('license_type', { length: 100 }).notNull(),
  license_status: varchar('license_status', { length: 30 }).notNull(),
  application_status: varchar('application_status', { length: 30 }),
  approved_license_type: varchar('approved_license_type', { length: 50 }),
  license_stage: varchar('license_stage', { length: 30 }),
  application_classification: varchar('application_classification', { length: 100 }),
  classification_tier1: varchar('classification_tier1', { length: 50 }),
  classification_tier2: varchar('classification_tier2', { length: 50 }),
  // Contact
  business_email: varchar('business_email', { length: 255 }),
  business_phone: varchar('business_phone', { length: 30 }),
  ein_tin: varchar('ein_tin', { length: 20 }),
  // Business address
  business_address_1: varchar('business_address_1', { length: 255 }),
  business_address_2: varchar('business_address_2', { length: 255 }),
  business_city: varchar('business_city', { length: 100 }),
  business_state: varchar('business_state', { length: 2 }),
  business_zip: varchar('business_zip', { length: 10 }),
  // Establishment (physical location)
  establishment_address_1: varchar('establishment_address_1', { length: 255 }),
  establishment_address_2: varchar('establishment_address_2', { length: 255 }),
  establishment_city: varchar('establishment_city', { length: 100 }),
  establishment_state: varchar('establishment_state', { length: 2 }),
  establishment_zip: varchar('establishment_zip', { length: 10 }),
  // Geography
  latitude: decimal('latitude', { precision: 10, scale: 8 }),
  longitude: decimal('longitude', { precision: 11, scale: 8 }),
  county: varchar('county', { length: 50 }),
  region: varchar('region', { length: 50 }),
  town: varchar('town', { length: 100 }),
  // Equity & Priority
  dbe_status: varchar('dbe_status', { length: 200 }),
  is_social_equity: boolean('is_social_equity').notNull().default(false),
  is_economic_empowerment: boolean('is_economic_empowerment').notNull().default(false),
  priority_status: boolean('priority_status').notNull().default(false),
  se_number: varchar('se_number', { length: 20 }),
  ee_number: varchar('ee_number', { length: 20 }),
  // Cultivation-specific
  cultivation_environment: varchar('cultivation_environment', { length: 20 }),
  cultivation_tier: varchar('cultivation_tier', { length: 50 }),
  // Timeline
  submitted_date: timestamp('submitted_date', { withTimezone: true }),
  application_approved_date: timestamp('application_approved_date', { withTimezone: true }),
  license_start_date: timestamp('license_start_date', { withTimezone: true }),
  license_expiration_date: timestamp('license_expiration_date', { withTimezone: true }),
  commence_operations_date: timestamp('commence_operations_date', { withTimezone: true }),
  first_compliance_review_date: timestamp('first_compliance_review_date', { withTimezone: true }),
  deemed_complete_date: timestamp('deemed_complete_date', { withTimezone: true }),
  // Financials
  payment_amount: decimal('payment_amount', { precision: 10, scale: 2 }),
  license_fee_amount: decimal('license_fee_amount', { precision: 10, scale: 2 }),
  // GLASS linkage
  operator_id: uuid('operator_id').references(() => operators.id, { onDelete: 'set null' }),
  // ETL metadata
  ccc_last_updated: timestamp('ccc_last_updated', { withTimezone: true }),
  source_file: varchar('source_file', { length: 100 }),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('ccc_licenses_number_unique').on(table.license_number),
  index('idx_licenses_business_name').on(table.business_name),
  index('idx_licenses_type').on(table.license_type),
  index('idx_licenses_status').on(table.license_status),
  index('idx_licenses_stage').on(table.license_stage),
  index('idx_licenses_city').on(table.establishment_city),
  index('idx_licenses_county').on(table.county),
  index('idx_licenses_location').on(table.latitude, table.longitude),
  index('idx_licenses_operator').on(table.operator_id),
  index('idx_licenses_ein').on(table.ein_tin),
  index('idx_licenses_expiration').on(table.license_expiration_date),
  index('idx_licenses_equity').on(table.is_social_equity, table.is_economic_empowerment),
  index('idx_licenses_type_status').on(table.license_type, table.license_status),
]);

// ============================================================
// COUNTY MARKET METRICS — Aggregated from license data
// ============================================================
export const cccCountyMetrics = pgTable('ccc_county_metrics', {
  id: uuid('id').primaryKey().defaultRandom(),
  county: varchar('county', { length: 50 }).notNull(),
  region: varchar('region', { length: 50 }),
  county_lat: decimal('county_lat', { precision: 10, scale: 6 }),
  county_lon: decimal('county_lon', { precision: 11, scale: 6 }),
  total_licenses: integer('total_licenses').notNull().default(0),
  active_retailers: integer('active_retailers').notNull().default(0),
  active_cultivators: integer('active_cultivators').notNull().default(0),
  active_manufacturers: integer('active_manufacturers').notNull().default(0),
  active_delivery: integer('active_delivery').notNull().default(0),
  active_testing_labs: integer('active_testing_labs').notNull().default(0),
  pending_applications: integer('pending_applications').notNull().default(0),
  social_equity_count: integer('social_equity_count').notNull().default(0),
  economic_empowerment_count: integer('economic_empowerment_count').notNull().default(0),
  dbe_count: integer('dbe_count').notNull().default(0),
  operators_per_10k_pop: decimal('operators_per_10k_pop', { precision: 6, scale: 2 }),
  saturation_score: decimal('saturation_score', { precision: 5, scale: 2 }),
  snapshot_date: timestamp('snapshot_date', { withTimezone: true }).notNull().defaultNow(),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('ccc_county_metrics_county_date').on(table.county, table.snapshot_date),
  index('idx_county_metrics_county').on(table.county),
  index('idx_county_metrics_region').on(table.region),
]);

// ============================================================
// OPERATOR SCORES — Computed intelligence (cached table, not mat view)
// ============================================================
export const operatorScores = pgTable('operator_scores', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  // Composite (0-100)
  health_score: integer('health_score'),
  // Component scores (each 0-100)
  price_competitiveness_score: integer('price_competitiveness_score'),
  product_quality_score: integer('product_quality_score'),
  compliance_score: integer('compliance_score'),
  market_presence_score: integer('market_presence_score'),
  review_score: integer('review_score'),
  // THC Integrity
  thc_integrity_index: integer('thc_integrity_index'),
  thc_integrity_sample_size: integer('thc_integrity_sample_size'),
  // Price Position
  price_position_vs_state: decimal('price_position_vs_state', { precision: 6, scale: 2 }),
  price_position_vs_local: decimal('price_position_vs_local', { precision: 6, scale: 2 }),
  price_position_label: varchar('price_position_label', { length: 20 }), // premium, competitive, budget, undercut
  // Growth Trajectory
  growth_trajectory_score: integer('growth_trajectory_score'),
  growth_trend_direction: varchar('growth_trend_direction', { length: 10 }),
  growth_data_points: integer('growth_data_points'),
  // Market Saturation
  local_saturation_score: decimal('local_saturation_score', { precision: 5, scale: 2 }),
  competitors_5mi: integer('competitors_5mi'),
  competitors_10mi: integer('competitors_10mi'),
  // Metadata
  computed_at: timestamp('computed_at', { withTimezone: true }).notNull().defaultNow(),
  data_freshness: jsonb('data_freshness'),
  computation_version: varchar('computation_version', { length: 20 }).notNull().default('v1'),
}, (table) => [
  unique('operator_scores_operator_version').on(table.operator_id, table.computation_version),
  index('idx_op_scores_operator').on(table.operator_id),
  index('idx_op_scores_health').on(table.health_score),
  index('idx_op_scores_computed').on(table.computed_at),
]);

// ============================================================
// GOOGLE REVIEWS — Individual reviews
// ============================================================
export const googleReviews = pgTable('google_reviews', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  place_id: varchar('place_id', { length: 100 }).notNull(),
  overall_rating: decimal('overall_rating', { precision: 3, scale: 2 }),
  total_reviews: integer('total_reviews'),
  reviewer_name: varchar('reviewer_name', { length: 200 }),
  review_rating: integer('review_rating'),
  review_text: text('review_text'),
  review_time: timestamp('review_time', { withTimezone: true }),
  review_language: varchar('review_language', { length: 5 }),
  sentiment_score: decimal('sentiment_score', { precision: 4, scale: 3 }),
  sentiment_label: varchar('sentiment_label', { length: 20 }),
  fetched_at: timestamp('fetched_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_google_reviews_operator').on(table.operator_id),
  index('idx_google_reviews_place').on(table.place_id),
  index('idx_google_reviews_rating').on(table.overall_rating),
  index('idx_google_reviews_time').on(table.review_time),
]);

// ============================================================
// GOOGLE PLACE STATS — Aggregate per operator (separate access pattern)
// ============================================================
export const googlePlaceStats = pgTable('google_place_stats', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }).unique(),
  google_place_id: varchar('google_place_id', { length: 255 }),
  current_rating: decimal('current_rating', { precision: 2, scale: 1 }),
  total_reviews: integer('total_reviews'),
  price_level: integer('price_level'),
  business_status: varchar('business_status', { length: 50 }),
  hours_json: jsonb('hours_json'),
  popular_times_json: jsonb('popular_times_json'),
  scraped_at: timestamp('scraped_at', { withTimezone: true }).notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_google_place_stats_operator').on(table.operator_id),
  index('idx_google_place_stats_rating').on(table.current_rating),
]);

// ============================================================
// CENSUS DEMOGRAPHICS — US Census ACS 5-year estimates for MA
// ============================================================
export const censusDemographics = pgTable('census_demographics', {
  id: uuid('id').primaryKey().defaultRandom(),
  geo_type: varchar('geo_type', { length: 20 }).notNull(), // 'zip', 'town', 'county'
  geo_id: varchar('geo_id', { length: 20 }).notNull(),
  geo_name: varchar('geo_name', { length: 255 }).notNull(),
  state_fips: varchar('state_fips', { length: 2 }).notNull().default('25'),
  total_population: integer('total_population'),
  median_household_income: integer('median_household_income'),
  median_age: decimal('median_age', { precision: 4, scale: 1 }),
  pct_age_21_34: decimal('pct_age_21_34', { precision: 5, scale: 2 }),
  pct_age_35_54: decimal('pct_age_35_54', { precision: 5, scale: 2 }),
  pct_age_55_plus: decimal('pct_age_55_plus', { precision: 5, scale: 2 }),
  total_housing_units: integer('total_housing_units'),
  pct_renter_occupied: decimal('pct_renter_occupied', { precision: 5, scale: 2 }),
  pct_bachelor_plus: decimal('pct_bachelor_plus', { precision: 5, scale: 2 }),
  acs_year: integer('acs_year').notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('census_geo_year_unique').on(table.geo_type, table.geo_id, table.acs_year),
  index('idx_census_geo_type').on(table.geo_type),
  index('idx_census_geo_id').on(table.geo_id),
  index('idx_census_population').on(table.total_population),
  index('idx_census_income').on(table.median_household_income),
]);

// ============================================================
// ENFORCEMENT ACTIONS
// ============================================================
export const enforcementActions = pgTable('enforcement_actions', {
  id: uuid('id').primaryKey().defaultRandom(),
  license_id: uuid('license_id').references(() => cccLicenses.id, { onDelete: 'set null' }),
  operator_id: uuid('operator_id').references(() => operators.id, { onDelete: 'set null' }),
  action_type: varchar('action_type', { length: 50 }).notNull(),
  action_date: timestamp('action_date', { withTimezone: true }).notNull(),
  description: text('description'),
  fine_amount: decimal('fine_amount', { precision: 10, scale: 2 }),
  resolution_status: varchar('resolution_status', { length: 30 }),
  resolution_date: timestamp('resolution_date', { withTimezone: true }),
  source_url: text('source_url'),
  source_document: text('source_document'),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_enforcement_license').on(table.license_id),
  index('idx_enforcement_operator').on(table.operator_id),
  index('idx_enforcement_type').on(table.action_type),
  index('idx_enforcement_date').on(table.action_date),
]);

// ============================================================
// STRAIN DATABASE — From Otreeba API (future)
// ============================================================
export const strains = pgTable('strains', {
  id: uuid('id').primaryKey().defaultRandom(),
  otreeba_id: varchar('otreeba_id', { length: 50 }),
  name: varchar('name', { length: 200 }).notNull(),
  slug: varchar('slug', { length: 200 }),
  strain_type: varchar('strain_type', { length: 20 }),
  thc_min: decimal('thc_min', { precision: 5, scale: 2 }),
  thc_max: decimal('thc_max', { precision: 5, scale: 2 }),
  cbd_min: decimal('cbd_min', { precision: 5, scale: 2 }),
  cbd_max: decimal('cbd_max', { precision: 5, scale: 2 }),
  description: text('description'),
  effects: jsonb('effects'),
  flavors: jsonb('flavors'),
  medical_uses: jsonb('medical_uses'),
  terpene_profile: jsonb('terpene_profile'),
  parent_strain_1: varchar('parent_strain_1', { length: 200 }),
  parent_strain_2: varchar('parent_strain_2', { length: 200 }),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('strains_otreeba_unique').on(table.otreeba_id),
  index('idx_strains_name').on(table.name),
  index('idx_strains_type').on(table.strain_type),
  index('idx_strains_slug').on(table.slug),
]);

// ============================================================
// ECOSYSTEM INTEGRATION TABLES
// ============================================================

// Tracks Virtual Budtender conversation sessions
export const budtenderSessions = pgTable('budtender_sessions', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenant_id: varchar('tenant_id', { length: 50 }).notNull(),
  operator_id: uuid('operator_id').references(() => operators.id, { onDelete: 'set null' }),
  session_token: varchar('session_token', { length: 255 }).notNull(),
  started_at: timestamp('started_at', { withTimezone: true }).notNull().defaultNow(),
  ended_at: timestamp('ended_at', { withTimezone: true }),
  message_count: integer('message_count').default(0),
  recommendation_count: integer('recommendation_count').default(0),
  click_through_count: integer('click_through_count').default(0),
  device_type: varchar('device_type', { length: 20 }),
  referrer: text('referrer'),
  metadata: jsonb('metadata').default({}),
}, (table) => [
  index('idx_bsessions_tenant').on(table.tenant_id),
  index('idx_bsessions_operator').on(table.operator_id),
  index('idx_bsessions_started').on(table.started_at),
]);

// Individual queries within sessions (raw demand signals)
export const budtenderQueries = pgTable('budtender_queries', {
  id: uuid('id').primaryKey().defaultRandom(),
  session_id: uuid('session_id').notNull().references(() => budtenderSessions.id, { onDelete: 'cascade' }),
  tenant_id: varchar('tenant_id', { length: 50 }).notNull(),
  query_text: text('query_text').notNull(),
  parsed_intent: jsonb('parsed_intent'),
  products_recommended: jsonb('products_recommended'), // UUID[]
  products_clicked: jsonb('products_clicked'), // UUID[]
  response_time_ms: integer('response_time_ms'),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_bqueries_session').on(table.session_id),
  index('idx_bqueries_tenant').on(table.tenant_id),
  index('idx_bqueries_created').on(table.created_at),
]);

// Aggregated demand signals (nightly batch from budtender_queries)
export const demandSignals = pgTable('demand_signals', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').references(() => operators.id, { onDelete: 'cascade' }),
  category: varchar('category', { length: 50 }).notNull(),
  goal: varchar('goal', { length: 50 }),
  experience_level: varchar('experience_level', { length: 20 }),
  budget_range: varchar('budget_range', { length: 20 }),
  query_count: integer('query_count').notNull().default(0),
  conversion_count: integer('conversion_count').default(0),
  period_start: timestamp('period_start', { withTimezone: true }).notNull(),
  period_end: timestamp('period_end', { withTimezone: true }).notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_demand_operator').on(table.operator_id),
  index('idx_demand_category').on(table.category),
  index('idx_demand_period').on(table.period_start),
]);

// Cross-product event stream
export const ecosystemEvents = pgTable('ecosystem_events', {
  id: uuid('id').primaryKey().defaultRandom(),
  source_product: varchar('source_product', { length: 20 }).notNull(), // 'glass', 'budtender', 'cue', 'delivery'
  event_type: varchar('event_type', { length: 50 }).notNull(),
  operator_id: uuid('operator_id').references(() => operators.id, { onDelete: 'set null' }),
  participant_id: varchar('participant_id', { length: 255 }),
  payload: jsonb('payload').notNull().default({}),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_events_source').on(table.source_product),
  index('idx_events_type').on(table.event_type),
  index('idx_events_operator').on(table.operator_id),
  index('idx_events_created').on(table.created_at),
]);

// ============================================================
// ETL RUN LOG — Track every import for auditability
// ============================================================
export const etlRuns = pgTable('etl_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  dataset: varchar('dataset', { length: 50 }).notNull(),
  source_file: varchar('source_file', { length: 255 }).notNull(),
  source_hash: varchar('source_hash', { length: 64 }),
  started_at: timestamp('started_at', { withTimezone: true }).notNull().defaultNow(),
  completed_at: timestamp('completed_at', { withTimezone: true }),
  status: varchar('status', { length: 20 }).notNull().default('running'),
  rows_read: integer('rows_read').default(0),
  rows_inserted: integer('rows_inserted').default(0),
  rows_updated: integer('rows_updated').default(0),
  rows_skipped: integer('rows_skipped').default(0),
  rows_errored: integer('rows_errored').default(0),
  error_log: jsonb('error_log').default([]),
  metadata: jsonb('metadata').default({}),
}, (table) => [
  index('idx_etl_runs_dataset').on(table.dataset),
  index('idx_etl_runs_status').on(table.status),
  index('idx_etl_runs_started').on(table.started_at),
]);
```

### 2.3 Modifications to Existing `operators` Table

```sql
-- Migration: Add CCC linkage columns to operators
ALTER TABLE operators ADD COLUMN IF NOT EXISTS license_type VARCHAR(100);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS county VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS region VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS ccc_license_id UUID REFERENCES ccc_licenses(id) ON DELETE SET NULL;
ALTER TABLE operators ADD COLUMN IF NOT EXISTS google_place_id VARCHAR(255);
CREATE INDEX IF NOT EXISTS idx_operators_county ON operators(county);
CREATE INDEX IF NOT EXISTS idx_operators_license_type ON operators(license_type);
CREATE INDEX IF NOT EXISTS idx_operators_ccc_license ON operators(ccc_license_id);
CREATE INDEX IF NOT EXISTS idx_operators_google_place ON operators(google_place_id);
```

### 2.4 New Tables in Cue (Neon PostgreSQL)

```sql
-- Cue: Generalized participant system (replaces budtender-only)
CREATE TYPE participant_type AS ENUM (
  'budtender', 'delivery_driver', 'brand_ambassador', 'customer'
);

CREATE TABLE participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  dispensary_id UUID REFERENCES dispensaries(id) ON DELETE SET NULL,
  type participant_type NOT NULL DEFAULT 'budtender',
  display_name VARCHAR(255),
  avatar_url TEXT,
  employer_name VARCHAR(255),
  employee_id VARCHAR(100),
  position VARCHAR(100),
  verified BOOLEAN DEFAULT FALSE,
  verified_at TIMESTAMPTZ,
  verified_by UUID,
  total_earnings DECIMAL(10, 2) DEFAULT 0,
  total_missions_completed INTEGER DEFAULT 0,
  total_submissions INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  metadata JSONB DEFAULT '{}',
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, type)
);

-- Mission type filter
ALTER TABLE missions ADD COLUMN eligible_participant_types TEXT[] DEFAULT ARRAY['budtender'];

-- Rename budtender_id → participant_id
ALTER TABLE mission_assignments RENAME COLUMN budtender_id TO participant_id;
ALTER TABLE sales_submissions RENAME COLUMN budtender_id TO participant_id;

-- Driver-specific submissions
CREATE TABLE delivery_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  participant_id UUID NOT NULL REFERENCES participants(id),
  mission_id UUID NOT NULL REFERENCES missions(id),
  delivery_count INTEGER,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  average_rating DECIMAL(3, 2),
  on_time_percentage DECIMAL(5, 2),
  proof_type VARCHAR(50) NOT NULL,
  proof_image_url TEXT,
  proof_notes TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  reviewed_by UUID,
  reviewed_at TIMESTAMPTZ,
  review_notes TEXT,
  earned_amount DECIMAL(10, 2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- GLASS product linkage
ALTER TABLE products ADD COLUMN glass_product_id VARCHAR(36);
ALTER TABLE products ADD COLUMN glass_operator_id VARCHAR(36);

-- Clerk ↔ Cue admin mapping
CREATE TABLE admin_auth_mappings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_user_id VARCHAR(255) NOT NULL UNIQUE,
  cue_user_id UUID NOT NULL REFERENCES users(id),
  glass_user_id UUID,
  role VARCHAR(50) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.5 Storage Estimates

| Table | Rows | Est. Size | Priority |
|-------|------|-----------|----------|
| `ccc_lab_tests` | ~149K (pivoted) | ~45MB | P0 |
| `ccc_facility_sales` | ~182K (3 files unified) | ~32MB | P0 |
| `ccc_monthly_prices` | 71 | <1KB | P0 |
| `ccc_licenses` | ~1,753 (merged) | ~3MB | P0 |
| `ccc_county_metrics` | ~14 (counties) | <100KB | P1 |
| `operator_scores` | ~500 | ~50KB | P1 |
| `google_reviews` | ~25K (future) | ~5MB | P2 |
| `google_place_stats` | ~500 (future) | ~50KB | P2 |
| `census_demographics` | ~500 (future) | ~500KB | P2 |
| `enforcement_actions` | ~50-200 (future) | ~100KB | P2 |
| `strains` | ~4K (future) | ~10MB | P3 |
| `budtender_sessions` | growing | — | P1 |
| `budtender_queries` | growing | — | P1 |
| `demand_signals` | growing | — | P1 |
| `ecosystem_events` | growing | — | P1 |
| `etl_runs` | ~100 | <100KB | P0 |
| **Total new** | **~360K+** | **~96MB** | |

Railway handles this trivially. No partitioning needed until any table exceeds 2M rows.

---

## 3. Composite Intelligence Scores

### 3.1 Operator Health Score (0–100)

**Formula:**
```
health_score = (
  price_competitiveness × 0.30 +
  product_quality × 0.20 +
  compliance × 0.20 +
  market_presence × 0.15 +
  review_score × 0.15
)
```

#### Price Competitiveness (0–100)

Compares operator's avg price/gram to state CCC benchmark and county average.

```sql
-- Score: 100 at state avg, decreasing with deviation. Bonus for trending toward market.
WITH latest_state_avg AS (
  SELECT avg_price_per_gram::numeric AS val FROM ccc_monthly_prices ORDER BY year_month DESC LIMIT 1
),
operator_avg AS (
  SELECT
    p.operator_id,
    AVG(p.price_per_gram::numeric) FILTER (WHERE p.scraped_at > NOW() - INTERVAL '30 days') AS avg_30d,
    AVG(p.price_per_gram::numeric) FILTER (WHERE p.scraped_at BETWEEN NOW() - INTERVAL '60 days' AND NOW() - INTERVAL '30 days') AS avg_60d
  FROM prices p
  WHERE p.price_per_gram IS NOT NULL AND p.price_per_gram::numeric BETWEEN 1 AND 50
  GROUP BY p.operator_id
  HAVING COUNT(*) FILTER (WHERE p.scraped_at > NOW() - INTERVAL '30 days') >= 3
)
SELECT
  oa.operator_id,
  GREATEST(0, LEAST(100,
    100 - ABS((oa.avg_30d - lsa.val) / lsa.val * 100) * 1.5
    + CASE WHEN oa.avg_30d < lsa.val THEN 10 ELSE 0 END
    + CASE WHEN oa.avg_60d IS NOT NULL AND ABS(oa.avg_30d - lsa.val) < ABS(oa.avg_60d - lsa.val) THEN 5 ELSE 0 END
  ))::integer AS price_competitiveness
FROM operator_avg oa CROSS JOIN latest_state_avg lsa;
```

#### Product Quality (0–100)

Based on menu breadth, depth, and THC data transparency.

```
base = 50
+ min(20, category_count × 4)           -- variety: up to 5 categories
+ min(15, log2(product_count) × 3)      -- depth: more products = better
+ (products_with_thc / total) × 15      -- transparency: listing THC%
```

#### Compliance (0–100)

```
Active license = 70 base
+ Social Equity/DBE bonus = +10
+ No enforcement actions (1yr) = +20
+ License not expiring within 90 days = +10
- Each enforcement action = -20
Expired license = 0
```

#### Market Presence (0–100)

```
= min(100,
    has_dutchie × 30
  + has_weedmaps × 30
  + has_website × 20
  + (products_listed / 200) × 20   -- menu completeness
)
```

#### Review Score (0–100)

```
= (google_rating / 5.0 × 70) + min(30, total_reviews × 0.3)
```

### 3.2 THC Integrity Index (0–100)

Measures how accurately dispensary menus represent THC% vs lab-tested reality.

```sql
-- 100 = menu THC matches lab THC exactly. Lower = more inflation.
CREATE MATERIALIZED VIEW mv_lab_thc_monthly AS
SELECT
  DATE_TRUNC('month', test_date) AS month,
  product_category,
  COUNT(*) AS test_count,
  ROUND(AVG(total_thc_percent::numeric), 2) AS avg_thc,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_thc_percent::numeric)::numeric, 2) AS median_thc,
  ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_thc_percent::numeric)::numeric, 2) AS p75_thc,
  ROUND(STDDEV(total_thc_percent::numeric), 2) AS stddev_thc
FROM ccc_lab_tests
WHERE total_thc_percent IS NOT NULL
  AND total_thc_percent::numeric BETWEEN 0.1 AND 50
  AND product_category = 'Buds'
GROUP BY DATE_TRUNC('month', test_date), product_category;

CREATE UNIQUE INDEX ON mv_lab_thc_monthly(month, product_category);

CREATE MATERIALIZED VIEW mv_menu_thc_monthly AS
SELECT
  DATE_TRUNC('month', pr.scraped_at) AS month,
  p.category,
  COUNT(*) AS listing_count,
  ROUND(AVG(p.thc_percent::numeric), 2) AS avg_listed_thc,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p.thc_percent::numeric)::numeric, 2) AS median_listed_thc
FROM prices pr
JOIN products p ON pr.product_id = p.id
WHERE p.category = 'flower'
  AND p.thc_percent IS NOT NULL
  AND p.thc_percent::numeric BETWEEN 0.1 AND 50
GROUP BY DATE_TRUNC('month', pr.scraped_at), p.category;

CREATE UNIQUE INDEX ON mv_menu_thc_monthly(month, category);
```

**Per-operator THC Integrity:**
```sql
-- operator's avg menu THC vs statewide lab avg → integrity score
SELECT
  op.id, op.name,
  AVG(p.thc_percent::numeric) AS menu_avg_thc,
  lab.avg_thc AS lab_avg_thc,
  GREATEST(0, 100 - ABS(AVG(p.thc_percent::numeric) - lab.avg_thc) * 10)::integer AS thc_integrity_index
FROM operators op
JOIN prices pr ON pr.operator_id = op.id AND pr.scraped_at > NOW() - INTERVAL '30 days'
JOIN products p ON pr.product_id = p.id AND p.category = 'flower' AND p.thc_percent IS NOT NULL
CROSS JOIN (SELECT AVG(total_thc_percent::numeric) AS avg_thc FROM ccc_lab_tests WHERE product_category = 'Buds' AND test_date > NOW() - INTERVAL '6 months') lab
GROUP BY op.id, op.name, lab.avg_thc;
```

### 3.3 Market Saturation Score (0–100)

Per zip code: higher = more saturated (harder to compete).

```sql
CREATE MATERIALIZED VIEW mv_market_gaps AS
WITH zip_operators AS (
  SELECT
    COALESCE(l.establishment_zip, LEFT(op.metadata->>'zip', 5)) AS zip_code,
    COUNT(DISTINCT op.id) AS operator_count
  FROM operators op
  LEFT JOIN ccc_licenses l ON l.operator_id = op.id
  WHERE op.status = 'active'
  GROUP BY 1
),
zip_pop AS (
  SELECT geo_id AS zip_code, total_population, median_household_income, pct_age_21_34
  FROM census_demographics WHERE geo_type = 'zip' AND state_fips = '25'
)
SELECT
  zp.zip_code,
  zp.total_population,
  COALESCE(zo.operator_count, 0) AS dispensary_count,
  CASE WHEN COALESCE(zo.operator_count, 0) = 0 THEN zp.total_population
       ELSE ROUND(zp.total_population::numeric / zo.operator_count, 0)
  END AS people_per_dispensary,
  -- Saturation: 100 = fully saturated, 0 = no competition
  LEAST(100, COALESCE(zo.operator_count, 0) * 100.0 / GREATEST(1, zp.total_population / 15000))::integer AS saturation_score,
  CASE
    WHEN COALESCE(zo.operator_count, 0) = 0 AND zp.total_population > 10000 THEN 'whitespace'
    WHEN COALESCE(zo.operator_count, 0) = 1 AND zp.total_population > 30000 THEN 'underserved'
    WHEN COALESCE(zo.operator_count, 0) >= 3 AND zp.total_population < 20000 THEN 'oversaturated'
    ELSE 'balanced'
  END AS market_status
FROM zip_pop zp
LEFT JOIN zip_operators zo ON zo.zip_code = zp.zip_code
WHERE zp.total_population > 5000;
```

### 3.4 Price Position Index

Where an operator sits relative to the statewide official benchmark.

```sql
-- price_position_vs_state = (operator_avg - state_avg) / state_avg × 100
-- Positive = above state average (premium), negative = below (budget)
-- price_position_label:
--   > +20%  → 'premium'
--   +5 to +20% → 'above_market'
--   -5 to +5% → 'competitive'
--   -20 to -5% → 'budget'
--   < -20% → 'undercut'
```

### 3.5 Growth Trajectory (0–100)

Uses price trend, product count trend, and review trend over 90 days.

```sql
-- Signals:
-- 1. Product count growing (adding inventory) = positive
-- 2. Price trending toward market (adjusting strategy) = positive
-- 3. Review count growing = positive
-- 4. No new prices in 14+ days (stale menu) = strongly negative
-- Score: 50 base, ±25 for each signal
```

### 3.6 Materialized View Refresh Schedule

```sql
-- Daily (6AM ET, after scraper runs)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_menu_thc_monthly;

-- Weekly (Sunday 3AM ET)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_lab_thc_monthly;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_market_gaps;

-- Monthly (1st of month, after CCC data import)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_weekly_market_revenue;
```

Operator scores recomputed via TypeScript job (`scripts/etl/compute-scores.ts`), not materialized views, because they need incremental updates.

---

## 4. Product Integration Matrix

### 4.1 GLASS ↔ Virtual Budtender

**Direction:** GLASS provides product catalog → VB consumes. VB provides demand signals → GLASS stores.

**Firestore Elimination Plan:**
1. GLASS catalog endpoint already has CH products from Dutchie scraping
2. VB backend switches from Firestore to GLASS API
3. VB logs queries back to GLASS (fire-and-forget)
4. Firebase Firestore project deleted

**GLASS → VB: Product Catalog API**

```typescript
// GET /api/v1/catalog/:operatorId/products
// Returns products with latest price for a specific operator
// Uses lateral join for most-recent-price-per-product

fastify.get('/catalog/:operatorId/products', {
  onRequest: [fastify.authenticateApiKey],
}, async (request, reply) => {
  const { operatorId } = request.params;
  const { category, inStock, limit = 300 } = request.query;

  const results = await db.execute(sql`
    SELECT
      p.id, p.sku, p.name, p.brand, p.category, p.weight_grams,
      p.strain_type, p.thc_percent, p.cbd_percent,
      lp.price AS latest_price, lp.price_per_gram,
      lp.availability, lp.promo_flag, lp.scraped_at AS last_seen_at,
      lp.raw_data AS metadata
    FROM products p
    INNER JOIN LATERAL (
      SELECT price, price_per_gram, availability, promo_flag, scraped_at, raw_data
      FROM prices WHERE prices.product_id = p.id AND prices.operator_id = ${operatorId}
      ORDER BY scraped_at DESC LIMIT 1
    ) lp ON true
    WHERE 1=1
      ${category ? sql`AND p.category = ${category}` : sql``}
      ${inStock ? sql`AND lp.availability IN ('in_stock', 'low_stock')` : sql``}
    ORDER BY p.name LIMIT ${limit}
  `);

  return { operator_id: operatorId, count: results.rows.length, items: results.rows };
});
```

**VB → GLASS: Query Logging**

```javascript
// virtual-budtender/backend/glassClient.js (new file)
const GLASS_API = process.env.GLASS_API_URL;
const GLASS_KEY = process.env.GLASS_API_KEY;

export async function logBudtenderQuery(sessionId, tenantId, queryData) {
  if (!GLASS_API) return; // graceful no-op
  try {
    await fetch(`${GLASS_API}/api/v1/budtender/queries`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Roviq-API-Key': GLASS_KEY },
      body: JSON.stringify({
        session_id: sessionId,
        tenant_id: tenantId,
        query_text: queryData.message,
        parsed_intent: queryData.answers || null,
        products_recommended: queryData.recommendedProductIds || [],
        response_time_ms: queryData.responseTimeMs,
      }),
    });
  } catch (err) {
    console.warn('GLASS query log failed (non-blocking):', err.message);
  }
}
```

### 4.2 GLASS ↔ Cue

**Direction:** GLASS market data → Cue mission targeting. Cue events → GLASS analytics.

**GLASS → Cue: Smart Mission Suggestions**

```
GET /api/v1/catalog/:operatorId/underperforming
→ "12 products priced 15%+ above market. Create sales missions."

GET /api/v1/demand/:operatorId
→ "47 edible queries this week, 32 under $30. Create edible-focused missions."
```

**Cue → GLASS: Ecosystem Events**

```typescript
// Cue backend fires on mission lifecycle events:
await glassClient.post('/ecosystem/events', {
  source_product: 'cue',
  event_type: 'mission_completed',  // or: mission_created, submission_approved, reward_redeemed
  operator_id: glassOperatorId,
  participant_id: participantId,
  payload: { mission_id, product_id, amount, ...metadata },
});
```

**GLASS Dashboard "Ecosystem" tab shows:**
- Brand spend heatmap
- Mission ROI (cost vs. sales lift)
- Budtender engagement scores
- Product push effectiveness

### 4.3 GLASS ↔ Delivered

**Direction:** GLASS provides product/market data. Delivery transaction data feeds back.

- Drivers can browse product catalog for training (GLASS API)
- Delivery completion data → Cue (driver submissions) → GLASS (ecosystem events)
- GLASS delivery channel intelligence (CCC market sales) validates delivery market size

### 4.4 Virtual Budtender ↔ Cue

**Direction:** VB demand signals inform Cue missions. VB widget usage can count as Cue missions.

- **Demand signals → missions:** If VB sees 47 edible queries/week, Cue creates "push edibles" mission
- **Recommendation missions:** Dispensary creates Cue mission "Recommend 10 products via VB → $15 bonus"
- **Verification:** Cue queries GLASS `budtender_queries` to verify recommendations objectively

**Shared product catalog:** Both VB and Cue reference GLASS products by UUID. No separate product tables needed in either system (Cue's products table adds `glass_product_id` for linkage).

### 4.5 Cue ↔ Delivered (Driver Program)

See [Section 8: CH Driver Program](#8-ch-driver-program) for full spec.

### 4.6 All Products → Newsletter

The newsletter auto-generates from GLASS data:

1. **The Number** — Official MA flower price: $X.XX/g (MoM, YoY change)
2. **Category Scoreboard** — Revenue by product category, what grew/shrank
3. **THC Inflation Report** — Lab avg vs. menu avg with trend line
4. **Delivery Watch** — Delivery market share + growth trajectory
5. **New Player Alert** — New license applications this month
6. **Enforcement Roundup** — Fines/suspensions
7. **Market Gap of the Week** — One underserved zip code with population data
8. **Price Leaderboard** — Top 5 cheapest/most expensive by category

```typescript
// Newsletter data package (auto-generated monthly)
interface NewsletterData {
  officialPrice: { current: number; momChange: number; yoyChange: number };
  categoryRevenue: Array<{ category: string; revenue: number; changePct: number }>;
  thcInflation: { labAvg: number; menuAvg: number; inflationPct: number };
  deliveryShare: { currentPct: number; growthPct: number };
  newApplications: { total: number; byType: Record<string, number> };
  enforcementActions: Array<{ business: string; action: string; amount: number }>;
  marketGap: { zipCode: string; town: string; population: number; dispensaries: number };
  priceLeaders: { cheapest: OperatorPrice[]; expensive: OperatorPrice[] };
}
```

### 4.7 All Products → SIGNAL (SEO)

Data-driven content generation at scale:

| Data Source | SEO Content |
|------------|-------------|
| Market Sales trends | "[City] Cannabis [Category] Trends [Year]" — auto-updated pages |
| Monthly Price | "Massachusetts Cannabis Prices [Month] [Year]" — authority page |
| Lab Tests | "Average THC Levels in Massachusetts Cannabis" — data-rich |
| Licensed Operators | Business listing enrichment with license data for E-E-A-T |
| Census + Market Gap | "Cannabis Dispensaries Near [Town], MA" — location pages |
| Strains | "[Strain] — Effects, THC Levels, Where to Buy in MA" |

**Content velocity:** 20 categories × 12 months + 500 strains + 300 towns + 12 price reports = **1,000+ auto-updating SEO pages/year**

---

## 5. API Design

### 5.1 Auth Tiers

| Tier | Mechanism | Used By |
|------|-----------|---------|
| **Public** | No auth, rate limited (100 req/min per IP) | Newsletter widgets, public data pages |
| **Authenticated** | Clerk JWT in `Authorization: Bearer` header | GLASS dashboard users |
| **Admin** | `X-Admin-Key` header matching `ADMIN_API_KEY` env var | Internal admin tools |
| **Service-to-Service** | `X-Roviq-API-Key` header, per-product keys | VB, Cue, Delivery backends |

```typescript
// Service-to-service auth plugin
const INTEGRATION_KEYS: Record<string, string> = {
  [process.env.VB_API_KEY!]: 'virtual-budtender',
  [process.env.CUE_API_KEY!]: 'cue',
  [process.env.DELIVERY_API_KEY!]: 'delivery',
};

fastify.decorate('authenticateApiKey', async (request) => {
  const apiKey = request.headers['x-roviq-api-key'] as string;
  if (!apiKey || !INTEGRATION_KEYS[apiKey]) {
    throw fastify.httpErrors.unauthorized('Invalid API key');
  }
  request.apiKeyProduct = INTEGRATION_KEYS[apiKey];
});
```

### 5.2 Complete Endpoint Catalog

#### Public Endpoints (no auth)

| Method | Path | Description | Cache |
|--------|------|-------------|-------|
| GET | `/api/v1/operators/search` | Search operators by name/city | 5 min |
| GET | `/api/v1/ccc/weekly-sales` | Statewide weekly sales aggregates | 1 hour |
| GET | `/api/v1/ccc/demographics` | Statewide demographics | 24 hours |
| GET | `/api/v1/ccc/cross-reference` | CCC vs scraped price comparison | 1 hour |
| GET | `/api/v1/ccc/price-benchmark` | Official monthly price per gram | 24 hours |
| GET | `/api/v1/ccc/price-benchmark/latest` | Latest month's price | 1 hour |
| GET | `/api/v1/ccc/lab-stats` | Aggregate lab testing statistics | 24 hours |
| GET | `/api/v1/ccc/delivery-share` | Delivery vs retail market share | 1 hour |
| GET | `/api/v1/ccc/licensed-operators/count` | License counts by type/status | 24 hours |
| POST | `/api/v1/waitlist` | Waitlist signup | — |
| POST | `/api/v1/newsletter/subscribe` | Newsletter signup | — |

#### Authenticated Endpoints (Clerk JWT)

| Method | Path | Description | Cache |
|--------|------|-------------|-------|
| GET | `/api/v1/dashboard` | Operator dashboard summary | 15 min |
| GET | `/api/v1/products` | Operator's product catalog | 15 min |
| GET | `/api/v1/prices/history` | Price history for products | 15 min |
| GET | `/api/v1/threats` | Threat radar for operator | 15 min |
| GET | `/api/v1/recommendations` | Price recommendations | 15 min |
| GET | `/api/v1/alerts` | Alerts feed | 5 min |
| GET | `/api/v1/intelligence/thc-accuracy` | THC inflation: lab vs menu | 1 hour |
| GET | `/api/v1/intelligence/thc-accuracy/:operatorId` | Per-operator THC accuracy | 1 hour |
| GET | `/api/v1/intelligence/market-gap` | Underserved zip code analysis | 24 hours |
| GET | `/api/v1/intelligence/revenue-cross-ref` | CCC vs scraped price comparison | 1 hour |
| GET | `/api/v1/intelligence/health-score/:operatorId` | Operator health score breakdown | 1 hour |
| GET | `/api/v1/intelligence/health-score/leaderboard` | Top/bottom operators | 1 hour |
| GET | `/api/v1/intelligence/category-trends` | Product category revenue trends | 1 hour |
| GET | `/api/v1/intelligence/delivery-growth` | Delivery channel growth metrics | 1 hour |
| GET | `/api/v1/threats/detect/:operatorId` | Full threat radar scan | 15 min |
| GET | `/api/v1/ccc/operators/search` | Search CCC licensed operators | 5 min |
| GET | `/api/v1/ccc/operators/:licenseNumber` | Full CCC operator profile | 1 hour |
| GET | `/api/v1/reviews/:operatorId` | Google reviews for operator | 1 hour |
| GET | `/api/v1/demographics/:zipCode` | Census data for zip code | 24 hours |
| GET | `/api/v1/strains/search` | Search strain database | 24 hours |
| GET | `/api/v1/demand/:operatorId` | Aggregated demand signals | 1 hour |

#### Admin Endpoints (ADMIN_API_KEY)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/admin/import/lab-tests` | Trigger lab test import |
| POST | `/api/v1/admin/import/market-sales` | Trigger market sales import |
| POST | `/api/v1/admin/import/licenses` | Trigger CCC license import |
| POST | `/api/v1/admin/match-operators` | Run operator matching algorithm |
| POST | `/api/v1/admin/refresh-views` | Refresh all materialized views |
| POST | `/api/v1/admin/compute-scores` | Recompute all operator scores |
| GET | `/api/v1/admin/import-status` | Status of last imports |
| GET | `/api/v1/admin/match-report` | Operator matching stats |
| GET | `/api/v1/admin/data-quality` | Data quality dashboard |
| GET | `/api/v1/admin/waitlist/stats` | Waitlist statistics |

#### Service-to-Service Endpoints (X-Roviq-API-Key)

| Method | Path | Consumer | Description |
|--------|------|----------|-------------|
| GET | `/api/v1/catalog/:operatorId/products` | VB, Cue | Live product catalog for operator |
| GET | `/api/v1/catalog/:operatorId/underperforming` | Cue | Products priced 15%+ above market |
| POST | `/api/v1/ecosystem/events` | Cue, VB, Delivery | Ingest cross-product events |
| POST | `/api/v1/budtender/sessions` | VB | Create/update VB session |
| POST | `/api/v1/budtender/queries` | VB | Log VB query + recommendations |
| GET | `/api/v1/demand/:operatorId` | Cue | Aggregated demand signals |

### 5.3 Caching Strategy

```typescript
// Layer 1: HTTP Cache-Control headers
const CACHE = {
  public_static: 'public, max-age=86400, s-maxage=86400',   // 24h
  public_aggregate: 'public, max-age=3600, s-maxage=3600',  // 1h
  authenticated: 'private, max-age=900',                     // 15min
  realtime: 'private, no-cache',                             // no cache
};

// Layer 2: In-memory LRU cache (Node process level)
import { LRUCache } from 'lru-cache';
const queryCache = new LRUCache<string, any>({
  max: 500,
  ttl: 1000 * 60 * 15,  // 15 min
  maxSize: 50 * 1024 * 1024,  // 50MB
  sizeCalculation: (value) => JSON.stringify(value).length,
});

// Layer 3: Materialized views (database level) — refreshed on schedule
// Layer 4: Future — Redis when multi-instance
```

### 5.4 Rate Limiting

| Tier | Limit | Window |
|------|-------|--------|
| Public (unauthenticated) | 100 req | 1 min per IP |
| Authenticated (Clerk JWT) | 1000 req | 1 min per user |
| Service-to-Service | 1000 req | 1 min per API key |
| Admin | 100 req | 1 min per key |

---

## 6. ETL & Data Pipeline

### 6.1 Architecture

```
┌─────────────────┐     ┌────────────────────┐     ┌─────────────────┐
│ CCC CSV Files    │     │  ETL Runner (TS)   │     │ PostgreSQL      │
│ (ccc-raw/*.csv)  │────▶│                    │────▶│ (Railway)       │
│                  │     │ 1. Parse CSV       │     │                 │
│ • testing.csv    │     │ 2. Clean/Validate  │     │ • ccc_lab_tests │
│ • sales.csv      │     │ 3. Hash for dedup  │     │ • ccc_fac_sales │
│ • medical.csv    │     │ 4. Upsert to DB    │     │ • ccc_licenses  │
│ • prices.csv     │     │ 5. Log to etl_runs │     │ • etl_runs      │
│ • commence.csv   │     │                    │     │                 │
│ • counties.csv   │     └────────┬───────────┘     └────────┬────────┘
└─────────────────┘              │                           │
                                  ▼                           ▼
                        ┌────────────────┐         ┌─────────────────┐
                        │ Operator Match │         │ Score Compute   │
                        │ (3-tier)       │         │ (post-ETL job)  │
                        └────────────────┘         └─────────────────┘
```

### 6.2 Shared ETL Infrastructure

File: `scripts/etl/lib/etl-base.ts`

```typescript
import { Pool } from 'pg';
import { createReadStream } from 'fs';
import { createHash } from 'crypto';
import * as csv from 'csv-parse';

const DATABASE_URL = process.env.DATABASE_URL
  ?? 'postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway';

export const pool = new Pool({ connectionString: DATABASE_URL, max: 10 });

// File hash for change detection
export async function fileHash(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const hash = createHash('sha256');
    createReadStream(filePath)
      .on('data', (chunk) => hash.update(chunk))
      .on('end', () => resolve(hash.digest('hex')))
      .on('error', reject);
  });
}

// Check if already imported
export async function isAlreadyImported(dataset: string, hash: string): Promise<boolean> {
  const r = await pool.query(
    `SELECT id FROM etl_runs WHERE dataset=$1 AND source_hash=$2 AND status='completed'`, [dataset, hash]
  );
  return r.rows.length > 0;
}

// Start/complete/fail ETL run
export async function startEtlRun(dataset: string, file: string, hash: string): Promise<string> {
  const r = await pool.query(
    `INSERT INTO etl_runs (dataset, source_file, source_hash) VALUES ($1,$2,$3) RETURNING id`,
    [dataset, file, hash]
  );
  return r.rows[0].id;
}

export async function completeEtlRun(runId: string, stats: Record<string, number>, errors: any[] = []) {
  await pool.query(
    `UPDATE etl_runs SET status='completed', completed_at=NOW(),
     rows_read=$2, rows_inserted=$3, rows_updated=$4, rows_skipped=$5, rows_errored=$6, error_log=$7
     WHERE id=$1`,
    [runId, stats.rows_read, stats.rows_inserted, stats.rows_updated, stats.rows_skipped, stats.rows_errored, JSON.stringify(errors)]
  );
}

// Parse CCC's verbose date format
export function parseCccDate(dateStr: string | null): Date | null {
  if (!dateStr?.trim()) return null;
  const s = dateStr.trim();
  if (/^\d{4}-\d{2}(-\d{2})?$/.test(s)) return new Date(s + (s.length === 7 ? '-01' : '') + 'T00:00:00Z');
  if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(s)) {
    const [m, d, y] = s.split('/');
    return new Date(`${y}-${m.padStart(2,'0')}-${d.padStart(2,'0')}T00:00:00Z`);
  }
  if (s.includes('GMT')) {
    const cleaned = s.replace(/\s*\([^)]*\)\s*$/, '');
    const d = new Date(cleaned);
    if (!isNaN(d.getTime())) return d;
  }
  const d = new Date(s);
  return isNaN(d.getTime()) ? null : d;
}

// Business name normalization for matching
export function normalizeBusinessName(name: string): string {
  return name
    .replace(/^"|"$/g, '')
    .replace(/,?\s*(INC\.?|LLC\.?|LTD\.?|CORP\.?)\s*$/i, '')
    .replace(/\s+D\/B\/A\s+.*/i, '')
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}
```

### 6.3 Import Strategy Per Dataset

| Dataset | Script | Rows | Import Strategy | Dedup Key |
|---------|--------|------|-----------------|-----------|
| Lab Tests | `import-lab-tests.ts` | 298K → 149K | Streaming CSV, pivot THC+THCA per METRC tag, batch upsert with `unnest` | `metrc_tag` |
| Facility Sales (AU) | `import-facility-sales.ts` | 67K | Streaming CSV, upsert. Skip $0 rows. | `(sale_date, market_type, delivery_type, product_category, unit_of_measure)` |
| ITD Sales | same script | 67K | Same schema, ON CONFLICT uses `GREATEST` for totals | same |
| Medical Sales | same script | 47K | `market_type='medical'`, `delivery_type='Medical'` | same |
| Monthly Prices | `import-monthly-prices.ts` | 71 | Direct upsert, compute MoM/YoY in-memory | `year_month` |
| Licenses (commence) | `import-licenses.ts` | 772 | Phase 1: upsert commence-ops | `license_number` |
| Licenses (counties) | same script | 1,753 | Phase 2: merge counties with COALESCE | same |
| Operator Match | same script | — | Phase 3: link licenses → operators (3-tier) | — |
| County Metrics | same script | — | Phase 4: aggregate from licenses | `(county, snapshot_date)` |

### 6.4 Operator Name Matching — 3-Tier Strategy

This is the most critical ETL step. Links CCC `business_name` to GLASS `operators.name`.

```sql
-- Tier 1: License number match (highest confidence)
UPDATE ccc_licenses l SET operator_id = o.id
FROM operators o WHERE o.license_number = l.license_number AND l.operator_id IS NULL;

-- Tier 2: Fuzzy name match with city filter (requires pg_trgm)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- Match where similarity > 0.3 AND same city, pick highest similarity
UPDATE ccc_licenses l SET operator_id = bm.operator_id
FROM (
  SELECT DISTINCT ON (ul.id)
    ul.id AS license_id, o.id AS operator_id,
    similarity(lower(regexp_replace(ul.business_name, '[^a-zA-Z0-9 ]', '', 'g')),
               lower(regexp_replace(o.name, '[^a-zA-Z0-9 ]', '', 'g'))) AS sim
  FROM ccc_licenses ul CROSS JOIN operators o
  WHERE lower(ul.establishment_city) = lower(o.city)
    AND similarity(lower(regexp_replace(ul.business_name, '[^a-zA-Z0-9 ]', '', 'g')),
                   lower(regexp_replace(o.name, '[^a-zA-Z0-9 ]', '', 'g'))) > 0.3
    AND ul.operator_id IS NULL AND ul.license_type = 'Marijuana Retailer'
  ORDER BY ul.id, sim DESC
) bm WHERE l.id = bm.license_id;

-- Tier 3: Geo-proximity (< 500 feet) for remaining unmatched
UPDATE ccc_licenses l SET operator_id = gm.operator_id
FROM (
  SELECT DISTINCT ON (ul.id)
    ul.id AS license_id, o.id AS operator_id,
    (3959 * acos(cos(radians(ul.latitude)) * cos(radians(o.lat::numeric)) *
     cos(radians(o.lon::numeric) - radians(ul.longitude)) +
     sin(radians(ul.latitude)) * sin(radians(o.lat::numeric)))) AS dist_mi
  FROM ccc_licenses ul CROSS JOIN operators o
  WHERE ul.operator_id IS NULL AND ul.license_type = 'Marijuana Retailer'
    AND ul.latitude IS NOT NULL AND o.lat IS NOT NULL
    AND ABS(ul.latitude - o.lat::numeric) < 0.01
  ORDER BY ul.id, dist_mi
) gm WHERE l.id = gm.license_id AND gm.dist_mi < 0.1;

-- Create operators from unmatched CCC licenses
INSERT INTO operators (name, license_number, city, state, lat, lon, status, email, phone, license_type, county, region)
SELECT business_name, license_number, COALESCE(establishment_city, business_city), 'MA',
  latitude, longitude,
  CASE WHEN license_stage = 'COMMENCE OPS' THEN 'active' ELSE 'pending' END,
  business_email, business_phone, license_type, county, region
FROM ccc_licenses
WHERE operator_id IS NULL AND establishment_city IS NOT NULL
ON CONFLICT DO NOTHING;
```

**Expected match rates:** ~450/492 existing operators matched (91%). ~280 CCC-only operators (cultivators, manufacturers, labs) created as new operators.

### 6.5 Update Frequency

| Dataset | Cadence | Trigger |
|---------|---------|---------|
| CCC CSV reimport | 1st of each month, 2AM ET | Cron or manual |
| Lab tests | Quarterly (when CCC updates) | Manual |
| Scraper (Dutchie) | Daily 3AM ET | Cron (CamoFox) |
| Scraper (Weedmaps) | Daily 10PM ET | Cron (Railway roviq-browser) |
| Google Reviews | Weekly (Sunday 2AM ET) | Cron |
| Census | Annually (December) | Manual |
| Enforcement | Weekly (Monday 8AM ET) | Scraper cron |
| Operator scores | Daily (6AM ET, after scrapers) | Post-scraper job |
| Materialized views | Daily/Weekly (see 3.6) | pg_cron or app cron |
| Demand signal aggregation | Nightly (1AM ET) | Cron |

### 6.6 Master ETL Runner

```typescript
// scripts/etl/run-all.ts
const SCRIPTS = [
  'import-monthly-prices.ts',  // 71 rows, fast
  'import-licenses.ts',        // 772+1753 rows, includes operator matching + county metrics
  'import-lab-tests.ts',       // 298K rows, ~3 min
  'import-facility-sales.ts',  // 182K rows, ~2 min
];
// After all imports: compute-scores.ts, refresh-views.ts
```

---

## 7. Unified Auth Strategy

### 7.1 Current Auth Landscape

| Product | Auth System | Users |
|---------|-------------|-------|
| GLASS | Clerk (JWT, email/password) | Dispensary operators, admins |
| Cue | Firebase Phone Auth (OTP) | Budtenders (mobile), Brand admins (dashboard) |
| Virtual Budtender | None | Anonymous customers |
| Delivery | TBD | Customers, drivers |

### 7.2 Strategy: Clerk as Primary, Firebase as Secondary

**Do NOT rip out Firebase Phone Auth from Cue.** Phone OTP is the right UX for budtenders/drivers on mobile.

```
┌─────────────────────────────────────────────────────┐
│                   UNIFIED AUTH                       │
│                                                      │
│  ┌──────────────┐                                    │
│  │ Clerk         │── GLASS Dashboard (existing)      │
│  │ (Email/Pass)  │── Cue Admin Dashboard (NEW)       │
│  │ Admin accounts │── VB Config Panel (NEW)           │
│  └──────────────┘                                    │
│                                                      │
│  ┌──────────────┐                                    │
│  │ Firebase      │── Cue Mobile App (existing)       │
│  │ Phone Auth    │── Delivery Driver App (FUTURE)    │
│  │ Field workers │                                   │
│  └──────────────┘                                    │
│                                                      │
│  ┌──────────────┐                                    │
│  │ Anonymous     │── Virtual Budtender Widget         │
│  │ (Session ID)  │── Delivery Customer App (FUTURE)  │
│  └──────────────┘                                    │
└─────────────────────────────────────────────────────┘
```

### 7.3 Implementation

**Cue backend: Accept both Clerk (admin) and Firebase (mobile):**

```typescript
// server/src/middleware/auth.ts
async function authenticate(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'No token' });

  try {
    // Try Clerk JWT first (admin dashboard)
    const clerkPayload = await verifyClerkJWT(token);
    req.user = { id: clerkPayload.sub, source: 'clerk', role: clerkPayload.metadata?.cue_role || 'admin' };
    return next();
  } catch {
    try {
      // Fall back to Firebase JWT (mobile app)
      const firebasePayload = await verifyFirebaseToken(token);
      req.user = { id: firebasePayload.uid, source: 'firebase', role: 'participant' };
      return next();
    } catch {
      return res.status(401).json({ error: 'Invalid token' });
    }
  }
}
```

**Clerk ↔ Cue mapping:** `admin_auth_mappings` table links Clerk user IDs to Cue user IDs.

**Service-to-service:** API key based (`X-Roviq-API-Key`). Each product gets its own key via env vars. Simpler than OAuth2 client credentials for a 4-product ecosystem.

**SSO path for dispensary admins:** One Clerk account → GLASS dashboard + Cue admin + VB config panel. Clerk instance: `humane-dinosaur-0.clerk.accounts.dev`.

---

## 8. CH Driver Program

### 8.1 Overview

Cannabis Healing wants driver incentives. Drivers can't receive cannabis (legal). Cue's Tremendous API integration enables gift card payouts.

- **Participants:** 3–8 delivery drivers
- **Verification:** Manual (V1) — driver submits proof, Brian (CH admin) approves
- **Payout:** Gift cards via Tremendous (Visa, Amazon, DoorDash, etc.)

### 8.2 Mission Types

| Type | Target | Reward | Period |
|------|--------|--------|--------|
| **Delivery Count** | 20+ deliveries | $25 gift card | Weekly |
| **Rating Threshold** | 4.5+ rating, 15+ deliveries | $15 gift card | Weekly |
| **Upsell Commission** | Pre-roll upsells | $2/unit, max $50 | Weekly |
| **Driver of the Month** | Top 3 by delivery count | $100/$50/$25 | Monthly |

### 8.3 Submission Flow

```
Driver completes deliveries
    → Opens Cue mobile app
    → Taps mission → Enters delivery count + rating
    → Uploads screenshot proof
    → Submits

CH Admin (Brian) reviews
    → Checks delivery count in Blaze POS / internal records
    → Verifies rating
    → Approves or rejects

Tremendous API sends gift card email to driver
    → Event logged to GLASS ecosystem_events
```

### 8.4 Verification Ladder

- **V1 (Now):** Manual self-report + admin approval. Good enough for 3–8 drivers.
- **V2 (If CH uses Dutchie Delivery):** Scrape delivery stats or CSV export → bulk verification.
- **V3 (If Delivered deal closes):** Blaze POS webhooks → zero manual intervention.

### 8.5 Cost Estimate

| Item | Monthly |
|------|---------|
| 5 drivers × $25/week avg gift cards | $500 |
| Tremendous fee (2.5%) | $12.50 |
| Cue platform fee (waived for beta) | $0 |
| **Total** | **~$512/mo** |

**ROI:** 10% delivery increase = 40 extra deliveries/month × $60 avg order = $2,400 incremental revenue. **4.7x ROI.**

### 8.6 Launch Checklist

```
□ Cue deployed to production (Neon DB + Railway API)
□ participants table migration run
□ delivery_submissions table created
□ Driver mission types configured
□ CH dispensary created in Cue
□ 3–8 driver phone numbers registered
□ Driver onboarding walkthrough
□ Brian trained on approval queue
□ Tremendous switched from testflight to production
□ Funding source loaded ($500 initial)
□ First test submission → approved → gift card received
□ Go live
```

---

## 9. Implementation Roadmap

### Phase 1: This Week (Feb 12–19) — Wire the Data

**Goal:** GLASS feeds live products to VB. Firestore eliminated. CCC data imported.

| # | Task | Repo | Files | Hours | Depends On |
|---|------|------|-------|-------|------------|
| 1.1 | Build GLASS catalog API endpoint | glass | `routes/budtender-api.ts` | 4h | — |
| 1.2 | Build API key auth plugin | glass | `plugins/api-key-auth.ts` | 2h | — |
| 1.3 | Map CH operator in GLASS DB | GLASS DB (SQL) | — | 0.5h | 1.1 |
| 1.4 | Switch VB from Firestore to GLASS API | virtual-budtender | `backend/server.js`, `backend/glassClient.js` | 4h | 1.1, 1.2, 1.3 |
| 1.5 | Test VB with GLASS data | Manual QA | — | 2h | 1.4 |
| 1.6 | Run DB migration (all new CCC tables) | glass | `scripts/migrations/006-ccc-data-integration.sql` | 2h | — |
| 1.7 | Build ETL base library | glass | `scripts/etl/lib/etl-base.ts` | 3h | — |
| 1.8 | Import all CCC CSVs (lab tests, sales, prices, licenses) | glass | `scripts/etl/import-*.ts` | 6h | 1.6, 1.7 |
| 1.9 | Run operator matching (3-tier) | glass | `scripts/etl/import-licenses.ts` | 2h | 1.8 |
| 1.10 | Deploy updated GLASS API + VB | Railway | — | 2h | 1.1–1.5 |

**Phase 1 total: ~27.5 hours**

**Deliverables:**
- VB pulls live products from GLASS (no more Firestore)
- All CCC data imported (149K lab tests, 182K sales, 71 price months, 1753 licenses)
- Operators matched to CCC licenses

### Phase 2: Two Weeks (Feb 19 – Mar 5) — Core Integrations

**Goal:** CH driver program live. VB query logging. Cue ↔ GLASS sync. First intelligence endpoints.

| # | Task | Repo | Hours | Depends On |
|---|------|------|-------|------------|
| 2.1 | Add `participants` table to Cue | Cue | 6h | — |
| 2.2 | Add driver mission types to Cue | Cue | 8h | 2.1 |
| 2.3 | Build driver submission flow (mobile) | Cue | 8h | 2.2 |
| 2.4 | Build CH driver admin config | Cue | 6h | 2.2 |
| 2.5 | Verify Tremendous for driver gift cards | Cue | 2h | 2.1 |
| 2.6 | Add integration tables to GLASS (sessions, queries, events) | GLASS | 3h | — |
| 2.7 | Build ecosystem event ingestion endpoint | GLASS | 4h | 2.6 |
| 2.8 | Add VB query logging (fire-and-forget) | VB | 3h | 2.6, 2.7 |
| 2.9 | Add `glass_product_id` to Cue products | Cue | 1h | — |
| 2.10 | Build Cue → GLASS product sync | Cue | 4h | 2.9 |
| 2.11 | Deploy Cue MVP (first deploy) | Neon + Railway | 8h | 2.1–2.5 |
| 2.12 | Set up CH as first Cue customer | Cue admin | 2h | 2.11 |
| 2.13 | Build THC accuracy endpoint | GLASS | 4h | Phase 1 |
| 2.14 | Build health score computation job | GLASS | 6h | Phase 1 |
| 2.15 | Create materialized views | GLASS | 3h | Phase 1 |

**Phase 2 total: ~68 hours (~2 developer-weeks)**

**Deliverables:**
- CH driver incentive program LIVE
- VB query data flowing into GLASS
- Cue products linked to GLASS catalog
- THC accuracy + health scores operational
- Cue deployed for first time

### Phase 3: One Month (Mar 5 – Apr 5) — Full Ecosystem Flywheel

| # | Task | Repo | Hours | Depends On |
|---|------|------|-------|------------|
| 3.1 | GLASS "Demand Intelligence" dashboard widget | GLASS web | 8h | 2.6, 2.8 |
| 3.2 | GLASS "Ecosystem" analytics tab | GLASS web | 12h | 2.7 |
| 3.3 | Demand signal aggregation cron job | GLASS | 4h | 2.6 |
| 3.4 | "Smart Mission Suggestions" in Cue admin | Cue | 8h | 1.1 |
| 3.5 | Switch Cue admin auth to Clerk | Cue | 12h | — |
| 3.6 | VB config panel (Clerk-authed) | VB or GLASS | 16h | 3.5 |
| 3.7 | Conversion tracking (click-through) in VB | VB + GLASS | 4h | 2.6 |
| 3.8 | Underperforming products endpoint | GLASS | 4h | — |
| 3.9 | Second VB tenant (non-CH) | VB config | 4h | Phase 1 |
| 3.10 | Google Reviews scraper | GLASS | 8h | — |
| 3.11 | Census data import | GLASS | 4h | — |
| 3.12 | Market gap analysis endpoint | GLASS | 4h | 3.11 |
| 3.13 | Cue → GLASS event reporting | Cue | 4h | 2.7 |
| 3.14 | Customer loyalty participant type | Cue | 12h | 2.1 |
| 3.15 | Delivery app wireframes + Blaze API spike | Design | 16h | — |

**Phase 3 total: ~120 hours (~3 developer-weeks)**

**Deliverables:**
- GLASS shows demand intelligence + ecosystem analytics
- Cue admin suggests missions from GLASS data
- Unified Clerk auth for admin dashboards
- Google Reviews + Census data integrated
- Market gap analysis live
- Second VB tenant proves multi-tenant

### Phase 4: Three Months (Apr 5 – Jul 5) — Scale & Optimize

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 4.1 | Delivery customer app (React Native + Blaze) | 200h | High (if Delivered closes) |
| 4.2 | Driver app ↔ Cue auto tracking | 40h | High |
| 4.3 | VB → Cue auto mission verification | 20h | Medium |
| 4.4 | Brand Ambassador participant type | 30h | Medium |
| 4.5 | Customer loyalty with receipt scanning | 60h | Medium |
| 4.6 | GLASS ML pricing model | 80h | Medium |
| 4.7 | GLASS → Newsletter automation | 20h | Low |
| 4.8 | SIGNAL auto-generate SEO pages from data | 40h | Medium |
| 4.9 | Real-time pricing alerts (push) | 30h | Medium |
| 4.10 | Enforcement action scraper | 8h | Low |
| 4.11 | Strain database (Otreeba) import | 8h | Low |
| 4.12 | Predictive analytics (price forecasting, churn) | 60h | Low |

**The flywheel at scale:**
```
GLASS scrapes prices → informs Cue mission targeting
  → budtenders/drivers earn from missions
    → VB captures demand signals from customers
      → GLASS shows demand intelligence
        → operators adjust pricing
          → GLASS scrapes new prices → cycle repeats
```

---

## 10. Risk Assessment

### 10.1 Data Quality Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| CCC anonymized strain names (`Strain_01`) | Can't match lab tests to specific products | Use category-level statistical analysis instead. THC accuracy is market-wide, not per-product. |
| Market sales are statewide aggregates, not per-facility | Can't calculate individual operator revenue | Revenue intel is market-level. Combine with scraped prices for relative positioning. |
| Operator matching false positives | Wrong CCC data linked to wrong operator | 3-tier algorithm (license → name → geo). Manual review for geo matches. Admin validation report. |
| CCC data refresh lag (monthly/quarterly) | Data staleness | Display "data as of" dates. Accept quarterly for lab tests. Monthly for sales/licenses. |
| Dutchie/Weedmaps menu data inconsistency | THC% listed differently across platforms | Normalize at scrape time. Cross-reference between platforms. Confidence scoring. |

### 10.2 Privacy/Legal Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Business email/phone from CCC data | Potential cold outreach legal exposure | CCC data is public record. Use for matching only, not mass outreach. CAN-SPAM compliance for any email. |
| Enforcement action data | Could be seen as competitive intelligence weaponization | Present as "industry compliance insights" not "competitor shaming." Show anonymized unless operator opts in. |
| Google Reviews scraping | TOS violation risk | Use official Google Places API (free tier sufficient). Don't scrape — use API. |
| Individual review storage | GDPR-adjacent concerns | Store aggregate stats always. Individual reviews optional. Allow operators to request removal of their review data. |

### 10.3 Performance Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| 149K lab test rows + 182K sales rows | Slow queries on Railway | Proper indexes (already defined). Materialized views for cross-references. No partitioning needed until 2M+ rows. |
| Lateral join for catalog endpoint | Could be slow at 100K+ products per operator | Limit to 300-500 products per request. Add covering index on `(product_id, operator_id, scraped_at DESC)`. |
| Concurrent scraper + API on same Railway PG | Resource contention | Scraper runs at 3AM/10PM ET (off-peak). `max: 10` connection pool. Monitor Railway metrics. |
| LRU cache memory usage | Node OOM on Railway | Cap at 50MB (`maxSize`). TTL of 15 min. Monitor memory in Railway dashboard. |

### 10.4 Architectural Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hub-and-spoke latency (cross-product API calls) | VB adds ~50-100ms for GLASS API call | Cache products locally in VB (5 min TTL). Fire-and-forget for logging. Product reads are non-blocking. |
| Single Railway PG as single point of failure | All products affected if Railway goes down | Railway has built-in backups. Cue on Neon is independent. VB degrades gracefully (shows cached products). Add Railway replica for reads (Phase 4). |
| API key rotation complexity | Downtime during rotation | Rotate one key at a time. Support 2 active keys per product during transition. Store in env vars, not code. |
| Cue first deploy complexity | Unknown unknowns | Budget 8h for deploy. Test on staging first. Start with CH only (3-8 drivers). |

---

## Appendix A: Environment Variables

### GLASS API (Railway)
```bash
VB_API_KEY=<generate-uuid>
CUE_API_KEY=<generate-uuid>
DELIVERY_API_KEY=<generate-uuid>
# Existing: DATABASE_URL, CLERK_*, ADMIN_API_KEY, CORS_ORIGIN
```

### Virtual Budtender
```bash
GLASS_API_URL=https://glass-api-production.up.railway.app
GLASS_API_KEY=<VB_API_KEY>
```

### Cue
```bash
GLASS_API_URL=https://glass-api-production.up.railway.app
GLASS_API_KEY=<CUE_API_KEY>
CLERK_PUBLISHABLE_KEY=<from GLASS Clerk instance>
CLERK_SECRET_KEY=<from GLASS Clerk instance>
TREMENDOUS_API_KEY=<production key>
TREMENDOUS_FUNDING_SOURCE=<funding source id>
```

## Appendix B: Repository Change Summary

| Repo | Files | Phase |
|------|-------|-------|
| `Roviq-AI/glass.git` | `services/api/src/routes/budtender-api.ts` (NEW) | 1 |
| `Roviq-AI/glass.git` | `services/api/src/routes/ecosystem.ts` (NEW) | 2 |
| `Roviq-AI/glass.git` | `services/api/src/routes/demand.ts` (NEW) | 2 |
| `Roviq-AI/glass.git` | `services/api/src/routes/intelligence.ts` (NEW) | 2 |
| `Roviq-AI/glass.git` | `services/api/src/plugins/api-key-auth.ts` (NEW) | 1 |
| `Roviq-AI/glass.git` | `services/api/src/db/schema.ts` (ADD 17 tables) | 1 |
| `Roviq-AI/glass.git` | `scripts/migrations/006-ccc-data-integration.sql` (NEW) | 1 |
| `Roviq-AI/glass.git` | `scripts/etl/*.ts` (NEW, 6 files) | 1 |
| `randytorres/virtual-budtender` | `backend/glassClient.js` (NEW) | 1 |
| `randytorres/virtual-budtender` | `backend/server.js` (MODIFY — replace Firestore) | 1 |
| `randytorres/virtual-budtender` | `backend/tenantConfig.js` (ADD glassOperatorId) | 1 |
| `randytorres/BudtenderIncentiveAI` | `server/db/schema.ts` (ADD participants, delivery_submissions) | 2 |
| `randytorres/BudtenderIncentiveAI` | `server/src/middleware/auth.ts` (MODIFY — dual auth) | 3 |
| `randytorres/BudtenderIncentiveAI` | `server/src/services/glassIntegration.ts` (NEW) | 2 |
| `randytorres/BudtenderIncentiveAI` | `mobile/src/screens/DriverSubmissionScreen.tsx` (NEW) | 2 |
| `randytorres/BudtenderIncentiveAI` | `admin/src/components/MissionSuggestions.tsx` (NEW) | 3 |

## Appendix C: Key Decisions Log

| Decision | Rationale | Alternative Rejected |
|----------|-----------|---------------------|
| Hub-and-spoke, not monolith | Each product has different deploy cadence, auth, team | Full merge into Railway PG |
| Eliminate Firestore | 300 products vs GLASS 100K+. Unnecessary cost/complexity | Keep as cache layer |
| Keep Firebase Phone Auth for mobile | Phone OTP is right UX for budtenders/drivers. Clerk phone auth less mature | Migrate everything to Clerk |
| API key for service-to-service | Simpler than OAuth2 for 4-product ecosystem | JWT service tokens |
| Pivoted lab tests (1 row per tag) | More efficient, easier THC calc | 2 rows per tag (Opus plan) |
| Merged license table (not 2 separate) | Same license_number key. COALESCE enrichment | Separate commence-ops + counties tables |
| Operator scores as table (not mat view) | Allows incremental recompute, versioning | Pure materialized view |
| Manual driver submission V1 | No POS integration at CH. 3-8 drivers = manual works | Wait for Blaze API |
| `participants` generalization | One table for all types, JSONB metadata for type-specific | Separate tables per type |
| Demand signals as nightly batch | Daily/weekly mission targeting doesn't need real-time | Real-time streaming |
| No partitioning (yet) | 360K rows with indexes = sub-10ms queries. Trigger at 2M | Premature partitioning |

---

*This is THE document the team builds from. All implementation references this plan. Update as decisions change.*

**Total estimated effort:**
- Phase 1: ~27.5h (1 week)
- Phase 2: ~68h (2 weeks)
- Phase 3: ~120h (1 month)
- Phase 4: ~596h (3 months, includes delivery app)

**Total infrastructure cost increase:** ~$5-10/mo (storage, negligible compute for batch imports)

**Revenue impact:** This data transforms GLASS from a $49/mo price tool into a $149-299/mo intelligence platform. At 50 subscribers, that's the difference between $2,450/mo and $14,950/mo ARR. Combined with Cue ($199/mo × 20 operators) and VB ($99-299/mo × 15 operators), the ecosystem targets $30-50K MRR within 6 months.
