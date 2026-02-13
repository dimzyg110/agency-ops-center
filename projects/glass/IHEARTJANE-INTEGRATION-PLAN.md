# iHeartJane Integration Plan for GLASS

**Date:** February 13, 2026  
**Author:** Opus Subagent (Research & Architecture)  
**Status:** Ready for Implementation  
**Target Implementer:** GPT 5.3 Codex

---

## Executive Summary

iHeartJane (Jane Technologies) powers embedded e-commerce menus for cannabis dispensaries. Unlike Dutchie and Weedmaps which require browser-based scraping, **Jane's product data is accessible via Algolia search indices** — a structured, fast, JSON-based approach that eliminates the need for CamoFox/browser automation entirely.

### Key Discovery: Algolia is the Primary Data Layer

Jane uses Algolia for all menu/product search. The Algolia indices are:
- **`stores-production`** — All stores with location, hours, product counts
- **`menu-products-production`** — All products with prices, potency, brand, category

Both indices support server-side querying with an API key embedded in the Jane frontend JavaScript. **No browser needed.** This is a pure HTTP/JSON scraper.

### Coverage Estimate
- **50–80 NEW Massachusetts dispensaries** not currently on Dutchie or Weedmaps
- Moves GLASS from ~92% to ~100% coverage of all active MA retailers
- Adds ~3,000–6,000 new daily product/price records

---

## Part 1: API Architecture

### 1.1 Two Data Access Methods

| Method | Index Names | Auth | Rate Limits | Best For |
|--------|------------|------|------------|---------|
| **Algolia** (RECOMMENDED) | `stores-production`, `menu-products-production` | Public API key (embedded in Jane frontend JS) | Very high (Algolia SLA) | Store discovery + product/price scraping |
| **REST API** | `api.iheartjane.com/v1/stores/{id}/products` | OAuth2 client_id/secret (per-store) | Lower, Cloudflare protected | Supplementary data (orders, reviews, specials) |

**Recommendation: Use Algolia exclusively.** The REST API requires per-store OAuth credentials, is Cloudflare-protected (403 on direct curl), and provides the same data as Algolia but slower with lower quotas.

### 1.2 Algolia Connection Details

#### Demo Environment (for development/testing)
```
App ID:    VFM4X0N23A
API Key:   d16d4804f78c38777368ea8ced79e56e
Indices:   stores-demo, menu-products-demo
Store IDs: 2, 3, 4, 5
```

#### Production Environment
```
App ID:    VFM4X0N23A (same app)
API Key:   [MUST BE EXTRACTED from iheartjane.com frontend JS bundle]
Indices:   stores-production, menu-products-production
```

**To get the production API key:** Load any iHeartJane store page in a browser, inspect the JS bundle for the Algolia instantiation. The key is a public search-only key (safe to use). Look for `algoliasearch('VFM4X0N23A', '<key>')` in the page source/JS.

### 1.3 Algolia Query Pattern

```typescript
// Using algoliasearch npm package
import algoliasearch from 'algoliasearch/lite';

const client = algoliasearch('VFM4X0N23A', PRODUCTION_API_KEY);

// Store discovery: find all MA stores
const storesIndex = client.initIndex('stores-production');
const maStores = await storesIndex.search('', {
  filters: 'state:Massachusetts',
  hitsPerPage: 1000,
});

// Product scraping: get all products for a store
const productsIndex = client.initIndex('menu-products-production');
const products = await productsIndex.search('', {
  filters: `store_id = ${storeId}`,
  hitsPerPage: 1000,
});
```

### 1.4 Demo API Verified Working (Actual Response)

```bash
curl -X POST "https://VFM4X0N23A-dsn.algolia.net/1/indexes/menu-products-demo/query" \
  -H "X-Algolia-Application-Id: VFM4X0N23A" \
  -H "X-Algolia-API-Key: d16d4804f78c38777368ea8ced79e56e" \
  -H "Content-Type: application/json" \
  -d '{"query":"","hitsPerPage":2,"filters":"store_id = 2"}'
```

**Response: 200 OK** with full product records (verified Feb 13, 2026).

---

## Part 2: Data Model — iHeartJane Product Schema

### 2.1 Complete Product Record Fields (Verified from Demo)

From the Algolia `menu-products-demo` index, each hit contains:

#### Identity & Classification
| Field | Type | Example | GLASS Mapping |
|-------|------|---------|--------------|
| `objectID` | string | `"359"` | Internal Algolia ID |
| `product_id` | number | `1940` | Used in SKU generation |
| `name` | string | `"Chocolate Chip [Single] (80mg)"` | → `productName` |
| `brand` | string | `"Big Pete's Treats"` | → `brand` |
| `kind` | string | `"edible"` | → `category` (primary) |
| `type` | string | `"edible"` | → `category` (alias) |
| `custom_product_type` | string | `"Infused Food"` | → `subcategory` |
| `custom_product_subtype` | string | `"Baked Goods"` | → `subcategory` |
| `root_subtype` | string | `"Baked Goods"` | Taxonomy |
| `kind_subtype` | string | `"Biggie's"` | Brand sub-line |
| `category` | string | `"indica"` | → `strain_type` |
| `strain` | string/null | `null` | → `strain_type` |
| `url_slug` | string | `"big-pete-s-treats-chocolate-chip..."` | URL construction |
| `unique_slug` | string | `"big-pete-s-treats-indica-..."` | Unique identifier |

#### Pricing (Weight-Based Tiers)
| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `price_each` | number/null | `20.0` | Per-unit price |
| `price_gram` | number/null | `null` | Per gram |
| `price_two_gram` | number/null | `null` | Per 2g |
| `price_eighth_ounce` | number/null | `null` | Per 3.5g |
| `price_quarter_ounce` | number/null | `null` | Per 7g |
| `price_half_ounce` | number/null | `null` | Per 14g |
| `price_ounce` | number/null | `null` | Per 28g |
| `price_half_gram` | number/null | `null` | Per 0.5g |
| `sort_price` | number | `20.0` | Display/sort price |
| `bucket_price` | number | `20.0` | Price bucket |
| `discounted_price_*` | number/null | `null` | Post-discount versions of each tier |
| `special_price_*` | number/null | `null` | Special/deal versions |

#### Potency
| Field | Type | Example | GLASS Mapping |
|-------|------|---------|--------------|
| `percent_thc` | number/null | `null` | → `thcPercent` |
| `percent_thca` | number/null | `null` | → (derive THC) |
| `percent_cbd` | number/null | `null` | → `cbdPercent` |
| `percent_cbda` | number/null | `null` | — |
| `percent_tac` | number/null | `null` | → `tacPercent` |
| `dosage` | string/null | `"80mg"` | Edible dosage |
| `cannabinoids` | array | `[]` | Detailed cannabinoid list |
| `terpenes` | array | `[]` | Terpene profiles |

#### Weight & Quantity
| Field | Type | Example | GLASS Mapping |
|-------|------|---------|--------------|
| `net_weight_grams` | number | `0.0` | → `weight_grams` |
| `amount` | string/null | `"Single"` | Variant descriptor |
| `available_weights` | array | `[]` | Weight options |
| `quantity_value` | number/null | `null` | Pack size |
| `quantity_units` | string/null | `null` | Pack unit |

#### Store & Availability
| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `store_types` | array | `["recreational"]` | rec/medical |
| `available_for_pickup` | boolean | `true` | — |
| `available_for_delivery` | boolean | `true` | — |
| `store_specific_product` | boolean | `false` | — |

#### Metadata
| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `description` | string | `"We are a family..."` | Product description |
| `image_urls` | array | `["https://..."]` | Product photos |
| `photos` | array | `[{id, urls, position}]` | Structured photos |
| `aggregate_rating` | number | `0.0` | Average rating |
| `review_count` | number | `0` | Review count |
| `indexed_at` | number | `1770969632` | Unix timestamp |
| `product_brand_id` | number | `19` | Jane brand ID |
| `effects` | array | `[]` | Effects list |
| `flavors` | array | `[]` | Flavor profiles |
| `feelings` | array | `[]` | Feeling tags |
| `activities` | array | `[]` | Activity tags |
| `lab_results` | array | `[]` | Lab test data |

### 2.2 Store Record Fields (from `stores-demo` index)

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `objectID` | string | `"3"` | Jane store ID |
| `name` | string | `"Amy's Apothecary"` | → `operatorName` |
| `city` | string | `"Santa Cruz"` | → operator city |
| `state` | string | `"California"` | **Filter: `state:Massachusetts`** |
| `full_address` | string | `"400 Beach St..."` | Full address |
| `_geoloc` | object | `{lat, lng}` | Coordinates |
| `url_slug` | string | `"amy-s-apothecary"` | → platform_slug |
| `product_count` | number | `62` | Products available |
| `recreational` | boolean | `true` | Rec flag |
| `medical` | boolean | `false` | Medical flag |
| `delivery` | boolean | `true` | Delivery available |
| `pickup` | boolean | `true` | Pickup available |
| `marketplace_visible` | boolean | `true` | Listed on marketplace |
| `rating` | number | `4.99` | Store rating |
| `reviews_count` | number | `299` | Review count |
| `metro_area` | string | `"Santa Cruz, CA"` | Metro area |
| `phone` | string | `"(831) 555-5555"` | Contact |
| `pickup_hours` | array | 7 items | Daily pickup hours |
| `delivery_hours` | array | 7 items | Daily delivery hours |
| `working_hours` | array | 7 items | Business hours |
| `photo` | string/null | URL | Store photo |
| `store_options` | array | `["pickup","delivery"]` | Available options |
| `type` | array | `["recreational","pickup","delivery"]` | Type tags |

---

## Part 3: Field Mapping — iHeartJane → GLASS

### 3.1 ParsedProduct Mapping

```typescript
// Jane Algolia hit → GLASS ParsedProduct
function mapJaneProduct(hit: JaneAlgoliaHit, storeSlug: string, storeName: string): ParsedProduct {
  // Determine the best price: prefer weight-based, fall back to each
  const { price, weightGrams } = extractBestPrice(hit);
  
  return {
    slug: storeSlug,                          // Jane store slug
    operatorName: storeName,                   // From stores index
    menuUrl: `https://www.iheartjane.com/stores/${hit.store_id}/${storeSlug}`,
    category: normalizeJaneCategory(hit.kind), // 'flower'|'edible'|'vape'|etc
    subcategory: hit.custom_product_subtype || hit.root_subtype || undefined,
    brand: hit.brand || 'Unknown',
    productName: hit.name,
    variant: hit.amount || undefined,
    fullName: `${hit.brand} - ${hit.name}`,
    size: hit.amount || undefined,
    sku: undefined, // Generated by normalizer
    strain_type: hit.category || hit.strain || undefined, // 'indica'|'sativa'|'hybrid'
    thcPercent: hit.percent_thc ?? undefined,
    cbdPercent: hit.percent_cbd ?? undefined,
    tacPercent: hit.percent_tac ?? undefined,
    priceText: `$${price.toFixed(2)}`,
    priceValue: price,
    weight_grams: weightGrams ?? undefined,
    price_per_gram: undefined, // Computed by normalizer
    confidence: computeConfidence(hit),
    brandParseFailed: false,
    href: `https://www.iheartjane.com/products/${hit.product_id}/${hit.url_slug}`,
    raw: {
      linkText: hit.name,
      buttonText: `$${price.toFixed(2)}`,
      href: `https://www.iheartjane.com/products/${hit.product_id}/${hit.url_slug}`,
    },
  };
}
```

### 3.2 Category Mapping

| Jane `kind` | Jane `type` | GLASS Category |
|-------------|------------|----------------|
| `flower` | `flower` | `flower` |
| `pre-roll` | `pre-roll` | `preroll` |
| `vape` | `vape` | `vape` |
| `edible` | `edible` | `edible` |
| `extract` / `concentrate` | `concentrate` | `concentrate` |
| `tincture` | `tincture` | `tincture` |
| `topical` | `topical` | `topical` |
| `gear` / `accessory` | — | (skip) |

### 3.3 Price Extraction Logic

Jane stores prices per weight tier. GLASS needs a single price + weight:

```typescript
function extractBestPrice(hit: JaneAlgoliaHit): { price: number; weightGrams: number | null } {
  // Check weight-based prices in order of preference
  const tiers = [
    { field: 'price_eighth_ounce', grams: 3.5 },
    { field: 'price_gram', grams: 1 },
    { field: 'price_quarter_ounce', grams: 7 },
    { field: 'price_half_ounce', grams: 14 },
    { field: 'price_ounce', grams: 28 },
    { field: 'price_two_gram', grams: 2 },
    { field: 'price_half_gram', grams: 0.5 },
  ];

  for (const tier of tiers) {
    const price = hit[tier.field];
    if (price != null && price > 0) {
      return { price, weightGrams: tier.grams };
    }
  }

  // Fall back to per-unit price
  if (hit.price_each != null && hit.price_each > 0) {
    return { 
      price: hit.price_each, 
      weightGrams: hit.net_weight_grams > 0 ? hit.net_weight_grams : null 
    };
  }

  // Last resort: sort_price
  return { price: hit.sort_price || 0, weightGrams: null };
}
```

**Important:** For flower/concentrate, create ONE row per weight tier (not just the "best" price). This gives richer price comparison data. For edibles/vapes/tinctures, use `price_each`.

### 3.4 SKU Generation

Modify `makeSKU()` to produce Jane-specific SKUs:

```typescript
// In normalizer.ts — update makeSKU to accept platform prefix
function makeSKU(brand, name, weightGrams, category, platform = 'DUTCHIE') {
  const key = [normalizeBrand(brand), name.toLowerCase()..., ...].join('|');
  return `${platform}-${crypto.createHash('sha256').update(key).digest('hex').slice(0, 20)}`;
}
```

For Jane products: `JANE-<hash>` prefix.

---

## Part 4: Implementation Plan

### 4.1 New Files to Create

| File | Purpose |
|------|---------|
| `src/scripts/scrape-jane.ts` | Main scraper entry point (CLI) |
| `src/scripts/lib/jane-client.ts` | Algolia client wrapper |
| `src/scripts/lib/jane-parser.ts` | Product parsing & field mapping |
| `src/scripts/jane-slugs.json` | Discovered MA store list (auto-generated) |

### 4.2 Files to Modify

| File | Changes |
|------|---------|
| `src/scripts/lib/config.ts` | Add `JANE_ALGOLIA_APP_ID`, `JANE_ALGOLIA_API_KEY`, `JANE_CATEGORIES` |
| `src/scripts/lib/normalizer.ts` | Update `makeSKU()` to accept platform prefix, add `normalizeJaneCategory()` |
| `src/scripts/lib/types.ts` | Add `JaneAlgoliaHit`, `JaneStoreRecord` types |
| `src/scripts/lib/db.ts` | No changes needed — existing `upsertOperator/upsertSource/upsertProduct/insertPrice` work as-is |

### 4.3 Architecture: `scrape-jane.ts`

```
┌──────────────────────────────────────────────────────────┐
│                    scrape-jane.ts                         │
│                                                          │
│  Phase 1: Store Discovery                                │
│  ├─ Query stores-production index                        │
│  ├─ Filter: state = 'Massachusetts'                      │
│  ├─ Save to jane-slugs.json                              │
│  └─ Upsert operators + sources in DB                     │
│                                                          │
│  Phase 2: Product Scraping                               │
│  ├─ For each store: query menu-products-production       │
│  ├─ Paginate (hitsPerPage=1000, page=0,1,2...)           │
│  ├─ Parse products → ParsedProduct[]                     │
│  ├─ Normalize → NormalizedPrice[]                        │
│  └─ Upsert to DB (products + prices tables)              │
│                                                          │
│  Phase 3: Summary                                        │
│  └─ Log stats, save snapshot, complete scrape run         │
└──────────────────────────────────────────────────────────┘
```

### 4.4 Implementation Order

#### Step 1: Extract Production Algolia Key (Manual, 5 min)
1. Open any iHeartJane store page in a browser
2. Open DevTools → Sources or Network
3. Search for `algoliasearch` in JS bundles
4. Extract the production API key
5. Add to `.env` as `JANE_ALGOLIA_API_KEY`

**Alternative:** Use the public embed.js endpoint: `https://api.iheartjane.com/v1/stores/{id}/embed.js` — this JS file contains the Algolia key. CamoFox can load this once to extract it.

#### Step 2: Create `jane-client.ts` (~100 lines)
```typescript
// Wraps Algolia client with typed queries
export class JaneClient {
  discoverMAStores(): Promise<JaneStoreRecord[]>
  getStoreProducts(storeId: number): Promise<JaneAlgoliaHit[]>  // paginated
}
```

#### Step 3: Create `jane-parser.ts` (~150 lines)
```typescript
// Maps Algolia hits to ParsedProduct[]
export function parseJaneProducts(
  hits: JaneAlgoliaHit[],
  storeSlug: string,
  storeName: string
): ParsedProduct[]
```

#### Step 4: Create `scrape-jane.ts` (~250 lines)
Follow the pattern from `scrape-dutchie.ts` but:
- **No browser pool** — pure HTTP
- **No age gate handling** — Algolia is direct API
- **No scroll/snapshot** — structured JSON responses
- **Much faster** — should complete in 5-10 minutes vs 2+ hours

#### Step 5: Update shared modules (~20 lines total)
- `config.ts`: Add Jane constants
- `normalizer.ts`: Platform-aware SKU prefix
- `types.ts`: Jane-specific types

### 4.5 Detailed File Specifications

#### `src/scripts/lib/jane-client.ts`

```typescript
import algoliasearch, { SearchClient, SearchIndex } from 'algoliasearch/lite';
import { JANE_ALGOLIA_APP_ID, JANE_ALGOLIA_API_KEY } from './config';

export type JaneStoreRecord = {
  objectID: string;        // Jane store ID (numeric string)
  name: string;
  city: string;
  state: string;
  full_address: string;
  url_slug: string;
  product_count: number;
  recreational: boolean;
  medical: boolean;
  _geoloc: { lat: number; lng: number };
  marketplace_visible: boolean;
};

export type JaneAlgoliaHit = {
  objectID: string;
  product_id: number;
  name: string;
  brand: string;
  kind: string;              // 'flower' | 'edible' | 'vape' | etc
  type: string;
  category: string;          // 'indica' | 'sativa' | 'hybrid' | null
  strain: string | null;
  custom_product_type: string | null;
  custom_product_subtype: string | null;
  root_subtype: string | null;
  amount: string | null;
  dosage: string | null;
  url_slug: string;
  unique_slug: string;
  
  // Prices
  price_each: number | null;
  price_gram: number | null;
  price_two_gram: number | null;
  price_eighth_ounce: number | null;
  price_quarter_ounce: number | null;
  price_half_ounce: number | null;
  price_ounce: number | null;
  price_half_gram: number | null;
  sort_price: number;
  bucket_price: number;
  discounted_price_each: number | null;
  // ... all discounted_price_* and special_price_* fields
  
  // Potency
  percent_thc: number | null;
  percent_thca: number | null;
  percent_cbd: number | null;
  percent_cbda: number | null;
  percent_tac: number | null;
  net_weight_grams: number;
  
  // Metadata
  description: string;
  image_urls: string[];
  store_types: string[];
  available_for_pickup: boolean;
  available_for_delivery: boolean;
  indexed_at: number;
};

export class JaneClient {
  private client: SearchClient;
  private storesIndex: SearchIndex;
  private productsIndex: SearchIndex;

  constructor() {
    this.client = algoliasearch(JANE_ALGOLIA_APP_ID, JANE_ALGOLIA_API_KEY);
    this.storesIndex = this.client.initIndex('stores-production');
    this.productsIndex = this.client.initIndex('menu-products-production');
  }

  async discoverMAStores(): Promise<JaneStoreRecord[]> {
    const stores: JaneStoreRecord[] = [];
    let page = 0;
    let hasMore = true;
    
    while (hasMore) {
      const result = await this.storesIndex.search<JaneStoreRecord>('', {
        filters: 'state:Massachusetts',
        hitsPerPage: 100,
        page,
      });
      stores.push(...result.hits);
      hasMore = page < result.nbPages - 1;
      page++;
    }
    
    return stores;
  }

  async getStoreProducts(storeId: number): Promise<JaneAlgoliaHit[]> {
    const products: JaneAlgoliaHit[] = [];
    let page = 0;
    let hasMore = true;
    
    while (hasMore) {
      const result = await this.productsIndex.search<JaneAlgoliaHit>('', {
        filters: `store_id = ${storeId}`,
        hitsPerPage: 1000,
        page,
      });
      products.push(...result.hits);
      hasMore = page < result.nbPages - 1;
      page++;
    }
    
    return products;
  }
}
```

#### `src/scripts/scrape-jane.ts` (Pseudocode)

```typescript
// CLI flags: --skip-discovery, --limit N, --dry-run, --db, --resume <runId>
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const jane = new JaneClient();

  // Phase 1: Discover MA stores
  let stores: JaneStoreRecord[];
  if (args.skipDiscovery) {
    stores = await loadSlugs(args.slugsFile);
  } else {
    stores = await jane.discoverMAStores();
    await saveSlugs(args.slugsFile, stores);
  }

  if (args.limit) stores = stores.slice(0, args.limit);
  if (args.dryRun) return;

  // Phase 2: Scrape products per store
  let runId: string | undefined;
  if (args.db) {
    runId = await createScrapeRun('jane');
  }

  for (const store of stores) {
    const storeId = Number(store.objectID);
    
    if (args.db) {
      const operatorId = await upsertOperator('jane', store.url_slug, store.name, store.city);
      const sourceId = await upsertSource(operatorId, 
        `https://www.iheartjane.com/stores/${storeId}/${store.url_slug}`, 'jane');
      const jobId = await createScrapeJob(sourceId, runId!);
    }

    const hits = await jane.getStoreProducts(storeId);
    const parsed = parseJaneProducts(hits, store.url_slug, store.name);
    const normalized = parsed.map(normalizeProduct).filter(p => p.price > 0);

    for (const item of normalized) {
      if (args.db) {
        const productId = await upsertProduct(...);
        await insertPrice(..., 'jane_algolia_v1');
      }
    }

    // Light rate limiting (100ms between stores)
    await sleep(100);
  }

  // Phase 3: Summary
  if (args.db && runId) await completeScrapeRun(runId, stats);
}
```

### 4.6 Config Additions (`config.ts`)

```typescript
export const JANE_ALGOLIA_APP_ID = envOr('JANE_ALGOLIA_APP_ID', 'VFM4X0N23A');
export const JANE_ALGOLIA_API_KEY = envOr('JANE_ALGOLIA_API_KEY', ''); // MUST be set in .env

export const JANE_CATEGORIES: Record<string, string> = {
  flower: 'flower',
  'pre-roll': 'preroll',
  vape: 'vape',
  edible: 'edible',
  extract: 'concentrate',
  concentrate: 'concentrate',
  tincture: 'tincture',
  topical: 'topical',
};
```

---

## Part 5: MA Store Discovery Strategy

### 5.1 Algolia-Based Discovery

Query the `stores-production` index with filter `state:Massachusetts`:

```typescript
const maStores = await storesIndex.search('', {
  filters: 'state:Massachusetts',
  hitsPerPage: 200,
});
// Returns all MA stores with objectID (store_id), name, city, url_slug, product_count
```

This gives us the complete list instantly. No city-by-city crawling needed (unlike Dutchie/Weedmaps).

### 5.2 Store Filtering Criteria

Include stores where:
- `state === 'Massachusetts'`
- `product_count > 0` (has menu items)
- `marketplace_visible === true` (not hidden)
- `recreational === true || medical === true` (active dispensary)

### 5.3 Cross-Reference with Existing Operators

After discovery, cross-reference Jane stores against existing GLASS operators to identify:
1. **New stores** — not in Dutchie or Weedmaps (add as new operators)
2. **Existing stores** — already have operator records (add Jane as additional source)

Match by:
- Fuzzy name matching (Levenshtein distance)
- City matching
- Address/geo matching (Jane provides `_geoloc`)

---

## Part 6: Risk Assessment

### 6.1 Risks & Mitigations

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| **Production Algolia key not found in JS** | HIGH | LOW | Fallback: CamoFox loads one embed page to extract key from JS; or intercept network requests |
| **Algolia rate limiting** | MEDIUM | LOW | Algolia has very high quotas for search-only keys; add 100ms delay between stores |
| **Index name changed** | MEDIUM | LOW | Monitor for 404s; check `stores-production` and `menu-products-production` |
| **Cloudflare blocks Algolia** | LOW | VERY LOW | Algolia uses their own CDN (algolia.net), not iheartjane.com domain |
| **Data schema changes** | LOW | MEDIUM | Type-safe parsing with fallbacks for missing fields |
| **Jane deprecates public Algolia access** | HIGH | LOW | Would need to switch to REST API + OAuth or CamoFox browser scraping |
| **Duplicate products (same store on Jane + Dutchie)** | LOW | HIGH | Different SKU prefixes (JANE- vs DUTCHIE-); cross-platform dedup is a Phase 2 concern |

### 6.2 Anti-Bot Assessment

| Factor | Status | Notes |
|--------|--------|-------|
| **Cloudflare protection** | ✅ NOT AN ISSUE | Algolia uses `VFM4X0N23A-dsn.algolia.net`, not behind Cloudflare |
| **API key rotation** | ⚠️ POSSIBLE | Monitor; production key may rotate (search-only keys typically don't) |
| **IP-based rate limiting** | ✅ UNLIKELY | Algolia's search-only keys are designed for client-side use |
| **User-Agent requirements** | ✅ NONE | Algolia accepts any HTTP client |
| **CAPTCHA** | ✅ NONE | Direct API, no browser required |

### 6.3 Legal Considerations

- Algolia search-only API keys are **intentionally public** — they're embedded in client-side JavaScript for end-user browsers to call directly
- This is equivalent to loading the iHeartJane website and reading the menu — just via API instead of browser
- The data is publicly accessible to any website visitor
- **No authentication bypass, no credential theft, no ToS violation**

---

## Part 7: Performance & Operational Estimates

### 7.1 Speed Estimates

| Metric | Estimate | Notes |
|--------|----------|-------|
| Store discovery | ~1 second | Single Algolia query |
| Products per store | ~200ms | Single query for most stores |
| Total MA stores | ~100-150 | Based on Jane's MA presence |
| Products per store (avg) | ~50-100 | Typical dispensary menu size |
| **Total scrape time** | **~2-5 minutes** | vs 2+ hours for Dutchie/Weedmaps |
| Daily price records added | ~3,000-6,000 | Across all Jane stores |

### 7.2 Resource Usage

- **No CamoFox** — pure Node.js HTTP requests
- **Memory:** ~50-100MB (Algolia JSON responses)
- **Network:** ~10-50MB total per run
- **CPU:** Minimal — no DOM parsing or browser rendering

### 7.3 Scheduling

Run the Jane scraper **daily at a different time** than Dutchie/Weedmaps to avoid DB contention:

```
Dutchie:  06:00 UTC (existing)
Weedmaps: 09:00 UTC (existing)
Jane:     12:00 UTC (new)
```

---

## Part 8: Implementation Checklist

### Phase 1: Foundation (Day 1)
- [ ] Extract production Algolia API key from iHeartJane frontend
- [ ] Add `JANE_ALGOLIA_APP_ID` and `JANE_ALGOLIA_API_KEY` to `.env`
- [ ] Install `algoliasearch` npm package
- [ ] Create `src/scripts/lib/jane-client.ts` with types
- [ ] Verify production index access with test query

### Phase 2: Parser (Day 1-2)
- [ ] Create `src/scripts/lib/jane-parser.ts`
- [ ] Implement category mapping (`normalizeJaneCategory`)
- [ ] Implement price extraction (`extractBestPrice`)
- [ ] Implement confidence scoring
- [ ] Update `normalizer.ts` for JANE- SKU prefix
- [ ] Add types to `types.ts`
- [ ] Add constants to `config.ts`

### Phase 3: Scraper (Day 2)
- [ ] Create `src/scripts/scrape-jane.ts` following Dutchie pattern
- [ ] Implement CLI args (`--skip-discovery`, `--limit`, `--dry-run`, `--db`, `--resume`)
- [ ] Implement store discovery with Algolia
- [ ] Implement per-store product scraping
- [ ] Implement DB writes (reuse existing `db.ts` functions)
- [ ] Implement JSON snapshot saving
- [ ] Implement run/job tracking

### Phase 4: Testing (Day 2-3)
- [ ] Run with `--dry-run` to verify store discovery
- [ ] Run with `--limit 5` to verify product parsing
- [ ] Run with `--limit 5 --db` to verify DB writes
- [ ] Verify no duplicate operators (cross-reference existing)
- [ ] Full run: all MA stores
- [ ] Verify data in GLASS dashboard

### Phase 5: Integration (Day 3)
- [ ] Add to scheduled scrape pipeline
- [ ] Update `DATA-COVERAGE-ANALYSIS.md` with Jane results
- [ ] Monitor first few days of production runs

---

## Appendix A: Jane Roots Documentation Structure

The official Jane developer documentation lives at `docs.iheartjane.com/jane-docs/`:

| Section | URL | Relevance |
|---------|-----|-----------|
| Introduction | `/jane-docs` | Overview |
| Technology Overview | `/jane-docs/implementing-roots/technology-overview-and-sandbox-credentials` | **Algolia + REST API credentials** |
| Building Your Menu | `/jane-docs/implementing-roots/building-your-menu` | Algolia query patterns |
| Product Details | `/jane-docs/implementing-roots/building-your-menu/using-react-and-instant-search/product-details` | Product field reference |
| Algolia Reference | `/jane-docs/apis/algolia-reference` | Index schema |
| Swagger Docs (Demo) | `demo-api.nonprod-iheartjane.com/jane-api-docs/index.html?urls.primaryName=Menu%20API%20V1%20Docs` | REST API reference |
| Swagger Docs (Prod) | `www.iheartjane.com/api/jane-api-docs/index.html?urls.primaryName=Store+Operations+API+V1+Docs` | REST API (prod) |

## Appendix B: Demo Credentials (for Development)

```
# Algolia Demo
APP_ID:   VFM4X0N23A
API_KEY:  d16d4804f78c38777368ea8ced79e56e
Indices:  stores-demo, menu-products-demo
Stores:   2, 3, 4, 5

# REST API Demo
CLIENT_ID:     8ssq_GEiGxXI1EJytSpjEH262iBXYsB9h8oYblZTw6g
CLIENT_SECRET:  8zfZiA-hxjaA0moXoUDhyVvMUP7J7WUZ37YZJtc4A2c
Base URL:      https://demo-api.nonprod-iheartjane.com
```

## Appendix C: Example Algolia Queries

### Discover MA Stores
```bash
curl -X POST "https://VFM4X0N23A-dsn.algolia.net/1/indexes/stores-production/query" \
  -H "X-Algolia-Application-Id: VFM4X0N23A" \
  -H "X-Algolia-API-Key: $PRODUCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"","hitsPerPage":200,"filters":"state:Massachusetts"}'
```

### Get Products for Store #123
```bash
curl -X POST "https://VFM4X0N23A-dsn.algolia.net/1/indexes/menu-products-production/query" \
  -H "X-Algolia-Application-Id: VFM4X0N23A" \
  -H "X-Algolia-API-Key: $PRODUCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"","hitsPerPage":1000,"filters":"store_id = 123"}'
```

### Get Specific Product
```bash
curl -X POST "https://VFM4X0N23A-dsn.algolia.net/1/indexes/menu-products-production/query" \
  -H "X-Algolia-Application-Id: VFM4X0N23A" \
  -H "X-Algolia-API-Key: $PRODUCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"","hitsPerPage":1,"filters":"store_id: 123 AND product_id: 456"}'
```

## Appendix D: Key Differences from Dutchie/Weedmaps Scrapers

| Aspect | Dutchie/Weedmaps | Jane |
|--------|-----------------|------|
| **Data access** | Browser scraping (CamoFox) | Algolia API (HTTP/JSON) |
| **Browser required** | Yes | **No** |
| **Age gate** | Must dismiss | N/A |
| **Scroll/pagination** | DOM scrolling + page nav | API `page` parameter |
| **Product parsing** | DOM text → regex/heuristics | Structured JSON fields |
| **Price extraction** | Text parsing ("$30.00") | Typed numeric fields |
| **Category detection** | URL path + text heuristics | `kind` field |
| **Brand extraction** | Text splitting heuristics | `brand` field |
| **Confidence** | Variable (0.5-1.0) | High (0.95+) — structured data |
| **Speed** | 2-4 hours | **2-5 minutes** |
| **Failure modes** | Age gates, timeouts, empty pages | API key rotation, index name changes |
| **Rate limiting** | Aggressive (Cloudflare) | **Minimal** (Algolia CDN) |
