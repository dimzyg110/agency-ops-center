# GLASS Data Intelligence Plan

**Purpose:** Design the proprietary data matching and cross-referencing engine that makes GLASS irreplaceable for MA dispensary operators.

**Assumptions:**
- Current PostgreSQL schema (drizzle ORM) as documented in `src/services/api/src/db/schema.ts`
- ~100K scraped products, ~117K price records, ~1,033 operators
- ~772 CCC licenses, 147K lab tests, 67K facility sales records
- All operators geocoded (lat/lon in `operators` table)

---

## 1. Product Matching Engine

The core unsolved problem: matching identical products across different dispensary menus.

### 1.1 Schema Changes Required

```sql
-- Canonical product: the "master" record representing one physical product
CREATE TABLE canonical_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_name VARCHAR(500) NOT NULL,
    normalized_brand VARCHAR(255),
    category VARCHAR(50),
    strain_type VARCHAR(50),
    weight_grams DECIMAL(10,3),
    typical_thc_range_min DECIMAL(5,2),
    typical_thc_range_max DECIMAL(5,2),
    typical_cbd_range_min DECIMAL(5,2),
    typical_cbd_range_max DECIMAL(5,2),
    match_count INTEGER NOT NULL DEFAULT 0,  -- how many store variants
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_canonical_brand ON canonical_products(normalized_brand);
CREATE INDEX idx_canonical_category ON canonical_products(category);
CREATE INDEX idx_canonical_strain ON canonical_products(strain_type);

-- Link scraped products to their canonical parent
CREATE TABLE product_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_product_id UUID NOT NULL REFERENCES canonical_products(id) ON DELETE CASCADE,
    source_product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    confidence_level VARCHAR(20) NOT NULL,  -- 'high', 'medium', 'low'
    match_score DECIMAL(5,4) NOT NULL,  -- 0.0000 to 1.0000
    match_reason JSONB NOT NULL,  -- { "brand_match": true, "weight_match": true, ... }
    is_reverse_matched BOOLEAN NOT NULL DEFAULT FALSE,  -- TRUE = matched after initial
    matched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(source_product_id)
);

CREATE INDEX idx_matches_canonical ON product_matches(canonical_product_id);
CREATE INDEX idx_matches_source ON product_matches(source_product_id);
CREATE INDEX idx_matches_confidence ON product_matches(confidence_level);

-- Tracking for ongoing matching (incremental updates)
CREATE TABLE matching_job_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(30) NOT NULL,  -- 'full', 'incremental', 'brand_normalize'
    products_processed INTEGER NOT NULL DEFAULT 0,
    new_canonicals_created INTEGER NOT NULL DEFAULT 0,
    new_matches_created INTEGER NOT NULL DEFAULT 0,
    matches_confirmed INTEGER NOT NULL DEFAULT 0,
    matches_rejected INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'running'
);
```

### 1.2 Matching Algorithm

The algorithm uses a **multi-stage hybrid approach** combining rule-based normalization with probabilistic scoring.

#### Stage 1: Brand Normalization (Preprocessing)

```python
def normalize_brand(brand: str, product_name: str) -> str:
    """
    Returns normalized brand name.
    Handles NULL brands, embedded brands, and known aliases.
    """
    if brand is NULL:
        # Try to extract brand from product name
        brand = extract_brand_from_name(product_name)
    
    # Known brand aliases mapping
    ALIASES = {
        "cookies": "Cookies",
        "cookie": "Cookies",
        "little_brown": "Little Brown",
        "lb": "Little Brown",
        "rythm": "Rythm",
        "rythm": "Rythm",
        "good_life": "The Good Life",
        "glf": "The Good Life",
    }
    
    if brand:
        brand = brand.strip().lower()
        return ALIASES.get(brand, brand.title())
    
    return NULL
```

**Data requirement:** Build a `brand_aliases` lookup table via manual curation + ML clustering of existing brand values.

#### Stage 2: Weight Extraction from Product Names

```python
import re

def extract_weight_grams(product_name: str) -> Optional[float]:
    """
    Extract weight in grams from product name.
    Examples:
      "Cookies - Gary Payton 3.5g" -> 3.5
      "1/2 oz Wedding Cake" -> 14.0
      "1oz Purple Punch" -> 28.0
      "5 pack pre-roll" -> None (no weight)
    """
    patterns = [
        r'(\d+\.?\d*)\s*g\b',           # 3.5g, 14g
        r'(\d+)\s*g\b',                 # 3g (no decimal)
        r'1/2\s*oz\b',                  # half ounce
        r'1/4\s*oz\b',                  # quarter ounce
        r'1/8\s*oz\b',                  # eighth
        r'1\s*oz\b',                    # ounce
        r'(\d+)\s*oz\b',                # 2oz, etc.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, product_name.lower())
        if match:
            value = float(match.group(1))
            if '1/2 oz' in product_name.lower():
                return 14.0
            elif '1/4 oz' in product_name.lower():
                return 7.0
            elif '1/8 oz' in product_name.lower():
                return 3.5
            elif 'oz' in pattern:
                return value * 28.0
            return value
    
    return None
```

#### Stage 3: Strain Name Normalization

```python
def normalize_strain(strain_name: str) -> str:
    """
    Normalize strain names handling common variations.
    """
    if not strain_name:
        return NULL
    
    strain = strain_name.strip().lower()
    
    # Known variations
    VARIATIONS = {
        "gary payton": "gary payton",
        "gary payton #1": "gary payton",
        "the gary payton": "gary payton",
        "gp": "gary payton",
        "wedding cake": "wedding cake",
        "wedding cake #1": "wedding cake",
        "wc": "wedding cake",
        "gelato": "gelato",
        "gelato #33": "gelato",
        "gelato 33": "gelato",
    }
    
    return VARIATIONS.get(strain, strain)
```

#### Stage 4: Similarity Scoring

```sql
-- Core similarity function using trigram similarity (PostgreSQL extension)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE FUNCTION product_similarity(
    p1_name TEXT, p1_brand TEXT, p1_category TEXT,
    p2_name TEXT, p2_brand TEXT, p2_category TEXT
) RETURNS DECIMAL(5,4) AS $$
DECLARE
    name_sim DECIMAL(5,4);
    brand_sim DECIMAL(5,4);
    category_sim DECIMAL(5,4);
BEGIN
    -- Name similarity (trigram)
    name_sim := similarity(lower(p1_name), lower(p2_name));
    
    -- Exact brand match or both NULL
    IF p1_brand IS NULL AND p2_brand IS NULL THEN
        brand_sim := 1.0;
    ELSIF p1_brand IS NULL OR p2_brand IS NULL THEN
        brand_sim := 0.0;
    ELSE
        brand_sim := CASE WHEN lower(p1_brand) = lower(p2_brand) THEN 1.0 ELSE 0.0 END;
    END IF;
    
    -- Category match
    category_sim := CASE WHEN p1_category = p2_category THEN 1.0 ELSE 0.0 END;
    
    -- Weighted combination: name is most important
    RETURN (name_sim * 0.6) + (brand_sim * 0.3) + (category_sim * 0.1);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

#### Stage 5: Multi-Pass Matching Pipeline

```python
def match_products_batch(products: List[Product], batch_size: int = 1000):
    """
    Multi-pass matching algorithm:
    1. Exact matches (name + brand + weight within 0.1g)
    2. High-confidence fuzzy (similarity > 0.85, same category, weight within 0.5g)
    3. Medium-confidence fuzzy (similarity > 0.7, same category)
    4. Low-confidence (similarity > 0.6, brand match, strain match)
    5. Manual review queue (similarity 0.5-0.6)
    """
    
    # PASS 1: Exact matches
    exact_matches = find_exact_matches(products)
    mark_as_matched(exact_matches, confidence='high')
    
    # PASS 2: High-confidence fuzzy
    high_conf = find_fuzzy_matches(products, min_score=0.85, weight_tolerance=0.5)
    mark_as_matched(high_conf, confidence='high')
    
    # PASS 3: Medium-confidence fuzzy
    med_conf = find_fuzzy_matches(products, min_score=0.7, exclude_matched=True)
    mark_as_matched(med_conf, confidence='medium')
    
    # PASS 4: Low-confidence with rules
    low_conf = find_rule_based_matches(products, exclude_matched=True)
    mark_as_matched(low_conf, confidence='low')
    
    # PASS 5: Queue for manual review
    review_queue = products.where(similarity.between(0.5, 0.6))
    send_to_review_queue(review_queue)
```

### 1.3 Confidence Scoring Matrix

| Factor | Weight | Criteria |
|--------|--------|----------|
| Name similarity (trigram) | 30% | >0.9 = full, 0.7-0.9 = partial, <0.7 = none |
| Brand exact match | 25% | Exact = full, NULL both = full, mismatch = none |
| Weight match | 20% | Within 0.1g = full, 0.5g = partial, >1g = none |
| Category match | 15% | Same = full, different = none |
| Strain match | 10% | Normalized match = full, NULL = partial |

**Confidence thresholds:**
- **HIGH**: Score ≥ 0.85 AND brand match
- **MEDIUM**: Score ≥ 0.70
- **LOW**: Score ≥ 0.55
- **REVIEW**: Score 0.45-0.55

### 1.4 Migration Plan for Existing Data

```sql
-- Step 1: Enable pg_trgm
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Step 2: Run initial full matching (offline, ~30 min for 100K products)
-- Estimated runtime: 25-40 minutes depending on hardware

-- Step 3: Create materialized view for canonical product aggregates
CREATE MATERIALIZED VIEW canonical_product_stats AS
SELECT 
    cp.id,
    cp.canonical_name,
    cp.normalized_brand,
    cp.category,
    cp.strain_type,
    cp.weight_grams,
    cp.match_count,
    COUNT(DISTINCT p.operator_id) AS store_count,
    MIN(pr.price) AS min_price,
    MAX(pr.price) AS max_price,
    AVG(pr.price) AS avg_price,
    AVG(pr.price_per_gram) AS avg_price_per_gram
FROM canonical_products cp
JOIN product_matches pm ON pm.canonical_product_id = cp.id
JOIN products p ON p.id = pm.source_product_id
JOIN prices pr ON pr.product_id = p.id
WHERE pr.scraped_at > NOW() - INTERVAL '7 days'
GROUP BY cp.id;

CREATE UNIQUE INDEX ON canonical_product_stats(id);
```

### 1.5 Effort & Compute Estimates

| Phase | Effort | Compute | Notes |
|-------|--------|---------|-------|
| Schema setup | 1 day | Minimal | New tables + indexes |
| Brand normalization table | 2 days | Manual curation | Top 200 brands |
| Weight extraction function | 1 day | Dev only | Regex + tests |
| Initial matching job | 2 days | ~4 vCPU, 30 min job | Batch processing |
| Confidence tuning | 3 days | A/B testing | Adjust thresholds |
| Review UI for corrections | 3 days | Frontend dev | Admin interface |
| **Total** | **12 days** | | |

**Batch processing recommendation:** Run initial matching in 10K-product batches via PostgreSQL `pg_cron` or Python background job. Process new products incrementally on each scrape run.

---

## 2. Supply Chain Graph

Build a graph of relationships between cultivators → manufacturers → retailers using CCC license data + lab tests.

### 2.1 What We Can Actually Prove vs Infer

**PROVABLE (from CCC data):**
- License relationships: cultivator license → retailer license (same business name/address)
- Lab test to cultivator: lab tests have `operator_id` (the cultivator who submitted)
- Facility sales: aggregated by market type (adult-use vs medical)

**INFERABLE (from scraped data):**
- Which cultivator's products appear at which retailers (via product matching)
- Brand ownership: if same entity owns multiple licenses (same owner name)

**NOT POSSIBLE with current data:**
- True batch-level traceability (no METRC tag linking to retail products)
- Wholesale pricing (not in scraped data)

### 2.2 Schema for Relationship Graph

```sql
-- Nodes: licensed entities
CREATE TABLE supply_chain_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_type VARCHAR(30) NOT NULL,  -- 'cultivator', 'manufacturer', 'retailer', 'distributor'
    ccc_license_id UUID REFERENCES ccc_licenses(id) ON DELETE SET NULL,
    operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
    business_name VARCHAR(500) NOT NULL,
    license_number VARCHAR(30),
    establishment_city VARCHAR(100),
    establishment_state VARCHAR(2),
    lat DECIMAL(10,8),
    lon DECIMAL(11,8),
    license_type VARCHAR(100),
    license_status VARCHAR(30),
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,  -- TRUE = proven via CCC data
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scn_type ON supply_chain_nodes(node_type);
CREATE INDEX idx_scn_license ON supply_chain_nodes(ccc_license_id);
CREATE INDEX idx_scn_operator ON supply_chain_nodes(operator_id);

-- Edges: proven or inferred relationships
CREATE TABLE supply_chain_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_node_id UUID NOT NULL REFERENCES supply_chain_nodes(id) ON DELETE CASCADE,
    to_node_id UUID NOT NULL REFERENCES supply_chain_nodes(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,  -- 'supplies_to', 'owns', 'manufactures_for'
    evidence_type VARCHAR(30) NOT NULL,  -- 'ccc_license', 'lab_test', 'product_match', 'inferred'
    confidence VARCHAR(20) NOT NULL,  -- 'proven', 'high', 'medium', 'low'
    evidence_data JSONB,  -- { "lab_test_count": 150, "product_overlap": 23 }
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_confirmed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(from_node_id, to_node_id, relationship_type)
);

CREATE INDEX idx_sce_from ON supply_chain_edges(from_node_id);
CREATE INDEX idx_sce_to ON supply_chain_edges(to_node_id);
CREATE INDEX idx_sce_type ON supply_chain_edges(relationship_type);
CREATE INDEX idx_sce_confidence ON supply_chain_edges(confidence);
```

### 2.3 Queries for Actionable Insights

#### Query: Cultivator Quality Rankings

```sql
-- Which cultivators have the best lab results?
SELECT 
    scn.business_name AS cultivator,
    COUNT(clt.id) AS test_count,
    AVG(clt.total_thc_percent) AS avg_thc,
    MAX(clt.total_thc_percent) AS max_thc,
    -- Contaminant pass rate
    SUM(CASE WHEN clt.test_comment LIKE '%fail%' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*) AS fail_rate
FROM supply_chain_nodes scn
JOIN ccc_lab_tests clt ON clt.operator_id = scn.operator_id
WHERE scn.node_type = 'cultivator'
    AND clt.test_date > NOW() - INTERVAL '90 days'
GROUP BY scn.id, scn.business_name
ORDER BY avg_thc DESC
LIMIT 50;
```

#### Query: Supply Chain Tracing (Cultivator → Retailer)

```sql
-- Which retailers carry which cultivators' products?
SELECT 
    retailer.business_name AS retailer,
    cultivator.business_name AS cultivator,
    COUNT(DISTINCT cp.id) AS product_overlap,
    MIN(pr.price) AS min_price,
    AVG(pr.price) AS avg_price
FROM canonical_products cp
JOIN product_matches pm ON pm.canonical_product_id = cp.id
JOIN products p ON p.id = pm.source_product_id
JOIN prices pr ON pr.product_id = p.id
JOIN operators retailer_op ON pr.operator_id = retailer_op.id
JOIN supply_chain_nodes retailer ON retailer.operator_id = retailer_op.id
JOIN supply_chain_nodes cultivator ON cultivator.id = (
    -- Find cultivator via lab tests matching this product's strain
    SELECT scn.id FROM supply_chain_nodes scn
    JOIN ccc_lab_tests clt ON clt.operator_id = scn.operator_id
    WHERE scn.node_type = 'cultivator'
    ORDER BY similarity(cp.strain_type, clt.strain_code) DESC
    LIMIT 1
)
WHERE cp.category IN ('flower', 'preroll')
    AND pr.scraped_at > NOW() - INTERVAL '7 days'
GROUP BY retailer.id, cultivator.id
ORDER BY product_overlap DESC;
```

#### Query: Brand Ownership Detection

```sql
-- Which brands are manufactured by the same entity?
-- (Multiple license holders with similar business names or same owners)
SELECT 
    STRING_AGG(DISTINCT scn.business_name, ' | ') AS entities,
    STRING_AGG(DISTINCT scn.license_type, ', ') AS license_types,
    COUNT(*) AS license_count
FROM supply_chain_nodes scn
WHERE scn.business_name IN (
    SELECT business_name FROM ccc_licenses 
    GROUP BY business_name HAVING COUNT(*) > 1
)
GROUP BY LOWER(business_name);
```

### 2.4 Effort Estimate

| Phase | Effort | Data Dependency |
|-------|--------|------------------|
| Node extraction from CCC | 2 days | ccc_licenses table |
| Edge creation (proven) | 2 days | Lab tests + licenses |
| Edge creation (inferred) | 3 days | Product matching required |
| Graph API endpoints | 2 days | Backend dev |
| **Total** | **9 days** | |

---

## 3. Competitive Intelligence Layer

For each operator, determine their real competitive landscape.

### 3.1 Geocoding Status

**What we have:**
- `operators.lat` and `operators.lon` — geocoded from address
- Already populated from previous geocoding run

**What we need for competitive analysis:**
- Nothing — geocoding complete

### 3.2 Per-Operator Competitive Snapshot Structure

```sql
-- Stored competitive analysis per operator
CREATE TABLE competitive_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Radius analysis
    competitor_count_5mi INTEGER,
    competitor_count_10mi INTEGER,
    competitor_count_25mi INTEGER,
    
    -- Price positioning
    avg_flower_price DECIMAL(10,2),
    flower_price_percentile INTEGER,  -- 1-100, lower = cheaper
    avg_vape_price DECIMAL(10,2),
    avg_edible_price DECIMAL(10,2),
    avg_concentrate_price DECIMAL(10,2),
    
    -- Assortment overlap
    unique_products INTEGER,
    overlap_with_nearest_competitor DECIMAL(5,2),  -- % overlap
    category_mix_flower_pct DECIMAL(5,2),
    category_mix_vape_pct DECIMAL(5,2),
    category_mix_edible_pct DECIMAL(5,2),
    category_mix_concentrate_pct DECIMAL(5,2),
    
    -- Demand gaps (requires demand signals)
    demand_gap_categories JSONB,  -- { "vapes": ["brand_x", "brand_y"] }
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(operator_id, snapshot_date)
);

CREATE INDEX idx_comp_snap_operator ON competitive_snapshots(operator_id);
CREATE INDEX idx_comp_snap_date ON competitive_snapshots(snapshot_date);
```

### 3.3 Radius Analysis Queries

```sql
-- Find nearest N competitors (PostGIS not required, haversine works)
CREATE FUNCTION nearest_competitors(
    op_lat DECIMAL, op_lon DECIMAL, 
    radius_miles INTEGER, limit_count INTEGER
) RETURNS TABLE (
    competitor_id UUID,
    competitor_name VARCHAR,
    competitor_city VARCHAR,
    distance_miles DECIMAL(10,2),
    product_overlap_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.id AS competitor_id,
        o.name AS competitor_name,
        o.city AS competitor_city,
        (6371 * acos(cos(radians(op_lat)) * cos(radians(o.lat::NUMERIC)) * 
         cos(radians(o.lon::NUMERIC) - radians(op_lon)) * 
         cos(radians(op_lat))))::DECIMAL(10,2) AS distance_miles,
        0 AS product_overlap_count  -- TODO: join with canonical_products
    FROM operators o
    WHERE o.id != op_lat  -- exclude self (passed differently)
      AND o.status = 'active'
      AND o.lat IS NOT NULL
      AND o.lon IS NOT NULL
    ORDER BY distance_miles ASC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;
```

### 3.4 API Endpoint Design

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/operators/{id}/competitors` | GET | Nearest N competitors with distance |
| `/api/v1/operators/{id}/competitive-snapshot` | GET | Full snapshot (cached, daily refresh) |
| `/api/v1/operators/{id}/price-position` | GET | Price positioning vs local market |
| `/api/v1/operators/{id}/category-mix` | GET | Category distribution vs competitors |

### 3.5 Effort Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Competitor radius query | 1 day | Geocoding complete |
| Product overlap calculation | 2 days | Product matching (Section 1) |
| Category mix analysis | 1 day | Products table |
| Snapshot cron job | 1 day | Backend scheduler |
| API endpoints | 2 days | Backend dev |
| **Total** | **7 days** | Requires Section 1 complete |

---

## 4. Demand Signal Pipeline

Transform Virtual Budtender queries into actionable demand intelligence.

### 4.1 Current State

The `demand_signals`, `budtender_sessions`, and `budtender_queries` tables exist but are empty. This pipeline designs how to populate them.

### 4.2 Aggregation Strategy

```sql
-- Aggregate query patterns into demand signals
CREATE FUNCTION aggregate_demand_signals(
    p_start DATE, p_end DATE
) RETURNS VOID AS $$
BEGIN
    -- Clear existing for period
    DELETE FROM demand_signals 
    WHERE period_start = p_start AND period_end = p_end;
    
    -- Insert aggregated from budtender_queries
    INSERT INTO demand_signals (
        operator_id, category, goal, experience_level, budget_range,
        query_count, conversion_count, period_start, period_end
    )
    SELECT 
        bq.operator_id,
        -- Infer category from query text or parsed_intent
        COALESCE(
            (bq.parsed_intent->>'category'),
            infer_category_from_query(bq.query_text)
        ) AS category,
        bq.parsed_intent->>'goal' AS goal,
        bq.parsed_intent->>'experience_level' AS experience_level,
        bq.parsed_intent->>'budget_range' AS budget_range,
        COUNT(*) AS query_count,
        SUM(CASE WHEN bq.products_clicked IS NOT NULL THEN 1 ELSE 0 END) AS conversion_count,
        p_start, p_end
    FROM budtender_queries bq
    WHERE bq.created_at::DATE BETWEEN p_start AND p_end
    GROUP BY 
        bq.operator_id,
        COALESCE((bq.parsed_intent->>'category'), infer_category_from_query(bq.query_text)),
        bq.parsed_intent->>'goal',
        bq.parsed_intent->>'experience_level',
        bq.parsed_intent->>'budget_range';
END;
$$ LANGUAGE plpgsql;
```

### 4.3 Gap Analysis Methodology

```sql
-- What are customers asking about that the store DOESN'T carry?
CREATE VIEW demand_gap_analysis AS
SELECT 
    ds.operator_id,
    ds.category,
    ds.query_count,
    -- Products in this category that exist in the market (via canonical)
    EXISTS(
        SELECT 1 FROM canonical_products cp
        WHERE cp.category = ds.category
    ) AS market_exists,
    -- Products the store actually carries
    (
        SELECT COUNT(DISTINCT p.id)
        FROM products p
        JOIN prices pr ON pr.product_id = p.id
        WHERE p.category = ds.category
          AND pr.operator_id = ds.operator_id
          AND pr.scraped_at > NOW() - INTERVAL '7 days'
    ) AS store_carries_count,
    -- If market exists but store carries less than 5 -> gap
    CASE 
        WHEN market_exists = TRUE AND store_carries_count < 5 
        THEN TRUE ELSE FALSE 
    END AS is_gap
FROM demand_signals ds
WHERE ds.period_end > NOW() - INTERVAL '30 days';
```

### 4.4 Alert Integration

```sql
-- Create alerts for demand gaps
CREATE FUNCTION check_demand_gaps_and_alert() RETURNS VOID AS $$
DECLARE
    gap RECORD;
BEGIN
    FOR gap IN 
        SELECT * FROM demand_gap_analysis WHERE is_gap = TRUE
    LOOP
        -- Only alert if query_count > threshold (reduce noise)
        IF gap.query_count > 10 THEN
            INSERT INTO alerts (operator_id, type, severity, title, summary, payload)
            VALUES (
                gap.operator_id,
                'demand_gap',
                'medium',
                'Product Gap Detected: ' || gap.category,
                'Customers asked about ' || gap.category || ' ' || gap.query_count || ' times but you carry less than competitors',
                jsonb_build_object(
                    'category', gap.category,
                    'query_count', gap.query_count,
                    'store_carries', gap.store_carries_count,
                    'recommended_products', (
                        SELECT jsonb_agg(jsonb_build_object('name', cp.canonical_name, 'brand', cp.normalized_brand))
                        FROM canonical_products cp
                        WHERE cp.category = gap.category
                        ORDER BY cp.match_count DESC
                        LIMIT 10
                    )
                )
            );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### 4.5 Effort Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Intent parsing (LLM or rules) | 3 days | Virtual Budtender integration |
| Aggregation function | 1 day | Existing schema |
| Gap analysis view | 1 day | Product matching |
| Alert cron job | 1 day | Alerts table |
| **Total** | **6 days** | Requires VB queries flowing |

---

## 5. Pricing Intelligence Engine

Detect pricing anomalies, coordinated pricing, and arbitrage opportunities.

### 5.1 Change Detection Algorithm

```sql
-- Track price changes per product per operator
CREATE MATERIALIZED VIEW price_changes AS
WITH latest_prices AS (
    SELECT 
        product_id,
        operator_id,
        price,
        scraped_at,
        LAG(price) OVER (
            PARTITION BY product_id, operator_id 
            ORDER BY scraped_at
        ) AS prev_price,
        LAG(scraped_at) OVER (
            PARTITION BY product_id, operator_id 
            ORDER BY scraped_at
        ) AS prev_scraped_at
    FROM prices
    WHERE scraped_at > NOW() - INTERVAL '30 days'
)
SELECT 
    product_id,
    operator_id,
    price,
    prev_price,
    prev_scraped_at,
    scraped_at,
    CASE 
        WHEN prev_price IS NULL THEN NULL
        WHEN prev_price = 0 THEN NULL
        ELSE ((price - prev_price) / prev_price * 100)::DECIMAL(6,2)
    END AS pct_change,
    CASE 
        WHEN prev_price IS NULL THEN 'new'
        WHEN prev_price = 0 THEN 'error'
        WHEN ABS((price - prev_price) / prev_price) > 0.20 THEN 'significant'
        WHEN ABS((price - prev_price) / prev_price) > 0.10 THEN 'moderate'
        ELSE 'minor'
    END AS change_type
FROM latest_prices
WHERE prev_price IS NOT NULL;

CREATE UNIQUE INDEX ON price_changes(product_id, operator_id, scraped_at);
```

### 5.2 Coordinated Pricing Detection

```sql
-- Detect when multiple stores change price on same product within 48 hours
CREATE VIEW coordinated_pricing AS
WITH price_changes_48h AS (
    SELECT 
        pc.product_id,
        pc.operator_id,
        pc.price,
        pc.scraped_at,
        pc.pct_change,
        o.city,
        o.lat,
        o.lon
    FROM price_changes pc
    JOIN operators o ON o.id = pc.operator_id
    WHERE pc.change_type = 'significant'
      AND pc.scraped_at > NOW() - INTERVAL '48 hours'
)
SELECT 
    pc1.product_id,
    pc1.operator_id AS store_1_id,
    o1.name AS store_1_name,
    pc2.operator_id AS store_2_id,
    o2.name AS store_2_name,
    pc1.pct_change AS store_1_change,
    pc2.pct_change AS store_2_change,
    ABS(pc1.pct_change - pc2.pct_change) AS change_diff,
    pc1.scraped_at AS store_1_time,
    pc2.scraped_at AS store_2_time,
    CASE 
        WHEN ABS(pc1.scraped_at - pc2.scraped_at) < INTERVAL '4 hours' THEN 'simultaneous'
        WHEN ABS(pc1.scraped_at - pc2.scraped_at) < INTERVAL '24 hours' THEN 'within_24h'
        ELSE 'within_48h'
    END AS timing_bucket
FROM price_changes_48h pc1
JOIN price_changes_48h pc2 ON 
    pc1.product_id = pc2.product_id 
    AND pc1.operator_id < pc2.operator_id
JOIN operators o1 ON o1.id = pc1.operator_id
JOIN operators o2 ON o2.id = pc2.operator_id
WHERE ABS(pc1.pct_change - pc2.pct_change) < 5  -- similar % change
ORDER BY ABS(pc1.scraped_at - pc2.scraped_at) ASC;
```

### 5.3 Arbitrage Opportunity Detection

```sql
-- Find same products with wildly different prices nearby
CREATE VIEW arbitrage_opportunities AS
SELECT 
    cp.id AS canonical_product_id,
    cp.canonical_name,
    cp.normalized_brand,
    cp.category,
    p1.operator_id AS store_1_id,
    o1.name AS store_1_name,
    o1.city AS store_1_city,
    pr1.price AS store_1_price,
    p2.operator_id AS store_2_id,
    o2.name AS store_2_name,
    o2.city AS store_2_city,
    pr2.price AS store_2_price,
    ABS(pr1.price - pr2.price) AS price_diff,
    (ABS(pr1.price - pr2.price) / LEAST(pr1.price, pr2.price) * 100)::DECIMAL(6,2) AS pct_diff,
    -- Distance (if both geocoded)
    (6371 * acos(cos(radians(o1.lat::NUMERIC)) * cos(radians(o2.lat::NUMERIC)) * 
     cos(radians(o2.lon::NUMERIC) - radians(o1.lon::NUMERIC)) * 
     cos(radians(o1.lat::NUMERIC))))::DECIMAL(10,2) AS distance_miles
FROM canonical_products cp
JOIN product_matches pm1 ON pm1.canonical_product_id = cp.id
JOIN products p1 ON p1.id = pm1.source_product_id
JOIN prices pr1 ON pr1.product_id = p1.id
JOIN operators o1 ON o1.id = pr1.operator_id
JOIN product_matches pm2 ON pm2.canonical_product_id = cp.id
JOIN products p2 ON p2.id = pm2.source_product_id
JOIN prices pr2 ON pr2.product_id = p2.id
JOIN operators o2 ON o2.id = pr2.operator_id
WHERE pr1.scraped_at > NOW() - INTERVAL '7 days'
  AND pr2.scraped_at > NOW() - INTERVAL '7 days'
  AND pr1.operator_id < pr2.operator_id
  AND (ABS(pr1.price - pr2.price) / LEAST(pr1.price, pr2.price)) > 0.30  -- 30%+ diff
  AND o1.lat IS NOT NULL 
  AND o2.lat IS NOT NULL
ORDER BY pct_diff DESC
LIMIT 100;
```

### 5.4 Promotional Pattern Detection

```sql
-- Detect recurring discount patterns by day of week
CREATE VIEW promo_patterns AS
SELECT 
    EXTRACT(DOW FROM pr.scraped_at)::INTEGER AS day_of_week,
    p.category,
    AVG(CASE WHEN pr.promo_flag = TRUE THEN pr.price END) AS promo_price,
    AVG(CASE WHEN pr.promo_flag = FALSE THEN pr.price END) AS regular_price,
    COUNT(*) FILTER (WHERE pr.promo_flag = TRUE) AS promo_count,
    COUNT(*) FILTER (WHERE pr.promo_flag = FALSE) AS regular_count,
    (AVG(CASE WHEN pr.promo_flag = TRUE THEN pr.price END) / 
     AVG(CASE WHEN pr.promo_flag = FALSE THEN pr.price END) - 1 * 100)::DECIMAL(6,2) AS avg_discount_pct
FROM prices pr
JOIN products p ON p.id = pr.product_id
WHERE pr.scraped_at > NOW() - INTERVAL '90 days'
GROUP BY day_of_week, p.category
HAVING COUNT(*) FILTER (WHERE pr.promo_flag = TRUE) > 50  -- meaningful sample
ORDER BY day_of_week, avg_discount_pct;
```

### 5.5 Effort Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Change detection MV | 1 day | Prices table |
| Coordinated pricing view | 1 day | Product matching |
| Arbitrage view | 1 day | Product matching |
| Promo pattern view | 1 day | Prices + promo_flag |
| Alert integration | 1 day | Alerts table |
| **Total** | **5 days** | Requires Section 1 |

---

## 6. Monetization Opportunities

Additional revenue streams beyond the $199/mo subscription.

### 6.1 Data Products for Brands & Cultivators

| Product | Description | Est. Price | Target |
|---------|-------------|------------|--------|
| **Brand Dashboard** | "Where is my product priced? How much shelf space?" | $499/mo | Brands (Cookies, Rythm) |
| **Cultivator Intelligence** | Lab results + retail pricing + competitor quality | $799/mo | Cultivators |
| **Compliance Monitor** | Price compliance checking for distributors | $299/mo | Distributors |
| **Market Share Reports** | Category-level share by region (anonymized) | $1,999/qtr | Investors, consultants |

### 6.2 API as a Product

**Product Match API** — sell matching as a service:
- Input: Product name, brand, weight, category
- Output: Matched canonical ID, confidence, alternative matches
- Price: $0.01 per lookup, or $99/mo unlimited

**Competitive API**:
- Input: Operator ID, radius
- Output: Competitor list, price benchmarks, category gaps
- Price: $49/mo per operator

### 6.3 White-Label Opportunities

| Opportunity | Description | Potential |
|-------------|-------------|-----------|
| **State Expansion** | Replicate GLASS for CT, NJ, NY | $50K setup + $199/mo per client |
| **Dispensary POS Integration** | Embed GLASS pricing in POS systems | Revenue share 10-20% |
| **Insurance/Lending** | Use GLASS data for business valuation | Per-query fees |

### 6.4 Revenue Model Summary

| Stream | One-Time | Recurring | Notes |
|--------|----------|-----------|-------|
| Brand dashboards | - | $5K-10K/mo | 10 brands @ $500-1K each |
| Cultivator intelligence | - | $8K/mo | 10 cultivators @ $800 each |
| API access | - | $5K/mo | 50 operators @ $100 each |
| Market reports | $24K/yr | - | 4 reports/yr @ $6K each |
| State expansion | $50K | $20K/mo | If 100 operators across 2 states |
| **Total potential** | **$50K** | **$38K/mo** | Conservative estimate |

---

## 7. Implementation Priority

Based on revenue impact, technical feasibility, and time to deliver.

### 7.1 Recommended Build Order

| Priority | Feature | Revenue Impact | Feasibility | Effort | Why First |
|----------|---------|----------------|-------------|--------|-----------|
| **P0** | Product Matching Engine | HIGH | Medium | 12 days | Enables ALL other features |
| **P1** | Pricing Intelligence | HIGH | High | 5 days | Direct value to operators |
| **P1** | Competitive Snapshots | High | High | 7 days | Direct value to operators |
| **P2** | Supply Chain Graph | Medium | Medium | 9 days | Valuable for cultivators |
| **P2** | Demand Signals | Medium | Low | 6 days | Requires VB adoption |
| **P3** | Monetization APIs | High | Low | 10 days | Revenue diversification |

### 7.2 Technical Dependencies

```
Product Matching (P0) ──┬──► Pricing Intelligence (P1)
                        ├──► Competitive Snapshots (P1)
                        ├──► Supply Chain Graph (P2)
                        └──► Demand Signals (P2)
```

**No dependencies:** Pricing Intelligence can build with existing `products` table, but product matching makes it far more accurate.

### 7.3 Quick Wins (Before Major Build)

1. **Price change alerts** — Use existing `prices` table, no matching needed
   - Alert when any product at an operator changes >15%
   - Effort: 1 day

2. **Nearest competitor query** — Use existing geocoding
   - Haversine query for N nearest
   - Effort: 1 day

3. **CCC lab test leaderboard** — Use existing `ccc_lab_tests`
   - Rank cultivators by avg THC, pass rate
   - Effort: 1 day

### 7.4 Resource Requirements

| Role | Quantity | Duration |
|------|----------|----------|
| Backend Engineer | 1 | 30 days |
| Data Engineer | 1 | 20 days |
| Frontend (admin UI) | 0.5 | 15 days |

**Total engineering: ~50 developer-days**

---

## 8. Data Gaps & Requirements

### 8.1 What We DON'T Have (Explicitly)

| Gap | Impact | Workaround |
|-----|--------|------------|
| Wholesale pricing | Cannot calculate true markup | Infer from retail price ranges |
| Batch/Lot traceability | Cannot trace product to specific harvest | Use strain-level matching |
| Real-time inventory | Prices may be stale | Scrape more frequently |
| Customer purchase data | No point-of-sale integration | Use demand signals proxy |

### 8.2 What We Need to Build

1. **Brand alias table** — Manual curation of known brand name variations
2. **Matching job scheduler** — `pg_cron` job to run matching nightly
3. **Snapshot refresh scheduler** — Daily competitive snapshot updates
4. **Alert delivery system** — Email + push notifications for pricing alerts

---

## 9. Summary

The data intelligence layer transforms GLASS from a "menu scraper" into a "market intelligence platform." The core value chain:

1. **Product Matching** is the foundation — without it, we have 100K disconnected product records
2. **Competitive Intelligence** delivers immediate operator value ($199/mo justification)
3. **Supply Chain** unlocks B2B revenue (cultivators, brands)
4. **Pricing Intelligence** creates actionable alerts (daily/weekly value)
5. **Demand Signals** enables proactive product recommendations

**Total implementation: ~50 developer-days across 3 months**

**Revenue potential: $38K/mo recurring + $50K one-time expansions**

---

*Plan created: 2026-02-13*
*For: GLASS Data Intelligence Architecture*
