# Fuzzy Matcher Review (`scripts/matching/fuzzy-matcher.ts`)

## Executive Summary

The matcher is not failing because of one threshold — it is failing due to a **stack of hard gates** that multiply together:

1. Candidate table staleness / referential drift (17,382 -> 6,144 usable pairs)
2. Exact category equality gate
3. Mandatory weight match with strict 5% tolerance **and disallowing missing/0 weights**
4. High name threshold (0.85) after prior hard gates

The biggest bottleneck in current data is **weight gating**. In same-category candidates, **84.8% have missing/0 weight on at least one side**, and current code rejects all of them.

---

## Data Checks Run

Using provided DB (`public` schema):

- `gpid_candidates` total: **17,382**
- `gpid_candidates` with both product IDs still present in `products`: **6,144**
- Missing at least one product record: **11,238** (64.7%)

From the 6,144 joinable pairs:
- Same category (`pa.category = pb.category`): **4,253**
- Different category: **1,891**

Weight buckets (joinable pairs):
- one_missing (NULL or 0 on either side): **5,352**
- within_5pct: **471**
- too_different: **321**

Brand exact (raw lower+trim):
- exact: **6,144**
- non-exact: **0**

Additional funnel checks:
- Same-category pairs: **4,253**
- Same-category with both non-null/non-zero weight: **648**
- Same-category + current 5% weight rule: **432**
- Same-category + allow missing/0 OR within 10%: **4,023**

---

## Constraint-by-Constraint Bottleneck Analysis

## 1) Candidate input quality mismatch (outside matcher SQL but huge practical bottleneck)
- **Where:** `computeMatches()` reads `public.gpid_candidates` (line ~298)
- **Issue:** 17,382 candidates expected, but only 6,144 still join to live products.
- **Estimated elimination:** **11,238 / 17,382 = 64.7%** lost before matching logic is even evaluated.
- **Likely cause:** stale candidate table vs evolving `products` table.
- **Impact:** Massive. This alone makes expected 15% hard to reach.

## 2) Exact category equality hard filter
- **Where:** `WHERE ... AND a.category = b.category` (line ~302)
- **Issue:** Hard gate before scoring. No tolerance/mapping for semantically close classes.
- **Estimated elimination:** from 6,144 -> 4,253 (drops **1,891**, i.e. **30.8%** of joinable pairs).
- **Impact:** High.
- **Notes:** Many mismatches are true cross-type mismatches (flower vs edible, etc.), so this gate is useful but too absolute as a pre-filter.

## 3) Weight is mandatory + missing values always fail + 5% tolerance
- **Where:** weight_match expression (lines ~292-296) and `WHERE weight_match` (line ~315)
- **Issue:**
  - Requires both weights present (`IS NOT NULL` on both)
  - 0 values are effectively treated as real numbers (0 vs non-zero fails)
  - 5% is strict for this domain
- **Estimated elimination:**
  - In same-category candidates (4,253), current rule leaves only **432** (drops **3,821**, ~**89.8%**)
  - Missing/0 weights among same-category pairs = **3,605** (84.8%) and all are auto-rejected today
- **Impact:** **Largest in-script bottleneck**.

## 4) Name gate is strict and combined with prior hard gates
- **Where:** `(name_exact OR name_similarity > 0.85)` (line ~317)
- **Issue:** 0.85 is high, especially after normalization differences and platform naming variance.
- **Estimated elimination:** Using raw candidate similarity, `name_similarity > 0.85` appears on 1,960/6,144 pairs; after category+weight hard gates it reduces further.
- **Impact:** Medium-high; currently secondary to weight bottleneck.

## 5) Brand gate is effectively non-constraining in this dataset
- **Where:** `(brand_exact OR brand_similarity > 0.8)` (line ~316)
- **Observed:** All joinable pairs are brand-exact already (per raw check), so this gate removes little to none right now.
- **Impact:** Low in this snapshot, but could matter in fresher/more diverse candidate sets.

## 6) Excluding products with empty brand during normalization
- **Where:** `if (!normalizedBrand || !category) continue;` (line ~453)
- **Issue:** Any product with blank brand is dropped from temp set entirely.
- **Data context:** ~61,232 priced products have empty brand globally.
- **Impact on current candidates:** likely limited (candidate generation already requires brand similarity > 0.5), but this is a systemic recall risk for future matching logic.

---

## Why `gpid_candidates` can show 17K but matcher outputs ~289

`gpid_candidates` is a **broad trigram prefilter** (name > 0.7, brand > 0.5) intended to surface plausible pairs.

Matcher then applies multiple **hard binary gates**:
1. product must still exist and be joinable
2. category must be exactly equal
3. weight must be present on both sides and within 5%
4. name must be exact or >0.85

This transforms a soft-recall candidate list into a narrow precision filter. The combination (especially stale candidates + weight gate) explains 289-level output.

---

## Normalization Review

## Name normalization (`normalizeName`, lines ~84-106)
- **Too aggressive in some spots:** removes taxonomy tokens (`flower`, `hybrid`, `sativa`, `indica`) which can reduce disambiguation.
- **Not aggressive enough in other spots:** does not standardize common cannabis naming noise deeply enough (e.g., `#` tokens, slash variants, punctuation harmonization beyond edges, common pack/unit variants beyond current regexes).
- **Net effect:** not the primary bottleneck, but can cause missed fuzzy hits at strict 0.85 threshold.

## Brand normalization (`normalizeBrandBase`, lines ~108-116)
- Reasonable baseline cleanup and alias mapping.
- Current pipeline does **not require exact only** (it allows similarity >0.8), but due candidate composition brand is already exact in current joinable set.

---

## Recommended Code Changes (with locations)

## P0 (highest impact): make weight a soft signal, not a hard gate
- **Current:** line ~315 hard requires `weight_match`
- **Change:** remove `WHERE weight_match` from mandatory criteria.
- **Replace with graded logic**, e.g.:
  - If both weights present and within tolerance -> positive score boost
  - If one/both missing or zero -> neutral (not fail)
  - If both present and wildly different -> penalty / require stronger name similarity

Suggested SQL pattern inside `candidate_rows`:
- `weight_status` enum: `missing | close | far`
- Then in ranked WHERE:
  - keep `name`+`brand` constraints
  - optional: exclude only extreme contradictions (e.g., both present and ratio > 2x)

## P1: loosen name threshold and use confidence cutoff
- **Current:** line ~317 uses `> 0.85`
- **Change:** start at `>= 0.78` to `0.82` and rely on composite confidence cutoff (e.g., `confidence >= 0.55`) rather than brittle single gate.

## P1: change category from hard prefilter to mapped/soft check
- **Current:** line ~302 hard `a.category = b.category`
- **Change options:**
  1. Keep hard only for incompatible macro-types, using category mapping table
  2. Otherwise treat as confidence factor, not mandatory equality
- Implement canonical categories (`flower`, `pre-roll`, `vape`, `edible`, `concentrate`, `tincture`, `topical`) and map aliases.

## P2: handle missing brand rows more gracefully
- **Current:** line ~453 drops products with blank brand
- **Change:** allow empty brand through with fallback token (`'unknown_brand'`) and lower confidence; do not skip row entirely.

## P2: normalization improvements
- **Name:** unify separators (`/`, `-`, `_`, `#`), standardize unit tokens, collapse duplicate tokens, optional sort token bag for strain names.
- **Brand:** strip punctuation internally (`&`, `.`, `'`) for similarity key while retaining display text separately.

---

## Suggested Threshold Set (initial)

- Brand: keep `brand_exact OR brand_similarity >= 0.75`
- Name: `name_exact OR name_similarity >= 0.80`
- Weight:
  - missing/zero on either side => neutral
  - both present => close if within 12%
  - >25% difference => penalty
- Category:
  - exact canonical match => boost
  - adjacent compatible classes => neutral
  - incompatible classes => penalty or reject only when other evidence weak

Then gate final rows on **composite confidence** (e.g., `>= 0.55`), not multiple hard booleans.

---

## Priority-Ordered Fix Plan

1. **Remove hard `WHERE weight_match` gate** and treat missing/0 as neutral.
2. **Refresh/rebuild `gpid_candidates`** (or enforce FK validity) so candidate table aligns with live products.
3. **Lower name similarity gate** (~0.80) and shift to confidence-based acceptance.
4. **Replace exact category prefilter** with canonical mapping + soft scoring.
5. Improve normalization passes (name and brand keys) after the above.

---

## Confidence / Caveats

- The database currently shows a major candidate-product drift (11,238 pairs referencing missing products). This may represent environment drift; verify in prod/staging before rollout.
- Some elimination estimates are based on raw product fields, while script uses normalized values; directionality is reliable, exact final counts will vary.
