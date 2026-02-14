# GLASS Visualization Plan
## Premium Data Visualization Architecture for Massachusetts Cannabis Market Intelligence

**Version:** 1.0  
**Date:** February 2026  
**Design System:** Black & White Luxury (Bloomberg Terminal meets Apple)  
**Accent Color:** #C45A3C (Copper/Red)  
**Typography:** Playfair Display (headlines), Geist Mono (data), Geist (body)

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Animation & Transition Guidelines](#animation--transition-guidelines)
3. [Mobile Responsiveness Strategy](#mobile-responsiveness-strategy)
4. [Performance Architecture](#performance-architecture)
5. [Price Intelligence Visualizations](#price-intelligence)
6. [Market Geography Visualizations](#market-geography)
7. [Product Analytics Visualizations](#product-analytics)
8. [Competitive Intelligence Visualizations](#competitive-intelligence)
9. [Regulatory & Threat Visualizations](#regulatory--threat)
10. [Macro Market Visualizations](#macro-market)
11. [Implementation Roadmap](#implementation-roadmap)

---

## Design Principles

### Visual Language
- **Background**: Deep black (#000000) to subtle surface (#0A0A0A)
- **Data Ink**: White (#FFFFFF) primary, muted grays (#999999, #666666) secondary
- **Accent**: Copper/red (#C45A3C) for highlights, alerts, and emphasis
- **Grid Lines**: #1A1A1A — barely visible but present
- **Negative Values**: #EF4444 (red-400)
- **Positive Values**: #22C55E (emerald-400) — use sparingly to avoid "Christmas" effect

### Typography Hierarchy
| Element | Font | Weight | Size |
|---------|------|--------|------|
| Chart Title | Playfair Display | 500 | 18px |
| Axis Labels | Geist Mono | 400 | 10px |
| Data Values | Geist Mono | 500 | 12-14px |
| Tooltips | Geist Mono | 400 | 11px |
| Annotations | Geist | 400 | 12px |

### Data Density
- **Dense Mode**: For power users, show maximum data points
- **Scannable Mode**: Reduced density for presentations
- **Minimal Mode**: Single metric focus for mobile

---

## Animation & Transition Guidelines

### Philosophy
Animations should feel "expensive" — like a luxury timepiece. Smooth, deliberate, never jarring.

### Timing Standards
```typescript
const TRANSITIONS = {
  micro: 150,      // Hover states, button feedback
  standard: 300,   // Chart updates, filter changes
  dramatic: 600,   // Page transitions, major reveals
  ambient: 2000,   // Continuous background motion
};

const EASINGS = {
  // Primary: Exponential ease-out for data updates
  data: 'cubic-bezier(0.16, 1, 0.3, 1)',      // Expo out
  // Secondary: Smooth ease for UI interactions
  ui: 'cubic-bezier(0.4, 0, 0.2, 1)',          // Material standard
  // Accent: Bounce for attention-grabbing reveals
  reveal: 'cubic-bezier(0.34, 1.56, 0.64, 1)', // Slight overshoot
};
```

### Motion Patterns

**Data Entry (Chart Draw)**
- Line charts: Draw from left to right with stroke-dashoffset animation
- Bar charts: Grow from zero with staggered delays (30ms between bars)
- Scatter plots: Fade in with scale from 0.8 to 1
- Area charts: Clip-path reveal from left edge

**Interaction Feedback**
- Hover: 150ms scale(1.02) with glow shadow
- Selection: 200ms border color transition to accent
- Active: Persistent accent glow pulse (subtle)

**Transitions**
- Time range change: Crossfade with 300ms overlap
- Filter application: Staggered exit/enter on data points
- View switch (list→chart): Shared element transition on common data

**Ambient Motion**
- Pulsing dots on live data points: 2s infinite ease-in-out
- Slow grid drift for 3D maps: 0.1deg/s rotation
- Price tickers: Continuous scroll with fade edges

### Accessibility
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Mobile Responsiveness Strategy

### Breakpoints
| Breakpoint | Width | Strategy |
|------------|-------|----------|
| Mobile | < 640px | Single column, minimal chrome, touch-optimized |
| Tablet | 640-1024px | Two column, simplified interactions |
| Desktop | > 1024px | Full feature set, hover states, dense data |

### Mobile Adaptations

**Chart Simplification**
- Remove grid lines (keep axes)
- Reduce data points through sampling (LTTB algorithm)
- Convert complex viz to simpler alternatives:
  - Heat maps → Sorted bar charts
  - 3D maps → 2D choropleth
  - Network graphs → Adjacency matrix
  - Multi-line → Sparkline grid

**Touch Interactions**
- Minimum tap target: 44x44px
- Swipe gestures for time range navigation
- Pinch-to-zoom on maps (native feel)
- Long-press for tooltips (replacing hover)

**Data Density Scaling**
```typescript
const densityMultiplier = {
  mobile: 0.3,   // Show 30% of data points
  tablet: 0.6,
  desktop: 1.0,
};
```

---

## Performance Architecture

### Data Handling (70K+ Products)

**Pre-aggregation Strategy**
```typescript
// Server-side rollups by time granularity
const aggregations = {
  raw: '5min',      // Last 24 hours only
  hour: '1h',       // Last 7 days
  day: '1d',        // Last 90 days
  week: '1w',       // Full history
};
```

**Client-Side Sampling**
- Largest Triangle Three Buckets (LTTB) for line charts
- Quadtree-based spatial indexing for scatter plots
- Virtual scrolling for lists > 100 items
- Web Workers for heavy computations (clustering, force layouts)

**Rendering Optimization**
- Canvas for > 1000 data points (D3 + canvas)
- SVG for < 1000 points (better accessibility)
- Three.js only for 3D geographic views
- Object pooling for animated particles
- GPU acceleration via transform3d

### Memory Management
```typescript
// LRU cache for fetched data
const dataCache = new LRUCache({
  max: 50,  // Max 50 datasets
  ttl: 1000 * 60 * 5,  // 5 minute TTL
});

// Dispose Three.js resources
const dispose = (scene) => {
  scene.traverse((obj) => {
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) {
      if (Array.isArray(obj.material)) {
        obj.material.forEach(m => m.dispose());
      } else {
        obj.material.dispose();
      }
    }
  });
};
```

---

## Price Intelligence

### 1. Price Positioning Matrix ("The Grid")

**Name:** Price Positioning Matrix  
**Description:** Interactive scatter plot showing your prices vs. market distribution across product categories

**Business Question:** "Am I priced competitively for flower in my area? Am I leaving money on the table?"

**Data Sources:**
- Product prices (Dutchie + Weedmaps)
- Operator locations
- Product categories
- Your dispensary's current pricing

**Library:** D3.js (SVG for interaction density)

**Interaction Model:**
- **Primary:** Drag to pan, scroll to zoom (brush for selection)
- **Filters:** Category dropdown, brand multi-select, THC% range slider
- **Views:** Switch between "vs Market Average", "vs Lowest Competitor", "vs Your Position"
- **Compare Mode:** Checkbox to overlay your prices as highlighted points
- **Time Scrubber:** Bottom timeline to scrub through historical positioning

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  PRICE POSITIONING MATRIX                          [?] [⚙] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    ↑                                                        │
│  $ │      ·  ·    ·    ·  ·     ◆ YOU                ·     │
│  P │    ·    ·  ·    ·    ·  ·      ·    ·  ·  ·    ·      │
│  R │  ·   ·    ·    ·  ·    ·    ·    ·    ·  ·    ·  ·    │
│  I │     ·  ·    ·    ◆ YOU    ·    ·    ·    ·  ·    ·    │
│  C │   ·    ·  ·    ·    ·  ·    ·    ·  ·    ·    ·       │
│  E │ ·   ·    ·    ·    ·    ·  ·    ·    ·    ·  ·   ·    │
│    └────────────────────────────────────────────────→       │
│         MARKET AVERAGE PRICE                                │
│                                                             │
│  [Flower ▼] [All Brands ▼] [THC: 15-30% ▼]  [Compare: ☑]   │
│                                                             │
│  ◆ = Your Price    · = Competitor    Size = Volume         │
└─────────────────────────────────────────────────────────────┘
```

- **Axes:** X = Market Average Price, Y = Your Price (or selected competitor)
- **Points:** 
  - Gray circles (#666666) for competitor products
  - Size proportional to sales volume (if available) or market presence
  - Copper diamond (#C45A3C, ◆) for your products
- **Quadrant Lines:** Dotted #1A1A1A lines at 45-degree showing premium/discount zones
- **Tooltip:** Product name, brand, your price, market avg, percentile rank

**Where it Lives:** `/prices/positioning` — dedicated page with full-screen layout

**Wow Factor:** 
- Real-time quadrant labeling: "Premium Position" / "Value Leader" / "Underpricing" / "Market Rate"
- Smart clustering at high zoom levels
- "What-if" slider: Drag your price point to see revenue impact projection

**Priority:** P0  
**Complexity:** M  
**Estimated Dev:** 3-4 days

---

### 2. Price Volatility Ribbon

**Name:** Price Volatility Ribbon  
**Description:** Multi-layered area chart showing price variance bands over time

**Business Question:** "How stable is the market for vape cartridges? Should I lock in inventory?"

**Data Sources:**
- Historical prices (daily aggregates)
- Category classifications
- Product weight/quantity normalization

**Library:** D3.js (SVG with canvas optimization for large time ranges)

**Interaction Model:**
- **Hover:** Crosshair with exact values, distribution histogram for that day
- **Range Selector:** Brushable mini-chart below main chart
- **Normalize Toggle:** Switch between absolute prices and $/gram equivalent
- **Volatility Mode:** Toggle to show standard deviation bands vs. price ranges

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  PRICE VOLATILITY: FLOWER                         [30D▼]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  $60 ┤ ╭─╮                                                 │
│  $55 ┤╭╯ ╰╮    ╭──────MAX                                  │
│  $50 ┤╯    ╰──╮╭╯      ╭──────75th %ile                    │
│  $45 ┤────────╯╰──────╮╭──────MEDIAN (solid white)         │
│  $40 ┤                ╰╯──────25th %ile                    │
│  $35 ┤───────────────────────MIN                           │
│      └────┬────┬────┬────┬────┬────┬────┬────→            │
│          Jan  Feb  Mar  Apr  May  Jun  Jul                 │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  [                    brushable range                    ] │
└─────────────────────────────────────────────────────────────┘
```

- **Layers (bottom to top):**
  1. Min-Max range: Subtle gray fill (#1A1A1A)
  2. 25th-75th percentile: Slightly lighter (#2A2A2A)
  3. Median: Solid white stroke (2px)
- **Your Price Line:** Copper (#C45A3C) overlay, dashed when outside market range
- **Alert Zones:** Red tinted background when volatility exceeds 15% CV

**Where it Lives:** `/prices/volatility` — embeddable widget also on Morning Brief

**Wow Factor:**
- "Volatility Weather Report": Animated sparkline icon showing current stability
- Predictive band: ML-based 7-day forecast with confidence interval
- Category comparison: Overlay multiple categories with opacity control

**Priority:** P0  
**Complexity:** M  
**Estimated Dev:** 3 days

---

### 3. Price Change Cascade

**Name:** Price Change Cascade  
**Description:** Animated waterfall showing sequential price changes across the market

**Business Question:** "Who started the price war on pre-rolls? How did it spread?"

**Data Sources:**
- Price change events with timestamps
- Operator hierarchy/geography
- Product matching across operators

**Library:** D3.js (force-directed layout with custom forces)

**Interaction Model:**
- **Play/Pause:** Animated playback of price changes over time
- **Speed Control:** 1x, 5x, 10x playback speeds
- **Filter:** Product, date range, operator type
- **Click Node:** Freeze and show detailed change history for that operator

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  PRICE CASCADE: PRE-ROLL PRICE WAR        [▶] [═] [5x]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│     ┌───┐                                                   │
│     │ A │ ─────┐                                            │
│     └───┘      │                                            │
│                ▼                                            │
│     ┌───┐   ┌───┐   ┌───┐                                  │
│     │ B │◄──│ C │──►│ D │                                  │
│     └───┘   └───┘   └───┘                                  │
│       │                    ╭─── Reaction chain              │
│       ▼                    │   3 days to propagate          │
│     ┌───┐   ┌───┐         │                                 │
│     │ E │──►│ F │◄────────╯                                 │
│     └───┘   └───┘                                           │
│                                                             │
│  ○ = No change    ↓ = Price Drop    ↑ = Price Increase     │
│  Line opacity = Strength of correlation                      │
└─────────────────────────────────────────────────────────────┘
```

- **Nodes:** Operator circles, size = market share, color = price change direction
- **Edges:** Curved lines showing influence/sequence, animated dash for flow
- **Timeline Scrubber:** Bottom control showing current playback position

**Where it Lives:** `/prices/cascade` — research/intelligence tool

**Wow Factor:**
- "Patient Zero" detection: Algorithmically identify who moved first
- Contagion metrics: "Price change reached 80% of market in 4.2 days"
- Export as shareable animated GIF/video

**Priority:** P1  
**Complexity:** L  
**Estimated Dev:** 5-6 days

---

### 4. Real-Time Price Ticker Wall

**Name:** Price Ticker Wall  
**Description:** Bloomberg-style scrolling ticker showing live price updates

**Business Question:** "What's happening right now in the market?"

**Data Sources:**
- Real-time price change stream
- Product catalog
- Operator registry

**Library:** Custom React + CSS animations (no D3 needed)

**Interaction Model:**
- **Pause on Hover:** Freeze ticker for reading
- **Click Item:** Navigate to product detail
- **Filter Strip:** Toggle categories to show/hide from ticker
- **Sound Toggle:** Optional audio cue on significant changes

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  LIVE PRICE CHANGES                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  ◄──────────────────────────────────────────────────────►  │
│                                                             │
│  BLUE DREAM 3.5g  THEORY WELLNESS  $42.00 → $38.50  -8.3%  │
│  GELATO 1g  COMMONWEALTH DISP  $15.00 → $18.00  +20.0%     │
│  WEDDING CAKE .5g  CURALEAF  $35.00 → $32.00  -8.6%       │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
│  [Flower●] [Vape●] [Edible○] [Concentrate●] [Pre-roll○]    │
└─────────────────────────────────────────────────────────────┘
```

- **Layout:** Two scrolling bands moving in opposite directions
- **Typography:** Geist Mono throughout
- **Color Coding:** Green for increases, red for decreases (market convention)
- **Speed:** Adjustable 1-5x

**Where it Lives:** Dashboard header banner + standalone `/prices/live`

**Wow Factor:**
- "Market Pulse" visualization: Subtle background brightness shifts with update frequency
- Breaking change alerts: Full-width flash for >20% moves
- Historical replay: Scroll back through today's changes

**Priority:** P1  
**Complexity:** S  
**Estimated Dev:** 2 days

---

## Market Geography

### 5. 3D Market Terrain Map

**Name:** Market Terrain Map  
**Description:** Three.js elevation map of Massachusetts showing competitive density as topography

**Business Question:** "Where is the market oversaturated? Where are the greenfield opportunities?"

**Data Sources:**
- Dispensary geocoded locations
- Delivery zone polygons
- License data (active + pending)
- Population density (census data)

**Library:** Three.js + React Three Fiber

**Interaction Model:**
- **Navigation:** OrbitControls (rotate, zoom, pan)
- **Layer Toggle:** Population | Competitor Count | Price Level | Delivery Coverage
- **Time Scrubber:** Watch the terrain evolve as licenses are approved
- **Click Location:** Fly-to with detailed market breakdown

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  MARKET TERRAIN: MASSACHUSETTS                       [?]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ╭──────╮                                 │
│              ╭────╯  BOS  ╰────╮        High density peaks │
│             ╭╯    ╭────────╮    ╰╮                          │
│            ╭╯    ╭╯ WORCESTER╰╮   ╰╮                        │
│           ╭╯    ╭╯            ╰╮   ╰╮      ◄─── Springfield│
│    ◄────╭─╯    ╭╯  PIONEER VALLEY╰╮   ╰──╮                  │
│  ALBANY│      ╭╯                   ╰╮     ╰╮               │
│        ╰─────╯                       ╰──────╯               │
│                                                             │
│  [Competitor Density ▼]  [Mar 2024 ▓▓▓▓▓░░░]  [Reset ▣]    │
│                                                             │
│  Height = Competitor count  Color = Avg price level         │
└─────────────────────────────────────────────────────────────┘
```

- **Terrain:** Exaggerated elevation for visual clarity (2-3x scale)
- **Color Ramp:**
  - Black (low) → Gray (medium) → Copper highlight (high activity)
  - OR heatmap: Blue → White → Red for different metrics
- **Labels:** Floating markers for major cities, fade with distance
- **Your Position:** Pulsing beacon with 3D ripple effect

**Where it Lives:** `/map/terrain` — premium feature for strategic planning

**Wow Factor:**
- "Time Machine": Scrub through years of license approvals watching terrain grow
- Fog of War: Undiscovered areas (no data) shown with actual fog effect
- Flight mode: Automated cinematic fly-throughs of your market

**Priority:** P1  
**Complexity:** XL  
**Estimated Dev:** 8-10 days

---

### 6. Delivery Zone Voronoi

**Name:** Delivery Zone Voronoi  
**Description:** Voronoi diagram showing service area coverage and gaps

**Business Question:** "Where can I legally deliver? Where are my competitors' weak spots?"

**Data Sources:**
- Delivery license locations
- Maximum delivery radii (regulatory)
- Actual service polygons (where available)
- Address/zip code centroids

**Library:** D3.js (d3-voronoi) with canvas rendering

**Interaction Model:**
- **Hover Cell:** Highlight delivery operator and show coverage stats
- **Overlap Toggle:** Show areas covered by multiple operators
- **Gap Highlight:** Toggle to show unserved areas
- **Your Location:** Click to set your position and see projected coverage

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  DELIVERY COVERAGE MAP                          [Gaps ▣]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │    ╱╲        ╱──────────────────────╲              │   │
│  │   ╱A ╲      ╱                        ╲    ┌───┐   │   │
│  │  ╱────╲    ╱           B              ╲   │ G │   │   │
│  │ ╱      ╲  ╱                            ╲  └───┘   │   │
│  │╱   C    ╲╱                              ╲________ │   │
│  │          ╲                                     ╱   │   │
│  │           ╲    ┌──────────────────┐           ╱    │   │
│  │            ╲   │                  │          ╱  F  │   │
│  │             ╲  │        D         │    ┌────┐      │   │
│  │              ╲ │                  │    │ E  │      │   │
│  │               ╲└──────────────────┘    └────┘      │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Legend: Cell = Delivery zone  ▓▓▓ = Overlap  ░░░ = Gap    │
└─────────────────────────────────────────────────────────────┘
```

- **Cells:** Semi-transparent fill (#C45A3C at 20% opacity for competitors, white at 30% for you)
- **Borders:** Solid lines, color-coded by operator
- **Gaps:** Pulsing pattern fill in unserved areas
- **Overlap:** Darker blending where zones intersect

**Where it Lives:** `/map/delivery` + widget on competitor detail pages

**Wow Factor:**
- Optimization suggestion: "Moving 2 miles north would cover 15,000 more residents"
- Gap opportunity scoring: Heat overlay on gaps showing demand potential

**Priority:** P1  
**Complexity:** M  
**Estimated Dev:** 4 days

---

### 7. Competitive Proximity Radar

**Name:** Competitive Proximity Radar  
**Description:** Polar/radar visualization of competitors by distance and threat level

**Business Question:** "Who are my closest competitors? Who poses the biggest threat?"

**Data Sources:**
- Geocoded locations
- Distance calculations
- Threat scoring algorithm
- Price comparison data

**Library:** D3.js (radar chart with custom radial force)

**Interaction Model:**
- **Your Position:** Center of radar
- **Ring Toggle:** Distance rings (1mi, 3mi, 5mi, 10mi)
- **Filter:** Show only new threats, only price competitors, etc.
- **Click Competitor:** Expand detail card with side-by-side comparison

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  COMPETITIVE RADAR: YOUR POSITION                    [⚙]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                        N                                    │
│                        │                                    │
│                   ╭────┼────╮                               │
│              ╭────╯ 10mi    ╰────╮                          │
│         ╭────╯         │         ╰────╮                     │
│        ╱   ·  ·    5mi─┼─·  ·  ·       ╲                    │
│       ╱  ·   ·    ·    │    ·    ·   ·  ╲                   │
│   W ─┤············3mi──┼──···············├─ E               │
│       ╲  ·   ·    ·    │    ·    ·   ·  ╱                   │
│        ╲   ·  ·    1mi─┼─·  ·  ·       ╱                    │
│         ╰────╮    ·    ●    ·    ╭────╯                     │
│              ╰────╯    │    ╰────╯        ● = You           │
│                   ╰────┼────╯          ◆ = High threat      │
│                        │               ◇ = Low threat       │
│                        S                                    │
│                                                             │
│  [1mi] [3mi] [5mi] [10mi]    [New Only ○] [Price War ○]    │
└─────────────────────────────────────────────────────────────┘
```

- **Rings:** Concentric circles with distance labels
- **Competitors:** 
  - Diamond markers (◆)
  - Size = threat score
  - Color intensity = price aggressiveness
  - Distance from center = actual distance (to scale)
  - Angular position = compass bearing
- **Pulse Animation:** New threats emit expanding rings for 10 seconds

**Where it Lives:** `/threats/radar` + dashboard widget

**Wow Factor:**
- Threat sonar: Subtle ping sound on new competitor entry (optional)
- Range estimation: "This competitor is within delivery range of your location"
- Cluster detection: Highlight areas with multiple competitors

**Priority:** P0  
**Complexity:** M  
**Estimated Dev:** 3-4 days

---

## Product Analytics

### 8. Brand Market Share Treemap

**Name:** Brand Market Share Treemap  
**Description:** Hierarchical treemap showing brand dominance across categories

**Business Question:** "Which brands are winning? Where should I focus my shelf space?"

**Data Sources:**
- Product counts by brand
- Price positioning by brand
- Category classifications
- Store placement data (if available)

**Library:** D3.js (d3-hierarchy) with zoomable treemap

**Interaction Model:**
- **Click to Zoom:** Drill into category → brand → individual products
- **Color Mode:** Toggle between "Market Share", "Price Tier", "Growth Rate"
- **Search:** Find specific brands with auto-zoom
- **Compare:** Multi-select brands for side panel comparison

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  BRAND LANDSCAPE: FLOWER                          [📊▼]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┬───────────┬─────────────────────┐     │
│  │                 │           │                     │     │
│  │   THEORY        │  CURALEAF │    RYTHM            │     │
│  │   WELLNESS      │           │                     │     │
│  │                 │───────────┤                     │     │
│  │   23% share     │  BUDDY'S  ├─────────────────────┤     │
│  │                 │  CANNABIS │    OTHER            │     │
│  │                 │           │    BRANDS           │     │
│  │                 │   8%      │    31%              │     │
│  ├─────────────────┴───────────┴─────────────────────┤     │
│  │                                                   │     │
│  │   NATURE'S HERITAGE                               │     │
│  │   18%                                             │     │
│  │                                                   │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
│  Size = SKU count  Color = Price tier  ◄── Back │ Zoom ►  │
└─────────────────────────────────────────────────────────────┘
```

- **Layout:** Squarified treemap for optimal aspect ratios
- **Colors:** 
  - Grayscale gradient for market share (darker = larger)
  - OR diverging scale for growth (red = declining, white = flat, green = growing)
- **Borders:** 1px #0A0A0A between cells
- **Labels:** Centered brand name + percentage, fade if cell too small

**Where it Lives:** `/products/brands` + embeddable widget

**Wow Factor:**
- Animated transitions on category switch (cells morph to new positions)
- "Rising Stars" highlight: Pulse animation on fastest-growing brands
- Empty space overlay: Show whitespace opportunity areas

**Priority:** P0  
**Complexity:** M  
**Estimated Dev:** 4 days

---

### 9. Category Mix Sunburst

**Name:** Category Mix Sunburst  
**Description:** Radial partition diagram showing product distribution across categories

**Business Question:** "How does my inventory mix compare to the market? Am I over-indexed on flower?"

**Data Sources:**
- Product categorization (flower, edible, vape, concentrate, preroll)
- Subcategory data (indica/sativa/hybrid, flavor profiles)
- Your inventory (if connected)

**Library:** D3.js (d3-hierarchy partition with custom radius)

**Interaction Model:**
- **Hover:** Highlight arc path to center, show breadcrumb trail
- **Click:** Zoom into that segment (focus mode)
- **Compare Ring:** Toggle to show your mix as inner ring vs. market as outer
- **Animation:** Rotate to align selected category at top

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  CATEGORY MIX ANALYSIS                              [?]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────┐                              │
│              ┌─────┤  FLOWER ├─────┐                        │
│              │ 45% └────┬────┘     │                        │
│              │    ╭────┴────╮      │                        │
│              │   ╱           ╲     │                        │
│         ┌────┤  ╱   INDICA   ╲    ├────┐                    │
│         │VAPE│ ╱      20%      ╲   │EDIBLE│                  │
│         │18% │╱                  ╲  │ 12%  │                  │
│         │    │      SATIVA        │ │      │                  │
│         │    │        15%         │ │      │                  │
│         │    │                    │ │      │                  │
│         │    ╲    HYBRID         ╱  │      │                  │
│         │     ╲     10%         ╱   │      │                  │
│         │      ╰───────────────╯    │      │                  │
│         └───────────────────────────┴──────┘                  │
│                                                             │
│  [Market Mix ●] [Your Mix ○]  [←Reset]  [Deep Dive ►]       │
│                                                             │
│  Selected: FLOWER > INDICA > 156 products                   │
└─────────────────────────────────────────────────────────────┘
```

- **Rings:** 
  - Inner: Major categories (Flower, Vape, Edible, etc.)
  - Middle: Subcategories (Indica/Sativa/Hybrid, etc.)
  - Outer: Price tiers or brand segments
- **Colors:** Category-specific palette (subtle distinctions, not rainbow)
  - Flower: #FFFFFF (white)
  - Vape: #C0C0C0 (silver)
  - Edible: #A0A0A0 (gray)
  - Concentrate: #808080 (dark gray)
  - Pre-roll: #C45A3C (copper accent)
- **Compare Mode:** Split arcs showing market vs. your mix

**Where it Lives:** `/products/categories` + inventory planning tool

**Wow Factor:**
- Opportunity gaps: Animated "grow" suggestion showing optimal mix
- Trend arrows: Small indicators on segments showing 30-day direction
- Breadcrumb navigation: Clickable path at top for easy drilling

**Priority:** P0  
**Complexity:** M  
**Estimated Dev:** 4 days

---

### 10. Strain Popularity Stream

**Name:** Strain Popularity Stream  
**Description:** Streamgraph showing strain popularity trends over time

**Business Question:** "Which strains are trending up? Which classics are fading?"

**Data Sources:**
- Product names parsed for strain identification
- Appearance frequency over time
- Price premium data by strain

**Library:** D3.js (d3-shape stack with basis interpolation)

**Interaction Model:**
- **Hover:** Highlight single stream, dim others
- **Search:** Filter to specific strains
- **Time Brush:** Select date range for detailed view
- **Normalize Toggle:** Absolute count vs. percentage share

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  STRAIN TRENDS: TOP 10                           [Norm ▣]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    100% ┤ ╭───╮                                           │
│         │╭╯   ╰──╮     ╭────── GELATO                      │
│     80% ┤╯       ╰╮   ╭╯                                   │
│         │          ╰─╮╯                                    │
│     60% ┤     ╭──────╯╮────── BLUE DREAM                   │
│         │  ╭──╯        ╰╮                                  │
│     40% ┤──╯             ╰──── WEDDING CAKE                │
│         │                                                  │
│     20% ┤─────────────────────── OTHER STRAINS             │
│         │                                                  │
│      0% └────┬────┬────┬────┬────┬────┬────┬────→         │
│             Jan  Feb  Mar  Apr  May  Jun  Jul              │
│                                                             │
│  Color = Price premium  Thickness = SKU count              │
└─────────────────────────────────────────────────────────────┘
```

- **Streams:** Smooth curves (basis interpolation) for organic feel
- **Colors:** Sequential gray to copper based on price premium
- **Ordering:** Layered by average popularity (most popular on top)
- **Labels:** Appear on hover with exact values

**Where it Lives:** `/products/strains` + trend report embed

**Wow Factor:**
- "Rising" and "Fading" badges: Auto-detected trends with icons
- Predictive overlay: ML forecast for next 30 days (dashed line)
- Cross-reference: Click strain to see all products using it

**Priority:** P1  
**Complexity:** M  
**Estimated Dev:** 4 days

---

## Competitive Intelligence

### 11. Operator Comparison Matrix

**Name:** Operator Comparison Matrix  
**Description:** Parallel coordinates or radar chart comparing multiple operators across metrics

**Business Question:** "How do I stack up against my top 3 competitors across all dimensions?"

**Data Sources:**
- Operator profiles
- Price aggregations by operator
- Product counts by category
- Review/rating data (if available)

**Library:** D3.js (parallel coordinates with brushing)

**Interaction Model:**
- **Multi-Select:** Add/remove operators from comparison (max 5)
- **Axis Reordering:** Drag to reorder comparison dimensions
- **Invert Axis:** Flip scales for "lower is better" metrics
- **Filter Brush:** Drag along axes to filter operators

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  OPERATOR COMPARISON                               [⚙]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Avg Price │ SKU Count │ Flower % │ Vape % │ Reviews        │
│      │          │          │         │         │             │
│  $60 ┤          │          │    ●    │         │             │
│      │    ●     │    ●     │   ╱│╲   │    ●    │       ●     │
│  $45 ┤   ╱│╲    │   ╱│╲    │  ╱ │ ╲  │   ╱│╲   │      ╱│╲    │
│      │  ╱ │ ╲   │  ╱ │ ╲   │ ●  │  ● │  ╱ │ ╲  │     ╱ │ ╲   │
│  $30 ┤ ●  │  ╲  │ ●  │  ╲  │    │    │ ●  │  ╲ │    ●  │  ╲  │
│      │    │   ● │    │   ● │    │    │    │   ●│       │   ● │
│  $15 ┤    │     │    │     │    │    │    │    │       │     │
│      └────┴─────┴────┴─────┴────┴────┴────┴────┴───────┴─────┤
│                                                             │
│  ●─── Theory Wellness (You)                                 │
│  ╱╲── Curaleaf                                              │
│  ◆─── Rythm                                                 │
│                                                             │
│  [+ Add Operator]  [Clear All]  [Export CSV]                │
└─────────────────────────────────────────────────────────────┘
```

- **Lines:** 
  - Solid white: Your operator
  - Dashed gray: Competitors
  - Line thickness: Market share
- **Axes:** Vertical scales for each metric, labeled at top
- **Brushing:** Semi-transparent overlay on axes for range selection

**Where it Lives:** `/operators/compare` + competitor profile pages

**Wow Factor:**
- "Similar To You" suggestion: Algorithmic matching of comparable operators
- Outlier highlighting: Glow effect on unusual patterns
- Hover intersection: Show exact values where cursor crosses lines

**Priority:** P0  
**Complexity:** M  
**Estimated Dev:** 4 days

---

### 12. Market Share Flow (Sankey)

**Name:** Market Share Flow  
**Description:** Sankey diagram showing market share transitions over time

**Business Question:** "Who's gaining share? Where are customers switching?"

**Data Sources:**
- Product availability by operator over time
- Estimated market share proxies
- New license/closure events

**Library:** D3.js (d3-sankey with custom node positioning)

**Interaction Model:**
- **Time Animation:** Play through periods watching flows shift
- **Node Hover:** Highlight all connected flows
- **Flow Hover:** Show volume and direction
- **Drill Down:** Click operator to see category-level breakdown

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  MARKET SHARE FLOW: Q1 → Q2 2024                  [▶▶▲]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Q1 2024                    Transitions              Q2 2024│
│                                                             │
│  ┌─────────┐                                        ┌─────┐ │
│  │THEORY   │═══════════════╗                        │THEORY│ │
│  │25%      │──────────╮    ║    ╭──────────────────►│ 28%  │ │
│  └────┬────┘          │    ║    │                   └──┬──┘ │
│       │               ▼    ▼    │                      │     │
│       │         ┌───────────┐   │                      │     │
│       │         │  CURALEAF │   │                      │     │
│       │         │    22%    │◄──┘                      │     │
│       │         └─────┬─────┘                          │     │
│       │               │                                │     │
│       │    ╭──────────┘                                │     │
│  ┌────┴────┤                                          ▼     │
│  │ OTHER   │◄───────────────────────────────────┌────────┐  │
│  │ 53%     │                                    │ OTHER  │  │
│  └─────────┘                                    │  50%   │  │
│                                                 └────────┘  │
│                                                             │
│  Line width = Share transfer volume  Color = Operator       │
└─────────────────────────────────────────────────────────────┘
```

- **Nodes:** Rectangles sized by market share
- **Flows:** Curved bands with width proportional to share movement
- **Colors:** Operator-specific, consistent across time
- **Animation:** Flows pulse with directional arrow indicators

**Where it Lives:** `/market/flows` + quarterly report section

**Wow Factor:**
- Event annotations: Vertical markers showing license approvals/closures
- Predictive flow: Ghost flows showing projected Q3 movements
- Gain/Loss summary: Side panel with biggest winners and losers

**Priority:** P1  
**Complexity:** L  
**Estimated Dev:** 5-6 days

---

### 13. Price War Heatmap

**Name:** Price War Heatmap  
**Description:** Calendar heatmap showing intensity of price competition over time

**Business Question:** "When are price wars most likely? What triggered the last one?"

**Data Sources:**
- Daily price variance by category
- Price change frequency
- Competitor clustering data

**Library:** D3.js (calendar heatmap with d3-time)

**Interaction Model:**
- **Hover Date:** Tooltip with daily summary of price activity
- **Click Date:** Navigate to detailed Price Wire for that day
- **Zoom:** Month view → Quarter view → Year view
- **Category Filter:** Toggle which categories contribute to heat

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  PRICE WAR INTENSITY: 2024                        [Cat ▼]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│     J  F  M  A  M  J  J  A  S  O  N  D                     │
│  Su ▓  ░  ▓  ░  ▒  ░  ▓  ▓  ░  ▒  ░  ▓                     │
│  Mo ░  ▒  ▓  ░  ░  ▒  ▓  ░  ░  ▓  ░  ░                     │
│  Tu ▒  ░  ▓  ▓  ░  ░  ▓  ▒  ░  ░  ▒  ░                     │
│  We ░  ░  ▓  ░  ▒  ░  ▓  ░  ▒  ░  ░  ▓                     │
│  Th ▓  ▒  ▓  ░  ░  ▓  ▓  ░  ░  ▒  ░  ░                     │
│  Fr ░  ░  ▓  ▒  ░  ░  ▓  ▓  ░  ░  ▓  ▒                     │
│  Sa ▒  ░  ▓  ░  ░  ▒  ▓  ░  ░  ▓  ░  ░                     │
│                                                             │
│  ░ = Low activity   ▒ = Moderate   ▓ = High price war      │
│                                                             │
│  Selected: July 15 — 23 price changes, 3 new lows          │
└─────────────────────────────────────────────────────────────┘
```

- **Cells:** 
  - Color intensity = number of significant price changes (>5%)
  - Border color = presence of new market lows
- **Legend:** Discrete scale (low/medium/high/war)
- **Navigation:** Month selector dropdown + prev/next arrows

**Where it Lives:** `/prices/wars` + Morning Brief widget

**Wow Factor:**
- Event overlay: Icons on dates showing license approvals or major news
- Pattern detection: "Price wars typically start on Thursdays"
- Anomaly alerts: Auto-highlighted cells requiring attention

**Priority:** P1  
**Complexity:** S  
**Estimated Dev:** 2-3 days

---

## Regulatory & Threat

### 14. CCC Action Timeline

**Name:** CCC Action Timeline  
**Description:** Interactive timeline of Cannabis Control Commission regulatory actions

**Business Question:** "What regulatory changes are coming? How will they affect my business?"

**Data Sources:**
- CCC meeting minutes
- License application data
- Violation and fine records
- Regulation amendments

**Library:** D3.js (horizontal timeline with zoom)

**Interaction Model:**
- **Scroll/Zoom:** Navigate through time (past and future)
- **Filter:** Event types (approvals, violations, policy changes)
- **Proximity Alert:** Toggle to show only events near your location
- **Click Event:** Expand details with full document links

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  REGULATORY TIMELINE                              [🔍▼]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TODAY                                                      │
│    │                                                        │
│    ▼                                                        │
│ ───┼────────────────────────────────────────────────────    │
│    │    ⚑                ⚑                                 │
│    │    │                 │                                 │
│    │    ▼                 ▼                                 │
│  ──┴────┴────────┬────────┴────────────────────────────    │
│           ┌──────┴──────┐                                   │
│           │  New License │                                 │
│           │  Approved    │                                 │
│           │  0.3mi away  │⚠                                │
│           └──────────────┘                                   │
│                        ▲                                    │
│                   ┌────┘                                    │
│                   │                                         │
│                   ▼                                         │
│              ┌─────────┐                                    │
│              │Violation│                                    │
│              │  Fined  │                                    │
│              └─────────┘                                    │
│                                                             │
│  ⚑ = License   ⚠ = Violation   📋 = Policy Change         │
└─────────────────────────────────────────────────────────────┘
```

- **Timeline:** Horizontal axis with zoom capability
- **Events:** Icons positioned at date points
  - Flag (⚑): New license
  - Warning (⚠): Violation/fine
  - Document (📋): Policy change
- **Your Position:** Vertical marker at "TODAY" with connecting lines to nearby events
- **Severity:** Icon size and color intensity (copper for proximity alerts)

**Where it Lives:** `/regulatory/timeline` + compliance dashboard

**Wow Factor:**
- Proximity scoring: "This license is 0.3 miles from your location — HIGH THREAT"
- Upcoming deadlines: Pulsing animation on approaching action dates
- Full text search: Search within meeting minutes and documents

**Priority:** P0  
**Complexity:** M  
**Estimated Dev:** 4 days

---

### 15. License Pipeline Funnel

**Name:** License Pipeline Funnel  
**Description:** Funnel chart showing license applications moving through approval stages

**Business Question:** "How many new competitors are in the pipeline? When might they open?"

**Data Sources:**
- CCC application status database
- Historical approval timing
- Geographic distribution of applicants

**Library:** D3.js (custom funnel with animated transitions)

**Interaction Model:**
- **Hover Stage:** Show count and average time in stage
- **Click Stage:** List all applications in that stage
- **Geography Filter:** Limit to specific regions
- **Time Projection:** Toggle to show expected approval dates

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  LICENSE PIPELINE: DISPENSARIES                   [📍▼]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│           ╭─────────────────────────────╮                   │
│           │      APPLICATION            │  47               │
│           │        SUBMITTED            │  ~90 days         │
│           ╰────────────┬────────────────╯                   │
│                        │                                    │
│                        ▼                                    │
│              ╭────────────────────╮                         │
│              │  UNDER REVIEW      │  23                    │
│              │                    │  ~60 days              │
│              ╰──────────┬─────────╯                         │
│                         │                                   │
│                         ▼                                   │
│                 ╭───────────────╮                           │
│                 │  CONDITIONAL  │  12                      │
│                 │   APPROVAL    │  ~30 days                │
│                 ╰───────┬───────╯                           │
│                         │                                   │
│                         ▼                                   │
│                    ╭─────────╮                              │
│                    │  FINAL  │  5                          │
│                    │APPROVAL │  ~14 days                   │
│                    ╰────┬────╯                              │
│                         │                                   │
│                         ▼                                   │
│                       ╭───╮                                 │
│                       │OPEN│  3  ← Expected next month     │
│                       ╰───╯                                 │
│                                                             │
│  [Show Map ▣]  [Export List]  [Set Alert for New Apps]     │
└─────────────────────────────────────────────────────────────┘
```

- **Shape:** Trapezoidal funnel, each stage narrower than last
- **Labels:** Stage name (center), count (right), avg duration (below)
- **Colors:** Gradient from gray (submitted) to copper (opening)
- **Animation:** Gentle pulse on stages with recent activity

**Where it Lives:** `/regulatory/pipeline` + threat intel dashboard

**Wow Factor:**
- Time estimation: ML-based prediction of when each app will reach final approval
- Geographic overlay: Mini-map showing pipeline locations
- Alert subscription: "Notify me when new applications are submitted near me"

**Priority:** P1  
**Complexity:** M  
**Estimated Dev:** 3-4 days

---

### 16. Threat Alert Network

**Name:** Threat Alert Network  
**Description:** Force-directed graph showing relationships between threats and affected operators

**Business Question:** "How connected are the threats I'm facing? Is this a coordinated market shift?"

**Data Sources:**
- Threat intelligence feeds
- Operator relationship mapping
- Price correlation analysis

**Library:** D3.js (force simulation with custom forces) + canvas for performance

**Interaction Model:**
- **Drag Nodes:** Reposition for clearer view
- **Hover Node:** Highlight connected threats
- **Click Node:** Threat detail panel
- **Filter:** Severity, type, time range
- **Cluster Toggle:** Group by threat type or geography

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  THREAT NETWORK                                   [⚙]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────┐                              │
│              ┌─────┤  NEW    ├─────┐                        │
│              │     │LICENSE  │     │                        │
│              │     └────┬────┘     │                        │
│              │          │          │                        │
│         ┌────┴───┐   ┌──┴──┐   ┌───┴───┐                   │
│         │PRICE   │   │ YOU │   │COMP B │                   │
│         │DROP    │   │ ●   │   │       │                   │
│         └────┬───┘   └──┬──┘   └───┬───┘                   │
│              │          │          │                        │
│              │      ┌───┴───┐      │                        │
│              │      │PRICE  │      │                        │
│              └─────►│MATCH  │◄─────┘                        │
│                     └───────┘                               │
│                                                             │
│  ● = You  ○ = Competitor  □ = Threat event                  │
│  Line = Connection  Line width = Threat strength            │
│                                                             │
│  [Severity: All▼] [Type: All▼] [Cluster by: None▼]         │
└─────────────────────────────────────────────────────────────┘
```

- **Nodes:** 
  - You: Large copper circle with pulse
  - Competitors: Gray circles sized by threat level
  - Threats: Squares with type icons
- **Edges:** Lines connecting related entities
  - Solid: Direct threat to you
  - Dashed: Competitor-competitor relationship
- **Simulation:** Gentle floating motion, settles on drag release

**Where it Lives:** `/threats/network` + primary threat dashboard

**Wow Factor:**
- Pattern detection: Auto-identify threat clusters requiring attention
- Causal chain: Animated path showing how threats propagate
- Scenario planning: "What if" mode to simulate threat mitigation

**Priority:** P0  
**Complexity:** L  
**Estimated Dev:** 5-6 days

---

## Macro Market

### 17. Total Market Size Chart

**Name:** Total Market Size Chart  
**Description:** Area chart showing estimated total Massachusetts cannabis market over time

**Business Question:** "Is the market growing? How big is the pie I'm competing for?"

**Data Sources:**
- Aggregated price × estimated volume
- CCC sales data (if available)
- License count and type

**Library:** D3.js (stacked area with uncertainty bands)

**Interaction Model:**
- **Hover:** Show exact value and growth rate
- **Breakdown Toggle:** View by category, region, or channel
- **Projection Toggle:** Show/hide forecast segments
- **Benchmark:** Overlay other state markets for comparison

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  MASSACHUSETTS MARKET SIZE                        [Cat ▼]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  $5B ┤                                           ╭──────    │
│      │                                     ╭────╯ FORECAST  │
│  $4B ┤                              ╭─────╯    ·········   │
│      │                        ╭─────╯                       │
│  $3B ┤                 ╭─────╯                             │
│      │           ╭─────╯                                    │
│  $2B ┤     ╭─────╯                                         │
│      │╭────╯                                                │
│  $1B ┤╯                                                      │
│      │                                                       │
│   $0 └────┬────┬────┬────┬────┬────┬────┬────┬────→        │
│          2020 2021 2022 2023 2024 2025 2026 2027           │
│                                                             │
│  Solid = Actual    ····· = Forecast    Band = Confidence   │
└─────────────────────────────────────────────────────────────┘
```

- **Area:** Stacked by category or region
- **Forecast:** Dotted line with confidence interval band
- **Growth Rate:** Annotation showing YoY percentage
- **Comparison:** Optional overlay line for other states

**Where it Lives:** `/market/size` + executive dashboard

**Wow Factor:**
- "Market Moments": Annotated milestones ( legalization dates, regulatory changes)
- Per-capita toggle: Normalize by population for true comparison
- Seasonal overlay: Show recurring patterns year-over-year

**Priority:** P1  
**Complexity:** M  
**Estimated Dev:** 3-4 days

---

### 18. Category Growth S-Curves

**Name:** Category Growth S-Curves  
**Description:** Small multiples showing adoption/growth curves for each product category

**Business Question:** "Which categories are mature vs. emerging? Where should I invest?"

**Data Sources:**
- Historical category mix data
- New product launch tracking
- Price evolution by category

**Library:** D3.js (small multiples with consistent scales)

**Interaction Model:**
- **Hover Chart:** Highlight and show tooltip
- **Sync Scrolling:** All charts scroll together through time
- **Normalize Toggle:** Absolute values vs. percentage of total
- **Compare Mode:** Overlay two categories in larger view

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  CATEGORY LIFECYCLES                              [Norm ▣]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FLOWER          EDIBLES         CONCENTRATES              │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐               │
│  │ ╭────── │     │      ╭──│──╮  │    ╭────│──╮            │
│  │╭╯       │     │     ╭╯  │   ╲ │   ╭╯    │   ╲           │
│  │╯  MATURE│     │  GROWTH│   │   │  ╱      │    ╲  EMERGING│
│  └─────────┘     └─────────┘     └─────────┘               │
│                                                             │
│  VAPE            PRE-ROLL        TOPICALS                  │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐               │
│  │    ╭────│──╮  │ ╭────── │     │    ╭─── │               │
│  │   ╭╯    │   ╲ │╭╯       │     │   ╭╯    │               │
│  │  ╱DECLIN│E   ╲│╯  GROWTH│     │  ╱  EARLY│               │
│  └─────────┘     └─────────┘     └─────────┘               │
│                                                             │
│  Click any chart to enlarge. Double-click to compare.       │
└─────────────────────────────────────────────────────────────┘
```

- **Layout:** 2×3 grid of sparkline-style charts
- **Curves:** Smoothed lines showing volume over time
- **Labels:** Large status label (MATURE, GROWTH, EMERGING, DECLINING)
- **Annotations:** Key events (new regulations, major brand entry)

**Where it Lives:** `/market/categories` + strategic planning section

**Wow Factor:**
- Lifecycle stage detection: Automatic classification with reasoning
- Prediction overlay: Dashed extension showing projected trajectory
- Opportunity score: Numeric rating for investment potential

**Priority:** P1  
**Complexity:** M  
**Estimated Dev:** 4 days

---

### 19. Seasonal Heat Cycle

**Name:** Seasonal Heat Cycle  
**Description:** Radial heatmap showing seasonal patterns in demand/pricing

**Business Question:** "When should I stock up? When do prices dip? What's the seasonal rhythm?"

**Data Sources:**
- Multi-year historical data
- Price and volume by week
- Holiday and event calendar

**Library:** D3.js (polar heatmap with d3-scale-chromatic)

**Interaction Model:**
- **Hover Cell:** Show exact values and year-over-year comparison
- **Year Selection:** Toggle which years to include
- **Metric Toggle:** Price vs. Volume vs. New Product Count
- **Zoom:** Click month to expand week-level detail

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  SEASONAL PATTERNS                                [Vol ▼]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                        N                                    │
│                        │                                    │
│                  ┌─────┼─────┬─────┐                        │
│             W ───┤ JAN │ FEB │ MAR ├─── E                   │
│                  │ ░▓░ │ ▓▓▓ │ ▒▒░ │                        │
│                  ├─────┼─────┼─────┤                        │
│                  │ APR │ MAY │ JUN │                        │
│                  │ ░░░ │ ▓▓▓ │ ▓▓▒ │                        │
│                  ├─────┼─────┼─────┤                        │
│                  │ JUL │ AUG │ SEP │                        │
│                  │ ▒▒▒ │ ▓▓▓ │ ▒▒░ │                        │
│                  ├─────┼─────┼─────┤                        │
│                  │ OCT │ NOV │ DEC │                        │
│                  │ ░░░ │ ▓▓▓ │ ▓▓▓ │                        │
│                  └─────┴─────┴─────┘                        │
│                        │                                    │
│                        S                                    │
│                                                             │
│  ░ = Low    ▒ = Medium    ▓ = High activity                │
│  Inner ring = 2023    Outer ring = 2024                     │
└─────────────────────────────────────────────────────────────┘
```

- **Grid:** 12 months × years (concentric rings)
- **Color Scale:** Sequential gray to copper (subtle, not rainbow)
- **Compass:** Cardinal directions labeled
- **Year Rings:** 2023 (inner), 2024 (middle), 2025 (outer, partial)

**Where it Lives:** `/market/seasonal` + planning calendar integration

**Wow Factor:**
- Event overlay: Icons showing 4/20, Black Friday, etc.
- Weather correlation: Temperature/vacation data overlay
- Predictive highlighting: "Stock up by March 15 for 4/20 demand"

**Priority:** P2  
**Complexity:** S  
**Estimated Dev:** 2-3 days

---

### 20. Economic Indicator Dashboard

**Name:** Economic Indicator Dashboard  
**Description:** Grid of sparkline KPIs showing key market health metrics

**Business Question:** "At a glance: is the market healthy? What are the warning signs?"

**Data Sources:**
- Aggregated price indices
- Product count trends
- New entrant rate
- Exit/closure rate

**Library:** Custom React + D3 sparklines (no heavy viz needed)

**Interaction Model:**
- **Hover Card:** Expand to full chart
- **Click:** Navigate to detailed view
- **Alert Threshold:** Visual indicator when metrics cross bounds
- **Compare:** Toggle between time periods

**Visual Mockup Description:**
```
┌─────────────────────────────────────────────────────────────┐
│  MARKET HEALTH INDICATORS                         [7D ▼]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ AVG PRICE      │  │ SKU COUNT      │  │ NEW ENTRANTS   │ │
│  │                │  │                │  │                │ │
│  │ $42.50   ╱╲    │  │ 68,421   ╲╱╲   │  │    12    ╲     │ │
│  │     +2.3% ╲╱   │  │     +1.2%  ╲╱  │  │    +3    ╲╱    │ │
│  │ ┌──────────┐   │  │ ┌──────────┐   │  │ ┌──────────┐   │ │
│  │ │ ╱╲╱╲╱╲   │   │  │ │╲╱╲╱╲╱╲╱╲  │   │  │ │╲ ╱╲╱     │   │ │
│  │ └──────────┘   │  │ └──────────┘   │  │ └──────────┘   │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
│                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ PRICE VOLATILITY│  │ MARKET CONC.  │  │ AVG MARGIN     │ │
│  │                │  │ (HHI)          │  │ (EST)          │ │
│  │   8.2%   ╲╱    │  │  0.24    ╱     │  │  32%     ╱╲    │ │
│  │    +1.5%  ╲    │  │   -0.02  ╲╱╲   │  │   -2.1%   ╲╱   │ │
│  │ ┌──────────┐   │  │ ┌──────────┐   │  │ ┌──────────┐   │ │
│  │ │╲╱╲╱╲╱╲╱╲  │   │  │ │  ╱╲╱╲    │   │  │ │╲╱╲╱╲╱╲╱╲  │   │ │
│  │ └──────────┘   │  │ └──────────┘   │  │ └──────────┘   │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
│                                                             │
│  ◄── Green (healthy)    Yellow (warning)    Red (critical)  │
└─────────────────────────────────────────────────────────────┘
```

- **Cards:** 6 metric cards in 2×3 grid
- **Sparklines:** 30-day trend in card footer
- **Indicators:** 
  - Green dot: Healthy trend
  - Yellow triangle: Warning threshold crossed
  - Red diamond: Critical alert
- **Values:** Large type for current value, smaller for change

**Where it Lives:** Morning Brief hero section + `/market/health` detail page

**Wow Factor:**
- Index composition: Click any metric to see what drives it
- Historical context: "This volatility is in the 90th percentile"
- Correlation matrix: Show which metrics move together

**Priority:** P0  
**Complexity:** S  
**Estimated Dev:** 2 days

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4) — P0 Items

| # | Visualization | Complexity | Owner | Dependencies |
|---|---------------|------------|-------|--------------|
| 1 | Price Positioning Matrix | M | Frontend | Price aggregation API |
| 2 | Price Volatility Ribbon | M | Frontend | Time-series API |
| 3 | Competitive Proximity Radar | M | Frontend | Geocoding service |
| 4 | Brand Market Share Treemap | M | Frontend | Brand aggregation API |
| 5 | Category Mix Sunburst | M | Frontend | Category taxonomy |
| 6 | Operator Comparison Matrix | M | Frontend | Operator profiles API |
| 7 | Threat Alert Network | L | Frontend | Threat scoring engine |
| 8 | CCC Action Timeline | M | Frontend | Regulatory data feed |
| 9 | Economic Indicator Dashboard | S | Frontend | KPI aggregation |

**Phase 1 Deliverable:** Core dashboard with 9 production visualizations

### Phase 2: Expansion (Weeks 5-8) — P1 Items

| # | Visualization | Complexity | Owner | Dependencies |
|---|---------------|------------|-------|--------------|
| 10 | Price Change Cascade | L | Frontend | Price change events |
| 11 | Real-Time Price Ticker | S | Frontend | WebSocket feed |
| 12 | 3D Market Terrain Map | XL | Frontend | 3D team + GIS data |
| 13 | Delivery Zone Voronoi | M | Frontend | Zone polygon data |
| 14 | Strain Popularity Stream | M | Frontend | Strain parsing engine |
| 15 | Market Share Flow | L | Frontend | Share estimation model |
| 16 | Price War Heatmap | S | Frontend | Price change frequency |
| 17 | License Pipeline Funnel | M | Frontend | Application status API |
| 18 | Total Market Size Chart | M | Frontend | Market estimation model |
| 19 | Category Growth S-Curves | M | Frontend | Historical trend data |

**Phase 2 Deliverable:** Full-featured platform with 19 visualizations

### Phase 3: Polish (Weeks 9-10) — P2 Items

| # | Visualization | Complexity | Owner | Dependencies |
|---|---------------|------------|-------|--------------|
| 20 | Seasonal Heat Cycle | S | Frontend | Multi-year data warehouse |

**Phase 3 Deliverable:** Advanced analytics and predictive features

---

## Technical Stack Summary

### Required Libraries

```typescript
// Core visualization
import * as d3 from 'd3';
import { scaleLinear, scaleTime, scaleOrdinal } from 'd3-scale';
import { line, area, curveBasis } from 'd3-shape';
import { hierarchy, treemap, partition } from 'd3-hierarchy';
import { forceSimulation, forceManyBody, forceLink } from 'd3-force';

// 3D (select visualizations only)
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';

// Animation
import { motion, AnimatePresence } from 'framer-motion';

// Performance
import { useVirtualizer } from '@tanstack/react-virtual';
import { LRUCache } from 'lru-cache';
```

### Component Architecture

```
src/components/visualizations/
├── common/
│   ├── ChartContainer.tsx      # Shared wrapper with title, controls, loading
│   ├── Tooltip.tsx             # Universal tooltip component
│   ├── Legend.tsx              # Configurable legend
│   ├── Brush.tsx               # Range selection component
│   └── Axis.tsx                # Shared axis rendering
├── price/
│   ├── PricePositioningMatrix.tsx
│   ├── PriceVolatilityRibbon.tsx
│   ├── PriceChangeCascade.tsx
│   └── PriceTickerWall.tsx
├── geography/
│   ├── MarketTerrainMap.tsx    # Three.js
│   ├── DeliveryZoneVoronoi.tsx
│   └── CompetitiveProximityRadar.tsx
├── product/
│   ├── BrandTreemap.tsx
│   ├── CategorySunburst.tsx
│   └── StrainStreamgraph.tsx
├── competitive/
│   ├── OperatorComparison.tsx
│   ├── MarketShareFlow.tsx
│   └── PriceWarHeatmap.tsx
├── regulatory/
│   ├── CCCTimeline.tsx
│   ├── LicensePipeline.tsx
│   └── ThreatNetwork.tsx
└── macro/
    ├── MarketSizeChart.tsx
    ├── CategoryGrowthCurves.tsx
    ├── SeasonalHeatCycle.tsx
    └── EconomicIndicators.tsx
```

### Shared Hooks

```typescript
// src/hooks/visualizations/
export const useChartData = (queryKey, fetcher, options) => {
  // React Query with caching
};

export const useResizeObserver = (ref) => {
  // Responsive chart sizing
};

export const useTooltip = () => {
  // Unified tooltip state management
};

export const useBrush = (domain, onChange) => {
  // Brush selection state
};
```

---

## Quality Checklist

Before any visualization ships:

- [ ] **Performance**: Renders in < 100ms for target data size
- [ ] **Accessibility**: Keyboard navigable, screen reader labels, reduced motion support
- [ ] **Mobile**: Usable at 375px width (or has dedicated mobile view)
- [ ] **Data**: Handles empty states, loading states, and error states gracefully
- [ ] **Interaction**: All hover/click states have visual feedback
- [ ] **Export**: Can export as PNG (and SVG where applicable)
- [ ] **Documentation**: JSDoc comments for all props and public methods
- [ ] **Testing**: Unit tests for data transformation, visual regression for rendering

---

## Appendix: Color Reference

| Usage | Hex | Token |
|-------|-----|-------|
| Background (primary) | #000000 | `bg-glass-black` |
| Background (surface) | #0A0A0A | `bg-glass-surface` |
| Background (elevated) | #111111 | `bg-glass-elevated` |
| Border | #1A1A1A | `border-glass-border` |
| Text (primary) | #FFFFFF | `text-glass-text` |
| Text (muted) | #999999 | `text-glass-muted` |
| Text (subtle) | #666666 | `text-glass-subtle` |
| Accent | #C45A3C | `text-glass-accent` |
| Accent (dim) | #9E4A30 | `text-glass-accent-dim` |
| Success | #22C55E | `text-emerald-400` |
| Danger | #EF4444 | `text-red-400` |
| Warning | #F59E0B | `text-amber-400` |

---

## Appendix: Icon Reference

| Meaning | Icon | Library |
|---------|------|---------|
| Price increase | TrendingUp | lucide-react |
| Price decrease | TrendingDown | lucide-react |
| Threat/Alert | ShieldAlert | lucide-react |
| New license | Flag | lucide-react |
| Violation | AlertTriangle | lucide-react |
| Your position | Target | lucide-react |
| Competitor | Building | lucide-react |
| Time/History | Clock | lucide-react |
| Filter | Filter | lucide-react |
| Download | Download | lucide-react |
| Expand | Maximize2 | lucide-react |
| Play animation | Play | lucide-react |
| Pause animation | Pause | lucide-react |

---

*This visualization plan is a living document. As data availability and business priorities evolve, visualizations may be reprioritized or redesigned. All designs should be reviewed against the GLASS design system before implementation.*

**Document Owner:** GLASS Product + Design Team  
**Last Updated:** February 2026  
**Next Review:** March 2026
