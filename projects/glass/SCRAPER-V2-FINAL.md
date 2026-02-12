# GLASS Price Intelligence Pipeline — V2 Final Plan

_Synthesized from COO plan + Codex 5.3 review. Addresses all REJECT findings._

---

## Architecture: What We're Actually Building (Week 1)

One thing. Dutchie scraper that works. Not a multi-platform analytics empire.

### Three Independent Scripts + Shared Libs

```
scripts/
├── lib/
│   ├── types.ts           # All shared types
│   ├── config.ts           # Env vars, constants, paths
│   ├── db.ts               # Drizzle pg client (direct connection)
│   ├── browser-pool.ts     # CamoFox launcher + tab pool (3 tabs)
│   ├── parser.ts           # DOM → ParsedProduct (with fixtures/tests)
│   └── normalizer.ts       # Weight→grams, brand cleanup, SKU gen, per-category metrics
├── scrape-dutchie.ts       # Main: discover + scrape + load (one script, 3 phases)
└── dutchie-slugs.json      # Cached 235 slugs
```

**NOT building yet:** Weedmaps, analytics views, API endpoints, Railway deploy. Those come after Dutchie is at 95%+ success rate.

---

## Schema Changes (Minimal, Non-Breaking)

Codex was right — don't create `prices_normalized`. Use existing tables + add columns.

### Migration SQL

```sql
-- 1. Operators: relax license_number for discovery, add platform fields
ALTER TABLE operators ALTER COLUMN license_number DROP NOT NULL;
ALTER TABLE operators ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE operators ADD COLUMN IF NOT EXISTS platform VARCHAR(50);
ALTER TABLE operators ADD COLUMN IF NOT EXISTS platform_slug VARCHAR(255);
CREATE UNIQUE INDEX IF NOT EXISTS idx_operators_platform_slug 
  ON operators (platform, platform_slug) WHERE platform IS NOT NULL;

-- 2. Products: add weight/strain fields
ALTER TABLE products ADD COLUMN IF NOT EXISTS weight_grams DECIMAL(10,3);
ALTER TABLE products ADD COLUMN IF NOT EXISTS strain_type VARCHAR(50);
ALTER TABLE products ADD COLUMN IF NOT EXISTS subcategory VARCHAR(50);

-- 3. Prices: add price_per_gram (computed on insert, not a separate table)
ALTER TABLE prices ADD COLUMN IF NOT EXISTS price_per_gram DECIMAL(10,4);
ALTER TABLE prices ADD COLUMN IF NOT EXISTS weight_grams DECIMAL(10,3);
ALTER TABLE prices ADD COLUMN IF NOT EXISTS menu_type VARCHAR(10) DEFAULT 'rec';

-- 4. Scrape runs: envelope for daily jobs (scrape_jobs already exists per-source)
CREATE TABLE IF NOT EXISTS scrape_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status VARCHAR(20) NOT NULL DEFAULT 'running',  -- running/completed/failed
  platform VARCHAR(20) NOT NULL,  -- 'dutchie'
  stores_attempted INT DEFAULT 0,
  stores_succeeded INT DEFAULT 0,
  stores_failed INT DEFAULT 0,
  products_found INT DEFAULT 0,
  prices_inserted INT DEFAULT 0,
  duration_seconds INT,
  error_log JSONB DEFAULT '[]',
  metadata JSONB DEFAULT '{}'
);

-- 5. Partition prices by month (for retention)
-- DEFERRED: Only needed when prices >1M rows. For now, indexes are sufficient.

-- 6. Index for price history queries
CREATE INDEX IF NOT EXISTS idx_prices_product_scraped 
  ON prices (product_id, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_prices_operator_category 
  ON prices (operator_id, scraped_at DESC);
```

**Key decision per Codex review:** `license_number` becomes NULLABLE for discovery phase. We reconcile against CCC data later in Phase 3.

---

## Job Model: Two-Level with Resume

```
scrape_runs (1 per daily execution)
  └── scrape_jobs (1 per source/store, already exists in schema)
        ├── status: pending → running → succeeded/failed/retry_exhausted  
        ├── method_used: 'camofox'
        ├── records_found / records_parsed
        └── error_message (if failed)
```

**Resume logic:** On startup, `scrape-dutchie.ts` checks for incomplete `scrape_runs` from today. If found, loads which `scrape_jobs` already succeeded and skips those stores. New stores get queued.

**Idempotency:** Price inserts use `(product_id, source_id, operator_id, scraped_at::date)` as a natural dedup key. If we re-scrape a store same day, we upsert (latest price wins).

---

## Entity Resolution: Realistic Approach

Codex was right that simple hash is fragile. But a full fuzzy matching pipeline is overengineering for Week 1.

### V2 Approach: Deterministic Keys + Manual Review Queue

**SKU Generation:**
```typescript
// Level 1: Exact match (handles 80%+ of cases)
function makeSKU(brand: string, name: string, weightGrams: number, category: string): string {
  const key = [
    brand.toLowerCase().trim(),
    name.toLowerCase().replace(/[^a-z0-9 ]/g, '').trim(),
    weightGrams.toFixed(1),
    category,
  ].join('|');
  return `DUTCHIE-${sha256(key).slice(0, 20)}`;
}
```

**Level 2 (deferred):** Fuzzy matching for cross-store dedup. Logged for now, implemented when we have data to tune on.

**Review queue:** Products with confidence < 0.75 get `metadata.needs_review = true`. Randy can review in GLASS dashboard later.

---

## Weight Normalization: Category-Specific

```typescript
const WEIGHT_MAP: Record<string, number> = {
  '1g': 1, '1 g': 1, '1 gram': 1,
  '2g': 2, '3.5g': 3.5, '3.5 g': 3.5,
  '1/8 oz': 3.5, '1/8oz': 3.5,
  '1/4 oz': 7, '1/4oz': 7, 'quarter': 7,
  '1/2 oz': 14, '1/2oz': 14, 'half oz': 14,
  '1 oz': 28, '1oz': 28, 'ounce': 28,
  '7g': 7, '14g': 14, '28g': 28,
};

// Price-per-gram ONLY for flower, preroll, concentrate
// Edibles use $/mg THC, vapes use $/ml — computed separately  
function computePriceMetric(category: string, price: number, weightGrams: number, thcPercent?: number): {
  pricePerGram: number | null;
  pricePerMgThc: number | null;
} {
  if (['flower', 'preroll', 'concentrate'].includes(category) && weightGrams > 0) {
    return { pricePerGram: price / weightGrams, pricePerMgThc: null };
  }
  if (category === 'edible' && thcPercent && weightGrams > 0) {
    const mgThc = weightGrams * 1000 * (thcPercent / 100);
    return { pricePerGram: null, pricePerMgThc: mgThc > 0 ? price / mgThc : null };
  }
  return { pricePerGram: null, pricePerMgThc: null };
}
```

---

## Browser Pool: Resilient Design

```typescript
// Single browser, 3 tabs, with crash recovery
class BrowserPool {
  private browser: Browser;
  private context: BrowserContext;
  private workers: Page[] = [];
  private MAX_TABS = 3;

  async init() {
    this.browser = await firefox.launch({
      executablePath: CAMOFOX_BIN,
      headless: true,
      args: ['--no-remote'],
    });
    this.context = await this.browser.newContext({
      userAgent: UA,
      viewport: { width: 1280, height: 720 },
    });
    // Pre-handle age gate: navigate to any Dutchie page, click Yes
    await this.handleAgeGate();
  }

  // If browser crashes, restart it (Codex concern: single point of failure)
  async ensureHealthy(): Promise<boolean> {
    try {
      // Ping check — create and close a tab
      const page = await this.context.newPage();
      await page.close();
      return true;
    } catch {
      console.warn('Browser unhealthy, restarting...');
      await this.restart();
      return true;
    }
  }

  async restart() {
    await this.browser?.close().catch(() => {});
    await this.init();
  }
}
```

---

## Parser: With Contract Tests

The parser extracts from `page.evaluate()` DOM output. Codex correctly flagged that DOM changes will silently break parsing.

**Solution:** Parser contract tests with frozen snapshots.

```
scripts/
├── lib/
│   ├── parser.ts
│   └── __fixtures__/
│       ├── pure-oasis-flower.json      # Real DOM snapshot
│       ├── 311-page-prerolls.json      # Real DOM snapshot
│       └── expected-products.json      # Expected parse output
├── test-parser.ts                      # Runs parser against fixtures, asserts counts + fields
```

**Drift detection:** After each scrape run, compute:
- % of products with null price (should be < 5%)
- % of products with null THC (< 30% is OK for ground flower)
- Average products per store (if drops >50% from 7-day avg, alert)

---

## Railway Validation: Spike First

Codex was right — we can't assume CamoFox works on Railway. Before building the full pipeline:

**Spike task (30 min):**
1. Create `Dockerfile.scraper` with CamoFox binary
2. Deploy to Railway as test service
3. Run a 5-store scrape
4. Measure: memory peak, CPU usage, runtime, any crashes
5. If fails: fallback plan = run scraper on this sandbox via OpenClaw cron, push data to Railway Postgres

This spike blocks full deployment but NOT script development. We build scripts locally, test locally, deploy after spike passes.

---

## Revised Cost Estimate

Per Codex: p95 timing is likely 45s/category, not 20s. And memory may need 3-4GB.

**Conservative estimate:**
- Runtime: 8-10 hours (400 stores at 45s/cat × 5 cats / 3 workers + retries)
- Resources: 2 vCPU + 4GB RAM
- Daily cost: 10h × ($0.056 vCPU + $0.056 mem) = $1.12/day
- **Monthly: ~$34** (not $10)

Still cheap. But the real question is whether Railway handles the browser at all — hence the spike.

---

## Implementation Order (Revised per Codex)

| # | Task | Why This Order |
|---|------|---------------|
| 1 | **Schema migration** | Data model first. Everything depends on this. |
| 2 | `lib/types.ts` + `lib/config.ts` | Foundation types before any code. |
| 3 | `lib/db.ts` | Drizzle client — needed for loader. |
| 4 | `lib/parser.ts` + fixtures | Parser with tests — validate extraction logic independently. |
| 5 | `lib/normalizer.ts` | Weight conversion, SKU gen, category metrics. |
| 6 | `lib/browser-pool.ts` | CamoFox pool with crash recovery. |
| 7 | `scrape-dutchie.ts` | Main orchestrator (discover → scrape → load). |
| 8 | **Test with --limit 20** | Validate full pipeline locally. |
| 9 | **Railway spike** | Prove CamoFox works on Railway. |
| 10 | `Dockerfile.scraper` + deploy | Only after spike passes. |

**Deferred to Phase 2+:**
- Weedmaps integration (after Dutchie 95%+)
- Materialized analytics views (after 1 week of data)
- API endpoints (after views exist)
- CCC license reconciliation (Phase 3)
- Fuzzy entity matching (after we see real dedup failures)

---

## Acceptance Criteria (Week 1)

- [ ] Schema migration runs clean on Railway Postgres
- [ ] Parser extracts products from 3+ fixture snapshots correctly
- [ ] 20-store local test run completes with >80% store success rate
- [ ] Products + prices land in DB with correct FKs
- [ ] Scrape run + scrape job records created with accurate counts
- [ ] Price-per-gram computed correctly for flower/preroll/concentrate
- [ ] Raw snapshots saved per store per day
- [ ] Resume works: re-run skips already-scraped stores from today
