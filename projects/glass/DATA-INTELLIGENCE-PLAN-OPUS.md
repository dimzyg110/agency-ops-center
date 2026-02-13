# GLASS Data Intelligence Engine — Architecture Plan

**Author:** Senior Data Intelligence Architect  
**Date:** February 13, 2026  
**Status:** PROPOSED  
**Scope:** Cross-data matching, intelligence layers, and monetization systems  

---

## Executive Summary

GLASS sits on a unique dataset: 100,849 products from ~490 dispensary menus, 147,649 lab tests, 772 CCC licenses, 67,333 facility-level sales records, and 116,991 price observations — all in Massachusetts. Nobody else has this cross-referenced at this granularity. But today these datasets are silos: products from different stores are separate records, lab tests don't connect to retail products, and CCC sales data doesn't link to menu prices.

This plan designs the intelligence layer that fuses them. The core thesis: **the same physical product sold at 50 different stores should be ONE canonical product with 50 price observations**. That single change unlocks price comparison, demand ranking, market share estimation, and competitive positioning — the features that make GLASS irreplaceable.

**What exists today (grounded in codebase audit):**
- Operator matching (`match-operators.ts`): 6-tier system linking 770/772 CCC licenses to operators ✅
- Brand normalization (`brand.ts`, `normalizer.ts`): centralized validation, 37.6% of products have valid brands ✅
- SKU generation: `buildSku()` creates deterministic SKUs per store — but NOT cross-store ❌
- `operator_scores` table: exists but **0 rows populated** ❌
- `refresh_health_scores()` function: exists but never called ❌
- Product matching: **does not exist** ❌

**What this plan adds:**
1. Cross-Store Product Matching Engine (the moat)
2. Supply Chain Intelligence (cultivator → retailer tracing)
3. Competitive Radius Analysis (per-operator competitive landscape)
4. Demand Intelligence (from Virtual Budtender queries)
5. Pricing Intelligence (change detection, coordination, arbitrage)
6. Monetization systems beyond $199/mo subscriptions

---

## Table of Contents

1. [Cross-Store Product Matching Engine](#1-cross-store-product-matching-engine)
2. [Supply Chain Intelligence](#2-supply-chain-intelligence)
3. [Competitive Radius Analysis](#3-competitive-radius-analysis)
4. [Demand Intelligence](#4-demand-intelligence)
5. [Pricing Intelligence](#5-pricing-intelligence)
6. [Monetization Beyond $199/mo](#6-monetization-beyond-199mo)
7. [Implementation Priority](#7-implementation-priority)

---

## 1. Cross-Store Product Matching Engine

### 1.1 Problem Statement

Currently, "Fernway Blue Dream Cartridge 0.5g" at Store A and "FERNWAY - Blue Dream Cart .5g" at Store B are two completely separate `products` records with different UUIDs and different SKUs. The existing `buildSku()` function in `normalizer.ts` generates SKUs as `{BRAND_OR_NAME}-{NAME_TOKEN}-{QTY_UNIT}`, which varies by whitespace, casing, and name truncation per store.

With 100,849 products across ~490 stores, we estimate 8,000–15,000 truly unique products represented by 5–12 records each on average (heavily skewed: top brands at 50+ stores, house brands at 1 store).

### 1.2 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  MATCHING PIPELINE                        │
│                                                           │
│  products table (100K rows)                               │
│       │                                                   │
│       ▼                                                   │
│  ┌─────────────────────┐                                  │
│  │ Stage 1: Normalize  │  brand, name, weight, category   │
│  │ (deterministic)     │  → product_fingerprint            │
│  └──────────┬──────────┘                                  │
│             ▼                                              │
│  ┌─────────────────────┐                                  │
│  │ Stage 2: Block      │  group by (norm_brand,            │
│  │ (reduce comparisons)│   category, weight_bucket)        │
│  └──────────┬──────────┘                                  │
│             ▼                                              │
│  ┌─────────────────────┐                                  │
│  │ Stage 3: Score      │  trigram + Levenshtein on         │
│  │ (pairwise within    │  normalized name, strain,         │
│  │  blocks)            │  THC%, weight                     │
│  └──────────┬──────────┘                                  │
│             ▼                                              │
│  ┌─────────────────────┐                                  │
│  │ Stage 4: Cluster    │  Union-Find on high-confidence    │
│  │ (transitivity)      │  pairs → canonical_product_id     │
│  └──────────┬──────────┘                                  │
│             ▼                                              │
│  canonical_products + product_matches tables              │
└──────────────────────────────────────────────────────────┘
```

### 1.3 Stage 1: Normalization Functions

These functions build a **fingerprint** for each product that makes approximate matching tractable.

```typescript
// product-fingerprint.ts

interface ProductFingerprint {
  norm_brand: string | null;     // normalized brand or null
  norm_name: string;             // cleaned product name (brand stripped, weight stripped)
  category: string;              // flower|preroll|vape|edible|concentrate|tincture|topical|other
  weight_grams: number | null;   // standardized to grams
  strain_name: string | null;    // extracted strain with variations normalized
  strain_type: string | null;    // indica|sativa|hybrid|cbd
  thc_bucket: string | null;     // '0-10'|'10-20'|'20-30'|'30+'
  fingerprint_key: string;       // deterministic hash for exact-match dedup
}

function normalizeBrandForMatching(brand: string | null, name: string): string | null {
  // 1. If brand is valid (passes isValidBrand), normalize:
  //    - lowercase, trim, collapse whitespace
  //    - strip common suffixes: " inc", " llc", " co", " cannabis", " farms"
  //    - Known alias map: {"good chem": "good chemistry", "b&b": "bountiful farms", ...}
  // 2. If brand is null, try to extract from name:
  //    - Match against known brand list (built from products WHERE brand IS NOT NULL, count > 5)
  //    - If name starts with a known brand, extract it
  // 3. Return null if unresolvable

  if (!brand && name) {
    // Try prefix matching against known brand dictionary
    const lowerName = name.toLowerCase();
    for (const [key, canonical] of BRAND_ALIASES.entries()) {
      if (lowerName.startsWith(key)) return canonical;
    }
  }
  return brand ? brand.toLowerCase().trim()
    .replace(/\s+(inc|llc|co|company|cannabis|farms|farm)\.?$/i, '')
    .replace(/\s+/g, ' ') : null;
}

function extractWeight(name: string, quantity: number | null, unit: string | null): number | null {
  // Priority: explicit quantity field > parsed from name
  if (quantity && unit) {
    return convertToGrams(quantity, unit);
  }
  
  // Parse from name: "0.5g", "1/8 oz", "3.5g", "1000mg", "100mg 10pk"
  const patterns = [
    /(\d+(?:\.\d+)?)\s*g\b/i,                    // "3.5g"
    /(\d+(?:\.\d+)?)\s*(?:oz|ounce)\b/i,          // "1 oz" → *28.35
    /1\/8\s*(?:oz|ounce)?/i,                       // "1/8 oz" → 3.5g
    /1\/4\s*(?:oz|ounce)?/i,                       // "1/4 oz" → 7g
    /1\/2\s*(?:oz|ounce)?/i,                       // "1/2 oz" → 14g
    /(\d+(?:\.\d+)?)\s*mg\b/i,                    // "100mg" → /1000 for edibles only
  ];
  // ... pattern matching with category-aware conversion
  return null;
}

function extractStrainName(name: string, brand: string | null): string | null {
  // 1. Remove brand prefix from name
  // 2. Remove weight/size suffixes
  // 3. Remove category words (cartridge, pre-roll, gummy, etc.)
  // 4. Normalize strain synonyms: {"gg4": "gorilla glue #4", "gsc": "girl scout cookies", ...}
  // 5. What remains is likely the strain name
  // Returns null for generic products ("House Blend", "Mixed Shake", etc.)
  
  let cleaned = name;
  if (brand) {
    cleaned = cleaned.replace(new RegExp(`^${escapeRegex(brand)}\\s*[-–—|:]?\\s*`, 'i'), '');
  }
  // Strip weight, category, packaging terms
  cleaned = cleaned
    .replace(/\b\d+(?:\.\d+)?\s*(g|mg|oz|ml|pk|pack|count|ct)\b/gi, '')
    .replace(/\b(cartridge|cart|vape|pre-?roll|joint|gummy|gummies|edible|tincture|flower|bud|concentrate|wax|shatter|rosin|badder|budder|sauce|diamonds?|live\s*resin|cured\s*resin|distillate|disposable|pod|all[- ]in[- ]one)\b/gi, '')
    .replace(/\b(indica|sativa|hybrid|cbd)\b/gi, '')
    .replace(/[-–—|:()]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  
  if (cleaned.length < 2 || /^\d+$/.test(cleaned)) return null;
  
  return STRAIN_ALIASES.get(cleaned.toLowerCase()) || cleaned.toLowerCase();
}

function buildFingerprint(product: Product): ProductFingerprint {
  const norm_brand = normalizeBrandForMatching(product.brand, product.name);
  const weight_grams = extractWeight(product.name, product.quantity, product.unit);
  const strain_name = extractStrainName(product.name, product.brand);
  const norm_name = buildNormalizedName(product.name, norm_brand, weight_grams);
  const thc_bucket = product.thc_percent 
    ? (product.thc_percent < 10 ? '0-10' : product.thc_percent < 20 ? '10-20' : product.thc_percent < 30 ? '20-30' : '30+')
    : null;
  
  // Deterministic fingerprint for exact dedup
  const fingerprint_key = [
    norm_brand || '_',
    product.category || '_',
    norm_name,
    weight_grams?.toFixed(1) || '_',
  ].join('|').toLowerCase();
  
  return { norm_brand, norm_name, category: product.category || 'other', 
           weight_grams, strain_name, strain_type: product.strain_type,
           thc_bucket, fingerprint_key };
}
```

### 1.4 Stage 2: Blocking Strategy

Comparing all 100K × 100K product pairs = 5 billion comparisons. Blocking reduces this to manageable sets.

**Blocking keys** (products share a block if they match on ALL of these):
1. `category` (flower, vape, edible, etc.)
2. `weight_bucket` (0-1g, 1-4g, 4-8g, 8-15g, 15-30g, 30g+, or NULL)
3. `norm_brand` (if both non-null) OR `first_3_chars_norm_name` (if brand is null)

**Expected block sizes:**
- Branded products: ~50–200 per block (e.g., "Fernway" + "vape" + "0.5g")
- Unbranded products: larger blocks, filtered by name prefix

**SQL to generate blocks:**

```sql
-- Add fingerprint columns to products table
ALTER TABLE products ADD COLUMN IF NOT EXISTS norm_brand VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS norm_name VARCHAR(300);
ALTER TABLE products ADD COLUMN IF NOT EXISTS weight_grams DECIMAL(10, 3);
ALTER TABLE products ADD COLUMN IF NOT EXISTS strain_name VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS fingerprint_key VARCHAR(500);
ALTER TABLE products ADD COLUMN IF NOT EXISTS canonical_product_id UUID;

CREATE INDEX idx_products_fingerprint ON products (fingerprint_key);
CREATE INDEX idx_products_norm_brand ON products (norm_brand);
CREATE INDEX idx_products_canonical ON products (canonical_product_id);

-- Block generation query
SELECT 
  category,
  CASE 
    WHEN weight_grams IS NULL THEN 'unknown'
    WHEN weight_grams < 1 THEN '0-1g'
    WHEN weight_grams < 4 THEN '1-4g'
    WHEN weight_grams < 8 THEN '4-8g'
    WHEN weight_grams < 15 THEN '8-15g'
    WHEN weight_grams < 30 THEN '15-30g'
    ELSE '30g+'
  END AS weight_bucket,
  COALESCE(norm_brand, LEFT(norm_name, 3)) AS brand_or_prefix,
  ARRAY_AGG(id) AS product_ids,
  COUNT(*) AS block_size
FROM products
WHERE category IS NOT NULL
GROUP BY 1, 2, 3
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;
```

### 1.5 Stage 3: Pairwise Similarity Scoring

Within each block, compute similarity scores between all pairs:

```sql
-- Requires: CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- (Already exists — created by match-operators.ts)

-- Similarity scoring function
CREATE OR REPLACE FUNCTION product_similarity(
  p1_name TEXT, p1_brand TEXT, p1_strain TEXT, p1_thc DECIMAL, p1_weight DECIMAL,
  p2_name TEXT, p2_brand TEXT, p2_strain TEXT, p2_thc DECIMAL, p2_weight DECIMAL
) RETURNS DECIMAL AS $$
DECLARE
  name_sim DECIMAL;
  brand_sim DECIMAL;
  strain_sim DECIMAL;
  thc_sim DECIMAL;
  weight_sim DECIMAL;
  total DECIMAL;
BEGIN
  -- Name similarity (trigram): weight 0.35
  name_sim := similarity(p1_name, p2_name);
  
  -- Brand similarity: weight 0.25 (0 if either is null, 1.0 if exact match)
  IF p1_brand IS NOT NULL AND p2_brand IS NOT NULL THEN
    brand_sim := similarity(p1_brand, p2_brand);
  ELSIF p1_brand IS NULL AND p2_brand IS NULL THEN
    brand_sim := 0.5; -- both unknown, neutral
  ELSE
    brand_sim := 0.0; -- one has brand, other doesn't → penalty
  END IF;
  
  -- Strain similarity: weight 0.20
  IF p1_strain IS NOT NULL AND p2_strain IS NOT NULL THEN
    strain_sim := similarity(p1_strain, p2_strain);
  ELSIF p1_strain IS NULL AND p2_strain IS NULL THEN
    strain_sim := 0.5;
  ELSE
    strain_sim := 0.2;
  END IF;
  
  -- THC proximity: weight 0.10 (1.0 if within 2%, 0 if >10% apart)
  IF p1_thc IS NOT NULL AND p2_thc IS NOT NULL THEN
    thc_sim := GREATEST(0, 1.0 - ABS(p1_thc - p2_thc) / 10.0);
  ELSE
    thc_sim := 0.5;
  END IF;
  
  -- Weight match: weight 0.10 (1.0 if same, 0 if different)
  IF p1_weight IS NOT NULL AND p2_weight IS NOT NULL THEN
    weight_sim := CASE WHEN ABS(p1_weight - p2_weight) < 0.1 THEN 1.0 ELSE 0.0 END;
  ELSE
    weight_sim := 0.5;
  END IF;
  
  total := (name_sim * 0.35) + (brand_sim * 0.25) + (strain_sim * 0.20) 
           + (thc_sim * 0.10) + (weight_sim * 0.10);
  
  RETURN ROUND(total, 4);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

**Confidence tiers:**
| Score Range | Confidence | Action |
|---|---|---|
| ≥ 0.90 | `auto_match` | Automatically linked, no human review |
| 0.75–0.89 | `high` | Linked, flagged for spot-check |
| 0.55–0.74 | `medium` | Queued for human review |
| < 0.55 | `no_match` | Not linked |

### 1.6 Stage 4: Clustering via Union-Find

Matching is transitive: if A≈B and B≈C, then A≈C. We use Union-Find to cluster products.

```typescript
// union-find.ts — Disjoint Set Union with path compression

class UnionFind {
  parent: Map<string, string> = new Map();
  rank: Map<string, number> = new Map();
  
  find(x: string): string {
    if (!this.parent.has(x)) {
      this.parent.set(x, x);
      this.rank.set(x, 0);
    }
    if (this.parent.get(x) !== x) {
      this.parent.set(x, this.find(this.parent.get(x)!)); // path compression
    }
    return this.parent.get(x)!;
  }
  
  union(x: string, y: string): void {
    const rx = this.find(x);
    const ry = this.find(y);
    if (rx === ry) return;
    
    const rankX = this.rank.get(rx)!;
    const rankY = this.rank.get(ry)!;
    if (rankX < rankY) { this.parent.set(rx, ry); }
    else if (rankX > rankY) { this.parent.set(ry, rx); }
    else { this.parent.set(ry, rx); this.rank.set(rx, rankX + 1); }
  }
  
  clusters(): Map<string, string[]> {
    const result = new Map<string, string[]>();
    for (const x of this.parent.keys()) {
      const root = this.find(x);
      if (!result.has(root)) result.set(root, []);
      result.get(root)!.push(x);
    }
    return result;
  }
}

// Usage:
// 1. Query all product_matches with confidence >= 'high'
// 2. For each match pair, uf.union(product_id_a, product_id_b)
// 3. Each cluster → one canonical_product
// 4. Pick the "best" record as canonical (most complete data, highest brand confidence)
```

### 1.7 Schema: New Tables

```sql
-- ============================================================
-- CANONICAL PRODUCTS — One record per real-world product
-- ============================================================
CREATE TABLE canonical_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Best-available product attributes (merged from matched products)
  name VARCHAR(500) NOT NULL,                -- "Fernway Blue Dream Cartridge 0.5g"
  brand VARCHAR(255),                         -- "Fernway"
  category VARCHAR(50) NOT NULL,              -- "vape"
  weight_grams DECIMAL(10, 3),                -- 0.500
  strain_name VARCHAR(100),                   -- "blue dream"
  strain_type VARCHAR(50),                    -- "sativa"
  thc_percent_avg DECIMAL(5, 2),              -- average across matched products
  cbd_percent_avg DECIMAL(5, 2),
  
  -- Matching metadata
  source_product_count INTEGER NOT NULL DEFAULT 1,  -- how many store-level products match
  store_count INTEGER NOT NULL DEFAULT 1,            -- distinct stores carrying this
  confidence_avg DECIMAL(3, 2),                      -- average match confidence
  
  -- Pricing summary (denormalized for fast reads)
  price_min DECIMAL(10, 2),
  price_max DECIMAL(10, 2),
  price_avg DECIMAL(10, 2),
  price_median DECIMAL(10, 2),
  price_spread_pct DECIMAL(5, 2),             -- (max-min)/avg * 100
  last_price_update TIMESTAMP WITH TIME ZONE,
  
  -- Lifecycle
  first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,     -- seen in last 7 days
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_canonical_brand ON canonical_products (brand);
CREATE INDEX idx_canonical_category ON canonical_products (category);
CREATE INDEX idx_canonical_strain ON canonical_products (strain_name);
CREATE INDEX idx_canonical_store_count ON canonical_products (store_count DESC);
CREATE INDEX idx_canonical_active ON canonical_products (is_active) WHERE is_active = TRUE;
CREATE INDEX idx_canonical_category_brand ON canonical_products (category, brand);

-- ============================================================
-- PRODUCT MATCHES — Links store-level products to canonical
-- ============================================================
CREATE TABLE product_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  canonical_product_id UUID NOT NULL REFERENCES canonical_products(id) ON DELETE CASCADE,
  
  -- Match quality
  confidence DECIMAL(3, 2) NOT NULL,           -- 0.00–1.00
  match_method VARCHAR(20) NOT NULL,           -- 'exact_fingerprint', 'similarity', 'manual'
  similarity_score DECIMAL(5, 4),              -- raw similarity score
  
  -- Audit
  matched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  verified_by VARCHAR(50),                     -- null = auto, 'human' = manually verified
  verified_at TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT uq_product_match UNIQUE (product_id)  -- each product maps to exactly one canonical
);

CREATE INDEX idx_product_matches_canonical ON product_matches (canonical_product_id);
CREATE INDEX idx_product_matches_confidence ON product_matches (confidence);
CREATE INDEX idx_product_matches_method ON product_matches (match_method);

-- ============================================================
-- BRAND DICTIONARY — Canonical brand names with aliases
-- ============================================================
CREATE TABLE brand_dictionary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_name VARCHAR(255) NOT NULL UNIQUE,  -- "Fernway"
  aliases JSONB NOT NULL DEFAULT '[]',           -- ["fernway", "fern way", "FERNWAY"]
  
  -- Brand metadata
  parent_company VARCHAR(255),                   -- for multi-brand operators
  license_number VARCHAR(30),                    -- CCC license if known
  operator_id UUID REFERENCES operators(id),     -- linked operator
  is_house_brand BOOLEAN NOT NULL DEFAULT FALSE, -- single-operator brand
  
  -- Product footprint
  product_count INTEGER NOT NULL DEFAULT 0,
  store_count INTEGER NOT NULL DEFAULT 0,
  categories JSONB NOT NULL DEFAULT '[]',        -- ["vape", "flower", "edible"]
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_brand_dict_canonical ON brand_dictionary (canonical_name);
CREATE INDEX idx_brand_dict_operator ON brand_dictionary (operator_id);
CREATE INDEX idx_brand_dict_license ON brand_dictionary (license_number);

-- GIN index for alias search
CREATE INDEX idx_brand_dict_aliases ON brand_dictionary USING GIN (aliases jsonb_path_ops);

-- ============================================================
-- MATCHING RUNS — Audit trail for matching pipeline
-- ============================================================
CREATE TABLE matching_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  status VARCHAR(20) NOT NULL DEFAULT 'running',
  
  -- Stats
  products_processed INTEGER NOT NULL DEFAULT 0,
  exact_matches INTEGER NOT NULL DEFAULT 0,        -- fingerprint dedup
  similarity_matches INTEGER NOT NULL DEFAULT 0,   -- scored matches
  new_canonicals INTEGER NOT NULL DEFAULT 0,        -- new canonical products created
  updated_canonicals INTEGER NOT NULL DEFAULT 0,    -- existing canonicals updated
  unmatched INTEGER NOT NULL DEFAULT 0,             -- products without a match
  
  -- Config
  similarity_threshold DECIMAL(3, 2) NOT NULL DEFAULT 0.75,
  config JSONB NOT NULL DEFAULT '{}',
  
  error_log JSONB DEFAULT '[]'
);
```

### 1.8 Matching Pipeline Pseudocode

```
PROCEDURE run_product_matching():
  
  create matching_run record
  
  -- PHASE 1: Exact fingerprint dedup (fast, high confidence)
  FOR each product without canonical_product_id:
    fingerprint = buildFingerprint(product)
    UPDATE product SET fingerprint columns
    
    IF fingerprint_key matches existing canonical_product:
      INSERT product_matches (confidence=1.0, method='exact_fingerprint')
      UPDATE canonical_product stats
    
  -- PHASE 2: Similarity matching within blocks  
  blocks = SELECT DISTINCT (category, weight_bucket, brand_or_prefix) 
           FROM products WHERE canonical_product_id IS NULL
  
  FOR each block:
    products_in_block = SELECT * FROM products WHERE block_key = block
    
    IF block.size > 500:
      -- Sub-block by first 5 chars of norm_name to keep pairwise tractable
      sub_blocks = partition(products_in_block, by=LEFT(norm_name, 5))
      FOR each sub_block: run_pairwise_matching(sub_block)
    ELSE:
      run_pairwise_matching(products_in_block)
  
  -- PHASE 3: Create canonicals from unmatched
  FOR each product still without canonical_product_id:
    CREATE canonical_product from product attributes
    INSERT product_matches (confidence=1.0, method='singleton')
  
  -- PHASE 4: Refresh canonical stats
  UPDATE canonical_products cp SET
    source_product_count = (SELECT COUNT(*) FROM product_matches WHERE canonical_product_id = cp.id),
    store_count = (SELECT COUNT(DISTINCT p.operator_id) FROM product_matches pm 
                   JOIN prices pr ON pr.product_id = pm.product_id
                   WHERE pm.canonical_product_id = cp.id),
    price_min = ..., price_max = ..., price_avg = ..., price_median = ...
    
  log matching_run stats

PROCEDURE run_pairwise_matching(product_ids[]):
  FOR each pair (a, b) in product_ids where a.id < b.id:
    score = product_similarity(a, b)
    IF score >= 0.75:
      -- Check if either already has a canonical
      IF a.canonical AND NOT b.canonical:
        link b to a's canonical
      ELIF b.canonical AND NOT a.canonical:
        link a to b's canonical
      ELIF neither has canonical:
        create new canonical from best_of(a, b)
        link both
      ELIF both have different canonicals AND score >= 0.90:
        merge canonicals (union-find)
```

### 1.9 Brand Dictionary Bootstrap

The brand dictionary bootstraps from existing data:

```sql
-- Bootstrap brand_dictionary from products table
INSERT INTO brand_dictionary (canonical_name, product_count, store_count, categories)
SELECT 
  brand AS canonical_name,
  COUNT(*) AS product_count,
  COUNT(DISTINCT p2.operator_id) AS store_count,
  jsonb_agg(DISTINCT p.category) FILTER (WHERE p.category IS NOT NULL) AS categories
FROM products p
LEFT JOIN prices p2 ON p2.product_id = p.id
WHERE p.brand IS NOT NULL
GROUP BY p.brand
HAVING COUNT(*) >= 3
ORDER BY COUNT(*) DESC;

-- Build aliases from variations
UPDATE brand_dictionary bd
SET aliases = (
  SELECT jsonb_agg(DISTINCT lower(p.brand))
  FROM products p
  WHERE similarity(lower(p.brand), lower(bd.canonical_name)) > 0.7
    AND lower(p.brand) != lower(bd.canonical_name)
);

-- Link brands to CCC licenses where possible
UPDATE brand_dictionary bd
SET license_number = cl.license_number,
    operator_id = cl.operator_id,
    parent_company = cl.business_name
FROM ccc_licenses cl
WHERE similarity(lower(bd.canonical_name), lower(cl.business_name)) > 0.5
  AND cl.license_type IN ('Marijuana Product Manufacturer', 'Marijuana Cultivator');
```

### 1.10 Incremental Matching (Daily)

The full matching pipeline runs once as a backfill. Daily, only new/updated products need matching:

```sql
-- Daily incremental: match new products since last run
WITH new_products AS (
  SELECT p.* 
  FROM products p
  LEFT JOIN product_matches pm ON pm.product_id = p.id
  WHERE pm.id IS NULL  -- no match yet
    AND p.created_at > (SELECT MAX(completed_at) FROM matching_runs)
)
-- Run through Stage 1 (fingerprint), then Stage 2-3 only if no exact match
```

### 1.11 Effort Estimate

| Task | Effort | Priority |
|---|---|---|
| Fingerprint functions + column migration | 8 hrs | P0 |
| Brand dictionary bootstrap | 4 hrs | P0 |
| Blocking + pairwise scoring (SQL functions) | 12 hrs | P0 |
| Union-Find clustering + canonical creation | 8 hrs | P0 |
| Incremental daily matching | 6 hrs | P0 |
| Admin review UI for medium-confidence matches | 12 hrs | P1 |
| **Total** | **50 hrs** | |

---

## 2. Supply Chain Intelligence

### 2.1 The Data We Have

CCC data contains the supply chain graph — we just need to assemble it:

- **`ccc_licenses`**: 772 licenses with types: Marijuana Retailer, Marijuana Cultivator, Marijuana Product Manufacturer, Delivery
- **`ccc_lab_tests`**: 147,649 tests with `metrc_tag`, `strain_code`, `testing_lab`, `test_date`, `thc_percent`, `thca_percent`
- **`ccc_facility_sales`**: 67,333 records with revenue by category and market type
- **`operators`** + **`prices`**: retail menu data

The key link: **METRC tags in lab tests are tied to license numbers** (the testing entity). The `strain_code` is anonymized (`Strain_01`), but `product_category` + THC ranges can still create useful signals.

### 2.2 What We Can Trace Today

**Cultivator → Lab Test Quality Rankings:**

```sql
-- Cultivator quality ranking by product category
CREATE MATERIALIZED VIEW mv_cultivator_quality AS
SELECT 
  cl.business_name AS cultivator_name,
  cl.license_number,
  cl.operator_id,
  lt.product_category,
  COUNT(*) AS test_count,
  ROUND(AVG(lt.total_thc_percent), 2) AS avg_thc,
  ROUND(STDDEV(lt.total_thc_percent), 2) AS thc_stddev,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY lt.total_thc_percent), 2) AS median_thc,
  ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY lt.total_thc_percent), 2) AS p90_thc,
  MIN(lt.test_date) AS first_test,
  MAX(lt.test_date) AS last_test,
  -- Consistency score: lower stddev relative to mean = more consistent
  CASE WHEN AVG(lt.total_thc_percent) > 0 
    THEN ROUND(1 - LEAST(1, STDDEV(lt.total_thc_percent) / AVG(lt.total_thc_percent)), 3)
    ELSE 0 
  END AS consistency_score
FROM ccc_lab_tests lt
JOIN ccc_licenses cl ON cl.license_number = SUBSTRING(lt.metrc_tag FROM 1 FOR 12)
  -- METRC tags typically start with the license prefix
WHERE cl.license_type LIKE '%Cultivator%'
GROUP BY cl.business_name, cl.license_number, cl.operator_id, lt.product_category
HAVING COUNT(*) >= 10;

CREATE INDEX idx_mv_cultivator_quality_license ON mv_cultivator_quality (license_number);
CREATE INDEX idx_mv_cultivator_quality_category ON mv_cultivator_quality (product_category);
```

**Note on METRC tag → license linkage:** Massachusetts METRC tags follow the format `{LICENSE_PREFIX}{SEQUENCE}`. We need to verify the exact prefix length against actual data. If the link isn't possible via tag prefix, we fall back to the `operator_id` FK on `ccc_lab_tests` (currently nullable — needs population via matching).

### 2.3 Cultivator → Retailer Connection (Inference)

Direct cultivator-to-retailer tracing requires METRC transfer data (not available in CCC public data). However, we can **infer** connections:

```sql
-- Schema: supply chain inferences
CREATE TABLE supply_chain_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Supply side
  cultivator_license VARCHAR(30) NOT NULL,
  cultivator_name VARCHAR(500),
  cultivator_operator_id UUID REFERENCES operators(id),
  
  -- Demand side  
  retailer_license VARCHAR(30),
  retailer_name VARCHAR(500),
  retailer_operator_id UUID REFERENCES operators(id),
  
  -- Link evidence
  link_type VARCHAR(30) NOT NULL,              -- 'same_entity', 'brand_match', 'strain_thc_match', 'address_match'
  confidence DECIMAL(3, 2) NOT NULL,
  evidence JSONB NOT NULL DEFAULT '{}',        -- supporting data points
  
  -- Product details
  product_category VARCHAR(50),
  brand_name VARCHAR(255),
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_supply_chain_cultivator ON supply_chain_links (cultivator_license);
CREATE INDEX idx_supply_chain_retailer ON supply_chain_links (retailer_operator_id);
CREATE INDEX idx_supply_chain_type ON supply_chain_links (link_type);
CREATE INDEX idx_supply_chain_confidence ON supply_chain_links (confidence);
```

**Inference methods:**

```
METHOD 1: Same Entity Detection (confidence: 0.95)
  -- Companies with multiple license types at same address
  SELECT c.business_name, c.license_type, c.establishment_address_1
  FROM ccc_licenses c
  WHERE c.establishment_address_1 IN (
    SELECT establishment_address_1 
    FROM ccc_licenses 
    GROUP BY establishment_address_1 
    HAVING COUNT(DISTINCT license_type) > 1
  )
  ORDER BY c.establishment_address_1;
  -- Example: "Curaleaf" has cultivator + manufacturer + retailer licenses

METHOD 2: Brand → Manufacturer → Retailer (confidence: 0.70)
  -- If brand X is made by manufacturer M (from brand_dictionary.license_number),
  -- and retailer R sells brand X products, then M → R is a supply link.
  SELECT 
    bd.canonical_name AS brand,
    bd.license_number AS manufacturer_license,
    DISTINCT p2.operator_id AS retailer_operator_id
  FROM brand_dictionary bd
  JOIN product_matches pm ON pm.canonical_product_id IN (
    SELECT cp.id FROM canonical_products cp WHERE cp.brand = bd.canonical_name
  )
  JOIN prices p2 ON p2.product_id = pm.product_id
  WHERE bd.license_number IS NOT NULL;

METHOD 3: THC Fingerprint Matching (confidence: 0.50)
  -- Match lab test THC% to retail product THC% within same strain
  -- If cultivator C's lab test shows "Strain_X at 28.3% THC" and
  -- retailer R sells "Blue Dream 28.5% THC", possible link
  -- (Low confidence due to strain code anonymization)
```

### 2.4 Wholesale-to-Retail Markup Estimation

CCC publishes transfer prices (what dispensaries pay). We have retail prices (what consumers pay). The delta is the retail markup.

```sql
-- Wholesale-to-retail markup by category
CREATE MATERIALIZED VIEW mv_markup_analysis AS
WITH transfer_prices AS (
  -- CCC monthly avg prices represent wholesale/transfer prices
  SELECT 
    year_month,
    avg_price_per_gram AS wholesale_per_gram,
    avg_price_per_eighth AS wholesale_per_eighth
  FROM ccc_monthly_prices
  WHERE year_month >= '2024-01'
),
retail_prices AS (
  -- Our scraped menu prices, aggregated monthly
  SELECT 
    TO_CHAR(scraped_at, 'YYYY-MM') AS year_month,
    category,
    -- Normalize to per-gram for flower
    AVG(CASE WHEN weight_grams > 0 THEN price / weight_grams END) AS retail_per_gram,
    AVG(price) FILTER (WHERE weight_grams BETWEEN 3.0 AND 4.0) AS retail_per_eighth,
    COUNT(*) AS observation_count
  FROM prices p
  JOIN products prod ON prod.id = p.product_id
  WHERE p.confidence >= 0.7
    AND prod.category = 'flower'
    AND p.price > 0
    AND p.price < 500  -- sanity cap
  GROUP BY 1, 2
)
SELECT 
  rp.year_month,
  rp.category,
  tp.wholesale_per_gram,
  rp.retail_per_gram,
  ROUND((rp.retail_per_gram - tp.wholesale_per_gram) / NULLIF(tp.wholesale_per_gram, 0) * 100, 1) AS markup_pct,
  tp.wholesale_per_eighth,
  rp.retail_per_eighth,
  ROUND((rp.retail_per_eighth - tp.wholesale_per_eighth) / NULLIF(tp.wholesale_per_eighth, 0) * 100, 1) AS eighth_markup_pct,
  rp.observation_count
FROM retail_prices rp
JOIN transfer_prices tp ON tp.year_month = rp.year_month
WHERE rp.category = 'flower'
ORDER BY rp.year_month;
```

### 2.5 Entity Graph: Which Brands Are Same Company

```sql
-- Find multi-brand entities using CCC license data
CREATE MATERIALIZED VIEW mv_entity_graph AS
WITH entity_licenses AS (
  SELECT 
    -- Group by normalized business entity
    REGEXP_REPLACE(
      REGEXP_REPLACE(lower(business_name), '\s*(inc|llc|corp|ltd|co|company)\.?\s*$', '', 'i'),
      '\s+', ' ', 'g'
    ) AS entity_key,
    ARRAY_AGG(DISTINCT license_number) AS license_numbers,
    ARRAY_AGG(DISTINCT license_type) AS license_types,
    ARRAY_AGG(DISTINCT business_name) AS dba_names,
    COUNT(DISTINCT license_number) AS license_count,
    ARRAY_AGG(DISTINCT establishment_city) AS cities
  FROM ccc_licenses
  WHERE license_status = 'Active'
  GROUP BY 1
  HAVING COUNT(DISTINCT license_number) > 1
)
SELECT 
  entity_key,
  license_numbers,
  license_types,
  dba_names,
  license_count,
  cities,
  -- Vertical integration score: has cultivator + manufacturer + retailer
  (CASE WHEN 'Marijuana Cultivator' = ANY(license_types) THEN 1 ELSE 0 END +
   CASE WHEN 'Marijuana Product Manufacturer' = ANY(license_types) THEN 1 ELSE 0 END +
   CASE WHEN 'Marijuana Retailer' = ANY(license_types) THEN 1 ELSE 0 END) AS vertical_integration_score
FROM entity_licenses
ORDER BY license_count DESC;
```

### 2.6 Effort Estimate

| Task | Effort | Priority |
|---|---|---|
| METRC tag → license linking investigation + implementation | 6 hrs | P1 |
| `mv_cultivator_quality` materialized view | 4 hrs | P1 |
| Same-entity detection (address matching) | 4 hrs | P1 |
| `supply_chain_links` table + inference pipeline | 8 hrs | P1 |
| `mv_markup_analysis` view | 3 hrs | P1 |
| Entity graph (multi-brand detection) | 4 hrs | P1 |
| Brand → manufacturer → retailer linking | 6 hrs | P2 |
| **Total** | **35 hrs** | |

---

## 3. Competitive Radius Analysis

### 3.1 Data Available

- **Operators**: 473 with lat/lon coordinates (geocoded)
- **CCC Licenses**: 772 with latitude/longitude
- **Products/Prices**: per-operator product assortment and pricing
- **Canonical Products** (from Section 1): cross-store product identity

### 3.2 Schema

```sql
-- ============================================================
-- COMPETITIVE RADIUS — Pre-computed competitive landscapes
-- ============================================================
CREATE TABLE competitor_pairs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  competitor_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  
  -- Distance
  distance_miles DECIMAL(6, 2) NOT NULL,
  
  -- Product overlap (requires canonical_products)
  shared_canonical_count INTEGER,              -- products both carry
  operator_only_count INTEGER,                 -- products only operator has
  competitor_only_count INTEGER,               -- products only competitor has
  overlap_pct DECIMAL(5, 2),                   -- shared / union * 100
  
  -- Price positioning (for shared products)
  avg_price_delta DECIMAL(10, 2),              -- operator avg - competitor avg (positive = operator is higher)
  avg_price_delta_pct DECIMAL(6, 2),           -- percentage difference
  cheaper_count INTEGER,                       -- products where operator is cheaper
  pricier_count INTEGER,                       -- products where operator is pricier
  same_price_count INTEGER,
  
  -- Category comparison
  operator_category_mix JSONB,                 -- {"flower": 45, "vape": 30, ...} (% of assortment)
  competitor_category_mix JSONB,
  
  -- Freshness
  calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  
  CONSTRAINT uq_competitor_pair UNIQUE (operator_id, competitor_id)
);

CREATE INDEX idx_competitor_pairs_operator ON competitor_pairs (operator_id);
CREATE INDEX idx_competitor_pairs_distance ON competitor_pairs (operator_id, distance_miles);
CREATE INDEX idx_competitor_pairs_overlap ON competitor_pairs (operator_id, overlap_pct DESC);
```

### 3.3 Computation Pipeline

```sql
-- Step 1: Compute all competitor pairs within 15 miles
INSERT INTO competitor_pairs (operator_id, competitor_id, distance_miles)
SELECT 
  a.id AS operator_id,
  b.id AS competitor_id,
  ROUND(
    3959 * acos(
      LEAST(1, GREATEST(-1,
        cos(radians(a.lat::double precision)) 
        * cos(radians(b.lat::double precision))
        * cos(radians(b.lon::double precision) - radians(a.lon::double precision))
        + sin(radians(a.lat::double precision)) 
        * sin(radians(b.lat::double precision))
      ))
    )::DECIMAL, 2
  ) AS distance_miles
FROM operators a
CROSS JOIN operators b
WHERE a.id != b.id
  AND a.lat IS NOT NULL AND a.lon IS NOT NULL
  AND b.lat IS NOT NULL AND b.lon IS NOT NULL
  AND a.status = 'active'
  AND b.status = 'active'
  -- Bounding box pre-filter (rough ~15 mile lat/lon box)
  AND ABS(a.lat::double precision - b.lat::double precision) < 0.22
  AND ABS(a.lon::double precision - b.lon::double precision) < 0.28
ON CONFLICT (operator_id, competitor_id) DO UPDATE
SET distance_miles = EXCLUDED.distance_miles, calculated_at = NOW()
-- Post-filter: exact distance < 15 miles
HAVING distance_miles <= 15;

-- Step 2: Product overlap (requires product matching from Section 1)
UPDATE competitor_pairs cp SET
  shared_canonical_count = overlap.shared,
  operator_only_count = overlap.op_only,
  competitor_only_count = overlap.comp_only,
  overlap_pct = CASE WHEN overlap.total > 0 
    THEN ROUND(overlap.shared::DECIMAL / overlap.total * 100, 1) ELSE 0 END,
  calculated_at = NOW()
FROM (
  SELECT 
    cp2.operator_id,
    cp2.competitor_id,
    COUNT(*) FILTER (WHERE op_has AND comp_has) AS shared,
    COUNT(*) FILTER (WHERE op_has AND NOT comp_has) AS op_only,
    COUNT(*) FILTER (WHERE NOT op_has AND comp_has) AS comp_only,
    COUNT(*) AS total
  FROM competitor_pairs cp2
  CROSS JOIN LATERAL (
    SELECT 
      pm.canonical_product_id,
      EXISTS(
        SELECT 1 FROM product_matches pm2 
        JOIN prices pr ON pr.product_id = pm2.product_id 
        WHERE pm2.canonical_product_id = pm.canonical_product_id 
          AND pr.operator_id = cp2.operator_id
      ) AS op_has,
      EXISTS(
        SELECT 1 FROM product_matches pm3 
        JOIN prices pr2 ON pr2.product_id = pm3.product_id 
        WHERE pm3.canonical_product_id = pm.canonical_product_id 
          AND pr2.operator_id = cp2.competitor_id
      ) AS comp_has
    FROM product_matches pm
    JOIN prices pr ON pr.product_id = pm.product_id
    WHERE pr.operator_id IN (cp2.operator_id, cp2.competitor_id)
    GROUP BY pm.canonical_product_id
  ) overlap_data
  GROUP BY cp2.operator_id, cp2.competitor_id
) overlap
WHERE cp.operator_id = overlap.operator_id 
  AND cp.competitor_id = overlap.competitor_id;

-- Step 3: Price positioning for shared products
UPDATE competitor_pairs cp SET
  avg_price_delta = pricing.delta,
  avg_price_delta_pct = pricing.delta_pct,
  cheaper_count = pricing.cheaper,
  pricier_count = pricing.pricier,
  same_price_count = pricing.same_price
FROM (
  SELECT 
    cp2.operator_id,
    cp2.competitor_id,
    ROUND(AVG(op_price.latest_price - comp_price.latest_price), 2) AS delta,
    ROUND(AVG((op_price.latest_price - comp_price.latest_price) 
      / NULLIF(comp_price.latest_price, 0) * 100), 1) AS delta_pct,
    COUNT(*) FILTER (WHERE op_price.latest_price < comp_price.latest_price) AS cheaper,
    COUNT(*) FILTER (WHERE op_price.latest_price > comp_price.latest_price) AS pricier,
    COUNT(*) FILTER (WHERE op_price.latest_price = comp_price.latest_price) AS same_price
  FROM competitor_pairs cp2
  JOIN LATERAL (
    -- Latest price per canonical product for operator
    SELECT pm.canonical_product_id, pr.price AS latest_price
    FROM product_matches pm
    JOIN prices pr ON pr.product_id = pm.product_id AND pr.operator_id = cp2.operator_id
    WHERE pr.scraped_at = (
      SELECT MAX(pr2.scraped_at) FROM prices pr2 
      WHERE pr2.product_id = pm.product_id AND pr2.operator_id = cp2.operator_id
    )
  ) op_price ON TRUE
  JOIN LATERAL (
    -- Latest price per canonical product for competitor
    SELECT pm.canonical_product_id, pr.price AS latest_price
    FROM product_matches pm
    JOIN prices pr ON pr.product_id = pm.product_id AND pr.operator_id = cp2.competitor_id
    WHERE pr.scraped_at = (
      SELECT MAX(pr2.scraped_at) FROM prices pr2 
      WHERE pr2.product_id = pm.product_id AND pr2.operator_id = cp2.competitor_id
    )
    AND pm.canonical_product_id = op_price.canonical_product_id
  ) comp_price ON TRUE
  GROUP BY cp2.operator_id, cp2.competitor_id
) pricing
WHERE cp.operator_id = pricing.operator_id 
  AND cp.competitor_id = pricing.competitor_id;
```

### 3.4 API Endpoints

```typescript
// GET /api/v1/operators/:id/competitors
// Returns sorted list of competitors within radius
interface CompetitorResponse {
  competitors: {
    operator_id: string;
    name: string;
    distance_miles: number;
    shared_products: number;
    overlap_pct: number;
    price_position: 'cheaper' | 'similar' | 'pricier';
    avg_price_delta_pct: number;
    category_comparison: {
      category: string;
      your_count: number;
      their_count: number;
    }[];
  }[];
  radius_summary: {
    total_competitors: number;
    avg_distance: number;
    you_are_cheapest_for: number;  // products
    you_are_priciest_for: number;
    biggest_price_gap: {
      product_name: string;
      your_price: number;
      competitor_price: number;
      delta_pct: number;
    };
  };
}

// GET /api/v1/operators/:id/competitors/:competitor_id/comparison
// Deep dive: product-by-product price comparison
```

### 3.5 Effort Estimate

| Task | Effort | Priority |
|---|---|---|
| Distance computation + `competitor_pairs` table | 4 hrs | P0 |
| Product overlap computation | 6 hrs | P1 (depends on product matching) |
| Price positioning computation | 4 hrs | P1 |
| Category mix comparison | 2 hrs | P1 |
| Competitor API endpoints | 6 hrs | P1 |
| Refresh pipeline (daily) | 3 hrs | P1 |
| **Total** | **25 hrs** | |

---

## 4. Demand Intelligence

### 4.1 Data Source: Virtual Budtender

The Virtual Budtender (VB) captures natural language queries from dispensary website visitors. The schema already exists:

- **`budtender_sessions`**: session-level data (tenant, timestamps, device)
- **`budtender_queries`**: individual queries with parsed intent and recommendations
- **`demand_signals`**: aggregated demand bucketed by category/goal/experience/budget/period
- **`vb_tenants`**: tenant configuration

**Current state:** Tables exist but are **mostly empty** (VB hasn't launched at scale). This section designs the intelligence layer that activates once data flows.

### 4.2 Query Intent Parsing

The `parsed_intent` JSONB field in `budtender_queries` should capture structured demand signals:

```typescript
interface ParsedIntent {
  // What they want
  category: string | null;        // "flower", "edible", "vape", etc.
  subcategory: string | null;     // "gummy", "cartridge", "pre-roll"
  strain_type: string | null;     // "indica", "sativa", "hybrid"
  specific_strain: string | null; // "Blue Dream", "OG Kush"
  specific_brand: string | null;  // "Fernway", "Jeeter"
  
  // Context
  goal: string | null;            // "sleep", "pain", "relaxation", "energy", "creativity"
  experience_level: string | null;// "beginner", "intermediate", "experienced"
  
  // Budget signals
  budget_range: string | null;    // "under_20", "20_40", "40_60", "60_plus"
  price_sensitive: boolean;       // mentioned price/deal/cheap/affordable
  
  // Product attributes
  potency_preference: string | null;  // "low", "medium", "high"
  consumption_method: string | null;  // "smoke", "vape", "eat", "topical"
  
  // Match outcome
  matched_to_inventory: boolean;  // did we find something they asked for?
  gap_detected: boolean;          // asked for something not in stock
  gap_detail: string | null;      // what specifically was missing
}
```

### 4.3 Demand Aggregation Pipeline

```sql
-- ============================================================
-- DEMAND AGGREGATION — Materialized from VB queries
-- ============================================================
CREATE MATERIALIZED VIEW mv_demand_signals AS
WITH parsed AS (
  SELECT 
    bq.tenant_id,
    bs.operator_id,
    bq.created_at,
    bq.parsed_intent->>'category' AS category,
    bq.parsed_intent->>'specific_brand' AS brand,
    bq.parsed_intent->>'goal' AS goal,
    bq.parsed_intent->>'strain_type' AS strain_type,
    bq.parsed_intent->>'budget_range' AS budget_range,
    (bq.parsed_intent->>'matched_to_inventory')::boolean AS matched,
    (bq.parsed_intent->>'gap_detected')::boolean AS gap,
    bq.parsed_intent->>'gap_detail' AS gap_detail,
    jsonb_array_length(COALESCE(bq.products_clicked, '[]'::jsonb)) > 0 AS converted
  FROM budtender_queries bq
  JOIN budtender_sessions bs ON bs.id = bq.session_id
  WHERE bq.parsed_intent IS NOT NULL
)
SELECT 
  operator_id,
  DATE_TRUNC('week', created_at) AS week,
  category,
  brand,
  goal,
  strain_type,
  budget_range,
  COUNT(*) AS query_count,
  COUNT(*) FILTER (WHERE converted) AS conversion_count,
  COUNT(*) FILTER (WHERE gap) AS gap_count,
  ROUND(COUNT(*) FILTER (WHERE converted)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 1) AS conversion_rate,
  ROUND(COUNT(*) FILTER (WHERE gap)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 1) AS gap_rate
FROM parsed
GROUP BY operator_id, DATE_TRUNC('week', created_at), category, brand, goal, strain_type, budget_range;

-- ============================================================
-- GAP ANALYSIS — What customers ask for but store doesn't stock
-- ============================================================
CREATE TABLE demand_gaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  
  -- What's missing
  gap_type VARCHAR(30) NOT NULL,     -- 'brand', 'category', 'strain', 'price_point', 'product_type'
  gap_value VARCHAR(255) NOT NULL,   -- "Jeeter", "edibles under $20", "Blue Dream"
  
  -- Evidence
  query_count INTEGER NOT NULL,       -- how many times asked for
  unique_sessions INTEGER NOT NULL,   -- distinct sessions
  time_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
  time_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
  
  -- Context
  nearest_match VARCHAR(255),         -- closest thing in stock
  competitors_stocking JSONB,         -- [{"operator_id": "...", "name": "...", "price": 45}]
  estimated_revenue DECIMAL(10, 2),   -- query_count × avg_price × est_conversion
  
  -- Resolution
  status VARCHAR(20) NOT NULL DEFAULT 'open', -- 'open', 'stocked', 'dismissed'
  resolved_at TIMESTAMP WITH TIME ZONE,
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_demand_gaps_operator ON demand_gaps (operator_id);
CREATE INDEX idx_demand_gaps_type ON demand_gaps (gap_type);
CREATE INDEX idx_demand_gaps_revenue ON demand_gaps (estimated_revenue DESC);
CREATE INDEX idx_demand_gaps_status ON demand_gaps (status);
```

### 4.4 Search-to-Stock Ratio

```sql
-- For each operator: what % of demand is satisfied by current inventory?
-- This becomes a key operator health metric

CREATE OR REPLACE FUNCTION compute_search_to_stock(p_operator_id UUID)
RETURNS TABLE (
  category VARCHAR,
  total_queries BIGINT,
  matched_queries BIGINT,
  stock_ratio DECIMAL,
  top_gaps TEXT[]
) AS $$
SELECT 
  COALESCE(pi->>'category', 'unknown') AS category,
  COUNT(*) AS total_queries,
  COUNT(*) FILTER (WHERE (pi->>'matched_to_inventory')::boolean = true) AS matched_queries,
  ROUND(
    COUNT(*) FILTER (WHERE (pi->>'matched_to_inventory')::boolean = true)::DECIMAL 
    / NULLIF(COUNT(*), 0) * 100, 1
  ) AS stock_ratio,
  ARRAY_AGG(DISTINCT pi->>'gap_detail') FILTER (
    WHERE pi->>'gap_detail' IS NOT NULL
  ) AS top_gaps
FROM budtender_queries bq
JOIN budtender_sessions bs ON bs.id = bq.session_id
CROSS JOIN LATERAL (SELECT bq.parsed_intent AS pi) intent
WHERE bs.operator_id = p_operator_id
  AND bq.created_at > NOW() - INTERVAL '30 days'
GROUP BY COALESCE(pi->>'category', 'unknown')
ORDER BY COUNT(*) DESC;
$$ LANGUAGE SQL STABLE;
```

### 4.5 Seasonal Pattern Detection

```sql
-- Weekly demand trends by category (requires 6+ months of data)
SELECT 
  EXTRACT(WEEK FROM created_at) AS week_of_year,
  COALESCE(parsed_intent->>'category', 'unknown') AS category,
  COUNT(*) AS queries,
  -- Compare to rolling average
  COUNT(*) - AVG(COUNT(*)) OVER (
    PARTITION BY COALESCE(parsed_intent->>'category', 'unknown')
    ORDER BY EXTRACT(WEEK FROM created_at)
    ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
  ) AS deviation_from_trend
FROM budtender_queries bq
JOIN budtender_sessions bs ON bs.id = bq.session_id
WHERE bq.parsed_intent IS NOT NULL
GROUP BY 1, 2
ORDER BY 1, 2;

-- Holiday/event demand spikes
-- Cannabis demand typically spikes: 4/20, Memorial Day, July 4th, Labor Day, Thanksgiving-Christmas
```

### 4.6 Effort Estimate

| Task | Effort | Priority |
|---|---|---|
| Query intent parser (NLP integration) | 12 hrs | P2 (VB must launch first) |
| `mv_demand_signals` materialized view | 3 hrs | P2 |
| Gap analysis pipeline + `demand_gaps` table | 8 hrs | P2 |
| Search-to-stock computation | 4 hrs | P2 |
| Seasonal pattern detection | 4 hrs | P3 (needs 6+ months data) |
| Demand API endpoints | 6 hrs | P2 |
| **Total** | **37 hrs** | |

---

## 5. Pricing Intelligence

### 5.1 Price Change Detection

The challenge: scraper runs daily, and raw price data has noise (rounding, availability changes, scraper errors). We need to distinguish **real price changes** from **noise**.

```sql
-- ============================================================
-- PRICE EVENTS — Significant price changes detected by pipeline
-- ============================================================
CREATE TABLE price_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- What changed
  product_id UUID NOT NULL REFERENCES products(id),
  canonical_product_id UUID REFERENCES canonical_products(id),
  operator_id UUID NOT NULL REFERENCES operators(id),
  
  -- Change details
  event_type VARCHAR(30) NOT NULL,         -- 'price_drop', 'price_increase', 'new_product', 'delisted', 'promo_start', 'promo_end'
  old_price DECIMAL(10, 2),
  new_price DECIMAL(10, 2),
  change_amount DECIMAL(10, 2),             -- new - old
  change_pct DECIMAL(6, 2),                 -- change as percentage
  
  -- Context
  category VARCHAR(50),
  brand VARCHAR(255),
  
  -- Significance scoring
  significance_score DECIMAL(3, 2) NOT NULL, -- 0.00–1.00
  is_significant BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Market context at time of event
  market_avg_price DECIMAL(10, 2),          -- category avg at event time
  competitor_avg_price DECIMAL(10, 2),      -- avg within 10 miles
  
  detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_price_events_operator ON price_events (operator_id);
CREATE INDEX idx_price_events_product ON price_events (product_id);
CREATE INDEX idx_price_events_canonical ON price_events (canonical_product_id);
CREATE INDEX idx_price_events_type ON price_events (event_type);
CREATE INDEX idx_price_events_detected ON price_events (detected_at);
CREATE INDEX idx_price_events_significant ON price_events (is_significant) WHERE is_significant = TRUE;
CREATE INDEX idx_price_events_operator_detected ON price_events (operator_id, detected_at);
```

### 5.2 Significance Scoring Algorithm

```typescript
// price-change-detector.ts

interface PriceChangeCandidate {
  product_id: string;
  operator_id: string;
  old_price: number;
  new_price: number;
  old_scraped_at: Date;
  new_scraped_at: Date;
  category: string;
  brand: string | null;
}

function scorePriceChange(change: PriceChangeCandidate, context: MarketContext): number {
  const changePct = Math.abs(change.new_price - change.old_price) / change.old_price;
  
  let score = 0;
  
  // Factor 1: Magnitude (weight: 0.30)
  // < 2% change → noise (likely rounding)
  // 2-5% → minor adjustment
  // 5-15% → significant
  // > 15% → major
  if (changePct < 0.02) score += 0;
  else if (changePct < 0.05) score += 0.10;
  else if (changePct < 0.15) score += 0.25;
  else score += 0.30;
  
  // Factor 2: Persistence (weight: 0.25)
  // Price held for 2+ consecutive scrapes = confirmed
  // Only seen once = might be error
  if (context.confirmedBySubsequentScrape) score += 0.25;
  else score += 0.05; // provisional
  
  // Factor 3: Product importance (weight: 0.20)
  // High-volume SKU at many stores → more significant
  if (context.storeCount > 20) score += 0.20;
  else if (context.storeCount > 5) score += 0.15;
  else score += 0.05; // niche product
  
  // Factor 4: Market deviation (weight: 0.15)
  // Does this price now deviate from market average?
  const newDeviation = Math.abs(change.new_price - context.marketAvgPrice) / context.marketAvgPrice;
  if (newDeviation > 0.30) score += 0.15; // now 30%+ off market
  else if (newDeviation > 0.15) score += 0.10;
  else score += 0.05;
  
  // Factor 5: Scraper confidence (weight: 0.10)
  if (context.scrapeConfidence >= 0.9) score += 0.10;
  else if (context.scrapeConfidence >= 0.7) score += 0.07;
  else score += 0.02;
  
  return Math.min(1.0, score);
}

// A price change is "significant" if score >= 0.50
// This filters out scraper noise, rounding, and one-off glitches
```

### 5.3 Coordinated Pricing Detection

Detect when multiple operators change prices on the same product in the same direction within a short window:

```sql
-- Coordinated pricing: 3+ operators change the same canonical product 
-- in the same direction within 48 hours
CREATE TABLE coordinated_price_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_product_id UUID NOT NULL REFERENCES canonical_products(id),
  
  -- Pattern
  direction VARCHAR(10) NOT NULL,           -- 'up' or 'down'
  operator_count INTEGER NOT NULL,           -- how many moved together
  avg_change_pct DECIMAL(6, 2) NOT NULL,
  
  -- Participants
  operators JSONB NOT NULL,                  -- [{operator_id, name, old_price, new_price, detected_at}]
  
  -- Timing
  window_start TIMESTAMP WITH TIME ZONE NOT NULL,
  window_end TIMESTAMP WITH TIME ZONE NOT NULL,
  
  -- Analysis
  likely_cause VARCHAR(50),                  -- 'wholesale_change', 'brand_msrp', 'market_pressure', 'unknown'
  
  detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Detection query (run daily)
WITH recent_changes AS (
  SELECT 
    pe.canonical_product_id,
    pe.operator_id,
    o.name AS operator_name,
    pe.old_price,
    pe.new_price,
    pe.change_pct,
    CASE WHEN pe.change_pct > 0 THEN 'up' ELSE 'down' END AS direction,
    pe.detected_at
  FROM price_events pe
  JOIN operators o ON o.id = pe.operator_id
  WHERE pe.is_significant = TRUE
    AND pe.detected_at > NOW() - INTERVAL '48 hours'
    AND pe.canonical_product_id IS NOT NULL
),
coordinated AS (
  SELECT 
    canonical_product_id,
    direction,
    COUNT(DISTINCT operator_id) AS operator_count,
    ROUND(AVG(change_pct), 2) AS avg_change_pct,
    MIN(detected_at) AS window_start,
    MAX(detected_at) AS window_end,
    jsonb_agg(jsonb_build_object(
      'operator_id', operator_id,
      'name', operator_name,
      'old_price', old_price,
      'new_price', new_price,
      'detected_at', detected_at
    )) AS operators
  FROM recent_changes
  GROUP BY canonical_product_id, direction
  HAVING COUNT(DISTINCT operator_id) >= 3
)
INSERT INTO coordinated_price_events 
  (canonical_product_id, direction, operator_count, avg_change_pct, operators, window_start, window_end)
SELECT * FROM coordinated;
```

### 5.4 Arbitrage Opportunity Detection

For operators: find products they sell at significantly different prices than nearby competitors.

```sql
-- Arbitrage opportunities for a given operator
CREATE OR REPLACE FUNCTION find_arbitrage_opportunities(
  p_operator_id UUID,
  p_radius_miles DECIMAL DEFAULT 10,
  p_min_delta_pct DECIMAL DEFAULT 10
)
RETURNS TABLE (
  canonical_product_name VARCHAR,
  brand VARCHAR,
  category VARCHAR,
  your_price DECIMAL,
  cheapest_competitor_price DECIMAL,
  cheapest_competitor_name VARCHAR,
  price_delta DECIMAL,
  delta_pct DECIMAL,
  competitor_count INTEGER,
  opportunity_type VARCHAR  -- 'you_are_high' or 'you_are_low'
) AS $$
WITH competitor_ids AS (
  SELECT competitor_id 
  FROM competitor_pairs 
  WHERE operator_id = p_operator_id 
    AND distance_miles <= p_radius_miles
),
your_prices AS (
  SELECT 
    cp.id AS canonical_id,
    cp.name AS product_name,
    cp.brand,
    cp.category,
    pr.price AS your_price
  FROM product_matches pm
  JOIN prices pr ON pr.product_id = pm.product_id
  JOIN canonical_products cp ON cp.id = pm.canonical_product_id
  WHERE pr.operator_id = p_operator_id
    AND pr.scraped_at = (
      SELECT MAX(scraped_at) FROM prices WHERE product_id = pm.product_id AND operator_id = p_operator_id
    )
),
competitor_prices AS (
  SELECT 
    pm.canonical_product_id,
    MIN(pr.price) AS cheapest_price,
    (ARRAY_AGG(o.name ORDER BY pr.price))[1] AS cheapest_name,
    COUNT(DISTINCT pr.operator_id) AS comp_count
  FROM product_matches pm
  JOIN prices pr ON pr.product_id = pm.product_id
  JOIN operators o ON o.id = pr.operator_id
  WHERE pr.operator_id IN (SELECT competitor_id FROM competitor_ids)
    AND pr.scraped_at > NOW() - INTERVAL '7 days'
  GROUP BY pm.canonical_product_id
)
SELECT 
  yp.product_name,
  yp.brand,
  yp.category,
  yp.your_price,
  cp.cheapest_price,
  cp.cheapest_name,
  yp.your_price - cp.cheapest_price AS price_delta,
  ROUND((yp.your_price - cp.cheapest_price) / NULLIF(cp.cheapest_price, 0) * 100, 1) AS delta_pct,
  cp.comp_count,
  CASE WHEN yp.your_price > cp.cheapest_price THEN 'you_are_high' ELSE 'you_are_low' END
FROM your_prices yp
JOIN competitor_prices cp ON cp.canonical_product_id = yp.canonical_id
WHERE ABS(yp.your_price - cp.cheapest_price) / NULLIF(cp.cheapest_price, 0) * 100 >= p_min_delta_pct
ORDER BY ABS(yp.your_price - cp.cheapest_price) DESC;
$$ LANGUAGE SQL STABLE;
```

### 5.5 Promotional Pattern Recognition

```sql
-- Detect recurring promotions (weekly sales, monthly specials)
CREATE TABLE promotional_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id),
  
  -- Pattern
  pattern_type VARCHAR(30) NOT NULL,         -- 'weekly_drop', 'monthly_sale', 'category_rotation', 'new_product_intro'
  day_of_week INTEGER,                        -- 0=Sunday for weekly patterns
  week_of_month INTEGER,                      -- 1-4 for monthly patterns
  
  -- What's affected
  category VARCHAR(50),
  brand VARCHAR(255),
  canonical_product_id UUID,
  
  -- Pattern details
  avg_discount_pct DECIMAL(5, 2),
  occurrences INTEGER NOT NULL,               -- how many times observed
  last_occurred TIMESTAMP WITH TIME ZONE,
  next_predicted TIMESTAMP WITH TIME ZONE,
  
  confidence DECIMAL(3, 2) NOT NULL,
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_promo_patterns_operator ON promotional_patterns (operator_id);
CREATE INDEX idx_promo_patterns_type ON promotional_patterns (pattern_type);
```

### 5.6 Effort Estimate

| Task | Effort | Priority |
|---|---|---|
| Price change detection pipeline | 8 hrs | P0 |
| Significance scoring algorithm | 4 hrs | P0 |
| `price_events` table + daily pipeline | 6 hrs | P0 |
| Coordinated pricing detection | 4 hrs | P1 |
| Arbitrage opportunity function | 4 hrs | P1 |
| Promotional pattern recognition | 8 hrs | P2 |
| **Total** | **34 hrs** | |

---

## 6. Monetization Beyond $199/mo

### 6.1 Revenue Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GLASS REVENUE TIERS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TIER 1: Free/Public (Lead Gen)                $0/mo           │
│  ├── Market page (aggregated stats)                             │
│  ├── State-level price index                                    │
│  ├── CCC data summary                                           │
│  └── Newsletter signup                                          │
│                                                                 │
│  TIER 2: Operator Dashboard               $199/mo              │
│  ├── Store Report Card                                          │
│  ├── Price Wire (competitor prices)                             │
│  ├── Threat Radar (CCC alerts)                                  │
│  ├── Basic competitive radius                                   │
│  └── 1 store                                                    │
│                                                                 │
│  TIER 3: Multi-Store / Pro               $499/mo               │
│  ├── Everything in Tier 2                                       │
│  ├── Up to 5 stores                                             │
│  ├── Portfolio view                                             │
│  ├── Price change alerts (push/email/SMS)                       │
│  ├── Arbitrage opportunities                                    │
│  ├── Product gap analysis                                       │
│  └── Competitive radius deep-dive                               │
│                                                                 │
│  TIER 4: Enterprise                      $999-$2,499/mo        │
│  ├── Everything in Pro                                          │
│  ├── Unlimited stores                                           │
│  ├── API access                                                 │
│  ├── Custom reports                                             │
│  ├── Supply chain intelligence                                  │
│  ├── Promotional pattern detection                              │
│  └── Dedicated support                                          │
│                                                                 │
│  TIER 5: Brand Intelligence              $299-$999/mo          │
│  ├── Brand performance across all 490 stores                    │
│  ├── Shelf placement tracking                                   │
│  ├── Price consistency monitoring                               │
│  ├── Competitor brand analysis                                  │
│  ├── Retailer penetration map                                   │
│  └── Demand signals for your brand                              │
│                                                                 │
│  TIER 6: Market Reports (one-time)       $500-$5,000           │
│  ├── Custom market analysis                                     │
│  ├── Category deep-dives                                        │
│  ├── Competitive landscape report                               │
│  ├── Market entry analysis                                      │
│  └── White-label for consultants                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Brand Intelligence Platform (New Revenue Line)

**Target market:** Cannabis brands and manufacturers selling through MA dispensaries  
**Value prop:** "See exactly how your products are priced, positioned, and performing across every dispensary in Massachusetts"

This is a different buyer than the dispensary operator. Brands care about:

| Feature | Why Brands Pay | Data Source |
|---|---|---|
| Price consistency monitoring | MAP violations, unauthorized discounting | `canonical_products` + `prices` |
| Retailer penetration map | Which stores carry us? Which don't? | `product_matches` + `operators` |
| Competitive shelf share | Our products vs competitor brands by store | `canonical_products` by brand |
| Price positioning vs competitors | Are we priced right category-wide? | `canonical_products` + market avg |
| Demand signals | What customers ask for (via VB) | `budtender_queries` |
| Promotional detection | Are retailers discounting our products? | `price_events` |

**Schema addition for brand accounts:**

```sql
CREATE TABLE brand_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_dictionary_id UUID NOT NULL REFERENCES brand_dictionary(id),
  
  -- Account info
  company_name VARCHAR(255) NOT NULL,
  contact_email VARCHAR(255) NOT NULL,
  contact_name VARCHAR(255),
  
  -- Subscription
  plan VARCHAR(30) NOT NULL DEFAULT 'basic',  -- 'basic', 'pro', 'enterprise'
  stripe_customer_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255),
  subscription_status VARCHAR(30) NOT NULL DEFAULT 'trial',
  
  -- Access control
  brands_tracked JSONB NOT NULL DEFAULT '[]',  -- brand_dictionary_ids they can see
  competitor_brands JSONB DEFAULT '[]',        -- competitor brands they want compared
  
  -- API
  api_key VARCHAR(100) UNIQUE,
  api_calls_monthly INTEGER NOT NULL DEFAULT 0,
  api_limit_monthly INTEGER NOT NULL DEFAULT 1000,
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

**Brand dashboard features:**

```typescript
// GET /api/v1/brands/:brand_id/distribution
interface BrandDistribution {
  total_stores_carrying: number;
  total_stores_in_state: number;
  penetration_pct: number;
  by_region: {
    region: string;
    stores_carrying: number;
    total_stores: number;
    penetration_pct: number;
  }[];
  by_category: {
    category: string;
    product_count: number;
    avg_price: number;
    price_range: { min: number; max: number };
  }[];
  price_consistency: {
    target_price: number | null;
    avg_retail_price: number;
    min_retail_price: number;
    max_retail_price: number;
    stores_above_target: number;
    stores_below_target: number;
    price_variance_pct: number;
  };
}

// GET /api/v1/brands/:brand_id/competitive-position
interface BrandCompetitivePosition {
  market_share_estimate: {
    category: string;
    your_store_count: number;
    total_stores_with_category: number;
    share_pct: number;
  }[];
  vs_competitors: {
    competitor_brand: string;
    their_store_count: number;
    your_store_count: number;
    stores_both: number;
    stores_only_you: number;
    stores_only_them: number;
    avg_price_delta: number;
  }[];
}
```

### 6.3 Cultivator Intelligence (Supply-Side Monetization)

**Target:** Licensed cultivators want to know which retailers to approach, quality benchmarking, and market pricing.

| Feature | Price Point | Data |
|---|---|---|
| Quality ranking vs other cultivators | $299/mo | `mv_cultivator_quality` |
| Retailer relationship mapping | $299/mo | `supply_chain_links` |
| Wholesale-to-retail markup by retailer | $499/mo | `mv_markup_analysis` |
| Lab test trend reports | $199/mo | `ccc_lab_tests` |

### 6.4 API Licensing

```
API Access Tiers:
├── Starter:  1,000 calls/mo  — $99/mo   (read-only, aggregated data)
├── Pro:      10,000 calls/mo — $499/mo  (product-level, real-time)
├── Enterprise: 100,000+      — Custom   (raw data, webhooks)
```

**API endpoints worth licensing:**

```
/api/v1/market/prices          — Current prices by category/region
/api/v1/market/trends          — Price trends over time
/api/v1/products/:id/prices    — All prices for a canonical product
/api/v1/operators/:id/products — Full product catalog for a store
/api/v1/brands/:name/presence  — Where a brand is sold + at what prices
/api/v1/market/reports/:month  — Monthly market summary
```

### 6.5 Aggregated Market Reports

**Monthly/Quarterly PDF reports:** sold to investors, consultants, law firms, and new market entrants.

| Report | Price | Content |
|---|---|---|
| MA Cannabis Market Overview | $500 | Price trends, category mix, new entrants, regulatory |
| Category Deep Dive (e.g., Vapes) | $750 | Brand rankings, price distribution, demand trends |
| Competitive Landscape (specific region) | $1,000 | Store-by-store comparison, gaps, opportunities |
| Market Entry Analysis | $2,500-$5,000 | Custom analysis for operators planning to open |
| Annual Market Report | $2,500 | Comprehensive yearly review |

### 6.6 White-Label Data

License GLASS data/analysis to:
- **Consultants** helping operators with pricing strategy
- **POS/ERP companies** wanting market benchmarks in their dashboards
- **Compliance platforms** wanting competitive pricing context
- **Cannabis media** wanting verified market data

### 6.7 Revenue Model Projections

| Revenue Line | Year 1 Target | Rationale |
|---|---|---|
| Operator subscriptions ($199-$499/mo) | $36,000 | 15 operators × $200/mo avg |
| Brand intelligence ($299-$999/mo) | $18,000 | 5 brands × $300/mo avg |
| Market reports | $10,000 | 10 reports × $1,000 avg |
| API licensing | $6,000 | 5 API customers × $100/mo avg |
| **Year 1 Total** | **$70,000** | |
| **Year 2 Target (with product-market fit)** | **$250,000** | Scale to 50 operators + 20 brands |

### 6.8 Effort Estimate

| Task | Effort | Priority |
|---|---|---|
| Multi-tier subscription backend (Stripe) | 12 hrs | P1 |
| Brand account system + dashboard | 20 hrs | P1 |
| Brand distribution API endpoints | 8 hrs | P1 |
| API key management + rate limiting | 6 hrs | P2 |
| Market report generator (PDF) | 16 hrs | P2 |
| White-label data export system | 8 hrs | P3 |
| **Total** | **70 hrs** | |

---

## 7. Implementation Priority

### Priority Matrix

Ordered by: **Revenue Impact × Feasibility × Speed to Deliver**

```
Priority Score = Revenue_Impact(1-5) × Feasibility(1-5) × (1/Weeks_to_Deliver)

Where:
  Revenue_Impact: How directly this drives subscription revenue
  Feasibility: How buildable with current data/infra
  Weeks_to_Deliver: Calendar time to production
```

### Phase 0: Foundation (Week 1-2) — CRITICAL PATH

**These block everything else.**

| # | Task | Revenue Impact | Feasibility | Weeks | Score | Dependencies |
|---|---|---|---|---|---|---|
| 0.1 | Populate `operator_scores` (run `refresh_health_scores()`) | 5 | 5 | 0.5 | 50.0 | Fix MV bug first |
| 0.2 | Fix MV bug (`ccc_avg_prices` → `ccc_monthly_prices`) | 5 | 5 | 0.1 | 250.0 | None |
| 0.3 | Schedule daily score refresh cron | 4 | 5 | 0.5 | 40.0 | 0.1 |
| 0.4 | Product fingerprint columns + migration | 5 | 5 | 1 | 25.0 | None |

**Total Phase 0: ~25 hours**

### Phase 1: Product Matching MVP (Week 2-4) — THE MOAT

| # | Task | Revenue Impact | Feasibility | Weeks | Score | Dependencies |
|---|---|---|---|---|---|---|
| 1.1 | Brand dictionary bootstrap from existing data | 4 | 5 | 0.5 | 40.0 | None |
| 1.2 | Fingerprint computation for all 100K products | 5 | 4 | 1 | 20.0 | 0.4 |
| 1.3 | Exact fingerprint matching (Stage 1 dedup) | 5 | 5 | 0.5 | 50.0 | 1.2 |
| 1.4 | Similarity scoring within blocks | 5 | 4 | 1.5 | 13.3 | 1.2 |
| 1.5 | Union-Find clustering + canonical product creation | 5 | 4 | 1 | 20.0 | 1.4 |
| 1.6 | Canonical product pricing summary refresh | 5 | 5 | 0.5 | 50.0 | 1.5 |

**Total Phase 1: ~38 hours. Unlocks: cross-store price comparison, competitive overlap, arbitrage.**

### Phase 2: Competitive Intelligence (Week 4-6)

| # | Task | Revenue Impact | Feasibility | Weeks | Score | Dependencies |
|---|---|---|---|---|---|---|
| 2.1 | Distance-based competitor pairs | 4 | 5 | 0.5 | 40.0 | Geocoded operators ✅ |
| 2.2 | Product overlap computation | 5 | 4 | 1 | 20.0 | Phase 1 |
| 2.3 | Price positioning per competitor | 5 | 4 | 0.5 | 40.0 | Phase 1 |
| 2.4 | Competitor API endpoints | 4 | 5 | 1 | 20.0 | 2.1-2.3 |
| 2.5 | Price change detection pipeline | 4 | 5 | 1 | 20.0 | None |
| 2.6 | Arbitrage opportunity detection | 4 | 4 | 0.5 | 32.0 | Phase 1, 2.1 |

**Total Phase 2: ~28 hours. Unlocks: "See what your competitors charge" (the headline promise).**

### Phase 3: Supply Chain + Brand Intelligence (Week 6-10)

| # | Task | Revenue Impact | Feasibility | Weeks | Score | Dependencies |
|---|---|---|---|---|---|---|
| 3.1 | Same-entity detection (multi-license companies) | 3 | 5 | 0.5 | 30.0 | None |
| 3.2 | Cultivator quality rankings | 3 | 4 | 1 | 12.0 | None |
| 3.3 | Wholesale-to-retail markup view | 4 | 4 | 0.5 | 32.0 | None |
| 3.4 | Brand account system | 4 | 4 | 2 | 8.0 | Phase 1 |
| 3.5 | Brand distribution API | 4 | 4 | 1 | 16.0 | Phase 1, 3.4 |
| 3.6 | Brand price consistency monitoring | 3 | 4 | 1 | 12.0 | Phase 1, 3.4 |
| 3.7 | Coordinated pricing detection | 2 | 4 | 0.5 | 16.0 | Phase 1, 2.5 |

**Total Phase 3: ~40 hours. Unlocks: new revenue from brands/cultivators.**

### Phase 4: Demand Intelligence + Advanced (Week 10-16)

| # | Task | Revenue Impact | Feasibility | Weeks | Score | Dependencies |
|---|---|---|---|---|---|---|
| 4.1 | VB query intent parser | 3 | 3 | 2 | 4.5 | VB launch |
| 4.2 | Demand aggregation + gap analysis | 3 | 3 | 1.5 | 6.0 | 4.1 |
| 4.3 | Search-to-stock ratio | 3 | 3 | 1 | 9.0 | 4.1 |
| 4.4 | API key management + rate limiting | 2 | 4 | 1 | 8.0 | None |
| 4.5 | Market report PDF generator | 2 | 3 | 2 | 3.0 | Phases 1-3 |
| 4.6 | Promotional pattern detection | 2 | 3 | 1.5 | 4.0 | 2.5 |
| 4.7 | Seasonal demand patterns | 1 | 2 | 2 | 0.5 | 4.1, 6+ months data |

**Total Phase 4: ~57 hours. Unlocks: demand-driven insights, API revenue.**

### Summary Gantt

```
Week:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
       ├───┤
       Phase 0: Foundation (25h)
           ├───────────┤
           Phase 1: Product Matching (38h)
                       ├───────┤
                       Phase 2: Competitive Intel (28h)
                               ├───────────────┤
                               Phase 3: Supply Chain + Brands (40h)
                                               ├───────────────────────┤
                                               Phase 4: Demand + Advanced (57h)

Total: ~188 hours ≈ 4.7 developer-weeks at 40h/wk
```

### Critical Path

```
Fix MV bug → Populate scores → Product fingerprinting → Exact match dedup
→ Similarity matching → Canonical products → Competitor overlap
→ Price positioning → Competitor API → $$$ REVENUE $$$

Everything downstream of "Canonical products" is revenue-generating.
The single most important thing to build is the product matching engine.
```

---

## Appendix A: Data Quality Notes

### Current Data State (from STATUS-AUDIT and BRAND-CLEANUP-FINAL)

| Metric | Value | Implication |
|---|---|---|
| Products with brand | 37.6% (36,089 / 95,984) | 62% need brand extraction from name |
| Distinct brands | ~700 after cleanup | Manageable brand dictionary |
| Products with weight | ~40% (from quantity field) | Need weight extraction from name for rest |
| Products with THC% | ~35% | Limited THC matching signal |
| Products with strain_type | ~30% | Partial strain matching |
| Operators with lat/lon | ~95% | Good for distance computation |
| CCC licenses matched | 770/772 | Excellent operator-license linkage |
| Weedmaps scraper success | 5.8% | Major data gap — fix scraper to unlock 163 more stores |

### Known Data Issues

1. **SKU collisions:** Current `buildSku()` truncates to 255 chars; two different products can collide if names are long and similar. Not critical for matching (we use product UUID), but affects dedup.

2. **Weight inconsistency:** Some products list weight in `quantity` field in mg (edibles), others in grams (flower). Need category-aware normalization.

3. **THC% from different sources:** Menu THC% (self-reported by retailer) vs lab test THC% (from CCC). The `thc_integrity_score` in operator_scores is designed to compare these, but operator_scores is empty.

4. **Weedmaps data gap:** Only 10/173 Weedmaps stores succeed. Fixing the scraper adds ~163 stores of competitive data.

5. **Price data freshness:** All WoW columns show "New" — daily scraping just started Feb 12. Need 2+ weeks of data for any trend analysis.

---

## Appendix B: SQL Migration Summary

All new tables proposed in this plan:

```sql
-- New tables (6):
-- 1. canonical_products      — cross-store product identity
-- 2. product_matches         — links products to canonicals
-- 3. brand_dictionary        — canonical brand names with aliases
-- 4. matching_runs           — audit trail for matching pipeline
-- 5. supply_chain_links      — cultivator → retailer inferences
-- 6. price_events            — significant price changes

-- New tables for monetization (3):
-- 7. coordinated_price_events — multi-operator price coordination
-- 8. promotional_patterns     — recurring promotion detection
-- 9. brand_accounts           — brand-side subscription accounts

-- New materialized views (3):
-- 10. mv_cultivator_quality    — cultivator quality rankings
-- 11. mv_markup_analysis       — wholesale-to-retail markup
-- 12. mv_entity_graph          — multi-brand entity detection

-- Existing tables modified (1):
-- 13. products                 — add fingerprint columns (norm_brand, norm_name, etc.)

-- Existing tables to populate (1):
-- 14. operator_scores          — run refresh_health_scores()

-- Existing tables ready for data (3, schema exists):
-- 15. demand_gaps              — populate from VB queries
-- 16. demand_signals           — already exists, needs data flow
-- 17. budtender_queries        — already exists, needs parsed_intent population
```

---

## Appendix C: Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Matching engine location | PostgreSQL (pg_trgm + custom functions) | Already in stack, 100K products is tractable in-DB, avoids new infrastructure |
| Union-Find | TypeScript (in matching script) | Too complex for pure SQL, runs as batch job |
| Fingerprint computation | TypeScript (batch job) | Complex string parsing best done in code |
| Competitive radius | PostGIS or Haversine SQL | Haversine already used in `match-operators.ts`, works for MA-scale |
| Materialized view refresh | pg_cron or external cron | Railway supports both; daily refresh sufficient |
| Brand matching | pg_trgm similarity() | Already loaded/used for operator matching |
| Price change detection | TypeScript daily job | Needs significance scoring logic |
| API | Existing Elysia/Hono stack | No new API framework needed |

---

## Appendix D: Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Product matching accuracy < 80% | Medium | High | Start with exact fingerprint (high precision), add similarity gradually. Manual review queue for medium-confidence. |
| Brand extraction from product names fails for 60%+ products | Medium | Medium | Focus matching on branded products first (37.6%). Unbranded products are often house brands (single-store), less critical for cross-store matching. |
| Weedmaps scraper stays broken | High | High | Without 163 more stores, competitive analysis is incomplete for 34% of market. Dedicate engineering time to fix. |
| METRC tag → license number link doesn't work | Medium | Medium | Lab test intelligence degrades but doesn't block core product matching or pricing intel. |
| Data freshness (daily scraping just started) | Low-Medium | Medium | Need 2-4 weeks of daily data before trends are meaningful. Set expectations with users. |
| Performance: 100K×100K pairwise comparison | Low | Medium | Blocking strategy reduces to ~100-200 per block. Largest blocks sub-blocked. Total pairwise < 500K comparisons. |
| Low VB adoption delays demand intelligence | High | Low | Phase 4 is deliberately last. Core value (pricing/competition) doesn't depend on VB. |

---

*End of Data Intelligence Plan*
