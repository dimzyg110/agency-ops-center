# Review Feedback — PR #26: fix/camoufox-binary-path

**Reviewer:** QA Agent (Claude Opus 4.6)  
**Date:** 2026-02-13  
**Branch:** `fix/camoufox-binary-path` → `main` (ALREADY MERGED)  
**Files Changed:** `scrapers/lib/browser.ts`, `scrapers/lib/run-lock.ts`

> ⚠️ **NOTE:** This PR was merged to main before review. Findings below are post-merge.

---

## Scores

| Dimension       | Score | Notes |
| --------------- | ----- | ----- |
| Correctness     | 3/5   | Binary path logic is correct for the happy path. Several edge cases and one dead code path. The CAMOU_CONFIG_1 env var mechanism is validated as real and correctly implemented. |
| Completeness    | 3/5   | Addresses the binary path issue. Missing chmod in Dockerfile, has dead import, Chromium flag in Firefox args. Run-lock intentionally weakened for dev. |
| Quality         | 3/5   | Clean code, good comments explaining "why". Some dead code. The fallback pattern in `npx camoufox fetch || echo "WARN"` is dangerous — fails silently. |
| Brief Adherence | 3/5   | Fixes the stated problem. Doesn't address all reliability concerns for production deployment. |

---

## Verdict

**APPROVE WITH CHANGES** — The core binary path fix is correct and will work on Railway. However, there are 1 major and several minor issues that should be addressed before this is considered production-ready.

---

## Full Execution Trace: `tsx jane/index.ts` on Railway

### 1. Dockerfile Build Phase ✅ (with caveats)

```dockerfile
FROM mcr.microsoft.com/playwright:v1.50.1-jammy
```

- **Base image:** Ubuntu 22.04 (Jammy) with Playwright 1.50.1's system deps (GTK, libdbus, libX11, fonts, etc.). These are the same deps CamoFox needs since it's a patched Firefox. ✅
- **Node.js 22 install:** Overwrites the image's Node 18 with Node 22 + tsx@4. ✅
- **`npm ci`:** Installs `camoufox@0.1.19`, `pg@8.18.0`, `playwright@1.50.1`. The `camoufox` package brings `fingerprint-generator@2.1.69` as a transitive dep (hoisted to root `node_modules`). ✅
- **`npx camoufox fetch`:** Downloads CamoFox binary to `~/.cache/camoufox/` (= `/root/.cache/camoufox/` in Docker). The `camoufox` install script runs `chmod -R 755` after extraction. ✅
- **`|| echo "WARN: camoufox fetch failed"`:** ⚠️ If fetch fails (network issue, rate limit), the build SUCCEEDS but the binary is missing. Runtime will crash with an opaque "camoufox-bin not found" error.

**Docker layout after build:**
```
/app/
  package.json, node_modules/
  lib/browser.ts, db.ts, run-lock.ts, timeout.ts, notify.ts
  jane/index.ts, Dockerfile, railway.toml
  scripts-lib/jane-parser.ts, normalizer.ts, types.ts, brand-filter.ts, config.ts
  data/jane-slugs.json
/root/.cache/camoufox/camoufox-bin   ← CamoFox binary
```

### 2. `findCamoufoxBinary()` Resolution ✅

Inside Docker, `HOME=/root`. The candidates list:
1. `/root/.cache/camoufox/camoufox-bin` ← **match** (from `homeDir + .cache/camoufox/camoufox-bin`)
2. `/root/.cache/camoufox/camoufox-bin` ← duplicate (XDG_CACHE_HOME unset, same as #1)
3. `/root/.cache/camoufox/camoufox-bin` ← duplicate (hardcoded /root)
4. `/app/camoufox-bin` ← fallback (won't match)

**Verdict:** Will find the binary on first try. Candidate #1, #2, #3 are all the same path — redundant but harmless.

### 3. Import Chain Resolution ✅

```
jane/index.ts
  → ../lib/browser.js     → /app/lib/browser.ts    ✅ (tsx resolves .ts)
  → ../lib/run-lock.js    → /app/lib/run-lock.ts    ✅
  → ../lib/timeout.js     → /app/lib/timeout.ts     ✅
  → ../lib/notify.js      → /app/lib/notify.ts      ✅
  → ../lib/db.js          → /app/lib/db.ts           ✅
  → ../scripts-lib/jane-parser.js → /app/scripts-lib/jane-parser.ts ✅
  → ../scripts-lib/normalizer.js  → /app/scripts-lib/normalizer.ts  ✅
    → ./types              → /app/scripts-lib/types.ts      ✅
    → ./brand-filter       → /app/scripts-lib/brand-filter.ts ✅
    → ./config             → /app/scripts-lib/config.ts      ✅
```

`config.ts` has a hardcoded local path (`SCRIPTS_DIR = path.resolve('/data/workspace/...')`), but **no code in the Jane import chain uses `SCRIPTS_DIR` or `RAW_SNAPSHOTS_DIR`**. Only `JANE_CATEGORIES` (a static object) is used. ✅

### 4. Browser Launch ✅

`firefox.launch({ executablePath, headless: true, env, firefoxUserPrefs, args })` — Playwright 1.50.1 spawns the CamoFox binary with the provided env vars and Firefox user prefs. The `CAMOU_CONFIG_1` env var is read by the CamoFox binary at startup (confirmed in the camoufox source — the binary is patched Firefox that reads `CAMOU_CONFIG_*` env vars to configure fingerprint spoofing).

### 5. Anti-Detection Config via CAMOU_CONFIG_1 ✅

**Verified as real and correctly implemented.** The official `camoufox` library generates `CAMOU_CONFIG_1` env vars with JSON-stringified config in the exact same way that `buildCamoufoxEnv()` in `browser.ts` does. The CamoFox binary (patched Firefox) reads these at startup. The config keys (`navigator.userAgent`, `screen.width`, `webGl.vendor`, etc.) match the documented format.

### 6. Cloudflare Clearance + Algolia Fetch ✅

The flow is:
1. Navigate to `www.iheartjane.com` → Cloudflare challenge completes
2. Wait 5s (+ 10s retry if still on challenge page)
3. Use `page.evaluate(fetch(...))` to call `search.iheartjane.com/1/indexes/*/query`
4. The `fetch()` runs in the browser's JS context with real TLS fingerprint + Cloudflare cookies
5. Cookies on `.iheartjane.com` parent domain are shared with `search.iheartjane.com`

This is the correct approach. Using `page.request.fetch()` would fail because Playwright's HTTP stack gets fingerprinted by Cloudflare. Using `page.evaluate(fetch())` uses the browser's native fetch. ✅

### 7. DB Writes ✅

`upsertOperator` → `upsertSource` → `createScrapeJob` → `upsertProduct` → `insertPrice` → `completeScrapeJob` → `completeScrapeRun`

All DB operations use the `pool` from `lib/db.ts` which requires `DATABASE_URL` env var. The `glass` schema is set via `SET search_path TO glass, public` on each connection. Standard `pg` Pool pattern. ✅

---

## Issues

### 🟠 1. Major — Silent Build Failure: `npx camoufox fetch || echo "WARN"`

**File:** `scrapers/jane/Dockerfile`, line 27

The `|| echo "WARN: camoufox fetch failed, will use playwright firefox"` pattern:
- If `camoufox fetch` fails (network, rate limit, disk), the Docker build **succeeds**
- But there is NO fallback to Playwright's Firefox — `launchCamoufox()` requires the CamoFox binary
- The error message says "will use playwright firefox" but the code has NO such fallback
- Runtime crash will be: `Error: camoufox-bin not found. Searched: ...`

**Fix:** Remove the `|| echo` fallback. Let the build fail if the binary can't be fetched:
```dockerfile
RUN npx camoufox fetch
```
Or add an explicit verification:
```dockerfile
RUN npx camoufox fetch && test -f /root/.cache/camoufox/camoufox-bin
```

### 🟡 2. Minor — Dead Import: `createRequire`

**File:** `scrapers/lib/browser.ts`, line 3

```ts
import { createRequire } from 'module';
```

This was used in the old `findCamoufoxBinary()` to resolve `camoufox-bin/package.json` via `require.resolve()`. After the rewrite, it's unused dead code.

**Fix:** Remove the import.

### 🟡 3. Minor — Chromium Flag in Firefox Args

**File:** `scrapers/lib/browser.ts`, line 152

```ts
args: ['--disable-blink-features=AutomationControlled'],
```

`--disable-blink-features` is a Chromium/Blink engine flag. Firefox uses Gecko, not Blink. This flag is silently ignored by Firefox/CamoFox — it won't cause a crash, but it's misleading and suggests a copy-paste from a Chromium automation setup.

**Fix:** Remove the flag, or replace with Firefox-relevant args if needed.

### 🟡 4. Minor — Redundant Binary Path Candidates

**File:** `scrapers/lib/browser.ts`, lines 94-104

Candidates #1, #2, and #3 all resolve to the same path when:
- `HOME=/root` (Docker default)
- `XDG_CACHE_HOME` is unset (Docker default)

All three become `/root/.cache/camoufox/camoufox-bin`. Not a bug, but needlessly checks the same path 3 times.

**Fix:** Deduplicate with a `Set`:
```ts
const candidates = [...new Set([
  path.join(homeDir, '.cache', 'camoufox', 'camoufox-bin'),
  path.join(process.env.XDG_CACHE_HOME || path.join(homeDir, '.cache'), 'camoufox', 'camoufox-bin'),
  '/root/.cache/camoufox/camoufox-bin',
  path.resolve(process.cwd(), 'camoufox-bin'),
])];
```

### 🟡 5. Minor — Playwright Version Mismatch

**File:** `scrapers/package.json`

- `playwright@1.50.1` (used by browser.ts) 
- `camoufox@0.1.19` depends on `playwright-core@^1.54.1` (resolved to 1.58.2)
- Docker image: `mcr.microsoft.com/playwright:v1.50.1-jammy`

The CamoFox binary is built for newer Playwright versions. The Playwright wire protocol (CDP for Chromium / the internal Firefox debugging protocol) might have differences between 1.50 and 1.54+. Currently works because Firefox's debugger protocol is more stable than CDP, but this is a **latent risk**. If CamoFox updates, the protocol mismatch could cause silent failures.

**Note:** This is pre-existing, not introduced by this PR.

### 🟡 6. Minor — No Run-Lock Concurrency Protection

**File:** `scrapers/lib/run-lock.ts`

The "always take over" pattern means two simultaneous Railway instances can both acquire locks and run concurrently, potentially causing duplicate data. The comment says "re-add the staleness check when pipeline is stable in production" — this is correct for dev but needs a ticket/reminder.

### ⚪ 7. Nit — Config.ts Hardcoded Path

**File:** `scripts/lib/config.ts`, line 7

```ts
export const SCRIPTS_DIR = path.resolve('/data/workspace/projects/glass/src/scripts');
```

This path doesn't exist in Docker. Not currently a problem because no Jane import chain uses `SCRIPTS_DIR`, but it's a footgun for future code that might import it.

### ⚪ 8. Nit — `maxStaleMins` Parameter Now Unused

**File:** `scrapers/lib/run-lock.ts`

The `maxStaleMins` parameter is accepted but completely ignored. The function signature should reflect this (or keep it for when the staleness check is re-added, with a JSDoc note).

---

## Strengths

- **Correct binary path resolution.** The rewrite from `node_modules/camoufox-bin/` to `~/.cache/camoufox/` matches where `npx camoufox fetch` actually puts the binary. This is the core fix and it's right.
- **CAMOU_CONFIG_1 env var mechanism is correctly replicated.** The config keys and JSON structure match the official camoufox library's output exactly. This will produce real anti-detection spoofing.
- **`page.evaluate(fetch())` is the correct Cloudflare bypass.** Using in-browser fetch rather than Playwright's HTTP API is essential for Cloudflare clearance.
- **Good error messages.** The `findCamoufoxBinary()` error now lists all searched paths and suggests the fix. Much better for debugging Railway failures.
- **Run-lock pragmatism.** Disabling the blocking behavior during dev/testing is the right call — stale locks were the #1 cause of failed retries.

---

## Summary

The core fix is correct — the binary path now matches where `npx camoufox fetch` actually downloads CamoFox. The `CAMOU_CONFIG_1` env var, the `page.evaluate(fetch())` Cloudflare bypass, and the full import chain all check out. The one **major issue** is the silent Dockerfile build failure pattern that could deploy a container without the CamoFox binary and crash at runtime with a confusing error. The minor issues (dead import, wrong browser engine flag, redundant paths) are cleanup items.

**This PR will work on Railway in the happy path.** Fix the Dockerfile `|| echo` to fail-fast on binary fetch failure to prevent the unhappy path from being silent.
