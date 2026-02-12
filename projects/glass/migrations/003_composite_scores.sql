-- Migration: 003_composite_scores.sql
-- Created: 2026-02-12
-- Description: Materialized views for operator health scores and THC integrity

-- ============================================================
-- PREREQUISITES: Add new tables that don't exist in 002
-- These are idempotent (IF NOT EXISTS)
-- ============================================================

-- CCC Monthly Prices
CREATE TABLE IF NOT EXISTS ccc_monthly_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_month TIMESTAMPTZ NOT NULL,
    category VARCHAR(50) NOT NULL,
    license_type VARCHAR(30) NOT NULL,
    avg_price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(10) NOT NULL,
    sample_size INTEGER,
    source VARCHAR(100),
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(report_month, category, license_type)
);

CREATE INDEX IF NOT EXISTS idx_monthly_prices_month ON ccc_monthly_prices(report_month);
CREATE INDEX IF NOT EXISTS idx_monthly_prices_category ON ccc_monthly_prices(category);

-- CCC Licenses
CREATE TABLE IF NOT EXISTS ccc_licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_number VARCHAR(50) NOT NULL UNIQUE,
    license_type VARCHAR(50) NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    dba_name VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    county VARCHAR(100),
    state VARCHAR(2) NOT NULL DEFAULT 'MA',
    zip VARCHAR(10),
    commence_date TIMESTAMPTZ,
    final_license_date TIMESTAMPTZ,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
    match_method VARCHAR(30),
    match_confidence DECIMAL(3,2),
    source_file VARCHAR(100),
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ccc_licenses_type ON ccc_licenses(license_type);
CREATE INDEX IF NOT EXISTS idx_ccc_licenses_city ON ccc_licenses(city);
CREATE INDEX IF NOT EXISTS idx_ccc_licenses_county ON ccc_licenses(county);
CREATE INDEX IF NOT EXISTS idx_ccc_licenses_operator ON ccc_licenses(operator_id);
CREATE INDEX IF NOT EXISTS idx_ccc_licenses_status ON ccc_licenses(status);
CREATE INDEX IF NOT EXISTS idx_ccc_licenses_business_name ON ccc_licenses(business_name);

-- Operator Scores
CREATE TABLE IF NOT EXISTS operator_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operator_id UUID NOT NULL UNIQUE REFERENCES operators(id) ON DELETE CASCADE,
    overall_score DECIMAL(5,2) NOT NULL,
    pricing_score DECIMAL(5,2) NOT NULL,
    compliance_score DECIMAL(5,2) NOT NULL,
    thc_integrity_score DECIMAL(5,2) NOT NULL,
    assortment_score DECIMAL(5,2) NOT NULL,
    market_position_score DECIMAL(5,2) NOT NULL,
    pricing_detail JSONB DEFAULT '{}',
    compliance_detail JSONB DEFAULT '{}',
    thc_integrity_detail JSONB DEFAULT '{}',
    assortment_detail JSONB DEFAULT '{}',
    market_position_detail JSONB DEFAULT '{}',
    grade VARCHAR(2) NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_operator_scores_overall ON operator_scores(overall_score);
CREATE INDEX IF NOT EXISTS idx_operator_scores_grade ON operator_scores(grade);
CREATE INDEX IF NOT EXISTS idx_operator_scores_calculated ON operator_scores(calculated_at);

-- ETL Runs
CREATE TABLE IF NOT EXISTS etl_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset VARCHAR(50) NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    source_hash VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    rows_read INTEGER NOT NULL DEFAULT 0,
    rows_inserted INTEGER NOT NULL DEFAULT 0,
    rows_updated INTEGER NOT NULL DEFAULT 0,
    rows_skipped INTEGER NOT NULL DEFAULT 0,
    rows_errored INTEGER NOT NULL DEFAULT 0,
    error_log JSONB DEFAULT '[]',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    UNIQUE(dataset, source_hash)
);

CREATE INDEX IF NOT EXISTS idx_etl_runs_dataset ON etl_runs(dataset);
CREATE INDEX IF NOT EXISTS idx_etl_runs_status ON etl_runs(status);
CREATE INDEX IF NOT EXISTS idx_etl_runs_started ON etl_runs(started_at);


-- ============================================================
-- MATERIALIZED VIEW: mv_operator_health
-- Precomputed composite health scores for each operator
-- Weights: pricing 25%, compliance 20%, thc_integrity 20%, assortment 20%, market_position 15%
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_operator_health AS
WITH pricing_scores AS (
    -- Score based on how close operator's prices are to market average
    SELECT
        pr.operator_id,
        GREATEST(0, LEAST(100,
            100 - AVG(
                CASE
                    WHEN ccc.avg_price > 0 THEN ABS(
                        ((CASE
                            WHEN p.category = 'flower' THEN pr.price::numeric / 3.5
                            ELSE pr.price::numeric
                        END) - ccc.avg_price::numeric) / ccc.avg_price::numeric
                    ) * 100
                    ELSE 0
                END
            )
        ))::numeric(5,2) AS score,
        jsonb_build_object(
            'observation_count', COUNT(*)::int,
            'avg_deviation_pct', ROUND(AVG(
                CASE
                    WHEN ccc.avg_price > 0 THEN ABS(
                        ((CASE WHEN p.category = 'flower' THEN pr.price::numeric / 3.5 ELSE pr.price::numeric END) - ccc.avg_price::numeric)
                        / ccc.avg_price::numeric
                    ) * 100
                    ELSE 0
                END
            ), 2)
        ) AS detail
    FROM prices pr
    JOIN products p ON p.id = pr.product_id
    LEFT JOIN LATERAL (
        SELECT avg_price
        FROM ccc_avg_prices cap
        WHERE LOWER(cap.category) LIKE '%' || LOWER(p.category) || '%'
          AND cap.report_date >= CURRENT_DATE - INTERVAL '180 days'
        ORDER BY cap.report_date DESC
        LIMIT 1
    ) ccc ON TRUE
    WHERE pr.scraped_at >= NOW() - INTERVAL '30 days'
      AND pr.price > 0
      AND pr.price < 500
      AND p.category IS NOT NULL
    GROUP BY pr.operator_id
),
compliance_scores AS (
    -- Score based on license status and CCC standing
    SELECT
        o.id AS operator_id,
        CASE
            WHEN cl.status = 'active' AND cl.commence_date IS NOT NULL THEN 100.0
            WHEN cl.status = 'active' THEN 85.0
            WHEN cl.status IS NULL THEN 50.0   -- no CCC license linked
            ELSE 30.0                           -- suspended/revoked
        END::numeric(5,2) AS score,
        jsonb_build_object(
            'license_number', cl.license_number,
            'license_status', COALESCE(cl.status, 'unknown'),
            'commence_date', cl.commence_date::text,
            'match_method', cl.match_method
        ) AS detail
    FROM operators o
    LEFT JOIN ccc_licenses cl ON cl.operator_id = o.id
    WHERE o.status != 'inactive'
),
thc_integrity_scores AS (
    -- Score based on how closely menu THC% matches lab-tested THC%
    SELECT
        pr.operator_id,
        GREATEST(0, LEAST(100,
            100 - AVG(
                CASE
                    WHEN lt.total_thc_percent > 0 AND p.thc_percent IS NOT NULL
                    THEN ABS(p.thc_percent::numeric - lt.total_thc_percent::numeric)
                    ELSE 0
                END
            ) * 5  -- 1% deviation = 5 point penalty
        ))::numeric(5,2) AS score,
        jsonb_build_object(
            'products_matched', COUNT(CASE WHEN lt.total_thc_percent IS NOT NULL THEN 1 END)::int,
            'avg_thc_deviation', ROUND(AVG(
                CASE
                    WHEN lt.total_thc_percent > 0 AND p.thc_percent IS NOT NULL
                    THEN ABS(p.thc_percent::numeric - lt.total_thc_percent::numeric)
                    ELSE NULL
                END
            ), 2),
            'products_without_lab', COUNT(CASE WHEN lt.total_thc_percent IS NULL THEN 1 END)::int
        ) AS detail
    FROM prices pr
    JOIN products p ON p.id = pr.product_id
    LEFT JOIN ccc_lab_tests lt ON lt.operator_id = pr.operator_id
        AND LOWER(lt.product_category) LIKE '%' || LOWER(p.category) || '%'
    WHERE pr.scraped_at >= NOW() - INTERVAL '30 days'
      AND p.category IS NOT NULL
    GROUP BY pr.operator_id
),
assortment_scores AS (
    -- Score based on category breadth and product count vs market
    SELECT
        pr.operator_id,
        LEAST(100, (
            -- Category diversity (up to 50 points for 5+ categories)
            LEAST(50, COUNT(DISTINCT p.category) * 10) +
            -- Product count relative to market median (up to 50 points)
            LEAST(50, (COUNT(DISTINCT p.id)::float / GREATEST(1, market.median_count) * 50)::int)
        ))::numeric(5,2) AS score,
        jsonb_build_object(
            'category_count', COUNT(DISTINCT p.category)::int,
            'product_count', COUNT(DISTINCT p.id)::int,
            'market_median_count', market.median_count::int
        ) AS detail
    FROM prices pr
    JOIN products p ON p.id = pr.product_id
    CROSS JOIN LATERAL (
        SELECT COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY sub.cnt
        ), 1) AS median_count
        FROM (
            SELECT COUNT(DISTINCT pr2.product_id) AS cnt
            FROM prices pr2
            WHERE pr2.scraped_at >= NOW() - INTERVAL '30 days'
            GROUP BY pr2.operator_id
        ) sub
    ) market
    WHERE pr.scraped_at >= NOW() - INTERVAL '30 days'
      AND p.category IS NOT NULL
    GROUP BY pr.operator_id, market.median_count
),
market_position_scores AS (
    -- Percentile rank among operators by combined price competitiveness + breadth
    SELECT
        sub.operator_id,
        (PERCENT_RANK() OVER (ORDER BY sub.composite_score ASC) * 100)::numeric(5,2) AS score,
        jsonb_build_object(
            'composite_raw', ROUND(sub.composite_score, 2),
            'percentile_among', COUNT(*) OVER ()::int
        ) AS detail
    FROM (
        SELECT
            pr.operator_id,
            COUNT(DISTINCT p.id)::float * GREATEST(0, 100 - AVG(
                CASE WHEN p.thc_percent IS NOT NULL THEN ABS(pr.price::numeric - 30) ELSE 0 END
            )) AS composite_score
        FROM prices pr
        JOIN products p ON p.id = pr.product_id
        WHERE pr.scraped_at >= NOW() - INTERVAL '30 days'
          AND pr.price > 0
          AND pr.price < 500
        GROUP BY pr.operator_id
    ) sub
)
SELECT
    o.id AS operator_id,
    -- Weighted composite: pricing 25%, compliance 20%, thc_integrity 20%, assortment 20%, market_position 15%
    ROUND((
        COALESCE(ps.score, 50) * 0.25 +
        COALESCE(cs.score, 50) * 0.20 +
        COALESCE(ts.score, 50) * 0.20 +
        COALESCE(ass.score, 50) * 0.20 +
        COALESCE(ms.score, 50) * 0.15
    ), 2)::numeric(5,2) AS overall_score,
    COALESCE(ps.score, 50)::numeric(5,2) AS pricing_score,
    COALESCE(cs.score, 50)::numeric(5,2) AS compliance_score,
    COALESCE(ts.score, 50)::numeric(5,2) AS thc_integrity_score,
    COALESCE(ass.score, 50)::numeric(5,2) AS assortment_score,
    COALESCE(ms.score, 50)::numeric(5,2) AS market_position_score,
    COALESCE(ps.detail, '{}'::jsonb) AS pricing_detail,
    COALESCE(cs.detail, '{}'::jsonb) AS compliance_detail,
    COALESCE(ts.detail, '{}'::jsonb) AS thc_integrity_detail,
    COALESCE(ass.detail, '{}'::jsonb) AS assortment_detail,
    COALESCE(ms.detail, '{}'::jsonb) AS market_position_detail,
    CASE
        WHEN ROUND((
            COALESCE(ps.score, 50) * 0.25 +
            COALESCE(cs.score, 50) * 0.20 +
            COALESCE(ts.score, 50) * 0.20 +
            COALESCE(ass.score, 50) * 0.20 +
            COALESCE(ms.score, 50) * 0.15
        ), 2) >= 90 THEN 'A'
        WHEN ROUND((
            COALESCE(ps.score, 50) * 0.25 +
            COALESCE(cs.score, 50) * 0.20 +
            COALESCE(ts.score, 50) * 0.20 +
            COALESCE(ass.score, 50) * 0.20 +
            COALESCE(ms.score, 50) * 0.15
        ), 2) >= 80 THEN 'B'
        WHEN ROUND((
            COALESCE(ps.score, 50) * 0.25 +
            COALESCE(cs.score, 50) * 0.20 +
            COALESCE(ts.score, 50) * 0.20 +
            COALESCE(ass.score, 50) * 0.20 +
            COALESCE(ms.score, 50) * 0.15
        ), 2) >= 70 THEN 'C'
        WHEN ROUND((
            COALESCE(ps.score, 50) * 0.25 +
            COALESCE(cs.score, 50) * 0.20 +
            COALESCE(ts.score, 50) * 0.20 +
            COALESCE(ass.score, 50) * 0.20 +
            COALESCE(ms.score, 50) * 0.15
        ), 2) >= 60 THEN 'D'
        ELSE 'F'
    END AS grade,
    NOW() AS calculated_at
FROM operators o
LEFT JOIN pricing_scores ps ON ps.operator_id = o.id
LEFT JOIN compliance_scores cs ON cs.operator_id = o.id
LEFT JOIN thc_integrity_scores ts ON ts.operator_id = o.id
LEFT JOIN assortment_scores ass ON ass.operator_id = o.id
LEFT JOIN market_position_scores ms ON ms.operator_id = o.id
WHERE o.status NOT IN ('inactive')
  AND o.name != 'New Operator';

-- Index on the materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_operator_health_operator ON mv_operator_health(operator_id);
CREATE INDEX IF NOT EXISTS idx_mv_operator_health_overall ON mv_operator_health(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_mv_operator_health_grade ON mv_operator_health(grade);


-- ============================================================
-- MATERIALIZED VIEW: mv_thc_integrity
-- Per-operator THC accuracy: lab-tested vs menu-listed
-- ============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_thc_integrity AS
WITH matched_products AS (
    -- Match products to lab tests by operator + category
    SELECT
        pr.operator_id,
        p.id AS product_id,
        p.name AS product_name,
        p.category,
        p.thc_percent::numeric AS menu_thc,
        lt.total_thc_percent::numeric AS lab_thc,
        lt.metrc_tag,
        lt.test_date,
        ABS(p.thc_percent::numeric - lt.total_thc_percent::numeric) AS deviation,
        CASE
            WHEN ABS(p.thc_percent::numeric - lt.total_thc_percent::numeric) <= 2 THEN 'accurate'
            WHEN ABS(p.thc_percent::numeric - lt.total_thc_percent::numeric) <= 5 THEN 'minor_deviation'
            ELSE 'significant_deviation'
        END AS accuracy_band
    FROM prices pr
    JOIN products p ON p.id = pr.product_id
    JOIN ccc_lab_tests lt ON lt.operator_id = pr.operator_id
    WHERE pr.scraped_at >= NOW() - INTERVAL '30 days'
      AND p.thc_percent IS NOT NULL
      AND lt.total_thc_percent IS NOT NULL
      AND lt.total_thc_percent > 0
      AND p.category IS NOT NULL
      AND LOWER(lt.product_category) LIKE '%' || LOWER(p.category) || '%'
)
SELECT
    mp.operator_id,
    COUNT(*)::int AS total_matched,
    COUNT(CASE WHEN mp.accuracy_band = 'accurate' THEN 1 END)::int AS accurate_count,
    COUNT(CASE WHEN mp.accuracy_band = 'minor_deviation' THEN 1 END)::int AS minor_deviation_count,
    COUNT(CASE WHEN mp.accuracy_band = 'significant_deviation' THEN 1 END)::int AS significant_deviation_count,
    ROUND(AVG(mp.deviation), 2)::numeric(5,2) AS avg_deviation_pct,
    ROUND(MAX(mp.deviation), 2)::numeric(5,2) AS max_deviation_pct,
    ROUND(
        (COUNT(CASE WHEN mp.accuracy_band = 'accurate' THEN 1 END)::numeric /
         GREATEST(1, COUNT(*))) * 100,
    2)::numeric(5,2) AS accuracy_pct,
    -- Detail: top 5 worst deviations
    (
        SELECT jsonb_agg(jsonb_build_object(
            'product_name', sub.product_name,
            'category', sub.category,
            'menu_thc', sub.menu_thc,
            'lab_thc', sub.lab_thc,
            'deviation', ROUND(sub.deviation, 2)
        ) ORDER BY sub.deviation DESC)
        FROM (
            SELECT DISTINCT ON (mp2.product_id) mp2.*
            FROM matched_products mp2
            WHERE mp2.operator_id = mp.operator_id
            ORDER BY mp2.product_id, mp2.deviation DESC
            LIMIT 5
        ) sub
    ) AS worst_deviations,
    NOW() AS calculated_at
FROM matched_products mp
GROUP BY mp.operator_id;

-- Indexes on the THC integrity materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_thc_integrity_operator ON mv_thc_integrity(operator_id);
CREATE INDEX IF NOT EXISTS idx_mv_thc_integrity_accuracy ON mv_thc_integrity(accuracy_pct DESC);


-- ============================================================
-- REFRESH FUNCTION (for cron or manual trigger)
-- ============================================================

CREATE OR REPLACE FUNCTION refresh_health_scores()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_operator_health;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_thc_integrity;

    -- Upsert into operator_scores table for fast Drizzle queries
    INSERT INTO operator_scores (
        operator_id, overall_score, pricing_score, compliance_score,
        thc_integrity_score, assortment_score, market_position_score,
        pricing_detail, compliance_detail, thc_integrity_detail,
        assortment_detail, market_position_detail,
        grade, calculated_at, version
    )
    SELECT
        operator_id, overall_score, pricing_score, compliance_score,
        thc_integrity_score, assortment_score, market_position_score,
        pricing_detail, compliance_detail, thc_integrity_detail,
        assortment_detail, market_position_detail,
        grade, calculated_at, 1
    FROM mv_operator_health
    ON CONFLICT (operator_id) DO UPDATE SET
        overall_score = EXCLUDED.overall_score,
        pricing_score = EXCLUDED.pricing_score,
        compliance_score = EXCLUDED.compliance_score,
        thc_integrity_score = EXCLUDED.thc_integrity_score,
        assortment_score = EXCLUDED.assortment_score,
        market_position_score = EXCLUDED.market_position_score,
        pricing_detail = EXCLUDED.pricing_detail,
        compliance_detail = EXCLUDED.compliance_detail,
        thc_integrity_detail = EXCLUDED.thc_integrity_detail,
        assortment_detail = EXCLUDED.assortment_detail,
        market_position_detail = EXCLUDED.market_position_detail,
        grade = EXCLUDED.grade,
        calculated_at = EXCLUDED.calculated_at,
        version = operator_scores.version + 1;
END;
$$ LANGUAGE plpgsql;
