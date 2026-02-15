# GLASS Frontend UI Redesign Plan
## Decision-First Architecture for Cannabis Operators

**Version:** 2.0  
**Date:** 2026-02-13  
**Status:** Planning Phase — DO NOT CODE YET

---

## Executive Summary

Current GLASS suffers from "dashboard fatigue" — it's a stock-trader style interface with charts and visualizations that operators rarely use. This redesign pivots to a **decision-first architecture** where every screen answers the question: *"What should I do right now?"*

### Core Philosophy Shift
| Before | After |
|--------|-------|
| "Explore the market" | "Fix your prices" |
| Charts-first | Tables-first |
| Passive monitoring | Active decision queue |
| Market-wide views | My-store-focused |
| Visualizations | Action buttons |

---

## 1. New Information Architecture

### 1.1 Route Structure Overhaul

```
CURRENT (Kill or Deprioritize)          NEW (Primary)
─────────────────────────────────────────────────────────
/ (Morning Brief - dashboard)     →   /products (NEW HOME)
/prices (Price Wire)              →   /products/:id (SKU detail)
/threats (Threat Radar)           →   /alerts (Action queue)
/geography (Market Terrain)       →   [DEPRECATED]
/recommendations                  →   /report-card (Rewritten)
/competitors                      →   /competitors (refocused)
/alerts                           →   /alerts (enhanced)
/settings                         →   /settings (keep)
```

### 1.2 Navigation Restructure

```typescript
// New Sidebar Navigation
const navItems = [
  { path: '/products', icon: Package, label: 'Products', badge: 'home' },
  { path: '/alerts', icon: Bell, label: 'Alerts', badge: 'unread_count' },
  { path: '/report-card', icon: Target, label: 'Report Card' },
  { path: '/competitors', icon: Users2, label: 'Competitors' },
];

// Remove from primary nav:
// - Morning Brief (kill)
// - Price Wire (merge into Products)
// - Threat Radar (merge into Alerts)
// - Recommendations (merge into Report Card)
// - Geography (kill)
```

### 1.3 Deprecated Visualizations

The following visualization components will be **removed** from the main UI (keep code for now, but unmount):

| Component | Status | Reason |
|-----------|--------|--------|
| `CategorySunburst` | DEPRECATE | Pretty but unused — operators don't browse by category hierarchy |
| `BrandTreemap` | DEPRECATE | Too abstract — operators think in SKUs, not market share |
| `MarketTerrainMap` | DEPRECATE | Geographic viz replaced by distance-sorted tables |
| `DeliveryVoronoi` | DEPRECATE | Over-engineered for actual use case |
| `StrainStream` | DEPRECATE | No strain-level decision value |
| `CategoryGrowthCurves` | DEPRECATE | Market-wide trend, not actionable |
| `PriceChangeCascade` | DEPRECATE | Replace with alert feed |
| `VolatilityRibbon` | DEPRECATE | Too abstract — replace with simple variance badges |
| `PricePositionMatrix` | DEPRECATE | Replace with inline position indicators in table |
| `ThreatNetwork` | DEPRECATE | Replace with plain English alert list |
| `MarketShareFlow` | DEPRECATE | Sankey diagrams confuse operators |
| `CccTimeline` | KEEP (admin only) | Regulatory timeline — move to admin panel |
| `PriceWarHeatmap` | KEEP (conditional) | Only in SKU detail, not main view |

---

## 2. Product Intelligence Screen (Core)

### 2.1 Page: `/products` (New Home Screen)

**Purpose:** Show every SKU the operator carries with competitive context and one-click actions.

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────────────┐
│  [Filters: Category ▼] [Brand ▼] [Weight ▼] [Radius ▼] [Export ▼]  │  ← Sticky
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ SKU Name          │ You    │ Market Band    │ Position │ ⚡ │   │
│  │                   │        │ P25 / Med / P75│          │    │   │
│  ├───────────────────┼────────┼────────────────┼──────────┼────┤   │
│  │ Cookies Gelato 3.5│ $45.00 │ $38 / $42 / $48│ +7% ▲    │Act │   │
│  │ Big Pine 1g Pre   │ $18.00 │ $15 / $16 / $20│ +12% ▲   │Act │   │
│  │ Stiiizy Pod .5g   │ $32.00 │ $30 / $35 / $40│ -9% ▼    │Act │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  [Load More]                                    Page 1 of 12        │
└─────────────────────────────────────────────────────────────────────┘
```

#### Table Columns

| Column | Type | Description |
|--------|------|-------------|
| **Product** | SKU + Brand + Weight | e.g., "Gelato 3.5g" |
| **Category** | Badge | flower, pre-roll, vape, etc. |
| **Your Price** | Currency | Current listed price |
| **Market Band** | 3-values | P25 / Median / P75 in radius |
| **Position** | Indicator | "+12% above median" with color |
| **Stores** | Count | # of nearby competitors carrying |
| **Actions** | Button Group | Match / Undercut / Hold |

#### Action Buttons

Each row has a dropdown or inline button group:

```typescript
interface ProductActionButtons {
  // Primary actions (always visible on hover)
  matchMedian: () => void;      // "Match $42" (sets to market median)
  undercutDollar: () => void;   // "Undercut $1" (sets to median - $1)
  holdPremium: () => void;      // "Hold +$3" (maintains current premium)
  
  // Secondary (in dropdown)
  viewDetail: () => void;       // Navigate to SKU detail
  addWatchlist: () => void;     // Track this SKU
}
```

#### Filter Bar (Always Visible)

```typescript
interface ProductFilters {
  category: 'all' | 'flower' | 'pre-roll' | 'vape' | 'concentrate' | 'edible';
  brand: string;                    // Search input with autocomplete
  weight: 'all' | '1g' | '3.5g' | '7g' | '14g' | '1oz' | 'other';
  radius: 1 | 3 | 5 | 10 | 25;      // miles
  competitorSet: string[];          // multi-select specific competitors
  pricePosition: 'all' | 'above' | 'at' | 'below' | 'significant_above';
  availability: 'all' | 'in_stock' | 'low_inventory';
}
```

#### Price Position Indicator

```typescript
// Color-coded position badges
const PositionIndicator = ({ yourPrice, marketMedian, marketP75 }) => {
  const diff = ((yourPrice - marketMedian) / marketMedian) * 100;
  
  if (diff > 15) return <Badge variant="danger">+{diff.toFixed(0)}% ▲</Badge>;      // Red
  if (diff > 5) return <Badge variant="warning">+{diff.toFixed(0)}% ▲</Badge>;       // Yellow
  if (diff > -5) return <Badge variant="success">At Market</Badge>;                  // Green
  if (diff > -15) return <Badge variant="info">{diff.toFixed(0)}% ▼</Badge>;        // Blue
  return <Badge variant="danger">{diff.toFixed(0)}% ▼</Badge>;                      // Red (too low)
};
```

### 2.2 Data Requirements

#### API Endpoint Needs

**EXISTING — Use As-Is:**
- `GET /api/v1/products` — search, filter by category/brand
- `GET /api/v1/catalog/:operator_id/products` — operator's own products

**NEEDS NEW ENDPOINT:**
```typescript
// NEW: GET /api/v1/products/competitive-context
interface CompetitiveContextRequest {
  operator_id: string;
  radius_miles: number;
  category?: string;
  brand?: string;
  page: number;
  limit: number;
}

interface CompetitiveContextResponse {
  data: {
    product_id: string;
    sku: string;
    brand: string;
    category: string;
    weight: string;
    your_price: number;
    your_availability: 'in_stock' | 'limited' | 'out_of_stock';
    market_stats: {
      p25: number;
      median: number;
      p75: number;
      min: number;
      max: number;
      competitor_count: number;
      sample_size: number;
    };
    position_percentile: number;  // 0-100, where you sit
    recommended_action: 'raise' | 'lower' | 'hold' | 'investigate';
    estimated_margin_impact: number;  // weekly $ impact if action taken
  }[];
  pagination: PaginatedResponse<any>['pagination'];
}
```

#### Database Queries Needed

```sql
-- Competitive context for operator's products
WITH operator_products AS (
  SELECT DISTINCT p.id, p.sku, p.brand, p.category, pr.price
  FROM products p
  JOIN prices pr ON pr.product_id = p.id
  WHERE pr.operator_id = :operator_id
    AND pr.scraped_at > NOW() - INTERVAL '24 hours'
),
nearby_competitors AS (
  SELECT o.id, o.lat, o.lon
  FROM operators o
  WHERE earth_distance(
    ll_to_earth(:lat, :lon),
    ll_to_earth(o.lat, o.lon)
  ) / 1609.34 <= :radius_miles
    AND o.id != :operator_id
),
competitor_prices AS (
  SELECT 
    op.id as product_id,
    op.sku,
    op.brand,
    op.category,
    op.price as your_price,
    ARRAY_AGG(pr.price) as competitor_prices,
    COUNT(DISTINCT pr.operator_id) as competitor_count
  FROM operator_products op
  LEFT JOIN prices pr ON pr.product_id = op.id
  LEFT JOIN nearby_competitors nc ON nc.id = pr.operator_id
  WHERE pr.scraped_at > NOW() - INTERVAL '24 hours'
  GROUP BY op.id, op.sku, op.brand, op.category, op.price
)
SELECT 
  product_id,
  sku,
  brand,
  category,
  your_price,
  competitor_count,
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY UNNEST(competitor_prices)) as p25,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY UNNEST(competitor_prices)) as median,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY UNNEST(competitor_prices)) as p75
FROM competitor_prices
GROUP BY product_id, sku, brand, category, your_price, competitor_count;
```

---

## 3. SKU Detail View

### 3.1 Page: `/products/:id`

**Purpose:** Deep-dive on a single SKU with full competitive landscape and price history.

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Back to Products              [Export] [Add to Watchlist]        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ COOKIES GELATO 3.5G (Flower)                                │   │
│  │                                                             │   │
│  │ Your Price: $45.00     Market Median: $42.00     Position:  │   │
│  │ Status: In Stock       You are +7% above median (+$3.00)    │   │
│  │                                                             │   │
│  │ [Match $42.00] [Undercut $1 → $41.00] [Hold Premium]        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────┐  ┌────────────────────────────────┐  │
│  │ COMPETITOR PRICES (12)   │  │ PRICE HISTORY (30 Days)        │  │
│  │                          │  │                                │  │
│  │ 1. GreenLeaf Med... $42  │  │ [Simple Line Chart]            │  │
│  │ 2. Herbology    2mi $42  │  │                                │  │
│  │ 3. The Botanist 3mi $44  │  │ Your price: ─────────────      │  │
│  │ 4. Sanctuary C... 4mi $40│  │ Market median: ─ ─ ─ ─ ─       │  │
│  │ 5. ...                   │  │                                │  │
│  │                          │  │                                │  │
│  │ Legend: 🏷️ = Promo       │  │                                │  │
│  └──────────────────────────┘  └────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ACTIVE PROMOS IN YOUR RADIUS                                │   │
│  │ • GreenLeaf: "2 for $80" (Save $4)                          │   │
│  │ • Herbology: "20% off all flower"                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

#### Competitor Table

| Rank | Store | Distance | Neighborhood | Price | Promo | Updated |
|------|-------|----------|--------------|-------|-------|---------|
| 1 | GreenLeaf Med | 1.2mi | Downtown | $42.00 | — | 2h ago |
| 2 | Herbology | 2.1mi | East Side | $42.00 | 2 for $80 | 4h ago |
| 3 | The Botanist | 3.4mi | North End | $44.00 | — | 1h ago |
| 4 | Sanctuary Cannabis | 4.8mi | South Side | $40.00 | 30% off | 6h ago |

#### Price History Chart (The ONE Chart)

```typescript
// Simple, focused time series
// Only two lines: Your price (solid) vs Market median (dashed)
// 30-day lookback, daily resolution
// NO: volume, volatility bands, or other complexity

interface PriceHistoryPoint {
  date: string;           // YYYY-MM-DD
  your_price: number;
  market_median: number;
  market_p25: number;
  market_p75: number;
  competitor_count: number;  // how many had this SKU that day
}
```

#### API Endpoint Needs

**NEW ENDPOINT:**
```typescript
// GET /api/v1/products/:id/competitive-landscape
interface CompetitiveLandscapeResponse {
  product: {
    id: string;
    sku: string;
    brand: string;
    category: string;
    weight: string;
  };
  your_listing: {
    price: number;
    availability: 'in_stock' | 'limited' | 'out_of_stock';
    last_updated: string;
    source_url?: string;
  };
  market_stats: {
    median: number;
    p25: number;
    p75: number;
    range_low: number;
    range_high: number;
  };
  competitors: {
    operator_id: string;
    operator_name: string;
    distance_miles: number;
    neighborhood: string;
    price: number;
    promo_flag: boolean;
    promo_details?: string;  // e.g., "2 for $80"
    availability: string;
    last_updated: string;
  }[];
  price_history: PriceHistoryPoint[];
  active_promos: {
    operator_name: string;
    promo_text: string;
    estimated_savings: number;
  }[];
}
```

---

## 4. Alerts / Action Queue

### 4.1 Page: `/alerts` (Rewritten)

**Purpose:** Plain-English feed of what needs attention RIGHT NOW.

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────────────┐
│  [Filter: All ▼] [Mark All Read]         3 Unread Actions           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🔴 URGENT: You are losing preroll share in 5-mile radius    │   │
│  │    7 stores undercut you by >$4 on Big Pine 1g              │   │
│  │                                                             │   │
│  │    [Lower to $16] [Ignore] [See Competitors]                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 💡 RECOMMENDATION: Raise price on Cookies Gelato 3.5g       │   │
│  │    You are $3 below P75. Raise to $48 for +$420/week est.   │   │
│  │                                                             │   │
│  │    [Raise to $48] [Dismiss]                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ⚠️  WARNING: Stop discounting Stiiizy Pod                   │   │
│  │    Market already moved up. You're leaving money on table.  │   │
│  │                                                             │   │
│  │    [Remove Promo] [Review SKU]                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ℹ️  INFO: New competitor detected 2.3 miles away            │   │
│  │    "Green Horizon" opened with aggressive flower pricing    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Alert Types

```typescript
interface Alert {
  id: string;
  type: 'urgent' | 'recommendation' | 'warning' | 'info';
  priority: 'critical' | 'high' | 'medium' | 'low';
  title: string;              // Plain English headline
  body: string;               // 1-2 sentence explanation
  context: {
    product_id?: string;
    product_name?: string;
    your_current_price?: number;
    suggested_price?: number;
    estimated_impact?: string;  // e.g., "+$420/week"
    competitor_count?: number;
    affected_skus?: string[];
  };
  actions: {
    primary: {
      label: string;
      action: string;         // e.g., "set_price:48.00"
    };
    secondary: {
      label: string;
      action: string;         // e.g., "dismiss" or "navigate:/products/123"
    }[];
  };
  read: boolean;
  created_at: string;
  expires_at?: string;        // urgency window
}
```

#### Alert Templates

```typescript
const ALERT_TEMPLATES = {
  UNDERPRICED_CATEGORY: (data) => ({
    title: `You are losing ${data.category} share in ${data.radius}-mile radius`,
    body: `${data.competitor_count} stores undercut you by >$${data.threshold} on ${data.product_count} SKUs`,
    actions: { primary: { label: `Review ${data.category} prices`, action: 'filter:category' } }
  }),
  
  RAISE_OPPORTUNITY: (data) => ({
    title: `Raise price on ${data.product_name}`,
    body: `You are $${data.below_p75} below P75. Raise to $${data.suggested_price} for ${data.estimated_impact}/week est.`,
    actions: { primary: { label: `Raise to $${data.suggested_price}`, action: `set_price:${data.suggested_price}` } }
  }),
  
  STOP_DISCOUNTING: (data) => ({
    title: `Stop discounting ${data.product_name}`,
    body: `Market already moved up. You're leaving ${data.estimated_impact}/week on the table.`,
    actions: { primary: { label: 'Remove Promo', action: 'remove_promo' } }
  }),
  
  NEW_COMPETITOR: (data) => ({
    title: `New competitor detected ${data.distance} miles away`,
    body: `"${data.operator_name}" opened with aggressive ${data.category} pricing`,
    actions: { primary: { label: 'View Competitor', action: `navigate:/competitors/${data.operator_id}` } }
  }),
  
  MISSING_HIGH_DEMAND: (data) => ({
    title: `Missing high-demand SKU: ${data.product_name}`,
    body: `${data.competitor_count} nearby stores carry this. Local median: $${data.median_price}`,
    actions: { primary: { label: 'Add to Watchlist', action: 'watchlist:add' } }
  })
};
```

#### Sticky Action Rail

On desktop, a sticky right rail shows:

```
┌─────────────────┐
│ TODAY'S ACTIONS │
├─────────────────┤
│ 3 Urgent        │
│ 5 Recommended   │
│ 2 Warnings      │
├─────────────────┤
│ [Process All]   │
└─────────────────┘
```

#### API Endpoint Needs

**EXISTING — Enhance:**
- `GET /api/v1/alerts` — already exists, enhance with action payloads

**NEW ENDPOINT:**
```typescript
// POST /api/v1/alerts/:id/action
// Execute the alert's suggested action directly
interface AlertActionRequest {
  action: string;  // parsed from alert.actions.primary.action
}

// Returns the result of the action (e.g., price update confirmation)
```

---

## 5. Report Card Rewrite

### 5.1 Page: `/report-card` (v2)

**Purpose:** Executive summary for buyer/GM meetings — exportable, scannable, prioritized.

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────────────┐
│  REPORT CARD                    [Export PDF] [Email to Team]        │
│  Week of Feb 10, 2026                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ OVERALL HEALTH: 🟡 WATCH                                    │   │
│  │ 3 pricing opportunities | 1 competitive threat | 92 Score   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ TOP 10 SKUs TO REPRICE TODAY                                │   │
│  │ ─────────────────────────────────────────────────────────── │   │
│  │ #  SKU                    Current  Target   Impact   Action │   │
│  │ 1  Big Pine 1g Pre      $18.00   $16.00   +$140/wk  [Fix]  │   │
│  │ 2  Cookies Gelato 3.5g  $45.00   $48.00   +$420/wk  [Fix]  │   │
│  │ 3  Stiiizy Pod .5g      $32.00   $35.00   +$280/wk  [Fix]  │   │
│  │ ...                                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ TOP 5 SKUs MISSING FROM YOUR MENU (High Local Demand)       │   │
│  │ ─────────────────────────────────────────────────────────── │   │
│  │ #  SKU                    Market Avg   Competitors  Action  │   │
│  │ 1  Raw Garden 1g Cart     $55.00       12 nearby    [Watch] │   │
│  │ 2  Jeeter 2g Infused      $35.00       8 nearby     [Watch] │   │
│  │ ...                                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ MARGIN LEAK TABLE                                           │   │
│  │ ─────────────────────────────────────────────────────────── │   │
│  │ Category    Current Avg  Suggested   Weekly Leak   Priority │   │
│  │ Flower      $42.00       $45.00      ~$840        HIGH      │   │
│  │ Pre-Roll    $16.00       $18.00      ~$320        MEDIUM    │   │
│  │ Vape        $38.00       $38.00      —            OK        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Data Structure

```typescript
interface ReportCardV2 {
  generated_at: string;
  period: { start: string; end: string };
  
  overall: {
    status: 'green' | 'yellow' | 'red';
    score: number;              // 0-100
    summary: string;
  };
  
  reprice_queue: {
    product_id: string;
    sku: string;
    brand: string;
    category: string;
    current_price: number;
    target_price: number;
    price_delta: number;
    estimated_weekly_impact: number;  // $ impact
    reason: string;                   // why this change
    confidence: 'high' | 'medium' | 'low';
  }[];
  
  missing_high_demand: {
    product_id: string;
    sku: string;
    brand: string;
    category: string;
    market_median_price: number;
    competitor_count: number;
    local_demand_score: number;       // 0-100
    why_consider: string;
  }[];
  
  margin_leak: {
    category: string;
    current_avg_price: number;
    suggested_avg_price: number;
    sku_count: number;
    weekly_leak_estimate: number;
    percentile_position: number;      // where you sit vs market
  }[];
  
  competitive_summary: {
    total_competitors_tracked: number;
    new_competitors_this_period: number;
    price_changes_by_competitors: number;
    your_price_changes: number;
  };
}
```

#### API Endpoint Needs

**EXISTING — Enhance:**
- `GET /api/v1/report-card/:operator_id` — enhance with v2 structure

---

## 6. UI Design Direction

### 6.1 Design Principles

1. **Dense Table-First Layout**
   - 12-14px font size for data
   - Tight padding (py-2, px-3)
   - Row hover states reveal actions
   - Inline editing where possible

2. **Filters Always Visible**
   - Sticky filter bar on `/products`
   - No hidden advanced search
   - One-click filter reset
   - Saved filter presets (v2)

3. **Minimal Charts**
   - Only ONE chart in entire app: SKU detail price history
   - Replace all other charts with:
     - Badges (position indicators)
     - Progress bars (percentile)
     - Sparklines (trend micro-viz)
     - Plain text stats

4. **One-Click Export**
   - Every table has CSV export
   - Report Card has PDF export
   - Pre-formatted for buyer/GM meetings

5. **Mobile: Simplified Action Queue**
   - Mobile view shows only `/alerts` interface
   - Full product table is desktop-only
   - Actions optimized for thumb-tap

### 6.2 Component Style Guide

```typescript
// Table density
const TABLE_STYLES = {
  row: 'py-2 px-3 text-sm',           // Compact rows
  header: 'py-2 px-3 text-xs uppercase tracking-wider font-medium',
  cell: 'text-glass-text',
  muted: 'text-glass-muted text-xs',
  action: 'opacity-0 group-hover:opacity-100 transition-opacity',
};

// Position badges
const POSITION_BADGES = {
  significantly_above: 'bg-red-500/10 text-red-400 border-red-500/30',    // >15% above
  above: 'bg-amber-500/10 text-amber-400 border-amber-500/30',           // 5-15% above
  at_market: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', // -5% to +5%
  below: 'bg-blue-500/10 text-blue-400 border-blue-500/30',              // 5-15% below
  significantly_below: 'bg-red-500/10 text-red-400 border-red-500/30',   // >15% below
};

// Action buttons
const ACTION_BUTTONS = {
  primary: 'bg-glass-accent text-glass-black hover:bg-glass-accent-dim',
  secondary: 'border border-glass-border hover:bg-glass-elevated',
  danger: 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30',
};
```

### 6.3 Color Coding

| State | Color | Usage |
|-------|-------|-------|
| Success/At Market | Emerald | Positioned correctly |
| Warning/Watch | Amber | Needs attention soon |
| Danger/Urgent | Red | Fix immediately |
| Info/Below | Blue | Competitive advantage |
| Neutral | Slate | Default text |

---

## 7. Component Inventory

### 7.1 NEW Components to Build

| Component | Location | Description |
|-----------|----------|-------------|
| `ProductIntelligenceTable` | `/components/products/` | Main dense table with competitive context |
| `PricePositionBadge` | `/components/products/` | Color-coded position indicator |
| `QuickActionButtons` | `/components/products/` | Match/Undercut/Hold buttons |
| `FilterBar` | `/components/products/` | Sticky filter controls |
| `SKUDetailView` | `/components/products/` | Single SKU deep-dive layout |
| `CompetitorPriceTable` | `/components/products/` | Nearby store price comparison |
| `PriceHistoryChart` | `/components/products/` | Simple 2-line time series |
| `AlertFeed` | `/components/alerts/` | Plain English alert cards |
| `AlertActionCard` | `/components/alerts/` | Alert with embedded actions |
| `ActionRail` | `/components/alerts/` | Sticky summary sidebar |
| `ReportCardV2` | `/components/report-card/` | Rewritten executive view |
| `RepriceQueueTable` | `/components/report-card/` | Top SKUs to reprice |
| `MissingSKUTable` | `/components/report-card/` | High-demand missing products |
| `MarginLeakTable` | `/components/report-card/` | Category margin analysis |
| `ExportButton` | `/components/shared/` | CSV/PDF export with dropdown |
| `MobileActionQueue` | `/components/mobile/` | Simplified mobile view |

### 7.2 EXISTING Components to Keep

| Component | Location | Usage in New Design |
|-----------|----------|---------------------|
| `Sidebar` | `/components/` | Update nav items only |
| `TopBar` | `/components/` | Keep, add export actions |
| `DashboardLayout` | `/layouts/` | Keep as wrapper |
| `EmptyState` | `/components/` | Reuse for zero states |
| `DataFreshness` | `/components/` | Keep in footer |
| `ErrorBoundary` | `/components/` | Keep as-is |
| `ReportCardSkeleton` | `/components/` | Adapt for v2 |
| `StatCard` | `/components/` | Use in report card header |
| `MiniChart` | `/components/` | Use for sparklines only |

### 7.3 EXISTING Components to Deprecate

| Component | Reason | Action |
|-----------|--------|--------|
| `CategorySunburst` | Overly complex | Remove from routes, keep file |
| `BrandTreemap` | Not actionable | Remove from routes, keep file |
| `MarketTerrainMap` | Replace with table | Remove from routes, keep file |
| `DeliveryVoronoi` | Over-engineered | Remove from routes, keep file |
| `StrainStream` | No decision value | Remove from routes, keep file |
| `CategoryGrowthCurves` | Market-wide, not actionable | Remove from routes, keep file |
| `PriceChangeCascade` | Replace with alerts | Remove from routes, keep file |
| `VolatilityRibbon` | Too abstract | Remove from routes, keep file |
| `PricePositionMatrix` | Replaced by inline badges | Remove from routes, keep file |
| `ThreatNetwork` | Replace with alert list | Remove from routes, keep file |
| `MarketShareFlow` | Sankey confusion | Remove from routes, keep file |
| `OperatorComparison` | Replaced by competitor table | Remove from routes, keep file |
| `PriceWarHeatmap` | Move to SKU detail only | Conditional render only |
| `ProximityRadar` | Replace with sorted table | Remove from routes, keep file |
| `PriceTicker` | Visual noise | Remove from routes, keep file |

---

## 8. API Endpoint Inventory

### 8.1 Existing Endpoints (Use As-Is)

| Endpoint | Usage |
|----------|-------|
| `GET /api/v1/products` | Product search & filter |
| `GET /api/v1/prices/movers` | Price change detection |
| `GET /api/v1/report-card/:operator_id` | Enhance for v2 |
| `GET /api/v1/operators` | Competitor lookup |
| `GET /api/v1/catalog/:operator_id/products` | Operator's own products |
| `GET /api/v1/scores/leaderboard` | Health scoring |
| `GET /api/v1/threats/feed` | Threat detection |
| `GET /api/v1/recommendations` | Price recommendations |
| `GET /api/v1/alerts` | Alert feed (enhance) |

### 8.2 New Endpoints Required

| Endpoint | Priority | Description |
|----------|----------|-------------|
| `GET /api/v1/products/competitive-context` | P0 | Main product table data |
| `GET /api/v1/products/:id/competitive-landscape` | P0 | SKU detail full view |
| `POST /api/v1/alerts/:id/action` | P1 | Execute alert action |
| `GET /api/v1/report-card/:id/v2` | P1 | Enhanced report card |
| `POST /api/v1/prices/bulk-update` | P2 | Batch price changes |
| `GET /api/v1/export/pricing` | P2 | CSV export endpoint |

### 8.3 Database Queries Needed

```sql
-- 1. Competitive context (P0)
-- See section 2.2 for full query

-- 2. Price history for SKU detail (P0)
WITH daily_prices AS (
  SELECT 
    DATE(pr.scraped_at) as date,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pr.price) as market_median,
    COUNT(DISTINCT pr.operator_id) as competitor_count
  FROM prices pr
  WHERE pr.product_id = :product_id
    AND pr.scraped_at > NOW() - INTERVAL '30 days'
    AND pr.operator_id != :your_operator_id
  GROUP BY DATE(pr.scraped_at)
),
your_prices AS (
  SELECT 
    DATE(pr.scraped_at) as date,
    pr.price as your_price
  FROM prices pr
  WHERE pr.product_id = :product_id
    AND pr.operator_id = :your_operator_id
    AND pr.scraped_at > NOW() - INTERVAL '30 days'
)
SELECT 
  d.date,
  d.market_median,
  d.competitor_count,
  y.your_price
FROM daily_prices d
LEFT JOIN your_prices y ON y.date = d.date
ORDER BY d.date;

-- 3. Reprice queue for report card (P1)
SELECT 
  p.id,
  p.sku,
  p.brand,
  p.category,
  your_prices.price as current_price,
  market_stats.median as target_price,
  market_stats.median - your_prices.price as price_delta,
  (market_stats.median - your_prices.price) * est_weekly_volume as weekly_impact
FROM products p
JOIN LATERAL (
  SELECT price FROM prices WHERE product_id = p.id AND operator_id = :your_id ORDER BY scraped_at DESC LIMIT 1
) your_prices ON true
JOIN LATERAL (
  SELECT 
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median,
    COUNT(DISTINCT operator_id) as competitor_count
  FROM prices 
  WHERE product_id = p.id 
    AND scraped_at > NOW() - INTERVAL '24 hours'
    AND operator_id != :your_id
) market_stats ON true
WHERE your_prices.price < market_stats.median * 0.95  -- significantly underpriced
  AND market_stats.competitor_count >= 3  -- enough data
ORDER BY weekly_impact DESC
LIMIT 10;

-- 4. Missing high-demand SKUs (P1)
WITH nearby_competitor_skus AS (
  SELECT 
    p.id,
    p.sku,
    p.brand,
    p.category,
    COUNT(DISTINCT pr.operator_id) as competitor_count,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pr.price) as median_price
  FROM products p
  JOIN prices pr ON pr.product_id = p.id
  JOIN nearby_operators no ON no.id = pr.operator_id
  WHERE pr.scraped_at > NOW() - INTERVAL '24 hours'
  GROUP BY p.id, p.sku, p.brand, p.category
  HAVING COUNT(DISTINCT pr.operator_id) >= 5  -- carried by 5+ nearby stores
),
your_skus AS (
  SELECT DISTINCT product_id 
  FROM prices 
  WHERE operator_id = :your_id
)
SELECT 
  ncs.*,
  (ncs.competitor_count / (SELECT COUNT(*) FROM nearby_operators)::float) as penetration_rate
FROM nearby_competitor_skus ncs
LEFT JOIN your_skus ys ON ys.product_id = ncs.id
WHERE ys.product_id IS NULL  -- you don't carry it
ORDER BY ncs.competitor_count DESC, penetration_rate DESC
LIMIT 5;
```

---

## 9. Implementation Phases

### Phase A: Product Table + Filters (2-3 weeks)
**Goal:** Ship standalone product intelligence screen

**Tasks:**
- [ ] Build `ProductIntelligenceTable` component
- [ ] Build `FilterBar` with category/brand/weight/radius
- [ ] Build `PricePositionBadge` component
- [ ] Build `QuickActionButtons` component
- [ ] Create new route `/products` (home screen)
- [ ] Build API endpoint: `GET /api/v1/products/competitive-context`
- [ ] Update Sidebar navigation
- [ ] Deprecate old dashboard routes (remove from nav only)

**Success Criteria:**
- Operator can see all their SKUs with market position
- Can filter by category, brand, weight
- Can take action on individual SKUs
- Page loads in <2 seconds

**Shippable:** YES — can replace current home screen

---

### Phase B: SKU Detail + Competitor View (2 weeks)
**Goal:** Deep-dive capability for individual products

**Tasks:**
- [ ] Build `SKUDetailView` layout
- [ ] Build `CompetitorPriceTable` component
- [ ] Build `PriceHistoryChart` (single chart)
- [ ] Create route `/products/:id`
- [ ] Build API endpoint: `GET /api/v1/products/:id/competitive-landscape`
- [ ] Add click-through from product table to detail

**Success Criteria:**
- Click any SKU to see full competitive landscape
- See price history over 30 days
- See all nearby competitors carrying same SKU

---

### Phase C: Alert Engine + Action Queue (2 weeks)
**Goal:** Proactive decision notifications

**Tasks:**
- [ ] Rewrite `/alerts` page with new design
- [ ] Build `AlertFeed` component
- [ ] Build `AlertActionCard` component
- [ ] Build `ActionRail` sticky sidebar
- [ ] Create alert generation service (backend)
- [ ] Enhance `GET /api/v1/alerts` with action payloads
- [ ] Build `POST /api/v1/alerts/:id/action` endpoint
- [ ] Create alert templates for common scenarios

**Success Criteria:**
- Plain English alerts generated automatically
- One-click actions on alerts
- Unread count badge on nav
- Sticky action rail shows today's priority

---

### Phase D: Report Card v2 (1-2 weeks)
**Goal:** Executive summary for buyer/GM meetings

**Tasks:**
- [ ] Rewrite `/report-card` page
- [ ] Build `RepriceQueueTable` component
- [ ] Build `MissingSKUTable` component
- [ ] Build `MarginLeakTable` component
- [ ] Build `ExportButton` with CSV/PDF options
- [ ] Enhance `GET /api/v1/report-card/:id` for v2 format
- [ ] Add export functionality

**Success Criteria:**
- Top 10 repricing opportunities listed
- Missing high-demand SKUs identified
- Margin leak quantified by category
- One-click export for meetings

---

### Phase E: Polish + Mobile (1 week)
**Goal:** Production-ready experience

**Tasks:**
- [ ] Build `MobileActionQueue` for mobile view
- [ ] Responsive breakpoints for all tables
- [ ] Loading states and error handling
- [ ] Empty states for zero data
- [ ] Performance optimization
- [ ] Remove deprecated viz from production bundle
- [ ] Update documentation

---

## 10. Migration Strategy

### 10.1 Route Migration

```typescript
// Current routes → New routes (during transition)
const TRANSITION_ROUTES = {
  '/': '/products',              // Old home redirects to new
  '/prices': '/products',        // Price wire merges
  '/products/:id': NEW,          // New route
  '/threats': '/alerts',         // Threat radar redirects
  '/recommendations': '/alerts', // Recommendations become alerts
  '/report-card': '/report-card', // Enhance in place
  '/competitors': '/competitors', // Refocus in place
};
```

### 10.2 Component Deprecation

1. **Phase A:** Remove deprecated viz from routes (unmount)
2. **Phase B:** Comment out imports (keep files)
3. **Phase C:** Move to `/archive/` folder
4. **Phase D:** Delete if no regressions

### 10.3 Data Migration

No data migration needed — all changes are UI/frontend only.

---

## 11. Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Time to first decision | 3+ clicks | 1 click | User testing |
| Price action rate | <5% | >30% | Button click analytics |
| Alert engagement | TBD | >50% open rate | Alert tracking |
| Export usage | 0 | >20% weekly | Export analytics |
| Mobile usage | TBD | >40% of sessions | Analytics |
| Page load time | 4s | <2s | Web vitals |
| Support questions | High | -50% | Support tickets |

---

## 12. Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Operators miss old visualizations | Medium | Keep files, easy rollback |
| New API endpoints slow | Medium | Aggressive caching, query optimization |
| Mobile experience poor | Low | Dedicated mobile view in Phase E |
| Alert fatigue | Medium | Smart throttling, preference controls |
| Data quality issues | High | Fallback to "insufficient data" states |

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
│ [Lower Price]   │
├─────────────────┤
│ 💡 RECOMMEND    │
│ Raise price on  │
│ Cookies Gelato  │
│                 │
│ [Raise $3]      │
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
│ [Match $42]     │
├─────────────────┤
│ Big Pine Pre    │
│ $18.00 +12% ▲   │
│ [Match $16]     │
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

**END OF PLAN**

*This is a planning document. DO NOT write code until this plan is reviewed and approved.*
