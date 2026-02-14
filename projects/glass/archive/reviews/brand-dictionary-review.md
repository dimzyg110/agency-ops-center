# Brand Dictionary Seeder Review

Date: 2026-02-14  
Reviewer: QA subagent

## Scope
Reviewed:
- `/data/workspace/projects/glass/src/scripts/matching/seed-brand-dictionary.ts`
- `/data/workspace/projects/glass/reports/brand-dictionary-2026-02-14.md`
- Live DB output in `public.brand_dictionary` using provided `DATABASE_URL`

---

## Executive Summary
The seeder is working for basic formatting/case/symbol variants, but the 6.79% merge rate is plausibly low because the current logic only merges:
1) exact normalized forms, and 2) high raw trigram similarity (`> 0.75`) with a strict length-diff cap.

Known examples were mostly merged correctly (**Cali-Blaze/Cali Blaze, Good News™, PAX®, Nature’s/Natures, Betty’s/Bettys, Coast Cannabis Co™/Co.**) except **Perpetual vs Perpetual Healthcare**, which remains split.

Biggest quality risk: source `products.brand` appears noisy (many rows are clearly product/category strings), and the current script seeds those directly into brand_dictionary.

---

## Diagnostic Query Findings

### Known aliases from brief
- ✅ `Cali-Blaze` merged with alias `Cali Blaze`.
- ✅ `Good News` merged with alias `Good News™`.
- ✅ `Pax` merged with aliases `PAX`, `PAX®`.
- ✅ `Nature's Heritage` merged with aliases including `Natures Heritage` and apostrophe variants.
- ✅ `Betty's Eddies` merged with apostrophe variant.
- ✅ `Coast Cannabis Co™` / `Coast Cannabis Co.` merged into canonical **`Coast Cannabis`** (note: suffix stripped).
- ❌ `Perpetual` and `Perpetual Healthcare` are still separate canonicals.
  - DB counts: `Perpetual` = 364, `Perpetual Healthcare` = 457
  - `similarity('Perpetual','Perpetual Healthcare') = 0.47619048`

### Alias distribution
- `has_aliases`: **7,545**
- `singleton`: **11,251**

This confirms many brands still remain singleton entries.

### Missed high-confidence merges observed
From targeted similarity scans among larger brands:
- `Charge Bar` vs `Charge Bars` (sim 0.769) → not merged
- `Seed And Strain` vs `Seed & Strain` (sim 0.733) → not merged

These are likely true aliases and indicate misses due current pipeline constraints.

---

## Code Review Findings

## 1) Normalization behavior (™®© and punctuation)
`normalizeBrand()` removes `™®©` **before** normalized bucketing, so those variants merge via normalized buckets.

However, similarity matching is computed on **raw strings** in SQL (`similarity(a.brand, b.brand)`), not normalized strings. So punctuation/symbol/corporate suffix normalization does **not** help trigram merge candidate generation.

### Gap
- Normalization and similarity are not aligned to the same text representation.

---

## 2) Threshold and matching logic
Current matching query:
- trigram `%` + `similarity > minSimilarity` (default 0.75)
- `abs(length(a.brand)-length(b.brand)) <= 8`
- `LIMIT 500`

### Gaps
1. **Hard limit of 500 similarity pairs** can truncate merge candidates at this scale (20k+ distinct strings).  
2. **Length-difference cap (<=8)** blocks many prefix/suffix brand variants with legal/entity words.  
3. **Single global threshold (0.75)** is blunt:
   - Too strict for some token-level variations (`And` vs `&`, singular/plural)
   - Too permissive if globally lowered (especially short strings)

### Short-name recommendation
Do **not** lower threshold globally for 3–4 char names (`RAW`, `PAX`, etc.). For short strings, lower thresholds increase false positives quickly. Use stricter short-name rules, and only lower thresholds for longer multi-token names with token-overlap safeguards.

---

## 3) Canonical picker quality
Canonical is chosen by highest product count among raw group members, then normalized:
```ts
canonicalRaw = most frequent member
canonicalName = normalizeBrand(canonicalRaw) || canonicalRaw
```

### Gaps
- Can produce over-generic canonicals by stripping terminal `co`/`inc`/`llc`.
  - Example: `Coast Cannabis Co.` canonicalized to `Coast Cannabis`.
- Alias set can include normalized artifacts and quoted garbage variants.
- No scoring for “cleanest display name” (e.g., punctuation quality, token completeness, casing consistency).

---

## 4) Edge cases checked
- `INSA` vs `Insa`: handled correctly (in aliases under canonical `Insa`).
- Very short canonical names (3–4 chars) are common and noisy (`Raw`, `Cali`, `Dcc`, `Mac`, etc.).
- Brand dictionary includes many likely non-brand tokens (`(h)`, `(i)`, `Roll`, `Cart`, etc.), suggesting upstream brand-field contamination and/or weak filtering.

---

## 5) Report quality / suspicious merges section
Report’s “suspicious merges (0.70–0.80)” table is mostly product-title-like strings, not brand entities. This suggests manual review workload is noisy and less actionable for true brand alias QA.

No clear catastrophic false-positive merge found in sampled known brands, but there is significant **data quality noise** in what is treated as a brand.

---

## Missed Merges (Specific Examples)
1. **Perpetual** ↔ **Perpetual Healthcare** (not merged; likely should be, per brief)
2. **Charge Bar** ↔ **Charge Bars** (sim 0.769, not merged)
3. **Seed And Strain** ↔ **Seed & Strain** (sim 0.733, not merged)

---

## False Positives / Suspicious Outcomes
Notable concern is less “bad merged brand pairs” and more **bad brand candidates** being included as canonicals (likely product/category values), e.g.:
- `(h)`, `(i)`
- `Roll`, `Cart`, `Each`, etc.

These pollute dictionary quality and reduce meaningful merge ratio.

---

## Priority-Ordered Fixes

### P0 (must do)
1. **Normalize before similarity candidate generation in SQL**
   - Build temp table with `normalized_brand` and compare on that field (or dual compare raw + normalized).
2. **Remove/raise `LIMIT 500` for similarityPairs**
   - This is likely clipping valid merges on a 20k+ brand universe.
3. **Add brand-quality filters before grouping**
   - Exclude obvious non-brand tokens/patterns (`(h)`, `(i)`, generic category-only strings, quoted fragments).

### P1 (high value)
4. **Token-aware merge heuristics for legal/entity suffixes and connector variants**
   - Handle `&` vs `and`, singular/plural (`bar`/`bars`), and suffixes like `healthcare`, `labs`, `collective`, etc. with controlled rules.
5. **Length-aware thresholding**
   - Keep strict threshold for short names (<=4 chars), allow slightly lower for longer multi-token names with high token overlap.

### P2 (quality polish)
6. **Canonical-name scoring function**
   - Prefer clean human-readable display names (no trailing quotes/punctuation artifacts), not only highest count.
7. **Improve report sections**
   - Split “brand-level suspicious merges” vs “product-like noise entries” for actionable QA.

---

## Final Assessment
Seeder is directionally correct for basic formatting aliases, but merge recall is constrained by raw-string similarity gating, candidate cap, and noisy upstream brand values. The 6.79% reduction is believable under current logic, and likely improvable with normalized/token-aware candidate generation plus stricter pre-filtering of non-brand values.
