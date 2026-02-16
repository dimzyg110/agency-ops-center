# ZeroClaw Agent Assignments

> Created: 2026-02-16 (Sunday)
> For: @glass, @clients, @roviq
> Reference: TASKS.md

---

## 🗂️ Source of Truth — Task Tracker

Canonical tracker file: `services/zeroclaw/workspace/TASK-TRACKER.md`

Required fields per task row:
- `task_id`
- `owner`
- `priority`
- `state`
- `pr_url`
- `updated_at`
- `blocker_reason`

Allowed workflow state machine:
`UNCLAIMED → CLAIMED → IN_PROGRESS → PR_OPEN → IN_REVIEW → CHANGES_REQUESTED → APPROVED → MERGED → DONE`

One-task invariant per lane: exactly one task maximum in active states (`CLAIMED`, `IN_PROGRESS`, `PR_OPEN`, `IN_REVIEW`, `CHANGES_REQUESTED`).

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

## 🧠 @roviq — Dev Shop

**Role:** Full-service dev lane  
**Focus:** Engineering, architecture, automation, research, general building

**Note:** The COO role (coordination, revenue, agent management) is handled by the main COO agent (this session). @roviq agent does the building.

### 📦 Workspace Requirements

| Item | Details | Priority |
|------|---------|----------|
| **GLASS Project** | `projects/glass/` — Next.js app, API routes | 🔴 P0 |
| **Social Tool** | `Roviq-AI/social-tool` | 🔴 P0 |
| **Lead Tool** | Scripts for automated outreach | 🔴 P0 |
| **GitHub Access** | Push to Roviq repos | 🔴 P0 |

### 🎯 Priority List

#### P0 (Tonight)
- [ ] Help @glass with scrapers if needed
- [ ] Support @clients with Vertex API setup

#### P1 (This Week)
- [ ] Social content engine (Gemini automation for GlassIntel)
- [ ] LinkedIn automation setup (with guardrails)
- [ ] Automated dispensary outreach with snapshots
- [ ] Any technical tasks from @clients

#### P2
- [ ] Improve/extend lead tool
- [ ] New automation ideas

---

## ⚠️ WORKFLOW ENFORCEMENT

**Every task follows this cycle:**

```
UNCLAIMED → CLAIMED → IN_PROGRESS → PR_OPEN → IN_REVIEW
→ (CHANGES_REQUESTED → IN_PROGRESS)* → APPROVED → MERGED → DONE
```

Execution protocol:
1. ONE TASK AT A TIME — claim top priority work in `TASK-TRACKER.md`
2. DO THE WORK — complete scoped changes on a branch
3. OPEN PR — push branch, create PR, write PR notes, set tracker `PR_OPEN`
4. REVIEW FLOW — @roviq assigns reviewers; review format must follow `team/QA.md`
5. APPLY FEEDBACK — if `CHANGES_REQUESTED`, resume same task immediately (no new task pickup)
6. APPROVE + MERGE — only after review approval, then update tracker to `MERGED` then `DONE`
7. REPEAT — pick next unclaimed highest-priority task

Assignment precedence:
1. Explicit tagged assignment from @roviq
2. P-level priority in this file
3. Backlog order

**Never:**
- Work on multiple P0 tasks simultaneously
- Skip the PR → review → merge cycle
- Merge your own code
- Report "done" without a PR link and terminal tracker state

## ✅ Definition of Done

A task is done only when all are true:
- Scope in assignment is implemented and validated
- PR is merged to target branch
- Review completed using `team/QA.md` format and no blocking issues remain
- `TASK-TRACKER.md` updated with current `state`, `pr_url`, `updated_at`, and `blocker_reason` (if any)
- Any handoff notes or follow-ups are recorded in the task row or linked PR

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| GLASS Site | https://glassintel.xyz |
| Glass Repo | https://github.com/Roviq-AI/glass |
| CH Web Repo | https://github.com/randytorres/ch-web |
| Social Tool | https://github.com/Roviq-AI/social-tool |
