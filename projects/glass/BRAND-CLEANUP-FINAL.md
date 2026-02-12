# Brand Cleanup Final Verification (2026-02-12 UTC)

## Code Changes (Second-Pass Hardening)

Centralized brand validation was added and wired into both pipelines:

- `services/scrape/src/brand.ts` (new)
  - Added shared `isValidBrand(input)` + whitespace normalizer
- `services/scrape/src/normalizer.ts`
  - `normalizeBrand()` now uses shared `isValidBrand()`
- `services/scrape/src/parsers/dutchie.ts`
  - Brand parsing now uses shared `isValidBrand()`
- `scripts/lib/brand-filter.ts` (new)
  - Added shared script-level `isValidBrand()` + normalizer
- `scripts/scrape-dutchie-ma.ts`
  - `sanitizeBrand()` now uses shared `isValidBrand()`
- `scripts/lib/weedmaps-parser.ts`
  - Brand parsing now rejects invalid brand candidates via shared `isValidBrand()`
- `scripts/lib/normalizer.ts`
  - Normalized brand path now uses shared `isValidBrand()`

## New Rejection Patterns Added

The centralized filters now reject brands that are:

- longer than **50 chars**
- category-style prefixes: `SHIRTS`, `HOODIES`, `HATS`, `APPAREL`, `ROLLING PAPERS`, `GUMMIES`, `Cartiridge/Cartridge`, `Pre-Roll`, `ALL-IN-ONE`
- start with `[`
- start with `by `
- contain `Bundle` / `Flower Bundle`
- contain `TAC:` / `THC:`
- contain `Disposable` / `Disposable,`
- look like product spec tokens (`100mg`, `1g`, `20pk`, numeric-only, etc.)
- begin with common descriptor prefixes (`THC`, `CBD`, `FLOWER`, `CHOCOLATES`, `BEVERAGE`, `SMALL BUD`, `PRE-GROUND`, `PREMIUM FLOWER`)

## DB Cleanup Applied

Database: `postgresql://postgres:***@turntable.proxy.rlwy.net:18582/railway`

Manual cleanup updates executed during final pass:

- pass A (second-pass pattern cleanup): **6,325** rows set `brand = NULL`
- pass B (remaining obvious descriptor/spec cleanup): **2,181** rows set `brand = NULL`

Total nullified this pass: **8,506** brands.

## Final Verification Query Results

### 1) Top 50 brands by count

Top results are now predominantly plausible brand entities (examples):
`Cali Blaze (250), Bountiful Farms (231), Happy Valley (145), Perpetual (145), Good Chemistry (106), Jeeter (92), Select (81), Fernway (75)`.

(Full top-50 query run completed; output captured in terminal logs.)

### 2) Suspicious-pattern query (top 30)

Remaining suspicious set includes mixed quality: some likely valid brands and some residual junk.
Top entries:

- `Choice Chews (74)`
- `Chews (41)`
- `Baked Bliss Edibles (40)`
- `Elderflower (28)`
- `Incredibles (22)`
- `Fruit Chews (20)`
- `High Purity THC (16)`
- plus long descriptor-like leftovers (`...All In One Diamonds Vape`, `...Infused Pre-Roll 5-pack`, etc.)

### 3) Total brand health

```sql
total_products: 95,984
with_brand:     36,089
without_brand:  59,895
brand_pct:      37.6%
```

### 4) Distinct brand count

```sql
COUNT(DISTINCT brand): 14,468
```

## Remaining Manual Review Needed

Residual suspicious brands still exist (especially long descriptor-like strings and generic edible/chew terms). Suggested follow-up:

1. Build an allowlist for confirmed edible brands (e.g., `Incredibles`, `Choice Chews` if legit).
2. Null out remaining descriptor-style brands matching:
   - `All In One`, `Infused Pre-Roll`, `Vape Cartridge`, bracketed pack descriptors, etc.
3. Run one final allowlist-aware cleanup to reduce false positives while preserving known brands.
