# GPID Accuracy Plan — Path to 95%+

**Date:** February 13, 2026  
**Author:** Opus subagent (COO-spawned)  
**Status:** READY FOR EXECUTION

---

## 1. Current State Audit

### 1.1 Database Reality Check

The GLASS database (Railway Postgres) has a `glass` schema with base tables, but:

| Table | Schema | Records | Notes |
|-------|--------|---------|-------|
| `glass.operators` | glass | 10 | Seed data only — 10 Boston stores |
| `glass.sources` | glass | 10 | All Dutchie, no Weedmaps/Leafly/Jane |
| `glass.products` | glass | 0 | Empty — no products ingested |
| `glass.prices` | glass | 0 | Empty — no prices ingested |
| `glass.scrape_jobs` | glass | 0 | Empty — no jobs tracked |

**Critical finding:** The `glass` schema tables lack the scraper migration columns (`platform`, `platform_slug`, `metadata`, `weight_grams`, `strain_type`, `scrape_runs` table, etc.). Migration `001-scraper-v2.sql` has NOT been applied. The matching engine migration `004_matching_engine.sql` has NOT been applied.

The scraper code (`db.ts`) writes to unqualified table names which resolve to the `public` schema via default `search_path`. But the `public` schema is the **Cue** application (budtenders, missions, wallet_ledger_entries, etc.) — it does NOT have the expected `operators`, `sources`, `prices`, or `scrape_runs` tables.

**Bottom line:** The pipeline cannot function until migrations are applied and the search_path issue is resolved. The data mentioned in `DATA-COVERAGE-ANALYSIS.md` (1,051 operators, 150K+ prices) was from a prior database state that no longer exists.

### 1.2 Scraper Summary Files (Best Available Data)

From the scrape summary JSON files on disk, the most recent scraper runs show:

| Platform | Slugs | Last Run Stores | Succeeded | Products | Prices | Status |
|----------|-------|-----------------|-----------|----------|--------|--------|
| Dutchie | 235 | 235 | 27 (11.5%) | 5,800 | 5,800 | 🔴 CamoFox crashes |
| Weedmaps | 282 | 143 | 0 (0%) | 0 | 0 | 🔴 Complete failure |
| Leafly | 292 | ? | ? | ? | ? | 🟡 Scraper exists but unclear state |
| Jane | 39 | 39 | ~39 | ? | ? | 🟢 API-based, stable |

**Error patterns from latest Dutchie run (Feb 13):**
- 27 stores succeeded (11.5%) 
- ~8 stores had empty menus (legitimate — no products listed)
- ~6 stores had partial category failures  
- **~200 stores failed with `TypeError: fetch failed` or CamoFox API 500** — CamoFox crashed mid-run

**Weedmaps (Feb 13):** 143 attempted, 0 succeeded, 0 products. Complete scraper failure.

### 1.3 Current `makeSKU()` Analysis

```typescript
// Current implementation in normalizer.ts
export function makeSKU(brand, name, weightGrams, category, platform = 'DUTCHIE') {
  const key = [
    normalizeBrand(brand),
    name.toLowerCase().replace(/[^a-z0-9 ]/g, '').trim(),
    (weightGrams ?? 0).toFixed(1),
    normalizeCategory(category),
  ].join('|');
  return `${platform}-${sha256(key).slice(0, 20)}`;
}
```

**Problems:**
1. **Platform prefix** — `DUTCHIE-abc123` ≠ `WEEDMAPS-abc123` even for identical products
2. **Brand normalization is shallow** — just lowercase + filter invalid brands, no alias resolution
3. **Name normalization loses structure** — strips punctuation but doesn't remove platform-specific suffixes
4. **Weight handling is brittle** — `undefined` becomes `0.0`, missing weights can't match weighted products
5. **No operator context** — same brand, same product at different stores generates the same SKU (correct) but there's no mechanism to link ACROSS operators for the SAME product

### 1.4 What Exists for Cross-Platform Matching

**Migration `004_matching_engine.sql` exists and is well-designed but NOT applied:**
- `canonical_products` table with GPID field
- `product_matches` linking source products → canonical products
- `brand_dictionary` with aliases
- `match_validation_samples` for ground truth
- `price_changes` for staleness detection
- SQL functions: `normalize_brand()`, `normalize_product_name()`, `extract_weight_grams()`, `extract_unit_count()`
- Views: `stage1_brand_normalization`, `stage2_exact_match_candidates`, `stage3_fuzzy_match_candidates`
- Function: `run_product_matching_stage1_stage2()` — executable pipeline

**This is ~60% of the matching pipeline already built.** It just needs to be applied and the upstream data pipeline needs to work.

---

## 2. Operator Matching Plan

### 2.1 Why Operator Matching is the Foundation

Before matching products across platforms, we need to know which platform sources represent the SAME physical dispensary. "Blue Dream $45 at NETA Brookline on Dutchie" can only be compared with "Blue Dream $42 at NETA Brookline on Weedmaps" if we know both sources belong to the same operator.

### 2.2 Matching Signals (Ranked by Reliability)

| Signal | Reliability | Coverage | Example |
|--------|------------|----------|---------|
| CCC License Number | 99% | ~70% of operators | `MR281963` matches across all platforms |
| Exact Address Match | 95% | ~80% | `100 Main St, Boston, MA 02118` |
| Phone Number Match | 90% | ~60% | `(617) 555-1234` |
| Normalized Name + City | 80% | ~95% | `neta` + `brookline` → same across Dutchie/WM/Leafly |
| Slug Similarity | 70% | ~100% | `neta-brookline` (Dutchie) ≈ `neta-brookline` (WM) |
| Lat/Lon Proximity (<200m) | 85% | ~70% | Two sources within 200m with similar names |

### 2.3 Implementation: `operator_sources` Cross-Reference Table

```sql
-- New table linking operators to all their platform sources
CREATE TABLE IF NOT EXISTS operator_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  platform VARCHAR(20) NOT NULL, -- 'dutchie', 'weedmaps', 'leafly', 'jane'
  platform_slug VARCHAR(500) NOT NULL,
  platform_url TEXT NOT NULL,
  match_method VARCHAR(20) NOT NULL, -- 'exact_slug', 'address', 'license', 'name_city', 'manual'
  match_confidence NUMERIC(5,4) NOT NULL DEFAULT 1.0,
  is_verified BOOLEAN NOT NULL DEFAULT FALSE,
  last_scraped_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_operator_sources_platform_slug UNIQUE (platform, platform_slug)
);

CREATE INDEX idx_operator_sources_operator ON operator_sources(operator_id);
CREATE INDEX idx_operator_sources_platform ON operator_sources(platform);
```

### 2.4 Automated Operator Matching Script

```typescript
// scripts/match-operators.ts
// Step 1: Load all slugs from all platforms
// Step 2: For each slug pair across platforms, compute similarity
// Step 3: Match by normalized name + city (highest coverage)

interface SlugRecord { slug: string; cities: string[]; nameHint?: string; }

function normalizeStoreName(slug: string): string {
  return slug
    .toLowerCase()
    .replace(/-(rec|med|menu|adult-use|medical|retail|au|pos-only|retail-rec)$/g, '')
    .replace(/-(inc|llc|co|dispensary|cannabis|marijuana)$/g, '')
    .replace(/[0-9]+$/g, '')  // trailing numbers (duplicates)
    .replace(/-+/g, '-')
    .replace(/-$/g, '');
}

function matchScore(a: string, b: string): number {
  const na = normalizeStoreName(a);
  const nb = normalizeStoreName(b);
  if (na === nb) return 1.0;
  // Levenshtein-based similarity
  const maxLen = Math.max(na.length, nb.length);
  if (maxLen === 0) return 0;
  const dist = levenshtein(na, nb);
  return 1 - (dist / maxLen);
}

// Match across platforms
for (const dutchieSlug of dutchieSlugs) {
  for (const wmSlug of weedmapsSlugs) {
    const score = matchScore(dutchieSlug.slug, wmSlug.slug);
    if (score >= 0.80) {
      // High confidence match — same operator
      matches.push({ dutchie: dutchieSlug, weedmaps: wmSlug, score });
    }
  }
}
```

### 2.5 Estimated Operator Overlap

Based on slug file analysis:
- **Dutchie:** 235 slugs (MA dispensaries)
- **Weedmaps:** 282 slugs (~119 with active menus)
- **Leafly:** 292 slugs
- **Jane:** 39 slugs

The DATA-COVERAGE-ANALYSIS found 38 exact slug matches between Dutchie and Weedmaps. With fuzzy matching on normalized names, we'd expect:
- **60-80 operators** present on both Dutchie and Weedmaps
- **100-150 operators** present on at least 2 platforms
- **30-50 operators** present on 3+ platforms

These multi-platform operators are where GPID matching creates the most value.

---

## 3. GPID Matching Pipeline (3 Stages)

### 3.1 Architecture Overview

```
Source Products (per-platform SKU)
    ↓
Stage 1: Exact Match (brand + name + weight + category → GPID hash)
    ↓ ~60-70% matched
Stage 2: Fuzzy Match (trigram similarity ≥ 0.6, same category/weight)
    ↓ ~85% matched  
Stage 3: AI Review (LLM evaluates ambiguous pairs)
    ↓ ~95% matched
Canonical Products (GPID = cross-platform identity)
```

### 3.2 Stage 1: Exact Matching (Already Built in 004_matching_engine.sql)

**How it works:**
1. Normalize brand via `normalize_brand()` (lowercase, strip legal suffixes, unaccent)
2. Normalize product name via `normalize_product_name()` (lowercase, strip non-alphanumeric)
3. Extract weight via `extract_weight_grams()` (parse "3.5g", "1/8 oz", "eighth", etc.)
4. Extract unit count via `extract_unit_count()` (parse "10pk", "5 pack")
5. Build exact match key: `brand|name|category|weight|unit_count|scope`
6. Hash → GPID: `GPID-{MD5(key)[0:12]}`
7. Group all source products with same key → same canonical product

**Critical improvement needed in normalizer.ts:** Remove the `platform` prefix from `makeSKU()`:

```typescript
// BEFORE (platform-specific, can't match cross-platform)
return `${platform}-${crypto.createHash('sha256').update(key).digest('hex').slice(0, 20)}`;

// AFTER (platform-agnostic)  
return `GPID-${crypto.createHash('sha256').update(key).digest('hex').slice(0, 12).toUpperCase()}`;
```

**Expected accuracy:** 60-70% of cross-platform products matched. Misses are due to:
- Brand spelled differently ("Fernway" vs "FERNWAY" vs "Fernway Cannabis")
- Product name formatted differently ("Blue Dream 1/8" vs "Blue Dream - Flower")
- Weight in name vs structured field
- Category differences ("pre-rolls" vs "preroll" vs "pre-roll")

### 3.3 Stage 2: Fuzzy Matching (Already Built in 004_matching_engine.sql)

**How it works (view `stage3_fuzzy_match_candidates`):**
1. Find all products NOT matched in Stage 1
2. For each, compute `score_product_similarity()` against all canonical products in the same category ± weight tolerance
3. Score = 0.35×brand_sim + 0.45×name_sim + 0.10×category_sim + 0.05×weight_sim + 0.05×unit_sim
4. Require `pg_trgm` similarity ≥ 0.35 on either name or brand (pre-filter)
5. Rank candidates, keep top 5 per source product
6. High confidence (≥0.80) → auto-match
7. Medium confidence (0.60-0.79) → queue for AI review

**Key improvements needed:**
- **Brand alias dictionary** — Pre-populate `brand_dictionary` with known MA cannabis brands and their variants
- **Weight normalization** — The `extract_weight_grams()` function needs to handle more patterns
- **Category cross-mapping** — Ensure consistent category normalization across all 4 platforms

### 3.4 Stage 3: AI Review (Needs Building)

**For products scoring 0.60-0.79 (ambiguous):**

```typescript
// scripts/lib/ai-review.ts
interface MatchCandidate {
  sourceProduct: { brand: string; name: string; category: string; weight: number; thc: number };
  candidateProduct: { brand: string; name: string; category: string; weight: number; thc: number };
  similarityScore: number;
}

async function reviewMatchBatch(candidates: MatchCandidate[]): Promise<MatchDecision[]> {
  // CRITICAL: Max 5 pairs per prompt (per 004_matching_engine.sql guardrail)
  const prompt = `You are a cannabis product matching expert. 
For each pair, decide if they are the SAME product (just listed differently) or DIFFERENT products.

Consider:
- Same brand + same strain + same weight = SAME (even if wording differs)
- Same brand + same strain + DIFFERENT weight = DIFFERENT
- Different brand + same strain name = DIFFERENT (unless brand is clearly an alias)

Pairs:
${candidates.map((c, i) => `
${i+1}. Source: "${c.sourceProduct.brand} - ${c.sourceProduct.name}" (${c.sourceProduct.weight}g, ${c.sourceProduct.category})
   Candidate: "${c.candidateProduct.brand} - ${c.candidateProduct.name}" (${c.candidateProduct.weight}g, ${c.candidateProduct.category})
   Similarity: ${c.similarityScore}
`).join('\n')}

For each pair, respond with: SAME or DIFFERENT and a brief reason.`;

  // Call LLM API
  const response = await callLLM(prompt);
  return parseMatchDecisions(response);
}
```

**Expected yield:** Resolves ~50-70% of ambiguous pairs correctly, pushing total match rate from 85% → 92-95%.

### 3.5 Stage 4: Community Verification (Feedback System)

The remaining 5-8% of unmatched products get resolved through:
- "Are these the same product?" UI prompts on comparison pages
- Operator claims and bulk menu uploads (operator-verified ground truth)
- Active learning: corrections retrain the similarity weights

This is fully designed in `FEEDBACK-SYSTEM-PLAN.md` (schema, API endpoints, trust scoring).

---

## 4. Data Quality Quick Wins

### 4.1 Ranked by Impact × Speed

| Rank | Improvement | Impact | Speed | Notes |
|------|------------|--------|-------|-------|
| **1** | Apply database migrations | 🔴 CRITICAL | 1 hour | Nothing works without this. Migrations 001-005+ must be applied. |
| **2** | Fix CamoFox crash handling | 🔴 HIGH | 2-4 hours | Auto-restart CamoFox on crash, resume runs. Currently 88.5% of Dutchie stores fail due to CamoFox crashes. |
| **3** | Fix Weedmaps scraper | 🔴 HIGH | 4-8 hours | 0% success rate on latest run. Likely browser/proxy issue. |
| **4** | Remove platform prefix from SKU | 🟡 MEDIUM | 30 min | `makeSKU()` change — enables cross-platform matching |
| **5** | Populate brand dictionary | 🟡 MEDIUM | 2-4 hours | Seed 200+ MA brand aliases from scraped data |
| **6** | Weight normalization rules | 🟡 MEDIUM | 1-2 hours | Extend WEIGHT_MAP with more patterns |
| **7** | Category taxonomy sync | 🟢 LOW | 1 hour | Ensure all 4 parsers output same canonical categories |
| **8** | Jane scraper to production | 🟡 MEDIUM | 2-4 hours | API-based, 39 stores, already works |

### 4.2 Weight Normalization Gaps

Current `WEIGHT_MAP` in normalizer.ts is missing common patterns:

```typescript
// Missing patterns that should be added:
const WEIGHT_MAP_ADDITIONS: Record<string, number> = {
  // Fractional ounces
  'eighth': 3.5,
  '1/8': 3.5,
  '1/8oz': 3.5,
  'quarter': 7,
  'quarter oz': 7,
  'quarter ounce': 7,
  '1/4': 7,
  'half': 14,
  'half ounce': 14,
  'half oz': 14,
  '1/2': 14,
  // Grams
  '0.5g': 0.5,
  '0.5 g': 0.5,
  'half gram': 0.5,
  '1g': 1, '2g': 2, '3.5g': 3.5, '5g': 5, '7g': 7, '10g': 10, '14g': 14, '28g': 28,
  // Pre-roll specific
  '0.35g': 0.35,
  '0.5g': 0.5,
  '0.7g': 0.7,
  '0.75g': 0.75,
  '1g': 1.0,
  '1.5g': 1.5,
  '2g': 2.0,
  // Edible specific (mg)
  '5mg': 0.005,
  '10mg': 0.01,
  '25mg': 0.025,
  '50mg': 0.05,
  '100mg': 0.1,
  '200mg': 0.2,
  '500mg': 0.5,
  '1000mg': 1.0,
};
```

### 4.3 Category Taxonomy Sync

Current canonical categories across parsers:

| Canonical | Dutchie | Weedmaps | Leafly | Jane |
|-----------|---------|----------|--------|------|
| `flower` | flower | FLOWER, BIG BUDS, SMALLS | flower | flower |
| `preroll` | pre-rolls | PRE-ROLL, PRE-ROLLS | pre-rolls | pre-roll, preroll |
| `vape` | vaporizers | VAPE, VAPE PENS, CARTRIDGE, DISPOSABLE | vaporizers | vape |
| `edible` | edibles | EDIBLES | edibles | edible |
| `concentrate` | concentrates | CONCENTRATES | concentrates | extract, concentrate |
| `tincture` | — | — | tinctures | tincture |
| `topical` | — | — | topicals | topical |

**Fix:** All parsers must output from the same canonical set: `flower`, `preroll`, `vape`, `edible`, `concentrate`, `tincture`, `topical`, `drink`, `accessories`.

---

## 5. Measurement Framework

### 5.1 Accuracy Metrics

| Metric | Definition | Target | How to Measure |
|--------|-----------|--------|---------------|
| **Cross-Platform Match Rate** | % of products on multi-platform operators that have a GPID match | ≥95% | `matched_products / total_products WHERE operator has 2+ sources` |
| **Price Accuracy** | % of prices within $1 or 24h of real price | ≥95% | Spot-check 100 random prices against live menus |
| **False Positive Rate** | % of GPID matches that are incorrect (different products matched) | <2% | Manual review of 100 random GPID matches |
| **Store Info Accuracy** | % of stores with correct hours/address/status | ≥95% | Compare against Google Places / CCC data |
| **Scrape Coverage** | % of active MA retailers scraped today | ≥85% | `scraped_today / 418_ccc_active_retailers` |
| **Scrape Success Rate** | % of attempted scrapes that succeed | ≥80% | `succeeded / attempted per platform` |

### 5.2 Ground Truth Dataset

```sql
-- Create a ground truth validation set
-- Randomly sample 100 product matches for manual verification
INSERT INTO match_validation_samples (canonical_product_id, sample_product_id, confidence_band, status)
SELECT 
  pm.canonical_product_id,
  pm.source_product_id,
  CASE 
    WHEN pm.confidence_score >= 0.95 THEN 'high'
    WHEN pm.confidence_score >= 0.80 THEN 'medium'
    ELSE 'low'
  END,
  'pending'
FROM product_matches pm
WHERE pm.status = 'matched'
ORDER BY RANDOM()
LIMIT 100
ON CONFLICT (canonical_product_id, sample_product_id) DO NOTHING;
```

### 5.3 Automated Accuracy Checks

```sql
-- Price variance check: same GPID across platforms should have similar prices
-- Flag products where price variance > 30% across sources
SELECT 
  cp.gpid,
  cp.brand,
  cp.product_name,
  MIN(p.price) as min_price,
  MAX(p.price) as max_price,
  MAX(p.price) - MIN(p.price) as price_spread,
  ROUND(((MAX(p.price) - MIN(p.price)) / NULLIF(AVG(p.price), 0) * 100)::numeric, 1) as variance_pct,
  COUNT(DISTINCT p.operator_id) as store_count
FROM canonical_products cp
JOIN product_matches pm ON pm.canonical_product_id = cp.id
JOIN prices p ON p.product_id = pm.source_product_id
WHERE p.scraped_at > NOW() - INTERVAL '24 hours'
GROUP BY cp.id, cp.gpid, cp.brand, cp.product_name
HAVING COUNT(DISTINCT p.operator_id) >= 2
  AND ((MAX(p.price) - MIN(p.price)) / NULLIF(AVG(p.price), 0)) > 0.30
ORDER BY variance_pct DESC;
```

### 5.4 Dashboard Metrics Query

```sql
-- Daily accuracy dashboard
SELECT
  (SELECT COUNT(*) FROM products WHERE updated_at > NOW() - INTERVAL '24 hours') as products_updated_today,
  (SELECT COUNT(*) FROM prices WHERE scraped_at > NOW() - INTERVAL '24 hours') as prices_today,
  (SELECT COUNT(DISTINCT operator_id) FROM prices WHERE scraped_at > NOW() - INTERVAL '24 hours') as operators_scraped_today,
  (SELECT COUNT(*) FROM product_matches WHERE status = 'matched') as total_matched,
  (SELECT COUNT(*) FROM product_matches WHERE status = 'needs_review') as needs_review,
  (SELECT COUNT(*) FROM canonical_products WHERE is_active = true) as canonical_products,
  (SELECT ROUND(AVG(confidence_score)::numeric, 3) FROM product_matches WHERE status = 'matched') as avg_match_confidence,
  (SELECT COUNT(*) FROM product_matches WHERE match_method = 'exact') as exact_matches,
  (SELECT COUNT(*) FROM product_matches WHERE match_method = 'similarity') as fuzzy_matches,
  (SELECT COUNT(*) FROM product_matches WHERE match_method = 'ai_review') as ai_matches;
```

---

## 6. Prioritized Roadmap (Ranked by Impact × Speed)

### THIS WEEK (Days 1-5)

| Priority | Task | Impact | Effort | Accuracy Gain |
|----------|------|--------|--------|---------------|
| **P0** | Apply all DB migrations (001-005+, 004_matching_engine) | Foundational | 2 hours | Enables everything |
| **P0** | Fix DB schema/search_path — ensure scrapers write to correct tables | Foundational | 1 hour | Enables data flow |
| **P1** | Fix CamoFox crash recovery (auto-restart + resume) | 🔴 Critical | 4 hours | +70% Dutchie coverage |
| **P1** | Debug & fix Weedmaps scraper (0% success rate) | 🔴 Critical | 4-8 hours | +119 stores |
| **P2** | Remove platform prefix from makeSKU() | High | 30 min | Enables cross-platform matching |
| **P2** | Run initial operator matching (slug-based) | High | 2-4 hours | Identifies ~80 multi-platform operators |
| **P2** | Run `run_product_matching_stage1_stage2()` on any data | High | 30 min | First GPIDs generated |

**Week 1 target: Scrapers working at 80%+ success rate, first GPIDs generated, operator matching done.**

### WEEK 2-3

| Priority | Task | Impact | Effort | Accuracy Gain |
|----------|------|--------|--------|---------------|
| **P1** | Seed brand dictionary (200+ MA brands) | High | 4-8 hours | +15-20% match rate |
| **P1** | Jane scraper to daily production | Medium | 2-4 hours | +39 stores |
| **P2** | Weight normalization improvements | Medium | 2 hours | +5-10% match rate |
| **P2** | Leafly scraper stabilization | Medium-High | 8-16 hours | +292 slugs |
| **P2** | Build ground truth validation set (100 manual matches) | High | 4 hours | Enables measurement |
| **P3** | Category taxonomy sync across all parsers | Medium | 2 hours | +3-5% match rate |

**Week 2-3 target: 85% match rate on multi-platform products. Ground truth validation running.**

### MONTH 2

| Priority | Task | Impact | Effort | Accuracy Gain |
|----------|------|--------|--------|---------------|
| **P1** | AI review pipeline (Stage 3) for ambiguous matches | High | 2-3 days | +10% match rate |
| **P2** | Feedback system MVP ("Wrong price?" button) | Medium | 1-2 days | Community validation begins |
| **P2** | Operator claim system | Medium | 2-3 days | Operator-verified data |
| **P2** | Price staleness detection & alerting | Medium | 1 day | Staleness < 24h |
| **P3** | Automated accuracy dashboard | Medium | 1 day | Ongoing measurement |

**Month 2 target: 92-95% match rate. Feedback loop operational.**

### LONG GAME (Month 3+)

| Priority | Task | Impact | Effort | Accuracy Gain |
|----------|------|--------|--------|---------------|
| **P2** | Active learning from community corrections | High | 1-2 weeks | Self-improving accuracy |
| **P3** | Embedding-based product matching | Medium | 2-3 weeks | Handles edge cases |
| **P3** | POS API integrations (BLAZE, Treez) | Medium | 4-8 weeks | +15-30 stores |
| **P3** | NCIA/BDSA market data integration | Low-Medium | 4 weeks | Market-level validation |

---

## 7. Technical Specs for Top 3 Improvements

### 7.1 Improvement #1: Apply Database Migrations & Fix Data Pipeline

**What:** Apply all pending migrations so the scraper can actually write data and the matching engine can operate.

**Files involved:**
- `src/scripts/migrations/001-scraper-v2.sql`
- `src/scripts/migrations/002-price-idempotency.sql`
- `src/scripts/migrations/003-data-quality-infra.sql`
- `src/scripts/migrations/004-merge-duplicate-operators.sql` (renamed — actually `004_matching_engine.sql` is in `src/migrations/`)
- `src/migrations/004_matching_engine.sql`
- `src/scripts/migrations/005-performance-indexes.sql`

**Step 1: Fix search_path issue**

The scraper's `db.ts` uses unqualified table names. The `glass` schema has the right tables but they're not in the default search_path. Options:

Option A (recommended): Set `search_path` in the connection:
```typescript
// In db.ts, after pool creation:
export const pool = new Pool({ 
  connectionString: DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Set search_path to glass schema
pool.on('connect', (client) => {
  client.query('SET search_path TO glass, public');
});
```

Option B: Qualify all table names in db.ts with `glass.` prefix.

**Step 2: Apply migrations**

```bash
DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway"

# Set search_path for the session
psql "$DATABASE_URL" -c "SET search_path TO glass, public;"

# Apply in order
psql "$DATABASE_URL" -f src/scripts/migrations/001-scraper-v2.sql
psql "$DATABASE_URL" -f src/scripts/migrations/002-price-idempotency.sql
psql "$DATABASE_URL" -f src/scripts/migrations/003-data-quality-infra.sql
psql "$DATABASE_URL" -f src/scripts/migrations/005-performance-indexes.sql
psql "$DATABASE_URL" -f src/migrations/004_matching_engine.sql
```

**⚠️ IMPORTANT:** Each migration file uses unqualified table names. Before running, either:
1. Prefix the psql command with `SET search_path TO glass;` in each file
2. Or set the search_path on the role: `ALTER ROLE postgres SET search_path TO glass, public;`

**Step 3: Verify**

```sql
SET search_path TO glass, public;

-- Check that all tables exist
SELECT tablename FROM pg_tables WHERE schemaname = 'glass' ORDER BY tablename;

-- Check new columns exist
SELECT column_name FROM information_schema.columns 
WHERE table_schema = 'glass' AND table_name = 'operators' 
AND column_name IN ('platform', 'platform_slug', 'metadata');

-- Check matching engine tables
SELECT COUNT(*) FROM glass.canonical_products;
SELECT COUNT(*) FROM glass.product_matches;
SELECT COUNT(*) FROM glass.brand_dictionary;
```

**Test approach:**
1. Run a single-store Dutchie scrape: `DATABASE_URL=... npx tsx scripts/scrape-dutchie.ts --skip-discovery --db --limit 1`
2. Verify data appears in `glass.operators`, `glass.products`, `glass.prices`
3. Run `SELECT * FROM run_product_matching_stage1_stage2();`
4. Verify `canonical_products` and `product_matches` are populated

### 7.2 Improvement #2: Fix CamoFox Crash Recovery

**Problem:** CamoFox crashes after scraping ~27 stores, causing 88.5% of remaining stores to fail with `TypeError: fetch failed` or `browser.newContext: Target page, context or browser has been closed`.

**Root cause:** CamoFox browser processes accumulate memory and crash. The scraper doesn't detect this and keeps trying to use the dead browser.

**Solution: Multi-level resilience**

**File: `src/scripts/lib/browser-pool.ts`**

```typescript
// Add CamoFox health check and auto-restart
async function ensureCamoFoxHealthy(baseUrl: string): Promise<boolean> {
  try {
    const res = await fetch(`${baseUrl}/health`, { signal: AbortSignal.timeout(5000) });
    return res.ok;
  } catch {
    return false;
  }
}

async function restartCamoFox(): Promise<void> {
  console.log('[CamoFox] Restarting...');
  // Kill existing processes
  const { execSync } = await import('child_process');
  try { execSync('pkill -f camoufox || true'); } catch {}
  // Wait for cleanup
  await new Promise(r => setTimeout(r, 3000));
  // Restart
  execSync('cd /data/.openclaw/extensions/camofox-browser && node server.js &', { stdio: 'ignore' });
  // Wait for startup
  for (let i = 0; i < 10; i++) {
    await new Promise(r => setTimeout(r, 2000));
    if (await ensureCamoFoxHealthy('http://localhost:9377')) {
      console.log('[CamoFox] Restarted successfully');
      return;
    }
  }
  throw new Error('CamoFox failed to restart after 20s');
}
```

**File: `src/scripts/scrape-dutchie.ts`**

```typescript
// Wrap each store scrape with health check and retry
async function scrapeStoreWithRecovery(slug: string, ...args: any[]) {
  const MAX_RETRIES = 2;
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      // Health check before each store
      if (!await ensureCamoFoxHealthy(CAMOFOX_URL)) {
        console.log(`[${slug}] CamoFox unhealthy, restarting...`);
        await restartCamoFox();
      }
      return await scrapeStore(slug, ...args);
    } catch (err: any) {
      const msg = err.message || '';
      const isCrash = msg.includes('fetch failed') || 
                       msg.includes('browser has been closed') ||
                       msg.includes('Target page');
      if (isCrash && attempt < MAX_RETRIES) {
        console.log(`[${slug}] CamoFox crash detected (attempt ${attempt+1}), restarting...`);
        await restartCamoFox();
        continue;
      }
      throw err;
    }
  }
}
```

**Also add periodic restart every N stores:**
```typescript
// In main scrape loop
const RESTART_EVERY_N = 30; // Restart CamoFox every 30 stores to prevent memory buildup
for (let i = 0; i < slugs.length; i++) {
  if (i > 0 && i % RESTART_EVERY_N === 0) {
    console.log(`[Maintenance] Restarting CamoFox after ${i} stores...`);
    await restartCamoFox();
  }
  await scrapeStoreWithRecovery(slugs[i], ...);
}
```

**Test approach:**
1. Run Dutchie scraper with `--limit 50`
2. Verify it restarts CamoFox on crash and continues
3. Check success rate > 80%
4. Full run (235 stores) should complete in ~5 hours with restarts

### 7.3 Improvement #3: Platform-Agnostic SKU + Operator Matching

**What:** 
1. Remove platform prefix from `makeSKU()` so same product generates same SKU regardless of platform
2. Build operator matching to link multi-platform sources

**File: `src/scripts/lib/normalizer.ts`**

```typescript
// CHANGE makeSKU() to generate platform-agnostic GPIDs
export function makeSKU(
  brand: string,
  name: string,
  weightGrams: number | undefined,
  category: string,
  _platform = 'DUTCHIE'  // kept for backward compat but no longer used in hash
): string {
  const key = [
    normalizeBrand(brand),
    name.toLowerCase().replace(/[^a-z0-9 ]/g, '').trim(),
    (weightGrams ?? 0).toFixed(1),
    normalizeCategory(category),
  ].join('|');

  // Platform-agnostic GPID
  return `GPID-${crypto.createHash('sha256').update(key).digest('hex').slice(0, 12).toUpperCase()}`;
}
```

**File: `src/scripts/match-operators.ts` (NEW)**

```typescript
#!/usr/bin/env tsx
/**
 * Cross-platform operator matching.
 * Reads slug files from all platforms, matches by normalized name + city,
 * and populates operator_sources table.
 */
import { readFileSync } from 'fs';
import { pool } from './lib/db';

interface SlugRecord {
  slug: string;
  cities: string[];
  nameHint?: string;
}

interface PlatformSlug {
  platform: string;
  slug: string;
  cities: string[];
  normalized: string;
}

function normalizeStoreName(slug: string): string {
  return slug
    .toLowerCase()
    // Strip common suffixes
    .replace(/-(rec|med|menu|adult-use|medical|retail|au|pos-only|retail-rec|adult-use-retail|med-retail)$/g, '')
    .replace(/-(inc|llc|co|dispensary|cannabis|marijuana)$/g, '')
    .replace(/[0-9]+$/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

function levenshtein(a: string, b: string): number {
  const m = a.length, n = b.length;
  const dp: number[][] = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = Math.min(
        dp[i-1][j] + 1,
        dp[i][j-1] + 1,
        dp[i-1][j-1] + (a[i-1] === b[j-1] ? 0 : 1)
      );
    }
  }
  return dp[m][n];
}

function similarity(a: string, b: string): number {
  const maxLen = Math.max(a.length, b.length);
  if (maxLen === 0) return 1;
  return 1 - levenshtein(a, b) / maxLen;
}

async function main() {
  // Load all slug files
  const platforms: { name: string; file: string }[] = [
    { name: 'dutchie', file: 'dutchie-slugs.json' },
    { name: 'weedmaps', file: 'weedmaps-slugs.json' },
    { name: 'leafly', file: 'leafly-slugs.json' },
    { name: 'jane', file: 'jane-slugs.json' },
  ];

  const allSlugs: PlatformSlug[] = [];
  
  for (const p of platforms) {
    try {
      const data: SlugRecord[] = JSON.parse(
        readFileSync(`/data/workspace/projects/glass/src/scripts/${p.file}`, 'utf-8')
      );
      for (const s of data) {
        allSlugs.push({
          platform: p.name,
          slug: s.slug,
          cities: s.cities || [],
          normalized: normalizeStoreName(s.slug),
        });
      }
    } catch {
      console.log(`Skipping ${p.file} — not found`);
    }
  }

  console.log(`Loaded ${allSlugs.length} slugs across ${platforms.length} platforms`);

  // Group by normalized name
  const groups = new Map<string, PlatformSlug[]>();
  for (const s of allSlugs) {
    const existing = groups.get(s.normalized) || [];
    existing.push(s);
    groups.set(s.normalized, existing);
  }

  // Find multi-platform groups
  const multiPlatform = [...groups.entries()]
    .filter(([, slugs]) => new Set(slugs.map(s => s.platform)).size >= 2)
    .sort((a, b) => b[1].length - a[1].length);

  console.log(`\nMulti-platform operator matches: ${multiPlatform.length}`);
  
  for (const [name, slugs] of multiPlatform.slice(0, 20)) {
    const platforms = slugs.map(s => `${s.platform}:${s.slug}`).join(', ');
    console.log(`  ${name} → ${platforms}`);
  }

  // Also do fuzzy matching for near-misses
  const dutchieSlugs = allSlugs.filter(s => s.platform === 'dutchie');
  const otherSlugs = allSlugs.filter(s => s.platform !== 'dutchie');
  
  let fuzzyMatches = 0;
  for (const d of dutchieSlugs) {
    for (const o of otherSlugs) {
      if (d.normalized === o.normalized) continue; // already exact match
      const sim = similarity(d.normalized, o.normalized);
      if (sim >= 0.85) {
        fuzzyMatches++;
        if (fuzzyMatches <= 20) {
          console.log(`  FUZZY (${sim.toFixed(2)}): dutchie:${d.slug} ↔ ${o.platform}:${o.slug}`);
        }
      }
    }
  }
  console.log(`\nFuzzy matches (≥0.85 similarity): ${fuzzyMatches}`);

  await pool.end();
}

main().catch(console.error);
```

**Database migration for operator_sources:**

```sql
-- Apply to glass schema
SET search_path TO glass;

CREATE TABLE IF NOT EXISTS operator_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  platform VARCHAR(20) NOT NULL,
  platform_slug VARCHAR(500) NOT NULL,
  platform_url TEXT NOT NULL,
  match_method VARCHAR(20) NOT NULL DEFAULT 'slug_match',
  match_confidence NUMERIC(5,4) NOT NULL DEFAULT 1.0,
  is_verified BOOLEAN NOT NULL DEFAULT FALSE,
  last_scraped_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_operator_sources_platform_slug UNIQUE (platform, platform_slug)
);

CREATE INDEX IF NOT EXISTS idx_operator_sources_operator ON operator_sources(operator_id);
CREATE INDEX IF NOT EXISTS idx_operator_sources_platform ON operator_sources(platform);
```

**Test approach:**
1. Run `match-operators.ts` — verify it finds 60-80 multi-platform matches
2. Manually verify 10 random matches against actual dispensary websites
3. Check that same-brand same-name products across matched operators generate the same GPID

---

## 8. Timeline to 95%

### Realistic Timeline

```
Week 1 (Feb 13-19): FOUNDATION
├── Day 1-2: Apply DB migrations, fix search_path, verify data pipeline
├── Day 3-4: Fix CamoFox crash recovery, fix Weedmaps scraper
├── Day 5: Run operator matching, first full scrape with resume
└── Milestone: Scraper success rate > 80%, data flowing to DB

Week 2 (Feb 20-26): FIRST GPIDs  
├── Day 1: Run Stage 1+2 matching pipeline
├── Day 2-3: Seed brand dictionary, weight normalization fixes
├── Day 4-5: Build ground truth validation set, measure baseline
└── Milestone: ~70% match rate, baseline accuracy measured

Week 3-4 (Feb 27 - Mar 12): FUZZY MATCHING
├── Tune similarity thresholds based on validation results
├── Category taxonomy sync across all parsers
├── Jane scraper to daily production
├── Leafly scraper stabilization
└── Milestone: ~85% match rate

Month 2 (Mar 13 - Apr 12): AI REVIEW + FEEDBACK
├── Week 5-6: Build AI review pipeline (Stage 3)
├── Week 7: Feedback system MVP ("Wrong price?" button)
├── Week 8: Automated accuracy dashboard
└── Milestone: ~92% match rate, community validation live

Month 3 (Apr 13 - May 12): CONVERGENCE TO 95%
├── Active learning from community corrections
├── Brand dictionary expansion from operator claims
├── Edge case resolution via AI + human review
└── Milestone: 95%+ match rate, <2% false positive rate
```

### Key Dependencies

```
DB Migrations ──→ Scraper Pipeline ──→ Product Data
                                          ↓
Slug Files ──→ Operator Matching ──→ Cross-Platform Links
                                          ↓
                                   Stage 1 Exact Match (70%)
                                          ↓
Brand Dictionary ──→ Stage 2 Fuzzy Match (85%)
                                          ↓
LLM API Access ──→ Stage 3 AI Review (92%)
                                          ↓
Feedback System ──→ Community Validation (95%+)
```

### Risk Factors

| Risk | Mitigation |
|------|-----------|
| CamoFox remains unstable | Migrate Dutchie scraping to Railway browser too |
| Weedmaps blocks all scraping | Use residential proxy rotation, or switch to API if available |
| Too few multi-platform operators | Jane + Leafly add more overlap; focus on brand-level matching instead |
| AI review has high false positive rate | Conservative thresholds (0.80+), human review for 0.60-0.79 |
| Community feedback is too slow | Focus on operator claims first — they have 100% knowledge of their own menus |

### Success Criteria

- [  ] **Week 1:** Scrapers running at 80%+ success rate, data in DB
- [  ] **Week 2:** First GPIDs generated, 60-70% match rate measured
- [  ] **Week 4:** 85% match rate, ground truth validation confirms <5% false positive
- [  ] **Month 2:** 92% match rate, feedback system collecting corrections
- [  ] **Month 3:** 95% match rate, <2% false positive rate, community flywheel operational

---

## Appendix A: SQL Cheat Sheet for Accuracy Monitoring

```sql
-- Set search path for all queries
SET search_path TO glass, public;

-- How many products per platform?
SELECT 
  s.source_type as platform,
  COUNT(DISTINCT p.id) as products,
  COUNT(DISTINCT pr.id) as prices,
  COUNT(DISTINCT o.id) as operators
FROM prices pr
JOIN products p ON pr.product_id = p.id
JOIN sources s ON pr.source_id = s.id
JOIN operators o ON pr.operator_id = o.id
GROUP BY s.source_type;

-- Multi-platform operators (after operator matching)
SELECT 
  o.name,
  array_agg(DISTINCT os.platform) as platforms,
  COUNT(DISTINCT os.platform) as platform_count
FROM operators o
JOIN operator_sources os ON os.operator_id = o.id
GROUP BY o.id, o.name
HAVING COUNT(DISTINCT os.platform) >= 2
ORDER BY platform_count DESC;

-- Products available at multi-platform operators
SELECT 
  cp.gpid,
  cp.brand,
  cp.product_name,
  cp.category,
  cp.weight_grams,
  cp.source_product_count,
  cp.store_count,
  cp.price_min,
  cp.price_max
FROM canonical_products cp
WHERE cp.store_count >= 2
  AND cp.is_active = true
ORDER BY cp.store_count DESC
LIMIT 20;

-- Match rate calculation
SELECT
  COUNT(*) as total_products,
  COUNT(pm.id) as matched_products,
  ROUND(100.0 * COUNT(pm.id) / NULLIF(COUNT(*), 0), 1) as match_rate_pct,
  COUNT(*) FILTER (WHERE pm.match_method = 'exact') as exact_matches,
  COUNT(*) FILTER (WHERE pm.match_method = 'similarity') as fuzzy_matches,
  COUNT(*) FILTER (WHERE pm.match_method = 'ai_review') as ai_matches,
  COUNT(*) FILTER (WHERE pm.id IS NULL) as unmatched
FROM products p
LEFT JOIN product_matches pm ON pm.source_product_id = p.id AND pm.status = 'matched';

-- Staleness report
SELECT 
  s.source_type as platform,
  COUNT(DISTINCT s.id) as sources,
  MIN(s.last_scraped_at) as oldest_scrape,
  MAX(s.last_scraped_at) as newest_scrape,
  AVG(EXTRACT(EPOCH FROM (NOW() - s.last_scraped_at)) / 3600)::int as avg_hours_stale
FROM sources s
WHERE s.status = 'active'
GROUP BY s.source_type;
```

## Appendix B: Brand Dictionary Seed Data (Top 50 MA Brands)

```sql
INSERT INTO brand_dictionary (canonical_brand_name, normalized_key, aliases, is_mso, is_house_brand) VALUES
('Cookies', 'cookies', ARRAY['Cookies', 'COOKIES', 'Cookies Cannabis'], true, false),
('Good Chemistry', 'good chemistry', ARRAY['Good Chemistry', 'GOOD CHEMISTRY', 'Good Chem'], false, false),
('PAX', 'pax', ARRAY['PAX', 'Pax', 'PAX Era'], false, false),
('Fernway', 'fernway', ARRAY['Fernway', 'FERNWAY', 'Fernway Cannabis'], false, false),
('Happy Valley', 'happy valley', ARRAY['Happy Valley', 'HAPPY VALLEY', 'HV'], false, true),
('Theory Wellness', 'theory wellness', ARRAY['Theory Wellness', 'THEORY WELLNESS', 'Theory'], false, true),
('NETA', 'neta', ARRAY['NETA', 'Neta', 'Nature''s Embrace', 'New England Treatment Access'], false, true),
('Curaleaf', 'curaleaf', ARRAY['Curaleaf', 'CURALEAF', 'Curaleaf MA'], true, false),
('INSA', 'insa', ARRAY['INSA', 'Insa', 'INSA Inc'], false, true),
('Trulieve', 'trulieve', ARRAY['Trulieve', 'TRULIEVE'], true, false),
('Cresco Labs', 'cresco labs', ARRAY['Cresco', 'Cresco Labs', 'CRESCO'], true, false),
('GTI', 'gti', ARRAY['GTI', 'Green Thumb Industries', 'Rise'], true, false),
('Ayr Wellness', 'ayr wellness', ARRAY['Ayr', 'AYR', 'Ayr Wellness'], true, false),
('Berkshire Roots', 'berkshire roots', ARRAY['Berkshire Roots', 'BERKSHIRE ROOTS'], false, true),
('Harbor House', 'harbor house', ARRAY['Harbor House', 'Harbor House Collective', 'HARBOR HOUSE'], false, true),
('Garden Remedies', 'garden remedies', ARRAY['Garden Remedies', 'GARDEN REMEDIES'], false, true),
('Smyth Cannabis', 'smyth cannabis', ARRAY['Smyth', 'Smyth Cannabis Co', 'SMYTH'], false, true),
('Liberty Cannabis', 'liberty cannabis', ARRAY['Liberty', 'Liberty Cannabis', 'LIBERTY'], false, false),
('Mass Alternative Care', 'mass alternative care', ARRAY['Mass Alternative Care', 'MAC', 'MASS ALTERNATIVE CARE'], false, true),
('CommCan', 'commcan', ARRAY['CommCan', 'COMMCAN', 'Community Cannabis'], false, true),
('Mayflower', 'mayflower', ARRAY['Mayflower', 'Mayflower Medicinals', 'MAYFLOWER'], false, true),
('Canna Provisions', 'canna provisions', ARRAY['Canna Provisions', 'CANNA PROVISIONS'], false, true),
('Resinate', 'resinate', ARRAY['Resinate', 'RESINATE'], false, true),
('Mission', 'mission', ARRAY['Mission', 'Mission Dispensary', 'MISSION'], false, true),
('Sira Naturals', 'sira naturals', ARRAY['Sira Naturals', 'SIRA', 'Sira'], false, true),
('Ethos', 'ethos', ARRAY['Ethos', 'ETHOS', 'Ethos Cannabis'], true, false),
('Pure Oasis', 'pure oasis', ARRAY['Pure Oasis', 'PURE OASIS'], false, true),
('Rev Clinics', 'rev clinics', ARRAY['Rev Clinics', 'Revolutionary Clinics', 'REV CLINICS', 'RevClinics'], false, true),
('Union Twist', 'union twist', ARRAY['Union Twist', 'UNION TWIST'], false, true),
('Bountiful Farms', 'bountiful farms', ARRAY['Bountiful Farms', 'BOUNTIFUL FARMS', 'Bountiful'], false, true)
ON CONFLICT (canonical_brand_name) DO UPDATE SET
  aliases = (
    SELECT array_agg(DISTINCT val)
    FROM unnest(array_cat(brand_dictionary.aliases, EXCLUDED.aliases)) AS val
  ),
  is_mso = EXCLUDED.is_mso,
  is_house_brand = EXCLUDED.is_house_brand,
  updated_at = NOW();
```

## Appendix C: File Change Summary

| File | Change | Priority |
|------|--------|----------|
| `src/scripts/lib/db.ts` | Add `SET search_path TO glass` on connect | P0 |
| `src/scripts/lib/normalizer.ts` | Remove platform prefix from `makeSKU()` | P2 |
| `src/scripts/lib/normalizer.ts` | Extend `WEIGHT_MAP` with more patterns | P2 |
| `src/scripts/lib/browser-pool.ts` | Add health check + auto-restart for CamoFox | P1 |
| `src/scripts/scrape-dutchie.ts` | Add crash recovery loop with CamoFox restart | P1 |
| `src/scripts/scrape-weedmaps.ts` | Debug and fix 0% success rate | P1 |
| `src/scripts/match-operators.ts` | NEW: Cross-platform operator matching script | P2 |
| `src/scripts/lib/ai-review.ts` | NEW: LLM-based match review for ambiguous pairs | P1 (Month 2) |
| `src/migrations/004_matching_engine.sql` | Apply to database (already written) | P0 |
| `src/scripts/migrations/001-005` | Apply all pending migrations | P0 |
