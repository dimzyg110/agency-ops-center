# GLASS Consolidation Plan: 234 → 500 Verified GPIDs

**Date:** 2026-02-14
**Goal:** 500 perfect verified GPIDs from the 308 verified brands → consumer launch
**Status:** We're closer than you think.

---

## TL;DR — The Punchline

**You already have enough parsed data to get to ~1,628 GPIDs.** The lock script has only been run on 10 brands (producing 234 GPIDs). Re-running it on all 308 verified brands would immediately jump to ~1,628 verified GPIDs. You don't need to parse more products to hit 500. You need to **re-run the existing pipeline** and **quality-check the output.**

The 500 target isn't a parsing problem. It's a pipeline execution problem.

---

## 1. The Gap: Where We Are vs. Where We Need to Be

### Current State (Live DB — Feb 14, 2026)

| Metric | Count | Notes |
|--------|------:|-------|
| **Verified GPIDs** (`verified_gpids`) | **234** | Lock script only ran on ~10 brands |
| Products mapped to GPIDs (`product_verified_gpids`) | 237 | Almost 1:1 with verified GPIDs |
| Parsed products (`parsed_products`) | 3,151 | LLM-parsed via Gemini 2.5 Flash |
| — Accepted | 2,210 | 70% of parsed |
| — Needs review | 857 | 27% of parsed |
| — Rejected | 94 | 3% of parsed |
| Products with verified brands | 36,559 | From the 308 brands |
| Products already parsed (verified brands) | 2,520 | ~7% of the 36K pool |
| Products NOT yet parsed (verified brands) | 34,445 | 93% of pool remains |
| Total products | 162,259 | All platforms |
| Products with NO brand | 61,707 | 38% — data quality gap |
| Total prices | 226,503 | Fresh daily |
| Verified brands (3+ platforms) | 308 | The foundation |

### The Critical Insight

The lock script (`lock-verified-gpids.ts`) generates GPIDs from ALL `accepted`/`pending` parsed products with brand + weight. But it was only run when ~10 brands had been parsed (Anthologie, Amber, Airo, Altitude Beverages, etc.). Since then, **257 more brands have been parsed** but the lock script hasn't been re-run.

**Right now, without touching anything else:**

| If we run... | We get... |
|---|---|
| Lock script on current parsed data (all brands) | **~1,628 GPIDs** from 308 brands |
| Lock script on accepted-only, with strain + weight | **~1,595 GPIDs** |
| Lock script on 0.90+ confidence, with strain + weight | **~1,560 GPIDs** |

**We are 3x OVER the 500 target in parsed data alone.** The bottleneck is not parsing — it's running the lock script and quality-checking the output.

### What Those 1,628 GPIDs Look Like

- **215 brands** have at least 1 GPID-ready parsed product (out of 308)
- **51 brands** have zero parsed products (need LLM parsing)
- Average confidence on accepted parses: **0.971** (high)
- 63% of parsed products have confidence ≥ 0.95
- Parsed data covers all major categories: flower, vape, preroll, edible, concentrate

### But... Quality Matters

Not all 1,628 are "perfect." Looking at the existing 234 GPIDs:
- **179 (76%)** have only 1 supporting product (single-source)
- **24 (10%)** have 2 supporting products
- **3 (1%)** have 3+ supporting products
- **28 (12%)** have 0 supporting products

For a "perfect" GPID that powers price comparison, we need **2+ supporting products from 2+ stores.** Currently, only ~261 potential GPIDs have 2+ parsed products pointing at them.

---

## 2. What Blocks Us

### Blocker 1: Lock Script Hasn't Been Re-Run ⚡ (Easy Fix)
**Impact:** Going from 234 → ~1,628 GPIDs immediately
**Effort:** 5 minutes
**Risk:** Low — script is proven, just needs re-execution

The lock script (`src/scripts/gpid/lock-verified-gpids.ts`) processes ALL eligible parsed_products. It was last run when only ~10 brands had data. Running it now would absorb all 2,230 eligible parsed products.

### Blocker 2: Low Cross-Store Coverage 🔶 (Medium Fix)
**Impact:** Most GPIDs currently have only 1 supporting product
**Effort:** 2-4 days of additional LLM parsing
**Risk:** Medium — need to parse more products from the same brands to build cross-store matches

Of the 36,559 products from verified brands, only 2,520 (~7%) have been parsed. The parser has been running on a "top brands" queue, but it's only scratched the surface. Parsing more products for the SAME brands will create more product→GPID mappings, giving us the cross-store price comparisons that make the consumer site valuable.

### Blocker 3: 51 Verified Brands Have Zero Parsed Products 🔶 (Medium Fix)
**Impact:** 51 of 308 brands have no representation in the GPID system
**Effort:** 1-2 days of LLM parsing
**Risk:** Low — these are smaller brands, may not contribute many GPIDs

### Blocker 4: 857 "Needs Review" Parsed Products 🟡 (Low Priority for 500)
**Impact:** ~27% of parsed products need human validation
**Effort:** 2-4 hours in the Verify UI
**Risk:** Some of these could become high-quality GPIDs if accepted

### Blocker 5: Brand Fill Gap (61K Products Missing Brand) 🟢 (NOT a Blocker for 500)
**Impact:** 38% of all products can't be matched to brands
**Effort:** Large — requires brand-inference pipeline
**Risk:** This is a long-term data quality issue, NOT a blocker for the initial 500

**Why it's not a blocker:** The 308 verified brands already account for 36,559 products (22% of total). These products HAVE brands. We're focused on making those 36K perfect, not fixing the brandless 61K. The brandless products are from smaller/local brands, store-branded items, or poorly formatted scraper output. They're a Phase 2 problem.

---

## 3. The Sequence: From Here to 500 Perfect GPIDs

### Phase 0: Instant Win — Re-Run Lock Script (Day 1, Hour 1)
**Time:** 15 minutes | **Yield:** 234 → ~1,628 GPIDs

```bash
cd /data/workspace/projects/glass/src
DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/gpid/lock-verified-gpids.ts
```

**What this does:**
1. Reads all 2,230 eligible parsed_products (accepted/pending, non-accessory, has brand + weight)
2. Computes deterministic SHA-256 GPID hash for each (brand|strain|form|weight)
3. Upserts into `verified_gpids` table
4. Maps products to GPIDs in `product_verified_gpids`
5. Updates supporting_product_count

**After this runs, we have ~1,628 GPIDs.** The "500 target" is already blown past in terms of raw count.

### Phase 1: Quality Gate — Select the Best 500 (Day 1-2)
**Time:** 4-8 hours | **Yield:** 500 verified, quality-checked GPIDs

Not all 1,628 GPIDs are equal. We need to select the best 500 based on:

**Selection Criteria (ranked):**
1. **Supporting product count ≥ 2** (cross-store comparison possible) — ~261 candidates
2. **Confidence ≥ 0.95** (high parser accuracy) — majority qualify
3. **Complete data** (brand + strain + weight + category all present) — ~1,595 qualify
4. **Brand is from the 308 verified list** — ~1,628 qualify
5. **Has recent price data** (scraped in last 7 days) — need to check

**The SQL to find the Top 500:**
```sql
SET search_path TO public;

-- After re-running lock script, select the best 500
SELECT 
  vg.gpid,
  vg.canonical_brand,
  vg.canonical_strain,
  vg.canonical_form,
  vg.weight_grams,
  vg.canonical_category,
  vg.supporting_product_count
FROM verified_gpids vg
WHERE vg.canonical_strain IS NOT NULL 
  AND TRIM(vg.canonical_strain) != ''
  AND vg.weight_grams IS NOT NULL
  AND EXISTS (
    SELECT 1 FROM brand_authority ba 
    WHERE ba.platform_count >= 3 
    AND LOWER(TRIM(vg.canonical_brand)) = LOWER(ba.canonical_name)
  )
ORDER BY 
  vg.supporting_product_count DESC,
  vg.canonical_brand ASC
LIMIT 500;
```

**If we don't have 500 with 2+ supporting products (currently ~261), we supplement with:**
- GPIDs with 1 supporting product but high confidence (0.95+) and from top brands
- GPIDs from brands with the highest product counts (Jeeter, High Supply, Nature's Heritage, etc.)

### Phase 2: Parse More to Enrich (Days 2-5)
**Time:** 3-4 days | **Yield:** Increase cross-store coverage for Top 500 GPIDs

**Goal:** Get every one of our 500 selected GPIDs to have **2+ supporting products from 2+ stores.**

**Strategy:**
1. Take the 500 selected GPIDs
2. Find all products in the `products` table that match the same brand (from verified brands)
3. Parse those products through the LLM parser
4. Re-run the lock script to map them to existing GPIDs

**Parsing priority (by unparsed product count):**

| Brand | Unparsed Products | Priority |
|-------|------------------:|----------|
| Jeeter | 1,236 | 🔴 High |
| High Supply | 974 | 🔴 High |
| Nature's Heritage | 914 | 🔴 High |
| Rove | 907 | 🔴 High |
| Happy Valley | 743 | 🔴 High |
| Bountiful Farms | 716 | 🔴 High |
| Fernway | 702 | 🔴 High |
| InHouse | 666 | 🔴 High |
| Simply Herb | 604 | 🟡 Medium |
| Treeworks | 563 | 🟡 Medium |

**Parsing cost estimate:**
- Gemini 2.5 Flash: ~$0.015 per 1K input tokens, ~$0.06 per 1K output tokens
- Each product parse: ~200 input tokens + ~150 output tokens ≈ $0.012/product
- 10,000 products (top 20 brands): **~$120**
- 34,445 products (all unparsed verified-brand): **~$415**

**The parse-top-brands script already supports this:**
```bash
cd /data/workspace/projects/glass/src
DATABASE_URL="..." GOOGLE_AI_API_KEY="..." \
  npx tsx scripts/gpid/parse-top-brands.ts --brand-top=308 --batch-size=50
```

### Phase 3: Review & Validate (Days 3-6)
**Time:** 2-3 days (can overlap with Phase 2) | **Yield:** Clean, validated GPIDs

1. **Process the 857 "needs_review" parsed products**
   - Use the GPID Verify UI (already deployed on Railway)
   - Focus on products from Top 500 GPID brands first
   - Accept or reject each one
   - Expected conversion: ~60% accepted → ~514 new accepted parses

2. **Spot-check the Top 500 GPIDs**
   - Sample 50 GPIDs (10%) manually
   - Verify: Is the brand correct? Is the strain spelled right? Is the weight accurate?
   - Flag any systemic issues (e.g., a brand being consistently misparsed)

3. **De-duplicate GPIDs**
   - Check for near-duplicate GPIDs (same product, slightly different form/weight parsing)
   - Example: "Fernway Berry Gelato Cart 0.5g" vs "Fernway Berry Gelato Cartridge 0.5g" → should be 1 GPID
   - The deterministic hash separates these; may need a fuzzy merge step

### Phase 4: Price Linking (Days 5-7)
**Time:** 2 days | **Yield:** 500 GPIDs with live price comparison data

**This is the step that makes GPIDs useful to consumers.** A GPID without prices is just a catalog entry.

1. **Build the GPID → Price bridge**
   - For each verified GPID, find all `product_verified_gpids` mappings
   - Join to `prices` table to get current prices per store
   - Populate `store_count` and `price_min`/`price_max` on the GPID

2. **Verify price freshness**
   - Recent scrape data shows strong daily inflow:
     - Feb 14: 25,049 prices
     - Feb 13: 87,613 prices
     - Feb 12: 114,055 prices
   - Products from verified brands span **351 stores**
   - **7,996 products** appear at 2+ stores (cross-store comparison possible)

3. **Build the consumer API query**
   - The consumer endpoints already exist (`/v1/consumer/search`, `/v1/consumer/gpid/:gpid`)
   - May need to update them to query `verified_gpids` + `product_verified_gpids` + `prices`

### Phase 5: Final QA & Launch Readiness (Days 7-10)
**Time:** 3 days | **Yield:** Launch-ready dataset

1. **Run QA sample script** (`src/scripts/gpid/qa-sample-gpids.ts`)
2. **Generate "Price Shock" cards** for Top 10 highest-spread GPIDs
3. **Verify consumer API returns correct data** for all 500 GPIDs
4. **Deploy updated frontend** with the 500 GPIDs
5. **Generate city/brand/store pages** for SEO

---

## 4. Effort Estimate

### The Timeline

| Phase | Days | Effort | Depends On |
|-------|------|--------|------------|
| **Phase 0:** Re-run lock script | Day 1 | 15 min | Nothing |
| **Phase 1:** Select Top 500 | Day 1-2 | 4-8 hrs | Phase 0 |
| **Phase 2:** Parse more products | Day 2-5 | 3-4 days (automated) | Phase 1 |
| **Phase 3:** Review & validate | Day 3-6 | 2-3 days (parallel) | Phase 0 |
| **Phase 4:** Price linking | Day 5-7 | 2 days | Phase 2+3 |
| **Phase 5:** Final QA & launch | Day 7-10 | 3 days | Phase 4 |

**Total: ~10 days to launch-ready.** Phases 2 and 3 can run in parallel.

### The Cost

| Item | Cost |
|------|-----:|
| LLM parsing (10K products, top 20 brands) | ~$120 |
| LLM parsing (all 34K unparsed) | ~$415 |
| Railway hosting (already running) | $0 incremental |
| Human review time (857 products) | ~4-8 hrs |
| **Total (conservative, parse 10K)** | **~$120 + time** |
| **Total (aggressive, parse all 34K)** | **~$415 + time** |

### Resources Needed

1. **LLM API Key** — `GOOGLE_AI_API_KEY` for Gemini 2.5 Flash (already configured)
2. **Database access** — Railway PostgreSQL (already running)
3. **GPID Verify UI** — Already deployed on Railway for human review
4. **Developer time** — 1 developer, ~10 days
5. **Scraper continuity** — All 4 scrapers already running daily ✅

---

## 5. What Can Go Wrong

### Risk 1: GPID Duplication (HIGH probability, MEDIUM impact)
**The problem:** The hash function uses `brand|strain|form|weight`. If the LLM parser produces slightly different strain names for the same product ("Berry Gelato" vs "Berry gelato" vs "Berry Gelato "), they get different GPIDs.

**Mitigation:** The hash normalizes to lowercase and trims whitespace. But typos, abbreviations, and variant names can still split what should be 1 GPID into 2+. Need a de-duplication pass.

**Evidence from current data:** The existing canonical_products table has 103,895 entries — many are likely duplicates of the same real-world product. The LLM parser should collapse these, but we need to verify.

### Risk 2: Low Cross-Store Coverage (MEDIUM probability, HIGH impact)
**The problem:** A GPID with prices from only 1 store isn't useful for price comparison. The whole value proposition is "same product, different prices."

**Mitigation:** Focus parsing on the highest-volume brands and products that appear across multiple platforms/stores. The 7,996 products that appear at 2+ stores are our priority pool.

**Current state:** Only 261 potential GPIDs have 2+ parsed products. We need to parse more products from the same brands to increase this.

### Risk 3: Parser Quality Degradation at Scale (LOW probability, MEDIUM impact)
**The problem:** The parser averages 0.971 confidence on the current 3K products. As we scale to 34K, quality might drop for weird product names.

**Mitigation:** The confidence threshold is built in. Products below 0.90 confidence get flagged for review. The parser already handles well — 63% of products parse at 0.95+ confidence.

### Risk 4: Stale Prices (LOW probability, HIGH impact)
**The problem:** If scrapers fail or prices aren't updated, the consumer site shows wrong prices. Trust is destroyed.

**Mitigation:** All 4 scrapers are running daily. Recent data shows 25K-114K prices scraped per day. Add a "last updated" timestamp to every price display. Don't show prices older than 48 hours.

### Risk 5: Brand Name Mismatches Between Systems (MEDIUM probability, LOW impact)
**The problem:** `brand_authority.canonical_name` might not match exactly with `parsed_products.parsed_brand` or `products.brand`. Case differences, punctuation, etc.

**Mitigation:** All comparisons use `LOWER()`. But "Nature's Heritage" vs "Natures Heritage" vs "Nature's Heritage" could cause misses. Need a brand alias system eventually.

---

## 6. The "Done" Definition

### Minimum Viable Launch (the "500 Perfect GPIDs" bar)

A GPID is "perfect" when ALL of the following are true:

| Criterion | Requirement |
|-----------|-------------|
| **Brand** | From the 308 verified brands (3+ platforms) |
| **Strain** | Present and normalized (not null, not empty) |
| **Weight** | Present and accurate (parsed_weight_grams != null) |
| **Category** | Present (flower/vape/preroll/edible/concentrate/etc.) |
| **Confidence** | ≥ 0.90 average across supporting products |
| **Price data** | At least 1 current price (scraped within 7 days) |
| **Cross-store** | BONUS: 2+ stores for price comparison |

### Launch Checklist

- [ ] **500+ GPIDs in `verified_gpids`** meeting the above criteria
- [ ] **Each GPID linked to products** via `product_verified_gpids`
- [ ] **Each linked product has current prices** in `prices` table
- [ ] **Consumer API returns correct data** for all 500 GPIDs
  - `/v1/consumer/search?q=fernway` returns matching GPIDs with prices
  - `/v1/consumer/gpid/:gpid` returns full price comparison
- [ ] **At least 100 GPIDs have 2+ store price comparison**
- [ ] **At least 200 of the 308 brands represented** in the 500 GPIDs
- [ ] **QA sample (50 GPIDs) passes manual review** — correct brand, strain, weight, prices
- [ ] **Top 10 "Price Shock" cards generated** — products with biggest price spreads
- [ ] **Frontend deployed** with search, product detail, and brand pages working
- [ ] **SEO pages generated** — at least 500 GPID pages + 50 brand pages + 10 city pages

### The Numbers That Matter at Launch

| Metric | Target | Why |
|--------|--------|-----|
| Verified GPIDs | ≥ 500 | Critical mass for consumer utility |
| GPIDs with 2+ stores | ≥ 100 | Price comparison is the value prop |
| Brands represented | ≥ 200 | Coverage across the MA market |
| Products linked to GPIDs | ≥ 2,000 | Depth of catalog |
| Stores with price data | ≥ 200 | Geographic coverage |
| Price freshness | < 48 hrs | Consumer trust |

---

## 7. The Action Plan — What to Do Monday Morning

### Hour 1: The Instant Win
1. SSH into the Railway environment or run locally
2. Re-run the lock script:
   ```bash
   cd /data/workspace/projects/glass/src
   DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
     npx tsx scripts/gpid/lock-verified-gpids.ts
   ```
3. Verify the count:
   ```sql
   SELECT COUNT(*) FROM verified_gpids;  -- Should jump from 234 to ~1,600+
   SELECT COUNT(*) FROM product_verified_gpids;  -- Should match
   ```

### Hour 2: Assess the Output
4. Run the quality query:
   ```sql
   SELECT 
     vg.supporting_product_count AS support,
     COUNT(*) AS gpid_count
   FROM verified_gpids vg
   GROUP BY 1
   ORDER BY 1 DESC;
   ```
5. Identify the Top 500 by quality criteria
6. Count how many have 2+ supporting products

### Hours 3-8: Start the Enrichment Parse
7. Run the parser on the top 20 unparsed brands:
   ```bash
   DATABASE_URL="..." GOOGLE_AI_API_KEY="..." \
     npx tsx scripts/gpid/parse-top-brands.ts --brand-top=20 --batch-size=50
   ```
8. This will chew through ~10K products over several hours
9. Re-run lock script periodically to absorb new parses

### Day 2-3: Review Queue
10. Open the GPID Verify UI
11. Work through the 857 "needs_review" products — prioritize verified brands
12. Accept or reject each one

### Day 4-5: Cross-Store Enrichment
13. Focus parsing on products that appear at multiple stores
14. Re-run lock script after each batch
15. Track the "2+ supporting products" count — target 250+

### Day 6-7: Price Linking & API
16. Verify consumer API endpoints return correct GPID data
17. Build/update the GPID → Price bridge query
18. Generate sample "Price Shock" cards

### Day 8-10: QA & Launch
19. Manual QA of 50 random GPIDs
20. Deploy frontend with live data
21. Generate SEO pages
22. Draft the r/bostontrees post

---

## 8. Beyond 500: The Path to Scale

Once the 500 are locked, the next milestones are:

| Milestone | GPIDs | What It Takes |
|-----------|------:|---------------|
| Launch | 500 | This plan |
| Phase 2 (Retailer Trap) | 2,000 | Parse all 34K verified-brand products |
| Phase 3 (Brand Portal) | 5,000 | Add brand-uploaded master catalogs |
| Phase 4 (ML Flywheel) | 20,000+ | Train classification model on 5K+ human-verified examples |

The 34K unparsed products from verified brands would yield an estimated **5,000-8,000 GPIDs** based on the current 1,628-from-2,520 ratio (~65% yield from parsed → GPID). That's enough for the Retailer Trap phase.

The brand fill gap (61K products with no brand) becomes relevant in Phase 4 when we train the ML model. The human-verified data from Phases 1-3 becomes the training set. But for launch? Ignore it.

---

## Appendix A: Current Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GLASS Data Pipeline                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [4 Scrapers] ──daily──→ [products] + [prices]                   │
│   Dutchie, Jane,          162K products                          │
│   Leafly, Weedmaps         226K prices                           │
│                                                                   │
│  [brand_authority] ─────→ 308 verified brands (3+ platforms)     │
│   1,001 total brands        36,559 products with verified brand  │
│                                                                   │
│  [products] ──LLM parse──→ [parsed_products]                     │
│   36,559 eligible             3,151 parsed (7% of eligible)      │
│   34,445 unparsed             2,210 accepted, 857 needs_review   │
│                                                                   │
│  [parsed_products] ──lock script──→ [verified_gpids]             │
│   2,230 lock-eligible              234 GPIDs (only 10 brands!)   │
│   ⚠️ SHOULD produce ~1,628        → re-run to unlock ~1,628     │
│                                                                   │
│  [verified_gpids] ──mapping──→ [product_verified_gpids]          │
│   234 GPIDs                      237 product mappings             │
│                                                                   │
│  [product_verified_gpids] + [prices] ──→ Consumer API            │
│   Price comparison per GPID              /v1/consumer/search     │
│                                          /v1/consumer/gpid/:gpid │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### The Bottleneck Is Here: ⚠️
The lock script ran once when only 10 brands had parsed data. It hasn't been re-run since 257 more brands were parsed. **This is the single biggest unlocked win.**

## Appendix B: Key Queries for Monitoring Progress

```sql
SET search_path TO public;

-- Dashboard query: overall pipeline health
SELECT 
  (SELECT COUNT(*) FROM verified_gpids) AS verified_gpids,
  (SELECT COUNT(*) FROM verified_gpids WHERE supporting_product_count >= 2) AS gpids_2plus_stores,
  (SELECT COUNT(*) FROM product_verified_gpids) AS products_mapped,
  (SELECT COUNT(*) FROM parsed_products WHERE validation_status = 'accepted') AS accepted_parses,
  (SELECT COUNT(*) FROM parsed_products WHERE validation_status = 'needs_review') AS review_queue,
  (SELECT COUNT(DISTINCT canonical_brand) FROM verified_gpids) AS brands_with_gpids;

-- Top brands by GPID count (after re-run)
SELECT 
  vg.canonical_brand, 
  COUNT(*) AS gpid_count,
  SUM(vg.supporting_product_count) AS total_products
FROM verified_gpids vg
GROUP BY vg.canonical_brand
ORDER BY gpid_count DESC
LIMIT 20;

-- GPIDs with best price comparison data
SELECT 
  vg.gpid,
  vg.canonical_brand,
  vg.canonical_strain,
  vg.weight_grams,
  vg.canonical_category,
  vg.supporting_product_count,
  COUNT(DISTINCT pr.source_id) AS store_count,
  MIN(pr.price) AS price_min,
  MAX(pr.price) AS price_max,
  MAX(pr.price) - MIN(pr.price) AS price_spread
FROM verified_gpids vg
JOIN product_verified_gpids pvg ON pvg.gpid = vg.gpid
JOIN prices pr ON pr.product_id = pvg.product_id
WHERE pr.scraped_at >= NOW() - INTERVAL '7 days'
GROUP BY vg.gpid, vg.canonical_brand, vg.canonical_strain, vg.weight_grams, vg.canonical_category, vg.supporting_product_count
HAVING COUNT(DISTINCT pr.source_id) >= 2
ORDER BY (MAX(pr.price) - MIN(pr.price)) DESC
LIMIT 20;
```

## Appendix C: Risk Register

| # | Risk | Probability | Impact | Mitigation | Owner |
|---|------|------------|--------|------------|-------|
| 1 | GPID duplication (variant strain names) | HIGH | MEDIUM | Post-lock de-duplication pass; fuzzy matching on strain | Dev |
| 2 | Low cross-store coverage at launch | MEDIUM | HIGH | Prioritize parsing multi-store products; set 100 minimum for 2+ stores | Dev |
| 3 | Parser quality drops at scale | LOW | MEDIUM | Confidence threshold (0.90); review queue for edge cases | Dev + QA |
| 4 | Stale prices at launch | LOW | HIGH | Verify all 4 scrapers running; add freshness filter to API | Ops |
| 5 | Brand name mismatches | MEDIUM | LOW | LOWER() normalization; build alias table long-term | Dev |
| 6 | Consumer API not ready for GPID queries | MEDIUM | HIGH | Test endpoints before frontend deploy; may need query updates | Dev |
| 7 | Lock script fails on full dataset | LOW | LOW | Script is proven; just hasn't run on full set. Test first. | Dev |

---

**Bottom line:** You're sitting on 1,628 unlocked GPIDs. Run the lock script. Pick the best 500. Parse more to enrich. Ship it.**
