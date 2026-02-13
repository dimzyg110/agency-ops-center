# DUTCHIE FORENSICS — Database-Verified Investigation

**Date:** 2026-02-13  
**Method:** Direct database queries + git log correlation. No memory files or investigation docs consulted.

---

## TL;DR

1. **Every successful Dutchie scrape was run from the SANDBOX** (`scripts/scrape-dutchie.ts`) on the OpenClaw server, using the **CamoFox HTTP API** (`localhost:9377` — the OpenClaw CamoFox plugin).
2. **The Railway Dutchie service has NEVER run.** There are zero Railway-tagged Dutchie runs in the database. It was only created on Feb 13 and the Dockerfile/code exists, but it was never deployed or triggered.
3. **The Railway service for ALL platforms has 0 successful prices.** Every `{"source": "railway"}` tagged run shows 0 prices inserted. Jane, Leafly, and Weedmaps Railway services all failed.
4. **Weedmaps also succeeded only from the sandbox** — all 86,568 Weedmaps prices have `run_id = NULL`, meaning they came from the sandbox script (which doesn't set `run_id` on prices).

---

## Timeline of ALL Dutchie Runs (from `scrape_runs` table)

| # | Run ID (short) | Date/Time (UTC) | Status | Stores Attempted | Stores OK | Prices Inserted | Source | Notes |
|---|---------------|-----------------|--------|-----------------|-----------|-----------------|--------|-------|
| 1 | `dd9a656d` | Feb 12 03:35 | completed | 0 | 0 | 0 | Sandbox | Early dev run, ran ~31 min, 0 results |
| 2 | `786bc008` | Feb 12 03:36 | completed | 0 | 0 | 0 | Sandbox | Overlapping dev run |
| 3 | `bf340f69` | Feb 12 03:37 | completed | 0 | 0 | 0 | Sandbox | Overlapping dev run |
| 4 | `61e2447d` | Feb 12 03:38 | completed | 0 | 0 | 0 | Sandbox | Overlapping dev run |
| 5 | `709534be` | Feb 12 03:40 | completed | 2 | 0 | 0 | Sandbox | First real attempt, 2 stores failed (7s) |
| 6 | `feba6e8f` | Feb 12 03:44 | completed | 2 | 0 | 0 | Sandbox | 2 stores failed (27s) |
| **7** | **`2b8b9015`** | **Feb 12 03:47** | **completed** | **2** | **2** | **293** | **Sandbox** | **🟢 FIRST SUCCESS — 293 prices from 2 stores** |
| **8** | **`dd81f57a`** | **Feb 12 04:07** | **completed** | **235** | **195** | **57,514** | **Sandbox** | **🟢 BIG SUCCESS — 195/235 stores, 57K+ prices, ~5.2 hours** |
| 9 | `fd980a98` | Feb 13 08:01 | completed | 0 | 0 | 0 | Sandbox | Ran 3.6 hours, 0 stores attempted (broken) |
| 10 | `3f6ca75a` | Feb 13 11:39 | completed | 0 | 0 | 0 | Sandbox | Another 0-store run (~32 min) |
| **11** | **`98b9ac88`** | **Feb 13 12:12** | **completed** | **1** | **1** | **47** | **Sandbox** | **🟢 Single store test** |
| **12** | **`0ffff7a9`** | **Feb 13 12:26** | **completed** | **1** | **1** | **395** | **Sandbox** | **🟢 Single store test** |
| **13** | **`2d4aa3f1`** | **Feb 13 13:28** | **completed** | **235** | **27** | **5,800** | **Sandbox** | **🟡 DEGRADED — only 27/235 stores (11.5%), then CamoFox crashed** |

### Key Observations

- **All 13 runs have empty metadata `{}`** — none say `"railway"`. The Railway service injects `{"source": "railway"}` in `run-lock.ts`, confirming these are all sandbox runs.
- **All 66,108 Dutchie prices have `run_id = NULL`** — the sandbox `scripts/scrape-dutchie.ts` doesn't pass `run_id` when inserting prices (or wasn't at that version), while the Railway service does.
- **No Dutchie Railway run exists at all** — the service was added in commit `8a64ce4` (Feb 13 17:37) but was never deployed.

---

## What Code Was Running During the Successful Runs?

### Run #7 (293 prices) — Feb 12 03:47 UTC

**Commit:** `1d1a076` — `feat(glass): scraper V2 working - CamoFox HTTP API, 293 products from 2 stores into prod DB`

**Code path:** `scripts/scrape-dutchie.ts` → `scripts/lib/browser-pool.ts`

**Browser approach:** **CamoFox HTTP API** — the `BrowserPool` class wraps `http://localhost:9377` (the OpenClaw CamoFox plugin). It calls:
- `POST /tabs` to create tabs
- `GET /tabs/:id/snapshot` for accessibility snapshots  
- `POST /tabs/:id/click` for element clicks
- `POST /tabs/:id/scroll` for scrolling
- `DELETE /tabs/:id` to close tabs

**This is NOT launching its own browser.** It's piggybacking on the OpenClaw CamoFox browser that's already running as a plugin on this server.

### Run #8 (57,514 prices) — Feb 12 04:07–10:54 UTC

**Same commit/code path as Run #7.** The script was run immediately after the 2-store test proved successful, with `--skip-discovery --db` to scrape all 235 known slugs.

**Success rate: 195/235 = 83%** — the 40 failures were individual store issues (page loads, empty menus), not systemic.

### Run #13 (5,800 prices) — Feb 13 13:28 UTC (DEGRADED)

**Commit:** Around `84e8a17` — `fix(dutchie): recover prices without button labels and avoid false empty failures`

**Same code path** (sandbox + CamoFox HTTP API), but degraded because:
- Only 27/235 stores succeeded (11.5%)
- Errors show TWO distinct failure modes:
  1. **`TypeError: fetch failed`** — the CamoFox HTTP API at localhost:9377 became unreachable (148 stores)
  2. **`CamoFox API 500: browser.newContext: Target page, context or browser has been closed`** — the CamoFox browser crashed mid-run (53 stores)

**Diagnosis:** The CamoFox plugin browser died partway through the run. The first ~27 stores worked, then the browser crashed, and all subsequent stores failed with either fetch errors or 500s.

---

## What Changed Between Working and Broken?

### The Sandbox Script (What Actually Works)

`scripts/scrape-dutchie.ts` + `scripts/lib/browser-pool.ts`:
- Uses **CamoFox HTTP API** at `localhost:9377`
- Talks to the **OpenClaw CamoFox plugin** (an already-running browser)
- Uses accessibility snapshots + regex parsing
- Navigates to `https://dutchie.com/embedded-menu/{slug}`
- Paginates through `?page=N` URLs
- Extracts product links via snapshot parsing
- **This code still exists and still works** — it just needs the CamoFox plugin to be running

### The Railway Service (What Was Built But Never Ran)

`scrapers/dutchie/index.ts` + `scrapers/lib/browser.ts`:
- Tries to **launch its own CamoFox binary** via Playwright
- Uses `npx camoufox fetch` in Dockerfile to download the binary
- Different browser approach: direct Playwright `page.evaluate()` for DOM extraction
- Different extraction logic: `document.querySelectorAll('a[href*="/product/"]')` instead of snapshot parsing
- **Was never deployed to Railway** — only committed on Feb 13

### The Critical Difference

| Aspect | Sandbox (worked) | Railway Service (never ran) |
|--------|------------------|-----------------------------|
| Browser | OpenClaw CamoFox plugin (HTTP API) | Self-launched CamoFox binary |
| Extraction | Accessibility snapshot + regex | `page.evaluate()` DOM queries |
| Runs on | This OpenClaw server | Railway container |
| CamoFox availability | Always running (plugin) | Must download + launch binary |
| Anti-detection | Full CamoFox (plugin-managed) | Binary launch with env config |

---

## Weedmaps Cross-Reference

| Run | Date | Stores OK | Prices | Source | Errors |
|-----|------|-----------|--------|--------|--------|
| `8de95280` | Feb 12 05:13 | 1/1 | 760 | Sandbox | Test run |
| `3894a123` | Feb 12 06:24 | 10/173 | 6,162 | Sandbox | 163 stores: "0 products parsed" |
| `8fc2016a` | Feb 13 03:01 | 0/143 | 0 | Sandbox | All 143: "0 products parsed" |
| `3aca3776` | Feb 13 15:17 | 0/0 | 0 | Sandbox | Empty run |
| `c5a93c83` | Feb 13 15:17 | 0/0 | 0 | Railway | Failed |
| `6b35a0c0` | Feb 13 19:53 | 0/0 | 0 | Railway | Failed `{"source": "railway"}` |

**Weedmaps had the same pattern:** Sandbox worked on Feb 12 (partially — 10/173 stores), then completely stopped working on Feb 13. The Railway service never succeeded.

All 86,568 Weedmaps prices also have `run_id = NULL` → confirmed sandbox origin.

---

## Railway Service Runs — Complete Failure Log

**Every single Railway-tagged run has 0 prices inserted:**

| Platform | Runs | All Failed? | Error Pattern |
|----------|------|-------------|---------------|
| Jane | 9 runs | Yes | CamoFox binary not found / Cloudflare blocks |
| Leafly | 3 runs | Yes | CamoFox binary not found |  
| Weedmaps | 2 runs | Yes | CamoFox binary not found / 0 stores |
| Dutchie | 0 runs | N/A | **Never deployed** |

The Railway services fail because:
1. The CamoFox binary download (`npx camoufox fetch`) in Docker may not be working correctly
2. Even if the binary exists, launching it in a Railway container without a display/Xvfb may fail
3. The services were all created and deployed on Feb 13 between 17:00-20:00 UTC and none worked

---

## What Broke and When

### Feb 12 (Day 1) — Everything Worked
- **03:47–10:54 UTC**: Dutchie sandbox scraper ran against CamoFox HTTP API → 57,514 prices from 195 stores
- **05:13–16:02 UTC**: Weedmaps sandbox scraper ran against CamoFox HTTP API → 6,922 prices from 11 stores
- Code was at commits `1d1a076` through `147a13c`

### Feb 13 (Day 2) — Degradation Then Total Failure
- **08:01–11:39 UTC**: Dutchie run #9 ran for 3.6 hours but attempted 0 stores (code bug or CamoFox plugin down)
- **12:12–12:17 UTC**: Small test succeeded (47 prices) — CamoFox HTTP API still available
- **13:28–14:47 UTC**: Full run degraded — 27/235 stores, then CamoFox crashed mid-run
- **17:37 UTC**: Railway services created (commit `8a64ce4`)
- **17:45–20:09 UTC**: Railway services deployed, all fail immediately
- **20:28 UTC**: Panic commit `d6d7e78` — switches Railway scrapers to plain Firefox (no CamoFox), which would lose anti-detection

### Root Cause Chain
1. **Feb 13 morning**: CamoFox plugin on the OpenClaw server became unstable (possibly memory/resource pressure from the 5+ hour run the night before)
2. **Feb 13 afternoon**: Agents started building Railway services to move scrapers off the sandbox — but the Railway services couldn't replicate the CamoFox HTTP API approach because Railway doesn't have the OpenClaw CamoFox plugin
3. **Feb 13 evening**: Multiple "fix" commits tried to get CamoFox working in Railway containers (ESM issues, binary paths, fingerprint-generator, plain Firefox fallback) — none worked
4. **The going-in-circles**: Each new "fix" was trying to solve Railway deployment issues, but the actual working code was the sandbox script that talks to the local CamoFox HTTP API

---

## Exact Recommendation to Get Dutchie Working Again

### Option A: Run Sandbox Script on OpenClaw Server (Proven, Fast)

This is what actually worked. Do it again.

```bash
cd /data/workspace/projects/glass/src
# Make sure CamoFox plugin is running (verify via OpenClaw)
curl -s http://localhost:9377/health

# Run the sandbox Dutchie scraper
npx tsx scripts/scrape-dutchie.ts --skip-discovery --db
```

**Requirements:**
- OpenClaw CamoFox plugin must be running and healthy at `localhost:9377`
- The server this command runs on must have network access to the Railway Postgres database
- `DATABASE_URL` env var must be set (or hardcoded in `scripts/lib/config.ts`)

**Why this works:** The CamoFox HTTP API provides a real anti-detection browser that's already running. No binary download, no ESM issues, no container display problems.

### Option B: Fix Railway Services (Correct Long-Term, Harder)

The Railway `scrapers/dutchie/index.ts` has the right structure but needs:

1. **Fix CamoFox binary in Docker** — verify `npx camoufox fetch` actually produces a working binary in the Railway build environment. Add explicit verification: `RUN ls -la /root/.cache/camoufox/ && /root/.cache/camoufox/camoufox-bin --version`

2. **Add Xvfb** — headless Firefox still needs a virtual framebuffer on Linux:
   ```dockerfile
   RUN apt-get install -y xvfb
   CMD ["xvfb-run", "--auto-servernum", "tsx", "dutchie/index.ts"]
   ```

3. **Test locally first** — before deploying to Railway, test the Docker container locally:
   ```bash
   docker build -t glass-dutchie -f scrapers/dutchie/Dockerfile .
   docker run --env DATABASE_URL=... glass-dutchie
   ```

4. **Don't use plain Firefox** — the `fix/weedmaps-dutchie-plain-firefox` branch (commit `d6d7e78`) switches to plain Firefox which will get IP-blacklisted. Don't merge this.

### Option C: Hybrid — Run Sandbox via Railway Cron Trigger (Compromise)

If the OpenClaw server is always running:
1. Have Railway trigger a webhook to the OpenClaw server
2. OpenClaw server runs the sandbox script locally
3. Gets the benefit of the CamoFox HTTP API without needing CamoFox in Railway

---

## Data Summary

| Metric | Value |
|--------|-------|
| Total Dutchie prices in DB | 66,108 |
| All from sandbox? | Yes (all have `run_id = NULL`) |
| Railway Dutchie service runs | 0 |
| Railway service total successes (all platforms) | 0 |
| Best Dutchie run | Feb 12: 195/235 stores, 57,514 prices |
| Best Dutchie success rate | 83% (195/235) |
| Code that worked | `scripts/scrape-dutchie.ts` + CamoFox HTTP API |
| Code that never ran | `scrapers/dutchie/index.ts` (Railway service) |

---

*This report was generated from direct database queries and git log analysis. No memory files, MEMORY.md, or previous investigation docs were consulted.*
