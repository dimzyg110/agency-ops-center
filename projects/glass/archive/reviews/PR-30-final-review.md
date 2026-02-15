# PR #30 Final Re-Review (vs `main`)

## Verdict
**REQUEST REVISION**

## Original 5 review issues status
All 5 issues from `/data/workspace/projects/glass/reviews/PR-30-review-codex.md` are addressed in this diff:
1. ✅ Jane init now has guarded cleanup on failure (`scripts/lib/jane-client.ts:62-125`)
2. ✅ Jane `page.evaluate` now has timeout + retriable handling (`scripts/lib/jane-client.ts:146-193`)
3. ✅ Leafly network/timeout exceptions now retry (`scripts/lib/leafly-client.ts:157-183`)
4. ✅ Leafly throttle reset added and called at run start (`scripts/lib/leafly-client.ts:99-104`, `scripts/scrape-leafly.ts:112-113`)
5. ✅ Weedmaps hot-loop debug output gated behind `WM_VERBOSE` (`scripts/scrape-weedmaps.ts:73`, `245-273`, `363-380`, `648-666`)

## Issues Found

### Critical
1. 🔴 **Critical — Syntax/parse break in Jane scraper (blocks execution):**
   Logging edit introduced mismatched block braces around DB init logic, causing TypeScript parse failure.
   - **File:** `scripts/scrape-jane.ts`
   - **Lines:** `128-134` (unbalanced block), parser fails at `314`
   - **Evidence:** `npx tsc --noEmit ...` reports `TS1128: Declaration or statement expected` at line 314.

2. 🔴 **Critical — Duplicate import declaration in Leafly scraper (build break in strict transpile/lint paths):**
   `logger` is imported twice, once at line 6 and again at line 20.
   - **File:** `scripts/scrape-leafly.ts`
   - **Lines:** `6` and `20`
   - **Impact:** Duplicate identifier/import declaration; should be removed before merge.

### Major
- None.

### Minor
1. 🟡 **Minor — Structured logging schema is not fully consistent across scrapers:**
   Field naming alternates between camelCase and snake_case for similar events.
   - **Examples:**
     - `scripts/scrape-jane.ts:91-97` (`totalStoresQueued`, `skipDiscovery`) vs `301-309` (`stores_total`, `duration_ms`)
     - `scripts/scrape-leafly.ts:115-120` (`totalStoresQueued`, `skipDiscovery`) vs `329-339` (`stores_total`, `duration_ms`, `final_penalty_ms`)
   - **Impact:** harder downstream parsing/aggregation if consumers expect one stable schema.

## Production-readiness
Not production-ready yet due to the 2 critical issues above. After fixing those, this is very close to merge-ready.
