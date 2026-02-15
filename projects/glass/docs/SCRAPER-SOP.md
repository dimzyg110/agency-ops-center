# GLASS Scraper Deployment SOP

This document provides step-by-step instructions for deploying and running GLASS scrapers locally and on Railway.

---

## Prerequisites

1. **Access:**
   - Railway account with access to GLASS project
   - PostgreSQL connection string (DATABASE_URL)
   - Discord webhook URL for notifications (optional)

2. **Local Development:**
   - Node.js 22+
   - Docker (for local testing)
   - `camoufox` browser binary (see below)

### Installing CamoFox

CamoFox is required for Dutchie, Leafly, and Weedmaps scrapers:

```bash
# Install camoufox binary (required before running scrapers)
npx camoufox fetch

# Verify installation
test -f ~/.cache/camoufox/camoufox-bin && echo "CamoFox installed"
```

---

## Running Locally

### Option 1: Full Docker Build

```bash
cd /data/workspace/projects/glass/src

# Build the Docker image
docker build -f scrapers/dutchie/Dockerfile -t glass-dutchie .

# Run with environment variables
docker run --rm \
  -e DATABASE_URL="postgresql://user:pass@host:port/database" \
  -e NODE_ENV=production \
  -e MAX_TIMEOUT_MS=10800000 \
  glass-dutchie
```

### Option 2: Direct Node Execution

```bash
cd /data/workspace/projects/glass/src

# Install dependencies
cd scrapers
npm install
cd ..

# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:port/database"
export NODE_ENV=production
export MAX_TIMEOUT_MS=10800000
export HEADLESS=true

# Run specific scraper
npx tsx scrapers/dutchie/index.ts
```

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:port/database` |
| `NODE_ENV` | Yes | Environment | `production` or `development` |
| `MAX_TIMEOUT_MS` | No | Hard timeout in milliseconds | `10800000` (3 hours) |
| `HEADLESS` | No | Run browser headless | `true` |
| `WEBHOOK_URL` | No | Discord webhook for notifications | Discord webhook URL |
| `JANE_ALGOLIA_APP_ID` | For Jane | Algolia app ID | `VFM4X0N23A` |
| `JANE_ALGOLIA_API_KEY` | For Jane | Algolia API key | `edc5435c65d771cecbd98bbd488aa8d3` |

---

## Deploying to Railway

### Method 1: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
cd /data/workspace/projects/glass/src
railway link

# Deploy specific scraper (from scrapers directory)
cd scrapers

# Dutchie
railway up --detach --service dutchie-scraper
# Select the GLASS project and create new service

# Or specify service name
railway up --detach --service dutchie-scraper --project GLASS
```

### Method 2: Git Integration

1. Push code to GitHub
2. Connect Railway to GitHub repo
3. Set up each scraper as a separate service
4. Configure the `railway.toml` in each scraper directory

### Configuring Scheduled Runs

1. Open Railway dashboard
2. Select the scraper service
3. Go to **Settings** → **Schedules**
4. Add cron schedule:

| Scraper | Cron (UTC) | Cron (ET) |
|---------|------------|-----------|
| Dutchie | `0 8 * * *` | `0 3 * * *` |
| Jane | `0 7 * * *` | `0 2 * * *` |
| Leafly | `5 7 * * *` | `5 2 * * *` |
| Weedmaps | `30 3 * * *` | `30 22 * * *` |

### Environment Setup on Railway

For each scraper service, set these variables in Railway dashboard:

```
DATABASE_URL=postgresql://postgres:password@turntable.proxy.rlwy.net:18582/railway
NODE_ENV=production
HEADLESS=true
MAX_TIMEOUT_MS=<scraper-specific-timeout>
```

---

## Adding a New Scraper

### Step 1: Create Scraper Directory

```bash
cd /data/workspace/projects/glass/src/scrapers
mkdir -p newplatform
```

### Step 2: Create Entry Point

Create `newplatform/index.ts`:

```typescript
#!/usr/bin/env node

import { pool, upsertOperator, upsertProduct, insertPrice, ... } from '../lib/db.js';
// ... imports

const PLATFORM = 'newplatform';
const DEFAULT_TIMEOUT_MS = 3600000; // 1 hour

async function main() {
  // 1. Acquire run lock
  const runLock = await acquireRunLock(PLATFORM);
  if (!runLock) {
    console.log('[newplatform] Another run in progress, exiting');
    return;
  }

  // 2. Create scrape run record
  const run = await createScrapeRun(PLATFORM);
  
  // 3. Scrape logic here
  // ...
  
  // 4. Complete scrape run
  await completeScrapeRun(run.id, stats);
  
  // 5. Cleanup
  await pool.end();
}

main().catch(async (err) => {
  console.error('[newplatform] Fatal error:', err);
  await notifyError(PLATFORM, err);
  process.exit(1);
});
```

### Step 3: Create Dockerfile

```dockerfile
# Newplatform Scraper — Railway Cron Service

FROM mcr.microsoft.com/playwright:v1.50.1-jammy

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    corepack enable && \
    npm install -g tsx@4

WORKDIR /app

COPY scrapers/package.json scrapers/package-lock.json* ./
RUN npm ci || npm install

RUN npx camoufox fetch

COPY scrapers/lib/ ./lib/
COPY scrapers/newplatform/ ./newplatform/
COPY scripts/lib/ ./scripts-lib/
COPY scripts/newplatform-slugs.json ./data/newplatform-slugs.json

ENV NODE_ENV=production
ENV HEADLESS=true
ENV MAX_TIMEOUT_MS=3600000

CMD ["tsx", "newplatform/index.ts"]
```

### Step 4: Create railway.toml

```toml
[build]
dockerfilePath = "scrapers/newplatform/Dockerfile"

[deploy]
startCommand = "tsx newplatform/index.ts"
restartPolicyType = "NEVER"
```

### Step 5: Add Slugs Data

Create `data/newplatform-slugs.json`:

```json
[
  {
    "slug": "store-name-1",
    "name": "Store Name 1",
    "city": "Boston",
    "state": "MA"
  }
]
```

### Step 6: Deploy

```bash
cd /data/workspace/projects/glass/src/scrapers
railway up --detach --service newplatform-scraper
```

---

## Monitoring

### Check Railway Logs

```bash
# View recent logs
railway logs --service dutchie-scraper --tail 100

# Follow logs in real-time
railway logs --service dutchie-scraper --tail
```

### Database Queries

```bash
# Connect to Railway database
PGPASSWORD=password psql -h turntable.proxy.rlwy.net -p 18582 -U postgres -d railway

# Check recent scrape runs
SELECT platform, status, started_at, stores_succeeded, stores_failed 
FROM scrape_runs 
ORDER BY started_at DESC 
LIMIT 10;

# Check for errors
SELECT platform, error_log 
FROM scrape_runs 
WHERE status = 'failed' 
ORDER BY started_at DESC 
LIMIT 5;
```

---

## Troubleshooting

### Common Issues

#### 1. "DATABASE_URL environment variable is required"

```bash
# Set the variable
export DATABASE_URL="postgresql://user:pass@host:port/database"
```

#### 2. "CamoFox unavailable"

```bash
# Reinstall CamoFox
npx camoufox fetch

# Or use plain Firefox for Jane scraper
# (Jane uses plain Firefox by design)
```

#### 3. "Target page, context or browser has been closed"

This is a browser crash. Check:
- Memory limits on Railway
- Timeout settings
- Browser pool exhaustion

#### 4. "Run lock already held"

Another scrape is running. Wait for it to complete or check for stuck processes:

```sql
SELECT * FROM scrape_runs 
WHERE status = 'running' 
AND started_at < now() - interval '1 hour';
```

---

## Quick Reference

### Start a Scrapy Manually (Railway)

```bash
railway run --service dutchie-scraper
```

### Force Restart Stuck Scraper

```bash
# Via Railway dashboard or CLI
railway redeploy --service dutchie-scraper
```

### Check Price Count by Platform

```sql
SELECT s.source_type, COUNT(p.id) as price_count
FROM prices p
JOIN sources s ON s.id = p.source_id
WHERE p.scraped_at > now() - interval '24 hours'
GROUP BY s.source_type;
```

### Update Slugs File

1. Edit `data/dutchie-slugs.json`
2. Rebuild and redeploy the Docker image

---

## Security Notes

- **Never commit** DATABASE_URL or other secrets to git
- Use Railway's environment variable encryption
- Rotate credentials periodically
- Use separate DB users for dev vs production if possible
