# Lead Tool Phase 2 PR Review

## Summary
Overall, the Phase 2 scripts are functional and reasonably readable, but several production-readiness gaps remain. The code lacks robust error handling/retry strategies for external services, uses hardcoded absolute paths, and in a few places falls back to mock data in a way that can mask real failures. There are also security concerns (notably SSL verification disabled in the menu scraper) and some logic issues that can skew signal outcomes. I recommend **Request Changes** before production use.

## File-by-File Review

### 1) `google_places_agent.py`
**What’s good**
- Clear CLI, good use of env var for API key.
- Caching design is sensible; includes review history and velocity calculation.
- Dry-run mode is helpful for testing.

**Concerns**
- **Rate limiting/retry**: On HTTP 429, the function sleeps 60s and recursively calls itself with no max retries. This can cause unbounded recursion (stack growth) and indefinite blocking if quota remains exceeded.
- **Velocity calculation**: Uses last `review_count` only; if cache entry missing `review_count` or counts reset, negative velocity may show without safeguards.
- **Cache key**: Uses `business_name|city` only; potential collisions for same-name businesses in different states or same city with multiple locations.
- **Error handling**: Any non-429 HTTP error returns `None`, which is treated as “not found”; this loses operational differentiation between “not found” and “error.”

**Production readiness**
- API key via env var ✅
- Logging is print-based; no levels or structured logs.

---

### 2) `menu_scraper.py`
**What’s good**
- Structured workflow with clear helpers for detection/scraping/analysis.
- Works without external dependencies.
- Good category normalization and gap detection logic.

**Concerns**
- **Security**: SSL verification is explicitly disabled for all HTTP requests. This is a production security risk (MITM exposure). If needed for edge cases, this should be optional and explicitly controlled.
- **Hardcoded paths**: `DEFAULT_INPUT` and `DEFAULT_OUTPUT_DIR` are absolute paths tied to the repo; this reduces portability and breaks in other environments.
- **Rate limiting**: There’s a sleep before scraping menus, but additional HTTP calls (fetch page + API + fallback) don’t enforce consistent per-host throttling. Could trigger blocks.
- **Scraping risks**: Public API endpoints (Dutchie/Jane/Weedmaps) may require auth or block non-browser clients; there is no retry/backoff or error categorization.
- **Detection**: If the platform is unknown, it still attempts HTML-based count estimation, which can produce false positives or be very noisy.

**Production readiness**
- No API keys required (fine), but blocking/ToS risk needs explicit consideration.
- Logging is verbose but not structured.

---

### 3) `job_monitor.py`
**What’s good**
- Clearly defined hiring signals and buyer detection heuristics.
- Has mock-data mode for testing.
- Reasonable output enrichment and summary stats.

**Concerns**
- **Hardcoded path**: `DEFAULT_INPUT` uses an absolute path with a fixed date. This will break as soon as the date changes or in other environments.
- **Search implementation gap**: The docstring says “uses Google/Brave search API,” but actual search only uses Brave API if `requests` and `BRAVE_API_KEY` exist; otherwise it returns an error and falls back to mock data. This can silently turn production runs into mock-mode results.
- **Signal logic skew**: Search results have `posted=None`, and `analyze_hiring_signals` treats `posted=None` as recent (within 30 days). That means *all* search-result jobs count as “recent,” inflating hot/warm signals.
- **Unused imports**: `subprocess`, `json`, and some urllib imports are unused.

**Production readiness**
- Env var usage for Brave API is correct.
- Lack of robust search integration leads to inconsistent outputs.

## Issues Found

### High Severity
1. **Menu scraper disables SSL verification globally** (`menu_scraper.py`, `make_request` / `make_api_request`).
   - Risk: MITM attack, data manipulation, and compliance concerns.

### Medium Severity
2. **Unbounded recursion on rate-limit** (`google_places_agent.py`, `search_google_places`).
   - Risk: stack overflow or indefinite hang if quota remains exceeded.
3. **Job monitor auto-falls back to mock data without flag** (`job_monitor.py`).
   - Risk: production outputs may be fabricated without user awareness.
4. **Hiring signal skew from `posted=None` treated as recent** (`job_monitor.py`).
   - Risk: inflated hot/warm signals; unreliable prioritization.

### Low Severity
5. **Hardcoded absolute paths** (`menu_scraper.py`, `job_monitor.py`).
   - Reduces portability; breaks outside repo environment.
6. **Sparse error classification** (`google_places_agent.py`).
   - Errors indistinguishable from “not found.”
7. **Unused imports** (`job_monitor.py`).
   - Minor maintainability issue.

## Suggestions (Production Improvements)
- Add capped retries with exponential backoff for API calls (Google Places, menu APIs).
- Replace recursive retry with loop and max attempts.
- Make SSL verification optional with a flag (default **on**). Only disable with explicit opt-in.
- Replace hardcoded paths with relative defaults and/or env-configurable directories.
- In `job_monitor.py`, require explicit `--mock` to use mock data; do not silently fallback in production.
- Treat unknown `posted` dates as “unknown recency” and separate from recent counts.
- Use structured logging (at least log level tags), or central logging helper.
- Add user-agent rotation or polite delays for scraping platforms to reduce blocking risk.
- Consider storing per-host request intervals and catching 429s with retry-after headers.

## Verdict
**Request Changes** — The core logic is promising, but security (SSL), reliability (rate limits/retries), and data integrity (mock fallback, recency calculation) require fixes before production release.