# Lead Tool Phase 3 Review

## Summary
Overall, the Phase 3 scripts are clear and mostly production-ready for a lightweight batch pipeline. They avoid hardcoded secrets, use env vars for API keys, and include basic rate limiting. The integration in `lead_enricher.py` is straightforward and the data flow is sensible. Main gaps: limited error handling/logging (prints only), weak/fragile Google fallback scraping, and some edge cases in website detection and CLI passthrough (e.g., `--limit` inconsistencies). I recommend **Request Changes** before production use.

## File-by-File Review

### 1) `decision_maker_lookup.py`
**What it does:** Searches LinkedIn via Brave (or Google HTML fallback) for GM/Buyer roles and chooses best candidate by confidence score.

**Strengths**
- Clear structure and well-factored helpers.
- Uses env var `BRAVE_API_KEY` and has dry-run mode.
- Basic rate limiting (`RATE_LIMIT_SECONDS`).
- Adds output columns safely without overwriting existing fields.

**Concerns / Edge Cases**
- Google fallback scrapes HTML (fragile, likely to break or trigger blocking). No backoff or captcha handling.
- `score_confidence()` hardcodes “Massachusetts/MA” which may not apply to all datasets.
- Candidate parsing relies on LinkedIn title format; can miss non-standard titles.
- No retry logic for transient network errors.
- Logging only via `print()`; no structured logs.

### 2) `mso_mapper.py`
**What it does:** Classifies operators as MSO/local chain/independent via name matching and optional website scan.

**Strengths**
- Clear normalization and detection pipeline.
- Rate limiting for website fetch.
- Graceful fallback to dataset frequency (“local chain” if ≥3 locations).

**Concerns / Edge Cases**
- Website HTML parsing is best-effort; no robots/blocked handling, no retries, no timeouts beyond request timeout.
- `detect_from_website()` catches all exceptions silently (no logging), making failures invisible.
- `ABOUT_KEYWORDS` detection is simplistic and may miss or mis-detect localized links.
- `location_count` computed after applying `--limit`, which can undercount chains when limiting.

### 3) `lead_enricher.py`
**What it does:** Orchestrates the full enrichment pipeline and writes final output.

**Strengths**
- Simple, readable pipeline structure.
- Uses env vars for base/output paths.
- `--skip-existing` helps resumability.

**Concerns / Edge Cases**
- `run_script()` ignores `dry_run` argument (not used) and doesn’t pass through to menu/job steps (only some steps support `--dry-run`); inconsistent.
- `--limit` is not passed to Google Places step, and limit for chain detection could be skewed in `mso_mapper`.
- `subprocess.run(..., capture_output=False)` provides no stdout capture or logging; failures only surface via exit code.
- No explicit check that scripts exist; if missing, pipeline fails with a generic error.

## Issues Found (Severity)

**High**
- Fragile Google HTML fallback in `decision_maker_lookup.py` risks frequent breakage and blocking. Needs a supported API or robust handling.

**Medium**
- Silent failure in `mso_mapper.detect_from_website()` swallows exceptions with no logging.
- `--limit` causes inaccurate `location_count` and can misclassify chains when limiting.
- Inconsistent `--dry-run`/`--limit` propagation in `lead_enricher.py`.

**Low**
- Hardcoded “Massachusetts/MA” in confidence scoring may reduce relevance outside MA.
- Lack of retry/backoff for transient network errors in both lookup and mapper.
- Print-based logging only; no log levels or structured logs.

## Suggestions
1. Replace Google HTML scraping with a supported search API or document it as strictly best-effort and add exponential backoff + user-agent rotation.
2. Add retries with backoff for network calls (Brave API, website fetch).
3. In `mso_mapper`, log exceptions with context (URL) rather than silent `except`.
4. Ensure `--limit` is passed consistently to all steps and note that it impacts `location_count`; consider computing counts on full dataset even when limiting.
5. Make `score_confidence()` location heuristic configurable (e.g., via env var or CLI).
6. Add structured logging (logging module) with log levels.

## Verdict
**Request Changes**

Primary blockers: fragile Google scraping, silent failures, and inconsistent limit/dry-run propagation. With the fixes above, the pipeline should be solid for production use.
