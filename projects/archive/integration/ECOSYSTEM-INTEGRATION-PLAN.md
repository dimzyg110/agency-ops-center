# Roviq Ecosystem Integration Plan

**Version:** 1.0  
**Date:** February 12, 2026  
**Author:** Product Architecture Team  
**Status:** Blueprint — Ready for implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Part 1: Data Flow Architecture](#part-1-data-flow-architecture)
3. [Part 2: Integration Points](#part-2-integration-points)
4. [Part 3: Unified Database Strategy](#part-3-unified-database-strategy)
5. [Part 4: Cue Expansion — Beyond Budtenders](#part-4-cue-expansion--beyond-budtenders)
6. [Part 5: Unified Auth](#part-5-unified-auth)
7. [Part 6: Implementation Roadmap](#part-6-implementation-roadmap)
8. [Part 7: CH Driver Program — Detailed Spec](#part-7-ch-driver-program--detailed-spec)

---

## 1. Executive Summary

The Roviq ecosystem consists of four products at different maturity stages:

| Product | Status | Database | Auth | Revenue Model |
|---------|--------|----------|------|---------------|
| **GLASS** | LIVE | PostgreSQL (Railway) | Clerk | Subscription ($49-$299/mo) |
| **Virtual Budtender** | LIVE (CH only) | Firebase Firestore | None (public widget) | SaaS (Free→$99→$299/mo) |
| **Cue** | MVP BUILT | PostgreSQL (Neon) | Firebase Phone Auth | Two-sided marketplace |
| **Delivery** | CONCEPT | Blaze POS (external) | TBD | Rev share + upfront |

**The core thesis:** GLASS is the data gravity well. Every product in the ecosystem either feeds data into GLASS or consumes data from GLASS. The integration strategy is **GLASS as the single source of truth for product/pricing data**, with purpose-built APIs connecting each spoke.

**Key architectural decision: Hub-and-spoke, not monolith.** Each product keeps its own database for domain-specific data (missions, conversations, orders) but shares a unified product catalog and pricing layer through GLASS's API. This avoids a premature mega-merge while still enabling the flywheel.

---

## Part 1: Data Flow Architecture

### 1.1 Current State — Three Isolated Data Islands

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CURRENT STATE (Isolated)                     │
│                                                                     │
│  ┌──────────────────────┐   ┌──────────────────┐   ┌────────────┐  │
│  │ GLASS PostgreSQL     │   │ Budtender         │   │ Cue Neon   │  │
│  │ (Railway)            │   │ Firestore         │   │ PostgreSQL │  │
│  │                      │   │                   │   │            │  │
│  │ • operators (472)    │   │ • products (CH    │   │ • users    │  │
│  │ • products (100K+)   │   │   only, ~300)     │   │ • brands   │  │
│  │ • prices (117K+)     │   │ • sessions (none) │   │ • missions │  │
│  │ • sources            │   │                   │   │ • products │  │
│  │ • threats            │   │                   │   │ • sales_   │  │
│  │ • recommendations    │   │                   │   │   submissions│ │
│  │ • scrape_runs        │   │                   │   │ • rewards  │  │
│  │ • alerts             │   │                   │   │ • courses  │  │
│  │ • margin_rules       │   │                   │   │            │  │
│  │ • waitlist           │   │                   │   │            │  │
│  │ • CCC tables (6)     │   │                   │   │            │  │
│  └──────────────────────┘   └──────────────────┘   └────────────┘  │
│                                                                     │
│  NO data flows between them today.                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Target State — GLASS as Data Hub

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           TARGET STATE (Integrated)                          │
│                                                                              │
│                    ┌──────────────────────────────┐                           │
│                    │       GLASS PostgreSQL        │                           │
│                    │       (Railway — Hub)         │                           │
│                    │                               │                           │
│                    │  SHARED TABLES:               │                           │
│                    │  • operators (500+)           │                           │
│                    │  • products (100K+)           │                           │
│                    │  • prices (117K+, growing)    │                           │
│                    │  • CCC data (6 tables)        │                           │
│                    │                               │                           │
│                    │  NEW INTEGRATION TABLES:      │                           │
│                    │  • budtender_sessions         │                           │
│                    │  • budtender_queries          │                           │
│                    │  • demand_signals             │                           │
│                    │  • ecosystem_events           │                           │
│                    │                               │                           │
│                    │  GLASS-ONLY TABLES:           │                           │
│                    │  • threats, alerts            │                           │
│                    │  • recommendations            │                           │
│                    │  • margin_rules, watchlists   │                           │
│                    │  • scrape_runs, scrape_jobs   │                           │
│                    │  • sources, users             │                           │
│                    └──────┬───────┬───────┬────────┘                           │
│                           │       │       │                                    │
│               ┌───────────┘       │       └───────────┐                        │
│               │                   │                   │                        │
│               ▼                   ▼                   ▼                        │
│  ┌────────────────────┐ ┌────────────────┐ ┌──────────────────┐               │
│  │ Virtual Budtender  │ │  Cue (Neon)    │ │ Delivery         │               │
│  │ (Reads GLASS API)  │ │  (Own domain   │ │ (Blaze POS +     │               │
│  │                    │ │   data)        │ │  React Native)   │               │
│  │ Firestore → GONE   │ │               │ │                  │               │
│  │ Uses GLASS API     │ │ • missions    │ │ • orders (Blaze) │               │
│  │ for product data   │ │ • submissions │ │ • routes (Blaze) │               │
│  │                    │ │ • participants│ │ • ratings         │               │
│  │ Writes back:       │ │ • rewards     │ │                  │               │
│  │ • query logs       │ │ • courses     │ │ Reads from Cue:  │               │
│  │ • demand signals   │ │               │ │ • driver missions│               │
│  │ • conversion data  │ │ Reads GLASS:  │ │ • incentive rules│               │
│  │                    │ │ • products    │ │                  │               │
│  └────────────────────┘ │ • prices      │ └──────────────────┘               │
│                         │ • operators   │                                    │
│                         │               │                                    │
│                         │ Writes GLASS: │                                    │
│                         │ • ecosystem_  │                                    │
│                         │   events      │                                    │
│                         └────────────────┘                                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Detailed Data Flow Table

| Data | Source | Destination | Mechanism | Frequency |
|------|--------|-------------|-----------|-----------|
| Product catalog (100K+) | GLASS scrapers → GLASS DB | Virtual Budtender, Cue | GLASS REST API | Real-time (on request) |
| Price observations | Dutchie/Weedmaps → GLASS DB | GLASS dashboard, Cue mission targeting | Direct DB (scrapers) | Daily (3AM + 10PM ET) |
| CCC state data | CCC CSV → GLASS DB | GLASS dashboard, Cue mission context | Import script | Weekly |
| Budtender queries | Customer → VB widget | GLASS `budtender_queries` table | VB backend → GLASS API | Per-conversation |
| Demand signals | Aggregated from VB queries | GLASS `demand_signals` table | Nightly batch job | Daily |
| Mission performance | Cue submissions | GLASS `ecosystem_events` table | Cue backend → GLASS API | Per-submission |
| Conversion tracking | VB recommendation → purchase | GLASS `budtender_sessions` | Dutchie redirect click tracking | Per-click |
| Driver delivery data | Blaze POS | Cue (via webhook or manual) | Blaze API or manual CSV | Per-delivery or daily |
| Gift card redemptions | Tremendous API → Cue | Cue `redemptions` table | Tremendous webhook | Per-redemption |
| Brand spend | Cue mission budgets | GLASS `ecosystem_events` | Cue → GLASS API | Per-mission-create |

### 1.4 New GLASS Tables for Integration

```sql
-- Add to GLASS PostgreSQL (Railway)

-- Tracks every Virtual Budtender conversation session
CREATE TABLE budtender_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id VARCHAR(50) NOT NULL,           -- 'ch', 'pureoasis', etc.
  operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  session_token VARCHAR(255) NOT NULL,      -- anonymous session ID
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  message_count INTEGER DEFAULT 0,
  recommendation_count INTEGER DEFAULT 0,
  click_through_count INTEGER DEFAULT 0,    -- how many product links clicked
  device_type VARCHAR(20),                  -- mobile/desktop/tablet
  referrer TEXT,                            -- where the user came from
  metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_bsessions_tenant ON budtender_sessions(tenant_id);
CREATE INDEX idx_bsessions_operator ON budtender_sessions(operator_id);
CREATE INDEX idx_bsessions_started ON budtender_sessions(started_at);

-- Tracks individual queries within sessions (demand signals)
CREATE TABLE budtender_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES budtender_sessions(id) ON DELETE CASCADE,
  tenant_id VARCHAR(50) NOT NULL,
  query_text TEXT NOT NULL,                 -- what the customer typed
  parsed_intent JSONB,                      -- { goal, experience, format, budget }
  products_recommended UUID[],              -- array of GLASS product IDs recommended
  products_clicked UUID[],                  -- products the customer clicked on
  response_time_ms INTEGER,                 -- how long the LLM took
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bqueries_session ON budtender_queries(session_id);
CREATE INDEX idx_bqueries_tenant ON budtender_queries(tenant_id);
CREATE INDEX idx_bqueries_created ON budtender_queries(created_at);

-- Aggregated demand signals (nightly batch from budtender_queries)
CREATE TABLE demand_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operator_id UUID REFERENCES operators(id) ON DELETE CASCADE,
  category VARCHAR(50) NOT NULL,            -- flower, edible, vape, etc.
  goal VARCHAR(50),                         -- sleep, relax, social, etc.
  experience_level VARCHAR(20),             -- new, casual, heavy
  budget_range VARCHAR(20),                 -- <25, 25-50, 50+
  query_count INTEGER NOT NULL DEFAULT 0,   -- how many times this combo was asked
  conversion_count INTEGER DEFAULT 0,       -- how many led to clicks
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_demand_operator ON demand_signals(operator_id);
CREATE INDEX idx_demand_category ON demand_signals(category);
CREATE INDEX idx_demand_period ON demand_signals(period_start);

-- Cross-product event stream for analytics
CREATE TABLE ecosystem_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_product VARCHAR(20) NOT NULL,      -- 'glass', 'budtender', 'cue', 'delivery'
  event_type VARCHAR(50) NOT NULL,          -- 'mission_completed', 'recommendation_clicked', etc.
  operator_id UUID REFERENCES operators(id) ON DELETE SET NULL,
  participant_id VARCHAR(255),              -- external user ID from the source system
  payload JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_events_source ON ecosystem_events(source_product);
CREATE INDEX idx_events_type ON ecosystem_events(event_type);
CREATE INDEX idx_events_operator ON ecosystem_events(operator_id);
CREATE INDEX idx_events_created ON ecosystem_events(created_at);
```

### 1.5 New GLASS API Endpoints for Integration

Add to `services/api/src/routes/`:

```
# New route files needed:
services/api/src/routes/ecosystem.ts     # Cross-product event ingestion
services/api/src/routes/budtender-api.ts # Product feed for VB widget
services/api/src/routes/demand.ts        # Demand signal reads/writes
```

**Public endpoints (API key auth, not Clerk):**

| Method | Path | Purpose | Consumer |
|--------|------|---------|----------|
| `GET` | `/api/v1/catalog/:operatorId/products` | Live product catalog for an operator | Virtual Budtender |
| `GET` | `/api/v1/catalog/:operatorId/products?category=flower&inStock=true` | Filtered catalog | Virtual Budtender |
| `POST` | `/api/v1/ecosystem/events` | Ingest events from any product | Cue, VB, Delivery |
| `POST` | `/api/v1/budtender/sessions` | Create/update VB session | Virtual Budtender |
| `POST` | `/api/v1/budtender/queries` | Log VB query + products recommended | Virtual Budtender |
| `GET` | `/api/v1/demand/:operatorId` | Aggregated demand signals | Cue (mission targeting) |
| `GET` | `/api/v1/catalog/:operatorId/underperforming` | Products with low velocity or high competitor gap | Cue (mission targeting) |

**Auth for integration endpoints:** API key based (`X-Roviq-API-Key` header). Each product gets its own key. Rate limited to 1000 req/min per key. No Clerk auth required — these are service-to-service calls.

```typescript
// services/api/src/plugins/api-key-auth.ts
import type { FastifyInstance, FastifyRequest } from 'fastify';

const INTEGRATION_KEYS: Record<string, string> = {
  // Set via env vars, not hardcoded
  [process.env.VB_API_KEY!]: 'virtual-budtender',
  [process.env.CUE_API_KEY!]: 'cue',
  [process.env.DELIVERY_API_KEY!]: 'delivery',
};

export async function apiKeyAuth(fastify: FastifyInstance) {
  fastify.decorate('authenticateApiKey', async (request: FastifyRequest) => {
    const apiKey = request.headers['x-roviq-api-key'] as string;
    if (!apiKey || !INTEGRATION_KEYS[apiKey]) {
      throw fastify.httpErrors.unauthorized('Invalid API key');
    }
    request.apiKeyProduct = INTEGRATION_KEYS[apiKey];
  });
}
```

---

## Part 2: Integration Points

### 2.1 GLASS → Virtual Budtender

**Current state:** VB reads from Firestore. Products imported via manual CSV upload (`npm run import-ch`). Stale within days of import.

**Target state:** VB reads directly from GLASS API. Products are always fresh (scraped daily). Firestore eliminated entirely.

#### What Changes in Virtual Budtender

**`backend/server.js` — Replace Firestore with GLASS API calls:**

```javascript
// OLD: Firestore query
const snapshot = await db.collection('products')
  .where('tenantId', '==', tenantId)
  .get();

// NEW: GLASS API call
const GLASS_API = process.env.GLASS_API_URL || 'https://glass-api-production.up.railway.app';
const GLASS_KEY = process.env.GLASS_API_KEY;

async function getProductsForTenant(tenantId) {
  // Map tenantId to GLASS operator_id
  const operatorId = TENANT_TO_OPERATOR[tenantId];
  if (!operatorId) throw new Error(`No GLASS operator mapped for tenant: ${tenantId}`);
  
  const response = await fetch(
    `${GLASS_API}/api/v1/catalog/${operatorId}/products?inStock=true&limit=500`,
    { headers: { 'X-Roviq-API-Key': GLASS_KEY } }
  );
  
  if (!response.ok) throw new Error(`GLASS API error: ${response.status}`);
  const data = await response.json();
  
  // Transform GLASS product format to VB format
  return data.items.map(glassProduct => ({
    id: glassProduct.id,
    tenantId,
    name: glassProduct.name,
    brand: glassProduct.brand,
    category: mapGlassCategory(glassProduct.category),
    isCannabis: true,
    isAvailableOnline: glassProduct.latest_availability === 'in_stock',
    inStock: glassProduct.latest_availability === 'in_stock' ? 1 : 0,
    price: parseFloat(glassProduct.latest_price),
    strain: glassProduct.strain_type,
    thcPercent: glassProduct.thc_percent ? parseFloat(glassProduct.thc_percent) : null,
    cbdPercent: glassProduct.cbd_percent ? parseFloat(glassProduct.cbd_percent) : null,
    imageUrl: glassProduct.metadata?.image_url || null,
    dutchieUrl: glassProduct.metadata?.dutchie_url || null,
    tags: []
  }));
}

// Map GLASS categories to VB categories
function mapGlassCategory(glassCategory) {
  const map = {
    'flower': 'flower',
    'pre-roll': 'Pre-Rolls',
    'preroll': 'Pre-Rolls',
    'vape': 'Cartridge',
    'edible': 'Edibles',
    'concentrate': 'Concentrate',
    'tincture': 'Tincture',
    'topical': 'Topical',
  };
  return map[glassCategory?.toLowerCase()] || glassCategory;
}
```

**`backend/tenantConfig.js` — Add operator mapping:**

```javascript
export const tenantConfigs = {
  ch: {
    name: 'Cannabis Healing',
    displayName: 'Flight Club',
    glassOperatorId: null, // TO BE SET: CH's operator UUID in GLASS DB
    // ... rest of existing config
  },
};
```

#### New GLASS API Endpoint: Catalog Feed

```typescript
// services/api/src/routes/budtender-api.ts
import type { FastifyInstance } from 'fastify';
import { Type } from '@sinclair/typebox';
import { db, schema } from '../db/index.js';
import { eq, and, sql, desc, isNotNull } from 'drizzle-orm';

export default async function budtenderApiRoutes(fastify: FastifyInstance) {
  
  // GET /api/v1/catalog/:operatorId/products
  // Returns products with their latest price for a specific operator
  fastify.get('/catalog/:operatorId/products', {
    onRequest: [fastify.authenticateApiKey],
    schema: {
      params: Type.Object({
        operatorId: Type.String({ format: 'uuid' }),
      }),
      querystring: Type.Partial(Type.Object({
        category: Type.String(),
        inStock: Type.Boolean(),
        limit: Type.Integer({ minimum: 1, maximum: 500 }),
      })),
    },
  }, async (request, reply) => {
    const { operatorId } = request.params as { operatorId: string };
    const query = request.query as Record<string, unknown>;
    const limit = (query.limit as number) || 300;

    // Get products with their latest price for this operator
    // Uses a lateral join to get the most recent price per product
    const results = await db.execute(sql`
      SELECT 
        p.id,
        p.sku,
        p.name,
        p.brand,
        p.category,
        p.quantity,
        p.unit,
        p.weight_grams,
        p.strain_type,
        p.subcategory,
        p.description,
        p.thc_percent,
        p.cbd_percent,
        lp.price AS latest_price,
        lp.price_per_gram AS latest_price_per_gram,
        lp.availability AS latest_availability,
        lp.promo_flag,
        lp.scraped_at AS last_seen_at,
        lp.raw_data AS metadata
      FROM products p
      INNER JOIN LATERAL (
        SELECT price, price_per_gram, availability, promo_flag, scraped_at, raw_data
        FROM prices
        WHERE prices.product_id = p.id
          AND prices.operator_id = ${operatorId}
        ORDER BY scraped_at DESC
        LIMIT 1
      ) lp ON true
      WHERE 1=1
        ${query.category ? sql`AND p.category = ${query.category}` : sql``}
        ${query.inStock ? sql`AND lp.availability IN ('in_stock', 'low_stock')` : sql``}
      ORDER BY p.name
      LIMIT ${limit}
    `);

    return reply.send({
      operator_id: operatorId,
      count: results.rows.length,
      items: results.rows,
    });
  });

  // GET /api/v1/catalog/:operatorId/underperforming
  // Products that are overpriced vs competitors or have low velocity
  fastify.get('/catalog/:operatorId/underperforming', {
    onRequest: [fastify.authenticateApiKey],
    schema: {
      params: Type.Object({
        operatorId: Type.String({ format: 'uuid' }),
      }),
    },
  }, async (request, reply) => {
    const { operatorId } = request.params as { operatorId: string };

    // Find products where this operator's price is >15% above market median
    const results = await db.execute(sql`
      WITH operator_prices AS (
        SELECT DISTINCT ON (product_id)
          product_id, price, scraped_at
        FROM prices
        WHERE operator_id = ${operatorId}
        ORDER BY product_id, scraped_at DESC
      ),
      market_medians AS (
        SELECT 
          product_id,
          PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
          COUNT(DISTINCT operator_id) AS store_count
        FROM prices
        WHERE scraped_at > NOW() - INTERVAL '7 days'
        GROUP BY product_id
        HAVING COUNT(DISTINCT operator_id) >= 3
      )
      SELECT 
        p.id,
        p.name,
        p.brand,
        p.category,
        op.price AS your_price,
        mm.median_price AS market_median,
        ROUND(((op.price - mm.median_price) / mm.median_price * 100)::numeric, 1) AS premium_pct,
        mm.store_count
      FROM operator_prices op
      JOIN market_medians mm ON mm.product_id = op.product_id
      JOIN products p ON p.id = op.product_id
      WHERE op.price > mm.median_price * 1.15
      ORDER BY ((op.price - mm.median_price) / mm.median_price) DESC
      LIMIT 50
    `);

    return reply.send({
      operator_id: operatorId,
      count: results.rows.length,
      items: results.rows,
    });
  });
}
```

#### VB → GLASS: Query Logging (Demand Signals)

After each VB `/chat` or `/recommend` call, the VB backend fires an async POST to GLASS:

```javascript
// backend/glassClient.js — new file in virtual-budtender repo
const GLASS_API = process.env.GLASS_API_URL;
const GLASS_KEY = process.env.GLASS_API_KEY;

export async function logBudtenderQuery(sessionId, tenantId, queryData) {
  if (!GLASS_API) return; // graceful no-op if GLASS not configured
  
  try {
    await fetch(`${GLASS_API}/api/v1/budtender/queries`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Roviq-API-Key': GLASS_KEY,
      },
      body: JSON.stringify({
        session_id: sessionId,
        tenant_id: tenantId,
        query_text: queryData.message,
        parsed_intent: queryData.answers || null,
        products_recommended: queryData.recommendedProductIds || [],
        response_time_ms: queryData.responseTimeMs,
      }),
    });
  } catch (err) {
    console.warn('Failed to log query to GLASS (non-blocking):', err.message);
  }
}

export async function logBudtenderSession(tenantId, sessionToken, metadata) {
  if (!GLASS_API) return;
  
  try {
    const resp = await fetch(`${GLASS_API}/api/v1/budtender/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Roviq-API-Key': GLASS_KEY,
      },
      body: JSON.stringify({
        tenant_id: tenantId,
        session_token: sessionToken,
        ...metadata,
      }),
    });
    const data = await resp.json();
    return data.id; // GLASS session UUID
  } catch (err) {
    console.warn('Failed to create GLASS session (non-blocking):', err.message);
    return null;
  }
}
```

### 2.2 GLASS → Cue

**Integration purpose:** GLASS market intelligence drives Cue mission creation. Cue can see which products need promotion (overpriced, underperforming, new), and mission results feed back into GLASS as ecosystem events.

#### GLASS Data Informs Mission Creation

The Cue admin dashboard pulls from GLASS to suggest missions:

```
GET /api/v1/catalog/:operatorId/underperforming
→ "These 12 products are priced 15%+ above market. Create missions to push volume."

GET /api/v1/demand/:operatorId
→ "Customers asked for edibles 3x more than you have in stock. Create edible-focused missions."

GET /api/v1/catalog/:operatorId/products?category=flower&inStock=true
→ Full product list for mission target selection
```

#### Cue Admin Dashboard — "Smart Mission Suggestions"

New component in Cue admin (`admin/src/components/MissionSuggestions.tsx`):

```typescript
interface MissionSuggestion {
  type: 'overpriced' | 'low_demand' | 'new_product' | 'competitor_threat';
  product: GlassProduct;
  reason: string;
  suggested_mission: {
    type: 'commission' | 'tiered' | 'competition';
    target_units: number;
    reward_amount: number;
  };
}

// Fetch suggestions from GLASS
async function getMissionSuggestions(operatorId: string): Promise<MissionSuggestion[]> {
  const [underperforming, demand] = await Promise.all([
    glassClient.get(`/catalog/${operatorId}/underperforming`),
    glassClient.get(`/demand/${operatorId}`),
  ]);
  
  return underperforming.items.map(product => ({
    type: 'overpriced',
    product,
    reason: `${product.name} is ${product.premium_pct}% above market. Push volume to justify premium or reduce price.`,
    suggested_mission: {
      type: 'commission',
      target_units: 20,
      reward_amount: Math.round(product.your_price * 0.05), // 5% commission
    },
  }));
}
```

#### Cue → GLASS: Mission Performance Events

When a Cue mission completes or a submission is approved:

```typescript
// Cue backend: server/src/services/glassIntegration.ts
import { glassClient } from '../lib/glass-client';

export async function reportMissionEvent(event: {
  type: 'mission_created' | 'submission_approved' | 'mission_completed' | 'reward_redeemed';
  missionId: string;
  participantId: string;
  operatorId: string;       // GLASS operator UUID
  productId?: string;       // GLASS product UUID
  amount?: number;
  metadata?: Record<string, any>;
}) {
  await glassClient.post('/ecosystem/events', {
    source_product: 'cue',
    event_type: event.type,
    operator_id: event.operatorId,
    participant_id: event.participantId,
    payload: {
      mission_id: event.missionId,
      product_id: event.productId,
      amount: event.amount,
      ...event.metadata,
    },
  });
}
```

**GLASS can then visualize:**
- Total brand spend through Cue per operator
- Missions that moved product velocity
- Budtender performance correlated with GLASS pricing data
- ROI of incentive programs vs market position changes

### 2.3 Virtual Budtender → Cue

**Integration purpose:** Budtender widget interactions can count as Cue missions. Demand signals from VB inform which products Cue should incentivize.

#### "Recommendation missions" — Widget Usage as Mission Proof

A dispensary could create a Cue mission: "Recommend 10 products via the virtual budtender → $15 bonus"

**How this works:**
1. VB widget logs `products_recommended` per session to GLASS
2. If the budtender's employee ID is attached to the session (kiosk mode or logged-in staff session), the recommendation counts
3. Cue queries GLASS `budtender_queries` to verify recommendations
4. No self-reporting needed — the data is objective

```typescript
// Cue backend: verifyBudtenderMission
async function verifyBudtenderRecommendationMission(
  participantId: string,
  missionId: string,
  startDate: Date,
  endDate: Date,
): Promise<{ count: number; verified: boolean }> {
  // Query GLASS for recommendation count
  const response = await glassClient.get('/budtender/queries', {
    params: {
      participant_id: participantId, // mapped to VB session
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      has_recommendations: true,
    },
  });
  
  return {
    count: response.total,
    verified: true, // GLASS data is objective, no manual verification needed
  };
}
```

#### Shared Product Catalog

Both VB and Cue reference GLASS products by UUID. No separate product tables needed in either system.

- **VB** reads products via `GET /api/v1/catalog/:operatorId/products`
- **Cue** references products in missions via GLASS product UUID
- Product details are always fetched from GLASS (single source of truth)

**Cue schema change:** The existing `products` table in Cue becomes a reference table that stores GLASS product UUIDs + any Cue-specific metadata (like mission association counts):

```sql
-- Cue Neon PostgreSQL: modify products table
ALTER TABLE products ADD COLUMN glass_product_id VARCHAR(36);
ALTER TABLE products ADD COLUMN glass_operator_id VARCHAR(36);
-- Keep existing product data as fallback for brands not in GLASS
```

### 2.4 Virtual Budtender → GLASS

**Integration purpose:** VB is a demand sensing instrument. What customers ask for = what the market wants. This data doesn't exist anywhere else.

#### Demand Signal Pipeline

```
Customer asks VB: "What edibles do you have under $30?"
                         │
                         ▼
VB logs to GLASS:  { category: "edible", budget: "<30", goal: null }
                         │
                         ▼
Nightly batch aggregates: "CH saw 47 edible queries this week, 
                           32 were budget-constrained under $30"
                         │
                         ▼
GLASS demand_signals:    operator_id=CH, category=edible, 
                         budget_range=<30, query_count=47
                         │
                         ▼
GLASS Dashboard:         New "Demand Intelligence" widget showing 
                         what customers want vs what you stock
                         │
                         ▼
Cue Integration:         "Create mission: push $25 edibles because 
                          68% of queries are budget-constrained"
```

#### Conversion Tracking

When VB recommends a product and the user clicks the Dutchie link:

```javascript
// VB frontend: ProductCard.jsx — add click tracking
const handleProductClick = (product, sessionId) => {
  // Track click before redirect
  fetch(`${API_URL}/track-click`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      product_id: product.id,
      tenant_id: tenantId,
    }),
  }).catch(() => {}); // fire and forget
  
  // Open Dutchie link
  window.open(product.dutchieUrl, '_blank');
};
```

This gives GLASS a `recommendation → click` conversion rate per product, per operator. True purchase conversion requires Dutchie checkout integration (future), but click-through is valuable on its own.

### 2.5 Cue → GLASS

Already covered in 2.2 (ecosystem events). Key data flows:

| Event | GLASS Use |
|-------|-----------|
| `mission_created` | Track brand investment per operator |
| `submission_approved` | Product velocity signals (budtender actually sold it) |
| `mission_completed` | Success metrics for incentive programs |
| `reward_redeemed` | Cost tracking for ROI calculations |
| `course_completed` | Training engagement metrics |
| `participant_joined` | Network growth metrics |

**GLASS Dashboard — "Ecosystem" tab:**
- Brand spend heatmap (which brands invest in which stores)
- Mission ROI chart (cost of mission vs sales lift)
- Budtender engagement scores
- Product push effectiveness (did incentivized products actually move?)

### 2.6 Cue → Delivery

**Integration purpose:** CH wants driver incentives. Cue's mission + gift card infrastructure handles this perfectly. Delivery is the use case, Cue is the platform.

#### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Delivery    │     │    Cue       │     │  Tremendous  │
│  Operations  │────▶│  Platform    │────▶│  API         │
│  (Blaze POS) │     │              │     │  (Gift Cards)│
│              │     │  • Driver    │     │              │
│  • Orders    │     │    missions  │     │  • Visa      │
│  • Routes    │     │  • Rating    │     │  • Amazon    │
│  • Manifests │     │    tracking  │     │  • DoorDash  │
│              │     │  • Photo     │     │              │
│              │     │    proof     │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

**Data flow:**
1. Driver completes deliveries (tracked in Blaze POS or manually reported)
2. Driver submits proof in Cue mobile app (screenshot of delivery count, photo of rating)
3. Cue admin (or automated rules) approves submission
4. Gift card issued via Tremendous API
5. Event logged to GLASS for analytics

Detailed spec in [Part 7](#part-7-ch-driver-program--detailed-spec).

---

## Part 3: Unified Database Strategy

### 3.1 Recommendation: Hub-and-Spoke (NOT Full Merge)

**Do NOT merge all databases into one.** Here's why:

| Approach | Pros | Cons |
|----------|------|------|
| **Full merge** (everything in Railway PG) | Single query across all data | Schema conflicts, migration hell, Cue's 19 tables + GLASS's 15+ tables = unmaintainable monolith. Coupling. Railway single point of failure. |
| **Full separation** (current state) | Independence | No data sharing. Duplicate products. Stale VB data. No ecosystem analytics. |
| **Hub-and-spoke** ✅ | Shared product/pricing truth via API. Domain isolation. Independent deploy. Gradual migration path. | Requires API key management. Slightly higher latency for cross-product queries. |

### 3.2 What Goes Where

| Database | Owns | Reads From |
|----------|------|------------|
| **GLASS PostgreSQL (Railway)** | Products, Prices, Operators, CCC data, Threats, Recommendations, Alerts, Margin Rules, Waitlist, Demand Signals, Ecosystem Events, Budtender Sessions/Queries | Scrapers (write), VB (write sessions), Cue (write events) |
| **Cue PostgreSQL (Neon)** | Users/Participants, Brands, Dispensaries, Missions, Submissions, Rewards, Redemptions, Courses, Certifications, Fraud Checks, Audit Logs | GLASS API (product catalog, underperforming products, demand signals) |
| **Virtual Budtender** | Nothing (stateless!) | GLASS API (product catalog). Firebase Firestore **ELIMINATED**. |
| **Delivery** | Nothing of its own (Blaze POS owns order data) | Cue (driver missions). GLASS API (product catalog for driver training). |

### 3.3 Firestore Elimination Plan

Firebase Firestore currently stores ~300 CH products and nothing else. It's the weakest link:

1. **Week 1:** Add GLASS catalog API endpoint (`/api/v1/catalog/:operatorId/products`)
2. **Week 1:** Map CH's `tenantId: "ch"` to a GLASS operator UUID
3. **Week 1:** Ensure CH products exist in GLASS DB (they already do from Dutchie scraping if CH uses Dutchie)
4. **Week 2:** Switch VB backend to call GLASS API instead of Firestore
5. **Week 2:** Test with CH — verify product count, pricing, categories match
6. **Week 3:** Remove Firebase dependencies from VB backend entirely
7. **Week 3:** Cancel Firebase project (or keep for Cue auth only)

**Risk:** If CH has products NOT on Dutchie (e.g., CBD products, accessories), they won't be in GLASS. Mitigation: GLASS gets a manual product upload endpoint for non-scraped items.

```typescript
// New GLASS endpoint for manual product additions
// POST /api/v1/catalog/:operatorId/products (API key auth)
// Used by dispensaries to add products not on Dutchie/Weedmaps
```

### 3.4 Cue ↔ GLASS Product Sync Strategy

Cue has its own `products` table (for brand-uploaded products that might not be on menus yet). The sync:

1. **Cue product creation:** When a brand adds a product in Cue, check if it exists in GLASS by SKU/name. If yes, store `glass_product_id`. If no, create it in GLASS via API.
2. **Mission targets:** Always reference GLASS product UUIDs. Cue's `missions` table gets a `glass_product_ids UUID[]` column.
3. **Submission verification:** When a budtender claims a sale, the product they sold is validated against GLASS's catalog for that operator.

---

## Part 4: Cue Expansion — Beyond Budtenders

### 4.1 The Participant Type System

**Current Cue schema:** The `users` and `budtenders` tables assume all participants are budtenders. This needs to generalize.

#### New Schema: `participants` Table (Replaces `budtenders`)

```sql
-- Cue Neon PostgreSQL: New participants table

CREATE TYPE participant_type AS ENUM (
  'budtender',
  'delivery_driver',
  'brand_ambassador',
  'customer'
);

CREATE TABLE participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  dispensary_id UUID REFERENCES dispensaries(id) ON DELETE SET NULL,
  
  -- Type and role
  type participant_type NOT NULL DEFAULT 'budtender',
  display_name VARCHAR(255),
  avatar_url TEXT,
  
  -- Work context (varies by type)
  employer_name VARCHAR(255),           -- dispensary name or delivery company
  employee_id VARCHAR(100),             -- internal employee ID
  position VARCHAR(100),                -- "Lead Budtender", "Driver", etc.
  
  -- Verification
  verified BOOLEAN DEFAULT FALSE,
  verified_at TIMESTAMPTZ,
  verified_by UUID,                     -- admin who verified
  
  -- Stats (denormalized for leaderboard performance)
  total_earnings DECIMAL(10, 2) DEFAULT 0,
  total_missions_completed INTEGER DEFAULT 0,
  total_submissions INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,     -- consecutive active days
  
  -- Type-specific metadata
  metadata JSONB DEFAULT '{}',
  -- For drivers: { vehicle_type, license_plate, delivery_zone }
  -- For brand_ambassadors: { brand_ids, territories }
  -- For customers: { loyalty_tier, total_spend }
  
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_participants_user ON participants(user_id);
CREATE INDEX idx_participants_type ON participants(type);
CREATE INDEX idx_participants_dispensary ON participants(dispensary_id);
CREATE INDEX idx_participants_status ON participants(status);
CREATE UNIQUE INDEX idx_participants_user_type ON participants(user_id, type);
-- A user can have multiple participant types (e.g., budtender AND delivery driver)
```

#### Mission System Generalization

The `missions` table needs a `participant_types` filter:

```sql
-- Add to existing missions table
ALTER TABLE missions ADD COLUMN eligible_participant_types participant_type[] 
  DEFAULT ARRAY['budtender']::participant_type[];

-- A mission can target multiple types:
-- { eligible_participant_types: ['budtender', 'delivery_driver'] }
-- means both budtenders and drivers can participate
```

#### New Mission Types for Drivers

```sql
CREATE TYPE driver_mission_type AS ENUM (
  'delivery_count',        -- Complete X deliveries
  'rating_threshold',      -- Maintain X+ rating
  'upsell_commission',     -- Recommend products during delivery
  'on_time_bonus',         -- X% on-time delivery rate
  'zone_coverage',         -- Complete deliveries in specific zones
  'customer_feedback'      -- Get X 5-star reviews
);

-- These map to the existing mission_type enum with new values
ALTER TYPE mission_type ADD VALUE 'delivery_count';
ALTER TYPE mission_type ADD VALUE 'rating_threshold';
ALTER TYPE mission_type ADD VALUE 'upsell_commission';
ALTER TYPE mission_type ADD VALUE 'on_time_bonus';
```

#### Mission Assignment Changes

```sql
-- mission_assignments: change budtender_id to participant_id
ALTER TABLE mission_assignments RENAME COLUMN budtender_id TO participant_id;
ALTER TABLE mission_assignments ADD CONSTRAINT fk_participant 
  FOREIGN KEY (participant_id) REFERENCES participants(id);

-- sales_submissions: similarly
ALTER TABLE sales_submissions RENAME COLUMN budtender_id TO participant_id;
ALTER TABLE sales_submissions ADD CONSTRAINT fk_participant
  FOREIGN KEY (participant_id) REFERENCES participants(id);
```

### 4.2 Participant Type Details

#### Budtenders (Current — No Changes)
- Phone OTP login
- Mission feed: sell products, complete training
- Photo proof of sales receipt
- Earnings wallet + gift card redemption

#### Delivery Drivers (NEW — CH Priority)
- Phone OTP login (same auth flow)
- Mission feed: delivery count, ratings, upsells
- Proof: screenshot of delivery app stats, or manual count entry + admin approval
- Earnings wallet + gift card redemption (Tremendous)
- **No POS integration required** — manual reporting with admin verification

#### Brand Ambassadors (FUTURE)
- Login via brand admin invite
- Mission feed: event attendance, store visits, training completion
- Proof: photo of event/display, GPS check-in
- Earnings wallet + gift card or direct deposit

#### Customer Loyalty (FUTURE)
- No auth required for basic tier (email/phone capture)
- Mission feed: purchase frequency, referrals, reviews
- Proof: receipt upload, referral code tracking
- Rewards: store credit, discounts, gift cards
- **This is the highest-volume use case** — requires separate optimization pass

### 4.3 Leaderboard Generalization

Current leaderboards are budtender-only. Generalize:

```typescript
// Cue API: GET /api/leaderboard?type=budtender&dispensary_id=X
// Cue API: GET /api/leaderboard?type=delivery_driver&dispensary_id=X
// Cue API: GET /api/leaderboard?type=all&dispensary_id=X (combined)

interface LeaderboardEntry {
  participant_id: string;
  participant_type: ParticipantType;
  display_name: string;
  avatar_url: string | null;
  total_earnings: number;
  missions_completed: number;
  rank: number;
  streak: number;
}
```

---

## Part 5: Unified Auth

### 5.1 Current Auth Landscape

| Product | Auth System | Users |
|---------|-------------|-------|
| GLASS | Clerk (JWT, email/password) | Dispensary operators, admins |
| Cue | Firebase Phone Auth (OTP) | Budtenders (mobile), Brand admins (dashboard) |
| Virtual Budtender | None | Anonymous customers |
| Delivery | TBD | Customers, drivers |

### 5.2 Recommendation: Clerk as Primary, Firebase as Secondary

**Don't rip out Firebase Phone Auth from Cue.** It works, and phone OTP is the right auth for budtenders/drivers on mobile. Instead:

#### Admin Auth: Clerk (Single Login)

Dispensary admins and brand admins get **one Clerk account** that works across:
- GLASS dashboard (already Clerk)
- Cue admin dashboard (currently Firebase — switch to Clerk)
- Virtual Budtender config panel (new — needs Clerk)

**Implementation:**

```typescript
// Cue admin dashboard: Replace Firebase auth with Clerk
// admin/src/lib/auth.ts

// OLD:
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

// NEW:
import { ClerkProvider, SignIn, useUser } from '@clerk/clerk-react';

// Cue backend: Accept both Clerk JWT (admin) and Firebase JWT (mobile)
// server/src/middleware/auth.ts
async function authenticate(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'No token' });
  
  try {
    // Try Clerk JWT first (admin dashboard)
    const clerkPayload = await verifyClerkJWT(token);
    req.user = {
      id: clerkPayload.sub,
      source: 'clerk',
      role: clerkPayload.metadata?.cue_role || 'admin',
    };
    return next();
  } catch {
    // Fall back to Firebase JWT (mobile app)
    try {
      const firebasePayload = await verifyFirebaseToken(token);
      req.user = {
        id: firebasePayload.uid,
        source: 'firebase',
        role: 'participant',
      };
      return next();
    } catch {
      return res.status(401).json({ error: 'Invalid token' });
    }
  }
}
```

#### Mobile Auth: Keep Firebase Phone Auth

Budtenders and drivers use phone OTP via Firebase. No change needed. This is the right UX for mobile-first, blue-collar workers who don't have/want email accounts for a work app.

#### Clerk ↔ Cue User Mapping

New table in Cue:

```sql
CREATE TABLE admin_auth_mappings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_user_id VARCHAR(255) NOT NULL UNIQUE,
  cue_user_id UUID NOT NULL REFERENCES users(id),
  glass_user_id UUID,                       -- their GLASS user ID if they have one
  role VARCHAR(50) NOT NULL,                 -- 'platform_admin', 'brand_admin', 'dispensary_admin'
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### Virtual Budtender: No Auth Change

The widget stays public for customers. For **dispensary staff kiosk mode** (where recommendations count toward Cue missions), add an optional staff login button:

```jsx
// VB widget: Optional staff identification (not full auth)
{staffMode && (
  <input 
    type="text" 
    placeholder="Staff ID (optional)" 
    onChange={(e) => setStaffId(e.target.value)}
  />
)}
```

### 5.3 Auth Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                     UNIFIED AUTH                           │
│                                                            │
│  ┌─────────────────┐                                       │
│  │   Clerk          │─── GLASS Dashboard (existing)        │
│  │   (Email/Pass)   │─── Cue Admin Dashboard (NEW)        │
│  │                   │─── VB Config Panel (NEW)            │
│  │   Admin accounts  │─── Delivery Admin (FUTURE)          │
│  └─────────────────┘                                       │
│                                                            │
│  ┌─────────────────┐                                       │
│  │  Firebase Phone  │─── Cue Mobile App (existing)         │
│  │  Auth (OTP)      │─── Delivery Driver App (FUTURE)      │
│  │                  │                                      │
│  │  Field workers   │                                      │
│  └─────────────────┘                                       │
│                                                            │
│  ┌─────────────────┐                                       │
│  │  Anonymous       │─── Virtual Budtender Widget          │
│  │  (Session only)  │─── Delivery Customer App (FUTURE)    │
│  └─────────────────┘                                       │
└────────────────────────────────────────────────────────────┘
```

---

## Part 6: Implementation Roadmap

### Phase 1: This Week (Feb 12-19) — Wire the Data

**Goal:** Get GLASS feeding live product data to Virtual Budtender. Eliminate Firestore dependency.

| # | Task | Repo | Effort | Depends On |
|---|------|------|--------|------------|
| 1.1 | Build GLASS catalog API endpoint (`/api/v1/catalog/:operatorId/products`) | `Roviq-AI/glass.git` → `services/api/src/routes/budtender-api.ts` | 4h | — |
| 1.2 | Build API key auth plugin for integration endpoints | `Roviq-AI/glass.git` → `services/api/src/plugins/api-key-auth.ts` | 2h | — |
| 1.3 | Find/create CH operator in GLASS DB, map to `tenantId: "ch"` | GLASS DB (SQL) | 30min | 1.1 |
| 1.4 | Switch VB backend from Firestore to GLASS API | `randytorres/virtual-budtender` → `backend/server.js`, new `backend/glassClient.js` | 4h | 1.1, 1.2, 1.3 |
| 1.5 | Test VB with GLASS data — verify product count, categories, prices match | Manual QA | 2h | 1.4 |
| 1.6 | Deploy updated GLASS API to Railway | Railway CLI | 1h | 1.1, 1.2 |
| 1.7 | Deploy updated VB backend | Existing VB deploy process | 1h | 1.4 |

**Total Phase 1 effort: ~14.5 hours**

**Deliverable:** Virtual Budtender pulls live product data from GLASS. No more manual CSV imports. Products update automatically when GLASS scrapers run nightly.

### Phase 2: Two Weeks (Feb 19 - Mar 5) — Core Integrations That Unlock Revenue

**Goal:** Launch CH driver program. Add VB query logging. Start Cue ↔ GLASS sync.

| # | Task | Repo | Effort | Depends On |
|---|------|------|--------|------------|
| 2.1 | Add `participants` table to Cue schema (replaces `budtenders`) | `randytorres/BudtenderIncentiveAI` → `server/db/schema.ts` | 6h | — |
| 2.2 | Add driver mission types to Cue | Cue → `server/src/missions/` | 8h | 2.1 |
| 2.3 | Build driver submission flow in Cue mobile app | Cue → `mobile/src/screens/` | 8h | 2.2 |
| 2.4 | Build CH driver program admin config | Cue → `admin/src/pages/` | 6h | 2.2 |
| 2.5 | Wire Tremendous API for driver gift cards (already built for budtenders) | Cue → verify existing integration works for new participant type | 2h | 2.1 |
| 2.6 | Add GLASS integration tables (`budtender_sessions`, `budtender_queries`, `demand_signals`, `ecosystem_events`) | GLASS DB migration | 3h | — |
| 2.7 | Build GLASS ecosystem event ingestion endpoint | `Roviq-AI/glass.git` → `services/api/src/routes/ecosystem.ts` | 4h | 2.6 |
| 2.8 | Add VB query logging (fire-and-forget to GLASS) | `randytorres/virtual-budtender` → `backend/glassClient.js` | 3h | 2.6, 2.7 |
| 2.9 | Add `glass_product_id` column to Cue products table | Cue DB migration | 1h | — |
| 2.10 | Build Cue → GLASS product sync (lookup by SKU/name) | Cue → `server/src/services/glassSync.ts` | 4h | 2.9, 1.1 |
| 2.11 | Deploy Cue MVP (first deploy ever) | Neon + Railway or Fly.io | 8h | 2.1-2.5 |
| 2.12 | Set up CH as first Cue customer (dispensary + driver accounts) | Cue admin | 2h | 2.11 |

**Total Phase 2 effort: ~55 hours (~2 developer-weeks)**

**Deliverables:**
- CH driver incentive program LIVE on Cue
- VB query data flowing into GLASS (demand signals)
- Cue products linked to GLASS catalog
- Cue deployed for the first time

### Phase 3: One Month (Mar 5 - Apr 5) — Full Ecosystem Flywheel

**Goal:** All four products connected. Smart mission suggestions. Demand intelligence visible in GLASS.

| # | Task | Repo | Effort | Depends On |
|---|------|------|--------|------------|
| 3.1 | Build GLASS "Demand Intelligence" dashboard widget | GLASS → `apps/web/src/components/DemandIntelligence.tsx` | 8h | 2.6, 2.8 |
| 3.2 | Build GLASS "Ecosystem" analytics tab | GLASS → `apps/web/src/pages/Ecosystem.tsx` | 12h | 2.7 |
| 3.3 | Build demand signal aggregation cron job | GLASS → `services/api/src/jobs/aggregate-demand.ts` | 4h | 2.6 |
| 3.4 | Build "Smart Mission Suggestions" in Cue admin | Cue → `admin/src/components/MissionSuggestions.tsx` | 8h | 1.1 (catalog endpoint) |
| 3.5 | Switch Cue admin auth from Firebase to Clerk | Cue → `admin/src/lib/auth.ts` + backend dual-auth middleware | 12h | — |
| 3.6 | Build VB config panel (Clerk-authed admin page) | New: `virtual-budtender/admin/` or integrated into GLASS | 16h | 3.5 |
| 3.7 | Add conversion tracking (click-through) to VB | VB → `backend/server.js` + GLASS API | 4h | 2.6 |
| 3.8 | Build underperforming products endpoint in GLASS | GLASS → `services/api/src/routes/budtender-api.ts` | 4h | — |
| 3.9 | Add second VB tenant (non-CH dispensary) | VB config + GLASS operator mapping | 4h | 1.4 |
| 3.10 | Build customer loyalty participant type (schema + basic missions) | Cue → schema migration + basic CRUD | 12h | 2.1 |
| 3.11 | Build Cue mission completion → GLASS event reporting | Cue → `server/src/services/glassIntegration.ts` | 4h | 2.7 |
| 3.12 | Delivery app wireframes + Blaze API integration research | Design + spike | 16h | — |

**Total Phase 3 effort: ~104 hours (~3 developer-weeks)**

**Deliverables:**
- GLASS shows demand intelligence from VB queries
- GLASS shows ecosystem analytics (Cue mission performance, brand spend)
- Cue admin suggests missions based on GLASS market data
- Unified Clerk auth for admin dashboards
- Second VB tenant proves multi-tenant works
- Customer loyalty framework in place

### Phase 4: Three Months (Apr 5 - Jul 5) — Scale and Optimize

| # | Task | Effort | Priority |
|---|------|--------|----------|
| 4.1 | Delivery customer app (React Native) with Blaze POS backend | 200h | High (if Delivered deal closes) |
| 4.2 | Driver app integration with Cue (automatic delivery tracking) | 40h | High |
| 4.3 | VB → Cue automatic mission verification (recommendation missions) | 20h | Medium |
| 4.4 | Brand Ambassador participant type + event missions | 30h | Medium |
| 4.5 | Full customer loyalty program with receipt scanning | 60h | Medium |
| 4.6 | GLASS ML pricing model (recommendations based on demand + competition) | 80h | Medium |
| 4.7 | GLASS → Newsletter automation (demand insights → content) | 20h | Low |
| 4.8 | Cue white-label for other states | 40h | Low (MA first) |
| 4.9 | Real-time pricing alerts (GLASS → Cue → mobile push) | 30h | Medium |
| 4.10 | A/B testing framework for VB recommendations | 20h | Low |

**The flywheel at scale:**
```
GLASS scrapes prices → informs Cue mission targeting
  → budtenders/drivers earn from missions
    → VB captures demand signals from customers
      → GLASS shows demand intelligence
        → operators adjust pricing
          → GLASS scrapes new prices → cycle repeats

Each product makes the others more valuable.
Competitors would need to build all four to replicate this.
```

---

## Part 7: CH Driver Program — Detailed Spec

### 7.1 Overview

Cannabis Healing wants to incentivize their delivery drivers. Drivers can't receive cannabis products as incentives (legal restriction). Cue's Tremendous API integration enables gift card payouts — solving the exact problem.

**Participant profile:**
- 3-8 delivery drivers
- Already use a delivery platform (likely Dutchie or internal) for dispatching
- No POS integration available for automated tracking
- Manual verification by CH admin (Brian) is acceptable for V1

### 7.2 Schema Changes Required

All changes in Cue Neon PostgreSQL:

```sql
-- 1. Add participant_type enum (if not already added from Part 4)
DO $$ BEGIN
  CREATE TYPE participant_type AS ENUM (
    'budtender', 'delivery_driver', 'brand_ambassador', 'customer'
  );
EXCEPTION
  WHEN duplicate_object THEN null;
END $$;

-- 2. Create participants table
CREATE TABLE participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  dispensary_id UUID REFERENCES dispensaries(id) ON DELETE SET NULL,
  type participant_type NOT NULL DEFAULT 'budtender',
  display_name VARCHAR(255),
  avatar_url TEXT,
  employer_name VARCHAR(255),
  employee_id VARCHAR(100),
  position VARCHAR(100),
  verified BOOLEAN DEFAULT FALSE,
  verified_at TIMESTAMPTZ,
  verified_by UUID,
  total_earnings DECIMAL(10, 2) DEFAULT 0,
  total_missions_completed INTEGER DEFAULT 0,
  total_submissions INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  metadata JSONB DEFAULT '{}',
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, type)
);

-- 3. Migrate existing budtender data
INSERT INTO participants (user_id, dispensary_id, type, display_name, total_earnings, 
  total_missions_completed, total_submissions, status, created_at)
SELECT user_id, dispensary_id, 'budtender', display_name, total_earnings,
  total_missions_completed, total_submissions, status, created_at
FROM budtenders;

-- 4. Add driver-specific mission types
-- (missions table already has a 'type' VARCHAR column)
-- New valid values: 'delivery_count', 'rating_threshold', 'upsell_commission'

-- 5. Add participant type filter to missions
ALTER TABLE missions ADD COLUMN eligible_participant_types TEXT[] 
  DEFAULT ARRAY['budtender'];

-- 6. Rename budtender_id → participant_id in related tables
ALTER TABLE mission_assignments RENAME COLUMN budtender_id TO participant_id;
ALTER TABLE sales_submissions RENAME COLUMN budtender_id TO participant_id;

-- 7. Driver delivery tracking table
CREATE TABLE delivery_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  participant_id UUID NOT NULL REFERENCES participants(id),
  mission_id UUID NOT NULL REFERENCES missions(id),
  
  -- Delivery metrics (manually reported)
  delivery_count INTEGER,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  average_rating DECIMAL(3, 2),          -- e.g., 4.85
  on_time_percentage DECIMAL(5, 2),      -- e.g., 95.50
  
  -- Proof
  proof_type VARCHAR(50) NOT NULL,        -- 'screenshot', 'photo', 'admin_verified'
  proof_image_url TEXT,                   -- Firebase Storage URL
  proof_notes TEXT,
  
  -- Verification
  status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, approved, rejected, disputed
  reviewed_by UUID,
  reviewed_at TIMESTAMPTZ,
  review_notes TEXT,
  
  -- Financials
  earned_amount DECIMAL(10, 2),
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_delivery_sub_participant ON delivery_submissions(participant_id);
CREATE INDEX idx_delivery_sub_mission ON delivery_submissions(mission_id);
CREATE INDEX idx_delivery_sub_status ON delivery_submissions(status);
CREATE INDEX idx_delivery_sub_period ON delivery_submissions(period_start, period_end);
```

### 7.3 Mission Types for Drivers

#### Type 1: Delivery Count Mission
```json
{
  "name": "Weekly Delivery Champion",
  "type": "delivery_count",
  "eligible_participant_types": ["delivery_driver"],
  "rules": {
    "target_deliveries": 20,
    "period": "weekly",
    "min_rating": 4.0,
    "reward_amount": 25.00,
    "reward_type": "gift_card"
  },
  "description": "Complete 20+ deliveries this week with a 4.0+ rating to earn a $25 gift card"
}
```

#### Type 2: Rating Threshold Mission
```json
{
  "name": "5-Star Driver",
  "type": "rating_threshold",
  "eligible_participant_types": ["delivery_driver"],
  "rules": {
    "min_rating": 4.5,
    "min_deliveries": 15,
    "period": "weekly",
    "reward_amount": 15.00,
    "reward_type": "gift_card"
  },
  "description": "Maintain 4.5+ rating with at least 15 deliveries to earn a $15 gift card"
}
```

#### Type 3: Upsell Commission
```json
{
  "name": "Pre-Roll Pusher",
  "type": "upsell_commission",
  "eligible_participant_types": ["delivery_driver"],
  "rules": {
    "target_product_category": "preroll",
    "commission_per_unit": 2.00,
    "max_payout": 50.00,
    "period": "weekly",
    "reward_type": "gift_card",
    "verification": "admin_manual"
  },
  "description": "Earn $2 for every pre-roll upsell during delivery (up to $50/week)"
}
```

#### Type 4: Top Driver Competition
```json
{
  "name": "Driver of the Month",
  "type": "competition",
  "eligible_participant_types": ["delivery_driver"],
  "rules": {
    "metric": "delivery_count",
    "period": "monthly",
    "prizes": [
      { "rank": 1, "amount": 100.00 },
      { "rank": 2, "amount": 50.00 },
      { "rank": 3, "amount": 25.00 }
    ],
    "reward_type": "gift_card",
    "min_rating": 4.0
  },
  "description": "Top 3 drivers by delivery count earn $100/$50/$25 gift cards"
}
```

### 7.4 Driver Submission Flow

Since there's no POS integration, drivers submit proof manually:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Driver       │     │  Cue Mobile  │     │  CH Admin    │     │  Tremendous  │
│  completes    │────▶│  App         │────▶│  reviews     │────▶│  sends gift  │
│  deliveries   │     │              │     │  submission  │     │  card        │
│               │     │  • Opens app │     │              │     │              │
│  Weekly       │     │  • Taps      │     │  • Checks    │     │  • $25 Visa  │
│  or per-      │     │    mission   │     │    delivery  │     │  • $25 Amazon│
│  period       │     │  • Enters    │     │    count     │     │  • $25 Target│
│               │     │    delivery  │     │  • Verifies  │     │              │
│               │     │    count     │     │    rating    │     │  Driver gets │
│               │     │  • Uploads   │     │  • Approves  │     │  email with  │
│               │     │    screenshot│     │    or rejects│     │  gift card   │
│               │     │  • Submits   │     │              │     │  link        │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

#### Mobile App: Driver Submission Screen

```typescript
// Cue mobile: screens/DriverSubmissionScreen.tsx

interface DriverSubmissionForm {
  missionId: string;
  deliveryCount: number;
  periodStart: string;          // ISO date
  periodEnd: string;            // ISO date
  averageRating: number | null; // optional, depends on mission type
  proofType: 'screenshot' | 'photo';
  proofImageUri: string;        // camera/gallery photo
  notes: string;
}

// POST /api/submissions/delivery
const submitDeliveryProof = async (form: DriverSubmissionForm) => {
  // 1. Upload proof image to Firebase Storage
  const imageUrl = await uploadImage(form.proofImageUri);
  
  // 2. Submit to Cue backend
  const response = await api.post('/submissions/delivery', {
    mission_id: form.missionId,
    delivery_count: form.deliveryCount,
    period_start: form.periodStart,
    period_end: form.periodEnd,
    average_rating: form.averageRating,
    proof_type: form.proofType,
    proof_image_url: imageUrl,
    proof_notes: form.notes,
  });
  
  return response.data;
};
```

#### What Proof Looks Like

Drivers can submit:
1. **Screenshot of delivery app dashboard** showing delivery count and rating for the period
2. **Photo of delivery manifest** (if paper-based)
3. **Admin direct verification** — Brian (CH admin) can approve without photo proof if he tracks deliveries internally

### 7.5 Tracking Without POS Integration

**V1 (Manual):**
- Drivers self-report delivery count + rating
- Upload screenshot proof
- CH admin verifies against their internal records
- Fraud detection: velocity checks (same driver can't submit twice for same period), image dedup (existing Cue feature)

**V2 (Semi-automated, if CH uses Dutchie Delivery):**
- Dutchie has a delivery tracking dashboard
- Cue could potentially scrape delivery stats (same CamoFox approach as GLASS)
- Or CH admin exports weekly delivery stats CSV → bulk verification

**V3 (Automated, if Delivered partnership closes):**
- Blaze POS API provides delivery completion webhooks
- Cue subscribes to Blaze webhooks for real-time verification
- Zero manual intervention

### 7.6 Gift Card Payout Flow

This uses Cue's existing Tremendous integration (already built for budtenders):

```typescript
// Cue backend: services/tremendous.ts (existing, just verify it works)

async function issueGiftCard(participantId: string, amount: number, catalog: string) {
  // 1. Create Tremendous order
  const order = await tremendous.createOrder({
    payment: { funding_source_id: process.env.TREMENDOUS_FUNDING_SOURCE },
    rewards: [{
      value: { denomination: amount, currency_code: 'USD' },
      delivery: { method: 'EMAIL' },
      recipient: {
        email: await getParticipantEmail(participantId),
        name: await getParticipantName(participantId),
      },
      products: [catalog], // 'visa', 'amazon', 'target', etc.
    }],
  });
  
  // 2. Record in Cue DB
  await db.insert(redemptions).values({
    participant_id: participantId,
    amount,
    tremendous_order_id: order.id,
    status: 'issued',
  });
  
  // 3. Report to GLASS
  await reportEcosystemEvent({
    type: 'reward_redeemed',
    participant_id: participantId,
    amount,
    source: 'cue',
  });
  
  return order;
}
```

**Gift card options (via Tremendous catalog):**
- Visa prepaid card (most flexible)
- Amazon
- Target
- DoorDash
- Uber/Lyft (useful for drivers)
- Custom catalog set by CH admin

### 7.7 CH Driver Program — Launch Checklist

```
□ Cue deployed to production (Neon DB + Railway/Fly.io API)
□ participants table migration run
□ delivery_submissions table migration run
□ Driver mission types configured in Cue admin
□ CH dispensary created in Cue
□ 3-8 driver accounts created (phone numbers from Brian)
□ Driver onboarding: install Expo Go, walk through first submission
□ CH admin (Brian) trained on approval queue
□ Tremendous API switched from testflight to production
□ Funding source loaded ($500 initial for first month)
□ First missions created:
  □ Weekly Delivery Champion ($25/week)
  □ Driver of the Month ($100/$50/$25)
□ First driver submits test submission → Brian approves → gift card received
□ Go live announcement to all CH drivers
```

### 7.8 Cost Estimate for CH

| Item | Monthly Cost |
|------|-------------|
| 5 drivers × $25/week avg gift cards | $500 |
| Tremendous API fee (2.5% on gift cards) | $12.50 |
| Cue platform fee (waived for beta) | $0 |
| **Total CH cost** | **~$512/mo** |

**CH's ROI argument:** If driver incentives increase delivery count by even 10% (2 extra deliveries/driver/week), that's 40+ extra deliveries/month. At average $60 order value = $2,400 incremental revenue vs $512 incentive cost. **4.7x ROI.**

---

## Appendix A: Environment Variables Required

### GLASS API (add to Railway)
```
VB_API_KEY=<generate-uuid>
CUE_API_KEY=<generate-uuid>
DELIVERY_API_KEY=<generate-uuid>
```

### Virtual Budtender (add to .env)
```
GLASS_API_URL=https://glass-api-production.up.railway.app
GLASS_API_KEY=<VB_API_KEY from above>
```

### Cue (add to .env when deploying)
```
GLASS_API_URL=https://glass-api-production.up.railway.app
GLASS_API_KEY=<CUE_API_KEY from above>
CLERK_PUBLISHABLE_KEY=<from GLASS Clerk instance>
CLERK_SECRET_KEY=<from GLASS Clerk instance>
```

## Appendix B: Repository Change Summary

| Repo | Files to Add/Modify | Priority |
|------|---------------------|----------|
| `Roviq-AI/glass.git` | `services/api/src/routes/budtender-api.ts` (NEW) | Phase 1 |
| `Roviq-AI/glass.git` | `services/api/src/routes/ecosystem.ts` (NEW) | Phase 2 |
| `Roviq-AI/glass.git` | `services/api/src/routes/demand.ts` (NEW) | Phase 2 |
| `Roviq-AI/glass.git` | `services/api/src/plugins/api-key-auth.ts` (NEW) | Phase 1 |
| `Roviq-AI/glass.git` | `services/api/src/db/schema.ts` (ADD 4 tables) | Phase 2 |
| `Roviq-AI/glass.git` | Migration SQL for new tables | Phase 2 |
| `randytorres/virtual-budtender` | `backend/glassClient.js` (NEW) | Phase 1 |
| `randytorres/virtual-budtender` | `backend/server.js` (MODIFY — replace Firestore) | Phase 1 |
| `randytorres/virtual-budtender` | `backend/tenantConfig.js` (ADD glassOperatorId) | Phase 1 |
| `randytorres/BudtenderIncentiveAI` | `server/db/schema.ts` (ADD participants, delivery_submissions) | Phase 2 |
| `randytorres/BudtenderIncentiveAI` | `server/src/middleware/auth.ts` (MODIFY — dual auth) | Phase 3 |
| `randytorres/BudtenderIncentiveAI` | `server/src/services/glassIntegration.ts` (NEW) | Phase 2 |
| `randytorres/BudtenderIncentiveAI` | `server/src/services/glassSync.ts` (NEW) | Phase 2 |
| `randytorres/BudtenderIncentiveAI` | `mobile/src/screens/DriverSubmissionScreen.tsx` (NEW) | Phase 2 |
| `randytorres/BudtenderIncentiveAI` | `admin/src/components/MissionSuggestions.tsx` (NEW) | Phase 3 |

## Appendix C: Key Decisions Log

| Decision | Rationale | Alternative Considered |
|----------|-----------|----------------------|
| Hub-and-spoke, not monolith | Each product has different deploy cadence, different auth, different team. API coupling is looser than DB coupling. | Full merge into Railway PG |
| Eliminate Firestore | 300 products in Firestore when GLASS has 100K+. Firebase adds unnecessary cost and complexity. GLASS already scrapes CH's Dutchie menu. | Keep Firestore as cache layer |
| Keep Firebase Phone Auth for mobile | Phone OTP is the right UX for budtenders/drivers. Clerk's phone auth is less mature. Don't fix what works. | Migrate everything to Clerk |
| API key auth for service-to-service | Simpler than OAuth2 client credentials for a 4-product ecosystem. Rotate keys via env vars. | JWT service tokens, OAuth2 |
| Manual driver submission for V1 | No POS integration available at CH. Manual + admin approval is good enough for 3-8 drivers. Automate later. | Wait for Blaze API integration |
| `participants` table as generalization | One table for all participant types avoids N separate tables. Type-specific data goes in JSONB `metadata`. | Separate tables per type |
| Demand signals as nightly batch | Real-time aggregation is overkill for daily/weekly mission targeting. Batch is simpler and cheaper. | Real-time streaming |

---

*This document is the single source of truth for ecosystem integration. All implementation should reference this plan. Update this document as decisions change.*
