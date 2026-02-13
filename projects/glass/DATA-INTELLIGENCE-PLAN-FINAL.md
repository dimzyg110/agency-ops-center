# GLASS Data Intelligence — Consolidated Plan (v2)

**Status:** APPROVED — EXECUTION READY  
**Date:** February 13, 2026  
**Updated:** February 13, 2026 — Post-Strategic Review  
**Purpose:** Single actionable plan synthesized from three strategy documents + expert strategic review  
**Audience:** Developers (primary), founder, investors  

---

## The One-Liner

GLASS becomes **Clearbit for Cannabis** — the canonical product database and intelligence layer for a $30B+ industry that has no Bloomberg, no Zillow, no Kelley Blue Book. Every data product we build flows from one foundation: **cross-store product matching**.

> **Core thesis (validated by expert review):** "In a fragmented, immature industry, the entity that normalizes the data layer becomes the monopoly tollbooth." This is the exact playbook CoStar used for commercial real estate, ZoomInfo used for B2B contacts, and Clearbit used for company data.

---

## ⚠️ Strategic Mandate: Foundation First

**HALT all forward-looking product ideation, UI design, and GTM planning until the Product Matching Engine is hitting 95%+ accuracy on existing MA data.**

Every high-value play — Fraud Machine, Supply Chain Graph, Pricing Intelligence, Brand Intelligence — relies on canonical product IDs (GPIDs). Without solving product matching, we have 490 useless CSVs, not a data monopoly.

**The matching engine IS the company right now.** Everything else is a distraction until this works.

---

## What We Have Today

| Dataset | Records | Source |
|---|---|---|
| Scraped products | ~100K | Dispensary menus (Dutchie, Weedmaps, Jane) |
| Price observations | ~117K | Scraped with products |
| CCC licenses | 772 | Massachusetts Cannabis Control Commission |
| Lab tests | 147K | CCC public data |
| Facility sales | 67K | CCC monthly reports |
| Operators (geocoded) | ~490 | Our matched operator database |
| VB chat logs | Growing | Virtual Budtender sessions (early) |

**What already works:** Operator matching (770/772 CCC licenses linked ✅), brand normalization pipeline ✅, geocoded operators ✅, `pg_trgm` extension loaded ✅.

**What doesn't exist yet:** Cross-store product matching ❌, `operator_scores` populated (0 rows) ❌, demand signal aggregation ❌.

---

## Section 1: The Clearbit Play (PRIORITY #1)

### Why This Is the $100M Idea

Every other industry has a canonical product identity layer. Retail has UPC codes. Business data has DUNS numbers. Company enrichment has Clearbit. **Cannabis has nothing.** The same "Blue Dream 3.5g" is listed 50 different ways across 50 stores. Without resolving products to a single identity, every other intelligence feature is impossible.

Whoever builds the canonical product database and gets adoption **owns the data infrastructure for the entire industry.**

### GLASS Product IDs (GPIDs)

Every matched product gets a permanent, unique **GLASS Product ID (GPID)**. This becomes cannabis's UPC equivalent.

```
GPID Format: GP-{CATEGORY_CODE}-{BRAND_HASH}-{PRODUCT_HASH}
Example:     GP-FLW-COOK-GP01    (Cookies - Gary Payton, Flower, 3.5g)
             GP-VAP-FERN-BD01    (Fernway - Blue Dream, Vape Cart, 0.5g)
```

Once POS systems, compliance platforms, and state regulators reference GPIDs, switching costs become massive. We become infrastructure.

### Product Matching Engine (The Foundation)

**What it does:** Takes 100K+ chaotic product listings across ~490 dispensaries and resolves them into canonical product entities. "Fernway Blue Dream Cartridge 0.5g" at Store A and "FERNWAY - Blue Dream Cart .5g" at Store B become ONE canonical product with multiple price observations.

**Architecture — 5-Stage Pipeline:**

```
products table (100K rows)
       │
       ▼
┌──────────────────┐
│ Stage 1: Normalize │  brand, name, weight, category → fingerprint
│ (deterministic)    │
└────────┬───────────┘
         ▼
┌──────────────────┐
│ Stage 2: Block     │  group by (norm_brand, category, weight_bucket)
│ (reduce N²)       │  reduces 5B comparisons to ~500K
└────────┬───────────┘
         ▼
┌──────────────────┐
│ Stage 3: Score     │  pg_trgm similarity on name, strain, THC%, weight
│ (pairwise)         │  within each block
└────────┬───────────┘
         ▼
┌──────────────────┐
│ Stage 4: AI Review │  Low-confidence (0.45-0.55) → LLM classification
│ (automated)        │  Claude Haiku / GPT-4o-mini via JSON schema
└────────┬───────────┘
         ▼
┌──────────────────┐
│ Stage 5: Cluster   │  Union-Find on high-confidence pairs
│ (transitivity)     │  → canonical_product_id + GPID
└────────┬───────────┘
         ▼
canonical_products + product_matches tables
```

> **Technical Decision (from expert review):** Stage 4 replaces human-in-the-loop review for edge cases. Pipe low-confidence matches (0.45–0.55 similarity) through a cheap LLM with a strict JSON schema prompt: `{"is_match": true/false, "confidence": 0-100, "reason": "..."}`. This resolves ~80% of edge cases for pennies and prevents the human review queue from crushing velocity.

**Normalization functions** (TypeScript batch job):
- `normalizeBrandForMatching()` — lowercase, strip suffixes (Inc, LLC), apply alias map
- `extractWeight()` — parse "3.5g", "1/8 oz", "1000mg" from product names → grams
- `extractStrainName()` — strip brand prefix, weight, category words → raw strain name
- `buildFingerprint()` — deterministic hash for exact-match dedup before fuzzy matching

**Blocking strategy** (prevents N² explosion):
- Block on: `category` + `weight_bucket` (0-1g, 1-4g, 4-8g, etc.) + `norm_brand` (or name prefix if no brand)
- Expected block sizes: 50-200 for branded products
- Sub-block by name prefix if block exceeds 500

**Similarity scoring** (PostgreSQL `pg_trgm` + custom function):

| Factor | Weight | Criteria |
|---|---|---|
| Name similarity (trigram) | 35% | Cleaned product name comparison |
| Brand match | 25% | Exact normalized brand match |
| Strain similarity | 20% | Normalized strain name comparison |
| THC% proximity | 10% | Within 2% = full score, >10% = zero |
| Weight match | 10% | Within 0.1g = full, different = zero |

**Confidence tiers:**

| Score | Confidence | Action |
|---|---|---|
| ≥ 0.90 | `auto_match` | Linked automatically |
| 0.75–0.89 | `high` | Linked, flagged for spot-check |
| 0.55–0.74 | `medium` | Queued for spot-check |
| 0.45–0.54 | `ai_review` | **Routed to LLM for classification** |
| < 0.45 | `no_match` | Not linked |

**Accuracy target:** 95%+ precision. False matches are worse than missed matches — a wrong match could attribute incorrect lab results to a product.

**Estimated canonical products:** 8,000–15,000 unique products from 100K listings (avg 5-12 store variants each; heavily skewed — top brands at 50+ stores, house brands at 1).

### Schema: Core Tables

```sql
-- CANONICAL PRODUCTS — One record per real-world product
CREATE TABLE canonical_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gpid VARCHAR(50) UNIQUE,                    -- GLASS Product ID
  name VARCHAR(500) NOT NULL,
  brand VARCHAR(255),
  category VARCHAR(50) NOT NULL,
  weight_grams DECIMAL(10, 3),
  strain_name VARCHAR(100),
  strain_type VARCHAR(50),
  thc_percent_avg DECIMAL(5, 2),
  cbd_percent_avg DECIMAL(5, 2),
  source_product_count INTEGER NOT NULL DEFAULT 1,
  store_count INTEGER NOT NULL DEFAULT 1,
  confidence_avg DECIMAL(3, 2),
  price_min DECIMAL(10, 2),
  price_max DECIMAL(10, 2),
  price_avg DECIMAL(10, 2),
  price_median DECIMAL(10, 2),
  price_spread_pct DECIMAL(5, 2),
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- PRODUCT MATCHES — Links store-level products to canonical
CREATE TABLE product_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  canonical_product_id UUID NOT NULL REFERENCES canonical_products(id) ON DELETE CASCADE,
  confidence DECIMAL(3, 2) NOT NULL,
  match_method VARCHAR(20) NOT NULL,   -- 'exact_fingerprint', 'similarity', 'ai_review', 'manual'
  similarity_score DECIMAL(5, 4),
  ai_review_result JSONB,             -- LLM response for ai_review matches
  matched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  verified_by VARCHAR(50),
  verified_at TIMESTAMPTZ,
  CONSTRAINT uq_product_match UNIQUE (product_id)
);

-- BRAND DICTIONARY — Canonical brand names with aliases
CREATE TABLE brand_dictionary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_name VARCHAR(255) NOT NULL UNIQUE,
  aliases JSONB NOT NULL DEFAULT '[]',
  parent_company VARCHAR(255),
  license_number VARCHAR(30),
  operator_id UUID REFERENCES operators(id),
  is_house_brand BOOLEAN NOT NULL DEFAULT FALSE,
  product_count INTEGER NOT NULL DEFAULT 0,
  store_count INTEGER NOT NULL DEFAULT 0,
  categories JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- MATCHING RUNS — Audit trail
CREATE TABLE matching_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status VARCHAR(20) NOT NULL DEFAULT 'running',
  products_processed INTEGER NOT NULL DEFAULT 0,
  exact_matches INTEGER NOT NULL DEFAULT 0,
  similarity_matches INTEGER NOT NULL DEFAULT 0,
  ai_review_matches INTEGER NOT NULL DEFAULT 0,
  new_canonicals INTEGER NOT NULL DEFAULT 0,
  unmatched INTEGER NOT NULL DEFAULT 0,
  similarity_threshold DECIMAL(3, 2) NOT NULL DEFAULT 0.75,
  ai_review_count INTEGER NOT NULL DEFAULT 0,
  ai_review_cost_usd DECIMAL(6, 4),
  config JSONB NOT NULL DEFAULT '{}',
  error_log JSONB DEFAULT '[]'
);

-- Products table additions (fingerprint columns)
ALTER TABLE products ADD COLUMN IF NOT EXISTS norm_brand VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS norm_name VARCHAR(300);
ALTER TABLE products ADD COLUMN IF NOT EXISTS weight_grams DECIMAL(10, 3);
ALTER TABLE products ADD COLUMN IF NOT EXISTS strain_name VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS fingerprint_key VARCHAR(500);
ALTER TABLE products ADD COLUMN IF NOT EXISTS canonical_product_id UUID;
```

### API Tiers (The Monetization Layer)

| Tier | Price | Access | Target |
|---|---|---|---|
| **Free** | $0 | Product lookup by GPID (basic info: name, brand, category) | Developers, POS companies (adoption play) |
| **Starter** | $99/mo | 1,000 calls/mo, aggregated pricing, market averages | Small POS integrators |
| **Pro** | $499/mo | 10,000 calls/mo, product-level pricing, real-time data | Operators, brands |
| **Enterprise** | Custom | Unlimited, raw data, webhooks, custom exports | MSOs, investors, regulators |

**Key API endpoints:**
```
GET /api/v1/products/lookup?name=...&brand=...  → GPID + canonical data
GET /api/v1/products/:gpid/prices               → All store prices
GET /api/v1/brands/:name/distribution            → Where brand is sold
GET /api/v1/market/prices?category=...           → Market averages
GET /api/v1/operators/:id/products               → Full catalog
```

### Network Effects

```
More operators scraped → More products matched → Better matching accuracy
→ More canonical products → More API consumers → More data contributions
→ Even better matching → Harder to replicate
```

Each layer compounds. A competitor would need to replicate historical data (years of scrapes), the trained matching model (100K+ human-corrected matches), and API adoption simultaneously. That's 18-24 months and millions of dollars.

---

## Section 2: GTM Strategy — Dual-Path Approach

> **Strategic decision (from expert review):** Run Path A (Operator SaaS) for distribution + data validation. Focus sales energy on Path B (Brand Intelligence / Whales) for revenue. This is not "do both" — it's "use Path A as infrastructure for Path B."

### Path A: Trojan Horse Bootstrapper (Distribution + Data QA)

**Focus:** Operator SaaS ($199/mo) + Pricing Intelligence

| Attribute | Detail |
|---|---|
| **Purpose** | Not primarily for revenue — operators act as **free QA for the matching engine** |
| **How it works** | When Store A complains you incorrectly matched their pre-roll to Store B's, they're cleaning your $100M dataset for you |
| **Price** | $199/mo (low enough to minimize sales friction) |
| **Target** | 30-50 dispensary operators in MA |
| **Risk** | Cash-strapped SMBs, high support burden, churn |
| **Mitigation** | Keep the product dead simple. No feature creep. Dashboard + alerts only. |

**What operators get:**
- Store Report Card (scores, rankings)
- Price Wire (price change alerts on their products and competitors')
- Threat Radar (new competitors, product overlaps within radius)
- Basic competitive radius analysis

### Path B: Whale Hunter (Revenue Engine)

**Focus:** Brand Intelligence + Supply Chain Graph

| Attribute | Detail |
|---|---|
| **Purpose** | Primary revenue driver. High ACV, low customer count needed. |
| **Target** | Top 20 Cultivators, MSOs, Private Equity firms |
| **Pitch** | *"14 of your retail partners are selling below MAP, and your live rosin sits on shelves 40% longer in Worcester than in Boston. Here are the receipts."* |
| **Price** | $2,000–$5,000/mo |
| **Revenue math** | 10 customers = $50K MRR. Only need 10. |
| **Delivery format** | PDFs, data drops, API access — **not a beautiful SaaS UI** |
| **Why this works** | Brands/MSOs/PE have actual money and actual pain. Distribution visibility, MAP enforcement, and quality benchmarking are problems they'll pay $5K/mo to solve. |

**What whales get:**
- Distribution tracking across all 490 stores
- MAP violation detection ("14 retailers selling below your MAP")
- Competitor brand analysis (shelf space, pricing, velocity proxies)
- Cultivator quality rankings (lab test consistency scores)
- Supply chain mapping (who's actually moving your product)
- Wholesale-to-retail markup analysis

### The Sequence

```
Month 1-2: Build matching engine → generate GPIDs → hit 95% accuracy
Month 2-3: Hand-deliver data PDFs to validate willingness-to-pay
Month 3:   Launch Path A dashboard (simple, automated)
Month 3+:  Flip to Path B — call whales with $5K/mo contracts
```

**Critical insight:** You don't need a beautiful frontend to sell Path B. Package insights as PDF reports or raw data exports. The $5K/mo customer wants answers, not pixels.

---

## Section 3: What We Build Now (Priority-Ordered)

### System 1: Product Matching Engine

**Priority: P0 — THE ENTIRE COMPANY DEPENDS ON THIS**

| Attribute | Detail |
|---|---|
| **What it does** | Resolves 100K product listings into ~10K canonical products with GPIDs |
| **Data we need** | Scraped products ✅, brand normalization ✅, pg_trgm ✅ |
| **Technical approach** | 5-stage pipeline (normalize → block → score → AI review → cluster) in PostgreSQL + TypeScript |
| **Revenue potential** | Indirect — enables every other revenue stream; direct via API licensing ($6K-$50K/yr) |
| **Effort** | 50 hours + 8 hours for AI review integration |
| **Dependencies** | None — can start today |
| **Accuracy gate** | **Do not proceed to any other system until matching hits 95%+ precision** |

**Quick wins before full build:**
1. **Fix MV bug** (`ccc_avg_prices` → `ccc_monthly_prices` reference) — 1 hour
2. **Populate `operator_scores`** (run `refresh_health_scores()`) — 2 hours
3. **Brand dictionary bootstrap** from existing product data — 4 hours

### System 2: Pricing Intelligence

**Priority: P1 — Direct operator value, partially works without matching**

| Attribute | Detail |
|---|---|
| **What it does** | Detects price changes, identifies arbitrage, tracks market pricing |
| **Data we need** | Prices table ✅, product matching (for cross-store comparison) |
| **Technical approach** | Daily batch job comparing consecutive scrapes; significance scoring filters noise |
| **Revenue potential** | Core justification for $199/mo operator subscription; premium alerts at $499/mo |
| **Effort** | 34 hours |
| **Dependencies** | Basic features work now; cross-store comparison needs product matching |

**Key features:**

1. **Price Change Detection** — Daily pipeline comparing consecutive scrapes per product per operator. Significance scoring:
   - < 2% change → noise (ignore)
   - 2-5% → minor (log only)
   - 5-15% → significant (alert operator)
   - > 15% → major (immediate alert)

2. **Arbitrage Opportunities** — Same canonical product priced 30%+ differently at nearby stores.

3. **Coordinated Pricing Detection** — 3+ operators changing same product in same direction within 48 hours. Present data only (not conclusions).

4. **Price Events Table:**

```sql
CREATE TABLE price_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id),
  canonical_product_id UUID REFERENCES canonical_products(id),
  operator_id UUID NOT NULL REFERENCES operators(id),
  event_type VARCHAR(30) NOT NULL,  -- 'price_drop', 'price_increase', 'new_product', 'delisted'
  old_price DECIMAL(10, 2),
  new_price DECIMAL(10, 2),
  change_pct DECIMAL(6, 2),
  significance_score DECIMAL(3, 2) NOT NULL,
  is_significant BOOLEAN NOT NULL DEFAULT FALSE,
  market_avg_price DECIMAL(10, 2),
  detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Quick win (before matching):** Price change alerts on per-store products. Alert when any product at an operator changes >15%. Effort: 1 day.

### System 3: Competitive Radius Analysis

**Priority: P1 — High operator value, straightforward to build**

| Attribute | Detail |
|---|---|
| **What it does** | For each operator: who are your competitors, what products overlap, who's cheaper |
| **Data we need** | Geocoded operators ✅, product matching (for overlap), prices ✅ |
| **Technical approach** | Haversine distance query (already used in codebase) + precomputed competitor pairs |
| **Revenue potential** | Core value prop for $199/mo tier; competitive deep-dive at $499/mo |
| **Effort** | 25 hours |
| **Dependencies** | Geocoding ✅; product overlap needs matching from System 1 |

**Schema:**

```sql
CREATE TABLE competitor_pairs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID NOT NULL REFERENCES operators(id),
  competitor_id UUID NOT NULL REFERENCES operators(id),
  distance_miles DECIMAL(6, 2) NOT NULL,
  shared_canonical_count INTEGER,
  overlap_pct DECIMAL(5, 2),
  avg_price_delta DECIMAL(10, 2),
  avg_price_delta_pct DECIMAL(6, 2),
  cheaper_count INTEGER,
  pricier_count INTEGER,
  calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_competitor_pair UNIQUE (operator_id, competitor_id)
);
```

**API endpoints:**
- `GET /api/v1/operators/:id/competitors` — Sorted list within radius
- `GET /api/v1/operators/:id/competitors/:competitor_id/comparison` — Product-by-product price comparison
- `GET /api/v1/operators/:id/price-position` — Where you sit in your market

**Quick win (before matching):** Nearest-N-competitors query using existing geocoding. Just distance + names. Effort: 1 day.

### System 4: Supply Chain Intelligence

**Priority: P2 — Unlocks Path B (Whale Hunter) revenue**

| Attribute | Detail |
|---|---|
| **What it does** | Maps cultivator → manufacturer → retailer relationships; quality rankings; markup analysis |
| **Data we need** | CCC licenses ✅, lab tests ✅, product matching (from System 1), facility sales ✅ |
| **Technical approach** | Entity resolution from CCC data + inference from product/brand matching. **PostgreSQL recursive CTEs only — no Neo4j.** |
| **Revenue potential** | Cultivator intelligence ($2,500–$5,000/mo to PE/MSOs); brand distribution tracking |
| **Effort** | 35 hours |
| **Dependencies** | Product matching for brand→retailer links; CCC data already loaded |

**What we can build today (no product matching needed):**

1. **Cultivator Quality Rankings** — Which cultivators have best/most consistent lab results:
```sql
-- Materialized view: cultivator quality by product category
-- Columns: cultivator_name, test_count, avg_thc, thc_stddev, 
--          median_thc, p90_thc, consistency_score
-- Consistency = 1 - (stddev / mean) → higher = more consistent
```

2. **Same-Entity Detection** — Companies with multiple license types at same address = vertically integrated.

3. **Wholesale-to-Retail Markup** — CCC publishes transfer prices; we have retail prices. Delta = retail markup.

4. **Entity Graph** — Shared business names, addresses, registered agents across licenses.

**What needs product matching (built after 95% accuracy gate):**

5. **Brand → Retailer Distribution** — brand_dictionary links to retailer product catalogs.
6. **Cultivator → Retailer Connection** — Inference from brand matching + lab test fingerprints.

**Supply Chain Links Schema:**
```sql
CREATE TABLE supply_chain_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cultivator_license VARCHAR(30) NOT NULL,
  cultivator_name VARCHAR(500),
  retailer_operator_id UUID REFERENCES operators(id),
  link_type VARCHAR(30) NOT NULL,    -- 'same_entity', 'brand_match', 'address_match'
  confidence DECIMAL(3, 2) NOT NULL,
  evidence JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Section 4: What We Kill (And Why)

### ❌ KILLED: Consumer App ("Kayak for Weed")

**Why:** B2C user acquisition is a bottomless money pit. Let Weedmaps burn their cash on consumer marketing. We are B2B infrastructure. Revisit only when B2B profits can fully fund a consumer marketing team. **This is not a "later" — it's a "never unless proven otherwise."**

### ❌ KILLED: State-in-a-Box (Regulatory Suite)

**Why:** Government procurement takes 12–24 months. We can start conversations, but do not build software for regulators until they have signed an LOI. Revisit Year 2-3.

### ❌ KILLED: Demand Signal Pipeline (NLP from VB Queries)

**Why:** Parsing intent from Budtender chat logs is notoriously messy and an endless engineering time-sink. Sell hard numbers (pricing, supply chain, lab results) first. Revisit when VB generates 50+ queries/day per operator consistently.

### ❌ KILLED: "The Fraud Machine" — Lab Test Integrity / Litigation Support

**Why:**
- Defamation risk ($50K+ to defend, even if you win)
- Labs and cultivators are potential customers — alienating them before we have market power is bad business
- Not core to the Clearbit play

**What we keep:** Aggregate quality rankings from lab test data (cultivator consistency scores) — that's benchmarking, not fraud accusation. Kept as a **back-pocket play for Month 6+** if we need a PR event to force State Regulators to take our meeting. If activated: sell the shovel, not the dig. Launch a sterilized "GLASS Integrity Index" and let regulators/journalists draw conclusions.

### ❌ KILLED: "The Ownership Graph" — Follow the Money

**Why:** Requires external data we don't have. "Exposing powerful people with lawyers" when we're a startup = suicide.

**What we keep:** Same-entity detection from CCC license data (public, factual, non-controversial).

### ❌ KILLED: Cannabis Credit Scoring / Lending Platform

**Why:** FCRA regulatory complexity, requires data we don't have, Series B play not seed-stage.

### ❌ KILLED: Neo4j Graph Database

**Why:** PostgreSQL recursive CTEs handle our scale (772 licenses, ~10K supply chain links). Adding Neo4j = massive DevOps overhead for zero benefit at MA scale.

### ❌ KILLED: "Regulatory Protection Racket" / Compliance Monitoring Upsell

**Why:** The framing is coercive. Bad brand. We can offer compliance value without implicit threats.

---

## Section 5: 90-Day Execution Roadmap (Developer-Ready)

> **This replaces all previous quarterly roadmaps. This is what gets built. Nothing else.**

### Month 1: The Data Sandbox (Weeks 1–4)

**Goal:** Matching engine live, GPIDs generated, basic price views working.  
**Gate:** Do not advance to Month 2 until matching hits 90%+ precision on a 1,000-product sample.

#### Week 1: Quick Wins + Foundation (35 hours)

| # | Task | Effort | Owner | Output |
|---|---|---|---|---|
| 1 | Fix `ccc_avg_prices` → `ccc_monthly_prices` MV bug | 1 hr | Dev | Working materialized view |
| 2 | Populate `operator_scores` (run `refresh_health_scores()`) | 2 hrs | Dev | Dashboard data live |
| 3 | Schedule daily score refresh (pg_cron or external cron) | 4 hrs | Dev | Automated freshness |
| 4 | Product fingerprint columns + migration | 8 hrs | Dev | `norm_brand`, `norm_name`, `weight_grams`, `strain_name`, `fingerprint_key` on products table |
| 5 | Brand dictionary bootstrap from existing product data | 4 hrs | Dev | ~700 canonical brands with aliases |
| 6 | Basic price change SQL views (per-store, no matching) | 8 hrs | Dev | `price_events` populated, >15% change alerts |
| 7 | Nearest-N-competitors query (distance only, no overlap) | 8 hrs | Dev | `GET /operators/:id/competitors` returning distance-sorted list |

**Deliverable:** Working quick-win features that demonstrate value while matching engine is being built.

#### Week 2–3: Product Matching Engine — Core (52 hours)

| # | Task | Effort | Owner | Output |
|---|---|---|---|---|
| 8 | Fingerprint computation for all 100K products | 8 hrs | Dev | All products have `fingerprint_key` |
| 9 | Exact fingerprint matching (dedup) | 4 hrs | Dev | High-precision exact matches linked |
| 10 | Blocking strategy implementation | 6 hrs | Dev | Products grouped into blocks of 50-200 |
| 11 | Pairwise similarity scoring (`pg_trgm` functions) | 12 hrs | Dev | Similarity scores computed within blocks |
| 12 | **AI Review pipeline for 0.45-0.55 confidence band** | 8 hrs | Dev | LLM integration (Haiku/mini) with JSON schema. Batch processing. Cost tracking per run. |
| 13 | Union-Find clustering + canonical product creation | 8 hrs | Dev | `canonical_products` table populated |
| 14 | GPID assignment system | 4 hrs | Dev | Every canonical product has a GPID |
| 15 | Canonical product pricing summary refresh | 4 hrs | Dev | Denormalized price stats on canonical_products |
| 16 | Incremental daily matching for new products | 6 hrs | Dev | New scrapes auto-matched nightly |

**AI Review Implementation Detail:**
```typescript
// Stage 4: AI Review for low-confidence matches
interface AIMatchRequest {
  product_a: { name: string; brand: string; category: string; weight: string; thc: string };
  product_b: { name: string; brand: string; category: string; weight: string; thc: string };
}

interface AIMatchResponse {
  is_match: boolean;
  confidence: number;  // 0-100
  reason: string;
}

// Prompt template:
// "You are a cannabis product matching expert. Determine if these two product 
//  listings refer to the same real-world product. Consider brand, strain name, 
//  weight, category, and THC%. Respond in JSON only."
//
// Model: claude-3-haiku or gpt-4o-mini (whichever is cheaper)
// Batch size: 100 pairs per API call
// Expected cost: ~$0.10 per 100 pairs
// Expected volume: 2,000-5,000 pairs in 0.45-0.55 band
```

**Deliverable:** `canonical_products` table populated with 8,000–15,000 products. `product_matches` linking 100K listings. Accuracy measured and reported.

#### Week 4: Accuracy Validation + Tuning (20 hours)

| # | Task | Effort | Owner | Output |
|---|---|---|---|---|
| 17 | Sample 500 matches across confidence tiers, manually verify | 8 hrs | Dev + Founder | Accuracy report: precision/recall per tier |
| 18 | Adjust thresholds based on validation results | 4 hrs | Dev | Tuned confidence tiers |
| 19 | Fix systematic errors (common brand aliases, weight parsing edge cases) | 8 hrs | Dev | Improved matching accuracy |

**Gate check:** If precision < 90% → stay in Month 1 until fixed. Do not proceed.

**Month 1 Total: ~107 hours**

---

### Month 2: Proof of Magic (Weeks 5–8)

**Goal:** Validate willingness-to-pay with real humans. First cash. Matching engine approaching 95%.  
**Gate:** Do not build a SaaS dashboard until 10 humans have said "yes I'd pay for this."

#### Week 5–6: Path A Validation — Operator Value (20 hours)

| # | Task | Effort | Owner | Output |
|---|---|---|---|---|
| 20 | Generate 10 operator-specific competitive reports (PDF/data) | 8 hrs | Dev | 10 PDFs showing: your prices vs. competitors, products you're missing, where you're expensive |
| 21 | Hand-deliver reports to 10 dispensary owners | 8 hrs | Founder | Direct feedback: would you pay $199/mo? What's useful? What's wrong? |
| 22 | Log all matching errors reported by operators → feed back into engine | 4 hrs | Dev | Real-world QA data |

**Deliverable:** 10 conversations with operators. Clear signal on willingness-to-pay. Matching engine errors identified and queued.

#### Week 6–7: Path B Validation — Whale Value (20 hours)

| # | Task | Effort | Owner | Output |
|---|---|---|---|---|
| 23 | Build "Cultivator Quality Rankings" materialized view | 4 hrs | Dev | Ranked list: cultivator × category × consistency_score |
| 24 | Build "Brand Distribution Map" query (brand × stores × prices) | 4 hrs | Dev | For any brand: where sold, at what price, vs. MAP |
| 25 | Package as "MA Cannabis Market Intelligence Q1 2026" PDF | 8 hrs | Dev | Professional report with charts/tables |
| 26 | Sell report to 5 PE firms / cultivators for $2,500 each | 4 hrs | Founder | $12,500 revenue. Validates Path B pricing. |

**Deliverable:** First revenue ($12,500). Clear signal on whale willingness-to-pay.

#### Week 7–8: Matching Engine Hardening (25 hours)

| # | Task | Effort | Owner | Output |
|---|---|---|---|---|
| 27 | Incorporate operator QA feedback into matching rules | 8 hrs | Dev | Higher accuracy |
| 28 | Competitive intelligence: product overlap computation | 6 hrs | Dev | `shared_canonical_count` on competitor_pairs |
| 29 | Competitive intelligence: price positioning per competitor | 4 hrs | Dev | "You're 12% cheaper than Store B on average" |
| 30 | Cross-store price comparison (requires matching) | 4 hrs | Dev | Same product, different prices, different stores |
| 31 | Run full accuracy validation again (500-product sample) | 3 hrs | Dev | Accuracy report v2 |

**Gate check:** If precision < 95% → continue hardening. Do not launch SaaS dashboard.

**Month 2 Total: ~65 hours**

---

### Month 3: SaaS Launch + The Flip (Weeks 9–12)

**Goal:** Automated operator dashboard live. Whale contracts signed.  
**Gate:** Matching engine at 95%+ before launching automated dashboard.

#### Week 9–10: Operator Dashboard (Path A Launch) (40 hours)

| # | Task | Effort | Owner | Output |
|---|---|---|---|---|
| 32 | Operator dashboard — Store Report Card view | 12 hrs | Dev | Scores, rankings, health metrics |
| 33 | Operator dashboard — Price Wire (price change alerts) | 8 hrs | Dev | Significant price changes, competitor moves |
| 34 | Operator dashboard — Threat Radar (competitive radius) | 8 hrs | Dev | Nearby competitors, product overlap, price position |
| 35 | Stripe subscription integration ($199/mo) | 8 hrs | Dev | Self-serve signup and billing |
| 36 | Email alert system (daily digest of significant events) | 4 hrs | Dev | Operators get daily email with key changes |

**Deliverable:** Live SaaS product. First paying operator subscribers.

#### Week 11–12: The Flip to Path B (Whale Hunting) (25 hours)

| # | Task | Effort | Owner | Output |
|---|---|---|---|---|
| 37 | Brand-specific intelligence reports (automated generation) | 8 hrs | Dev | Per-brand: distribution, pricing, MAP violations, competitor analysis |
| 38 | Supply chain links (brand → manufacturer → retailer via CCC data) | 6 hrs | Dev | `supply_chain_links` table populated |
| 39 | Same-entity detection (multi-license matching) | 4 hrs | Dev | Vertically integrated companies identified |
| 40 | Wholesale-to-retail markup analysis view | 3 hrs | Dev | Category × month markup percentages |
| 41 | **Whale outreach: call Top 20 cultivators/MSOs/PE for $5K/mo contracts** | 4 hrs | Founder | Target: 3-5 signed contracts |

**Deliverable:** Path B revenue pipeline active. Target: $15K-$25K MRR from whale contracts.

**Month 3 Total: ~65 hours**

---

### 90-Day Summary

| Month | Focus | Hours | Key Output | Revenue Target |
|---|---|---|---|---|
| Month 1 | Data Sandbox | 107 hrs | Matching engine live, GPIDs assigned, 90%+ accuracy | $0 |
| Month 2 | Proof of Magic | 65 hrs | 10 operator conversations, $12.5K from report sales | $12,500 (one-time) |
| Month 3 | SaaS Launch + Flip | 65 hrs | Operator dashboard live, whale contracts | $15K-$25K MRR |
| **Total** | | **237 hrs** | | **$15K-$25K MRR** |

**237 hours ≈ 6 developer-weeks.** This is achievable with 1 full-time developer in 12 calendar weeks, or 2 developers in 6 weeks.

---

## Section 6: Technical Architecture Decisions

> Decisions locked based on expert review + current stack reality. Do not revisit without founder approval.

### 6.1 Database: PostgreSQL Only (No Neo4j, No Separate TimescaleDB)

| Decision | Rationale |
|---|---|
| **No Neo4j** | 772 licenses and ~10K supply chain links is not a graph-at-scale problem. PostgreSQL `WITH RECURSIVE` CTEs handle ownership/supply chain hops trivially at MA scale. Adding Neo4j = new ops burden for zero benefit. |
| **TimescaleDB as extension** | If we need time-series optimizations for pricing data, install `timescaledb` extension on existing Postgres instance. Do NOT spin up a separate database service. Keep the stack boring. |
| **No InfluxDB** | Same reasoning as TimescaleDB. We're already on Postgres via Railway. One database. |

### 6.2 AI for Matching (Stage 4)

| Decision | Rationale |
|---|---|
| **LLM for edge cases** | Low-confidence matches (0.45–0.55 similarity) go through Claude Haiku or GPT-4o-mini instead of human review queue. JSON schema prompt: `{"is_match": true/false, "confidence": 0-100, "reason": "..."}` |
| **Cost model** | ~$0.10 per 100 pair evaluations. Expected 2,000–5,000 pairs in the ambiguous band = $2-$5 total per full matching run. |
| **Fallback** | If LLM confidence < 60% on its own assessment → still queue for human review. This should be < 5% of edge cases. |
| **Audit trail** | Store full LLM response in `product_matches.ai_review_result` for quality monitoring. |

### 6.3 Scraper Risk Mitigation (Existential Threat)

> **WARNING:** The entire vision depends on scraping. If Dutchie/Jane implements strict Cloudflare bot protection, we die overnight.

| Risk | Mitigation |
|---|---|
| **Scraping blocked** | Use the $199/mo Operator SaaS as a Trojan horse. Offer the pricing tier for **free** in exchange for read-only API access to their POS system. Once we're inside the POS via API, we have an unblockable data feed. |
| **Legal risk** | Scraping public menu data is legally defensible (hiQ v. LinkedIn). But API access is legally bulletproof AND higher quality. |
| **Data quality** | API feeds > scraped data. Structured, real-time, no parsing errors. Actively pursue POS integrations. |
| **Priority** | This is a Month 4-6 initiative. Don't build POS integrations before the matching engine works. But start conversations with POS companies now. |

**POS Integration Strategy (Post-90-Day):**
```
Phase 1: Offer "free competitive intelligence tier" to operators
         who grant read-only POS API access
Phase 2: Build lightweight POS adapters (Dutchie, Jane, Blaze)
Phase 3: As API feeds grow, reduce scraping dependency
Phase 4: Eventually, API feeds > scraped data → scrapers become backup
```

### 6.4 Stack Summary

| Layer | Technology | Notes |
|---|---|---|
| Database | PostgreSQL (Railway) | Single instance. `pg_trgm`, `pg_cron` extensions. TimescaleDB if needed later. |
| Backend | TypeScript + Elysia/Hono | Existing stack. No new frameworks. |
| Matching engine | TypeScript batch jobs + PostgreSQL | Normalize in TS, score in PG, cluster in TS |
| AI review | Claude Haiku / GPT-4o-mini API | For 0.45-0.55 confidence band only |
| Competitive radius | Haversine SQL | No PostGIS needed at MA scale |
| MV refresh | pg_cron or external cron | Daily refresh sufficient |
| Frontend | Existing stack | Minimal investment until Month 3 |
| Delivery (Path B) | PDF generation (Python/TS) | Whales want data, not dashboards |

---

## Section 7: Revenue Model

### Subscription Tiers (Path A — Operators)

| Tier | Price | Target | Features |
|---|---|---|---|
| **Free / Public** | $0 | Lead gen | Market page, state-level stats |
| **Operator Standard** | $199/mo | Dispensaries | Store Report Card, Price Wire, Threat Radar, basic competitive radius, 1 store |
| **Operator Pro** | $499/mo | Multi-store operators | Up to 5 stores, price change alerts, arbitrage opps, product gap analysis |
| **Operator Enterprise** | $999-$2,499/mo | MSOs | Unlimited stores, API access, supply chain intel, custom reports |

### Brand Intelligence (Path B — Whales)

| Package | Price | Includes |
|---|---|---|
| **Brand Standard** | $2,000/mo | Distribution map, pricing overview, MAP violation alerts, 1 brand |
| **Brand Pro** | $3,500/mo | + Competitor analysis, quality rankings, 3 brands |
| **Brand Enterprise** | $5,000/mo | + Supply chain intel, custom alerts, unlimited brands, raw data exports |
| **One-Time Reports** | $2,500–$5,000 | Market overview, competitive landscape, market entry analysis |

### API Revenue (Future — Post-90-Day)

| Tier | Price | Volume | Target |
|---|---|---|---|
| Free | $0 | 100 calls/day | Adoption play for POS companies |
| Starter | $99/mo | 1,000 calls | Small integrators |
| Pro | $499/mo | 10,000 calls | POS companies, compliance platforms |
| Enterprise | Custom | 100K+ | Large integrators, data resellers |

### Revenue Projections (Revised — Conservative)

| Revenue Stream | Month 3 | Month 6 | Month 12 |
|---|---|---|---|
| Path A: Operator subscriptions | $2K MRR | $6K MRR | $12K MRR |
| Path B: Whale contracts | $15K MRR | $30K MRR | $60K MRR |
| One-time reports | $5K | $10K | $25K |
| API licensing | $0 | $1K MRR | $5K MRR |
| **Total MRR** | **$17K** | **$37K** | **$77K** |
| **Total ARR (annualized)** | **$204K** | **$444K** | **$924K** |

**Key insight from expert review:** You only need **10 whale customers at $5K/mo = $50K MRR**. Path B is the revenue engine. Path A is the data validation engine.

### Unit Economics

| Metric | Path A (Operators) | Path B (Whales) |
|---|---|---|
| CAC (estimated) | $500 (outbound sales) | $2,000 (longer sales cycle) |
| ACV | $2,388/yr | $36,000/yr |
| LTV (18mo avg) | $3,582 | $54,000 |
| LTV:CAC ratio | 7.2x | 27x |
| Gross margin | ~85% | ~90% |

---

## Section 8: Critical Path

```
Fix MV bug → Populate scores → Fingerprinting → Exact match dedup
→ Similarity matching → AI review for edge cases → Canonical products + GPIDs
→ ACCURACY GATE (95%+) → Competitive overlap → Price positioning
→ Path A dashboard → Path B whale reports → $$$ REVENUE $$$

The single most important thing to build is the product matching engine.
Every day spent on anything else before 95% accuracy is a wasted day.
```

---

## Appendix A: Technology Decisions (Summary)

| Decision | Choice | Why |
|---|---|---|
| Matching engine | PostgreSQL (`pg_trgm` + TypeScript batch jobs) | Already in stack; 100K products is tractable in-DB |
| Edge case resolution | LLM (Haiku/mini) | Cheaper and faster than human review |
| Clustering | TypeScript Union-Find (batch job) | Too complex for pure SQL |
| Competitive radius | Haversine SQL (no PostGIS) | Already used in `match-operators.ts`; works at MA scale |
| Graph traversal | PostgreSQL recursive CTEs | No Neo4j. 772 licenses isn't a graph-scale problem |
| Time-series | TimescaleDB extension (if needed) | Not a separate DB. Extension on existing Postgres. |
| MV refresh | pg_cron or external cron | Daily refresh sufficient |
| API framework | Existing Elysia/Hono stack | No new framework needed |
| Path B delivery | PDF/data exports | Whales want answers, not pixels |

## Appendix B: Data Quality Notes

| Metric | Value | Impact |
|---|---|---|
| Products with brand | 37.6% | 62% need brand extraction from name |
| Distinct brands (after cleanup) | ~700 | Manageable brand dictionary |
| Products with weight | ~40% | Need weight extraction from name for rest |
| Products with THC% | ~35% | Limited THC matching signal |
| Operators with lat/lon | ~95% | Good for distance computation |
| CCC licenses matched | 770/772 | Excellent |
| Weedmaps scraper success | 5.8% (10/173) | **Major data gap** — fixing adds 163 stores (Post-90-Day priority) |

## Appendix C: Risk Register (Updated)

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Scraping blocked by Dutchie/Jane** | Medium | **EXISTENTIAL** | Trojan horse: free tier for POS API access. See §6.3. |
| Product matching accuracy < 90% | Medium | High | Start with exact fingerprint (high precision), add similarity gradually. AI review for edge cases. Human review as last resort. |
| Product matching accuracy stuck 90-95% | Medium | Medium | Iterate: operator QA feedback loop, expanded brand dictionary, weight/strain parsing improvements. |
| Brand extraction fails for 60%+ | Medium | Medium | Focus on branded products first (37.6%). Unbranded = house brands = less critical for cross-store. |
| Weedmaps scraper stays broken | High | High | Fixing adds ~163 stores. Post-90-Day priority. API access path mitigates long-term. |
| Path B whales won't pay $5K/mo | Medium | Medium | Validate in Month 2 with $2,500 reports. Adjust pricing based on signal. Even $2K/mo × 10 = $20K MRR. |
| Low operator adoption of Path A | Medium | Low | Path A is for data QA, not revenue. Even 10 operators providing feedback is sufficient. |
| LLM matching costs escalate | Low | Low | Expected $2-$5 per full run. Even 10x = $50. Negligible. |

## Appendix D: Strategic Review Summary

*This plan was reviewed by an independent product strategist on February 13, 2026. Key findings:*

1. **Core thesis validated:** "In a fragmented, immature industry, the entity that normalizes the data layer becomes the monopoly tollbooth." The Clearbit/CoStar/ZoomInfo playbook is correct.

2. **Critical warning accepted:** Eight massive businesses mapped but only ~50 developer-days budgeted. Trying to build everything simultaneously = death by indigestion. Plan restructured to ruthlessly sequence execution.

3. **Foundation First mandate adopted:** All forward-looking product ideation halted until matching engine hits 95%+ accuracy. Every high-value play depends on GPIDs.

4. **GTM path selected:** Path A (Operator SaaS) for distribution + data validation. Path B (Brand Intelligence / Whale Hunter) for revenue. Path C (Fraud Machine) held in reserve for Month 6+ PR play.

5. **Kill list enforced:** Consumer App, State-in-a-Box, and Demand Signal Pipeline removed from active development. Fraud Machine, Ownership Graph, Credit Scoring also killed for now.

6. **Technical decisions locked:** No Neo4j (PostgreSQL CTEs), TimescaleDB as extension only, AI for matching edge cases, scraper risk mitigation via POS API access.

7. **90-day execution plan adopted:** 237 developer-hours across 3 months. Clear gates between phases. Revenue target: $15K-$25K MRR by Day 90.

---

*Consolidated from: DATA-INTELLIGENCE-PLAN.md (MiniMax), DATA-INTELLIGENCE-PLAN-CREATIVE.md (Opus creative), DATA-INTELLIGENCE-PLAN-OPUS.md (Opus technical), Expert Strategic Review (February 13, 2026)*  
*Plan created: February 13, 2026*  
*Plan updated: February 13, 2026 — Post-Strategic Review v2*
