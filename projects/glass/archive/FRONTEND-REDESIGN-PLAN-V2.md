# GLASS Frontend UI Redesign Plan V2.1
## Decision-First Architecture for Cannabis Operators

**Version:** 2.1 (Enhanced per Opus Review)  
**Date:** 2026-02-13  
**Status:** Phase 0 Ready for Implementation — START HERE

---

## 🎯 WHAT TO BUILD FIRST (Priority Order)

**Read this section first. If you do nothing else, complete Phase 0.**

### Phase 0 Checklist (Days 1-3) — START HERE

| # | Task | File to Edit | Notes |
|---|------|--------------|-------|
| 1 | Update App.tsx routes | `src/apps/web/src/App.tsx` | Change `/` to show Market for signed-out, redirect signed-in to `/products` |
| 2 | Create PricingPage | `src/apps/web/src/pages/Pricing.tsx` | New file with Stripe checkout |
| 3 | Add email signup to Market | `src/apps/web/src/pages/Market.tsx` | Add hero form, remove demographics |
| 4 | Update navigation | `src/apps/web/src/components/LandingNav.tsx` | Add Pricing link |
| 5 | Kill Landing.tsx | Delete after test | Replaced by Market homepage |
| 6 | Test email flow | Manual test | POST to `/api/v1/waitlist` |

**These 6 tasks unblock outreach emails. Complete before anything else.**

---

## Executive Summary

This revised plan incorporates critical feedback from strategic review. The core shift remains — from "explore dashboards" to "fix your prices" — but the **execution order is corrected** to ship revenue-generating features first.

### Key Changes from V1

| Change | V1 | V2.1 |
|--------|-----|-----|
| Homepage | `/` → Landing.tsx | `/` → Market.tsx (public) |
| Phase 0 | Did not exist | Market-as-homepage (3 days) |
| Action buttons | "Match/Undercut/Hold" | "Target/Flag/Watchlist" (log intent) |
| Product matching | Assumed solved | Phase 2 — acknowledged as hard problem |
| Pricing page | Missing | Added `/pricing` with Stripe |
| What to build first | Unclear | This document — 6-task checklist above |

---

## 1. New Information Architecture

### 1.1 Route Structure (Phase 0 Ready)

```
PUBLIC ROUTES (No auth required)
─────────────────────────────────
/                   → Market Intelligence Homepage (was /market)
/pricing            → Pricing & plans ($199/mo, Stripe checkout) ← NEW
/report/:slug       → Public report card (existing)
/login              → Clerk sign-in
/signup             → Clerk sign-up

PROTECTED ROUTES (Auth required) — Build after Phase 0
───────────────────────────────────────────────────────
/products           → Product Intelligence Table (NEW HOME after login)
/products/:id       → SKU Detail (Phase B — slide-out first)
/alerts             → Action Queue (plain English alerts)
/report-card        → Executive Summary (v2)
/competitors        → Competitor management
/settings           → Profile, billing, preferences, watchlist
```

### 1.2 App.tsx Changes Required (EXACT CODE)

**File:** `src/apps/web/src/App.tsx`

**BEFORE (Current):**
```typescript
<Route path="/" element={
  <>
    <SignedOut><Landing /></SignedOut>
    <SignedIn><DashboardEntry /></SignedIn>
  </>
} />
<Route path="/market" element={<Market />} />
```

**AFTER (Phase 0):**
```typescript
// Phase 0: Market homepage with email signup
<Route path="/" element={
  <>
    <SignedOut><Market /></SignedOut>
    <SignedIn><Navigate to="/products" replace /></SignedIn>
  </>
} />

// Phase 0: Redirect old routes
<Route path="/market" element={<Navigate to="/" replace />} />
<Route path="/landing" element={<Navigate to="/" replace />} />

// Phase 0: NEW Pricing page
<Route path="/pricing" element={<Pricing />} />
```

**You also need to:**
1. Add `import Pricing from './pages/Pricing';` at the top
2. Create the `Pricing.tsx` file (code below)
3. Update signed-in redirect from `DashboardEntry` to `/products` route

### 1.3 Navigation Update Required

**File:** `src/apps/web/src/components/LandingNav.tsx`

Add pricing link to public nav:
```typescript
const publicNavItems = [
  { path: '/pricing', label: 'Pricing' },
  { path: '/login', label: 'Sign In' },
  { path: '/signup', label: 'Get Started', primary: true },
];
```

---

## 2. Phase 0: Market-as-Homepage (Ships in DAYS)

### 2.1 Overview

**Duration:** 3 days maximum  
**Goal:** Unblock outreach emails immediately  
**Uses ONLY existing code/endpoints — no backend work needed**

### 2.2 Deliverables

#### 2.2.1 Pricing Page (`/pricing`) — CREATE NEW FILE

**File:** `src/apps/web/src/pages/Pricing.tsx`

```typescript
import { Link } from 'react-router-dom';
import { Check } from 'lucide-react';
import { LandingNav } from '../components/LandingNav';
import { Footer } from '../components/Footer';

const Pricing = () => {
  return (
    <div className="min-h-screen bg-glass-black">
      <LandingNav />
      
      <main className="mx-auto max-w-4xl px-4 py-20">
        <div className="text-center mb-16">
          <h1 className="font-display text-4xl font-medium text-white mb-4">
            Track your competitive position
          </h1>
          <p className="text-xl text-glass-muted">
            Know exactly where you stand on every SKU, every day.
          </p>
        </div>

        {/* Pricing Card */}
        <div className="mx-auto max-w-md rounded-2xl border border-glass-border bg-glass-surface p-8">
          <div className="text-center mb-8">
            <h2 className="font-display text-2xl text-white mb-2">Professional</h2>
            <div className="flex items-baseline justify-center gap-1">
              <span className="text-5xl font-medium text-white">$199</span>
              <span className="text-glass-muted">/month</span>
            </div>
            <p className="mt-2 text-sm text-glass-subtle">Billed monthly. Cancel anytime.</p>
          </div>

          <ul className="space-y-4 mb-8">
            {[
              'Full product intelligence table',
              'Unlimited competitor tracking',
              'Daily price alerts',
              'Weekly report card (PDF export)',
              '25-mile radius coverage',
              'Priority email support',
            ].map((feature) => (
              <li key={feature} className="flex items-center gap-3 text-glass-text">
                <Check className="h-5 w-5 text-glass-accent flex-shrink-0" />
                {feature}
              </li>
            ))}
          </ul>

          <a
            href="https://buy.stripe.com/test_placeholder_replace_me"
            className="block w-full rounded-lg bg-glass-text py-3 text-center font-medium text-glass-black hover:bg-glass-muted transition-colors"
          >
            Start 14-Day Free Trial
          </a>
          
          <p className="mt-4 text-center text-sm text-glass-subtle">
            14-day money-back guarantee • No credit card required for trial
          </p>
        </div>

        {/* FAQ Section */}
        <div className="mt-20 mx-auto max-w-2xl">
          <h2 className="font-display text-2xl text-white text-center mb-8">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-4">
            {[
              {
                q: 'How does the free trial work?',
                a: 'Sign up and get full access for 14 days. No credit card required. Explore all features before subscribing.',
              },
              {
                q: 'Can I track competitors outside my radius?',
                a: 'Professional plan includes up to 25 miles. Contact us for custom coverage on larger territories.',
              },
              {
                q: 'How often is data updated?',
                a: 'We scan menus daily. Price changes typically appear within 24 hours of being published.',
              },
              {
                q: 'What if I need to cancel?',
                a: 'Cancel anytime from settings. No questions asked. You\'ll keep access until the end of your billing period.',
              },
            ].map((faq) => (
              <details
                key={faq.q}
                className="group rounded-lg border border-glass-border bg-glass-surface cursor-pointer"
              >
                <summary className="flex items-center justify-between p-4 font-medium text-white list-none">
                  {faq.q}
                  <span className="transition-transform group-open:rotate-180">▼</span>
                </summary>
                <p className="px-4 pb-4 text-glass-muted">{faq.a}</p>
              </details>
            ))}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Pricing;
```

**⚠️ NOTE:** Replace the Stripe URL with the actual production link. The link above is a placeholder.

#### 2.2.2 Market.tsx Updates — EDIT EXISTING FILE

**File:** `src/apps/web/src/pages/Market.tsx`

**Remove these sections:**
- ❌ Demographics section (donut charts of gender/race)
- ❌ "Premium Data Teaser" section with blurred dashboard
- ❌ Old CTA buttons

**Add to Market.tsx:**

```typescript
// Add this hero section at the top of the Market component
const EmailSignupHero = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await fetch('/api/v1/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: 'homepage_hero' })
      });
      setSubmitted(true);
    } catch (err) {
      console.error('Waitlist signup failed:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <section className="border-b border-glass-border bg-glass-surface">
      <div className="mx-auto max-w-4xl px-4 py-16 text-center">
        <h1 className="font-display text-4xl font-medium text-white mb-4">
          The most complete picture of Massachusetts cannabis pricing
        </h1>
        <p className="text-xl text-glass-muted mb-8">
          Updated daily from 200+ licensed retailers. Cross-referenced with CCC data.
        </p>
        
        {submitted ? (
          <div className="rounded-lg bg-glass-elevated border border-glass-border p-6 max-w-md mx-auto">
            <p className="text-white font-medium">Thanks! We'll be in touch soon.</p>
            <p className="text-glass-subtle text-sm mt-2">Check your inbox for updates.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex gap-3 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="flex-1 rounded-lg border border-glass-border bg-glass-black px-4 py-3 text-white placeholder:text-glass-subtle focus:border-glass-text focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-glass-text px-6 py-3 font-medium text-glass-black hover:bg-glass-muted disabled:opacity-50 transition-colors"
            >
              {loading ? 'Sending...' : 'Get Early Access'}
            </button>
          </form>
        )}
        
        <p className="mt-6 text-glass-subtle text-sm">
          Already tracking your store?{' '}
          <Link to="/login" className="text-glass-accent hover:underline">Sign in</Link>
        </p>
      </div>
    </section>
  );
};
```

**Add to Market return statement (before the stats grid):**
```typescript
return (
  <div className="min-h-screen bg-glass-black">
    <LandingNav />
    <EmailSignupHero />  {/* ADD THIS LINE */}
    {/* ... rest of existing Market content */}
  </div>
);
```

### 2.3 API Endpoints for Phase 0

**EXISTING — Use As-Is (No new backend work):**

| Endpoint | Status | Usage in Phase 0 |
|----------|--------|------------------|
| `GET /api/v1/market/stats` | ✅ EXISTS | Market stats for hero section |
| `GET /api/v1/market/weekly-sales` | ✅ EXISTS | Weekly sales chart |
| `GET /api/v1/market/license-pipeline` | ✅ EXISTS | License pipeline data |
| `POST /api/v1/waitlist` | ✅ EXISTS | Email signup |
| `GET /api/v1/report-card/:slug` | ✅ EXISTS | Public report cards |

**NO NEW ENDPOINTS REQUIRED FOR PHASE 0**

### 2.4 Success Criteria for Phase 0

- [ ] `/` shows Market data with email signup hero (signed-out users)
- [ ] `/` redirects signed-in users to `/products`
- [ ] `/market` redirects to `/`
- [ ] `/landing` redirects to `/`
- [ ] `/pricing` page live with Stripe checkout link
- [ ] Email signups POST to `/api/v1/waitlist` successfully
- [ ] 24 outreach emails can be sent pointing to new homepage
- [ ] Old `Landing.tsx` can be deleted

---

## 3. Revised Implementation Phases

### Phase 0: Market-as-Homepage (3 days) — SHIP FIRST ✅ READY
**Goal:** Unblock outreach emails immediately  
**Uses ONLY existing code/endpoints**

See Section 2 above for detailed implementation.

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

---

## 4. The Product Matching Problem (Phase B — Not Phase A)

### 4.1 The Challenge

Products from different scraped stores are **NOT** the same `product_id`. Competitive context requires fuzzy matching across:

- Brand name (normalized: "Cookies" = "COOKIES")
- Product name (trigram similarity for typos/variations)
- Weight (extracted and normalized: "3.5g" = "1/8th" = "eighth")
- Category (flower, pre-roll, vape, etc.)

### 4.2 Why This Is Phase B, Not Phase A

Product matching requires:
1. Algorithm development and testing
2. Database migrations
3. Backfill of historical matches
4. Confidence threshold tuning
5. Edge case handling (new products, discontinued products)

**Phase A uses category-level benchmarks** (no matching needed):
- "Your average flower price: $42/unit"
- "Market average flower price: $38/unit"
- "Your position: 10% above market"

This requires zero product matching and uses data already in the database.

---

## 5. Action Buttons: Honest Design

### 5.1 The Reality

GLASS cannot write to operator menus. There is no POS integration. When an operator clicks a button, GLASS can only:

1. **Log the intent** — "Operator wants to target $42 for SKU X"
2. **Generate a task** — Plain text instruction for the operator
3. **Track follow-through** — Compare next scrape to see if price changed

### 5.2 Button Redesign

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
// TargetPriceButtons.tsx
interface ProductActionButtons {
  // Log intent to price_targets table
  targetPrice: (price: number) => void;     // "Target $42"
  flagForReview: () => void;                 // "Flag for review"
  addToWatchlist: () => void;                // "Add to watchlist"
}
```

**UI Implementation:**
```typescript
const ProductActions = ({ product, yourPrice, marketMedian }) => {
  const [showWorkflow, setShowWorkflow] = useState(false);
  
  const handleTarget = async () => {
    await fetch('/api/v1/price-targets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_id: product.id,
        current_price: yourPrice,
        target_price: marketMedian
      })
    });
    setShowWorkflow(true);
  };
  
  if (showWorkflow) {
    return (
      <div className="workflow-panel p-4 rounded-lg bg-glass-elevated border border-glass-border">
        <p className="text-white font-medium">✓ Target logged: ${marketMedian}</p>
        <p className="text-glass-muted text-sm mt-2">
          To implement: Log into your POS and change {product.name} to ${marketMedian}. 
          We'll verify the change on our next scan.
        </p>
        <button 
          onClick={() => setShowWorkflow(false)}
          className="mt-3 text-glass-accent text-sm hover:underline"
        >
          Done
        </button>
      </div>
    );
  }
  
  return (
    <div className="action-buttons flex gap-2">
      <button 
        className="btn-primary px-3 py-1 rounded bg-glass-text text-glass-black text-sm font-medium"
        onClick={handleTarget}
      >
        Target ${marketMedian}
      </button>
      <button className="btn-secondary px-3 py-1 rounded border border-glass-border text-glass-text text-sm">
        Flag
      </button>
      <button className="btn-secondary px-3 py-1 rounded border border-glass-border text-glass-text text-sm">
        Watch
      </button>
    </div>
  );
};
```

---

## 6. API Endpoint Inventory

### 6.1 Existing Endpoints (Working Today)

| Endpoint | Status | Usage |
|----------|--------|-------|
| `GET /api/v1/market/stats` | ✅ EXISTS | Market stats for homepage |
| `GET /api/v1/market/weekly-sales` | ✅ EXISTS | Weekly sales chart |
| `GET /api/v1/market/license-pipeline` | ✅ EXISTS | License pipeline data |
| `POST /api/v1/waitlist` | ✅ EXISTS | Email signup |
| `GET /api/v1/products` | ✅ EXISTS | Product search & filter |
| `GET /api/v1/prices/movers` | ✅ EXISTS | Price change detection |
| `GET /api/v1/catalog/:operator_id/products` | ✅ EXISTS | Operator's own products |
| `GET /api/v1/report-card/:operator_id` | ✅ EXISTS | Report card data |
| `GET /api/v1/operators` | ✅ EXISTS | Competitor lookup |
| `GET /api/v1/scores/leaderboard` | ✅ EXISTS | Health scoring |
| `GET /api/v1/threats/feed` | ✅ EXISTS | Threat detection |
| `GET /api/v1/recommendations` | ✅ EXISTS | Price recommendations |
| `GET /api/v1/alerts` | ✅ EXISTS | Alert feed |

### 6.2 New Endpoints Required

| Endpoint | Priority | Effort | Risk | Description |
|----------|----------|--------|------|-------------|
| `GET /api/v1/products/competitive-context` | P1 | 1-2 weeks | **HIGH** | Per-operator competitive stats. Requires product matching engine. |
| `GET /api/v1/products/:id/competitive-landscape` | P1 | 3-5 days | MEDIUM | Single SKU competitive view. Depends on competitive-context. |
| `POST /api/v1/price-targets` | P2 | 1-2 days | LOW | Log price target intent. New table: `price_targets`. |
| `POST /api/v1/alerts/:id/action` | P2 | 1-2 days | LOW | Log alert action intent. Simple metadata update. |
| `GET /api/v1/report-card/:id/v2` | P2 | 3-5 days | LOW | Enhanced report card. Builds on existing endpoint. |
| `GET /api/v1/export/pricing` | P2 | 2-3 days | LOW | CSV export. Simple query + formatting. |

### 6.3 Endpoints REMOVED from Plan

| Endpoint | Reason |
|----------|--------|
| `POST /api/v1/prices/bulk-update` | GLASS cannot write to operator menus. No POS integration. |

---

## 7. Component Kill/Keep/Build

### 7.1 KILL (Remove from routes, archive files)

| Component | Reason |
|-----------|--------|
| `Landing.tsx` | Replaced by Market homepage |
| `MorningBrief` | Dashboard fatigue |
| `CategorySunburst` | Pretty but unused |
| `BrandTreemap` | Not actionable |
| `MarketTerrainMap` | Replace with table |
| `DeliveryVoronoi` | Over-engineered |
| `StrainStream` | No decision value |
| `CategoryGrowthCurves` | Market-wide, not actionable |
| `PriceChangeCascade` | Replace with alerts |
| `VolatilityRibbon` | Too abstract |
| `PricePositionMatrix` | Replaced by inline badges |
| `ThreatNetwork` | Replace with alert list |
| `MarketShareFlow` | Sankey confusion |
| `OperatorComparison` | Replaced by competitor table |
| `PriceWarHeatmap` | Move to SKU detail only |
| `ProximityRadar` | Replace with sorted table |
| `PriceTicker` | Visual noise |

### 7.2 KEEP (Existing components to retain)

| Component | Usage |
|-----------|-------|
| `Sidebar` | Update nav items only |
| `TopBar` | Keep, add export actions |
| `DashboardLayout` | Keep as wrapper |
| `EmptyState` | Reuse for zero states |
| `DataFreshness` | Keep in footer |
| `ErrorBoundary` | Keep as-is |
| `Market.tsx` | **ENHANCE** — becomes homepage |

### 7.3 BUILD (New components, prioritized)

| Component | Phase | Description |
|-----------|-------|-------------|
| `PricingPage` | 0 | $199/mo plan details, Stripe checkout |
| `ProductIntelligenceTable` | A | Main dense table with competitive context |
| `PricePositionBadge` | A | Color-coded position indicator |
| `TargetPriceButtons` | A | Log intent, not execute |
| `FilterBar` | A | Sticky filter controls |
| `ExportButton` | A | CSV export with current filters |
| `SKUDetailSlideout` | B | Single SKU deep-dive as slide-out |
| `CompetitorPriceTable` | B | Nearby store price comparison |
| `PriceHistoryChart` | B | Simple 2-line time series |
| `AlertFeed` | C | Plain English alert cards |
| `AlertActionCard` | C | Alert with embedded actions |
| `ReportCardV2` | D | Rewritten executive view |
| `OnboardingFlow` | D | Post-signup: claim store, see report |
| `SettingsPage` | D | Profile, billing, preferences, watchlist |

---

## 8. Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Product Matching Engine** | High | High | Start with category benchmarks (Phase A). Build matching as progressive enhancement (Phase B). |
| **Stale Data Display** | High | Medium | Add `scraped_at` timestamps to all price displays. Badge rows >48h old. |
| **Query Performance** | Medium | High | Add indexes (see Section 9). Use materialized views. Cache aggressively. |
| **Action Button Confusion** | Medium | Medium | Rename to "Target" (not "Match"). Show workflow panel explaining manual steps. |
| **No Customers During Build** | High | High | **Phase 0 ships first.** Collect emails while building paid product. |

---

## 9. Database Schema Additions

### 9.1 New Tables

```sql
-- Price targets (logged intent, not executed)
CREATE TABLE price_targets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID REFERENCES operators(id),
  product_id UUID REFERENCES products(id),
  current_price DECIMAL(10,2),
  target_price DECIMAL(10,2),
  status VARCHAR(50) DEFAULT 'pending',
  source VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_price_targets_operator ON price_targets(operator_id, status);

-- Product matches (for competitive context) — Phase B
CREATE TABLE product_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id_1 UUID REFERENCES products(id),
  product_id_2 UUID REFERENCES products(id),
  match_confidence DECIMAL(3,2),
  match_type VARCHAR(50),
  verified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(product_id_1, product_id_2)
);

CREATE INDEX idx_product_matches_lookup ON product_matches(product_id_1, match_confidence DESC);

-- Watchlist
CREATE TABLE watchlist_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID REFERENCES operators(id),
  product_id UUID REFERENCES products(id),
  alert_threshold DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_watchlist_operator ON watchlist_items(operator_id);
```

### 9.2 Indexes for Performance

```sql
CREATE INDEX idx_prices_product_operator_scraped 
  ON prices(product_id, operator_id, scraped_at DESC);

CREATE INDEX idx_prices_operator_scraped 
  ON prices(operator_id, scraped_at DESC);

CREATE INDEX idx_operators_location 
  ON operators USING gist(ll_to_earth(lat, lon));

CREATE INDEX idx_products_category_brand 
  ON products(category, brand);
```

---

## 10. Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Homepage email conversion | 0% | >5% | Signups / visitors |
| Time to first decision | 3+ clicks | 1 click | User testing |
| Price target rate | <5% | >15% | Button click analytics |
| Alert engagement | TBD | >50% open rate | Alert tracking |
| Page load time | 4s | <2s | Web vitals |

---

## 11. Implementation Checklist

### Phase 0 (Start Here — 3 days max)

- [ ] **App.tsx:** Update routes (Market as `/`, signed-in → `/products`)
- [ ] **App.tsx:** Add Pricing import and route
- [ ] **Pricing.tsx:** Create new page with Stripe link
- [ ] **LandingNav.tsx:** Add Pricing link to nav
- [ ] **Market.tsx:** Add email signup hero
- [ ] **Market.tsx:** Remove demographics section
- [ ] **Market.tsx:** Remove blurred dashboard teaser
- [ ] **Market.tsx:** Update CTAs to point to `/signup`
- [ ] **Test:** Email signup POSTs to `/api/v1/waitlist`
- [ ] **Deploy:** Ready for outreach emails

### Phase A (After Phase 0 — 1-2 weeks)

- [ ] Create `/products` route with auth guard
- [ ] Build ProductIntelligenceTable component
- [ ] Build FilterBar component
- [ ] Build PricePositionBadge component
- [ ] Build TargetPriceButtons component
- [ ] Connect to existing endpoints
- [ ] Add CSV export
- [ ] Add data freshness indicators

### Phase B (After Phase A — 2-3 weeks)

- [ ] Build product matching engine (backend)
- [ ] Create competitive-context endpoint
- [ ] Build SKUDetailSlideout component
- [ ] Build CompetitorPriceTable component
- [ ] Build PriceHistoryChart component

### Phase C (After Phase B — 2 weeks)

- [ ] Rewrite /alerts page
- [ ] Build AlertFeed component
- [ ] Build AlertActionCard component
- [ ] Create alert generation service
- [ ] Add unread count badge to nav

### Phase D (After Phase C — 1-2 weeks)

- [ ] Rewrite /report-card page
- [ ] Build RepriceQueueTable component
- [ ] Build MissingSKUTable component
- [ ] Build MarginLeakTable component
- [ ] Build ExportButton with PDF
- [ ] Revise /onboarding flow
- [ ] Build /settings page

---

**END OF PLAN V2.1**

*Phase 0 is ready for immediate implementation. A developer can start coding Phase 0 today using the exact code snippets in this document.*
