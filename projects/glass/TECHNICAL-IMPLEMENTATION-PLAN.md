# GLASS Technical Implementation Plan (90-Day Build)

**Date:** 2026-02-13  
**Owner:** Lead Architect  
**Source Inputs:** `DATA-INTELLIGENCE-PLAN-FINAL.md` + strategic review (Path A + Path B, scraper risk, no Neo4j, TimescaleDB extension, AI-assisted matching)

---

## 1) Execution Objective

Build the **canonical product intelligence layer** first (GPIDs + product matching), then prove commercial value with hand-delivered intelligence reports, then launch a lightweight operator SaaS and flip revenue focus to whale contracts.

**Non-negotiable gate sequence:**
1. Matching precision >= 90% before Month 2 execution
2. Matching precision >= 95% before dashboard automation and scaled SaaS (Month 3)

---

## 2) Locked Architecture Decisions

1. **PostgreSQL is the system of record** (no Neo4j)
2. **Graph traversal via recursive CTEs**
3. **Time-series optimization via TimescaleDB extension only** (same Postgres instance)
4. **Matching pipeline = deterministic + trigram + AI review for 0.45-0.55 band**
5. **False positives are worse than false negatives** (optimize precision)
6. **Path A (operator dashboard) is data QA + distribution; Path B is revenue engine**

---

## 3) Repo + Implementation Lanes

- API service: `/data/workspace/projects/glass/src/services/api`
- Scraping service: `/data/workspace/projects/glass/src/services/scrape`
- SQL migrations folder: `/data/workspace/projects/glass/migrations`

### Codex CLI best-practice execution pattern
- Work in isolated branch/worktree per lane:
  - `matching-engine`
  - `reporting-pdfs`
  - `dashboard-path-a`
- Keep migrations additive and idempotent (`IF NOT EXISTS` where possible)
- Every major step ends with:
  - migration apply
  - backfill script
  - validation query
  - rollback note

---

## 4) Month 1 (107h): Data Sandbox

## Goal
GPIDs generated, matching pipeline running nightly, and quick-win price change intelligence live.

### Week 1 (35h): Foundation + Quick Wins

### Task M1.1 — DB extensions + baseline migration (4h)
Create migration: `migrations/004_matching_foundation.sql`

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_cron;
-- Optional when needed for heavier time-series workloads:
-- CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### Task M1.2 — Products normalization columns (8h)

```sql
ALTER TABLE products ADD COLUMN IF NOT EXISTS norm_brand VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS norm_name VARCHAR(500);
ALTER TABLE products ADD COLUMN IF NOT EXISTS norm_strain VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS weight_bucket VARCHAR(20);
ALTER TABLE products ADD COLUMN IF NOT EXISTS fingerprint_key VARCHAR(512);
ALTER TABLE products ADD COLUMN IF NOT EXISTS canonical_product_id UUID;

CREATE INDEX IF NOT EXISTS idx_products_norm_brand ON products (norm_brand);
CREATE INDEX IF NOT EXISTS idx_products_norm_name_trgm ON products USING gin (norm_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_products_fingerprint ON products (fingerprint_key);
```

### Task M1.3 — Brand dictionary bootstrap (4h)
Seed `brand_dictionary` from existing product brands + known aliases.

### Task M1.4 — Quick-win price change view (8h)
Implement table + view from schema section below and expose “>15% change” feed.

### Task M1.5 — MV bug + operator scores refresh automation (11h)
- Fix `ccc_avg_prices -> ccc_monthly_prices` dependency
- Schedule `refresh_health_scores()` daily using `pg_cron`

```sql
SELECT cron.schedule(
  'refresh-operator-scores-daily',
  '5 6 * * *',
  $$SELECT refresh_health_scores();$$
);
```

---

### Week 2-3 (52h): Matching Engine Core

### Task M1.6 — Deterministic normalization job (8h)
File: `src/scripts/etl/normalize-products.ts`

```ts
function normalizeBrand(input?: string): string {
  if (!input) return 'unknown';
  return input
    .toLowerCase()
    .normalize('NFKD')
    .replace(/\b(inc|llc|co|company|labs?)\b/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function extractWeightGrams(name: string): number | null {
  const n = name.toLowerCase();
  const g = n.match(/(\d+(?:\.\d+)?)\s?g\b/);
  if (g) return Number(g[1]);
  const oz = n.match(/1\/8\s?oz|eighth/);
  if (oz) return 3.5;
  const mg = n.match(/(\d+(?:\.\d+)?)\s?mg\b/);
  if (mg) return Number(mg[1]) / 1000;
  return null;
}
```

### Task M1.7 — Exact fingerprint pass (4h)
Fingerprint pattern: `category|norm_brand|norm_name|weight_bucket`

```sql
WITH exact_groups AS (
  SELECT fingerprint_key, MIN(id) AS anchor_id, COUNT(*) AS cnt
  FROM products
  WHERE fingerprint_key IS NOT NULL
  GROUP BY fingerprint_key
  HAVING COUNT(*) > 1
)
SELECT * FROM exact_groups ORDER BY cnt DESC;
```

### Task M1.8 — Blocking + candidate generation (6h)
Block by `(category, weight_bucket, norm_brand)`; split oversized blocks by name prefix.

```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS match_blocks AS
SELECT
  id AS product_id,
  category,
  COALESCE(weight_bucket, 'unknown') AS weight_bucket,
  COALESCE(norm_brand, 'unknown') AS norm_brand,
  LEFT(COALESCE(norm_name, ''), 8) AS name_prefix
FROM products;

CREATE INDEX IF NOT EXISTS idx_match_blocks_key
  ON match_blocks (category, weight_bucket, norm_brand, name_prefix);
```

### Task M1.9 — Trigram similarity scoring (12h)

```sql
WITH candidates AS (
  SELECT
    p1.id AS product_a,
    p2.id AS product_b,
    similarity(p1.norm_name, p2.norm_name) AS name_sim,
    CASE WHEN p1.norm_brand = p2.norm_brand THEN 1 ELSE 0 END AS brand_sim,
    similarity(COALESCE(p1.norm_strain,''), COALESCE(p2.norm_strain,'')) AS strain_sim,
    CASE
      WHEN p1.weight_grams IS NULL OR p2.weight_grams IS NULL THEN 0.5
      WHEN ABS(p1.weight_grams - p2.weight_grams) <= 0.1 THEN 1
      ELSE 0
    END AS weight_sim,
    CASE
      WHEN p1.thc_percent IS NULL OR p2.thc_percent IS NULL THEN 0.5
      WHEN ABS(p1.thc_percent - p2.thc_percent) <= 2 THEN 1
      WHEN ABS(p1.thc_percent - p2.thc_percent) >= 10 THEN 0
      ELSE 0.5
    END AS thc_sim
  FROM products p1
  JOIN products p2
    ON p1.id < p2.id
   AND p1.category = p2.category
   AND COALESCE(p1.weight_bucket,'unknown') = COALESCE(p2.weight_bucket,'unknown')
   AND COALESCE(p1.norm_brand,'unknown') = COALESCE(p2.norm_brand,'unknown')
)
SELECT
  product_a,
  product_b,
  ROUND((0.35*name_sim + 0.25*brand_sim + 0.20*strain_sim + 0.10*weight_sim + 0.10*thc_sim)::numeric, 4) AS confidence
FROM candidates;
```

### Task M1.10 — AI review band (8h)
Route pairs with **0.45 <= confidence <= 0.55** to low-cost LLM.

**Prompt contract (strict JSON):**

```json
{
  "is_match": true,
  "confidence": 78,
  "reason": "Same brand, same strain, same size; punctuation differences only"
}
```

**Worker behavior:**
- Batch 100 pairs/request
- Model: cheapest reliable JSON mode (Haiku/mini)
- Auto-accept only when `is_match=true AND confidence>=60`
- Else mark `needs_manual_review=true`

Pseudo-code:

```ts
if (pair.confidence >= 0.90) autoMatch('exact_or_high');
else if (pair.confidence >= 0.55) autoMatch('similarity');
else if (pair.confidence >= 0.45) queueAiReview(pair);
else rejectPair();
```

### Task M1.11 — Cluster + GPID assignment (8h)
Use union-find in TS to build connected components from accepted edges.

```ts
const gpid = `GP-${catCode}-${brandHash.slice(0,4)}-${nameHash.slice(0,4)}`;
```

### Task M1.12 — Nightly incremental matcher (6h)
- Input: products added/updated since last run
- Compare only against relevant blocks + existing canonical members
- Save run metrics into `matching_runs`

---

### Week 4 (20h): Validation + Tuning

### Task M1.13 — Human QA sample validation (8h)
- Stratified sample by confidence tier
- Metrics:
  - precision by tier
  - false positive root causes
  - alias misses

### Task M1.14 — Threshold tuning + parser fixes (12h)
- Tune exact/high/medium/AI thresholds
- Update brand alias map
- Improve weight parsing edge cases (e.g., “2x0.5g”, “14g shake”)

**Month 1 exit criteria:**
- >= 90% precision on 1,000 sampled pairs
- Canonical table populated
- GPIDs generated
- Price change views producing daily events

---

## 5) Month 2 (65h): Proof of Magic

## Goal
Convert intelligence into paid trust via hand-delivered reports and whale-grade analytics.

### Task M2.1 — Report data mart views (10h)
Create views for:
- operator price positioning
- product gaps vs nearest competitors
- category-level deltas

### Task M2.2 — PDF report generation pipeline (10h)
Use HTML template + Playwright PDF render (already dependency in repo root).

```ts
// src/scripts/reports/render-operator-report.ts
const html = renderTemplate({ operator, pricing, competitors, opportunities });
await page.setContent(html, { waitUntil: 'networkidle' });
await page.pdf({ path: outPath, format: 'A4', printBackground: true });
```

### Task M2.3 — Cultivator Quality Rankings query (8h)

```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS cultivator_quality_rankings AS
SELECT
  lt.cultivator_name,
  lt.product_category,
  COUNT(*) AS test_count,
  AVG(lt.thc_percent)::numeric(6,2) AS avg_thc,
  STDDEV_POP(lt.thc_percent)::numeric(6,2) AS thc_stddev,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY lt.thc_percent) AS median_thc,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY lt.thc_percent) AS p90_thc,
  GREATEST(0, 1 - (COALESCE(STDDEV_POP(lt.thc_percent),0) / NULLIF(AVG(lt.thc_percent),0)))::numeric(6,4) AS consistency_score
FROM lab_tests lt
WHERE lt.thc_percent IS NOT NULL
GROUP BY lt.cultivator_name, lt.product_category;
```

### Task M2.4 — Brand Distribution Map query (8h)
- `brand -> store_count -> avg_price -> min/max -> map_violations`
- Export CSV + PDF chart blocks

### Task M2.5 — Operator feedback loop into matching engine (9h)
Build a correction endpoint:
- mark match as wrong/right
- store correction in audit table
- include corrections in next matching run as hard rules

### Task M2.6 — Second precision audit (5h)
Gate to Month 3 only if precision >= 95%.

### Task M2.7 — Sales enablement packaging (15h)
- 10 operator PDFs
- 1 market intelligence PDF for whales
- repeatable script to regenerate weekly

**Month 2 exit criteria:**
- 10 report conversations completed
- Cultivator rankings live
- matching precision >= 95%

---

## 6) Month 3 (65h): SaaS Launch + Flip to Whale Contracts

## Goal
Operator dashboard live (Path A) + whale contract conversion engine (Path B).

### Task M3.1 — Dashboard backend APIs (24h)
Implement/upgrade operator dashboard routes in Fastify under `/api/v1/operator-dashboard/*` (or extend existing `/dashboard/*` routes).

### Required API route design

### 1) Store Report Card
- `GET /api/v1/operator-dashboard/report-card`
- Auth: Clerk JWT
- Query: `operator_id` optional (defaults to auth operator)
- Response:

```json
{
  "overall_score": 72,
  "category_scores": [{"category":"Flower","score":65,"status":"warning"}],
  "top_actions": ["Lower top 10 flower SKUs by 4-6%"]
}
```

### 2) Price Wire
- `GET /api/v1/operator-dashboard/price-wire?window=24h&min_change_pct=5`
- Returns significant local changes + same-GPID market moves

### 3) Threat Radar
- `GET /api/v1/operator-dashboard/threat-radar?radius_miles=10`
- Returns nearest competitors, overlap %, price position

### 4) Canonical Product Lookup
- `GET /api/v1/operator-dashboard/products/:gpid`
- Returns canonical product card + cross-store prices

### 5) Competitor Comparison
- `GET /api/v1/operator-dashboard/competitors/:competitor_id/comparison?limit=100`
- Returns shared GPIDs and price deltas

### 6) Daily Digest Trigger
- `POST /api/v1/operator-dashboard/digest/send`
- Creates digest payload + queues email send

### Task M3.2 — Subscription + entitlements (8h)
- Reuse existing billing routes
- Gate advanced endpoints by plan (`operator_standard`, `operator_pro`)

### Task M3.3 — Email digest system (8h)
- Daily cron
- Include top 5 price events + 3 threat signals + 3 actions

### Task M3.4 — Whale report automation (15h)
- Brand intelligence endpoint + export
- Generate MAP violations and distribution trends per brand

### Task M3.5 — Whale conversion tooling (10h)
- CRM-friendly payloads
- endpoint to generate “executive 1-pager” PDF in <60s per account

**Month 3 exit criteria:**
- Operator dashboard production-ready
- Automated weekly whale reports
- Sales workflow for Top 20 whale targets

---

## 7) Required SQL Schemas

Create migration: `migrations/005_matching_core_tables.sql`

```sql
-- 1) canonical_products
CREATE TABLE IF NOT EXISTS canonical_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gpid VARCHAR(64) NOT NULL UNIQUE,
  canonical_name VARCHAR(500) NOT NULL,
  canonical_brand VARCHAR(255),
  category VARCHAR(64) NOT NULL,
  strain_name VARCHAR(255),
  strain_type VARCHAR(64),
  weight_grams NUMERIC(10,3),
  thc_percent_avg NUMERIC(5,2),
  cbd_percent_avg NUMERIC(5,2),
  source_product_count INTEGER NOT NULL DEFAULT 0,
  store_count INTEGER NOT NULL DEFAULT 0,
  price_min NUMERIC(10,2),
  price_max NUMERIC(10,2),
  price_avg NUMERIC(10,2),
  price_median NUMERIC(10,2),
  confidence_avg NUMERIC(5,4),
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_canonical_products_category ON canonical_products(category);
CREATE INDEX IF NOT EXISTS idx_canonical_products_brand ON canonical_products(canonical_brand);
CREATE INDEX IF NOT EXISTS idx_canonical_products_last_seen ON canonical_products(last_seen_at DESC);


-- 2) product_matches
CREATE TABLE IF NOT EXISTS product_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  canonical_product_id UUID NOT NULL REFERENCES canonical_products(id) ON DELETE CASCADE,
  confidence NUMERIC(5,4) NOT NULL,
  match_method VARCHAR(32) NOT NULL CHECK (match_method IN ('exact_fingerprint','similarity','ai_review','manual')),
  similarity_score NUMERIC(5,4),
  ai_review_result JSONB,
  needs_manual_review BOOLEAN NOT NULL DEFAULT FALSE,
  reviewed_by UUID,
  reviewed_at TIMESTAMPTZ,
  matched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_product_matches_product UNIQUE (product_id)
);

CREATE INDEX IF NOT EXISTS idx_product_matches_canonical ON product_matches(canonical_product_id);
CREATE INDEX IF NOT EXISTS idx_product_matches_confidence ON product_matches(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_product_matches_method ON product_matches(match_method);


-- 3) brand_dictionary
CREATE TABLE IF NOT EXISTS brand_dictionary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_name VARCHAR(255) NOT NULL UNIQUE,
  aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
  normalized_key VARCHAR(255) NOT NULL UNIQUE,
  parent_company VARCHAR(255),
  operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  is_house_brand BOOLEAN NOT NULL DEFAULT FALSE,
  confidence NUMERIC(5,4) NOT NULL DEFAULT 1.0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brand_dictionary_operator ON brand_dictionary(operator_id);
CREATE INDEX IF NOT EXISTS idx_brand_dictionary_aliases_gin ON brand_dictionary USING gin (aliases jsonb_path_ops);


-- 4) price_changes
CREATE TABLE IF NOT EXISTS price_changes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  canonical_product_id UUID REFERENCES canonical_products(id) ON DELETE SET NULL,
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  previous_price NUMERIC(10,2) NOT NULL,
  current_price NUMERIC(10,2) NOT NULL,
  change_amount NUMERIC(10,2) NOT NULL,
  change_pct NUMERIC(7,2) NOT NULL,
  severity VARCHAR(16) NOT NULL CHECK (severity IN ('noise','minor','significant','major')),
  changed_at TIMESTAMPTZ NOT NULL,
  detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  run_id UUID,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_price_changes_operator_time ON price_changes(operator_id, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_changes_canonical_time ON price_changes(canonical_product_id, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_changes_severity ON price_changes(severity, changed_at DESC);
```

Optional Timescale conversion once volume justifies:

```sql
-- SELECT create_hypertable('price_changes', 'changed_at', if_not_exists => TRUE);
```

---

## 8) AI Matching Pipeline Design (0.45-0.55 Band)

## Pipeline stages
1. Normalize + fingerprint
2. Exact match (precision-first)
3. Trigram weighted similarity
4. **AI arbitration for 0.45-0.55 only**
5. Union-find clustering -> canonical product
6. Persist run metrics

## LLM review data contract

Input payload (per pair):

```json
{
  "pair_id": "uuid",
  "a": {"name": "...", "brand": "...", "category": "...", "weight_grams": 0.5, "thc": 82.1},
  "b": {"name": "...", "brand": "...", "category": "...", "weight_grams": 0.5, "thc": 81.8},
  "rules": ["false positives are costly", "respond JSON only"]
}
```

Output payload:

```json
{
  "is_match": true,
  "confidence": 72,
  "reason": "Equivalent SKU naming variation"
}
```

## Acceptance policy
- Auto-match if `is_match=true AND confidence>=60`
- Auto-reject if `is_match=false AND confidence>=70`
- Else `needs_manual_review=true`

## Cost controls
- Batch up to 100 pairs/request
- Cache deterministic pair signatures (`sha256(normA|normB)`)
- Log usage in `matching_runs.ai_review_cost_usd`

---

## 9) Scraper Risk Mitigation (POS API Trojan Horse)

Scraping remains existential risk. Design transition path now.

## Technical approach
1. Introduce unified ingestion interface:
   - `source_type`: `scrape | pos_api`
2. Add connector scaffolding for Dutchie/Jane/Blaze read-only APIs
3. Offer **free operator intelligence tier** in exchange for API tokens
4. Use API feed as primary truth where available; scraper as fallback

### Required schema extension

```sql
CREATE TABLE IF NOT EXISTS pos_connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  provider VARCHAR(50) NOT NULL, -- dutchie/jane/blaze
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  scopes JSONB NOT NULL DEFAULT '[]'::jsonb,
  last_sync_at TIMESTAMPTZ,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Ingestion precedence rule
- If API feed freshness < 6h, use API records
- Else use latest scrape records
- Tag lineage on each price record (`data_lineage: api|scrape`)

---

## 10) PostgreSQL Feature Usage (Explicit)

### Use now
- `pg_trgm` for fuzzy similarity
- `unaccent` for normalization
- `pgcrypto` for UUID and hashing support
- `pg_cron` for refresh + matching schedules
- materialized views for heavy analytics

### Use for supply chain graph traversal (instead of Neo4j)

```sql
WITH RECURSIVE license_graph AS (
  SELECT
    l.license_number,
    l.business_name,
    l.license_number AS root_license,
    0 AS depth
  FROM ccc_licenses l
  WHERE l.license_number = $1

  UNION ALL

  SELECT
    c.license_number,
    c.business_name,
    g.root_license,
    g.depth + 1
  FROM ccc_licenses c
  JOIN license_graph g
    ON (
      c.normalized_business_name = g.business_name
      OR c.normalized_address = (SELECT normalized_address FROM ccc_licenses WHERE license_number = g.license_number)
    )
  WHERE g.depth < 4
)
SELECT * FROM license_graph;
```

### TimescaleDB extension (same DB) trigger point
Enable only after `price_changes` > 5M rows and query latency > target.

---

## 11) API Delivery Plan for Operator Dashboard

Implement these in `src/services/api/src/routes/dashboard.ts` (or split into dedicated files):

1. `GET /dashboard/report-card`
2. `GET /dashboard/price-wire`
3. `GET /dashboard/threat-radar`
4. `GET /dashboard/competitors`
5. `GET /dashboard/competitors/:id/comparison`
6. `GET /dashboard/products/:gpid`
7. `POST /dashboard/digest/send`

### Fastify route skeleton example

```ts
fastify.get('/dashboard/price-wire', {
  onRequest: [fastify.authenticate],
  schema: {
    querystring: Type.Object({
      window: Type.Optional(Type.String({ default: '24h' })),
      min_change_pct: Type.Optional(Type.Number({ default: 5 }))
    })
  }
}, async (request) => {
  const operatorId = request.auth.operator_id;
  // query price_changes joined to canonical_products
  // return major/significant moves sorted by abs(change_pct)
});
```

---

## 12) Acceptance Criteria by Month

## Month 1
- Matching pipeline runs end-to-end nightly
- `canonical_products`, `product_matches`, `brand_dictionary`, `price_changes` populated
- precision >= 90%

## Month 2
- 10 operator-ready PDFs generated with one command
- Cultivator rankings + brand distribution included
- precision >= 95%

## Month 3
- Operator dashboard routes stable and authenticated
- Daily digest + billing gates active
- Whale report generation automated for outbound sales

---

## 13) First Build Sequence (Developer Start Here)

1. Add `004_matching_foundation.sql`
2. Add `005_matching_core_tables.sql`
3. Build `normalize-products.ts` and backfill normalization fields
4. Build candidate + scoring SQL pipeline
5. Add AI review worker for 0.45-0.55
6. Add union-find clustering job + GPID generator
7. Add `price_changes` detection job
8. Add report query views + PDF renderer
9. Add dashboard endpoints + plan gating

This order preserves the **foundation-first mandate** and aligns with the 90-day revenue strategy.