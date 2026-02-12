-- Migration: 002_ccc_tables.sql
-- Created: 2026-02-12 19:09:20
-- Description: CCC regulatory data tables for MA cannabis market intelligence

-- ============================================================
-- CCC LAB TESTS TABLE
-- Pivoted: one row per METRC tag with THC + THCA
-- Source: testing-thc-thca.csv (298K raw → ~149K pivoted)
-- ============================================================

CREATE TABLE ccc_lab_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metrc_tag VARCHAR(30) NOT NULL UNIQUE,
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
    imported_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- CCC LAB TESTS INDEXES
-- ============================================================

CREATE INDEX idx_lab_tests_category ON ccc_lab_tests(product_category);
CREATE INDEX idx_lab_tests_strain ON ccc_lab_tests(strain_code);
CREATE INDEX idx_lab_tests_date ON ccc_lab_tests(test_date);
CREATE INDEX idx_lab_tests_lab ON ccc_lab_tests(testing_lab);
CREATE INDEX idx_lab_tests_thc ON ccc_lab_tests(total_thc_percent);
CREATE INDEX idx_lab_tests_operator ON ccc_lab_tests(operator_id);
CREATE INDEX idx_lab_tests_category_thc ON ccc_lab_tests(product_category, total_thc_percent);
CREATE INDEX idx_lab_tests_date_category ON ccc_lab_tests(test_date, product_category);


-- ============================================================
-- CCC FACILITY SALES TABLE
-- Unified adult + medical + delivery
-- Sources: facility-sales-stats.csv, itd-retail-delivery-sales.csv, medical-facility-stats.csv
-- ============================================================

CREATE TABLE ccc_facility_sales (
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
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(sale_date, market_type, delivery_type, product_category, unit_of_measure)
);


-- ============================================================
-- CCC FACILITY SALES INDEXES
-- ============================================================

CREATE INDEX idx_facility_sales_date ON ccc_facility_sales(sale_date);
CREATE INDEX idx_facility_sales_market ON ccc_facility_sales(market_type);
CREATE INDEX idx_facility_sales_delivery ON ccc_facility_sales(delivery_type);
CREATE INDEX idx_facility_sales_category ON ccc_facility_sales(product_category);
CREATE INDEX idx_facility_sales_date_market_cat ON ccc_facility_sales(sale_date, market_type, product_category);
CREATE INDEX idx_facility_sales_date_delivery ON ccc_facility_sales(sale_date, delivery_type);


-- ============================================================
-- CCC MONTHLY PRICES TABLE
-- Official state avg price/gram
-- Source: avg-monthly-price-oz.csv (71 rows, Jan 2020 – Nov 2025)
-- ============================================================

CREATE TABLE ccc_monthly_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year_month VARCHAR(7) NOT NULL UNIQUE,
    avg_price_per_gram DECIMAL(6,2) NOT NULL,
    avg_price_per_oz DECIMAL(8,2),
    avg_price_per_eighth DECIMAL(7,2),
    mom_change_pct DECIMAL(6,2),
    yoy_change_pct DECIMAL(6,2),
    imported_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_monthly_prices_month ON ccc_monthly_prices(year_month);


-- ============================================================
-- CCC LICENSES TABLE
-- Merged from commence-ops.csv + adult-market-data-counties.csv
-- One row per license_number. A business may hold multiple licenses.
-- ============================================================

CREATE TABLE ccc_licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_number VARCHAR(30) NOT NULL UNIQUE,
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
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- CCC LICENSES INDEXES
-- ============================================================

CREATE INDEX idx_licenses_business_name ON ccc_licenses(business_name);
CREATE INDEX idx_licenses_type ON ccc_licenses(license_type);
CREATE INDEX idx_licenses_status ON ccc_licenses(license_status);
CREATE INDEX idx_licenses_stage ON ccc_licenses(license_stage);
CREATE INDEX idx_licenses_city ON ccc_licenses(establishment_city);
CREATE INDEX idx_licenses_county ON ccc_licenses(county);
CREATE INDEX idx_licenses_location ON ccc_licenses(latitude, longitude);
CREATE INDEX idx_licenses_operator ON ccc_licenses(operator_id);
CREATE INDEX idx_licenses_ein ON ccc_licenses(ein_tin);
CREATE INDEX idx_licenses_expiration ON ccc_licenses(license_expiration_date);
CREATE INDEX idx_licenses_equity ON ccc_licenses(is_social_equity, is_economic_empowerment);
CREATE INDEX idx_licenses_type_status ON ccc_licenses(license_type, license_status);


-- ============================================================
-- OPERATOR SCORES TABLE
-- Computed intelligence (cached table, not materialized view)
-- ============================================================

CREATE TABLE operator_scores (
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
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    data_freshness JSONB,
    computation_version VARCHAR(20) NOT NULL DEFAULT 'v1',
    UNIQUE(operator_id, computation_version)
);

CREATE INDEX idx_op_scores_operator ON operator_scores(operator_id);
CREATE INDEX idx_op_scores_health ON operator_scores(health_score);
CREATE INDEX idx_op_scores_computed ON operator_scores(computed_at);


-- ============================================================
-- GOOGLE REVIEWS TABLE
-- Individual reviews
-- ============================================================

CREATE TABLE google_reviews (
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
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_google_reviews_operator ON google_reviews(operator_id);
CREATE INDEX idx_google_reviews_place ON google_reviews(place_id);
CREATE INDEX idx_google_reviews_rating ON google_reviews(overall_rating);
CREATE INDEX idx_google_reviews_time ON google_reviews(review_time);


-- ============================================================
-- GOOGLE PLACE STATS TABLE
-- Aggregate per operator (separate access pattern)
-- ============================================================

CREATE TABLE google_place_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operator_id UUID NOT NULL UNIQUE REFERENCES operators(id) ON DELETE CASCADE,
    google_place_id VARCHAR(255),
    current_rating DECIMAL(2,1),
    total_reviews INTEGER,
    price_level INTEGER,
    business_status VARCHAR(50),
    hours_json JSONB,
    popular_times_json JSONB,
    scraped_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_google_place_stats_operator ON google_place_stats(operator_id);
CREATE INDEX idx_google_place_stats_rating ON google_place_stats(current_rating);
