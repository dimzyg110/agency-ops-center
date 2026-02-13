# Leafly Direct HTTP Validation: Will It Work at Scale on Railway?

**Date**: 2026-02-13  
**Investigator**: Opus 4.6 (subagent validation)  
**Status**: Complete — **Direct HTTP is RISKY at 292 stores. Keep browser fallback.**

---

## TL;DR

The Leafly investigation's conclusion — "just use direct HTTP, no browser needed" — is **partially correct but dangerously incomplete**. The sandbox scraper already uses direct HTTP and it works today from the sandbox IP (`162.220.232.206`). But the production data tells a different story: **the sandbox itself hit 429 Cloudflare rate limits after ~200 stores in a single run**, and those rate limits hit the HTML pages, not just the API. Direct HTTP will probably work for ~75-100 stores per run before Cloudflare kicks in. At 292 stores, it will fail on the tail end unless mitigated.

**Recommendation**: Use direct HTTP as the primary path (much faster, much simpler) but with aggressive rate-limit mitigation and a browser fallback for stores that get 429'd.

---

## Evidence: What the Database Actually Shows

### Successful Runs (All From Sandbox, All Direct HTTP)

| Run ID | Stores Attempted | Succeeded | Failed | Prices | Duration | Notes |
|--------|-----------------|-----------|--------|--------|----------|-------|
| `c55fed46` | 3 | 3 | 0 | 157 | 11s | Small test, 100% success |
| `835e4fa6` | 3 | 1 | 2 | 48 | 9s | 2 stores genuinely empty |
| `f1aad11f` | 5 | 1 | 3 | 723 | 30s | 3 stores genuinely empty |

These are tiny test runs (3-5 stores). They prove the code works but say nothing about scale.

### The Big Run: `dbac0809` — 292 Stores, Sandbox, Direct HTTP

This is the critical evidence. This run was executed from the sandbox using direct HTTP (`scrape-leafly.ts` with `--db`). Here's what actually happened:

**Phase 1 (14:33–15:03 UTC, ~30 minutes): Processed ~200 stores**
- 76 stores succeeded, 124 failed with "No menu items"
- **Zero rate limits** — Cloudflare was fine
- ~3-5 stores processed per minute (includes jitter of 1.7-3.6s between stores)
- 32,989 total prices inserted across all Leafly runs

**Gap (15:03–17:00 UTC, ~2 hours): Process died/paused**
- Likely sandbox resource exhaustion (memory note says 40+ zombie tsx processes)

**Phase 2 (17:00–17:07 UTC, ~7 minutes): Resumed remaining ~125 stores**
- **0 stores succeeded**
- **19 stores hit 429** on `www.leafly.com/dispensary-info/` (HTML page)
- **105 stores failed** with "No menu items" — but these previously-empty stores now ALSO couldn't get page data
- The 429 response body: `"Just a moment..."` — classic Cloudflare challenge page

**Key insight**: The 429s hit the **HTML page fetch** (`fetchLeaflyStorePageProps`), not the API. But since the scraper tries the HTML page first (for `__NEXT_DATA__`) and then the API, a 429 on the HTML page causes the whole store to fail before the API is even attempted.

### Railway Runs (All Failures)

| Run ID | Status | Stores | Notes |
|--------|--------|--------|-------|
| `8aedc194` | running | 0 succeeded, 1 failed | Currently running (20:09 UTC) |
| `31edaa73` | failed | 0 succeeded, 1 failed | 19:52 UTC |
| `f8570283` | failed | 0 succeeded, 1 failed | 18:47 UTC |
| `73553def` | failed | 0 succeeded, 1 failed | 18:12 UTC |

These are the Railway CamoFox-based scraper attempts (not direct HTTP). They fail for entirely different reasons (CamoFox `page.request.fetch()` TLS fingerprint issue documented in LEAFLY-INVESTIGATION.md). These are NOT relevant to validating direct HTTP.

---

## The Scraper Code Analysis

### What `scrape-leafly.ts` Actually Does

The sandbox Leafly scraper uses **100% plain HTTP** via Node.js native `fetch()`. No Playwright, no browser, no CamoFox imports anywhere:

```
For each store:
  1. fetchLeaflyStorePageProps(slug) → HTTP GET www.leafly.com/dispensary-info/{slug}
     - Extracts __NEXT_DATA__ JSON from HTML
     - Gets carousel menu items as backup
  2. fetchAllLeaflyMenuItems(slug) → HTTP GET consumer-api.leafly.com/api/...
     - Paginates through all menu items (18 per page)
     - 220-380ms delay between API pages
  3. Parse + normalize + write to DB
  4. Sleep 1.7-3.6s jitter before next store
```

**Rate limiting built into the code:**
- 1.7-3.6s random jitter between stores (`jitterMs(1700, 3600)`)
- 220-380ms delay between API pagination pages
- 5 retry attempts on 429/503 with exponential backoff (1.2s, 2.4s, 3.6s, 4.8s, 6.0s)

### Why 229 Stores Had "No Menu Items"

Most of the 229 "No menu items" failures are **genuinely empty stores on Leafly**. The API returns `{"data":[], "metadata":{"totalCount":0}}` for these stores. This is NOT a scraping failure — these dispensaries simply don't have menus on Leafly (they may use Dutchie, Jane, or Weedmaps instead).

**Out of 292 discovered Leafly MA stores:**
- ~76 have actual menu data (~26%)
- ~216 are empty listings (no menu, just a storefront page)

This is consistent with the investigation's note: "Some stores fail with 'No menu items found' because they genuinely have zero items."

### The Cloudflare Rate Limit Pattern

The 429s appeared ONLY after:
1. ~200 HTML page fetches to `www.leafly.com`
2. ~200+ API calls to `consumer-api.leafly.com`
3. A 2-hour pause (process died and resumed)
4. Resuming rapid-fire requests from the same IP

Cloudflare likely flagged the IP after cumulative request volume. The 2-hour gap didn't help — Cloudflare rate limiting is often based on rolling windows, and resuming a burst after a pause can actually make it worse (the "burst after cool-down" pattern looks more bot-like).

---

## What About Railway IPs?

### The IP Difference

| Environment | IP Range | Type | Cloudflare Treatment |
|-------------|----------|------|---------------------|
| Sandbox (OpenClaw) | 162.220.232.x | Unknown datacenter | Worked for ~200 stores |
| Railway | GCP datacenter IPs | Known cloud provider | Likely more aggressive CF |

**Railway runs on GCP.** Cloudflare has specific datacenter IP lists and treats them with higher suspicion. An IP that's already flagged as a cloud provider will:
- Get challenged sooner (lower request threshold before 429)
- Be more likely to trigger JS challenges
- Have shorter rate limit recovery windows

**However**: The sandbox IP `162.220.232.206` is also a datacenter IP (not residential). The fact that it worked for 200 stores suggests Leafly's Cloudflare rules are relatively lenient on the API endpoint, and moderate on the HTML pages.

### Real-Time Test (Sandbox)

I tested both endpoints from the sandbox right now (20:29 UTC):

```
consumer-api.leafly.com (API): 10/10 rapid requests → all HTTP 200
www.leafly.com/dispensary-info/ (HTML): 10/10 rapid requests → all HTTP 200
```

The API endpoint showed zero rate limiting even with zero delay between requests. The HTML pages also survived rapid-fire. But this is only 10 requests — the production data shows the limit kicks in around 200+ cumulative requests.

---

## Weedmaps and Dutchie Comparison

### Weedmaps
- **Best run**: 10/173 stores succeeded (5.8% success rate)
- **Failure mode**: "age gate or redirect detected" — Cloudflare/WAF redirecting to challenge pages
- **Latest run** (0/143): 100% failure, same pattern
- **Does NOT use direct HTTP** — uses CamoFox browser
- **Rate limiting observed**: Not HTTP 429 specifically, but Cloudflare challenge pages served to the browser

### Dutchie
- **Best run**: 195/235 stores succeeded (83%) — took 5.2 hours
- **Latest run**: 27/235 (11.5%) — "fetch failed" errors (152 out of 208 failures), likely CamoFox browser crashes
- **Also uses browser-based scraping**
- **Rate limiting observed**: Not 429, but browser connection failures after sustained load

### Key Difference
Weedmaps and Dutchie **require browsers** because their menu data is rendered client-side (React SPA, Cloudflare-protected). Direct HTTP would get nothing but a shell HTML page. This is fundamentally different from Leafly, where the API responds to plain HTTP.

**There is no evidence that direct HTTP was tested against Weedmaps or Dutchie and rate-limited.** The rate limiting these platforms show is browser-level (Cloudflare challenges, WAF redirects, connection drops). These are different anti-bot mechanisms than what Leafly uses.

---

## Risk Assessment

### Will Direct HTTP Work at 292 Stores on Railway?

| Scenario | Likelihood | Outcome |
|----------|-----------|---------|
| API works for all 292 stores | **Low** (~15%) | Best case — but history shows 429 after ~200 |
| API works for ~100-200 stores, 429 on remainder | **High** (~55%) | Same as sandbox experience |
| API gets 429 immediately from Railway IP | **Medium** (~25%) | GCP datacenter IP flagged by CF |
| API works but HTML pages get 429 | **Medium** (~40%) | API succeeds but pageProps extraction fails |
| Full Cloudflare JS challenge (not just 429) | **Low** (~10%) | Would need full browser |

**The most likely outcome**: Direct HTTP works for the first 100-200 stores (covering most stores that actually have menu data), then gets rate-limited on the tail end. Since only ~76 stores actually have menus, this might be acceptable.

### The "76 Out of 292 Actually Have Data" Factor

This changes the math significantly:
- Only ~76 stores have actual menu data
- The scraper processes ALL 292, but 216 are quick failures (empty API response, <1s each)
- The stores with data require multiple paginated API calls (potentially 5-20 calls per store)
- Total API calls: ~292 HTML page fetches + ~76 × ~10 API pages = ~1,052 requests

At 1.7-3.6s jitter between stores + 220-380ms between API pages, the full run takes ~15-20 minutes. That's a lot of requests from one IP in a short window.

---

## Recommendations

### Primary: Direct HTTP with Rate-Limit Hardening

1. **Use direct HTTP** — it's dramatically simpler and faster than any browser approach
2. **Skip the HTML page fetch for most stores** — the `fetchLeaflyStorePageProps()` call is only needed for the carousel fallback. Try the API first. If the API returns data, skip the HTML page entirely. This halves the request count.
3. **Increase jitter between stores** — bump from 1.7-3.6s to 3-6s. The extra time costs ~10 minutes but dramatically reduces 429 risk.
4. **Add exponential backoff on HTML page 429** — when the first 429 hits, double the delay. After 3 consecutive 429s, pause for 60s.
5. **Batch in waves** — scrape 50 stores, pause 2-3 minutes, scrape 50 more. This avoids the cumulative volume trigger.

### Fallback: Browser Proxy for 429 Recovery

6. **If a store gets 429'd, queue it for browser-based retry** — don't try the browser for every store, only for the ones that fail with 429. This keeps the fast path (direct HTTP) for 90% of stores while handling the edge case.
7. **The browser fallback should use roviq-browser** (plain Firefox, not CamoFox) — per the Jane investigation, plain Firefox works and CamoFox causes more problems than it solves.

### Architecture for Railway

```
Direct HTTP path (primary, ~90% of stores):
  fetchAllLeaflyMenuItems(slug) → consumer-api.leafly.com (direct fetch)
  If 200 → parse → DB
  If 429/503 → add to retry queue

Browser fallback path (retry queue only, ~10% of stores):  
  roviq-browser HTTP API → navigate to consumer-api.leafly.com → page.evaluate(fetch)
  Or: roviq-browser → navigate to store page → extract __NEXT_DATA__
```

### What NOT To Do

- **Don't remove the browser entirely** — the investigation's "Option A: Remove Browser" is too aggressive. History shows 429s will happen at scale. Need a fallback.
- **Don't assume Railway IPs will behave like sandbox IPs** — they might get 429'd sooner.
- **Don't use `page.request.fetch()`** — this is confirmed broken (Playwright TLS fingerprint).
- **Don't use CamoFox** — per both Jane and Leafly investigations, CamoFox causes more problems than it solves. Plain Firefox via roviq-browser is the proven path.

---

## Conclusion

**Is "direct HTTP for Leafly" safe at 292 stores on Railway IPs?**  
No, not without mitigation. It will likely work for the first 100-200 stores but hit Cloudflare 429 rate limits on the remainder. However, since only ~76 stores have actual menu data, it might scrape all meaningful data before the rate limit kicks in.

**Should Leafly keep a browser as fallback?**  
Yes. Not as the primary path (too slow, too complex), but as a retry mechanism for stores that get 429'd. Use roviq-browser (plain Firefox), not embedded CamoFox.

**What's the safest approach that actually works at scale?**  
Direct HTTP first (API-only, skip HTML pages where possible), with increased jitter, wave batching, and a browser fallback queue for 429'd stores. This gives the speed benefits of direct HTTP (15-20 min vs 40-80 min) while handling the rate limit edge case that WILL occur at 292 stores.

---

## Data Sources Used

1. Database: `scrape_runs` and `scrape_jobs` tables — 8 Leafly runs analyzed
2. Code: `scripts/scrape-leafly.ts` and `scripts/lib/leafly-client.ts` — confirmed pure HTTP, no browser
3. Live testing: 10 rapid-fire requests to both API and HTML endpoints from sandbox — all 200
4. Memory logs: Feb 12-13 daily logs, MEMORY.md long-term memory
5. Investigation docs: LEAFLY-INVESTIGATION.md, JANE-INVESTIGATION.md, WEEDMAPS-INVESTIGATION.md
6. Cross-platform comparison: Weedmaps (0-5.8% success), Dutchie (11.5-83% success), Jane data
