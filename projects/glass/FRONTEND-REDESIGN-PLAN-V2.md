# GLASS Frontend UI Redesign Plan V2
## Decision-First Architecture for Cannabis Operators

**Version:** 2.1 (Revised per Opus Review)  
**Date:** 2026-02-13  
**Status:** Phase 0 Ready for Implementation

---

## Executive Summary

This revised plan incorporates critical feedback from strategic review. The core shift remains — from "explore dashboards" to "fix your prices" — but the **execution order is corrected** to ship revenue-generating features first.

### Key Changes from V1

| Change | V1 | V2 |
|--------|-----|-----|
| Homepage | `/` → Landing.tsx | `/` → Market.tsx (public) |
| Phase 0 | Did not exist | Market-as-homepage (2-3 days) |
| Action buttons | "Match/Undercut/Hold" | "Target/Flag/Watchlist" (log intent) |
| Product matching | Assumed solved | Phase 2 hard problem |
| Pricing page | Missing | Added `/pricing` |
| Onboarding | Unchanged | Revised post-signup flow |

---

## 1. New Information Architecture

### 1.1 Route Structure (Revised)

```
PUBLIC ROUTES (No auth required)
─────────────────────────────────
/                   → Market Intelligence Homepage (was /market)
/pricing            → Pricing & plans ($199/mo, Stripe checkout)
/report/:slug       → Public report card (existing)
/login              → Clerk sign-in
/signup             → Clerk sign-up

PROTECTED ROUTES (Auth required)
─────────────────────────────────
/onboarding         → Post-signup: claim store, see report card
/products           → Product Intelligence Table (NEW HOME)
/products/:id       → SKU Detail (Phase B — slide-out first)
/alerts             → Action Queue (plain English alerts)
/report-card        → Executive Summary (v2)
/competitors        → Competitor management
/settings           → Profile, billing, preferences, watchlist
```

### 1.2 Navigation Structure

```typescript
// Sidebar Navigation (Protected Routes Only)
const navItems = [
  { path: '/products', icon: Package, label: 'Products', badge: 'home' },
  { path: '/alerts', icon: Bell, label: 'Alerts', badge: 'unread_count' },
  { path: '/report-card', icon: Target, label: 'Report Card' },
  { path: '/competitors', icon: Users2, label: 'Competitors' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

// Public Navigation (Market Homepage)
const publicNavItems = [
  { path: '/pricing', label: 'Pricing' },
  { path: '/login', label: 'Sign In' },
  { path: '/signup', label: 'Get Started', primary: true },
];
```

### 1.3 Component Kill/Keep/Build (Revised)

**KILL (Remove from routes, archive files):**

| Component | Reason | Action |
|-----------|--------|--------|
| `Landing.tsx` | Replaced by Market homepage | Delete after Phase 0 |
| `MorningBrief` | Dashboard fatigue | Remove from routes |
| `CategorySunburst` | Pretty but unused | Remove from routes |
| `BrandTreemap` | Not actionable | Remove from routes |
| `MarketTerrainMap` | Replace with table | Remove from routes |
| `DeliveryVoronoi` | Over-engineered | Remove from routes |
| `StrainStream` | No decision value | Remove from routes |
| `CategoryGrowthCurves` | Market-wide, not actionable | Remove from routes |
| `PriceChangeCascade` | Replace with alerts | Remove from routes |
| `VolatilityRibbon` | Too abstract | Remove from routes |
| `PricePositionMatrix` | Replaced by inline badges | Remove from routes |
| `ThreatNetwork` | Replace with alert list | Remove from routes |
| `MarketShareFlow` | Sankey confusion | Remove from routes |
| `OperatorComparison` | Replaced by competitor table | Remove from routes |
| `PriceWarHeatmap` | Move to SKU detail only | Conditional render only |
| `ProximityRadar` | Replace with sorted table | Remove from routes |
| `PriceTicker` | Visual noise | Remove from routes |

**KEEP (Existing components to retain):**

| Component | Usage |
|-----------|-------|
| `Sidebar` | Update nav items only |
| `TopBar` | Keep, add export actions |
| `DashboardLayout` | Keep as wrapper |
| `EmptyState` | Reuse for zero states |
| `DataFreshness` | Keep in footer |
| `ErrorBoundary` | Keep as-is |
| `ReportCardSkeleton` | Adapt for v2 |
| `StatCard` | Use in report card header |
| `MiniChart` | Use for sparklines only |
| `Market.tsx` | **ENHANCE** — becomes homepage |

**BUILD (New components, prioritized):**

| Component | Phase | Description |
|-----------|-------|-------------|
| `MarketHomepage` | 0 | Enhanced Market.tsx with email signup |
| `PricingPage` | 0 | $199/mo plan details, Stripe checkout |
| `EmailSignupHero` | 0 | Hero section with waitlist form |
| `ProductIntelligenceTable` | A | Main dense table with competitive context |
| `PricePositionBadge` | A | Color-coded position indicator |
| `TargetPriceButtons` | A | Log intent, not execute (renamed from QuickActionButtons) |
| `FilterBar` | A | Sticky filter controls |
| `ExportButton` | A | CSV export with current filters |
| `AlertFeed` | C | Plain English alert cards |
| `AlertActionCard` | C | Alert with embedded actions |
| `ReportCardV2` | D | Rewritten executive view |
| `RepriceQueueTable` | D | Top SKUs to reprice |
| `MissingSKUTable` | D | High-demand missing products |
| `MarginLeakTable` | D | Category margin analysis |
| `SKUDetailView` | B | Single SKU deep-dive layout |
| `CompetitorPriceTable` | B | Nearby store price comparison |
| `PriceHistoryChart` | B | Simple 2-line time series |
| `OnboardingFlow` | D | Post-signup: claim store, see report |
| `SettingsPage` | D | Profile, billing, preferences, watchlist |

---

## 2. Phase 0: Market-as-Homepage (Ships in DAYS)

### 2.1 Overview

**Duration:** 3-5 days  
**Goal:** Unblock outreach emails immediately  
**Uses ONLY existing code/endpoints**

This phase transforms the existing `/market` page into the public homepage at `/`, adds email capture, and creates a pricing page. It requires **no new backend work** — only frontend changes.

### 2.2 Changes Required

#### App.tsx Route Updates

```typescript
// BEFORE
<Route path="/" element={
  <>
    <SignedOut><Landing /></SignedOut>
    <SignedIn><DashboardEntry /></SignedIn>
  </>
} />

// AFTER
<Route path="/" element={
  <>
    <SignedOut><MarketHomepage /></SignedOut>
    <SignedIn><Navigate to="/products" replace /></SignedIn>
  </>
} />
<Route path="/market" element={<Navigate to="/" replace />} />
<Route path="/landing" element={<Navigate to="/" replace />} />
```

#### MarketHomepage Component (Enhanced Market.tsx)

**New Hero Section with Email Signup:**

```typescript
// Hero section replaces current CTA buttons
const HeroWithEmailSignup = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // POST to existing /api/v1/waitlist endpoint
    await fetch('/api/v1/waitlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, source: 'homepage_hero' })
    });
    setSubmitted(true);
  };
  
  return (
    <div className="hero-section">
      <h1>The most complete picture of Massachusetts cannabis pricing</h1>
      <p>Updated daily from 200+ licensed retailers. Cross-referenced with CCC data.</p>
      
      {submitted ? (
        <div className="success-message">Thanks! We'll be in touch soon.</div>
      ) : (
        <form onSubmit={handleSubmit} className="email-signup">
          <input 
            type="email" 
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button type="submit">Get Early Access</button>
        </form>
      )}
      
      <p className="secondary-cta">
        Already tracking your store? <a href="/login">Sign in</a>
      </p>
    </div>
  );
};
```

**Remove from Market.tsx:**
- ❌ Demographics section (donut charts of gender/race)
- ❌ Blurred dashboard teaser with deprecated viz components
- ❌ "Premium Data Teaser" section

**Add to Market.tsx:**
- ✅ Email signup hero (above the fold)
- ✅ Clear CTA: "See your store's report card" → links to `/signup` or `/report/:slug`
- ✅ Data freshness stats prominently displayed
- ✅ CCC cross-reference badge

#### Pricing Page (`/pricing`)

```typescript
// Simple pricing page component
const PricingPage = () => {
  return (
    <div className="pricing-page">
      <h1>Track your competitive position</h1>
      <p>Know exactly where you stand on every SKU, every day.</p>
      
      <div className="pricing-card">
        <h2>Professional</h2>
        <div className="price">$199<span>/month</span></div>
        <p className="billing">Billed monthly. Cancel anytime.</p>
        
        <ul className="features">
          <li>✓ Full product intelligence table</li>
          <li>✓ Unlimited competitor tracking</li>
          <li>✓ Daily price alerts</li>
          <li>✓ Weekly report card (PDF export)</li>
          <li>✓ 25-mile radius coverage</li>
          <li>✓ Email support</li>
        </ul>
        
        <a 
          href="https://buy.stripe.com/5kQ4gA8YR8pYc8H0jmcfK0b" 
          className="cta-button"
        >
          Start 14-Day Free Trial
        </a>
        
        <p className="guarantee">14-day money-back guarantee</p>
      </div>
      
      <div className="faq-section">
        <h3>Frequently Asked Questions</h3>
        <details>
          <summary>How does the free trial work?</summary>
          <p>Sign up and get full access for 14 days. No credit card required.</p>
        </details>
        <details>
          <summary>Can I track competitors outside my radius?</summary>
          <p>Professional plan includes up to 25 miles. Contact us for custom coverage.</p>
        </details>
        <details>
          <summary>How often is data updated?</summary>
          <p>We scan menus daily. Price changes typically appear within 24 hours.</p>
        </details>
      </div>
    </div>
  );
};
```

### 2.3 API Endpoints for Phase 0

**EXISTING — Use As-Is (No new backend work):**

| Endpoint | Usage in Phase 0 |
|----------|------------------|
| `GET /api/v1/market/stats` | Market stats for hero section |
| `GET /api/v1/market/weekly-sales` | Weekly sales chart |
| `GET /api/v1/market/license-pipeline` | License pipeline data |
| `GET /api/v1/waitlist` | Email signup (POST) |
| `GET /api/v1/report-card/:slug` | Public report cards |

**NO NEW ENDPOINTS REQUIRED FOR PHASE 0**

### 2.4 Success Criteria for Phase 0

- [ ] `/` shows Market data with email signup hero
- [ ] `/market` redirects to `/`
- [ ] `/landing` redirects to `/`
- [ ] `/pricing` page live with Stripe checkout link
- [ ] Signed-in users redirect from `/` to `/products`
- [ ] Email signups POST to `/api/v1/waitlist` successfully
- [ ] 24 outreach emails can be sent pointing to new homepage

---

## 3. Revised Implementation Phases

### Phase 0: Market-as-Homepage (3-5 days) — SHIP FIRST
**Goal:** Unblock outreach emails immediately  
**Uses ONLY existing code/endpoints**

- [ ] Move `/market` content to `/` for signed-out users
- [ ] Add email signup form in hero section (POST to `/api/v1/waitlist`)
- [ ] Remove demographics section from Market page
- [ ] Remove blurred dashboard teaser
- [ ] Add CTA: "See your store's report card" → `/signup` or `/report/:slug`
- [ ] Create `/pricing` page ($199/mo, Stripe link)
- [ ] Signed-in users redirect `/` → `/products`
- [ ] Kill `Landing.tsx`
- [ ] Update SEO meta tags

**Shippable:** YES — enables immediate outreach

---

### Phase A: Product Intelligence MVP (1-2 weeks)
**Goal:** Core product table with filters  
**Uses EXISTING endpoints only**

- [ ] Build `ProductIntelligenceTable` component
- [ ] Build `FilterBar` with category/brand/weight filters
- [ ] Build `PricePositionBadge` (category-level benchmarks)
- [ ] Build `TargetPriceButtons` (log intent, not execute)
- [ ] Create `/products` route (auth required)
- [ ] Use `GET /api/v1/catalog/:operator_id/products` for product list
- [ ] Use `GET /api/v1/products` + aggregation for category benchmarks
- [ ] Position badges based on operator's price vs category average (not per-SKU matching)
- [ ] Add data freshness indicators (use `scraped_at` timestamps)
- [ ] Add CSV export button

**Key Constraint:** NO per-SKU competitive matching yet. Show category-level benchmarks only.

**Shippable:** YES — operators can see their products with category benchmarks

---

### Phase B: Product Matching Engine + Competitive Context (2-3 weeks)
**Goal:** Real per-SKU competitive intelligence  
**Requires NEW backend endpoint**

- [ ] Build product matching engine (backend)
- [ ] Implement fuzzy matching: brand normalization + trigram similarity on product name
- [ ] Extract and normalize weight fields (1g, 3.5g, 7g, etc.)
- [ ] Build `GET /api/v1/products/competitive-context` endpoint
- [ ] Add radius-based filtering
- [ ] Upgrade `ProductIntelligenceTable` with real competitive stats
- [ ] Build `SKUDetailView` as slide-out panel (not separate route)
- [ ] Build `CompetitorPriceTable` component
- [ ] Build `PriceHistoryChart` (simple 2-line time series)

**Technical Risk:** Product matching is the hardest problem. May need iterative refinement.

**Shippable:** YES — full competitive intelligence

---

### Phase C: Alert Engine + Action Queue (2 weeks)
**Goal:** Proactive decision notifications  
**Uses existing alert endpoints + enhancements**

- [ ] Rewrite `/alerts` page with plain English cards
- [ ] Build `AlertFeed` component
- [ ] Build `AlertActionCard` component
- [ ] Create alert generation service (backend)
- [ ] Enhance `GET /api/v1/alerts` with action payloads
- [ ] Build `POST /api/v1/alerts/:id/action` endpoint (logs intent)
- [ ] Create alert templates for common scenarios
- [ ] Add unread count badge to nav

**Shippable:** YES — proactive notifications

---

### Phase D: Report Card v2 + Onboarding Flow (1-2 weeks)
**Goal:** Executive summary + improved onboarding  
**Enhances existing report card**

- [ ] Rewrite `/report-card` page
- [ ] Build `RepriceQueueTable` component
- [ ] Build `MissingSKUTable` component
- [ ] Build `MarginLeakTable` component
- [ ] Build `ExportButton` with CSV/PDF options
- [ ] Enhance `GET /api/v1/report-card/:id` for v2 format
- [ ] Revise `/onboarding` flow: claim store → see report card → explore products
- [ ] Build `/settings` page: profile, billing, preferences, watchlist

**Shippable:** YES — executive reporting + onboarding

---

## 4. API Endpoint Inventory (Realistic)

### 4.1 Existing Endpoints (Working Today)

| Endpoint | Status | Usage |
|----------|--------|-------|
| `GET /api/v1/market/stats` | ✅ EXISTS | Market stats for homepage |
| `GET /api/v1/market/weekly-sales` | ✅ EXISTS | Weekly sales chart |
| `GET /api/v1/market/license-pipeline` | ✅ EXISTS | License pipeline data |
| `GET /api/v1/waitlist` | ✅ EXISTS | Email signup (POST) |
| `GET /api/v1/products` | ✅ EXISTS | Product search & filter |
| `GET /api/v1/prices/movers` | ✅ EXISTS | Price change detection |
| `GET /api/v1/catalog/:operator_id/products` | ✅ EXISTS | Operator's own products |
| `GET /api/v1/report-card/:operator_id` | ✅ EXISTS | Report card data |
| `GET /api/v1/operators` | ✅ EXISTS | Competitor lookup |
| `GET /api/v1/scores/leaderboard` | ✅ EXISTS | Health scoring |
| `GET /api/v1/threats/feed` | ✅ EXISTS | Threat detection |
| `GET /api/v1/recommendations` | ✅ EXISTS | Price recommendations |
| `GET /api/v1/alerts` | ✅ EXISTS | Alert feed |

### 4.2 New Endpoints Required (With Effort Estimates)

| Endpoint | Priority | Effort | Risk | Description |
|----------|----------|--------|------|-------------|
| `GET /api/v1/products/competitive-context` | P1 | 1-2 weeks | **HIGH** | Per-operator competitive stats. Requires product matching engine. |
| `GET /api/v1/products/:id/competitive-landscape` | P1 | 3-5 days | MEDIUM | Single SKU competitive view. Depends on competitive-context. |
| `POST /api/v1/alerts/:id/action` | P2 | 1-2 days | LOW | Log alert action intent. Simple metadata update. |
| `GET /api/v1/report-card/:id/v2` | P2 | 3-5 days | LOW | Enhanced report card. Builds on existing endpoint. |
| `GET /api/v1/export/pricing` | P2 | 2-3 days | LOW | CSV export. Simple query + formatting. |
| `POST /api/v1/price-targets` | P2 | 2-3 days | LOW | Log price target intent. New table: `price_targets`. |

### 4.3 Endpoints REMOVED from Plan

| Endpoint | Reason |
|----------|--------|
| `POST /api/v1/prices/bulk-update` | GLASS cannot write to operator menus. No POS integration. |

---

## 5. The Product Matching Problem (Phase 2)

### 5.1 The Challenge

Products from different scraped stores are **NOT** the same `product_id`. Competitive context requires fuzzy matching across:

- Brand name (normalized: "Cookies" = "COOKIES")
- Product name (trigram similarity for typos/variations)
- Weight (extracted and normalized: "3.5g" = "1/8th" = "eighth")
- Category (flower, pre-roll, vape, etc.)

### 5.2 Matching Approach

```typescript
// Product matching algorithm (Phase 2)
interface ProductMatcher {
  // Step 1: Brand normalization
  normalizeBrand(brand: string): string;
  // "Cookies" → "cookies"
  // "COOKIES" → "cookies"
  // "Cookies™" → "cookies"
  
  // Step 2: Weight extraction
  extractWeight(name: string): { grams: number; normalized: string } | null;
  // "Gelato 3.5g" → { grams: 3.5, normalized: "3.5g" }
  // "Gelato 1/8th" → { grams: 3.5, normalized: "3.5g" }
  // "Gelato Eighth" → { grams: 3.5, normalized: "3.5g" }
  
  // Step 3: Name similarity (trigram)
  calculateSimilarity(name1: string, name2: string): number;
  // "Gelato" vs "Gelato" → 1.0
  // "Gelato" vs "Gelato Flower" → 0.85
  // "Gelato" vs "Wedding Cake" → 0.2
  
  // Step 4: Match decision
  isMatch(productA: Product, productB: Product): boolean;
  // Same normalized brand + similar name + same weight + same category
}
```

### 5.3 Database Schema Addition

```sql
-- New table for product matches (Phase 2)
CREATE TABLE product_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id_1 UUID REFERENCES products(id),
  product_id_2 UUID REFERENCES products(id),
  match_confidence DECIMAL(3,2), -- 0.00 to 1.00
  match_type VARCHAR(50), -- 'exact', 'fuzzy_brand', 'fuzzy_name'
  verified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(product_id_1, product_id_2)
);

-- Index for match lookups
CREATE INDEX idx_product_matches_lookup 
  ON product_matches(product_id_1, match_confidence DESC);
```

### 5.4 Why This Is Phase 2

Product matching requires:
1. Algorithm development and testing
2. Database migrations
3. Backfill of historical matches
4. Confidence threshold tuning
5. Edge case handling (new products, discontinued products)

**Phase 1 uses category-level benchmarks** (no matching needed):
- "Your average flower price: $42/unit"
- "Market average flower price: $38/unit"
- "Your position: 10% above market"

This requires zero product matching and uses data already in the database.

---

## 6. Action Buttons: Honest Design

### 6.1 The Reality

GLASS cannot write to operator menus. There is no POS integration. When an operator clicks a button, GLASS can only:

1. **Log the intent** — "Operator wants to target $42 for SKU X"
2. **Generate a task** — Plain text instruction for the operator
3. **Track follow-through** — Compare next scrape to see if price changed

### 6.2 Button Redesign

**OLD (Fiction):**
```typescript
interface ProductActionButtons {
  matchMedian: () => void;      // "Match $42" — implies execution
  undercutDollar: () => void;   // "Undercut $1" — implies execution
  holdPremium: () => void;      // "Hold +$3" — implies execution
}
```

**NEW (Honest):**
```typescript
interface ProductActionButtons {
  // Log intent to price_targets table
  targetPrice: (price: number) => void;     // "Target $42"
  flagForReview: () => void;                 // "Flag for review"
  addToWatchlist: () => void;                // "Add to watchlist"
}

// New table for price targets
interface PriceTarget {
  id: string;
  operator_id: string;
  product_id: string;
  current_price: number;
  target_price: number;
  status: 'pending' | 'acknowledged' | 'implemented' | 'dismissed';
  created_at: string;
  updated_at: string;
}
```

### 6.3 UI Implementation

```typescript
// Action button group for each product row
const ProductActions = ({ product, yourPrice, marketMedian }) => {
  const [showWorkflow, setShowWorkflow] = useState(false);
  const [targetPrice, setTargetPrice] = useState(marketMedian);
  
  const handleTarget = async () => {
    // Log intent to backend
    await fetch('/api/v1/price-targets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_id: product.id,
        current_price: yourPrice,
        target_price: targetPrice
      })
    });
    setShowWorkflow(true);
  };
  
  if (showWorkflow) {
    return (
      <div className="workflow-panel">
        <p>✓ Target logged: ${targetPrice}</p>
        <p className="instructions">
          To implement: Log into your POS and change {product.sku} to ${targetPrice}.
          We'll verify the change on our next scan.
        </p>
        <button onClick={() => setShowWorkflow(false)}>Done</button>
      </div>
    );
  }
  
  return (
    <div className="action-buttons">
      <button 
        className="btn-primary"
        onClick={handleTarget}
      >
        Target ${marketMedian}
      </button>
      <button 
        className="btn-secondary"
        onClick={() => {/* Flag for review */}}
      >
        Flag
      </button>
      <button 
        className="btn-secondary"
        onClick={() => {/* Add to watchlist */}}
      >
        Watch
      </button>
    </div>
  );
};
```

---

## 7. API Endpoint Inventory (Realistic)

### 7.1 Existing Endpoints (Working Today)

| Endpoint | Status | Usage |
|----------|--------|-------|
| `GET /api/v1/market/stats` | ✅ EXISTS | Market stats for homepage |
| `GET /api/v1/market/weekly-sales` | ✅ EXISTS | Weekly sales chart |
| `GET /api/v1/market/license-pipeline` | ✅ EXISTS | License pipeline data |
| `GET /api/v1/waitlist` | ✅ EXISTS | Email signup (POST) |
| `GET /api/v1/products` | ✅ EXISTS | Product search & filter |
| `GET /api/v1/prices/movers` | ✅ EXISTS | Price change detection |
| `GET /api/v1/catalog/:operator_id/products` | ✅ EXISTS | Operator's own products |
| `GET /api/v1/report-card/:operator_id` | ✅ EXISTS | Report card data |
| `GET /api/v1/operators` | ✅ EXISTS | Competitor lookup |
| `GET /api/v1/scores/leaderboard` | ✅ EXISTS | Health scoring |
| `GET /api/v1/threats/feed` | ✅ EXISTS | Threat detection |
| `GET /api/v1/recommendations` | ✅ EXISTS | Price recommendations |
| `GET /api/v1/alerts` | ✅ EXISTS | Alert feed |

### 7.2 New Endpoints Required (With Effort Estimates)

| Endpoint | Priority | Effort | Risk | Description |
|----------|----------|--------|------|-------------|
| `GET /api/v1/products/competitive-context` | P1 | 1-2 weeks | **HIGH** | Per-operator competitive stats. Requires product matching engine. |
| `GET /api/v1/products/:id/competitive-landscape` | P1 | 3-5 days | MEDIUM | Single SKU competitive view. Depends on competitive-context. |
| `POST /api/v1/price-targets` | P2 | 1-2 days | LOW | Log price target intent. New table. |
| `POST /api/v1/alerts/:id/action` | P2 | 1-2 days | LOW | Log alert action intent. |
| `GET /api/v1/report-card/:id/v2` | P2 | 3-5 days | LOW | Enhanced report card. Builds on existing. |
| `GET /api/v1/export/pricing` | P2 | 2-3 days | LOW | CSV export. Simple query + formatting. |

### 7.3 Endpoints REMOVED from Plan

| Endpoint | Reason |
|----------|--------|
| `POST /api/v1/prices/bulk-update` | GLASS cannot write to operator menus. No POS integration. |

---

## 8. Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Product Matching Engine** | High | High | Start with category benchmarks (Phase A). Build matching as progressive enhancement (Phase B). Use brand + weight + trigram similarity. |
| **Stale Data Display** | High | Medium | Add `scraped_at` timestamps to all price displays. Badge rows >48h old. Show "last updated" prominently. |
| **Query Performance** | Medium | High | Add indexes (see Appendix B). Use materialized views for competitive stats. Cache aggressively. |
| **Action Button Confusion** | Medium | Medium | Rename to "Target" (not "Match"). Show workflow panel explaining manual steps. Track follow-through on next scrape. |
| **Mobile Experience** | Low | Medium | Build responsive tables from start. Don't create separate mobile components. |
| **Alert Fatigue** | Medium | Medium | Smart throttling. Preference controls in settings. Severity filtering. |
| **No Customers During Build** | High | High | **Phase 0 ships first.** Collect emails while building paid product. |

---

## 9. Component Inventory (Final)

### 9.1 NEW Components to Build (Prioritized)

| Component | Phase | Location | Description |
|-----------|-------|----------|-------------|
| `MarketHomepage` | 0 | `/pages/` | Enhanced Market.tsx with email signup |
| `EmailSignupHero` | 0 | `/components/market/` | Hero section with waitlist form |
| `PricingPage` | 0 | `/pages/` | $199/mo plan, Stripe checkout |
| `ProductIntelligenceTable` | A | `/components/products/` | Main dense table |
| `PricePositionBadge` | A | `/components/products/` | Color-coded position indicator |
| `TargetPriceButtons` | A | `/components/products/` | Log intent (not execute) |
| `FilterBar` | A | `/components/products/` | Sticky filter controls |
| `ExportButton` | A | `/components/shared/` | CSV export |
| `DataFreshnessIndicator` | A | `/components/shared/` | Stale data badge |
| `ProductMatchingEngine` | B | Backend | Fuzzy matching algorithm |
| `SKUDetailSlideout` | B | `/components/products/` | Slide-out panel (not route) |
| `CompetitorPriceTable` | B | `/components/products/` | Nearby store comparison |
| `PriceHistoryChart` | B | `/components/products/` | Simple 2-line time series |
| `AlertFeed` | C | `/components/alerts/` | Plain English alert cards |
| `AlertActionCard` | C | `/components/alerts/` | Alert with actions |
| `ReportCardV2` | D | `/components/report-card/` | Executive view |
| `RepriceQueueTable` | D | `/components/report-card/` | Top SKUs to reprice |
| `MissingSKUTable` | D | `/components/report-card/` | High-demand missing products |
| `MarginLeakTable` | D | `/components/report-card/` | Category margin analysis |
| `OnboardingFlow` | D | `/pages/` | Post-signup: claim → report → products |
| `SettingsPage` | D | `/pages/` | Profile, billing, preferences, watchlist |

### 9.2 EXISTING Components to Keep

| Component | Usage |
|-----------|-------|
| `Sidebar` | Update nav items only |
| `TopBar` | Keep, add export actions |
| `DashboardLayout` | Keep as wrapper |
| `EmptyState` | Reuse for zero states |
| `DataFreshness` | Keep in footer |
| `ErrorBoundary` | Keep as-is |
| `ReportCardSkeleton` | Adapt for v2 |
| `StatCard` | Use in report card header |
| `MiniChart` | Use for sparklines only |
| `Market.tsx` | **ENHANCE** — becomes homepage |

### 9.3 EXISTING Components to Deprecate

| Component | Reason | Action |
|-----------|--------|--------|
| `Landing.tsx` | Replaced by Market homepage | Delete after Phase 0 |
| `MorningBrief` | Dashboard fatigue | Remove from routes |
| `CategorySunburst` | Pretty but unused | Remove from routes |
| `BrandTreemap` | Not actionable | Remove from routes |
| `MarketTerrainMap` | Replace with table | Remove from routes |
| `DeliveryVoronoi` | Over-engineered | Remove from routes |
| `StrainStream` | No decision value | Remove from routes |
| `CategoryGrowthCurves` | Market-wide, not actionable | Remove from routes |
| `PriceChangeCascade` | Replace with alerts | Remove from routes |
| `VolatilityRibbon` | Too abstract | Remove from routes |
| `PricePositionMatrix` | Replaced by inline badges | Remove from routes |
| `ThreatNetwork` | Replace with alert list | Remove from routes |
| `MarketShareFlow` | Sankey confusion | Remove from routes |
| `OperatorComparison` | Replaced by competitor table | Remove from routes |
| `PriceWarHeatmap` | Move to SKU detail only | Conditional render only |
| `ProximityRadar` | Replace with sorted table | Remove from routes |
| `PriceTicker` | Visual noise | Remove from routes |

---

## 10. Database Schema Additions

### 10.1 New Tables

```sql
-- Price targets (logged intent, not executed)
CREATE TABLE price_targets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID REFERENCES operators(id),
  product_id UUID REFERENCES products(id),
  current_price DECIMAL(10,2),
  target_price DECIMAL(10,2),
  status VARCHAR(50) DEFAULT 'pending', -- pending, acknowledged, implemented, dismissed
  source VARCHAR(50), -- 'user_action', 'alert', 'recommendation'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_price_targets_operator ON price_targets(operator_id, status);
CREATE INDEX idx_price_targets_product ON price_targets(product_id);

-- Product matches (for competitive context)
CREATE TABLE product_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id_1 UUID REFERENCES products(id),
  product_id_2 UUID REFERENCES products(id),
  match_confidence DECIMAL(3,2), -- 0.00 to 1.00
  match_type VARCHAR(50), -- 'exact', 'fuzzy_brand', 'fuzzy_name', 'manual'
  verified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(product_id_1, product_id_2)
);

CREATE INDEX idx_product_matches_lookup ON product_matches(product_id_1, match_confidence DESC);
CREATE INDEX idx_product_matches_reverse ON product_matches(product_id_2, match_confidence DESC);

-- Watchlist
CREATE TABLE watchlist_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID REFERENCES operators(id),
  product_id UUID REFERENCES products(id),
  alert_threshold DECIMAL(10,2), -- optional price threshold for alerts
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_watchlist_operator ON watchlist_items(operator_id);
```

### 10.2 Indexes for Performance

```sql
-- For competitive context queries
CREATE INDEX idx_prices_product_operator_scraped 
  ON prices(product_id, operator_id, scraped_at DESC);

CREATE INDEX idx_prices_operator_scraped 
  ON prices(operator_id, scraped_at DESC);

-- For nearby operator queries  
CREATE INDEX idx_operators_location 
  ON operators USING gist(ll_to_earth(lat, lon));

-- For product filtering
CREATE INDEX idx_products_category_brand 
  ON products(category, brand);

-- For price history
CREATE INDEX idx_prices_product_scraped 
  ON prices(product_id, scraped_at DESC);
```

---

## 11. Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Product Matching Engine** | High | High | Start with category benchmarks (Phase A). Build matching as progressive enhancement (Phase B). Use brand + weight + trigram similarity. |
| **Stale Data Display** | High | Medium | Add `scraped_at` timestamps to all price displays. Badge rows >48h old. Show "last updated" prominently. |
| **Query Performance** | Medium | High | Add indexes (see Section 10.2). Use materialized views for competitive stats. Cache aggressively. |
| **Action Button Confusion** | Medium | Medium | Rename to "Target" (not "Match"). Show workflow panel explaining manual steps. Track follow-through on next scrape. |
| **Mobile Experience** | Low | Medium | Build responsive tables from start. Don't create separate mobile components. |
| **Alert Fatigue** | Medium | Medium | Smart throttling. Preference controls in settings. Severity filtering. |
| **No Customers During Build** | High | High | **Phase 0 ships first.** Collect emails while building paid product. |

---

## 12. Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Homepage email conversion | 0% | >5% | Signups / visitors |
| Time to first decision | 3+ clicks | 1 click | User testing |
| Price target rate | <5% | >15% | Button click analytics |
| Alert engagement | TBD | >50% open rate | Alert tracking |
| Export usage | 0 | >20% weekly | Export analytics |
| Mobile usage | TBD | >40% of sessions | Analytics |
| Page load time | 4s | <2s | Web vitals |
| Support questions | High | -50% | Support tickets |

---

## 13. Implementation Checklist

### Phase 0 (Ready to Start)

- [ ] **App.tsx:** Update routes (Market as `/`, kill Landing)
- [ ] **MarketHomepage:** Add email signup form to hero
- [ ] **MarketHomepage:** Remove demographics section
- [ ] **MarketHomepage:** Remove blurred dashboard teaser
- [ ] **MarketHomepage:** Add "See your store's report card" CTA
- [ ] **PricingPage:** Create `/pricing` with Stripe link
- [ ] **Auth:** Signed-in redirect `/` → `/products`
- [ ] **SEO:** Update meta tags for new homepage
- [ ] **Test:** Email signup POSTs to `/api/v1/waitlist`
- [ ] **Deploy:** Ready for outreach emails

---

## Appendix A: Mobile Wireframes

### Mobile Alerts (Primary View)
```
┌─────────────────┐
│ GLASS    🔔 3   │
├─────────────────┤
│ TODAY'S ACTIONS │
├─────────────────┤
│ 🔴 URGENT       │
│ You are losing  │
│ preroll share   │
│                 │
│ [Target $16]    │
├─────────────────┤
│ 💡 RECOMMEND    │
│ Raise price on  │
│ Cookies Gelato  │
│                 │
│ [Target $48]    │
├─────────────────┤
│ [See All 8]     │
└─────────────────┘
```

### Mobile Product List (Simplified)
```
┌─────────────────┐
│ Products   🔍   │
├─────────────────┤
│ [Flower ▼] 5mi  │
├─────────────────┤
│ Cookies Gelato  │
│ $45.00  +7% ▲   │
│ [Target $42]    │
├─────────────────┤
│ Big Pine Pre    │
│ $18.00 +12% ▲   │
│ [Target $16]    │
└─────────────────┘
```

---

## Appendix B: Database Index Recommendations

```sql
-- For competitive context queries
CREATE INDEX idx_prices_product_operator_scraped 
  ON prices(product_id, operator_id, scraped_at DESC);

CREATE INDEX idx_prices_operator_scraped 
  ON prices(operator_id, scraped_at DESC);

-- For nearby operator queries  
CREATE INDEX idx_operators_location 
  ON operators USING gist(ll_to_earth(lat, lon));

-- For product filtering
CREATE INDEX idx_products_category_brand 
  ON products(category, brand);

-- For price history
CREATE INDEX idx_prices_product_scraped 
  ON prices(product_id, scraped_at DESC);
```

---

**END OF REVISED PLAN**

*Phase 0 is ready for immediate implementation. All other phases await Phase 0 completion.*
