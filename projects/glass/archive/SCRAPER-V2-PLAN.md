# GLASS Price Intelligence Pipeline — V2 Production Plan

_POC validated: 912+ products from 3 dispensaries. Now build it at scale._

---

## 1. Coverage Gap: Why Only 235?

**The 235 slugs are only Dutchie-powered dispensaries we found via city pages.** Here's the full picture:

| Source | Estimated MA Coverage | Data Access |
|--------|----------------------|-------------|
| **CCC Licensed Retailers** | **650+ approved to operate** (717 provisionally licensed, Feb 2025) | CCC licensing tracker (public CSV) |
| **Dutchie** | ~235-350 (40%+ national market share, 6,500+ partners) | Browser scraping (CamoFox) ✅ proven |
| **Weedmaps** | ~300-400 listings | JSON API in network tab (no auth for public listings) |
| **Leafly** | ~200-300 listings | Web scraping |
| **iHeartJane** | ~100-150 stores | Embed widget (similar to Dutchie) |
| **Direct websites** | ~50-100 (own menus, no platform) | Per-site scraping |

**Real total: ~450-550 unique operating dispensaries in MA.** Our 235 Dutchie slugs = ~45% coverage.

### How to Get Full Coverage

**Phase 1 (now):** Dutchie — 235+ stores via CamoFox. Already working.
**Phase 2 (week 2):** Weedmaps — their public pages load menu data via JSON XHR requests (`api-g.weedmaps.com`). CamoFox can intercept these. Adds ~100-150 unique stores not on Dutchie.
**Phase 3 (week 3):** CCC license CSV as master list — cross-reference scraped stores against CCC data to find gaps, get correct license numbers, addresses. Public download at `masscannabiscontrol.com`.
**Phase 4 (month 2):** iHeartJane + Leafly for remaining stragglers.

**Target: 400+ stores with live menu data within 4 weeks.**

---

## 2. Speed — How to Scrape 400+ Stores Without Getting Blocked

### The Math

POC results per store: **~300 products across 5 categories** (912 from 3 stores ≈ 304 avg)
At 400 stores × 5 categories = **2,000 page loads**

### Speed Strategy: Parallel Workers + Smart Scheduling

```
┌─────────────────────────────────────────────────┐
│           SCRAPE ORCHESTRATOR (run-daily.ts)      │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Worker 1  │ │ Worker 2  │ │ Worker 3  │         │
│  │ (Tab 1)   │ │ (Tab 2)   │ │ (Tab 3)   │         │
│  │ Store A   │ │ Store B   │ │ Store C   │         │
│  │ 5 cats    │ │ 5 cats    │ │ 5 cats    │         │
│  └──────────┘ └──────────┘ └──────────┘          │
│        ↕              ↕              ↕             │
│  ┌─────────────────────────────────────────────┐  │
│  │     ONE CamoFox Browser Instance             │  │
│  │     (shared context = shared cookies)        │  │
│  └─────────────────────────────────────────────┘  │
│        ↓              ↓              ↓             │
│  ┌─────────────────────────────────────────────┐  │
│  │            PostgreSQL (Railway)               │  │
│  │  operators → sources → products → prices      │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Anti-detection measures:**
- **3 concurrent tabs max** — looks like a real user with multiple tabs
- **2-4 second jitter** between page navigations per tab
- **Staggered starts** — workers don't all navigate simultaneously
- **Realistic viewport** (1280×720) + desktop user agent
- **Cookie persistence** — age gate clicked once, cookie carries to all tabs
- **Category rotation** — each worker scrapes one store's 5 categories before moving on (mimics browsing)
- **Circuit breaker** — if 3+ consecutive 403s, pause that worker for 60s
- **Daily cadence only** — one full sweep per 24h, no aggressive polling

**Speed estimate:**
- Per category: ~20s (navigate 5s + wait 3s + scroll 6s + extract 2s + delay 4s)
- Per store: ~100s (5 categories)
- 3 workers: ~400 stores / 3 workers = ~133 stores each
- 133 × 100s = ~3.7 hours
- **Total: ~4 hours** (with failures/retries)

This is fine for a daily 2-6 AM overnight window.

---

## 3. Railway Deployment — Cost Analysis

### Railway Pricing
- **vCPU:** $0.000463/min ($0.028/hr, ~$20/mo continuous)
- **Memory:** $0.000231/GB/min ($0.014/GB/hr, ~$10/GB/mo continuous)
- **Network:** $0.05/GB egress

### Our Scraper Worker
- Needs: ~2 vCPU + 2GB RAM (headless browser is memory-hungry)
- Runtime: ~4 hours/day
- Daily cost: 4h × ($0.056 + $0.028) = **$0.34/day = ~$10/month**

### Deployment Architecture

```
Railway Project (existing glass project):
├── glass-api          (always on — $15-20/mo)
├── glass-web          (always on — $5-10/mo)
├── Postgres           (always on — $7/mo)
├── Redis              (always on — $5/mo)
└── glass-scraper  ← NEW (cron: daily 3AM EST, sleeps after)
```

**Railway Cron Jobs** — the scraper service gets a cron schedule. Railway spins it up, runs the script, it exits, Railway stops billing. Perfect for this use case.

```toml
# railway-scraper.toml
[build]
  builder = "dockerfile"
  dockerfilePath = "Dockerfile.scraper"

[deploy]
  startCommand = "node scripts/run-daily.js"
  cronSchedule = "0 8 * * *"  # 8 AM UTC = 3 AM EST
```

**Total added cost: ~$10/month** for 400+ stores scraped daily.

---

## 4. Data Processing Pipeline — Raw → Usable Intelligence

This is the real value. Raw prices are noise. Intelligence is signal.

### Stage 1: Extract & Normalize (during scrape)

```
Raw DOM → ParsedProduct
├── name: "Bloom | Godfather OG | Ground Flower"
├── brand: "BLOOM"
├── category: "flower"
├── weight: "1/2 oz"
├── price: 39.99
├── thc: 23.53%
├── cbd: null
├── strain_type: "Indica-Hybrid"
└── store: "pure-oasis-dtx"
```

**Normalization rules:**
- Weight standardization: "1/2 oz" → 14g, "1/8 oz" → 3.5g, "1g" → 1g
- Price per gram calculation: $39.99 / 14g = $2.86/g
- Brand normalization: "BLOOM" = "Bloom" = "bloom"
- Category mapping: "Ground Flower" → flower/ground, "Pre-Rolls" → preroll
- Promo detection: "$39.99 ~~$49.99~~" → promo_flag=true, regular_price=49.99

### Stage 2: Entity Resolution (load step)

Products from different stores need to be matched:
```
Store A: "Bloom | Godfather OG | Ground Flower | 1/2oz"
Store B: "BLOOM - Godfather OG Ground Flower (14g)"
→ Same canonical product, different stores + prices
```

**SKU Strategy:**
```
canonical_sku = sha256(lowercase(brand) + "|" + normalized_name + "|" + weight_grams)
```

This gives us: **one product row, many price rows across stores.**

### Stage 3: Computed Analytics (daily post-scrape job)

After prices are loaded, compute and cache:

```sql
-- Materialized views / computed tables

-- 1. Market averages by product
CREATE MATERIALIZED VIEW market_averages AS
SELECT product_id, category,
  AVG(price_per_gram) as avg_price_per_gram,
  MIN(price_per_gram) as min_price_per_gram,
  MAX(price_per_gram) as max_price_per_gram,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_gram) as median_price,
  COUNT(DISTINCT operator_id) as num_stores,
  COUNT(*) as num_observations
FROM prices_normalized
WHERE scraped_at > NOW() - INTERVAL '7 days'
GROUP BY product_id, category;

-- 2. Store positioning (where does each store rank?)
CREATE MATERIALIZED VIEW store_positioning AS
SELECT operator_id, category,
  AVG(price_per_gram) as avg_price,
  PERCENT_RANK() OVER (PARTITION BY category ORDER BY AVG(price_per_gram)) as price_percentile
FROM prices_normalized
WHERE scraped_at > NOW() - INTERVAL '7 days'
GROUP BY operator_id, category;

-- 3. Price movers (what changed since yesterday?)
CREATE MATERIALIZED VIEW price_movers AS
SELECT p1.product_id, p1.operator_id,
  p1.price as current_price,
  p2.price as previous_price,
  ((p1.price - p2.price) / p2.price * 100) as pct_change
FROM latest_prices p1
JOIN previous_prices p2 ON p1.product_id = p2.product_id 
  AND p1.operator_id = p2.operator_id
WHERE ABS(p1.price - p2.price) / p2.price > 0.05;  -- >5% change

-- 4. Category benchmarks
CREATE MATERIALIZED VIEW category_benchmarks AS
SELECT category, weight_grams,
  PERCENTILE_CONT(0.25) as p25,
  PERCENTILE_CONT(0.50) as p50,
  PERCENTILE_CONT(0.75) as p75,
  AVG(price) as mean_price,
  COUNT(DISTINCT operator_id) as store_count
FROM prices_normalized
WHERE scraped_at > NOW() - INTERVAL '7 days'
GROUP BY category, weight_grams;
```

### Stage 4: Intelligence Products (what GLASS shows users)

| Feature | Data Source | Update Frequency |
|---------|-----------|-----------------|
| **Price Wire** | price_movers view | Daily after scrape |
| **Morning Brief** | category_benchmarks + price_movers | Daily 7 AM EST |
| **Margin Engine** | user's costs vs market_averages | Real-time on login |
| **Threat Radar** | store_positioning + new competitor detection | Daily |
| **Recommendations** | margin_rules × market_averages × price_movers | Daily post-scrape |
| **Alerts** | threshold crossings from watchlists | During price load |

---

## 5. Database Schema Additions

Current schema handles individual prices but lacks the analytics layer.

```sql
-- New table: normalized prices with computed fields
CREATE TABLE prices_normalized (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  price_id UUID REFERENCES prices(id),
  product_id UUID REFERENCES products(id),
  operator_id UUID REFERENCES operators(id),
  source_id UUID REFERENCES sources(id),
  category VARCHAR(50),
  weight_grams DECIMAL(10,3),
  price DECIMAL(10,2),
  price_per_gram DECIMAL(10,4),
  thc_percent DECIMAL(5,2),
  cbd_percent DECIMAL(5,2),
  promo_flag BOOLEAN DEFAULT false,
  regular_price DECIMAL(10,2),  -- pre-promo price if detected
  in_stock BOOLEAN DEFAULT true,
  menu_type VARCHAR(10),  -- 'rec' or 'med'
  scraped_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- New table: scrape run metadata
CREATE TABLE scrape_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMPTZ NOT NULL,
  completed_at TIMESTAMPTZ,
  stores_attempted INT DEFAULT 0,
  stores_succeeded INT DEFAULT 0,
  stores_failed INT DEFAULT 0,
  products_found INT DEFAULT 0,
  prices_inserted INT DEFAULT 0,
  duration_seconds INT,
  platform VARCHAR(20),  -- 'dutchie', 'weedmaps', etc
  metadata JSONB DEFAULT '{}'
);

-- Add to operators
ALTER TABLE operators ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE operators ADD COLUMN IF NOT EXISTS platform VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS platform_slug VARCHAR(255);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS store_hours JSONB;

-- Add to products  
ALTER TABLE products ADD COLUMN IF NOT EXISTS weight_grams DECIMAL(10,3);
ALTER TABLE products ADD COLUMN IF NOT EXISTS strain_type VARCHAR(50);
ALTER TABLE products ADD COLUMN IF NOT EXISTS subcategory VARCHAR(50);
```

---

## 6. File Structure

```
projects/glass/src/
├── scripts/
│   ├── lib/
│   │   ├── types.ts           # Shared types
│   │   ├── config.ts          # Environment + constants
│   │   ├── db.ts              # Drizzle client (direct pg connection)
│   │   ├── browser-pool.ts    # CamoFox launch + tab pool + age gate
│   │   ├── parser.ts          # DOM extraction → ParsedProduct
│   │   ├── normalizer.ts      # Weight conversion, brand normalization, SKU gen
│   │   ├── loader.ts          # Upsert products + insert prices via Drizzle
│   │   └── analytics.ts       # Refresh materialized views
│   ├── discover-slugs.ts      # Phase 1: find all Dutchie stores
│   ├── scrape-menus.ts        # Phase 2: parallel browser scraping
│   ├── load-prices.ts         # Phase 3: DB loading + normalization
│   ├── compute-analytics.ts   # Phase 4: refresh materialized views
│   ├── run-daily.ts           # Orchestrator: chains all phases
│   ├── dutchie-slugs.json     # Cached slugs (235+)
│   └── raw-snapshots/         # Daily snapshots (gitignored)
│       └── 2026-02-12/
│           ├── pure-oasis-dtx.json
│           └── ...
├── Dockerfile.scraper         # Docker image with CamoFox baked in
└── railway-scraper.toml       # Railway cron config
```

---

## 7. Implementation Order

| # | Task | Scope | Model |
|---|------|-------|-------|
| 1 | `lib/types.ts` + `lib/config.ts` | Shared types, env config, constants | Codex 5.3 |
| 2 | `lib/db.ts` | Drizzle client with direct pg connection string | Codex 5.3 |
| 3 | `lib/browser-pool.ts` | CamoFox launcher, tab pool (3 workers), age gate handler, cookie reuse | Codex 5.3 |
| 4 | `lib/parser.ts` | DOM extraction from page.evaluate(), product card parsing | Codex 5.3 |
| 5 | `lib/normalizer.ts` | Weight→grams, brand normalization, SKU generation, price-per-gram, promo detection | Codex 5.3 |
| 6 | `lib/loader.ts` | Upsert operators/sources/products, append prices, update scrape_jobs | Codex 5.3 |
| 7 | `lib/analytics.ts` | Refresh materialized views, compute price movers | Codex 5.3 |
| 8 | `scrape-menus.ts` | Worker pool orchestrator with queue, circuit breaker, progress logging | Codex 5.3 |
| 9 | `run-daily.ts` | Chain: discover → scrape → load → compute → report | Codex 5.3 |
| 10 | Schema migration SQL | New tables + columns + materialized views | Codex 5.3 |
| 11 | `Dockerfile.scraper` | Multi-stage: install CamoFox binary + Node + scripts | Codex 5.3 |
| 12 | `railway-scraper.toml` | Cron schedule + resource limits | COO |
| 13 | API endpoints for analytics | `/api/market-averages`, `/api/price-movers`, `/api/benchmarks` | Phase 2 |

**Codex builds steps 1-11. COO reviews. Then deploy.**

---

## 8. Success Metrics

- [ ] **400+ MA dispensaries** with live menu data (Dutchie + Weedmaps)
- [ ] **100,000+ price observations** per daily run
- [ ] **Scrape completes in <5 hours** (3 parallel workers)
- [ ] **<$15/month** Railway cost for scraper service
- [ ] **Zero raw SQL** — all DB ops via Drizzle ORM
- [ ] **Scrape run tracking** — success rate, duration, product counts
- [ ] **Price-per-gram normalization** across all weight formats
- [ ] **Market analytics views** refreshed daily
- [ ] **Entity resolution** — same product from different stores linked
- [ ] **Raw snapshots saved** — reprocessable if parser improves

---

## 9. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Cloudflare blocks CamoFox at scale | Scrape fails | 3 concurrent max, 2-4s delays, rotate UA, daily only |
| Dutchie DOM changes | Parser breaks silently | Raw snapshots saved, parser has fallback chains, QA check on product counts |
| Railway cron misfire | Miss daily window | Scrape run table tracks last success, alert if >30h stale |
| Memory pressure from 3 browsers | OOM kill | Single browser instance, 3 tabs (not 3 browsers), 2GB limit |
| Duplicate products across stores | Inflated counts | SKU-based dedup + brand normalization |
| Legal/ToS risk | Cease & desist | Public menu data only, no login-gated content, respectful rate limiting, ToS review |
| Stale/closed stores | Garbage data | Track consecutive failures, auto-deactivate after 7 days of 0 products |

---

## 10. Timeline

| Week | Deliverable |
|------|------------|
| **Week 1** | Core libs (types, db, browser-pool, parser, normalizer, loader) + scrape-menus.ts + run-daily.ts. Test with --limit 20. |
| **Week 2** | Schema migration, Dockerfile, Railway deploy. Full 235-store Dutchie run. Fix parser issues from real data. |
| **Week 3** | Weedmaps scraper (second platform). CCC license CSV integration. Analytics views. |
| **Week 4** | API endpoints for analytics. Frontend updates to use real data. 400+ store coverage. |

**Week 1 is the critical path. Everything else builds on it.**
