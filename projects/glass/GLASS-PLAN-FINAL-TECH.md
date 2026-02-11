# GLASS Final Technical Build Plan
## Web-Only, GLASS-Revenue, Aggressive Scraping

**Version:** 1.0  
**Date:** 2026-02-11  
**Status:** Final execution plan

---

## 1. Locked Decisions

These are final and should not be reopened during implementation.

1. GLASS is **web only** for MVP and Phase 2. No React Native app.
2. Revenue reporting is **GLASS-only**. Do not mix in full Delivered or AC topline.
3. Scraping strategy is **aggressive by default**. Firecrawl and AI agents are core infrastructure, not optional helpers.
4. Build target is Massachusetts first, with depth over breadth.

---

## 2. Scope and Success Criteria

## Product scope (MVP to Week 12)
- Morning Brief dashboard
- Price Wire
- Threat Radar
- Margin Engine v1 (rules + basic model)
- Alerting and exports
- Operator onboarding (web)

## Success criteria by Week 12
1. 20 active operators
2. 95 percent+ scrape coverage for top 50 MA operators
3. Data freshness under 6 hours for full scans
4. Watched SKU deltas under 60 minutes
5. Threat alerts published within 24 hours of source release
6. Margin recommendations with operator adoption above 30 percent

---

## 3. System Architecture (Web Only)

## 3.1 Frontend
- React + TypeScript + Vite
- Tailwind + Recharts
- PWA shell for mobile web use
- No native mobile codebase in this plan

## 3.2 Backend
- Node.js + Fastify (modular monolith)
- Background workers for scraping, parsing, alerts
- Python ML service (FastAPI) for Margin Engine scoring

## 3.3 Data Layer
- PostgreSQL: core entities and transactional data
- ClickHouse: time-series price history and analytics
- Redis: queue, cache, rate control, job state
- S3: raw source snapshots and parse artifacts

## 3.4 Queue and Jobs
- BullMQ over Redis
- Queue classes:
  - `scrape.full`
  - `scrape.delta`
  - `parse.normalize`
  - `ccc.ingest`
  - `alerts.compute`
  - `margin.score`

## 3.5 Why modular monolith first
- Faster delivery with smaller coordination overhead
- Easier debugging in first 90 days
- Split into services only after proven load bottlenecks

---

## 4. Aggressive Scraping Architecture (Firecrawl + Agents)

## 4.1 Ingestion Strategy

Use a multi-path ingestion system so coverage survives source changes.

1. **Primary path:** Firecrawl extraction for known menu pages and collections
2. **Fallback path:** Playwright workers for dynamic JS sites and anti-bot changes
3. **Tertiary path:** AI-agent assisted rescue jobs for parser breakage and edge sources

## 4.2 Source Registry

Every source tracked in `source_registry` with:
- operator_id
- source_type (`dutchie`, `leafly`, `jane`, `custom`)
- url
- preferred_method (`firecrawl`, `playwright`)
- fallback_method
- auth_required (bool)
- status (`active`, `degraded`, `paused`)
- freshness_sla_minutes

## 4.3 Parsing Pipeline

1. Pull raw content (HTML/JSON/text) via Firecrawl or Playwright
2. Run deterministic parser per provider
3. Run LLM extraction only when parser confidence is low
4. Normalize to canonical schema:
   - SKU name
   - brand
   - category
   - quantity
   - price
   - promo flags
   - availability
5. Score confidence and store parse traces
6. Route low-confidence rows to QA queue

## 4.4 AI Agent Roles in Scraping

1. **Parser Maintainer Agent:** patches broken selectors/parsers
2. **Normalization Agent:** updates brand/SKU dictionaries
3. **Anomaly Agent:** reviews large price swings and suspicious deltas
4. **Coverage Agent:** finds missing stores/pages and adds registry candidates

Each agent produces files and PRs in owned directories only.

## 4.5 Scheduling

- Full scrape: every 6 hours (aligned to ET reporting windows)
- Watched SKU delta scrape: every 60 minutes
- Auto-rescrape on anomaly trigger
- Nightly backfill repair for failed jobs

## 4.6 Observability

Track at minimum:
- scrape_success_rate by source type
- median scrape latency
- parser_confidence distribution
- percent stale records > 6h
- coverage by operator and category

Hard alerts:
- Any top-50 operator stale > 8h
- Source success < 85 percent over 3 runs
- Parser confidence drop > 20 percent day-over-day

---

## 5. GLASS-Only Revenue Model (Reporting Standard)

All dashboards and planning models must use this accounting standard.

## Count as GLASS revenue
- Premium Analytics subscriptions
- Margin Engine Pro subscriptions
- Cue platform fees paid to GLASS
- Delivered referral fee paid to GLASS
- AC Toll referral/commission paid to GLASS

## Do not count as GLASS revenue
- Total Delivered GMV
- Total AC processing revenue
- Non-GLASS agency contracts unless sourced and tagged by GLASS pipeline

## Required metrics
- MRR (GLASS recognized)
- ARPO (average recognized revenue per operator)
- Gross margin by line
- LTV/CAC based on recognized revenue only

---

## 6. Build Phases and Technical Steps

## Phase 0 (Week 0)
1. Finalize contracts package (API + event schemas)
2. Freeze canonical data model
3. Stand up CI/CD, environments, secrets vault
4. Define coding ownership map by directory

## Phase 1 (Weeks 1-2): Foundation
1. Create backend skeleton (Fastify modules)
2. Create DB schema v1 (operators, sources, products, prices, alerts)
3. Set up queues and worker framework
4. Build frontend app shell and auth

## Phase 2 (Weeks 3-4): Scraping Core
1. Implement source registry and scheduler
2. Ship Firecrawl connector
3. Ship Playwright fallback workers
4. Build normalization pipeline + confidence scoring
5. Launch QA queue for low-confidence rows

## Phase 3 (Weeks 5-6): Price Wire + Morning Brief
1. Build Price Wire API endpoints
2. Build Morning Brief web screen
3. Add watchlists and watched-SKU deltas
4. Add data freshness timestamps and operator-level status

## Phase 4 (Weeks 7-8): Threat Radar
1. Build CCC ingestion workers
2. Add entity extraction + geocoding
3. Compute threat scoring and radius matching
4. Deliver Threat Radar UI and alerts

## Phase 5 (Weeks 9-10): Margin Engine v1
1. Rules engine for margin guardrails
2. Basic elasticity model service
3. Recommendation API with confidence and rationale
4. Apply workflow creates tasks, no auto-write by default

## Phase 6 (Weeks 11-12): Pilot and Hardening
1. Operator onboarding for first 20
2. Reliability fixes on scraping and alerting
3. Export/reporting v1
4. KPI checkpoint and scope decision for next phase

## Phase 7 (Weeks 13-20): Spokes and Scale
1. Cue integration
2. Delivered toggle
3. AC Toll workflow
4. Expand coverage and performance tuning

---

## 7. Parallel Agent Execution Without Conflicts

## 7.1 Ownership Lanes (Mandatory)

- `apps/web/**` -> Frontend Agent
- `services/api/**` -> Backend Agent
- `services/scrape/**` -> Scraping Agent
- `services/intelligence/**` -> Threat Agent
- `services/ml/**` -> ML Agent
- `infra/**` -> Platform Agent
- `contracts/**` -> Contract Agent (shared gatekeeper)
- `db/migrations/**` -> Migration Agent (single owner per sprint)

Agents must not edit outside their owned paths unless explicitly assigned.

## 7.2 Contract-First Rule

1. Any API/event change starts in `contracts/**`
2. Contract PR merges first
3. Consumer and producer lanes implement against versioned contract
4. CI blocks incompatible changes

## 7.3 Branch and PR Rules

- Branch pattern: `codex/<lane>-<task>`
- Small PRs, target under 500 changed lines when possible
- Rebase on `main` daily
- Merge window twice daily (midday and end of day ET)

## 7.4 Migration Safety

- One migration owner per sprint
- Additive migrations only during sprint
- Destructive migrations require dedicated release window

## 7.5 CI Gates (Block Merge if Failed)

1. Typecheck + lint
2. Unit tests
3. Contract compatibility checks
4. Migration safety checks
5. Smoke tests for critical endpoints

## 7.6 Review Protocol

Every major PR needs 2 reviews from different model families.

Required checks:
1. Requirement coverage
2. Regression risk
3. Data integrity and idempotency
4. Security and secrets handling
5. Logging and observability coverage

---

## 8. Sprint 1 Agent Task Board (Ready to Run)

1. **Contract Agent**
   - Deliver: `contracts/openapi.yaml`, `contracts/events/*.json`
2. **Backend Agent**
   - Deliver: API skeleton, auth, operator/source endpoints
3. **Scraping Agent**
   - Deliver: Firecrawl connector + Playwright fallback + scheduler
4. **Data Agent**
   - Deliver: normalization pipeline + confidence scoring + QA queue
5. **Frontend Agent**
   - Deliver: web app shell + Morning Brief v1 + Price Wire table
6. **Platform Agent**
   - Deliver: CI pipeline, environments, observability baseline
7. **Reviewer 1 + Reviewer 2**
   - Deliver: independent reviews before merge

---

## 9. Immediate Next 72 Hours

1. Approve this plan as source-of-truth
2. Create repo lane structure and ownership file (`CODEOWNERS`)
3. Start Phase 1 tickets and assign agents by lane
4. Stand up Firecrawl + Playwright workers in staging
5. Ship first end-to-end scrape for 10 operators and validate output

---

## 10. Final Call

This plan optimizes for speed, data dominance, and parallel execution quality.

Web-only removes split focus.  
GLASS-only revenue reporting keeps decisions honest.  
Aggressive scraping with Firecrawl + AI agents creates the moat fast.

