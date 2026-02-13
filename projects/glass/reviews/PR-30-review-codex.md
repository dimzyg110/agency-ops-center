# Review Feedback

## Scores

| Dimension       | Score | Notes |
| --------------- | ----- | ----- |
| Correctness     | 2/5   | Core behavior is close, but Jane proxy init/fetch failure paths can leak browser processes and miss key retry/error cases. |
| Completeness    | 3/5   | Requested rewrites/logging are present, but robustness requirements are not fully met for network/CF failure modes. |
| Quality         | 3/5   | Code is readable and mostly consistent; a few reliability gaps and noisy logging reduce production quality. |
| Brief Adherence | 3/5   | Implements Playwright Firefox + evaluate(fetch), adaptive Leafly throttling, and Weedmaps progress logs, but misses some edge-case handling the brief explicitly calls out. |

## Verdict

**REQUEST REVISION**

## Issues

1. 🔴 **Critical — Resource leak / lifecycle safety (`scripts/lib/jane-client.ts`):** `BrowserProxy.init()` creates `browser`/`context`/`page` (lines ~60-71 on branch) but has no guard to clean up partial state if any later step throws (e.g., `newContext`, `newPage`, navigation errors outside the local try blocks). In long-running scrapes or repeated retries, this can orphan Firefox processes. **Suggested fix:** wrap init body in `try/catch`, and on failure call `await this.close()` before rethrowing.

2. 🟠 **Major — Error handling gap for `page.evaluate(fetch())` (`scripts/lib/jane-client.ts`):** `browserFetch()` only handles non-OK HTTP responses returned from in-page fetch, but does not handle thrown evaluate-level failures (execution context destroyed, page closed, navigation interruption, network exception) and has no timeout around the in-page fetch call (lines ~107-125). This can fail hard or hang indefinitely. **Suggested fix:** wrap `page.evaluate` in retryable try/catch, add timeout via `Promise.race`, and treat evaluate exceptions similarly to 403 re-init paths.

3. 🟠 **Major — Retry policy misses network/timeout exceptions (`scripts/lib/leafly-client.ts`):** New retry loop in `fetchJson()` (maxAttempts=8) only retries HTTP 429/503 after a response exists (lines ~127-159). If `fetchWithTimeout()` throws (AbortError, ECONNRESET, DNS, transient socket errors), the function exits immediately and bypasses retries. This weakens robustness under real scrape conditions. **Suggested fix:** catch thrown fetch errors inside the attempt loop and retry with same exponential backoff/jitter when retriable.

4. 🟡 **Minor — Adaptive throttle state is process-global and sticky (`scripts/lib/leafly-client.ts`, `scripts/scrape-leafly.ts`):** Exported mutable singleton throttle is shared across all calls in process lifetime. If this module is reused in multiple runs/tests in one process, stale `penaltyMs/total429s` carries forward unexpectedly. **Suggested fix:** add an explicit `reset()` (or instantiate per run) and call it at scrape start.

5. 🟡 **Minor — Potential log-volume regression (`scripts/scrape-weedmaps.ts`):** Added per-attempt/per-page `console.log` in hot loops (`getMenuReadySnapshot`, `scrapePaginatedMenu`, worker flow) significantly increases output volume. This can slow large runs and inflate log storage/costs. **Suggested fix:** gate detailed logs behind a verbose/debug flag and keep structured `logEvent` as default.

## Strengths

- Playwright Firefox migration in Jane client is directionally correct and preserves the required `page.evaluate(fetch(...))` strategy.
- Leafly backoff strategy now has better shape (exponential growth, cap, jitter) and introduces adaptive request pacing.
- Scrape summaries were improved (Leafly throttle stats, Weedmaps run summary/failure typing), which helps post-run diagnostics.
- Weedmaps tab cleanup patterns remain intact (`finally` with `closeTab`), reducing browser-tab leakage risk.

## Summary

This PR is close, but it should not ship yet. Fix the Jane lifecycle/evaluate failure handling and Leafly thrown-error retry behavior first; those are the main reliability blockers for long-running production scrapes.
