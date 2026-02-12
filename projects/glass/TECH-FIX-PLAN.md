# GLASS Platform — Technical Fix Plan

**Author:** Technical Architect (synthesized from 3 independent reviews + DB audit + code analysis)
**Date:** 2026-02-12
**Database verified:** Live queries against Railway PostgreSQL
**Codebase verified:** All source files read and cross-referenced

---

## Executive Summary

Three independent reviews converged on the same critical finding: **GLASS has genuinely valuable data (95K products, 110K prices, 31K CCC records, 46K plant activity records) wrapped in a layer of fake fallbacks, unit mismatches, and parsing garbage that would destroy credibility with any informed operator.**

This plan addresses 10 issues across 3 priority tiers. Total estimated effort: **38-52 hours of agent work + 4-6 hours of Randy's time** (API keys, deployment decisions). With parallel execution, the P0 fixes can ship in **2-3 days**.

---

## Execution Order & Parallelism

```
DAY 1 (parallel):
  ├── Lane A: Fix #1 (CCC Cross-Reference) + Fix #5 (CCC Weekly Sales Nulls)
  ├── Lane B: Fix #2 (Kill Fake Fallbacks) — audit + implement empty states
  └── Lane C: Fix #3 (Brand Parsing Bug) — SQL cleanup + scraper fix

DAY 2 (parallel):
  ├── Lane A: Fix #4 (Geocode Operators) — needs API key from Randy
  ├── Lane B: Fix #6 (Normalize Categories) + Fix #7 (Surface Plant Activity)
  └── Lane C: Fix #2 continued (finishing all pages)

DAY 3:
  ├── Lane A: Fix #8 (Pending Applications → Threats)
  └── Lane B: Fix #9 + #10 (Historical Data Architecture) — design + implement

ONGOING:
  └── Daily scraping operational (Fix #9) — accumulates data for all time-series features
```

---

## Fix #1: CCC Cross-Reference Unit Mismatch

### Problem
The public Market page's flagship feature shows **"509% markup on flower"** — comparing CCC's per-gram wholesale price ($5.81/g) against GLASS's per-unit shelf price ($35.53 per eighth). This is a unit mismatch, not a real markup. Any operator who does the math will immediately distrust the platform.

**Evidence (live DB query):**
```
CCC flower avg (per gram, last 365d): $4.04/g
GLASS flower avg (per unit): $35.53
GLASS flower avg (per gram, where available): $18.15/g
Real markup (per-gram to per-gram): ~349% (CCC is blended wholesale/transfer, not retail)
```

The `prices` table has a `price_per_gram` column — 26,615 of 48,967 flower observations (54%) have this populated. For concentrates, 5,789 of 5,920 (98%) have it. So we CAN do apples-to-apples comparison for these categories.

### Root Cause
The `/ccc/cross-reference` endpoint in `src/services/api/src/routes/ccc.ts` uses `AVG(pr.price)` (per-unit) for the GLASS side but CCC reports per-gram prices. The query does no unit normalization.

### Fix

**File: `src/services/api/src/routes/ccc.ts` — Replace the `cross-reference` endpoint**

The correct approach is a **hybrid strategy**:
- For categories where `price_per_gram` is available (flower, preroll, concentrate): use per-gram comparison
- For categories where pricing is per-unit (edible, vape): compare per-unit directly
- Always show the unit in the response so the frontend can label clearly

```sql
-- Replace the GLASS CTE in the cross-reference query with:
glass AS (
  SELECT
    p.category AS glass_category,
    CASE 
      -- Per-gram categories: use price_per_gram where available
      WHEN p.category IN ('flower', 'preroll', 'concentrate') THEN
        ROUND(AVG(pr.price_per_gram)::numeric, 2)
      -- Per-unit categories: use shelf price directly  
      ELSE
        ROUND(AVG(pr.price::numeric)::numeric, 2)
    END AS glass_scraped_avg,
    CASE 
      WHEN p.category IN ('flower', 'preroll', 'concentrate') THEN 'g'
      ELSE 'ea'
    END AS glass_unit,
    COUNT(*)::int AS glass_observation_count
  FROM prices pr
  JOIN products p ON p.id = pr.product_id
  WHERE pr.scraped_at >= NOW() - INTERVAL '30 days'
    AND p.category IN ('flower', 'preroll', 'vape', 'edible', 'concentrate')
    AND CASE 
      WHEN p.category IN ('flower', 'preroll', 'concentrate') THEN pr.price_per_gram IS NOT NULL
      ELSE TRUE
    END
    AND pr.price > 0 AND pr.price < 500  -- filter outliers
  GROUP BY p.category
),
-- Also filter CCC to matching units:
ccc AS (
  SELECT
    glass_category,
    ROUND(AVG(avg_price)::numeric, 2) AS ccc_official_avg,
    MAX(report_date) AS as_of
  FROM mapped_ccc
  WHERE glass_category IS NOT NULL
    AND (
      (glass_category IN ('flower', 'preroll', 'concentrate') AND unit = 'g')
      OR (glass_category IN ('edible') AND unit = 'ea')
      OR (glass_category IN ('vape') AND unit = 'ea')
    )
  GROUP BY glass_category
)
```

**Also update the SELECT to include unit:**
```sql
SELECT
  INITCAP(REPLACE(ccc.glass_category, '-', ' ')) AS category,
  ccc.ccc_official_avg::float8 AS ccc_official_avg,
  glass.glass_scraped_avg::float8 AS glass_scraped_avg,
  glass.glass_unit AS unit,
  CASE
    WHEN ccc.ccc_official_avg > 0
      THEN ROUND((((glass.glass_scraped_avg - ccc.ccc_official_avg) / ccc.ccc_official_avg) * 100)::numeric, 1)::float8
    ELSE NULL
  END AS markup_pct,
  glass.glass_observation_count,
  ccc.as_of::text AS as_of
FROM ccc
JOIN glass ON glass.glass_category = ccc.glass_category
ORDER BY category ASC
```

**File: `src/apps/web/src/pages/Market.tsx`**
- Update the `FALLBACK_CROSS_REFERENCE` to use per-gram values and include unit
- Update the cross-reference table to show unit labels: `$18.15/g` not just `$18.15`
- Change "markup" label to "Retail Premium over CCC Transfer Price" with a tooltip explaining what CCC transfer prices mean
- Add footnote: "CCC reports average transfer prices between licensees. GLASS tracks retail shelf prices. The premium reflects retail margin + operating costs."

### Estimated Effort
- API change: 2 hours
- Frontend label/context updates: 1 hour
- **Total: 3 hours**

### Dependencies
None — can start immediately.

### Verification
```sql
-- After fix, cross-reference should show realistic markups:
-- Flower: ~349% (per-gram retail vs per-gram CCC transfer) 
-- This is still a big number but it's CORRECT — CCC transfer prices are wholesale
-- Edible: ~-3% (actually comparable since both are per-unit)
-- The key test: no category should show >500% markup
```

---

## Fix #2: Kill All Fake Data Fallbacks

### Problem
When API calls return empty or null data, the frontend falls back to hardcoded fake data. This means the platform shows fabricated sparklines, fabricated weekly sales charts, fabricated WoW/MoM trends, fabricated demographics, and fabricated news headlines — all presented as real data with no indication they're fake.

**Evidence (code audit):**

| File | Fake Data | Impact |
|------|-----------|--------|
| `Market.tsx:65-134` | 7 FALLBACK_* constants (snapshot, prices, cross-ref, weekly sales, pipeline, demographics, news) | Public page shows fake sales, fake demographics, fake news |
| `Market.tsx:289-295` | State initialized to fallback values (flash of fake data on every load) | Users see fake data before API responds |
| `Market.tsx:394-495` | 15+ fallback-to-FALLBACK patterns in data processing | Any API failure silently shows fake data |
| `MorningBrief.tsx:43-66` | `generateSparklineData()` — deterministic pseudo-random sparkline generator | Fake price trends for every product |
| `MorningBrief.tsx:235-288` | 6 mock data objects (treemapMock, sunburstMock, economicMock, strainStreamMock, marketSizeMock, growthCurvesMock) | Defined but appear unused (API data loads over them) |
| `MorningBrief.tsx:324-325` | `totalProducts = movers.length * 150`, `priceChanges24h = movers.length * 15` | Fabricated hero stat numbers |
| `PriceWire.tsx:38-55` | `generateSparklineData()` (different implementation, uses Math.random) | Random sparklines on price wire |
| `PriceWire.tsx:147-198` | 5 mock objects (matrixMock, volatilityMock, radarMock, cascadeMock, tickerMock) | Fallbacks for all viz panels |
| `ThreatRadar.tsx:16-45` | 4 mock objects (nodes, links, timeline, pipeline) | Fake threat network |
| `Settings.tsx:11-29` | mockOperator, mockWatchlist | Fake operator profile |

### Root Cause
The original developer pattern was "always show something" — which is reasonable for demos, but in production it creates a trust problem. The frontend uses `state initialized to FALLBACK → API fetches → updates if data exists → falls back silently if empty`.

### Fix

**Strategy: Replace fake data with honest empty states.**

The key principle: **Better to show "No data yet" than to show fake data that an operator might act on.**

**Step 1: Create a reusable `DataPending` component**

```tsx
// src/apps/web/src/components/DataPending.tsx
interface DataPendingProps {
  title?: string;
  message?: string;
  startDate?: string; // When we started collecting
  daysNeeded?: number; // How many days of data needed
}

export function DataPending({ 
  title = "Collecting data", 
  message = "This visualization requires historical data. We started tracking on Feb 12, 2026.",
  startDate = "2026-02-12",
  daysNeeded
}: DataPendingProps) {
  const daysSince = Math.floor((Date.now() - new Date(startDate).getTime()) / 86400000);
  const progress = daysNeeded ? Math.min(100, (daysSince / daysNeeded) * 100) : null;
  
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="mb-3 h-10 w-10 rounded-full border border-glass-border flex items-center justify-center">
        <Clock className="h-5 w-5 text-glass-subtle" />
      </div>
      <p className="font-display text-sm text-glass-muted">{title}</p>
      <p className="mt-1 font-mono text-[10px] text-glass-subtle">{message}</p>
      {progress !== null && (
        <div className="mt-3 w-48">
          <div className="h-1 rounded-full bg-glass-elevated">
            <div className="h-full rounded-full bg-glass-accent" style={{ width: `${progress}%` }} />
          </div>
          <p className="mt-1 font-mono text-[10px] text-glass-subtle">{daysSince}/{daysNeeded} days collected</p>
        </div>
      )}
    </div>
  );
}
```

**Step 2: File-by-file changes**

**`Market.tsx`:**
1. Remove `FALLBACK_SNAPSHOT` — replace initial state with `null`, show skeleton loader until API responds
2. Remove `FALLBACK_PRICE_ROWS` — compute price rows purely from cross-reference API data; show "—" for WoW/MoM until we have 7+ days of data
3. Keep `FALLBACK_CROSS_REFERENCE` but ONLY as initial loading state (never as permanent fallback). If API returns empty, show `<DataPending />` instead
4. Remove `FALLBACK_WEEKLY_SALES` entirely. Show `<DataPending title="Weekly sales data unavailable" message="CCC weekly sales figures are being re-imported. Check back soon." />` since all 71 rows have NULL values
5. Remove `FALLBACK_PIPELINE` — the real pending applications API works (234 rows), so this fallback is unnecessary
6. Remove `FALLBACK_DEMOGRAPHICS` — ccc_demographics has 0 rows. Show `<DataPending title="Demographics data coming soon" message="CCC industry demographics are being sourced." />`
7. Remove `FALLBACK_NEWS` — show nothing or a link to the newsletter instead of fake headlines
8. Change state initialization: `useState<SnapshotData | null>(null)` instead of `useState<SnapshotData>(FALLBACK_SNAPSHOT)`

**`MorningBrief.tsx`:**
1. Remove `generateSparklineData()` function entirely (lines 43-66)
2. Replace sparkline in Price Wire summary with either:
   - A simple "↑ +2.3%" or "↓ -1.1%" text indicator (no chart)
   - Or `<DataPending />` with "Sparklines available after 7 days of price tracking"
3. Fix hero stats calculation (lines 324-325):
   ```tsx
   // BEFORE (fabricated):
   totalProducts: briefData.price_wire?.top_movers?.length ? briefData.price_wire.top_movers.length * 150 : 2847,
   // AFTER (real or honest):
   totalProducts: briefData.snapshot?.total_products ?? null, // needs API change to return real count
   ```
4. Remove all 6 mock data objects (lines 235-288) — they appear unused (API data loads) but should be deleted to prevent future fallback

**`PriceWire.tsx`:**
1. Remove `generateSparklineData()` (line 38-55)
2. Remove all 5 mock objects (lines 147-198)
3. When viz data is empty, show `<DataPending daysNeeded={14} />` instead of mock data

**`ThreatRadar.tsx`:**
1. Remove 4 mock objects (lines 16-45)
2. Show real `ccc_pending_applications` data instead of the 6 hand-crafted threats

**`Settings.tsx`:**
1. Replace `mockOperator` with data from the authenticated user's operator
2. Replace `mockWatchlist` with actual watchlist data (or empty state)

### Estimated Effort
- DataPending component: 1 hour
- Market.tsx overhaul: 3 hours
- MorningBrief.tsx cleanup: 2 hours
- PriceWire.tsx cleanup: 1.5 hours
- ThreatRadar.tsx + Settings.tsx: 1.5 hours
- Testing across all pages: 2 hours
- **Total: 11 hours**

### Dependencies
None — can start immediately. Should coordinate with Fix #1 (cross-reference) and Fix #5 (weekly sales) since those affect what Market.tsx displays.

### Verification
1. Load Market page with DevTools Network tab open → no FALLBACK_ values should appear in rendered HTML
2. Disable API temporarily → page should show `<DataPending />` states, NOT fake data
3. Check for any `Math.random()` or pseudo-random data generation in the entire frontend: `grep -rn "Math.random\|generateSparkline\|pseudoRandom" src/apps/web/`
4. Visual scan of every page — nothing should show data that doesn't come from the DB

---

## Fix #3: Brand Parsing Bug

### Problem
"stock. Order soon." is the #1 brand in the database with **4,149 products**. At least **16,376 products** (~17%) have garbage brand values parsed from UI elements, category names, product format labels, or availability badges.

**Evidence (live DB query — top garbage brands):**
```
stock. Order soon.     4,149 products
Unknown                2,074 products  
510                      346 products (vape format)
Flower                   299 products (category)
Gummies                  242 products (category)
Medical patients only    122 products (access restriction)
Pre-Roll                 114 products (category)
Disposable               111 products (format)
Preroll | 1g             107 products (category + weight)
Infused Pre-Roll          95 products (category)
THC                       92 products (chemical compound)
| Smash Hits              89 products (pipe-separated junk)
Gummy                     86 products (category)
| Assorted Colors         83 products (pipe-separated junk)
| 3.5g Flower             79 products (pipe-separated junk)
Preroll                   75 products (category)
Hybrid | 1g               70 products (strain type + weight)
```

Also found: `stock. Order soon."` (with trailing quote, 62 products), `| Nature's Heritage` (leading pipe, 58 products), many `| XXX` patterns.

### Root Cause
The Dutchie parser in `src/services/scrape/src/parsers/dutchie.ts` extracts brand from LD+JSON and `__PRELOADED_STATE__` blobs. The parser does not filter out:
1. Availability badge text ("stock. Order soon.", "Medical patients only")
2. Category names being placed in brand fields by Dutchie's data structure
3. Pipe-separated compound fields (e.g., "| Smash Hits", "Hybrid | 1g")
4. Product format descriptors ("510", "Disposable", "Gummy")

The normalizer in `src/services/scrape/src/normalizer.ts` has a `normalizeBrand()` function that only trims whitespace and title-cases — no content validation.

### Fix

**Part A: SQL Cleanup Script (run once, immediately)**

```sql
-- Step 1: Fix the known garbage brands
-- Set to NULL (not 'Unknown') so they can be re-extracted if scraper improves
UPDATE products SET brand = NULL WHERE brand IN (
  'stock. Order soon.',
  'stock. Order soon."',
  'Unknown',
  'Medical patients only',
  '510',
  'THC',
  'Gummy',
  'Gummies', 
  'Flower',
  'Pre-Roll',
  'Preroll',
  'Disposable',
  'Infused Pre-Roll',
  'Cones 1 1/4'
);

-- Step 2: Fix pipe-prefixed brands (| Smash Hits, | Assorted Colors, etc.)
UPDATE products SET brand = TRIM(LEADING '| ' FROM brand)
WHERE brand LIKE '| %' AND LENGTH(TRIM(LEADING '| ' FROM brand)) > 2;

-- Step 3: Fix pipe-suffixed brands (Infused Pre-Roll |, Disposable Vape |, etc.)
UPDATE products SET brand = NULL
WHERE brand LIKE '% |' OR brand LIKE '%| ';

-- Step 4: Fix compound pipe fields where the brand contains product info
UPDATE products SET brand = NULL
WHERE brand ~ '^\|' -- starts with pipe
   OR brand ~ '\| \d' -- pipe followed by number (e.g., "Preroll | 1g")
   OR brand ~ '^\d+(\.\d+)?(mg|g|oz|ml)' -- starts with weight
   OR brand ~ 'Hybrid \|' -- strain type compounds
   OR brand ~ 'Indica \|'
   OR brand ~ 'Sativa \|'
   OR brand ~ 'SDH \|';

-- Step 5: Normalize known brand duplicates
UPDATE products SET brand = 'Cali Blaze' WHERE brand = 'Cali-Blaze';

-- Step 6: Count the damage
SELECT 
  COUNT(*) FILTER (WHERE brand IS NULL) as null_brands,
  COUNT(*) FILTER (WHERE brand IS NOT NULL) as valid_brands,
  COUNT(*) as total
FROM products;
```

**Part B: Fix the Dutchie Parser**

**File: `src/services/scrape/src/parsers/dutchie.ts`**

Add a brand validation step after extraction:

```typescript
// Add this constant at the top of the file
const GARBAGE_BRAND_PATTERNS = [
  /^stock\b/i,
  /order soon/i,
  /medical patients/i,
  /^\d+(mg|g|oz|ml)/i,   // Starts with weight
  /^\|/,                   // Starts with pipe
  /\|$/,                   // Ends with pipe
  /^(flower|preroll|pre-roll|vape|edible|concentrate|tincture|topical|gummies?|disposable|infused|hybrid|indica|sativa|thc|cbd|cones?)$/i,
  /^510$/,
];

function isGarbageBrand(brand: string): boolean {
  const trimmed = brand.trim();
  if (trimmed.length < 2) return true;
  if (trimmed.length > 80) return true;
  return GARBAGE_BRAND_PATTERNS.some(pattern => pattern.test(trimmed));
}
```

Then in both `parseFromLdJson` and `parseFromStateBlob`, add the filter:
```typescript
const brand = /* existing extraction logic */;
const cleanBrand = brand && !isGarbageBrand(brand) ? brand : undefined;
```

**Part C: Fix the Normalizer**

**File: `src/services/scrape/src/normalizer.ts`**

Add to `normalizeBrand()`:
```typescript
function normalizeBrand(brand: string | undefined): string | null {
  if (!brand) return null;
  const normalized = normalizeWhitespace(brand);
  if (normalized.length < 2 || normalized.length > 80) return null;
  
  // Filter known garbage patterns
  const lower = normalized.toLowerCase();
  const garbagePatterns = [
    'stock', 'order soon', 'medical patients', 'low stock',
    'out of stock', 'coming soon', 'sold out'
  ];
  if (garbagePatterns.some(p => lower.includes(p))) return null;
  
  // Filter if brand matches a category name
  const categories = ['flower', 'preroll', 'pre-roll', 'vape', 'edible', 
    'concentrate', 'tincture', 'topical', 'gummies', 'gummy', 'disposable', 'thc', 'cbd'];
  if (categories.includes(lower)) return null;
  
  // Filter pipe-prefixed junk
  if (normalized.startsWith('|') || normalized.endsWith('|')) return null;
  
  return normalized.length > 0 ? toTitleCase(normalized) : null;
}
```

### Estimated Effort
- SQL cleanup script: 1 hour (write, test on sample, run)
- Parser fix: 2 hours
- Normalizer fix: 1 hour
- Testing: 1 hour
- **Total: 5 hours**

### Dependencies
None — can start immediately. The SQL cleanup is independent of the parser fix.

### Verification
```sql
-- After cleanup:
SELECT brand, COUNT(*) FROM products 
WHERE brand IS NOT NULL 
GROUP BY brand ORDER BY COUNT(*) DESC LIMIT 10;
-- Should show real brands (Bountiful Farms, Happy Valley, etc.)
-- "stock. Order soon." should not appear

-- Check garbage count
SELECT COUNT(*) FROM products WHERE brand IN (
  'stock. Order soon.', 'Unknown', '510', 'Flower', 'Gummies'
);
-- Should return 0
```

---

## Fix #4: Geocode All Operators

### Problem
Only **10 of 492 operators** (2%) have lat/lon coordinates. This breaks:
- Geography page (shows 10 dots instead of 500)
- Proximity Radar (non-functional for 98% of operators)
- Delivery Voronoi zones (10 points)
- Competitor distance calculations
- Threat scoring based on proximity
- The entire spatial intelligence layer of the platform

**Evidence:**
```
Total operators: 492
With lat/lon: 10
Missing: 482
```

The 10 geocoded operators are the original seed operators (Pure Oasis, NETA Brookline, etc.).

### Root Cause
The scraper creates operator records from Dutchie/Weedmaps data but only stores city/state — no geocoding step in the pipeline. The intelligence service has a `geocoder.ts` module but it's only used for threat events, not operators.

### Fix

**Part A: Batch Geocoding Script**

Create `src/services/scrape/scripts/geocode-operators.ts`:

```typescript
import { db } from '../db.js';
import { sql } from 'drizzle-orm';

// Option 1: Google Maps Geocoding API (most accurate for business addresses)
// Option 2: OpenCage or Nominatim (free, less accurate for business names)
// Recommended: Google Maps — cost is ~$5/thousand requests → 482 requests = ~$2.50

const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;

interface GeocodeResult {
  lat: number;
  lon: number;
  formatted_address: string;
}

async function geocodeOperator(name: string, city: string, state: string): Promise<GeocodeResult | null> {
  // Use name + city + state for best results
  const query = encodeURIComponent(`${name}, ${city}, ${state}`);
  const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${query}&key=${GOOGLE_MAPS_API_KEY}`;
  
  const response = await fetch(url);
  const data = await response.json();
  
  if (data.status === 'OK' && data.results.length > 0) {
    const loc = data.results[0].geometry.location;
    return {
      lat: loc.lat,
      lon: loc.lng,
      formatted_address: data.results[0].formatted_address,
    };
  }
  
  // Fallback: try city + state only
  const fallbackQuery = encodeURIComponent(`${city}, ${state}`);
  const fallbackUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${fallbackQuery}&key=${GOOGLE_MAPS_API_KEY}`;
  const fallbackResponse = await fetch(fallbackUrl);
  const fallbackData = await fallbackResponse.json();
  
  if (fallbackData.status === 'OK' && fallbackData.results.length > 0) {
    const loc = fallbackData.results[0].geometry.location;
    return {
      lat: loc.lat,
      lon: loc.lng, 
      formatted_address: fallbackData.results[0].formatted_address,
    };
  }
  
  return null;
}

async function main() {
  const operators = await db.execute(sql`
    SELECT id, name, city, state 
    FROM operators 
    WHERE lat IS NULL AND city IS NOT NULL
    ORDER BY name
  `);
  
  console.log(`Geocoding ${operators.length} operators...`);
  let success = 0;
  let failed = 0;
  
  for (const op of operators as any[]) {
    try {
      const result = await geocodeOperator(op.name, op.city, op.state || 'MA');
      if (result) {
        await db.execute(sql`
          UPDATE operators 
          SET lat = ${result.lat}, lon = ${result.lon}
          WHERE id = ${op.id}::uuid
        `);
        success++;
        console.log(`✓ ${op.name} (${op.city}) → ${result.lat}, ${result.lon}`);
      } else {
        failed++;
        console.log(`✗ ${op.name} (${op.city}) — no result`);
      }
      
      // Rate limit: 50 requests/second for Google Maps
      await new Promise(r => setTimeout(r, 100));
    } catch (error) {
      failed++;
      console.error(`✗ ${op.name}: ${error}`);
    }
  }
  
  console.log(`\nComplete: ${success} geocoded, ${failed} failed`);
}

main();
```

**Part B: Add geocoding to the scrape pipeline**

**File: `src/services/scrape/src/workers/scrape-full.ts`** (or wherever operators are upserted)

After upserting an operator, if lat/lon is null, queue a geocoding job:
```typescript
if (!operator.lat) {
  await geocodeQueue.add('geocode-operator', { 
    operatorId: operator.id, 
    name: operator.name, 
    city: operator.city, 
    state: operator.state 
  });
}
```

### Estimated Effort
- Write batch geocoding script: 2 hours
- Run batch geocode (482 operators, ~10 minutes): 0.5 hours
- Add geocoding to scrape pipeline: 2 hours
- Verify Geography page works: 1 hour
- **Total: 5.5 hours**

### Dependencies
**🔑 Randy needs to provide a Google Maps Geocoding API key** (or confirm use of an existing key). Cost: ~$2.50 for the batch run. The existing `geocoder.ts` in the intelligence service likely already has a key configured — check `process.env.GOOGLE_MAPS_API_KEY`.

Alternative: Use Nominatim (free, no key needed) but less accurate for business names.

### Verification
```sql
-- After geocoding:
SELECT 
  COUNT(*) as total,
  COUNT(lat) as geocoded,
  COUNT(*) - COUNT(lat) as still_missing
FROM operators;
-- Target: 450+ geocoded (some may fail due to bad city names)

-- Check Geography page shows points
-- Check Proximity Radar returns neighbors for a test operator
```

---

## Fix #5: CCC Weekly Sales Nulls

### Problem
The `ccc_weekly_sales` table has **71 rows but ALL value columns are NULL**. The Market page weekly sales chart falls back to `FALLBACK_WEEKLY_SALES` — hardcoded fake numbers showing $28-34M weekly sales.

**Evidence (live DB query):**
```
Total rows: 71
Non-null total_sales: 0
Non-null adult_use_sales: 0
Non-null medical_sales: 0
Non-null transaction_count: 0
Date range: 2020-01-31 to 2025-12-31 (monthly, not weekly)
```

### Root Cause
The CCC ingest run log shows:
```
source: newsletter-data-bridge
status: failed
error: "ON CONFLICT DO UPDATE command cannot affect row a second time"
details: { weekly_sales: 71 }
```

The `newsletter-data-bridge` script created 71 rows with dates but failed to populate the value columns. Looking at the data, the dates are monthly (not weekly despite the table name), suggesting the scraper was pulling from a monthly summary page and storing into the wrong format.

The CCC publishes weekly sales data at https://masscannabiscontrol.com/open-data/data-visualization/ — this data needs to be re-scraped properly.

### Fix

**Option A (Fast — disable and show honest state):**
1. Remove the weekly sales chart from Market.tsx entirely
2. Replace with `<DataPending title="Weekly sales data being imported" />`
3. This takes 30 minutes and stops showing fake data immediately

**Option B (Proper — re-import the data):**
1. Check if the CCC open data portal has a CSV/API endpoint for weekly sales
2. Write a proper import script that populates `total_sales`, `adult_use_sales`, `medical_sales`, `transaction_count`
3. Fix the `newsletter-data-bridge` ON CONFLICT error

**Recommended: Do Option A immediately, then Option B as a follow-up task.**

**For Option A:**

**File: `src/apps/web/src/pages/Market.tsx`**

Replace the weekly sales section (around line 365-380 in the rendered JSX) with:

```tsx
<section className="border-y border-glass-light-muted/20 bg-[#FCFAF8] py-16">
  <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div className="mb-8">
      <div className="section-marker mb-3"><span>Weekly Sales Tracker</span></div>
      <h2 className="font-display text-3xl sm:text-4xl">Massachusetts total cannabis sales</h2>
    </div>
    <div className="rounded-2xl border border-glass-black/10 bg-glass-black p-8 text-center text-white">
      <p className="font-mono text-[11px] uppercase tracking-[0.15em] text-white/60">Data Import In Progress</p>
      <p className="mt-3 font-display text-xl text-white/80">CCC weekly sales data is being re-imported from official sources.</p>
      <p className="mt-2 font-mono text-sm text-white/50">Subscribe to our weekly report for sales updates.</p>
    </div>
  </div>
</section>
```

**For Option B (follow-up):**

Check CCC open data: `https://masscannabiscontrol.com/open-data/` and `https://data.mass.gov/` for cannabis sales datasets.

```sql
-- When real data is available, update existing rows:
UPDATE ccc_weekly_sales 
SET total_sales = $1, adult_use_sales = $2, medical_sales = $3, transaction_count = $4
WHERE week_ending = $5;
```

### Estimated Effort
- Option A (immediate): 1 hour
- Option B (proper import): 4-6 hours (research CCC data source + write import script)
- **Total: 1 hour now + 4-6 hours later**

### Dependencies
None for Option A. Option B depends on finding the CCC data source URL.

### Verification
```sql
-- Option A verification: weekly sales chart should show "Data Import In Progress"
-- Option B verification:
SELECT COUNT(*) FROM ccc_weekly_sales WHERE total_sales IS NOT NULL;
-- Should be 71 (all rows populated)
```

---

## Fix #6: Normalize Categories

### Problem
The products table has mostly consistent categories (`flower`, `preroll`, `vape`, `edible`, `concentrate`), but the CCC cross-reference endpoint maps `pre-roll` differently than the products table stores `preroll`. The normalizer also maps to `pre-roll` (with hyphen) while the DB stores `preroll` (without).

**Evidence:**
```
Products table:     flower (42,235), preroll (21,235), vape (14,521), edible (12,670), concentrate (4,992)
Normalizer mapping: 'pre-roll' → 'pre-roll', 'preroll' → 'pre-roll'  
Cross-ref query:    AND p.category IN ('flower', 'pre-roll', 'vape', 'edible', 'concentrate')
Actual DB values:   'preroll' (no hyphen)
```

This means the cross-reference query's `WHERE p.category IN ('flower', 'pre-roll', ...)` **misses all 21,235 preroll products** because the DB value is `preroll` not `pre-roll`.

### Root Cause
The normalizer in `normalizer.ts` maps to `'pre-roll'` but the data in the DB is stored as `'preroll'`. There's a disconnect between the normalizer's output and what the scraper actually stored (the bulk scrape may have bypassed the normalizer, or the normalizer was changed after the initial scrape).

### Fix

**Part A: Standardize the canonical category values**

Pick one standard form for each category and stick to it. Using the values already in the DB:

```sql
-- If any 'pre-roll' exist, normalize to 'preroll':
UPDATE products SET category = 'preroll' WHERE category = 'pre-roll';
UPDATE products SET category = 'preroll' WHERE LOWER(category) IN ('pre-roll', 'pre-rolls', 'pre roll', 'joint', 'joints');
```

**Part B: Fix the normalizer**

**File: `src/services/scrape/src/normalizer.ts`**

Update the categoryMap to output DB-consistent values:
```typescript
const categoryMap = new Map<string, ProductCategory>([
  ['flower', 'flower'],
  ['bud', 'flower'],
  ['buds', 'flower'],
  ['pre-roll', 'preroll'],   // Changed: was 'pre-roll'
  ['preroll', 'preroll'],    // Changed: was 'pre-roll'
  ['pre roll', 'preroll'],
  ['joint', 'preroll'],
  ['vape', 'vape'],
  ['cartridge', 'vape'],
  ['cart', 'vape'],
  ['concentrate', 'concentrate'],
  ['wax', 'concentrate'],
  ['shatter', 'concentrate'],
  ['edible', 'edible'],
  ['edibles', 'edible'],
  ['tincture', 'tincture'],
  ['topical', 'topical'],
]);
```

**Part C: Fix the cross-reference query**

**File: `src/services/api/src/routes/ccc.ts`**

Change the GLASS CTE filter:
```sql
AND p.category IN ('flower', 'preroll', 'vape', 'edible', 'concentrate')
-- Was: ('flower', 'pre-roll', 'vape', 'edible', 'concentrate')
```

Also fix the CCC mapping in `mapped_ccc` to output `preroll`:
```sql
WHEN LOWER(category) LIKE '%pre-roll%' OR LOWER(category) LIKE '%pre rolls%' THEN 'preroll'
```

### Estimated Effort
- SQL migration: 0.5 hours
- Normalizer fix: 0.5 hours
- API query fixes: 1 hour (audit all endpoints that reference categories)
- **Total: 2 hours**

### Dependencies
None.

### Verification
```sql
SELECT DISTINCT category FROM products ORDER BY category;
-- Should return: concentrate, edible, flower, preroll, tincture, topical, vape
-- No 'pre-roll' with hyphen

-- Cross-reference should now include preroll category
SELECT * FROM (/* cross-reference query */) WHERE category = 'Preroll';
-- Should return data
```

---

## Fix #7: Surface Plant Activity Data

### Problem
The `ccc_plant_activity` table has **46,863 records** of actual CCC-reported transaction volume data spanning Nov 2018 to Dec 2025 — and it's NOT surfaced ANYWHERE in the frontend. This is real supply-side intelligence showing retail and delivery transaction volumes by category.

**Evidence (DB structure):**
```
Columns: id, report_date, metric_name, metric_value, source, created_at
Unique dates: 2,552
Date range: 2018-11-20 to 2025-12-21
Sample metric_names:
  - "Retail | Retail | Buds" → 176 units
  - "Retail | Retail | Raw Pre-Rolls" → 633,989 units
  - "Delivery and MBs | Delivery Operators | Vape Product" → 6,974 units
```

The `metric_name` follows a pattern: `{Channel} | {Operator Type} | {Product Category}`.

### Root Cause
The data was imported by the `newsletter-data-bridge` (46,863 records) but no API endpoint or frontend component was built to surface it.

### Fix

**Part A: New API Endpoint**

**File: `src/services/api/src/routes/ccc.ts`** — Add new endpoint:

```typescript
fastify.get('/ccc/plant-activity', {
  schema: {
    querystring: Type.Partial(Type.Object({
      channel: Type.String(), // 'retail' | 'delivery' | 'all'
      days: Type.Integer({ minimum: 30, maximum: 2600, default: 365 }),
    })),
  },
}, async (request, reply) => {
  const { channel, days } = request.query as { channel?: string; days?: number };
  const lookback = Math.min(2600, Math.max(30, Number(days || 365)));
  
  const channelFilter = channel === 'retail' 
    ? "AND metric_name LIKE 'Retail%'"
    : channel === 'delivery'
    ? "AND metric_name LIKE 'Delivery%'"
    : '';

  const rows = await db.execute(sql`
    WITH parsed AS (
      SELECT
        report_date,
        metric_name,
        metric_value,
        -- Parse the pipe-separated metric_name
        SPLIT_PART(metric_name, ' | ', 1) AS channel,
        SPLIT_PART(metric_name, ' | ', 2) AS operator_type,
        SPLIT_PART(metric_name, ' | ', 3) AS product_category
      FROM ccc_plant_activity
      WHERE report_date >= CURRENT_DATE - (${lookback} * INTERVAL '1 day')
        AND metric_value IS NOT NULL
        ${channel === 'retail' ? sql`AND metric_name LIKE 'Retail%'` : 
          channel === 'delivery' ? sql`AND metric_name LIKE 'Delivery%'` : sql``}
    )
    SELECT
      product_category AS category,
      channel,
      ROUND(SUM(metric_value)::numeric, 0)::float8 AS total_volume,
      ROUND(AVG(metric_value)::numeric, 2)::float8 AS avg_weekly_volume,
      COUNT(DISTINCT report_date)::int AS data_points,
      MIN(report_date)::text AS earliest_date,
      MAX(report_date)::text AS latest_date
    FROM parsed
    WHERE product_category IS NOT NULL AND product_category != ''
    GROUP BY product_category, channel
    ORDER BY total_volume DESC
    LIMIT 50
  `);

  return reply.send({ data: rows });
});

// Also add a time-series endpoint for trending
fastify.get('/ccc/plant-activity-trend', {
  schema: {
    querystring: Type.Partial(Type.Object({
      category: Type.String(),
      days: Type.Integer({ minimum: 30, maximum: 2600, default: 365 }),
    })),
  },
}, async (request, reply) => {
  const { category, days } = request.query as { category?: string; days?: number };
  const lookback = Math.min(2600, Math.max(30, Number(days || 365)));

  const rows = await db.execute(sql`
    SELECT
      DATE_TRUNC('month', report_date)::date::text AS month,
      SPLIT_PART(metric_name, ' | ', 3) AS category,
      ROUND(SUM(metric_value)::numeric, 0)::float8 AS volume
    FROM ccc_plant_activity
    WHERE report_date >= CURRENT_DATE - (${lookback} * INTERVAL '1 day')
      AND metric_value IS NOT NULL
      ${category ? sql`AND metric_name LIKE ${'%' + category + '%'}` : sql``}
    GROUP BY DATE_TRUNC('month', report_date), SPLIT_PART(metric_name, ' | ', 3)
    ORDER BY month ASC, volume DESC
  `);

  return reply.send({ data: rows });
});
```

**Part B: Morning Brief Component**

Add a "Category Volume Intelligence" card to MorningBrief showing:
- Bar chart: Transaction volumes by category (Retail channel)
- Highlight: Top 3 categories by volume
- Trend: MoM volume changes

This should be a new viz component `<PlantActivityChart />` that fetches from `/ccc/plant-activity`.

### Estimated Effort
- API endpoints: 2 hours
- Frontend component: 3 hours
- Integration into MorningBrief: 1 hour
- **Total: 6 hours**

### Dependencies
None — data already exists in DB.

### Verification
```bash
curl /ccc/plant-activity | jq '.data | length'
# Should return 30-50 rows

curl /ccc/plant-activity-trend?days=365 | jq '.data[:3]'
# Should return monthly volume data
```

---

## Fix #8: Connect Pending Applications to Threats

### Problem
234 real CCC pending applications are not feeding the threat system. The Threat Radar shows 6 hand-crafted threats while 234 real pending license applications sit unused in `ccc_pending_applications`. The license pipeline visualization in `viz.ts` uses the `threats` table (6 rows) instead of `ccc_pending_applications` (234 rows).

### Root Cause
The `ccc-ingest.ts` worker fetches applications and extracts threats, but it requires the CCC API to be reachable (needs `CCC_APP_TOKEN`). The 234 existing applications were imported via the `newsletter-data-bridge` (a separate ingest path) and never connected to the threat pipeline.

The `license-pipeline` endpoint in `viz.ts` queries the `threats` table instead of `ccc_pending_applications`:
```sql
SELECT 'Submitted'::text AS stage, COUNT(*)::int FROM threats WHERE type IN ('new_license', 'competitor_opening')
```

### Fix

**Part A: Fix the License Pipeline Endpoint**

**File: `src/services/api/src/routes/viz.ts`** — Replace the license-pipeline query:

```sql
-- Replace the existing license-pipeline UNION ALL query with:
SELECT stage, count FROM (
  SELECT 'Pending Applications'::text AS stage, COUNT(*)::int AS count 
  FROM ccc_pending_applications WHERE status IS DISTINCT FROM 'approved'
  UNION ALL
  SELECT license_type AS stage, COUNT(*)::int AS count
  FROM ccc_pending_applications
  GROUP BY license_type
) t
ORDER BY count DESC
```

**Part B: Create a Threat Generation Job**

Add a function that converts pending applications into threat entries (for operators in the same city):

```typescript
// src/services/intelligence/src/workers/application-threat-sync.ts
async function syncApplicationsToThreats() {
  const db = getDb();
  
  // Get pending applications with cities that match operator cities
  const pendingApps = await db.execute(sql`
    SELECT 
      pa.id,
      pa.applicant_name,
      pa.license_type,
      pa.city,
      pa.application_date,
      COUNT(o.id) as operators_in_city
    FROM ccc_pending_applications pa
    LEFT JOIN operators o ON LOWER(o.city) = LOWER(pa.city)
    WHERE pa.city IS NOT NULL AND pa.city != ''
    GROUP BY pa.id, pa.applicant_name, pa.license_type, pa.city, pa.application_date
    HAVING COUNT(o.id) > 0
  `);
  
  for (const app of pendingApps) {
    // Insert as threat if not already present
    await db.insert(threats).values({
      type: 'new_license',
      severity: app.operators_in_city > 20 ? 'low' : 'medium', // High-density cities = lower individual impact
      entity_name: app.applicant_name,
      description: `New ${app.license_type} application filed in ${app.city}. ${app.operators_in_city} existing operators in this city.`,
      source_system: 'ccc_pending_applications',
      published_at: app.application_date,
      metadata: { license_type: app.license_type, city: app.city },
    }).onConflictDoNothing();
  }
}
```

**Part C: Add a City-Based Threat Summary Endpoint**

```typescript
// New endpoint in ccc.ts
fastify.get('/ccc/competition-density', {}, async (_request, reply) => {
  const rows = await db.execute(sql`
    SELECT 
      COALESCE(o.city, pa.city) AS city,
      COUNT(DISTINCT o.id)::int AS existing_operators,
      COUNT(DISTINCT pa.id)::int AS pending_applications,
      CASE 
        WHEN COUNT(DISTINCT o.id) > 0 
        THEN ROUND((COUNT(DISTINCT pa.id)::numeric / COUNT(DISTINCT o.id)::numeric) * 100, 1)::float8
        ELSE 0
      END AS growth_pct
    FROM operators o
    FULL OUTER JOIN ccc_pending_applications pa 
      ON LOWER(o.city) = LOWER(pa.city)
    WHERE COALESCE(o.city, pa.city) IS NOT NULL
    GROUP BY COALESCE(o.city, pa.city)
    HAVING COUNT(DISTINCT pa.id) > 0
    ORDER BY pending_applications DESC
    LIMIT 30
  `);
  
  return reply.send({ data: rows });
});
```

### Estimated Effort
- Fix license-pipeline endpoint: 1 hour
- Application-to-threat sync: 3 hours
- Competition density endpoint: 1 hour
- **Total: 5 hours**

### Dependencies
Fix #4 (Geocode Operators) would make this even more powerful by enabling distance-based threat matching instead of city-name matching.

### Verification
```sql
-- License pipeline should show real data:
SELECT license_type, COUNT(*) FROM ccc_pending_applications GROUP BY license_type ORDER BY COUNT(*) DESC;
-- Should show Marijuana Retailer, Marijuana Courier, etc.

-- Competition density should return meaningful data:
-- Boston: 77 existing, 17+ pending
-- Holyoke: many pending
```

---

## Fix #9: Daily Scraping Architecture

### Problem
99.9% of price data is from a single day (Feb 12, 2026). The scraper infrastructure exists but has only successfully completed one bulk scrape. Without daily data, every time-series visualization (WoW trends, price movers, volatility, sparklines) is fiction.

**Evidence:**
```
Feb 5-11:  15-20 rows/day (seed data from test operators)
Feb 12:    110,016 rows (first real bulk scrape)
Total:     110,133 prices across 8 days
```

The scrape infrastructure already exists:
- `scheduler.ts`: Cron jobs defined — full scrape every 6 hours, delta every hour
- `scrape-full.ts` / `scrape-delta.ts`: Worker implementations exist
- `scrape_runs` table: 10 runs logged, 1 successful bulk (57,514 prices from 195 Dutchie stores)
- Queue system: BullMQ with Redis

### Root Cause
The scheduler is configured but likely not running as a persistent service. The scrape runs show the full scrape taking **5+ hours** (18,599 seconds) for 195 Dutchie stores — this suggests sequential processing. One Weedmaps run succeeded (760 prices) but another is stuck in "running" status.

### Fix

**Part A: Verify and stabilize the existing scraper**

1. Check if the scraper service is deployed and running:
   ```bash
   # Check Railway deployment status
   # Is the scrape service running? Does it have Redis access?
   ```

2. Fix the stuck Weedmaps run:
   ```sql
   UPDATE scrape_runs SET status = 'failed', completed_at = NOW() 
   WHERE id = '3894a123-61de-40b0-8715-eea731d00f2b' AND status = 'running';
   ```

3. Optimize scrape speed:
   - Increase concurrency (currently processing stores sequentially)
   - Target: 195 Dutchie stores in < 2 hours instead of 5
   - Add Weedmaps stores (282 operators) to the scrape rotation

**Part B: Schedule configuration**

The existing scheduler.ts is well-designed. Recommended cadence:

```
Full scrape:  0 4 * * *    (4 AM ET daily — captures overnight price changes)
Delta scrape: 0 */4 * * *  (every 4 hours — catches intra-day changes)
```

Reduce from current every-6-hours to daily for full, every-4-hours for delta. This balances data freshness with system load.

**Part C: Railway deployment checklist** (Randy needs to verify)

- [ ] Scrape service is deployed as a Railway service
- [ ] Redis instance is accessible from scrape service
- [ ] Environment variables set: `REDIS_URL`, `DATABASE_URL`, `FULL_SCRAPE_CRON`, `DELTA_SCRAPE_CRON`
- [ ] Service has enough memory/CPU for concurrent scraping (recommend 1GB+ RAM)
- [ ] Error alerts configured (Railway logs or external monitoring)

**Part D: Monitoring endpoint**

Add to the API:
```typescript
fastify.get('/viz/scrape-health', {}, async (_request, reply) => {
  const rows = await db.execute(sql`
    SELECT 
      platform,
      status,
      started_at::text,
      completed_at::text,
      stores_attempted,
      stores_succeeded,
      prices_inserted,
      duration_seconds
    FROM scrape_runs
    ORDER BY started_at DESC
    LIMIT 10
  `);
  
  const latestComplete = await db.execute(sql`
    SELECT MAX(completed_at) as last_complete,
           EXTRACT(EPOCH FROM (NOW() - MAX(completed_at)))/3600 as hours_since
    FROM scrape_runs WHERE status = 'completed'
  `);
  
  return reply.send({ runs: rows, health: latestComplete[0] });
});
```

### Estimated Effort
- Verify and fix existing deployment: 2 hours (Randy involved)
- Optimize scrape concurrency: 3 hours
- Monitoring endpoint: 1 hour
- **Total: 6 hours**

### Dependencies
- **Randy needs to confirm**: Railway deployment status of the scrape service
- Redis must be accessible
- After 7 days of daily scraping, all time-series features become real

### Verification
```sql
-- After 2 days of operation:
SELECT DATE(scraped_at), COUNT(*) FROM prices 
GROUP BY DATE(scraped_at) ORDER BY DATE(scraped_at) DESC LIMIT 5;
-- Should show ~100K+ rows per day for the last 2+ days

-- Scrape health check:
SELECT * FROM scrape_runs WHERE status = 'completed' ORDER BY started_at DESC LIMIT 3;
-- Should show recent successful runs
```

---

## Fix #10: Price History Schema

### Problem
There's no efficient way to track price changes over time. The current `prices` table stores every price observation, which will grow rapidly with daily scraping (~110K rows/day = 40M rows/year). Time-series queries use `LAG()` over the entire table, which will become slow.

### Root Cause
The schema was designed for single-snapshot analysis, not longitudinal tracking. There's no price history summary table, no aggregation layer, and no efficient way to query "what was the price of product X last week?"

### Fix

**Part A: Price History Summary Table**

```sql
-- Create a daily price summary table for efficient time-series queries
CREATE TABLE price_daily_summary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id),
  operator_id UUID NOT NULL REFERENCES operators(id),
  date DATE NOT NULL,
  min_price NUMERIC(10,2) NOT NULL,
  max_price NUMERIC(10,2) NOT NULL,
  avg_price NUMERIC(10,2) NOT NULL,
  price_per_gram NUMERIC(10,2),
  observation_count INT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(product_id, operator_id, date)
);

-- Index for common queries
CREATE INDEX idx_pds_date ON price_daily_summary(date);
CREATE INDEX idx_pds_operator_date ON price_daily_summary(operator_id, date);
CREATE INDEX idx_pds_product_date ON price_daily_summary(product_id, date);

-- Create a category-level daily summary for market-wide trends
CREATE TABLE market_daily_summary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category VARCHAR NOT NULL,
  city VARCHAR,
  date DATE NOT NULL,
  avg_price NUMERIC(10,2) NOT NULL,
  median_price NUMERIC(10,2),
  min_price NUMERIC(10,2),
  max_price NUMERIC(10,2),
  avg_price_per_gram NUMERIC(10,2),
  product_count INT NOT NULL,
  operator_count INT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(category, city, date)
);

CREATE INDEX idx_mds_category_date ON market_daily_summary(category, date);
```

**Part B: Nightly Aggregation Job**

Run after each full scrape completes:

```sql
-- Aggregate today's prices into daily summary
INSERT INTO price_daily_summary (product_id, operator_id, date, min_price, max_price, avg_price, price_per_gram, observation_count)
SELECT 
  product_id,
  operator_id,
  DATE(scraped_at) as date,
  MIN(price::numeric) as min_price,
  MAX(price::numeric) as max_price,
  ROUND(AVG(price::numeric), 2) as avg_price,
  ROUND(AVG(price_per_gram), 2) as price_per_gram,
  COUNT(*) as observation_count
FROM prices
WHERE DATE(scraped_at) = CURRENT_DATE
GROUP BY product_id, operator_id, DATE(scraped_at)
ON CONFLICT (product_id, operator_id, date) 
DO UPDATE SET 
  min_price = LEAST(price_daily_summary.min_price, EXCLUDED.min_price),
  max_price = GREATEST(price_daily_summary.max_price, EXCLUDED.max_price),
  avg_price = EXCLUDED.avg_price,
  price_per_gram = EXCLUDED.price_per_gram,
  observation_count = EXCLUDED.observation_count;

-- Aggregate into market-level summary
INSERT INTO market_daily_summary (category, city, date, avg_price, median_price, min_price, max_price, avg_price_per_gram, product_count, operator_count)
SELECT
  p.category,
  o.city,
  DATE(pr.scraped_at) as date,
  ROUND(AVG(pr.price::numeric), 2),
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pr.price::numeric), 2),
  MIN(pr.price::numeric),
  MAX(pr.price::numeric),
  ROUND(AVG(pr.price_per_gram), 2),
  COUNT(DISTINCT pr.product_id),
  COUNT(DISTINCT pr.operator_id)
FROM prices pr
JOIN products p ON p.id = pr.product_id
JOIN operators o ON o.id = pr.operator_id
WHERE DATE(pr.scraped_at) = CURRENT_DATE
  AND p.category IS NOT NULL
GROUP BY p.category, o.city, DATE(pr.scraped_at)
ON CONFLICT (category, city, date) DO UPDATE SET
  avg_price = EXCLUDED.avg_price,
  median_price = EXCLUDED.median_price,
  min_price = EXCLUDED.min_price,
  max_price = EXCLUDED.max_price,
  avg_price_per_gram = EXCLUDED.avg_price_per_gram,
  product_count = EXCLUDED.product_count,
  operator_count = EXCLUDED.operator_count;
```

**Part C: Backfill from existing data**

```sql
-- Backfill the Feb 12 data into the summary tables
-- (Same query as above but with WHERE DATE(scraped_at) = '2026-02-12')
```

**Part D: Update API endpoints to use summary tables**

Once summary tables are populated, update these endpoints to use them:
- `/viz/price-volatility` → query `market_daily_summary` instead of raw prices
- `/viz/price-cascade` → query `price_daily_summary` with LAG()
- `/viz/price-ticker` → query `price_daily_summary`
- `/viz/economic-indicators` → query `market_daily_summary`

**Part E: Real sparklines from summary data**

```typescript
// New endpoint for real sparklines
fastify.get('/viz/sparkline/:productId', {}, async (request, reply) => {
  const { productId } = request.params;
  const rows = await db.execute(sql`
    SELECT date::text, avg_price::float8 as value
    FROM price_daily_summary
    WHERE product_id = ${productId}::uuid
    ORDER BY date ASC
    LIMIT 30
  `);
  return reply.send({ data: rows });
});
```

### Estimated Effort
- Schema creation + backfill: 2 hours
- Aggregation job: 2 hours
- API endpoint updates: 3 hours
- **Total: 7 hours**

### Dependencies
- Fix #9 (Daily Scraping) must be operational for this to accumulate meaningful data
- Can create the schema and backfill Feb 12 data immediately

### Verification
```sql
-- After schema creation and backfill:
SELECT date, COUNT(*) FROM price_daily_summary GROUP BY date ORDER BY date;
-- Should show at least 1 date with data

-- After 7 days:
SELECT date, avg_price FROM market_daily_summary 
WHERE category = 'flower' AND city IS NULL
ORDER BY date;
-- Should show 7+ rows with daily averages
```

---

## Summary: Effort & Ownership

| Fix # | Title | Hours | Agent-Doable? | Randy Required? |
|-------|-------|-------|---------------|-----------------|
| 1 | CCC Cross-Reference | 3 | ✅ Yes | No |
| 2 | Kill Fake Fallbacks | 11 | ✅ Yes | No |
| 3 | Brand Parsing Bug | 5 | ✅ Yes | No |
| 4 | Geocode Operators | 5.5 | ⚠️ Mostly | API key needed |
| 5 | CCC Weekly Sales | 1+5 | ✅ Yes (Option A) | CCC data source for Option B |
| 6 | Normalize Categories | 2 | ✅ Yes | No |
| 7 | Surface Plant Activity | 6 | ✅ Yes | No |
| 8 | Pending Apps → Threats | 5 | ✅ Yes | No |
| 9 | Daily Scraping | 6 | ⚠️ Partially | Railway deployment verification |
| 10 | Price History Schema | 7 | ✅ Yes | No |
| | **Total** | **~52 hours** | | |

### What Randy Needs To Do
1. **Provide Google Maps Geocoding API key** (or confirm existing key) — needed for Fix #4
2. **Verify Railway deployment** of scrape service — needed for Fix #9
3. **Confirm the CCC data source URL** for weekly sales — needed for Fix #5 Option B
4. **Review and approve** the tech plan before agents start executing

### What Agents Can Do Autonomously (No Randy Required)
- Fix #1: CCC cross-reference query rewrite
- Fix #2: Frontend fallback removal (all pages)
- Fix #3: SQL cleanup + parser/normalizer fixes
- Fix #5 Option A: Replace weekly sales with honest empty state
- Fix #6: Category normalization migration
- Fix #7: Plant activity API + UI
- Fix #8: Pending applications → threat pipeline
- Fix #10: Schema creation + aggregation job

### Estimated Timeline (With Parallel Execution)

| Day | Lane A | Lane B | Lane C |
|-----|--------|--------|--------|
| 1 | Fix #1 (3h) + Fix #5A (1h) + Fix #6 (2h) | Fix #2 Market.tsx (3h) + MorningBrief (2h) | Fix #3 SQL + Parser (5h) |
| 2 | Fix #4 (5.5h) — needs API key | Fix #2 remaining pages (5h) | Fix #7 (6h) |
| 3 | Fix #8 (5h) | Fix #10 (7h) | Fix #9 (6h) — needs Randy |

**P0 fixes complete by end of Day 2. Full plan complete by end of Day 3.**

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cross-reference fix reveals other CCC unit issues | Medium | Medium | Test all 5 categories individually |
| Removing fallbacks causes blank pages | Low | High | Test each page with API disabled |
| Brand cleanup removes legitimate brands | Low | Medium | Review the SQL UPDATE with `SELECT` first |
| Geocoding API costs more than expected | Low | Low | Cap at 500 requests ($2.50) |
| Scraper deployment issues on Railway | Medium | High | Randy needs to verify infrastructure |
| Summary table aggregation misses edge cases | Low | Medium | Verify with known product price checks |

---

## Success Criteria

After all fixes are implemented:

1. ✅ No page shows fake/fabricated data — every number comes from the DB
2. ✅ Cross-reference shows unit-matched comparisons with clear labels
3. ✅ Brand Treemap shows real brands, not "stock. Order soon."
4. ✅ 450+ operators have lat/lon (Geography page is functional)
5. ✅ Plant activity data is visible in the UI
6. ✅ Pending applications feed the threat system
7. ✅ Daily scraping is operational and monitored
8. ✅ Price history schema exists and accumulates data
9. ✅ After 7 days of scraping, sparklines show real trends
10. ✅ An informed operator can inspect any number on the platform and find it trustworthy
