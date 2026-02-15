# GLASS Consumer Web UX Improvement Plan

> **Generated:** 2026-02-15  
> **Source:** Frontend UX Audit Feedback  
> **Status:** Actionable execution plan for developers

---

## Executive Summary

The GLASS web app has a strong data foundation (4,288 GPIDs, 6,299 price points) and a premium dark theme, but currently feels like a "data dashboard pretending to be a consumer app." This plan prioritizes fixes that bridge that gap — starting with critical credibility issues, then moving to high-impact UX improvements, and finally differentiation features that create "can't stop using it" value.

**Success Metrics:**
- P0 completion = "This feels like a real product"
- P1 completion = "This is useful for comparison shopping"
- P2/P3 completion = "This is my go-to cannabis tool"

---

## Phase 1: P0 — Critical Fixes (Week 1)

> **Goal:** Fix credibility-killing issues before any feature work. These are blocking user trust.

### 1.1 Fix Product Images — The #1 Credibility Issue
**Effort:** 1 day  
**Impact:** 🔥🔥🔥🔥🔥  
**Owner:** Frontend + Backend

**Current State:** ~70% of cards show gray placeholder icons. This screams "beta."

**Implementation Plan:**

```
Task A: Scraper Image Integration (Backend)
├── Check if Dutchie/Jane menu scrapes include product.imageUrl
├── If yes: ensure image URLs are stored in gpid.product_image_url
├── If no: add image extraction to scrapers
└── Add fallback_url field for category-based defaults

Task B: Category Fallback Images (Design + Frontend)
├── Create category image assets:
│   ├── /images/categories/flower.jpg
│   ├── /images/categories/edible.jpg
│   ├── /images/categories/concentrate.jpg
│   ├── /images/categories/vape.jpg
│   ├── /images/categories/preroll.jpg
│   └── /images/categories/default.jpg
├── Update DealCard component to use category fallback when no product image
└── Ensure images are 1:1 aspect ratio, dark-themed to match UI

Task C: Image Loading States
├── Add blur-up loading pattern
├── Handle broken images gracefully (fallback chain)
└── Lazy load below-the-fold images
```

**Acceptance Criteria:**
- [ ] >90% of cards show relevant images (product or category)
- [ ] No gray placeholder icons visible on first scroll
- [ ] Images load within 1 second on 3G

**Dependencies:** None (can start immediately)

---

### 1.2 Shrink Hero — Show Value Above the Fold
**Effort:** 2 hours  
**Impact:** 🔥🔥🔥🔥  
**Owner:** Frontend

**Current State:** Hero + search + filters take 100% viewport. Users see zero deals on load.

**Implementation Plan:**

```
File: app/page.tsx (or Hero section component)

Changes:
├── Reduce hero height from 100vh to ~60vh
├── Tighten vertical padding (py-16 → py-10)
├── Reduce headline font size on mobile
├── Compress vertical spacing between elements
└── Ensure DealCard peeks above fold (negative margin or reduced spacing)
```

**Specific Values to Try:**
- Hero max-height: `min(600px, 60vh)`
- Headline: `text-4xl md:text-5xl` (down from 5xl/6xl)
- Padding: `py-8 md:py-12` (down from py-16)
- Gap after search: `mb-4` (down from mb-8)

**Acceptance Criteria:**
- [ ] Top deal card is partially visible without scrolling on 13" laptop
- [ ] Hero still communicates value proposition clearly
- [ ] Mobile experience preserved (test on actual devices)

**Dependencies:** None

---

### 1.3 Location Button — Add Feedback & Geo-Routing
**Effort:** 4 hours  
**Impact:** 🔥🔥🔥  
**Owner:** Frontend

**Current State:** Button fires `getCurrentPosition` but shows no feedback. Users don't know if it worked.

**Implementation Plan:**

```
Component: LocationButton (or in Hero/Search)

States to Implement:
├── IDLE: Button shows "Use My Location" with pin icon
├── LOADING: Button disabled, shows spinner + "Finding you..."
├── SUCCESS: Shows "📍 Boston" (city name), updates URL
└── ERROR: Shows "❌ Location unavailable" with retry

URL Routing on Success:
├── Extract lat/lng from geolocation API
├── Navigate to: /?lat={lat}&lng={lng}&sort=distance
└── Trigger fresh server render with geo-sorted results

UI Feedback:
├── Show city/area name in results header: "Showing deals near Boston"
├── Highlight nearby deals with distance badge
└── Add "Change location" link to clear geo params
```

**Code Structure:**
```typescript
// Pseudo-code for state machine
const [locationState, setLocationState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
const [locationName, setLocationName] = useState<string>('');

async function handleLocationClick() {
  setLocationState('loading');
  try {
    const pos = await getCurrentPosition();
    const city = await reverseGeocode(pos.lat, pos.lng); // or just use coords
    setLocationName(city);
    setLocationState('success');
    router.push(`/?lat=${pos.lat}&lng=${pos.lng}&sort=distance`);
  } catch {
    setLocationState('error');
  }
}
```

**Acceptance Criteria:**
- [ ] Loading state visible immediately on click
- [ ] City name displayed within 3 seconds on success
- [ ] URL updates with lat/lng params
- [ ] Results re-sort by distance automatically
- [ ] Error state handled gracefully (no infinite spinners)

**Dependencies:** None (uses existing geolocation API)

---

### 1.4 Fix Deal of the Day Reliability
**Effort:** 2 hours  
**Impact:** 🔥🔥🔥  
**Owner:** Backend + Frontend

**Current State:** Component exists but doesn't render (API returns null or savings threshold not met).

**Implementation Plan:**

```
Backend: /api/deal-of-the-day endpoint
├── Lower minimum savings threshold (e.g., from 30% to 15%)
├── Add fallback: if no deal meets threshold, return best available deal
├── Ensure endpoint ALWAYS returns 200 with a deal (never null)
└── Add "featured_reason" field: "Best savings today" | "Popular choice"

Frontend: DealOfTheDay component
├── Remove conditional rendering (always show if API returns data)
├── Add loading skeleton while fetching
├── Display featured_reason badge
└── Add "See all deals" link below
```

**Acceptance Criteria:**
- [ ] Deal of the Day renders on every page load
- [ ] Fallback logic ensures always a deal shown
- [ ] Component is visually prominent but doesn't block content

**Dependencies:** Backend endpoint change (trivial)

---

## Phase 2: P1 — High-Impact UX (Week 2-3)

> **Goal:** Make the app feel complete and useful for comparison shopping.

### 2.1 Make Cards Fully Clickable
**Effort:** 30 minutes  
**Impact:** 🔥🔥🔥  
**Owner:** Frontend

**Current State:** Only "Compare X stores →" link is clickable. Counterintuitive.

**Implementation:**
```typescript
// Wrap entire card in Link component
<Link href={`/product/${deal.gpid_slug}`} className="block">
  <Card className="hover:ring-2 hover:ring-primary/50 transition-all cursor-pointer">
    {/* existing card content */}
    <Button onClick={(e) => {
      e.preventDefault(); // Prevent card click when clicking CTA
      e.stopPropagation();
      // handle compare action
    }}>
      Compare stores
    </Button>
  </Card>
</Link>
```

**Acceptance Criteria:**
- [ ] Entire card navigates to detail page on click
- [ ] CTA buttons still work independently
- [ ] Hover state indicates clickability

**Dependencies:** None

---

### 2.2 Wire Up Price History Sparkline on Detail Page
**Effort:** 4 hours  
**Impact:** 🔥🔥🔥🔥  
**Owner:** Frontend + Backend

**Current State:** `PriceSparkline` component exists but isn't used on detail page.

**Implementation Plan:**

```
Backend:
├── Ensure /api/products/[slug]/history returns price history array
├── Include: date, avg_price, min_price, max_price, sample_count
└── Return last 30 days of data

Frontend:
├── Import PriceSparkline in product detail page
├── Fetch history data in page loader
├── Render sparkline below price range
├── Add tooltip on hover showing specific date/price
└── Add "Last 30 days" label

Visual Design:
├── Green line for avg price trend
├── Shaded area for min/max range
├── Highlight current price position
└── Responsive: full width on mobile, 300px on desktop
```

**Acceptance Criteria:**
- [ ] Sparkline visible on all product detail pages
- [ ] Shows 30-day price trend
- [ ] Interactive hover states
- [ ] Graceful fallback if no history data

**Dependencies:** Backend endpoint for price history (may exist)

---

### 2.3 Expand Search to Strains + Products
**Effort:** 4 hours  
**Impact:** 🔥🔥🔥🔥  
**Owner:** Frontend + Backend

**Current State:** Search only works against `brandOptions` (brand names only).

**Implementation Plan:**

```
Backend: /api/search?q={query}
├── Already supports text matching (per feedback)
├── Ensure it searches: product names, strain names, categories
├── Return: type (product | strain | brand), label, value/id
└── Limit to 10 results for autocomplete

Frontend: SearchAutocomplete component
├── Replace <datalist> with custom dropdown
├── Show grouped results:
│   ├── 🔍 Products (5)
│   ├── 🌿 Strains (3)
│   └── 🏢 Brands (2)
├── Highlight match in bold
├── Support keyboard navigation (arrows + enter)
└── Debounce input (300ms)

Search Page:
├── On submit, navigate to /search?q={query}
├── Show results grouped by type
└── Add filters for category, price range
```

**Acceptance Criteria:**
- [ ] Can search "GMO Cookies" and find products
- [ ] Can search "edible" and see category results
- [ ] Can search "Fernway" and see brand results
- [ ] Autocomplete dropdown replaces native datalist
- [ ] Keyboard navigation works

**Dependencies:** Backend search endpoint (may already exist)

---

### 2.4 Add Category Filter Counts
**Effort:** 2 hours  
**Impact:** 🔥🔥  
**Owner:** Frontend + Backend

**Current State:** Filters show "FLOWER" with no indication of result count.

**Implementation:**
```typescript
// Backend: include counts in /api/filters or /api/deals
{
  categories: [
    { id: 'flower', label: 'Flower', count: 1247 },
    { id: 'edible', label: 'Edible', count: 856 },
    // ...
  ]
}

// Frontend: update FilterPill component
<button className="filter-pill">
  FLOWER <span className="text-muted-foreground">(1,247)</span>
</button>
```

**Acceptance Criteria:**
- [ ] Each filter pill shows result count
- [ ] Counts update when other filters applied
- [ ] Format large numbers (1.2k for 1,200)

**Dependencies:** Backend to return counts with filter options

---

### 2.5 Link Dispensary Leaderboard to Store Pages
**Effort:** 1 hour  
**Impact:** 🔥🔥🔥  
**Owner:** Frontend

**Current State:** Leaderboard shows store names as plain text.

**Implementation:**
```typescript
// In leaderboard component
{stores.map(store => (
  <Link 
    key={store.id} 
    href={`/store/${store.slug}`}
    className="hover:underline hover:text-primary"
  >
    {store.name}
  </Link>
))}
```

**Acceptance Criteria:**
- [ ] Every store name in leaderboard is a link
- [ ] Links navigate to /store/[slug]
- [ ] Hover state indicates clickability

**Dependencies:** Store slugs available in leaderboard data

---

## Phase 3: P2 — Differentiation Features (Week 4-6)

> **Goal:** Add "can't stop using it" features that create retention and viral loops.

### 3.1 Price Alerts (Email Capture + Cron)
**Effort:** 2-3 days  
**Impact:** 🔥🔥🔥🔥🔥  
**Owner:** Full Stack

**The Single Most Addictive Feature.**

**Implementation Plan:**

```
Database Schema:
├── price_alerts table:
│   ├── id, user_email, gpid_id, target_price, created_at
│   ├── is_active, triggered_at, trigger_price
│   └── notification_sent_at

Frontend:
├── "Set Price Alert" button on product detail page
├── Modal: "Notify me when [Product] drops below $[input]"
├── Email input (with "we'll never spam" reassurance)
├── Confirmation: "✓ Alert set! We'll email you at [email]"
└── "Manage my alerts" link in footer

Backend Cron (Daily):
├── Query all active alerts where current_price <= target_price
├── For each triggered alert:
│   ├── Send email notification
│   ├── Mark as triggered
│   └── Include deep link to product
└── Weekly digest option: "Your price alerts this week"

Email Template:
├── Subject: "🚨 Price Drop: [Product] is now $[price]"
├── Show: product image, new price, old price, savings %
├── CTA: "Shop this deal" (deep link)
└── Footer: "Manage alerts" link
```

**Acceptance Criteria:**
- [ ] Users can set price alerts on any product
- [ ] Email captures in database
- [ ] Daily cron job checks prices
- [ ] Notification emails sent when price drops
- [ ] Users can unsubscribe/manage alerts

**Dependencies:**
- Email service (Resend already configured)
- Cron job infrastructure (Vercel cron or external)

---

### 3.2 "Shop Now" Deep Links
**Effort:** 4 hours  
**Impact:** 🔥🔥🔥🔥  
**Owner:** Frontend

**Current State:** Users see prices but can't click to buy.

**Implementation:**
```typescript
// On product detail page, for each store offering:
<StoreRow>
  <span>{store.name} - ${price}</span>
  <Button 
    variant="outline" 
    href={store.dutchie_url || store.jane_url || store.website_url}
    target="_blank"
    rel="noopener"
  >
    Shop Now →
  </Button>
</StoreRow>

// Add UTM params for attribution
const shopUrl = `${store.menu_url}?utm_source=glass&utm_medium=referral&utm_campaign=product_detail`;
```

**Acceptance Criteria:**
- [ ] Each store listing has "Shop Now" button
- [ ] Links directly to product on Dutchie/Jane
- [ ] UTM params included for tracking
- [ ] Opens in new tab

**Dependencies:** Store URLs stored in database

---

### 3.3 Share Deal Button + OG Images
**Effort:** 1 day  
**Impact:** 🔥🔥🔥🔥  
**Owner:** Full Stack

**Virality Loop: Make sharing effortless.**

**Implementation Plan:**

```
Frontend:
├── "Share this deal" button on deal cards
├── Options: Copy link, Share to Twitter/X, Share to SMS
├── Copy: "Check out this deal on GLASS: [short link]"
└── Toast confirmation: "Link copied!"

Backend: OG Image Generation
├── Route: /api/og?gpid={id}
├── Generate dynamic image with:
│   ├── Product image
│   ├── Product name + brand
│   ├── "Save $X" badge
│   ├── GLASS logo
│   └── "Compare cannabis prices"
├── Use @vercel/og or similar
└── Cache generated images

Meta Tags:
├── Update product detail page <Head>
├── og:title: "Save $46 on Fernway Sour Diesel - GLASS"
├── og:description: "Compare prices across 12 Massachusetts dispensaries"
├── og:image: /api/og?gpid={id}
└── twitter:card: summary_large_image
```

**Acceptance Criteria:**
- [ ] Share button on every deal card
- [ ] OG images generate dynamically
- [ ] Social previews look professional
- [ ] Copy link works on mobile

**Dependencies:** @vercel/og package

---

### 3.4 Saved Products / "My Brands"
**Effort:** 1 day  
**Impact:** 🔥🔥🔥🔥  
**Owner:** Frontend (localStorage first)

**Personalization without accounts (start simple).**

**Implementation:**
```typescript
// localStorage-based first
const SAVED_KEY = 'glass:saved_products';

function saveProduct(gpid: string) {
  const saved = JSON.parse(localStorage.getItem(SAVED_KEY) || '[]');
  if (!saved.includes(gpid)) {
    localStorage.setItem(SAVED_KEY, JSON.stringify([...saved, gpid]));
  }
}

// UI Components:
├── Heart icon on deal cards (toggle save)
├── "Saved" page at /saved showing all saved products
├── Badge on nav showing saved count
└── "Your saved products have new prices" banner (compare current vs saved price)

// Future: optional email sync
// When user adds email for price alerts, also sync saved products
```

**Acceptance Criteria:**
- [ ] Heart/toggle on cards to save
- [ ] /saved page lists all saved products
- [ ] Data persists across sessions
- [ ] Shows price change since saving

**Dependencies:** None (client-side only)

---

## Phase 4: P3 — Polish & Growth (Ongoing)

### 4.1 "Claim Your Store" CTA
**Effort:** 4 hours  
**Impact:** 🔥🔥🔥  
**Owner:** Frontend

**B2B Lead Gen Embedded in B2C Product.**

```typescript
// On every store mention:
<StoreName>
  {store.name}
  <Link 
    href="/claim-store?store={store.slug}" 
    className="text-xs text-muted-foreground hover:text-primary ml-2"
  >
    Is this your store?
  </Link>
</StoreName>

// /claim-store page:
├── Form: store name, contact name, email, phone
├── Verification: "We'll verify ownership within 24 hours"
└── Submit → notification to admin + email confirmation
```

---

### 4.2 Design Polish Items

| Area | Issue | Fix |
|------|-------|-----|
| Typography | Serif headline feels disconnected | Use serif ONLY for hero, keep rest mono/sans |
| Color | Green (#00E5A0) used for savings AND verification | Use green = savings only, blue checkmark for verification |
| Dark glow | Blue outer glow inconsistent | Either embrace fully or remove |
| Card density | Only 2 cards per viewport on desktop | Add compact list view toggle (like GasBuddy) |
| Footer | Just "© 2026 ROVIQ" — wasted space | Add: About, Privacy, FAQ, "Add Your Store", social links |
| Loading | Skeleton exists but not tuned | Match card dimensions exactly, avoid layout shift |
| Animations | Only hover:-translate-y-0.5 | Add staggered entrance animations on scroll |

---

## Dependencies & Blockers

### Current Blockers
| Blocker | Impact | Resolution |
|---------|--------|------------|
| Product images not in scraper data | P0 Image fix | Backend to verify Dutchie/Jane image URLs |
| Price history endpoint | P1 Sparkline | Verify /api/products/[slug]/history exists |
| Search endpoint capabilities | P1 Search expansion | Confirm /api/search supports text queries |
| Email service setup | P2 Price alerts | Resend already configured, needs domain |

### External Dependencies
- **Resend:** Email service for price alerts (configured, domain pending)
- **Cron service:** Vercel cron or external scheduler for daily price checks
- **OG image service:** @vercel/og for dynamic social images

---

## Effort Summary

| Phase | Tasks | Total Effort |
|-------|-------|--------------|
| P0 Critical | 4 tasks | ~2.5 days |
| P1 High-Impact | 5 tasks | ~2 days |
| P2 Differentiation | 4 tasks | ~5 days |
| P3 Polish | 2 tasks | ~1.5 days |
| **Total** | **15 tasks** | **~11 days** |

**Recommended Team:**
- 1 Full-stack developer (8 days)
- 1 Frontend-focused (3 days)
- Design support as needed (image assets, OG image template)

---

## Definition of Done

### P0 Complete
- [ ] All deal cards show images (product or category)
- [ ] Hero shows at least one deal above the fold
- [ ] Location button gives clear feedback and sorts results
- [ ] Deal of the Day renders reliably on every load

### P1 Complete
- [ ] Cards are fully clickable
- [ ] Price history sparkline on detail pages
- [ ] Search finds strains, products, not just brands
- [ ] Category filters show counts
- [ ] Leaderboard stores link to store pages

### P2 Complete
- [ ] Price alerts functional (set, notify, manage)
- [ ] "Shop Now" deep links on all store listings
- [ ] Share buttons with OG image generation
- [ ] Saved products feature working

### P3 Complete
- [ ] "Claim Your Store" CTA implemented
- [ ] Design polish items addressed
- [ ] Footer expanded with useful links

---

## Success Metrics

| Metric | Baseline | Target (P0) | Target (P1) | Target (P2+) |
|--------|----------|-------------|-------------|--------------|
| Image coverage | ~30% | >90% | >95% | 100% |
| Scroll depth | Unknown | >50% see first card | >70% see first card | >80% |
| Location usage | Unknown | >20% of sessions | >30% | >40% |
| Search success | Brand-only | - | Strains + products | Full text |
| Price alert signups | 0 | - | - | >100/week |
| Social shares | 0 | - | - | >50/week |

---

## Next Actions (Immediate)

1. **Today:** Verify scraper image data availability (backend check)
2. **Today:** Shrink hero height (frontend, 30 min)
3. **Day 2:** Implement location button feedback (frontend)
4. **Day 2:** Fix Deal of the Day fallback logic (backend)
5. **Week 1:** Complete P0 image fixes with category fallbacks
6. **Week 2:** Begin P1 sparkline and search expansion

---

*This plan was generated from UX audit feedback. Priority order is fixed — do not skip P0 items for P1 features. The credibility fixes must come first.*
