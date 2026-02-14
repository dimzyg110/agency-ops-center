# Review Feedback — `fuzzy-matcher.ts` (v2)

## Scores

| Dimension | Score | Notes |
| --- | --- | --- |
| Correctness | 4/5 | Matcher logic is coherent and deterministic; DB-backed checks align with observed outputs. |
| Completeness | 4/5 | Covers brand/name/category/weight/THC and candidate health logging, but lacks deeper rejection telemetry. |
| Quality | 3/5 | Good structure, but normalization + diagnostics are still not strong enough for current recall goals. |
| Brief Adherence | 4/5 | Uses brand dictionary aliases directly and supports cross-platform matching; key optimization opportunities remain. |

## Verdict

**APPROVE WITH CHANGES**

## Issues

1. 🟠 **Major — Recall gap remains high (pair-level):**
   - `gpid_candidates` (joinable) = **7,438**
   - `product_matches` = **3,612**
   - Unmatched candidate pairs = **3,826** (**51.44%** missed; pair recall 48.56%)
   - Query used:
   ```sql
   WITH c AS (
     SELECT DISTINCT LEAST(gc.product_a_id,gc.product_b_id) a, GREATEST(gc.product_a_id,gc.product_b_id) b
     FROM gpid_candidates gc
     JOIN products pa ON pa.id=gc.product_a_id
     JOIN products pb ON pb.id=gc.product_b_id
   ), m AS (
     SELECT DISTINCT LEAST(product_a_id,product_b_id) a, GREATEST(product_a_id,product_b_id) b
     FROM product_matches
   )
   SELECT (SELECT COUNT(*) FROM c) AS candidate_pairs_joinable,
          (SELECT COUNT(*) FROM m) AS matched_pairs,
          (SELECT COUNT(*) FROM c LEFT JOIN m USING(a,b) WHERE m.a IS NULL) AS unmatched_pairs;
   ```
   - Suggested fix: add explicit rejection reason counters in matcher output (`failed_name_threshold`, `failed_category_gate`, `failed_weight_far`, `failed_confidence`) to target the biggest loss points quickly.

2. 🟠 **Major — Brand dictionary is used, but not exploited for blocking strategy:**
   - The matcher **does** load aliases from `brand_dictionary` (`loadBrandAliasMap`, lines 188–214) and applies canonicalization in `normalizeBrand` (lines 143–147).
   - However, matching is still gated by precomputed `gpid_candidates`; no explicit canonical-brand-first batching strategy in SQL.
   - Diagnostic finding: all unmatched candidates are effectively same canonical brand in current pool; this indicates brand canonicalization is strong, but downstream gates (name/category/weight) are the bottleneck.
   - Suggested fix: add a mode to generate/score pairs within canonical-brand partitions (possibly with category subpartitions) before relying on broad candidate similarity.

3. 🟠 **Major — Category gate is likely suppressing many valid pairs due source taxonomy noise:**
   - In unmatched set, many high-name-sim pairs are blocked by category incompatibility (sample diagnostics suggest ~1,013 of unmatched with name>=0.78 are category-blocked).
   - Example false-negative pattern seen in sample: identical names/brands but one source labeled `flower`, another `vape`/`tincture`.
   - Suggested fix: introduce category confidence/fallback (soft penalty) rather than hard gate when name+brand evidence is very strong.

4. 🟡 **Minor — Confidence threshold at 0.50 is not the main limiting factor:**
   - Existing matched confidence stats:
     - min 0.5313, avg 0.7674, p50 0.7640, p90 0.9000
     - only 71 rows in ~0.5–0.6 bucket
   - This implies current recall is mostly lost **before** final thresholding (name/category/weight filters), not at `confidence < 0.50` cutoff.
   - Suggested fix: instrument pre-threshold candidate confidence distribution to tune earlier gates.

5. 🟡 **Minor — Why so many `exact` matches (1,751) after re-hash:**
   - Match types: `fuzzy_name=1861`, `exact=1751`, no `fuzzy_brand`/`fuzzy_both`.
   - Of 1,751 `exact`, **1,282** have non-identical raw `name` or `brand`; they become exact only **after normalization/canonicalization**.
   - So these are not necessarily duplicates that re-hash should have caught (depends on re-hash normalization parity).
   - Suggested fix: align re-hash normalization with matcher normalization to reduce redundant exacts downstream.

6. 🟡 **Minor — Name normalization still misses platform-specific noise tokens:**
   - Current stripping handles grams/mg/pack and some descriptors (lines 47–59, 120–125).
   - Diagnostic samples still show recurring tokens affecting similarity: `AIO`, `Traveler`, `Flavor Line`, `By`, `Device`, platform-prefix forms (`GUMMY -`, `CHEW -`, etc.).
   - Suggested fix: expand token normalization dictionary and test on top rejected pairs.

## Strengths

- Brand dictionary integration is real and correctly implemented (canonical + normalized_key + aliases).
- Matching logic is reasonably transparent and tunable (weights and gates are readable).
- `product_matches` schema handling and indexing are solid.
- Candidate health logging is useful and currently shows no stale candidate rows.

## Summary

The improved matcher is materially better and clearly uses the reseeded brand dictionary, but current recall is constrained by hard category/name gating and incomplete normalization rather than the 0.50 confidence threshold. Next gains should come from canonical-brand pre-grouping plus better rejection telemetry and category/noise handling.

---

## Diagnostic snapshots used

```sql
SET search_path TO public;
SELECT COUNT(*) FROM brand_dictionary; -- 3092
SELECT COUNT(*) FROM gpid_candidates; -- 7438
SELECT COUNT(*) FROM product_matches; -- 3612
SELECT match_type, COUNT(*) FROM product_matches GROUP BY 1 ORDER BY 2 DESC;
-- fuzzy_name 1861, exact 1751
```

```sql
SELECT ROUND(MIN(confidence)::numeric,4) AS min_conf,
       ROUND(MAX(confidence)::numeric,4) AS max_conf,
       ROUND(AVG(confidence)::numeric,4) AS avg_conf,
       PERCENTILE_CONT(ARRAY[0.1,0.25,0.5,0.75,0.9]) WITHIN GROUP (ORDER BY confidence) AS pct
FROM product_matches;
-- min 0.5313, max 1.0000, avg 0.7674, pct {0.6191,0.6665,0.764,0.9,0.9}
```

```sql
SELECT COUNT(*) AS exact_nonidentical_raw
FROM product_matches pm
JOIN products a ON a.id=pm.product_a_id
JOIN products b ON b.id=pm.product_b_id
WHERE pm.match_type='exact'
  AND (COALESCE(lower(trim(a.name)),'') <> COALESCE(lower(trim(b.name)),'')
       OR COALESCE(lower(trim(a.brand)),'') <> COALESCE(lower(trim(b.brand)),''));
-- 1282
```