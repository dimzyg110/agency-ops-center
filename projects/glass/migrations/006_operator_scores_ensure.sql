-- Migration: 006_operator_scores_ensure.sql
-- Created: 2026-02-13
-- Description: Ensure operator_scores table exists for dashboard scoring
-- Idempotent: Safe to run multiple times

-- ============================================================
-- OPERATOR SCORES TABLE
-- Stores composite health scores for operator dashboard
-- ============================================================

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

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_operator_scores_overall ON operator_scores(overall_score);
CREATE INDEX IF NOT EXISTS idx_operator_scores_grade ON operator_scores(grade);
CREATE INDEX IF NOT EXISTS idx_operator_scores_calculated ON operator_scores(calculated_at);

-- Comment for documentation
COMMENT ON TABLE operator_scores IS 'Composite health scores for operator dashboard display';
COMMENT ON COLUMN operator_scores.overall_score IS 'Weighted composite score 0-100';
COMMENT ON COLUMN operator_scores.pricing_score IS 'Pricing competitiveness 0-100';
COMMENT ON COLUMN operator_scores.compliance_score IS 'Data quality/compliance 0-100';
COMMENT ON COLUMN operator_scores.assortment_score IS 'Product assortment breadth 0-100';
COMMENT ON COLUMN operator_scores.market_position_score IS 'Market positioning 0-100';
COMMENT ON COLUMN operator_scores.grade IS 'Letter grade A-F with +/-';

-- ============================================================
-- OPTIONAL: Add trigger to auto-update calculated_at on score changes
-- ============================================================

CREATE OR REPLACE FUNCTION update_operator_scores_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.calculated_at = NOW();
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_operator_scores_update ON operator_scores;

CREATE TRIGGER trigger_operator_scores_update
    BEFORE UPDATE ON operator_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_operator_scores_timestamp();

-- ============================================================
-- BACKFILL: Create placeholder scores for existing operators without scores
-- ============================================================

INSERT INTO operator_scores (
    operator_id,
    overall_score,
    pricing_score,
    compliance_score,
    thc_integrity_score,
    assortment_score,
    market_position_score,
    grade,
    calculated_at
)
SELECT 
    o.id,
    50.00, -- neutral starting score
    50.00,
    50.00,
    50.00,
    50.00,
    50.00,
    'C',
    NOW() - INTERVAL '7 days'
FROM operators o
LEFT JOIN operator_scores os ON o.id = os.operator_id
WHERE os.id IS NULL
ON CONFLICT (operator_id) DO NOTHING;

-- ============================================================
-- VERIFICATION QUERY (run manually to check)
-- ============================================================
-- SELECT 
--     COUNT(*) as total_operators,
--     COUNT(os.id) as operators_with_scores,
--     AVG(os.overall_score) as avg_overall_score
-- FROM operators o
-- LEFT JOIN operator_scores os ON o.id = os.operator_id;
