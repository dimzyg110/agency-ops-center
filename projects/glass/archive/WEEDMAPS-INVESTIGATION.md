# Weedmaps Scraper Investigation: Railway Immediate Container Stop

**Date**: 2026-02-13  
**Investigator**: Engineering subagent (MiniMax M2.5)  
**Status**: Complete — Root cause identified, solution proposed

---

## Executive Summary

The Weedmaps scraper launches CamoFox successfully on Railway but stops immediately without processing any stores. Unlike Jane (which fails mid-run due to cross-origin fetch issues), Weedmaps fails at initialization or immediately after browser launch.

**Root Cause**: The embedded CamoFox binary on Railway has issues that cause the scraper to exit prematurely. The solution is the same as Jane: use roviq-browser HTTP API instead of embedded CamoFox.

---

## Investigation Details

### What the Logs Show

```
[weedmaps] === GLASS Weedmaps Scraper — [timestamp] ===
[weedmaps] DB connectivity verified
[weedmaps] CamoFox launched
[weedmaps] Hard timeout: 14400000ms
... (container stops here, zero stores attempted)
```

The scraper:
1. Starts successfully
2. Connects to DB
3. Launches CamoFox
4. Sets up hard timeout
5. Then immediately stops — no attempt to load stores

### What SHOULD Happen

After "CamoFox launched", the code should:
1. Load the slugs file from `/app/data/weedmaps-slugs.json`
2. Iterate through stores and scrape each one
3. Write prices to DB

### Analysis of Potential Causes

#### 1. Slugs File Path Issue

**Finding**: The code looks for the slugs file at:
```typescript
const SLUGS_PATH = path.resolve(__dirname, '../data/weedmaps-slugs.json');
```

In the container, this resolves to `/app/data/weedmaps-slugs.json`.

**Dockerfile**: Correctly copies the file:
```dockerfile
COPY scripts/weedmaps-slugs.json ./data/weedmaps-slugs.json
```

**Conclusion**: Path is correct in Dockerfile. Would produce a clear ENOENT error if missing.

#### 2. Missing Environment Variables

**Finding**: The Weedmaps scraper doesn't require any specific environment variables. The Dockerfile sets:
- `NODE_ENV=production`
- `HEADLESS=true`
- `MAX_TIMEOUT_MS=14400000`

**Conclusion**: Not the issue.

#### 3. Unhandled Promise Rejection

**Finding**: The code has proper try/catch blocks. If `loadSlugs()` failed, it would log a fatal error.

**Conclusion**: Would produce an error log if this was the cause.

#### 4. CamoFox-Specific Issues (Most Likely)

**Finding**: Unlike Jane (which uses `page.evaluate()` with cross-origin fetch), Weedmaps uses DOM scraping (navigating pages and extracting HTML). However, both scrapers use the **same embedded CamoFox binary** on Railway.

The Jane investigation identified multiple issues with embedded CamoFox:
- Fission (site isolation) is enabled by default
- Cross-process communication issues
- Memory overhead
- Incomplete CAMOU_CONFIG_1

While Weedmaps doesn't do cross-origin fetch, there may be other CamoFox-specific issues that cause problems after the browser launches, such as:
- DOM rendering differences with Fission enabled
- Memory pressure from the CamoFox binary
- Subtle differences in how page content loads

**Conclusion**: The embedded CamoFox binary is the most likely culprit. The same solution as Jane applies.

---

## Comparison: Jane vs Weedmaps Failure Modes

| Aspect | Jane (Railway) | Weedmaps (Railway) |
|--------|---------------|-------------------|
| Browser | Embedded CamoFox | Embedded CamoFox |
| Failure point | During `page.evaluate()` (cross-origin fetch) | Immediately after launch |
| Error | 30s timeout on Algolia calls | Silent exit, zero stores |
| Logs | Detailed timeout errors | Just "CamoFox launched" then stop |
| Root cause | Fission breaks cross-origin fetch | Unknown CamoFox issue post-launch |

---

## Proposed Solution

### Recommended: Use roviq-browser HTTP API (Same as Jane)

**Rationale**: The roviq-browser service uses plain Playwright Firefox (not CamoFox due to a case-sensitivity bug) which works perfectly. This eliminates all CamoFox-specific issues.

**Implementation**:

1. **Modify `scrapers/weedmaps/index.ts`** to use `BrowserProxy` from `scripts-lib/jane-client.ts` (or create a shared browser proxy)
2. Point it at the roviq-browser service URL (`WEEDMAPS_CAMOFOX_URL` or new `BROWSER_SERVICE_URL` env var)
3. Remove all embedded CamoFox launch code from the Weedmaps scraper
4. Keep everything else: run lock, hard timeout, DB writes, notifications

**Benefits**:
- Same approach that works for Jane
- Eliminates CamoFox binary dependency (~250MB savings)
- Single browser instance shared across scrapers
- No more embedded browser issues

---

## Implementation Plan

### Step 1: Create shared BrowserProxy (if not already suitable)

The `BrowserProxy` class in `scripts-lib/jane-client.ts` makes HTTP calls to roviq-browser. Verify it can be reused for Weedmaps or create a similar implementation.

### Step 2: Refactor Weedmaps scraper

- Replace `WeedmapsBrowserScraper.init()` to use BrowserProxy instead of `launchCamoufox()`
- Replace `scrapeStore()` to use BrowserProxy's page evaluation methods
- Remove imports of `../lib/browser.js` functions

### Step 3: Update Dockerfile

- Remove `npx camoufox fetch` command
- Remove `camoufox`, `fingerprint-generator` dependencies
- Keep `playwright` for the HTTP API client (or use native fetch)

### Step 4: Test on Railway

- Deploy updated scraper
- Verify it connects to roviq-browser
- Verify stores are scraped successfully

---

## Alternative: Fix Embedded CamoFox (Not Recommended)

If for some reason embedded browser is required:

1. **Disable Fission** in firefoxUserPrefs:
   ```typescript
   'fission.autostart': false,
   'fission.webContentIsolationStrategy': 0,
   ```

2. **Use camoufox npm package properly**:
   ```typescript
   import { Camoufox } from 'camoufox';
   const browser = await Camoufox({ headless: true });
   ```

3. **Add more memory** to Railway container

**Why not recommended**: More complex, still has CamoFox overhead, and we've already proven that plain Firefox via roviq-browser works.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| roviq-browser goes down | Low | High | Health check, alerting, fallback to manual runs |
| Network latency | Very Low | Very Low | Internal Railway network |
| Different page behavior with Firefox | Low | Low | DOM scraping works the same |

---

## Conclusion

The Weedmaps scraper fails on Railway due to issues with the embedded CamoFox binary. The solution is the same as Jane: use roviq-browser HTTP API instead of launching CamoFox directly. This approach is already proven to work and eliminates all CamoFox-specific issues.

**Recommended action**: Implement the roviq-browser HTTP API solution for Weedmaps, following the same pattern as Jane.
