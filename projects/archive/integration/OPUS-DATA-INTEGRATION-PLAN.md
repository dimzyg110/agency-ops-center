# GLASS Data Integration Plan — Opus Blueprint

**Author:** Data Architecture Subagent (Opus 4.6)
**Date:** 2026-02-12
**Status:** READY FOR IMPLEMENTATION

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Part 1: Database Schema Design](#part-1-database-schema-design)
3. [Part 2: Import Pipeline Architecture](#part-2-import-pipeline-architecture)
4. [Part 3: Cross-Reference Intelligence](#part-3-cross-reference-intelligence)
5. [Part 4: API Endpoints](#part-4-api-endpoints)
6. [Part 5: Product Impact Map](#part-5-how-each-product-benefits)
7. [Part 6: Implementation Roadmap](#part-6-implementation-roadmap)

---

## 1. Executive Summary

GLASS currently has **100K products**, **117K prices**, and **492 operators** from scraping. The CCC just gave us the entire regulatory backbone: **298K lab tests**, **182K daily sales records**, **773 licensed operators with contact info**, **72 months of official pricing**, and **county-level market data**. This is the difference between "a price comparison tool" and "the Bloomberg Terminal for Massachusetts cannabis."

**The play:** CCC data is the **ground truth**. Our scraped data is the **real-time signal**. Neither alone is sufficient. Together, they create intelligence no one else in this market has.

**Storage estimate:** ~250MB total for all new tables. Railway PostgreSQL handles this trivially.

**Key insight from data sampling:**
- Lab tests have METRC tag IDs (seed-to-sale tracking numbers) — these are the Rosetta Stone connecting CCC regulatory data to physical product
- Facility sales are **statewide aggregates by product category per day** — NOT per-facility. This is market-level data, not operator-level revenue
- The commence-ops CSV has **773 rows with emails, phones, license numbers, and geocoding** — this supersedes our manually-built 492-operator table
- ITD retail/delivery and facility sales CSVs are **identical structure, identical row count (67,334)** — they're the same dataset. Import once.
- Monthly price per ounce shows MA flower crashed from **$14.68/g (Jan 2020) to $4.01/g (Nov 2025)** — a 73% collapse. This is the narrative that sells GLASS subscriptions.

---

## Part 1: Database Schema Design

### Naming Convention
All new CCC tables prefixed with `ccc_` to distinguish regulatory data from scraped data. Existing tables (`operators`, `products`, `prices`) remain untouched — they represent our proprietary scraped intelligence layer.

---

### 1.1 Lab Testing Results — `ccc_lab_tests`

**Source:** `testing-thc-thca.csv` (298,342 data rows)
**Estimated storage:** ~75MB (298K rows × ~250 bytes avg)
**Refresh:** Quarterly (CCC updates this dataset periodically)

```typescript
// Drizzle ORM schema
export const cccLabTests = pgTable('ccc_lab_tests', {
  id: uuid('id').primaryKey().defaultRandom(),
  metrc_tag: varchar('metrc_tag', { length: 50 }).notNull(),
  product_category: varchar('product_category', { length: 50 }).notNull(),
  strain: varchar('strain', { length: 255 }).notNull(),
  test_type: varchar('test_type', { length: 100 }).notNull(),
  test_result: decimal('test_result', { precision: 6, scale: 3 }),
  testing_lab: varchar('testing_lab', { length: 100 }).notNull(),
  test_date: timestamp('test_date', { withTimezone: true }).notNull(),
  test_comment: varchar('test_comment', { length: 500 }),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_ccc_lab_tests_metrc').on(table.metrc_tag),
  index('idx_ccc_lab_tests_strain').on(table.strain),
  index('idx_ccc_lab_tests_category').on(table.product_category),
  index('idx_ccc_lab_tests_date').on(table.test_date),
  index('idx_ccc_lab_tests_type').on(table.test_type),
  index('idx_ccc_lab_tests_lab').on(table.testing_lab),
  index('idx_ccc_lab_tests_result').on(table.test_result),
  // Composite for the THC accuracy cross-reference query
  index('idx_ccc_lab_tests_strain_type_date').on(table.strain, table.test_type, table.test_date),
  // Unique constraint: one test type per METRC tag
  unique('ccc_lab_tests_metrc_type_unique').on(table.metrc_tag, table.test_type),
]);
```

**Data observations:**
- Each METRC tag has exactly 2 rows: one THC%, one THCA% (149,171 each = 298,342 total)
- `product_category` values: `Buds` (261K), `ShakeTrim` (34K), `Plants` (2K), `Concentrate` (450), `InfusedNonEdible` (6), `InfusedEdible` (2)
- Labs are anonymized as `LabA`, `LabB`, etc. — 10 labs total. Top 3 handle 69% of tests.
- Strains are anonymized as `Strain_01`, `Strain_02`, etc. — **this limits direct product matching but still enables statistical analysis by category/time**
- Test results range from 0% to ~35%+ for THC

**Design decisions:**
- Store each row individually (not pivoted) — easier to add CBD, terpene tests later
- `metrc_tag` indexed but NOT foreign-keyed to products — matching is fuzzy, done at query time
- Unique on `(metrc_tag, test_type)` prevents duplicate imports

---

### 1.2 Market Sales (Adult-Use) — `ccc_market_sales`

**Source:** `facility-sales-stats.csv` AND `itd-retail-delivery-sales.csv` (identical — 67,333 data rows)
**Estimated storage:** ~20MB
**Refresh:** Monthly (CCC publishes monthly updates)

```typescript
export const cccMarketSales = pgTable('ccc_market_sales', {
  id: uuid('id').primaryKey().defaultRandom(),
  sale_date: timestamp('sale_date', { withTimezone: true }).notNull(),
  delivery_type: varchar('delivery_type', { length: 50 }).notNull(), // 'Retail', 'Delivery Operators', 'Delivery Couriers'
  product_category: varchar('product_category', { length: 100 }).notNull(),
  unit_of_measure: varchar('unit_of_measure', { length: 20 }).notNull(), // 'ea', 'g'
  quantity: decimal('quantity', { precision: 14, scale: 2 }),
  units: integer('units'),
  count_based_total: decimal('count_based_total', { precision: 14, scale: 2 }),
  dollar_count_based: decimal('dollar_count_based', { precision: 14, scale: 2 }),
  weight_based_total: decimal('weight_based_total', { precision: 14, scale: 2 }),
  dollar_weight_based: decimal('dollar_weight_based', { precision: 14, scale: 2 }),
  total_dollars: decimal('total_dollars', { precision: 14, scale: 2 }).notNull(),
  market_type: varchar('market_type', { length: 20 }).notNull().default('adult_use'),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_ccc_market_sales_date').on(table.sale_date),
  index('idx_ccc_market_sales_category').on(table.product_category),
  index('idx_ccc_market_sales_delivery').on(table.delivery_type),
  index('idx_ccc_market_sales_market').on(table.market_type),
  // Composite for time-series category analysis
  index('idx_ccc_market_sales_date_cat').on(table.sale_date, table.product_category),
  // Composite for delivery channel analysis
  index('idx_ccc_market_sales_date_delivery').on(table.sale_date, table.delivery_type),
  // Prevent duplicate imports
  unique('ccc_market_sales_unique').on(table.sale_date, table.delivery_type, table.product_category, table.market_type),
]);
```

**Data observations:**
- 20 product categories (Buds, Raw Pre-Rolls, Infused Pre-Rolls, Vape Product, Concentrate, Edible, Beverage, Kief, Shake/Trim, etc.)
- 3 delivery types: `Retail` (57%), `Delivery Couriers` (23%), `Delivery Operators` (20%)
- Date range: 2019-01-26 through 2025-09+ (daily granularity)
- Dollar amounts are statewide totals — e.g., Retail Buds on a given day might be $2.5M total across all MA retailers
- Weight-based products (Buds, Shake/Trim) use grams; count-based products (Edibles, Vapes) use 'ea'

**Design decisions:**
- Single table for both adult-use AND medical (discriminated by `market_type`)
- Medical data has slightly different columns (no `DeliveryType`, has `Industry`) — normalize by defaulting delivery_type to `'Retail'` for medical
- The `SalePeriod`, `DataType`, `SalesPeriodType` columns are metadata about the CSV download window — discard them

---

### 1.3 Medical Market Sales — merged into `ccc_market_sales`

**Source:** `medical-facility-stats.csv` (47,647 data rows)
**Decision:** Import into same `ccc_market_sales` table with `market_type = 'medical'`

Medical has these differences from adult-use:
- No `DeliveryType` column → set to `'Retail'` (medical is all dispensary-based)
- `Industry` column = always `'Medical'` → maps to our `market_type`
- Otherwise identical: same product categories, same dollar/weight structure

---

### 1.4 Monthly Price Benchmark — `ccc_monthly_price_benchmark`

**Source:** `avg-monthly-price-oz.csv` (71 data rows)
**Estimated storage:** <1KB (tiny but incredibly valuable)
**Refresh:** Monthly

```typescript
export const cccMonthlyPriceBenchmark = pgTable('ccc_monthly_price_benchmark', {
  id: uuid('id').primaryKey().defaultRandom(),
  year_month: varchar('year_month', { length: 7 }).notNull().unique(), // '2020-01'
  avg_price_per_gram: decimal('avg_price_per_gram', { precision: 6, scale: 2 }).notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_ccc_price_benchmark_month').on(table.year_month),
]);
```

**Data observations:**
- Jan 2020 ($14.68/g) → Nov 2025 ($4.01/g) = **73% price collapse**
- April 2020 anomaly: dropped to $10.15/g (COVID shutdown, only medical open)
- Steepest decline: H2 2022 (from $10.15 to $7.61 — oversupply hitting market)
- Plateauing in 2025 around $4.00-4.20/g — approaching floor

**This is the single most valuable table for the newsletter.** "The official MA price hit $4.01/g this month, down 73% from 2020. Here's what operators in your zip code are charging vs. the state average."

---

### 1.5 Licensed Operators (CCC Master) — `ccc_licensed_operators`

**Source:** `commence-ops.csv` (772 data rows)
**Estimated storage:** ~2MB
**Refresh:** Monthly

```typescript
export const cccLicensedOperators = pgTable('ccc_licensed_operators', {
  id: uuid('id').primaryKey().defaultRandom(),
  business_name: varchar('business_name', { length: 500 }).notNull(),
  license_type: varchar('license_type', { length: 100 }).notNull(),
  license_number: varchar('license_number', { length: 50 }).notNull(),
  ein_tin: varchar('ein_tin', { length: 20 }),
  application_status: varchar('application_status', { length: 50 }),
  approved_license_type: varchar('approved_license_type', { length: 100 }),
  license_status: varchar('license_status', { length: 50 }).notNull(),
  application_classification: varchar('application_classification', { length: 100 }),
  classification_detail_1: varchar('classification_detail_1', { length: 100 }),
  classification_detail_2: varchar('classification_detail_2', { length: 100 }),
  approved_license_stage: varchar('approved_license_stage', { length: 50 }),
  cultivation_environment: varchar('cultivation_environment', { length: 50 }),
  cultivation_tier: varchar('cultivation_tier', { length: 100 }),
  is_priority: boolean('is_priority').default(false),
  dbe_status: varchar('dbe_status', { length: 200 }),
  rmd_priority_status: varchar('rmd_priority_status', { length: 50 }),
  business_email: varchar('business_email', { length: 255 }),
  business_phone: varchar('business_phone', { length: 30 }),
  business_address: text('business_address'),
  business_city: varchar('business_city', { length: 100 }),
  business_state: varchar('business_state', { length: 2 }),
  business_zip: varchar('business_zip', { length: 10 }),
  establishment_address: text('establishment_address'),
  establishment_city: varchar('establishment_city', { length: 100 }),
  establishment_state: varchar('establishment_state', { length: 2 }),
  establishment_zip: varchar('establishment_zip', { length: 10 }),
  lat: decimal('lat', { precision: 10, scale: 8 }),
  lon: decimal('lon', { precision: 11, scale: 8 }),
  county: varchar('county', { length: 100 }),
  submitted_date: timestamp('submitted_date', { withTimezone: true }),
  approved_date: timestamp('approved_date', { withTimezone: true }),
  license_start_date: timestamp('license_start_date', { withTimezone: true }),
  license_expiration_date: timestamp('license_expiration_date', { withTimezone: true }),
  commence_operations_date: timestamp('commence_operations_date', { withTimezone: true }),
  license_fee: decimal('license_fee', { precision: 10, scale: 2 }),
  payment_amount: decimal('payment_amount', { precision: 10, scale: 2 }),
  ccc_last_updated: timestamp('ccc_last_updated', { withTimezone: true }),
  // Link to our operators table (populated by matching script)
  glass_operator_id: uuid('glass_operator_id').references(() => operators.id, { onDelete: 'set null' }),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_ccc_operators_license').on(table.license_number),
  index('idx_ccc_operators_name').on(table.business_name),
  index('idx_ccc_operators_type').on(table.license_type),
  index('idx_ccc_operators_status').on(table.license_status),
  index('idx_ccc_operators_city').on(table.establishment_city),
  index('idx_ccc_operators_county').on(table.county),
  index('idx_ccc_operators_location').on(table.lat, table.lon),
  index('idx_ccc_operators_dbe').on(table.dbe_status),
  index('idx_ccc_operators_glass_link').on(table.glass_operator_id),
  unique('ccc_operators_license_unique').on(table.license_number),
]);
```

**Data observations:**
- 772 records with 53 columns — heavily denormalized CCC export
- License types: Retailer (155), Cultivator (57), Manufacturer (43), Delivery (13), Courier (9), Testing Lab (9), Microbusiness (8), etc.
- License statuses: `FINAL LICENSE` (454), `Active` (274), `Expired` (23), `IN PROCESS` (14), `Surrendered` (7)
- **Already geocoded** — CSV has lat/lon/county columns
- **Has emails and phone numbers** — goldmine for outreach
- The `EIN_TIN` field links multiple licenses to same business entity

**Design decisions:**
- This table does NOT replace `operators` — it augments it. `operators` has scraped data (Dutchie slugs, Weedmaps URLs, menu status). `ccc_licensed_operators` has regulatory data (license dates, fees, DBE status, EIN).
- `glass_operator_id` is the foreign key bridge. A matching script (see Part 2) populates this.
- Store all 772 rows, not just retailers. Cultivators and manufacturers are relevant for the supply chain intelligence, toll processing outreach, and the Virtual Budtender (knowing which brands have their own cultivation vs. buying wholesale).

---

### 1.6 Adult Market County Data — `ccc_county_licenses`

**Source:** `adult-market-data-counties.csv` (1,753 data rows)
**Estimated storage:** ~3MB
**Refresh:** Monthly

```typescript
export const cccCountyLicenses = pgTable('ccc_county_licenses', {
  id: uuid('id').primaryKey().defaultRandom(),
  application_status: varchar('application_status', { length: 50 }),
  license_type: varchar('license_type', { length: 100 }).notNull(),
  application_classification: varchar('application_classification', { length: 100 }),
  classification_detail_1: varchar('classification_detail_1', { length: 100 }),
  classification_detail_2: varchar('classification_detail_2', { length: 100 }),
  approved_license_type: varchar('approved_license_type', { length: 100 }),
  approved_license_stage: varchar('approved_license_stage', { length: 50 }),
  commence_operations_date: timestamp('commence_operations_date', { withTimezone: true }),
  license_status: varchar('license_status', { length: 50 }),
  license_number: varchar('license_number', { length: 50 }).notNull(),
  business_name: varchar('business_name', { length: 500 }).notNull(),
  establishment_city: varchar('establishment_city', { length: 100 }),
  establishment_zip: varchar('establishment_zip', { length: 10 }),
  business_email: varchar('business_email', { length: 255 }),
  business_phone: varchar('business_phone', { length: 30 }),
  business_address: text('business_address'),
  business_city: varchar('business_city', { length: 100 }),
  business_state: varchar('business_state', { length: 2 }),
  business_zip: varchar('business_zip', { length: 10 }),
  ein_tin: varchar('ein_tin', { length: 20 }),
  dbe_status: varchar('dbe_status', { length: 200 }),
  cultivation_environment: varchar('cultivation_environment', { length: 50 }),
  cultivation_tier: varchar('cultivation_tier', { length: 100 }),
  town: varchar('town', { length: 100 }),
  county: varchar('county', { length: 100 }),
  county_lat: decimal('county_lat', { precision: 10, scale: 6 }),
  county_lon: decimal('county_lon', { precision: 11, scale: 6 }),
  region: varchar('region', { length: 100 }),
  lat: decimal('lat', { precision: 10, scale: 8 }),
  lon: decimal('lon', { precision: 11, scale: 8 }),
  se_number: varchar('se_number', { length: 50 }),
  priority: varchar('priority', { length: 100 }),
  fee_waiver: varchar('fee_waiver', { length: 20 }),
  submitted_date: timestamp('submitted_date', { withTimezone: true }),
  approved_date: timestamp('approved_date', { withTimezone: true }),
  license_start_date: timestamp('license_start_date', { withTimezone: true }),
  license_expiration_date: timestamp('license_expiration_date', { withTimezone: true }),
  license_fee: decimal('license_fee', { precision: 10, scale: 2 }),
  payment_amount: decimal('payment_amount', { precision: 10, scale: 2 }),
  ccc_last_updated: timestamp('ccc_last_updated', { withTimezone: true }),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_ccc_county_licenses_county').on(table.county),
  index('idx_ccc_county_licenses_type').on(table.license_type),
  index('idx_ccc_county_licenses_town').on(table.town),
  index('idx_ccc_county_licenses_region').on(table.region),
  index('idx_ccc_county_licenses_license').on(table.license_number),
  index('idx_ccc_county_licenses_status').on(table.license_status),
  unique('ccc_county_licenses_unique').on(table.license_number),
]);
```

**Data observations:**
- 1,753 rows — LARGER than commence-ops (772). This includes all applications, not just commenced operations.
- License types: Retailer (569), Cultivator (422), Manufacturer (337), Delivery Pre-Cert (119), Courier Pre-Cert (115), etc.
- Has `Region` column (e.g., "Central MA", "Greater Boston") — useful for geographic analysis
- Has `Town` and `county` columns with county-level lat/lon for centroid mapping
- Overlaps significantly with commence-ops — use this as the **broader** dataset, commence-ops as the **operational** subset

**Design decision:** Both tables exist because they serve different purposes:
- `ccc_licensed_operators` (from commence-ops): **operational operators** with detailed license lifecycle dates
- `ccc_county_licenses` (from adult-market): **all applications** including pending/denied, with county/region tagging

The `license_number` field links them. A materialized view can join them for the full picture.

---

### 1.7 Google Reviews — `google_reviews`

**Source:** Google Places API (future scrape)
**Estimated storage:** ~5MB for 500 operators × 50 reviews each
**Refresh:** Weekly

```typescript
export const googleReviews = pgTable('google_reviews', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  google_place_id: varchar('google_place_id', { length: 255 }),
  rating: decimal('rating', { precision: 2, scale: 1 }),
  total_reviews: integer('total_reviews'),
  review_text: text('review_text'),
  review_author: varchar('review_author', { length: 255 }),
  review_rating: integer('review_rating'), // 1-5
  review_time: timestamp('review_time', { withTimezone: true }),
  review_language: varchar('review_language', { length: 5 }),
  scraped_at: timestamp('scraped_at', { withTimezone: true }).notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_google_reviews_operator').on(table.operator_id),
  index('idx_google_reviews_rating').on(table.rating),
  index('idx_google_reviews_scraped').on(table.scraped_at),
  index('idx_google_reviews_place').on(table.google_place_id),
]);

// Separate table for aggregate stats (updated per scrape)
export const googlePlaceStats = pgTable('google_place_stats', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }).unique(),
  google_place_id: varchar('google_place_id', { length: 255 }),
  current_rating: decimal('current_rating', { precision: 2, scale: 1 }),
  total_reviews: integer('total_reviews'),
  price_level: integer('price_level'), // 0-4
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
```

---

### 1.8 Census Demographics — `census_demographics`

**Source:** US Census Bureau ACS 5-year estimates
**Estimated storage:** ~500KB
**Refresh:** Annually (new ACS data every December)

```typescript
export const censusDemographics = pgTable('census_demographics', {
  id: uuid('id').primaryKey().defaultRandom(),
  geo_type: varchar('geo_type', { length: 20 }).notNull(), // 'zip', 'town', 'county'
  geo_id: varchar('geo_id', { length: 20 }).notNull(), // FIPS or ZIP code
  geo_name: varchar('geo_name', { length: 255 }).notNull(),
  state_fips: varchar('state_fips', { length: 2 }).notNull().default('25'), // MA
  total_population: integer('total_population'),
  median_household_income: integer('median_household_income'),
  median_age: decimal('median_age', { precision: 4, scale: 1 }),
  pct_age_21_34: decimal('pct_age_21_34', { precision: 5, scale: 2 }),
  pct_age_35_54: decimal('pct_age_35_54', { precision: 5, scale: 2 }),
  pct_age_55_plus: decimal('pct_age_55_plus', { precision: 5, scale: 2 }),
  total_housing_units: integer('total_housing_units'),
  pct_renter_occupied: decimal('pct_renter_occupied', { precision: 5, scale: 2 }),
  pct_bachelor_plus: decimal('pct_bachelor_plus', { precision: 5, scale: 2 }),
  acs_year: integer('acs_year').notNull(), // e.g., 2023
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_census_geo_type').on(table.geo_type),
  index('idx_census_geo_id').on(table.geo_id),
  index('idx_census_population').on(table.total_population),
  index('idx_census_income').on(table.median_household_income),
  unique('census_geo_year_unique').on(table.geo_type, table.geo_id, table.acs_year),
]);
```

**Key Census variables to pull (ACS 5-Year):**
| Variable | Description |
|----------|-------------|
| B01003_001E | Total population |
| B19013_001E | Median household income |
| B01002_001E | Median age |
| B01001_010E-014E | Males 21-34 |
| B01001_034E-038E | Females 21-34 |
| B25001_001E | Total housing units |
| B25003_003E | Renter-occupied |
| B15003_022E-025E | Bachelor's degree or higher |

**Query:** `https://api.census.gov/data/2023/acs/acs5?get=B01003_001E,B19013_001E,...&for=zip%20code%20tabulation%20area:*&in=state:25`

---

### 1.9 Enforcement Actions — `ccc_enforcement_actions`

**Source:** CCC website scrape (future)
**Estimated storage:** ~100KB
**Refresh:** Weekly

```typescript
export const cccEnforcementActions = pgTable('ccc_enforcement_actions', {
  id: uuid('id').primaryKey().defaultRandom(),
  license_number: varchar('license_number', { length: 50 }),
  business_name: varchar('business_name', { length: 500 }).notNull(),
  action_type: varchar('action_type', { length: 100 }).notNull(), // 'fine', 'suspension', 'revocation', 'warning'
  action_date: timestamp('action_date', { withTimezone: true }).notNull(),
  fine_amount: decimal('fine_amount', { precision: 10, scale: 2 }),
  description: text('description'),
  resolution: text('resolution'),
  resolved_date: timestamp('resolved_date', { withTimezone: true }),
  source_url: text('source_url'),
  document_url: text('document_url'),
  glass_operator_id: uuid('glass_operator_id').references(() => operators.id, { onDelete: 'set null' }),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_enforcement_license').on(table.license_number),
  index('idx_enforcement_name').on(table.business_name),
  index('idx_enforcement_type').on(table.action_type),
  index('idx_enforcement_date').on(table.action_date),
  index('idx_enforcement_operator').on(table.glass_operator_id),
]);
```

---

### 1.10 Strain Database — `strains`

**Source:** Otreeba API (future)
**Estimated storage:** ~10MB
**Refresh:** Monthly

```typescript
export const strains = pgTable('strains', {
  id: uuid('id').primaryKey().defaultRandom(),
  otreeba_id: varchar('otreeba_id', { length: 50 }),
  name: varchar('name', { length: 255 }).notNull(),
  slug: varchar('slug', { length: 255 }).notNull().unique(),
  strain_type: varchar('strain_type', { length: 20 }), // 'indica', 'sativa', 'hybrid'
  thc_avg: decimal('thc_avg', { precision: 5, scale: 2 }),
  cbd_avg: decimal('cbd_avg', { precision: 5, scale: 2 }),
  effects: jsonb('effects'), // ['relaxed', 'creative', 'euphoric']
  flavors: jsonb('flavors'), // ['earthy', 'pine', 'citrus']
  description: text('description'),
  lineage: jsonb('lineage'), // { parent1: 'OG Kush', parent2: 'Durban Poison' }
  terpene_profile: jsonb('terpene_profile'), // { myrcene: 0.5, limonene: 0.3, ... }
  grow_info: jsonb('grow_info'), // { difficulty, flowering_time, yield }
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('idx_strains_name').on(table.name),
  index('idx_strains_type').on(table.strain_type),
  index('idx_strains_otreeba').on(table.otreeba_id),
]);
```

---

### 1.11 Updated `operators` Table — Add CCC Link Column

Add to existing `operators` schema:

```typescript
// New columns to add to operators table
ccc_license_number: varchar('ccc_license_number', { length: 50 }),
ccc_license_type: varchar('ccc_license_type', { length: 100 }),
ccc_dbe_status: varchar('ccc_dbe_status', { length: 200 }),
google_place_id: varchar('google_place_id', { length: 255 }),
```

```sql
-- Migration SQL
ALTER TABLE operators ADD COLUMN ccc_license_number VARCHAR(50);
ALTER TABLE operators ADD COLUMN ccc_license_type VARCHAR(100);
ALTER TABLE operators ADD COLUMN ccc_dbe_status VARCHAR(200);
ALTER TABLE operators ADD COLUMN google_place_id VARCHAR(255);
CREATE INDEX idx_operators_ccc_license ON operators(ccc_license_number);
CREATE INDEX idx_operators_google_place ON operators(google_place_id);
```

---

### Schema Summary

| Table | Rows | Est. Size | Source | Refresh |
|-------|------|-----------|--------|---------|
| `ccc_lab_tests` | 298,342 | 75MB | CSV | Quarterly |
| `ccc_market_sales` | 114,980 | 35MB | CSV × 2 | Monthly |
| `ccc_monthly_price_benchmark` | 71 | <1KB | CSV | Monthly |
| `ccc_licensed_operators` | 772 | 2MB | CSV | Monthly |
| `ccc_county_licenses` | 1,753 | 3MB | CSV | Monthly |
| `google_reviews` | ~25,000 | 5MB | API | Weekly |
| `google_place_stats` | ~492 | 50KB | API | Weekly |
| `census_demographics` | ~500 | 500KB | API | Annually |
| `ccc_enforcement_actions` | ~50-200 | 100KB | Scrape | Weekly |
| `strains` | ~4,000 | 10MB | API | Monthly |
| **Total new** | **~441K** | **~131MB** | | |

---

## Part 2: Import Pipeline Architecture

### 2.1 Import Strategy Overview

| Dataset | Method | Script Type | Matching Strategy |
|---------|--------|-------------|-------------------|
| Lab Tests | Streaming CSV → batch INSERT | One-time + quarterly | METRC tag (no direct match to operators) |
| Market Sales (AU + Med) | CSV → batch INSERT | One-time + monthly append | No operator match needed (statewide aggregates) |
| Monthly Price | Direct INSERT | One-time + monthly append | No match needed |
| Licensed Operators | CSV → UPSERT on license_number | One-time + monthly refresh | License number → operators table |
| County Licenses | CSV → UPSERT on license_number | One-time + monthly refresh | License number |
| Google Reviews | API → UPSERT per operator | Recurring weekly cron | operator_id (already geocoded) |
| Census | API → UPSERT per geo | Annual one-time | ZIP code join |
| Enforcement | HTML scrape → INSERT | Recurring weekly cron | Business name + license number |
| Strains | API → UPSERT on slug | Recurring monthly cron | Strain name fuzzy match to products |

---

### 2.2 Import Script Architecture

All import scripts live at `services/api/src/scripts/import/`:

```
scripts/import/
├── import-lab-tests.ts         # 298K rows, streaming
├── import-market-sales.ts      # facility + medical CSVs
├── import-price-benchmark.ts   # 71 rows
├── import-operators-ccc.ts     # commence-ops + matching
├── import-county-licenses.ts   # adult-market-data
├── match-operators.ts          # Link CCC → GLASS operators
├── scrape-google-reviews.ts    # Google Places API
├── scrape-enforcement.ts       # CCC website
├── import-census.ts            # Census API
├── import-strains.ts           # Otreeba API
└── lib/
    ├── csv-parser.ts           # Shared CSV streaming util
    ├── date-parser.ts          # CCC date format handling
    └── name-matcher.ts         # Fuzzy business name matching
```

---

### 2.3 Data Cleaning Rules

#### CCC Date Parsing
CCC exports dates in this insane format:
```
"Tue Jul 03 2018 16:02:41 GMT-0400 (Eastern Daylight Time)"
```

Parser:
```typescript
function parseCCCDate(raw: string): Date | null {
  if (!raw || raw.trim() === '') return null;
  // Try the verbose CCC format first
  const match = raw.match(/\w+ (\w+ \d+ \d+ \d+:\d+:\d+)/);
  if (match) return new Date(match[1]);
  // Try ISO date
  if (/^\d{4}-\d{2}/.test(raw)) return new Date(raw);
  // Try MM/DD/YYYY
  const parts = raw.split('/');
  if (parts.length === 3) return new Date(`${parts[2]}-${parts[0].padStart(2,'0')}-${parts[1].padStart(2,'0')}`);
  return null;
}
```

#### Business Name Normalization
```typescript
function normalizeBusinessName(name: string): string {
  return name
    .replace(/^["']|["']$/g, '')    // Strip quotes
    .replace(/,?\s*(INC\.?|LLC\.?|CORP\.?|CO\.?|LTD\.?)$/i, '') // Strip suffixes
    .replace(/\s+/g, ' ')           // Collapse whitespace
    .trim()
    .toUpperCase();
}
```

#### Product Category Normalization
Map CCC categories to GLASS categories:
```typescript
const CATEGORY_MAP: Record<string, string> = {
  'Buds': 'flower',
  'Raw Pre-Rolls': 'pre-rolls',
  'Infused Pre-Rolls': 'pre-rolls',
  'Shake/Trim (by strain)': 'flower',
  'Shake/Trim': 'flower',
  'Concentrate': 'concentrates',
  'Concentrate (Each)': 'concentrates',
  'Concentrate (Bulk)': 'concentrates',
  'Vape Product': 'vaporizers',
  'Infused (edible)': 'edibles',
  'Infused Beverage': 'edibles',
  'Infused Beverages (Bulk)': 'edibles',
  'Infused (non-edible)': 'topicals',
  'Kief': 'concentrates',
  'Seeds': 'accessories',
  'Immature Plants': 'accessories',
  'Fresh Frozen Flower': 'flower',
};
```

---

### 2.4 Operator Matching Algorithm

This is the **most critical** import step. We need to link 772 CCC-licensed operators to our 492 scraped operators.

**Strategy: Multi-pass matching**

```typescript
// match-operators.ts

async function matchOperators(db: Pool) {
  const cccOps = await db.query('SELECT * FROM ccc_licensed_operators WHERE glass_operator_id IS NULL');
  const glassOps = await db.query('SELECT * FROM operators');

  for (const ccc of cccOps.rows) {
    let match: string | null = null;

    // Pass 1: Exact license number match
    // Our operators table now has ccc_license_number column
    match = glassOps.rows.find(g =>
      g.license_number && g.license_number === ccc.license_number
    )?.id;

    if (!match) {
      // Pass 2: Exact normalized name match
      const cccName = normalizeBusinessName(ccc.business_name);
      match = glassOps.rows.find(g =>
        normalizeBusinessName(g.name) === cccName
      )?.id;
    }

    if (!match) {
      // Pass 3: Fuzzy name + city match (Levenshtein distance < 3)
      const cccName = normalizeBusinessName(ccc.business_name);
      const cccCity = (ccc.establishment_city || '').toUpperCase();
      match = glassOps.rows.find(g => {
        const gName = normalizeBusinessName(g.name);
        const gCity = (g.city || '').toUpperCase();
        return gCity === cccCity && levenshtein(cccName, gName) < 3;
      })?.id;
    }

    if (!match) {
      // Pass 4: Geographic proximity (< 100m) + partial name match
      if (ccc.lat && ccc.lon) {
        match = glassOps.rows.find(g => {
          if (!g.lat || !g.lon) return false;
          const dist = haversineMeters(
            parseFloat(ccc.lat), parseFloat(ccc.lon),
            parseFloat(g.lat), parseFloat(g.lon)
          );
          if (dist > 100) return false;
          // At least 3 words in common
          const cccWords = normalizeBusinessName(ccc.business_name).split(' ');
          const gWords = normalizeBusinessName(g.name).split(' ');
          const common = cccWords.filter(w => gWords.includes(w));
          return common.length >= 2;
        })?.id;
      }
    }

    if (match) {
      await db.query(
        'UPDATE ccc_licensed_operators SET glass_operator_id = $1 WHERE id = $2',
        [match, ccc.id]
      );
      // Also backfill the operators table with CCC data
      await db.query(
        `UPDATE operators SET
          ccc_license_number = $1,
          ccc_license_type = $2,
          ccc_dbe_status = $3,
          email = COALESCE(email, $4),
          phone = COALESCE(phone, $5)
        WHERE id = $6`,
        [ccc.license_number, ccc.license_type, ccc.dbe_status,
         ccc.business_email, ccc.business_phone, match]
      );
    }
  }

  // Report: how many matched?
  const matched = await db.query(
    'SELECT COUNT(*) FROM ccc_licensed_operators WHERE glass_operator_id IS NOT NULL'
  );
  const unmatched = await db.query(
    'SELECT COUNT(*) FROM ccc_licensed_operators WHERE glass_operator_id IS NULL'
  );
  console.log(`Matched: ${matched.rows[0].count}, Unmatched: ${unmatched.rows[0].count}`);

  // Unmatched CCC operators → candidates for adding to operators table
  // (they exist but we don't scrape them yet — probably no Dutchie/Weedmaps presence)
}
```

**Expected match rates:**
- Pass 1 (license number): ~0 initially (we don't have license numbers yet)
- Pass 2 (exact name): ~300 matches (60% of our 492)
- Pass 3 (fuzzy name + city): ~100 more
- Pass 4 (geo proximity): ~50 more
- **Total:** ~450/492 (91% match rate)

The ~280 CCC operators with no GLASS match are likely cultivators, manufacturers, and testing labs (not in Dutchie/Weedmaps because they don't sell retail).

---

### 2.5 Lab Test Import Script

```typescript
// import-lab-tests.ts
import { createReadStream } from 'fs';
import { parse } from 'csv-parse';
import { Pool } from 'pg';

const BATCH_SIZE = 5000;

async function importLabTests(csvPath: string, db: Pool) {
  const parser = createReadStream(csvPath).pipe(
    parse({ columns: true, skip_empty_lines: true })
  );

  let batch: any[] = [];
  let total = 0;
  let skipped = 0;

  for await (const row of parser) {
    const testResult = parseFloat(row.TestResult);
    if (isNaN(testResult)) { skipped++; continue; }

    batch.push({
      metrc_tag: row.ID,
      product_category: row.ProductCategoryType,
      strain: row.Strain,
      test_type: row['Test Type Name'],
      test_result: testResult,
      testing_lab: row['TestingLab(ITL)'],
      test_date: parseCCCDate(row.TestPerformedDate) || new Date(row.TestPerformedDate),
      test_comment: row.TestComment || null,
    });

    if (batch.length >= BATCH_SIZE) {
      await insertBatch(db, batch);
      total += batch.length;
      batch = [];
      console.log(`Imported ${total} rows...`);
    }
  }

  if (batch.length) {
    await insertBatch(db, batch);
    total += batch.length;
  }

  console.log(`Done. Imported: ${total}, Skipped: ${skipped}`);
}

async function insertBatch(db: Pool, batch: any[]) {
  // Use ON CONFLICT for idempotent re-runs
  const values = batch.map((r, i) => {
    const offset = i * 8;
    return `($${offset+1}, $${offset+2}, $${offset+3}, $${offset+4}, $${offset+5}, $${offset+6}, $${offset+7}, $${offset+8})`;
  }).join(',');

  const params = batch.flatMap(r => [
    r.metrc_tag, r.product_category, r.strain, r.test_type,
    r.test_result, r.testing_lab, r.test_date, r.test_comment
  ]);

  await db.query(`
    INSERT INTO ccc_lab_tests (metrc_tag, product_category, strain, test_type, test_result, testing_lab, test_date, test_comment)
    VALUES ${values}
    ON CONFLICT (metrc_tag, test_type) DO NOTHING
  `, params);
}
```

**Performance note:** 298K rows at 5K/batch = ~60 batches. With ON CONFLICT, expect ~2-3 minutes on Railway.

---

### 2.6 Market Sales Import Script

```typescript
// import-market-sales.ts

async function importMarketSales(csvPath: string, marketType: 'adult_use' | 'medical', db: Pool) {
  const parser = createReadStream(csvPath).pipe(
    parse({ columns: true, skip_empty_lines: true })
  );

  let batch: any[] = [];
  let total = 0;

  for await (const row of parser) {
    const saleDate = new Date(row.SaleDate);
    if (isNaN(saleDate.getTime())) continue;

    const totalDollars = parseFloat(row['TOTAL_$'] || row.TOTAL_$);
    if (isNaN(totalDollars)) continue;

    // Medical doesn't have DeliveryType
    const deliveryType = row.DeliveryType || 'Retail';

    batch.push({
      sale_date: saleDate,
      delivery_type: deliveryType,
      product_category: row.ProductCategoryName,
      unit_of_measure: row.UnitOfMeasureName,
      quantity: parseFloat(row.Quantity) || null,
      units: parseInt(row.Units) || null,
      count_based_total: parseFloat(row.CountBasedTotal) || null,
      dollar_count_based: parseFloat(row.DollarCountBasedTotal) || null,
      weight_based_total: parseFloat(row.WeightBasedTotal) || null,
      dollar_weight_based: parseFloat(row.DollarWeightBasedTotal) || null,
      total_dollars: totalDollars,
      market_type: marketType,
    });

    if (batch.length >= 5000) {
      await insertSalesBatch(db, batch);
      total += batch.length;
      batch = [];
    }
  }

  if (batch.length) {
    await insertSalesBatch(db, batch);
    total += batch.length;
  }

  console.log(`Imported ${total} ${marketType} sales rows`);
}

// Run both:
// await importMarketSales('facility-sales-stats.csv', 'adult_use', db);
// await importMarketSales('medical-facility-stats.csv', 'medical', db);
```

---

### 2.7 Update Frequency Matrix

| Dataset | First Import | Ongoing Cadence | Method |
|---------|-------------|-----------------|--------|
| Lab Tests | One-time (Week 1) | Quarterly manual re-import | Check CCC data catalog for new file |
| Market Sales (AU) | One-time (Week 1) | Monthly append | Download new CSV, import delta |
| Market Sales (Medical) | One-time (Week 1) | Monthly append | Same |
| Monthly Price | One-time (Week 1) | Monthly append | Add new row |
| Licensed Operators | One-time (Week 1) | Monthly UPSERT | Re-download, UPSERT on license_number |
| County Licenses | One-time (Week 1) | Monthly UPSERT | Re-download, UPSERT |
| Google Reviews | Week 2 | Weekly cron (Sunday 2AM) | Google Places API |
| Census | Week 3 | Annual (December) | Census API |
| Enforcement | Week 3 | Weekly cron (Monday 8AM) | CCC website scrape |
| Strains | Week 3 | Monthly | Otreeba API |

---

## Part 3: Cross-Reference Intelligence

This is where GLASS goes from "data warehouse" to "intelligence platform." Each cross-reference creates insights that don't exist anywhere else.

---

### 3.1 THC Accuracy Score

**Question:** How accurately do dispensaries represent THC percentages on their menus vs. what labs actually measure?

**Challenge:** CCC lab data uses anonymized strain names (`Strain_01`), not real names. Direct strain-to-product matching is impossible. But we can do **statistical analysis by category and time period.**

#### Approach A: Category-Level THC Distribution Comparison

```sql
-- What does the CCC say the average THC% is for buds in a given month?
CREATE MATERIALIZED VIEW mv_lab_thc_monthly AS
SELECT
  DATE_TRUNC('month', test_date) AS month,
  product_category,
  test_type,
  COUNT(*) AS test_count,
  ROUND(AVG(test_result)::numeric, 2) AS avg_thc,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY test_result)::numeric, 2) AS median_thc,
  ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY test_result)::numeric, 2) AS p25_thc,
  ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY test_result)::numeric, 2) AS p75_thc,
  ROUND(STDDEV(test_result)::numeric, 2) AS stddev_thc
FROM ccc_lab_tests
WHERE test_type = 'THC (%) Raw Plant Material'
  AND product_category = 'Buds'
  AND test_result BETWEEN 0.1 AND 50 -- sanity bounds
GROUP BY DATE_TRUNC('month', test_date), product_category, test_type
ORDER BY month;

-- What do dispensary menus say the average THC% is?
CREATE MATERIALIZED VIEW mv_menu_thc_monthly AS
SELECT
  DATE_TRUNC('month', p_prices.scraped_at) AS month,
  p_products.category,
  COUNT(*) AS listing_count,
  ROUND(AVG(p_products.thc_percent::numeric), 2) AS avg_listed_thc,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p_products.thc_percent::numeric)::numeric, 2) AS median_listed_thc,
  ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY p_products.thc_percent::numeric)::numeric, 2) AS p25_listed_thc,
  ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY p_products.thc_percent::numeric)::numeric, 2) AS p75_listed_thc
FROM prices p_prices
JOIN products p_products ON p_prices.product_id = p_products.id
WHERE p_products.category = 'flower'
  AND p_products.thc_percent IS NOT NULL
  AND p_products.thc_percent::numeric BETWEEN 0.1 AND 50
GROUP BY DATE_TRUNC('month', p_prices.scraped_at), p_products.category
ORDER BY month;

-- THE CROSS-REFERENCE: Lab reality vs. menu claims
SELECT
  lab.month,
  lab.avg_thc AS lab_avg_thc,
  menu.avg_listed_thc AS menu_avg_thc,
  ROUND(menu.avg_listed_thc - lab.avg_thc, 2) AS thc_inflation,
  ROUND(((menu.avg_listed_thc - lab.avg_thc) / lab.avg_thc * 100)::numeric, 1) AS pct_inflation,
  lab.test_count,
  menu.listing_count
FROM mv_lab_thc_monthly lab
JOIN mv_menu_thc_monthly menu ON lab.month = menu.month
ORDER BY lab.month DESC;
```

**Expected insight:** If labs say average flower THC is 22%, but menus average 27%, that's a **23% inflation rate**. This is a newsletter headline every month.

#### Approach B: Per-Operator THC Accuracy (future)

When we have more scraping history, we can rank operators:
```sql
-- Per-operator: how far is their average menu THC from the statewide lab average?
SELECT
  op.name AS operator_name,
  op.city,
  ROUND(AVG(p.thc_percent::numeric), 1) AS avg_menu_thc,
  lab_avg.avg_thc AS state_lab_avg_thc,
  ROUND(AVG(p.thc_percent::numeric) - lab_avg.avg_thc, 1) AS thc_delta,
  COUNT(*) AS products_with_thc,
  CASE
    WHEN AVG(p.thc_percent::numeric) - lab_avg.avg_thc > 5 THEN 'inflated'
    WHEN AVG(p.thc_percent::numeric) - lab_avg.avg_thc < -2 THEN 'conservative'
    ELSE 'accurate'
  END AS accuracy_grade
FROM operators op
JOIN prices pr ON pr.operator_id = op.id
JOIN products p ON pr.product_id = p.id
CROSS JOIN (
  SELECT AVG(test_result) AS avg_thc
  FROM ccc_lab_tests
  WHERE test_type = 'THC (%) Raw Plant Material'
    AND product_category = 'Buds'
    AND test_date > NOW() - INTERVAL '6 months'
) lab_avg
WHERE p.category = 'flower'
  AND p.thc_percent IS NOT NULL
GROUP BY op.id, op.name, op.city, lab_avg.avg_thc
ORDER BY thc_delta DESC;
```

---

### 3.2 Revenue Intelligence

**What we have:** Statewide daily sales totals by product category. **What we need to infer:** Per-operator revenue estimates.

#### Statewide Revenue Dashboard

```sql
-- Weekly statewide revenue by product category
CREATE MATERIALIZED VIEW mv_weekly_market_revenue AS
SELECT
  DATE_TRUNC('week', sale_date) AS week,
  product_category,
  delivery_type,
  market_type,
  SUM(total_dollars) AS total_revenue,
  SUM(COALESCE(weight_based_total, 0)) AS total_grams,
  SUM(COALESCE(count_based_total, 0)) AS total_units,
  -- Implied price per gram for weight-based products
  CASE
    WHEN SUM(COALESCE(weight_based_total, 0)) > 0
    THEN ROUND((SUM(COALESCE(dollar_weight_based, 0)) / SUM(weight_based_total))::numeric, 2)
    ELSE NULL
  END AS implied_price_per_gram,
  -- Implied price per unit for count-based products
  CASE
    WHEN SUM(COALESCE(count_based_total, 0)) > 0
    THEN ROUND((SUM(COALESCE(dollar_count_based, 0)) / SUM(count_based_total))::numeric, 2)
    ELSE NULL
  END AS implied_price_per_unit
FROM ccc_market_sales
GROUP BY DATE_TRUNC('week', sale_date), product_category, delivery_type, market_type
ORDER BY week DESC, total_revenue DESC;

-- CROSS-REFERENCE: CCC implied price vs. GLASS scraped prices
SELECT
  ccc.week,
  ccc.product_category AS ccc_category,
  ccc.implied_price_per_gram AS ccc_price_per_gram,
  glass.avg_price_per_gram AS glass_scraped_price_per_gram,
  ROUND(glass.avg_price_per_gram - ccc.implied_price_per_gram, 2) AS retail_markup,
  ROUND(((glass.avg_price_per_gram - ccc.implied_price_per_gram) / ccc.implied_price_per_gram * 100)::numeric, 1) AS markup_pct
FROM mv_weekly_market_revenue ccc
JOIN (
  SELECT
    DATE_TRUNC('week', pr.scraped_at) AS week,
    ROUND(AVG(pr.price_per_gram::numeric), 2) AS avg_price_per_gram
  FROM prices pr
  JOIN products p ON pr.product_id = p.id
  WHERE p.category = 'flower'
    AND pr.price_per_gram IS NOT NULL
    AND pr.price_per_gram::numeric BETWEEN 1 AND 50
  GROUP BY DATE_TRUNC('week', pr.scraped_at)
) glass ON glass.week = ccc.week
WHERE ccc.product_category = 'Buds'
  AND ccc.market_type = 'adult_use'
  AND ccc.delivery_type = 'Retail'
ORDER BY ccc.week DESC;
```

**Already proven:** CCC says $8.19/g average, GLASS scrapes show $11.13/g = **36% markup**. This is the proprietary insight.

#### Delivery Channel Intelligence

```sql
-- Delivery market share over time
SELECT
  DATE_TRUNC('month', sale_date) AS month,
  delivery_type,
  SUM(total_dollars) AS revenue,
  ROUND(SUM(total_dollars) / SUM(SUM(total_dollars)) OVER (PARTITION BY DATE_TRUNC('month', sale_date)) * 100, 1) AS market_share_pct
FROM ccc_market_sales
WHERE market_type = 'adult_use'
GROUP BY DATE_TRUNC('month', sale_date), delivery_type
ORDER BY month DESC, revenue DESC;
```

**This is critical for the Delivered partnership** — shows delivery market share growth trajectory.

---

### 3.3 Operator Health Score

Composite scoring system combining multiple data sources. Score 0-100.

```sql
-- Materialized view: Operator Health Score
CREATE MATERIALIZED VIEW mv_operator_health_score AS
WITH pricing_score AS (
  -- How competitive are their prices vs. market average?
  SELECT
    pr.operator_id,
    ROUND(AVG(pr.price_per_gram::numeric), 2) AS avg_price_per_gram,
    -- Score: 100 if at market avg, decreasing as they deviate above
    GREATEST(0, LEAST(100,
      100 - (AVG(pr.price_per_gram::numeric) -
        (SELECT AVG(price_per_gram::numeric) FROM prices
         WHERE price_per_gram IS NOT NULL
         AND price_per_gram::numeric BETWEEN 1 AND 50
         AND scraped_at > NOW() - INTERVAL '30 days')
      ) * 10
    )) AS price_competitiveness
  FROM prices pr
  WHERE pr.scraped_at > NOW() - INTERVAL '30 days'
    AND pr.price_per_gram IS NOT NULL
    AND pr.price_per_gram::numeric BETWEEN 1 AND 50
  GROUP BY pr.operator_id
),
product_breadth AS (
  -- How many product categories do they carry?
  SELECT
    pr.operator_id,
    COUNT(DISTINCT p.category) AS category_count,
    COUNT(DISTINCT p.id) AS product_count,
    -- Score: more categories = better (max 5 common categories)
    LEAST(100, COUNT(DISTINCT p.category) * 20) AS breadth_score
  FROM prices pr
  JOIN products p ON pr.product_id = p.id
  WHERE pr.scraped_at > NOW() - INTERVAL '30 days'
  GROUP BY pr.operator_id
),
review_score AS (
  -- Google review quality
  SELECT
    operator_id,
    current_rating::numeric AS google_rating,
    total_reviews,
    -- Score: weighted by both rating and volume
    LEAST(100, (current_rating::numeric / 5.0 * 70) + LEAST(30, total_reviews * 0.3)) AS review_quality
  FROM google_place_stats
  WHERE current_rating IS NOT NULL
),
compliance_score AS (
  -- License status and enforcement history
  SELECT
    clo.glass_operator_id AS operator_id,
    CASE clo.license_status
      WHEN 'Active' THEN 100
      WHEN 'FINAL LICENSE' THEN 100
      WHEN 'IN PROCESS' THEN 50
      WHEN 'Expired' THEN 10
      WHEN 'Surrendered' THEN 0
      ELSE 50
    END AS license_score,
    -- Penalty for enforcement actions
    COALESCE((
      SELECT -20 * COUNT(*)
      FROM ccc_enforcement_actions ea
      WHERE ea.glass_operator_id = clo.glass_operator_id
        AND ea.action_date > NOW() - INTERVAL '1 year'
    ), 0) AS enforcement_penalty
  FROM ccc_licensed_operators clo
  WHERE clo.glass_operator_id IS NOT NULL
)
SELECT
  op.id AS operator_id,
  op.name,
  op.city,
  COALESCE(ps.price_competitiveness, 50) AS price_score,
  COALESCE(pb.breadth_score, 30) AS breadth_score,
  COALESCE(rs.review_quality, 50) AS review_score,
  COALESCE(cs.license_score, 50) + COALESCE(cs.enforcement_penalty, 0) AS compliance_score,
  -- COMPOSITE: weighted average
  ROUND((
    COALESCE(ps.price_competitiveness, 50) * 0.30 +
    COALESCE(pb.breadth_score, 30) * 0.15 +
    COALESCE(rs.review_quality, 50) * 0.25 +
    (COALESCE(cs.license_score, 50) + COALESCE(cs.enforcement_penalty, 0)) * 0.30
  )::numeric, 0) AS health_score,
  pb.product_count,
  pb.category_count,
  rs.google_rating,
  rs.total_reviews,
  ps.avg_price_per_gram
FROM operators op
LEFT JOIN pricing_score ps ON ps.operator_id = op.id
LEFT JOIN product_breadth pb ON pb.operator_id = op.id
LEFT JOIN review_score rs ON rs.operator_id = op.id
LEFT JOIN compliance_score cs ON cs.operator_id = op.id
WHERE op.status = 'active'
ORDER BY health_score DESC;
```

**Weights:**
- Price competitiveness: 30% (most actionable)
- Compliance/license health: 30% (risk signal)
- Google review quality: 25% (customer perception)
- Product breadth: 15% (selection matters but less)

---

### 3.4 Market Gap Analysis

**Question:** Which zip codes are underserved relative to their population and demographics?

```sql
-- Market gap analysis: population per dispensary by zip code
CREATE MATERIALIZED VIEW mv_market_gaps AS
WITH zip_operators AS (
  -- Count operators per zip code
  SELECT
    COALESCE(clo.establishment_zip, LEFT(op.metadata->>'zip', 5)) AS zip_code,
    COUNT(DISTINCT op.id) AS operator_count,
    ARRAY_AGG(DISTINCT op.name) AS operator_names
  FROM operators op
  LEFT JOIN ccc_licensed_operators clo ON clo.glass_operator_id = op.id
  WHERE op.status = 'active'
  GROUP BY COALESCE(clo.establishment_zip, LEFT(op.metadata->>'zip', 5))
),
zip_demand AS (
  SELECT
    cd.geo_id AS zip_code,
    cd.geo_name,
    cd.total_population,
    cd.median_household_income,
    cd.pct_age_21_34,
    cd.median_age,
    -- Demand proxy: population × income-weighted propensity
    -- Higher income + younger age = higher cannabis spend
    ROUND((
      cd.total_population *
      (COALESCE(cd.pct_age_21_34, 15.0) / 100.0) *
      LEAST(1.5, COALESCE(cd.median_household_income, 50000)::numeric / 75000.0)
    )::numeric, 0) AS demand_index
  FROM census_demographics cd
  WHERE cd.geo_type = 'zip'
    AND cd.state_fips = '25'
)
SELECT
  zd.zip_code,
  zd.geo_name,
  zd.total_population,
  zd.median_household_income,
  COALESCE(zo.operator_count, 0) AS dispensary_count,
  zo.operator_names,
  -- Key metric: people per dispensary
  CASE
    WHEN COALESCE(zo.operator_count, 0) = 0 THEN zd.total_population
    ELSE ROUND(zd.total_population::numeric / zo.operator_count, 0)
  END AS people_per_dispensary,
  zd.demand_index,
  CASE
    WHEN COALESCE(zo.operator_count, 0) = 0 AND zd.total_population > 10000 THEN 'whitespace'
    WHEN COALESCE(zo.operator_count, 0) = 1 AND zd.total_population > 30000 THEN 'underserved'
    WHEN COALESCE(zo.operator_count, 0) >= 3 AND zd.total_population < 20000 THEN 'oversaturated'
    ELSE 'balanced'
  END AS market_status
FROM zip_demand zd
LEFT JOIN zip_operators zo ON zo.zip_code = zd.zip_code
WHERE zd.total_population > 5000 -- Exclude tiny towns
ORDER BY people_per_dispensary DESC NULLS FIRST;
```

**Why this matters:** An operator considering a new location can see that ZIP 02148 (Malden, pop 66K) has only 1 dispensary, while ZIP 02301 (Brockton, pop 105K) has zero. That's actionable intelligence worth a subscription.

---

### 3.5 Threat Detection

Combines enforcement actions, new license applications, and proximity analysis.

```sql
-- Threat radar: new competitors + enforcement risks near an operator
CREATE OR REPLACE FUNCTION detect_threats(target_operator_id UUID, radius_miles NUMERIC DEFAULT 5)
RETURNS TABLE (
  threat_type TEXT,
  severity TEXT,
  entity_name TEXT,
  description TEXT,
  distance_miles NUMERIC,
  detected_at TIMESTAMPTZ
) AS $$
BEGIN
  -- Threat 1: New license applications within radius
  RETURN QUERY
  SELECT
    'new_competitor'::TEXT AS threat_type,
    CASE
      WHEN cl.approved_license_stage = 'COMMENCE OPS' THEN 'high'
      WHEN cl.approved_license_stage = 'PROVISIONAL LICENSE' THEN 'medium'
      ELSE 'low'
    END AS severity,
    cl.business_name::TEXT AS entity_name,
    FORMAT('New %s application (%s stage) at %s, %s',
      cl.license_type, COALESCE(cl.approved_license_stage, 'unknown'),
      cl.establishment_city, cl.establishment_zip
    )::TEXT AS description,
    ROUND((
      3959 * ACOS(
        COS(RADIANS(op.lat::numeric)) * COS(RADIANS(cl.lat::numeric)) *
        COS(RADIANS(cl.lon::numeric) - RADIANS(op.lon::numeric)) +
        SIN(RADIANS(op.lat::numeric)) * SIN(RADIANS(cl.lat::numeric))
      )
    )::NUMERIC, 1) AS distance_miles,
    COALESCE(cl.approved_date, cl.submitted_date, cl.created_at) AS detected_at
  FROM operators op
  CROSS JOIN ccc_county_licenses cl
  WHERE op.id = target_operator_id
    AND cl.license_type LIKE '%Retailer%'
    AND cl.lat IS NOT NULL AND cl.lon IS NOT NULL
    AND op.lat IS NOT NULL AND op.lon IS NOT NULL
    -- Haversine distance filter
    AND (
      3959 * ACOS(
        COS(RADIANS(op.lat::numeric)) * COS(RADIANS(cl.lat::numeric)) *
        COS(RADIANS(cl.lon::numeric) - RADIANS(op.lon::numeric)) +
        SIN(RADIANS(op.lat::numeric)) * SIN(RADIANS(cl.lat::numeric))
      )
    ) <= radius_miles
    -- Only recent applications (last 6 months)
    AND COALESCE(cl.approved_date, cl.submitted_date) > NOW() - INTERVAL '6 months';

  -- Threat 2: Enforcement actions on nearby operators
  RETURN QUERY
  SELECT
    'enforcement_nearby'::TEXT AS threat_type,
    CASE ea.action_type
      WHEN 'revocation' THEN 'high'
      WHEN 'suspension' THEN 'medium'
      ELSE 'low'
    END AS severity,
    ea.business_name::TEXT AS entity_name,
    FORMAT('%s: %s', ea.action_type, LEFT(ea.description, 200))::TEXT AS description,
    NULL::NUMERIC AS distance_miles,
    ea.action_date AS detected_at
  FROM ccc_enforcement_actions ea
  WHERE ea.action_date > NOW() - INTERVAL '90 days';

  -- Threat 3: Price undercutting (operators with significantly lower prices)
  RETURN QUERY
  SELECT
    'price_undercut'::TEXT AS threat_type,
    CASE
      WHEN competitor_avg < target_avg * 0.7 THEN 'high'
      WHEN competitor_avg < target_avg * 0.85 THEN 'medium'
      ELSE 'low'
    END AS severity,
    comp_name::TEXT AS entity_name,
    FORMAT('%s is pricing flower at $%.2f/g vs. your $%.2f/g (%.0f%% lower)',
      comp_name, competitor_avg, target_avg,
      (1 - competitor_avg / target_avg) * 100
    )::TEXT AS description,
    comp_distance AS distance_miles,
    NOW() AS detected_at
  FROM (
    SELECT
      comp_op.name AS comp_name,
      AVG(comp_pr.price_per_gram::numeric) AS competitor_avg,
      AVG(target_pr.price_per_gram::numeric) AS target_avg,
      ROUND((
        3959 * ACOS(
          COS(RADIANS(target_op.lat::numeric)) * COS(RADIANS(comp_op.lat::numeric)) *
          COS(RADIANS(comp_op.lon::numeric) - RADIANS(target_op.lon::numeric)) +
          SIN(RADIANS(target_op.lat::numeric)) * SIN(RADIANS(comp_op.lat::numeric))
        )
      )::NUMERIC, 1) AS comp_distance
    FROM operators target_op
    JOIN prices target_pr ON target_pr.operator_id = target_op.id
    JOIN products target_p ON target_pr.product_id = target_p.id
    CROSS JOIN operators comp_op
    JOIN prices comp_pr ON comp_pr.operator_id = comp_op.id
    JOIN products comp_p ON comp_pr.product_id = comp_p.id
    WHERE target_op.id = target_operator_id
      AND comp_op.id != target_operator_id
      AND target_p.category = 'flower'
      AND comp_p.category = 'flower'
      AND target_pr.scraped_at > NOW() - INTERVAL '7 days'
      AND comp_pr.scraped_at > NOW() - INTERVAL '7 days'
      AND target_pr.price_per_gram IS NOT NULL
      AND comp_pr.price_per_gram IS NOT NULL
      AND target_op.lat IS NOT NULL AND comp_op.lat IS NOT NULL
      AND (
        3959 * ACOS(
          COS(RADIANS(target_op.lat::numeric)) * COS(RADIANS(comp_op.lat::numeric)) *
          COS(RADIANS(comp_op.lon::numeric) - RADIANS(target_op.lon::numeric)) +
          SIN(RADIANS(target_op.lat::numeric)) * SIN(RADIANS(comp_op.lat::numeric))
        )
      ) <= radius_miles
    GROUP BY comp_op.name, target_op.lat, target_op.lon, comp_op.lat, comp_op.lon
    HAVING AVG(comp_pr.price_per_gram::numeric) < AVG(target_pr.price_per_gram::numeric) * 0.85
  ) price_threats;

END;
$$ LANGUAGE plpgsql;
```

---

### 3.6 Materialized View Refresh Strategy

```sql
-- All materialized views and their refresh schedule
-- Run via pg_cron or application-level cron

-- Daily (after scraper runs at 6AM ET)
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_price_averages;

-- Weekly (Sunday night)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_lab_thc_monthly;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_menu_thc_monthly;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_operator_health_score;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_market_gaps;

-- Monthly (1st of month, after new CCC data import)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_weekly_market_revenue;
```

---

## Part 4: API Endpoints

### 4.1 Endpoint Inventory

All endpoints under `https://glass-api-production.up.railway.app/api/v1/`

#### Public Endpoints (no auth required)

| Method | Path | Description | Cache |
|--------|------|-------------|-------|
| GET | `/ccc/market-sales` | Statewide sales aggregates | 1 hour |
| GET | `/ccc/market-sales/timeseries` | Weekly/monthly revenue timeseries | 1 hour |
| GET | `/ccc/price-benchmark` | Official monthly price per gram | 24 hours |
| GET | `/ccc/price-benchmark/latest` | Latest month's price | 1 hour |
| GET | `/ccc/lab-stats` | Aggregate lab testing statistics | 24 hours |
| GET | `/ccc/delivery-share` | Delivery vs. retail market share | 1 hour |
| GET | `/ccc/licensed-operators/count` | License counts by type/status | 24 hours |

#### Authenticated Endpoints (Clerk JWT required)

| Method | Path | Description | Cache |
|--------|------|-------------|-------|
| GET | `/intelligence/thc-accuracy` | THC inflation: lab vs. menu | 1 hour |
| GET | `/intelligence/thc-accuracy/:operatorId` | Per-operator THC accuracy | 1 hour |
| GET | `/intelligence/market-gap` | Underserved zip code analysis | 24 hours |
| GET | `/intelligence/revenue-cross-ref` | CCC vs. scraped price comparison | 1 hour |
| GET | `/intelligence/health-score/:operatorId` | Operator health score breakdown | 1 hour |
| GET | `/intelligence/health-score/leaderboard` | Top/bottom operators by health | 1 hour |
| GET | `/intelligence/category-trends` | Product category revenue trends | 1 hour |
| GET | `/intelligence/delivery-growth` | Delivery channel growth metrics | 1 hour |
| GET | `/threats/detect/:operatorId` | Full threat radar scan | 15 min |
| GET | `/ccc/operators/search` | Search licensed operators | 5 min |
| GET | `/ccc/operators/:licenseNumber` | Full operator CCC profile | 1 hour |
| GET | `/strains/search` | Search strain database | 24 hours |
| GET | `/strains/:slug` | Strain details + effects | 24 hours |
| GET | `/reviews/:operatorId` | Google reviews for operator | 1 hour |
| GET | `/demographics/:zipCode` | Census data for zip code | 24 hours |

#### Admin Endpoints (ADMIN_API_KEY required)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/admin/import/lab-tests` | Trigger lab test import |
| POST | `/admin/import/market-sales` | Trigger market sales import |
| POST | `/admin/import/operators` | Trigger CCC operator import |
| POST | `/admin/match-operators` | Run operator matching algorithm |
| POST | `/admin/refresh-views` | Refresh all materialized views |
| GET | `/admin/import-status` | Status of last imports |
| GET | `/admin/match-report` | Operator matching report |

---

### 4.2 Endpoint Specs (Key Examples)

#### `GET /api/v1/intelligence/thc-accuracy`

```typescript
// Query params
interface THCAccuracyQuery {
  months?: number;      // default: 12
  category?: string;    // default: 'flower'
}

// Response
interface THCAccuracyResponse {
  meta: {
    dateRange: { from: string; to: string };
    labTestCount: number;
    menuListingCount: number;
  };
  monthly: Array<{
    month: string;        // '2024-01'
    labAvgTHC: number;    // 22.3
    menuAvgTHC: number;   // 27.1
    inflationPct: number; // 21.5
    labMedianTHC: number;
    menuMedianTHC: number;
    labTestCount: number;
    menuListingCount: number;
  }>;
  summary: {
    avgInflation: number;
    trendDirection: 'increasing' | 'decreasing' | 'stable';
  };
}
```

**Route handler:**
```typescript
app.get('/api/v1/intelligence/thc-accuracy', {
  preHandler: [requireAuth],
}, async (req, reply) => {
  const months = parseInt(req.query.months) || 12;

  const result = await db.query(`
    SELECT
      lab.month,
      lab.avg_thc AS lab_avg_thc,
      lab.median_thc AS lab_median_thc,
      menu.avg_listed_thc AS menu_avg_thc,
      menu.median_listed_thc AS menu_median_thc,
      ROUND(((menu.avg_listed_thc - lab.avg_thc) / NULLIF(lab.avg_thc, 0) * 100)::numeric, 1) AS inflation_pct,
      lab.test_count,
      menu.listing_count
    FROM mv_lab_thc_monthly lab
    JOIN mv_menu_thc_monthly menu ON lab.month = menu.month
    WHERE lab.month > NOW() - INTERVAL '${months} months'
    ORDER BY lab.month DESC
  `);

  reply.header('Cache-Control', 'public, max-age=3600');
  return {
    meta: {
      dateRange: {
        from: result.rows[result.rows.length - 1]?.month,
        to: result.rows[0]?.month,
      },
      labTestCount: result.rows.reduce((s, r) => s + r.test_count, 0),
      menuListingCount: result.rows.reduce((s, r) => s + r.listing_count, 0),
    },
    monthly: result.rows.map(r => ({
      month: r.month,
      labAvgTHC: parseFloat(r.lab_avg_thc),
      menuAvgTHC: parseFloat(r.menu_avg_thc),
      inflationPct: parseFloat(r.inflation_pct),
      labMedianTHC: parseFloat(r.lab_median_thc),
      menuMedianTHC: parseFloat(r.menu_median_thc),
      labTestCount: r.test_count,
      menuListingCount: r.listing_count,
    })),
    summary: {
      avgInflation: result.rows.reduce((s, r) => s + parseFloat(r.inflation_pct), 0) / result.rows.length,
      trendDirection: determineTrend(result.rows.map(r => parseFloat(r.inflation_pct))),
    },
  };
});
```

#### `GET /api/v1/ccc/market-sales/timeseries`

```typescript
// Query params
interface MarketSalesTimeseriesQuery {
  granularity?: 'daily' | 'weekly' | 'monthly'; // default: 'weekly'
  category?: string;       // filter by product category
  deliveryType?: string;   // 'Retail', 'Delivery Operators', 'Delivery Couriers'
  marketType?: 'adult_use' | 'medical' | 'all'; // default: 'adult_use'
  from?: string;           // ISO date
  to?: string;             // ISO date
}

// Response
interface MarketSalesTimeseriesResponse {
  meta: {
    granularity: string;
    dateRange: { from: string; to: string };
    totalRevenue: number;
  };
  series: Array<{
    period: string;
    totalRevenue: number;
    categories: Record<string, number>;  // { 'Buds': 123456, 'Vape Product': 78901, ... }
    deliveryBreakdown: Record<string, number>; // { 'Retail': 100000, 'Delivery': 23456 }
  }>;
}
```

#### `GET /api/v1/intelligence/health-score/:operatorId`

```typescript
// Response
interface HealthScoreResponse {
  operatorId: string;
  operatorName: string;
  healthScore: number; // 0-100
  breakdown: {
    priceCompetitiveness: { score: number; avgPricePerGram: number; marketAvg: number };
    productBreadth: { score: number; categoryCount: number; productCount: number };
    reviewQuality: { score: number; googleRating: number; totalReviews: number };
    compliance: { score: number; licenseStatus: string; enforcementActions: number };
  };
  rank: number;      // out of total operators
  totalOperators: number;
  percentile: number; // e.g., 85 = top 15%
  recommendations: string[]; // ["Your prices are 15% above market average", "Consider adding edibles"]
}
```

#### `GET /api/v1/intelligence/market-gap`

```typescript
// Query params
interface MarketGapQuery {
  county?: string;
  minPopulation?: number;  // default: 5000
  status?: 'whitespace' | 'underserved' | 'oversaturated' | 'balanced';
}

// Response
interface MarketGapResponse {
  gaps: Array<{
    zipCode: string;
    townName: string;
    county: string;
    population: number;
    medianIncome: number;
    dispensaryCount: number;
    dispensaryNames: string[];
    peoplePerDispensary: number;
    demandIndex: number;
    marketStatus: 'whitespace' | 'underserved' | 'oversaturated' | 'balanced';
  }>;
  summary: {
    totalWhitespace: number;
    totalUnderserved: number;
    totalOversaturated: number;
    avgPeoplePerDispensary: number;
  };
}
```

---

### 4.3 Caching Strategy

```typescript
// Caching layers:

// 1. HTTP Cache-Control headers (CDN/browser level)
const CACHE_DURATIONS = {
  public_aggregate: 'public, max-age=3600, s-maxage=3600',      // 1 hour
  public_static: 'public, max-age=86400, s-maxage=86400',       // 24 hours
  authenticated: 'private, max-age=900',                         // 15 min
  realtime: 'private, no-cache',                                 // no cache
} as const;

// 2. In-memory LRU cache (Node process level) — for expensive queries
import { LRUCache } from 'lru-cache';

const queryCache = new LRUCache<string, any>({
  max: 500,
  ttl: 1000 * 60 * 15, // 15 minutes
  maxSize: 50 * 1024 * 1024, // 50MB
  sizeCalculation: (value) => JSON.stringify(value).length,
});

// 3. Materialized views (database level) — for cross-reference queries
// Already covered in Part 3 — refreshed on schedule

// 4. Future: Redis (when Railway Redis is added)
// Move query cache to Redis for multi-instance support
```

**Why not Redis right now?** Railway Redis is an additional ~$5/mo and adds operational complexity. The Node LRU cache is sufficient at current scale (single API instance). Add Redis when we hit multi-instance or need shared cache across scraper + API.

---

## Part 5: How Each Product Benefits

### 5.1 GLASS Dashboard

| Dataset | Visualization | Value |
|---------|--------------|-------|
| Lab Tests | **THC Reality Check** — bar chart: lab-tested avg vs. menu-listed avg per month | "Your competitors are inflating THC by 23%. Here's the data." |
| Market Sales | **Revenue Tide** — stacked area chart: weekly revenue by category | Shows which categories are growing/shrinking. Buds declining, vapes rising. |
| Market Sales | **Delivery Pulse** — line chart: delivery market share over time | Tracks delivery adoption trajectory. Critical for Delivered pitch. |
| Monthly Price | **Price Erosion Tracker** — line chart overlaid with operator's own prices | Official MA price vs. what you're charging. Where's your margin going? |
| Licensed Operators | **Competitive Landscape Map** — map with operator pins, colored by license type | See every competitor, their license status, DBE designation |
| County Licenses | **Pipeline Radar** — new applications near you, by stage | "3 new retailer applications within 5 miles of you in the last 90 days" |
| Google Reviews | **Reputation Score** — your rating vs. nearby competitors | Quantified competitive advantage/weakness |
| Census | **Demand Density** — heat map: population per dispensary by zip | Shows underserved areas = expansion opportunities |
| Enforcement | **Compliance Feed** — recent enforcement actions in your area | Know when competitors get fined/suspended |
| Health Score | **Operator Report Card** — composite 0-100 with breakdown | The single number every operator wants to improve |

**New Dashboard Sections:**
1. **Market Intelligence** (top of page): Price erosion line, revenue tide, delivery share
2. **Competitive Radar** (map view): Nearby operators + pending apps + enforcement
3. **Your Report Card** (sidebar): Health score, THC accuracy, price rank
4. **Market Opportunities** (bottom): Underserved zip codes, growing categories

---

### 5.2 Virtual Budtender

| Dataset | Improvement |
|---------|-------------|
| Lab Tests | Recommend products based on **actual lab-tested THC ranges** rather than menu-inflated numbers. "This batch tested at 24.3% THC — verified by [lab]." |
| Strains (Otreeba) | Recommend by **effects and terpene profiles**: "Looking for relaxation? Blue Dream has myrcene-dominant profile with 78% of users reporting calm effects." |
| Lab + Strains | **Confidence score** on recommendations: "Based on 47 lab tests, this strain consistently tests 22-26% THC with earthy/pine flavor profile" |
| Market Sales | **Trending products**: "Pre-rolls are up 34% in MA this month. Consider featuring your Gorilla Glue pre-rolls." |
| Google Reviews | **Social proof integration**: "This product is from NETA Brookline — 4.2 stars, 1,847 reviews. Customers praise their flower selection." |

**Technical integration:**
```typescript
// Virtual Budtender query enhancement
interface EnhancedProductRecommendation {
  product: Product;
  labVerifiedTHC?: { avg: number; range: [number, number]; testCount: number };
  strainProfile?: { effects: string[]; flavors: string[]; type: string; terpenes: Record<string, number> };
  operatorRating?: { stars: number; reviewCount: number };
  trendingScore?: number; // based on category growth in CCC data
  confidenceScore: number; // 0-1, higher = more data supporting recommendation
}
```

---

### 5.3 Cue (Incentive Platform)

| Dataset | Use Case |
|---------|----------|
| Market Sales | **Demand-driven missions**: If edibles are trending up 20% month-over-month, create missions to upsell edibles. "Sell 5 edible units today → $10 bonus." |
| Census Demographics | **Demographic-targeted missions**: Zip codes with high 21-34 age population → emphasize vape/concentrate missions. Older demographics → flower/edible missions. |
| Monthly Price | **Margin protection missions**: When official price drops below threshold, auto-create missions to push premium products that maintain margin. |
| Lab Tests | **Education missions**: "If a customer asks about THC percentages, explain that lab-tested averages are X% — earn $2 per educated customer." |
| Google Reviews | **Review boost missions**: "If Google rating drops below 4.0, create mission: Get a 5-star review from a satisfied customer → $5 bonus." |

---

### 5.4 Delivery (Partnership)

| Dataset | Use Case |
|---------|----------|
| Market Sales | **Delivery growth narrative**: "Delivery is now X% of MA sales, up from Y% 12 months ago. That's $Z million." Use this in Delivered pitch deck. |
| Census Demographics | **Route optimization**: Serve zip codes with highest demand index first. Route drivers through high-population, high-income areas. |
| Market Gap (whitespace) | **Coverage planning**: Identify towns with population > 20K and zero delivery operators. These are expansion targets. |
| Licensed Operators | **Partner sourcing**: Find all cultivators + manufacturers with active licenses → potential wholesale suppliers for delivery inventory. |

---

### 5.5 Newsletter ("The Operator's Margin Report")

**Every issue now includes:**

1. **The Number** — Official MA flower price this month: $X.XX/g (↓Y% from last month, ↓Z% from last year)
2. **Category Scoreboard** — Revenue by product category: which ones grew, which ones shrank
3. **THC Inflation Report** — Lab-tested avg vs. menu-listed avg (with trend line)
4. **Delivery Watch** — Delivery market share this month + growth trajectory
5. **New Player Alert** — How many new license applications this month, by type
6. **Enforcement Roundup** — Any fines/suspensions this month
7. **Market Gap of the Week** — One underserved zip code, with population data, showing why someone should open there
8. **Price Leaderboard** — Top 5 cheapest / most expensive operators by category (scraped data)

**Data-driven content generation:**
```typescript
// Newsletter data package (auto-generated monthly)
interface NewsletterData {
  officialPrice: { current: number; monthAgo: number; yearAgo: number; allTimeHigh: number };
  categoryRevenue: Array<{ category: string; revenue: number; changePct: number }>;
  thcInflation: { labAvg: number; menuAvg: number; inflationPct: number };
  deliveryShare: { currentPct: number; growthPct: number };
  newApplications: { total: number; byType: Record<string, number> };
  enforcementActions: Array<{ business: string; action: string; amount: number }>;
  marketGap: { zipCode: string; town: string; population: number; dispensaries: number };
  priceLeaders: { cheapest: Array<{ name: string; avgPrice: number }>; expensive: Array<{ name: string; avgPrice: number }> };
}
```

---

### 5.6 SIGNAL (Cannabis SEO)

| Dataset | SEO Improvement |
|---------|----------------|
| Market Sales | **Trend-based content**: When a category surges (e.g., beverages), auto-generate SEO content targeting "[city] cannabis beverages" keywords |
| Monthly Price | **Price-anchored content**: "Massachusetts Cannabis Prices in [Month] [Year]" — auto-updated page that ranks for price queries |
| Lab Tests | **THC content pages**: "Average THC Levels in Massachusetts Cannabis [Year]" — data-rich page targeting informational queries |
| Licensed Operators | **Business listing enrichment**: Add license numbers, DBE status, license dates to operator profile pages for E-E-A-T |
| Census + Market Gap | **Location pages**: Auto-generate "Cannabis Dispensaries Near [Town], MA" with demand data showing why the town needs more options |
| Strains | **Strain pages**: "Blue Dream Strain — Effects, THC Levels, Where to Buy in MA" with real lab data backing up claims |

**Content velocity calculation:**
- 20 product categories × 12 months = 240 trend pages/year
- 500+ unique strains × 1 page each = 500 strain pages
- 300+ MA towns × 1 location page each = 300 location pages
- Monthly price report × 12 = 12 evergreen authority pages
- **Total:** 1,000+ data-driven SEO pages that auto-update

---

## Part 6: Implementation Roadmap

### Week 1: Foundation (Days 1-7)

**Goal:** Import all CSV data, run operator matching, build first cross-reference.

#### Day 1-2: Schema + Migration
```bash
# Create all new tables
# Run SQL migration against Railway PostgreSQL
```
- [ ] Add new table DDL to `schema.ts` (all 7 new table definitions from Part 1)
- [ ] Generate migration SQL: `drizzle-kit generate`
- [ ] Apply migration to Railway: `drizzle-kit push`
- [ ] Add columns to `operators` table (ccc_license_number, etc.)
- [ ] Verify all indexes created

#### Day 3: CSV Import Scripts
- [ ] Write `scripts/import/lib/csv-parser.ts` (shared streaming parser)
- [ ] Write `scripts/import/lib/date-parser.ts` (CCC date format handler)
- [ ] Write `import-lab-tests.ts` → import 298K rows (~3 min)
- [ ] Write `import-market-sales.ts` → import 67K adult-use + 47K medical (~2 min)
- [ ] Write `import-price-benchmark.ts` → import 71 rows (~1 sec)
- [ ] Write `import-operators-ccc.ts` → import 772 commence-ops rows
- [ ] Write `import-county-licenses.ts` → import 1,753 county rows

#### Day 4: Operator Matching
- [ ] Write `match-operators.ts` (4-pass algorithm from Part 2)
- [ ] Run matching → expect ~450/492 matched
- [ ] Review unmatched operators → determine if they should be added to `operators`
- [ ] Backfill `operators.ccc_license_number`, `email`, `phone` from CCC data

#### Day 5: First Cross-Reference
- [ ] Create `mv_lab_thc_monthly` materialized view
- [ ] Create `mv_menu_thc_monthly` materialized view
- [ ] Create `mv_weekly_market_revenue` materialized view
- [ ] Test THC accuracy query → get first inflation number
- [ ] Test revenue cross-reference → confirm ~36% markup finding

#### Day 6-7: First API Endpoints
- [ ] `/ccc/market-sales/timeseries` (public)
- [ ] `/ccc/price-benchmark` (public)
- [ ] `/intelligence/thc-accuracy` (authenticated)
- [ ] `/intelligence/revenue-cross-ref` (authenticated)
- [ ] Test via Postman/curl
- [ ] Deploy to Railway

**Week 1 Deliverable:** All CCC CSVs imported, operators matched, THC accuracy + revenue cross-reference live on the API.

---

### Week 2-3: Intelligence Layer (Days 8-21)

#### Week 2: Operator Health Score + Threats
- [ ] Create `mv_operator_health_score` materialized view
- [ ] Build `/intelligence/health-score/:operatorId` endpoint
- [ ] Build `/intelligence/health-score/leaderboard` endpoint
- [ ] Create `detect_threats()` function
- [ ] Build `/threats/detect/:operatorId` endpoint
- [ ] Integrate threat detection into existing `threats` table (auto-populate)
- [ ] Build `/ccc/operators/search` endpoint

#### Week 3: Market Gap + Google Reviews
- [ ] Write `import-census.ts` → fetch ACS data for all MA zip codes
- [ ] Create `mv_market_gaps` materialized view
- [ ] Build `/intelligence/market-gap` endpoint
- [ ] Write `scrape-google-reviews.ts` → first full scrape of 492 operators
- [ ] Build `/reviews/:operatorId` endpoint
- [ ] Integrate Google ratings into health score

**Week 2-3 Deliverable:** Health scores for all operators, threat radar functional, market gap analysis live, Google reviews scraped.

---

### Month 1: Full Integration (Days 22-30)

- [ ] Dashboard frontend: Add "Market Intelligence" section (price erosion chart, revenue tide chart)
- [ ] Dashboard frontend: Add "Your Report Card" sidebar widget (health score + breakdown)
- [ ] Dashboard frontend: Add threat radar map integration
- [ ] Newsletter automation: Build monthly data package generator
- [ ] Newsletter: Generate first data-enriched issue
- [ ] Deploy updated frontend to Railway
- [ ] Write admin import trigger endpoints
- [ ] Set up materialized view refresh schedule (cron in Fastify)

**Month 1 Deliverable:** Full GLASS dashboard with CCC cross-references live. Newsletter auto-generates with real data. Admin can trigger re-imports.

---

### Month 2-3: Automated Pipelines + Advanced Analytics (Days 31-90)

#### Month 2: Automation
- [ ] Write `scrape-enforcement.ts` → CCC enforcement page scraper
- [ ] Write `import-strains.ts` → Otreeba API import
- [ ] Set up weekly cron: Google reviews refresh (Sunday 2AM)
- [ ] Set up weekly cron: Enforcement scrape (Monday 8AM)
- [ ] Set up monthly cron: CCC data re-import (1st of month)
- [ ] Build CCC data catalog checker (notify if new CSVs available)
- [ ] Virtual Budtender: Integrate strain data + lab data into recommendation engine
- [ ] SIGNAL: Auto-generate first batch of trend-based SEO pages

#### Month 3: Advanced Analytics
- [ ] Predictive pricing model: Use CCC price trend + scraped prices to forecast next month's market price
- [ ] Category growth predictions: Which product categories will grow/shrink based on trend analysis
- [ ] Operator churn prediction: Which operators are likely to close (expired license + declining reviews + pricing above market)
- [ ] Delivery demand forecasting: Use market sales + census data to predict delivery demand by zip code
- [ ] Build GLASS API developer documentation (for future third-party access)
- [ ] Consider: PostgreSQL → PostGIS migration for native geographic queries

**Month 2-3 Deliverable:** Fully automated data pipelines. All intelligence materialized views auto-refreshing. Virtual Budtender enhanced with lab/strain data. SIGNAL generating SEO pages from data. Predictive analytics layer operational.

---

## Appendix A: SQL Migration Script

```sql
-- GLASS Data Integration Migration
-- Run against Railway PostgreSQL
-- Date: 2026-02-12

BEGIN;

-- 1. Lab Tests
CREATE TABLE IF NOT EXISTS ccc_lab_tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metrc_tag VARCHAR(50) NOT NULL,
  product_category VARCHAR(50) NOT NULL,
  strain VARCHAR(255) NOT NULL,
  test_type VARCHAR(100) NOT NULL,
  test_result DECIMAL(6, 3),
  testing_lab VARCHAR(100) NOT NULL,
  test_date TIMESTAMPTZ NOT NULL,
  test_comment VARCHAR(500),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (metrc_tag, test_type)
);
CREATE INDEX IF NOT EXISTS idx_ccc_lab_tests_metrc ON ccc_lab_tests(metrc_tag);
CREATE INDEX IF NOT EXISTS idx_ccc_lab_tests_strain ON ccc_lab_tests(strain);
CREATE INDEX IF NOT EXISTS idx_ccc_lab_tests_category ON ccc_lab_tests(product_category);
CREATE INDEX IF NOT EXISTS idx_ccc_lab_tests_date ON ccc_lab_tests(test_date);
CREATE INDEX IF NOT EXISTS idx_ccc_lab_tests_type ON ccc_lab_tests(test_type);
CREATE INDEX IF NOT EXISTS idx_ccc_lab_tests_lab ON ccc_lab_tests(testing_lab);
CREATE INDEX IF NOT EXISTS idx_ccc_lab_tests_result ON ccc_lab_tests(test_result);
CREATE INDEX IF NOT EXISTS idx_ccc_lab_tests_strain_type_date ON ccc_lab_tests(strain, test_type, test_date);

-- 2. Market Sales (unified adult-use + medical)
CREATE TABLE IF NOT EXISTS ccc_market_sales (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sale_date TIMESTAMPTZ NOT NULL,
  delivery_type VARCHAR(50) NOT NULL,
  product_category VARCHAR(100) NOT NULL,
  unit_of_measure VARCHAR(20) NOT NULL,
  quantity DECIMAL(14, 2),
  units INTEGER,
  count_based_total DECIMAL(14, 2),
  dollar_count_based DECIMAL(14, 2),
  weight_based_total DECIMAL(14, 2),
  dollar_weight_based DECIMAL(14, 2),
  total_dollars DECIMAL(14, 2) NOT NULL,
  market_type VARCHAR(20) NOT NULL DEFAULT 'adult_use',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (sale_date, delivery_type, product_category, market_type)
);
CREATE INDEX IF NOT EXISTS idx_ccc_market_sales_date ON ccc_market_sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_ccc_market_sales_category ON ccc_market_sales(product_category);
CREATE INDEX IF NOT EXISTS idx_ccc_market_sales_delivery ON ccc_market_sales(delivery_type);
CREATE INDEX IF NOT EXISTS idx_ccc_market_sales_market ON ccc_market_sales(market_type);
CREATE INDEX IF NOT EXISTS idx_ccc_market_sales_date_cat ON ccc_market_sales(sale_date, product_category);
CREATE INDEX IF NOT EXISTS idx_ccc_market_sales_date_delivery ON ccc_market_sales(sale_date, delivery_type);

-- 3. Monthly Price Benchmark
CREATE TABLE IF NOT EXISTS ccc_monthly_price_benchmark (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  year_month VARCHAR(7) NOT NULL UNIQUE,
  avg_price_per_gram DECIMAL(6, 2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ccc_price_benchmark_month ON ccc_monthly_price_benchmark(year_month);

-- 4. Licensed Operators (CCC Master)
CREATE TABLE IF NOT EXISTS ccc_licensed_operators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_name VARCHAR(500) NOT NULL,
  license_type VARCHAR(100) NOT NULL,
  license_number VARCHAR(50) NOT NULL UNIQUE,
  ein_tin VARCHAR(20),
  application_status VARCHAR(50),
  approved_license_type VARCHAR(100),
  license_status VARCHAR(50) NOT NULL,
  application_classification VARCHAR(100),
  classification_detail_1 VARCHAR(100),
  classification_detail_2 VARCHAR(100),
  approved_license_stage VARCHAR(50),
  cultivation_environment VARCHAR(50),
  cultivation_tier VARCHAR(100),
  is_priority BOOLEAN DEFAULT false,
  dbe_status VARCHAR(200),
  rmd_priority_status VARCHAR(50),
  business_email VARCHAR(255),
  business_phone VARCHAR(30),
  business_address TEXT,
  business_city VARCHAR(100),
  business_state VARCHAR(2),
  business_zip VARCHAR(10),
  establishment_address TEXT,
  establishment_city VARCHAR(100),
  establishment_state VARCHAR(2),
  establishment_zip VARCHAR(10),
  lat DECIMAL(10, 8),
  lon DECIMAL(11, 8),
  county VARCHAR(100),
  submitted_date TIMESTAMPTZ,
  approved_date TIMESTAMPTZ,
  license_start_date TIMESTAMPTZ,
  license_expiration_date TIMESTAMPTZ,
  commence_operations_date TIMESTAMPTZ,
  license_fee DECIMAL(10, 2),
  payment_amount DECIMAL(10, 2),
  ccc_last_updated TIMESTAMPTZ,
  glass_operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_license ON ccc_licensed_operators(license_number);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_name ON ccc_licensed_operators(business_name);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_type ON ccc_licensed_operators(license_type);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_status ON ccc_licensed_operators(license_status);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_city ON ccc_licensed_operators(establishment_city);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_county ON ccc_licensed_operators(county);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_location ON ccc_licensed_operators(lat, lon);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_dbe ON ccc_licensed_operators(dbe_status);
CREATE INDEX IF NOT EXISTS idx_ccc_operators_glass_link ON ccc_licensed_operators(glass_operator_id);

-- 5. County Licenses
CREATE TABLE IF NOT EXISTS ccc_county_licenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_status VARCHAR(50),
  license_type VARCHAR(100) NOT NULL,
  application_classification VARCHAR(100),
  classification_detail_1 VARCHAR(100),
  classification_detail_2 VARCHAR(100),
  approved_license_type VARCHAR(100),
  approved_license_stage VARCHAR(50),
  commence_operations_date TIMESTAMPTZ,
  license_status VARCHAR(50),
  license_number VARCHAR(50) NOT NULL UNIQUE,
  business_name VARCHAR(500) NOT NULL,
  establishment_city VARCHAR(100),
  establishment_zip VARCHAR(10),
  business_email VARCHAR(255),
  business_phone VARCHAR(30),
  business_address TEXT,
  business_city VARCHAR(100),
  business_state VARCHAR(2),
  business_zip VARCHAR(10),
  ein_tin VARCHAR(20),
  dbe_status VARCHAR(200),
  cultivation_environment VARCHAR(50),
  cultivation_tier VARCHAR(100),
  town VARCHAR(100),
  county VARCHAR(100),
  county_lat DECIMAL(10, 6),
  county_lon DECIMAL(11, 6),
  region VARCHAR(100),
  lat DECIMAL(10, 8),
  lon DECIMAL(11, 8),
  se_number VARCHAR(50),
  priority VARCHAR(100),
  fee_waiver VARCHAR(20),
  submitted_date TIMESTAMPTZ,
  approved_date TIMESTAMPTZ,
  license_start_date TIMESTAMPTZ,
  license_expiration_date TIMESTAMPTZ,
  license_fee DECIMAL(10, 2),
  payment_amount DECIMAL(10, 2),
  ccc_last_updated TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ccc_county_licenses_county ON ccc_county_licenses(county);
CREATE INDEX IF NOT EXISTS idx_ccc_county_licenses_type ON ccc_county_licenses(license_type);
CREATE INDEX IF NOT EXISTS idx_ccc_county_licenses_town ON ccc_county_licenses(town);
CREATE INDEX IF NOT EXISTS idx_ccc_county_licenses_region ON ccc_county_licenses(region);
CREATE INDEX IF NOT EXISTS idx_ccc_county_licenses_license ON ccc_county_licenses(license_number);
CREATE INDEX IF NOT EXISTS idx_ccc_county_licenses_status ON ccc_county_licenses(license_status);

-- 6. Google Reviews
CREATE TABLE IF NOT EXISTS google_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  google_place_id VARCHAR(255),
  rating DECIMAL(2, 1),
  total_reviews INTEGER,
  review_text TEXT,
  review_author VARCHAR(255),
  review_rating INTEGER,
  review_time TIMESTAMPTZ,
  review_language VARCHAR(5),
  scraped_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_google_reviews_operator ON google_reviews(operator_id);
CREATE INDEX IF NOT EXISTS idx_google_reviews_rating ON google_reviews(rating);
CREATE INDEX IF NOT EXISTS idx_google_reviews_scraped ON google_reviews(scraped_at);
CREATE INDEX IF NOT EXISTS idx_google_reviews_place ON google_reviews(google_place_id);

CREATE TABLE IF NOT EXISTS google_place_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE UNIQUE,
  google_place_id VARCHAR(255),
  current_rating DECIMAL(2, 1),
  total_reviews INTEGER,
  price_level INTEGER,
  business_status VARCHAR(50),
  hours_json JSONB,
  popular_times_json JSONB,
  scraped_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_google_place_stats_operator ON google_place_stats(operator_id);
CREATE INDEX IF NOT EXISTS idx_google_place_stats_rating ON google_place_stats(current_rating);

-- 7. Census Demographics
CREATE TABLE IF NOT EXISTS census_demographics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  geo_type VARCHAR(20) NOT NULL,
  geo_id VARCHAR(20) NOT NULL,
  geo_name VARCHAR(255) NOT NULL,
  state_fips VARCHAR(2) NOT NULL DEFAULT '25',
  total_population INTEGER,
  median_household_income INTEGER,
  median_age DECIMAL(4, 1),
  pct_age_21_34 DECIMAL(5, 2),
  pct_age_35_54 DECIMAL(5, 2),
  pct_age_55_plus DECIMAL(5, 2),
  total_housing_units INTEGER,
  pct_renter_occupied DECIMAL(5, 2),
  pct_bachelor_plus DECIMAL(5, 2),
  acs_year INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (geo_type, geo_id, acs_year)
);
CREATE INDEX IF NOT EXISTS idx_census_geo_type ON census_demographics(geo_type);
CREATE INDEX IF NOT EXISTS idx_census_geo_id ON census_demographics(geo_id);
CREATE INDEX IF NOT EXISTS idx_census_population ON census_demographics(total_population);
CREATE INDEX IF NOT EXISTS idx_census_income ON census_demographics(median_household_income);

-- 8. Enforcement Actions
CREATE TABLE IF NOT EXISTS ccc_enforcement_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  license_number VARCHAR(50),
  business_name VARCHAR(500) NOT NULL,
  action_type VARCHAR(100) NOT NULL,
  action_date TIMESTAMPTZ NOT NULL,
  fine_amount DECIMAL(10, 2),
  description TEXT,
  resolution TEXT,
  resolved_date TIMESTAMPTZ,
  source_url TEXT,
  document_url TEXT,
  glass_operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_enforcement_license ON ccc_enforcement_actions(license_number);
CREATE INDEX IF NOT EXISTS idx_enforcement_name ON ccc_enforcement_actions(business_name);
CREATE INDEX IF NOT EXISTS idx_enforcement_type ON ccc_enforcement_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_enforcement_date ON ccc_enforcement_actions(action_date);
CREATE INDEX IF NOT EXISTS idx_enforcement_operator ON ccc_enforcement_actions(glass_operator_id);

-- 9. Strains
CREATE TABLE IF NOT EXISTS strains (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  otreeba_id VARCHAR(50),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) NOT NULL UNIQUE,
  strain_type VARCHAR(20),
  thc_avg DECIMAL(5, 2),
  cbd_avg DECIMAL(5, 2),
  effects JSONB,
  flavors JSONB,
  description TEXT,
  lineage JSONB,
  terpene_profile JSONB,
  grow_info JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_strains_name ON strains(name);
CREATE INDEX IF NOT EXISTS idx_strains_type ON strains(strain_type);
CREATE INDEX IF NOT EXISTS idx_strains_otreeba ON strains(otreeba_id);

-- 10. Add CCC link columns to existing operators table
ALTER TABLE operators ADD COLUMN IF NOT EXISTS ccc_license_number VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS ccc_license_type VARCHAR(100);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS ccc_dbe_status VARCHAR(200);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS google_place_id VARCHAR(255);
CREATE INDEX IF NOT EXISTS idx_operators_ccc_license ON operators(ccc_license_number);
CREATE INDEX IF NOT EXISTS idx_operators_google_place ON operators(google_place_id);

COMMIT;
```

---

## Appendix B: Materialized View DDL

```sql
-- Run AFTER data import

-- 1. Lab THC Monthly Averages
CREATE MATERIALIZED VIEW mv_lab_thc_monthly AS
SELECT
  DATE_TRUNC('month', test_date) AS month,
  product_category,
  test_type,
  COUNT(*) AS test_count,
  ROUND(AVG(test_result)::numeric, 2) AS avg_thc,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY test_result)::numeric, 2) AS median_thc,
  ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY test_result)::numeric, 2) AS p25_thc,
  ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY test_result)::numeric, 2) AS p75_thc,
  ROUND(STDDEV(test_result)::numeric, 2) AS stddev_thc
FROM ccc_lab_tests
WHERE test_result BETWEEN 0.1 AND 50
GROUP BY DATE_TRUNC('month', test_date), product_category, test_type
ORDER BY month;

CREATE UNIQUE INDEX ON mv_lab_thc_monthly(month, product_category, test_type);

-- 2. Menu THC Monthly Averages (from scraped data)
CREATE MATERIALIZED VIEW mv_menu_thc_monthly AS
SELECT
  DATE_TRUNC('month', pr.scraped_at) AS month,
  p.category,
  COUNT(*) AS listing_count,
  ROUND(AVG(p.thc_percent::numeric), 2) AS avg_listed_thc,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p.thc_percent::numeric)::numeric, 2) AS median_listed_thc,
  ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY p.thc_percent::numeric)::numeric, 2) AS p25_listed_thc,
  ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY p.thc_percent::numeric)::numeric, 2) AS p75_listed_thc
FROM prices pr
JOIN products p ON pr.product_id = p.id
WHERE p.thc_percent IS NOT NULL
  AND p.thc_percent::numeric BETWEEN 0.1 AND 50
GROUP BY DATE_TRUNC('month', pr.scraped_at), p.category
ORDER BY month;

CREATE UNIQUE INDEX ON mv_menu_thc_monthly(month, category);

-- 3. Weekly Market Revenue
CREATE MATERIALIZED VIEW mv_weekly_market_revenue AS
SELECT
  DATE_TRUNC('week', sale_date) AS week,
  product_category,
  delivery_type,
  market_type,
  SUM(total_dollars) AS total_revenue,
  SUM(COALESCE(weight_based_total, 0)) AS total_grams,
  SUM(COALESCE(count_based_total, 0)) AS total_units,
  CASE
    WHEN SUM(COALESCE(weight_based_total, 0)) > 0
    THEN ROUND((SUM(COALESCE(dollar_weight_based, 0)) / SUM(weight_based_total))::numeric, 2)
    ELSE NULL
  END AS implied_price_per_gram,
  CASE
    WHEN SUM(COALESCE(count_based_total, 0)) > 0
    THEN ROUND((SUM(COALESCE(dollar_count_based, 0)) / SUM(count_based_total))::numeric, 2)
    ELSE NULL
  END AS implied_price_per_unit
FROM ccc_market_sales
GROUP BY DATE_TRUNC('week', sale_date), product_category, delivery_type, market_type
ORDER BY week DESC, total_revenue DESC;

CREATE UNIQUE INDEX ON mv_weekly_market_revenue(week, product_category, delivery_type, market_type);

-- 4. Operator Health Score
-- (See Part 3.3 for full query — depends on Google reviews existing)
-- Created in Week 2 after Google reviews are scraped

-- 5. Market Gaps
-- (See Part 3.4 for full query — depends on Census data existing)
-- Created in Week 3 after Census data is imported
```

---

## Appendix C: Environment Variables

Add to Railway glass-api service:

```bash
# No new env vars needed for CSV imports (they're one-time scripts run locally)
# Google Places API key is already configured

# Future additions:
CENSUS_API_KEY=your_key_here   # Free from census.gov (optional, no key needed for basic queries)
OTREEBA_API_URL=https://api.otreeba.com/v1  # No key needed
```

---

## Appendix D: Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| CCC anonymized strain names → can't match to products | Limits THC accuracy to category-level, not product-level | Use statistical distribution comparison instead of direct match. Advocate for CCC to release real strain names. |
| Market sales are statewide, not per-facility | Can't calculate individual operator revenue | Revenue intel is market-level. Combine with scraped price data for relative positioning (is this operator above/below market?). |
| Operator matching false positives | Wrong CCC data linked to wrong GLASS operator | Multi-pass algorithm with increasing strictness. Manual review of geo-proximity matches. Validation report for admin. |
| CCC data refresh lag | Data could be months stale | Accept quarterly lag on lab data. Monthly on sales. Display "data as of" dates prominently. |
| Railway storage limits | 250MB new data could push limits | Railway Hobby plan has no hard storage limit. Watch for $5+/GB/mo beyond 500MB. Current usage ~200MB. |
| Google Places API costs | 492 operators × weekly = ~2,000 calls/month | Places API basic = $0 for first 100K calls/mo. We're well under. |

---

## Appendix E: Success Metrics

| Metric | Target (Month 1) | Target (Month 3) |
|--------|------------------|-------------------|
| CCC tables populated | 7/7 | 7/7 + automated refresh |
| Operator match rate | >85% | >95% (with manual corrections) |
| Cross-reference views | 3 live | 5+ live |
| New API endpoints | 8 | 15+ |
| Newsletter data points | 5 per issue | 8+ per issue |
| Dashboard visualizations | 2 new | 6+ new |
| THC accuracy data | Monthly aggregates | Per-operator scores |
| Market gap analysis | Zip-level | Zip + town + county |
| Health scores | Basic (price + breadth) | Full composite (+ reviews + compliance) |

---

*This document is the single source of truth for the GLASS data integration project. All implementation should reference this plan. Update this document as decisions change.*

**Estimated total engineering effort:** 120-160 hours across 2-3 months.
**Estimated infrastructure cost increase:** ~$5-10/mo (mostly storage, negligible compute for batch imports).
**Expected revenue impact:** This data transforms GLASS from a $49/mo price tool into a $149-299/mo intelligence platform. At 50 subscribers, that's the difference between $2,450/mo and $14,950/mo ARR.
