# Verdict: REQUEST CHANGES

## Merge Blockers (must fix)
1. **Orchestrator can hard-hang indefinitely**: all `BrowserPool` HTTP calls (`createTab`, `snapshot`, `navigate`, etc.) use raw `fetch` with **no timeout/abort**. If Camofox endpoint stalls, the run never progresses.
2. **Category mapping bug in parser**: `weedmaps-parser.ts` does not map vape-tagged products (e.g. `VAPORIZERS` / `VAPE`) while `WEEDMAPS_CATEGORIES` includes `vape`. This causes systematic misclassification (defaults to `flower`) and distorts category coverage metrics.
3. **DB connections are never closed** when `--db` is used. Script closes browser pool but never `await db pool.end()`, which can leave process open and look hung post-run.
4. **Pagination stop condition still brittle**: single empty page (plus one retry) can prematurely terminate deep menus under intermittent challenge/load failure.

## Orchestrator Hang Analysis
The most credible root cause is **unbounded I/O waits** in browser API calls:
- `camofoxFetch()` has no timeout.
- Weedmaps flow depends heavily on `snapshot()`/`navigate()` during discovery + pagination.
- A single stalled request blocks the worker loop forever.

Secondary contributors that make this look worse:
- Weedmaps discovery path has minimal progress logging (unlike Dutchie), so long waits look like deadlock right after “BrowserPool initialized”.
- With `--db`, even successful completion may not exit because PG pool remains open.

**Fix (clear):**
- Add request timeout + abort in `camofoxFetch` (e.g. 30–45s `AbortController`) and throw typed timeout errors.
- Add bounded retries with backoff for `snapshot/navigate/createTab` at call-sites.
- Add per-store timeout budget (e.g. fail store after N minutes).
- Ensure finalizer closes DB pool (`await pool.end()` in `main` finally path for DB mode).
- Add progress logs at discovery/store/page boundaries.

## Parser Assessment
What’s good:
- Good fixture-driven extraction/parsing split.
- Brand blocklist + `brandParseFailed` signal present.
- Rating suffix removal and THC/CBD extraction are solid for provided fixture style.

Issues:
- Missing vape tags in `CATEGORY_TAGS` (blocker).
- `stripCategoryTag()` defaults unknown tags to `flower`, which can inflate flower counts.
- Brand fallback (`tail3/tail2/tail1`) can still mis-assign brand for atypical titles.
- `extractWeedmapsProductsFromSnapshot()` assumes a specific snapshot shape/window; acceptable for MVP but should be monitored with more fixtures.

## Pagination Assessment
Strengths:
- Correct move to all-products `?page=N` iteration.
- Uses `NNN Products` hint + 24/page expected pages.
- De-dupes by href across pages.
- Includes one empty-page retry (hardening step).

Gaps:
- One retry may be insufficient for transient challenge pages.
- No explicit blocked/challenge detection; empty extraction is treated as content absence.
- Could silently under-capture large menus.

Recommendation:
- Require either 2 consecutive empty pages **with non-challenge state** or explicit end-of-results markers before break.
- Add challenge signature detection and retry/backoff.

## Review Changes Verification (all 5)
1. **Brand blocklist**: ✅ Incorporated (`NON_BRAND_TOKENS`, `brandParseFailed`).
2. **`weedmaps_v1` parser type**: ✅ Incorporated in `insertPrice(..., 'weedmaps_v1')`.
3. **Auto-resume**: ✅ Incorporated (`getActiveRunForToday`, skip completed source IDs).
4. **Pagination hardening**: ✅ Partially incorporated (empty-page retry exists; still needs stronger challenge handling).
5. **Fixtures/tests**: ✅ Incorporated (`diem`, `missing-brand`, `multiword-brand` + test runner).

## Recommended Fixes
- Add timeout/abort + retry wrappers for all BrowserPool network calls.
- Add `try/finally` in `main` to always close browser + DB pool.
- Extend category tag mapping for vape labels and avoid defaulting unknown tags to flower when ambiguous.
- Strengthen pagination termination logic and challenge detection.
- Add structured logs: discovery city progress, store start/end, page index, retry counts, timeout errors.

## What's Good
- Architecture mirrors proven Dutchie pipeline patterns well.
- DB run/job integration is strong (`run`, `job`, quality metrics, summary snapshots).
- Parser and orchestrator are close to production shape.
- Core requested enhancements from prior review are largely present.

With the hang hardening + category mapping fixes, this is merge-ready for controlled rollout.