# Combined QA Review — PR #45 and PR #46

Reviewer: QA subagent  
Date (UTC): 2026-02-14

---

## PR #45 — `wartime/phase0-quarantine`

### Scope Reviewed
- `scripts/migrations/014-wartime-quarantine.sql`
- `reports/phase0-quarantine-report.md`
- Live DB verification on Railway (`public` search path)

### DB Verification Results
Executed with `SET search_path TO public;`:
- Confirmed existing tables:
  - `brand_authority`
  - `parsed_products`
  - `verified_gpids`
  - `product_verified_gpids`
  - `gpid_review_queue`
  - `brand_dictionary_legacy`
- Confirmed `brand_dictionary` no longer exists (`to_regclass` returned null)
- Confirmed quarantine comment exists on `brand_dictionary_legacy`

### Verdict
**REQUEST CHANGES**

### Findings
1. 🟠 **Major — Migration safety edge case (rename/comment):**
   - Migration uses `ALTER TABLE IF EXISTS brand_dictionary RENAME TO brand_dictionary_legacy;`, but immediately runs `COMMENT ON TABLE brand_dictionary_legacy ...` unconditionally.
   - If this migration is run on an environment where neither `brand_dictionary` nor `brand_dictionary_legacy` exists, `COMMENT ON TABLE` will fail and abort transaction.
   - Recommendation: guard comment with `DO $$ BEGIN IF to_regclass('public.brand_dictionary_legacy') IS NOT NULL THEN ... END IF; END $$;`.

2. 🟡 **Minor — `pgcrypto` extension appears unnecessary in this migration:**
   - `CREATE EXTENSION IF NOT EXISTS pgcrypto;` is included, but no `gen_random_uuid()`/digest/hmac functions are used in this SQL file.
   - Recommendation: remove until actually needed, or document explicit forward dependency in migration comment.

3. 🟡 **Minor — Data quality constraints are permissive in several numeric fields:**
   - No `CHECK` bounds on confidence-style columns (e.g., `source_confidence`, `confidence`) and counts.
   - Recommendation: consider `CHECK (source_confidence BETWEEN 0 AND 1)` and non-negative checks for count columns to prevent bad writes.

4. ⚪ **Nit — `canonical_slug` normalization can leave leading/trailing hyphens:**
   - Expression is valid and functional, but not fully normalized.
   - Recommendation: optionally wrap with trim regex (e.g., remove `^-+|-+$`).

### Direct Answers to Requested Checks
- CREATE TABLE statements: **Structurally valid** and deployed successfully.
- Brand dictionary rename safety: **Partially safe** (rename is guarded, comment is not fully guarded).
- `migration_log` entry: **Looks correct** (`ON CONFLICT DO NOTHING` is acceptable if unique conflict exists on table).
- CHECK constraints (`validation_status`, `source`, etc.): **Present and generally correct**, though additional bounds checks would improve safety.
- Generated `canonical_slug`: **Well-formed enough to run**, but could be tighter normalization.
- `product_verified_gpids` FK to `verified_gpids`: **Makes sense** for many-products-to-one-gpid mapping.
- `pgcrypto` necessity: **Not required by current SQL content**.

---

## PR #46 — `wartime/phase1-brand-authority`

### Scope Reviewed
- `scripts/brand-authority/scrape-leafly-brands.ts`
- `scripts/brand-authority/scrape-weedmaps-brands.ts`
- `reports/phase1-brand-authority-report.md`
- `reports/top-50-authority-brands.csv`
- Live DB verification queries

### DB Verification Results
Executed with `SET search_path TO public;`:
- `brand_authority` row counts by source:
  - `leafly`: 469 (verified 469)
  - `weedmaps`: 225 (verified 225)
  - `internal`: 307 (verified 0)
- `brand_authority` rows with `platform_count >= 3`: **308**

### Verdict
**REQUEST CHANGES**

### Findings
1. 🟠 **Major — Deliverable mismatch: top-50 CSV is not top-50:**
   - `reports/top-50-authority-brands.csv` contains only header + 1 data row.
   - Given DB has 308 brands with `platform_count >= 3`, output is not aligned with expected “top-50 authority brands” deliverable.
   - Recommendation: fix ranking/export query and regenerate file with 50 rows (or explicit documented reason if fewer than 50, which is not the case here).

2. 🟠 **Major — Cloudflare/block handling not explicit:**
   - Scripts implement fetch-first with Playwright fallback, which is good.
   - However, no explicit challenge-page detection (e.g., title/body markers for Cloudflare/Access Denied/captcha), so blocked HTML could be misinterpreted as valid low-quality scrape data.
   - Recommendation: add explicit block detection and hard-fail/fallback path with clear logs.

3. 🟡 **Minor — Upsert loop is row-by-row without batching/transaction:**
   - Functional, but slower and more failure-prone at scale.
   - Recommendation: batch upserts (multi-values insert) or wrap in transaction for consistency.

4. 🟡 **Minor — Internal seeding query validation is only reported, not codified:**
   - Report says join was adapted correctly through `prices` to get `sources.source_type` (`products -> prices -> sources`), which is correct in this schema.
   - But query is not captured as a committed script artifact in this PR, reducing reproducibility.
   - Recommendation: include seeding/backfill SQL in versioned script file.

### Direct Answers to Requested Checks
- Playwright usage pattern: **Yes** (fetch first, Playwright Firefox fallback).
- Upsert correctness into `brand_authority`: **Yes**, conflict target `(canonical_name, source)` is consistent with schema.
- Error handling (Cloudflare/empty responses): **Partial** (empty response fallback present; Cloudflare/challenge handling not explicit).
- Browser/DB cleanup: **Yes**, both scripts close page/browser and release/end DB pool in `finally`.
- Hardcoded credentials: **No exposed secrets**; only localhost fallback DSN.
- Top-50 CSV reasonableness: **No** (currently clearly incomplete).
- Internal seeding query join through prices to source_type: **Conceptually correct** per report.

---

## Overall Recommendation
Both PRs are close but should **not** be approved as-is.  
Primary blockers are:
- PR #45 migration robustness edge case around unconditional comment
- PR #46 incomplete top-50 artifact and weak explicit anti-block handling in scrapers

After those are corrected, re-review should be straightforward.