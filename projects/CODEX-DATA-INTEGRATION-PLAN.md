# GLASS Data Integration Plan (Public Data Expansion)

**Author:** Senior Data Engineering / Systems Architecture Plan  
**Date:** 2026-02-12 (UTC)  
**Target stack:** PostgreSQL (Railway) + Fastify + Drizzle ORM + React/Vite + Clerk  
**API base:** `https://glass-api-production.up.railway.app`

---

## 0) Executive Architecture Decisions (Opinionated)

1. **Use a bronze/silver/gold data model in one Postgres cluster** (raw ingest tables → normalized canonical tables → materialized intelligence views).
2. **Treat CCC CSVs as periodic append-or-restate snapshots**, not true CDC streams. Build deterministic upserts with dataset fingerprints.
3. **Create an explicit operator identity resolution layer** (`operator_aliases`, `operator_match_candidates`) rather than writing fuzzy results directly into `operators`.
4. **Partition only where read/write patterns justify it**:
   - `lab_test_results`: range partition by `test_performed_date` month.
   - Keep small/medium tables non-partitioned.
5. **Compute business scores in SQL materialized views + scheduled refresh**, not per-request in API handlers.
6. **Cache only top fan-out endpoints** with Redis (5–30 min TTL), keep operator-specific intelligence in DB with indexed queries.
7. **Store PII-sensitive fields (emails/phones/EIN) with minimization controls** and explicit admin-only exposure.

---

## 1) Dataset Inventory and Canonical Mapping

### 1.1 Immediate datasets (already downloaded)

| # | File | Size | Canonical destination |
|---|------|------|----------------------|
|1|`testing-thc-thca.csv`|298,343 rows|`lab_test_results` + `lab_test_batches` + `operator_quality_daily`|
|2|`facility-sales-stats.csv`|67,334 rows|`facility_sales_daily`|
|3|`itd-retail-delivery-sales.csv`|67,334 rows|`itd_sales_daily`|
|4|`medical-facility-stats.csv`|47,648 rows|`medical_sales_daily`|
|5|`avg-monthly-price-oz.csv`|72 rows|`state_monthly_price_benchmark`|
|6|`commence-ops.csv`|773 rows|`ccc_operator_registry` + matching layer|
|7|`adult-market-data-counties.csv`|1,754 rows|`county_market_daily` + county/operator mapping|

### 1.2 Future datasets (planned)

| # | Source | Canonical destination |
|---|--------|-----------------------|
|8|Google Places Reviews API|`operator_google_places`, `operator_google_reviews_daily`|
|9|US Census API|`geo_census_profile`|
|10|CCC enforcement docs scrape|`ccc_enforcement_actions`|
|11|Otreeba strain API|`strain_reference`, `product_strain_map`|

---

## 2) A) Schema Design (Drizzle + constraints + indexes + partitioning)

> Add this as new module `src/services/api/src/db/schema_ccc_intelligence.ts` and export in db index.

```ts
import {
  pgTable,
  uuid,
  varchar,
  text,
  timestamp,
  boolean,
  integer,
  decimal,
  jsonb,
  date,
  unique,
  index,
  primaryKey,
} from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';
import { operators, products } from './schema';

// -----------------------------
// DATASET RUN/AUDIT LAYER
// -----------------------------
export const datasetIngestRuns = pgTable('dataset_ingest_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  dataset_key: varchar('dataset_key', { length: 80 }).notNull(), // e.g. ccc.testing_thc_thca
  source_file_name: varchar('source_file_name', { length: 255 }).notNull(),
  file_sha256: varchar('file_sha256', { length: 64 }).notNull(),
  source_updated_at: timestamp('source_updated_at', { withTimezone: true }),
  row_count_raw: integer('row_count_raw').notNull().default(0),
  row_count_loaded: integer('row_count_loaded').notNull().default(0),
  row_count_rejected: integer('row_count_rejected').notNull().default(0),
  status: varchar('status', { length: 20 }).notNull().default('running'), // running|success|failed|partial
  error_summary: text('error_summary'),
  metrics: jsonb('metrics').default({}),
  started_at: timestamp('started_at', { withTimezone: true }).notNull().defaultNow(),
  completed_at: timestamp('completed_at', { withTimezone: true }),
}, (t) => [
  unique('dataset_ingest_runs_dataset_file_hash_unq').on(t.dataset_key, t.file_sha256),
  index('idx_dataset_ingest_runs_dataset').on(t.dataset_key, t.started_at),
  index('idx_dataset_ingest_runs_status').on(t.status),
]);

export const datasetRejectRows = pgTable('dataset_reject_rows', {
  id: uuid('id').primaryKey().defaultRandom(),
  ingest_run_id: uuid('ingest_run_id').notNull().references(() => datasetIngestRuns.id, { onDelete: 'cascade' }),
  dataset_key: varchar('dataset_key', { length: 80 }).notNull(),
  line_number: integer('line_number').notNull(),
  reason_code: varchar('reason_code', { length: 80 }).notNull(),
  reason_detail: text('reason_detail'),
  raw_row: jsonb('raw_row').notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  index('idx_dataset_reject_rows_run').on(t.ingest_run_id),
  index('idx_dataset_reject_rows_dataset').on(t.dataset_key),
]);

// -----------------------------
// OPERATOR IDENTITY RESOLUTION LAYER
// -----------------------------
export const operatorAliases = pgTable('operator_aliases', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  alias_name: varchar('alias_name', { length: 255 }).notNull(),
  alias_normalized: varchar('alias_normalized', { length: 255 }).notNull(),
  source_system: varchar('source_system', { length: 50 }).notNull(), // ccc, google, manual
  confidence: decimal('confidence', { precision: 5, scale: 4 }).notNull().default('1.0000'),
  is_primary: boolean('is_primary').notNull().default(false),
  metadata: jsonb('metadata').default({}),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('operator_aliases_operator_source_alias_unq').on(t.operator_id, t.source_system, t.alias_normalized),
  index('idx_operator_aliases_norm').on(t.alias_normalized),
  index('idx_operator_aliases_operator').on(t.operator_id),
]);

export const operatorMatchCandidates = pgTable('operator_match_candidates', {
  id: uuid('id').primaryKey().defaultRandom(),
  source_system: varchar('source_system', { length: 50 }).notNull(),
  source_record_key: varchar('source_record_key', { length: 255 }).notNull(),
  source_name: varchar('source_name', { length: 255 }).notNull(),
  source_city: varchar('source_city', { length: 120 }),
  source_license_number: varchar('source_license_number', { length: 100 }),
  matched_operator_id: uuid('matched_operator_id').references(() => operators.id, { onDelete: 'set null' }),
  similarity_score: decimal('similarity_score', { precision: 5, scale: 4 }),
  status: varchar('status', { length: 20 }).notNull().default('pending'), // pending|auto_matched|manual_confirmed|manual_rejected
  rationale: jsonb('rationale').default({}),
  reviewed_by_user_id: uuid('reviewed_by_user_id'),
  reviewed_at: timestamp('reviewed_at', { withTimezone: true }),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('operator_match_candidates_src_unq').on(t.source_system, t.source_record_key),
  index('idx_operator_match_candidates_status').on(t.status),
  index('idx_operator_match_candidates_operator').on(t.matched_operator_id),
]);

// -----------------------------
// COMMENCE OPS + ADULT COUNTY REGISTRY
// -----------------------------
export const cccOperatorRegistry = pgTable('ccc_operator_registry', {
  id: uuid('id').primaryKey().defaultRandom(),
  source_record_key: varchar('source_record_key', { length: 255 }).notNull(), // hash/business+license
  business_name: varchar('business_name', { length: 255 }).notNull(),
  business_name_normalized: varchar('business_name_normalized', { length: 255 }).notNull(),
  license_number: varchar('license_number', { length: 100 }),
  license_type: varchar('license_type', { length: 120 }),
  application_status: varchar('application_status', { length: 80 }),
  license_status: varchar('license_status', { length: 80 }),
  ein_tin: varchar('ein_tin', { length: 32 }), // restrict output access
  business_email: varchar('business_email', { length: 255 }),
  business_phone: varchar('business_phone', { length: 32 }),
  address_1: varchar('address_1', { length: 255 }),
  city: varchar('city', { length: 120 }),
  state: varchar('state', { length: 2 }),
  zip_code: varchar('zip_code', { length: 12 }),
  county: varchar('county', { length: 120 }),
  dbe_flag: boolean('dbe_flag'),
  source_dataset: varchar('source_dataset', { length: 60 }).notNull(), // commence_ops | adult_market_counties
  matched_operator_id: uuid('matched_operator_id').references(() => operators.id, { onDelete: 'set null' }),
  raw_payload: jsonb('raw_payload').notNull(),
  valid_from: date('valid_from').default(sql`CURRENT_DATE`),
  valid_to: date('valid_to'),
  is_current: boolean('is_current').notNull().default(true),
  ingest_run_id: uuid('ingest_run_id').references(() => datasetIngestRuns.id, { onDelete: 'set null' }),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('ccc_operator_registry_src_key_unq').on(t.source_record_key, t.source_dataset, t.is_current),
  index('idx_ccc_operator_registry_license').on(t.license_number),
  index('idx_ccc_operator_registry_match').on(t.matched_operator_id),
  index('idx_ccc_operator_registry_name_norm').on(t.business_name_normalized),
]);

// -----------------------------
// LAB TESTING (PARTITIONED IN SQL MIGRATION)
// -----------------------------
export const labTestResults = pgTable('lab_test_results', {
  id: uuid('id').primaryKey().defaultRandom(),
  metrc_tag_id: varchar('metrc_tag_id', { length: 120 }).notNull(),
  product_category_type: varchar('product_category_type', { length: 120 }),
  strain_name: varchar('strain_name', { length: 255 }),
  test_type_name: varchar('test_type_name', { length: 120 }).notNull(), // THC | THCA
  test_result_pct: decimal('test_result_pct', { precision: 8, scale: 4 }).notNull(),
  testing_lab_name: varchar('testing_lab_name', { length: 255 }),
  test_performed_date: date('test_performed_date').notNull(),
  test_comment: text('test_comment'),
  source_row_hash: varchar('source_row_hash', { length: 64 }).notNull(),
  ingest_run_id: uuid('ingest_run_id').references(() => datasetIngestRuns.id, { onDelete: 'set null' }),
  raw_payload: jsonb('raw_payload').notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('lab_test_results_source_row_hash_unq').on(t.source_row_hash),
  index('idx_lab_test_results_metrc').on(t.metrc_tag_id),
  index('idx_lab_test_results_date').on(t.test_performed_date),
  index('idx_lab_test_results_type_date').on(t.test_type_name, t.test_performed_date),
  index('idx_lab_test_results_strain').on(t.strain_name),
]);

export const labTestBatches = pgTable('lab_test_batches', {
  id: uuid('id').primaryKey().defaultRandom(),
  metrc_tag_id: varchar('metrc_tag_id', { length: 120 }).notNull(),
  strain_name: varchar('strain_name', { length: 255 }),
  product_category_type: varchar('product_category_type', { length: 120 }),
  testing_lab_name: varchar('testing_lab_name', { length: 255 }),
  test_performed_date: date('test_performed_date').notNull(),
  thc_pct: decimal('thc_pct', { precision: 8, scale: 4 }),
  thca_pct: decimal('thca_pct', { precision: 8, scale: 4 }),
  total_potential_thc_pct: decimal('total_potential_thc_pct', { precision: 8, scale: 4 }),
  source_count: integer('source_count').notNull().default(1),
  source_last_ingest_run_id: uuid('source_last_ingest_run_id').references(() => datasetIngestRuns.id, { onDelete: 'set null' }),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('lab_test_batches_metrc_date_unq').on(t.metrc_tag_id, t.test_performed_date),
  index('idx_lab_test_batches_date').on(t.test_performed_date),
  index('idx_lab_test_batches_total_thc').on(t.total_potential_thc_pct),
]);

// -----------------------------
// SALES FACT TABLES
// -----------------------------
export const facilitySalesDaily = pgTable('facility_sales_daily', {
  id: uuid('id').primaryKey().defaultRandom(),
  sale_date: date('sale_date').notNull(),
  sale_period: varchar('sale_period', { length: 40 }),
  data_type: varchar('data_type', { length: 80 }),
  sales_period_type: varchar('sales_period_type', { length: 40 }),
  delivery_type: varchar('delivery_type', { length: 80 }),
  product_category_name: varchar('product_category_name', { length: 120 }),
  unit_of_measure_name: varchar('unit_of_measure_name', { length: 40 }),
  quantity: decimal('quantity', { precision: 16, scale: 4 }),
  units: decimal('units', { precision: 16, scale: 4 }),
  count_based_total: decimal('count_based_total', { precision: 16, scale: 4 }),
  dollar_count_based_total: decimal('dollar_count_based_total', { precision: 16, scale: 2 }),
  weight_based_total: decimal('weight_based_total', { precision: 16, scale: 4 }),
  dollar_weight_based_total: decimal('dollar_weight_based_total', { precision: 16, scale: 2 }),
  total_dollars: decimal('total_dollars', { precision: 16, scale: 2 }).notNull(),
  source_row_hash: varchar('source_row_hash', { length: 64 }).notNull(),
  ingest_run_id: uuid('ingest_run_id').references(() => datasetIngestRuns.id, { onDelete: 'set null' }),
  raw_payload: jsonb('raw_payload').notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('facility_sales_daily_row_hash_unq').on(t.source_row_hash),
  index('idx_facility_sales_daily_date').on(t.sale_date),
  index('idx_facility_sales_daily_cat_date').on(t.product_category_name, t.sale_date),
  index('idx_facility_sales_daily_delivery').on(t.delivery_type, t.sale_date),
]);

export const itdSalesDaily = pgTable('itd_sales_daily', {
  id: uuid('id').primaryKey().defaultRandom(),
  sale_date: date('sale_date').notNull(),
  channel_type: varchar('channel_type', { length: 80 }).notNull(), // delivery_operator|courier|retail etc
  product_category_name: varchar('product_category_name', { length: 120 }),
  quantity: decimal('quantity', { precision: 16, scale: 4 }),
  total_dollars: decimal('total_dollars', { precision: 16, scale: 2 }).notNull(),
  source_row_hash: varchar('source_row_hash', { length: 64 }).notNull(),
  ingest_run_id: uuid('ingest_run_id').references(() => datasetIngestRuns.id, { onDelete: 'set null' }),
  raw_payload: jsonb('raw_payload').notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('itd_sales_daily_row_hash_unq').on(t.source_row_hash),
  index('idx_itd_sales_daily_date').on(t.sale_date),
  index('idx_itd_sales_daily_channel_date').on(t.channel_type, t.sale_date),
]);

export const medicalSalesDaily = pgTable('medical_sales_daily', {
  id: uuid('id').primaryKey().defaultRandom(),
  sale_date: date('sale_date').notNull(),
  product_category_name: varchar('product_category_name', { length: 120 }),
  quantity: decimal('quantity', { precision: 16, scale: 4 }),
  total_dollars: decimal('total_dollars', { precision: 16, scale: 2 }).notNull(),
  source_row_hash: varchar('source_row_hash', { length: 64 }).notNull(),
  ingest_run_id: uuid('ingest_run_id').references(() => datasetIngestRuns.id, { onDelete: 'set null' }),
  raw_payload: jsonb('raw_payload').notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('medical_sales_daily_row_hash_unq').on(t.source_row_hash),
  index('idx_medical_sales_daily_date').on(t.sale_date),
  index('idx_medical_sales_daily_cat').on(t.product_category_name, t.sale_date),
]);

export const stateMonthlyPriceBenchmark = pgTable('state_monthly_price_benchmark', {
  id: uuid('id').primaryKey().defaultRandom(),
  benchmark_month: date('benchmark_month').notNull(), // set to first day of month
  avg_price_per_ounce: decimal('avg_price_per_ounce', { precision: 10, scale: 2 }).notNull(),
  avg_price_per_gram: decimal('avg_price_per_gram', { precision: 10, scale: 4 }).notNull(),
  source_row_hash: varchar('source_row_hash', { length: 64 }).notNull(),
  ingest_run_id: uuid('ingest_run_id').references(() => datasetIngestRuns.id, { onDelete: 'set null' }),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('state_monthly_price_benchmark_month_unq').on(t.benchmark_month),
  index('idx_state_monthly_price_benchmark_month').on(t.benchmark_month),
]);

export const countyMarketDaily = pgTable('county_market_daily', {
  id: uuid('id').primaryKey().defaultRandom(),
  county: varchar('county', { length: 120 }).notNull(),
  report_date: date('report_date').notNull(),
  metric_name: varchar('metric_name', { length: 120 }).notNull(),
  metric_value: decimal('metric_value', { precision: 18, scale: 4 }),
  unit: varchar('unit', { length: 40 }),
  source_row_hash: varchar('source_row_hash', { length: 64 }).notNull(),
  ingest_run_id: uuid('ingest_run_id').references(() => datasetIngestRuns.id, { onDelete: 'set null' }),
  raw_payload: jsonb('raw_payload').notNull(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('county_market_daily_row_hash_unq').on(t.source_row_hash),
  index('idx_county_market_daily_county_date').on(t.county, t.report_date),
  index('idx_county_market_daily_metric').on(t.metric_name, t.report_date),
]);

// -----------------------------
// GOOGLE + CENSUS + ENFORCEMENT + STRAINS
// -----------------------------
export const operatorGooglePlaces = pgTable('operator_google_places', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  place_id: varchar('place_id', { length: 255 }).notNull(),
  place_name: varchar('place_name', { length: 255 }),
  formatted_address: varchar('formatted_address', { length: 255 }),
  rating: decimal('rating', { precision: 3, scale: 2 }),
  user_ratings_total: integer('user_ratings_total'),
  price_level: integer('price_level'),
  website: text('website'),
  phone: varchar('phone', { length: 40 }),
  raw_payload: jsonb('raw_payload').notNull(),
  last_synced_at: timestamp('last_synced_at', { withTimezone: true }).notNull().defaultNow(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('operator_google_places_operator_unq').on(t.operator_id),
  unique('operator_google_places_place_unq').on(t.place_id),
  index('idx_operator_google_places_rating').on(t.rating),
]);

export const operatorGoogleReviewsDaily = pgTable('operator_google_reviews_daily', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  as_of_date: date('as_of_date').notNull(),
  rating: decimal('rating', { precision: 3, scale: 2 }),
  total_reviews: integer('total_reviews').notNull(),
  reviews_delta_7d: integer('reviews_delta_7d'),
  sentiment_score: decimal('sentiment_score', { precision: 6, scale: 4 }),
  source_payload: jsonb('source_payload').default({}),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('operator_google_reviews_daily_operator_date_unq').on(t.operator_id, t.as_of_date),
  index('idx_operator_google_reviews_daily_date').on(t.as_of_date),
]);

export const geoCensusProfile = pgTable('geo_census_profile', {
  id: uuid('id').primaryKey().defaultRandom(),
  geo_type: varchar('geo_type', { length: 40 }).notNull(), // county|tract|zip
  geo_id: varchar('geo_id', { length: 40 }).notNull(),
  state_fips: varchar('state_fips', { length: 2 }).notNull(),
  county_fips: varchar('county_fips', { length: 3 }),
  population_total: integer('population_total'),
  median_household_income: integer('median_household_income'),
  median_age: decimal('median_age', { precision: 5, scale: 2 }),
  pct_21_plus: decimal('pct_21_plus', { precision: 6, scale: 3 }),
  pct_white: decimal('pct_white', { precision: 6, scale: 3 }),
  pct_black: decimal('pct_black', { precision: 6, scale: 3 }),
  pct_hispanic: decimal('pct_hispanic', { precision: 6, scale: 3 }),
  source_year: integer('source_year').notNull(),
  source_payload: jsonb('source_payload').default({}),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('geo_census_profile_geo_year_unq').on(t.geo_type, t.geo_id, t.source_year),
  index('idx_geo_census_profile_geo').on(t.geo_type, t.geo_id),
]);

export const cccEnforcementActions = pgTable('ccc_enforcement_actions', {
  id: uuid('id').primaryKey().defaultRandom(),
  source_doc_url: text('source_doc_url').notNull(),
  source_doc_hash: varchar('source_doc_hash', { length: 64 }).notNull(),
  action_date: date('action_date').notNull(),
  business_name: varchar('business_name', { length: 255 }),
  license_number: varchar('license_number', { length: 120 }),
  action_type: varchar('action_type', { length: 120 }).notNull(),
  severity: varchar('severity', { length: 40 }),
  fine_amount: decimal('fine_amount', { precision: 12, scale: 2 }),
  summary: text('summary'),
  matched_operator_id: uuid('matched_operator_id').references(() => operators.id, { onDelete: 'set null' }),
  source_payload: jsonb('source_payload').default({}),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('ccc_enforcement_actions_doc_hash_unq').on(t.source_doc_hash),
  index('idx_ccc_enforcement_actions_date').on(t.action_date),
  index('idx_ccc_enforcement_actions_operator').on(t.matched_operator_id),
]);

export const strainReference = pgTable('strain_reference', {
  id: uuid('id').primaryKey().defaultRandom(),
  provider: varchar('provider', { length: 40 }).notNull().default('otreeba'),
  provider_strain_id: varchar('provider_strain_id', { length: 120 }).notNull(),
  canonical_name: varchar('canonical_name', { length: 255 }).notNull(),
  normalized_name: varchar('normalized_name', { length: 255 }).notNull(),
  strain_type: varchar('strain_type', { length: 40 }),
  aliases: jsonb('aliases').default([]),
  terpenes: jsonb('terpenes').default([]),
  source_payload: jsonb('source_payload').default({}),
  updated_at: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('strain_reference_provider_id_unq').on(t.provider, t.provider_strain_id),
  index('idx_strain_reference_normalized').on(t.normalized_name),
]);

export const productStrainMap = pgTable('product_strain_map', {
  product_id: uuid('product_id').notNull().references(() => products.id, { onDelete: 'cascade' }),
  strain_reference_id: uuid('strain_reference_id').notNull().references(() => strainReference.id, { onDelete: 'cascade' }),
  confidence: decimal('confidence', { precision: 5, scale: 4 }).notNull(),
  method: varchar('method', { length: 40 }).notNull(), // exact|fuzzy|manual
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  primaryKey({ columns: [t.product_id, t.strain_reference_id], name: 'product_strain_map_pk' }),
  index('idx_product_strain_map_confidence').on(t.confidence),
]);

// -----------------------------
// SCORES SNAPSHOT TABLE
// -----------------------------
export const operatorIntelligenceScoresDaily = pgTable('operator_intelligence_scores_daily', {
  id: uuid('id').primaryKey().defaultRandom(),
  operator_id: uuid('operator_id').notNull().references(() => operators.id, { onDelete: 'cascade' }),
  as_of_date: date('as_of_date').notNull(),
  operator_health_score: decimal('operator_health_score', { precision: 5, scale: 2 }),
  thc_integrity_index: decimal('thc_integrity_index', { precision: 5, scale: 2 }),
  market_saturation_score: decimal('market_saturation_score', { precision: 5, scale: 2 }),
  price_position_score: decimal('price_position_score', { precision: 5, scale: 2 }),
  growth_trajectory_score: decimal('growth_trajectory_score', { precision: 5, scale: 2 }),
  score_payload: jsonb('score_payload').notNull(),
  model_version: varchar('model_version', { length: 40 }).notNull().default('v1.0'),
  created_at: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => [
  unique('operator_intelligence_scores_daily_operator_date_unq').on(t.operator_id, t.as_of_date),
  index('idx_operator_intelligence_scores_daily_date').on(t.as_of_date),
  index('idx_operator_intelligence_scores_daily_health').on(t.operator_health_score),
]);
```

### 2.1 Postgres partitioning strategy (lab tests)

Drizzle currently lacks first-class declarative partition DDL; use SQL migration:

```sql
-- 001_create_lab_test_results_partitioned.sql
CREATE TABLE IF NOT EXISTS lab_test_results (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  metrc_tag_id varchar(120) NOT NULL,
  product_category_type varchar(120),
  strain_name varchar(255),
  test_type_name varchar(120) NOT NULL,
  test_result_pct numeric(8,4) NOT NULL,
  testing_lab_name varchar(255),
  test_performed_date date NOT NULL,
  test_comment text,
  source_row_hash varchar(64) NOT NULL,
  ingest_run_id uuid,
  raw_payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id, test_performed_date),
  UNIQUE (source_row_hash)
) PARTITION BY RANGE (test_performed_date);

CREATE TABLE IF NOT EXISTS lab_test_results_2021_04 PARTITION OF lab_test_results
  FOR VALUES FROM ('2021-04-01') TO ('2021-05-01');

-- repeat monthly partitions through current + 6 months future

CREATE INDEX IF NOT EXISTS idx_lab_test_results_parent_metrc ON ONLY lab_test_results (metrc_tag_id);
CREATE INDEX IF NOT EXISTS idx_lab_test_results_parent_type_date ON ONLY lab_test_results (test_type_name, test_performed_date);
```

**Rationale:** monthly partitioning gives cheap partition pruning on date windows and manageable vacuum/analyze behavior while avoiding over-fragmentation.

---

## 3) B) ETL Pipeline Design

## 3.1 Folder structure

```txt
src/services/api/src/scripts/etl/
  datasets/
    ccc-testing-thc-thca.ts
    ccc-facility-sales.ts
    ccc-itd-sales.ts
    ccc-medical-sales.ts
    ccc-monthly-price-oz.ts
    ccc-commence-ops.ts
    ccc-adult-market-counties.ts
  shared/
    csv.ts
    hash.ts
    normalize.ts
    dedupe.ts
    match-operator.ts
    ingest-run.ts
  run-etl.ts
```

## 3.2 Core ingestion pattern (TypeScript)

```ts
// run-etl.ts
import { db } from '../../db/client';
import { startIngestRun, completeIngestRun, failIngestRun } from './shared/ingest-run';
import { ingestTestingThcThca } from './datasets/ccc-testing-thc-thca';

async function run() {
  const run = await startIngestRun(db, {
    datasetKey: 'ccc.testing_thc_thca',
    sourceFileName: 'testing-thc-thca.csv',
    filePath: '/data/workspace/projects/glass/src/data/ccc-raw/testing-thc-thca.csv',
  });

  try {
    const metrics = await ingestTestingThcThca({ db, ingestRunId: run.id });
    await completeIngestRun(db, run.id, metrics);
  } catch (error: any) {
    await failIngestRun(db, run.id, error);
    throw error;
  }
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
```

## 3.3 Data cleaning rules (dataset-specific)

### 1) `testing-thc-thca.csv`
- Trim all strings; convert blank strings to null.
- Standardize `Test Type Name` to uppercase enum: `THC`, `THCA`.
- Parse `TestResult` with regex `[-+]?[0-9]*\.?[0-9]+`; reject if outside `[0, 100]`.
- Parse `TestPerformedDate` to ISO date; reject invalid/future > now +1 day.
- Normalize METRC tags (`ID`) by stripping whitespace and zero-width chars.
- Deduplicate on `sha256(metrc_tag_id|test_type_name|test_result_pct|test_performed_date|testing_lab_name)`.

### 2) `facility-sales-stats.csv`
- Parse money with commas and `$` stripping.
- Force decimal scale to 2 for dollar values.
- Validate `TOTAL_$ >= 0` and `Quantity/Units >= 0`.
- Coalesce inconsistent category labels via lookup map (`Pre-Rolls` vs `Pre Rolls`).

### 3) `itd-retail-delivery-sales.csv`
- Canonicalize channel labels:
  - `Delivery Operators`, `Delivery Operator` → `delivery_operator`
  - `Couriers` → `courier`
  - `Retail` → `retail`
- Same money/date constraints.

### 4) `medical-facility-stats.csv`
- Treat missing quantity as null (not zero).
- Validate non-negative dollars.

### 5) `avg-monthly-price-oz.csv`
- Parse month to first day (`YYYY-MM-01`).
- Convert ounce to gram benchmark `oz/28.3495` and store both.

### 6) `commence-ops.csv`
- Normalize names and address components.
- Validate email and phone format; invalid kept in raw_payload but null in canonical columns.
- EIN/TIN masked for non-admin responses (`***-**1234` style at API layer).

### 7) `adult-market-data-counties.csv`
- Normalize county names (e.g., “Middlesex County” → `Middlesex`).
- Enforce controlled metric naming dictionary.

## 3.4 Operator matching strategy (fuzzy + deterministic)

### Matching waterfall (strict → loose)
1. **Exact license number match** (if present) → auto-match confidence 1.0.
2. **Exact normalized business name + city** → auto-match confidence 0.98.
3. **Exact normalized business name only** → candidate confidence 0.93.
4. **Trigram similarity** (`pg_trgm`) on normalized names with city boost:
   - base threshold `>= 0.82`
   - +0.05 if city match
   - +0.03 if phone suffix match.
5. Anything below threshold goes to `operator_match_candidates` for review.

### SQL prerequisites

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_operators_name_trgm ON operators USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_operator_aliases_norm_trgm ON operator_aliases USING gin (alias_normalized gin_trgm_ops);
```

### Matching function pseudo-code

```ts
export async function resolveOperator(source: {
  sourceSystem: string;
  sourceRecordKey: string;
  name: string;
  city?: string | null;
  licenseNumber?: string | null;
  phone?: string | null;
}) {
  // 1) license
  // 2) exact normalized name + city
  // 3) trigram candidate list top N=5
  // 4) write operator_match_candidates with rationale
  // 5) return matched_operator_id | null
}
```

## 3.5 Deduplication logic

- Every row gets immutable `source_row_hash` from canonicalized field order.
- Unique index on each fact table `source_row_hash`.
- Use upsert:
  - **append-only datasets:** `ON CONFLICT DO NOTHING`
  - **restated snapshots (commence/adult counties):** close old record (`valid_to=now, is_current=false`) and insert new current version if hash changed.
- If same business/license appears with changed contact fields, store new SCD2 version in `ccc_operator_registry`.

## 3.6 Incremental update strategy

- Maintain `dataset_ingest_runs` with `file_sha256`.
- Skip run if hash already successful.
- If new hash:
  1. Load to staging temp table.
  2. Run validation and reject logging.
  3. Merge into canonical.
  4. Refresh dependent materialized views.
- Cadence:
  - CCC CSV pulls: daily at 05:00 UTC.
  - Google reviews: daily at 07:00 UTC.
  - Census: monthly or yearly as source updates.
  - Enforcement scraper: every 6h.

---

## 4) C) Composite Scores & Intelligence Specs

All scores normalized to **0–100**, persisted daily in `operator_intelligence_scores_daily`.

## 4.1 Operator Health Score (0–100)

```text
OperatorHealth =
  0.25 * PricingCompetitiveness
+ 0.25 * SalesMomentum
+ 0.20 * ReviewReputation
+ 0.15 * ComplianceScore
+ 0.15 * ProductQualityScore
```

### Components
- **PricingCompetitiveness (0-100):** inverse percentile of operator flower $/gram against county peers (winsorized 5–95).
- **SalesMomentum (0-100):** z-score of 8-week slope from `facility_sales_daily` + ITD split trend.
- **ReviewReputation (0-100):** scaled rating and review velocity `(rating*20) * log10(1+reviews_delta_30d)` capped 100.
- **ComplianceScore (0-100):** starts 100; subtract weighted penalties from `ccc_enforcement_actions` (time-decayed half-life 180 days).
- **ProductQualityScore (0-100):** median THC integrity + lab consistency (stddev inverse) from lab-linked products.

## 4.2 THC Integrity Index

```text
THCIntegrity = 100 - min(100, abs(AdvertisedTHC - LabTHC) * 4)
```

- `AdvertisedTHC`: product menu THC average from `products`/latest `prices.raw_data` where available.
- `LabTHC`: `lab_test_batches.total_potential_thc_pct` linked via METRC or strain-category proxy.
- Require minimum sample size N>=20 else flagged low confidence.

## 4.3 Market Saturation Score

```text
OpsPer100k = (active_ops_in_geo / population_total) * 100000
Relative = OpsPer100k / statewide_ops_per_100k
MarketSaturationScore = clamp(100 - (Relative - 1) * 50, 0, 100)
```

Lower score means crowded market.

## 4.4 Price Position Score

```text
PricePositionPct = percentile_rank(operator_avg_price_per_gram within county/category)
PricePositionScore = 100 - PricePositionPct
```

- 0 = most expensive, 100 = most affordable relative to local market.

## 4.5 Growth Trajectory Score

```text
GrowthTrajectory =
  0.50 * normalized_sales_slope_12w
+ 0.30 * normalized_market_growth_county_12w
+ 0.20 * normalized_new_applications_inverse
```

- New applications inverse means high nearby pending apps reduce score.

---

## 5) SQL Materialized Views (Gold layer)

```sql
-- mv_operator_price_position
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_operator_price_position AS
WITH latest_prices AS (
  SELECT
    p.operator_id,
    date_trunc('week', p.scraped_at)::date AS week_start,
    avg(p.price_per_gram) FILTER (WHERE p.price_per_gram IS NOT NULL) AS avg_price_per_gram
  FROM prices p
  WHERE p.scraped_at >= now() - interval '90 days'
  GROUP BY 1,2
),
operator_geo AS (
  SELECT o.id AS operator_id, coalesce(o.city, 'UNKNOWN') AS city
  FROM operators o
)
SELECT
  lp.operator_id,
  og.city,
  lp.week_start,
  lp.avg_price_per_gram,
  percent_rank() OVER (
    PARTITION BY og.city, lp.week_start
    ORDER BY lp.avg_price_per_gram
  ) AS price_percentile
FROM latest_prices lp
JOIN operator_geo og ON og.operator_id = lp.operator_id;

CREATE INDEX IF NOT EXISTS idx_mv_operator_price_position_operator_week
  ON mv_operator_price_position (operator_id, week_start);

-- mv_operator_growth_trajectory
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_operator_growth_trajectory AS
WITH weekly_sales AS (
  SELECT
    sale_date,
    sum(total_dollars) AS dollars
  FROM facility_sales_daily
  WHERE sale_date >= current_date - interval '180 days'
  GROUP BY 1
),
rolling AS (
  SELECT
    sale_date,
    dollars,
    avg(dollars) OVER (ORDER BY sale_date ROWS BETWEEN 83 PRECEDING AND CURRENT ROW) AS ma_12w
  FROM weekly_sales
)
SELECT * FROM rolling;

-- mv_operator_health_components (join stubs; enrich once full linking done)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_operator_health_components AS
SELECT
  o.id AS operator_id,
  current_date AS as_of_date,
  coalesce(100 - (mopp.price_percentile * 100), 50) AS pricing_competitiveness,
  50::numeric AS sales_momentum,
  coalesce((ogrd.rating * 20), 50) AS review_reputation,
  90::numeric AS compliance_score,
  60::numeric AS product_quality_score
FROM operators o
LEFT JOIN LATERAL (
  SELECT price_percentile
  FROM mv_operator_price_position m
  WHERE m.operator_id = o.id
  ORDER BY week_start DESC
  LIMIT 1
) mopp ON true
LEFT JOIN LATERAL (
  SELECT rating
  FROM operator_google_reviews_daily g
  WHERE g.operator_id = o.id
  ORDER BY as_of_date DESC
  LIMIT 1
) ogrd ON true;
```

### Refresh strategy

```sql
-- run after ETL batches
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_operator_price_position;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_operator_growth_trajectory;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_operator_health_components;
```

---

## 6) D) API Design (Fastify routes + auth + optimization)

## 6.1 Endpoints

### Public (rate-limited, no auth)
1. `GET /api/v1/market/benchmarks/monthly-price`
   - Query: `from`, `to`
   - Response: monthly state price benchmark series.
2. `GET /api/v1/market/saturation`
   - Query: `county`
   - Response: operators per capita vs state.

### Authenticated (Clerk JWT)
3. `GET /api/v1/operators/:operatorId/intelligence/scorecard`
4. `GET /api/v1/operators/:operatorId/intelligence/thc-integrity`
5. `GET /api/v1/operators/:operatorId/intelligence/price-position`
6. `GET /api/v1/intelligence/rankings?metric=operator_health_score&limit=50`
7. `GET /api/v1/intelligence/opportunities?county=Middlesex`

### Admin-only (`ADMIN_API_KEY` + role owner/admin)
8. `POST /api/v1/admin/etl/run?dataset=ccc.testing_thc_thca`
9. `GET /api/v1/admin/etl/runs?dataset=...`
10. `GET /api/v1/admin/operator-matching/candidates?status=pending`
11. `POST /api/v1/admin/operator-matching/:id/resolve`
12. `POST /api/v1/admin/materialized-views/refresh`

## 6.2 Example response schemas

### `GET /api/v1/operators/:id/intelligence/scorecard`

```json
{
  "operatorId": "4b3b6eec-65ec-4e1d-91d7-0da15c1a6233",
  "asOfDate": "2026-02-12",
  "scores": {
    "operatorHealthScore": 78.4,
    "thcIntegrityIndex": 72.1,
    "marketSaturationScore": 41.6,
    "pricePositionScore": 84.2,
    "growthTrajectoryScore": 68.7
  },
  "components": {
    "pricingCompetitiveness": 86.9,
    "salesMomentum": 66.2,
    "reviewReputation": 82.3,
    "complianceScore": 91.0,
    "productQualityScore": 67.5
  },
  "confidence": {
    "overall": 0.84,
    "thcIntegrity": 0.71,
    "reviews": 0.93
  },
  "updatedAt": "2026-02-12T07:15:43.000Z"
}
```

### `GET /api/v1/admin/etl/runs`

```json
{
  "runs": [
    {
      "id": "f30e9fd6-b8f6-422d-90d1-c082b4037af0",
      "datasetKey": "ccc.testing_thc_thca",
      "sourceFileName": "testing-thc-thca.csv",
      "status": "success",
      "rowCountRaw": 298343,
      "rowCountLoaded": 297980,
      "rowCountRejected": 363,
      "startedAt": "2026-02-12T05:00:00Z",
      "completedAt": "2026-02-12T05:07:12Z"
    }
  ]
}
```

## 6.3 Query optimization

- Use materialized views for rank/order heavy queries.
- Composite indexes on `(operator_id, as_of_date)` and `(county, report_date)`.
- For scorecard endpoint, single indexed lookup in `operator_intelligence_scores_daily` + `score_payload` JSON.
- Redis cache keys:
  - `intel:scorecard:{operatorId}:{date}` TTL 10m
  - `intel:rankings:{metric}:{date}` TTL 5m
  - `market:saturation:{county}:{date}` TTL 1h

## 6.4 Rate limiting tiers

- **Public:** 60 req/min/IP burst, 10 req/sec hard cap.
- **Authenticated:** 300 req/min/user.
- **Admin:** 30 req/min/user + strict audit logging.
- **ETL trigger endpoints:** 5 req/hour globally.

---

## 7) E) Product Integration Map (dataset × product)

Legend: **P0** immediate, **P1** near-term, **P2** later.

## 7.1 GLASS Dashboard

| Dataset | Flow | Features Enabled | Priority |
|---|---|---|---|
|Lab Testing|`lab_test_batches` → scorecard|THC Integrity cards, quality volatility|P0|
|Facility Sales|`facility_sales_daily`|category demand trends, momentum|P0|
|ITD Sales|`itd_sales_daily`|delivery vs retail channel shifts|P1|
|Medical Stats|`medical_sales_daily`|med market opportunities|P1|
|Monthly Price/Oz|`state_monthly_price_benchmark`|state benchmark overlays|P0|
|Commence Ops|`ccc_operator_registry`|operator profile enrichment|P0|
|Adult Counties|`county_market_daily`|county heatmaps/saturation|P0|
|Google Reviews|`operator_google_reviews_daily`|reputation trend + rank|P1|
|Census|`geo_census_profile`|per-capita saturation and TAM|P1|
|Enforcement|`ccc_enforcement_actions`|compliance risk alerts|P1|
|Strain DB|`strain_reference`|strain-level price/quality analytics|P2|

## 7.2 Virtual Budtender

| Dataset | Flow | Features Enabled | Priority |
|---|---|---|---|
|Lab Testing|strain potency trust profile|confidence-weighted recommendations|P1|
|Facility/ITD Sales|demand trend priors|"what’s moving now" suggestions|P1|
|Monthly Price/Oz|price fairness context|value messaging|P2|
|Google Reviews|store service quality priors|location recommendation bias|P1|
|Strain DB|effects/terpene enrichment|better intent matching|P0|

## 7.3 Cue

| Dataset | Flow | Features Enabled | Priority |
|---|---|---|---|
|Facility Sales|category volume dynamics|dynamic pricing trigger logic|P0|
|ITD Sales|channel incentive targeting|driver/budtender promos by channel|P1|
|Monthly Price/Oz|benchmark anchor|min/max guardrails|P0|
|Google Reviews|service-score tie-ins|incentives tied to CX signals|P1|
|Enforcement|risk guardrails|block risky promo plays|P1|

## 7.4 Delivered (future)

| Dataset | Flow | Features Enabled | Priority |
|---|---|---|---|
|ITD Sales|delivery/courier trends|delivery territory selection|P0|
|Adult Counties + Census|county TAM + competition|expansion market scoring|P0|
|Facility Sales|category mix by locale|inventory planning by route|P1|
|Google Reviews|competitor weakness detection|acquisition messaging|P1|

## 7.5 Newsletter (Operator’s Margin Report)

| Dataset | Flow | Features Enabled | Priority |
|---|---|---|---|
|Monthly Price/Oz|monthly benchmark change|headline KPI panels|P0|
|Facility Sales|weekly category movers|"what changed this week"|P0|
|Adult Counties + Census|county spotlight|localized operator intel|P1|
|Enforcement|compliance watch section|risk intelligence block|P1|
|Google Reviews|sentiment watchlist|brand momentum commentary|P1|
|Lab Testing|quality spotlight|potency inflation stories|P2|

## 7.6 SIGNAL

| Dataset | Flow | Features Enabled | Priority |
|---|---|---|---|
|Commence Ops + Adult Counties|directory enrichment|operator local SEO pages|P0|
|Google Reviews|review snippets + reputation SEO|location page authority|P0|
|Census + Sales|market landing pages|data-backed content generation|P1|
|Enforcement|trust/compliance content hooks|thought leadership automation|P2|

---

## 8) F) Implementation Schedule

## Phase 1 (Days 1–3) — Quick wins

1. Create core tables + ingest audit tables.
2. Ingest datasets 2,5,6,7 first (smallest/highest immediate value).
3. Build operator matching v1 (license + exact name/city + manual queue).
4. Ship APIs:
   - monthly benchmark
   - county saturation
   - operator registry enrichment
5. Materialized view v1: `mv_operator_price_position`.

**Deliverable:** benchmark charts + county map + enriched operator cards live.

## Phase 2 (Week 1–2) — Core intelligence

1. Ingest lab testing dataset with partitioning.
2. Build `lab_test_batches` compaction pipeline.
3. Integrate Google Reviews API daily sync.
4. Build `operator_intelligence_scores_daily` compute job (v1 formulas).
5. Ship scorecard endpoint + UI module.

**Deliverable:** Operator Health Score + THC Integrity visible in GLASS.

## Phase 3 (Month 1) — Cross-reference engine

1. Add Census profiles and county per-capita metrics.
2. Add enforcement scraper/parser with action normalization.
3. Build full cross-source entity graph:
   - operator ↔ license ↔ county ↔ reviews ↔ enforcement.
4. Add ranking and opportunity endpoints.
5. Add admin review queue UI for operator matching.

**Deliverable:** full market intelligence graph + actionable rankings.

## Phase 4 (Month 2+) — Automation + ML

1. Automate all pulls via scheduler with retry and alerting.
2. Introduce probabilistic matching model (XGBoost/lightGBM feature scoring).
3. Add predictive components:
   - demand forecast by category/county
   - risk forecast from enforcement + sentiment drift
4. Feed insights into Cue and Budtender APIs.

**Deliverable:** autonomous daily intelligence pipeline and predictive recommendations.

---

## 9) G) Risk Assessment

## 9.1 Data quality by CSV

- **testing-thc-thca:** duplicate METRC tags, non-numeric test values, inconsistent test type labels.
- **facility-sales:** mixed formatting for currency and unit fields; occasional negative corrections.
- **itd sales:** category/channel taxonomy drift.
- **medical stats:** sparse quantity fields.
- **monthly price/oz:** low volume dataset, but highly reliable.
- **commence ops:** stale contact info, inconsistent business naming, potential duplicate licenses.
- **adult counties:** county naming inconsistencies and mixed metric semantics.

Mitigation: strict validation + reject-row log + change reports per run.

## 9.2 Privacy / legal

- Business emails/phones and EIN/TIN are sensitive; expose only to admin roles.
- Enforce column-level response filtering at API serializer layer.
- Keep raw payload snapshots internal; redact in logs.
- Enforcement data must include source URL and extraction timestamp for defensibility.

## 9.3 Storage / performance

- Lab tests grow steadily; monthly partitioning + indexes + monthly `ANALYZE`.
- Materialized views can lock if non-concurrent; always use `CONCURRENTLY` with supporting unique index where needed.
- Track DB bloat with weekly maintenance (`VACUUM (ANALYZE)` on hot tables).

## 9.4 External API rate limits

- **Google Places:** likely quota-based. Use incremental daily sync + backoff + caching by place_id. Persist last success timestamp per operator.
- **Census API:** free but can throttle bursts. Batch county requests and cache by year.
- **CCC website/doc scraping:** respect robots, request spacing, user-agent identification, and scrape-change monitors.

---

## 10) Operational Runbook (Production)

1. ETL orchestrator runs via cron.
2. Each dataset writes `dataset_ingest_runs` record.
3. Reject rows capped to 10k per run; overflow summarized in metrics.
4. On success: refresh impacted materialized views.
5. Recompute daily scores.
6. Trigger alert if:
   - reject rate > 2%
   - row volume drift > ±30% week-over-week
   - score compute misses SLA (15 min post-ingest)

---

## 11) Final Build Checklist

- [ ] Add new Drizzle schema file and exports
- [ ] Generate migrations incl. partition SQL for `lab_test_results`
- [ ] Build ETL scripts and shared validation utilities
- [ ] Add pg_trgm extension migration
- [ ] Add materialized views and refresh job
- [ ] Add admin ETL and matching endpoints
- [ ] Add intelligence score compute job
- [ ] Add Redis caching layer for high-read intelligence endpoints
- [ ] Add role-based response redaction for sensitive fields
- [ ] Add monitoring dashboard (ingest success/reject rates/latency)

---

## 12) Expected Outcomes

Within 2 weeks, GLASS will have:
- deterministic ingestion for all current CCC datasets,
- operator-level intelligence scores updated daily,
- quality/compliance/reputation integrated signals,
- and APIs that directly power GLASS, Cue, Budtender, Newsletter, and SIGNAL without schema rework.

This design is production-safe, incremental, and extensible to additional states once Massachusetts pipelines stabilize.
