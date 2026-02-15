# GLASS Scraper Runbook

This is the operational handbook for running and maintaining GLASS scrapers. Use this when something goes wrong or you need to check status.

---

## Daily Checklist

1. [ ] Check Railway dashboard for scraper status
2. [ ] Verify prices were inserted yesterday
3. [ ] Check for failed runs in last 24 hours

---

## How to Check If Scrapers Are Running

### Method 1: Railway Dashboard

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select GLASS project
3. Check each scraper service status:
   - Green = running successfully
   - Red = failed
   - Gray = not running (expected between cron jobs)

### Method 2: Database Query

```sql
-- Check last 24 hours of scrape runs
SELECT 
  platform,
  status,
  started_at,
  completed_at,
  stores_succeeded,
  stores_failed,
  products_upserted
FROM scrape_runs
WHERE started_at > now() - interval '24 hours'
ORDER BY started_at DESC;
```

Expected output:
```
platform  | status    | started_at              | stores_succeeded
----------+-----------+-------------------------+------------------
 dutchie  | completed | 2026-02-15 08:00:00+00  | 235
 jane     | completed | 2026-02-15 07:00:00+00  | 39
 leafly   | completed | 2026-02-15 07:05:00+00  | 0
 weedmaps | completed | 2026-02-15 03:30:00+00  | 0
```

---

## How to Check Data in Database

### Check Price Counts by Platform

```sql
SELECT 
  s.source_type,
  COUNT(DISTINCT p.id) as total_prices,
  COUNT(DISTINCT DATE(p.scraped_at)) as days_of_data
FROM prices p
JOIN sources s ON s.id = p.source_id
GROUP BY s.source_type
ORDER BY s.source_type;
```

### Check Most Recent Prices

```sql
SELECT 
  p.price,
  p.weight_grams,
  pr.name as product_name,
  o.name as operator_name,
  s.source_type,
  p.scraped_at
FROM prices p
JOIN products pr ON pr.id = p.product_id
JOIN operators o ON o.id = p.operator_id
JOIN sources s ON s.id = p.source_id
ORDER BY p.scraped_at DESC
LIMIT 20;
```

### Check Sources Status

```sql
SELECT 
  source_type,
  status,
  COUNT(*) as count,
  COUNT(last_scraped_at) as scraped_count,
  COUNT(last_success_at) as success_count
FROM sources
GROUP BY source_type, status;
```

---

## Common Errors and Fixes

### Error: "browserContext.newPage: Target page, context or browser has been closed"

**Cause:** Browser crashed during scrape, usually due to:
- Memory exhaustion
- Page navigation timeout
- Cloudflare blocking

**Fix:**
1. Check Railway logs: `railway logs --service dutchie-scraper`
2. Check if it's a consistent issue or one-time
3. For Dutchie: This is a known issue - browser pool may be exhausting
4. Redeploy if needed: `railway redeploy --service dutchie-scraper`

### Error: "page.goto: Timeout"

**Cause:** Page took too long to load

**Fix:**
1. Check the store URL in the error
2. Verify the store is still active
3. Increase timeout if needed (but max is 6h for Dutchie)

### Error: "Run lock already held"

**Cause:** Previous scrape is still running or crashed without releasing lock

**Fix:**
```sql
-- Check for stuck runs
SELECT * FROM scrape_runs 
WHERE status = 'running' 
AND started_at < now() - interval '1 hour';

-- Manual fix - set to failed
UPDATE scrape_runs 
SET status = 'failed', 
    completed_at = now() 
WHERE id = '<run-id>' 
AND status = 'running';
```

### Error: "DATABASE_URL environment variable is required"

**Cause:** Missing DATABASE_URL in environment

**Fix:**
1. Check Railway service settings
2. Verify DATABASE_URL is set in environment variables

### Error: "CamoFox unavailable"

**Cause:** CamoFox binary not installed in Docker image

**Fix:**
1. Rebuild Docker image with `npx camoufox fetch`
2. Check Dockerfile has the fetch command

### Error: "Cloudflare challenge failed"

**Cause:** Bot detection triggered

**Fix:**
1. For Dutchie/Leafly/Weedmaps: Should use CamoFox
2. For Jane: This is expected but should pass through browser
3. Check if IP was blocked

---

## How to Restart/Re-run Scrapers

### Method 1: Railway Dashboard

1. Go to Railway dashboard
2. Select the scraper service
3. Click **Run** button

### Method 2: Railway CLI

```bash
# Run Dutchie scraper
railway run --service dutchie-scraper

# Or deploy and run
railway up --detach --service dutchie-scraper
railway run --service dutchie-scraper
```

### Method 3: Manual Trigger (Database)

Not recommended - scrapers should be triggered from Railway.

---

## Debugging Failed Runs

### Step 1: Get Error Details

```sql
SELECT 
  id,
  platform,
  started_at,
  completed_at,
  status,
  error_log,
  metadata
FROM scrape_runs
WHERE status = 'failed'
ORDER BY started_at DESC
LIMIT 5;
```

### Step 2: Check Store-Level Errors

```sql
SELECT 
  sj.source_id,
  s.url,
  sj.status,
  sj.error_message,
  sj.started_at
FROM scrape_jobs sj
JOIN sources s ON s.id = sj.source_id
JOIN scrape_runs sr ON sr.id = sj.run_id
WHERE sr.platform = 'dutchie'
AND sr.started_at > now() - interval '24 hours'
AND sj.status = 'failed'
LIMIT 20;
```

### Step 3: Check Logs

```bash
# All scraper logs
railway logs --service dutchie-scraper --tail 200

# Filter for errors
railway logs --service dutchie-scraper --tail 200 | grep -i error
```

---

## Recovery Procedures

### Scenario: All Scrapers Failing

1. **Check Railway status** - Is Railway experiencing issues?
2. **Check DATABASE_URL** - Can you connect?
   ```bash
   PGPASSWORD=password psql -h turntable.proxy.rlwy.net -p 18582 -U postgres -d railway -c "SELECT 1"
   ```
3. **Redeploy all scrapers**:
   ```bash
   railway redeploy --service dutchie-scraper
   railway redeploy --service jane-scraper
   railway redeploy --service leafly-scraper
   railway redeploy --service weedmaps-scraper
   ```

### Scenario: One Scraper Failing Consistently

1. **Check error logs** (see above)
2. **Check slugs file** - Is the store list valid?
3. **Test locally** - Run scraper locally to see full error
4. **Check website** - Has the platform changed their site?

### Scenario: Database Full

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('railway'));

-- Check largest tables
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Check old prices to purge
SELECT COUNT(*) FROM prices 
WHERE scraped_at < now() - interval '90 days';
```

---

## Emergency Contacts

- **Railway Support:** https://railway.app/support
- **Project Lead:** Randy

---

## Quick Commands Reference

```bash
# Check scraper status
railway status

# View logs
railway logs --service dutchie-scraper --tail 100

# Run scraper manually
railway run --service dutchie-scraper

# Redeploy
railway redeploy --service dutchie-scraper

# Connect to DB
PGPASSWORD=password psql -h turntable.proxy.rlwy.net -p 18582 -U postgres -d railway

# Query recent runs
psql -h turntable.proxy.rlwy.net -p 18582 -U postgres -d railway -c "SELECT platform, status, started_at FROM scrape_runs ORDER BY started_at DESC LIMIT 10;"
```

---

## Log Retention

- Railway logs: Last 1000 lines viewable in dashboard
- Database: All scrape_runs retained indefinitely
- Prices: Retained indefinitely (can be purged manually)
