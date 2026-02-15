# GLASS Scraper Local Run Guide

This document audits portability and local reliability for:
- `scripts/scrape-jane.ts`
- `scripts/scrape-leafly.ts`
- `scripts/scrape-weedmaps.ts`
- `scripts/scrape-dutchie.ts`

## What was verified

## 1) CLI help support
All 4 scrapers now support `--help` / `-h` and print usage.

## 2) End-to-end run status (with `--skip-discovery --limit 1 --db`)
- **Jane**: ✅ successful run (1 store, prices inserted)
- **Leafly**: ⚠️ script runs, but `--limit 1` depends on first slug in slugs file (may be empty/dead menu)
- **Weedmaps**: ✅ runs locally with Playwright Firefox (long-running on high-volume stores)
- **Dutchie**: ✅ runs when `CAMOFOX_URL` points to a reachable CamoFox HTTP API (local or remote)

---

## Requirements by scraper

### Shared npm/runtime requirements
From `src/package.json`:
- `playwright`
- `pg`
- `drizzle-orm` (not directly used by these 4 scripts, but present in project)
- `csv-parse` (not required by these 4)
- TypeScript runtime invocation via `npx tsx`

### Shared env vars
- `DATABASE_URL` (required when `--db` is passed)
- `SCRAPER_CONCURRENCY` (optional, default `1`)

### Jane (`scrape-jane.ts`)
- External services:
  - iHeartJane + Algolia proxy (`https://search.iheartjane.com`)
- System dependencies:
  - Playwright Firefox browser binary (`npx playwright install firefox`)
- Important env vars (optional overrides in `scripts/lib/config.ts`):
  - `JANE_ALGOLIA_APP_ID`
  - `JANE_ALGOLIA_API_KEY`
  - `JANE_STORES_INDEX`
  - `JANE_PRODUCTS_INDEX`
  - `JANE_STATE_FILTER`

### Leafly (`scrape-leafly.ts`)
- External services:
  - `www.leafly.com` + `consumer-api.leafly.com`
- System dependencies:
  - None beyond Node runtime
- Notes:
  - Per-store outcomes vary by slug quality; some slugs are dead/empty menus.

### Weedmaps (`scrape-weedmaps.ts`)
- External services:
  - `weedmaps.com`
- System dependencies:
  - Playwright Firefox browser binary
  - Linux host libs for Playwright (`npx playwright install-deps` on fresh Linux)
- Notes:
  - Some stores have very large menus; `--limit 1` can still take multiple minutes.

### Dutchie (`scrape-dutchie.ts`)
- External services:
  - Dutchie site
  - CamoFox HTTP API endpoint
- System dependencies:
  - Reachable CamoFox server (`CAMOFOX_URL`, default `http://localhost:9377`)
- Env vars:
  - `CAMOFOX_URL` (set this for non-local CamoFox, e.g. hosted endpoint)

---

## Portability issues found and fixes applied

### Fixed
1. **Hardcoded absolute workspace path**
   - File: `scripts/lib/config.ts`
   - Before: `SCRIPTS_DIR` hardcoded to `/data/workspace/projects/glass/src/scripts`
   - After: computed relative to module path (`import.meta.url` + `fileURLToPath`)
   - Impact: scripts now portable across machines/paths.

2. **No `--help` support in all 4 scrapers**
   - Files:
     - `scripts/scrape-jane.ts`
     - `scripts/scrape-leafly.ts`
     - `scripts/scrape-weedmaps.ts`
     - `scripts/scrape-dutchie.ts`
   - Added `--help` / `-h` flag handling + usage output.

### Remaining operational assumptions (documented, not hardcoded blockers)
- Dutchie requires a running CamoFox HTTP API (local or remote)
- Jane/Weedmaps require Playwright browser binaries and Linux libs
- `--skip-discovery` assumes slug JSON files already exist

---

## Portable run script

Use:
- `src/scripts/run-scrapers-local.sh`

It:
- Validates required env (`DATABASE_URL`)
- Sets `CAMOFOX_URL` default for Dutchie
- Installs Playwright browsers
- Runs all 4 `--help` checks
- Runs all 4 end-to-end smoke commands

---

## Recommended local bootstrap

```bash
cd /path/to/glass/src
npm install
npx playwright install firefox chromium
# Linux only (fresh machine):
npx playwright install-deps

export DATABASE_URL="postgresql://..."
# For Dutchie if not running local camofox server:
export CAMOFOX_URL="https://roviq-browser-production.up.railway.app"

./scripts/run-scrapers-local.sh
```
