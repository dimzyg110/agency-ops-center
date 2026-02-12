# GLASS Ecosystem — Product Specifications

**Virtual Budtender + Cue: Complete Technical & Commercial Specs**

Version 1.0 | February 2026
Status: PROPOSED — awaiting review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Virtual Budtender — Complete Product Spec](#2-virtual-budtender)
3. [Cue — Complete Product Spec](#3-cue)
4. [Data Flow Architecture](#4-data-flow-architecture)
5. [API Endpoints](#5-api-endpoints)
6. [MVP Build Plan (2-Week Sprints)](#6-mvp-build-plan)
7. [Revenue Projections](#7-revenue-projections)
8. [Competitive Analysis](#8-competitive-analysis)
9. [Go-to-Market Strategy](#9-go-to-market-strategy)

---

## 1. Executive Summary

The GLASS ecosystem has three product layers:

| Layer | Product | Price | Purpose |
|-------|---------|-------|---------|
| Intelligence | GLASS Dashboard | Free | Attract operators, build data moat |
| Engagement | Virtual Budtender | Free → $99–$299/mo | Embed GLASS into operator storefronts, capture demand signals |
| Commerce | Cue | $199–$999/mo | Turn GLASS intelligence into automated revenue actions |

**Why these two products matter:**
- GLASS alone is a dashboard operators check. Budtender makes GLASS a dependency in their customer-facing workflow. Cue makes GLASS the engine behind their pricing and inventory decisions.
- Combined, they create a closed data loop: consumer preferences (Budtender) feed demand signals (Cue) which optimize inventory (operators) which improves recommendations (Budtender).

**What we have today:**
- 492+ MA operators tracked
- 20,000+ products with names, brands, strains, THC%, categories
- 21,000+ price observations updated daily
- Competitor proximity data + CCC regulatory intelligence
- Landing pages for both products (no functionality)

**What this spec delivers:**
- How each product works end-to-end (user → API → data → output)
- Exact API contracts developers can build against
- 2-week MVP scope for each product
- Revenue models tied to GLASS data we already have

---

## 2. Virtual Budtender — Complete Product Spec

### 2.1 Product Definition

An AI-powered product recommendation engine that dispensaries embed on their website or deploy on an in-store tablet. It answers customer questions in natural language and recommends products *from that dispensary's actual menu* using GLASS market data.

**One-liner:** "An AI budtender for your website that knows your real menu."

### 2.2 Why It Works

Most dispensary websites are a Dutchie iframe or a static menu page. Customers can't ask questions. They scroll until they find something or leave. The Virtual Budtender turns that dead-end into a guided sale.

The secret: we already have the data. GLASS scrapes 20,000+ products daily. We know what every dispensary carries, what it costs, and how it compares to competitors. The Budtender just puts a conversational interface on top of that data, scoped to one operator's menu.

### 2.3 User Flows

#### Flow 1: Customer on Dispensary Website

```
1. Customer visits dispensary website (e.g., pureoasis.com)
2. Floating widget appears (bottom-right): "Need help choosing? Ask me anything."
3. Customer types: "I want something for relaxation, not too strong"
4. Budtender AI:
   a. Parses intent: effect=relaxation, potency=low-medium
   b. Queries GLASS products WHERE operator_id = {this_dispensary}
   c. Filters: category IN (flower, edible, vape), thc_percent < 20
   d. Ranks by: relevance to "relaxation" + in_stock + price competitiveness
   e. Returns 3 recommendations with explanations
5. Customer sees:
   ┌──────────────────────────────────────────────────┐
   │ 🌿 Based on your goals, I'd recommend:          │
   │                                                  │
   │ 1. CBD:THC Ratio Gummies 1:1 — $31              │
   │    Good Chemistry · 10mg/gummy · THC:CBD balanced│
   │    "Great for relaxation without heavy sedation" │
   │    [Add to Cart] [More Info]                     │
   │                                                  │
   │ 2. Sleep Gummies THC:CBN — $34                   │
   │    The Botanist · 10mg/gummy · CBN for calm      │
   │    "CBN terpene profile promotes gentle wind-down"│
   │    [Add to Cart] [More Info]                     │
   │                                                  │
   │ 3. Blue Dream Flower 3.5g — $42                  │
   │    Good Chemistry · 24% THC · Sativa-leaning     │
   │    "Lighter sativa if you prefer flower"          │
   │    [Add to Cart] [More Info]                     │
   │                                                  │
   │ 💬 Want to narrow by price or product type?       │
   └──────────────────────────────────────────────────┘
6. Customer can:
   - Click a product → goes to that product's page on the dispensary site
   - Ask a follow-up: "Something cheaper?" or "Do you have vapes?"
   - Filter: price range slider, category chips, THC level
7. Every interaction is tracked (anonymized) and feeds GLASS demand signals
```

#### Flow 2: In-Store Tablet Mode

```
1. Dispensary places a tablet at the counter or waiting area
2. Kiosk-mode UI (no widget — full-screen experience)
3. Large touch-friendly cards, voice input option
4. Same recommendation engine, different UI surface
5. Staff can also use it as a recommendation assist tool
6. Tracks: what's recommended, what customer selects, time-to-decision
```

#### Flow 3: Operator Setup

```
1. Operator signs up at glass.roviq.com/budtender
2. Enters: dispensary name, website URL, goals (conversion / AOV / education)
3. System auto-detects their operator_id from GLASS database
   - If found: "We already track 247 products on your menu. Ready to go."
   - If not found: "We'll add your menu within 24 hours." (triggers scrape priority)
4. Operator gets:
   - Embed code: <script src="https://budtender.glass.roviq.com/embed.js" data-operator="abc123"></script>
   - Configuration panel:
     - Theme: light/dark/auto
     - Position: bottom-right / bottom-left / inline
     - Branding: custom logo, accent color
     - Tone: friendly / professional / expert
     - Category weighting: promote certain categories
     - Excluded products: hide specific SKUs
   - Preview panel: test the widget before going live
5. Operator pastes script tag into their website header
6. Widget goes live immediately — pulling from GLASS data
```

### 2.4 Recommendation Engine Design

```
Input: {
  operator_id: uuid,        // Which dispensary's menu to use
  query: string,            // "something for relaxation, not too strong"
  filters?: {
    category?: string[],    // ["flower", "edible"]
    price_min?: number,
    price_max?: number,
    thc_max?: number,
    thc_min?: number,
    effects?: string[],     // ["relaxation", "sleep", "energy"]
    strain_type?: string    // "indica", "sativa", "hybrid"
  },
  session_id: string,       // Track conversation context
  previous_recommendations?: uuid[]  // Don't repeat
}

Processing Pipeline:
┌─────────────────────────────────────────────────────────┐
│ 1. INTENT PARSING (LLM)                                │
│    Input: raw customer query                            │
│    Output: structured intent {effects, potency,         │
│            category_preference, price_sensitivity,      │
│            experience_level}                            │
│    Model: GPT-4o-mini (fast, cheap, good at NLU)       │
│    Cost: ~$0.0003 per query                             │
│    Latency: 200-400ms                                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 2. PRODUCT RETRIEVAL (Database)                         │
│    Query GLASS: SELECT products + latest prices         │
│    WHERE operator_id = {this_dispensary}                 │
│    AND availability IN ('in_stock', 'low_stock')        │
│    AND category matches intent                          │
│    Apply explicit filters from user                     │
│    Result: 10-50 candidate products                     │
│    Latency: 10-30ms (indexed query)                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 3. SCORING & RANKING (Algorithm — no LLM)               │
│                                                         │
│    Score = Σ(weight × factor)                           │
│                                                         │
│    Factors:                                             │
│    - Effect match (0-1): parsed intent vs product       │
│      attributes (strain_type, THC%, CBD%, category)     │
│    - Potency fit (0-1): THC% within desired range       │
│    - Price competitiveness (0-1): vs local market avg   │
│    - Availability (0/0.5/1): in_stock > low_stock       │
│    - Popularity signal (0-1): how often recommended     │
│      + clicked by similar queries (learned over time)   │
│    - Operator promotion weight (0-2): boosted SKUs      │
│    - Freshness penalty: lower score if data is stale    │
│                                                         │
│    Weights (tunable per operator):                      │
│    effect_match: 0.35                                   │
│    potency_fit: 0.20                                    │
│    price_competitiveness: 0.15                          │
│    availability: 0.10                                   │
│    popularity: 0.10                                     │
│    operator_boost: 0.10                                 │
│                                                         │
│    Output: top 3 products ranked by composite score     │
│    Latency: <5ms (in-memory scoring)                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 4. RESPONSE GENERATION (LLM)                            │
│    Input: top 3 products + customer intent + context    │
│    Output: conversational recommendation with           │
│            product-specific explanations                 │
│    Model: GPT-4o-mini                                   │
│    System prompt: tone + operator branding + cannabis    │
│                   education guidelines                   │
│    Cost: ~$0.0005 per response                          │
│    Latency: 300-600ms                                   │
│                                                         │
│    Total pipeline latency: ~600-1100ms                  │
│    Total LLM cost per recommendation: ~$0.001           │
│    At 100 recs/day: ~$3/month in API costs              │
└─────────────────────────────────────────────────────────┘
```

### 2.5 Effect-to-Product Mapping

Since we don't have explicit "effect" labels on products (GLASS scrapes name, brand, strain, THC%, category), we need a mapping layer:

```
EFFECT MAPPING TABLE (curated, updated quarterly):

| Customer Says       | Maps To                                           |
|---------------------|---------------------------------------------------|
| "relaxation"        | indica strains, CBD products, low-THC edibles     |
| "sleep"             | indica, CBN products, heavy THC edibles           |
| "energy"            | sativa strains, low-dose edibles                  |
| "pain relief"       | high-THC indica, topicals, tinctures, 1:1 ratios  |
| "creativity"        | sativa, hybrid, moderate THC                      |
| "social / party"    | sativa, low-dose edibles, vape pens               |
| "anxiety relief"    | CBD-dominant, 1:1 ratios, low-THC flower          |
| "first time"        | low-THC (<15%), edibles (2.5-5mg), balanced ratio |
| "strong / potent"   | THC >25%, concentrates, high-dose edibles         |
| "microdose"         | edibles <5mg, low-THC tinctures                   |

Implementation: static lookup table + LLM intent parser as fallback for
queries that don't match known patterns.
```

### 2.6 Embedding Architecture

```
Option A: Script Tag (recommended for MVP)
─────────────────────────────────────────
<script 
  src="https://budtender.glass.roviq.com/embed.js" 
  data-operator="op_abc123"
  data-theme="light"
  data-position="bottom-right"
  data-accent="#D94F3D"
></script>

- embed.js is a tiny loader (~5KB gzipped)
- Creates an iframe pointing to budtender.glass.roviq.com/widget/{operator_id}
- iframe isolates CSS/JS from host site
- Communicates via postMessage for:
  - Product click → redirect to product URL on host site
  - Theme sync → match host site dark/light mode
  - Resize events → responsive widget height
- No cookies set on host domain (3P cookie safe)

Option B: Web Component (future — for custom integrations)
──────────────────────────────────────────────────────────
<glass-budtender 
  operator="op_abc123" 
  theme="dark"
  position="inline"
></glass-budtender>

- Shadow DOM encapsulation
- Deeper integration with host site styling
- Can be placed inline (not just floating)
- Requires more setup, better for enterprise tier

Option C: React Component (future — for Dutchie-embedded sites)
────────────────────────────────────────────────────────────────
import { VirtualBudtender } from '@glass/budtender-react';

<VirtualBudtender 
  operatorId="op_abc123" 
  onProductClick={(product) => addToCart(product.sku)}
/>

- Deep POS integration
- Cart manipulation
- Enterprise only
```

### 2.7 Analytics Dashboard (for operators)

Operators see these metrics inside their GLASS dashboard under "Budtender" tab:

```
┌─────────────────────────────────────────────────────────┐
│  VIRTUAL BUDTENDER — ANALYTICS                          │
│                                                         │
│  This Week                    vs Last Week              │
│  ─────────                    ──────────                │
│  Sessions: 342                ▲ +18%                    │
│  Queries: 891                 ▲ +24%                    │
│  Recommendations served: 2,673 ▲ +22%                  │
│  Product clicks: 487          ▲ +31%                    │
│  Click-through rate: 18.2%    ▲ +1.4pp                 │
│  Add-to-cart (if connected): 89  ▲ +42%                │
│                                                         │
│  ─── TOP QUERIES ───────────────────────────────────    │
│  1. "something for sleep"           — 67 queries        │
│  2. "edibles under $30"             — 52 queries        │
│  3. "strongest flower you have"     — 41 queries        │
│  4. "good for anxiety"              — 38 queries        │
│  5. "first time recommendations"    — 29 queries        │
│                                                         │
│  ─── TOP RECOMMENDED (clicked) ─────────────────────    │
│  1. Sleep Gummies THC:CBN           — 67 clicks         │
│  2. Blue Dream Flower 3.5g          — 54 clicks         │
│  3. CBD:THC Ratio Gummies 1:1       — 48 clicks         │
│                                                         │
│  ─── DEMAND GAP (queries with no good match) ────────   │
│  ⚠ "CBD flower" — 23 queries, 0 products in stock      │
│  ⚠ "beverages" — 18 queries, only 1 product            │
│  ⚠ "microdose edibles 2.5mg" — 15 queries, 0 matches  │
│                                                         │
│  ℹ Demand gaps feed into Cue inventory recommendations  │
└─────────────────────────────────────────────────────────┘
```

### 2.8 Revenue Model

| Tier | Price | Includes | Target |
|------|-------|----------|--------|
| **Free** | $0/mo | 100 recommendations/month, basic widget, GLASS branding | Lead magnet — get operators embedding GLASS on their site |
| **Pro** | $99/mo | Unlimited recommendations, analytics dashboard, custom branding (remove GLASS logo), priority data refresh | Operators who see value from free tier and want more |
| **Enterprise** | $299/mo | Everything in Pro + POS integration, A/B testing, multi-location, dedicated support, custom training data | Multi-store operators, high-volume dispensaries |

**Why free tier works:** The free tier isn't charity. Every recommendation generates a demand signal. Every customer query tells us what people want to buy. That data is worth more than $99/mo — it feeds Cue's demand forecasting, newsletter content, and GLASS market intelligence. The operator gets a useful tool. We get a data exhaust pipe bolted onto their storefront.

**LLM cost at scale:**
- 100 recs/month (free tier): ~$0.10/month in API costs
- 1,000 recs/month (typical Pro): ~$1.00/month
- 10,000 recs/month (enterprise): ~$10.00/month
- Margin on Pro tier: >98%

### 2.9 Data Events Tracked

Every interaction creates structured events stored in GLASS:

```typescript
// Event taxonomy
interface BudtenderEvent {
  event_type: 
    | 'widget_loaded'          // Widget appeared on page
    | 'session_started'        // Customer opened widget
    | 'query_submitted'        // Customer asked a question
    | 'recommendation_served'  // AI returned results
    | 'product_clicked'        // Customer clicked a recommendation
    | 'filter_applied'         // Customer used a filter
    | 'follow_up_query'        // Customer asked a follow-up
    | 'session_ended'          // Widget closed / navigated away
    | 'add_to_cart'            // Product added to cart (if POS connected)
    | 'purchase_completed';    // Purchase confirmed (if POS connected)
  
  operator_id: string;
  session_id: string;          // Anonymous session (no PII)
  timestamp: string;
  
  // Query-specific
  query_text?: string;         // Raw customer input
  parsed_intent?: {
    effects: string[];
    potency: 'low' | 'medium' | 'high';
    categories: string[];
    price_sensitivity: 'low' | 'medium' | 'high';
  };
  
  // Recommendation-specific
  products_recommended?: string[];  // Product IDs
  products_clicked?: string[];
  position_clicked?: number;        // 1st, 2nd, or 3rd recommendation
  
  // Metadata
  source: 'widget' | 'tablet' | 'api';
  page_url?: string;               // Which page the widget was on
  device_type: 'mobile' | 'desktop' | 'tablet';
}
```

### 2.10 Database Additions for Budtender

```sql
-- New tables for Virtual Budtender

CREATE TABLE budtender_configs (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id     uuid NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  api_key         varchar(64) NOT NULL UNIQUE,       -- op_abc123...
  theme           varchar(10) DEFAULT 'light',        -- light/dark/auto
  position        varchar(20) DEFAULT 'bottom-right',
  accent_color    varchar(7) DEFAULT '#D94F3D',
  tone            varchar(20) DEFAULT 'friendly',     -- friendly/professional/expert
  logo_url        text,
  branding_visible boolean DEFAULT true,              -- show GLASS branding (free tier)
  category_weights jsonb DEFAULT '{}',                -- {"flower": 1.5, "edible": 1.0}
  excluded_skus   text[] DEFAULT '{}',
  tier            varchar(20) DEFAULT 'free',         -- free/pro/enterprise
  monthly_recs_used integer DEFAULT 0,
  monthly_recs_limit integer DEFAULT 100,
  is_active       boolean DEFAULT true,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE budtender_sessions (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id     uuid NOT NULL REFERENCES operators(id),
  session_token   varchar(64) NOT NULL,
  device_type     varchar(10),                        -- mobile/desktop/tablet
  source          varchar(10) DEFAULT 'widget',       -- widget/tablet/api
  page_url        text,
  queries_count   integer DEFAULT 0,
  clicks_count    integer DEFAULT 0,
  started_at      timestamptz NOT NULL DEFAULT now(),
  ended_at        timestamptz
);

CREATE INDEX idx_bt_sessions_operator ON budtender_sessions(operator_id);
CREATE INDEX idx_bt_sessions_started ON budtender_sessions(started_at);

CREATE TABLE budtender_events (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      uuid NOT NULL REFERENCES budtender_sessions(id),
  operator_id     uuid NOT NULL REFERENCES operators(id),
  event_type      varchar(30) NOT NULL,
  query_text      text,
  parsed_intent   jsonb,
  products_recommended uuid[],
  products_clicked     uuid[],
  position_clicked     smallint,
  filters_applied      jsonb,
  metadata             jsonb,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_bt_events_operator ON budtender_events(operator_id);
CREATE INDEX idx_bt_events_type ON budtender_events(event_type);
CREATE INDEX idx_bt_events_created ON budtender_events(created_at);
CREATE INDEX idx_bt_events_session ON budtender_events(session_id);

-- Aggregated demand signals (computed nightly from events)
CREATE TABLE budtender_demand_signals (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date            date NOT NULL,
  operator_id     uuid REFERENCES operators(id),     -- NULL = market-wide
  effect          varchar(50) NOT NULL,               -- "relaxation", "sleep", etc.
  query_count     integer NOT NULL DEFAULT 0,
  click_count     integer NOT NULL DEFAULT 0,
  conversion_count integer NOT NULL DEFAULT 0,        -- add-to-cart
  avg_price_clicked numeric(10,2),
  top_categories  text[],
  created_at      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT bt_demand_unique UNIQUE (date, operator_id, effect)
);

CREATE INDEX idx_bt_demand_date ON budtender_demand_signals(date);
CREATE INDEX idx_bt_demand_effect ON budtender_demand_signals(effect);
```

---

## 3. Cue — Complete Product Spec

### 3.1 Product Definition

Cue is an AI commerce platform that turns GLASS intelligence into automated actions: dynamic pricing, demand forecasting, inventory optimization, and brand incentives. It's the paid layer that sits on top of GLASS data and tells operators exactly what to do — then does it.

**One-liner:** "Your AI pricing and inventory strategist, powered by every menu in Massachusetts."

### 3.2 Why Cue Exists

GLASS shows operators what's happening in the market. Cue tells them what to do about it. The gap between "knowing" and "acting" is where money lives:

- Operator sees competitor dropped flower to $35. **Now what?** Cue says: "Match at $33 — your margin stays above 42%, and you'll gain 12 units/week based on local elasticity."
- Operator has too much concentrate. **Now what?** Cue says: "Run a bundle (concentrate + vape) at 15% off. Similar bundles in your area lifted basket size 6.8%."
- Brand wants shelf space. **Now what?** Cue says: "Brand X will fund $2/unit for 30 days on their new vape cart. Your margin goes from 48% to 56%."

### 3.3 Module Architecture

Cue has four modules. Each can be adopted independently, but they compound when used together.

#### Module 1: Dynamic Pricing ($199/mo standalone)

**What it does:** Monitors competitor prices via GLASS data and recommends price adjustments in real-time.

```
Input: 
  - Operator's current prices (from GLASS scrape of their menu)
  - Competitor prices (from GLASS scrape of nearby operators)
  - Operator's margin rules (min/max price, target margin %)
  - Market velocity signals (which products are moving?)

Processing:
  1. Every price observation triggers a comparison:
     "Your Blue Dream 3.5g is at $46. Median in 5-mile radius: $41.50."
  2. Scoring engine evaluates:
     - Gap to market (how far above/below?)
     - Margin impact (does adjusting still hit target?)
     - Velocity signal (are sales trending up or down for this product?)
     - Competitor count (how many stores carry this product nearby?)
  3. Generates recommendation:
     - Recommended price: $42
     - Confidence: 0.90
     - Expected impact: +12.5 units/week, -1.8% margin
     - Rationale: "Competitor median moved to $41.50..."

Output:
  - Dashboard card with "Apply / Edit / Dismiss" buttons
  - Email/SMS alert for high-confidence recommendations
  - Weekly pricing report (PDF)
  - If POS connected: auto-apply approved changes
```

**Alert Types:**
```
┌──────────────────────────────────────────────────────────┐
│ 🔴 CRITICAL: Competitor Undercut                         │
│ "NETA Brookline just dropped Wedding Cake 3.5g to $38.  │
│  You're at $48. Cue recommends $41 to stay competitive.  │
│  Margin impact: 52% → 45% (above your 42% floor)."      │
│  [Apply $41] [Edit Price] [Dismiss]                      │
├──────────────────────────────────────────────────────────┤
│ 🟡 WARNING: Category Drift                               │
│ "Your vape cart pricing is 14% above market median.      │
│  3 competitors dropped vape prices this week.             │
│  Cue suggests reviewing 4 SKUs."                         │
│  [Review SKUs →]                                         │
├──────────────────────────────────────────────────────────┤
│ 🟢 OPPORTUNITY: Upward Pricing                           │
│ "Your Sleep Gummies are $31. Market median is $37.       │
│  You have room to increase to $35 with minimal           │
│  volume impact. Expected margin lift: +$420/month."      │
│  [Apply $35] [Edit Price] [Dismiss]                      │
└──────────────────────────────────────────────────────────┘
```

#### Module 2: Demand Forecasting ($499/mo bundle)

**What it does:** Predicts what products will sell this week based on GLASS market trends, Budtender demand signals, seasonality, and local patterns.

```
Data Sources:
  - GLASS price observations (21K+/day across MA)
  - Budtender query patterns ("sleep" queries up 40% this week)
  - CCC plant activity data (delivery vs storefront trends)
  - Seasonal patterns (learned from price history)
  - Local events / weather (future integration)

Output:
  - Category demand forecast: "Edible demand is trending +18% this week"
  - Product-level predictions: "Sleep gummies will outsell energy gummies 3:1"
  - Reorder suggestions: "Order 2x more concentrate; supply disruption lifting"

Key Insight:
  Virtual Budtender demand signals are the unique data asset here.
  No competitor has a real-time feed of "what customers are asking for"
  at the product/effect level, aggregated across multiple dispensaries.
```

#### Module 3: Inventory Optimization ($499/mo bundle)

**What it does:** Analyzes what's on the shelf vs. what the market wants, and recommends adjustments.

```
Signals:
  - Product velocity: How fast is each SKU selling? (from scrape frequency changes)
  - Market demand: What are Budtender customers asking for?
  - Competitive gaps: What do nearby competitors NOT carry?
  - Margin profile: Which categories generate the best margin?

Output:
  ┌──────────────────────────────────────────────────────┐
  │ INVENTORY HEALTH — This Week                         │
  │                                                      │
  │ ⚠️ OVERSTOCKED                                       │
  │ • Concentrates: 34 SKUs, low velocity on 12          │
  │   → Suggest: Bundle with vapes at 15% off            │
  │                                                      │
  │ 🔴 UNDERSTOCKED                                      │
  │ • Edibles (sleep/CBD): 3 SKUs, high Budtender demand │
  │   → "Sleep" queries up 40%, only 1 matching product  │
  │   → Suggest: Add 2-3 CBD:THC ratio products          │
  │                                                      │
  │ ✅ BALANCED                                           │
  │ • Flower: 14 SKUs, healthy mix of price points       │
  │ • Vapes: 8 SKUs, good velocity                       │
  │                                                      │
  │ 💡 MARKET GAP OPPORTUNITY                             │
  │ • "Beverages" — 18 Budtender queries this week,      │
  │   you carry 0 products. Nearest competitor has 4.    │
  └──────────────────────────────────────────────────────┘
```

#### Module 4: Brand Incentives (Enterprise — $999/mo)

**What it does:** Creates a marketplace where brands pay operators to feature their products. Cue facilitates the deal, tracks performance, and handles payouts.

```
How It Works:
  1. Brand (e.g., Fernway) wants to increase presence in Boston-area stores
  2. Brand creates a "Spiff" in Cue: "$2/unit bonus on Fernway 1g Vape Cart"
  3. Cue matches the spiff to operators who:
     - Carry Fernway products
     - Are in the target geography
     - Have high foot traffic (based on GLASS data)
  4. Operator sees in Cue dashboard:
     "Fernway is offering $2/unit on 1g Vape Carts this month.
      Your projected volume: 45 units. Extra revenue: $90."
     [Accept Incentive] [Pass]
  5. Cue tracks sell-through against the spiff
  6. Brand pays operator at end of period

Revenue Model for GLASS:
  - Brands pay GLASS 15% platform fee on all spiff payouts
  - If brand pays $2/unit and operator sells 100 → $200 to operator, $30 to GLASS
```

### 3.4 Cue Dashboard UX

```
Cue is NOT a separate app. It's a section within the GLASS dashboard.

Navigation:
  GLASS Dashboard
  ├── Morning Brief
  ├── Price Wire
  ├── Threat Radar
  ├── Competitors
  ├── Geography
  ├── Recommendations      ← existing (becomes Cue's output surface)
  ├── Alerts               ← existing (Cue adds pricing alerts here)
  │
  ├── 🟠 CUE              ← new section (badge: "Pro" or "Early Access")
  │   ├── Dynamic Pricing   ← competitor-responsive price recommendations
  │   ├── Demand Forecast   ← category/product demand predictions
  │   ├── Inventory Health  ← over/under stock analysis
  │   └── Brand Deals       ← active incentives (enterprise only)
  │
  └── Tools
      ├── Virtual Budtender
      └── Delivery (waitlist)
```

### 3.5 Revenue Model

| Tier | Price | Modules | Target |
|------|-------|---------|--------|
| **Starter** | $199/mo | Dynamic Pricing only | Operators who want competitive pricing alerts |
| **Professional** | $499/mo | Dynamic Pricing + Demand Forecasting + Inventory Optimization | Operators who want full optimization stack |
| **Enterprise** | $999/mo | All modules + Brand Incentives + API access + multi-location + dedicated strategist | Multi-store operators and chains |

**Annual discount:** 20% off (2 months free)

**Brand-side pricing (Incentives module):**
- Self-serve: 15% platform fee on payouts
- Managed campaigns: $500/mo base + 15% fee
- Enterprise brand deals: custom pricing

### 3.6 MVP Scope: Dynamic Pricing Only

For the first release, Cue = Dynamic Pricing. The other modules layer on top over time.

**MVP is just an alert + recommendation layer on top of existing GLASS data.**

What we already have:
- `recommendations` table with price recommendations
- `alerts` table with pricing alerts
- `margin_rules` table with operator-specific floors/ceilings
- Competitor price data refreshed daily
- Proximity calculations for nearby operators

What we need to build:
1. **Pricing comparison engine** — automated job that compares operator's prices to nearby competitors and generates recommendations
2. **Recommendation delivery** — email/SMS alerts when high-confidence recommendations are generated
3. **Apply/Dismiss flow** — operators can approve recommendations (logged, not auto-applied to POS in MVP)
4. **Weekly pricing report** — automated PDF/email summary of price position vs market

### 3.7 Database Additions for Cue

```sql
-- Cue subscriptions
CREATE TABLE cue_subscriptions (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id     uuid NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
  tier            varchar(20) NOT NULL DEFAULT 'starter', -- starter/professional/enterprise
  modules         text[] NOT NULL DEFAULT '{dynamic_pricing}',
  status          varchar(20) NOT NULL DEFAULT 'active',  -- active/paused/cancelled/trial
  trial_ends_at   timestamptz,
  billing_cycle   varchar(10) DEFAULT 'monthly',          -- monthly/annual
  monthly_price   numeric(10,2) NOT NULL,
  stripe_subscription_id varchar(255),
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

-- Cue pricing snapshots (daily market position)
CREATE TABLE cue_pricing_snapshots (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id     uuid NOT NULL REFERENCES operators(id),
  date            date NOT NULL,
  category        varchar(50) NOT NULL,
  operator_avg_price    numeric(10,2) NOT NULL,
  market_median_price   numeric(10,2) NOT NULL,
  market_avg_price      numeric(10,2) NOT NULL,
  percentile_rank       numeric(5,2),           -- 0-100: where operator sits
  competitor_count      integer,
  radius_miles          numeric(5,2),
  recommendations_generated integer DEFAULT 0,
  recommendations_applied   integer DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT cue_snapshot_unique UNIQUE (operator_id, date, category)
);

CREATE INDEX idx_cue_snapshots_operator ON cue_pricing_snapshots(operator_id);
CREATE INDEX idx_cue_snapshots_date ON cue_pricing_snapshots(date);

-- Brand incentives (enterprise module)
CREATE TABLE cue_brand_incentives (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_name      varchar(255) NOT NULL,
  brand_contact_email varchar(255),
  product_id      uuid REFERENCES products(id),
  category        varchar(50),
  incentive_type  varchar(20) NOT NULL,          -- per_unit / flat_fee / percentage
  incentive_amount numeric(10,2) NOT NULL,
  target_geography jsonb,                         -- {"cities": ["Boston"], "radius_miles": 10}
  start_date      date NOT NULL,
  end_date        date NOT NULL,
  max_budget      numeric(12,2),
  spent_to_date   numeric(12,2) DEFAULT 0,
  status          varchar(20) DEFAULT 'active',
  created_at      timestamptz NOT NULL DEFAULT now()
);

-- Brand incentive enrollments (operator opts in)
CREATE TABLE cue_incentive_enrollments (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  incentive_id    uuid NOT NULL REFERENCES cue_brand_incentives(id),
  operator_id     uuid NOT NULL REFERENCES operators(id),
  status          varchar(20) DEFAULT 'active',
  units_sold      integer DEFAULT 0,
  payout_amount   numeric(10,2) DEFAULT 0,
  enrolled_at     timestamptz NOT NULL DEFAULT now()
);
```

---

## 4. Data Flow Architecture

### 4.1 The Complete Data Loop

```
                    ┌─────────────────────────────────────┐
                    │          CUSTOMER LAYER              │
                    │                                     │
                    │  Customer visits dispensary website   │
                    │  Interacts with Virtual Budtender    │
                    │  "I want something for sleep"        │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │      VIRTUAL BUDTENDER              │
                    │                                     │
                    │  1. Parse intent (LLM)              │
                    │  2. Query GLASS products            │
                    │  3. Score & rank                    │
                    │  4. Generate recommendation         │
                    │                                     │
                    │  OUTPUT: Recommendation to customer │
                    │  SIGNAL: demand_event {             │
                    │    effect: "sleep",                 │
                    │    category: "edible",              │
                    │    clicked: "Sleep Gummies",        │
                    │    operator: "Pure Oasis"           │
                    │  }                                  │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │     GLASS DATABASE (PostgreSQL)      │
                    │                                     │
                    │  ┌──────────┐  ┌────────────────┐   │
                    │  │ Products │  │ Prices         │   │
                    │  │ 20K+    │  │ 21K+/day       │   │
                    │  └──────────┘  └────────────────┘   │
                    │  ┌──────────┐  ┌────────────────┐   │
                    │  │ Operators│  │ Threats        │   │
                    │  │ 492+    │  │ CCC + market   │   │
                    │  └──────────┘  └────────────────┘   │
                    │  ┌──────────────────────────────┐   │
                    │  │ Budtender Events / Demand    │   │
                    │  │ Signals (NEW — from widget)  │   │
                    │  └──────────────────────────────┘   │
                    │  ┌──────────────────────────────┐   │
                    │  │ CCC Regulatory Data          │   │
                    │  │ (weekly sales, pending apps, │   │
                    │  │  demographics, plant activity)│   │
                    │  └──────────────────────────────┘   │
                    └────┬──────────┬──────────┬──────────┘
                         │          │          │
              ┌──────────┘          │          └──────────┐
              ▼                     ▼                     ▼
    ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐
    │ CUE ENGINE       │  │ NEWSLETTER      │  │ GLASS DASHBOARD  │
    │                  │  │                 │  │                  │
    │ Pricing Engine:  │  │ "Sleep product  │  │ Price Wire       │
    │ "Competitor       │  │  queries up 40% │  │ Threat Radar     │
    │  dropped flower   │  │  — are you      │  │ Competitors      │
    │  to $35. Adjust   │  │  stocked?"      │  │ Recommendations  │
    │  to $33."         │  │                 │  │                  │
    │                  │  │ Market intel +   │  │ Personalized     │
    │ Demand Forecast:  │  │ demand signals  │  │ per-operator     │
    │ "Edibles +18%     │  │ = unique content│  │ insights         │
    │  this week.       │  │                 │  │                  │
    │  Stock up."       │  │                 │  │                  │
    │                  │  │                 │  │                  │
    │ Inventory:       │  │                 │  │                  │
    │ "You're missing   │  │                 │  │                  │
    │  beverages.       │  │                 │  │                  │
    │  18 queries,     │  │                 │  │                  │
    │  0 products."    │  │                 │  │                  │
    └────────┬─────────┘  └────────┬────────┘  └────────┬─────────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │  MORE OPERATORS  │
                          │  SIGN UP         │
                          │                  │
                          │  Better data     │
                          │  = Better recs   │
                          │  = More signups  │
                          │  = Better data   │
                          │  (FLYWHEEL)      │
                          └─────────────────┘
```

### 4.2 Data Dependencies Between Products

```
GLASS Scraper
  ├── feeds → GLASS Dashboard (direct queries)
  ├── feeds → Virtual Budtender (product recommendations)
  ├── feeds → Cue Dynamic Pricing (competitor comparisons)
  └── feeds → Newsletter (market intel sections)

Virtual Budtender
  ├── reads ← GLASS products + prices (for recommendations)
  ├── writes → budtender_events (every interaction)
  ├── writes → budtender_demand_signals (nightly aggregation)
  ├── feeds → Cue Demand Forecasting (what customers want)
  ├── feeds → Cue Inventory Optimization (demand gaps)
  └── feeds → Newsletter (trending queries as content)

Cue Dynamic Pricing
  ├── reads ← GLASS prices + operator's margin_rules
  ├── reads ← Competitor proximity data
  ├── writes → recommendations (price change suggestions)
  ├── writes → alerts (pricing alerts)
  └── writes → cue_pricing_snapshots (daily market position)

Cue Demand Forecasting
  ├── reads ← budtender_demand_signals (what customers ask for)
  ├── reads ← GLASS price trends (what's selling)
  ├── reads ← CCC plant activity (market-level demand)
  └── writes → alerts (demand trend alerts)

Cue Inventory Optimization
  ├── reads ← budtender_demand_signals (demand vs supply gaps)
  ├── reads ← GLASS product availability per operator
  ├── reads ← Competitor product mix
  └── writes → recommendations (stock adjustment suggestions)

Newsletter
  ├── reads ← GLASS prices, brands, threats
  ├── reads ← CCC regulatory data
  ├── reads ← budtender_demand_signals (trending queries)
  └── output → Beehiiv email distribution
```

### 4.3 Nightly Aggregation Jobs

```
┌─────────────────────────────────────────────────────────┐
│  NIGHTLY JOBS (run at 2 AM ET)                          │
│                                                         │
│  1. budtender_aggregate_demand (2:00 AM)                │
│     - Aggregate yesterday's budtender_events             │
│     - Write to budtender_demand_signals                  │
│     - Input: raw events grouped by operator + effect     │
│     - Output: demand signal rows with counts + trends    │
│                                                         │
│  2. cue_pricing_snapshot (2:15 AM)                       │
│     - For each Cue subscriber operator:                  │
│       - Calculate market position per category           │
│       - Compare to nearby competitors                    │
│       - Generate recommendations if gap > threshold      │
│     - Input: prices + operators + margin_rules            │
│     - Output: cue_pricing_snapshots + recommendations    │
│                                                         │
│  3. cue_demand_forecast (2:30 AM)                        │
│     - Aggregate demand signals across all operators       │
│     - Identify trending effects / categories              │
│     - Generate inventory alerts for subscribers           │
│     - Input: budtender_demand_signals + prices            │
│     - Output: alerts (demand trend type)                  │
│                                                         │
│  4. newsletter_data_export (3:00 AM)                     │
│     - Generate glass_data.json with all sections          │
│     - Include CCC cross-references                        │
│     - Include top Budtender demand signals                │
│     - Input: all GLASS tables                             │
│     - Output: glass_data.json for newsletter pipeline     │
└─────────────────────────────────────────────────────────┘
```

---

## 5. API Endpoints

### 5.1 Virtual Budtender API

```
BASE: https://api.glass.roviq.com/v1/budtender

── WIDGET ENDPOINTS (public, rate-limited, API key auth) ──

POST /recommend
  Auth: API key (data-operator attribute from embed)
  Rate limit: 100/month (free), unlimited (pro/enterprise)
  Body: {
    query: string,                  // "something for relaxation"
    session_id: string,             // widget-generated anonymous ID
    filters?: {
      categories?: string[],
      price_min?: number,
      price_max?: number,
      thc_min?: number,
      thc_max?: number,
      effects?: string[],
      strain_type?: string
    },
    previous_recommendations?: string[],  // product IDs to exclude
    limit?: number                        // default 3, max 5
  }
  Response: {
    recommendations: [{
      product_id: string,
      name: string,
      brand: string,
      category: string,
      price: number,
      thc_percent: number,
      cbd_percent: number,
      strain_type: string,
      explanation: string,          // "Great for relaxation without..."
      score: number,                // 0-1 relevance score
      availability: string
    }],
    follow_up_suggestions: string[],  // ["Want something cheaper?", "Try vapes?"]
    session_context: {
      parsed_intent: object,
      products_considered: number,
      response_time_ms: number
    }
  }

POST /event
  Auth: API key
  Rate limit: 1000/hour
  Body: {
    session_id: string,
    event_type: string,
    product_id?: string,
    position?: number,
    metadata?: object
  }
  Response: { ok: true }

GET /products
  Auth: API key
  Description: Returns all products available for this operator
  Query: ?category=flower&in_stock=true&limit=50&offset=0
  Response: {
    products: [...],
    total: number,
    categories: string[],
    last_updated: string
  }

── OPERATOR MANAGEMENT ENDPOINTS (Clerk auth required) ──

GET /config
  Auth: Clerk JWT
  Response: BudtenderConfig object

PUT /config
  Auth: Clerk JWT
  Body: { theme, position, accent_color, tone, category_weights, excluded_skus }

GET /analytics
  Auth: Clerk JWT
  Query: ?period=7d|30d|90d
  Response: {
    sessions: number,
    queries: number,
    recommendations_served: number,
    product_clicks: number,
    click_through_rate: number,
    top_queries: [{query, count}],
    top_recommended: [{product_id, name, clicks}],
    demand_gaps: [{query_pattern, count, matching_products}],
    daily_breakdown: [{date, sessions, queries, clicks}]
  }

GET /analytics/demand-signals
  Auth: Clerk JWT
  Query: ?period=7d|30d
  Response: {
    signals: [{
      effect: string,
      query_count: number,
      trend: 'rising' | 'stable' | 'declining',
      matching_products: number,
      gap_severity: 'none' | 'low' | 'high'
    }]
  }

POST /config/generate-key
  Auth: Clerk JWT
  Response: { api_key: "op_..." }

GET /embed-code
  Auth: Clerk JWT
  Response: { script_tag: string, iframe_url: string }
```

### 5.2 Cue API

```
BASE: https://api.glass.roviq.com/v1/cue

── DYNAMIC PRICING ──

GET /pricing/position
  Auth: Clerk JWT
  Query: ?category=flower&radius_miles=5
  Response: {
    categories: [{
      category: string,
      your_avg_price: number,
      market_median: number,
      market_avg: number,
      percentile_rank: number,       // 0-100
      competitor_count: number,
      trend: 'rising' | 'stable' | 'declining',
      recommendation_count: number
    }],
    snapshot_date: string
  }

GET /pricing/recommendations
  Auth: Clerk JWT
  Query: ?status=pending&category=flower&confidence_min=0.75
  Response: {
    recommendations: [{
      id: string,
      product: { id, name, brand, category },
      current_price: number,
      recommended_price: number,
      confidence: number,
      expected_unit_delta: number,
      expected_margin_delta: number,
      rationale: string,
      factors: object,
      market_context: object,
      expires_at: string
    }],
    total: number
  }

POST /pricing/recommendations/:id/apply
  Auth: Clerk JWT
  Body: { applied_price?: number }    // optional override
  Response: { ok: true, applied_price: number }

POST /pricing/recommendations/:id/dismiss
  Auth: Clerk JWT
  Body: { reason?: string }
  Response: { ok: true }

GET /pricing/report
  Auth: Clerk JWT
  Query: ?period=7d|30d
  Response: {
    summary: {
      total_recommendations: number,
      applied: number,
      dismissed: number,
      estimated_revenue_impact: number
    },
    by_category: [...],
    competitor_movements: [{
      competitor: string,
      products_changed: number,
      avg_change_pct: number
    }]
  }

── DEMAND FORECASTING ──

GET /demand/forecast
  Auth: Clerk JWT (Professional+ tier)
  Query: ?period=7d
  Response: {
    category_forecasts: [{
      category: string,
      demand_trend: 'rising' | 'stable' | 'declining',
      trend_strength: number,       // 0-1
      budtender_signal: {
        query_count: number,
        top_effects: string[],
        week_over_week_change: number
      },
      market_signal: {
        price_trend: string,
        new_products_listed: number
      }
    }],
    effect_trends: [{
      effect: string,
      query_count_7d: number,
      trend: string,
      top_matching_products: string[]
    }]
  }

── INVENTORY OPTIMIZATION ──

GET /inventory/health
  Auth: Clerk JWT (Professional+ tier)
  Response: {
    overstocked: [{
      category: string,
      sku_count: number,
      low_velocity_skus: [{product_id, name, days_stale}],
      suggestion: string
    }],
    understocked: [{
      category: string,
      demand_signals: number,        // budtender queries
      current_sku_count: number,
      competitor_avg_sku_count: number,
      suggestion: string
    }],
    gaps: [{
      query_pattern: string,
      query_count: number,
      matching_products: number,
      competitor_has: boolean,
      suggestion: string
    }],
    balanced: [{
      category: string,
      sku_count: number,
      velocity: string
    }]
  }

── BRAND INCENTIVES ──

GET /incentives
  Auth: Clerk JWT (Enterprise tier)
  Response: {
    available: [{
      id: string,
      brand: string,
      product: { id, name },
      incentive_type: string,
      amount: number,
      start_date: string,
      end_date: string,
      projected_volume: number,
      projected_payout: number
    }],
    active: [{
      id: string,
      brand: string,
      units_sold: number,
      payout_to_date: number,
      remaining_budget: number
    }]
  }

POST /incentives/:id/enroll
  Auth: Clerk JWT (Enterprise)
  Response: { enrollment_id: string, ok: true }

── SUBSCRIPTION MANAGEMENT ──

GET /subscription
  Auth: Clerk JWT
  Response: CueSubscription object

POST /subscription
  Auth: Clerk JWT
  Body: { tier: 'starter' | 'professional' | 'enterprise', billing_cycle: 'monthly' | 'annual' }

PUT /subscription
  Auth: Clerk JWT
  Body: { tier?, billing_cycle?, status? }
```

---

## 6. MVP Build Plan (2-Week Sprints)

### 6.1 Virtual Budtender MVP — 2 Weeks

**Goal:** Working recommendation widget that operators can embed on their site. Free tier only.

```
WEEK 1: Backend + Recommendation Engine
─────────────────────────────────────────

Day 1-2: Database + API scaffold
  - Create budtender_configs, budtender_sessions, budtender_events tables
  - Migrate schema
  - Create /v1/budtender/* route stubs in Fastify
  - API key generation + validation middleware

Day 3-4: Recommendation engine core
  - Intent parser: integrate GPT-4o-mini for query understanding
  - Product retrieval: query products + latest prices for operator_id
  - Scoring algorithm: implement weighted scoring (effect match, potency,
    price, availability)
  - Effect mapping table (static lookup — 10 primary effects)
  - Response generator: GPT-4o-mini for conversational output
  - End-to-end test: query → parse → retrieve → score → respond

Day 5: Event tracking + analytics queries
  - POST /event endpoint for widget events
  - Analytics aggregation queries for /analytics endpoint
  - Rate limiting middleware (100 recs/month for free tier)

WEEK 2: Widget Frontend + Operator Setup
─────────────────────────────────────────

Day 6-7: Embeddable widget
  - embed.js loader script (~5KB)
  - Widget iframe app (React, minimal bundle):
    - Chat interface with message bubbles
    - Product recommendation cards
    - Filter chips (category, price, effect)
    - "Powered by GLASS" branding
  - postMessage bridge for product click → host site redirect
  - Theme support: light/dark/auto

Day 8-9: Operator setup flow
  - Update /budtender page with real setup flow:
    - Auto-detect operator from GLASS database
    - Generate API key
    - Preview widget with demo conversation
    - Copy embed code
  - Config panel: theme, position, tone, category weights
  - Basic analytics view in GLASS dashboard

Day 10: Integration testing + deploy
  - Test embed on 3 operator sites (Dutchie-hosted pages)
  - Load test: 100 concurrent recommendations
  - Deploy: embed.js to CDN, API to Railway
  - Smoke test with real GLASS data

DELIVERABLE: Working widget that answers customer questions using
real GLASS product data. Operators can sign up, configure, and embed.
```

### 6.2 Cue MVP (Dynamic Pricing) — 2 Weeks

**Goal:** Automated pricing recommendations based on competitor data. Starter tier ($199/mo).

```
WEEK 1: Pricing Engine + Recommendations
─────────────────────────────────────────

Day 1-2: Database + pricing comparison engine
  - Create cue_subscriptions, cue_pricing_snapshots tables
  - Pricing comparison worker:
    - For each Cue subscriber, for each category:
      - Get operator's current prices
      - Get competitor prices within radius (using existing GLASS data)
      - Calculate market position (median, avg, percentile)
      - Generate snapshot row
  - Schedule: run nightly at 2:15 AM ET

Day 3-4: Recommendation generation
  - Extend existing recommendations table workflow:
    - Scoring logic: gap to market + margin impact + velocity
    - Confidence calculation
    - Rationale generation (template-based, not LLM — faster, cheaper)
    - Respect margin_rules floor/ceiling
  - Apply / Dismiss API endpoints
  - Historical tracking: which recommendations were applied?

Day 5: Alert system
  - Trigger email/SMS for high-confidence recommendations (>0.85)
  - Alert types: competitor_undercut, category_drift, upward_opportunity
  - Rate limit: max 3 alerts/day per operator
  - Use existing alerts table with new Cue-specific types

WEEK 2: Dashboard UI + Subscription
─────────────────────────────────────────

Day 6-7: Cue dashboard section
  - Market position overview: category percentile cards
  - Pricing recommendations list with Apply/Edit/Dismiss
  - Competitor movement feed
  - Weekly pricing report view
  - Integrate into existing GLASS sidebar under "Cue"

Day 8-9: Subscription + billing
  - Stripe integration for $199/mo Starter tier
  - Subscription management: upgrade/downgrade/cancel
  - Trial flow: 14-day free trial, then $199/mo
  - Paywall middleware: check subscription before serving Cue endpoints

Day 10: Testing + deploy
  - Seed test data: run pricing engine against 10 existing operators
  - Verify recommendations make sense (sanity checks)
  - Deploy pricing worker as Railway cron service
  - Activate for first 5 beta operators (free trial)

DELIVERABLE: Working dynamic pricing system that compares operator 
prices to competitors and generates actionable recommendations with 
Apply/Dismiss workflow. $199/mo subscription with Stripe billing.
```

### 6.3 Post-MVP Roadmap

```
Month 2: Budtender Pro + Cue Demand
  - Budtender Pro tier ($99/mo): remove branding, full analytics
  - Budtender demand signal aggregation (nightly job)
  - Cue Demand Forecasting module (reads from Budtender signals)
  - A/B test: different recommendation strategies per operator

Month 3: Cue Professional + Inventory
  - Cue Inventory Optimization module
  - Cross-reference: Budtender demand gaps → inventory suggestions
  - Cue Professional tier ($499/mo)
  - POS integration exploration (Dutchie API, Blaze API)

Month 4-6: Enterprise + Brand Incentives
  - Cue Brand Incentives module
  - Brand-side dashboard and campaign builder
  - Multi-location support
  - Budtender web component + React SDK
  - POS auto-apply for pricing recommendations
```

---

## 7. Revenue Projections

### 7.1 Assumptions

```
Massachusetts market:
  - 650+ licensed retailers
  - ~492 tracked by GLASS currently
  - TAM for Budtender: any operator with a website (~500)
  - TAM for Cue: operators who care about pricing optimization (~300)

Conversion funnel:
  - GLASS free users (target by EOY 2026): 100-200 operators
  - Budtender free tier: 40% of GLASS users try it → 40-80
  - Budtender Pro conversion: 15% of free → 6-12
  - Cue Starter trial: 10% of GLASS users → 10-20
  - Cue Starter conversion after trial: 50% → 5-10
  - Cue Professional upgrade: 30% of Starter → 2-3
```

### 7.2 Year 1 Projections (12 months from launch)

| Metric | Conservative | Moderate | Aggressive |
|--------|-------------|----------|------------|
| **GLASS free users** | 75 | 150 | 250 |
| | | | |
| **Virtual Budtender** | | | |
| Free tier active | 25 | 50 | 100 |
| Pro ($99/mo) | 4 | 10 | 20 |
| Enterprise ($299/mo) | 1 | 3 | 6 |
| **Budtender ARR** | **$8,244** | **$22,680** | **$45,360** |
| | | | |
| **Cue** | | | |
| Starter ($199/mo) | 5 | 12 | 25 |
| Professional ($499/mo) | 2 | 5 | 10 |
| Enterprise ($999/mo) | 0 | 1 | 3 |
| **Cue ARR** | **$23,880** | **$70,440** | **$155,400** |
| | | | |
| **Brand Incentives** | | | |
| Active brands | 0 | 3 | 8 |
| Platform fees/mo | $0 | $600 | $2,000 |
| **Incentives ARR** | **$0** | **$7,200** | **$24,000** |
| | | | |
| **TOTAL PRODUCT ARR** | **$32,124** | **$100,320** | **$224,760** |

### 7.3 Revenue Ramp (Monthly Progression — Moderate Scenario)

```
Month 1-2: Beta testing, free only                          $0/mo
Month 3:   Budtender free + 2 Pro + 1 Cue trial           $198/mo
Month 4:   3 Budtender Pro + 3 Cue Starter                $894/mo
Month 5:   5 Budtender Pro + 5 Cue Starter + 1 Pro        $2,490/mo
Month 6:   7 BT Pro + 1 BT Ent + 8 Cue Start + 2 Pro     $4,289/mo
Month 7:   8 BT Pro + 2 BT Ent + 10 Cue Start + 3 Pro    $5,887/mo
Month 8:   9 BT Pro + 2 BT Ent + 11 Cue Start + 4 Pro    $6,885/mo
Month 9:   10 BT Pro + 3 BT Ent + 12 Cue Start + 5 Pro   $8,282/mo
Month 10:  10 BT Pro + 3 BT Ent + 12 Cue Start + 5 Pro + 1 Ent  $9,281/mo
Month 11:  10 BT Pro + 3 BT Ent + 12 Cue Start + 5 Pro + 1 Ent  $9,281/mo
Month 12:  10 BT Pro + 3 BT Ent + 12 Cue Start + 5 Pro + 1 Ent  $9,281/mo

Moderate EOY MRR: ~$9,300/mo ($111K ARR run rate)
```

### 7.4 Cost Structure

```
LLM Costs (Budtender):
  - GPT-4o-mini: ~$0.001 per recommendation
  - At 50 active free + 10 Pro operators:
    - Free: 50 × 100 recs/mo = 5,000 × $0.001 = $5/mo
    - Pro: 10 × 500 recs/mo = 5,000 × $0.001 = $5/mo
    - Total LLM: ~$10/mo
    - At 10x scale: ~$100/mo

Infrastructure:
  - Railway API service: $20-40/mo (already running)
  - Railway cron worker (Cue): $34/mo
  - CDN for widget (Cloudflare): $0 (free tier)
  - Stripe fees: 2.9% + $0.30 per transaction
  - Total infra at moderate scale: ~$100/mo

COGS at moderate Year 1:
  LLM: ~$100/mo
  Infra: ~$100/mo
  Stripe: ~$300/mo (on ~$8K MRR)
  Total: ~$500/mo
  
  Gross margin: ~94%
```

### 7.5 Year 3 Projection (Moderate)

```
Assuming:
  - Expand to 3 states (MA, CT, ME — similar small markets)
  - 300 Budtender operators (100/state)
  - 80 Cue subscribers across tiers
  - Active brand marketplace (20 brands)

Revenue:
  Budtender: 50 Pro + 15 Enterprise → $113K ARR
  Cue: 40 Starter + 25 Pro + 15 Enterprise → $425K ARR
  Brand Incentives: 20 brands × $1,200/mo avg → $288K ARR
  
  Total Year 3 ARR: ~$826K
  
Combined with GLASS dashboard and agency services:
  GLASS ecosystem total: $826K + $623K (from GLASS-PLAN projections) = ~$1.4M
```

---

## 8. Competitive Analysis

### 8.1 Virtual Budtender Competitors

| Competitor | What They Do | How We're Different |
|-----------|-------------|-------------------|
| **Jointly** | AI-powered cannabis shopping app. Customers search by desired effects. Partners with dispensaries for fulfillment. | Jointly is a *destination app* — customers must go to Jointly. Budtender is *embedded on the dispensary's own site*. The operator keeps the customer. Jointly charges the dispensary for leads. We give the tool for free. |
| **Dutchie** | Online ordering platform with basic product search/filter. Some AI recommendation features in development. | Dutchie is a *menu platform*, not a recommendation engine. Their "recommendations" are basic (similar products, popular items). No conversational AI. No natural language queries. And they own the customer relationship — operators are inside Dutchie's iframe. |
| **FlowHub / Treez / Meadow POS** | POS systems with basic upsell suggestions to budtenders (staff-facing). | Staff-facing tools, not customer-facing. They help the human budtender, not replace the website experience. Also: they require POS integration. Budtender works without any POS. |
| **Alpine IQ / Surfside** | Marketing automation (loyalty, CRM, targeted campaigns). Some product recommendation in emails. | Different category: they're email/SMS marketing tools. Not real-time conversational AI on the website. No natural language. No demand signal capture. |
| **ChatGPT / generic AI chatbots** | Operators could paste their menu into ChatGPT or use a generic chatbot widget. | No dispensary-specific data. No real-time pricing. No demand signal loop. No analytics. Every operator would have to set it up themselves. And it wouldn't know what's actually in stock. |

**Our moat:** We have the data. 20,000+ products with real-time prices across 492+ MA operators. No one else has this scraped, normalized, and queryable. A generic chatbot can't answer "What's your cheapest indica under $40?" because it doesn't know the current menu. We do.

### 8.2 Cue Competitors

| Competitor | What They Do | How We're Different |
|-----------|-------------|-------------------|
| **LeafLink** | Wholesale B2B marketplace ($5B+ annual orders). Some pricing tools for wholesale. | Wholesale only. Doesn't touch retail pricing. Different layer of the supply chain. |
| **Headset** | Cannabis market intelligence — point-of-sale data analytics, consumer insights. Used by brands and operators. | Headset is the closest competitor. BUT: (1) Headset requires POS integration (we don't), (2) Headset sells to brands primarily (we sell to operators), (3) Headset doesn't generate *actionable recommendations* — it shows charts. Cue tells you what to do. (4) Headset doesn't have local competitive pricing — they aggregate POS data, not competitor menus. (5) Headset pricing: $299-999/mo for basic access. |
| **BDSA (now part of BDSA/New Frontier)** | Market research reports. State-level and category-level analytics. | Quarterly PDF reports, not real-time. No per-operator recommendations. No competitive pricing. Research tool, not an operating tool. $10K+/year. |
| **Apex Trading** | MA wholesale marketplace with METRC integration, CRM, email marketing. | Wholesale platform. Does not cover retail pricing, demand forecasting, or consumer-facing tools. Different layer. |
| **Dutchie Analytics** | Menu platform's built-in analytics (sales velocity, popular products). | Only shows *your own* data. Doesn't compare to competitors. Doesn't generate pricing recommendations. Can't tell you "NETA just dropped Wedding Cake to $38" because they don't scrape competitors. |
| **Flowhub / Treez reporting** | POS-native reporting (sales, inventory, margin by category). | Same limitation as Dutchie: your data only. No competitive intelligence. No market-level demand signals. |

**Our moat:** Three things no competitor has simultaneously:
1. **Real-time competitor pricing** (scraped daily from 492+ operators)
2. **Consumer demand signals** (from Virtual Budtender — no competitor captures what customers *ask for* at the effect/product level)
3. **Regulatory intelligence** (CCC data cross-referenced — pending applications, delivery trends, enforcement actions)

Headset is the closest threat. Their advantage: they have POS data (actual transaction volumes). Our advantage: we have competitive pricing data + consumer intent signals + we're 10x cheaper and don't require POS integration.

### 8.3 Competitive Positioning Matrix

```
                    Has Competitive     Has Consumer      Has Regulatory     Requires
                    Pricing Data        Demand Signals    Intelligence       POS Integration
─────────────────────────────────────────────────────────────────────────────────────────
GLASS + Budtender     ✅ (scraped)       ✅ (unique)       ✅ (CCC data)       ❌ (zero friction)
  + Cue

Headset               ❌                 ❌                ❌                  ✅
Dutchie Analytics     ❌                 ❌                ❌                  ✅ (locked in)
LeafLink              ❌ (wholesale)     ❌                ❌                  N/A
BDSA                  ❌ (reports only)  ❌                Partial             N/A
Generic Chatbot       ❌                 ❌                ❌                  N/A
Jointly               ❌                 Partial           ❌                  ❌
```

---

## 9. Go-to-Market Strategy

### 9.1 Virtual Budtender GTM

**Phase 1: Seed with GLASS users (Month 1-2)**

```
Target: Existing GLASS dashboard users (free tier)
Channel: In-app CTAs (already designed in FLYWHEEL-UI-PLAN.md)
Message: "Your customers are scrolling your menu and leaving. 
         Give them an AI assistant that knows your products."
Offer: Free forever (100 recs/mo), setup in 2 minutes

Tactics:
  1. Morning Brief CTA: "Turn today's top movers into personalized picks"
  2. Email to all GLASS signups: "New free tool: AI budtender for your website"
  3. Newsletter mention: "Operators using Virtual Budtender saw 18% CTR"
  4. Demo video: 30-second screen recording of a customer conversation
```

**Phase 2: Cold outreach via the widget itself (Month 3-4)**

```
Target: MA dispensaries NOT yet on GLASS
Channel: Direct outreach with a free offer that's too good to ignore
Message: "We built an AI product recommender for dispensary websites. 
         It's free. Here's what it looks like on [THEIR COMPETITOR'S] site."

Tactics:
  1. Show a mock-up with THEIR product data (we already have it from scraping)
  2. "Your competitor Pure Oasis already has this on their site. Want one?"
  3. Setup takes 2 minutes — paste a script tag
  4. No commitment, no credit card, no POS integration required
  
  This approach works because:
  - Randy hates cold outreach → but this isn't a pitch, it's a free tool with a demo
  - The competitive angle creates urgency without pushy sales
  - Once embedded, the operator depends on GLASS data (retention hook)
```

**Phase 3: Pro upgrade (Month 4-6)**

```
Target: Free tier operators who hit 100 rec/month limit or want analytics
Channel: In-widget prompt + email
Message: "You hit 100 recommendations this month. Your customers asked about 
         'sleep' 34 times. Upgrade to Pro for unlimited recs + full analytics."
Offer: $99/mo, 14-day free trial

Upsell triggers:
  - Hit monthly limit (natural friction)
  - High demand gap ("23 queries for CBD flower, 0 products — see analytics")
  - Competitor adoption ("3 dispensaries near you upgraded to Pro this month")
```

### 9.2 Cue GTM

**Phase 1: Beta with GLASS power users (Month 1-2)**

```
Target: GLASS users who actively check Price Wire and Recommendations
Channel: Direct invitation (email + in-app)
Message: "You check competitor prices every morning. 
         What if we just told you what to change?"
Offer: Free 30-day beta (no commitment)

Selection criteria for beta:
  - Active GLASS users (logged in 3+/week)
  - Have margin_rules configured
  - Located near competitors (competitive market)
  - 5-10 operators max
```

**Phase 2: Paid launch with case studies (Month 3-4)**

```
Target: All GLASS users + MA operator outreach
Channel: Newsletter, in-app, direct email
Message: "[Beta operator] adjusted 14 prices in the first week 
         based on Cue recommendations. Estimated margin lift: $X/month."
Offer: $199/mo Starter, 14-day free trial

Content marketing:
  - Newsletter case study: "How [Operator] uses Cue to stay competitive"
  - Public Market page: "Average MA dispensary is 14% above market on vapes"
  - LinkedIn/industry posts by Randy
```

**Phase 3: Professional tier + Demand module (Month 5-8)**

```
Target: Starter subscribers who want more
Channel: In-app upsell + email
Message: "Your customers asked for 'sleep products' 67 times last week. 
         You carry 1 matching product. Cue Professional shows you what to stock."
Offer: $499/mo (includes Demand Forecasting + Inventory Optimization)

The Budtender→Cue pipeline:
  - Budtender captures demand signals
  - Cue Demand module turns signals into recommendations
  - This creates a natural upgrade path: free tool → see the gap → pay to fill it
```

**Phase 4: Enterprise + Brand marketplace (Month 9-12)**

```
Target: Multi-store operators + cannabis brands
Channel: Direct sales (Randy or agency partner)
Message: To operators: "Brands will pay you to feature their products. 
         Cue manages it all."
         To brands: "Access 100+ dispensary operators through one platform. 
         Pay for performance, not impressions."
Offer: Enterprise $999/mo + brand marketplace access

Revenue model:
  - Operators pay subscription
  - Brands pay platform fee (15% of payouts)
  - GLASS takes both sides
```

### 9.3 Combined GTM Flywheel

```
Newsletter (free weekly email)
  → "See your competitor's prices" (GLASS signup CTA)
  → GLASS Dashboard (free, see market data)
  → "Give your customers an AI assistant" (Budtender CTA)
  → Virtual Budtender (free, embed on site)
  → Budtender captures demand signals
  → "Your customers want X but you don't carry it" (Cue CTA)
  → Cue Starter ($199/mo, dynamic pricing)
  → Cue shows inventory gaps from Budtender data
  → Cue Professional ($499/mo, full optimization)
  → Brand marketplace connects brands to operators
  → Cue Enterprise ($999/mo)
  → All data feeds back into GLASS intelligence
  → Better GLASS data → better Newsletter → more signups
  → FLYWHEEL ACCELERATES
```

### 9.4 Key Metrics to Track

```
Acquisition:
  - GLASS free signups/month
  - Budtender widget installations/month
  - Cue trial starts/month
  - Newsletter → GLASS conversion rate
  - GLASS → Budtender activation rate
  - GLASS → Cue trial rate

Engagement:
  - Budtender: recommendations/session, CTR, daily active operators
  - Cue: recommendations viewed, applied %, dismissed %
  - GLASS: DAU/MAU ratio, pages per session

Revenue:
  - MRR by product (Budtender Pro, Cue Starter/Pro/Enterprise)
  - ARPU (average revenue per user)
  - Churn rate by tier
  - Trial → paid conversion rate
  - Expansion revenue (upgrades Starter → Pro → Enterprise)

Flywheel:
  - Budtender demand signals generated/day
  - Demand signals consumed by Cue/day
  - Recommendations applied → actual price change rate
  - Time from signal to action (how fast do operators act?)
```

---

## Appendix A: Effect-to-Product Mapping (V1)

```typescript
// src/services/api/src/budtender/effect-map.ts

export const EFFECT_MAP: Record<string, {
  strain_types: string[];
  categories: string[];
  thc_range: [number, number]; // min, max
  cbd_min?: number;
  keywords: string[];
}> = {
  relaxation: {
    strain_types: ['indica', 'hybrid'],
    categories: ['flower', 'edible', 'vape', 'tincture'],
    thc_range: [5, 25],
    cbd_min: 0,
    keywords: ['relax', 'relaxing', 'calm', 'chill', 'unwind', 'wind down', 'de-stress'],
  },
  sleep: {
    strain_types: ['indica'],
    categories: ['edible', 'flower', 'tincture', 'vape'],
    thc_range: [10, 30],
    keywords: ['sleep', 'insomnia', 'bedtime', 'nighttime', 'rest', 'knockout'],
  },
  energy: {
    strain_types: ['sativa'],
    categories: ['flower', 'vape', 'edible'],
    thc_range: [10, 25],
    keywords: ['energy', 'energetic', 'uplifting', 'daytime', 'focus', 'productive', 'wake'],
  },
  pain_relief: {
    strain_types: ['indica', 'hybrid'],
    categories: ['topical', 'tincture', 'edible', 'flower', 'concentrate'],
    thc_range: [15, 35],
    cbd_min: 5,
    keywords: ['pain', 'relief', 'ache', 'sore', 'chronic', 'inflammation', 'arthritis'],
  },
  creativity: {
    strain_types: ['sativa', 'hybrid'],
    categories: ['flower', 'vape', 'edible'],
    thc_range: [12, 25],
    keywords: ['creative', 'creativity', 'art', 'music', 'inspired', 'imaginative'],
  },
  social: {
    strain_types: ['sativa', 'hybrid'],
    categories: ['flower', 'vape', 'edible', 'preroll'],
    thc_range: [5, 20],
    keywords: ['social', 'party', 'friends', 'fun', 'giggly', 'talkative', 'hangout'],
  },
  anxiety_relief: {
    strain_types: ['indica', 'hybrid'],
    categories: ['edible', 'tincture', 'flower', 'vape'],
    thc_range: [0, 15],
    cbd_min: 5,
    keywords: ['anxiety', 'anxious', 'stress', 'nervous', 'worry', 'panic', 'calm down'],
  },
  beginner: {
    strain_types: ['hybrid', 'indica', 'sativa'],
    categories: ['edible', 'vape', 'tincture', 'flower'],
    thc_range: [0, 15],
    keywords: ['first time', 'beginner', 'never tried', 'new to', 'starter', 'mild', 'gentle'],
  },
  potent: {
    strain_types: ['indica', 'hybrid', 'sativa'],
    categories: ['concentrate', 'flower', 'edible', 'vape'],
    thc_range: [25, 100],
    keywords: ['strong', 'potent', 'powerful', 'heavy', 'intense', 'maximum', 'highest THC'],
  },
  microdose: {
    strain_types: ['hybrid', 'sativa', 'indica'],
    categories: ['edible', 'tincture'],
    thc_range: [0, 5],
    keywords: ['microdose', 'micro', 'low dose', 'minimal', '2.5mg', '5mg', 'light'],
  },
};
```

## Appendix B: System Prompt for Budtender LLM

```typescript
// src/services/api/src/budtender/system-prompt.ts

export function getBudtenderSystemPrompt(config: BudtenderConfig): string {
  return `You are a virtual budtender for ${config.operator_name || 'a Massachusetts dispensary'}.

ROLE: Help customers find the right cannabis products based on their needs.
TONE: ${config.tone || 'friendly'} — knowledgeable but approachable. Never clinical. Never preachy.

RULES:
1. Only recommend products from the provided product list (the dispensary's actual menu)
2. Never recommend products not in stock
3. Always mention: product name, brand, price, THC%, and a brief reason why it fits
4. If the customer's needs are unclear, ask a clarifying question
5. For new/first-time customers, always suggest starting low and slow
6. Never make medical claims. You're not a doctor.
7. Keep responses concise — 2-3 sentences per product recommendation
8. If asked about something the dispensary doesn't carry, say so honestly and suggest the closest alternative
9. Use the customer's language — if they say "munchies", don't say "appetite stimulation"
10. Maximum 3 recommendations per response unless the customer asks for more

CONTEXT:
- You have access to real-time product data including prices, THC%, CBD%, strain type, and availability
- Products are from a Massachusetts licensed dispensary
- All customers are 21+ (age-verified before accessing the widget)

FORMAT:
- Start with a brief acknowledgment of what they're looking for
- List recommendations with name, brand, price, key stat, and a one-line reason
- End with a follow-up question or suggestion to narrow further`;
}
```

## Appendix C: Pricing Engine Pseudocode

```typescript
// src/services/api/src/cue/pricing-engine.ts (pseudocode)

interface PricingInput {
  operator_id: string;
  radius_miles: number;      // default 5
  min_confidence: number;    // default 0.75
}

async function generatePricingRecommendations(input: PricingInput) {
  // 1. Get operator's current products + prices
  const operatorProducts = await db.query(`
    SELECT p.id, p.name, p.brand, p.category, 
           pr.price, pr.scraped_at,
           mr.min_price, mr.max_price, mr.target_margin_pct
    FROM products p
    JOIN prices pr ON pr.product_id = p.id AND pr.operator_id = $1
    LEFT JOIN margin_rules mr ON mr.operator_id = $1 AND mr.category = p.category
    WHERE pr.scraped_at > NOW() - INTERVAL '7 days'
    ORDER BY pr.scraped_at DESC
  `, [input.operator_id]);

  // 2. For each product, get competitor prices
  for (const product of operatorProducts) {
    const competitors = await db.query(`
      SELECT pr.price, o.name as competitor_name, o.city,
             haversine(op.lat, op.lon, o.lat, o.lon) as distance_miles
      FROM prices pr
      JOIN operators o ON pr.operator_id = o.id
      JOIN operators op ON op.id = $1
      JOIN products p ON pr.product_id = p.id
      WHERE p.category = $2
        AND pr.operator_id != $1
        AND pr.scraped_at > NOW() - INTERVAL '7 days'
        AND haversine(op.lat, op.lon, o.lat, o.lon) <= $3
    `, [input.operator_id, product.category, input.radius_miles]);

    if (competitors.length < 2) continue; // need enough data

    // 3. Calculate market statistics
    const prices = competitors.map(c => c.price);
    const median = calculateMedian(prices);
    const avg = calculateAvg(prices);
    const percentile = calculatePercentile(product.price, prices);

    // 4. Determine if recommendation is warranted
    const gap = (product.price - median) / median;
    
    if (Math.abs(gap) < 0.05) continue; // within 5% of median — no action

    // 5. Calculate recommended price
    let recommendedPrice: number;
    let type: string;
    
    if (gap > 0.10) {
      // Overpriced by 10%+: suggest reduction
      recommendedPrice = Math.max(
        median * 0.98,                    // slightly below median
        product.min_price || 0            // respect floor
      );
      type = 'reduce';
    } else if (gap < -0.10) {
      // Underpriced by 10%+: suggest increase
      recommendedPrice = Math.min(
        median * 0.95,                    // slightly below median (still competitive)
        product.max_price || Infinity     // respect ceiling
      );
      type = 'increase';
    }

    // 6. Calculate confidence
    const confidence = calculateConfidence({
      competitor_count: competitors.length,
      data_freshness: daysSinceLastScrape,
      gap_size: Math.abs(gap),
      margin_rule_exists: !!product.target_margin_pct,
    });

    if (confidence < input.min_confidence) continue;

    // 7. Generate recommendation
    await db.insert('recommendations', {
      operator_id: input.operator_id,
      product_id: product.id,
      current_price: product.price,
      recommended_price: recommendedPrice,
      confidence,
      expected_unit_delta: estimateUnitImpact(gap, product.category),
      expected_margin_delta: estimateMarginImpact(product.price, recommendedPrice, product.target_margin_pct),
      status: 'pending',
      rationale: generateRationale(type, product, median, competitors),
      model_version: 'cue-pricing-v1.0.0',
      factors: { gap, median, avg, percentile, competitor_count: competitors.length },
      market_context: { radius_miles: input.radius_miles, window_days: 7 },
      expires_at: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000), // 5 days
    });
  }
}
```

---

*This spec defines two real products connected to real GLASS data. The Virtual Budtender is a free tool that operators embed on their sites — it captures demand signals no competitor has. Cue turns GLASS intelligence into revenue-generating pricing, inventory, and brand incentive actions. Together, they create a data flywheel where every customer interaction makes the entire ecosystem smarter.*

*Build order: Budtender MVP (2 weeks) → Cue Dynamic Pricing MVP (2 weeks) → iterate based on operator feedback.*
