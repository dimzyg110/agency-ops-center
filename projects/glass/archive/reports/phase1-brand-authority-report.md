# Phase 1 Brand Authority Report

Date (UTC): 2026-02-14

## Summary
- Leafly brands scraped/upserted: **469**
- Weedmaps brands scraped/upserted: **225**
- Internal brands seeded: **307**

## What was executed
1. Added new scrapers:
   - `scripts/brand-authority/scrape-leafly-brands.ts`
   - `scripts/brand-authority/scrape-weedmaps-brands.ts`
2. Ensured `public.brand_authority` exists (idempotent create in scraper scripts, per sprint schema).
3. Ran directory ingest and upserts into `brand_authority` with:
   - `verified = true`
   - `verification_method = 'directory'`
   - `source_confidence = 0.95`
4. Seeded internal brands using provided SQL (`source='internal'`, `verification_method='hybrid'`, `source_confidence=0.70`).
5. Ran authority count backfill from products/prices/sources join.
6. Generated top-50 output CSV:
   - `/data/workspace/projects/glass/reports/top-50-authority-brands.csv`

## Top-50 authority brands (rank query output)

```csv
brand_id,canonical_name,source,product_count,platform_count
383,Anthologie,leafly,219,4
```

## Errors / Issues
- The sprint plan backfill SQL section 1.5 references `products.source_id`, but in this DB shape `products` does not have `source_id`.
- Backfill was adapted to join through `prices`:
  - `products p -> prices pr (pr.product_id = p.id) -> sources s (s.id = pr.source_id)`
- Due canonical name strict matching (`lower(trim(ba.canonical_name)) = lower(trim(p.brand))`), only a small subset of verified directory brands currently matched internal product brand values in the top-50 rank query.

## Notes
- Scraper scripts include fetch-first strategy and Playwright Firefox fallback per wartime spec.
- Search path was set to `public` for all SQL execution.
