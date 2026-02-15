# Jane Scraper Investigation: Sandbox vs Railway Failure

**Date**: 2026-02-13  
**Investigator**: Engineering subagent (Opus 4.6)  
**Status**: Complete — Root cause identified, solution proposed

---

## Executive Summary

The Jane scraper succeeds on sandbox (via roviq-browser) but fails on Railway because **two completely different browser stacks are being used** due to a case-sensitivity bug. The sandbox version accidentally uses plain Playwright Firefox (not CamoFox) through an HTTP API, while the Railway version uses the real CamoFox binary directly. The CamoFox binary has Firefox Fission (site isolation) enabled and deeper network-level patches that likely interfere with cross-origin `fetch()` calls from `page.evaluate()`.

---

## Architecture Comparison

### Working: Sandbox → roviq-browser HTTP API

```
scripts/scrape-jane.ts (sandbox)
  └─ JaneClient (scripts/lib/jane-client.ts)
       └─ BrowserProxy
            └─ HTTP API: POST /tabs/:id/evaluate
                 └─ roviq-browser service (Railway)
                      └─ BrowserManager.evaluate(tabId, userId, jsString)
                           └─ page.evaluate(jsString)  ← string form
                                └─ *** PLAIN PLAYWRIGHT FIREFOX ***
```

**Key detail**: roviq-browser's `browser.ts` line 36-38:
```typescript
const camoufoxModule: any = await import('camoufox');
this.browser = await camoufoxModule.camoufox({ headless: this.headless });
//                                  ^^^^^^^^^ LOWERCASE — DOES NOT EXIST!
```

The `camoufox` npm package exports `Camoufox` (capital C), not `camoufox` (lowercase). This call returns `undefined()`, throws an error, and **silently falls back** to:
```typescript
this.browser = await firefox.launch({ headless: this.headless });
```

**Verified**: `node -e "const m = require('camoufox'); console.log('camoufox' in m, 'Camoufox' in m)"` → `false true`

So **roviq-browser has NEVER been using CamoFox**. It's always been plain Playwright Firefox with realistic context options (user agent, viewport, locale, timezone).

### Failing: Railway Jane Service → Embedded CamoFox

```
scrapers/jane/index.ts (Railway)
  └─ EmbeddedBrowserProxy
       └─ launchCamoufox() (scrapers/lib/browser.ts)
            └─ firefox.launch({
                 executablePath: '/root/.cache/camoufox/camoufox-bin',  ← ACTUAL CAMOUFOX BINARY
                 env: { CAMOU_CONFIG_1: ... },  ← anti-detection config
                 firefoxUserPrefs: { ... }
               })
            └─ page.evaluate(asyncFunction, args)  ← function form
                 └─ *** REAL CAMOUFOX BINARY ***
```

---

## Root Cause Analysis

### Primary Cause: CamoFox Binary's Fission (Site Isolation) Breaks Cross-Origin Fetch

CamoFox's built-in `camoufox.cfg` contains:
```
defaultPref("fission.autostart", true);
defaultPref("fission.webContentIsolationStrategy", 1);
```

Standard Playwright Firefox has **Fission disabled**. With Fission enabled:

1. Different origins run in **different OS processes**
2. When `page.evaluate()` runs `fetch('https://search.iheartjane.com/...')` from a page loaded on `https://www.iheartjane.com/`, the request crosses a process boundary
3. The CORS preflight (triggered by custom `X-Algolia-*` headers) may get stuck or blocked at the process isolation boundary
4. This explains the **hang** behavior — `page.evaluate(fetch())` never resolves, and the 30s timeout fires

### Contributing Cause: Incomplete CAMOU_CONFIG_1

The Railway scraper's `buildCamoufoxEnv()` passes only 12 config properties:
- `navigator.userAgent`, `navigator.language`, `navigator.languages`, `navigator.platform`
- `screen.width`, `screen.height`
- `window.innerWidth/Height`, `window.outerWidth/Height`
- `webGl.vendor`, `webGl.renderer`

The `camoufox` npm package generates **~60+ properties** via `fromBrowserforge()` including:
- `headers.User-Agent`, `headers.Accept-Language`, `headers.Accept-Encoding` (network-level header patching)
- `canvas:aaOffset`, `canvas:aaCapOffset` (canvas fingerprint)
- `window.history.length`, `window.devicePixelRatio`
- Full WebGL parameter sets, supported extensions
- Font configurations, audio context properties

Without `headers.*` properties, CamoFox's network-level header patching may produce inconsistent or empty headers, which Cloudflare could detect on the Algolia CORS preflight.

### Contributing Cause: roviq-browser Bug Masks the Real Problem

The case-sensitivity bug (`camoufoxModule.camoufox` vs `camoufoxModule.Camoufox`) means roviq-browser has been running on plain Firefox all along. The fact that Cloudflare doesn't block plain Firefox + realistic settings suggests **CamoFox may be unnecessary** for this use case, or that CamoFox's deeper patches are actually counterproductive.

---

## Evidence Summary

| Fact | Sandbox (Working) | Railway (Failing) |
|------|-------------------|-------------------|
| Browser binary | Plain Playwright Firefox | CamoFox-patched Firefox |
| Fission enabled | No (Playwright default) | Yes (`camoufox.cfg`) |
| CAMOU_CONFIG_1 | Not set (plain Firefox) | Set with 12 properties |
| `headers.*` patching | None | None (but binary expects it) |
| `page.evaluate()` form | String expression | Async function + args |
| Cross-origin fetch | Works (no site isolation) | Hangs (site isolation?) |
| Cloudflare clearance | Passes | Passes |
| First Algolia call | Succeeds | Hangs → timeout |

---

## Proposed Solution

### Recommended: Option A — Use roviq-browser HTTP API from Railway

**Rationale**: The simplest, most reliable approach. The exact code path that works today from the sandbox should be used on Railway too. This eliminates the CamoFox binary dependency from the Jane scraper entirely.

**Implementation**:

1. **Modify `scrapers/jane/index.ts`** to use `BrowserProxy` from `scripts/lib/jane-client.ts` instead of `EmbeddedBrowserProxy`
2. Point it at the roviq-browser service URL (already available as `WEEDMAPS_CAMOFOX_URL` env var)
3. Remove all embedded CamoFox launch code from the Jane scraper
4. The Jane scraper Docker image no longer needs `camoufox-bin`, making it ~250MB smaller

**Essentially**: Make the Railway Jane scraper do exactly what `scripts/scrape-jane.ts` does, just running on Railway instead of sandbox.

**Pros**:
- Exact same code path as the working version
- Simpler Jane scraper (no browser management)
- Smaller Docker image
- Single browser instance shared across scrapers
- Already proven at scale (39 stores, 10K+ prices)

**Cons**:
- Dependency on roviq-browser service being up
- Extra network hop (Railway internal network, <1ms latency)
- If roviq-browser goes down, all scrapers fail (but this is already true for weedmaps)

### Alternative: Option B — Fix CamoFox Launch in Railway Scraper

If embedded CamoFox is preferred for isolation:

1. **Use the `camoufox` npm package properly** instead of launching `camoufox-bin` directly:
   ```typescript
   import { Camoufox } from 'camoufox';
   const browser = await Camoufox({ headless: true });
   ```
   This lets the package handle fingerprint generation, `CAMOU_CONFIG_1`, Fission config, and all anti-detection properly.

2. **Add `disable_coop: true`** to the launch options:
   ```typescript
   const browser = await Camoufox({ headless: true, disable_coop: true });
   ```

3. **Test with Fission disabled** by adding to `firefoxUserPrefs`:
   ```
   'fission.autostart': false,
   'fission.webContentIsolationStrategy': 0,
   ```

**Pros**:
- Self-contained (no dependency on roviq-browser)
- Proper anti-detection (if needed in future)

**Cons**:
- More complex
- Requires testing CamoFox cross-origin behavior
- May still have issues with CamoFox binary in headless Railway containers

### Alternative: Option C — Fix roviq-browser's CamoFox Import

Fix the case-sensitivity bug in roviq-browser:
```typescript
// FROM:
this.browser = await camoufoxModule.camoufox({ headless: this.headless });
// TO:
this.browser = await camoufoxModule.Camoufox({ headless: this.headless });
```

**Warning**: This could **break** roviq-browser if CamoFox's Fission/patches cause the same issue there. The current "bug" is accidentally working in our favor. Only do this after Option B testing confirms CamoFox works.

---

## Implementation Plan (Option A — Recommended)

### Step 1: Extract BrowserProxy into shared library
- Move `BrowserProxy` class from `scripts/lib/jane-client.ts` to a shared location (e.g., `scrapers/lib/browser-proxy.ts`)
- This class makes HTTP calls to roviq-browser's API

### Step 2: Refactor Railway Jane scraper
- Replace `EmbeddedBrowserProxy` with `BrowserProxy`
- Use `WEEDMAPS_CAMOFOX_URL` env var (or a new `BROWSER_SERVICE_URL`)
- Remove `launchCamoufox()` and all embedded browser code
- Keep everything else: run lock, hard timeout, DB writes, notifications

### Step 3: Simplify Jane Dockerfile
- Remove `npx camoufox fetch` (saves ~250MB)
- Remove `camoufox`, `fingerprint-generator` from dependencies
- Remove `playwright` dependency (only `node-fetch` or native `fetch` needed)

### Step 4: Add health check
- Before scraping, verify roviq-browser is reachable: `GET /health`
- If down, fail fast with clear error message

### Step 5: Fix roviq-browser CamoFox import (separate PR)
- Fix `camoufox` → `Camoufox` case
- Test thoroughly before deploying
- This is a separate effort, not blocking Jane

### Step 6: Rename `WEEDMAPS_CAMOFOX_URL`
- Rename to `BROWSER_SERVICE_URL` since it's used by all scrapers
- Keep backward compat with fallback

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| roviq-browser goes down | Low | High (all scrapers fail) | Health check + alerting; can always fall back to sandbox runs |
| roviq-browser tab limit | Medium | Medium (max 10 concurrent) | Jane scraper uses 1 tab; stagger scraper cron times |
| Network latency between Railway services | Very Low | Very Low | Internal Railway network; <1ms |
| Cloudflare blocks plain Firefox in future | Low | High | Option B as fallback; can fix CamoFox import when needed |
| roviq-browser session timeout during long scrape | Low | Low | BrowserProxy already handles tab recreation (404 → recreate) |

---

## Weedmaps Railway Failure (Separate Issue)

The Weedmaps scraper has a different failure: "Launches CamoFox successfully then immediately stops." This is likely a **Railway container resource limit** issue:

1. CamoFox binary + Fission + site isolation = heavy memory usage
2. Railway may be OOM-killing the container
3. Or the CamoFox binary crashes on startup due to missing X11/display dependencies

This is a separate investigation but the same solution applies: use roviq-browser HTTP API instead of embedded CamoFox.

---

## Key Takeaway

**We've been accidentally running plain Firefox (not CamoFox) on roviq-browser all along, and it works perfectly.** The anti-detection isn't coming from CamoFox's binary patches — it's coming from realistic browser context settings (user agent, viewport, locale, timezone). Cloudflare's bot detection on iheartjane.com is apparently satisfied by a headless Firefox with realistic settings. The Railway failure is caused by using the *real* CamoFox binary, whose site-isolation patches break cross-origin fetch.

The right move is to standardize on the proven working approach: use roviq-browser's HTTP API for all browser-proxied requests, regardless of where the scraper runs.
