# WEEDMAPS Fix Verification

Date: 2026-02-12

## Scope Reviewed
- `src/scripts/lib/browser-pool.ts`
- `src/scripts/scrape-weedmaps.ts`
- `src/scripts/lib/config.ts`
- `src/scripts/run-scrapers-sequential.ts` (new)
- `src/scripts/test-weedmaps-parser.ts`
- `src/scripts/lib/weedmaps-parser.ts` (doc comment only; parser regex unchanged)
- `src/scripts/lib/__fixtures__/weedmaps-boston-city-listing.snapshot.txt` (new fixture)

## Fix-by-Fix Verification

### 1) BrowserPool per-instance options + createTab retry/backoff
- **File:** `src/scripts/lib/browser-pool.ts`
- **Lines:** 31-52, 54-75, 85-110, and all endpoint call sites updated across 113-260
- **Implemented:**
  - Added `BrowserPoolOptions` with `baseUrl`, `userId`, `sessionKey`.
  - Constructor now accepts `(maxTabs = 3, opts = {})` and defaults to previous behavior (`CAMOFOX_URL || localhost`, `glass-scraper`, `scrape-session`).
  - `camofoxFetch` now supports per-call timeout argument.
  - `createTab` now retries 4 attempts with 30s timeout/call and exponential backoff (1s, 2s, 4s).
- **Status:** PASS
- **Backward-compatibility check:** PASS (existing `new BrowserPool(CONCURRENCY)` remains valid with unchanged defaults).

### 2) Force local CamoFox for Weedmaps
- **File:** `src/scripts/lib/config.ts`
- **Lines:** 38-41
- **Implemented:** Added `WEEDMAPS_CAMOFOX_URL = 'http://localhost:9377'`.
- **Status:** PASS

- **File:** `src/scripts/scrape-weedmaps.ts`
- **Lines:** 5-13, 340-349
- **Implemented:**
  - Imported `WEEDMAPS_CAMOFOX_URL`.
  - Instantiated BrowserPool with forced local endpoint and Weedmaps-specific user/session IDs.
  - Added startup log: `[wm] CamoFox endpoint: http://localhost:9377 (forced local)`.
- **Status:** PASS

### 3) Discovery progress logging (cities + slugs)
- **File:** `src/scripts/scrape-weedmaps.ts`
- **Lines:** 170-197, 199-251
- **Implemented:**
  - Added city discovery logs (state URL, tab open, gate handling, each scroll pass, extraction totals).
  - Added per-city slug discovery progress logs (city index, match counts, new slug counts, rolling unique total).
  - Added final discovery summary log.
- **Status:** PASS

### 4) Harden cookie/age gate dismissal
- **File:** `src/scripts/scrape-weedmaps.ts`
- **Lines:** 125-158, call sites at 178, 212, 433
- **Implemented:**
  - Replaced one-pass gate handler with `dismissWeedmapsInterstitials()` retry loop (max 4 attempts).
  - Handles both age gate and cookie/banner accept patterns with wait/retry and explicit logging.
  - Updated all Weedmaps flow call sites (city discovery, slug discovery, store scrape).
- **Status:** PASS

### 5) Sequential Dutchie→Weedmaps runner with resilient error handling
- **File:** `src/scripts/run-scrapers-sequential.ts` (new)
- **Lines:** 1-85
- **Implemented:**
  - Runs Dutchie first, then Weedmaps in sequence.
  - If Dutchie fails, logs error and still runs Weedmaps.
  - Prints step-by-step summary with durations and exit causes.
  - Exits non-zero if either step fails.
- **Status:** PASS
- **Error-flow check (required):** PASS (Dutchie failure does **not** skip Weedmaps).

### 6) Parser validation fixture updates (without regex changes)
- **File:** `src/scripts/test-weedmaps-parser.ts`
- **Lines:** 7-25
- **Implemented:** Added city-listing fixture check expecting `raw=0` while keeping existing menu fixture checks.
- **Status:** PASS

- **File:** `src/scripts/lib/__fixtures__/weedmaps-boston-city-listing.snapshot.txt`
- **Implemented:** Added provided city-listing snapshot fixture.
- **Status:** PASS

- **File:** `src/scripts/lib/weedmaps-parser.ts`
- **Lines:** 151-155
- **Implemented:** Added doc comment clarifying function contract (menu snapshots only).
- **Status:** PASS
- **Parser regex changed?:** NO (confirmed unchanged).

## TypeScript / Import Consistency Review
- Read all modified TS files and reviewed syntax + imports.
- No missing imports observed in modified files.
- No new circular dependencies introduced by these changes.
- `BrowserPool` API remains compatible with existing Dutchie usage.

## Notes
- Attempted `npx tsc --noEmit` in `src/` for compile verification, but local TypeScript CLI is not installed in this environment (`This is not the tsc command you are looking for`).
- Per-file manual syntax and import review completed successfully.
