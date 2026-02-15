# Phase 0 Quarantine Execution Report

**Timestamp (UTC):** 2026-02-14  
**Operator:** Codex subagent  
**Database:** Railway Postgres (`public` schema)

## 0) Preconditions
- Read: `/data/workspace/projects/glass/CONTRIBUTING.md`
- Read: `/data/workspace/projects/glass/WARTIME-SPRINT-PLAN.md`
- Constraint observed: did **not** modify `product_matches`, `gpid_verdicts`, `products`, or `prices` tables.

---

## 1) Quarantine `brand_dictionary`

### SQL executed
```sql
SET search_path TO public;
BEGIN;
LOCK TABLE brand_dictionary IN ACCESS EXCLUSIVE MODE;
ALTER TABLE brand_dictionary RENAME TO brand_dictionary_legacy;
COMMENT ON TABLE brand_dictionary_legacy IS
  'Quarantined on 2026-02-14 during wartime sprint. Do not use in matching pipeline.';
COMMIT;

SET search_path TO public;
SELECT to_regclass('public.brand_dictionary') AS brand_dictionary,
       to_regclass('public.brand_dictionary_legacy') AS brand_dictionary_legacy;
SELECT obj_description('public.brand_dictionary_legacy'::regclass, 'pg_class') AS legacy_comment;
```

### Output
```text
SET
BEGIN
LOCK TABLE
ALTER TABLE
COMMENT
COMMIT
SET
 brand_dictionary | brand_dictionary_legacy 
------------------+-------------------------
                  | brand_dictionary_legacy
(1 row)

                                  legacy_comment                                   
-----------------------------------------------------------------------------------
 Quarantined on 2026-02-14 during wartime sprint. Do not use in matching pipeline.
(1 row)
```

### Result
✅ `brand_dictionary` successfully renamed to `brand_dictionary_legacy` and commented as quarantined.

---

## 2) Create `brand_authority` table (Phase 0.2)

### SQL executed
```sql
SET search_path TO public;

CREATE TABLE IF NOT EXISTS brand_authority (
  brand_id BIGSERIAL PRIMARY KEY,
  canonical_name TEXT NOT NULL,
  canonical_slug TEXT GENERATED ALWAYS AS (
    regexp_replace(lower(trim(canonical_name)), '[^a-z0-9]+', '-', 'g')
  ) STORED,
  source TEXT NOT NULL CHECK (source IN ('leafly','weedmaps','manual','internal')),
  source_brand_url TEXT,
  source_confidence NUMERIC(5,4) DEFAULT 1.0000,
  verified BOOLEAN NOT NULL DEFAULT FALSE,
  verification_method TEXT CHECK (verification_method IN ('directory','manual','llm','hybrid')),
  product_count INTEGER NOT NULL DEFAULT 0,
  platform_count INTEGER NOT NULL DEFAULT 0,
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (canonical_name, source)
);

CREATE INDEX IF NOT EXISTS idx_brand_authority_canonical_name ON brand_authority (lower(canonical_name));
CREATE INDEX IF NOT EXISTS idx_brand_authority_verified ON brand_authority (verified);
CREATE INDEX IF NOT EXISTS idx_brand_authority_platform_count ON brand_authority (platform_count DESC, product_count DESC);
```

### Output
```text
SET
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
```

### Result
✅ `brand_authority` created with required generated slug, uniqueness constraint, and indexes.

---

## 3) Create `parsed_products` table (Phase 2.2)

### SQL executed
```sql
SET search_path TO public;

CREATE TABLE IF NOT EXISTS parsed_products (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID NOT NULL,
  product_id UUID NOT NULL,
  source_id UUID,
  platform TEXT,
  original_name TEXT NOT NULL,

  parsed_brand TEXT,
  parsed_strain TEXT,
  parsed_category TEXT,
  parsed_form TEXT,
  parsed_weight_grams NUMERIC(10,3),
  parsed_pack_size INTEGER,
  parsed_total_mg NUMERIC(10,3),
  parsed_thc_percent NUMERIC(8,3),

  is_accessory BOOLEAN NOT NULL DEFAULT FALSE,
  accessory_reason TEXT,
  weight_inferred BOOLEAN NOT NULL DEFAULT FALSE,
  weight_inference_reason TEXT,

  confidence NUMERIC(5,4),
  parser_model TEXT NOT NULL,
  parser_prompt_version TEXT NOT NULL,
  raw_llm_json JSONB NOT NULL,

  validation_status TEXT NOT NULL DEFAULT 'pending' CHECK (validation_status IN ('pending','accepted','rejected','needs_review')),
  validation_notes TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (run_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_parsed_products_product_id ON parsed_products(product_id);
CREATE INDEX IF NOT EXISTS idx_parsed_products_run_id ON parsed_products(run_id);
CREATE INDEX IF NOT EXISTS idx_parsed_products_validation_status ON parsed_products(validation_status);
```

### Output
```text
SET
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
```

### Result
✅ `parsed_products` created with accessory/weight inference flags and validation status indexing.

---

## 4) Create `verified_gpids` + `product_verified_gpids` (Phase 3.3)

### SQL executed
```sql
SET search_path TO public;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS verified_gpids (
  gpid TEXT PRIMARY KEY,
  canonical_brand TEXT NOT NULL,
  canonical_strain TEXT,
  canonical_form TEXT,
  weight_grams NUMERIC(10,3) NOT NULL,
  canonical_category TEXT,

  verification_status TEXT NOT NULL DEFAULT 'verified' CHECK (verification_status IN ('verified','provisional','rejected')),
  verification_method TEXT NOT NULL DEFAULT 'deterministic_hash',
  first_verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  supporting_product_count INTEGER NOT NULL DEFAULT 0,

  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS product_verified_gpids (
  product_id UUID PRIMARY KEY,
  gpid TEXT NOT NULL REFERENCES verified_gpids(gpid) ON DELETE CASCADE,
  parse_run_id UUID NOT NULL,
  confidence NUMERIC(5,4),
  mapped_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_product_verified_gpids_gpid ON product_verified_gpids(gpid);
```

### Output
```text
SET
NOTICE:  extension "pgcrypto" already exists, skipping
CREATE EXTENSION
CREATE TABLE
CREATE TABLE
CREATE INDEX
```

### Result
✅ `verified_gpids` and `product_verified_gpids` created; `pgcrypto` present.

---

## 5) Create `gpid_review_queue` (Expansion Plan)

### SQL executed
```sql
SET search_path TO public;

CREATE TABLE IF NOT EXISTS gpid_review_queue (
  id BIGSERIAL PRIMARY KEY,
  product_id UUID NOT NULL,
  run_id UUID NOT NULL,
  reason TEXT NOT NULL,
  priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('high','normal','low')),
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','approved','rejected')),
  assigned_to TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);
```

### Output
```text
SET
CREATE TABLE
```

### Result
✅ `gpid_review_queue` created.

---

## 6) Table creation confirmation query

### SQL executed
```sql
SELECT to_regclass('public.brand_authority') AS brand_authority,
       to_regclass('public.parsed_products') AS parsed_products,
       to_regclass('public.verified_gpids') AS verified_gpids,
       to_regclass('public.product_verified_gpids') AS product_verified_gpids,
       to_regclass('public.gpid_review_queue') AS gpid_review_queue;
```

### Output
```text
 brand_authority | parsed_products | verified_gpids | product_verified_gpids | gpid_review_queue 
-----------------+-----------------+----------------+------------------------+-------------------
 brand_authority | parsed_products | verified_gpids | product_verified_gpids | gpid_review_queue
(1 row)
```

---

## 7) `brand_dictionary` reference search (potential breakpoints)

### Command executed
```bash
cd /data/workspace/projects/glass/src && grep -rn "brand_dictionary" scripts services scrapers
```

### Output / files referencing `brand_dictionary`
- `scripts/matching/fuzzy-matcher.ts:196`
- `scripts/matching/seed-brand-dictionary.ts:201`
- `scripts/matching/seed-brand-dictionary.ts:214`
- `scripts/matching/seed-brand-dictionary.ts:231`
- `scripts/matching/seed-brand-dictionary.ts:234`
- `scripts/matching/seed-brand-dictionary.ts:241`
- `scripts/matching/seed-brand-dictionary.ts:246`
- `scripts/matching/seed-brand-dictionary.ts:247`
- `scripts/matching/seed-brand-dictionary.ts:624`
- `scripts/matching/seed-brand-dictionary.ts:631`
- `scripts/matching/seed-brand-dictionary.ts:642`
- `scripts/matching/seed-brand-dictionary.ts:678`

> All matches are `brand_dictionary` (not `brand_dictionary_legacy`).

---

## 8) Top 30 brands preview by platform coverage

### SQL executed
```sql
SET search_path TO public;
WITH brand_stats AS (
  SELECT
    lower(trim(p.brand)) AS brand_norm,
    COUNT(*) AS product_count,
    COUNT(DISTINCT s.source_type) AS platform_count
  FROM products p
  JOIN prices pr ON pr.product_id = p.id
  JOIN sources s ON s.id = pr.source_id
  WHERE p.brand IS NOT NULL AND trim(p.brand) <> ''
  GROUP BY lower(trim(p.brand))
)
SELECT brand_norm, product_count, platform_count
FROM brand_stats
WHERE platform_count >= 3
ORDER BY platform_count DESC, product_count DESC
LIMIT 30;
```

### Output
```text
    brand_norm     | product_count | platform_count 
-------------------+---------------+----------------
 nature's heritage |          1412 |              5
 fernway           |          1339 |              5
 happy valley      |          1278 |              5
 cresco            |           502 |              5
 pax               |           185 |              5
 jeeter            |          1664 |              4
 high supply       |          1542 |              4
 rove              |          1509 |              4
 bountiful farms   |          1154 |              4
 rythm             |           989 |              4
 simply herb       |           951 |              4
 wyld              |           929 |              4
 treeworks         |           858 |              4
 sparq             |           822 |              4
 insa              |           654 |              4
 bostica           |           639 |              4
 incredibles       |           634 |              4
 levia             |           519 |              4
 perpetual         |           481 |              4
 dime industries   |           479 |              4
 ozone             |           473 |              4
 good chemistry    |           471 |              4
 kanha             |           463 |              4
 strane            |           460 |              4
 khalifa kush      |           455 |              4
 camino            |           431 |              4
 green gold group  |           414 |              4
 holiday           |           409 |              4
 select            |           406 |              4
 tower three       |           405 |              4
(30 rows)
```

---

## 9) Errors / Issues

1. No SQL errors encountered.
2. `pgcrypto` extension already existed (notice only).
3. Git commit scope issue: requested report path (`/data/workspace/projects/glass/reports/...`) is **outside** git repo root (`/data/workspace/projects/glass/src`), so this file cannot be directly committed from the `src` repository unless copied/symlinked into repo tree.

---

## 10) Final status

- ✅ Quarantine completed (`brand_dictionary_legacy` in place with safety comment)
- ✅ `brand_authority` created
- ✅ `parsed_products` created
- ✅ `verified_gpids` + `product_verified_gpids` created
- ✅ `gpid_review_queue` created
- ✅ Reference impact scan completed
- ✅ Top-brand preview query executed
- ✅ Report written to requested path
