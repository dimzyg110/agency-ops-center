# Roviq SEO Domination Tool — Technical Architecture

**Date:** 2026-02-12  
**Authoring Basis:** Synthesized from `RESEARCH-REPORT.md`, `RESEARCH-REVIEW.md`, and `RESEARCH-REVIEW-OPUS.md` (FINAL-PLAN not found).  
**Goal:** A build-ready architecture for Phase 1 MVP, with clear extension path to multi-client SaaS.

---

## 0) Executive Architecture Decision

### Chosen Approach: **Monorepo**

Use a monorepo for speed, shared domain models, and consistent deployment pipelines across:
- API/backend orchestration
- AI content pipeline workers
- client adapters (Netlify, WordPress, GitHub Pages)
- shared schemas/types
- admin UI

**Why monorepo now:**
- Faster Phase 1 execution with one CI/CD setup
- Shared types for content entities, jobs, and tenant configs
- Easier cross-service refactors while architecture is still evolving
- Avoid early distributed-system overhead

**When to split later:**
- If one service has separate scaling/security boundaries (e.g., high-throughput worker farm)
- If independent team ownership becomes bottleneck

---

## 1) System Architecture

## 1.1 High-Level Topology

```text
                    +----------------------------+
                    |   Admin UI (Next.js)       |
                    |   (operators + analysts)    |
                    +-------------+--------------+
                                  |
                                  v
+-------------------+   REST    +---------------------------+
| External APIs     |<--------->| SEO Core API (NestJS)     |
| - GLASS API       |           | - tenants/configs         |
| - GSC API         |           | - campaigns/content/jobs  |
| - GBP API         |           | - scoring + approvals     |
+---------+---------+           +------------+--------------+
          |                                  |
          |                                  | enqueue
          |                                  v
          |                     +---------------------------+
          |                     | Queue (Redis + BullMQ)    |
          |                     +------------+--------------+
          |                                  |
          |                                  v
          |                     +---------------------------+
          |                     | Worker Services           |
          |                     | - Research agent          |
          |                     | - Draft agent             |
          |                     | - Review/QA agent         |
          |                     | - Humanize agent          |
          |                     | - Publish adapter runner  |
          |                     +------------+--------------+
          |                                  |
          v                                  v
+----------------------+         +---------------------------+
| PostgreSQL           |         | Client Destinations       |
| (multi-tenant data)  |         | - Netlify repos           |
| + pgvector           |         | - WordPress REST API      |
+----------------------+         | - GitHub Pages repos      |
                                 +---------------------------+
```

## 1.2 Monorepo Structure

```text
seo-domination/
  apps/
    api/                    # NestJS REST API
    admin/                  # Next.js internal dashboard
    worker/                 # BullMQ workers + pipeline executors
    scheduler/              # Cron-trigger service (campaign cadence)
  packages/
    domain/                 # TypeScript domain models, DTOs, enums
    db/                     # Prisma schema + migrations + seeders
    ai/                     # prompt templates, model routers, guardrails
    scoring/                # quality scoring engine
    templates/              # Nunjucks/Handlebars page templates
    adapters/               # publish adapters (netlify/wp/github)
    integrations/           # GLASS, GSC, GBP, schema, sitemap clients
    observability/          # logging, tracing, metrics helpers
    config/                 # config loader + validation (zod)
  scripts/
    bootstrap-client.ts
    reindex-keywords.ts
    backfill-rankings.ts
  infra/
    docker/
    terraform/
    railway/
  docs/
    api/
    runbooks/
```

## 1.3 Service Boundaries

### Services
1. **SEO Core API (`apps/api`)**
   - Tenant/auth/config CRUD
   - Campaign planning APIs
   - Job creation and orchestration endpoints
   - Approval workflow state transitions

2. **Worker Service (`apps/worker`)**
   - Executes content pipeline stages
   - Pulls data from GLASS/GSC
   - Runs AI generation/review/humanization
   - Publishes through adapters

3. **Scheduler (`apps/scheduler`)**
   - Recurring jobs: ranking pulls, refresh pages, GBP post cadence, sitemap ping

4. **Admin UI (`apps/admin`)**
   - Internal ops console for reviewing drafts, scores, failures, publish logs

### Libraries
- `packages/domain`, `packages/db`, `packages/ai`, `packages/scoring`, `packages/templates`, `packages/adapters`, `packages/integrations`

### Scripts
- One-off maintenance tasks and migration utilities only; no business logic duplication.

## 1.4 Database Schema (PostgreSQL, multi-tenant)

> Use `tenant_id` on all business tables + row-level security (RLS) where possible.

### Core tables

- `tenants`
  - `id (uuid pk)`
  - `name`
  - `slug`
  - `status` (`active|paused|churned`)
  - `created_at`

- `tenant_users`
  - `id`
  - `tenant_id`
  - `email`
  - `role` (`owner|editor|viewer|ops`)

- `client_configs`
  - `id`
  - `tenant_id`
  - `version`
  - `config_json (jsonb)`
  - `is_active`

- `audiences`
  - `id`
  - `tenant_id`
  - `name`
  - `locale`
  - `persona_json`

- `keyword_clusters`
  - `id`
  - `tenant_id`
  - `name`
  - `funnel_stage` (`transactional|commercial|informational|local`)

- `keywords`
  - `id`
  - `tenant_id`
  - `cluster_id`
  - `keyword`
  - `locale`
  - `priority`
  - `target_url`
  - `difficulty`
  - `volume`

- `rankings`
  - `id`
  - `tenant_id`
  - `keyword_id`
  - `date`
  - `position`
  - `url`
  - `search_engine`
  - `location`

- `content_items`
  - `id`
  - `tenant_id`
  - `type` (`location_page|product_page|blog|pillar|faq|gbp_post`)
  - `status` (`planned|research|draft|review|humanize|approved|published|failed`)
  - `title`
  - `slug`
  - `primary_keyword_id`
  - `language`
  - `outline_json`
  - `body_md`
  - `body_html`
  - `schema_jsonld`
  - `quality_score`
  - `publish_target` (`netlify|wordpress|github_pages`)
  - `published_url`

- `content_versions`
  - `id`
  - `content_item_id`
  - `version`
  - `stage` (`draft|reviewed|humanized|approved`)
  - `body_md`
  - `score_json`
  - `created_by`

- `content_facts` (for traceability)
  - `id`
  - `content_item_id`
  - `source_type` (`glass|gsc|gbp|manual|web`)
  - `source_ref`
  - `fact_text`
  - `confidence`

- `jobs`
  - `id`
  - `tenant_id`
  - `job_type`
  - `status`
  - `payload_json`
  - `attempts`
  - `last_error`
  - `started_at`
  - `finished_at`

- `publish_logs`
  - `id`
  - `tenant_id`
  - `content_item_id`
  - `adapter`
  - `status`
  - `remote_id`
  - `response_json`

## 1.5 Queue/Job System

**Choice:** Redis + BullMQ

**Queues**
- `research.queue`
- `draft.queue`
- `review.queue`
- `humanize.queue`
- `schema.queue`
- `publish.queue`
- `rank-sync.queue`
- `retry-dlq`

**Job idempotency key**
- `tenant_id + content_item_id + stage + version`

**Retry policy**
- External API failures: exponential backoff (3-5 retries)
- AI parse/format failures: 2 retries + fallback model
- Publish failures: 3 retries, then DLQ and alert

## 1.6 REST API Design (Phase 1)

Base: `/v1`

### Tenants & Config
- `POST /tenants`
- `GET /tenants/:id`
- `POST /tenants/:id/configs`
- `GET /tenants/:id/configs/active`

**`POST /tenants/:id/configs` request**
```json
{
  "version": "1.0.0",
  "config": { "brand": {}, "seo": {}, "publishing": {} }
}
```

### Campaigns & Keywords
- `POST /tenants/:id/keywords/import`
- `GET /tenants/:id/keywords`
- `POST /tenants/:id/campaigns`

**Campaign create request**
```json
{
  "name": "CH East Boston Q1",
  "contentTypes": ["location_page", "blog"],
  "keywordClusterIds": ["uuid1"],
  "weeklyVolume": 6
}
```

### Content Pipeline
- `POST /tenants/:id/content/plan`
- `POST /tenants/:id/content/:contentId/run-stage`
- `GET /tenants/:id/content/:contentId`
- `POST /tenants/:id/content/:contentId/approve`
- `POST /tenants/:id/content/:contentId/publish`

### Rankings & Analytics
- `POST /tenants/:id/rankings/sync`
- `GET /tenants/:id/rankings?from=...&to=...`

### Integrations
- `POST /tenants/:id/integrations/glass/test`
- `POST /tenants/:id/integrations/gsc/connect`
- `POST /tenants/:id/integrations/gbp/connect`

---

## 2) Content Generation Pipeline

## 2.1 Stage Flow

1. **Research**
   - Inputs: keyword cluster, locale, audience, competitor SERP snapshot, GLASS product/price trend snippets
   - Output: structured brief (`intent`, `outline`, `facts`, `entities`, `required schema`, `internal links`)

2. **Draft**
   - Uses template + research brief
   - Produces markdown draft + metadata (title, meta description, FAQs)

3. **Review (AI QA)**
   - Checks: factual references, duplication risk, keyword stuffing, compliance constraints, readability, entity completeness
   - Generates score + revision directives

4. **Humanize**
   - Style adaptation to client brand voice
   - Removes robotic patterns and repetitive phrasing
   - Ensures local authenticity (e.g., East Boston landmarks)

5. **Publish**
   - Generates schema JSON-LD + canonical + sitemap entry
   - Sends to destination adapter
   - Records remote IDs and final URL

## 2.2 Agent/Tool Mapping

- `Research Agent` (LLM + integrations)
- `Draft Agent` (LLM + templates)
- `QA Agent` (LLM + deterministic lint checks)
- `Humanize Agent` (LLM style rewrite constrained by facts)
- `Publisher Runner` (adapter + API client)

## 2.3 GLASS Data Integration

GLASS endpoint base: `https://glass-api-production.up.railway.app`

**Used data contracts (normalized in `glass_snapshots`)**
- Product catalog snapshots
- Price comparisons by category and geography
- Trend deltas (week-over-week/month-over-month)

**Injection points**
- Research stage: source facts + comparison bullets
- Draft stage: local “market insight” blocks
- Schema stage: enrich Product/AggregateOffer where allowed
- Blog generation: monthly “market intelligence” pieces

**Rule:** Every GLASS-derived claim must create a `content_facts` record for auditability.

## 2.4 Template Engine

Use `Nunjucks` with typed template inputs.

Template families:
- `location-page`
- `product-page`
- `comparison-page`
- `faq-page`
- `pillar-guide`
- `gbp-post`

Each template defines:
- required sections
- min/max word count
- required schema types
- allowed CTA types

## 2.5 Quality Scoring System (Automated Pre-Review)

Score 0-100, weighted:
- Topical coverage (20)
- Search intent match (15)
- Factual grounding / citations (15)
- Uniqueness / duplication risk (15)
- Readability + clarity (10)
- On-page SEO completeness (title/meta/H1/H2/FAQ/internal links) (15)
- Compliance and claim safety (10)

**Thresholds**
- `<75`: block publish
- `75-84`: requires human editor approval
- `>=85`: eligible for auto-approval policy (tenant-configurable)

---

## 3) Multi-Client Architecture

## 3.1 Client Configuration Schema (JSON)

```json
{
  "tenant": {
    "name": "Cannabis Healing",
    "slug": "ch"
  },
  "brand": {
    "voice": "community, local, trustworthy",
    "languages": ["en", "es"],
    "compliance": {
      "allowMedicalClaims": false,
      "ageGateRequired": true
    }
  },
  "seo": {
    "primaryGeo": "East Boston, MA",
    "keywordPolicy": {
      "maxPrimaryPerPage": 1,
      "maxDensity": 1.8
    },
    "contentCadence": {
      "locationPagesPerWeek": 3,
      "blogsPerWeek": 2
    }
  },
  "publishing": {
    "adapter": "netlify",
    "repo": "github.com/randytorres/ch-web",
    "branch": "main",
    "contentPath": "src/content/seo"
  },
  "integrations": {
    "glass": { "baseUrl": "https://glass-api-production.up.railway.app" },
    "gsc": { "property": "sc-domain:cannabishealingllc.com" },
    "gbp": { "locationId": "..." }
  }
}
```

## 3.2 Example Client Configs

### CH (React/Netlify)
- `adapter: netlify`
- Content committed to repo as markdown/json data files
- Netlify build deploy triggered by PR merge

### AC (Swift iOS brand site + content microsite)
- Keep app separate; SEO pages on web microsite
- `adapter: github_pages` or `netlify`
- Publish long-form content to static site, deep-link from app

### Delivered (WordPress)
- `adapter: wordpress`
- Publish via WP REST + JWT/app password
- Auto-update post/page, taxonomies, Yoast fields (if plugin available)

## 3.3 Publishing Adapters

- `NetlifyAdapter`
  - Creates branch/commit/PR with generated files
  - Optionally auto-merge for approved content

- `WordPressAdapter`
  - `POST /wp-json/wp/v2/pages|posts`
  - media upload support
  - meta/schema injection

- `GitHubPagesAdapter`
  - Commit static markdown/frontmatter + rebuild trigger

Adapter interface:
```ts
interface PublisherAdapter {
  publish(input: PublishPayload): Promise<PublishResult>;
  update(input: PublishPayload): Promise<PublishResult>;
  unpublish(input: UnpublishPayload): Promise<void>;
}
```

## 3.4 Isolation Model

- Hard tenant partitioning via `tenant_id`
- Separate API keys per tenant integration
- Keyword clusters scoped per tenant
- No cross-tenant embeddings or prompt context
- Per-tenant queue concurrency limits

---

## 4) Integration Points

## 4.1 GLASS API

- Client wrapper in `packages/integrations/glass`
- Scheduled ingest jobs store normalized snapshots
- Cache with TTL to reduce upstream calls
- Data provenance attached to every generated claim

## 4.2 Google Search Console API

Use for:
- query/page performance pulls
- indexing state checks
- quick-win identification (positions 4-20)

## 4.3 Google Business Profile API

Use for:
- location metadata sync
- GBP post creation from selected content snippets
- Q&A/review workflow ingestion where API permissions allow

## 4.4 Schema.org Generator

`packages/integrations/schema` generates JSON-LD for:
- `LocalBusiness`
- `Product`
- `FAQPage`
- `Article`
- `BreadcrumbList`

Validation via schema lint before publish.

## 4.5 Sitemap Generator

- Aggregate published URLs per tenant
- Generate `sitemap.xml` (and index if segmented)
- Trigger search engine ping endpoints after batch publish

## 4.6 Content Delivery to Client Sites

Path by adapter:
- Netlify: PR/merge => build => deploy
- WordPress: REST publish => immediate live URL
- GitHub Pages: commit => action build => deploy

Every publish writes `publish_logs` with remote ID and response payload.

---

## 5) Tech Stack Recommendation

## 5.1 Languages & Frameworks

- **TypeScript (Node 20+)** everywhere for shared types and faster staffing
- **NestJS** for robust API architecture
- **BullMQ** for queue orchestration
- **Next.js** for internal admin UI
- **Prisma + PostgreSQL** for typed data access

## 5.2 Database

- **PostgreSQL 16** (+ `pgvector` optional for semantic retrieval)
- Rationale: strong relational integrity + JSONB flexibility + mature tooling

## 5.3 Queue

- **Redis + BullMQ**
- Rationale: reliable retries, backoff, scheduling, operational simplicity

## 5.4 Hosting / Deployment

- Phase 1: Railway (API, worker, Redis, Postgres) for speed
- Phase 2+: Move to Kubernetes/ECS if workload justifies
- Admin UI: Vercel or Netlify

## 5.5 Cost Estimates (Monthly)

### MVP (1-3 clients)
- Railway services + DB + Redis: **$120-$300**
- LLM/API usage: **$300-$1,200** (depends on cadence)
- Observability (Sentry/Logtail): **$0-$100**
- Rank data tools/API: **$100-$300**
- Total infra/tooling: **~$520-$1,900/mo** (excluding labor)

### Multi-client (10+ clients)
- Infra + queue + DB scale: **$800-$2,500**
- LLM usage: **$2,000-$8,000**
- SEO data APIs/tools: **$500-$1,500**
- Total: **~$3,300-$12,000/mo**

---

## 6) Implementation Roadmap

## Phase 1 (MVP, 4-6 weeks)
**Smallest useful thing:** One tenant (CH), one destination (Netlify), one content type family (location pages + blogs), full pipeline with manual approval gate.

### Deliverables
1. Tenant config + auth skeleton
2. Keyword import + campaign planner
3. Pipeline stages: research/draft/review/humanize/publish
4. GLASS ingestion and fact injection
5. Netlify publish adapter (PR-based)
6. Quality score engine + editor approval screen
7. GSC sync and ranking dashboard (basic)

### Team/Effort
- 1 backend engineer
- 1 full-stack engineer (admin UI + adapter)
- 1 prompt/SEO engineer (templates + scoring rules)
- Estimated: **4-6 weeks**

## Phase 2 (Multi-client, 6-8 weeks)

### Additions
1. WordPress + GitHub Pages adapters
2. Tenant-level isolation hardening (RLS, audit logs)
3. Template packs by client type (dispensary/delivery/cultivator)
4. GBP integration workflows
5. Automated sitemap/schema validation pipeline
6. Multi-tenant reporting dashboards

Estimated: **6-8 weeks**

## Phase 3 (Self-service SaaS, 8-12 weeks)

### Additions
1. Self-serve onboarding wizard
2. Billing (Stripe), plan limits, usage metering
3. Role-based access + invite flows
4. Advanced automations (auto-refresh by ranking decay)
5. Marketplace of publishing adapters
6. SLA, alerting, and enterprise-grade observability

Estimated: **8-12 weeks**

---

## 7) Phase 1 Build Checklist (Developer-Ready)

1. Initialize monorepo (`pnpm` workspaces + Turborepo)
2. Scaffold apps: `api`, `worker`, `admin`
3. Add Postgres + Redis, Prisma migrations for core tables
4. Implement `POST /tenants/:id/content/plan`
5. Implement BullMQ pipeline processors by stage
6. Build first template set (`location-page`, `blog`)
7. Implement quality scoring rules and thresholds
8. Implement Netlify adapter via GitHub PR flow
9. Add GSC read integration and weekly ranking sync
10. Add admin review screen + approve/publish actions
11. Add observability: job metrics, failure alerts, publish logs
12. Run end-to-end on CH sandbox campaign (10 pages)

---

## 8) Key Risks and Mitigations

- **Risk:** AI hallucinated claims  
  **Mitigation:** fact table + source-required checks + block publish under threshold

- **Risk:** Cross-tenant data leakage  
  **Mitigation:** strict `tenant_id` filtering + RLS + integration key segregation

- **Risk:** Publishing breakage per platform  
  **Mitigation:** adapter contract tests + dry-run mode + rollback hooks

- **Risk:** Overproduction of thin pages  
  **Mitigation:** quality floor + template constraints + editorial gating

---

## 9) Final Recommendation

Build Phase 1 as a **CH-first, Netlify-native pipeline** (not WordPress-first), with GLASS-backed factual content, quality scoring, and human approval. This gives immediate execution value while keeping architecture extensible for Delivered (WordPress) and future clients.
