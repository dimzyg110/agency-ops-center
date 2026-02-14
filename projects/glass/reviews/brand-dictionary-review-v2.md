# Review Feedback

## Scores

| Dimension | Score | Notes |
| --- | --- | --- |
| Correctness | 1/5 | Massive false merges are present (e.g., `Jeeter` has 22,422 aliases including gift cards, generic product strings, and unrelated brands). |
| Completeness | 4/5 | Review requests were covered: false positives, missed merges, canonical quality, alias QA spot checks, and Jeeter deep check. |
| Quality | 2/5 | Seeding output is internally consistent but materially low-quality for brand identity use due over-merging and noisy canonical entries. |
| Brief Adherence | 5/5 | Review directly addresses all requested focus areas with DB evidence. |

## Verdict

**REJECT**

## Issues

1. 🔴 **Critical — False positive merges (catastrophic cluster chaining):** `Jeeter` is clearly over-merged. Query result: `product_count=73,214`, `alias_count=22,422`. Alias sample includes obvious non-brand strings and unrelated entities (examples from sorted aliases): `$100 Gift Card`, `$10 Rolling Tray`, `1000mg &shine`, `1/8 Oz Mochi`, `1906 Bliss Tin`, etc. This is not a valid brand-entity cluster.
   - Likely root cause in `seed-brand-dictionary.ts`: global substring union (`position(a.normalized_brand in b.normalized_brand) > 0 OR ...`) with min length 5 + transitive union-find collapse can snowball unrelated records into giant components.

2. 🔴 **Critical — Non-brand data is being canonicalized as brands:** Top alias-count canons include entries like `Roll Tac 26 50`, `Roll Tac 31 50`, `Roll Tac 39 12%`, `$200 Gift Certificate`, etc. These are product/metadata strings, not brands.
   - Evidence: Top-20-by-alias-count query shows these entries with high alias counts and non-brand alias families.

3. 🟠 **Major — Short-name collision risk confirmed:** Short canonical names include `Vape` (174), `Buds` (121), `Mac` (120), `Haze` (114), `Nea` (104), etc. These are generic terms likely colliding across many contexts.

4. 🟠 **Major — Canonical quality still degraded despite punctuation cleanup:** While trailing punctuation/symbol checks returned clean for canonical strings, many canonical names are still semantically poor/non-brand (examples from random spot checks): `Aio Tac 90 14%`, `Phoenix 7pk I`, `C0070000113`, `V See-Through Quartz`, `Fuck`.

5. 🟡 **Minor — Missed merges appear limited among high-volume brands:** Similarity scan (`>0.75`) with both sides `product_count >= 50` returned no results, suggesting major high-signal duplicates are mostly collapsed. Remaining near-duplicates are mostly low-volume/noisy strings.

6. 🟡 **Minor — Alias-array data quality is inconsistent but mostly structurally valid:** Random 20-entry spot check showed mixed quality: some good (`Wyld` <- `WYLD`, `Space Poppers` variants), some noisy/non-brand (`Aio Tac 90 14%`, code-like IDs, explicit profanity).

## Strengths

- The run achieved substantial dedupe and removed simple formatting variants effectively.
- Canonical string formatting hygiene improved (no obvious trailing punctuation/symbol issues in canonical_name).
- High-count near-duplicate canonical brands appear mostly consolidated.

## Summary

This version over-corrected and is not safe to ship for brand identity use. The merge logic is too aggressive (especially substring + transitive union), producing severe false positives, with `Jeeter` as the clearest failure case.

## Query Notes / Outputs Used

- Top-20 by alias count: shows `Jeeter` + multiple non-brand canonical clusters (`Roll Tac ...`, gift certificates, etc.).
- Jeeter-specific: only one Jeeter canonical exists, with `22,422` aliases and many unrelated terms.
- Short names (<=4 chars): surfaced generic collision-prone canons (`Vape`, `Buds`, `Mac`, etc.).
- Similar canonical names (`similarity > 0.7`): mostly low-quality/noisy strings; no high-volume pair misses at >0.75 and >=50 products.
- Additional targeted checks:
  - `Amber`/`Amber Trichomes`: no canonical entries found (no direct evidence of this specific merge).
  - Canonical trailing punctuation/symbols: none found.
  - Random 20-row alias spot check completed.

## Recommended Fix Direction (before next seed)

- Remove unconditional substring union; only allow strict containment with token-boundary rules and high asymmetry guards.
- Add a hard denylist for non-brand patterns (`TAC`, `%`, dosage/weights, `gift card`, `pre-roll`, `vape`, SKU-like IDs, etc.) before union.
- Require at least one side to look like a proper brand token set before any union.
- Add max-component-size guardrail and manual review queue when clusters exceed a threshold (e.g., >200 aliases).
- Re-run and compare top 50 clusters before execute.
