# GLASS Scraper Architecture

This document describes the GLASS price scraper infrastructure - what scrapers exist, how they work, where they run, and how data flows.

---

## Overview

GLASS has **4 platform scrapers** that collect dispensary menu prices from major cannabis platforms:

| Platform | Scraper | Browser | Timeout | Schedule (UTC) | Schedule (ET) |
|---------|---------|---------|---------|---------------|---------------|
| Dutchie | `dutchie/index.ts` | CamoFox | 6h | 08:00 | 03:00 |
| Jane    | `jane/index.ts` | Plain Firefox | 10m | 07:00 | 02:00 |
| Leafly  | `leafly/index.ts` | CamoFox | 30m | 07:05 | 02:05 |
| Weedmaps| `weedmaps/index.ts` | CamoFox | 4h | 03:30 | 22:30 |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCRAPER INFRASTRUCTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Dutchie   │    │    Jane    │    │   Leafly    │   │  Weedmaps   │  │
│  │  (CamoFox)  │    │  (Firefox) │    │  (CamoFox)  │   │  (CamoFox)  │  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│         │                  │                  │                  │         │
│         └──────────────────┴──────────────────┴──────────────────┘         │
│                                       │                                     │
│                                       ▼                                     │
│                         ┌─────────────────────────┐                          │
│                         │   Railway PostgreSQL    │                          │
│                         │  turntable.proxy.rlwy   │                          │
│                         │     .net:18582/railway  │                          │
│                         └────────────┬────────────┘                          │
│                                      │                                      │
│                                      ▼                                      │
│                         ┌─────────────────────────┐                          │
│                         │      public schema      │                          │
│                         │                         │                          │
│                         │  - scrape_runs          │                          │
│                         │  - scrape_jobs          │                          │
│                         │  - sources              │                          │
│                         │  - prices               │                          │
│                         │  - operators            │                          │
│                         │  - products             │                          │
│                         └─────────────────────────┘                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Scraper Details

### 1. Dutchie Scraper

**Location:** `src/scrapers/dutchie/index.ts`

**Purpose:** Scrape dispensary menus powered by Dutchie (the largest cannabis menu platform)

**How it works:**
- Launches CamoFox anti-detection browser
- Reads store slugs from `data/dutchie-slugs.json` (~470 stores)
- Navigates to each dispensary's Dutchie menu page
- Extracts product data from page DOM
- Parses prices, weights, product names
- Upserts data to `prices` table

**Database writes:**
- `scrape_runs` - tracks each scrape execution
- `scrape_jobs` - tracks per-store scrape status  
- `sources` - updates source metadata (last scraped time)
- `prices` - inserts/updates price records
- `operators` - upserts dispensary operators
- `products` - upserts products

**Key environment variables:**
- `DATABASE_URL` - PostgreSQL connection
- `MAX_TIMEOUT_MS=10800000` (3 hours)
- `DUTCHIE_SHARD_COUNT=2` - parallel browser instances

**Current issues:**
- High failure rate with "browser context closed" errors
- Some stores return 0 products despite having menus

---

### 2. Jane Scraper (iHeartJane)

**Location:** `src/scrapers/jane/index.ts`

**Purpose:** Scrape menus from iHeartJane.com

**How it works:**
- Uses plain Firefox (not CamoFox - different anti-detection approach)
- Navigates to www.iheartjane.com to pass Cloudflare
- Uses `page.evaluate(fetch())` to call Algolia API from browser context
- This carries real TLS fingerprints + Cloudflare cookies
- Fetches product data via Algolia search API

**Database writes:** Same as Dutchie (scrape_runs, prices, operators, products)

**Key environment variables:**
- `DATABASE_URL` - PostgreSQL connection
- `MAX_TIMEOUT_MS=600000` (10 minutes)
- `JANE_ALGOLIA_APP_ID` - Algolia app ID
- `JANE_ALGOLIA_API_KEY` - Algolia API key

**Schedule:** Runs at 07:00 UTC (2:00 AM ET)

---

### 3. Leafly Scraper

**Location:** `src/scrapers/leafly/index.ts`

**Purpose:** Scrape dispensary menus from Leafly.com

**How it works:**
- Uses CamoFox browser (required - Cloudflare blocks HTTP API)
- Reads store slugs from `data/leafly-slugs.json` (~292 stores)
- Navigates to Leafly store pages
- Extracts `__NEXT_DATA__` JSON from page
- Parses menu items from the JSON

**Database writes:** Same as other scrapers

**Key environment variables:**
- `DATABASE_URL` - PostgreSQL connection
- `MAX_TIMEOUT_MS=1800000` (30 minutes)

**Schedule:** Runs at 07:05 UTC (2:05 AM ET)

---

### 4. Weedmaps Scraper

**Location:** `src/scrapers/weedmaps/index.ts`

**Purpose:** Scrape menus from Weedmaps.com

**How it works:**
- Uses CamoFox browser
- Reads store slugs from `data/weedmaps-slugs.json` (~284 stores)
- Navigates to dispensary menu pages
- Extracts product data from page

**Database writes:** Same as other scrapers

**Key environment variables:**
- `DATABASE_URL` - PostgreSQL connection
- `MAX_TIMEOUT_MS=14400000` (4 hours)

**Schedule:** Runs at 03:30 UTC (10:30 PM ET)

---

## Shared Infrastructure

### Library Code (`src/scrapers/lib/`)

| File | Purpose |
|------|---------|
| `db.ts` | PostgreSQL connection pool, CRUD for scrape_runs/prices |
| `browser.ts` | Browser launch utilities (CamoFox, plain Firefox) |
| `timeout.ts` | Hard timeout enforcement, run ID tracking |
| `run-lock.ts` | Prevents concurrent scraper runs |
| `notify.ts` | Discord/Slack notifications on completion/failure |
| `runtime-preflight.ts` | Validates environment at startup |

### Scripts Library (`src/scrapers/scripts-lib/`)

| File | Purpose |
|------|---------|
| `parser.ts` | Dutchie HTML parsing |
| `jane-parser.ts` | Jane/Algolia response parsing |
| `leafly-parser.ts` | Leafly JSON parsing |
| `weedmaps-parser.ts` | Weedmaps HTML parsing |
| `normalizer.ts` | Product name/brand normalization |
| `types.ts` | TypeScript interfaces |

---

## Database Schema

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `scrape_runs` | Track each scraper execution | `platform`, `status`, `started_at`, `completed_at`, `stores_succeeded`, `stores_failed`, `error_log` |
| `scrape_jobs` | Per-store scrape status | `source_id`, `status`, `started_at`, `completed_at` |
| `sources` | Dispensary source URLs | `operator_id`, `source_type`, `url`, `last_scraped_at`, `last_success_at` |
| `prices` | Price records | `product_id`, `source_id`, `operator_id`, `price`, `scraped_at`, `confidence` |
| `operators` | Dispensary entities | `name`, `city`, `state`, `source_platform` |
| `products` | Product catalog | `name`, `brand`, `category`, `unit_weight_grams` |

### Source Type Distribution (Current)

```
source_type | count 
------------+-------
 dutchie    |   470
 jane       |    42
 leafly     |   292
 weedmaps   |   284
 menu       |     9
 website    |     6
```

---

## Deployment

### Railway Project

Each scraper is deployed as a **separate Railway service** with:
- **Dockerfile**: `scrapers/*/Dockerfile`
- **railway.toml**: `scrapers/*/railway.toml`
- **Schedule**: Cron via Railway's scheduled deployments
- **Restart policy**: `NEVER` (one-shot execution)

### Build Configuration

Each scraper's `railway.toml`:
```toml
[build]
dockerfilePath = "scrapers/dutchie/Dockerfile"

[deploy]
startCommand = "tsx dutchie/index.ts"
restartPolicyType = "NEVER"
```

### Environment Variables (Railway)

Set in Railway dashboard for each service:
- `DATABASE_URL` - PostgreSQL connection string
- `NODE_ENV=production`
- `HEADLESS=true`
- `MAX_TIMEOUT_MS` - per-scraper timeout

---

## Current Status (2026-02-15)

### Recent Activity

| Platform | Last Run | Status | Stores |
|----------|----------|--------|--------|
| Dutchie | 2026-02-15 11:43 UTC | FAILED | 0 succeeded |
| Jane | 2026-02-15 05:03 UTC | COMPLETED | 39 succeeded |
| Leafly | 2026-02-15 05:10 UTC | COMPLETED | 0 succeeded |
| Weedmaps | 2026-02-15 05:03 UTC | FAILED | 0 succeeded |

### Known Issues

1. **Dutchie failures**: Multiple "browser context closed" errors causing cascading failures
2. **Leafly/Weedmaps**: Currently showing 0 products despite running
3. **Jane**: Working but only capturing 42 stores vs 470 Dutchie

### Price Data

- Total price records: **319,929**
- Scrape runs tracked: **78**
- Scrape jobs: **5,528**
- Sources configured: **1,103**

---

## Files Reference

```
src/scrapers/
├── lib/
│   ├── db.ts                    # Database operations
│   ├── browser.ts               # Browser launch utilities
│   ├── timeout.ts               # Timeout enforcement
│   ├── run-lock.ts              # Run locking
│   ├── notify.ts                # Notifications
│   └── runtime-preflight.ts     # Startup validation
├── scripts-lib/
│   ├── parser.ts                # Dutchie parser
│   ├── jane-parser.ts           # Jane parser
│   ├── leafly-parser.ts         # Leafly parser
│   ├── weedmaps-parser.ts      # Weedmaps parser
│   ├── normalizer.ts            # Product normalization
│   └── types.ts                 # TypeScript types
├── data/
│   ├── dutchie-slugs.json      # ~470 Dutchie store slugs
│   ├── jane-slugs.json         # Jane store slugs
│   ├── leafly-slugs.json       # Leafly store slugs
│   └── weedmaps-slugs.json     # Weedmaps store slugs
├── dutchie/
│   ├── index.ts                 # Dutchie scraper entry
│   ├── Dockerfile               # Docker build
│   └── railway.toml             # Railway config
├── jane/
│   ├── index.ts                 # Jane scraper entry
│   ├── Dockerfile
│   └── railway.toml
├── leafly/
│   ├── index.ts
│   ├── Dockerfile
│   └── railway.toml
└── weedmaps/
    ├── index.ts
    ├── Dockerfile
    └── railway.toml
```
