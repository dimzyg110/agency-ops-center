# GLASS Weedmaps Scraper — Implementation Plan

_Second data source for GLASS price intelligence. Builds on proven Dutchie pipeline patterns._

---

## Executive Summary

Weedmaps is the second scraping target for GLASS. Unlike Dutchie (which uses DOM evaluation), Weedmaps data is best extracted from **CamoFox accessibility snapshots** — the product data is richly structured in `listitem` blocks with category tags, THC%, brand, price, and weight all in predictable text patterns.

**Key differences from Dutchie:**
- Products are on the **dispensary page itself** (not a separate `/products/` path)
- Category navigation: `/dispensaries/{slug}/{category}` (not `/products/{category}`)
- **Pagination** via `?page=N` (Dutchie used infinite scroll)
- Product text format is **more structured** — category tag, brand, THC%, rating all inline
- Age gate text differs: "Yes, let me in!" vs Dutchie's "Yes"
- Store metadata is richer: license, hours, rec/med designation, amenities

**Reusable from Dutchie pipeline:** `browser-pool.ts`, `db.ts`, `normalizer.ts` (with additions), `types.ts` (with extensions), config patterns, orchestrator structure.

**New files needed:** `weedmaps-parser.ts`, `scrape-weedmaps.ts`, `weedmaps-slugs.json`.

---

## 1. Discovery Phase — Collecting MA Dispensary Slugs

### Strategy: Two-Pass Discovery

**Pass 1: State page footer scan**
The MA state page (`/dispensaries/in/united-states/massachusetts`) contains a comprehensive city list in the footer under "Massachusetts Dispensary Maps". This is the most reliable source.

```
URL: https://weedmaps.com/dispensaries/in/united-states/massachusetts
Footer section: "Massachusetts Dispensary Maps"
City links: /dispensaries/in/united-states/massachusetts/{city}
```

**Pass 2: Per-city dispensary extraction**
Each city page lists dispensaries with links like `/dispensaries/{slug}`. Extract all unique slugs.

### Discovery Implementation

```typescript
// In scrape-weedmaps.ts — discovery section

const WM_STATE_URL = 'https://weedmaps.com/dispensaries/in/united-states/massachusetts';

async function discoverWeedmapsCities(pool: BrowserPool): Promise<string[]> {
  const tabId = await pool.createTab(WM_STATE_URL);
  await pool.sleep(3000);
  
  // Handle age gate
  await handleWeedmapsAgeGate(pool, tabId);
  await pool.sleep(2000);

  // Scroll to footer to ensure city links are loaded
  for (let i = 0; i < 5; i++) {
    await pool.scroll(tabId, 'down', 3000);
    await pool.sleep(800);
  }
  
  const snapshot = await pool.snapshot(tabId);
  
  // Extract city slugs from footer links
  // Pattern: link "Boston" [eN]: /url: /dispensaries/in/united-states/massachusetts/boston
  const cityRegex = /link "[^"]+" \[e\d+\]:\s*\n\s*-\s*\/url:\s*\/dispensaries\/in\/united-states\/massachusetts\/([a-z0-9-]+)/gi;
  const cities: string[] = [];
  let match;
  while ((match = cityRegex.exec(snapshot)) !== null) {
    const city = match[1];
    if (city && !cities.includes(city)) {
      cities.push(city);
    }
  }
  
  await pool.closeTab(tabId);
  return cities;
}

async function discoverWeedmapsSlugs(pool: BrowserPool, cities: string[]): Promise<SlugRecord[]> {
  const map = new Map<string, SlugRecord>();

  for (let i = 0; i < cities.length; i++) {
    const city = cities[i];
    const cityUrl = `https://weedmaps.com/dispensaries/in/united-states/massachusetts/${city}`;
    let tabId: string | undefined;

    try {
      console.log(`[wm-discover ${i + 1}/${cities.length}] ${city}`);
      tabId = await pool.createTab(cityUrl);
      await pool.sleep(3000);
      await handleWeedmapsAgeGate(pool, tabId);
      await pool.sleep(2000);

      // Scroll to load all dispensary listings
      for (let s = 0; s < 3; s++) {
        await pool.scroll(tabId, 'down', 3000);
        await pool.sleep(800);
      }

      const snapshot = await pool.snapshot(tabId);
      
      // Extract dispensary slugs
      // Pattern: link "Dispensary Name" [eN]: /url: /dispensaries/{slug}
      // Must NOT match /dispensaries/in/ (those are city/state links)
      const slugRegex = /link "[^"]+" \[e\d+\]:\s*\n\s*-\s*\/url:\s*\/dispensaries\/([a-z0-9][a-z0-9-]+[a-z0-9])(?:\s|$)/gi;
      let match;
      while ((match = slugRegex.exec(snapshot)) !== null) {
        const slug = match[1];
        // Filter out navigation/city links
        if (slug.startsWith('in/') || slug.includes('/')) continue;
        
        // Extract name from the link text
        const nameMatch = snapshot.substring(match.index - 200, match.index).match(/link "([^"]+)"/);
        const nameHint = nameMatch ? nameMatch[1] : undefined;

        const existing = map.get(slug);
        if (!existing) {
          map.set(slug, { slug, cities: [city], discoveredFrom: [cityUrl], nameHint });
        } else {
          if (!existing.cities.includes(city)) existing.cities.push(city);
          if (!existing.discoveredFrom.includes(cityUrl)) existing.discoveredFrom.push(cityUrl);
        }
      }

      console.log(`  total unique slugs: ${map.size}`);
    } catch (error) {
      console.warn(`  ! discovery failed for ${city}: ${String(error)}`);
    } finally {
      if (tabId) await pool.closeTab(tabId).catch(() => undefined);
      await pool.sleep(jitter());
    }
  }

  return [...map.values()].sort((a, b) => a.slug.localeCompare(b.slug));
}
```

### Discovery Output

Save to `weedmaps-slugs.json` with the same `SlugRecord` format as Dutchie:

```json
[
  {
    "slug": "diem-cannabis",
    "cities": ["worcester"],
    "discoveredFrom": ["https://weedmaps.com/dispensaries/in/united-states/massachusetts/worcester"],
    "nameHint": "Diem Cannabis"
  }
]
```

**Expected yield:** ~150-250 dispensaries (Weedmaps has broader MA coverage than Dutchie's ~235).

---

## 2. Parser Design — `weedmaps-parser.ts`

### Product Text Format Analysis

From accessibility snapshots, Weedmaps products follow this pattern in `listitem` blocks:

```
- listitem:
  - button "Favorite {product name}" [eN]:
  - link "{product name} product detail page" [eN]:
    - /url: /dispensaries/{slug}/menu/{product-slug}
    - text: {CATEGORY_TAG} {Brand} - {Category} - {Product Name} - {Weight} {THC%} THC {Brand} {rating}
  - text: ${price} {weight_display}
  - button "Add to cart" [eN]
```

**Key insight:** The text line inside the link contains ALL product metadata in a single string. The second text line has price and weight display.

### Parser Architecture

```typescript
// src/scripts/lib/weedmaps-parser.ts

import type { ParsedProduct } from './types';

/**
 * Weedmaps category tags as they appear in product text (uppercase).
 * Maps to our normalized categories.
 */
const WM_CATEGORY_TAGS: Record<string, string> = {
  'FLOWER': 'flower',
  'PRE-ROLL': 'preroll',
  'PRE-ROLLS': 'preroll',
  'INFUSED PRE-ROLL': 'preroll',
  'INFUSED PRE-ROLLS': 'preroll',
  'VAPE PENS': 'vape',
  'VAPE PEN': 'vape',
  'CONCENTRATES': 'concentrate',
  'CONCENTRATE': 'concentrate',
  'EDIBLES': 'edible',
  'EDIBLE': 'edible',
  'DRINKS': 'edible',
  'DRINK': 'edible',
  'WELLNESS': 'tincture',
  'TINCTURE': 'tincture',
  'TINCTURES': 'tincture',
  'TOPICALS': 'topical',
  'TOPICAL': 'topical',
  'ACCESSORIES': 'accessory',
  'GEAR': 'accessory',
};

/**
 * Category tag regex — matches the uppercase tag at the start of product text.
 * Built dynamically from WM_CATEGORY_TAGS keys, longest-first to avoid partial matches.
 */
const CATEGORY_TAG_PATTERN = Object.keys(WM_CATEGORY_TAGS)
  .sort((a, b) => b.length - a.length) // longest first
  .join('|');
const CATEGORY_TAG_REGEX = new RegExp(`^(${CATEGORY_TAG_PATTERN})\\s+`, 'i');

/**
 * Extracts THC percentage from Weedmaps product text.
 * Format: "28.6% THC" or "28.6 % THC"
 */
const THC_REGEX = /(\d+(?:\.\d+)?)\s*%\s*THC/i;

/**
 * Extracts CBD percentage from Weedmaps product text.
 */
const CBD_REGEX = /(\d+(?:\.\d+)?)\s*%\s*CBD/i;

/**
 * Extracts star rating from Weedmaps product text.
 * Format: "5.0 star average rating from 11 reviews"
 */
const RATING_REGEX = /(\d+(?:\.\d+)?)\s*star\s+average\s+rating\s+from\s+(\d+)\s+reviews?/i;

/**
 * Extracts price from the price/weight text line.
 * Format: "$40.00 1/8 oz" or "$25.00 1g" or "$40.00"
 */
const PRICE_REGEX = /\$(\d+(?:\.\d{2})?)/;

/**
 * Extracts weight display from the price/weight text line.
 * Everything after the price value.
 */
const WEIGHT_AFTER_PRICE_REGEX = /\$\d+(?:\.\d{2})?\s+(.+)/;

/**
 * Represents a raw Weedmaps product extracted from a snapshot.
 */
export interface WeedmapsRawProduct {
  /** The text content of the product link (contains category, name, THC, brand, rating) */
  linkText: string;
  /** The URL path to the product detail page */
  href: string;
  /** The price/weight text line (e.g. "$40.00 1/8 oz") */
  priceText: string;
}

/**
 * Parses Weedmaps product text into structured brand, name, and metadata.
 *
 * Text format examples:
 *   "FLOWER Khalifa Kush - Flower - Baby Turtle - 3.5g 28.6% THC Khalifa Kush 5.0 star average rating from 11 reviews"
 *   "PRE-ROLL Leiffa - Pre-Roll - Cherry Pie - 1g 22.1% THC Leiffa"
 *   "EDIBLES Wana - Edible - Blueberry Indica Gummies - 100mg 10mg THC Wana 4.8 star average rating from 5 reviews"
 *
 * The pattern is typically:
 *   {CATEGORY_TAG} {Brand} - {Category} - {Product Name} - {Size} {THC%} THC {Brand(repeat)} {rating?}
 *
 * But sometimes:
 *   {CATEGORY_TAG} {Product Full Name} {THC%} THC {Brand} {rating?}
 */
function parseWeedmapsProductText(text: string): {
  category: string;
  brand: string;
  productName: string;
  fullName: string;
  thcPercent?: number;
  cbdPercent?: number;
  rating?: number;
  reviewCount?: number;
  weight?: string;
} {
  let remaining = text.trim();

  // 1. Extract category tag
  let category = 'flower'; // default
  const catMatch = remaining.match(CATEGORY_TAG_REGEX);
  if (catMatch) {
    category = WM_CATEGORY_TAGS[catMatch[1].toUpperCase()] || 'flower';
    remaining = remaining.slice(catMatch[0].length).trim();
  }

  // 2. Extract and remove rating (at the end)
  let rating: number | undefined;
  let reviewCount: number | undefined;
  const ratingMatch = remaining.match(RATING_REGEX);
  if (ratingMatch) {
    rating = Number(ratingMatch[1]);
    reviewCount = Number(ratingMatch[2]);
    remaining = remaining.replace(RATING_REGEX, '').trim();
  }

  // 3. Extract and remove THC/CBD
  let thcPercent: number | undefined;
  let cbdPercent: number | undefined;
  const thcMatch = remaining.match(THC_REGEX);
  if (thcMatch) {
    thcPercent = Number(thcMatch[1]);
    remaining = remaining.replace(THC_REGEX, '').trim();
  }
  const cbdMatch = remaining.match(CBD_REGEX);
  if (cbdMatch) {
    cbdPercent = Number(cbdMatch[1]);
    remaining = remaining.replace(CBD_REGEX, '').trim();
  }

  // 4. Parse brand and product name from remaining text
  // Pattern A: "Brand - Category - Product Name - Size" (dash-separated, brand repeated at end)
  // Pattern B: "Product Full Name Brand" (brand at end after THC removal)
  
  const fullName = remaining;
  let brand = 'Unknown';
  let productName = remaining;
  let weight: string | undefined;

  // Try Pattern A: dash-separated segments
  // "Khalifa Kush - Flower - Baby Turtle - 3.5g Khalifa Kush"
  const dashParts = remaining.split(/\s+-\s+/).map(s => s.trim()).filter(Boolean);

  if (dashParts.length >= 3) {
    // First segment is brand, last segment may contain size + repeated brand
    brand = dashParts[0];
    
    // Skip segment that matches category name (e.g., "Flower", "Pre-Roll")
    const categoryNames = ['flower', 'pre-roll', 'pre-rolls', 'preroll', 'edible', 'edibles',
      'vape pen', 'vape pens', 'concentrate', 'concentrates', 'drink', 'drinks',
      'tincture', 'tinctures', 'topical', 'topicals', 'wellness', 'infused pre-roll'];
    
    const nameSegments = dashParts.slice(1).filter(seg => 
      !categoryNames.includes(seg.toLowerCase())
    );

    // The last name segment might contain weight and repeated brand
    // e.g., "Baby Turtle - 3.5g Khalifa Kush" → last = "3.5g Khalifa Kush"
    if (nameSegments.length > 0) {
      const lastSeg = nameSegments[nameSegments.length - 1];
      
      // Extract weight from last segment (e.g., "3.5g", "1g", "100mg")
      const weightMatch = lastSeg.match(/(\d+(?:\.\d+)?(?:g|mg|oz|ml))\b/i);
      if (weightMatch) {
        weight = weightMatch[1];
        // Remove weight and anything after it (repeated brand) from the segment
        const beforeWeight = lastSeg.substring(0, weightMatch.index).trim();
        const cleanedLast = beforeWeight || lastSeg.replace(weightMatch[0], '').trim();
        
        // Remove repeated brand name from end
        const brandLower = brand.toLowerCase();
        const cleanedLastLower = cleanedLast.toLowerCase();
        if (cleanedLastLower.endsWith(brandLower)) {
          nameSegments[nameSegments.length - 1] = cleanedLast.slice(0, -brand.length).trim();
        } else {
          nameSegments[nameSegments.length - 1] = cleanedLast;
        }
      } else {
        // No weight found — check if last segment is just the brand repeated
        if (lastSeg.toLowerCase().trim() === brand.toLowerCase().trim()) {
          nameSegments.pop();
        } else {
          // Remove trailing brand name if present
          const brandLower = brand.toLowerCase();
          if (lastSeg.toLowerCase().endsWith(brandLower)) {
            nameSegments[nameSegments.length - 1] = lastSeg.slice(0, -brand.length).trim();
          }
        }
      }

      productName = nameSegments.filter(Boolean).join(' - ').trim() || fullName;
    } else {
      productName = fullName;
    }
  } else if (dashParts.length === 2) {
    // "Brand - Product Name" or "Product - Size"
    brand = dashParts[0];
    productName = dashParts[1];
    
    // Check if productName ends with brand repeated
    if (productName.toLowerCase().endsWith(brand.toLowerCase())) {
      productName = productName.slice(0, -brand.length).trim();
    }
  } else {
    // No dashes — try to find brand as the last capitalized word group before we removed THC
    // This is a fallback; brand may be "Unknown"
    brand = 'Unknown';
    productName = remaining;
  }

  // Clean up any trailing/leading dashes or whitespace
  productName = productName.replace(/^[\s-]+|[\s-]+$/g, '').trim();
  brand = brand.replace(/^[\s-]+|[\s-]+$/g, '').trim();

  return {
    category,
    brand: brand || 'Unknown',
    productName: productName || fullName,
    fullName: text.trim(),
    thcPercent,
    cbdPercent,
    rating,
    reviewCount,
    weight,
  };
}

/**
 * Extracts raw product data from a Weedmaps accessibility snapshot.
 *
 * Products are in `listitem` blocks with this structure:
 * ```
 * - listitem:
 *   - button "Favorite ..." [eN]:
 *   - link "... product detail page" [eN]:
 *     - /url: /dispensaries/{slug}/menu/{product-slug}
 *     - text: {CATEGORY_TAG} {Brand} - {Product} {THC%} THC {Brand} {rating}
 *   - text: ${price} {weight}
 *   - button "Add to cart" [eN]
 * ```
 */
export function extractProductsFromSnapshot(snapshot: string, slug: string): WeedmapsRawProduct[] {
  const products: WeedmapsRawProduct[] = [];
  const lines = snapshot.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Match product links ending in "product detail page"
    const linkMatch = line.match(/^-?\s*link "(.+?product detail page)" \[e\d+\]/i);
    if (!linkMatch) continue;

    // Extract href from following lines
    let href = '';
    let linkText = '';
    for (let j = i + 1; j < Math.min(i + 8, lines.length); j++) {
      const nextLine = lines[j].trim();
      
      const hrefMatch = nextLine.match(/^-?\s*\/url:\s*(.+)/);
      if (hrefMatch) {
        href = hrefMatch[1].trim();
        continue;
      }

      // The text line inside the link contains all product metadata
      const textMatch = nextLine.match(/^-?\s*text:\s*(.+)/);
      if (textMatch && !linkText) {
        linkText = textMatch[1].trim();
        continue;
      }

      // Stop if we hit another element at the same or higher level
      if (nextLine.startsWith('- link') || nextLine.startsWith('- button') || nextLine.startsWith('- listitem')) break;
    }

    // Must be a dispensary menu product URL
    if (!href.includes(`/dispensaries/${slug}/menu/`)) continue;
    if (!linkText) continue;

    // Find the price text line (outside the link, next text element in the listitem)
    let priceText = '';
    for (let j = i + 1; j < Math.min(i + 15, lines.length); j++) {
      const priceLine = lines[j].trim();
      
      // Price text line starts with $ and is at the listitem level (not inside the link)
      const priceMatch = priceLine.match(/^-?\s*text:\s*(\$\d+.*)$/);
      if (priceMatch) {
        priceText = priceMatch[1].trim();
        break;
      }

      // Stop at next listitem
      if (priceLine.startsWith('- listitem')) break;
    }

    products.push({ linkText, href, priceText });
  }

  return products;
}

/**
 * Parses raw Weedmaps products into ParsedProduct format compatible with the normalizer.
 */
export function parseWeedmapsProducts(
  rawProducts: WeedmapsRawProduct[],
  slug: string,
  categoryOverride?: string
): ParsedProduct[] {
  return rawProducts.map((raw) => {
    const parsed = parseWeedmapsProductText(raw.linkText);
    
    // Extract price from the price text line
    const priceMatch = raw.priceText.match(PRICE_REGEX);
    const priceValue = priceMatch ? Number(priceMatch[1]) : undefined;
    const priceText = priceMatch ? `$${priceMatch[1]}` : undefined;

    // Extract weight display from price text line
    const weightDisplayMatch = raw.priceText.match(WEIGHT_AFTER_PRICE_REGEX);
    const weightDisplay = weightDisplayMatch ? weightDisplayMatch[1].trim() : parsed.weight;

    // Use category override if provided (when scraping by category page), else parsed
    const category = categoryOverride || parsed.category;

    return {
      slug,
      operatorName: slug,
      menuUrl: `https://weedmaps.com${raw.href}`,
      category,
      brand: parsed.brand,
      productName: parsed.productName,
      fullName: parsed.fullName,
      size: weightDisplay,
      strain_type: undefined, // Weedmaps doesn't show strain type in list view
      thcPercent: parsed.thcPercent,
      cbdPercent: parsed.cbdPercent,
      priceText,
      priceValue,
      confidence: priceValue ? 0.85 : 0.60,
      brandParseFailed: parsed.brand === 'Unknown',
      href: `https://weedmaps.com${raw.href}`,
      raw: {
        linkText: raw.linkText,
        buttonText: raw.priceText, // Reuse buttonText field for price text
        href: raw.href,
      },
    } satisfies ParsedProduct;
  });
}
```

### Parser Test Fixtures

Create `__fixtures__/weedmaps-diem-flower.txt` with a real snapshot excerpt and expected parse output:

```typescript
// test-weedmaps-parser.ts
import { extractProductsFromSnapshot, parseWeedmapsProducts } from './lib/weedmaps-parser';
import { readFileSync } from 'fs';

const snapshot = readFileSync('__fixtures__/weedmaps-diem-flower.txt', 'utf8');
const raw = extractProductsFromSnapshot(snapshot, 'diem-cannabis');
const parsed = parseWeedmapsProducts(raw, 'diem-cannabis', 'flower');

console.log(`Extracted ${raw.length} raw products, parsed ${parsed.length}`);

// Validate known product
const babyTurtle = parsed.find(p => p.productName.includes('Baby Turtle'));
console.assert(babyTurtle, 'Should find Baby Turtle');
console.assert(babyTurtle?.brand === 'Khalifa Kush', `Brand should be Khalifa Kush, got ${babyTurtle?.brand}`);
console.assert(babyTurtle?.thcPercent === 28.6, `THC should be 28.6, got ${babyTurtle?.thcPercent}`);
console.assert(babyTurtle?.priceValue === 40.00, `Price should be 40.00, got ${babyTurtle?.priceValue}`);
console.assert(babyTurtle?.size === '1/8 oz', `Size should be 1/8 oz, got ${babyTurtle?.size}`);
```

---

## 3. Pagination Strategy

### How Weedmaps Pagination Works

- Default page shows ~24 products
- URL pattern: `/dispensaries/{slug}?page=2`, `/dispensaries/{slug}/flower?page=2`
- Total product count shown: "664 Products"
- Pages numbered sequentially from 1

### Pagination Implementation

```typescript
/**
 * Extracts total product count from snapshot.
 * Looks for text like "664 Products" or "24 Products"
 */
const PRODUCT_COUNT_REGEX = /(\d+)\s+Products?/i;

function extractProductCount(snapshot: string): number | null {
  const match = snapshot.match(PRODUCT_COUNT_REGEX);
  return match ? Number(match[1]) : null;
}

const PRODUCTS_PER_PAGE = 24; // Weedmaps default

/**
 * Calculates total pages needed for a given product count.
 */
function totalPages(productCount: number): number {
  return Math.ceil(productCount / PRODUCTS_PER_PAGE);
}

/**
 * Scrapes all pages of a Weedmaps store/category, handling pagination.
 * Returns all raw products across all pages.
 */
async function scrapeAllPages(
  pool: BrowserPool,
  tabId: string,
  slug: string,
  categoryPath: string, // e.g., 'flower', '' for all
  baseUrl: string
): Promise<{ products: WeedmapsRawProduct[]; totalCount: number; pagesScraped: number }> {
  const allProducts: WeedmapsRawProduct[] = [];
  const seen = new Set<string>(); // dedup by href

  // Page 1 is already loaded (the base URL)
  const firstSnapshot = await pool.snapshot(tabId);
  const firstBatch = extractProductsFromSnapshot(firstSnapshot, slug);
  
  for (const p of firstBatch) {
    if (!seen.has(p.href)) {
      seen.add(p.href);
      allProducts.push(p);
    }
  }

  const totalCount = extractProductCount(firstSnapshot);
  if (!totalCount || totalCount <= PRODUCTS_PER_PAGE) {
    return { products: allProducts, totalCount: totalCount || allProducts.length, pagesScraped: 1 };
  }

  const numPages = totalPages(totalCount);
  const maxPages = Math.min(numPages, 50); // Safety cap at 50 pages (1200 products)

  console.log(`    ${slug}/${categoryPath || 'all'}: ${totalCount} products across ${numPages} pages`);

  for (let page = 2; page <= maxPages; page++) {
    const pageUrl = `${baseUrl}?page=${page}`;
    
    try {
      await pool.navigate(tabId, pageUrl);
      await pool.sleep(2000);

      // Scroll to ensure products load
      await pool.scroll(tabId, 'down', 2000);
      await pool.sleep(800);

      const pageSnapshot = await pool.snapshot(tabId);
      const pageBatch = extractProductsFromSnapshot(pageSnapshot, slug);
      
      let newCount = 0;
      for (const p of pageBatch) {
        if (!seen.has(p.href)) {
          seen.add(p.href);
          allProducts.push(p);
          newCount++;
        }
      }

      // If we got 0 new products, we've likely hit the end
      if (newCount === 0) {
        console.log(`    page ${page}: 0 new products, stopping pagination`);
        break;
      }
    } catch (error) {
      console.warn(`    page ${page} failed: ${String(error)}`);
      // Continue to next page rather than failing entirely
    }

    // Jitter between page loads (lighter than between stores)
    await pool.sleep(jitter(800, 1500));
  }

  return { products: allProducts, totalCount, pagesScraped: Math.min(numPages, maxPages) };
}
```

### Scraping Strategy: Category-First vs All Products

**Option A: Scrape all products page (default view + pagination)**
- Fewer requests (1 base URL + N pages)
- Category comes from product text parsing
- Simpler but less structured

**Option B: Scrape per-category pages**
- Category is known from URL
- Smaller page counts per category
- More total requests but more reliable category assignment

**Recommendation: Option B (per-category)**

Scrape each category page separately. This:
1. Gives us reliable category assignment (not dependent on text parsing)
2. Limits pagination depth per category (most categories have <5 pages)
3. Mirrors our Dutchie approach (per-category navigation)
4. Makes it easy to detect "no products" per category for quality checks

```typescript
const WEEDMAPS_CATEGORIES: Record<string, string> = {
  flower: 'flower',
  preroll: 'pre-roll',
  vape: 'vape-pens',
  concentrate: 'concentrates',
  edible: 'edibles',
  drink: 'drinks',
  tincture: 'wellness',
  accessory: 'accessories',
};
```

---

## 4. Orchestrator Design — `scrape-weedmaps.ts`

### Architecture

Follows the exact same pattern as `scrape-dutchie.ts`:
1. **Discovery** → collect slugs (or load from cache)
2. **Scrape** → per-store, per-category with pagination
3. **Load** → upsert operators, products, prices via `db.ts`

### Key Differences from Dutchie Orchestrator

| Aspect | Dutchie | Weedmaps |
|--------|---------|----------|
| Platform string | `'dutchie'` | `'weedmaps'` |
| Base URL | `dutchie.com/dispensary/{slug}` | `weedmaps.com/dispensaries/{slug}` |
| Category URLs | `/products/{category}` | `/{category}` |
| Pagination | Scroll-based (infinite scroll) | URL-based (`?page=N`) |
| Age gate | "Yes" button | "Yes, let me in!" button |
| Product extraction | DOM evaluate → parse | Snapshot text → regex parse |
| Products per page | Variable (scroll-loaded) | ~24 (paginated) |
| Parser type flag | `'dutchie_v2'` | `'weedmaps_v1'` |

### Age Gate Handler

```typescript
async function handleWeedmapsAgeGate(pool: BrowserPool, tabId: string): Promise<void> {
  try {
    const snap = await pool.snapshot(tabId);
    
    // Weedmaps age gate: button "Yes, let me in!" or similar
    const yesMatch = snap.match(/button "Yes,?\s*let me in!?" \[(e\d+)\]/i)
      || snap.match(/button "[^"]*[Yy]es[^"]*let me in[^"]*" \[(e\d+)\]/i);
    
    if (yesMatch) {
      await pool.click(tabId, yesMatch[1]);
      await pool.sleep(2000);
      console.log('  Weedmaps age gate handled');
      
      // After age gate, there may be a cookie banner — try to dismiss
      const snap2 = await pool.snapshot(tabId);
      const cookieMatch = snap2.match(/button "[^"]*[Aa]ccept[^"]*" \[(e\d+)\]/i)
        || snap2.match(/button "[^"]*[Gg]ot it[^"]*" \[(e\d+)\]/i)
        || snap2.match(/button "[^"]*[Cc]lose[^"]*" \[(e\d+)\]/i);
      if (cookieMatch) {
        await pool.click(tabId, cookieMatch[1]);
        await pool.sleep(500);
      }
    }
  } catch {
    // No age gate present, continue
  }
}
```

### Store Scrape Worker

```typescript
async function scrapeWeedmapsStore(
  pool: BrowserPool,
  task: WorkerTask,
  args: CliArgs,
  runId: string | undefined,
  stats: ScrapeRunStats
): Promise<ScrapeResult> {
  const result: ScrapeResult = { slug: task.slug, products: [], errors: [], durationMs: 0 };
  const storeStarted = Date.now();
  const categorySnapshots: StoreCategorySnapshot[] = [];
  let jobId: string | undefined;
  let brandParseFailures = 0;

  try {
    if (args.db && runId && task.sourceId) {
      jobId = await createScrapeJob(task.sourceId, runId);
    }

    let tabId: string | undefined;

    try {
      // Navigate to store's first category page
      const categoryEntries = Object.entries(WEEDMAPS_CATEGORIES);
      const firstUrl = `https://weedmaps.com/dispensaries/${task.slug}/${categoryEntries[0][1]}`;
      tabId = await pool.createTab(firstUrl);
      await pool.sleep(3000);

      // Handle age gate on first load
      await handleWeedmapsAgeGate(pool, tabId);
      await pool.sleep(2000);

      for (let catIdx = 0; catIdx < categoryEntries.length; catIdx++) {
        const [normalizedCat, categoryPath] = categoryEntries[catIdx];
        const baseUrl = `https://weedmaps.com/dispensaries/${task.slug}/${categoryPath}`;
        const categorySnap: StoreCategorySnapshot = {
          category: normalizedCat,
          categoryPath,
          url: baseUrl,
          rawRows: [],
          parsedCount: 0,
          normalizedCount: 0,
        };

        try {
          // Navigate to category (skip for first since tab was created with that URL)
          if (catIdx > 0) {
            await pool.navigate(tabId, baseUrl);
            await pool.sleep(2000);
          }

          // Scroll down to ensure products load
          await pool.scroll(tabId, 'down', 2000);
          await pool.sleep(DELAYS.scrollWaitMs);

          // Scrape all pages for this category
          const { products: rawProducts, totalCount, pagesScraped } = 
            await scrapeAllPages(pool, tabId, task.slug, categoryPath, baseUrl);

          const parsed = parseWeedmapsProducts(rawProducts, task.slug, normalizedCat);
          brandParseFailures += parsed.filter(p => p.brandParseFailed).length;
          const normalized = parsed.map(normalizeProduct).filter(p => p.price > 0);

          categorySnap.rawRows = rawProducts.map(p => ({
            linkText: p.linkText,
            buttonText: p.priceText,
            href: p.href,
          }));
          categorySnap.parsedCount = parsed.length;
          categorySnap.normalizedCount = normalized.length;

          for (const item of normalized) {
            result.products.push(item.raw);
          }

          // DB writes
          if (args.db && jobId && task.operatorId && task.sourceId) {
            for (const item of normalized) {
              const productId = await upsertProduct(
                item.sku, item.productName, item.brand, item.category,
                item.weightGrams, item.strainType, item.thcPercent, item.cbdPercent
              );
              await insertPrice(
                productId, task.sourceId, task.operatorId,
                item.price, item.pricePerGram, item.weightGrams,
                item.confidence,
                { slug: task.slug, category: normalizedCat, categoryPath, menuUrl: item.menuUrl, raw: item.raw },
                jobId
              );
              stats.pricesInserted += 1;
            }
          }

          console.log(
            `  ${task.slug}/${normalizedCat}: ${parsed.length} products (${pagesScraped} pages, ${totalCount || '?'} total)`
          );
        } catch (error) {
          const msg = `${task.slug}/${normalizedCat} failed: ${String(error)}`;
          result.errors.push(msg);
          categorySnap.error = msg;
        }

        categorySnapshots.push(categorySnap);

        // Jitter between categories
        if (catIdx < categoryEntries.length - 1) {
          await pool.sleep(jitter());
        }
      }
    } finally {
      if (tabId) await pool.closeTab(tabId).catch(() => undefined);
    }

    // Save snapshot + complete job (same pattern as Dutchie)
    // ... (identical job completion logic as scrape-dutchie.ts)

  } catch (error) {
    // ... (identical error handling as scrape-dutchie.ts)
  } finally {
    result.durationMs = Date.now() - storeStarted;
    await pool.ensureHealthy();
    await sleep(jitter());
  }

  return result;
}
```

### CLI Interface

Same flags as Dutchie, with platform-specific defaults:

```bash
# Full run
npx tsx src/scripts/scrape-weedmaps.ts --db

# Discovery only
npx tsx src/scripts/scrape-weedmaps.ts --dry-run

# Test with limit
npx tsx src/scripts/scrape-weedmaps.ts --limit 5

# Skip discovery, use cached slugs
npx tsx src/scripts/scrape-weedmaps.ts --skip-discovery --db

# Resume interrupted run
npx tsx src/scripts/scrape-weedmaps.ts --resume <run-id> --db
```

---

## 5. Data Model Implications

### SKU Generation — Cross-Platform Aware

The current `makeSKU()` prefixes with `DUTCHIE-`. For Weedmaps, we need platform-specific SKUs AND a future cross-platform matching key.

#### Platform-Specific SKU (Phase 1 — what we build now)

```typescript
// In normalizer.ts — add platform-aware SKU generation

export function makeSKU(
  brand: string,
  name: string,
  weightGrams: number | undefined,
  category: string,
  platform: string = 'DUTCHIE'  // NEW: platform parameter with backward-compatible default
): string {
  const key = [
    normalizeBrand(brand),
    name.toLowerCase().replace(/[^a-z0-9 ]/g, '').trim(),
    (weightGrams ?? 0).toFixed(1),
    normalizeCategory(category),
  ].join('|');

  return `${platform}-${crypto.createHash('sha256').update(key).digest('hex').slice(0, 20)}`;
}
```

This means:
- Dutchie product: `DUTCHIE-a3f8c91b2e4d7f6a1c0b`
- Weedmaps same product: `WEEDMAPS-a3f8c91b2e4d7f6a1c0b`

The hash portion will be **identical** for the same `brand|name|weight|category` — this is the bridge for cross-platform dedup.

#### Cross-Platform Canonical SKU (Phase 2 — deferred)

```typescript
// Future: canonical SKU strips platform prefix
export function canonicalSKU(sku: string): string {
  return sku.replace(/^(DUTCHIE|WEEDMAPS)-/, 'GLASS-');
}
```

### Schema Changes Needed

```sql
-- parser_type column in prices already exists; we add 'weedmaps_v1' as a valid value
-- No schema changes needed for prices table

-- Products: no changes — sku already handles platform via prefix

-- Operators: platform + platform_slug already exists from Dutchie migration
-- Weedmaps operators get platform='weedmaps', platform_slug='{slug}'

-- Sources: source_type already accepts 'weedmaps'

-- scrape_runs: platform already accepts 'weedmaps'

-- ADD: Cross-reference table for known store matches (Phase 2)
CREATE TABLE IF NOT EXISTS store_crossref (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dutchie_operator_id UUID REFERENCES operators(id),
  weedmaps_operator_id UUID REFERENCES operators(id),
  match_method VARCHAR(50) NOT NULL, -- 'address', 'name_fuzzy', 'manual'
  confidence DECIMAL(3,2) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(dutchie_operator_id, weedmaps_operator_id)
);

-- ADD: Product cross-reference (Phase 2)
CREATE TABLE IF NOT EXISTS product_crossref (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dutchie_product_id UUID REFERENCES products(id),
  weedmaps_product_id UUID REFERENCES products(id),
  match_method VARCHAR(50) NOT NULL, -- 'sku_hash', 'name_fuzzy', 'manual'
  confidence DECIMAL(3,2) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(dutchie_product_id, weedmaps_product_id)
);
```

### DB Helper Updates

```typescript
// In db.ts — update insertPrice to accept platform-specific parser_type

export async function insertPrice(
  productId: string,
  sourceId: string,
  operatorId: string,
  price: number,
  pricePerGram: number | undefined,
  weightGrams: number | undefined,
  confidence: number,
  rawData: Record<string, unknown>,
  scrapeJobId: string,
  parserType: string = 'dutchie_v2'  // NEW: platform-specific parser type
): Promise<void> {
  const sql = `
    INSERT INTO prices (
      product_id, source_id, operator_id, price, price_per_gram, weight_grams,
      promo_flag, confidence, parser_type, raw_data, scrape_job_id, menu_type, scraped_at
    ) VALUES ($1, $2, $3, $4, $5, $6, false, $7, $8, $9::jsonb, $10, 'rec', NOW())
    ON CONFLICT (product_id, source_id, operator_id, (date(scraped_at AT TIME ZONE 'UTC')))
    DO UPDATE SET
      price = EXCLUDED.price,
      price_per_gram = EXCLUDED.price_per_gram,
      weight_grams = EXCLUDED.weight_grams,
      confidence = EXCLUDED.confidence,
      raw_data = EXCLUDED.raw_data,
      scrape_job_id = EXCLUDED.scrape_job_id,
      parser_type = EXCLUDED.parser_type,
      menu_type = EXCLUDED.menu_type,
      scraped_at = EXCLUDED.scraped_at
  `;
  await pool.query(sql, [
    productId, sourceId, operatorId, price,
    pricePerGram ?? null, weightGrams ?? null,
    confidence, parserType, JSON.stringify(rawData), scrapeJobId,
  ]);
}
```

---

## 6. Overlap & Cross-Reference — Multi-Platform Intelligence

### Store Matching Strategy

Many dispensaries list on both Dutchie and Weedmaps. We need to match them.

**Matching signals (in order of reliability):**

| Signal | Reliability | Implementation |
|--------|------------|----------------|
| Street address | 95%+ | Exact/fuzzy string match on `operators.metadata->address` |
| Phone number | 90%+ | Normalized phone comparison |
| License number | 99%+ | When available (CCC reconciliation, Phase 3) |
| Name similarity | 70-85% | Levenshtein distance on normalized names |
| URL/website | 85%+ | When store websites match across platforms |

**Phase 1 (build now):** Capture store metadata during scraping so matching is possible later.

```typescript
// Extract store info from the Weedmaps dispensary page (before category navigation)
async function extractStoreMetadata(pool: BrowserPool, tabId: string, slug: string): Promise<Record<string, unknown>> {
  const snapshot = await pool.snapshot(tabId);
  
  const metadata: Record<string, unknown> = { weedmaps_slug: slug };

  // Address: typically in a text block near the top
  const addressMatch = snapshot.match(/text:\s*(\d+\s+[A-Za-z0-9 ,.\-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)[^,]*,\s*[A-Z]{2}\s+\d{5})/i);
  if (addressMatch) metadata.address = addressMatch[1].trim();

  // Phone
  const phoneMatch = snapshot.match(/text:\s*\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}/);
  if (phoneMatch) metadata.phone = phoneMatch[0].replace('text:', '').trim();

  // License
  const licenseMatch = snapshot.match(/(?:license|lic)[^:]*:\s*([A-Z0-9-]+)/i);
  if (licenseMatch) metadata.license = licenseMatch[1].trim();

  // Rec vs Med
  const isRec = /recreational/i.test(snapshot);
  const isMed = /medical/i.test(snapshot);
  metadata.menu_types = [];
  if (isRec) (metadata.menu_types as string[]).push('recreational');
  if (isMed) (metadata.menu_types as string[]).push('medical');

  // Rating
  const ratingMatch = snapshot.match(/(\d+(?:\.\d+)?)\s*star.*?(\d+)\s*reviews?/i);
  if (ratingMatch) {
    metadata.rating = Number(ratingMatch[1]);
    metadata.review_count = Number(ratingMatch[2]);
  }

  return metadata;
}
```

**Phase 2 (deferred):** Automated store matching script.

```typescript
// Future: scripts/match-stores.ts
// 1. Load all operators with platform='dutchie' and platform='weedmaps'
// 2. For each pair, compute match score based on address, phone, name
// 3. Insert high-confidence matches into store_crossref
// 4. Flag low-confidence matches for manual review
```

### Product Matching Strategy

Products across platforms can be matched using the **hash portion** of the SKU:

```typescript
// Same brand + name + weight + category → same hash
// DUTCHIE-a3f8c91b2e4d7f6a1c0b → hash = a3f8c91b2e4d7f6a1c0b
// WEEDMAPS-a3f8c91b2e4d7f6a1c0b → hash = a3f8c91b2e4d7f6a1c0b

function skuHash(sku: string): string {
  return sku.replace(/^[A-Z]+-/, '');
}

// Cross-platform product match query:
// SELECT d.sku AS dutchie_sku, w.sku AS weedmaps_sku, d.name, d.brand
// FROM products d
// JOIN products w ON substring(d.sku from '-(.+)$') = substring(w.sku from '-(.+)$')
// WHERE d.sku LIKE 'DUTCHIE-%' AND w.sku LIKE 'WEEDMAPS-%'
```

**Challenges:**
- Brand names may differ across platforms ("Berkshire Roots" vs "Berkshire Roots Inc.")
- Product names may have slight variations
- Weight formats may differ ("3.5g" vs "1/8 oz")

**Mitigation:** The normalizer already handles weight normalization to grams and brand cleanup. As long as these are consistent, the hash will match. For edge cases, Phase 2 fuzzy matching will catch them.

### Cross-Platform Price Comparison Query (Future)

```sql
-- Compare flower prices for same product across platforms
WITH matched_products AS (
  SELECT 
    d.id AS dutchie_id,
    w.id AS weedmaps_id,
    d.name,
    d.brand,
    d.weight_grams
  FROM products d
  JOIN products w 
    ON substring(d.sku from '-(.+)$') = substring(w.sku from '-(.+)$')
  WHERE d.sku LIKE 'DUTCHIE-%' 
    AND w.sku LIKE 'WEEDMAPS-%'
    AND d.category = 'flower'
)
SELECT 
  mp.brand,
  mp.name,
  mp.weight_grams,
  dp.price AS dutchie_price,
  wp.price AS weedmaps_price,
  dp.price - wp.price AS price_diff,
  do2.name AS dutchie_store,
  wo.name AS weedmaps_store
FROM matched_products mp
JOIN prices dp ON dp.product_id = mp.dutchie_id AND dp.scraped_at::date = CURRENT_DATE
JOIN prices wp ON wp.product_id = mp.weedmaps_id AND wp.scraped_at::date = CURRENT_DATE
JOIN operators do2 ON dp.operator_id = do2.id
JOIN operators wo ON wp.operator_id = wo.id
ORDER BY ABS(dp.price - wp.price) DESC;
```

---

## 7. Implementation Timeline

### Phase 1: Weedmaps Scraper MVP (3-4 days)

| Day | Task | Details | Effort |
|-----|------|---------|--------|
| **1** | **Parser + Fixtures** | `weedmaps-parser.ts` with text extraction, brand/name/THC/price parsing. Create 3+ fixture snapshots from real Weedmaps pages. Write `test-weedmaps-parser.ts`. | 4-5h |
| **1** | **Config updates** | Add `WEEDMAPS_CATEGORIES` to `config.ts`. | 30min |
| **2** | **Normalizer update** | Make `makeSKU()` platform-aware (backward compatible). Verify weight normalization handles Weedmaps formats ("1/8 oz", "1g", "100mg"). | 1-2h |
| **2** | **Discovery** | Build city discovery + slug extraction. Test against live Weedmaps. Save to `weedmaps-slugs.json`. | 2-3h |
| **3** | **Orchestrator** | `scrape-weedmaps.ts` — age gate, per-category navigation, pagination, DB writes. Reuse `browser-pool.ts`, `db.ts`. | 4-5h |
| **3** | **Local test** | Run `--limit 5` against 5 stores. Validate products land in DB correctly. | 1-2h |
| **4** | **Full test + tune** | Run `--limit 20`. Fix parser edge cases. Tune jitter/timeouts. Validate quality metrics. | 3-4h |

**Total Phase 1: ~18-24 hours of dev time**

### Phase 2: Cross-Platform Intelligence (Week 2)

| Task | Details | Effort |
|------|---------|--------|
| Store metadata extraction | Extract address/phone/license from Weedmaps store pages | 2-3h |
| `store_crossref` table + matcher | Automated store matching by address/phone | 3-4h |
| Product cross-reference | Match products by SKU hash, populate `product_crossref` | 2-3h |
| Cross-platform price views | SQL views for comparing prices across platforms | 2h |

### Phase 3: Production Hardening (Week 3)

| Task | Details | Effort |
|------|---------|--------|
| Parallel scheduling | Run Dutchie and Weedmaps scrapers back-to-back (or staggered) | 1-2h |
| Drift detection | Alert on product count drops, parse failure rate spikes | 2h |
| Dashboard integration | Surface Weedmaps data in GLASS UI | Varies |

---

## 8. Estimated Runtime & Costs

### Weedmaps Scrape Timing

| Step | Time per store | Notes |
|------|---------------|-------|
| Page load + age gate | 5s | First page only |
| Per category (no pagination) | 4s | Navigate + scroll + snapshot |
| Per pagination page | 3s | Navigate + snapshot |
| Jitter between categories | 2.5s avg | Random 1.5-3.5s |
| Jitter between stores | 2.5s avg | Random 1.5-3.5s |

**Average store (8 categories, ~3 pages avg per category):**
- 5s + (8 × 4s) + (8 × 2 × 3s) + (7 × 2.5s) + 2.5s = 5 + 32 + 48 + 17.5 + 2.5 = **105s/store**

**Full MA run (~200 stores):**
- Serial (CONCURRENCY=1): 200 × 105s = 21,000s ≈ **5.8 hours**
- With CONCURRENCY=2: ~3 hours
- With CONCURRENCY=3: ~2 hours

### Combined Daily Run (Dutchie + Weedmaps)

- Dutchie: ~8-10 hours
- Weedmaps: ~4-6 hours
- **Total: ~12-16 hours** (can overlap with concurrency)

---

## 9. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Weedmaps changes DOM structure | Medium | High | Fixture tests, drift detection, snapshot archival |
| Age gate changes | Low | Medium | Regex flexibility, fallback patterns |
| Rate limiting / IP blocking | Low | High | Jitter, concurrency limits, CamoFox anti-detection |
| Pagination format changes | Low | Medium | Safety cap on pages, dedup by href |
| Brand parsing accuracy | High | Medium | Multiple parse strategies, confidence scoring, review queue |
| Products behind "Load More" | Medium | Medium | Verify pagination covers all products; compare count vs scraped |

---

## 10. File Structure (Final)

```
src/scripts/
├── lib/
│   ├── types.ts                    # (extended with WeedmapsRawProduct)
│   ├── config.ts                   # (add WEEDMAPS_CATEGORIES)
│   ├── db.ts                       # (update insertPrice for parser_type param)
│   ├── browser-pool.ts             # (reused as-is)
│   ├── parser.ts                   # (Dutchie — unchanged)
│   ├── weedmaps-parser.ts          # NEW: Weedmaps snapshot → ParsedProduct
│   ├── normalizer.ts               # (update makeSKU for platform param)
│   └── __fixtures__/
│       ├── pure-oasis-flower.json         # (existing Dutchie)
│       ├── weedmaps-diem-flower.txt       # NEW: Weedmaps snapshot fixture
│       ├── weedmaps-neta-edibles.txt      # NEW: Weedmaps snapshot fixture
│       └── weedmaps-expected-products.json # NEW: Expected parse output
├── scrape-dutchie.ts               # (unchanged)
├── scrape-weedmaps.ts              # NEW: Weedmaps orchestrator
├── test-weedmaps-parser.ts         # NEW: Parser contract tests
├── dutchie-slugs.json              # (existing)
└── weedmaps-slugs.json             # NEW: Cached Weedmaps slugs
```

---

## 11. Acceptance Criteria (Phase 1)

- [ ] Parser extracts products from 3+ Weedmaps fixture snapshots correctly
- [ ] Brand, THC%, price, weight parsed with >80% accuracy
- [ ] Discovery finds 100+ MA dispensary slugs
- [ ] Pagination works for stores with >24 products (tested on Diem Cannabis: 664 products)
- [ ] 5-store local test run completes with >80% store success rate
- [ ] Products + prices land in DB with correct FKs and `parser_type='weedmaps_v1'`
- [ ] Scrape run + scrape job records created with accurate counts
- [ ] Price-per-gram computed correctly for flower/preroll/concentrate
- [ ] Raw snapshots saved per store per day
- [ ] Resume works: re-run skips already-scraped stores from today
- [ ] SKU format: `WEEDMAPS-{hash}` with same hash logic as Dutchie
- [ ] No regressions in Dutchie scraper (makeSKU backward compatible)
