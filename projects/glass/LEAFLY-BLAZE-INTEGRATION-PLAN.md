# Leafly & Blaze POS Integration Plans

> **Research Date:** February 13, 2026  
> **Purpose:** Evaluate two additional data sources for GLASS cannabis price intelligence platform

---

## Executive Summary

| Source | MA Coverage | Access Method | Difficulty | Timeline |
|--------|-------------|----------------|------------|----------|
| **Leafly** | ~160 dispensaries | Web scraping (CamoFox) | Medium | 2-3 weeks |
| **Blaze POS** | Unknown (estimate: 15-30) | Partner API | Hard | 4-8 weeks |

**Recommendation:** Pursue Leafly first for immediate coverage gains. Begin Blaze BPN application in parallel for strategic partnership access.

---

## Part 1: Leafly

### 1.1 Discovery

#### Coverage Estimate
- **160+ licensed MA dispensaries** listed on Leafly (per their state page)
- This likely includes both recreational and medical dispensaries
- Filter to ~120-140 recreational (target market for price intelligence)

#### Store Discovery Method

**Option A: Internal API (Recommended)**

Based on research, Leafly exposes an internal search endpoint:

```
https://web-finder.leafly.com/api/search-this-area
  ?topLeftLat=42.98
  &topLeftLon=-73.50
  &bottomRightLat=41.23
  &bottomRightLon=-69.93
  &userLat=42.36
  &userLon=-71.05
  &retailType=dispensary
```

**Response format** (observed from Reddit research):
```json
{
  "stores": [
    {
      "name": "Dispensary Name",
      "slug": "dispensary-slug",
      "permalink": "herbal-nation",
      "latitude": 42.3601,
      "longitude": -71.0589,
      "address": "...",
      "phone": "...",
      "hours": {...}
    }
  ]
}
```

**MA Bounding Box for full coverage:**
- Top-left: 42.98, -73.50 (NW corner near Williamstown)
- Bottom-right: 41.23, -69.93 (SE corner near Provincetown)

**Option B: State Page Scraping**
- URL: `https://www.leafly.com/dispensaries/massachusetts`
- Requires CamoFox due to client-side rendering
- Parse dispensary cards/links from accessibility snapshot

#### URL Patterns

| Type | Pattern | Example |
|------|---------|---------|
| State listing | `/dispensaries/{state}` | `/dispensaries/massachusetts` |
| Dispensary info | `/dispensary-info/{slug}` | `/dispensary-info/dispo-93f49` |
| Menu (likely API) | Internal: `/api/v1/dispensaries/{id}/menu` | N/A - internal |

### 1.2 Menu Data

#### Historical API Context

Leafly previously had a public API with endpoints like:
```
GET /locations/{slug}/menu
```

**However, this API is now deprecated/locked.** The python-leafly wrapper (https://github.com/lionheart/python-leafly) shows the old structure but no longer functions.

Leafly's official stance (from help center):  
> "At this time, Leafly only has Menu and Order API endpoints available for POS integrators. We do not have endpoints to fetch strain data, brand-supplied product information, or reviews from our site."

#### Current Approach: Client-Side Rendering

Leafly dispensary pages load menus via JavaScript. Implementation approach:

1. **CamoFox browser navigation** to `/dispensary-info/{slug}`
2. **Wait for hydration** - menu loads via XHR/fetch
3. **Poll for data** using one of:
   - Accessibility snapshot parsing (like Dutchie approach)
   - Network interception (if CamoFox supports)
   - DOM scraping of rendered product cards

#### Expected Product Data Fields

Based on observed Leafly menu structures:

| Field | Availability | Notes |
|-------|--------------|-------|
| `productName` | ✅ High | Full product name |
| `brand` | ✅ High | Usually parsed from name |
| `category` | ✅ High | Flower, Pre-roll, Edible, etc. |
| `price` | ✅ High | Current price |
| `thcPercent` | ✅ Medium | Often shown on menu cards |
| `cbdPercent` | ⚠️ Low | Sometimes shown |
| `weight` | ✅ High | e.g., "3.5g", "1/8 oz" |
| `strain` | ✅ Medium | For flower products |
| `sku` | ❌ No | Leafly doesn't expose SKUs |

**Sample observed data structure:**
```javascript
{
  "id": "product-12345",
  "name": "Blue Dream 3.5g",
  "brand": "Nature's Heritage",
  "category": "Flower",
  "price": 45.00,
  "thc": 22.5,
  "cbd": 0.1,
  "weight": "3.5g",
  "strainName": "Blue Dream",
  "strainType": "Hybrid"
}
```

#### Anti-Bot Assessment

**Confirmed protections:**
- **Cloudflare** - Confirmed via multiple sources (GitHub: gugarosa/leaflyer)
- **reCAPTCHA v2** - Observed on some endpoints
- Bot detection triggers on rapid requests

**CamoFox compatibility:**
- ✅ Required - Leafly blocks datacenter IPs
- ✅ Residential proxy recommended for production scale
- ✅ Rate limiting essential (3-5 second delays between requests)

#### Data Model Mapping to GLASS Schema

```typescript
// Parsed from Leafly menu
interface LeaflyProduct {
  slug: string;              // Dispensary slug
  operatorName: string;      // Dispensary name
  menuUrl: string;           // Full URL
  productName: string;       // Full display name
  brand: string;             // Parsed from name or explicit field
  category: string;          // Mapped to GLASS categories
  priceValue: number;        // Numeric price
  thcPercent?: number;       // If available
  cbdPercent?: number;       // If available
  size?: string;             // Raw weight display
  weight_grams?: number;     // Computed
}

// Category mapping
const LEAFLY_TO_GLASS = {
  'Flower': 'flower',
  'Pre-roll': 'preroll',
  'Pre-Roll': 'preroll',
  'Vape': 'vape',
  'Cartridge': 'vape',
  'Edible': 'edible',
  'Concentrate': 'concentrate',
  'Extract': 'concentrate',
  'Tincture': 'tincture',
  'Topical': 'topical'
};

// SKU generation
// Use same hash-based approach as Dutchie:
// `LEAFLY-${hash(brand|name|weight|category)}`
```

### 1.3 Implementation Plan

#### Phase 1: Discovery (Week 1)
```typescript
// scripts/discovery/leafly-slugs.ts
// 1. Call web-finder API for MA bounding box
// 2. Filter to recreational dispensaries
// 3. Build leafly-slugs.json with:
//    - slug
//    - name
//    - address
//    - lat/lng
// 4. Manual sample validation (10 stores)
```

#### Phase 2: Scraper Development (Week 1-2)
```typescript
// scripts/scrape-leafly.ts
// Similar structure to scrape-dutchie.ts

const LEAFLY_CATEGORIES = [
  'flower',
  'pre-roll', 
  'vape',
  'edible',
  'concentrate'
];

async function scrapeLeaflyStore(slug: string) {
  const tab = await browserPool.createTab();
  await tab.navigate(`https://www.leafly.com/dispensary-info/${slug}`);
  
  // Wait for menu hydration
  await tab.waitForSelector('[data-testid="menu-item"]');
  
  // Scroll to load all products
  await autoScroll(tab);
  
  // Extract via accessibility snapshot
  const snapshot = await tab.accessibilitySnapshot();
  return parseLeaflyMenu(snapshot);
}
```

#### Phase 3: Parser Development (Week 2)
- Build `lib/parsers/leafly-parser.ts`
- Handle Leafly's specific product card format
- Brand extraction from product names (common pattern)
- Category normalization

#### Phase 4: Testing & Deployment (Week 3)
- Test on 20 sample stores
- Verify price accuracy vs manual checks
- Rate limit calibration
- Add to daily run script

### 1.4 Coverage Estimate

| Metric | Estimate |
|--------|----------|
| Total MA stores on Leafly | ~160 |
| Recreational stores | ~130 |
| Expected successful scrapes (70%) | ~90 |
| Avg products per store | ~150 |
| **Total price points (daily)** | **~13,500** |

**Overlap with existing sources:**
- Dutchie: ~30-40% of stores likely use both platforms
- Weedmaps: ~60% overlap expected
- **Net new coverage:** ~50-60 stores, ~7,500 prices/day

---

## Part 2: Blaze POS

### 2.1 API Documentation

#### Overview
- **Docs:** https://apidocs.blaze.me
- **Access:** Blaze Partner Network (BPN) required
- **Cost:** Partner API access is paid (amount undisclosed, requires negotiation)
- **Authentication:** Partner Key + Retailer (Dispensary) Key

#### Relevant Endpoints

Based on apidocs.blaze.me research, relevant endpoints for menu/pricing data:

**1. GET /v1/partner/stores/{storeId}/products**
```
Authorization: Bearer {partnerKey}
X-Retailer-Key: {dispensaryKey}
```

**2. GET /v1/partner/stores/{storeId}/batches**
- Inventory batches with pricing

**3. GET /v1/partner/stores/{storeId}/inventory**
- Current inventory levels

**4. Search Products**
```
GET /v1/partner/stores/{storeId}/products/search
?category={category}
&active=true
```

**Observed response structure** (from API docs snippets):
```json
{
  "id": "prod-12345",
  "name": "Blue Dream",
  "category": "Flower",
  "strain": "Blue Dream",
  "strainType": "Hybrid",
  "brand": "Nature's Heritage",
  "weightGrams": 3.5,
  "price": 45.00,
  "thc": 22.5,
  "cbd": 0.1,
  "batchId": "batch-67890",
  "quantityAvailable": 24,
  "sku": "NH-BD-35-001"
}
```

#### Data Model Mapping to GLASS Schema

| Blaze Field | GLASS Field | Notes |
|--------------|--------------|-------|
| `id` | - | Blaze internal ID |
| `sku` | `sku` | If present, use directly |
| `name` + `brand` | `productName` | Composite name |
| `category` | `category` | Direct mapping |
| `strain` | `strainType` + strain name |
| `thc` | `thcPercent` | Direct |
| `cbd` | `cbdPercent` | Direct |
| `price` | `price` | Direct |
| `weightGrams` | `weightGrams` | Pre-computed |
| `quantityAvailable` | - | Stock level |
| `batchId` | - | For traceability |

**Category mapping:**
```javascript
const BLAZE_TO_GLASS = {
  'Flower': 'flower',
  'Preroll': 'preroll',
  'Vape': 'vape',
  'Edible': 'edible',
  'Concentrate': 'concentrate',
  'Tincture': 'tincture',
  'Topical': 'topical',
  'Accessories': 'other'
};
```

### 2.2 Access Process

#### Step 1: BPN Application
1. Navigate to: https://www.blaze.me/bpn/
2. Complete "Third-Party Integration Partner" application
3. Estimated time: 4 minutes to complete form
4. Required information:
   - Company details
   - Use case description
   - Integration type (select: Analytics/Market Intelligence)

#### Step 2: Approval Process
- **Timeline:** Unknown (estimate 1-2 weeks)
- **Cost:** Negotiated based on usage tiers
- **Contract:** Legal review of partner agreement required

#### Step 3: Technical Onboarding
1. Receive **Partner Key** (your organization key)
2. Receive **Staging Account** for testing
3. Per-store integration requires **Retailer/Dispensary Key**

#### Access Model Options

**Option A: Blaze Corporate Partnership**
- Partner with Blaze corporate for bulk data access
- Pros: One integration covers all Blaze retailers
- Cons: Requires BPN, ongoing fees, legal review

**Option B: Individual Dispensary Grants**
- Each dispensary generates API key for GLASS
- Pros: Direct relationship, no BPN required
- Cons: Sales effort per store, inconsistent coverage

**Recommended:** Option A for scalable coverage

### 2.3 Implementation Plan

#### Phase 1: BPN Application (Week 1-2)
```
Action: Submit BPN application
Owner: Business/Development team
Output: Partner application submitted
```

#### Phase 2: Discovery (Parallel)
```
Action: Identify MA dispensaries using Blaze
Sources:
- Blaze marketing claims "Massachusetts" as active state
- Delivered Inc (Clinton, MA) confirmed Blaze customer
- Direct outreach to MA dispensaries
Estimate: 15-30 stores in MA
```

#### Phase 3: Technical Integration (Week 4-6)
```typescript
// scripts/scrape-blaze.ts

interface BlazeCredentials {
  partnerKey: string;
  dispensaryKey: string;
  storeId: string;
}

async function fetchBlazeMenu(creds: BlazeCredentials) {
  const response = await fetch(
    `https://api.blaze.me/v1/partner/stores/${creds.storeId}/products`,
    {
      headers: {
        'Authorization': `Bearer ${creds.partnerKey}`,
        'X-Retailer-Key': creds.dispensaryKey,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.json();
}

// Categories to fetch
const BLAZE_CATEGORIES = [
  'Flower',
  'Preroll',
  'Vape',
  'Edible',
  'Concentrate'
];
```

#### Phase 4: Data Pipeline (Week 6-8)
- Build `lib/parsers/blaze-parser.ts`
- Map to GLASS NormalizedPrice schema
- Implement batch fetching for efficiency
- Rate limit handling (API quota management)

### 2.4 Coverage Estimate

**MA Store Count Estimation:**
- Blaze operates in 20+ states
- Claims "thousands of businesses" nationally
- MA market: ~160 total dispensaries
- Industry market share estimates:
  - Dutchie: ~40%
  - Blaze: ~10-15%
  - Flowhub: ~10%
  - Others: ~35%

**Conservative estimate:** 15-30 MA dispensaries use Blaze

| Metric | Estimate |
|--------|----------|
| Blaze stores in MA | 15-30 |
| Expected API access | 20-25 |
| Avg products per store | ~200 |
| **Total price points (daily)** | **~4,000-5,000** |

**Strategic value:**
- Often higher-end retailers
- Real-time inventory data
- Direct API = 100% reliability (no scraping issues)

### 2.5 Risks and Considerations

| Risk | Impact | Mitigation |
|------|--------|------------|
| BPN application rejected | High | Prepare alternative proposal; emphasize data aggregation value |
| API costs prohibitive | High | Negotiate volume pricing; prioritize high-value stores |
| Data freshness lag | Medium | API polling frequency (recommend: hourly) |
| Rate limiting | Low | Implement exponential backoff; cached access |
| Terms of service changes | Medium | Quarterly contract review; SLA requirements |
| Individual store opt-out | Medium | Maintain relationship with Blaze corporate for renewal |

---

## Part 3: Comparison & Priority

### Coverage Comparison

| Source | Est. MA Stores | Est. Prices/Day | New Coverage | Complexity |
|--------|----------------|------------------|--------------|------------|
| **Dutchie** | 235 | 57,000 | Baseline | Solved |
| **Weedmaps** | 282 | 6,000 (flaky) | Baseline | Medium |
| **Leafly** | 90-130 | 13,500 | +50-60 stores | Medium |
| **Blaze** | 15-30 | 4,000-5,000 | +15-25 stores | Hard |

### Recommendation: Sequential Implementation

**Phase 1: Leafly (Immediate - 2-3 weeks)**
- ✅ Highest coverage gain
- ✅ Uses existing CamoFox infrastructure
- ✅ Similar complexity to Weedmaps
- ✅ No partnerships/legal needed
- 🎯 Target: Deploy by March 1

**Phase 2: Blaze (Strategic - 6-8 weeks)**
- ✅ Premium data source
- ✅ 100% API reliability
- ✅ Competitive differentiation
- ⚠️ Requires BPN application
- ⚠️ Cost negotiation needed
- 🎯 Target: Deploy by April 1

### Implementation Order

```
Week 1-2:  Leafly discovery + scraper dev
Week 3:    Leafly deployment + testing
Week 4:    Blaze BPN application submitted
Week 6-8:  Blaze integration (pending approval)
```

---

## Appendix A: Technical References

### Leafly Resources
- State page: https://www.leafly.com/dispensaries/massachusetts
- Finder API pattern: `https://web-finder.leafly.com/api/search-this-area`  
- Dispensary page template: `https://www.leafly.com/dispensary-info/{slug}`
- Historical API wrapper: https://github.com/lionheart/python-leafly (deprecated)
- Leafly support: help@leafly.com

### Blaze Resources
- BPN portal: https://www.blaze.me/bpn/
- API docs: https://apidocs.blaze.me
- Support: (415) 964-5689 ext. 1
- Active states include Massachusetts
- Confirmed MA customer: Delivered Inc (Clinton, MA)

### GLASS Integration Points
- Add leafly-slugs.json to config
- Add BLAZE_PARTNER_KEY to secrets (pending BPN)
- Update daily run script with new scrapers
- Extend types.ts with source-specific RawProduct types

---

## Appendix B: Open Questions

**Leafly:**
1. Confirm `web-finder.leafly.com` endpoint stability
2. Validate menu data structure via CamoFox inspection
3. Test anti-bot detection thresholds

**Blaze:**
1. BPN application response time (inquire directly)
2. API pricing tiers (request quote)
3. Sandbox environment access timeline
4. Exact list of MA dispensaries using Blaze
5. Data refresh frequency guarantees

---

*Document prepared for GLASS platform expansion planning.*
*Next step: Review with product team and prioritize implementation.*
