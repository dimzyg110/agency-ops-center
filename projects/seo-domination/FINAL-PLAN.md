# SIGNAL — SEO Intelligence, Generation, Navigation, and Authority Layer

## Roviq's AI-Powered SEO Domination Engine for Cannabis Retail

**Version:** 1.0  
**Date:** February 12, 2026  
**Status:** Final Plan — Ready for Architecture & Execution  
**Author:** Synthesized from research report, two independent reviews, and client documentation  
**Classification:** Confidential — Roviq Internal

---

## Table of Contents

1. [Product Definition](#1-product-definition)
2. [System Architecture](#2-system-architecture)
3. [Content Engine](#3-content-engine)
4. [Multi-Client Configuration](#4-multi-client-configuration)
5. [SEO Automation](#5-seo-automation)
6. [8-Week Execution Plan](#6-8-week-execution-plan)
7. [Tech Stack](#7-tech-stack)
8. [Competitive Moat](#8-competitive-moat)
9. [Appendix A: Client Configuration Examples](#appendix-a)
10. [Appendix B: API Reference](#appendix-b)
11. [Appendix C: Content Templates](#appendix-c)
12. [Appendix D: Cost Model](#appendix-d)

---

## 1. Product Definition

### Name: **SIGNAL**

**SEO Intelligence, Generation, Navigation, and Authority Layer**

### One-Paragraph Pitch

SIGNAL is an AI-powered SEO automation engine purpose-built for cannabis retail. It ingests real-time market data from GLASS (500+ MA dispensaries, 70K+ products, daily price scraping), generates SEO-optimized content at scale — location pages, product pages, market intelligence, blog posts — and publishes through platform-agnostic adapters to any client stack (React/Netlify, WordPress, Next.js, or headless CMS). Unlike generic SEO tools or agency playbooks, SIGNAL produces content that no competitor can replicate because it's powered by proprietary market data that doesn't exist anywhere else. One operator (Randy) + AI agents can deliver what a $5K/month SEO agency does, at 10x the speed, with data-driven content that earns backlinks organically.

### Ecosystem Fit

```
┌─────────────────────────────────────────────────────────┐
│                    ROVIQ ECOSYSTEM                       │
│                                                         │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐       │
│  │   GLASS   │───▶│  SIGNAL   │    │    Cue    │       │
│  │  Market   │    │    SEO    │    │    AI     │       │
│  │  Intel    │    │  Engine   │    │ Commerce  │       │
│  │           │    │           │    │ Platform  │       │
│  │ • Scraping│    │ • Content │    │ • Virtual │       │
│  │ • Pricing │    │ • Pages   │    │   Bud-    │       │
│  │ • Products│    │ • Schema  │    │   tender  │       │
│  │ • Trends  │    │ • Links   │    │ • POS     │       │
│  │ • Alerts  │    │ • Reports │    │ • Orders  │       │
│  └───────────┘    └───────────┘    └───────────┘       │
│       ▲                │                │               │
│       │                ▼                ▼               │
│  ┌─────────────────────────────────────────────┐       │
│  │            CLIENT WEBSITES                   │       │
│  │  CH (React/Netlify) │ AC (React/Netlify)    │       │
│  │  Delivery (WordPress) │ Future clients      │       │
│  └─────────────────────────────────────────────┘       │
│       ▲                                                 │
│       │                                                 │
│  ┌───────────┐                                         │
│  │  GLASS    │  ← Public market intelligence microsite │
│  │  .report  │  ← Link-earning engine for all clients  │
│  └───────────┘                                         │
└─────────────────────────────────────────────────────────┘
```

**GLASS** = The data layer. Scrapes, normalizes, and stores market intelligence (prices, products, inventory, trends, CCC regulatory data). GLASS is the moat.

**SIGNAL** = The SEO/content layer. Consumes GLASS data, generates optimized content, manages technical SEO, publishes to client sites, tracks performance. SIGNAL is the engine.

**Cue** = The commerce layer. Full AI commerce platform (ordering, loyalty, POS integration, Virtual Budtender widget). Cue is the customer-facing product. Separate from SIGNAL.

These three products are independent but synergistic. GLASS feeds SIGNAL with data. SIGNAL drives traffic to client sites. Cue converts that traffic into orders. Together they represent a vertically integrated cannabis technology stack that no competitor has.

### Revenue Model: Hybrid (Service + Productized Tool)

| Revenue Stream | Price | Model | Timeline |
|---|---|---|---|
| **Managed SEO Service** | $1,500–3,000/mo per client | Retainer — SIGNAL powers the work, Roviq manages execution | Now (CH is Client #1) |
| **SIGNAL SaaS** (future) | $500–1,500/mo per seat | Self-serve — client accesses SIGNAL dashboard, generates content, manages SEO | Month 6+ (after 3 clients validate the system) |
| **GLASS Market Intel Subscription** | $299/mo per subscriber | Data product — operators and brands pay for GLASS market data | Month 3+ (after public microsite launches) |
| **Setup / Onboarding Fee** | $2,500–5,000 one-time | Technical audit + SEO architecture + initial content generation | Per new client |

**Phase 1 (Now – Month 3):** CH as paid pilot client. SIGNAL is built *during* the CH engagement. CH pays for the service ($1,500–2,000/mo retainer); Roviq builds the reusable system. Every template, script, and automation built for CH becomes a product asset.

**Phase 2 (Month 3–6):** Second client (AC or Delivery) validates the system on a different vertical (cultivator B2B SEO or delivery programmatic pages). Revenue: $3,000–5,000/mo from 2 clients.

**Phase 3 (Month 6+):** Productize. SIGNAL dashboard available as self-serve SaaS. "See what we did for CH — now do it yourself." Revenue target: $10K+ MRR from 5–8 clients.

---

## 2. System Architecture

### 2.1 High-Level System Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SIGNAL ENGINE                                │
│                                                                      │
│  ┌────────────────────────────────────┐                              │
│  │         DATA INGESTION LAYER       │                              │
│  │                                    │                              │
│  │  GLASS API ──────┐                 │                              │
│  │  Google Trends ───┤                │                              │
│  │  GSC API ─────────┤  Normalizer ──▶│─── Content DB (PostgreSQL)   │
│  │  PAA Scraper ─────┤                │                              │
│  │  Competitor URLs ─┘                │                              │
│  └────────────────────────────────────┘                              │
│                          │                                           │
│                          ▼                                           │
│  ┌────────────────────────────────────┐                              │
│  │       CONTENT GENERATION LAYER     │                              │
│  │                                    │                              │
│  │  Template Engine ─────┐            │                              │
│  │  AI Writer (LLM API) ─┤            │                              │
│  │  Schema Generator ────┤  Pipeline ─┤──▶ Content Queue             │
│  │  Internal Link Engine ┤            │                              │
│  │  Translation Engine ──┘            │                              │
│  └────────────────────────────────────┘                              │
│                          │                                           │
│                          ▼                                           │
│  ┌────────────────────────────────────┐                              │
│  │         REVIEW & QA LAYER          │                              │
│  │                                    │                              │
│  │  Automated Quality Gates ──┐       │                              │
│  │  Compliance Checker ───────┤ Gate ─┤──▶ Approved │ Flagged        │
│  │  Duplicate Detector ───────┤       │                              │
│  │  Human Review Queue ───────┘       │                              │
│  └────────────────────────────────────┘                              │
│                          │                                           │
│                          ▼                                           │
│  ┌────────────────────────────────────┐                              │
│  │       PUBLISHING LAYER             │                              │
│  │                                    │                              │
│  │  ┌──────────────┐  ┌───────────┐  │                              │
│  │  │ Git Adapter  │  │ WP REST   │  │                              │
│  │  │ (React/Vite/ │  │ Adapter   │  │                              │
│  │  │  Netlify)    │  │ (WP API)  │  │                              │
│  │  └──────────────┘  └───────────┘  │                              │
│  │  ┌──────────────┐  ┌───────────┐  │                              │
│  │  │ Headless CMS │  │ Static    │  │                              │
│  │  │ Adapter      │  │ Generator │  │                              │
│  │  │ (Sanity etc) │  │ (Astro)   │  │                              │
│  │  └──────────────┘  └───────────┘  │                              │
│  └────────────────────────────────────┘                              │
│                          │                                           │
│                          ▼                                           │
│  ┌────────────────────────────────────┐                              │
│  │       MONITORING & REPORTING       │                              │
│  │                                    │                              │
│  │  Rank Tracker ────────────┐        │                              │
│  │  GSC Performance ─────────┤        │                              │
│  │  GA4 Analytics ───────────┤ Report │                              │
│  │  GBP Insights ────────────┤        │                              │
│  │  Backlink Monitor ────────┘        │                              │
│  └────────────────────────────────────┘                              │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow: GLASS → Content → Client Site

```
Step 1: GLASS scrapes 500+ MA dispensaries daily
         ↓
Step 2: SIGNAL pulls via GLASS API:
         - Product catalog (name, brand, category, THC%, CBD%, price)
         - Price trends (7d, 30d, 90d per product/category/dispensary)
         - New product launches
         - Competitor inventory changes
         - Market aggregates (avg price by category, region, etc.)
         ↓
Step 3: Content Generator creates:
         - Product descriptions (unique per product, enriched with effects/terpene data)
         - Price comparison pages ("Cheapest flower in East Boston — live data")
         - Market reports ("Cannabis Price Index: Boston Metro, Feb 2026")
         - Location pages (enriched with local dispensary density, price context)
         - Blog posts (data-driven: "5 Dispensaries with the Best Edible Prices This Week")
         ↓
Step 4: Quality Gate checks:
         - Minimum word count met
         - No duplicate content (cosine similarity < 0.85 with existing pages)
         - Cannabis compliance passed (no medical claims without disclaimers, no youth-targeted language)
         - Schema markup valid (JSON-LD validates against schema.org)
         - Internal links present (minimum 3 per page)
         - Readability score (Flesch-Kincaid 8th–10th grade)
         ↓
Step 5: Publishing Adapter:
         [For CH — React/Netlify]:
           - Generate MDX files in content directory
           - Create PR to ch-web repo via GitHub API
           - Netlify auto-deploys on merge
           - Sitemap regenerated automatically
         [For Delivery — WordPress]:
           - POST to WordPress REST API
           - Auto-publish or draft for review
           - Yoast/RankMath metadata populated
         [For GLASS Market Intel — Static Site]:
           - Generate pages via Astro/Next.js SSG
           - Auto-deploy to Netlify/Vercel
         ↓
Step 6: Post-publish verification:
         - Confirm page is live (HTTP 200)
         - Submit URL to Google Search Console Indexing API
         - Verify schema markup renders in Rich Results Test
         - Add to rank tracking watchlist
```

### 2.3 Multi-Client Tenant Model

SIGNAL is a **multi-tenant system** where each client is a "tenant" with isolated configuration but shared infrastructure.

```
┌─────────────────────────────────────────────────────┐
│                   SIGNAL CORE                        │
│                                                     │
│  Shared Infrastructure:                             │
│  • Content Generation Engine (LLM pipeline)         │
│  • GLASS Data Access Layer                          │
│  • Schema Markup Generator                          │
│  • Rank Tracking Engine                             │
│  • Quality Gate Framework                           │
│  • Internal Linking Engine                          │
│  • Translation Pipeline                             │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Tenant:  │  │ Tenant:  │  │ Tenant:  │         │
│  │ CH       │  │ AC       │  │ Delivery │         │
│  │          │  │          │  │          │         │
│  │ Config:  │  │ Config:  │  │ Config:  │         │
│  │ • Keywords│  │ • Keywords│  │ • Keywords│         │
│  │ • Tone   │  │ • Tone   │  │ • Tone   │         │
│  │ • Platform│  │ • Platform│  │ • Platform│         │
│  │ • Pages  │  │ • Pages  │  │ • Pages  │         │
│  │ • Schema │  │ • Schema │  │ • Schema │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

**Tenant isolation rules:**
- Each tenant has its own keyword universe, content templates, brand voice profile, and publishing target
- Content generated for Tenant A is never published on Tenant B's site
- GLASS data is shared (it's market data, not client-proprietary), but content derived from it is tenant-specific
- Shared content (e.g., "MA Cannabis Laws 2026") can be syndicated across tenants with canonical URLs pointing to the originating tenant or to GLASS public microsite
- White-label: tenant branding is configurable. SIGNAL branding does not appear on client sites unless opted in

### 2.4 API Design

SIGNAL exposes a REST API for internal use and (eventually) external SaaS customers.

**Base URL:** `https://api.signal.roviq.com/v1`

| Endpoint | Method | Description |
|---|---|---|
| `/tenants` | GET, POST | List/create client tenants |
| `/tenants/:id/config` | GET, PUT | Read/update tenant configuration |
| `/tenants/:id/keywords` | GET, POST, DELETE | Manage keyword universe |
| `/tenants/:id/content` | GET, POST | List/create content pieces |
| `/tenants/:id/content/:id` | GET, PUT, DELETE | Read/update/delete specific content |
| `/tenants/:id/content/:id/publish` | POST | Trigger publishing pipeline |
| `/tenants/:id/content/generate` | POST | Trigger AI content generation |
| `/tenants/:id/pages` | GET | List all published pages |
| `/tenants/:id/pages/sitemap` | GET | Generate XML sitemap |
| `/tenants/:id/schema` | GET | Generate schema markup for all pages |
| `/tenants/:id/rankings` | GET | Current keyword rankings |
| `/tenants/:id/reports` | GET, POST | Generate/retrieve SEO reports |
| `/tenants/:id/links/internal` | GET, POST | Internal link suggestions/updates |
| `/tenants/:id/links/external` | GET | Backlink monitoring |
| `/glass/products` | GET | GLASS product data (filtered by region/category) |
| `/glass/prices` | GET | GLASS price data (current + historical) |
| `/glass/trends` | GET | GLASS market trend data |
| `/glass/reports` | GET, POST | Generate market intelligence reports |
| `/health` | GET | System health check |

**Authentication:** API key per tenant (header: `X-Signal-Key`). Rate limited to 1000 req/hr per key.

### 2.5 Integration with Existing Client Stacks

#### CH: React 18 + Vite 5 + Tailwind CSS 3.4 → Netlify

**This is the primary integration target.** CH is NOT WordPress. The integration approach:

1. **Content Storage:** Blog posts and SEO pages are authored as MDX/Markdown files in the `ch-web` repo under `src/data/blogs/` (blogs already work this way) and a new `src/data/pages/` directory for SEO landing pages.

2. **Page Generation:** SIGNAL generates MDX files with frontmatter containing all SEO metadata:
   ```mdx
   ---
   title: "Dispensary Near Logan Airport — 5 Minute Drive"
   slug: "dispensary-near-logan-airport"
   description: "Cannabis Healing is the closest dispensary to Logan Airport..."
   keywords: ["dispensary near logan airport", "weed near logan"]
   schema:
     type: "LocalBusiness"
     data: { ... }
   faqSchema:
     - q: "How far is Cannabis Healing from Logan Airport?"
       a: "Just 5 minutes by car or 20 minutes walking..."
   internalLinks:
     - { text: "shop our menu", href: "/shop" }
     - { text: "airport guide", href: "/airport" }
   locale: "en"
   publishedAt: "2026-02-15"
   ---

   # Dispensary Near Logan Airport

   [Content here...]
   ```

3. **Publishing Pipeline:**
   - SIGNAL generates the MDX file
   - Creates a Pull Request to the `ch-web` GitHub repo via GitHub API
   - Randy reviews and merges (or auto-merge if quality gates pass)
   - Netlify auto-deploys on merge to `main`
   - Post-deploy hook confirms page is live and submits to GSC

4. **Dynamic Data (Product Pages):**
   - For product pages that need live data (prices, availability), CH site fetches from GLASS API at build time (Vite SSG) or via client-side fetch
   - Product pages are pre-rendered at build time with `vite-plugin-ssr` or a lightweight SSG approach
   - Dutchie menu embed remains on `/shop` — product SEO pages are *in addition to* (not replacing) the Dutchie embed
   - Each product SEO page links to the relevant Dutchie category/product for ordering

5. **Sitemap & Robots:**
   - Sitemap is auto-generated at build time from the page/blog manifest
   - `public/sitemap.xml` and `public/robots.txt` are maintained in the repo
   - SIGNAL updates the manifest; build process generates the sitemap

6. **Schema Markup:**
   - Generated per-page in frontmatter, rendered as `<script type="application/ld+json">` in the React component
   - Types: `LocalBusiness`, `FAQPage`, `Product`, `Article`, `BreadcrumbList`
   - Schema data is validated before publishing (using `schema-dts` or raw JSON-LD validation)

#### AC: React 18 + Vite → Netlify

Same architecture as CH (both are React/Vite/Netlify). Content types differ:
- B2B wholesale pages instead of local dispensary pages
- Strain/product showcase pages instead of location pages
- Brand authority content instead of tourist/traveler content

#### Delivery (formerly Delivered Inc): WordPress (Compromised)

**NOTE:** The Delivered Inc WordPress site is currently compromised with spam content (Chatib review pages, etc.). Before any SEO work, the site requires:
1. Complete hack cleanup and spam content removal
2. Security hardening (plugin audit, password rotation, WAF)
3. Google Search Console spam URL removal requests
4. Fresh sitemap submission

Once remediated, the WordPress integration is straightforward:
- WordPress REST API for content publishing (`POST /wp-json/wp/v2/posts`)
- Yoast SEO or RankMath for on-page metadata
- Custom post types for location pages and product pages
- Standard WP schema markup plugins

**IMPORTANT:** Refer to Delivery (not "Delivered") in all client-facing materials until the deal closes.

#### Future Clients (Unknown Stacks)

SIGNAL's publishing layer is adapter-based. Adding a new adapter requires:
1. Define the publishing target (Git repo, REST API, headless CMS API, etc.)
2. Implement the adapter interface: `publish(content, metadata) → result`
3. Configure in the tenant profile

Supported adapter pattern:
```
PublishingAdapter (interface)
├── GitHubPRAdapter (React/Vite/Netlify, Astro, Next.js SSG)
├── WordPressRESTAdapter (WordPress sites)
├── HeadlessCMSAdapter (Sanity, Contentful, Strapi)
└── StaticFileAdapter (direct file generation for custom stacks)
```

---

## 3. Content Engine

### 3.1 AI Content Generation Pipeline

The content pipeline has 6 stages. Every piece of content flows through all 6.

```
Stage 1: RESEARCH
  Input:  Target keyword + content type + tenant config
  Action: Pull GLASS data, scrape PAA questions, analyze SERP competitors,
          check existing content for overlap
  Output: Content brief (keyword, audience, angle, data points, competitor gaps,
          word count target, required sections)

Stage 2: DRAFT
  Input:  Content brief + tenant brand voice profile
  Action: LLM generates first draft using template + brief + voice profile
  Output: Raw draft (Markdown)

Stage 3: ENRICH
  Input:  Raw draft + GLASS data
  Action: Inject live data (prices, product counts, market comparisons),
          add internal links, generate FAQ section, create schema markup,
          add local context (landmarks, transit, neighborhood details)
  Output: Enriched draft

Stage 4: QUALITY GATE (Automated)
  Input:  Enriched draft
  Checks:
    ☐ Word count ≥ target (1,500+ for location pages, 2,000+ for pillars, 800+ for product pages)
    ☐ Primary keyword in title, H1, first 100 words, meta description
    ☐ No duplicate content (cosine similarity < 0.85 vs existing pages)
    ☐ Readability: Flesch-Kincaid grade 8–10
    ☐ Cannabis compliance: no unsubstantiated medical claims, no youth-targeting
    ☐ Schema markup validates against schema.org
    ☐ Internal links present (≥ 3 per page)
    ☐ External links present (≥ 1 authoritative source per page)
    ☐ Images have alt text with keyword variants
    ☐ Meta title ≤ 60 chars, meta description ≤ 160 chars
    ☐ No hallucinated data (all GLASS data points verified against source)
  Output: PASS → Stage 5 | FAIL → flag specific issues, return to Stage 2

Stage 5: HUMAN REVIEW (When Required)
  Triggers:
    • First 10 pieces of content for any new tenant (always human-reviewed)
    • Any content flagged by Quality Gate
    • Pillar content and market reports (always human-reviewed)
    • Any content making health/medical claims
    • Any content mentioning competitors by name
    • Random 10% sample of auto-approved content
  Action: Randy reviews in GitHub PR (for Git-based sites) or review dashboard
  Output: Approved | Revision requested

Stage 6: PUBLISH
  Input:  Approved content
  Action: Publishing adapter pushes to client site
  Post-publish:
    • Verify page is live (HTTP 200)
    • Submit URL to GSC Indexing API
    • Add to rank tracking
    • Schedule social promotion (if configured)
    • Log in SIGNAL analytics
```

### 3.2 Template System

Each content type has a template that defines structure, required elements, and GLASS data integration points.

#### Template: Location Page

```yaml
type: location_page
min_words: 1,500
required_sections:
  - hero: "H1 with primary keyword + location"
  - intro: "2-3 paragraphs — what this dispensary offers, why choose it, unique angles"
  - getting_here: "Directions from key landmarks (airport, MBTA stations, highways)"
  - what_we_carry: "Product categories with links to product pages"
  - pricing_snapshot: "GLASS-powered — average prices vs. local competitors (anonymized)"
  - neighborhood_guide: "Local context — what's nearby, parking, transit, restaurants"
  - faq: "5+ location-specific Q&As with FAQPage schema"
  - cta: "Order now / get directions / call"
required_schema:
  - LocalBusiness
  - FAQPage
  - BreadcrumbList
glass_data:
  - product_count_by_category: "Show breadth of menu"
  - avg_price_vs_local: "Price positioning (without naming competitors)"
  - popular_products: "Top sellers / trending items"
internal_links:
  - to: "/shop" (menu)
  - to: related location pages (hub-and-spoke)
  - to: relevant blog posts
variants:
  - language: ["en", "es"] (for East Boston pages)
```

#### Template: Product Page

```yaml
type: product_page
min_words: 800
required_sections:
  - hero: "Product name, brand, category, image"
  - description: "AI-generated unique description (NOT manufacturer copy)"
  - effects_and_terpenes: "Effect profile, dominant terpenes, recommended use"
  - pricing: "Current price + price history (GLASS data)"
  - similar_products: "3-5 related products with links"
  - faq: "3+ product-specific Q&As"
  - order_cta: "Link to Dutchie order page"
required_schema:
  - Product (name, brand, price, availability, description)
  - FAQPage
  - BreadcrumbList
glass_data:
  - current_price: "Live from GLASS"
  - price_trend: "7d/30d trend"
  - availability: "In stock / out of stock"
  - similar_products: "Same category, similar price range"
```

#### Template: Market Report

```yaml
type: market_report
min_words: 2,000
required_sections:
  - headline: "Data-driven title with timeframe"
  - executive_summary: "Key findings in 3-5 bullets"
  - methodology: "GLASS data — X dispensaries, Y products, Z timeframe"
  - price_analysis: "Category-by-category price trends with charts"
  - market_movements: "New product launches, price changes, store openings/closings"
  - regional_breakdown: "Boston metro, Western MA, Cape Cod, etc."
  - consumer_insights: "What's trending, what's declining"
  - about: "About GLASS — link to GLASS public site"
required_schema:
  - Article
  - Dataset (schema.org/Dataset for the data)
glass_data:
  - full dataset access for the reporting period
purpose: "Link-earning asset — designed to be cited by journalists and industry analysts"
publishing_target: "GLASS public microsite (glass.report or similar)"
```

#### Template: Blog Post (Cluster)

```yaml
type: blog_post
min_words: 1,500
required_sections:
  - intro: "Hook + what reader will learn"
  - body: "3-5 H2 sections covering the topic"
  - data_callout: "At least 1 GLASS data point woven into the narrative"
  - faq: "3+ questions from PAA data"
  - related_reading: "Links to pillar page + related cluster posts"
  - cta: "Visit us / shop / sign up for Flight Club"
required_schema:
  - Article
  - FAQPage
  - BreadcrumbList
```

#### Template: Strain Guide

```yaml
type: strain_guide
min_words: 1,200
required_sections:
  - strain_profile: "Name, type (indica/sativa/hybrid), genetics, THC/CBD range"
  - effects: "Effects, medical applications (with disclaimers), terpene profile"
  - growing_info: "Origin, cultivation notes (for authority)"
  - where_to_buy: "Available at [client dispensary] — link to product page"
  - price_context: "GLASS data — average price for this strain in MA"
  - similar_strains: "3-5 alternatives with links"
  - faq: "3+ strain-specific Q&As"
required_schema:
  - Product (as a variant)
  - FAQPage
glass_data:
  - avg_price_ma: "Average price for this strain across MA"
  - availability_count: "Number of dispensaries carrying this strain"
  - price_range: "Low to high price range"
```

### 3.3 Quality Gates: Detailed Specification

#### Automated Checks (Every Piece of Content)

| Check | Rule | Fail Action |
|---|---|---|
| **Word Count** | ≥ template minimum | Block publish, return to draft |
| **Keyword Density** | Primary keyword in title, H1, first 100 words, meta description; density 1–3% | Flag for revision |
| **Duplicate Detection** | Cosine similarity < 0.85 vs all existing content in tenant | Block publish, show similar content |
| **Readability** | Flesch-Kincaid grade 8–10 | Flag for simplification |
| **Cannabis Compliance** | No claims like "cures cancer", "treats anxiety" without disclaimer; no "safe", "harmless" language without context; no imagery/language targeting minors | Block publish, flag for human review |
| **Schema Validation** | JSON-LD validates against schema.org; required types present | Block publish, auto-fix if possible |
| **Internal Links** | ≥ 3 internal links per page; no broken links | Flag for enrichment |
| **Meta Tags** | Title ≤ 60 chars, description ≤ 160 chars, both contain primary keyword | Auto-truncate or flag |
| **Image Alt Text** | All images have alt text; at least one contains keyword variant | Flag for completion |
| **Data Freshness** | All GLASS data points within 48 hours | Re-pull data and regenerate |
| **Hallucination Check** | All specific claims (prices, product counts, rankings) verified against GLASS source data | Block publish if unverifiable |

#### Human Review Triggers

| Trigger | Why |
|---|---|
| First 10 pages per tenant | Calibrate AI output quality |
| Pillar content (>2,000 words) | High-value, high-visibility |
| Market reports | Data accuracy critical for reputation |
| Competitor mentions | Legal/ethical sensitivity |
| Health/medical claims | Compliance risk |
| Spanish-language content | Quality assurance for non-English |
| Random 10% sample | Ongoing quality monitoring |
| Any automated gate failure after 2 revision cycles | AI stuck — needs human guidance |

### 3.4 GLASS Data Integration Points

| GLASS Data | Content Use | Update Frequency |
|---|---|---|
| **Product catalog** (name, brand, category, THC%, CBD%, price) | Product pages, menu pages, strain guides | Daily |
| **Price history** (per product, per dispensary, per category) | Price comparison content, market reports, "deals" pages | Daily |
| **Market aggregates** (avg price by region, category trends) | Market intelligence reports, blog data callouts | Weekly |
| **New product launches** | "New this week" content, product launch blog posts | Daily |
| **Competitor inventory** (what's in/out of stock where) | Availability content, stock alerts, competitive positioning | Daily |
| **Dispensary metadata** (location, hours, license info) | Location page enrichment, directory data | Weekly |
| **CCC regulatory data** (license changes, enforcement, new rules) | Compliance content, regulatory update blog posts | Weekly |

### 3.5 Schema Markup Automation

SIGNAL auto-generates JSON-LD for every page based on content type:

**LocalBusiness (every client page):**
```json
{
  "@context": "https://schema.org",
  "@type": "Store",
  "name": "Cannabis Healing",
  "description": "East Boston's premier wellness dispensary, 5 minutes from Logan Airport",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "4 Neptune Road",
    "addressLocality": "East Boston",
    "addressRegion": "MA",
    "postalCode": "02128"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": 42.3742, "longitude": -71.0204 },
  "telephone": "+1-XXX-XXX-XXXX",
  "openingHoursSpecification": [
    { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "opens": "12:00", "closes": "22:00" }
  ],
  "priceRange": "$$",
  "image": "https://cannabishealingllc.com/images/storefront.jpg",
  "url": "https://cannabishealingllc.com"
}
```

**Product (product pages):**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Blue Dream Flower — 3.5g",
  "brand": { "@type": "Brand", "name": "Advanced Cultivators" },
  "description": "...",
  "offers": {
    "@type": "Offer",
    "price": "35.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "seller": { "@type": "Store", "name": "Cannabis Healing" }
  },
  "additionalProperty": [
    { "@type": "PropertyValue", "name": "THC", "value": "22%" },
    { "@type": "PropertyValue", "name": "CBD", "value": "0.5%" },
    { "@type": "PropertyValue", "name": "Category", "value": "Flower" }
  ]
}
```

**FAQPage (every page with FAQ section):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How far is Cannabis Healing from Logan Airport?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Cannabis Healing is just 5 minutes by car from Logan Airport..."
      }
    }
  ]
}
```

Schema is generated programmatically from content frontmatter and GLASS data. No manual schema writing required.

### 3.6 Internal Linking Automation

SIGNAL maintains a **link graph** of all pages across a tenant's site and automatically:

1. **Suggests internal links** during content generation based on keyword relevance
2. **Updates existing pages** when new related content is published (adds links to the new page)
3. **Enforces hub-and-spoke architecture:**
   - Every location page links to the regional hub page AND to 2-3 related location pages
   - Every blog post links to its pillar page AND to 2-3 related cluster posts
   - Every product page links to its category page AND to 2-3 related products
4. **Prevents orphan pages** — flags any page with <2 incoming internal links
5. **Balances link equity** — no single page should receive >20% of all internal links

Link graph is stored in SIGNAL's database and recomputed weekly.

---

## 4. Multi-Client Configuration

### 4.1 Client Profile Schema

Every SIGNAL tenant is configured with a profile that controls all content generation:

```yaml
tenant:
  id: "ch"
  name: "Cannabis Healing"
  business_type: "dispensary"  # dispensary | delivery | cultivator | brand
  
  location:
    address: "4 Neptune Road, East Boston, MA 02128"
    coordinates: { lat: 42.3742, lng: -71.0204 }
    service_area:
      primary: ["East Boston", "Winthrop", "Revere", "Chelsea"]
      secondary: ["Downtown Boston", "Charlestown", "South Boston", "Somerville", "Cambridge"]
      extended: ["Greater Boston Metro"]
    landmarks:
      - { name: "Logan Airport", distance: "5 min drive / 20 min walk", keywords: ["dispensary near logan airport", "weed near boston airport"] }
      - { name: "Maverick Station (Blue Line)", distance: "5 min walk", keywords: ["dispensary near maverick station"] }
      - { name: "Suffolk Downs", distance: "10 min drive" }
    hours: "12:00 PM – 10:00 PM daily"

  brand:
    tagline: "Land. Walk. Relax."
    positioning: "Modern luxury meets street culture — Boston's premier wellness dispensary"
    voice:
      tone: "Confident, warm, elevated but approachable. Never clinical or stiff."
      avoid: ["bro culture", "stoner stereotypes", "medical claims without disclaimers"]
      personality: "Like a knowledgeable friend who happens to work at the dopest dispensary"
    colors:
      primary: "#0F0F10"  # Ink Black
      accent: "#D4AF37"   # Gold
      light: "#F4F2EC"    # Bone

  audience:
    primary:
      name: "Airport Travelers"
      description: "Tourists and business travelers arriving at Logan Airport looking for cannabis"
      intent: "Quick purchase, convenient location, tourist-friendly experience"
      keywords_suffix: ["near logan airport", "near boston airport", "for tourists", "before flight"]
    secondary:
      name: "East Boston Locals"
      description: "Neighborhood residents, many Hispanic/Latino, regular customers"
      intent: "Best prices, loyalty rewards, community connection"
      keywords_suffix: ["east boston", "eastie", "near me"]
    tertiary:
      name: "Greater Boston Cannabis Consumers"
      description: "Boston-area consumers comparing dispensaries"
      intent: "Product selection, prices, reviews, experience"
      keywords_suffix: ["boston", "near me", "best dispensary"]

  platform:
    type: "react-vite-netlify"
    repo: "randytorres/ch-web"
    content_path: "src/data"
    blog_path: "src/data/blogs"
    pages_path: "src/data/pages"
    deploy_branch: "main"
    build_command: "npm run build"
    adapter: "GitHubPRAdapter"

  seo:
    primary_keywords:
      - "dispensary near logan airport"
      - "dispensary east boston"
      - "cannabis healing"
      - "dispensary near me" # (geo-targeted)
    content_clusters:
      - pillar: "Complete Guide to Cannabis in East Boston"
        clusters:
          - "best strains for beginners"
          - "edibles dosage guide"
          - "cannabis for pain relief"
          - "cannabis laws massachusetts 2026"
      - pillar: "Dispensary Near Logan Airport — Everything You Need to Know"
        clusters:
          - "cannabis before your flight"
          - "dispensary near maverick station"
          - "cannabis for boston tourists"
          - "flight kit cannabis"
    programmatic_pages:
      type: "location"
      template: "location_page"
      targets:  # Generate one page per target
        neighborhoods:
          - { name: "Maverick Square", slug: "maverick-square" }
          - { name: "Orient Heights", slug: "orient-heights" }
          - { name: "Jeffries Point", slug: "jeffries-point" }
          - { name: "Day Square", slug: "day-square" }
          - { name: "Eagle Hill", slug: "eagle-hill" }
        adjacent_towns:
          - { name: "Winthrop", slug: "winthrop-ma" }
          - { name: "Revere", slug: "revere-ma" }
          - { name: "Chelsea", slug: "chelsea-ma" }
          - { name: "Charlestown", slug: "charlestown" }
        broader_areas:
          - { name: "Downtown Boston", slug: "downtown-boston" }
          - { name: "South Boston", slug: "south-boston" }
          - { name: "North End", slug: "north-end" }
          - { name: "Back Bay", slug: "back-bay" }

  features:
    spanish_content: true
    product_pages: true
    market_reports: false  # CH doesn't publish market reports (GLASS site does)
    review_generation: true
    gbp_management: true

  compliance:
    state: "MA"
    regulations: "935 CMR 500"
    license: "MR283634"
    restrictions:
      - "No medical claims without 'consult your doctor' disclaimer"
      - "No claims of safety or harmlessness"
      - "No youth-targeted imagery or language"
      - "No price advertising in certain contexts (check CMR 500.105)"
      - "All content must include 21+ messaging"

  integrations:
    pos: "dutchie"
    loyalty: "alpine_iq"
    analytics: "ga4:G-LTSSR06PT8"
    gsc: "cannabishealingllc.com"
    gbp: "Cannabis Healing LLC"
```

### 4.2 Client Configuration Differences

| Dimension | CH (Dispensary) | AC (Cultivator) | Delivery (Delivery) |
|---|---|---|---|
| **Business Type** | Dispensary | Cultivator/Manufacturer | Delivery Operator |
| **Location** | East Boston, MA | Worcester area, MA | Clinton, MA (delivers statewide) |
| **Primary Audience** | Airport travelers + locals | Retail buyers (B2B: dispensaries. B2C: end consumers via retail partners) | Home delivery customers across MA |
| **Primary Keywords** | "dispensary near logan airport", "dispensary east boston" | "AC cannabis", "premium cannabis MA", "wholesale cannabis MA" | "cannabis delivery [town]", "weed delivery [town]" |
| **Programmatic Pages** | Location pages (neighborhoods + adjacent towns) | Strain pages, retailer locator pages ("where to buy AC products") | Town/city delivery pages (100+ municipalities) |
| **Content Clusters** | Tourist guides, local guides, product education | Craft cannabis, growing process, strain science, wholesale info | Delivery guides, product guides, zone-specific content |
| **Brand Voice** | Confident, warm, elevated streetwear culture | Premium, heritage-forward, craft/artisan, Aztec heritage | Convenient, reliable, midnight-aesthetic, urban |
| **Platform** | React + Vite + Tailwind → Netlify | React + Vite + Tailwind → Netlify | WordPress (after hack remediation) |
| **Adapter** | GitHubPRAdapter | GitHubPRAdapter | WordPressRESTAdapter |
| **Spanish Content** | Yes (57% Hispanic/Latino in East Boston) | No (unless data warrants) | Yes (multilingual play: Spanish + Portuguese) |
| **GLASS Data Use** | Product pages, price context, competitor positioning | Retail partner locations, brand presence mapping | Product availability by zone, delivery pricing |
| **Unique Angle** | Airport proximity, Flight Kits, culture house | Heritage brand, craft quality, vertical integration with HOP | Social equity, speed, zone coverage, app |
| **Link Building** | Tourism sites, airport guides, local East Boston | Industry publications, retail partner "where to buy" pages | Town/city community pages, delivery service directories |

### 4.3 Shared vs Client-Specific Content

| Content Type | Shared or Specific | Hosting |
|---|---|---|
| MA Cannabis Law Guides | **Shared** — canonical on GLASS public site, syndicated (with canonical tag) to clients | GLASS microsite |
| Market Reports | **Shared** — published on GLASS public site, clients link to it | GLASS microsite |
| Strain Guides | **Shared template, specific content** — same structure but customized with client's pricing, availability, and CTA | Each client site |
| Location Pages | **Client-specific** — unique to each client's location/service area | Each client site |
| Product Pages | **Client-specific** — based on each client's actual inventory | Each client site |
| Blog Posts | **Client-specific** — tailored to client's audience, brand voice, keyword targets | Each client site |

### 4.4 White-Label Capability

SIGNAL is built white-label by default:
- No "Powered by SIGNAL" or "Powered by Roviq" on client sites (unless opted in)
- All content appears to come from the client's brand
- Market reports on GLASS public site are branded to GLASS (Roviq's data product), not to individual clients
- Client dashboards (future SaaS) can be white-labeled for agencies that want to resell

---

## 5. SEO Automation

### 5.1 Technical SEO Automation

| Component | Automation Level | How |
|---|---|---|
| **XML Sitemap** | Fully automated | Generated at build time from page manifest. Submitted to GSC via API after each deploy. |
| **Robots.txt** | Semi-automated | Template maintained in repo. SIGNAL alerts if changes needed (e.g., new directory to block). |
| **Canonical URLs** | Fully automated | Every page gets a `<link rel="canonical">` tag. Self-referencing by default. Cross-domain canonical for syndicated content (e.g., shared guides → GLASS microsite). |
| **Schema Markup** | Fully automated | Generated from content frontmatter + GLASS data. JSON-LD injected per page. Validated against schema.org before publish. |
| **Meta Tags** | Fully automated | Title, description, Open Graph, Twitter Cards — all generated from content brief and template. |
| **Hreflang** | Fully automated | For pages with Spanish variants, proper `hreflang="es"` and `hreflang="en"` tags are generated. |
| **Core Web Vitals** | Monitored | Monthly Lighthouse audit triggered by SIGNAL. Flags any page scoring <90 on Performance. |
| **Redirect Management** | Semi-automated | SIGNAL tracks all published URLs. If a page slug changes, auto-generates 301 redirect in Netlify `_redirects` file. |
| **Indexing** | Automated | New pages submitted to GSC Indexing API within 1 hour of publish. |
| **404 Monitoring** | Automated | Weekly crawl of all tenant URLs. Any 404s flagged and redirect suggested. |

### 5.2 Programmatic Page Generation

#### For CH (Dispensary): Location Pages

SIGNAL generates location pages from a **target list** + **enrichment data**:

```
Target: { name: "Chelsea, MA", slug: "dispensary-chelsea-ma" }
    +
Template: location_page
    +
Enrichment:
  - Google Maps API: driving time from Chelsea to CH
  - Census data: demographics (e.g., population, median income)
  - GLASS data: number of competing dispensaries in Chelsea, avg prices
  - Local context: landmarks, MBTA access, parking info
  - PAA data: "People Also Ask" questions for "dispensary chelsea ma"
    =
Output: 1,500+ word unique location page with schema, FAQ, internal links
```

**Scale target for CH:** 20–25 hyper-local pages (East Boston neighborhoods + adjacent towns) in the first 8 weeks. Broader metro pages in months 3–6.

#### For Delivery: Town/City Pages

Same engine, different template:

```
Target: { name: "Framingham, MA", slug: "cannabis-delivery-framingham-ma" }
    +
Template: delivery_location_page
    +
Enrichment:
  - Delivery zone confirmation
  - Delivery time estimate
  - GLASS data: competing delivery services in this area
  - Local context: popular neighborhoods, landmarks
    =
Output: 1,500+ word unique delivery page
```

**Scale target for Delivery:** 50+ town pages in first 8 weeks (this is more aggressive because WordPress publishing is faster than Git-based deploys and Delivery's business model covers more geography).

#### For AC (Cultivator): Product/Retailer Pages

```
Target: { strain: "Golden Hour", type: "hybrid" }
    +
Template: strain_guide
    +
Enrichment:
  - GLASS data: which dispensaries carry this strain, at what prices
  - Lab data: COA data from AC's internal records
  - Effect profile: from strain databases + GLASS review aggregation
    =
Output: 1,200+ word strain guide with "where to buy" section
```

### 5.3 Local SEO

#### Google Business Profile (GBP) Management

| Task | Automation Level | Cadence |
|---|---|---|
| Profile completeness audit | Automated (checklist) | Monthly |
| Category optimization | Semi-automated (SIGNAL suggests, human applies) | Quarterly |
| Photo uploads | Manual (requires actual photos) | Weekly |
| GBP Posts | Semi-automated (SIGNAL drafts, human approves) | 3x/week |
| Q&A seeding | Semi-automated (SIGNAL generates Q&As from FAQ data) | Monthly |
| Review responses | Semi-automated (SIGNAL drafts response, human approves and posts) | Within 24 hours |
| Product catalog update | Semi-automated (synced from GLASS data, human verifies) | Weekly |

**Note on GBP API:** The Google Business Profile API has restricted access and requires business verification. Initial GBP management will be done via the GBP dashboard manually, with SIGNAL providing content drafts and scheduling reminders. Full API automation is a Phase 2 goal.

#### Citation Building (NAP Consistency)

SIGNAL maintains a **citation registry** — a list of all directories where each client is listed, with NAP data.

**Priority directories for CH:**

| Tier | Directory | Priority | Status |
|---|---|---|---|
| 1 | Google Business Profile | 🔴 Critical | Claimed |
| 1 | Weedmaps | 🔴 Critical | Listed — needs optimization |
| 1 | Leafly | 🔴 Critical | Create/claim |
| 1 | Yelp | 🔴 Critical | Claim and optimize |
| 2 | Apple Maps | 🟡 High | Submit |
| 2 | Bing Places | 🟡 High | Submit |
| 2 | TripAdvisor | 🟡 High | Create (tourists!) |
| 2 | Facebook Business | 🟡 High | Verify active |
| 2 | Dutchie listing | 🟡 High | Active |
| 3 | Cannabis.net | 🟢 Medium | Submit |
| 3 | PotGuide | 🟢 Medium | Submit |
| 3 | AllBud | 🟢 Medium | Submit |

**Every listing must have identical:**
- Name: Cannabis Healing
- Address: 4 Neptune Road, East Boston, MA 02128
- Phone: [consistent number]
- Description: Must include "5 minutes from Logan Airport"
- Website: https://cannabishealingllc.com

#### Review Generation

| Tactic | Implementation | Expected Volume |
|---|---|---|
| Post-purchase SMS (Alpine IQ) | Automated — 2 hours after purchase | 5–10/week |
| QR code at checkout | Physical card → direct Google review link | 3–5/week |
| Flight Kit insert | Card inside every kit → review link | 2–3/week |
| Staff verbal ask | Budtender training script | 2–5/week |
| Review response | Every review within 24 hours, keyword-rich | Signals to Google |

**Target:** 50 reviews in 60 days → 150 in 6 months → 500+ in 12 months

### 5.4 Link Building Strategy

#### Tier 1: GLASS Public Data as Link Magnet (Highest Priority)

This is SIGNAL's most defensible link building strategy:

1. **Launch GLASS public microsite** (`glass.report` or `masscannabisdata.com`)
2. Publish **weekly/monthly market reports:**
   - "Massachusetts Cannabis Price Index — February 2026"
   - "Cheapest Dispensaries by Region: Live Data from 500+ Stores"
   - "New Product Launches This Week: Boston Metro"
   - "Cannabis Delivery Price Comparison: Who's Cheapest?"
3. These reports get **naturally cited by:**
   - Cannabis industry journalists (Leafly News, MJBizDaily, Cannabis Business Times)
   - Local journalists covering cannabis (Boston Globe, Boston.com)
   - Reddit communities (r/bostontrees, r/trees)
   - Other dispensaries and brands (they share data about themselves)
   - Market analysts and investors
4. **Strategic linking:** Every market report links back to relevant client pages
   - "Data from 500+ dispensaries including **Cannabis Healing** in East Boston" → link to CH
   - "Based on delivery data from operators like **[Delivery client]** in Clinton" → link to Delivery
5. **This is the #1 reason to start with data content before programmatic pages.** Programmatic location pages don't earn backlinks. Data-driven content does. Backlinks build domain authority. Domain authority makes location pages rank.

#### Tier 2: Industry & Brand Partnerships

| Strategy | Execution | Expected Links |
|---|---|---|
| Brand "Where to Buy" pages | Ask brands CH carries to link to CH from their website | 5–10 per quarter |
| GLASS data widgets | Offer embeddable price/product widgets to industry sites | 3–5 per quarter |
| Guest posts | Pitch cannabis industry publications with data-driven articles | 2–3 per quarter |
| AC cross-linking | AC product pages link to CH as authorized retailer | 10+ permanent links |

#### Tier 3: Local & Community

| Strategy | Execution | Expected Links |
|---|---|---|
| East Boston community orgs | Sponsor local events, get listed on org websites | 2–3 per quarter |
| Tourism/travel content | Guest post on Boston travel blogs about "what to do near Logan" | 2–3 total |
| Government/regulatory | Optimize existing listings on masscannabiscontrol.com | Already referring traffic |
| Chamber of Commerce | Join East Boston chamber, get directory listing | 1 link |

#### Tier 4: Digital PR

| Strategy | Execution | Expected Links |
|---|---|---|
| HARO / journalist outreach | Respond to cannabis industry queries with GLASS data | 1–2 per quarter |
| Reddit value contributions | Genuine answers in r/bostontrees with username tied to CH | Referral traffic + signals |
| Data-driven press releases | When GLASS reveals interesting trends, press release it | 1–2 per quarter |

### 5.5 Answer Engine Optimization (AEO)

CH is already receiving traffic from `chatgpt.com` (3 sessions as of Feb 2026). AEO is the 2026 frontier. No cannabis company in MA is systematically optimizing for AI search.

**AEO Implementation:**

1. **FAQ schema on every page** — AI models pull FAQ structured data into answers
2. **Direct answer format** — Every page has at least one H2 that directly answers a question:
   ```
   ## How far is Cannabis Healing from Logan Airport?
   
   Cannabis Healing is located at 4 Neptune Road in East Boston, just 5 minutes
   by car from Logan Airport and 20 minutes walking distance...
   ```
3. **Entity consistency** — NAP data identical across all platforms (Google, Yelp, Weedmaps, Leafly, website) so AI models have high confidence in the entity
4. **Factual, structured content** — AI models prefer content that makes clear, verifiable factual statements. GLASS data enables this:
   - "Cannabis Healing carries 200+ products across 6 categories" (verifiable)
   - "Average flower price at Cannabis Healing is $X per eighth" (verifiable)
5. **Citation-worthy original data** — AI models cite sources they trust. GLASS market reports establish SIGNAL-powered sites as authoritative data sources
6. **Question-based keyword targeting** — Target the exact questions people ask AI:
   - "Where is the closest dispensary to Logan Airport?"
   - "What's the best dispensary in East Boston?"
   - "Can I buy weed near Boston airport?"

---

## 6. 8-Week Execution Plan (Revised)

### Design Principles for This Plan

This plan was revised based on two independent reviews that identified critical issues with the original:

1. **Start with GLASS data content, not programmatic pages.** Data content earns backlinks → backlinks build domain authority → authority makes location pages rank. The original plan had this backwards.
2. **Right-sized scope.** The original targeted 50+ location pages, 100+ product pages, 15+ blog posts, and 30+ backlinks in 8 weeks. That's unrealistic for 1 human + AI. This plan targets 20–25 location pages, 30–40 product pages, 8–10 blog posts, and 10–15 quality backlinks. Quality > quantity.
3. **CH stack-correct.** No WordPress references. Everything flows through the React/Vite/Tailwind/Netlify stack via GitHub PRs.
4. **Clear ownership.** Every task is labeled: 🤖 = AI-automated, 🤖👤 = AI drafts + human review, 👤 = human required.
5. **Dependency-aware.** Tasks are sequenced based on what needs to happen first.

---

### Week 0 (Days 1–3): Baseline & Infrastructure

**Theme: "Measure Before You Move"**

CH's site is NOT compromised (that's Delivery's WordPress site). CH is underdeveloped, not broken. Week 0 is about establishing baselines and infrastructure.

| Task | Owner | KPI | Time |
|---|---|---|---|
| Verify `cannabishealingllc.com` in Google Search Console | 👤 Randy | GSC verified | 30 min |
| Set up GA4 key events: Get Directions, Order Now, Phone, Flight Club signup | 👤 Randy | 5 events tracking | 2 hrs |
| Baseline audit: crawl site with Screaming Frog, record all indexed URLs | 🤖 SIGNAL | Crawl report | 1 hr |
| Record baseline keyword rankings for 50 target keywords | 🤖 SIGNAL | Ranking snapshot | 1 hr |
| Verify Core Web Vitals (Lighthouse audit all 10 pages) | 🤖 SIGNAL | CWV report | 30 min |
| Set up SIGNAL repo and tenant config for CH | 👤 Randy | Repo initialized | 2 hrs |
| GLASS API access confirmed and test queries working | 👤 Randy | API returning data | 1 hr |

**Week 0 Deliverables:**
- ✅ GSC verified and tracking
- ✅ GA4 conversion events live
- ✅ Baseline ranking snapshot saved
- ✅ SIGNAL infrastructure ready
- ✅ GLASS API integration tested

---

### Week 1: Technical Foundation + GBP + First Data Content

**Theme: "Quick Wins + Authority Seeds"**

| Task | Owner | KPI | Time |
|---|---|---|---|
| Quick-fix all title tags and meta descriptions (10 pages) | 🤖👤 | All 10 pages updated | 2 hrs |
| Add `LocalBusiness` + `FAQPage` schema to homepage, airport page, FAQ page | 🤖👤 | Schema live on 3 pages | 2 hrs |
| Claim/optimize Google Business Profile (100% completeness) | 👤 Randy | GBP 100% complete | 3 hrs |
| Upload 20+ photos to GBP (exterior, interior, products, parking) | 👤 Randy | 20 photos live | 2 hrs |
| Build and submit XML sitemap to GSC | 🤖👤 | Sitemap submitted | 1 hr |
| Publish **GLASS Market Report #1**: "Cannabis Prices in East Boston: Live Data from 12 Dispensaries" | 🤖👤 | Report live on GLASS site | 4 hrs |
| Publish **GLASS Data Page**: "Cheapest Dispensaries Near Logan Airport" (with live data table) | 🤖👤 | Data page live | 3 hrs |
| Begin claiming citations: Leafly, Yelp, Apple Maps, Bing Places (top 6) | 👤 Randy | 6 citations submitted | 3 hrs |
| First 3 GBP posts (deal, product highlight, traveler tip) | 🤖👤 | 3 posts live | 1 hr |

**Week 1 Deliverables:**
- ✅ All existing pages have optimized meta tags and schema
- ✅ GBP fully optimized with photos and posts
- ✅ 2 GLASS data pieces published (link-earning assets)
- ✅ 6 citations submitted
- ✅ Sitemap live in GSC

**Week 1 KPIs:**
- GBP impressions baseline established
- GSC data flowing (impressions, clicks, positions)
- GA4 conversion events firing

---

### Week 2: First Location Pages + More Data Content

**Theme: "Hyper-Local + Data Authority"**

| Task | Owner | KPI | Time |
|---|---|---|---|
| Publish 5 hyper-local location pages (East Boston neighborhoods only) | 🤖👤 | 5 pages live | 6 hrs |
| — Maverick Square, Orient Heights, Jeffries Point, Day Square, Eagle Hill | | | |
| Publish "Dispensary Near Logan Airport" deep-dive page (2,000+ words) | 🤖👤 | Page live | 3 hrs |
| Publish Spanish-language airport page: "Dispensario Cerca del Aeropuerto Logan" | 🤖👤 | Page live | 2 hrs |
| Publish **GLASS Market Report #2**: "New Cannabis Products This Week: Boston Metro" | 🤖👤 | Report live | 3 hrs |
| Begin outreach with data content: email 10 journalists/bloggers about Report #1 | 🤖👤 | 10 outreach emails sent | 3 hrs |
| Set up review generation: Alpine IQ post-purchase SMS + QR code at checkout | 👤 Randy | System active | 2 hrs |
| Claim 6 more citations (cannabis-specific directories) | 👤 Randy | 12 total citations | 2 hrs |
| GBP: 3 more posts | 🤖👤 | Posts live | 30 min |

**Week 2 Deliverables:**
- ✅ 7 new pages live (5 location + airport deep-dive + Spanish airport)
- ✅ 1 more GLASS data piece (total: 3)
- ✅ Outreach campaign launched
- ✅ Review generation system active
- ✅ 12 total citations

**Week 2 KPIs:**
- Pages indexed in GSC within 48 hours of publish
- First outreach responses received
- First post-purchase review request SMS sent

---

### Week 3: Content Cluster Foundation + Product Pages

**Theme: "Build Topical Authority"**

| Task | Owner | KPI | Time |
|---|---|---|---|
| Publish Pillar: "Complete Guide to Cannabis in East Boston" (3,000+ words) | 🤖👤 | Pillar live | 4 hrs |
| Publish 3 cluster blog posts: | 🤖👤 | 3 posts live | 4 hrs |
| — "Best Cannabis Strains for Beginners in Massachusetts" | | | |
| — "Cannabis Before Your Flight: What You Need to Know" | | | |
| — "Cannabis for Boston Tourists: A First-Timer's Guide" | | | |
| Generate 15 native product pages (top sellers, with GLASS price data + schema) | 🤖👤 | 15 product pages live | 5 hrs |
| Add FAQ schema to all new and existing pages | 🤖 | FAQPage schema on 20+ pages | 2 hrs |
| Internal linking pass: connect all new pages into hub-and-spoke | 🤖👤 | Links verified | 1 hr |
| 3 more GBP posts | 🤖👤 | Posts live | 30 min |
| Respond to all new Google reviews within 24 hours | 🤖👤 | All reviews responded | Ongoing |

**Week 3 Deliverables:**
- ✅ 1 pillar + 3 cluster posts + 15 product pages = 19 new pages
- ✅ FAQPage schema on 20+ total pages
- ✅ Hub-and-spoke internal linking established
- ✅ Total site: ~36 pages (up from 10)

**Week 3 KPIs:**
- GSC impressions trending up from Week 1 baseline
- Product pages indexed
- First organic keyword movement (branded terms + low-competition local)

---

### Week 4: Expand Location Pages + Link Building

**Theme: "Widen the Net"**

| Task | Owner | KPI | Time |
|---|---|---|---|
| Publish 8 more location pages (adjacent towns + broader Boston) | 🤖👤 | 8 pages live | 6 hrs |
| — Winthrop, Revere, Chelsea, Charlestown, Downtown Boston, South Boston, North End, Back Bay | | | |
| Publish 2 Spanish-language pages (East Boston local + Maverick Square) | 🤖👤 | 2 pages live | 2 hrs |
| Publish 2 more blog posts: | 🤖👤 | 2 posts live | 3 hrs |
| — "Edibles Dosage Guide: How Much Should You Take?" | | | |
| — "Dispensary Open Late in Boston: Your After-Hours Options" | | | |
| Email 5 brands CH carries — request "where to buy" backlink | 👤 Randy | 5 outreach emails | 2 hrs |
| Publish **GLASS Market Report #3**: "Cannabis Price Index: MA — Q1 2026" | 🤖👤 | Report live | 4 hrs |
| Follow up on Week 2 outreach — send GLASS Report #3 to non-responders | 🤖👤 | Follow-ups sent | 1 hr |
| 3 GBP posts | 🤖👤 | Posts live | 30 min |

**Week 4 Deliverables:**
- ✅ 12 more pages (8 location + 2 Spanish + 2 blog)
- ✅ Total site: ~48 pages
- ✅ 4 total GLASS data pieces published
- ✅ Brand outreach for backlinks initiated
- ✅ 18+ total citations

**Week 4 KPIs:**
- First backlink from brand partner or journalist
- Spanish pages indexed
- "dispensary near logan airport" entering top 20 (from unranked)
- First new Google reviews from automated system

---

### Week 5: Product SEO + AEO Layer

**Theme: "Answer Every Question"**

| Task | Owner | KPI | Time |
|---|---|---|---|
| Generate 15 more product pages (expanding to 30 total) | 🤖👤 | 30 product pages live | 4 hrs |
| Implement AEO-optimized FAQ sections on top 15 performing pages | 🤖👤 | 15 pages updated | 3 hrs |
| Research and answer 30 "People Also Ask" questions across existing pages | 🤖👤 | 30 PAAs addressed | 3 hrs |
| Publish 2 data-driven blog posts using GLASS data: | 🤖👤 | 2 posts live | 4 hrs |
| — "Cheapest Dispensaries in East Boston: Data from GLASS" | | | |
| — "Cannabis Price Trends: Is Flower Getting Cheaper in Boston?" | | | |
| Create Flight Kit landing page (unique product page with schema) | 🤖👤 | Page live | 2 hrs |
| 3 GBP posts | 🤖👤 | Posts live | 30 min |
| Review and respond to all reviews | 🤖👤 | All responded | Ongoing |

**Week 5 Deliverables:**
- ✅ 30 total product pages
- ✅ AEO content on 15+ pages
- ✅ 30 PAA questions answered
- ✅ Total site: ~65 pages
- ✅ Flight Kit page (unique competitive advantage)

**Week 5 KPIs:**
- FAQ rich snippets appearing in Google for any CH pages
- Product pages showing up in GSC
- "flight kit cannabis" — targeting #1 (zero competition)
- 10+ Google reviews from automated system

---

### Week 6: Link Building Sprint + Authority Content

**Theme: "Earn Authority"**

| Task | Owner | KPI | Time |
|---|---|---|---|
| Guest post outreach: pitch 5 cannabis/travel publications | 🤖👤 | 5 pitches sent | 3 hrs |
| Publish shareable data asset: "Cannabis Prices in Boston — Interactive Map" (GLASS microsite) | 🤖👤 | Asset live | 5 hrs |
| Publish 2 blog posts (healing/wellness theme, brand-aligned): | 🤖👤 | 2 posts live | 3 hrs |
| — "The Healing Power of Terpenes: A Complete Guide" | | | |
| — "Cannabis and Sleep: Best Strains for Insomnia" | | | |
| Create "East Boston Community Guide" resource page | 🤖👤 | Guide live | 2 hrs |
| Request backlinks from 5 brands on "where to buy" pages | 👤 Randy | 5 requests sent | 1 hr |
| Submit 3 HARO responses using GLASS data | 🤖👤 | 3 submissions | 2 hrs |
| 3 GBP posts + 3 GBP Q&A seeds | 🤖👤 | Posts + Q&As live | 1 hr |

**Week 6 Deliverables:**
- ✅ 5 guest post/PR pitches sent
- ✅ 1 major shareable data asset (interactive map)
- ✅ 2 more blog posts + 1 community guide
- ✅ Total site: ~68 pages
- ✅ 5+ GLASS data pieces total (all earning backlinks)

**Week 6 KPIs:**
- First guest post published or accepted
- First HARO mention
- 3+ backlinks from brand partners confirmed
- 20+ total Google reviews

---

### Week 7: Optimize + Scale Winners

**Theme: "Double Down on What Works"**

| Task | Owner | KPI | Time |
|---|---|---|---|
| Analyze GSC + ranking data: identify quick-win keywords (positions 5–20) | 🤖 | 15+ quick wins identified | 2 hrs |
| Optimize top 10 underperforming pages (update content, strengthen keywords) | 🤖👤 | 10 pages updated | 4 hrs |
| Generate 5 more product pages (based on search demand data) | 🤖👤 | 35 total product pages | 2 hrs |
| Publish 5 more location pages targeting identified opportunities | 🤖👤 | 25 total location pages | 4 hrs |
| A/B test meta titles on top 5 performing pages | 🤖 | Tests running | 1 hr |
| Publish 3 more Spanish-language pages (top-performing English pages translated) | 🤖👤 | 5 total Spanish pages | 3 hrs |
| GBP: weekly posts + review responses + fresh photos | 🤖👤 | Content live | 1 hr |

**Week 7 Deliverables:**
- ✅ 10 pages optimized based on real performance data
- ✅ 5 new location pages (25 total)
- ✅ 5 new product pages (35 total)
- ✅ 5 total Spanish pages
- ✅ Total site: ~78 pages

**Week 7 KPIs:**
- Rankings improving for 15+ keywords
- Quick-win keywords moving to page 1
- Spanish pages indexed
- Organic sessions +100% from baseline (from ~700/mo to ~1,400+/mo)

---

### Week 8: Measurement + Automation + Roadmap

**Theme: "Lock It In"**

| Task | Owner | KPI | Time |
|---|---|---|---|
| Comprehensive ranking report: all 50+ target keywords | 🤖 | Report delivered | 2 hrs |
| Traffic analysis: organic sessions, conversion events, user journeys | 🤖👤 | Report delivered | 2 hrs |
| GBP Insights report: impressions, clicks, calls, directions | 👤 Randy | Report delivered | 1 hr |
| Identify and fix any indexing issues (pages not indexed, crawl errors) | 🤖 | 0 issues | 1 hr |
| Document automated content publishing pipeline (SOP for ongoing) | 🤖👤 | SOP document | 2 hrs |
| Create monthly maintenance playbook | 🤖👤 | Playbook document | 2 hrs |
| Build Month 3–6 expansion roadmap | 🤖👤 | Roadmap document | 3 hrs |
| Competitive re-analysis: check BOUTIQ, Rolling Releaf, Happy Valley responses | 🤖 | Analysis complete | 2 hrs |
| Prepare client presentation: before/after + next phase proposal | 🤖👤 | Deck ready | 3 hrs |

**Week 8 Deliverables:**
- ✅ Complete before/after performance report
- ✅ Automated pipeline documented and operational
- ✅ Monthly maintenance playbook
- ✅ Month 3–6 roadmap
- ✅ Client-ready presentation

**Week 8 KPIs (8-Week Summary):**

| Metric | Baseline | Week 8 Target | Stretch Target |
|---|---|---|---|
| Total pages on site | 10 | 78+ | 90+ |
| Location pages | 1 (airport) | 25+ | 30+ |
| Product pages | 0 | 35+ | 40+ |
| Blog posts | 1 | 10+ | 12+ |
| Spanish pages | 0 | 5+ | 8+ |
| GLASS data pieces | 0 | 5+ | 7+ |
| Keywords tracked | 0 | 50+ | 75+ |
| Keywords on page 1 | 0 | 5–10 | 15+ |
| Keywords on pages 1–2 | 0 | 15–20 | 30+ |
| Organic sessions/month | ~700 | 1,500+ | 2,500+ |
| Google reviews | ~1 | 30+ | 50+ |
| Backlinks gained | 0 | 10–15 | 20+ |
| GBP impressions/month | Unknown | 2x baseline | 3x baseline |
| GA4 key events | 0 tracking | Tracking + baseline | Optimizing |

---

### Ongoing (Month 3+): Maintenance Rhythm

| Cadence | Task |
|---|---|
| **Daily** | Review responses (AI drafts, human approves) |
| **3x/week** | GBP posts (AI generates, human approves) |
| **Weekly** | 1 blog post + 5 product page updates + rank check |
| **Biweekly** | GLASS data content (market report or data page) |
| **Monthly** | Full ranking report, traffic analysis, competitor check, content audit |
| **Quarterly** | Strategy review, keyword universe refresh, new content cluster planning |

**Ongoing human time:** 5–8 hours/week (review, approve, strategic decisions)
**AI handles:** ~80% of ongoing content generation, monitoring, and reporting

---

## 7. Tech Stack

### 7.1 Build vs Buy

| Component | Decision | Rationale |
|---|---|---|
| **Content Generation Engine** | BUILD | Core IP. LLM API + custom templates + GLASS integration. This is SIGNAL's brain. |
| **Template System** | BUILD | YAML-based templates for each content type. Simple to author, powerful in combination with LLM. |
| **Quality Gate Engine** | BUILD | Custom rules engine checking content against compliance, quality, and duplicate standards. |
| **Publishing Adapters** | BUILD | GitHubPR adapter, WordPress REST adapter, etc. Core to multi-client support. |
| **Schema Generator** | BUILD | JSON-LD generation from content frontmatter + GLASS data. Straightforward scripting. |
| **Internal Link Engine** | BUILD | Graph-based link suggestion and management. Core SEO value. |
| **Rank Tracking** | BUY | Ahrefs or SEMrush API. Not worth building; mature tools exist. |
| **Backlink Monitoring** | BUY | Ahrefs API. Industry standard. |
| **Keyword Research** | BUY | Ahrefs/SEMrush + "People Also Ask" scraping. |
| **Crawling/Technical Audit** | BUY | Screaming Frog (free tier) or Sitebulb. |
| **Analytics** | BUY | Google Analytics 4 + Google Search Console (both free). |
| **Translation** | BUY | DeepL API for drafts + native speaker review. |
| **GBP Management** | MANUAL (for now) | GBP API access is restricted. Manual via dashboard with SIGNAL content drafts. |
| **Citation Management** | BUY (optional) | BrightLocal or Whitespark. Or manual for small client count. |

### 7.2 Specific Tools, APIs, and Costs

| Tool/Service | Purpose | Monthly Cost | Notes |
|---|---|---|---|
| **Ahrefs Lite** | Rank tracking, backlink monitoring, keyword research | $129/mo | Primary SEO intelligence tool |
| **OpenAI API (GPT-4+)** | Content generation LLM | $50–150/mo | Usage-based; estimated for ~80 pages/month |
| **Claude API** | Review/QA pass on generated content | $30–60/mo | Second model for quality verification |
| **DeepL API** | Spanish translation drafts | $25/mo | Pro tier for API access |
| **Screaming Frog** | Technical crawling | Free (500 URLs) | Free tier sufficient for CH |
| **Google Search Console** | Indexing, performance | Free | |
| **Google Analytics 4** | Traffic analytics | Free | |
| **GitHub** | Code hosting, PR-based publishing | Free | Already in use |
| **Netlify** | CH/AC hosting + deploy | Free–$19/mo | Already in use |
| **BrightLocal** | Citation management + local rank tracking | $29/mo | Optional — can do manually |
| **Firecrawl** | PAA scraping, SERP analysis | $19/mo | Part of GLASS infra |
| **Vercel/Netlify** | GLASS public microsite hosting | Free–$20/mo | Static site |
| **Domain** | glass.report or similar | $12/year | One-time |
| **Total Monthly** | | **$295–450/mo** | |

### 7.3 Where SIGNAL Lives

**Repository:** Standalone monorepo — `roviq/signal`

```
signal/
├── packages/
│   ├── core/                   # Content generation engine, templates, quality gates
│   │   ├── src/
│   │   │   ├── generator/      # LLM-powered content generation
│   │   │   ├── templates/      # YAML content templates
│   │   │   ├── quality/        # Quality gate checks
│   │   │   ├── schema/         # JSON-LD schema generator
│   │   │   ├── links/          # Internal linking engine
│   │   │   └── translate/      # Translation pipeline
│   │   └── package.json
│   ├── adapters/               # Publishing adapters
│   │   ├── github-pr/          # Git-based publishing (React/Netlify)
│   │   ├── wordpress/          # WordPress REST API publishing
│   │   └── static/             # Static file generation
│   ├── data/                   # GLASS API client, data normalization
│   ├── monitor/                # Rank tracking, analytics, reporting
│   └── api/                    # REST API server (Fastify)
├── tenants/                    # Tenant configuration files
│   ├── ch.yaml
│   ├── ac.yaml
│   └── delivery.yaml
├── scripts/                    # CLI tools for manual operations
│   ├── generate.ts             # Generate content for a tenant
│   ├── publish.ts              # Publish approved content
│   ├── audit.ts                # Run technical SEO audit
│   └── report.ts               # Generate SEO report
├── tests/
├── package.json
├── tsconfig.json
└── README.md
```

**Tech:** Node.js + TypeScript + Fastify (API server) + BullMQ (job queue for content generation) + PostgreSQL (content DB, link graph, tenant config) + Redis (queue, cache)

**Why standalone?** SIGNAL is not part of GLASS (different concern: GLASS = data, SIGNAL = content/SEO). Not part of any client repo (SIGNAL serves multiple clients). It's a Roviq-owned platform product.

**Deployment:** Railway or Render (same infra as GLASS). Background workers for content generation. API server for dashboard/management. CLI scripts for manual operations.

---

## 8. Competitive Moat

### 8.1 Why SIGNAL Beats SERPCOM Prometheus

| Dimension | SERPCOM Prometheus | SIGNAL | Advantage |
|---|---|---|---|
| **Content Quality** | Thin, templated (200–400 words, obvious town-name swaps) | 1,500+ word unique pages with local data, neighborhood context, transit info, FAQs | 3–5x content depth |
| **Data Integration** | None — generic product descriptions, no market data | GLASS feeds live pricing, trends, inventory, competitor intelligence into every page | Structural moat — can't be copied without building a scraping network |
| **Content Freshness** | Pages appear static; no evidence of regular updates | Product pages update with live pricing; market reports refresh weekly/monthly | Google rewards freshness |
| **AEO/AI Search** | No FAQ schema, no question-answer format, no AI optimization | Every page has FAQ schema, direct-answer format, entity consistency for AI citation | First-mover in cannabis AEO |
| **Multilingual** | English only | English + Spanish (with proper hreflang, not just translation) | 57% of East Boston is Hispanic/Latino |
| **Speed** | Manual process — Prometheus requires human setup per client | AI-automated pipeline — new pages generated and published in minutes | 10x faster content production |
| **Platform Lock-in** | WordPress only | Platform-agnostic adapters (React/Netlify, WordPress, headless CMS, static) | Can serve any client regardless of stack |
| **Schema Markup** | Product schema present but limited | Comprehensive JSON-LD on every page: LocalBusiness, Product, FAQPage, Article, BreadcrumbList | Richer rich snippets |
| **Link Building** | Directory listings + SERPCOM portfolio page | GLASS market data as organic link magnet + directories + brand partnerships + PR | Defensible backlink flywheel |
| **Cost to Client** | Estimated $3,000–5,000/mo | $1,500–3,000/mo (managed) or $500–1,500/mo (self-serve SaaS) | 50–70% cheaper |

### 8.2 Why SIGNAL Can't Be Easily Replicated

1. **GLASS data is the moat.** SIGNAL's content is uniquely valuable because it's powered by real-time market intelligence from 500+ dispensaries and 70K+ products. Building that data infrastructure takes 6–12 months and significant engineering investment. Any competitor copying SIGNAL's content approach without GLASS data produces generic content indistinguishable from what agencies already generate.

2. **Data flywheel compounds.** More clients using SIGNAL → more data collected about what content ranks → better templates and generation → better results → more clients. GLASS data gets richer over time (more historical data = more trend analysis = more linkable content).

3. **Multi-client intelligence.** SIGNAL learns from every client engagement. What keyword strategies work for dispensaries informs delivery clients and vice versa. SERPCOM may have multiple cannabis clients, but their per-client Prometheus setup doesn't appear to share learnings across clients systematically.

4. **AI-native architecture.** SERPCOM Prometheus was built in the pre-AI era. It's a WordPress framework with templating. SIGNAL is built AI-first — every component assumes LLM content generation, automated quality checks, and adaptive optimization. Retrofitting Prometheus to compete would require a rewrite.

5. **Public data moat.** The GLASS public microsite earns backlinks for all clients simultaneously. One investment in data journalism powers domain authority across every client site. SERPCOM has no equivalent — their client sites are isolated islands.

### 8.3 How GLASS Data Makes This Unique

| Without GLASS (What Agencies Do) | With GLASS (What SIGNAL Does) |
|---|---|
| "Cannabis Healing has a great selection of products" | "Cannabis Healing carries 215 products across 6 categories, with flower starting at $X — below the East Boston average of $Y" |
| "We offer competitive pricing" | "Our average eighth is $X vs the area average of $Y (data from 12 East Boston dispensaries)" |
| "Visit our dispensary near Logan Airport" | "We're the closest dispensary to Logan Airport. The next closest is [X] in [Y], 15 minutes further. Compare prices →" |
| "Check out our strain selection" | "We carry [X] of the top 10 most popular strains in MA this month, including [strain] which has dropped $Y in price over 30 days" |
| Generic blog: "Best Strains for Beginners" | Data-driven blog: "Best Strains for Beginners in MA — Based on Sales Data from 500+ Dispensaries" |
| No market intelligence | "Massachusetts Cannabis Price Index — Feb 2026: Flower down 3%, edibles up 7%, delivery premiums averaging 15%" |

**The difference:** GLASS makes every piece of SIGNAL content factual, specific, data-rich, and impossible to replicate by hand. This is the content that earns citations from journalists, gets shared on Reddit, and gets cited by AI models. It's also the content that Google rewards with higher rankings because it provides genuine value that thin templated pages never can.

---

## Appendix A: Client Configuration Examples {#appendix-a}

### CH Configuration (Abbreviated)

```yaml
tenant:
  id: "ch"
  name: "Cannabis Healing"
  business_type: "dispensary"
  platform:
    type: "react-vite-netlify"
    repo: "randytorres/ch-web"
    adapter: "GitHubPRAdapter"
  audience:
    primary: "Airport travelers (Land. Walk. Relax.)"
    secondary: "East Boston locals (57% Hispanic/Latino)"
    tertiary: "Greater Boston cannabis consumers"
  unique_angles:
    - "Closest dispensary to Logan Airport (5 min)"
    - "Flight Kits for travelers"
    - "Culture House — not just a dispensary"
    - "Open 12–10pm daily (late hours)"
    - "Spanish-language content for East Boston community"
  competitor_focus: ["BOUTIQ", "Happy Valley", "East Boston Cannabis"]
  programmatic_focus: "Neighborhood + adjacent town location pages"
  spanish_content: true
```

### AC Configuration (Abbreviated)

```yaml
tenant:
  id: "ac"
  name: "Advanced Cultivators"
  business_type: "cultivator"
  platform:
    type: "react-vite-netlify"
    repo: "randytorres/ac-web-new"
    adapter: "GitHubPRAdapter"
  audience:
    primary: "Dispensary buyers (B2B wholesale)"
    secondary: "End consumers seeking premium craft cannabis"
  unique_angles:
    - "Mexican/Aztec heritage brand"
    - "Craft quality, small-batch"
    - "Vertical integration with HOP"
    - "AC Certified retail partnership program"
  competitor_focus: ["Other MA cultivators"]
  programmatic_focus: "Strain guides + retailer locator pages"
  spanish_content: false
```

### Delivery Configuration (Abbreviated)

```yaml
tenant:
  id: "delivery"
  name: "Delivery" # (formerly Delivered Inc — name pending deal close)
  business_type: "delivery"
  platform:
    type: "wordpress"
    url: "https://deliveredinc.com" # (after hack remediation)
    adapter: "WordPressRESTAdapter"
  audience:
    primary: "Home delivery customers across Greater Boston + suburbs"
    secondary: "Cannabis consumers who prefer convenience"
  unique_angles:
    - "Social equity certified"
    - "Speed and reliability"
    - "Zone coverage (100+ municipalities)"
    - "Midnight cannabis lounge aesthetic"
  competitor_focus: ["Rolling Releaf (SERPCOM client)", "Zyp Run"]
  programmatic_focus: "Town/city delivery coverage pages (100+)"
  spanish_content: true
  portuguese_content: true
  prerequisite: "HACK REMEDIATION MUST COMPLETE BEFORE ANY SEO WORK"
```

---

## Appendix B: API Reference {#appendix-b}

### Content Generation Endpoint

```
POST /v1/tenants/:tenantId/content/generate

Body:
{
  "type": "location_page",          // location_page | product_page | blog_post | market_report | strain_guide
  "target": {
    "name": "Chelsea, MA",
    "slug": "dispensary-chelsea-ma",
    "primary_keyword": "dispensary chelsea ma"
  },
  "options": {
    "language": "en",               // en | es | pt
    "include_glass_data": true,
    "include_faq": true,
    "min_words": 1500,
    "auto_publish": false            // if true, skip human review
  }
}

Response:
{
  "content_id": "cnt_abc123",
  "status": "draft",                 // draft | review | approved | published | failed
  "type": "location_page",
  "slug": "dispensary-chelsea-ma",
  "content": "...",                  // Markdown/MDX content
  "frontmatter": { ... },           // SEO metadata, schema, internal links
  "quality_score": {
    "word_count": 1847,
    "readability": 8.2,
    "keyword_density": 1.8,
    "duplicate_score": 0.12,
    "compliance_pass": true,
    "schema_valid": true,
    "internal_links": 5,
    "overall": "PASS"
  },
  "glass_data_used": [
    { "type": "competitor_count", "value": 4, "source": "glass_api", "timestamp": "2026-02-12T06:00:00Z" },
    { "type": "avg_flower_price", "value": 38.50, "source": "glass_api", "timestamp": "2026-02-12T06:00:00Z" }
  ],
  "created_at": "2026-02-12T07:15:00Z"
}
```

### Publishing Endpoint

```
POST /v1/tenants/:tenantId/content/:contentId/publish

Body:
{
  "adapter_config": {
    "create_pr": true,               // For GitHubPR adapter
    "auto_merge": false,             // Require manual merge
    "branch": "signal/dispensary-chelsea-ma"
  }
}

Response:
{
  "status": "published",
  "url": "https://cannabishealingllc.com/dispensary-chelsea-ma/",
  "pr_url": "https://github.com/randytorres/ch-web/pull/42",
  "gsc_submission": "pending",
  "published_at": "2026-02-12T08:00:00Z"
}
```

### Reporting Endpoint

```
GET /v1/tenants/:tenantId/reports?type=weekly&period=2026-W07

Response:
{
  "period": "2026-W07",
  "rankings": {
    "tracked_keywords": 52,
    "page_1": 7,
    "page_2": 12,
    "improved": 23,
    "declined": 4,
    "new": 8
  },
  "traffic": {
    "organic_sessions": 1245,
    "organic_change": "+34%",
    "top_pages": [ ... ],
    "top_keywords": [ ... ]
  },
  "content": {
    "pages_published": 8,
    "pages_updated": 3,
    "total_pages": 65
  },
  "backlinks": {
    "new": 3,
    "lost": 0,
    "total": 18
  },
  "gbp": {
    "impressions": 4521,
    "clicks": 234,
    "calls": 18,
    "directions": 87
  }
}
```

---

## Appendix C: Content Templates (Expanded) {#appendix-c}

### Location Page — Full Structure

```markdown
---
title: "Dispensary in [Location] — [Client Name]"
slug: "dispensary-[location-slug]"
description: "[Client Name] is [distance/time] from [Location]. Shop [product count]+ products..."
keywords: ["dispensary [location]", "cannabis [location]", "weed [location]"]
schema:
  localBusiness: { ... }
  faqPage: { ... }
  breadcrumb: ["Home", "Locations", "[Location]"]
locale: "en"
template: "location_page"
---

# Dispensary in [Location] — [Client Name]

[2-3 sentence intro with primary keyword, distance, and unique value prop]

## Why Choose [Client Name] Near [Location]?

[3-4 paragraphs covering:
- What makes us unique (airport proximity, product selection, atmosphere)
- What we carry (categories, product count from GLASS)
- Pricing context (average prices vs. local area from GLASS)
- Customer experience (reviews, hours, loyalty program)]

## Getting to [Client Name] from [Location]

### By Car
[Driving directions, parking info, drive time from GLASS/Maps data]

### By Public Transit
[MBTA directions, closest station, walking time]

### By Rideshare
[Uber/Lyft pickup info, cost estimate]

[Embedded Google Map with custom pin]

## What We Carry

| Category | Products Available | Price Range |
|---|---|---|
| Flower | [count from GLASS] | $[range from GLASS] |
| Edibles | [count] | $[range] |
| Vapes | [count] | $[range] |
| Pre-Rolls | [count] | $[range] |
| Concentrates | [count] | $[range] |
| Accessories | [count] | $[range] |

[CTA: View our full menu →]

## [Location] Cannabis FAQ

### How far is [Client Name] from [Location]?
[Direct answer with specific time/distance]

### What are the hours at [Client Name]?
[Hours with "open late" callout if applicable]

### Do I need a medical card to buy cannabis in Massachusetts?
[Standard MA recreational answer]

### Can I order online for pickup?
[Yes + link to Dutchie/ordering]

### Do you have a loyalty program?
[Flight Club details]

## Nearby Dispensaries vs [Client Name]

[Brief, factual comparison — not disparaging competitors. Focus on CH's advantages: proximity, hours, selection, pricing]

## Visit Us Today

[Final CTA with address, phone, hours, order link, directions link]
```

### Product Page — Full Structure

```markdown
---
title: "[Product Name] — [Brand] | [Client Name]"
slug: "products/[product-slug]"
description: "Shop [Product Name] by [Brand] at [Client Name]. [THC%] THC, $[price]..."
keywords: ["[product name]", "[brand] [product type]", "[product type] east boston"]
schema:
  product: { name, brand, price, availability, thc, cbd }
  faqPage: { ... }
  breadcrumb: ["Home", "Products", "[Category]", "[Product Name]"]
template: "product_page"
glass_refresh: "daily"
---

# [Product Name] — [Brand]

[Product image]

**Category:** [Flower/Edible/Vape/etc]  
**Brand:** [Brand Name]  
**THC:** [X]% | **CBD:** [Y]%  
**Price:** $[price] ([comparison to category average from GLASS])

[CTA: Order Now →]

## About [Product Name]

[AI-generated unique description — NOT manufacturer copy. 150-300 words covering:
- What it is and what to expect
- Effects profile (with appropriate disclaimers)
- Terpene profile (if available)
- Best for: [use cases]
- Recommended for: [experience level]]

## Price Context

[GLASS-powered]:
- This product: $[price]
- Average [category] price at [Client Name]: $[avg]
- Average [category] price in East Boston: $[avg]
- Price trend: [↑↓→] [X]% over 30 days

## Similar Products

[3-5 related products with links, prices, and brief descriptions — from GLASS data]

## Frequently Asked Questions

### What does [Product Name] feel like?
[Effects description with disclaimer]

### How should I dose [Product Name]?
[Dosing guidance appropriate to category]

### Is [Product Name] available for online ordering?
[Yes + order link]

[CTA: Order [Product Name] for Pickup →]
```

---

## Appendix D: Cost Model {#appendix-d}

### Monthly Operating Costs

| Category | Item | Cost | Notes |
|---|---|---|---|
| **SEO Tools** | Ahrefs Lite | $129/mo | Rank tracking, backlink analysis, keyword research |
| **AI APIs** | OpenAI API | $50–150/mo | Content generation (~80 pages/month) |
| | Claude API | $30–60/mo | Quality review pass |
| **Translation** | DeepL Pro | $25/mo | Spanish content drafts |
| **Hosting** | SIGNAL on Railway | $20–50/mo | API server + workers + DB |
| | GLASS microsite | $0–20/mo | Static site on Netlify/Vercel |
| **Optional** | BrightLocal | $29/mo | Citation management |
| | Screaming Frog | Free | Technical crawling |
| **Total** | | **$283–463/mo** | |

### Revenue vs Cost (Per Client)

| | Managed Service | SaaS (Future) |
|---|---|---|
| Client pays | $1,500–3,000/mo | $500–1,500/mo |
| SIGNAL operating cost per tenant | ~$100–150/mo (marginal) | ~$50–100/mo (marginal) |
| Shared infrastructure cost | ~$150–250/mo (amortized) | ~$100–150/mo (amortized) |
| **Gross margin** | **70–85%** | **80–90%** |

### Break-Even

- **1 client (CH) at $1,500/mo:** Revenue covers all SIGNAL operating costs + tools. Randy's time is the real cost.
- **3 clients at $1,500/mo avg:** $4,500/mo revenue vs ~$500/mo costs = $4,000/mo contribution margin. Randy spends ~15 hrs/week across all 3 (5 hrs each).
- **10 clients (SaaS) at $750/mo avg:** $7,500/mo revenue vs ~$1,000/mo costs = $6,500/mo contribution margin. Most work is automated; Randy spends ~2 hrs/week per client on review/strategy.

---

## Document History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-02-12 | Initial final plan. Synthesized from research report + 2 independent reviews + client documentation. Corrected all identified factual errors (CH/Delivered mix-up, platform mismatch). Right-sized 8-week timeline. Added GLASS public microsite strategy. |

---

*This is the definitive plan for SIGNAL. It is comprehensive enough to hand to an architect and say "build this." Every section is informed by real client data, competitive intelligence, and two rounds of independent expert review.*

*Next step: Randy reviews and approves → Begin Week 0.*
