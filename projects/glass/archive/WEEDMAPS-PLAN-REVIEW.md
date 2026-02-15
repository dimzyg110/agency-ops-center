# Verdict: APPROVE WITH CHANGES

## Executive Summary
The Weedmaps plan is strong and production-oriented: it correctly reuses the Dutchie pipeline architecture, accounts for Weedmaps-specific UX (age gate + pagination), and includes realistic orchestration details. However, there are several correctness and resilience gaps that should be fixed before implementation starts, primarily in parser robustness, pagination stop conditions, and cross-platform dedup assumptions. With the critical changes below, this is a solid MVP plan.

## Plan Completeness Assessment
**Covered well:** discovery, store/category scraping flow, parser module design, pagination handling, DB integration, run/job tracking, and phased timeline. The plan also includes fixture testing, acceptance criteria, and risk register.

**Missing / under-specified:**
- Explicit quality guardrails at Weedmaps job level (parallel to Dutchie fixes: brand parse failure thresholds, suspicious category-coverage checks).
- Concrete auto-resume behavior integration in `scrape-weedmaps.ts` (plan references parity but does not show it wired in).
- Parser-type propagation into `insertPrice` call path (current shared `db.ts` defaults to `dutchie_v2`; must be explicit).
- Operational handling for anti-bot/challenge states (Cloudflare/challenge page detection and retry/backoff policy).

## Parser Design Review
The proposed parser is directionally good, but several regex/parsing assumptions are brittle against real Weedmaps snapshots:

- **Link detection is too strict**: `link "... product detail page" [eN]` may fail if snapshot format omits `[eN]`, changes quote shape, or includes minor text variants. Add fallback URL-driven extraction using `/dispensaries/{slug}/menu/` as primary signal.
- **Category tag regex risk**: dynamic union from human strings is fine, but should be escaped to avoid regex metachar issues in future tag additions.
- **Brand inference can mis-assign**: taking first dash segment as brand will fail for products where first segment is not a brand or where brand is missing; should apply Dutchie-learned non-brand blocklist and confidence scoring.
- **Weight extraction from `lastSeg` is too narrow**: misses common formats (`1/8 oz`, spaced units, pack counts like `10pk`, mixed text). Should defer to normalizer where possible and keep parser permissive.
- **THC/CBD extraction** is acceptable, but should avoid stripping meaningful name tokens when “THC” appears in branded phrases.
- **Rating parsing** is fine as optional metadata.

Net: parser approach is acceptable for MVP if backed by stronger fixtures and explicit quality thresholds.

## Pagination Strategy Review
Using `?page=N` and dedup-by-href is the right base strategy. For 600+ products (e.g., 28 pages), this should work if hardened:

- **Good:** page-based navigation, dedup set, safety cap, continue-on-page-failure.
- **Needs change:** stopping when `newCount === 0` can prematurely terminate on transient load failures/challenge pages. Require 2 consecutive empty pages or verify expected pagination markers before stopping.
- **Count extraction (`/\d+ Products?/`) is fragile** when multiple counters exist on page; anchor extraction near product grid context if possible.
- **Efficiency:** single-tab sequential pagination per category is fine; do not open page-per-tab for deep stores due to tab/session pressure.

## Lessons Learned Integration
The plan partially incorporates Dutchie fixes, but not fully:

1. **Brand blocklist / quality signals**: not clearly integrated into Weedmaps parser logic (must add).
2. **Price idempotency**: plan proposes `insertPrice(parserType)` change, but must be reflected end-to-end and keep daily upsert behavior.
3. **Auto-resume**: mentioned in CLI, but run-resume logic should be explicit in orchestrator pseudocode.
4. **Schema alignment**: plan is mostly aligned, but avoid introducing unused phase-2 tables in MVP PR unless needed now.
5. **Quality guardrails**: acceptance criteria are too soft; add hard fail/suspicious thresholds as in Dutchie.

## Cross-Platform Dedup Assessment
The platform-prefixed SKU strategy is a good start (`DUTCHIE-` vs `WEEDMAPS-` with shared hash body), but hash equality across platforms is only as good as normalization consistency.

Risks:
- Brand/name variants across platforms break hash parity.
- Different packaging text can shift canonical name.
- Category mismatch between source taxonomies can split matches.

Recommendation: keep current strategy for MVP, but define canonical key generation rules centrally in `normalizer.ts` and validate on sampled cross-platform pairs before claiming match quality.

## Risk Assessment
Biggest production risks:
1. **Parser drift** from snapshot formatting changes.
2. **Anti-bot/challenge intermittency** causing false-empty pages/categories.
3. **Deep pagination runtime variance** on large stores.
4. **Shared CamoFox session constraints** (tab/session collisions if multiple runs overlap).
5. **False confidence in dedup** without measured match rate.

Mitigations needed now: challenge detection, retry/backoff with capped attempts, stronger fixture coverage, and run-level quality alarms.

## Timeline Assessment
**3–4 days is realistic for MVP** if scope stays tight (discovery + scrape + load + fixtures + 5/20-store validation). It becomes unrealistic if phase-2 crossref tables/matching logic are included in same implementation window.

## Critical Issues (must address)
1. Add Weedmaps parser guardrails equivalent to Dutchie fixes: non-brand blocklist, `brandParseFailed` signal, and fail/suspicious thresholds persisted in `quality_metrics`.
2. Make `insertPrice` parser type explicit per call (`weedmaps_v1`) and verify idempotent upsert semantics remain intact.
3. Implement explicit auto-resume logic in `scrape-weedmaps.ts` (reuse active run, skip succeeded sources).
4. Harden pagination stop logic (no single-empty-page early stop; detect challenge/blocked states).
5. Expand fixtures to include edge cases: missing brand, missing THC, multi-word brands, `1/8 oz`, ratings absent/present, and at least one 20+ page store excerpt.

## Recommended Changes (nice to have)
1. Escape dynamic regex keys when building category-tag regex.
2. Add Cloudflare/challenge signature detection and exponential backoff before marking category empty.
3. Keep phase-2 schema (`store_crossref`, `product_crossref`) out of MVP migration unless immediately consumed.
4. Add per-store timeout budget and retry counters to avoid long-tail stalls.
5. Capture store-level metadata extraction in a separate optional pass to keep product scrape path fast.

## What's Good
- Excellent reuse of proven Dutchie architecture and shared libs.
- Correct identification of Weedmaps-specific mechanics (age gate + `?page=N`).
- Clear orchestrator flow and practical CLI flags.
- Good acceptance checklist and realistic runtime/cost thinking.
- Strong phased plan that can ship MVP quickly if critical hardening items are applied.