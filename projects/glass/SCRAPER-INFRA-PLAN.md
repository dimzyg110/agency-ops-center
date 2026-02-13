# GLASS Scraper Infrastructure Plan

> **Status:** Proposed — awaiting approval  
> **Author:** Infrastructure Architecture Agent  
> **Date:** 2026-02-13  
> **Scope:** Complete redesign of scraper pipeline infrastructure for daily reliability

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Architecture (What's Broken)](#2-current-architecture-whats-broken)
3. [Proposed Architecture](#3-proposed-architecture)
4. [Detailed Answers to the 7 Questions](#4-detailed-answers-to-the-7-questions)
5. [Railway Service Specifications](#5-railway-service-specifications)
6. [Dockerfiles & Configuration](#6-dockerfiles--configuration)
7. [Orchestration & Monitoring](#7-orchestration--monitoring)
8. [Cost Estimates](#8-cost-estimates)
9. [Migration Plan (Step-by-Step)](#9-migration-plan-step-by-step)
10. [Risk Assessment](#10-risk-assessment)
11. [Future Optimizations](#11-future-optimizations)

---

## 1. Executive Summary

The GLASS scraper pipeline is the lifeblood of the product. If scrapers don't run, there's no data, and the product is dead. Today, the pipeline is fragile: scrapers share process space with the AI orchestrator, CamoFox crashes mid-run, zombie processes fill the process table, and there's no isolation between workloads.

**The fix:** Move all scraper execution to Railway as self-contained Docker services, each with its own browser instance. The OpenClaw sandbox becomes a pure orchestration/AI layer — it triggers scrapes but never runs them locally. Each scraper gets its own Railway service with an embedded CamoFox browser (no shared browser instances). A lightweight cron orchestrator triggers daily runs and monitors health.

**Key outcomes:**
- Scrapers run to completion regardless of AI agent activity
- Zero zombie process contamination between workloads
- Each scraper has a dedicated browser — no contention
- Dutchie parallelized from ~5 hours down to ~1.5 hours
- Daily automated runs with monitoring and retry
- Total estimated Railway cost: **$25-45/month** (usage-based)

---

## 2. Current Architecture (What's Broken)

```
┌──────────────────────────────────────────────────────────────────┐
│                   OPENCLAW SANDBOX                                │
│                   (single containerized Linux)                    │
│                                                                   │
│  ┌─────────────┐  ┌───────────────┐  ┌────────────────────┐     │
│  │ AI Agents   │  │ Dutchie       │  │ Weedmaps           │     │
│  │ (subagents) │  │ Scraper       │  │ Scraper            │     │
│  │             │  │ (tsx process) │  │ (tsx process)      │     │
│  │ Spawns tsx  │  │               │  │                    │     │
│  │ processes   │  │ Uses local    │  │ Uses Railway       │     │
│  │ that become │  │ CamoFox ──────│──│ roviq-browser ─────│──┐  │
│  │ zombies     │  │ :9377         │  │                    │  │  │
│  └──────┬──────┘  └───────┬───────┘  └────────────────────┘  │  │
│         │                 │                                    │  │
│         │     ┌───────────┴───────────┐                       │  │
│         │     │ CamoFox Plugin        │                       │  │
│         │     │ (single browser)      │                       │  │
│         │     │ localhost:9377         │                       │  │
│         │     │ CRASHES under load    │                       │  │
│         │     └───────────────────────┘                       │  │
│         │                                                      │  │
│         ▼ ZOMBIE PROCESSES (defunct tsx)                       │  │
│         fill process table → EAGAIN → can't fork()            │  │
│         kills ALL processes including scrapers                 │  │
└──────────────────────────────────────────────────────────────────┘
                                                                 │
                    ┌────────────────────────────────────────────┘
                    ▼
        ┌───────────────────────┐     ┌─────────────────────┐
        │ Railway roviq-browser │     │ Railway PostgreSQL   │
        │ (single CamoFox)     │     │ (GLASS DB)           │
        │ Used by Weedmaps     │     │                      │
        │ only                 │     │                      │
        └───────────────────────┘     └─────────────────────┘
```

### Failure Modes

| Failure | Frequency | Impact | Root Cause |
|---------|-----------|--------|------------|
| Zombie tsx processes | Every 10+ subagent tasks | EAGAIN kills all forking | Node subagents never reap children |
| CamoFox crash | 1-2x per Dutchie run | Scraper stalls, partial data | Memory/resource pressure from shared process space |
| Port 9377 held by zombie | After CamoFox crash | Can't restart browser | Dead camoufox-bin holds socket |
| Scraper killed by agent work | Intermittent | Partial data day | No process isolation, shared CPU/RAM |
| Single browser contention | Every run | Can't run Dutchie+Jane simultaneously on local | CamoFox is single-instance |

---

## 3. Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            RAILWAY PLATFORM                              │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ glass-scrape-     │  │ glass-scrape-     │  │ glass-scrape-     │      │
│  │ dutchie           │  │ weedmaps          │  │ jane              │      │
│  │                   │  │                   │  │                   │      │
│  │ Node.js + tsx     │  │ Node.js + tsx     │  │ Node.js + tsx     │      │
│  │ Embedded CamoFox  │  │ Embedded CamoFox  │  │ Embedded CamoFox  │      │
│  │ (Playwright +     │  │ (Playwright +     │  │ (Playwright +     │      │
│  │  camoufox)        │  │  camoufox)        │  │  camoufox)        │      │
│  │                   │  │                   │  │                   │      │
│  │ 3 worker shards   │  │ 1 worker (serial) │  │ 1 worker (fast)   │      │
│  │ ~235 stores       │  │ ~300 stores       │  │ ~39 stores        │      │
│  │ ~1.5 hrs total    │  │ ~3 hrs            │  │ ~1 min            │      │
│  └────────┬──────────┘  └────────┬──────────┘  └────────┬──────────┘      │
│           │                      │                      │                 │
│  ┌──────────────────┐                                                    │
│  │ glass-scrape-     │  ┌─────────────────────────────────────────┐      │
│  │ leafly            │  │                                          │      │
│  │                   │  │  Railway PostgreSQL (GLASS DB)           │      │
│  │ Node.js + tsx     │  │  postgresql://...@turntable.proxy.rlwy  │      │
│  │ Pure HTTP (no     │  │                                          │      │
│  │ browser needed)*  │  └─────────────────────────────────────────┘      │
│  │                   │           ▲        ▲        ▲        ▲            │
│  │ ~70 stores        │           │        │        │        │            │
│  │ ~5 min            │           └────────┴────────┴────────┘            │
│  └────────┬──────────┘      All scrapers write directly to DB            │
│           │                                                              │
└───────────┼──────────────────────────────────────────────────────────────┘
            │
            │
┌───────────┼──────────────────────────────────────────────────────────────┐
│           │          OPENCLAW SANDBOX (orchestration only)                │
│           │                                                              │
│  ┌────────┴────────┐                                                    │
│  │ Cron Orchestrator│     ┌───────────────┐                              │
│  │ (daily-scrape.ts)│────▶│ AI Agents     │  ← No longer share          │
│  │                  │     │ (subagents)   │    resources with scrapers   │
│  │ Triggers Railway │     │               │                              │
│  │ services via     │     │ Free to do    │                              │
│  │ Railway API or   │     │ heavy work    │                              │
│  │ HTTP webhook     │     │ without       │                              │
│  └──────────────────┘     │ killing       │                              │
│                           │ scrapers      │                              │
│                           └───────────────┘                              │
└──────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Each scraper = its own Railway service.** Complete process isolation. One scraper's crash or OOM cannot affect another.

2. **Browser is embedded in each scraper service**, not a shared external API. The scraper service starts its own CamoFox/Playwright browser at process start, uses it throughout the run, and exits when done. No HTTP API hop — direct Playwright calls.

3. **Leafly stays HTTP-only for now.** The Leafly scraper currently uses `consumer-api.leafly.com` (pure HTTP). If Cloudflare blocks this, Leafly gets CamoFox too (same pattern as Jane). But today it works without a browser.

4. **Scrapers run as Railway "cron services"** (or one-off deploys triggered by Railway API). They spin up, run, write to DB, exit. You don't pay for idle time.

5. **OpenClaw sandbox never runs scrapers.** It only triggers them and monitors results.

---

## 4. Detailed Answers to the 7 Questions

### Q1: Architecture — How to isolate scrapers from AI orchestrator?

**Answer: Separate Railway services.**

Not Docker containers on the same host (still shares kernel/cgroup). Not separate processes with resource limits (zombie problem persists). Fully separate Railway services — different containers, different hosts, different process trees.

Why Railway over alternatives:
- **Already in use** — roviq-browser proves the pattern works
- **Usage-based pricing** — scrapers only run 5-8 hours/day, rest is free
- **No infrastructure to manage** — no EC2 instances, no Kubernetes
- **Simple deployment** — Dockerfile + `railway up`
- **Built-in cron** — Railway supports cron schedules natively

Why not GitHub Actions:
- 6-hour job timeout limit would barely cover Dutchie
- No persistent storage for resume state
- Browser-in-CI is fragile and expensive on runners
- Concurrency limits on free plans

### Q2: CamoFox strategy — 4 instances or pooled?

**Answer: Embedded browser per service, no shared pool.**

Current architecture uses CamoFox as an HTTP API (`roviq-browser`). This adds an unnecessary network hop and creates a single point of failure. The proposed architecture **embeds the browser directly in each scraper process**.

Each Railway scraper service:
1. Starts → launches `camoufox` (or falls back to `playwright firefox`)
2. Runs scrape loop with direct Playwright API calls (no HTTP intermediary)
3. Finishes → browser exits with process

**Why not pool/share?**
- Browser sessions accumulate memory leaks — a fresh browser per run is healthier
- Scheduling is simpler (no contention management)
- Isolation is total (one bad site can't poison another scraper's browser state)
- The HTTP API abstraction adds latency (each snapshot is an HTTP round-trip)

**What about roviq-browser?** Keep it for ad-hoc browser tasks (AI agent CamoFox operations, debugging). But scraper production runs should not depend on it.

### Q3: Zombie prevention

**Answer: Problem eliminated by design.**

Zombies occur because:
1. AI subagent spawns tsx child processes in the OpenClaw sandbox
2. These children become defunct (parent doesn't waitpid)
3. Process table fills up → `fork()` returns EAGAIN

Moving scrapers to Railway means:
- Scrapers never share a PID namespace with AI agents
- Each Railway service has its own container with its own PID 1 (init)
- When the scraper process exits, the container exits — all children are reaped
- No accumulation possible across runs

For the sandbox itself (AI agents): Consider adding a periodic zombie reaper:
```bash
# Add to sandbox cron or heartbeat
while true; do sleep 300; kill -9 $(ps -eo pid,ppid,stat | awk '$3~/^Z/{print $1}') 2>/dev/null; done &
```

But this is a **defense-in-depth** measure. The primary fix is: scrapers don't run in the sandbox.

### Q4: Orchestration — How to trigger and monitor daily scrapes?

**Answer: Railway cron services + health check from sandbox.**

**Triggering:**

Railway supports cron schedules on services. Each scraper service gets a cron schedule:

| Scraper | Cron (ET) | Duration | Strategy |
|---------|-----------|----------|----------|
| Jane | `0 2 * * *` (2:00 AM) | ~1 min | Runs first (fastest, validates browser health) |
| Leafly | `5 2 * * *` (2:05 AM) | ~5 min | Runs second (HTTP only, fast) |
| Dutchie | `15 2 * * *` (2:15 AM) | ~1.5 hrs | Starts after quick scrapers validate infra |
| Weedmaps | `15 2 * * *` (2:15 AM) | ~3 hrs | Runs parallel with Dutchie |

**Monitoring:**

Each scraper writes run results to `scrape_runs` table. A lightweight monitor checks:

```sql
-- "Did all 4 scrapers complete today?"
SELECT platform, status, stores_succeeded, stores_failed, duration_seconds
FROM scrape_runs
WHERE started_at >= CURRENT_DATE
ORDER BY started_at DESC;
```

The OpenClaw heartbeat cycle (already running every 15 min) adds a check:
1. After 7:00 AM ET, query `scrape_runs` for today
2. If any platform is missing or failed, alert via Discord
3. If Dutchie completion rate < 80%, flag for investigation

**Retries:**

Each scraper supports `--resume <run-id>`. If a run fails:
1. Monitor detects the failure
2. Triggers a re-run with `--resume` flag (skips completed stores)
3. Railway API: `POST /v1/services/{serviceId}/deploy` with env override `SCRAPE_ARGS=--resume <run-id>`

For Railway cron services, a simpler approach: the scraper checks on startup if there's an incomplete run from today and auto-resumes it.

### Q5: Leafly migration

**Answer: Leafly doesn't need CamoFox today. Monitor and prepare.**

Current state (verified from code):
- `leafly-client.ts` uses **pure HTTP** via `consumer-api.leafly.com/api/dispensaries/v1/{slug}/menu_items`
- Discovery uses HTML scraping of `leafly.com/dispensaries/massachusetts`
- No browser needed — Leafly's API returns JSON directly

If Cloudflare blocks the API:
1. **Quick fix (hours):** Add CamoFox browser proxy (same pattern as `jane-client.ts`)
2. **Deploy:** Already in Railway, just add browser deps to `glass-scrape-leafly` Dockerfile
3. **Pattern:** Navigate to `leafly.com`, get Cloudflare clearance, proxy API calls through `page.evaluate(fetch(...))`

**Prep now:** Build the `glass-scrape-leafly` service with browser dependencies included but disabled. The Dockerfile includes Playwright/camoufox, but the scraper uses HTTP by default. Add a `--use-browser` flag that switches to browser-proxied mode.

### Q6: Concurrency — Parallelizing Dutchie

**Answer: Yes. 3 shards, ~1.5 hours instead of ~5.**

Dutchie's 235 stores are independent. Each store scrape takes ~75 seconds average. Currently serial with concurrency=1.

**Proposed: Shard the store list across 3 parallel workers within one Railway service.**

```
┌────────────────────────────────────────────────────┐
│           glass-scrape-dutchie (Railway)            │
│                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │ Worker 0    │ │ Worker 1    │ │ Worker 2    │  │
│  │ Stores 0-78 │ │ Stores 79-156│ │Stores 157-234│  │
│  │ Own browser │ │ Own browser │ │ Own browser │  │
│  │ context     │ │ context     │ │ context     │  │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘  │
│         └───────────┬───┴───────────┬───┘          │
│                     ▼               ▼              │
│              Shared DB pool (max 20 conns)         │
│              Single process, Promise.all           │
└────────────────────────────────────────────────────┘
```

Implementation:
```typescript
// In scrape-dutchie.ts, add sharding support
const SHARD_COUNT = Number(process.env.DUTCHIE_SHARDS || '3');

async function main() {
  const stores = await loadSlugs(args.slugsFile);
  
  // Create N browser contexts (same browser, different contexts)
  const browser = await camoufox({ headless: true });
  const shards = Array.from({ length: SHARD_COUNT }, (_, i) => {
    const start = Math.floor(i * stores.length / SHARD_COUNT);
    const end = Math.floor((i + 1) * stores.length / SHARD_COUNT);
    return stores.slice(start, end);
  });
  
  // Run shards in parallel
  await Promise.all(shards.map((shardStores, i) => 
    processShard(browser, shardStores, i)
  ));
}
```

**Why 3 shards, not 5 or 10?**
- Each browser context uses ~200-400MB RAM
- 3 contexts ≈ 1.2GB RAM — fits comfortably in Railway's 2GB default
- Diminishing returns past 3: the bottleneck becomes Dutchie's rate limiting, not our parallelism
- 235 stores ÷ 3 = ~78 stores per shard × 75 sec = ~1.5 hours

### Q7: Cost

**Answer: $25-45/month estimated.**

Railway pricing (Pro plan, usage-based):
- **CPU:** $0.000463/min per vCPU
- **RAM:** $0.000231/min per GB
- **No charge when container isn't running**

| Service | Runtime/Day | vCPU | RAM | Monthly Cost |
|---------|------------|------|-----|-------------|
| glass-scrape-dutchie | 1.5 hrs | 2 vCPU | 2 GB | ~$5.50 |
| glass-scrape-weedmaps | 3 hrs | 1 vCPU | 1.5 GB | ~$4.50 |
| glass-scrape-jane | 2 min | 1 vCPU | 1 GB | ~$0.30 |
| glass-scrape-leafly | 5 min | 0.5 vCPU | 512 MB | ~$0.20 |
| Railway Postgres | 24/7 | shared | 1 GB | ~$5-10 |
| Railway Redis (if used) | 24/7 | shared | 256 MB | ~$3-5 |
| **Total** | | | | **~$19-26** |

Add 30-50% buffer for retries, failed runs, discovery phases: **$25-45/month**.

**Compared to current cost:** roviq-browser runs 24/7 on Railway even though Weedmaps only needs it for 3 hours. Moving to cron-based services could actually **save money** vs the current always-on browser service.

**Note:** Railway Pro plan is $5/seat/month base. If not already on Pro, add $5.

---

## 5. Railway Service Specifications

### Service: `glass-scrape-dutchie`

| Property | Value |
|----------|-------|
| **Type** | Cron service |
| **Cron** | `15 2 * * *` (America/New_York) |
| **Source** | `Roviq-AI/glass` repo |
| **Root directory** | `/` |
| **Dockerfile** | `infra/scraper-dutchie/Dockerfile` |
| **Start command** | `node scraper.mjs` |
| **CPU** | 2 vCPU |
| **RAM** | 2 GB |
| **Env vars** | `DATABASE_URL`, `DUTCHIE_SHARDS=3`, `SCRAPER_CONCURRENCY=1` |

### Service: `glass-scrape-weedmaps`

| Property | Value |
|----------|-------|
| **Type** | Cron service |
| **Cron** | `15 2 * * *` (America/New_York) |
| **Source** | `Roviq-AI/glass` repo |
| **Root directory** | `/` |
| **Dockerfile** | `infra/scraper-weedmaps/Dockerfile` |
| **Start command** | `node scraper.mjs` |
| **CPU** | 1 vCPU |
| **RAM** | 1.5 GB |
| **Env vars** | `DATABASE_URL` |

### Service: `glass-scrape-jane`

| Property | Value |
|----------|-------|
| **Type** | Cron service |
| **Cron** | `0 2 * * *` (America/New_York) |
| **Source** | `Roviq-AI/glass` repo |
| **Root directory** | `/` |
| **Dockerfile** | `infra/scraper-jane/Dockerfile` |
| **Start command** | `node scraper.mjs` |
| **CPU** | 1 vCPU |
| **RAM** | 1 GB |
| **Env vars** | `DATABASE_URL` |

### Service: `glass-scrape-leafly`

| Property | Value |
|----------|-------|
| **Type** | Cron service |
| **Cron** | `5 2 * * *` (America/New_York) |
| **Source** | `Roviq-AI/glass` repo |
| **Root directory** | `/` |
| **Dockerfile** | `infra/scraper-leafly/Dockerfile` |
| **Start command** | `node scraper.mjs` |
| **CPU** | 0.5 vCPU |
| **RAM** | 512 MB |
| **Env vars** | `DATABASE_URL` |

---

## 6. Dockerfiles & Configuration

### Base Dockerfile (shared pattern for browser-enabled scrapers)

```dockerfile
# infra/scraper-base/Dockerfile.browser
# Base image for scrapers that need CamoFox/Playwright
FROM mcr.microsoft.com/playwright:v1.50.1-jammy

# Install Node.js 22 (Playwright image has Node 18)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    corepack enable

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

# Install camoufox binary
RUN npx camoufox fetch || true

# Copy scraper code
COPY src/scripts/ ./scripts/
COPY tsconfig.json ./

# Build (if using tsc) or run directly with tsx
RUN npm install -g tsx

# Default env
ENV NODE_ENV=production
ENV HEADLESS=true
```

### Dutchie Dockerfile

```dockerfile
# infra/scraper-dutchie/Dockerfile
FROM mcr.microsoft.com/playwright:v1.50.1-jammy

# Node 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g tsx

WORKDIR /app

# Copy package files and install deps
COPY package.json package-lock.json* ./
RUN npm ci

# Install camoufox browser binary
RUN npx camoufox fetch || true

# Copy scraper source
COPY src/scripts/ ./scripts/

# Entrypoint script
COPY infra/scraper-dutchie/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

ENV NODE_ENV=production
ENV HEADLESS=true
ENV DUTCHIE_SHARDS=3

CMD ["./entrypoint.sh"]
```

**Dutchie entrypoint:**

```bash
#!/bin/bash
# infra/scraper-dutchie/entrypoint.sh
set -euo pipefail

echo "=== GLASS Dutchie Scraper — $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="
echo "Shards: ${DUTCHIE_SHARDS:-3}"

# Run the scraper with embedded browser (no external CamoFox dependency)
exec tsx scripts/scrape-dutchie.ts \
  --skip-discovery \
  --db \
  ${SCRAPE_ARGS:-}
```

### Weedmaps Dockerfile

```dockerfile
# infra/scraper-weedmaps/Dockerfile
FROM mcr.microsoft.com/playwright:v1.50.1-jammy

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g tsx

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

RUN npx camoufox fetch || true

COPY src/scripts/ ./scripts/

COPY infra/scraper-weedmaps/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

ENV NODE_ENV=production
ENV HEADLESS=true

CMD ["./entrypoint.sh"]
```

### Jane Dockerfile

```dockerfile
# infra/scraper-jane/Dockerfile
FROM mcr.microsoft.com/playwright:v1.50.1-jammy

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g tsx

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

RUN npx camoufox fetch || true

COPY src/scripts/ ./scripts/

COPY infra/scraper-jane/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

ENV NODE_ENV=production
ENV HEADLESS=true

CMD ["./entrypoint.sh"]
```

### Leafly Dockerfile (lightweight — no browser)

```dockerfile
# infra/scraper-leafly/Dockerfile
FROM node:22-bookworm-slim

RUN npm install -g tsx

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

COPY src/scripts/ ./scripts/

COPY infra/scraper-leafly/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

ENV NODE_ENV=production

CMD ["./entrypoint.sh"]
```

### Railway Configuration

Each service gets a `railway.toml` in its infra directory:

```toml
# infra/scraper-dutchie/railway.toml
[build]
dockerfilePath = "infra/scraper-dutchie/Dockerfile"

[deploy]
startCommand = "./entrypoint.sh"
healthcheckPath = ""
restartPolicyType = "NEVER"
cronSchedule = "15 2 * * *"
```

```toml
# infra/scraper-weedmaps/railway.toml
[build]
dockerfilePath = "infra/scraper-weedmaps/Dockerfile"

[deploy]
startCommand = "./entrypoint.sh"
restartPolicyType = "NEVER"
cronSchedule = "15 2 * * *"
```

```toml
# infra/scraper-jane/railway.toml
[build]
dockerfilePath = "infra/scraper-jane/Dockerfile"

[deploy]
startCommand = "./entrypoint.sh"
restartPolicyType = "NEVER"
cronSchedule = "0 2 * * *"
```

```toml
# infra/scraper-leafly/railway.toml
[build]
dockerfilePath = "infra/scraper-leafly/Dockerfile"

[deploy]
startCommand = "./entrypoint.sh"
restartPolicyType = "NEVER"
cronSchedule = "5 2 * * *"
```

---

## 7. Orchestration & Monitoring

### Daily Flow

```
2:00 AM ET  → Jane scraper fires (Railway cron)
              - Takes ~1 min
              - Validates browser+DB connectivity
              - Writes to scrape_runs table

2:05 AM ET  → Leafly scraper fires (Railway cron)
              - Takes ~5 min
              - Pure HTTP, validates API is up
              - Writes to scrape_runs table

2:15 AM ET  → Dutchie + Weedmaps fire simultaneously (Railway cron)
              - Dutchie: 3 shards, ~1.5 hrs → done by ~3:45 AM
              - Weedmaps: serial, ~3 hrs → done by ~5:15 AM
              - Both write to scrape_runs table

6:00 AM ET  → OpenClaw heartbeat checks scrape_runs
              - Verifies all 4 platforms have today's completed run
              - Checks success rates (Dutchie >80%, Weedmaps >50%, Jane >90%, Leafly >80%)
              - If failures: alerts via Discord, optionally triggers retry
```

### Auto-Resume Logic

Each scraper should check for incomplete runs on startup:

```typescript
// Add to each scraper's main()
async function main() {
  // Check for incomplete run from today
  const existingRun = await getActiveRunForToday(PLATFORM);
  if (existingRun) {
    console.log(`Resuming incomplete run: ${existingRun}`);
    args.resume = existingRun;
  }
  // ... rest of scrape logic
}
```

This means if a cron fires and a previous run was interrupted, it automatically resumes rather than starting fresh.

### Monitoring Query (for heartbeat)

```sql
-- Check today's scrape health
WITH today_runs AS (
  SELECT 
    platform,
    status,
    stores_succeeded,
    stores_failed,
    stores_succeeded::float / NULLIF(stores_succeeded + stores_failed, 0) AS success_rate,
    duration_seconds,
    started_at,
    completed_at
  FROM scrape_runs
  WHERE started_at >= CURRENT_DATE
  ORDER BY started_at DESC
)
SELECT * FROM today_runs;
```

### Discord Alert Template

```
🔴 GLASS Scraper Alert — {date}

Missing runs: {missing_platforms}
Failed runs: {failed_details}

Dutchie: {success}/{total} stores ({rate}%)
Weedmaps: {success}/{total} stores ({rate}%)
Jane: {success}/{total} stores ({rate}%)
Leafly: {success}/{total} stores ({rate}%)

Action needed: {action}
```

---

## 8. Cost Estimates

### Monthly Railway Costs (Detailed)

**Assumptions:**
- Railway Pro plan ($5/seat base)
- Usage-based pricing: CPU $0.000463/vCPU-min, RAM $0.000231/GB-min
- 30 days/month

#### glass-scrape-dutchie
- Runtime: 1.5 hrs/day × 30 = 2,700 min/month
- CPU: 2 vCPU × 2,700 min × $0.000463 = **$2.50**
- RAM: 2 GB × 2,700 min × $0.000231 = **$1.25**
- **Subtotal: $3.75/month**

#### glass-scrape-weedmaps
- Runtime: 3 hrs/day × 30 = 5,400 min/month
- CPU: 1 vCPU × 5,400 min × $0.000463 = **$2.50**
- RAM: 1.5 GB × 5,400 min × $0.000231 = **$1.87**
- **Subtotal: $4.37/month**

#### glass-scrape-jane
- Runtime: 2 min/day × 30 = 60 min/month
- CPU: 1 vCPU × 60 min × $0.000463 = **$0.03**
- RAM: 1 GB × 60 min × $0.000231 = **$0.01**
- **Subtotal: $0.04/month**

#### glass-scrape-leafly
- Runtime: 5 min/day × 30 = 150 min/month
- CPU: 0.5 vCPU × 150 min × $0.000463 = **$0.03**
- RAM: 0.5 GB × 150 min × $0.000231 = **$0.02**
- **Subtotal: $0.05/month**

#### Existing services (already paid)
- Railway PostgreSQL: ~$5-10/month (already running)
- roviq-browser (can be removed): ~$8-12/month saved

### Total New Spend

| Item | Monthly |
|------|---------|
| glass-scrape-dutchie | $3.75 |
| glass-scrape-weedmaps | $4.37 |
| glass-scrape-jane | $0.04 |
| glass-scrape-leafly | $0.05 |
| Retry buffer (+30%) | $2.47 |
| **New scraper total** | **$10.68** |
| Savings (remove roviq-browser 24/7) | -$8 to -$12 |
| **Net new cost** | **~$0-3/month** |

**Bottom line: This migration is roughly cost-neutral** because the always-on roviq-browser service costs more than 4 cron-based scraper services.

---

## 9. Migration Plan (Step-by-Step)

### Phase 0: Preparation (Day 1, ~2 hours)

**Goal:** Set up infra directory structure, test locally.

1. Create directory structure in the glass repo:
   ```
   infra/
   ├── scraper-dutchie/
   │   ├── Dockerfile
   │   ├── entrypoint.sh
   │   └── railway.toml
   ├── scraper-weedmaps/
   │   ├── Dockerfile
   │   ├── entrypoint.sh
   │   └── railway.toml
   ├── scraper-jane/
   │   ├── Dockerfile
   │   ├── entrypoint.sh
   │   └── railway.toml
   └── scraper-leafly/
       ├── Dockerfile
       ├── entrypoint.sh
       └── railway.toml
   ```

2. Refactor `BrowserPool` to support **embedded mode** (direct Playwright, no HTTP API):
   ```typescript
   // browser-pool.ts additions
   export class EmbeddedBrowserPool {
     private browser: Browser | null = null;
     
     async init(): Promise<void> {
       // Try camoufox first, fall back to playwright firefox
       try {
         const { camoufox } = await import('camoufox');
         this.browser = await camoufox({ headless: true });
       } catch {
         this.browser = await firefox.launch({ headless: true });
       }
     }
     
     async createTab(url: string): Promise<{ tabId: string; page: Page }> {
       const context = await this.browser.newContext({ /* realistic options */ });
       const page = await context.newPage();
       await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
       return { tabId: randomUUID(), page };
     }
     // ... same interface as BrowserPool but with direct Playwright calls
   }
   ```

3. Add environment flag to switch between HTTP API mode and embedded mode:
   ```typescript
   const pool = process.env.BROWSER_MODE === 'embedded'
     ? new EmbeddedBrowserPool()
     : new BrowserPool(3, { baseUrl: process.env.CAMOFOX_URL });
   ```

4. Test locally: run each scraper with `BROWSER_MODE=embedded` and `--limit 2 --db`

### Phase 1: Jane + Leafly on Railway (Day 2, ~3 hours)

**Goal:** Prove the pattern with the two fastest/simplest scrapers.

1. **Create `glass-scrape-jane` Railway service:**
   - Railway dashboard → Project → + New → Docker
   - Point to glass repo, set Dockerfile path
   - Set `DATABASE_URL` env var (reference Railway Postgres)
   - Set `BROWSER_MODE=embedded`
   - Set cron schedule: `0 2 * * *`

2. **Create `glass-scrape-leafly` Railway service:**
   - Same process, uses lightweight Dockerfile (no browser)
   - Set cron schedule: `5 2 * * *`

3. **Test both services:**
   - Trigger manual deploy on Railway
   - Verify `scrape_runs` table has new entries
   - Verify product/price data is correct

4. **Disable sandbox runs** for Jane and Leafly (remove from any local cron/orchestrator)

### Phase 2: Weedmaps on Railway (Day 3, ~3 hours)

**Goal:** Migrate the service that already uses Railway browser.

1. **Create `glass-scrape-weedmaps` Railway service:**
   - Dockerfile with embedded browser
   - Env: `DATABASE_URL`, `BROWSER_MODE=embedded`
   - Cron: `15 2 * * *`

2. **Modify `scrape-weedmaps.ts`:**
   - Remove dependency on `WEEDMAPS_CAMOFOX_URL` in embedded mode
   - Use direct Playwright/camoufox for page operations

3. **Test with `--limit 5 --db`** on Railway

4. **Full test run** — let cron trigger overnight, verify next morning

5. **Once confirmed:** Consider removing `roviq-browser` service (saves $8-12/month). Keep it if AI agents still need ad-hoc browser access.

### Phase 3: Dutchie on Railway + Parallelization (Day 4-5, ~6 hours)

**Goal:** Migrate the longest, most complex scraper and speed it up.

1. **Add sharding support to `scrape-dutchie.ts`:**
   ```typescript
   const SHARD_COUNT = Number(process.env.DUTCHIE_SHARDS || '1');
   
   // Split stores into shards
   const shards = splitIntoShards(stores, SHARD_COUNT);
   
   // Launch parallel browser contexts
   const browser = await initBrowser();
   const results = await Promise.allSettled(
     shards.map((shardStores, i) => runShard(browser, shardStores, i, args))
   );
   ```

2. **Create `glass-scrape-dutchie` Railway service:**
   - Dockerfile with embedded browser
   - Env: `DATABASE_URL`, `BROWSER_MODE=embedded`, `DUTCHIE_SHARDS=3`
   - Cron: `15 2 * * *`
   - Resources: 2 vCPU, 2 GB RAM

3. **Test with `--limit 15 --db`** (5 per shard) on Railway

4. **Full test run** — verify all 235 stores complete in ~1.5 hours

5. **Remove local Dutchie execution** from sandbox

### Phase 4: Monitoring & Hardening (Day 6, ~3 hours)

1. **Add auto-resume logic** to all scrapers (check for incomplete run on startup)

2. **Add heartbeat monitoring query** to OpenClaw's 15-minute cycle:
   ```typescript
   // In heartbeat, after 7 AM ET:
   const today = new Date().toISOString().slice(0, 10);
   const runs = await db.query(`
     SELECT platform, status, stores_succeeded, stores_failed
     FROM scrape_runs WHERE started_at::date = $1
   `, [today]);
   
   // Alert if missing or failed
   ```

3. **Add Discord notification** on scraper completion (each scraper sends a webhook at end of run)

4. **Test failure recovery:**
   - Kill a Dutchie run mid-flight
   - Verify next cron trigger resumes
   - Verify monitoring alerts fire

### Phase 5: Cleanup (Day 7, ~2 hours)

1. **Remove local CamoFox dependency** from scraper scripts
2. **Update `SCRAPER-ARCHITECTURE.md`** to reflect new Railway-based architecture
3. **Update `run-daily-dutchie.sh`** to be a Railway trigger script (or deprecate)
4. **Remove `services/scrape/` legacy service** (formally archive)
5. **Optionally decommission `roviq-browser`** if no other consumers

### Timeline Summary

| Phase | Duration | What | Risk |
|-------|----------|------|------|
| 0 | Day 1 | Prep, refactor BrowserPool | Low — local only |
| 1 | Day 2 | Jane + Leafly on Railway | Low — fast scrapers, easy rollback |
| 2 | Day 3 | Weedmaps on Railway | Medium — longer run, more pages |
| 3 | Day 4-5 | Dutchie + parallelization | Medium — complex scraper, sharding logic |
| 4 | Day 6 | Monitoring + hardening | Low — additive |
| 5 | Day 7 | Cleanup + docs | Low — documentation |

**Total: 5-7 working days** with one developer agent focused on it.

---

## 10. Risk Assessment

### Risk: CamoFox doesn't install in Playwright Docker image

**Likelihood:** Medium  
**Mitigation:** The `roviq-browser` service already proves this works — it uses `mcr.microsoft.com/playwright:v1.50.1-jammy` with `camoufox` package. If `camoufox fetch` fails, Playwright's built-in Firefox is the fallback (it works for Dutchie and Weedmaps, just without anti-detection stealth).  
**Escalation:** If Cloudflare detects Playwright Firefox, use a custom `camoufox` Docker image (build from the camoufox repo directly).

### Risk: Railway cron service has cold start latency

**Likelihood:** Medium  
**Impact:** Low — adds 30-60 seconds to start time  
**Mitigation:** Acceptable for scrapers that run for hours. Jane (1 min total) could be affected more, but even 60s cold start is fine.

### Risk: Dutchie rate-limits parallel shards

**Likelihood:** Medium  
**Impact:** Some stores get blocked, reducing success rate  
**Mitigation:** 
1. Each shard uses a different browser context (different cookies/session)
2. Inter-request jitter (1.5-3.5s) already built in
3. Monitor: if success rate drops below 80%, reduce to 2 shards
4. Shards share the same IP (Railway egress). If this is an issue, add proxy rotation as a future optimization.

### Risk: Database connection exhaustion with parallel workers

**Likelihood:** Low  
**Impact:** Connection errors during scrape runs  
**Mitigation:** Current pool is `max: 20` connections. With 3 Dutchie shards + 1 Weedmaps + 1 Jane + 1 Leafly all running simultaneously, that's ~6 clients hitting the same DB. Each needs 2-3 connections max. Railway Postgres default limit is 100 connections. No issue.

### Risk: Scraper code changes require Railway redeployment

**Likelihood:** High (it's a feature, not a bug)  
**Impact:** Deployment latency for fixes  
**Mitigation:** 
1. Railway auto-deploys on git push (if connected to repo)
2. Manual trigger via `railway up` or dashboard
3. Can test locally first with `BROWSER_MODE=embedded tsx scripts/scrape-*.ts --limit 2`

---

## 11. Future Optimizations

### Short-term (Month 1-2)

- **Proxy rotation for Dutchie:** If 3 shards from same IP causes rate limiting, add residential proxy pool (~$20-40/month for ~5GB bandwidth)
- **Structured logging:** Replace console.log with structured JSON → Railway log explorer becomes queryable
- **Metrics endpoint:** Add Prometheus metrics to each scraper for grafana-style dashboards
- **Adaptive scheduling:** If a scraper consistently finishes early, tighten the schedule; if late, add buffer

### Medium-term (Month 2-4)

- **Store discovery automation:** Run discovery (new store detection) weekly instead of relying on static slug files
- **Multi-state expansion:** When expanding beyond Massachusetts, shard by state
- **Browser fingerprint rotation:** Rotate camoufox profiles to avoid long-term fingerprint tracking
- **Webhook notifications:** Scraper completion triggers webhook → updates dashboard, sends Slack/Discord

### Long-term (Month 4+)

- **Dedicated scraper queue:** Replace cron with BullMQ-based job queue on Railway for fine-grained retry/priority
- **Cost optimization:** Move to Fly.io or self-hosted if Railway costs grow beyond $100/month
- **Data quality pipeline:** Post-scrape validation service that checks for anomalies before data hits the consumer-facing DB

---

## Appendix A: Key Code Changes Required

### 1. `browser-pool.ts` — Add EmbeddedBrowserPool

Create a new class that uses direct Playwright API instead of HTTP. It should implement the same interface (`createTab`, `snapshot`, `click`, `scroll`, `closeTab`, `handleAgeGate`, `evaluate`) but call `page.*` methods directly instead of fetching `http://localhost:9377/*`.

### 2. `scrape-dutchie.ts` — Add sharding

- Accept `DUTCHIE_SHARDS` env var
- Split store list into N chunks
- Create N browser contexts from one browser instance
- Process chunks in parallel with `Promise.allSettled`
- Each chunk uses its own context (isolated cookies/sessions)
- Aggregate results from all chunks into single `scrape_runs` entry

### 3. `jane-client.ts` — Add embedded browser mode

Currently uses HTTP API to create tabs on remote CamoFox. Add direct Playwright mode:
```typescript
// If BROWSER_MODE=embedded, use direct Playwright
if (process.env.BROWSER_MODE === 'embedded') {
  const browser = await camoufox({ headless: true });
  const page = await browser.newPage();
  await page.goto(JANE_HOME_URL);
  // Use page.evaluate() directly instead of HTTP proxy
}
```

### 4. `config.ts` — Add Railway-specific defaults

```typescript
export const BROWSER_MODE = process.env.BROWSER_MODE || 'http'; // 'http' | 'embedded'
export const DUTCHIE_SHARDS = Number(process.env.DUTCHIE_SHARDS || '1');
```

### 5. Entrypoint scripts — Add auto-resume

Each entrypoint should:
1. Check for incomplete run from today in `scrape_runs` table
2. If found, pass `--resume <run_id>` to the scraper
3. If not found, start fresh

---

## Appendix B: Environment Variables Reference

| Variable | Service | Description | Example |
|----------|---------|-------------|---------|
| `DATABASE_URL` | All | Railway Postgres connection string | `postgresql://...@turntable.proxy.rlwy.net:18582/railway` |
| `BROWSER_MODE` | Dutchie, Weedmaps, Jane | `embedded` for Railway, `http` for sandbox | `embedded` |
| `CAMOFOX_URL` | Dutchie, Weedmaps (http mode only) | CamoFox HTTP API URL | `http://localhost:9377` |
| `DUTCHIE_SHARDS` | Dutchie | Number of parallel browser contexts | `3` |
| `SCRAPER_CONCURRENCY` | All | Per-shard concurrency (keep at 1) | `1` |
| `SCRAPE_ARGS` | All | Additional CLI args for retry/resume | `--resume abc-123` |
| `HEADLESS` | Dutchie, Weedmaps, Jane | Browser headless mode | `true` |
| `NODE_ENV` | All | Runtime environment | `production` |

---

## Appendix C: Rollback Plan

If Railway services fail and we need to revert to sandbox execution:

1. **Stop Railway cron services** (disable schedule in dashboard)
2. **Verify local CamoFox** is running: `curl http://localhost:9377/health`
3. **Run scrapers locally** as before:
   ```bash
   # Jane
   DATABASE_URL=$GLASS_DB npx tsx scripts/scrape-jane.ts --skip-discovery --db
   # Leafly
   DATABASE_URL=$GLASS_DB npx tsx scripts/scrape-leafly.ts --skip-discovery --db
   # Dutchie
   DATABASE_URL=$GLASS_DB bash scripts/run-daily-dutchie.sh
   # Weedmaps
   WEEDMAPS_CAMOFOX_URL=https://roviq-browser-production.up.railway.app \
   DATABASE_URL=$GLASS_DB npx tsx scripts/scrape-weedmaps.ts --skip-discovery --db
   ```

The code changes are backward-compatible — `BROWSER_MODE=http` (default) preserves the old behavior exactly.

---

*This document is the implementation blueprint. A developer agent should be able to execute Phase 0-5 from this spec alone without additional architectural decisions needed.*
