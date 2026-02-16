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
| **Scraper Config** | Playwright, CamoFox (NO Firecrawl) | 🔴 P0 |
| **Bot-bus Access** | For inter-agent messaging | 🟡 P1 |
| **GitHub Access** | Push to `Roviq-AI/glass` repo | 🔴 P0 |

### 🎯 Priority List

#### P0 (Do First)
- [ ] Fix Weedmaps scraper (broken)
- [ ] Get Jane.com scraper running nightly
- [ ] Get Dutchie scraper running nightly
- [ ] Fix Leafly scraper nightly
- [ ] Set up daily scraper automation + monitoring

#### P1
- [ ] Delivery waitlist flow (area input → waitlist capture)
- [ ] Map + Near Me view (Google Maps style, mobile-first)
- [ ] Dispensary claim system
- [ ] Get all CH products verified

#### P2
- [ ] Better analytics + comparisons
- [ ] Security audit (AI pentest before launch)
- [ ] Weedmaps scraping improvement

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

### 🎯 Priority List

#### P0 (Do First)
- [ ] AC: Get Vertex API working for Nano Banana Pro (images)
- [ ] AC: Test video generation (Seedance Pro 2 OR Veo 3.2 from Vertex)
- [ ] AC: Start AC Game Plan doc
- [ ] CH: Merge SEO links PR

#### P1
- [ ] AC Growth Strategy (IG + TikTok, no flower/plant)
- [ ] AC TikTok video concepts (Nano Banana Pro + Seedance 2.0)
- [ ] AC LinkedIn content strategy
- [ ] AC Use live COAs for social proof
- [ ] AC Prerolls promotion flow
- [ ] CH Finalize pages
- [ ] CH 4-week content schedule
- [ ] Roviq GTM Plan for GlassIntel
- [ ] Roviq Social Engine setup (auto-create IG/TikTok)

#### P2
- [ ] CH 420 push campaign
- [ ] CH World Cup campaign
- [ ] CH Billboards
- [ ] AC NeCann promotion

---

## 🧠 @roviq — The Operator

**Role:** COO & Revenue Orchestrator  
**Focus:** Internal ops, revenue pipeline, agent coordination

### 🎯 Tasks
- Coordinate assignments
- Track progress
- Resolve blockers
- Review every deliverable (2+ reviews before Randy sees it)

---

## ⚠️ WORKFLOW ENFORCEMENT

**Every task follows this cycle:**

```
1. ONE TASK AT A TIME — pick the highest priority not yet started
2. DO THE WORK — complete the task fully
3. OPEN PR — push branch, create PR, write PR notes
4. SPAWN REVIEWER — @roviq spawns a subagent to review (different model)
5. GET APPROVED — @roviq synthesizes feedback → Approve / Request Changes
6. MERGE — @roviq merges to main (only after approval)
7. REPEAT — move to next priority task
```

**Never:**
- Work on multiple P0 tasks simultaneously
- Skip the PR → review → merge cycle
- Merge your own code
- Report "done" without a PR link

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| GLASS Site | https://glassintel.xyz |
| Glass Repo | https://github.com/Roviq-AI/glass |
| CH Web Repo | https://github.com/randytorres/ch-web |
| Social Tool | https://github.com/Roviq-AI/social-tool |
