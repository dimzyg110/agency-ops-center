# Leafly Scraper Investigation: Why Railway Fails

**Date**: 2026-02-13  
**Investigator**: Engineering subagent (Opus 4.6)  
**Status**: Complete — Root causes identified, solution proposed

---

## Executive Summary

The Leafly Railway scraper fails because of **three compounding problems**:

1. **`page.request.fetch()` uses Playwright's HTTP stack, not the browser's** — Cloudflare fingerprints it as non-browser and returns 429/CF challenge pages. The browser API calls fail silently with retry exhaustion.
2. **CamoFox Fission (site isolation) may interfere** with cross-origin cookie sharing when navigating leafly.com pages and making API calls to consumer-api.leafly.com.
3. **The direct API fallback is unnecessary** — `consumer-api.leafly.com` is NOT actually Cloudflare-blocked for simple HTTP requests. The sandbox script proves this: it calls the API directly via `fetch()` with no browser at all and succeeds.

The biggest finding: **Leafly doesn't need a browser at all.** The `consumer-api.leafly.com` API responds to simple HTTP requests with a User-Agent header. The entire browser-based architecture was built on the incorrect assumption that Cloudflare was blocking it.

---

## Architecture Comparison

### Sandbox Script (WORKS — No Browser)

```
scripts/scrape-leafly.ts
  └─ leafly-client.ts
       ├─ fetchLeaflyStorePageProps(slug)  →  HTTP GET leafly.com/dispensary-info/{slug}
       │     └─ Extract __NEXT_DATA__ from HTML
       ├─ fetchAllLeaflyMenuItems(slug)    →  HTTP GET consumer-api.leafly.com/api/...
       │     └─ Direct HTTP with User-Agent header — NO BROWSER
       └─ extractLeaflyMenuItems(pageProps) → parse carousel items from __NEXT_DATA__
```

**Key fact**: The sandbox uses plain `fetch()` (Node.js native) to call `consumer-api.leafly.com` directly. No Playwright, no CamoFox, no browser at all. It works.

### Railway Service (FAILS — Unnecessary Browser)

```
scrapers/leafly/index.ts
  └─ LeaflyBrowserScraper
       ├─ launchCamoufox()   → Real CamoFox binary with Fission enabled
       ├─ page.goto(storeUrl) → Navigate to dispensary page
       ├─ page.evaluate()     → Extract __NEXT_DATA__ (works)
       ├─ page.request.fetch() → Call consumer-api.leafly.com (FAILS)
       │     └─ Playwright HTTP stack, NOT browser engine
       │     └─ Cloudflare fingerprints Playwright's TLS/HTTP as non-browser → 429
       └─ fetchAllLeaflyMenuItemsDirect() → Direct HTTP fallback (would work but...)
             └─ Runs from Railway IP, gets CF-challenged due to datacenter IP
```

---

## Detailed Root Cause Analysis

### Root Cause 1: `page.request.fetch()` is NOT the Browser

The Leafly Railway scraper's `fetchMenuItemsViaBrowser()` method (line 305-370) uses:

```typescript
response = await page.request.fetch(apiUrl, {
  headers: { 'Accept': 'application/json' },
});
```

The comment on lines 305-308 says:
> Fetch all menu items for a store via the Leafly API, using Playwright's `page.request.fetch()` which shares the browser context's cookie jar. This properly carries Cloudflare clearance cookies cross-subdomain, unlike `page.evaluate(fetch(...))` which may not.

**This is half-right and half-wrong:**
- ✅ `page.request.fetch()` does carry the cookie jar
- ❌ But `page.request.fetch()` uses **Playwright's own HTTP stack**, not the browser engine
- Cloudflare doesn't just check cookies — it fingerprints the TLS stack, HTTP/2 settings, header ordering, etc.
- Playwright's HTTP client has a distinct fingerprint that Cloudflare recognizes as non-browser

This is **exactly the same issue the Jane scraper hit** (commit `cbc3eb5`):
> "page.request.fetch() uses Playwright's HTTP stack which Cloudflare fingerprints as non-browser (403 on every request)"

The Jane scraper was switched to `page.evaluate(fetch())` to fix this. But the Leafly scraper still uses `page.request.fetch()`.

### Root Cause 2: The Problem Was Already Known — But Applied Inconsistently

The git history shows a pendulum of approaches:

| Commit | Jane Approach | Result |
|--------|---------------|--------|
| Original | `page.evaluate(fetch())` | Hangs (CamoFox Fission cross-origin) |
| `7c7b56f` | `page.request.fetch()` | 403 (Playwright TLS fingerprint) |
| `cbc3eb5` | `page.evaluate(fetch())` + same-origin nav | Current approach |

The Leafly scraper was NOT updated to match. It's stuck on `page.request.fetch()` — the approach that was explicitly rejected for Jane.

### Root Cause 3: CamoFox Fission Complicates Cross-Origin

Even if Leafly switched to `page.evaluate(fetch())`, CamoFox's Fission would cause issues:

- Page is on `https://www.leafly.com/dispensary-info/{slug}`
- API is on `https://consumer-api.leafly.com/api/...`
- These are **different origins** (different subdomain)
- Fission puts them in **different OS processes**
- `page.evaluate(fetch('https://consumer-api.leafly.com/...'))` would cross a process boundary
- This is the exact pattern that broke Jane initially

**But here's the key difference from Jane**: With Jane, the only way to query the Algolia API is through the browser (CF-protected proxy). With Leafly, the API responds to plain HTTP requests.

### Root Cause 4: The "Cloudflare Blocking" Assumption Is Wrong

The file header says:
> IMPORTANT: Leafly MUST use CamoFox browser from day 1. Cloudflare is already blocking the HTTP API (consumer-api.leafly.com).

**This is incorrect.** Verified today:

```bash
$ curl -s -o /dev/null -w "%{http_code}" \
  "https://consumer-api.leafly.com/api/dispensaries/v1/253-farmacy-amherst/menu_items?skip=0&take=5" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0"
200
```

The API returns 200 with full JSON data. No Cloudflare challenge. The sandbox `scrape-leafly.ts` script uses this direct HTTP approach and successfully scrapes hundreds of products.

**Why it might fail from Railway**: Railway's datacenter IPs may trigger Cloudflare's datacenter detection, returning challenges. This would explain why the direct API fallback in the Railway scraper also fails. But this doesn't mean a browser is needed — a proxy or residential IP would also work.

### The Slow Progression Problem

The Railway logs show "progresses very slowly through stores." This is because:
1. Each store opens a new page tab
2. Navigates to the store page (Cloudflare challenge wait: 2-3s)
3. Waits for `__NEXT_DATA__` (up to 12s timeout)
4. Tries `page.request.fetch()` with 3 retry attempts (each with increasing backoff: 1.2s, 2.4s, 3.6s)
5. All 3 attempts fail (Playwright TLS fingerprint)
6. Falls back to direct API (also fails from Railway datacenter IP)
7. Falls back to carousel items from `__NEXT_DATA__`
8. Carousel is sparse (incomplete subset of menu) → fails quality check
9. Total per-store time: 30-60+ seconds, most of it wasted on failing API calls
10. Jitter between stores: 1.7-3.6s additional

With 80+ stores, this could take 40-80 minutes.

---

## Evidence Summary

| Fact | Sandbox Script | Railway Service |
|------|---------------|-----------------|
| Browser used | None (plain HTTP) | CamoFox binary (Fission ON) |
| Menu API method | Direct HTTP `fetch()` | `page.request.fetch()` (Playwright stack) |
| API URL | `consumer-api.leafly.com` | `consumer-api.leafly.com` |
| CF protection | Not blocked (sandbox IP) | Playwright fingerprint → 429 |
| `__NEXT_DATA__` | Extracted via HTTP GET + regex | Extracted via `page.evaluate()` |
| Carousel fallback | Available (but intentionally rejected) | Available (but sparse/incomplete) |
| Stores succeeded | 3/3 in multiple runs | Store 1 fails, very slow |
| Products per run | 157-723 | ~0 |

---

## Proposed Solution

### Recommended: Option A — Remove Browser, Use Direct HTTP Like Sandbox

**Rationale**: The sandbox `scrape-leafly.ts` already has a working, proven approach that doesn't need a browser at all. The Railway service should use the same approach.

**Implementation**:

1. **Replace `LeaflyBrowserScraper` with the sandbox's `leafly-client.ts` functions** — `fetchAllLeaflyMenuItems()`, `fetchLeaflyStorePageProps()`, `extractLeaflyMenuItems()`
2. **Remove all CamoFox/Playwright code** from the Leafly Railway scraper
3. **Remove browser dependencies** from Dockerfile (saves ~250MB+ image size)
4. **Keep the `__NEXT_DATA__` carousel as a fallback** but prefer the API

**Risk: Railway datacenter IP gets CF-challenged.**

**Mitigation**: Test the direct API from Railway first. If it fails:
- Use roviq-browser HTTP API as a proxy (like Jane does from sandbox)
- Or add a `page.evaluate(fetch())` approach with same-origin navigation (navigate to `consumer-api.leafly.com` first, then fetch from there — but this requires browser)

**Pros**:
- Dramatically simpler (no browser dependency)
- 10x faster (no page navigation, no CF challenge waits, no Playwright overhead)
- Smaller Docker image (~250MB less)
- Exact same code path that works in sandbox
- No CamoFox Fission issues
- No Playwright TLS fingerprinting issues

**Cons**:
- May get CF-challenged from Railway datacenter IPs (test required)
- If CF starts protecting the API, would need to fall back to browser approach

### Fallback: Option B — Fix Railway Browser Approach

If direct HTTP fails from Railway IPs:

1. **Switch from `page.request.fetch()` to `page.evaluate(fetch())`** — match what Jane does
2. **Navigate to `consumer-api.leafly.com` first** to get same-origin CF clearance
3. **Disable Fission** in `launchCamoufox()` firefoxUserPrefs:
   ```typescript
   'fission.autostart': false,
   'fission.webContentIsolationStrategy': 0,
   ```
4. **Or use roviq-browser** — the same approach recommended in the Jane investigation

### Alternative: Option C — Use roviq-browser HTTP API (Like Jane Sandbox)

Same as Jane investigation's recommendation:

1. Use `BrowserProxy` class from `scripts/lib/jane-client.ts` to proxy API calls through roviq-browser
2. roviq-browser uses plain Firefox (not CamoFox — case bug), which works
3. Navigate browser tab to `consumer-api.leafly.com` for CF clearance
4. Execute `page.evaluate(fetch())` via the HTTP API

---

## Implementation Plan (Option A — Recommended)

### Step 1: Test Direct API from Railway
Before any code changes, verify `consumer-api.leafly.com` responds from Railway:
- SSH to Railway container or add a startup test
- `curl -s -o /dev/null -w "%{http_code}" "https://consumer-api.leafly.com/api/dispensaries/v1/253-farmacy-amherst/menu_items?skip=0&take=2" -H "Accept: application/json" -H "User-Agent: Mozilla/5.0..."`
- If 200 → proceed with Option A
- If 429/503 → fall back to Option B or C

### Step 2: Refactor Railway Leafly Scraper
If API works from Railway:
1. Import `fetchAllLeaflyMenuItems`, `fetchLeaflyStorePageProps`, `extractLeaflyMenuItems` from shared lib
2. Replace `LeaflyBrowserScraper` class with direct HTTP calls
3. Keep store discovery via HTTP (already works)
4. Keep all DB logic, run-lock, timeout, notification code unchanged

### Step 3: Simplify Dockerfile
```dockerfile
# FROM mcr.microsoft.com/playwright:v1.50.1-jammy  ← REMOVE
FROM node:22-slim  ← USE THIS

# Remove: camoufox, playwright, fingerprint-generator
# Keep: pg, tsx
```

### Step 4: Increase Throughput
Without browser overhead:
- Each store takes ~1-3s (API call + parsing) instead of 30-60s
- Full scrape of 80+ stores: 5-10 minutes instead of 40-80 minutes
- Can reduce jitter since we're not loading browser pages

### Step 5: Add CF Detection
```typescript
// In fetchAllLeaflyMenuItems, detect CF challenge pages
const response = await fetch(url, { ... });
if (response.status === 403 || response.status === 429) {
  const body = await response.text();
  if (body.includes('Cloudflare') || body.includes('cf-')) {
    throw new Error('Cloudflare challenge detected — need browser proxy');
  }
}
```

---

## Connection to Jane Investigation

The Jane investigation found:
1. **roviq-browser's CamoFox import is broken** (case bug) → uses plain Firefox
2. **Plain Firefox works** — anti-detection comes from realistic context settings, not CamoFox binary
3. **CamoFox Fission breaks cross-origin fetch** via `page.evaluate()`

For Leafly, these findings are relevant but the solution is different:
- Jane **must** use a browser (Algolia proxy is CF-protected, no direct API access)
- Leafly **doesn't need** a browser (`consumer-api.leafly.com` responds to plain HTTP)
- The Railway Leafly scraper should be simplified to not use a browser at all

**If** Railway IPs get CF-challenged on the Leafly API, then the Jane findings apply:
- Use roviq-browser (which is plain Firefox, not CamoFox)
- Or disable Fission and use `page.evaluate(fetch())` with same-origin navigation

---

## Stores With Zero Menu Items

Some stores fail with "No menu items found" because they **genuinely have zero items**:
- `1-connection`: API returns `{"data":[], "metadata":{"totalCount":0}}`
- `affinity---boston`: Same
- `alternative-therapies-group`: Same

These are valid empty stores, not scraping failures. The scraper should handle them gracefully (skip or mark as "empty" instead of "failed").

---

## Key Takeaway

**The Leafly Railway scraper is over-engineered.** It uses CamoFox + Playwright + `page.request.fetch()` to call an API that responds to plain HTTP requests. The browser adds complexity, failure modes, and slowness without providing any benefit.

The fix is: **delete the browser code and use direct HTTP**, matching the sandbox script that already works. If Railway IPs get blocked in the future, add a browser proxy as a fallback — but start simple.

The reason `page.request.fetch()` fails is well-documented: Playwright's HTTP stack has a different TLS fingerprint than a real browser, and Cloudflare detects it. This was already discovered and fixed for the Jane scraper (commit `cbc3eb5`) but the fix was never applied to Leafly.
