# Weedmaps Scraper Build Summary

## What was implemented

### 1) New parser: `src/scripts/lib/weedmaps-parser.ts`
- Added Weedmaps snapshot extractor:
  - `extractWeedmapsProductsFromSnapshot(snapshot)`
- Added Weedmaps parser:
  - `parseWeedmapsProducts(rawProducts, slug)`
- Implemented category tag handling for:
  - `FLOWER`, `BIG BUDS`, `SMALLS`, `PRE-ROLL`, `INFUSED`, `CONCENTRATES`, `EDIBLES`, `DRINKS`, `WELLNESS`, `GEAR`
- Added `NON_BRAND_TOKENS` blocklist and `brandParseFailed` signaling.
- Handles edge cases:
  - missing THC%
  - missing brand (falls back to heuristics / Unknown)
  - multi-word brands
  - rating suffix text removal

### 2) New orchestrator: `src/scripts/scrape-weedmaps.ts`
- Full CLI parity with Dutchie:
  - `--skip-discovery`
  - `--slugs-file <path>`
  - `--limit <n>`
  - `--db`
  - `--dry-run`
  - `--resume <runId>`
- Discovery flow implemented:
  - state page city extraction from `/dispensaries/in/united-states/massachusetts`
  - city page slug discovery
  - writes to `weedmaps-slugs.json`
- Age-gate handling for Weedmaps button: `Yes, let me in!`
- Cookie banner best-effort dismiss/ignore
- Pagination implemented for default all-products menu (`?page=N`) with hardening:
  - extracts total product count (`NNN Products`)
  - expected pages = `Math.ceil(count / 24)`
  - safety cap at 50 pages
  - dedup by href across pages
  - retry once on empty page before stopping
- Auto-resume implemented concretely:
  - startup checks `getActiveRunForToday('weedmaps')` when no explicit `--resume`
  - skips already completed sources in the active run
- Quality guardrails included:
  - 0 parsed products => failed job
  - >50% empty category coverage with historical data => suspicious
  - tracks brand parse failures in quality metrics
- DB writes use parser type:
  - `weedmaps_v1`

### 3) New slugs seed file: `src/scripts/weedmaps-slugs.json`
- Added initial Weedmaps slug record in Dutchie-compatible format.

### 4) Config updates: `src/scripts/lib/config.ts`
- Added `WEEDMAPS_CATEGORIES` mapping exactly as requested.
- Added `WEEDMAPS_MA_CITIES` list for discovery fallback/support.

### 5) Type updates: `src/scripts/lib/types.ts`
- Added `WeedmapsRawProduct`.
- Added `WeedmapsSlugRecord` alias.

### 6) DB helper update: `src/scripts/lib/db.ts`
- `insertPrice()` now accepts parser type parameter (default remains `dutchie_v2` for compatibility).
- Weedmaps orchestrator passes `weedmaps_v1` explicitly.

### 7) Fixtures/tests from real Weedmaps-style snapshots
Added fixture files:
- `src/scripts/lib/__fixtures__/weedmaps-diem-page1.snapshot.txt`
- `src/scripts/lib/__fixtures__/weedmaps-missing-brand.snapshot.txt`
- `src/scripts/lib/__fixtures__/weedmaps-multiword-brand.snapshot.txt`

Added parser fixture runner:
- `src/scripts/test-weedmaps-parser.ts`

## Validation run
- Ran parser fixture script:
  - `npx tsx src/scripts/test-weedmaps-parser.ts`
  - Output confirms extraction/parsing across all fixtures.

## Notes
- TypeScript compiler (`tsc`) is not installed in this environment, so full `tsc --noEmit` could not be run.
- Implementation follows Dutchie pipeline patterns while applying Weedmaps-specific behavior and all 5 mandatory review changes.
