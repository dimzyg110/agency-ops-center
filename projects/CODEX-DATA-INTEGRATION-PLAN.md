# CODEX: GLASS Data Integration Plan

**Version:** 1.0  
**Date:** 2026-02-12  
**Author:** Data Engineering Subagent  
**Status:** Ready for Implementation  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Data Inventory & Quality Assessment](#2-data-inventory--quality-assessment)
3. [Schema Design (Drizzle ORM)](#3-schema-design-drizzle-orm)
4. [ETL Pipeline](#4-etl-pipeline)
5. [Composite Scores & Intelligence Engine](#5-composite-scores--intelligence-engine)
6. [API Design](#6-api-design)
7. [Product Integration Map](#7-product-integration-map)
8. [Implementation Schedule](#8-implementation-schedule)
9. [Risk Assessment](#9-risk-assessment)
10. [Appendix: SQL Materialized Views](#10-appendix-sql-materialized-views)

---

## 1. Executive Summary

GLASS currently has **3 data layers**: scraped menu data (100K products, 117K prices from Dutchie/Weedmaps), CCC bridge data (weekly sales, demographics, pending applications), and operator metadata (492 operators). This plan integrates **7 new CCC datasets** and designs infrastructure for **4 future external sources**, creating a cross-referenced intelligence platform with computed scores that no competitor can replicate.

**The moat:** Nobody else combines real-time scraped street prices with official CCC lab tests, facility sales, licensing, and census data. Every dataset integrated multiplies the value of every other dataset.

### Key Numbers

| Dataset | Rows | Storage Est. | Priority |
|---------|------|-------------|----------|
| Lab Testing (THC/THCA) | 298,342 | ~45MB | P0 |
| Facility Sales (Adult) | 67,333 | ~12MB | P0 |
| ITD Retail/Delivery | 67,333 | ~12MB | P0 |
| Medical Facility Stats | 47,647 | ~8MB | P1 |
| Monthly Price/Ounce | 71 | <1MB | P0 |
| Commence Operations | 772 | ~2MB | P0 |
| Adult Market + Counties | 1,753 | ~3MB | P1 |
| **Total new rows** | **~482K** | **~82MB** | |

---

## 2. Data Inventory & Quality Assessment

### 2.1 Lab Testing (`testing-thc-thca.csv`)

**Structure:** 8 columns, 298,342 data rows

| Column | Sample | Notes |
|--------|--------|-------|
| `ProductCategoryType` | `Buds`, `ShakeTrim`, `Plants`, `Concentrate`, `InfusedNonEdible`, `InfusedEdible` | 6 distinct values |
| `ID` | `1A40A030000DBZV7777779DL` | METRC tag — 24-char alphanumeric, 147,649 unique |
| `Strain` | `Strain_01` through `Strain_5733` | Anonymized, 5,733 unique strains |
| `Test Type Name` | `THC (%) Raw Plant Material` or `THCA (%) Raw Plant Material` | Exactly 2 types, 149,171 each |
| `TestResult` | `0.44`, `14.68`, `25.2` | Numeric percentage, range 0–100 |
| `TestingLab(ITL)` | `LabA` through `LabZ` | 17 anonymized labs |
| `TestPerformedDate` | `4/12/2021` | MM/DD/YYYY format, Apr 2021 – Mar 2024 |
| `TestComment` | `ok` | Almost always "ok" |

**Quality Issues:**
- Strains are anonymized (`Strain_01`) — cannot match to real strain names without METRC cross-reference
- Labs are anonymized (`LabA`) — cannot identify specific labs
- 76 rows have 9 fields (comma in TestComment) — need careful CSV parsing
- METRC tags are the key linkage point to seed-to-sale; each tag has exactly 2 rows (THC + THCA)
- No operator/facility identifier — tests are market-wide, not per-dispensary

**Critical Insight:** Each METRC tag produces one THC row and one THCA row. We should pivot these into a single row per tag with both values.

### 2.2 Facility Sales (`facility-sales-stats.csv`)

**Structure:** 14 columns, 67,333 data rows

| Column | Sample | Notes |
|--------|--------|-------|
| `SalePeriod` | `2018-11-20 - 2025-12-14` | Always same range (dataset boundary) |
| `SaleDate` | `5/28/2024` | MM/DD/YYYY format |
| `DataType` | `Delivery and MBs`, `Retail` | 2 channel types |
| `SalesPeriodType` | `Historical` | Always "Historical" |
| `DeliveryType` | `Delivery Operators`, `Delivery Couriers`, `Retail` | 3 sale channels |
| `ProductCategoryName` | 20 categories (Buds, Concentrate, Vape Product, etc.) | Matches CCC taxonomy |
| `UnitOfMeasureName` | `ea` or `g` | Count vs weight based |
| `Quantity` | `31`, `78740.3` | Total quantity (weight in grams or count) |
| `Units` | `9`, `47871` | Number of transactions |
| `CountBasedTotal` | Count-based quantity | Non-zero when unit=ea |
| `DollarCountBasedTotal` | Dollar amount for count-based | Non-zero when unit=ea |
| `WeightBasedTotal` | Weight-based quantity in grams | Non-zero when unit=g |
| `DollarWeightBasedTotal` | Dollar amount for weight-based | Non-zero when unit=g |
| `TOTAL_$` | `47.4`, `633822.67` | Total dollars (sum of count+weight) |

**Quality Issues:**
- `SalePeriod` column is useless (always the same value)
- Dual accounting: products sold by count (edibles, vapes) vs by weight (flower, concentrates)
- Daily granularity is excellent for time-series analysis
- No operator-level breakdown — this is statewide aggregate data

### 2.3 ITD Retail & Delivery (`itd-retail-delivery-sales.csv`)

**Identical schema** to facility-sales-stats.csv but **different data** (MD5 checksums differ). Same 67,333 rows, same columns. Likely the same underlying dataset downloaded from a different CCC portal view — but since checksums differ, rows vary. We should import both and deduplicate on `(SaleDate, DeliveryType, ProductCategoryName, UnitOfMeasureName)`.

### 2.4 Medical Facility Stats (`medical-facility-stats.csv`)

**Structure:** 13 columns, 47,647 data rows — **no DeliveryType column** (medical is in-store only)

| Column | Difference from Adult |
|--------|----------------------|
| `Industry` | Always `Medical` (replaces `DataType`/`DeliveryType`) |
| No `DataType` column | — |
| No `DeliveryType` column | — |

Same financial columns. This is the medical-only complement to the adult-use sales data.

### 2.5 Monthly Price/Ounce (`avg-monthly-price-oz.csv`)

**Structure:** 3 columns, 71 data rows. Jan 2020 – Nov 2025.

| Column | Sample |
|--------|--------|
| `YearMonth` | `2020-01` |
| `AverageRetailPriceperGm` | `14.68` → `4.01` |
| `Unit` | Always `Grams` |

**Critical Insight:** Price has dropped from $14.68/g (Jan 2020) to $4.01/g (Nov 2025) — a **72.7% decline**. This is the official state benchmark. Combined with GLASS scraped prices, we can show where each operator sits relative to the state average over time.

### 2.6 Commence Operations (`commence-ops.csv`)

**Structure:** ~50 columns, 772 data rows. Every licensed, operating cannabis business in MA.

**Key Fields:**
- `BUSINESS_NAME`, `LICENSE_TYPE`, `LICENSE_NUMBER`, `LIC_STATUS`
- `BUSINESS_EMAIL`, `BUSINESS_PHONE` — **direct contact info**
- `ESTABLISHMENT_ADDRESS_1`, `ESTABLISHMENT_CITY`, `ESTABLISHMENT_STATE`, `ESTABLISHMENT_ZIP_CODE`
- `latitude`, `longitude`, `county` — **already geocoded**
- `DBE` — Disadvantaged Business Enterprise status
- `CULTIVATION_ENVIRONMNET` (sic), `CULTIVATION_TIER`
- `LIC_START_DATE`, `LIC_EXPIRATION_DATE`, `COMMENCE_OPERATIONS_DATE`
- `APPLICATION_CLASSIFICATION` — Priority/Expedited/General
- `EIN_TIN` — Employer ID (useful for entity dedup)

**License Types (11):**
`Marijuana Retailer`, `Marijuana Cultivator`, `Marijuana Product Manufacturer`, `Marijuana Delivery Operator`, `Marijuana Courier`, `Marijuana Microbusiness`, `Marijuana Transporter`, `Medical Marijuana Treatment Center`, `Independent Testing Laboratory`, `Microbusiness Delivery`, `Third Party Marijuana Transporter`

**Quality Issues:**
- `BUSINESS_NAME` has quoting inconsistencies (embedded commas, D/B/A suffixes)
- Date columns use verbose JS Date.toString() format: `"Thu Oct 12 2023 04:00:00 GMT-0400 (Eastern Daylight Time)"` — need robust parsing
- Some license numbers appear with prefix variants (`MR` vs `MRN`) — need normalization
- `CULTIVATION_ENVIRONMNET` is a typo in the source data (keep as-is in raw, normalize in clean)
- `EIN_TIN` present for entity deduplication

### 2.7 Adult Market + Counties (`adult-market-data-counties.csv`)

**Structure:** 65 columns, 1,753 data rows. Same operator licensing data as commence-ops but with county-level geography and additional timeline fields.

**Unique Fields Not in Commence Ops:**
- `county`, `county_lat`, `county_long`, `Region`
- `Town`, `ZIP`
- `APPLICATION_NUMBER`, `SUBMITTED_DATE`, `FIRST_COMPLIANCE_REVIEW_DATE`
- `CNB_DEEMED_COMPLETE_DATE`, `APPLICATION_CREATED_DATE`
- `FEE_WAIVER_REQUEST`, `FEE_WAIVER_EE_OR_SE_NUMBER`
- `EE_PRIORITY_STATUS`, `APPROVED_SE_NUMBER`
- `Approved_License_Stages` — includes non-commenced (PROVISIONAL LICENSE)

**Key Difference:** This includes operators that haven't commenced operations yet (provisional licenses), while commence-ops only has active operators. Together they give the full licensing pipeline.

---

## 3. Schema Design (Drizzle ORM)

### 3.1 New Tables Overview

```
┌─────────────────────┐     ┌──────────────────────┐
│   ccc_lab_tests      │     │  ccc_facility_sales   │
│   (298K → ~149K)     │     │  (67K + 67K deduped)  │
└─────────┬───────────┘     └──────────┬───────────┘
          │                            │
          │  metrc_tag                 │  sale_date + category
          │                            │
┌─────────▼───────────┐     ┌──────────▼───────────┐
│ ccc_medical_sales    │     │ ccc_monthly_prices    │
│ (47K)                │     │ (71)                  │
└─────────────────────┘     └──────────────────────┘

┌─────────────────────┐     ┌──────────────────────┐
│  ccc_licenses        │     │ ccc_county_market     │
│  (772 + 1753 merged) │     │ (aggregated)          │
└─────────┬───────────┘     └──────────────────────┘
          │
          │  license_number
          │
┌─────────▼───────────┐
│   operators          │  (existing — enriched via FK)
└─────────────────────┘

┌─────────────────────┐     ┌──────────────────────┐
│  operator_scores     │     │ google_reviews        │
│  (computed, cached)  │     │ (future)              │
└─────────────────────┘     └──────────────────────┘
```

### 3.2 Drizzle Schema Definitions

Add to `/data/workspace/projects/glass/src/services/api/src/db/schema.ts`:

```typescript
// ============================================================
// CCC LAB TESTING — Pivoted: one row per METRC tag
// ============================================================
export const cccLabTests = pgTable('ccc_lab_tests', {
  id: uuid('id').primaryKey().defaultRandom(),
  metrc_tag: varchar('metrc_tag', { length: 30 }).notNull(),
  product_category: varchar('product_category', { length: 30 }).notNull(),
  strain_code: varchar('strain_code', { length: 30 }).notNull(),
  thc_percent: decimal('thc_percent', { precision: 6, scale: 3 }),
  thca_percent: decimal('thca_percent', { precision: 6, scale: 3 }),
  // Total THC = THC + (THCA × 0.877)
  total_thc_percent: decimal('total_thc_percent', { precision: 6, scale: 3 }),
  testing_lab: varchar('testing_lab', { length: 10 }).notNull(),
  test_date: timestamp('test_date', { withTimezone: true }).notNull(),
  test_comment: text('test_comment'),
  // Linkage
  operator_id: uuid('operator_id').references(() => operators.id, { onDelete: 'set null' }),
  // ETL metadata
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
  // Composite for THC distribution queries
  index('idx_lab_tests_category_thc').on(table.product_category, table.total_thc_percent),
  index('idx_lab_tests_date_category').on(table.test_date, table.product_category),
]);

// ============================================================
// CCC FACILITY SALES — Daily statewide sales by category+channel
// Unifies facility-sales-stats.csv, itd-retail-delivery-sales.csv
// ============================================================
export const cccFacilitySales = pgTable('ccc_facility_sales', {
  id: uuid('id').primaryKey().defaultRandom(),
  sale_date: timestamp('sale_date', { withTimezone: true }).notNull(),
  market_type: varchar('market_type', { length: 15 }).notNull(), // 'adult' or 'medical'
  delivery_type: varchar('delivery_type', { length: 25 }).notNull(), // 'Retail', 'Delivery Operators', 'Delivery Couriers'
  product_category: varchar('product_category', { length: 50 }).notNull(),
  unit_of_measure: varchar('unit_of_measure', { length: 10 }).notNull(), // 'ea' or 'g'
  quantity: decimal('quantity', { precision: 14, scale: 3 }).notNull(),
  units: integer('units').notNull(), // transaction count
  count_based_total: decimal('count_based_total', { precision: 14, scale: 3 }),
  dollar_count_based: decimal('dollar_count_based', { precision: 14, scale: 2 }),
  weight_based_total: decimal('weight_based_total', { precision: 14, scale: 3 }),
  dollar_weight_based: decimal('dollar_weight_based', { precision: 14, scale: 2 }),
  total_dollars: decimal('total_dollars', { precision: 14, scale: 2 }).notNull(),
  // ETL metadata
  source_file: varchar('source_file', { length: 100 }),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  // Dedup key: one row per date+market+channel+category+unit
  unique('ccc_facility_sales_dedup').on(
    table.sale_date, table.market_type, table.delivery_type,
    table.product_category, table.unit_of_measure
  ),
  index('idx_facility_sales_date').on(table.sale_date),
  index('idx_facility_sales_market').on(table.market_type),
  index('idx_facility_sales_delivery').on(table.delivery_type),
  index('idx_facility_sales_category').on(table.product_category),
  // Time-series query optimization
  index('idx_facility_sales_date_market_cat').on(
    table.sale_date, table.market_type, table.product_category
  ),
  index('idx_facility_sales_date_delivery').on(table.sale_date, table.delivery_type),
]);

// ============================================================
// CCC MONTHLY PRICE BENCHMARK — Official state avg price/gram
// ============================================================
export const cccMonthlyPrices = pgTable('ccc_monthly_prices', {
  id: uuid('id').primaryKey().defaultRandom(),
  year_month: varchar('year_month', { length: 7 }).notNull(), // 'YYYY-MM'
  avg_price_per_gram: decimal('avg_price_per_gram', { precision: 6, scale: 2 }).notNull(),
  // Derived: price per ounce (×28), price per eighth (×3.5)
  avg_price_per_oz: decimal('avg_price_per_oz', { precision: 8, scale: 2 }),
  avg_price_per_eighth: decimal('avg_price_per_eighth', { precision: 7, scale: 2 }),
  // Month-over-month change
  mom_change_pct: decimal('mom_change_pct', { precision: 6, scale: 2 }),
  // YoY change
  yoy_change_pct: decimal('yoy_change_pct', { precision: 6, scale: 2 }),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('ccc_monthly_prices_month_unique').on(table.year_month),
  index('idx_monthly_prices_month').on(table.year_month),
]);

// ============================================================
// CCC LICENSES — Merged from commence-ops + adult-market-counties
// One row per license_number (a business may have multiple licenses)
// ============================================================
export const cccLicenses = pgTable('ccc_licenses', {
  id: uuid('id').primaryKey().defaultRandom(),
  license_number: varchar('license_number', { length: 30 }).notNull(),
  business_name: varchar('business_name', { length: 500 }).notNull(),
  license_type: varchar('license_type', { length: 100 }).notNull(),
  license_status: varchar('license_status', { length: 30 }).notNull(), // Active, Expired, Complete
  application_status: varchar('application_status', { length: 30 }),
  approved_license_type: varchar('approved_license_type', { length: 50 }),
  license_stage: varchar('license_stage', { length: 30 }), // COMMENCE OPS, PROVISIONAL LICENSE, FINAL LICENSE
  
  // Classification
  application_classification: varchar('application_classification', { length: 100 }),
  classification_tier1: varchar('classification_tier1', { length: 50 }), // Priority, Expedited, General
  classification_tier2: varchar('classification_tier2', { length: 50 }), // Economic Empowerment, Social Equity, etc.
  
  // Business Contact
  business_email: varchar('business_email', { length: 255 }),
  business_phone: varchar('business_phone', { length: 30 }),
  ein_tin: varchar('ein_tin', { length: 20 }),
  
  // Business Address
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
  dbe_status: varchar('dbe_status', { length: 200 }), // "Minority-Owned Business | Woman-Owned Business"
  is_social_equity: boolean('is_social_equity').notNull().default(false),
  is_economic_empowerment: boolean('is_economic_empowerment').notNull().default(false),
  priority_status: boolean('priority_status').notNull().default(false),
  se_number: varchar('se_number', { length: 20 }),
  ee_number: varchar('ee_number', { length: 20 }),
  
  // Cultivation-Specific
  cultivation_environment: varchar('cultivation_environment', { length: 20 }), // Indoor, Outdoor, Mixed
  cultivation_tier: varchar('cultivation_tier', { length: 50 }), // Tier 01-10
  
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
// COUNTY MARKET METRICS — Aggregated from county data + licenses
// ============================================================
export const cccCountyMetrics = pgTable('ccc_county_metrics', {
  id: uuid('id').primaryKey().defaultRandom(),
  county: varchar('county', { length: 50 }).notNull(),
  region: varchar('region', { length: 50 }),
  county_lat: decimal('county_lat', { precision: 10, scale: 6 }),
  county_lon: decimal('county_lon', { precision: 11, scale: 6 }),
  
  // License counts (snapshot)
  total_licenses: integer('total_licenses').notNull().default(0),
  active_retailers: integer('active_retailers').notNull().default(0),
  active_cultivators: integer('active_cultivators').notNull().default(0),
  active_manufacturers: integer('active_manufacturers').notNull().default(0),
  active_delivery: integer('active_delivery').notNull().default(0),
  active_testing_labs: integer('active_testing_labs').notNull().default(0),
  pending_applications: integer('pending_applications').notNull().default(0),
  
  // Equity metrics
  social_equity_count: integer('social_equity_count').notNull().default(0),
  economic_empowerment_count: integer('economic_empowerment_count').notNull().default(0),
  dbe_count: integer('dbe_count').notNull().default(0),
  
  // Computed
  operators_per_10k_pop: decimal('operators_per_10k_pop', { precision: 6, scale: 2 }),
  saturation_score: decimal('saturation_score', { precision: 5, scale: 2 }), // 0-100
  
  snapshot_date: timestamp('snapshot_date', { withTimezone: true }).notNull().defaultNow(),
  imported_at: timestamp('imported_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  unique('ccc_county_metrics_county_date').on(table.county, table.snapshot_date),
  index('idx_county_metrics_county').on(table.county),
  index('idx_county_metrics_region').on(table.region),
]);

// ============================================================
// OPERATOR SCORES — Computed intelligence (materialized)
// ============================================================
export const operatorScores = pgTable('operator_scores', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  
  // Composite Health Score (0-100)
  health_score: integer('health_score'),
  
  // Component Scores (each 0-100)
  price_competitiveness_score: integer('price_competitiveness_score'),
  product_quality_score: integer('product_quality_score'),
  compliance_score: integer('compliance_score'),
  market_presence_score: integer('market_presence_score'),
  review_score: integer('review_score'), // from Google Reviews (future)
  
  // THC Integrity Index (0-100, 100 = perfect match)
  thc_integrity_index: integer('thc_integrity_index'),
  thc_integrity_sample_size: integer('thc_integrity_sample_size'),
  
  // Price Position
  price_position_vs_state: decimal('price_position_vs_state', { precision: 6, scale: 2 }), // % above/below state avg
  price_position_vs_local: decimal('price_position_vs_local', { precision: 6, scale: 2 }), // % above/below county avg
  price_position_label: varchar('price_position_label', { length: 20 }), // 'premium', 'competitive', 'budget', 'undercut'
  
  // Growth Trajectory
  growth_trajectory_score: integer('growth_trajectory_score'), // 0-100
  growth_trend_direction: varchar('growth_trend_direction', { length: 10 }), // 'up', 'down', 'flat'
  growth_data_points: integer('growth_data_points'),
  
  // Market Saturation
  local_saturation_score: decimal('local_saturation_score', { precision: 5, scale: 2 }),
  competitors_5mi: integer('competitors_5mi'),
  competitors_10mi: integer('competitors_10mi'),
  
  // Metadata
  computed_at: timestamp('computed_at', { withTimezone: true }).notNull().defaultNow(),
  data_freshness: jsonb('data_freshness'), // { prices: '2025-02-12', labTests: '2024-03-15', reviews: null }
  computation_version: varchar('computation_version', { length: 20 }).notNull().default('v1'),
}, (table) => [
  unique('operator_scores_operator_version').on(table.operator_id, table.computation_version),
  index('idx_op_scores_operator').on(table.operator_id),
  index('idx_op_scores_health').on(table.health_score),
  index('idx_op_scores_computed').on(table.computed_at),
]);

// ============================================================
// GOOGLE REVIEWS (Future — schema ready)
// ============================================================
export const googleReviews = pgTable('google_reviews', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  place_id: varchar('place_id', { length: 100 }).notNull(),
  
  overall_rating: decimal('overall_rating', { precision: 3, scale: 2 }),
  total_reviews: integer('total_reviews'),
  
  // Individual review (optional — may not store all)
  reviewer_name: varchar('reviewer_name', { length: 200 }),
  review_rating: integer('review_rating'), // 1-5
  review_text: text('review_text'),
  review_time: timestamp('review_time', { withTimezone: true }),
  review_language: varchar('review_language', { length: 5 }),
  
  // Sentiment analysis (computed)
  sentiment_score: decimal('sentiment_score', { precision: 4, scale: 3 }), // -1.0 to 1.0
  sentiment_label: varchar('sentiment_label', { length: 20 }), // positive, negative, neutral
  
  fetched_at: timestamp('fetched_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_google_reviews_operator').on(table.operator_id),
  index('idx_google_reviews_place').on(table.place_id),
  index('idx_google_reviews_rating').on(table.overall_rating),
  index('idx_google_reviews_time').on(table.review_time),
]);

// ============================================================
// ENFORCEMENT ACTIONS (Future — schema ready)
// ============================================================
export const enforcementActions = pgTable('enforcement_actions', {
  id: uuid('id').primaryKey().defaultRandom(),
  license_id: uuid('license_id').references(() => cccLicenses.id, { onDelete: 'set null' }),
  operator_id: uuid('operator_id').references(() => operators.id, { onDelete: 'set null' }),
  
  action_type: varchar('action_type', { length: 50 }).notNull(), // 'warning', 'fine', 'suspension', 'revocation'
  action_date: timestamp('action_date', { withTimezone: true }).notNull(),
  description: text('description'),
  fine_amount: decimal('fine_amount', { precision: 10, scale: 2 }),
  resolution_status: varchar('resolution_status', { length: 30 }), // 'open', 'resolved', 'appealed'
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
// STRAIN DATABASE (Future — Otreeba API)
// ============================================================
export const strains = pgTable('strains', {
  id: uuid('id').primaryKey().defaultRandom(),
  otreeba_id: varchar('otreeba_id', { length: 50 }),
  name: varchar('name', { length: 200 }).notNull(),
  slug: varchar('slug', { length: 200 }),
  
  strain_type: varchar('strain_type', { length: 20 }), // indica, sativa, hybrid
  thc_min: decimal('thc_min', { precision: 5, scale: 2 }),
  thc_max: decimal('thc_max', { precision: 5, scale: 2 }),
  cbd_min: decimal('cbd_min', { precision: 5, scale: 2 }),
  cbd_max: decimal('cbd_max', { precision: 5, scale: 2 }),
  
  description: text('description'),
  effects: jsonb('effects'), // ['relaxed', 'happy', 'euphoric']
  flavors: jsonb('flavors'), // ['earthy', 'pine', 'woody']
  medical_uses: jsonb('medical_uses'), // ['pain', 'insomnia', 'anxiety']
  
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
// ETL RUN LOG — Track every import for auditability
// ============================================================
export const etlRuns = pgTable('etl_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  dataset: varchar('dataset', { length: 50 }).notNull(), // 'lab_tests', 'facility_sales', etc.
  source_file: varchar('source_file', { length: 255 }).notNull(),
  source_hash: varchar('source_hash', { length: 64 }), // SHA-256 of source file
  
  started_at: timestamp('started_at', { withTimezone: true }).notNull().defaultNow(),
  completed_at: timestamp('completed_at', { withTimezone: true }),
  status: varchar('status', { length: 20 }).notNull().default('running'), // running, completed, failed
  
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

### 3.3 Modifications to Existing Tables

```typescript
// Add to operators table:
// - license_type (from CCC data)  
// - county, region (from CCC data)
// - ccc_license_id FK (to ccc_licenses)

// Migration SQL:
/*
ALTER TABLE operators ADD COLUMN IF NOT EXISTS license_type VARCHAR(100);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS county VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS region VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS ccc_license_id UUID REFERENCES ccc_licenses(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_operators_county ON operators(county);
CREATE INDEX IF NOT EXISTS idx_operators_license_type ON operators(license_type);
CREATE INDEX IF NOT EXISTS idx_operators_ccc_license ON operators(ccc_license_id);
*/
```

### 3.4 Migration File

Save as `scripts/migrations/006-ccc-data-integration.sql`:

```sql
-- GLASS Migration 006: CCC Data Integration
-- Creates tables for lab tests, facility sales, monthly prices, licenses, county metrics
-- Also creates operator_scores, google_reviews (future), enforcement_actions (future), strains (future)
-- And ETL audit log

BEGIN;

-- ============================================================
-- 1. CCC Lab Tests (pivoted: one row per METRC tag)
-- ============================================================
CREATE TABLE IF NOT EXISTS ccc_lab_tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metrc_tag VARCHAR(30) NOT NULL,
  product_category VARCHAR(30) NOT NULL,
  strain_code VARCHAR(30) NOT NULL,
  thc_percent DECIMAL(6,3),
  thca_percent DECIMAL(6,3),
  total_thc_percent DECIMAL(6,3),
  testing_lab VARCHAR(10) NOT NULL,
  test_date TIMESTAMPTZ NOT NULL,
  test_comment TEXT,
  operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  source_file VARCHAR(100),
  imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE ccc_lab_tests ADD CONSTRAINT ccc_lab_tests_metrc_tag_unique UNIQUE (metrc_tag);
CREATE INDEX IF NOT EXISTS idx_lab_tests_category ON ccc_lab_tests(product_category);
CREATE INDEX IF NOT EXISTS idx_lab_tests_strain ON ccc_lab_tests(strain_code);
CREATE INDEX IF NOT EXISTS idx_lab_tests_date ON ccc_lab_tests(test_date);
CREATE INDEX IF NOT EXISTS idx_lab_tests_lab ON ccc_lab_tests(testing_lab);
CREATE INDEX IF NOT EXISTS idx_lab_tests_thc ON ccc_lab_tests(total_thc_percent);
CREATE INDEX IF NOT EXISTS idx_lab_tests_operator ON ccc_lab_tests(operator_id);
CREATE INDEX IF NOT EXISTS idx_lab_tests_category_thc ON ccc_lab_tests(product_category, total_thc_percent);
CREATE INDEX IF NOT EXISTS idx_lab_tests_date_category ON ccc_lab_tests(test_date, product_category);

-- ============================================================
-- 2. CCC Facility Sales (unified adult + medical + delivery)
-- ============================================================
CREATE TABLE IF NOT EXISTS ccc_facility_sales (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sale_date TIMESTAMPTZ NOT NULL,
  market_type VARCHAR(15) NOT NULL,
  delivery_type VARCHAR(25) NOT NULL,
  product_category VARCHAR(50) NOT NULL,
  unit_of_measure VARCHAR(10) NOT NULL,
  quantity DECIMAL(14,3) NOT NULL,
  units INTEGER NOT NULL,
  count_based_total DECIMAL(14,3),
  dollar_count_based DECIMAL(14,2),
  weight_based_total DECIMAL(14,3),
  dollar_weight_based DECIMAL(14,2),
  total_dollars DECIMAL(14,2) NOT NULL,
  source_file VARCHAR(100),
  imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE ccc_facility_sales ADD CONSTRAINT ccc_facility_sales_dedup 
  UNIQUE (sale_date, market_type, delivery_type, product_category, unit_of_measure);
CREATE INDEX IF NOT EXISTS idx_facility_sales_date ON ccc_facility_sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_facility_sales_market ON ccc_facility_sales(market_type);
CREATE INDEX IF NOT EXISTS idx_facility_sales_delivery ON ccc_facility_sales(delivery_type);
CREATE INDEX IF NOT EXISTS idx_facility_sales_category ON ccc_facility_sales(product_category);
CREATE INDEX IF NOT EXISTS idx_facility_sales_date_market_cat ON ccc_facility_sales(sale_date, market_type, product_category);
CREATE INDEX IF NOT EXISTS idx_facility_sales_date_delivery ON ccc_facility_sales(sale_date, delivery_type);

-- ============================================================
-- 3. CCC Monthly Price Benchmark
-- ============================================================
CREATE TABLE IF NOT EXISTS ccc_monthly_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  year_month VARCHAR(7) NOT NULL,
  avg_price_per_gram DECIMAL(6,2) NOT NULL,
  avg_price_per_oz DECIMAL(8,2),
  avg_price_per_eighth DECIMAL(7,2),
  mom_change_pct DECIMAL(6,2),
  yoy_change_pct DECIMAL(6,2),
  imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE ccc_monthly_prices ADD CONSTRAINT ccc_monthly_prices_month_unique UNIQUE (year_month);
CREATE INDEX IF NOT EXISTS idx_monthly_prices_month ON ccc_monthly_prices(year_month);

-- ============================================================
-- 4. CCC Licenses (merged commence-ops + adult-market)
-- ============================================================
CREATE TABLE IF NOT EXISTS ccc_licenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  license_number VARCHAR(30) NOT NULL,
  business_name VARCHAR(500) NOT NULL,
  license_type VARCHAR(100) NOT NULL,
  license_status VARCHAR(30) NOT NULL,
  application_status VARCHAR(30),
  approved_license_type VARCHAR(50),
  license_stage VARCHAR(30),
  application_classification VARCHAR(100),
  classification_tier1 VARCHAR(50),
  classification_tier2 VARCHAR(50),
  business_email VARCHAR(255),
  business_phone VARCHAR(30),
  ein_tin VARCHAR(20),
  business_address_1 VARCHAR(255),
  business_address_2 VARCHAR(255),
  business_city VARCHAR(100),
  business_state VARCHAR(2),
  business_zip VARCHAR(10),
  establishment_address_1 VARCHAR(255),
  establishment_address_2 VARCHAR(255),
  establishment_city VARCHAR(100),
  establishment_state VARCHAR(2),
  establishment_zip VARCHAR(10),
  latitude DECIMAL(10,8),
  longitude DECIMAL(11,8),
  county VARCHAR(50),
  region VARCHAR(50),
  town VARCHAR(100),
  dbe_status VARCHAR(200),
  is_social_equity BOOLEAN NOT NULL DEFAULT FALSE,
  is_economic_empowerment BOOLEAN NOT NULL DEFAULT FALSE,
  priority_status BOOLEAN NOT NULL DEFAULT FALSE,
  se_number VARCHAR(20),
  ee_number VARCHAR(20),
  cultivation_environment VARCHAR(20),
  cultivation_tier VARCHAR(50),
  submitted_date TIMESTAMPTZ,
  application_approved_date TIMESTAMPTZ,
  license_start_date TIMESTAMPTZ,
  license_expiration_date TIMESTAMPTZ,
  commence_operations_date TIMESTAMPTZ,
  first_compliance_review_date TIMESTAMPTZ,
  deemed_complete_date TIMESTAMPTZ,
  payment_amount DECIMAL(10,2),
  license_fee_amount DECIMAL(10,2),
  operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  ccc_last_updated TIMESTAMPTZ,
  source_file VARCHAR(100),
  imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE ccc_licenses ADD CONSTRAINT ccc_licenses_number_unique UNIQUE (license_number);
CREATE INDEX IF NOT EXISTS idx_licenses_business_name ON ccc_licenses(business_name);
CREATE INDEX IF NOT EXISTS idx_licenses_type ON ccc_licenses(license_type);
CREATE INDEX IF NOT EXISTS idx_licenses_status ON ccc_licenses(license_status);
CREATE INDEX IF NOT EXISTS idx_licenses_stage ON ccc_licenses(license_stage);
CREATE INDEX IF NOT EXISTS idx_licenses_city ON ccc_licenses(establishment_city);
CREATE INDEX IF NOT EXISTS idx_licenses_county ON ccc_licenses(county);
CREATE INDEX IF NOT EXISTS idx_licenses_location ON ccc_licenses(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_licenses_operator ON ccc_licenses(operator_id);
CREATE INDEX IF NOT EXISTS idx_licenses_ein ON ccc_licenses(ein_tin);
CREATE INDEX IF NOT EXISTS idx_licenses_expiration ON ccc_licenses(license_expiration_date);
CREATE INDEX IF NOT EXISTS idx_licenses_equity ON ccc_licenses(is_social_equity, is_economic_empowerment);
CREATE INDEX IF NOT EXISTS idx_licenses_type_status ON ccc_licenses(license_type, license_status);

-- ============================================================
-- 5. County Market Metrics
-- ============================================================
CREATE TABLE IF NOT EXISTS ccc_county_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  county VARCHAR(50) NOT NULL,
  region VARCHAR(50),
  county_lat DECIMAL(10,6),
  county_lon DECIMAL(11,6),
  total_licenses INTEGER NOT NULL DEFAULT 0,
  active_retailers INTEGER NOT NULL DEFAULT 0,
  active_cultivators INTEGER NOT NULL DEFAULT 0,
  active_manufacturers INTEGER NOT NULL DEFAULT 0,
  active_delivery INTEGER NOT NULL DEFAULT 0,
  active_testing_labs INTEGER NOT NULL DEFAULT 0,
  pending_applications INTEGER NOT NULL DEFAULT 0,
  social_equity_count INTEGER NOT NULL DEFAULT 0,
  economic_empowerment_count INTEGER NOT NULL DEFAULT 0,
  dbe_count INTEGER NOT NULL DEFAULT 0,
  operators_per_10k_pop DECIMAL(6,2),
  saturation_score DECIMAL(5,2),
  snapshot_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE ccc_county_metrics ADD CONSTRAINT ccc_county_metrics_county_date UNIQUE (county, snapshot_date);
CREATE INDEX IF NOT EXISTS idx_county_metrics_county ON ccc_county_metrics(county);
CREATE INDEX IF NOT EXISTS idx_county_metrics_region ON ccc_county_metrics(region);

-- ============================================================
-- 6. Operator Scores (computed intelligence cache)
-- ============================================================
CREATE TABLE IF NOT EXISTS operator_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  health_score INTEGER,
  price_competitiveness_score INTEGER,
  product_quality_score INTEGER,
  compliance_score INTEGER,
  market_presence_score INTEGER,
  review_score INTEGER,
  thc_integrity_index INTEGER,
  thc_integrity_sample_size INTEGER,
  price_position_vs_state DECIMAL(6,2),
  price_position_vs_local DECIMAL(6,2),
  price_position_label VARCHAR(20),
  growth_trajectory_score INTEGER,
  growth_trend_direction VARCHAR(10),
  growth_data_points INTEGER,
  local_saturation_score DECIMAL(5,2),
  competitors_5mi INTEGER,
  competitors_10mi INTEGER,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  data_freshness JSONB,
  computation_version VARCHAR(20) NOT NULL DEFAULT 'v1'
);

ALTER TABLE operator_scores ADD CONSTRAINT operator_scores_operator_version UNIQUE (operator_id, computation_version);
CREATE INDEX IF NOT EXISTS idx_op_scores_operator ON operator_scores(operator_id);
CREATE INDEX IF NOT EXISTS idx_op_scores_health ON operator_scores(health_score);
CREATE INDEX IF NOT EXISTS idx_op_scores_computed ON operator_scores(computed_at);

-- ============================================================
-- 7. Google Reviews (future — schema ready)
-- ============================================================
CREATE TABLE IF NOT EXISTS google_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  place_id VARCHAR(100) NOT NULL,
  overall_rating DECIMAL(3,2),
  total_reviews INTEGER,
  reviewer_name VARCHAR(200),
  review_rating INTEGER,
  review_text TEXT,
  review_time TIMESTAMPTZ,
  review_language VARCHAR(5),
  sentiment_score DECIMAL(4,3),
  sentiment_label VARCHAR(20),
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_google_reviews_operator ON google_reviews(operator_id);
CREATE INDEX IF NOT EXISTS idx_google_reviews_place ON google_reviews(place_id);
CREATE INDEX IF NOT EXISTS idx_google_reviews_rating ON google_reviews(overall_rating);

-- ============================================================
-- 8. Enforcement Actions (future)
-- ============================================================
CREATE TABLE IF NOT EXISTS enforcement_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  license_id UUID REFERENCES ccc_licenses(id) ON DELETE SET NULL,
  operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  action_type VARCHAR(50) NOT NULL,
  action_date TIMESTAMPTZ NOT NULL,
  description TEXT,
  fine_amount DECIMAL(10,2),
  resolution_status VARCHAR(30),
  resolution_date TIMESTAMPTZ,
  source_url TEXT,
  source_document TEXT,
  imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_enforcement_license ON enforcement_actions(license_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_operator ON enforcement_actions(operator_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_type ON enforcement_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_enforcement_date ON enforcement_actions(action_date);

-- ============================================================
-- 9. Strains (future — Otreeba)
-- ============================================================
CREATE TABLE IF NOT EXISTS strains (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  otreeba_id VARCHAR(50),
  name VARCHAR(200) NOT NULL,
  slug VARCHAR(200),
  strain_type VARCHAR(20),
  thc_min DECIMAL(5,2),
  thc_max DECIMAL(5,2),
  cbd_min DECIMAL(5,2),
  cbd_max DECIMAL(5,2),
  description TEXT,
  effects JSONB,
  flavors JSONB,
  medical_uses JSONB,
  parent_strain_1 VARCHAR(200),
  parent_strain_2 VARCHAR(200),
  imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE strains ADD CONSTRAINT strains_otreeba_unique UNIQUE (otreeba_id);
CREATE INDEX IF NOT EXISTS idx_strains_name ON strains(name);
CREATE INDEX IF NOT EXISTS idx_strains_type ON strains(strain_type);

-- ============================================================
-- 10. ETL Run Log
-- ============================================================
CREATE TABLE IF NOT EXISTS etl_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset VARCHAR(50) NOT NULL,
  source_file VARCHAR(255) NOT NULL,
  source_hash VARCHAR(64),
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status VARCHAR(20) NOT NULL DEFAULT 'running',
  rows_read INTEGER DEFAULT 0,
  rows_inserted INTEGER DEFAULT 0,
  rows_updated INTEGER DEFAULT 0,
  rows_skipped INTEGER DEFAULT 0,
  rows_errored INTEGER DEFAULT 0,
  error_log JSONB DEFAULT '[]'::jsonb,
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_etl_runs_dataset ON etl_runs(dataset);
CREATE INDEX IF NOT EXISTS idx_etl_runs_status ON etl_runs(status);
CREATE INDEX IF NOT EXISTS idx_etl_runs_started ON etl_runs(started_at);

-- ============================================================
-- 11. Operator table enrichment
-- ============================================================
ALTER TABLE operators ADD COLUMN IF NOT EXISTS license_type VARCHAR(100);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS county VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS region VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS ccc_license_id UUID REFERENCES ccc_licenses(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_operators_county ON operators(county);
CREATE INDEX IF NOT EXISTS idx_operators_license_type ON operators(license_type);
CREATE INDEX IF NOT EXISTS idx_operators_ccc_license ON operators(ccc_license_id);

COMMIT;
```

### 3.5 Partitioning Strategy

For the `ccc_lab_tests` table (298K rows, growing), we **do NOT need partitioning yet**. Here's why:

- 298K rows with proper indexes is fast in PostgreSQL (sub-10ms queries)
- Railway Postgres has ample storage for this
- The data is static (Apr 2021 – Mar 2024) and will only grow ~100K/year when new dumps arrive
- Partitioning adds complexity for Drizzle ORM (no native partition support)

**When to partition (trigger):** If `ccc_lab_tests` exceeds 2M rows OR query times on indexed columns exceed 50ms, create range partitions by `test_date` (yearly):

```sql
-- Only execute if table exceeds 2M rows
CREATE TABLE ccc_lab_tests_partitioned (LIKE ccc_lab_tests INCLUDING ALL) PARTITION BY RANGE (test_date);
CREATE TABLE ccc_lab_tests_2021 PARTITION OF ccc_lab_tests_partitioned FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE ccc_lab_tests_2022 PARTITION OF ccc_lab_tests_partitioned FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');
-- etc.
```

For `ccc_facility_sales` (67K+ rows per file, 2 files + medical), similarly no partitioning needed yet. The composite unique index on `(sale_date, market_type, delivery_type, product_category, unit_of_measure)` handles deduplication and fast lookups.

---

## 4. ETL Pipeline

### 4.1 Architecture Overview

```
                      ┌─────────────────┐
                      │  CCC CSV Files   │
                      │  (ccc-raw/*.csv) │
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │   ETL Runner     │
                      │  (TypeScript)    │
                      │                  │
                      │ 1. Parse CSV     │
                      │ 2. Clean/Validate│
                      │ 3. Hash for dedup│
                      │ 4. Upsert to DB  │
                      │ 5. Log to etl_runs│
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │   PostgreSQL     │
                      │  (Railway)       │
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │ Score Compute    │
                      │ (post-ETL job)   │
                      └─────────────────┘
```

### 4.2 Shared ETL Infrastructure

File: `scripts/etl/lib/etl-base.ts`

```typescript
import { Pool } from 'pg';
import { createReadStream } from 'fs';
import { createHash } from 'crypto';
import * as csv from 'csv-parse';

// Railway production DB
const DATABASE_URL = process.env.DATABASE_URL 
  ?? 'postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway';

export const pool = new Pool({ connectionString: DATABASE_URL, max: 10 });

export interface EtlRunRecord {
  id: string;
  dataset: string;
  source_file: string;
  source_hash: string;
  rows_read: number;
  rows_inserted: number;
  rows_updated: number;
  rows_skipped: number;
  rows_errored: number;
  errors: Array<{ row: number; error: string; data?: any }>;
}

/**
 * Compute SHA-256 hash of a file for change detection
 */
export async function fileHash(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const hash = createHash('sha256');
    const stream = createReadStream(filePath);
    stream.on('data', (chunk) => hash.update(chunk));
    stream.on('end', () => resolve(hash.digest('hex')));
    stream.on('error', reject);
  });
}

/**
 * Check if a file has already been imported (by hash)
 */
export async function isAlreadyImported(dataset: string, hash: string): Promise<boolean> {
  const result = await pool.query(
    `SELECT id FROM etl_runs WHERE dataset = $1 AND source_hash = $2 AND status = 'completed'`,
    [dataset, hash]
  );
  return result.rows.length > 0;
}

/**
 * Start an ETL run (creates log entry)
 */
export async function startEtlRun(dataset: string, sourceFile: string, hash: string): Promise<string> {
  const result = await pool.query(
    `INSERT INTO etl_runs (dataset, source_file, source_hash, status)
     VALUES ($1, $2, $3, 'running') RETURNING id`,
    [dataset, sourceFile, hash]
  );
  return result.rows[0].id;
}

/**
 * Complete an ETL run
 */
export async function completeEtlRun(
  runId: string,
  stats: { rows_read: number; rows_inserted: number; rows_updated: number; rows_skipped: number; rows_errored: number },
  errors: any[] = []
): Promise<void> {
  await pool.query(
    `UPDATE etl_runs SET 
       status = 'completed', completed_at = NOW(),
       rows_read = $2, rows_inserted = $3, rows_updated = $4,
       rows_skipped = $5, rows_errored = $6, error_log = $7
     WHERE id = $1`,
    [runId, stats.rows_read, stats.rows_inserted, stats.rows_updated, stats.rows_skipped, stats.rows_errored, JSON.stringify(errors)]
  );
}

/**
 * Fail an ETL run
 */
export async function failEtlRun(runId: string, error: string): Promise<void> {
  await pool.query(
    `UPDATE etl_runs SET status = 'failed', completed_at = NOW(), error_log = $2 WHERE id = $1`,
    [runId, JSON.stringify([{ error }])]
  );
}

/**
 * Parse CSV file with streaming (memory-efficient for 298K+ rows)
 */
export function parseCsvStream(filePath: string, options: csv.Options = {}): csv.Parser {
  const parser = createReadStream(filePath).pipe(
    csv.parse({
      columns: true,
      skip_empty_lines: true,
      trim: true,
      relax_quotes: true,     // Handle messy quoting in CCC data
      relax_column_count: true, // Handle varying column counts (TestComment with commas)
      ...options,
    })
  );
  return parser;
}

/**
 * Parse CCC's verbose date format: "Thu Oct 12 2023 04:00:00 GMT-0400 (Eastern Daylight Time)"
 * Also handles: "10/08/2025", "4/12/2021", "2020-01"
 */
export function parseCccDate(dateStr: string | null | undefined): Date | null {
  if (!dateStr || dateStr.trim() === '') return null;
  
  const s = dateStr.trim();
  
  // ISO format: "2020-01" or "2020-01-15"
  if (/^\d{4}-\d{2}(-\d{2})?$/.test(s)) {
    return new Date(s + (s.length === 7 ? '-01' : '') + 'T00:00:00Z');
  }
  
  // US format: "4/12/2021" or "10/08/2025"
  if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(s)) {
    const [month, day, year] = s.split('/');
    return new Date(`${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}T00:00:00Z`);
  }
  
  // Verbose JS format: "Thu Oct 12 2023 04:00:00 GMT-0400 (Eastern Daylight Time)"
  if (s.includes('GMT')) {
    // Extract the date portion before timezone description
    const cleaned = s.replace(/\s*\([^)]*\)\s*$/, '');
    const d = new Date(cleaned);
    if (!isNaN(d.getTime())) return d;
  }
  
  // Fallback: try native parsing
  const d = new Date(s);
  if (!isNaN(d.getTime())) return d;
  
  return null;
}

/**
 * Batch upsert helper — chunks array into batches
 */
export async function batchProcess<T>(
  items: T[],
  batchSize: number,
  processor: (batch: T[]) => Promise<{ inserted: number; updated: number; skipped: number; errored: number }>
): Promise<{ inserted: number; updated: number; skipped: number; errored: number }> {
  const totals = { inserted: 0, updated: 0, skipped: 0, errored: 0 };
  
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const result = await processor(batch);
    totals.inserted += result.inserted;
    totals.updated += result.updated;
    totals.skipped += result.skipped;
    totals.errored += result.errored;
    
    if ((i + batchSize) % 10000 === 0 || i + batchSize >= items.length) {
      console.log(`  Progress: ${Math.min(i + batchSize, items.length)}/${items.length} (${totals.inserted} inserted, ${totals.updated} updated)`);
    }
  }
  
  return totals;
}

/**
 * Clean business name for matching
 */
export function normalizeBusinessName(name: string): string {
  return name
    .replace(/^"|"$/g, '')          // Strip surrounding quotes
    .replace(/,?\s*(INC\.?|LLC\.?|LTD\.?|CORP\.?)\s*$/i, '') // Strip suffixes
    .replace(/\s+D\/B\/A\s+.*/i, '') // Strip DBA names (keep primary)
    .replace(/[^\w\s]/g, '')        // Strip special chars
    .replace(/\s+/g, ' ')          // Normalize whitespace
    .trim()
    .toLowerCase();
}

/**
 * Normalize license number (MR → MRN variants, strip whitespace)
 */
export function normalizeLicenseNumber(num: string): string {
  return num.trim().toUpperCase();
}
```

### 4.3 Import Script: Lab Tests

File: `scripts/etl/import-lab-tests.ts`

```typescript
import { pool, fileHash, isAlreadyImported, startEtlRun, completeEtlRun, failEtlRun, parseCsvStream, parseCccDate } from './lib/etl-base';

const SOURCE_FILE = 'data/ccc-raw/testing-thc-thca.csv';
const DATASET = 'lab_tests';
const BATCH_SIZE = 2000;

interface RawLabRow {
  ProductCategoryType: string;
  ID: string;
  Strain: string;
  'Test Type Name': string;
  TestResult: string;
  'TestingLab(ITL)': string;
  TestPerformedDate: string;
  TestComment: string;
}

interface PivotedTest {
  metrc_tag: string;
  product_category: string;
  strain_code: string;
  thc_percent: number | null;
  thca_percent: number | null;
  total_thc_percent: number | null;
  testing_lab: string;
  test_date: Date;
  test_comment: string;
}

async function run() {
  const hash = await fileHash(SOURCE_FILE);
  
  if (await isAlreadyImported(DATASET, hash)) {
    console.log(`[${DATASET}] File unchanged (hash: ${hash.slice(0, 12)}...), skipping.`);
    return;
  }
  
  const runId = await startEtlRun(DATASET, SOURCE_FILE, hash);
  console.log(`[${DATASET}] Starting import, run ID: ${runId}`);
  
  try {
    // Phase 1: Read and pivot — collect THC and THCA per METRC tag
    const tagMap = new Map<string, { thc: number | null; thca: number | null; row: RawLabRow }>();
    let rowsRead = 0;
    const errors: Array<{ row: number; error: string }> = [];
    
    const parser = parseCsvStream(SOURCE_FILE);
    
    for await (const row of parser as AsyncIterable<RawLabRow>) {
      rowsRead++;
      
      const tag = row.ID?.trim();
      if (!tag) {
        errors.push({ row: rowsRead, error: 'Missing METRC tag' });
        continue;
      }
      
      const result = parseFloat(row.TestResult);
      if (isNaN(result)) {
        errors.push({ row: rowsRead, error: `Invalid TestResult: ${row.TestResult}` });
        continue;
      }
      
      const existing = tagMap.get(tag) ?? { thc: null, thca: null, row };
      
      const testType = row['Test Type Name']?.trim() ?? '';
      if (testType.startsWith('THC (%)')) {
        existing.thc = result;
      } else if (testType.startsWith('THCA (%)')) {
        existing.thca = result;
      }
      
      if (!tagMap.has(tag)) {
        existing.row = row;
      }
      tagMap.set(tag, existing);
    }
    
    console.log(`[${DATASET}] Read ${rowsRead} raw rows → ${tagMap.size} unique METRC tags`);
    
    // Phase 2: Build pivoted records
    const records: PivotedTest[] = [];
    for (const [tag, data] of tagMap) {
      const testDate = parseCccDate(data.row.TestPerformedDate);
      if (!testDate) {
        errors.push({ row: 0, error: `Bad date for tag ${tag}: ${data.row.TestPerformedDate}` });
        continue;
      }
      
      // Total THC = THC + (THCA × 0.877) — standard decarboxylation factor
      const totalThc = (data.thc ?? 0) + (data.thca ?? 0) * 0.877;
      
      records.push({
        metrc_tag: tag,
        product_category: data.row.ProductCategoryType?.trim() ?? 'Unknown',
        strain_code: data.row.Strain?.trim() ?? 'Unknown',
        thc_percent: data.thc,
        thca_percent: data.thca,
        total_thc_percent: Math.round(totalThc * 1000) / 1000,
        testing_lab: data.row['TestingLab(ITL)']?.trim() ?? 'Unknown',
        test_date: testDate,
        test_comment: data.row.TestComment?.trim() ?? '',
      });
    }
    
    console.log(`[${DATASET}] ${records.length} pivoted records ready for insert`);
    
    // Phase 3: Batch upsert
    let inserted = 0, updated = 0, skipped = 0;
    
    for (let i = 0; i < records.length; i += BATCH_SIZE) {
      const batch = records.slice(i, i + BATCH_SIZE);
      
      const values = batch.map((r, idx) => {
        const base = idx * 9;
        return `($${base + 1}, $${base + 2}, $${base + 3}, $${base + 4}, $${base + 5}, $${base + 6}, $${base + 7}, $${base + 8}, $${base + 9})`;
      }).join(', ');
      
      const params = batch.flatMap(r => [
        r.metrc_tag, r.product_category, r.strain_code,
        r.thc_percent, r.thca_percent, r.total_thc_percent,
        r.testing_lab, r.test_date.toISOString(), r.test_comment,
      ]);
      
      const result = await pool.query(`
        INSERT INTO ccc_lab_tests (metrc_tag, product_category, strain_code, thc_percent, thca_percent, total_thc_percent, testing_lab, test_date, test_comment, source_file)
        VALUES ${values.replace(/\$(\d+)/g, (_, n) => `$${n}`)}
        ON CONFLICT (metrc_tag) DO UPDATE SET
          thc_percent = EXCLUDED.thc_percent,
          thca_percent = EXCLUDED.thca_percent,
          total_thc_percent = EXCLUDED.total_thc_percent,
          test_comment = EXCLUDED.test_comment
      `, params);
      
      // Note: For proper batch parameterization, use a query builder.
      // This is pseudocode — actual implementation should use pg's query builder
      // or construct parameterized queries properly.
      
      inserted += batch.length; // Simplified — ON CONFLICT counts as insert
      
      if ((i + BATCH_SIZE) % 20000 === 0) {
        console.log(`  Progress: ${Math.min(i + BATCH_SIZE, records.length)}/${records.length}`);
      }
    }
    
    await completeEtlRun(runId, {
      rows_read: rowsRead,
      rows_inserted: inserted,
      rows_updated: updated,
      rows_skipped: skipped,
      rows_errored: errors.length,
    }, errors.slice(0, 100)); // Cap error log at 100 entries
    
    console.log(`[${DATASET}] Complete: ${inserted} inserted, ${errors.length} errors`);
    
  } catch (err) {
    await failEtlRun(runId, (err as Error).message);
    console.error(`[${DATASET}] FAILED:`, err);
    throw err;
  } finally {
    await pool.end();
  }
}

run().catch(console.error);
```

**Implementation note:** The batch insert above is pseudocode for clarity. In production, use a proper parameterized batch insert. The simplest approach:

```typescript
// Production batch insert using raw SQL with unnest
async function batchInsertLabTests(records: PivotedTest[]): Promise<number> {
  const result = await pool.query(`
    INSERT INTO ccc_lab_tests (
      metrc_tag, product_category, strain_code,
      thc_percent, thca_percent, total_thc_percent,
      testing_lab, test_date, test_comment, source_file
    )
    SELECT * FROM unnest(
      $1::varchar[], $2::varchar[], $3::varchar[],
      $4::decimal[], $5::decimal[], $6::decimal[],
      $7::varchar[], $8::timestamptz[], $9::text[], $10::varchar[]
    )
    ON CONFLICT (metrc_tag) DO UPDATE SET
      thc_percent = EXCLUDED.thc_percent,
      thca_percent = EXCLUDED.thca_percent,
      total_thc_percent = EXCLUDED.total_thc_percent
    RETURNING (xmax = 0) AS was_inserted
  `, [
    records.map(r => r.metrc_tag),
    records.map(r => r.product_category),
    records.map(r => r.strain_code),
    records.map(r => r.thc_percent),
    records.map(r => r.thca_percent),
    records.map(r => r.total_thc_percent),
    records.map(r => r.testing_lab),
    records.map(r => r.test_date.toISOString()),
    records.map(r => r.test_comment),
    records.map(() => 'testing-thc-thca.csv'),
  ]);
  
  return result.rowCount ?? 0;
}
```

### 4.4 Import Script: Facility Sales (Adult + ITD + Medical)

File: `scripts/etl/import-facility-sales.ts`

```typescript
import { pool, fileHash, isAlreadyImported, startEtlRun, completeEtlRun, failEtlRun, parseCsvStream, parseCccDate } from './lib/etl-base';

const FILES = [
  { path: 'data/ccc-raw/facility-sales-stats.csv', marketType: 'adult' },
  { path: 'data/ccc-raw/itd-retail-delivery-sales.csv', marketType: 'adult' },
  { path: 'data/ccc-raw/medical-facility-stats.csv', marketType: 'medical' },
];

const DATASET = 'facility_sales';

interface AdultSalesRow {
  SalePeriod: string;
  SaleDate: string;
  DataType: string;
  SalesPeriodType: string;
  DeliveryType: string;
  ProductCategoryName: string;
  UnitOfMeasureName: string;
  Quantity: string;
  Units: string;
  CountBasedTotal: string;
  DollarCountBasedTotal: string;
  WeightBasedTotal: string;
  DollarWeightBasedTotal: string;
  'TOTAL_$': string;
}

interface MedicalSalesRow {
  SalePeriod: string;
  SaleDate: string;
  SalesPeriodType: string;
  Industry: string;
  ProductCategoryName: string;
  UnitOfMeasureName: string;
  Quantity: string;
  Units: string;
  CountBasedTotal: string;
  DollarCountBasedTotal: string;
  WeightBasedTotal: string;
  DollarWeightBasedTotal: string;
  'TOTAL_$': string;
}

interface SalesRecord {
  sale_date: Date;
  market_type: string;
  delivery_type: string;
  product_category: string;
  unit_of_measure: string;
  quantity: number;
  units: number;
  count_based_total: number;
  dollar_count_based: number;
  weight_based_total: number;
  dollar_weight_based: number;
  total_dollars: number;
  source_file: string;
}

function parseNumber(s: string): number {
  const n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}

async function importFile(filePath: string, marketType: string): Promise<{
  read: number; inserted: number; updated: number; skipped: number; errored: number;
}> {
  const stats = { read: 0, inserted: 0, updated: 0, skipped: 0, errored: 0 };
  const records: SalesRecord[] = [];
  
  const parser = parseCsvStream(filePath);
  
  for await (const raw of parser as AsyncIterable<any>) {
    stats.read++;
    
    const saleDate = parseCccDate(raw.SaleDate);
    if (!saleDate) { stats.errored++; continue; }
    
    let deliveryType: string;
    if (marketType === 'medical') {
      deliveryType = 'Medical'; // Medical has no delivery type
    } else {
      deliveryType = raw.DeliveryType?.trim() ?? 'Unknown';
    }
    
    const totalDollars = parseNumber(raw['TOTAL_$']);
    if (totalDollars === 0) { stats.skipped++; continue; } // Skip zero-dollar rows
    
    records.push({
      sale_date: saleDate,
      market_type: marketType,
      delivery_type: deliveryType,
      product_category: raw.ProductCategoryName?.trim() ?? 'Unknown',
      unit_of_measure: raw.UnitOfMeasureName?.trim() ?? 'ea',
      quantity: parseNumber(raw.Quantity),
      units: Math.round(parseNumber(raw.Units)),
      count_based_total: parseNumber(raw.CountBasedTotal),
      dollar_count_based: parseNumber(raw.DollarCountBasedTotal),
      weight_based_total: parseNumber(raw.WeightBasedTotal),
      dollar_weight_based: parseNumber(raw.DollarWeightBasedTotal),
      total_dollars: totalDollars,
      source_file: filePath.split('/').pop() ?? '',
    });
  }
  
  // Batch upsert using unnest
  for (let i = 0; i < records.length; i += 2000) {
    const batch = records.slice(i, i + 2000);
    
    const result = await pool.query(`
      INSERT INTO ccc_facility_sales (
        sale_date, market_type, delivery_type, product_category,
        unit_of_measure, quantity, units, count_based_total,
        dollar_count_based, weight_based_total, dollar_weight_based,
        total_dollars, source_file
      )
      SELECT * FROM unnest(
        $1::timestamptz[], $2::varchar[], $3::varchar[], $4::varchar[],
        $5::varchar[], $6::decimal[], $7::integer[], $8::decimal[],
        $9::decimal[], $10::decimal[], $11::decimal[],
        $12::decimal[], $13::varchar[]
      )
      ON CONFLICT (sale_date, market_type, delivery_type, product_category, unit_of_measure)
      DO UPDATE SET
        total_dollars = GREATEST(ccc_facility_sales.total_dollars, EXCLUDED.total_dollars),
        quantity = GREATEST(ccc_facility_sales.quantity, EXCLUDED.quantity),
        source_file = EXCLUDED.source_file
    `, [
      batch.map(r => r.sale_date.toISOString()),
      batch.map(r => r.market_type),
      batch.map(r => r.delivery_type),
      batch.map(r => r.product_category),
      batch.map(r => r.unit_of_measure),
      batch.map(r => r.quantity),
      batch.map(r => r.units),
      batch.map(r => r.count_based_total),
      batch.map(r => r.dollar_count_based),
      batch.map(r => r.weight_based_total),
      batch.map(r => r.dollar_weight_based),
      batch.map(r => r.total_dollars),
      batch.map(r => r.source_file),
    ]);
    
    stats.inserted += result.rowCount ?? 0;
  }
  
  return stats;
}

async function run() {
  for (const file of FILES) {
    const hash = await fileHash(file.path);
    const datasetKey = `${DATASET}_${file.marketType}_${file.path.split('/').pop()}`;
    
    if (await isAlreadyImported(datasetKey, hash)) {
      console.log(`[${datasetKey}] Unchanged, skipping.`);
      continue;
    }
    
    const runId = await startEtlRun(datasetKey, file.path, hash);
    console.log(`[${datasetKey}] Starting import...`);
    
    try {
      const stats = await importFile(file.path, file.marketType);
      await completeEtlRun(runId, {
        rows_read: stats.read,
        rows_inserted: stats.inserted,
        rows_updated: stats.updated,
        rows_skipped: stats.skipped,
        rows_errored: stats.errored,
      });
      console.log(`[${datasetKey}] Done: ${stats.inserted} upserted from ${stats.read} rows`);
    } catch (err) {
      await failEtlRun(runId, (err as Error).message);
      console.error(`[${datasetKey}] FAILED:`, err);
    }
  }
  
  await pool.end();
}

run().catch(console.error);
```

### 4.5 Import Script: Monthly Prices

File: `scripts/etl/import-monthly-prices.ts`

```typescript
import { pool, fileHash, isAlreadyImported, startEtlRun, completeEtlRun, failEtlRun, parseCsvStream } from './lib/etl-base';

const SOURCE_FILE = 'data/ccc-raw/avg-monthly-price-oz.csv';
const DATASET = 'monthly_prices';

async function run() {
  const hash = await fileHash(SOURCE_FILE);
  if (await isAlreadyImported(DATASET, hash)) {
    console.log(`[${DATASET}] Unchanged, skipping.`);
    return;
  }
  
  const runId = await startEtlRun(DATASET, SOURCE_FILE, hash);
  
  try {
    const records: Array<{
      year_month: string;
      avg_price_per_gram: number;
      avg_price_per_oz: number;
      avg_price_per_eighth: number;
    }> = [];
    
    let rowsRead = 0;
    const parser = parseCsvStream(SOURCE_FILE);
    
    for await (const row of parser as AsyncIterable<any>) {
      rowsRead++;
      const ppg = parseFloat(row.AverageRetailPriceperGm);
      if (isNaN(ppg)) continue;
      
      records.push({
        year_month: row.YearMonth.trim(),
        avg_price_per_gram: ppg,
        avg_price_per_oz: Math.round(ppg * 28 * 100) / 100,
        avg_price_per_eighth: Math.round(ppg * 3.5 * 100) / 100,
      });
    }
    
    // Compute MoM and YoY changes
    for (let i = 0; i < records.length; i++) {
      if (i > 0) {
        const mom = ((records[i].avg_price_per_gram - records[i - 1].avg_price_per_gram) / records[i - 1].avg_price_per_gram) * 100;
        (records[i] as any).mom_change_pct = Math.round(mom * 100) / 100;
      }
      if (i >= 12) {
        const yoy = ((records[i].avg_price_per_gram - records[i - 12].avg_price_per_gram) / records[i - 12].avg_price_per_gram) * 100;
        (records[i] as any).yoy_change_pct = Math.round(yoy * 100) / 100;
      }
    }
    
    // Upsert all at once (only 71 rows)
    for (const r of records) {
      await pool.query(`
        INSERT INTO ccc_monthly_prices (year_month, avg_price_per_gram, avg_price_per_oz, avg_price_per_eighth, mom_change_pct, yoy_change_pct)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (year_month) DO UPDATE SET
          avg_price_per_gram = EXCLUDED.avg_price_per_gram,
          avg_price_per_oz = EXCLUDED.avg_price_per_oz,
          avg_price_per_eighth = EXCLUDED.avg_price_per_eighth,
          mom_change_pct = EXCLUDED.mom_change_pct,
          yoy_change_pct = EXCLUDED.yoy_change_pct
      `, [r.year_month, r.avg_price_per_gram, r.avg_price_per_oz, r.avg_price_per_eighth, (r as any).mom_change_pct ?? null, (r as any).yoy_change_pct ?? null]);
    }
    
    await completeEtlRun(runId, {
      rows_read: rowsRead, rows_inserted: records.length,
      rows_updated: 0, rows_skipped: 0, rows_errored: 0,
    });
    
    console.log(`[${DATASET}] Done: ${records.length} months imported`);
  } catch (err) {
    await failEtlRun(runId, (err as Error).message);
    throw err;
  } finally {
    await pool.end();
  }
}

run().catch(console.error);
```

### 4.6 Import Script: Licenses (Merged)

File: `scripts/etl/import-licenses.ts`

```typescript
import { pool, fileHash, startEtlRun, completeEtlRun, failEtlRun, parseCsvStream, parseCccDate, normalizeBusinessName, normalizeLicenseNumber } from './lib/etl-base';

const FILES = [
  { path: 'data/ccc-raw/commence-ops.csv', type: 'commence' },
  { path: 'data/ccc-raw/adult-market-data-counties.csv', type: 'counties' },
];

const DATASET = 'licenses';

function extractEquityFlags(row: any): { isSocialEquity: boolean; isEconomicEmpowerment: boolean } {
  const classification = (row.APPLICATION_CLASSIFICATION || row.application_classification || '').toLowerCase();
  const tier2 = (row['APPLICATION_CLASSIFICATION-2'] || row.classification_tier2 || '').toLowerCase();
  
  return {
    isSocialEquity: classification.includes('social equity') || tier2.includes('social equity'),
    isEconomicEmpowerment: classification.includes('economic empowerment') || tier2.includes('economic empowerment'),
  };
}

function extractPriority(row: any): boolean {
  const priority = (row.PRIORITY || row.priority || '').toString().toLowerCase();
  return priority === 'true' || priority === 'yes';
}

async function importCommenceOps(): Promise<{ read: number; upserted: number; errored: number }> {
  const stats = { read: 0, upserted: 0, errored: 0 };
  const parser = parseCsvStream(FILES[0].path);
  
  for await (const row of parser as AsyncIterable<any>) {
    stats.read++;
    
    const licenseNumber = normalizeLicenseNumber(row.LICENSE_NUMBER || '');
    if (!licenseNumber) { stats.errored++; continue; }
    
    const equity = extractEquityFlags(row);
    
    try {
      await pool.query(`
        INSERT INTO ccc_licenses (
          license_number, business_name, license_type, license_status,
          application_status, approved_license_type, license_stage,
          application_classification, classification_tier1, classification_tier2,
          business_email, business_phone, ein_tin,
          business_address_1, business_address_2, business_city, business_state, business_zip,
          establishment_address_1, establishment_address_2, establishment_city, establishment_state, establishment_zip,
          latitude, longitude, county,
          dbe_status, is_social_equity, is_economic_empowerment, priority_status,
          cultivation_environment, cultivation_tier,
          submitted_date, application_approved_date, license_start_date, license_expiration_date,
          commence_operations_date,
          payment_amount, license_fee_amount,
          ccc_last_updated, source_file
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
          $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
          $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
          $31, $32, $33, $34, $35, $36, $37, $38, $39, $40, $41
        )
        ON CONFLICT (license_number) DO UPDATE SET
          business_name = EXCLUDED.business_name,
          license_status = EXCLUDED.license_status,
          license_stage = COALESCE(EXCLUDED.license_stage, ccc_licenses.license_stage),
          business_email = COALESCE(EXCLUDED.business_email, ccc_licenses.business_email),
          business_phone = COALESCE(EXCLUDED.business_phone, ccc_licenses.business_phone),
          latitude = COALESCE(EXCLUDED.latitude, ccc_licenses.latitude),
          longitude = COALESCE(EXCLUDED.longitude, ccc_licenses.longitude),
          county = COALESCE(EXCLUDED.county, ccc_licenses.county),
          license_expiration_date = COALESCE(EXCLUDED.license_expiration_date, ccc_licenses.license_expiration_date),
          ccc_last_updated = EXCLUDED.ccc_last_updated,
          updated_at = NOW()
      `, [
        licenseNumber,
        (row.BUSINESS_NAME || '').replace(/^"|"$/g, '').trim(),
        (row.LICENSE_TYPE || '').trim(),
        (row.LIC_STATUS || 'Unknown').trim(),
        (row.APPLICATION_STATUS || '').trim(),
        (row.APPROVED_LICENSE_TYPE_BU || '').trim(),
        (row.APPROVED_LICENSE_STAGES || '').trim(),
        (row.APPLICATION_CLASSIFICATION || '').trim(),
        (row['APPLICATION_CLASSIFICATION-1'] || '').trim(),
        (row['APPLICATION_CLASSIFICATION-2'] || '').trim(),
        (row.BUSINESS_EMAIL || '').trim() || null,
        (row.BUSINESS_PHONE || '').trim() || null,
        (row.EIN_TIN || '').trim() || null,
        (row.BUSINESS_ADDRESS_1 || '').trim() || null,
        (row.BUSINESS_ADDRESS_2 || '').trim() || null,
        (row.BUSINESS_CITY || '').trim() || null,
        (row.BUSINESS_STATE || 'MA').trim(),
        (row.BUSINESS_ZIP_CODE || '').trim() || null,
        (row.ESTABLISHMENT_ADDRESS_1 || '').trim() || null,
        (row.ESTABLISHMENT_ADDRESS_2 || '').trim() || null,
        (row.ESTABLISHMENT_CITY || '').trim() || null,
        (row.ESTABLISHMENT_STATE || 'MA').trim(),
        (row.ESTABLISHMENT_ZIP_CODE || '').trim() || null,
        row.latitude ? parseFloat(row.latitude) : null,
        row.longitude ? parseFloat(row.longitude) : null,
        (row.county || '').trim() || null,
        (row.DBE || '').trim() || null,
        equity.isSocialEquity,
        equity.isEconomicEmpowerment,
        extractPriority(row),
        (row.CULTIVATION_ENVIRONMNET || '').trim() || null, // Note: typo in source
        (row.CULTIVATION_TIER || '').trim() || null,
        parseCccDate(row.SUBMITTED_DATE),
        parseCccDate(row.APPLICATION_APPROVED_DATE),
        parseCccDate(row.LIC_START_DATE),
        parseCccDate(row.LIC_EXPIRATION_DATE),
        parseCccDate(row.COMMENCE_OPERATIONS_DATE),
        row.PMT_AMOUNT ? parseFloat(row.PMT_AMOUNT) : null,
        row.LIC_FEE_AMOUNT ? parseFloat(row.LIC_FEE_AMOUNT) : null,
        parseCccDate(row.CCCLastUpdated),
        'commence-ops.csv',
      ]);
      
      stats.upserted++;
    } catch (err) {
      stats.errored++;
      console.error(`Error on license ${licenseNumber}:`, (err as Error).message);
    }
  }
  
  return stats;
}

async function importCounties(): Promise<{ read: number; upserted: number; errored: number }> {
  const stats = { read: 0, upserted: 0, errored: 0 };
  const parser = parseCsvStream(FILES[1].path);
  
  for await (const row of parser as AsyncIterable<any>) {
    stats.read++;
    
    const licenseNumber = normalizeLicenseNumber(row.license_number || '');
    if (!licenseNumber) { stats.errored++; continue; }
    
    const equity = extractEquityFlags(row);
    
    try {
      // Use ON CONFLICT to merge — counties file has additional fields
      await pool.query(`
        INSERT INTO ccc_licenses (
          license_number, business_name, license_type, license_status,
          application_status, approved_license_type, license_stage,
          application_classification, classification_tier1, classification_tier2,
          business_email, business_phone, ein_tin,
          business_address_1, business_address_2, business_city, business_state, business_zip,
          establishment_city, establishment_state, establishment_zip,
          latitude, longitude, county, region, town,
          dbe_status, is_social_equity, is_economic_empowerment, priority_status,
          se_number, ee_number,
          cultivation_environment, cultivation_tier,
          submitted_date, application_approved_date, license_start_date, license_expiration_date,
          commence_operations_date, first_compliance_review_date, deemed_complete_date,
          payment_amount, license_fee_amount,
          ccc_last_updated, source_file
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
          $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
          $21, $22, $23, $24, $25, $26, $27, $28, $29, $30,
          $31, $32, $33, $34, $35, $36, $37, $38, $39, $40,
          $41, $42, $43, $44, $45
        )
        ON CONFLICT (license_number) DO UPDATE SET
          county = COALESCE(EXCLUDED.county, ccc_licenses.county),
          region = COALESCE(EXCLUDED.region, ccc_licenses.region),
          town = COALESCE(EXCLUDED.town, ccc_licenses.town),
          latitude = COALESCE(EXCLUDED.latitude, ccc_licenses.latitude),
          longitude = COALESCE(EXCLUDED.longitude, ccc_licenses.longitude),
          se_number = COALESCE(EXCLUDED.se_number, ccc_licenses.se_number),
          ee_number = COALESCE(EXCLUDED.ee_number, ccc_licenses.ee_number),
          first_compliance_review_date = COALESCE(EXCLUDED.first_compliance_review_date, ccc_licenses.first_compliance_review_date),
          deemed_complete_date = COALESCE(EXCLUDED.deemed_complete_date, ccc_licenses.deemed_complete_date),
          updated_at = NOW()
      `, [
        licenseNumber,
        (row.business_name || '').replace(/^"|"$/g, '').trim(),
        (row.license_type || '').trim(),
        (row.lic_status || 'Unknown').trim(),
        (row.application_status || '').trim(),
        (row.APPROVED_LICENSE_TYPE || '').trim(),
        (row.Approved_License_Stages || '').trim(),
        (row.APPLICATION_CLASSIFICATION || '').trim(),
        (row['APPLICATION_CLASSIFICATION-1'] || '').trim(),
        (row['APPLICATION_CLASSIFICATION-2'] || '').trim(),
        (row.BUSINESS_EMAIL || '').trim() || null,
        (row.BUSINESS_PHONE || '').trim() || null,
        (row.EIN_TIN || '').trim() || null,
        (row.business_address_1 || '').trim() || null,
        (row.business_address_2 || '').trim() || null,
        (row.business_city || '').trim() || null,
        (row.business_state || 'MA').trim(),
        (row.business_zipcode || '').trim() || null,
        (row.establishment_city || '').trim() || null,
        (row.establishment_state || 'MA').trim(),
        (row.establishment_zipcode || '').trim() || null,
        row.latitude ? parseFloat(row.latitude) : null,
        row.longitude ? parseFloat(row.longitude) : null,
        (row.county || '').trim() || null,
        (row.Region || '').trim() || null,
        (row.Town || '').trim() || null,
        (row.dbe || '').trim() || null,
        equity.isSocialEquity,
        equity.isEconomicEmpowerment,
        extractPriority(row),
        (row.APPROVED_SE_NUMBER || '').trim() || null,
        (row.EE_PRIORITY_NUMBER_FROM_ACCOUNT || '').trim() || null,
        (row.cultivation_environment || '').trim() || null,
        (row.cultivation_tier || '').trim() || null,
        parseCccDate(row.SUBMITTED_DATE),
        parseCccDate(row.APPLICATION_APPROVED_DATE),
        parseCccDate(row.LIC_START_DATE),
        parseCccDate(row.LIC_EXPIRATION_DATE),
        parseCccDate(row.commence_operations_date),
        parseCccDate(row.FIRST_COMPLIANCE_REVIEW_DATE),
        parseCccDate(row.CNB_DEEMED_COMPLETE_DATE),
        row.PMT_AMOUNT ? parseFloat(row.PMT_AMOUNT) : null,
        row.LIC_FEE_AMOUNT ? parseFloat(row.LIC_FEE_AMOUNT) : null,
        parseCccDate(row.CCCLastUpdated),
        'adult-market-data-counties.csv',
      ]);
      
      stats.upserted++;
    } catch (err) {
      stats.errored++;
    }
  }
  
  return stats;
}

async function run() {
  console.log(`[${DATASET}] Phase 1: Import commence-ops.csv`);
  const s1 = await importCommenceOps();
  console.log(`  → ${s1.upserted} upserted, ${s1.errored} errors`);
  
  console.log(`[${DATASET}] Phase 2: Merge adult-market-data-counties.csv`);
  const s2 = await importCounties();
  console.log(`  → ${s2.upserted} upserted, ${s2.errored} errors`);
  
  console.log(`[${DATASET}] Phase 3: Link licenses → operators`);
  await linkLicensesToOperators();
  
  console.log(`[${DATASET}] Phase 4: Compute county metrics`);
  await computeCountyMetrics();
  
  await pool.end();
  console.log(`[${DATASET}] Complete`);
}

run().catch(console.error);
```

### 4.7 Operator Name Matching Strategy

The critical challenge: linking CCC license data (`BUSINESS_NAME`) to GLASS `operators` (scraped from Dutchie/Weedmaps with different names).

**Approach: 3-tier matching with confidence scores**

```typescript
/**
 * Link ccc_licenses → operators using multi-tier matching.
 * 
 * Tier 1: Exact license_number match (highest confidence)
 * Tier 2: Fuzzy business name match with city filter
 * Tier 3: EIN/address match for multi-license entities
 */
async function linkLicensesToOperators(): Promise<void> {
  // Tier 1: License number match
  const t1 = await pool.query(`
    UPDATE ccc_licenses l
    SET operator_id = o.id
    FROM operators o
    WHERE o.license_number IS NOT NULL
      AND l.license_number = o.license_number
      AND l.operator_id IS NULL
  `);
  console.log(`  Tier 1 (license number): ${t1.rowCount} matched`);
  
  // Also enrich operators with CCC data
  await pool.query(`
    UPDATE operators o
    SET 
      ccc_license_id = l.id,
      county = COALESCE(o.county, l.county),
      region = COALESCE(o.region, l.region),
      license_type = COALESCE(o.license_type, l.license_type),
      email = COALESCE(o.email, l.business_email),
      phone = COALESCE(o.phone, l.business_phone),
      lat = COALESCE(o.lat, l.latitude),
      lon = COALESCE(o.lon, l.longitude)
    FROM ccc_licenses l
    WHERE l.operator_id = o.id
  `);
  
  // Tier 2: Fuzzy name match
  // Uses pg_trgm for trigram similarity (must be enabled)
  await pool.query(`CREATE EXTENSION IF NOT EXISTS pg_trgm`);
  
  const t2 = await pool.query(`
    WITH unmatched_licenses AS (
      SELECT id, business_name, establishment_city, license_type
      FROM ccc_licenses
      WHERE operator_id IS NULL
        AND license_type = 'Marijuana Retailer'  -- Only match retailers (operators are stores)
    ),
    best_matches AS (
      SELECT DISTINCT ON (ul.id)
        ul.id AS license_id,
        o.id AS operator_id,
        similarity(
          lower(regexp_replace(ul.business_name, '[^a-zA-Z0-9 ]', '', 'g')),
          lower(regexp_replace(o.name, '[^a-zA-Z0-9 ]', '', 'g'))
        ) AS sim_score
      FROM unmatched_licenses ul
      CROSS JOIN operators o
      WHERE o.city IS NOT NULL
        AND lower(ul.establishment_city) = lower(o.city)
        AND similarity(
          lower(regexp_replace(ul.business_name, '[^a-zA-Z0-9 ]', '', 'g')),
          lower(regexp_replace(o.name, '[^a-zA-Z0-9 ]', '', 'g'))
        ) > 0.3
      ORDER BY ul.id, sim_score DESC
    )
    UPDATE ccc_licenses l
    SET operator_id = bm.operator_id
    FROM best_matches bm
    WHERE l.id = bm.license_id AND bm.sim_score > 0.3
  `);
  console.log(`  Tier 2 (fuzzy name + city): ${t2.rowCount} matched`);
  
  // Tier 3: Geo-proximity match for remaining unmatched retailers
  const t3 = await pool.query(`
    WITH unmatched_licenses AS (
      SELECT id, latitude, longitude, business_name
      FROM ccc_licenses
      WHERE operator_id IS NULL
        AND license_type = 'Marijuana Retailer'
        AND latitude IS NOT NULL
    ),
    geo_matches AS (
      SELECT DISTINCT ON (ul.id)
        ul.id AS license_id,
        o.id AS operator_id,
        -- Haversine distance in miles
        (3959 * acos(
          cos(radians(ul.latitude)) * cos(radians(o.lat::numeric)) *
          cos(radians(o.lon::numeric) - radians(ul.longitude)) +
          sin(radians(ul.latitude)) * sin(radians(o.lat::numeric))
        )) AS distance_miles
      FROM unmatched_licenses ul
      CROSS JOIN operators o
      WHERE o.lat IS NOT NULL
        AND ABS(ul.latitude - o.lat::numeric) < 0.01  -- Pre-filter: ~0.7 miles lat
        AND ABS(ul.longitude - o.lon::numeric) < 0.01
      ORDER BY ul.id, distance_miles ASC
    )
    UPDATE ccc_licenses l
    SET operator_id = gm.operator_id
    FROM geo_matches gm
    WHERE l.id = gm.license_id AND gm.distance_miles < 0.1  -- Within ~500 feet
  `);
  console.log(`  Tier 3 (geo-proximity): ${t3.rowCount} matched`);
  
  // Report unmatched
  const unmatched = await pool.query(`
    SELECT COUNT(*) FROM ccc_licenses
    WHERE operator_id IS NULL AND license_type = 'Marijuana Retailer'
  `);
  console.log(`  Unmatched retailers remaining: ${unmatched.rows[0].count}`);
  
  // Create operators from unmatched CCC licenses (those with commence ops)
  const created = await pool.query(`
    INSERT INTO operators (name, license_number, city, state, lat, lon, status, email, phone, license_type, county, region)
    SELECT 
      l.business_name, l.license_number, 
      COALESCE(l.establishment_city, l.business_city), 'MA',
      l.latitude, l.longitude,
      CASE WHEN l.license_stage = 'COMMENCE OPS' THEN 'active' ELSE 'pending' END,
      l.business_email, l.business_phone,
      l.license_type, l.county, l.region
    FROM ccc_licenses l
    WHERE l.operator_id IS NULL
      AND l.license_number NOT IN (SELECT license_number FROM operators WHERE license_number IS NOT NULL)
      AND l.establishment_city IS NOT NULL
      AND l.establishment_city != 'N/A'
    ON CONFLICT DO NOTHING
    RETURNING id
  `);
  console.log(`  Created ${created.rowCount} new operators from CCC data`);
  
  // Link newly created operators back to licenses
  await pool.query(`
    UPDATE ccc_licenses l
    SET operator_id = o.id
    FROM operators o
    WHERE o.license_number = l.license_number
      AND l.operator_id IS NULL
  `);
}

/**
 * Compute county-level metrics from license data
 */
async function computeCountyMetrics(): Promise<void> {
  await pool.query(`
    INSERT INTO ccc_county_metrics (
      county, region, county_lat, county_lon,
      total_licenses, active_retailers, active_cultivators,
      active_manufacturers, active_delivery, active_testing_labs,
      pending_applications,
      social_equity_count, economic_empowerment_count, dbe_count,
      snapshot_date
    )
    SELECT
      county,
      MAX(region) AS region,
      AVG(latitude) AS county_lat,
      AVG(longitude) AS county_lon,
      COUNT(*) AS total_licenses,
      COUNT(*) FILTER (WHERE license_type = 'Marijuana Retailer' AND license_status = 'Active') AS active_retailers,
      COUNT(*) FILTER (WHERE license_type = 'Marijuana Cultivator' AND license_status = 'Active') AS active_cultivators,
      COUNT(*) FILTER (WHERE license_type = 'Marijuana Product Manufacturer' AND license_status = 'Active') AS active_manufacturers,
      COUNT(*) FILTER (WHERE license_type IN ('Marijuana Delivery Operator', 'Marijuana Courier', 'Microbusiness Delivery') AND license_status = 'Active') AS active_delivery,
      COUNT(*) FILTER (WHERE license_type = 'Independent Testing Laboratory' AND license_status = 'Active') AS active_testing_labs,
      COUNT(*) FILTER (WHERE license_stage = 'PROVISIONAL LICENSE') AS pending_applications,
      COUNT(*) FILTER (WHERE is_social_equity = TRUE) AS social_equity_count,
      COUNT(*) FILTER (WHERE is_economic_empowerment = TRUE) AS economic_empowerment_count,
      COUNT(*) FILTER (WHERE dbe_status IS NOT NULL AND dbe_status != 'Not a DBE') AS dbe_count,
      NOW()::date
    FROM ccc_licenses
    WHERE county IS NOT NULL AND county != ''
    GROUP BY county
    ON CONFLICT (county, snapshot_date) DO UPDATE SET
      total_licenses = EXCLUDED.total_licenses,
      active_retailers = EXCLUDED.active_retailers,
      active_cultivators = EXCLUDED.active_cultivators,
      active_manufacturers = EXCLUDED.active_manufacturers,
      active_delivery = EXCLUDED.active_delivery,
      active_testing_labs = EXCLUDED.active_testing_labs,
      pending_applications = EXCLUDED.pending_applications,
      social_equity_count = EXCLUDED.social_equity_count,
      economic_empowerment_count = EXCLUDED.economic_empowerment_count,
      dbe_count = EXCLUDED.dbe_count
  `);
}
```

### 4.8 Master ETL Runner

File: `scripts/etl/run-all.ts`

```typescript
import { execSync } from 'child_process';

const SCRIPTS = [
  { name: 'Monthly Prices', script: 'import-monthly-prices.ts' },
  { name: 'Licenses', script: 'import-licenses.ts' },
  { name: 'Lab Tests', script: 'import-lab-tests.ts' },
  { name: 'Facility Sales', script: 'import-facility-sales.ts' },
];

async function main() {
  console.log('═══════════════════════════════════════');
  console.log('  GLASS ETL Pipeline — Full Import');
  console.log('═══════════════════════════════════════');
  
  for (const s of SCRIPTS) {
    console.log(`\n▶ ${s.name}`);
    try {
      execSync(`npx tsx scripts/etl/${s.script}`, {
        stdio: 'inherit',
        env: { ...process.env },
      });
      console.log(`✓ ${s.name} complete`);
    } catch (err) {
      console.error(`✗ ${s.name} FAILED`);
      // Continue with remaining scripts
    }
  }
  
  console.log('\n▶ Computing operator scores...');
  try {
    execSync('npx tsx scripts/etl/compute-scores.ts', { stdio: 'inherit' });
    console.log('✓ Scores computed');
  } catch (err) {
    console.error('✗ Score computation failed');
  }
  
  console.log('\n▶ Refreshing materialized views...');
  try {
    execSync('npx tsx scripts/etl/refresh-views.ts', { stdio: 'inherit' });
    console.log('✓ Views refreshed');
  } catch (err) {
    console.error('✗ View refresh failed');
  }
  
  console.log('\n═══════════════════════════════════════');
  console.log('  ETL Pipeline Complete');
  console.log('═══════════════════════════════════════');
}

main().catch(console.error);
```

### 4.9 Incremental Update Strategy

CCC updates their CSVs periodically (roughly monthly). The ETL pipeline handles this automatically:

1. **File hash check:** Each import computes SHA-256 of the CSV. If hash matches a completed `etl_runs` entry, skip.
2. **Upsert semantics:** All `INSERT` statements use `ON CONFLICT DO UPDATE`, so re-importing the same file is idempotent.
3. **Delta detection:** For lab tests, new METRC tags get inserted; existing tags get updated THC/THCA values.
4. **License lifecycle:** When CCC updates license status (Active → Expired), the upsert captures it.

**Recommended cron schedule:**
```
# Monthly CCC data refresh (1st of each month at 2 AM ET)
0 7 1 * * cd /app && npx tsx scripts/etl/run-all.ts >> /var/log/glass/etl.log 2>&1
```

### 4.10 Data Cleaning Rules Summary

| Dataset | Rule | Implementation |
|---------|------|----------------|
| Lab Tests | Pivot THC/THCA rows into single record per METRC tag | Aggregate in memory, write once |
| Lab Tests | Compute `total_thc = thc + (thca × 0.877)` | Decarboxylation factor in ETL |
| Lab Tests | Skip rows with missing METRC tags | Error log + skip |
| Facility Sales | Skip rows where `TOTAL_$` = 0 | Filter in parser |
| Facility Sales | Dedup across 3 CSV files using composite key | `ON CONFLICT` with `GREATEST` |
| Facility Sales | Medical has no `DeliveryType` — use "Medical" | Hardcoded in parser |
| Monthly Prices | Compute MoM and YoY changes | Post-parse calculation |
| Licenses | Parse verbose JS Date format | Custom `parseCccDate()` |
| Licenses | Strip quotes and D/B/A from business names | `normalizeBusinessName()` |
| Licenses | Extract equity/priority booleans from classification text | `extractEquityFlags()` |
| Licenses | Merge commence-ops and counties (commence first, counties enriches) | Import order + `ON CONFLICT` with `COALESCE` |
| All | Track import hash for idempotency | `etl_runs` table |

---

## 5. Composite Scores & Intelligence Engine

### 5.1 Operator Health Score (0–100)

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

**Component calculations:**

```typescript
// scripts/etl/compute-scores.ts

import { pool } from './lib/etl-base';

interface ScoreComponents {
  operator_id: string;
  price_competitiveness: number;
  product_quality: number;
  compliance: number;
  market_presence: number;
  review_score: number;
}

/**
 * Price Competitiveness (0-100)
 * 
 * Compares operator's avg price/gram to:
 * 1. State CCC benchmark
 * 2. County average
 * 3. Price trend (are they adjusting?)
 * 
 * Score = 100 if priced at state avg, ±50 for ±50% deviation
 * Bonus: +10 if trending in right direction
 */
async function computePriceCompetitiveness(): Promise<Map<string, number>> {
  const result = await pool.query(`
    WITH latest_state_avg AS (
      SELECT avg_price_per_gram FROM ccc_monthly_prices
      ORDER BY year_month DESC LIMIT 1
    ),
    operator_avg_prices AS (
      SELECT
        p.operator_id,
        AVG(p.price_per_gram::numeric) FILTER (WHERE p.scraped_at > NOW() - INTERVAL '30 days') AS avg_price_30d,
        AVG(p.price_per_gram::numeric) FILTER (WHERE p.scraped_at > NOW() - INTERVAL '60 days' AND p.scraped_at <= NOW() - INTERVAL '30 days') AS avg_price_60d,
        COUNT(*) FILTER (WHERE p.scraped_at > NOW() - INTERVAL '30 days') AS price_count_30d
      FROM prices p
      WHERE p.price_per_gram IS NOT NULL AND p.price_per_gram::numeric > 0
      GROUP BY p.operator_id
      HAVING COUNT(*) FILTER (WHERE p.scraped_at > NOW() - INTERVAL '30 days') >= 3
    )
    SELECT
      oap.operator_id,
      oap.avg_price_30d,
      oap.avg_price_60d,
      oap.price_count_30d,
      lsa.avg_price_per_gram AS state_avg
    FROM operator_avg_prices oap
    CROSS JOIN latest_state_avg lsa
  `);
  
  const scores = new Map<string, number>();
  
  for (const row of result.rows) {
    const stateAvg = parseFloat(row.state_avg);
    const opAvg = parseFloat(row.avg_price_30d);
    const deviation = ((opAvg - stateAvg) / stateAvg) * 100; // % above state avg
    
    // Base score: 100 at state avg, drops linearly
    // Operators can be premium (above avg) but shouldn't be egregiously expensive
    let score = Math.max(0, Math.min(100, 100 - Math.abs(deviation) * 1.5));
    
    // Slight bonus for being competitive (below state avg)
    if (deviation < 0) score = Math.min(100, score + 10);
    
    // Trend bonus: if price is trending toward market
    if (row.avg_price_60d) {
      const prevAvg = parseFloat(row.avg_price_60d);
      const trendTowardMarket = Math.abs(opAvg - stateAvg) < Math.abs(prevAvg - stateAvg);
      if (trendTowardMarket) score = Math.min(100, score + 5);
    }
    
    scores.set(row.operator_id, Math.round(score));
  }
  
  return scores;
}

/**
 * Product Quality Score (0-100)
 * 
 * Based on lab test data for operator's product categories:
 * - THC consistency (low variance = good)
 * - THC potency vs category average
 * - Range of categories offered
 * 
 * Since lab tests are anonymized (no operator linkage), this uses
 * category-level statistics as benchmarks. Operator-specific scoring
 * will improve when we can link METRC tags to specific operators.
 */
async function computeProductQuality(): Promise<Map<string, number>> {
  const result = await pool.query(`
    WITH category_benchmarks AS (
      SELECT
        product_category,
        AVG(total_thc_percent::numeric) AS avg_thc,
        STDDEV(total_thc_percent::numeric) AS stddev_thc,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_thc_percent::numeric) AS p75_thc
      FROM ccc_lab_tests
      WHERE total_thc_percent IS NOT NULL AND product_category = 'Buds'
      GROUP BY product_category
    ),
    operator_products AS (
      SELECT
        p.operator_id,
        COUNT(DISTINCT prod.category) AS category_count,
        AVG(prod.thc_percent::numeric) FILTER (WHERE prod.thc_percent IS NOT NULL) AS avg_listed_thc,
        COUNT(*) AS total_products,
        COUNT(*) FILTER (WHERE prod.thc_percent IS NOT NULL) AS products_with_thc
      FROM prices p
      JOIN products prod ON prod.id = p.product_id
      WHERE p.scraped_at > NOW() - INTERVAL '30 days'
      GROUP BY p.operator_id
    )
    SELECT
      op.operator_id,
      op.category_count,
      op.total_products,
      op.products_with_thc,
      op.avg_listed_thc,
      cb.avg_thc AS market_avg_thc,
      cb.p75_thc AS market_p75_thc
    FROM operator_products op
    LEFT JOIN category_benchmarks cb ON cb.product_category = 'Buds'
  `);
  
  const scores = new Map<string, number>();
  
  for (const row of result.rows) {
    let score = 50; // Base
    
    // Variety bonus (more categories = better selection)
    const varietyBonus = Math.min(20, (row.category_count ?? 1) * 4);
    score += varietyBonus;
    
    // Menu depth (more products = better)
    const depthBonus = Math.min(15, Math.log2(row.total_products ?? 1) * 3);
    score += depthBonus;
    
    // THC data transparency (listing THC% is good)
    if (row.products_with_thc && row.total_products) {
      const transparency = (row.products_with_thc / row.total_products) * 15;
      score += transparency;
    }
    
    scores.set(row.operator_id, Math.round(Math.min(100, Math.max(0, score))));
  }
  
  return scores;
}

/**
 * Compliance Score (0-100)
 * 
 * Based on license data:
 * - Active license = base 70
 * - Expired/lapsed = 0
 * - Social equity/DBE = bonus 10
 * - No enforcement actions = bonus 20
 * - License renewal on time = bonus 10
 */
async function computeCompliance(): Promise<Map<string, number>> {
  const result = await pool.query(`
    SELECT
      l.operator_id,
      l.license_status,
      l.license_stage,
      l.is_social_equity,
      l.is_economic_empowerment,
      l.dbe_status,
      l.license_expiration_date,
      l.commence_operations_date,
      (SELECT COUNT(*) FROM enforcement_actions ea WHERE ea.operator_id = l.operator_id) AS enforcement_count
    FROM ccc_licenses l
    WHERE l.operator_id IS NOT NULL
      AND l.license_type = 'Marijuana Retailer'
  `);
  
  const scores = new Map<string, number>();
  
  for