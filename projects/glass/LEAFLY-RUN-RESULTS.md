# Leafly Full-Scale Scrape Audit & Run Results (2026-02-13 UTC)

## 1) Completeness audit (MANDATORY)

### Files audited
- `src/scripts/scrape-leafly.ts`
- `src/scripts/lib/leafly-client.ts`
- `src/scripts/lib/leafly-parser.ts`

### Finding: current carousel extraction is incomplete
The old extraction path used:
- `pageProps.productsForCategoryCarousels[].menuItems[]`

For large stores, this is only a featured subset (roughly ~8 items/category), not full inventory.

### Evidence (3-store comparison)

| Store slug | `pageProps.totalItems` | Carousel extracted | Full API total (`metadata.totalCount`) |
|---|---:|---:|---:|
| `253-farmacy-amherst` | 521 | 50 | 521 |
| `253-organic` | 731 | 49 | 731 |
| `bask---adult-use--recreational-` | 351 | 57 | 351 |

Conclusion: carousel extraction misses the majority of products.

### Full menu source identified
Frontend JS loads full inventory via paginated API:
- `GET https://consumer-api.leafly.com/api/dispensaries/v1/{slug}/menu_items?skip={n}&take={m}`
- `metadata.totalCount` exposes full item count
- `take` is capped at 18 by backend; requires pagination

### Pagination / infinite-scroll behavior
- Store page uses client-side pagination/infinite load via `skip`/`take`
- No usable `?page=2` SSR route for full menu payload
- Full inventory is fetched incrementally from API, not fully embedded in `__NEXT_DATA__`

---

## 2) Fix implemented

### Code changes
- **`src/scripts/lib/leafly-client.ts`**
  - Added `fetchAllLeaflyMenuItems(slug, perPage=18)`
  - Paginates through `/api/dispensaries/v1/{slug}/menu_items` until complete
  - Dedupes by `menuItemId/id/name`
  - Added retry/backoff for 429/503 and request timeout
- **`src/scripts/scrape-leafly.ts`**
  - Switched product source from carousel SSR data to `fetchAllLeaflyMenuItems(slug)`
  - Added explicit guard to prevent fallback to incomplete carousel subset

### Commit
- `b8c4df7`
- Message: `leafly: paginate full menu via consumer API instead of carousel`

---

## 3) Validation run

### Smoke run
Executed:
- `npx tsx scripts/scrape-leafly.ts --db --limit 5`

Observed examples:
- `253-organic: 723 products` (near full inventory scale, not carousel-scale)
- Some stores return no menu data (API + carousel both empty), expected for certain locations

---

## 4) Full-scale run

Launched full run:
```bash
cd /data/workspace/projects/glass/src
DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/scrape-leafly.ts --db 2>&1 | tee /tmp/leafly-scrape-20260213.log
```

Current session/log:
- Process session: `marine-slug`
- Log file: `/tmp/leafly-scrape-20260213.log`
- Progress observed during audit window: through `[leafly 12/292]`

---

## 5) Verification SQL

Note: this DB appears to use the `glass` schema (not default `public`) for scraper tables.
Use:

```sql
-- Today's Leafly price rows
SELECT COUNT(*)
FROM glass.prices p
JOIN glass.sources s ON p.source_id = s.id
WHERE s.source_type = 'leafly'
  AND p.scraped_at > CURRENT_DATE;

-- Per-store counts
SELECT s.url, COUNT(p.*)
FROM glass.prices p
JOIN glass.sources s ON p.source_id = s.id
WHERE s.source_type = 'leafly'
  AND p.scraped_at > CURRENT_DATE
GROUP BY s.url
ORDER BY count DESC
LIMIT 20;
```

---

## 6) Important operational note

Because the complete API is paginated at 18 items/request, full-completeness scraping is significantly heavier than carousel scraping and may trigger intermittent rate limiting (429). Retry/backoff is now built in, but full run duration is materially longer.