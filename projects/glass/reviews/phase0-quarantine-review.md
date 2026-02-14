# Review Feedback — PR #45 `wartime/phase0-quarantine`

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Correctness | 1/5 | Reported DB actions do not match live DB state; quarantine not present. |
| Completeness | 2/5 | Includes a narrative report, but no committed migration/scripts and no enforceable code changes. |
| Quality | 2/5 | Documentation is structured, but evidence is internally inconsistent with verification query results. |
| Brief Adherence | 2/5 | Intended checklist addressed in prose, but core required outcome (actual quarantine + tables) is not true in target DB. |

## Verdict

**REJECT**

## Findings by Category

### 1) SQL Schema Quality

1. 🔴 **Critical — Execution reality mismatch:** Live Railway verification shows only `public.brand_dictionary` exists; none of the expected new tables exist (`brand_authority`, `parsed_products`, `verified_gpids`, `product_verified_gpids`, `gpid_review_queue`), and `brand_dictionary_legacy` does not exist.
   - Verification run:
   ```sql
   SET search_path TO public;
   SELECT to_regclass('public.brand_dictionary') AS brand_dictionary,
          to_regclass('public.brand_dictionary_legacy') AS brand_dictionary_legacy,
          to_regclass('public.brand_authority') AS brand_authority,
          to_regclass('public.parsed_products') AS parsed_products,
          to_regclass('public.verified_gpids') AS verified_gpids,
          to_regclass('public.product_verified_gpids') AS product_verified_gpids,
          to_regclass('public.gpid_review_queue') AS gpid_review_queue;
   ```
   Returned: only `brand_dictionary` non-null.

2. 🟠 **Major — Schema review blocked by absence:** Because the tables are not present in target DB, practical validation of constraints/index behavior is blocked. On paper, the SQL in the report matches the sprint plan definitions for these tables.

3. 🟡 **Minor — `canonical_slug` normalization quality:** Expression used in plan/report (`regexp_replace(lower(trim(canonical_name)), '[^a-z0-9]+', '-', 'g')`) may leave leading/trailing hyphens (e.g., `"  #1 Brand! " -> "-1-brand-"`). Consider wrapping with `trim(both '-' from ...)` in a follow-up migration.

### 2) Sprint Plan Compliance

1. 🔴 **Critical — Not actually executed in environment:** Phase 0 required `brand_dictionary` rename and `brand_authority` creation. Current DB indicates neither persisted.

2. 🟠 **Major — PR contents are non-operational:** `git diff main..wartime/phase0-quarantine` shows only one added file:
   - `reports/phase0-quarantine-report.md`
   No migration SQL files, no scripts, no job-disable changes. This makes execution non-reproducible and unauditable from code.

3. 🟡 **Minor — Scope deviation vs “exact SQL from plan”:** Report claims Phase 2/3/expansion tables were created during Phase 0 PR. That is a process deviation; could be acceptable only if explicitly approved and actually applied.

### 3) Safety Check

1. 🟠 **Major — Cannot validate legacy preservation:** Since `brand_dictionary_legacy` does not exist, we cannot confirm preserved legacy data under renamed table.

2. 🟡 **Minor — Protected tables change risk not evidenced:** No repo DDL touching `product_matches`, `gpid_verdicts`, `products`, `prices` in this PR diff (report-only change). No evidence of modifications from code side.

3. 🔴 **Critical — Reversibility claim invalid currently:** Reversible quarantine presumes rename happened. It did not (or was reverted), so rollback path in plan is not currently applicable.

### 4) Code References / Runtime Risk

1. 🟠 **Major — `fuzzy-matcher.ts` depends on `public.brand_dictionary`:** `scripts/matching/fuzzy-matcher.ts` queries:
   ```sql
   SELECT canonical_brand_name, normalized_key, aliases
   FROM public.brand_dictionary
   ```
   - If quarantine is re-applied without compatibility layer, this script will fail at runtime (`relation public.brand_dictionary does not exist`).

2. 🟠 **Major — `seed-brand-dictionary.ts` also creates/writes `public.brand_dictionary`:** Multiple references remain; these are not safe long-term once quarantine is truly applied.

3. 🟡 **Minor — Reported reference scan is directionally correct:** Listed files are plausible breakpoints and should be tracked in Phase 1 remediation.

### 5) Top Brands Preview Quality

1. 🟡 **Minor — List is mostly plausible for MA cannabis:** `Nature’s Heritage`, `Fernway`, `Happy Valley`, `Rythm`, `Insa`, `Tower Three`, `Bountiful Farms`, `Wyld`, `Levia` look reasonable.
2. 🟡 **Minor — Potential junk/generic entries to review:** `holiday`, `sparq`, possibly `select` can be ambiguous and may require brand-authority disambiguation rules.
3. 🟡 **Minor — Possible notable omissions in top sample:** Depending on dataset coverage, brands like `Smyth`, `Nanticoke`, `Good News`, `Berkshire Roots`, `Theory Wellness` might be expected; absence may be due to platform-count filter.

## Issues that must be fixed before merge

1. Execute (or re-execute) Phase 0/declared SQL against the target Railway DB and capture fresh evidence outputs.
2. Re-run required verification query proving:
   - `brand_dictionary` **does not** exist
   - `brand_dictionary_legacy` **does** exist
   - all 5 new tables exist
3. Commit operational artifacts to repo (migration SQL / scripts / runbook), not only a report file.
4. Add compatibility plan for `brand_dictionary` runtime dependencies (update scripts to `brand_dictionary_legacy` or temporary compatibility view) before next fuzzy-match run.
5. Include explicit before/after row counts to prove legacy data preservation.

## Recommendations for Phase 1+

- Add migration files under versioned migrations directory with idempotent up/down steps.
- Add a temporary compatibility view if needed:
  `CREATE VIEW public.brand_dictionary AS SELECT * FROM public.brand_dictionary_legacy;`
  (only if required for short-term script continuity).
- Add CI check that fails if `scripts/matching/*` still references deprecated `brand_dictionary` directly after quarantine.
- Add a post-migration smoke script that prints `to_regclass(...)` checks and key row counts.

## Summary

PR #45 is **not mergeable** in its current state. The committed deliverable is report-only, and live DB verification contradicts the report’s core claims. Re-run and codify the migration with reproducible artifacts, then re-submit for review.