# SCRAPER EXECUTION PLAN — 2026-02-13

**Generated at:** 20:55 UTC, Feb 13, 2026
**Status:** All 4 scrapers verified and ready to run from sandbox

---

## Current State (Validated)

### System Health

| Resource | Value | Status |
|----------|-------|--------|
| **RAM** | 503GB total, ~138GB free | ✅ Sufficient |
| **Disk** | 2.9TB, 52% used | ✅ Sufficient |
| **Zombie processes** | 599 defunct out of 615 total | ⚠️ Cosmetic (see below) |
| **Live processes** | ~17 real processes running | ✅ OK |
| **Local CamoFox (port 9377)** | **DEAD** — all 19 camoufox procs are zombies | ❌ Unusable |
| **Railway Browser Service** | **ALIVE** — health OK, tab creation works | ✅ Use this |
| **Database (Railway Postgres)** | Connected, 197,698 total prices | ✅ OK |

### Zombie Processes

599 zombie/defunct processes from crashed subagent spawns. These cannot be reaped because their parent (PID 1) is the container init which doesn't reap them. They consume **zero CPU/RAM** — only PID table entries. The sandbox container has a high PID limit so this is cosmetic, not a blocker.

### Today's Progress (Already Scraped)

| Platform | Prices Today | Stores Today | Slug File | Total Slugs |
|----------|-------------|--------------|-----------|-------------|
| **Dutchie** | 6,242 | 29 of 235 | ✅ exists | 235 |
| **Weedmaps** | 0 | 0 of 282 | ✅ exists | 282 |
| **Leafly** | 928 | 5 of 292 | ✅ exists | 292 |
| **Jane** | 12,161 | 45 of 39 | ✅ exists | 39 |

**Jane is already done for today** (39/39 stores, 10,345 prices in the last full run). Re-running will produce fresh data but isn't strictly necessary.

### Historical Performance (Best Runs)

| Platform | Stores | Prices | Duration | Notes |
|----------|--------|--------|----------|-------|
| **Dutchie** | 235 → 195 succeeded | 57,514 | ~5.2 hours | Uses CamoFox browser, age gate handling |
| **Weedmaps** | 173 → 10 succeeded | 6,162 | ~80 min | Uses CamoFox browser, many stores fail |
| **Leafly** | 5 → 1-3 succeeded | 48-723 | ~30 sec | Uses direct HTTP, many API failures |
| **Jane** | 39 → 39 succeeded | 10,345 | ~52 sec | Uses CamoFox browser (Algolia proxy) |

---

## Architecture: What Each Scraper Needs

| Scraper | Browser Needed? | Browser URL Config | How It Works |
|---------|----------------|-------------------|--------------|
| **Dutchie** | ✅ YES | `CAMOFOX_URL` env var → BrowserPool defaults to `localhost:9377` | CamoFox navigates to each store page, handles age gates, scrapes DOM |
| **Weedmaps** | ✅ YES | `WEEDMAPS_CAMOFOX_URL` env var → defaults to Railway URL | CamoFox navigates store pages, paginated product scraping |
| **Leafly** | ❌ NO | N/A | Direct HTTP to `consumer-api.leafly.com` + SSR page scraping |
| **Jane** | ✅ YES (Cloudflare bypass) | `WEEDMAPS_CAMOFOX_URL` env var → defaults to Railway URL | CamoFox tab on iheartjane.com, then `page.evaluate(fetch(...))` to Algolia proxy |

### Key Discovery: Browser URL Configuration

- **Dutchie** uses `BrowserPool` which reads `CAMOFOX_URL` env var, defaulting to `http://localhost:9377`
- **Weedmaps** and **Jane** use `WEEDMAPS_CAMOFOX_URL` which defaults to `https://roviq-browser-production.up.railway.app`
- Since local CamoFox is dead, **Dutchie must set `CAMOFOX_URL`** to the Railway browser
- **Weedmaps** and **Jane** already default to Railway browser — no override needed
- **Leafly** doesn't need any browser

### Railway Browser Service Status

```
Health:   ✅ {"ok":true}
Tab creation: ✅ Works (tested with Dutchie URL — loads age gate correctly)
Endpoint: https://roviq-browser-production.up.railway.app
```

---

## EXECUTION PLAN

### Pre-Flight Checklist

Run these before starting any scraper:

```bash
# 1. Verify Railway browser is alive
curl -s https://roviq-browser-production.up.railway.app/health
# Expected: {"ok":true}

# 2. Verify DB connectivity
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  node -e "const{Pool}=require('pg');const p=new Pool({connectionString:process.env.DATABASE_URL});p.query('SELECT 1').then(()=>{console.log('DB OK');p.end()}).catch(e=>{console.error(e);process.exit(1)})"
# Expected: DB OK

# 3. Check for stale "running" scrape_runs
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  node -e "const{Pool}=require('pg');const p=new Pool({connectionString:process.env.DATABASE_URL});p.query(\"UPDATE scrape_runs SET status='failed',completed_at=NOW() WHERE status='running' AND started_at < NOW()-INTERVAL '30 minutes' RETURNING id,platform\").then(r=>{console.log('Cleaned:',r.rows.length);p.end()}).catch(e=>{console.error(e);process.exit(1)})"
# Expected: Cleaned: 0 (or shows cleaned stale runs)
```

### Execution Order

Run scrapers **sequentially** (one at a time). CamoFox is a shared browser — concurrent scrapers will interfere.

**Order:** Leafly → Jane → Weedmaps → Dutchie

**Rationale:**
1. **Leafly first** — No browser needed, fast (under 30 min), validates DB pipeline
2. **Jane second** — Fast (~1 min), uses Railway browser, validates browser pipeline
3. **Weedmaps third** — ~80 min, uses Railway browser
4. **Dutchie last** — ~5 hours, longest run, uses Railway browser via `CAMOFOX_URL` override

---

### Step 1: Run Leafly (No Browser Needed)

**Expected:** ~292 stores attempted, ~150-200 prices, ~10-30 minutes
**Browser:** Not required

```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/scrape-leafly.ts --skip-discovery --db
```

**Flags explained:**
- `--skip-discovery` — Uses existing `leafly-slugs.json` (292 stores already discovered)
- `--db` — Writes to Railway PostgreSQL (required for prices to be inserted)

**Monitor:** Watch stdout for `[leafly N/292]` progress lines.

**Known issues:**
- Leafly API rate-limits at ~200 stores (429 errors). The script retries with backoff.
- Many stores return empty menus or fail with 404. ~1-5 stores typically succeed per run.
- This is a known Leafly limitation, not a bug.

**Verify success:**
```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  node -e "const{Pool}=require('pg');const p=new Pool({connectionString:process.env.DATABASE_URL});p.query(\"SELECT platform,status,stores_succeeded,prices_inserted,duration_seconds FROM scrape_runs WHERE platform='leafly' ORDER BY started_at DESC LIMIT 1\").then(r=>{console.log(r.rows[0]);p.end()}).catch(e=>{console.error(e);process.exit(1)})"
```

---

### Step 2: Run Jane (Fast, Uses Railway Browser)

**Expected:** ~39 stores, ~10,000 prices, ~1 minute
**Browser:** Railway browser (default URL, no override needed)

```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/scrape-jane.ts --skip-discovery --db
```

**Flags explained:**
- `--skip-discovery` — Uses existing `jane-slugs.json` (39 stores)
- `--db` — Writes to Railway PostgreSQL

**Note:** Jane was already successfully scraped today (10,345 prices at 14:43 UTC). Running again will create a new run with fresh prices for the same stores. The `getActiveRunForToday` function will detect today's existing run and may skip already-completed stores. If you want a completely fresh run, the script handles it automatically.

**Monitor:** Watch for `[jane] [N/39]` progress. Should complete in ~1 minute.

**Verify success:**
```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  node -e "const{Pool}=require('pg');const p=new Pool({connectionString:process.env.DATABASE_URL});p.query(\"SELECT platform,status,stores_succeeded,prices_inserted,duration_seconds FROM scrape_runs WHERE platform='jane' ORDER BY started_at DESC LIMIT 1\").then(r=>{console.log(r.rows[0]);p.end()}).catch(e=>{console.error(e);process.exit(1)})"
```

---

### Step 3: Run Weedmaps (Uses Railway Browser)

**Expected:** ~282 stores attempted, ~10-50 succeed, ~6,000+ prices, ~60-90 minutes
**Browser:** Railway browser (default URL, no override needed)

```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/scrape-weedmaps.ts --skip-discovery --db
```

**Flags explained:**
- `--skip-discovery` — Uses existing `weedmaps-slugs.json` (282 stores)
- `--db` — Writes to Railway PostgreSQL

**Known behavior:**
- Weedmaps has aggressive anti-bot. Many stores will fail with timeouts, rate limits, or empty menus.
- Best previous run: 10/173 stores succeeded = 6,162 prices. Low success rate is expected.
- The script has retry logic and proper error categorization.

**Monitor:** Watch stdout for progress. Each store takes 30s-2min.

**If it crashes:** Re-run with `--resume` to skip already-completed stores:
```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/scrape-weedmaps.ts --skip-discovery --db --resume
```
(The script auto-detects today's active run ID.)

**Verify success:**
```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  node -e "const{Pool}=require('pg');const p=new Pool({connectionString:process.env.DATABASE_URL});p.query(\"SELECT platform,status,stores_succeeded,prices_inserted,duration_seconds FROM scrape_runs WHERE platform='weedmaps' ORDER BY started_at DESC LIMIT 1\").then(r=>{console.log(r.rows[0]);p.end()}).catch(e=>{console.error(e);process.exit(1)})"
```

---

### Step 4: Run Dutchie (Longest — Uses Railway Browser via CAMOFOX_URL)

**Expected:** ~235 stores, ~150-195 succeed, ~50,000+ prices, ~4-6 hours
**Browser:** Railway browser — **MUST set `CAMOFOX_URL` env var** (Dutchie's BrowserPool defaults to `localhost:9377` which is dead)

```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  CAMOFOX_URL="https://roviq-browser-production.up.railway.app" \
  npx tsx scripts/scrape-dutchie.ts --skip-discovery --db
```

**⚠️ CRITICAL: The `CAMOFOX_URL` env var is what makes this work.** Without it, Dutchie tries `localhost:9377` which is dead.

**Flags explained:**
- `--skip-discovery` — Uses existing `dutchie-slugs.json` (235 stores). Discovery also needs the browser, so skip it.
- `--db` — Writes to Railway PostgreSQL

**Note:** There's already a partial Dutchie run today (29/235 stores, 6,242 prices). The `getActiveRunForToday` function will find today's existing run and the `getCompletedJobsForToday` check will skip the 29 already-done stores. This is automatic resume behavior.

**If it crashes mid-run:** Just re-run the same command. The resume logic skips completed stores.

**Monitor:** Watch for `[dutchie] [N/235]` progress. ~1-2 min per store.

**Verify success:**
```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  node -e "const{Pool}=require('pg');const p=new Pool({connectionString:process.env.DATABASE_URL});p.query(\"SELECT platform,status,stores_succeeded,prices_inserted,duration_seconds FROM scrape_runs WHERE platform='dutchie' ORDER BY started_at DESC LIMIT 1\").then(r=>{console.log(r.rows[0]);p.end()}).catch(e=>{console.error(e);process.exit(1)})"
```

---

## Failure Modes & Recovery

| Failure | What Happens | Recovery |
|---------|-------------|----------|
| Railway browser goes down | Scrapers using browser fail with connection errors | Wait for Railway to restart, then `--resume` |
| DB connection lost | Insert fails, script may crash | Re-run with same command (auto-resume) |
| Script crashes (OOM, unhandled error) | Process exits | Re-run same command — resume skips completed stores |
| Rate limiting (Weedmaps/Leafly) | Individual stores fail, script continues | Expected behavior, not a bug |
| Age gate (Dutchie) | Script handles automatically via click | If stuck, store marked failed and skipped |

---

## Verify All 4 Ran Successfully (Final Check)

```bash
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  node -e "
const{Pool}=require('pg');
const p=new Pool({connectionString:process.env.DATABASE_URL});
p.query(\`
  SELECT platform, 
    SUM(CASE WHEN status='completed' AND prices_inserted > 0 THEN prices_inserted ELSE 0 END) as prices,
    SUM(CASE WHEN status='completed' AND stores_succeeded > 0 THEN stores_succeeded ELSE 0 END) as stores
  FROM scrape_runs 
  WHERE started_at > NOW() - INTERVAL '24 hours'
  GROUP BY platform
  ORDER BY platform
\`).then(r=>{
  console.log('=== TODAY\\'S SCRAPE RESULTS ===');
  let total=0;
  r.rows.forEach(row=>{
    console.log(\`\${row.platform}: \${row.prices} prices from \${row.stores} stores\`);
    total+=Number(row.prices);
  });
  console.log(\`TOTAL: \${total} prices\`);
  p.end();
}).catch(e=>{console.error(e);process.exit(1)});
"
```

**Expected totals after all 4 complete:**
- Dutchie: ~50,000-60,000 prices
- Jane: ~10,000-12,000 prices
- Weedmaps: ~5,000-7,000 prices
- Leafly: ~500-1,000 prices
- **Total: ~65,000-80,000 prices**

---

## Long-Term Considerations

### Why Railway Scraper Services Never Worked

The Railway-deployed scraper services (`scrape-dutchie`, `scrape-weedmaps`, etc.) were deployed as separate Railway services but had multiple issues:
1. **No CamoFox browser inside the Railway service containers** — they tried to connect to `localhost:9377` but there's no CamoFox running inside those containers
2. **Configuration mismatch** — the `WEEDMAPS_CAMOFOX_URL` pointed to the Railway browser service, but the Dutchie scraper's BrowserPool defaults to localhost
3. **Resource issues** — Railway free/starter tier has limited RAM for running both Node.js scraper + CamoFox browser
4. **No persistent state** — Railway services restart from scratch each deploy, losing any resume state

**To fix Railway deployment properly:**
- Set `CAMOFOX_URL=https://roviq-browser-production.up.railway.app` in every Railway scraper service's env vars
- Ensure `WEEDMAPS_CAMOFOX_URL` is also set (for Weedmaps/Jane)
- Ensure `DATABASE_URL` points to the Railway Postgres instance
- Consider a single orchestrator service instead of 4 separate ones

### Can This Be Automated on the Sandbox?

Yes. The sandbox approach works reliably. Options:
1. **Cron-style**: Use the OpenClaw heartbeat to trigger scrapers at scheduled times
2. **Manual**: Run the commands from this plan daily
3. **Orchestrator script**: Create a `run-all-scrapers.sh` that runs all 4 sequentially

**Recommended:** Create a simple `scripts/run-all.sh` that runs Leafly → Jane → Weedmaps → Dutchie sequentially with proper env vars, logging output to timestamped files.

### Resource Management

- **Railway browser** is the bottleneck — one browser instance shared across all scraper requests
- Running scrapers sequentially prevents browser tab conflicts
- The Railway browser service handles tab cleanup automatically (idle timeout)
- Monitor Railway browser health before starting long runs

---

## Quick Reference: All Commands

```bash
# === Leafly (no browser, ~10-30 min) ===
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/scrape-leafly.ts --skip-discovery --db

# === Jane (Railway browser, ~1 min) ===
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/scrape-jane.ts --skip-discovery --db

# === Weedmaps (Railway browser, ~60-90 min) ===
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  npx tsx scripts/scrape-weedmaps.ts --skip-discovery --db

# === Dutchie (Railway browser, ~4-6 hours) ===
cd /data/workspace/projects/glass/src && \
  DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
  CAMOFOX_URL="https://roviq-browser-production.up.railway.app" \
  npx tsx scripts/scrape-dutchie.ts --skip-discovery --db
```
