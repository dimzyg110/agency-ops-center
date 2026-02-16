# ZeroClaw Agent Assignments

> Created: 2026-02-16 (Sunday)
> For: @glass, @clients, @roviq
> Reference: TASKS.md

---

## 🤖 @glass — The Builder

**Role:** CTO & Lead Engineer  
**Focus:** GLASS platform, scrapers, data pipelines, technical infrastructure

### 📦 Workspace Requirements

| Item | Details | Priority |
|------|---------|----------|
| **GLASS Project** | `projects/glass/` — Next.js app, API routes, DB schema | 🔴 P0 |
| **Database** | Railway Postgres — `postgresql://postgres:***@turntable.proxy.rlwy.net:18582/railway` | 🔴 P0 |
| **Scraper Config** | Firecrawl, Playwright, CamoFox keys | 🔴 P0 |
| **Bot-bus Access** | For inter-agent messaging | 🟡 P1 |
| **GitHub Access** | Push to `Roviq-AI/glass` repo | 🔴 P0 |

### 🎯 Assigned Tasks

#### 🔥 TONIGHT (Sunday Night)
- [ ] **Fix Weedmaps scraper** — currently broken, debug and deploy
- [ ] **Get Jane.com scraper running** — nightly run
- [ ] **Get Dutchie scraper running** — nightly run
- [ ] **Fix Leafly scraper** — nightly run
- [ ] **Set up daily automation + monitoring** — cron jobs, alerts

#### This Week (P1)
- [ ] **Delivery waitlist flow** — area input → waitlist capture
- [ ] **Map + Near Me view** — Google Maps style, mobile-first
- [ ] **Dispensary claim system** — interactive claiming
- [ ] **Get all CH products verified** — run through parser

#### This Week (P2)
- [ ] **Better analytics + comparisons** — benchmarking tools
- [ ] **Security audit** — AI pentest before launch
- [ ] **Weedmaps scraping improvement** — productionize

### 📋 Dependencies
- Needs GLASS repo synced to workspace
- Needs Postgres connection string in env
- Needs scraper API keys (Firecrawl, etc.)

---

## 🎨 @clients — The Creative

**Role:** Creative Director & Account Manager  
**Focus:** AC, CH, HOP deliverables — design, content, social, websites

### 📦 Workspace Requirements

| Item | Details | Priority |
|------|---------|----------|
| **Client Folders** | `clients/ac/`, `clients/ch/`, `clients/hop/` | 🔴 P0 |
| **CH Web Repo** | `randytorres/ch-web` — React+Vite+Tailwind | 🔴 P0 |
| **Roviq Social Tool** | `Roviq-AI/social-tool` — Gemini content engine | 🔴 P0 |
| **Vertex API Key** | For Nano Banana Pro image generation | 🔴 P0 |
| **Canva/Design Tools** | For social content | 🟡 P1 |
| **GitHub Access** | Push to client repos | 🔴 P0 |

### 🎯 Assigned Tasks

#### 🔥 TONIGHT (Sunday Night)
- [ ] **AC Social Flow Setup**
  - Get Vertex API working for Nano Banana Pro (images)
  - Test Seedance Pro 2 OR Veo 3.2 (Vertex) for videos
  - Create test output for review
- [ ] **AC Game Plan Doc** — Start strategy doc using GLASS data

#### This Week (P1)
- [ ] **AC Growth Strategy**
  - IG + TikTok strategy (no flower/plant content)
  - TikTok video concepts with Nano Banana Pro + Seedance 2.0
  - LinkedIn content strategy
  - Use live COAs from AC website for social proof
  - Prerolls promotion flow

- [ ] **CH Web**
  - Merge PR with SEO links: https://github.com/randytorres/ch-web/pulls
  - Finalize CH pages
  - 4-week content schedule

- [ ] **Roviq Social Engine**
  - GTM Plan for GlassIntel
  - Set up auto-create for Instagram/TikTok content
  - Configure guardrails (no spam, human-sounding)

#### This Week (P2)
- [ ] **CH Campaigns**
  - 420 push campaign
  - World Cup campaign
  - Billboards coordination

- [ ] **NeCann Promotion** — AC event promotion

### 📋 Dependencies
- Needs Vertex API key configured
- Needs access to CH web repo
- Needs social-tool repo synced
- Coordinate with @glass on CH product data

---

## 🧠 @roviq — The Operator (That's Me)

**Role:** COO & Revenue Orchestrator  
**Focus:** Internal ops, revenue pipeline, agent coordination

### 📦 Workspace Requirements

| Item | Details | Priority |
|------|---------|----------|
| **Main Workspace** | `agency-ops-center/` — TASKS.md, memory, docs | 🔴 P0 |
| **Bot-bus Access** | Message relay between agents | 🔴 P0 |
| **Discord** | #general channel for agent comms | 🔴 P0 |

### 🎯 My Tasks

- [ ] **Coordinate** — Assign work, track progress, resolve blockers
- [ ] **Review** — Every deliverable gets 2+ reviews before reaching Randy
- [ ] **Sync** — Daily check-ins with @glass and @clients
- [ ] **Revenue** — Keep pipeline moving, surface opportunities

---

## 🚀 Tonight's Kickoff Message

Copy/paste for #general:

```
📋 **SUNDAY NIGHT SPRINT — ASSIGNMENTS**

**@glass** — GLASS / Tech
P0 Tonight:
→ Fix Weedmaps scraper (broken)
→ Get Jane.com + Dutchie + Leafly running nightly
→ Set up daily automation + monitoring
Report back when done or blocked.

**@clients** — Clients / Creative
P0 Tonight:
→ AC: Get Vertex API working for Nano Banana Pro (images)
→ AC: Test video generation (Seedance Pro 2 or Veo 3.2)
→ AC: Start AC Game Plan doc
→ CH: Merge SEO links PR
Report back when done or blocked.

@roviq will coordinate and review. Let's go.
```

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| GLASS Site | https://glassintel.xyz |
| AC Website | (need URL) |
| CH Website | (need URL) |
| Glass Repo | https://github.com/Roviq-AI/glass |
| CH Web Repo | https://github.com/randytorres/ch-web |
| Social Tool | https://github.com/Roviq-AI/social-tool |
| TASKS.md | /data/workspace/TASKS.md |
