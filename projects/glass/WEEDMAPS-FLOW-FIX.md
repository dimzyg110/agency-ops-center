# Weedmaps Flow Fix (2026-02-13)

## Summary
Parser mismatch (Problem 1) was already fixed in `weedmaps-parser.ts` (`9b0de82`).
The remaining blocker is post-interstitial timing/interaction in scraper flow.

## Manual live verification (Railway CamoFox)
Target: `https://weedmaps.com/dispensaries/ddm-cannabis`

- Age gate appears first (`Yes, let me in!`).
- After clicking age gate and waiting ~5s, products are present in snapshot.
- Cookie dialog is also present (`Accept`) while products are present.
- Saved snapshots:
  - pre-gate: `/tmp/wm-ddm-pre.txt`
  - post-interstitial: `/tmp/wm-ddm-post.txt`

Observed post-interstitial snapshot contained menu product links immediately (`/dispensaries/<slug>/menu/...`) and product count hint (`568 Products`).

## Root cause found in flow
`dismissWeedmapsInterstitials` can keep interacting with cookie/UI controls during hydration windows, and scraping immediately after dismiss can happen before menu cards are reliably hydrated in some runs.

## Fix applied
File: `src/scripts/scrape-weedmaps.ts`

- Added a stabilization wait after interstitial dismissal in store worker flow:
  - after `dismissWeedmapsInterstitials(...)`
  - now waits `1500ms` before entering `scrapePaginatedMenu(...)`

This makes page-1 snapshot capture more reliable and reduces false `empty_menu`/timeout outcomes immediately after gate/cookie interactions.

## Validation notes
- Direct Railway CamoFox smoke check confirms products are visible post-gate.
- Additional quick check script confirmed post-gate menu href count = 24 on initial page window.
- Full 5-store run was started with Railway endpoint + DB settings to validate end-to-end against known-good slugs.

## Command used for multi-store run
```bash
DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
WEEDMAPS_CAMOFOX_URL="https://roviq-browser-production.up.railway.app" \
npx tsx scripts/scrape-weedmaps.ts --skip-discovery --db --slugs-file /tmp/wm-test-slugs-full.json
```
