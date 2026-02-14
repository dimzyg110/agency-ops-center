# Wartime Sprint Full QA Review (PRs #45, #46, #47, #48)

Date (UTC): 2026-02-14
Reviewer: QA subagent
Repo: `/data/workspace/projects/glass/src`
Sprint spec: `/data/workspace/projects/glass/WARTIME-SPRINT-PLAN.md`

---

## Live DB Verification (requested checks)

Executed with `SET search_path TO public;`.

- Required tables exist: ✅
  - `brand_authority`
  - `parsed_products`
  - `verified_gpids`
  - `product_verified_gpids`
  - `gpid_review_queue`
  - `brand_dictionary_legacy`
- `brand_dictionary` removed: ✅ (`EXISTS = false`)
- Current data state:
  - `brand_authority`: **1001**
  - `parsed_products` by model:
    - `gemini-2.5-flash`: 330 (avg confidence 0.950)
    - `meta/llama-3.3-70b-instruct`: 141 (avg confidence 0.789)
    - `gemini-2.5-pro`: 20 (avg confidence 0.950)
  - `verified_gpids`: **125**
  - `product_verified_gpids`: **96**
- Sample verified GPIDs with prices returned rows as expected.

---

## PR #45 — `wartime/phase0-quarantine`

### Scope reviewed
- `scripts/migrations/014-wartime-quarantine.sql`
- `reports/phase0-quarantine-report.md`

### Findings

1. 🔴 **Critical — Idempotency/robustness gap:**
   `COMMENT ON TABLE brand_dictionary_legacy ...` is unconditional. If `brand_dictionary` never existed (or was dropped), this migration can fail even though `ALTER TABLE IF EXISTS ...` is used.

2. 🟠 **Major — Safe quarantine behavior missing lock:**
   Sprint Phase 0 explicitly calls for `LOCK TABLE brand_dictionary IN ACCESS EXCLUSIVE MODE;` before rename. Migration omits this lock, so concurrent writes during rename are not guarded.

3. 🟠 **Major — Reversibility requirement not implemented in migration assets:**
   Sprint requires rollback path; migration file provides no paired down/rollback script or documented reversible step in migration system.

4. 🟡 **Minor — Constraint completeness:**
   Core CHECK constraints are present for enumerated fields, but no range check exists for `source_confidence` (expected logical range `[0,1]`). Not explicitly required in plan, but recommended for data integrity.

### Verdict
**REQUEST CHANGES**

---

## PR #46 — `wartime/phase1-brand-authority`

### Scope reviewed
- `scripts/brand-authority/scrape-leafly-brands.ts`
- `scripts/brand-authority/scrape-weedmaps-brands.ts`
- `reports/phase1-brand-authority-report.md`
- `reports/top-50-authority-brands.csv`

### Findings

1. 🔴 **Critical — Sprint deliverable incomplete:**
   Phase 1 plan requires `scripts/brand-authority/rank-top-brands.ts` and an orchestrator flow. This PR only adds two scrapers; ranking implementation is missing.

2. 🟠 **Major — Error handling for anti-bot/Cloudflare is weak:**
   `fetch` path silently returns `null` on non-OK responses and does not explicitly detect/annotate challenge pages. Fallback exists, but observability and explicit failure reasons are insufficient.

3. 🟡 **Minor — Internal seeding query not versioned in code:**
   Report mentions adapting join via `products -> prices -> sources` (which is correct for this schema), but actual seeding SQL/script is not included in branch code for repeatability.

4. 🟡 **Minor — Top-50 CSV output quality issue:**
   CSV currently contains only one brand row, which is not operationally aligned with the sprint objective of broad authority ranking output.

### Verdict
**REQUEST CHANGES**

---

## PR #47 — `wartime/phase4-consumer-api`

### Scope reviewed
- `services/api/src/routes/consumer.ts`
- `services/api/src/index.ts`
- `services/consumer-api/Dockerfile`
- `services/consumer-api/railway.toml`

### Findings

1. ✅ **Injection safety:** Queries use Drizzle SQL tagged templates with parameterization (`${...}`), no raw string interpolation for user inputs.

2. ✅ **7-day freshness filter:** Implemented (`pr.scraped_at >= NOW() - INTERVAL '7 days'`). In this DB schema `prices.scraped_at` exists; `collected_at` does not.

3. 🟠 **Major — Response contract mismatch (Sprint §4.4):**
   Search response mostly aligns, but details diverge from contract:
   - No geo filters (`lat`, `lng`, `radius_miles`) implemented though endpoint contract includes them.
   - GPID detail endpoint response shape differs from contract style used for search payload.

4. ✅/🟡 **CORS:** Global CORS is configured in `index.ts` and env-driven. Acceptable, but no consumer-route-specific hardening needed/added.

5. ✅ **N+1 concerns:** No per-item follow-up query loop in search/top endpoints. GPID detail uses two fixed queries (not N+1).

### Verdict
**APPROVE WITH CHANGES**

---

## PR #48 — `wartime/phase3-gpid-lock`

### Scope reviewed
- `scripts/gpid/lock-verified-gpids.ts`
- `scripts/gpid/qa-sample-gpids.ts`
- `reports/phase3-gpid-lock-report.md`
- `reports/phase3-gpid-sample.csv`

### Findings

1. 🟠 **Major — Hash formula parity risk vs sprint SQL canonicalization:**
   Implementation uses JS formatting (`toFixed(3)` + regex trim) rather than the exact SQL canonical expression from plan. Usually equivalent, but cross-language canonicalization drift risk remains.

2. ✅ **Drop rules enforcement:**
   Script filters out accessories, null/blank brands, and null weights before mapping.

3. ✅ **`supporting_product_count` update:**
   Backfill update from `product_verified_gpids` is present and followed by zeroing orphaned rows.

4. 🟠 **Major — QA metrics/report query typing issue:**
   Several reporting queries cast counts to `text` and then order by the text alias (`ORDER BY 2 DESC`), which can sort lexicographically and mis-rank categories/brands in reports.

5. 🟠 **Major — Sprint target miss (live state):**
   Plan target for Phase 3 is **500–1,000 verified GPIDs**; live DB shows **125**.

### Verdict
**REQUEST CHANGES**

---

## Overall Sprint Assessment

**Overall verdict: REQUEST CHANGES before merge of the wartime sprint set.**

- Core architecture direction is correct (quarantine + authority + verified-only consumer path).
- But execution is uneven and not yet at sprint acceptance quality:
  - Missing required Phase 1 ranking script.
  - Phase 0 migration robustness gaps.
  - Phase 3 still below target coverage and has report/query quality issues.
  - Phase 4 is close, but contract alignment is partial.

---

## Critical issues that MUST be fixed before merge

1. Fix PR #45 migration robustness:
   - Guard comment/rename path to be truly idempotent and safe.
   - Add explicit lock behavior or equivalent migration-safe concurrency handling.
2. Complete PR #46 required artifacts:
   - Add `rank-top-brands.ts` per plan (and orchestrated runnable path).
3. Resolve PR #48 canonical hash parity guarantee:
   - Ensure GPID hash canonicalization matches sprint formula exactly and demonstrably.
4. Bring GPID output toward phase gate expectation (or formally downgrade scope with approval).

---

## Nice-to-haves (can wait)

1. Add `source_confidence` range check constraint on `brand_authority`.
2. Improve scraper observability (explicit Cloudflare/challenge detection + structured logs).
3. Align consumer API fully with optional geo filtering contract.
4. Add unit tests for hash canonicalization edge cases and response schema conformance.

---

## Security concerns

- No hardcoded production credentials found in reviewed PR code.
- SQL access patterns in consumer routes are parameterized (good).
- No direct injection vector observed in new route SQL.
- Minor operational security note: scraper scripts default to localhost DB if `DATABASE_URL` missing (acceptable for local dev, but production should fail-fast).
