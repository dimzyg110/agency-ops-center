# GLASS Wartime Sprint Plan (72 Hours)

**Owner:** CTO (execution delegated to agent teams)  
**Window:** Sat → Mon (72 hours)  
**Objective:** Ship consumer-facing price comparison using only high-confidence, verified GPIDs from top brands.

---

## Command Center: Non-Negotiables

1. **Stop boiling the ocean:** only top brands with multi-platform presence.
2. **No fuzzy auto-matching in critical path:** deterministic parse + deterministic hash only.
3. **No consumer query on unverified products.**
4. **Preserve good historical assets:** `product_matches`, `gpid_verdicts` are read-only during sprint.
5. **Every phase has a rollback.**

---

## 72-Hour Timeline (Hard Schedule)

- **Phase 0 (Tonight, 2h):** Quarantine bad brand dictionary + create clean authority layer.
- **Phase 1 (Tonight/Tomorrow, 4h):** Build authoritative brand corpus from Leafly/Weedmaps and rank top brands.
- **Phase 2 (Tomorrow, 6h):** LLM parse top-brand products (~15k rows) into `parsed_products`.
- **Phase 3 (Sunday, 4h):** Deterministic GPID lock into `verified_gpids`, QA gate.
- **Phase 4 (Monday, 4h):** Consumer query API serving only verified GPIDs.
- **Expansion (daily):** +50 verified GPIDs/day.

---

## PHASE 0 — QUARANTINE (Tonight, 2 hours)

### 0.1 Exact SQL: quarantine `brand_dictionary`

Run from repo root (`/data/workspace/projects/glass/src`):

```bash
psql "postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" <<'SQL'
SET search_path TO public;
BEGIN;

-- Lock to avoid concurrent writes while renaming
LOCK TABLE brand_dictionary IN ACCESS EXCLUSIVE MODE;

-- Preserve legacy table intact
ALTER TABLE brand_dictionary RENAME TO brand_dictionary_legacy;

-- Safety marker comment
COMMENT ON TABLE brand_dictionary_legacy IS
  'Quarantined on 2026-02-14 during wartime sprint. Do not use in matching pipeline.';

COMMIT;
SQL
```

### 0.2 Exact SQL: create `brand_authority`

```bash
psql "postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" <<'SQL'
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
SQL
```

### 0.3 Cron/jobs/scripts to kill immediately

**Disable any brand-dictionary refresh/alias expansion jobs** before next scrape cycle.

Known daily scraper schedules (keep scrapers running, kill only brand dictionary derivation jobs):
- `src/scrapers/leafly/railway.toml` (`cronSchedule = "5 7 * * *"`)
- `src/scrapers/weedmaps/railway.toml` (`cronSchedule = "30 3 * * *"`)
- `src/scrapers/jane/railway.toml`
- `src/scrapers/dutchie/railway.toml`

**Stop these patterns if present in Railway/job configs:**
- `brand_dictionary*`
- `buildBrandDictionary*`
- `brand-alias*`
- any script that writes to `brand_dictionary` (now `brand_dictionary_legacy`)

**Detection command (exact):**

```bash
cd /data/workspace/projects/glass/src
rg -n "brand_dictionary|build.*brand|alias.*brand|brand.*normalize" scripts services scrapers
```

### 0.4 Do NOT touch

- `product_matches` (preserve)
- `gpid_verdicts` (preserve)
- existing raw `products` and `prices` ingest flow

Only isolate broken brand dictionary; do not invalidate prior human-reviewed matching artifacts.

---

## PHASE 1 — BRAND AUTHORITY (Tonight/Tomorrow, 4 hours)

### 1.1 Leafly brand directory scraper spec

**Target:** `https://leafly.com/brands`  
**New script path:** `src/scripts/brand-authority/scrape-leafly-brands.ts`

**Extraction fields:**
- `canonical_name`
- `source_brand_url`
- optional logo URL
- optional brand description

**Rules:**
1. Load index page and paginate/scroll until no new brand cards.
2. Extract brand display name exactly as shown.
3. Normalize for matching key (`lower(trim(name))` only; no aggressive aliasing).
4. Upsert into `brand_authority` with `source='leafly'`, `verification_method='directory'`, `verified=true`, `source_confidence=0.95`.

### 1.2 Weedmaps brand directory scraper spec

**Target:** `https://weedmaps.com/brands`  
**New script path:** `src/scripts/brand-authority/scrape-weedmaps-brands.ts`

**Rules:** same as Leafly, with `source='weedmaps'`.

### 1.3 Combined loader command

Create orchestrator: `src/scripts/brand-authority/sync-brand-authority.ts`

```bash
cd /data/workspace/projects/glass/src
node --loader tsx scripts/brand-authority/scrape-leafly-brands.ts
node --loader tsx scripts/brand-authority/scrape-weedmaps-brands.ts
node --loader tsx scripts/brand-authority/rank-top-brands.ts --min-platforms=3 --top=50
```

### 1.4 SQL: identify top brands by product + platform coverage

```sql
SET search_path TO public;

WITH norm_products AS (
  SELECT
    p.id AS product_id,
    lower(trim(COALESCE(p.brand, ''))) AS brand_norm,
    s.platform,
    p.name
  FROM products p
  JOIN sources s ON s.id = p.source_id
  WHERE p.brand IS NOT NULL
    AND trim(p.brand) <> ''
),
brand_rollup AS (
  SELECT
    brand_norm,
    COUNT(*) AS product_count,
    COUNT(DISTINCT platform) AS platform_count
  FROM norm_products
  GROUP BY brand_norm
),
authority_resolved AS (
  SELECT
    ba.brand_id,
    ba.canonical_name,
    br.product_count,
    br.platform_count
  FROM brand_authority ba
  JOIN brand_rollup br
    ON lower(trim(ba.canonical_name)) = br.brand_norm
  WHERE ba.verified = TRUE
)
SELECT *
FROM authority_resolved
WHERE platform_count >= 3
ORDER BY platform_count DESC, product_count DESC
LIMIT 50;
```

### 1.5 Backfill authority counts

```sql
SET search_path TO public;

WITH brand_rollup AS (
  SELECT
    lower(trim(p.brand)) AS brand_norm,
    COUNT(*)::int AS product_count,
    COUNT(DISTINCT s.platform)::int AS platform_count
  FROM products p
  JOIN sources s ON s.id = p.source_id
  WHERE p.brand IS NOT NULL AND trim(p.brand) <> ''
  GROUP BY lower(trim(p.brand))
)
UPDATE brand_authority ba
SET
  product_count = br.product_count,
  platform_count = br.platform_count,
  last_seen_at = NOW()
FROM brand_rollup br
WHERE lower(trim(ba.canonical_name)) = br.brand_norm;
```

---

## PHASE 2 — LLM MEAT GRINDER (Tomorrow, 6 hours)

### 2.1 Modify parser script

**Existing:** `src/scripts/experiments/llm-product-parser.ts`  
**Create production runner:** `src/scripts/gpid/parse-top-brands.ts`

#### Required changes

1. Add CLI flags:
   - `--brand-top=30`
   - `--min-platforms=3`
   - `--batch-size=25`
   - `--model=deepseek-ai/deepseek-r1`
   - `--dry-run=false`
2. Query only products tied to top-N authority brands.
3. Add fields:
   - `is_accessory BOOLEAN`
   - `accessory_reason TEXT`
   - `weight_inferred BOOLEAN`
   - `weight_inference_reason TEXT`
4. Persist every parse to `parsed_products` table.

### 2.2 SQL schema: `parsed_products`

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

### 2.3 Prompt (exact, v1)

Use as system prompt in parser:

```text
You are a deterministic cannabis product normalization engine.
Return ONLY minified JSON matching the exact schema.
Never include markdown, prose, or comments.

Task:
Given a dispensary product name, extract canonical fields for GPID generation.

Output schema:
{
  "brand": string|null,
  "strain": string|null,
  "category": "flower"|"pre_roll"|"vape"|"edible"|"concentrate"|"tincture"|"topical"|"capsule"|"beverage"|"other"|null,
  "form": string|null,
  "weight_grams": number|null,
  "pack_size": number|null,
  "is_accessory": boolean,
  "accessory_reason": string|null,
  "weight_inferred": boolean,
  "weight_inference_reason": string|null,
  "thc_percent": number|null,
  "confidence": number
}

Rules:
1) Mark accessories true for non-cannabis items: batteries, chargers, shirts, hoodies, gift cards, lighters, merch, rigs, papers, devices with no cannabis content.
2) Infer weight_grams when explicit pack patterns exist:
   - "7pk 0.5g" => 3.5
   - "10 x 0.35g" => 3.5
   - "3.5g" => 3.5
   - "1/8" => 3.5, "1/4" => 7, "1/2" => 14, "oz" => 28
   If inferred, set weight_inferred=true and explain.
3) If no reliable weight, set weight_grams=null.
4) Keep brand/strain clean; remove promo words and store-specific noise.
5) Confidence in [0,1].
6) Prefer precision over recall.
```

### 2.4 Batching strategy for 15K rows

- Batch size: **25 products/request**.
- Parallel workers: **4**.
- Retry: exponential backoff (2s, 5s, 10s) max 3 tries.
- Checkpoint every 500 products (`run_progress` JSON file + DB commits).
- Expected requests: `15,000 / 25 = 600` total requests.

### 2.5 Validation and disagreement handling

Auto-accept row when all true:
- `is_accessory = false`
- `parsed_brand IS NOT NULL`
- `parsed_weight_grams IS NOT NULL`
- confidence `>= 0.80`
- category is known enum

Set `needs_review` when:
- LLM brand differs from DB brand (normalized mismatch)
- weight differs by >20%
- accessory=true but DB category indicates cannabis
- confidence <0.80

**Do not overwrite source `products` row.** Store disagreements in `parsed_products.validation_notes`.

---

## PHASE 3 — GPID LOCK (Sunday, 4 hours)

### 3.1 Drop rules (strict)

Exclude from GPID generation:
1. `is_accessory = true`
2. `parsed_weight_grams IS NULL`
3. `parsed_brand IS NULL OR parsed_brand = ''`

### 3.2 Hash formula (exact)

```sql
encode(
  digest(
    lower(trim(parsed_brand)) || '|' ||
    lower(trim(COALESCE(parsed_strain, ''))) || '|' ||
    lower(trim(COALESCE(parsed_form, ''))) || '|' ||
    trim(to_char(parsed_weight_grams, 'FM999999990.###')),
    'sha256'
  ),
  'hex'
)
```

### 3.3 SQL schema: `verified_gpids` + link table

```sql
SET search_path TO public;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS verified_gpids (
  gpid TEXT PRIMARY KEY, -- sha256 hex
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

### 3.4 Link across all 4 platforms

```sql
INSERT INTO product_verified_gpids (product_id, gpid, parse_run_id, confidence)
SELECT
  pp.product_id,
  encode(digest(
    lower(trim(pp.parsed_brand)) || '|' ||
    lower(trim(COALESCE(pp.parsed_strain, ''))) || '|' ||
    lower(trim(COALESCE(pp.parsed_form, ''))) || '|' ||
    trim(to_char(pp.parsed_weight_grams, 'FM999999990.###')),
  'sha256'), 'hex') AS gpid,
  pp.run_id,
  pp.confidence
FROM parsed_products pp
WHERE pp.validation_status IN ('accepted','pending')
  AND pp.is_accessory = FALSE
  AND pp.parsed_brand IS NOT NULL
  AND pp.parsed_weight_grams IS NOT NULL
ON CONFLICT (product_id) DO UPDATE
SET gpid = EXCLUDED.gpid,
    parse_run_id = EXCLUDED.parse_run_id,
    confidence = EXCLUDED.confidence,
    mapped_at = NOW();
```

Then backfill `verified_gpids` aggregates from mapping table.

### 3.5 Quality gate: manual spot check of 50 random GPIDs

```sql
SELECT vg.gpid, vg.canonical_brand, vg.canonical_strain, vg.canonical_form, vg.weight_grams,
       COUNT(pvg.product_id) AS products
FROM verified_gpids vg
JOIN product_verified_gpids pvg ON pvg.gpid = vg.gpid
GROUP BY 1,2,3,4,5
ORDER BY random()
LIMIT 50;
```

Gate passes only if **>= 47/50** are correct (94% precision).

### 3.6 Metrics to capture

- total verified GPIDs
- products mapped to verified GPIDs
- unique stores (operators) covered
- price points per GPID

---

## PHASE 4 — CONSUMER QUERY LAYER (Monday, 4 hours)

### 4.1 API endpoint design

**File path:** `src/services/api/src/routes/consumer.ts`

Endpoints:
1. `GET /v1/consumer/search?q=&brand=&category=&lat=&lng=&radius_miles=&limit=&offset=`
2. `GET /v1/consumer/gpid/:gpid`
3. `GET /v1/consumer/brands/top`

### 4.2 Query pattern (verified only)

```sql
SELECT
  vg.gpid,
  vg.canonical_brand,
  vg.canonical_strain,
  vg.canonical_form,
  vg.weight_grams,
  MIN(pr.price) AS min_price,
  MAX(pr.price) AS max_price,
  COUNT(*) AS price_points,
  COUNT(DISTINCT o.id) AS store_count
FROM verified_gpids vg
JOIN product_verified_gpids pvg ON pvg.gpid = vg.gpid
JOIN products p ON p.id = pvg.product_id
JOIN prices pr ON pr.product_id = p.id
JOIN sources s ON s.id = p.source_id
JOIN operators o ON o.id = s.operator_id
WHERE pr.collected_at >= NOW() - INTERVAL '7 days'
  AND vg.verification_status = 'verified'
GROUP BY vg.gpid, vg.canonical_brand, vg.canonical_strain, vg.canonical_form, vg.weight_grams
ORDER BY price_points DESC
LIMIT $1 OFFSET $2;
```

### 4.3 Freshness policy

- Only show prices `collected_at >= NOW() - INTERVAL '7 days'`.
- Return `freshness_status`:
  - `fresh` (<=48h)
  - `aging` (48h–7d)
  - hide if stale (>7d)

### 4.4 Response format (frontend contract)

```json
{
  "meta": {
    "query": "blue dream",
    "count": 25,
    "limit": 25,
    "offset": 0,
    "generated_at": "2026-02-17T12:00:00Z"
  },
  "results": [
    {
      "gpid": "<sha256>",
      "brand": "jeeter",
      "strain": "blue dream",
      "form": "pre_roll",
      "weight_grams": 1.0,
      "category": "pre_roll",
      "pricing": {
        "min": 12.0,
        "max": 22.0,
        "median": 16.5,
        "price_points": 31
      },
      "coverage": {
        "stores": 18,
        "platforms": ["leafly", "weedmaps", "jane"]
      },
      "freshness_status": "fresh"
    }
  ]
}
```

---

## EXPANSION PLAN — Ongoing (+50 GPIDs/day)

### Daily cron workflow

New cron script: `src/scripts/gpid/daily-gpid-expansion.ts`

1. Select next brands from `brand_authority` not yet fully parsed.
2. Parse products for next 3–5 brands/day.
3. Auto-approve high-confidence rows.
4. Queue edge cases for human review.
5. Materialize new verified GPIDs.

### Cron schedule

- Daily at `09:30 UTC` (off peak):

```cron
30 9 * * *
```

### Human review queue

Create table:

```sql
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

### Re-run vs auto-approve policy

- **Auto-approve:** confidence >= 0.90 and no DB conflicts.
- **Re-run model:** confidence 0.70–0.89 OR single-field conflict.
- **Human review:** confidence <0.70 OR brand mismatch + weight mismatch.

---

## AGENT TASK BREAKDOWN (copy-pasteable)

> Model hierarchy requested: **Codex T1**, **MiniMax T3**, **Kimi T4**

### Phase 0 Task

- **Model:** Codex T1
- **Dependencies:** none
- **ETA:** 2h
- **Success:** `brand_dictionary_legacy` exists; `brand_authority` exists; risky jobs disabled.

```text
Read /data/workspace/projects/glass/CONTRIBUTING.md first. Then execute Phase 0 quarantine:
1) Run SQL to rename public.brand_dictionary to public.brand_dictionary_legacy.
2) Create public.brand_authority with schema from WARTIME-SPRINT-PLAN.md.
3) Search repo for jobs/scripts writing to brand_dictionary and produce disable list with exact file paths.
4) Do NOT modify product_matches or gpid_verdicts.
Save execution log to /data/workspace/projects/glass/reports/phase0-quarantine-report.md
```

### Phase 1 Task

- **Model:** MiniMax T3
- **Dependencies:** Phase 0 complete
- **ETA:** 4h
- **Success:** 200+ verified authority brands loaded with product/platform counts.

```text
Read /data/workspace/projects/glass/CONTRIBUTING.md first. Build brand authority ingestion:
1) Implement scripts/brand-authority/scrape-leafly-brands.ts and scrape-weedmaps-brands.ts.
2) Upsert results into public.brand_authority.
3) Implement rank-top-brands.ts to compute top brands with platform_count>=3.
4) Produce top-50 brand output CSV at /data/workspace/projects/glass/reports/top-50-authority-brands.csv.
5) Save runbook and SQL evidence to /data/workspace/projects/glass/reports/phase1-brand-authority-report.md
```

### Phase 2 Task

- **Model:** Codex T1
- **Dependencies:** Phase 1 top brands ready
- **ETA:** 6h
- **Success:** 15k+ rows parsed into `parsed_products`, >=90% field accuracy on QA sample.

```text
Read /data/workspace/projects/glass/CONTRIBUTING.md first. Productionize LLM parsing:
1) Fork scripts/experiments/llm-product-parser.ts into scripts/gpid/parse-top-brands.ts.
2) Add CLI filters for top brands/platform thresholds.
3) Switch default model to deepseek-ai/deepseek-r1 at https://integrate.api.nvidia.com/v1.
4) Add accessory detection, weight inference, and confidence handling.
5) Persist output to public.parsed_products (new table).
6) Implement retries/checkpointing for 15k row run.
7) Generate QA comparison report at /data/workspace/projects/glass/reports/phase2-parser-qa.md
```

### Phase 3 Task

- **Model:** Codex T1
- **Dependencies:** Phase 2 parsed data available
- **ETA:** 4h
- **Success:** 500–1,000 verified GPIDs, manual sample >=94% correct.

```text
Read /data/workspace/projects/glass/CONTRIBUTING.md first. Implement deterministic GPID lock:
1) Create verified_gpids and product_verified_gpids tables.
2) Apply strict drop rules (accessory/null weight/null brand).
3) Compute SHA256 hash gpid exactly per sprint spec.
4) Backfill mapping from parsed_products.
5) Create SQL for 50-random-GPID QA sampling and export sample to /data/workspace/projects/glass/reports/phase3-gpid-sample.csv.
6) Write summary metrics to /data/workspace/projects/glass/reports/phase3-gpid-lock-report.md
```

### Phase 4 Task

- **Model:** Kimi T4
- **Dependencies:** Phase 3 complete
- **ETA:** 4h
- **Success:** consumer API serves verified-only pricing, fresh data only.

```text
Read /data/workspace/projects/glass/CONTRIBUTING.md first. Build consumer query layer:
1) Add routes in services/api for /v1/consumer/search, /v1/consumer/gpid/:gpid, /v1/consumer/brands/top.
2) Query only verified_gpids path (verified_gpids -> product_verified_gpids -> products -> prices -> sources -> operators).
3) Enforce freshness filter (last 7 days).
4) Return response JSON contract from WARTIME-SPRINT-PLAN.md.
5) Add endpoint tests and save results to /data/workspace/projects/glass/reports/phase4-consumer-api-report.md
```

---

## RISK REGISTER

| Phase | Risk | Mitigation | Rollback |
|---|---|---|---|
| 0 | Rename breaks code expecting `brand_dictionary` | Grep all refs before deploy; hotfix alias view if needed | `ALTER TABLE brand_dictionary_legacy RENAME TO brand_dictionary;` |
| 1 | Directory scraping blocked/HTML changes | Use Playwright fallback + resilient selectors + retry | Load last-known-good brand dump from reports |
| 2 | Model output malformed JSON | strict JSON schema validation + retry + reject on parse fail | Keep parsed rows tagged by run_id; discard failed run |
| 2 | DeepSeek throughput instability | reduce concurrency, fallback to llama-3.3-70b | rerun failed batches only from checkpoint |
| 3 | Hash collisions/normalization bugs | include delimiter + exact formatting + unit tests | regenerate GPIDs from parsed snapshot with patched formula |
| 3 | Over-filtering removes too many products | monitor drop-rate dashboard every 1k rows | temporarily mark low-confidence rows provisional |
| 4 | API latency from heavy joins | add indexes + limit/offset + optional materialized view | serve cached pre-aggregates while tuning |
| Ongoing | Drift in brand naming over time | monthly authority refresh + review queue | freeze auto-approve and require manual review |

---

## METRICS DASHBOARD (Phase Gates)

### Core tables to monitor
- `brand_authority`
- `parsed_products`
- `verified_gpids`
- `product_verified_gpids`
- `prices` freshness

### Phase targets (hard)

1. **Phase 1:** `brand_authority` has **200+ verified brands**.
2. **Phase 2:** **15,000+ parsed products**, **>90% field accuracy** on audited sample.
3. **Phase 3:** **500–1,000 verified GPIDs** covering top 30 brands.
4. **Phase 4:** API returns accurate comparisons for **500+ products** with <=7-day prices.

### On-track vs behind rules

- **On track:** target met within phase window and error rate under threshold.
- **At risk:** <80% of target by midpoint time.
- **Behind:** <60% of target by phase deadline.

### SQL snippets for dashboard checks

```sql
-- Phase 1
SELECT COUNT(*) FROM brand_authority WHERE verified = TRUE;

-- Phase 2
SELECT COUNT(*) FROM parsed_products;
SELECT validation_status, COUNT(*) FROM parsed_products GROUP BY 1;

-- Phase 3
SELECT COUNT(*) FROM verified_gpids;
SELECT COUNT(*) FROM product_verified_gpids;

-- Phase 4 freshness coverage
SELECT COUNT(*)
FROM prices
WHERE collected_at >= NOW() - INTERVAL '7 days';
```

---

## Execution Notes for Agents

- Work from `/data/workspace/projects/glass/src`.
- All code changes via feature branch + PR (no direct main commits).
- No edits to `.env` or secrets.
- All outputs must include report file under `/data/workspace/projects/glass/reports/`.

**Definition of Victory (Monday EOD):** Consumer API uses only `verified_gpids`, shows real cross-store price deltas for top brands, and expansion pipeline is running at +50 GPIDs/day.
