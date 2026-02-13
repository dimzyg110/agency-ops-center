# Jane Scraper Run Results — 2026-02-13

## Summary

| Metric | Value |
|--------|-------|
| **Run ID** | `565a517c-d09b-434a-b73f-17bee3ae24ba` |
| **Date** | 2026-02-13 14:42 UTC |
| **Status** | ✅ **FULL SUCCESS** |
| **Stores Discovered** | 39 |
| **Stores Succeeded** | 39 |
| **Stores Failed** | 0 |
| **Products Found** | 10,345 |
| **Prices Inserted** | 10,345 |
| **Duration** | 52 seconds |
| **Errors** | None |

## Test Run (3 stores)

Before the full run, a test with `--limit 3` was executed:

- **full-harvest-moonz**: 375 products ✅
- **fine-fettle-west-springfield**: 533 products ✅
- **cannabist-lowell-adult-use**: 337 products ✅
- **Total test prices**: 1,245

## Full Run — All 39 Stores

| # | Store | Products |
|---|-------|----------|
| 1 | full-harvest-moonz | 375 |
| 2 | fine-fettle-west-springfield | 534 |
| 3 | cannabist-lowell-adult-use | 337 |
| 4 | zen-leaf-sharon-rec | 328 |
| 5 | sanctuary-woburn-med | 155 |
| 6 | sanctuary-danvers-med | 159 |
| 7 | sanctuary-gardner-rec | 236 |
| 8 | rise-dispensaries-dracut | 496 |
| 9 | sanctuary-brookline-rec | 218 |
| 10 | fine-fettle-rowley | 445 |
| 11 | fine-fettle-northampton | 378 |
| 12 | cbdistillery-1 | (counted) |
| 13-21 | (various stores) | ✅ |
| 22 | rooted-in-newbury | 191 |
| 23 | patriot-care-greenfield-adult-use | 383 |
| 24 | patriot-care-greenfield-medical | 364 |
| 25 | zen-leaf-sharon-med | 98 |
| 26 | verilife-wareham-ma-med | 304 |
| 27 | kapha-cannabis | 372 |
| 28 | heal-cannabis-sturbridge | 6 |
| 29 | verilife-shrewsbury-ma-med | 248 |
| 30 | himalayan-high | 147 |
| 31 | hadleaf-cannabis | 198 |
| 32 | balagan-cannabis | 171 |
| 33 | spliffsecond-delivery | 175 |
| 34 | pinnacle-cannabis | 570 |
| 35 | rebelle-boston | 49 |
| 36 | rebelle-great-barrington-ma | 87 |
| 37 | rise-dispensaries-chelsea-medical | 351 |
| 38 | clear-sky-cannabis-dispensary-belchertown-rrh | 259 |
| 39 | clear-sky-cannabis-dispensary-north-adams-rrh | 259 |

## Architecture Notes

The `search.iheartjane.com` fix works perfectly:

1. **JaneClient** creates a CamoFox browser tab on Railway (`roviq-browser-production.up.railway.app`)
2. Tab navigates to `iheartjane.com` to obtain Cloudflare clearance cookies
3. All Algolia queries route through `search.iheartjane.com` via `page.evaluate(fetch(...))` inside the browser context
4. This bypasses Cloudflare bot protection since the browser has valid TLS fingerprint + challenge cookies

**No code changes were needed** — the implementation worked correctly on the first run.

## DB Impact

- Total prices in DB today after run: **59,423** (across all scrapers)
- Jane contribution: **~10,345 prices** from this run

## Log File

Full log: `/tmp/jane-scrape-20260213.log`
Summary JSON: `/data/workspace/projects/glass/src/scripts/jane-scrape-summary-1770993872992.json`
