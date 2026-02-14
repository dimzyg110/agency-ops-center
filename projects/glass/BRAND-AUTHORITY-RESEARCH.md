# BRAND AUTHORITY RESEARCH

**Date:** 2026-02-14 (UTC)
**Scope:** Massachusetts cross-platform cannabis brand normalization for GLASS

---

## Executive summary

Your current brand dictionary is materially corrupted by over-merging and non-brand ingestion. A single-source authority does not exist in MA public data. The highest-confidence path is a **layered authority model**:

1. **Platform-curated brand directories** (Leafly + Weedmaps) as external canonical layer
2. **CCC manufacturer licenses** as legal-entity anchor layer
3. **Product-anchored + consensus graph** as internal reconciliation layer
4. **LLM/embedding only as adjudication tools** on restricted candidates (not first-pass clustering)

This can be mostly automated with confidence scoring + human review only for low-confidence conflicts.

---

## What I validated in your DB

Connection used:
`postgresql://postgres:***@turntable.proxy.rlwy.net:18582/railway` with `SET search_path TO public`

### Baseline dataset shape
- Total products: **161,695**
- Products with non-empty brand: **100,017**
- Distinct brand strings in products: **20,243**

Platform product/brand footprint (from `products + prices + sources`):
- weedmaps: 59,907 products / 13,023 brand strings
- dutchie: 51,412 products / 7,098 brand strings
- leafly: 44,730 products / 1,485 brand strings
- jane: 6,273 products / 399 brand strings

### 1) CCC manufacturer `business_name` overlap with product brands
- Manufacturer licenses (`Marijuana Product Manufacturer`): **127**
- Exact normalized overlap vs product brands (punctuation only): **4** manufacturer names
- Suffix-stripped overlap (remove LLC/INC/CORP/etc, normalize): **42** manufacturer names with at least one brand match

Interpretation: exact business name is too strict; legal-entity-to-brand mapping is useful but incomplete.

### 2) Brand distribution: how many brands appear on 3+ platforms?
Distinct brand strings by platform count:
- 1 platform: **18,886** (93.31%)
- 2 platforms: **1,059** (5.23%)
- 3 platforms: **179** (0.88%)
- 4 platforms: **116** (0.57%)

Brands on 3+ platforms: **295 / 20,240 = 1.46%**

Interpretation: pure cross-platform agreement is sparse; external authority is required for long-tail brands.

### 3) % of products whose brand appears on only 1 platform
- Products with brand: **99,993**
- Products whose brand is single-platform-only: **49,476**
- Percentage: **49.48%**

Interpretation: ~half of branded products need non-consensus validation.

### 4) `brand_dictionary` quality sample
`brand_dictionary` stats:
- Canonical rows: **3,092**
- Avg aliases per canonical: **8.06**
- Max aliases: **22,422** (extreme over-merge)
- Avg platform_count: **1.17**
- platform_count max: **5** (should be ≤4 for current sources)

Observed corruption examples:
- `Jeeter` with 73,214 products and 22,422 aliases (contains obvious product strings)
- Canonicals like `Roll Tac 26 50`, `Zip-Up Hoodie Xl`, `$200 Gift Certificate`, `Leaves Per Pack`

Interpretation: current dictionary cannot be treated as authority without rebuild + constraints.

---

## External source viability (researched)

- **Leafly** has public brand directory endpoints/pages (`/brands`, `/brands/all`) and branded landing pages (`/brands/{slug}`).
- **Weedmaps** has public brand directory pages (`/brands`, `/brands/all`).
- **Leafly help docs** indicate menu-brand linking to a managed brand database (strong signal that Leafly maintains canonical entities).
- **Dutchie** support docs reference a managed content catalog and product matching in Brand Portal (strong signal of internal normalization).
- **METRC** API access appears licensee-key-based (state/vendor agreements; not a public anonymous feed).
- **Jane** appears to expose brand/manufacturer in menu/catalog payloads (also confirmed by your parser: `hit.brand` in `scripts/lib/jane-parser.ts`).

---

## Approach-by-approach evaluation

Scoring legend: Reliability 1 (low) → 10 (high)

## 1) Platform APIs as brand authority
**How it works**
- Ingest platform-native brand entities from APIs/page payloads (brand id, name, slug, maybe parent).
- Maintain `brand_authority_source(platform, platform_brand_id, canonical_name, slug, metadata)`.
- Crosswalk internal raw brand strings to platform entities before cross-platform matching.

**Pros**
- Curated by platforms already solving this problem.
- Usually stable canonical IDs/slugs.
- High automation once ingestion is stable.

**Cons**
- Access varies by platform (private APIs, anti-bot, ToS constraints).
- Platform-specific naming bias and lag.

**Estimated coverage**: **45–70%** of MA brand strings (higher for common/menu-active brands)
**Implementation effort**: **3–7 days** (connectors + parser hardening + upsert logic)
**Reliability**: **8/10**
**Fully automatable?**: **Mostly** (yes, with monitoring and fallbacks)
**Dependencies**: API access / scraping tolerance, possible keys, legal/ToS review

---

## 2) METRC as source of truth
**How it works**
- Use METRC package/item/manufacturer records via licensee-authorized API.
- Map METRC item + licensee/manufacturer to brand authority entries.

**Pros**
- Regulatory provenance and auditable chain.
- Strong manufacturer attribution.

**Cons**
- Not generally public; requires licensee API credentials and agreements.
- Manufacturer != consumer-facing brand in many cases.
- Your current `ccc_lab_tests` has metrc tags but no linked operator/brand in practice (operator_id null).

**Estimated coverage**: **20–60%** (depends entirely on access + mapping depth)
**Implementation effort**: **2–6 weeks** (permissions + integration + data model)
**Reliability**: **9/10** for provenance, **6/10** for consumer brand identity
**Fully automatable?**: **Yes after access**, otherwise no
**Dependencies**: METRC licensee keys, legal access, partner/licensee cooperation

---

## 3) CCC manufacturer licenses → brand mapping
**How it works**
- Seed authority from `ccc_licenses` manufacturer business names.
- Normalize legal suffixes and punctuation.
- Build deterministic + fuzzy map from legal entity to observed product brands.

**Pros**
- Public/available in your DB.
- High confidence for entity existence in MA.
- Good for parent-company graph.

**Cons**
- Under-covers consumer-facing sub-brands.
- Requires 1-to-many parent→brand mapping layer.

**Estimated coverage**: **15–35%** direct; **40–55%** with parent-brand enrichment
**Implementation effort**: **1–3 days** for seed + mapping heuristics
**Reliability**: **7/10** (entity high, brand identity medium)
**Fully automatable?**: **Yes**, with periodic manual audits for multi-brand manufacturers
**Dependencies**: CCC refresh cadence; enrichment source for brand portfolios

---

## 4) Weedmaps/Leafly brand directories (scraping)
**How it works**
- Crawl `/brands/all` + paginated listings and brand profile pages.
- Extract canonical brand names, slugs, optional alternate stylings.
- Use as external canonical layer.

**Pros**
- High-signal curated catalogs.
- Immediate impact without partner API deals.

**Cons**
- Anti-bot/front-end changes can break parsers.
- Aliases are usually implicit, not explicit.

**Estimated coverage**: **35–65%** (especially high-frequency retail brands)
**Implementation effort**: **2–5 days** initial + ongoing maintenance
**Reliability**: **8/10** for canonical names; **5/10** for alias completeness
**Fully automatable?**: **Mostly**
**Dependencies**: scraper infra, cadence jobs, legal review

---

## 5) Dutchie brand catalog
**How it works**
- Extract Dutchie menu brand field + if available catalog match metadata.
- Build canonicalization around Dutchie’s catalog-controlled names.

**Pros**
- Dutchie is a major menu backend with normalization incentives.
- Good coverage in your data (51k products).

**Cons**
- Access to deep catalog entities may be partner-only.
- Public scraping may only expose rendered strings, not canonical IDs.

**Estimated coverage**: **25–50%** standalone; better as ensemble signal
**Implementation effort**: **2–6 days** depending on payload accessibility
**Reliability**: **7/10**
**Fully automatable?**: **Partly to mostly**
**Dependencies**: endpoint accessibility, parser stability

---

## 6) Consensus-based approach (no external source)
**How it works**
- Build brand string graph per normalized candidate.
- Elect canonical spellings by weighted vote (platform_count, product_count, recency).
- Merge only when lexical similarity + product-cooccurrence evidence exceed strict thresholds.

**Pros**
- No external dependency.
- Transparent scoring and replayable decisions.

**Cons**
- Fails on single-platform long tail (which is 93% of brand strings).
- Can reinforce dominant noisy spellings.

**Estimated coverage**: **20–40% high confidence**, poor long-tail resolution
**Implementation effort**: **2–4 days**
**Reliability**: **6/10**
**Fully automatable?**: **Yes**
**Dependencies**: strong internal evidence tables

---

## 7) Product-anchored brand detection
**How it works**
- First match products cross-platform using strong identifiers (exact/near-exact product name + quantity/unit + category + optional THC/CBD ranges).
- For confirmed product matches, infer brand equivalence pairs from attached brand strings.
- Build alias dictionary bottom-up from these high-precision product anchors.

**Pros**
- Avoids direct noisy brand-to-brand clustering.
- Creates explainable alias evidence.

**Cons**
- Requires robust product matching pipeline first.
- Weak on unique products with no cross-platform twins.

**Estimated coverage**: **30–55%** with high precision
**Implementation effort**: **4–8 days** (if GPID pipeline exists, less)
**Reliability**: **8/10**
**Fully automatable?**: **Yes**, with confidence thresholds
**Dependencies**: mature product match scoring, validation tables

---

## 8) Embedding-based matching
**How it works**
- Embed brand strings (and optional context: common products/categories/platforms).
- Use ANN nearest neighbors + constrained clustering.
- Only accept clusters meeting strict structural constraints.

**Pros**
- Better than trigram for punctuation/format variations.
- Good candidate generation for adjudication stage.

**Cons**
- Still risky as autonomous merge authority (semantic drift, homonyms).
- Needs robust guardrails and evaluation set.

**Estimated coverage**: **40–70% candidate generation**, **20–45% auto-resolve safely**
**Implementation effort**: **3–6 days**
**Reliability**: **6/10** standalone; **8/10** in hybrid with constraints
**Fully automatable?**: **Partially**
**Dependencies**: embedding API, vector index, evaluation harness

---

## 9) LLM-powered classification
**How it works**
- Feed candidate pairs (A,B) with structured evidence (token overlap, platform overlap, sample product names, known parent company).
- Ask binary + confidence + rationale:
  - same brand?
  - parent/child relationship?
  - non-brand junk token?

**Pros**
- Excellent for ambiguous edge cases and junk detection.
- Useful as adjudicator after deterministic filters.

**Cons**
- Cost/latency if used naively at pairwise scale.
- Non-determinism; must cache and threshold.

**Estimated coverage**: **10–25% direct resolution** (the ambiguous slice), high impact on precision
**Implementation effort**: **2–5 days**
**Reliability**: **7/10** with good prompt + evidence; **5/10** raw
**Fully automatable?**: **Yes for low-risk decisions; human-in-loop for borderline**
**Dependencies**: LLM API budget, prompt/version controls, caching

---

## 10) Hybrid (CCC anchor + platform directories + consensus)
**How it works**
- Build authority ledger with source-weighted confidence:
  - Tier A: regulatory/entity anchors (CCC manufacturer)
  - Tier B: curated platform directories (Leafly/Weedmaps + Dutchie if accessible)
  - Tier C: internal consensus + product-anchored alias inference
  - Tier D: embeddings/LLM only for unresolved conflicts
- Persist every alias decision with provenance and score.

**Pros**
- Best precision/coverage tradeoff.
- Degrades gracefully when one source is missing.
- Fully auditable and incrementally improvable.

**Cons**
- More moving parts.
- Requires quality pipeline and monitoring.

**Estimated coverage**: **70–90%** of active MA brand strings over time
**Implementation effort**: **2–4 weeks** phased
**Reliability**: **9/10**
**Fully automatable?**: **Mostly** (with queue-based human review for low confidence)
**Dependencies**: all above data feeds + scoring framework

---

## Recommended strategy (prioritized by effort vs impact)

### Phase 0 (1–2 days): Stop further dictionary corruption
1. Freeze current auto-merge writes.
2. Add hard constraints:
   - Reject canonicals that look like products/accessories (gift card, hoodie, grams, pack, roll, etc.)
   - Enforce `platform_count <= 4` for current platform universe
   - Require provenance metadata for every alias insertion
3. Snapshot old dictionary as legacy.

### Phase 1 (3–5 days): Build authoritative seed layer
1. Ingest Leafly + Weedmaps brand directories into `brand_authority_sources`.
2. Seed CCC manufacturer entities and normalized legal-name variants.
3. Create `brand_authority` canonical table with provenance scoring.

### Phase 2 (4–7 days): High-precision alias expansion
1. Run product-anchored cross-platform matcher to derive alias pairs.
2. Add consensus voting only where product evidence exists.
3. Auto-accept only high-confidence merges; queue rest.

### Phase 3 (2–4 days): Intelligent adjudication
1. Use embeddings for candidate retrieval only.
2. Use LLM for tie-break/ambiguous pair classification + junk detection.
3. Cache decisions and re-use by normalized pair hash.

### Phase 4 (ongoing): Quality ops
- Weekly precision audits on random accepted merges.
- Drift dashboard: new raw brands, unresolved queue, false merge rollback rate.
- Backtest against frozen gold set (200–500 manually verified brand pairs).

---

## Suggested target schema additions

- `brand_authority` (canonical_id, canonical_name, parent_company, status, confidence)
- `brand_alias` (alias_text, canonical_id, source_type, source_ref, confidence, decision_method, created_at)
- `brand_resolution_queue` (alias_text, candidates[], evidence_json, priority, review_status)
- `brand_merge_audit` (before/after, reason, model/version, operator)

This makes every decision traceable and reversible.

---

## Bottom line

- **Do not rely on trigram-only brand clustering** for canonicalization.
- **No single public source is sufficient** for MA cannabis brand authority.
- The best path is a **hybrid authority graph**: platform-curated brand catalogs + CCC legal anchors + product-anchored evidence, with embeddings/LLMs as controlled adjudicators.
- Given current DB signals (93% single-platform brand strings, dictionary corruption), this hybrid is the only realistic way to scale without sacrificing precision.
