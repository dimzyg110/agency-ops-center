# GLASS Matching Precision Test & Validation Plan

**Goal:** validate the 4-stage matching engine to **>=95% overall precision** before production.

**Engine stages:**
1. Stage 1: Brand normalization
2. Stage 2: Exact match
3. Stage 3: Fuzzy match
4. Stage 4: AI review (0.45–0.55 band)

---

## 0) Production Gate (Hard Stop Criteria)

Ship only if all are true for the latest candidate run:

- **Overall precision >= 95%** (human-adjudicated sample)
- Band precision thresholds met:
  - `0.95–1.00` => `>99%`
  - `0.80–0.95` => `>95%`
  - `0.60–0.80` => `>85%`
  - `0.45–0.55` (AI) => `>80%`
- Automated consistency checks all pass:
  - symmetry violations = 0
  - transitivity violations = 0
  - cycle violations = 0
- Edge-case suite passes all required cases

---

## 1) Human Validation Protocol

## 1.1 Sampling Methodology (Random + Stratified)

Use **hybrid sampling** every run:

- **90% stratified sample** by confidence band (ensures coverage where risk is highest)
- **10% pure random sentinel sample** from all matched outputs (catches blind spots)

### Why hybrid
- Pure random under-samples low-confidence areas.
- Pure stratified can miss global drift.
- Hybrid gives reliable control + drift detection.

## 1.2 Sample Sizes per Confidence Band (per release candidate run)

| Band | Expected precision | Min sample size | Notes |
|---|---:|---:|---|
| 0.95–1.00 | >99% | 150 | high precision guardrail |
| 0.80–0.95 | >95% | 250 | core production volume |
| 0.60–0.80 | >85% | 350 | primary risk band |
| 0.45–0.55 (AI) | >80% | 300 | highest uncertainty / AI decisions |
| **Total stratified** |  | **1,050** | plus 10% random sentinel |

> If run volume in a band is low, review all rows in that band.

## 1.3 Reviewer Workflow

Each sampled match gets:
1. **Reviewer A** label (`match`, `no_match`, `unsure`)
2. **Reviewer B** label (blind to A)
3. If disagreement or `unsure` => **Adjudicator** final label

Only adjudicated labels count for precision metrics.

## 1.4 Reviewer UI (Mockups)

### Queue View

```text
+--------------------------------------------------------------------------------------+
| MATCH REVIEW QUEUE (Run: 2026-02-13-rc3)                                            |
+--------------------------------------------------------------------------------------+
| Filter: [Band ▼] [Stage ▼] [Category ▼] [Brand ▼] [Only disagreements ☐]            |
|--------------------------------------------------------------------------------------|
| Match ID | Band      | Stage | Product A                          | Product B        |
|--------------------------------------------------------------------------------------|
| m_18291  | 0.60-0.80 | fuzzy | Blue Dream 5pk 1.75g Prerolls     | Blue Dream 1.75g |
| m_18292  | 0.95-1.00 | exact | Half Gram Preroll                  | 14g Flower       |
| ...                                                                              ... |
+--------------------------------------------------------------------------------------+
```

### Review Detail View

```text
+--------------------------------------------------+-----------------------------------+
| PRODUCT A                                        | PRODUCT B                         |
+--------------------------------------------------+-----------------------------------+
| Name: Blue Dream 5pk 1.75g Prerolls              | Name: Blue Dream 1.75g Preroll    |
| Brand: House Brand X                             | Brand: House Brand X              |
| Operator: Store A                                | Operator: Store B                 |
| Category: Pre-roll                               | Category: Pre-roll                |
| Weight: 8.75g total (5 x 1.75g)                  | Weight: 1.75g                     |
+--------------------------------------------------------------------------------------+
| Evidence: [stage=fuzzy] [sim=0.78] [brand_norm=yes] [pack_count_mismatch=yes]       |
+--------------------------------------------------------------------------------------+
| Decision: ( ) Match   ( ) No Match   ( ) Unsure                                     |
| Notes: [........................................................................]     |
| Shortcuts: [M]=Match [N]=No Match [U]=Unsure [Enter]=Submit                         |
+--------------------------------------------------------------------------------------+
```

## 1.5 Precision Calculations

For sampled predicted matches:

- `TP = final_label = 'match'`
- `FP = final_label = 'no_match'`
- `Precision = TP / (TP + FP)`

Compute **per confidence band**, **per stage**, and **overall**.

---

## 2) Automated Consistency Tests

Use graph-level checks on accepted pairwise edges (`match_edges`) and canonical assignments.

### Required audit table (if not already present)

```sql
-- Pairwise decisions emitted by Stage 2/3/4 before clustering
CREATE TABLE IF NOT EXISTS match_edges (
  run_id UUID NOT NULL,
  left_product_id UUID NOT NULL,
  right_product_id UUID NOT NULL,
  stage SMALLINT NOT NULL,                  -- 2,3,4
  confidence NUMERIC(5,4) NOT NULL,
  is_match BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (run_id, left_product_id, right_product_id)
);

CREATE INDEX IF NOT EXISTS idx_match_edges_run_match
  ON match_edges(run_id, is_match, stage);
```

## 2.1 Symmetry Test (A->B => B->A)

```sql
-- Expected: 0 rows
SELECT
  e1.run_id,
  e1.left_product_id AS a,
  e1.right_product_id AS b,
  e1.stage,
  e1.confidence
FROM match_edges e1
LEFT JOIN match_edges e2
  ON e2.run_id = e1.run_id
 AND e2.left_product_id = e1.right_product_id
 AND e2.right_product_id = e1.left_product_id
 AND e2.is_match = TRUE
WHERE e1.is_match = TRUE
  AND e1.run_id = '{{RUN_ID}}'::uuid
  AND e2.left_product_id IS NULL;
```

## 2.2 Transitivity Test (A->B and B->C => A->C)

```sql
-- Expected: 0 rows
WITH edges AS (
  SELECT run_id, left_product_id, right_product_id
  FROM match_edges
  WHERE run_id = '{{RUN_ID}}'::uuid
    AND is_match = TRUE
),
triples AS (
  SELECT
    e1.run_id,
    e1.left_product_id AS a,
    e1.right_product_id AS b,
    e2.right_product_id AS c
  FROM edges e1
  JOIN edges e2
    ON e2.run_id = e1.run_id
   AND e2.left_product_id = e1.right_product_id
  WHERE e1.left_product_id <> e2.right_product_id
)
SELECT t.*
FROM triples t
LEFT JOIN edges e3
  ON e3.run_id = t.run_id
 AND e3.left_product_id = t.a
 AND e3.right_product_id = t.c
WHERE e3.left_product_id IS NULL;
```

## 2.3 No Cycles Detection (for parent-link representation)

If clustering uses parent links (`match_union_parent`), enforce DAG:

```sql
CREATE TABLE IF NOT EXISTS match_union_parent (
  run_id UUID NOT NULL,
  product_id UUID NOT NULL,
  parent_product_id UUID,
  PRIMARY KEY (run_id, product_id)
);
```

```sql
-- Expected: 0 rows
WITH RECURSIVE walk AS (
  SELECT
    run_id,
    product_id,
    parent_product_id,
    ARRAY[product_id] AS path,
    FALSE AS cycle
  FROM match_union_parent
  WHERE run_id = '{{RUN_ID}}'::uuid
    AND parent_product_id IS NOT NULL

  UNION ALL

  SELECT
    w.run_id,
    w.product_id,
    p.parent_product_id,
    w.path || p.product_id,
    p.product_id = ANY(w.path) AS cycle
  FROM walk w
  JOIN match_union_parent p
    ON p.run_id = w.run_id
   AND p.product_id = w.parent_product_id
  WHERE w.cycle = FALSE
    AND array_length(w.path, 1) < 100
)
SELECT run_id, product_id, path
FROM walk
WHERE cycle = TRUE;
```

## 2.4 Stage 1 Brand Normalization Coverage Check

```sql
-- Brands in recent matches that fail to map to canonical brand_dictionary entries/aliases
-- Expected: low and trending down each run
WITH recent_brands AS (
  SELECT DISTINCT lower(trim(p.brand)) AS brand_raw
  FROM product_matches pm
  JOIN products p ON p.id = pm.product_id
  WHERE pm.matched_at >= NOW() - INTERVAL '14 days'
    AND p.brand IS NOT NULL
),
mapped AS (
  SELECT rb.brand_raw
  FROM recent_brands rb
  JOIN brand_dictionary bd
    ON lower(bd.canonical_name) = rb.brand_raw
    OR EXISTS (
      SELECT 1
      FROM jsonb_array_elements_text(bd.aliases) a(alias)
      WHERE lower(a.alias) = rb.brand_raw
    )
)
SELECT rb.brand_raw
FROM recent_brands rb
LEFT JOIN mapped m ON m.brand_raw = rb.brand_raw
WHERE m.brand_raw IS NULL
ORDER BY rb.brand_raw;
```

---

## 3) Edge Case Test Suite (Required)

Build this as a **must-pass SQL suite** against accepted matches.

### Helper view for pair inspection inside each canonical cluster

```sql
CREATE OR REPLACE VIEW v_canonical_match_pairs AS
WITH product_operator AS (
  SELECT DISTINCT ON (pr.product_id)
    pr.product_id,
    pr.operator_id
  FROM prices pr
  ORDER BY pr.product_id, pr.scraped_at DESC
)
SELECT
  pm1.canonical_product_id,
  pm1.product_id AS p1_id,
  pm2.product_id AS p2_id,
  p1.name AS p1_name,
  p2.name AS p2_name,
  lower(coalesce(p1.brand, '')) AS p1_brand,
  lower(coalesce(p2.brand, '')) AS p2_brand,
  p1.category AS p1_category,
  p2.category AS p2_category,
  po1.operator_id AS p1_operator_id,
  po2.operator_id AS p2_operator_id,
  COALESCE(p1.weight_grams, CASE
    WHEN lower(coalesce(p1.unit,'')) IN ('g','gram','grams') THEN p1.quantity::numeric
    WHEN lower(coalesce(p1.unit,'')) IN ('mg') THEN p1.quantity::numeric / 1000
    ELSE NULL
  END) AS p1_weight_g,
  COALESCE(p2.weight_grams, CASE
    WHEN lower(coalesce(p2.unit,'')) IN ('g','gram','grams') THEN p2.quantity::numeric
    WHEN lower(coalesce(p2.unit,'')) IN ('mg') THEN p2.quantity::numeric / 1000
    ELSE NULL
  END) AS p2_weight_g,
  COALESCE(NULLIF((regexp_match(lower(p1.name), '(\d+)\s*(pk|pack)'))[1], '')::int, 1) AS p1_pack_count,
  COALESCE(NULLIF((regexp_match(lower(p2.name), '(\d+)\s*(pk|pack)'))[1], '')::int, 1) AS p2_pack_count
FROM product_matches pm1
JOIN product_matches pm2
  ON pm2.canonical_product_id = pm1.canonical_product_id
 AND pm2.product_id > pm1.product_id
JOIN products p1 ON p1.id = pm1.product_id
JOIN products p2 ON p2.id = pm2.product_id
LEFT JOIN product_operator po1 ON po1.product_id = p1.id
LEFT JOIN product_operator po2 ON po2.product_id = p2.id;
```

## 3.1 "Half Gram Prerolls" must NOT match 14g flower

```sql
-- Expected: 0 rows
SELECT *
FROM v_canonical_match_pairs v
WHERE (
    (
      (v.p1_name ~* 'half\s*gram|0\.5\s*g')
      OR (v.p1_weight_g BETWEEN 0.45 AND 0.55)
    )
    AND (
      (v.p2_name ~* '(^|\W)14\s*g($|\W)')
      OR (v.p2_weight_g BETWEEN 13.8 AND 14.2)
    )
  )
   OR (
    (
      (v.p2_name ~* 'half\s*gram|0\.5\s*g')
      OR (v.p2_weight_g BETWEEN 0.45 AND 0.55)
    )
    AND (
      (v.p1_name ~* '(^|\W)14\s*g($|\W)')
      OR (v.p1_weight_g BETWEEN 13.8 AND 14.2)
    )
  );
```

## 3.2 "5pk 1.75g" vs "1.75g" must be different products

```sql
-- Expected: 0 rows
SELECT *
FROM v_canonical_match_pairs v
WHERE (
    v.p1_name ~* '(5\s*(pk|pack))' AND v.p2_name !~* '(5\s*(pk|pack))'
    AND (v.p1_name ~* '1\.75\s*g' OR v.p2_name ~* '1\.75\s*g')
  )
   OR (
    v.p2_name ~* '(5\s*(pk|pack))' AND v.p1_name !~* '(5\s*(pk|pack))'
    AND (v.p1_name ~* '1\.75\s*g' OR v.p2_name ~* '1\.75\s*g')
  );
```

## 3.3 House brands from different operators must NOT match

```sql
-- Expected: 0 rows
WITH product_operator AS (
  SELECT DISTINCT ON (pr.product_id)
    pr.product_id,
    pr.operator_id
  FROM prices pr
  ORDER BY pr.product_id, pr.scraped_at DESC
)
SELECT
  pm.canonical_product_id,
  bd.canonical_name AS house_brand,
  COUNT(DISTINCT po.operator_id) AS distinct_operators,
  ARRAY_AGG(DISTINCT po.operator_id) AS operator_ids
FROM product_matches pm
JOIN products p ON p.id = pm.product_id
JOIN brand_dictionary bd
  ON lower(coalesce(p.brand, '')) = lower(bd.canonical_name)
 AND bd.is_house_brand = TRUE
LEFT JOIN product_operator po ON po.product_id = p.id
GROUP BY pm.canonical_product_id, bd.canonical_name
HAVING COUNT(DISTINCT po.operator_id) > 1;
```

## 3.4 Unit count mismatches (pack/count) must not be clustered together

```sql
-- Expected: 0 rows (or explicitly approved exceptions only)
SELECT *
FROM v_canonical_match_pairs v
WHERE v.p1_pack_count <> v.p2_pack_count
  AND greatest(v.p1_pack_count, v.p2_pack_count) >= 2;
```

---

## 4) Confidence Band Validation

## 4.1 QA tables for review + adjudication

```sql
CREATE TABLE IF NOT EXISTS match_validation_queue (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID NOT NULL,
  match_id UUID NOT NULL REFERENCES product_matches(id) ON DELETE CASCADE,
  confidence_band VARCHAR(20) NOT NULL,
  sampled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (run_id, match_id)
);

CREATE TABLE IF NOT EXISTS match_validation_labels (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID NOT NULL,
  match_id UUID NOT NULL REFERENCES product_matches(id) ON DELETE CASCADE,
  reviewer_id UUID NOT NULL REFERENCES users(id),
  label VARCHAR(10) NOT NULL CHECK (label IN ('match','no_match','unsure')),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS match_validation_adjudications (
  match_id UUID PRIMARY KEY REFERENCES product_matches(id) ON DELETE CASCADE,
  run_id UUID NOT NULL,
  final_label VARCHAR(10) NOT NULL CHECK (final_label IN ('match','no_match')),
  adjudicator_id UUID NOT NULL REFERENCES users(id),
  adjudicated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 4.2 Stratified sample pull SQL

```sql
-- Pull stratified sample into queue for one run
WITH scored AS (
  SELECT
    pm.id AS match_id,
    pm.matched_at,
    pm.confidence::numeric AS conf,
    CASE
      WHEN pm.confidence::numeric >= 0.95 THEN '0.95-1.00'
      WHEN pm.confidence::numeric >= 0.80 THEN '0.80-0.95'
      WHEN pm.confidence::numeric >= 0.60 THEN '0.60-0.80'
      WHEN pm.confidence::numeric >= 0.45 AND pm.confidence::numeric < 0.55 THEN '0.45-0.55'
      ELSE 'other'
    END AS band
  FROM product_matches pm
  WHERE pm.matched_at >= NOW() - INTERVAL '14 days'
),
eligible AS (
  SELECT s.*
  FROM scored s
  WHERE s.band IN ('0.95-1.00','0.80-0.95','0.60-0.80','0.45-0.55')
    AND NOT EXISTS (
      SELECT 1
      FROM match_validation_adjudications a
      WHERE a.match_id = s.match_id
    )
),
ranked AS (
  SELECT
    e.*,
    ROW_NUMBER() OVER (PARTITION BY e.band ORDER BY RANDOM()) AS rn
  FROM eligible e
)
INSERT INTO match_validation_queue (run_id, match_id, confidence_band)
SELECT '{{RUN_ID}}'::uuid, r.match_id, r.band
FROM ranked r
WHERE (r.band = '0.95-1.00' AND r.rn <= 150)
   OR (r.band = '0.80-0.95' AND r.rn <= 250)
   OR (r.band = '0.60-0.80' AND r.rn <= 350)
   OR (r.band = '0.45-0.55' AND r.rn <= 300);
```

```sql
-- Optional: add 10% pure random sentinel sample across all matched rows
INSERT INTO match_validation_queue (run_id, match_id, confidence_band)
SELECT
  '{{RUN_ID}}'::uuid,
  pm.id,
  'random-sentinel'
FROM product_matches pm
WHERE pm.matched_at >= NOW() - INTERVAL '14 days'
  AND NOT EXISTS (
    SELECT 1 FROM match_validation_queue q
    WHERE q.run_id = '{{RUN_ID}}'::uuid
      AND q.match_id = pm.id
  )
ORDER BY RANDOM()
LIMIT 117; -- ~10% of 1,050 stratified
```

## 4.3 Precision by band + pass/fail thresholds

```sql
WITH thresholds AS (
  SELECT * FROM (VALUES
    ('0.95-1.00'::varchar, 0.99::numeric),
    ('0.80-0.95'::varchar, 0.95::numeric),
    ('0.60-0.80'::varchar, 0.85::numeric),
    ('0.45-0.55'::varchar, 0.80::numeric)
  ) t(confidence_band, min_precision)
),
band_stats AS (
  SELECT
    q.confidence_band,
    COUNT(*) AS n,
    SUM(CASE WHEN a.final_label = 'match' THEN 1 ELSE 0 END) AS tp,
    SUM(CASE WHEN a.final_label = 'no_match' THEN 1 ELSE 0 END) AS fp,
    ROUND(
      SUM(CASE WHEN a.final_label = 'match' THEN 1 ELSE 0 END)::numeric
      / NULLIF(COUNT(*), 0),
      4
    ) AS precision
  FROM match_validation_queue q
  JOIN match_validation_adjudications a
    ON a.match_id = q.match_id
   AND a.run_id = q.run_id
  WHERE q.run_id = '{{RUN_ID}}'::uuid
  GROUP BY q.confidence_band
)
SELECT
  t.confidence_band,
  t.min_precision,
  COALESCE(b.n, 0) AS sample_size,
  COALESCE(b.precision, 0) AS observed_precision,
  (COALESCE(b.precision, 0) > t.min_precision) AS pass
FROM thresholds t
LEFT JOIN band_stats b
  ON b.confidence_band = t.confidence_band
ORDER BY t.confidence_band DESC;
```

## 4.4 Overall precision gate

```sql
SELECT
  '{{RUN_ID}}'::uuid AS run_id,
  COUNT(*) AS n,
  ROUND(
    SUM(CASE WHEN a.final_label = 'match' THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*),0),
    4
  ) AS overall_precision,
  (
    ROUND(
      SUM(CASE WHEN a.final_label = 'match' THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*),0),
      4
    ) >= 0.95
  ) AS pass
FROM match_validation_adjudications a
WHERE a.run_id = '{{RUN_ID}}'::uuid;
```

---

## 5) SQL Test Query Pack (Operator Checklist)

Run in this order for every candidate run:

1. **Queue generation** (Section 4.2)
2. Human review + adjudication
3. **Band precision** (Section 4.3)
4. **Overall precision** (Section 4.4)
5. **Symmetry** (Section 2.1)
6. **Transitivity** (Section 2.2)
7. **No cycles** (Section 2.3)
8. **Edge cases 3.1–3.4**

Optional but recommended:

```sql
-- Reviewer agreement (before adjudication)
WITH ranked AS (
  SELECT
    l.*,
    ROW_NUMBER() OVER (PARTITION BY l.run_id, l.match_id ORDER BY l.created_at) AS rn
  FROM match_validation_labels l
  WHERE l.run_id = '{{RUN_ID}}'::uuid
),
pairs AS (
  SELECT
    a.match_id,
    a.label AS label_1,
    b.label AS label_2
  FROM ranked a
  JOIN ranked b
    ON b.run_id = a.run_id
   AND b.match_id = a.match_id
   AND a.rn = 1
   AND b.rn = 2
)
SELECT
  COUNT(*) AS reviewed_pairs,
  ROUND(AVG(CASE WHEN label_1 = label_2 THEN 1 ELSE 0 END)::numeric, 4) AS raw_agreement
FROM pairs;
```

---

## 6) Feedback Loop (User Corrections -> Model Improvement)

## 6.1 Capture corrections in product UI

Add "Report bad match" action wherever canonical mapping is shown.

```sql
CREATE TABLE IF NOT EXISTS match_user_corrections (
  id BIGSERIAL PRIMARY KEY,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  canonical_product_id UUID NOT NULL REFERENCES canonical_products(id) ON DELETE CASCADE,
  suggested_canonical_product_id UUID,
  correction_type VARCHAR(30) NOT NULL,   -- wrong_match, should_match, wrong_brand, wrong_pack_count, wrong_weight
  reason TEXT,
  submitted_by_user_id UUID REFERENCES users(id),
  submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status VARCHAR(20) NOT NULL DEFAULT 'open', -- open, accepted, rejected
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMPTZ
);
```

## 6.2 Weekly correction triage process

1. Group corrections by failure reason (brand, weight, pack count, operator house-brand leakage).
2. Promote high-confidence corrections into training data.
3. Update:
   - Stage 1 brand dictionary aliases/house-brand rules
   - Stage 3 fuzzy features/weights/thresholds
   - Stage 4 AI prompt/schema and confidence routing
4. Re-run full validation suite.

## 6.3 Iteration cadence

- **Daily:** ingest user corrections, deduplicate, tag reason
- **Weekly:** threshold tuning + rule updates
- **Bi-weekly:** re-score held-out validation set
- **Monthly:** model/prompt version bump and compare against previous baseline

## 6.4 Feedback-loop KPIs

- Correction rate per 1,000 matches
- Repeat-error rate (same failure mode recurring after fix)
- Median correction resolution time
- Precision delta by band after each model version

---

## 7) Operational Runbook (Release Candidate)

1. Run matching pipeline (`RUN_ID` created)
2. Execute automated checks (symmetry/transitivity/cycles/edge-case queries)
3. Generate stratified queue (Section 4.2)
4. Complete 2-reviewer + adjudication workflow
5. Run precision queries (band + overall)
6. Compare against hard-stop thresholds
7. If any fail: fix rule/model/prompt and repeat
8. Ship only when all gates pass

---

## 8) Notes on Current GLASS Schema

Current production schema already contains `products`, `prices`, and core business entities.
For this precision framework, ensure these matching tables exist in DB:

- `canonical_products`
- `product_matches`
- `brand_dictionary`
- `matching_runs`
- QA tables in this plan (`match_validation_*`, `match_user_corrections`)

This plan is executable as-is once those tables are present.
