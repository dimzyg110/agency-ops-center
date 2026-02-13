# SIGNAL — SEO Automation Engine

**Version:** 0.1.0  
**Last Updated:** February 13, 2026  
**Status:** Functional MVP (with caveats)

---

## What Signal Is

### Purpose

Signal is a CLI tool built by Roviq for automated SEO content generation targeting cannabis dispensary clients. It produces React/JSX content that deploys via GitHub PRs to Netlify-hosted sites.

### Design Philosophy

- **Data-first content**: Signal injects real market data (prices, products, competitor info) from GLASS API into generated content
- **Pipeline automation**: Research → Generate → Review → Humanize → Publish
- **Quality gating**: Automated checks prevent low-quality or non-compliant content from publishing
- **Multi-client ready**: YAML-based configuration with Zod validation per client

### Target Users

- Roviq's internal team (primary)
- Automated content generation for client websites
- Specifically designed for cannabis dispensaries in Massachusetts

### How It Fits Into Roviq's Client Workflow

1. **Client onboarded** → Config created in `src/config/clients/*.yaml`
2. **Content strategy defined** → Keywords and content types configured
3. **Signal generates** → Runs pipeline to produce TSX content
4. **Review passes** → 12 quality checks verify SEO/compliance
5. **Humanize** → AI pattern removal + brand voice application
6. **Publish** → Creates GitHub PR for client review/merge

---

## Architecture

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SIGNAL PIPELINE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│  │ RESEARCH │───▶│ GENERATE │───▶│  REVIEW  │───▶│HUMANIZE  │    │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘    │
│       │                                                    │        │
│       │                                                    ▼        │
│       │                                          ┌──────────────┐   │
│       └─────────────────────────────────────────▶│   PUBLISH   │   │
│                                                └──────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

| Stage | File | What It Does |
|-------|------|--------------|
| **Research** | `src/pipeline/research.ts` | Fetches GLASS market data, Google autocomplete suggestions, generates keyword brief with LLM |
| **Generate** | `src/pipeline/generate.ts` | Calls LLM to produce content, renders TSX templates with schema markup |
| **Review** | `src/pipeline/review.ts` | Runs 12 automated quality checks (SEO, compliance, word count) |
| **Humanize** | `src/pipeline/humanize.ts` | Removes AI patterns (24+ patterns), optionally runs LLM enhancement pass |
| **Publish** | `src/pipeline/publish.ts` | Creates GitHub branch, commits content, opens PR |

### CLI Commands

```bash
# Generate a single content piece (skips publishing)
signal generate --client ch --type location-page --target "East Boston"

# Run full pipeline (generate + review + humanize + publish)
signal pipeline --client ch --type location-page --target "East Boston"

# Generate all content types for a client
signal pipeline --client ch --type all

# Publish an existing generated file
signal publish --client ch --content ./output/ch/location-page-east-boston.tsx

# Show client configuration status
signal status --client ch

# Score content for AI patterns
signal score @path/to/content.tsx
signal score "some text content"
```

### Config System

**Location:** `src/config/clients/*.yaml`

**Schema (Zod):**
```typescript
{
  client: {
    name: string;           // "Cannabis Healing"
    slug: string;          // "ch" 
    domain: string;         // "cannabishealing.com"
    platform: "react-netlify";  // Locked to React/Netlify for now
    repo: string;          // "randytorres/ch-web"
    contentDir: string;    // "src/data"
  },
  audience: {
    primary: string;
    secondary: string;
    language: string[];
  },
  keywords: {
    primary: string[];
    location: string[];
    product: string[];
  },
  content: {
    locationPages: { enabled: boolean; towns: string[]; };
    productPages: { enabled: boolean; categories: string[]; };
    marketReports: { enabled: boolean; frequency: string; };
    blogPosts: { enabled: boolean; frequency: string; };
  },
  tone: {
    voice: string;
    avoid: string[];
  }
}
```

**Current Clients:**
| Client | Config File | Status |
|--------|-------------|--------|
| Cannabis Healing (CH) | `src/config/clients/ch.yaml` | Configured, primary test client |

### LLM Dependencies

**Supported Providers (in priority order):**

| Provider | Env Variable | Models Used |
|----------|--------------|-------------|
| OpenAI | `OPENAI_API_KEY` | gpt-4o (content), gpt-4o-mini (humanizer/research) |
| NVIDIA | `NVIDIA_API_KEY` | meta/llama-3.3-70b-instruct (content), meta/llama-3.1-8b-instruct (humanizer/research) |
| OpenRouter | `OPENROUTER_API_KEY` | anthropic/claude-3.5-sonnet (content), claude-3.5-haiku (humanizer/research) |

**Retry Logic:**
- 3 retries with exponential backoff (1s → 2s → 4s + jitter)
- Retries on: 429, 500, 502, 503, timeouts, ECONNRESET

---

## Current Capabilities

### What Actually Works ✅

| Capability | Status | Notes |
|------------|--------|-------|
| **CLI commands** | ✅ Works | `generate`, `pipeline`, `publish`, `status`, `score` all execute |
| **Config loading** | ✅ Works | CH YAML loads and validates via Zod |
| **TypeScript** | ✅ Clean | `tsc --noEmit` passes |
| **LLM integration** | ✅ Works | Uses NVIDIA fallback (OpenAI key expired) |
| **Research module** | ✅ Works | Google autocomplete + LLM keyword brief |
| **Review module** | ✅ Works | 12 quality checks run |
| **Humanizer** | ✅ Works | Rule-based + LLM enhancement |
| **Template rendering** | ✅ Works | TSX output is structurally valid |
| **Schema markup** | ✅ Works | JSON-LD for LocalBusiness, Product, FAQ, Article, Breadcrumb |
| **Internal linking** | ✅ Works | Topic clusters, breadcrumbs |
| **GitHub publishing** | ✅ Implemented | Branch → commit → PR flow |
| **Batch mode** | ✅ Works | `--type all` generates all configured content |

### Content Types Supported

| Type | Template | Target Word Count |
|------|----------|-------------------|
| Location Page | `templates/location-page.ts` | 1,500-2,000 |
| Product Page | `templates/product-page.ts` | 800-1,200 |
| Market Report | `templates/market-report.ts` | 1,500-2,000 |
| Blog Post | `templates/blog-post.ts` | 1,500-2,000 |

### What's Configured for CH

```
Client: Cannabis Healing
Platform: react-netlify
Repo: randytorres/ch-web

Location Pages: East Boston, Chelsea, Revere, Winthrop
Product Pages: flower, edibles, pre-rolls, vapes
Market Reports: weekly
Blog Posts: 2x-weekly

Primary Keywords:
- dispensary near logan airport
- cannabis near boston airport  
- east boston dispensary
```

---

## Current Limitations & Gaps

### Critical Issues (Broken/Missing)

| Issue | Impact | Status |
|-------|--------|--------|
| **GLASS API routes mismatch** | Market data unavailable | GLASS client expects `/operators`, `/prices`, `/products` but real API uses `/api/v1/*` routes |
| **GLASS_API_KEY not set** | No market data | Auth required but not configured |
| **OpenAI API key expired** | Using NVIDIA fallback | Pipeline works but OpenAI not usable |
| **GITHUB_TOKEN not set** | Can't publish | PR creation would fail |
| **DATABASE_URL invalid** | No job tracking | Local PostgreSQL not available |

### Content Quality Issues

| Issue | Description |
|-------|-------------|
| **Generic output without GLASS data** | LLM generates filler content ("we have 0 products") when GLASS is unavailable |
| **Schema incomplete in output** | LocalBusiness schema generated with empty address/phone fields |
| **No client-specific context** | No supplemental data file with real business details (address, hours, products) |

### Missing Features (vs. Complete SEO Tool)

| Missing Feature | Impact |
|-----------------|--------|
| **Google Business Profile management** | #1 local SEO factor not managed |
| **Google Search Console integration** | No indexing API, no performance data |
| **Review management** | #2 local ranking factor not addressed |
| **Citation management** | NAP consistency critical for local SEO |
| **Backlink monitoring** | No Ahrefs/SEMrush integration |
| **Rank tracking** | DB schema exists but not implemented |
| **Core Web Vitals monitoring** | Page speed affects rankings |
| **Image optimization** | No alt text, no compression |
| **Content refresh system** | Pages become stale as prices change |
| **hreflang tags** | Spanish content needs proper tags |
| **Open Graph / Twitter Cards** | Incomplete social sharing |

### Fragile/Hacky Areas

| Area | Issue |
|------|-------|
| **Config embedded in index.ts** | Schema defined at bottom of CLI file (code smell) |
| **Humanizer LLM pass** | Can sometimes strip JSX structure, falls back to rule-based |
| **Review word counting** | Counts HTML tag "words" not actual text |
| **Batch error handling** | Partial failures logged but pipeline continues silently |
| **No tests** | Zero unit tests exist |

---

## Room for Improvement

### High Priority

1. **Fix GLASS client routes** — Update to match actual API (`/api/v1/operators`, `/api/v1/prices`, `/api/v1/products`)
2. **Configure GLASS_API_KEY** — Get auth token for production GLASS access
3. **Add client context file** — Create `ch-context.md` with real business details (address, hours, Flight Kit pricing)
4. **Populate schema fields** — Pass real address/phone/hours from config to schema generators
5. **Get GITHUB_TOKEN** — Token with repo write access for `randytorres/ch-web`

### Medium Priority

6. **Content refresh system** — Flag pages for regeneration when GLASS data changes significantly
7. **Add unit tests** — At minimum for pipeline stages and quality gates
8. **Batch mode testing** — Full end-to-end test of `--type all`
9. **Improve word counting** — Count actual text words, not HTML tags
10. **Title tag validation** — Add to review module (currently only checks description)

### Lower Priority

11. **Database setup** — Railway PostgreSQL for job tracking
12. **GSC integration** — Indexing API submission post-publish
13. **Rank tracking** — Pull positions via Ahrefs API
14. **Auto-merge path** — For content passing quality gates above threshold
15. **PR templates** — Include quality score, data freshness in PR body

### Integration Opportunities

| Opportunity | Data Source | Use Case |
|-------------|-------------|----------|
| **Competitor pricing** | GLASS prices | "Our eighth is $38 vs. area average $42" |
| **Product availability** | GLASS products | "Blue Dream in stock at 3 nearby dispensaries" |
| **CCC data** | CCC API | Compliance verification, license status |
| **GSC quick wins** | Google Search Console | Identify ranking opportunities (positions 5-20) |

---

## Comparison: Original Vision vs Current State

### Original Vision (from BUILD-SUMMARY.md, STATUS.md, planning docs)

**What Signal Was Supposed to Be:**
- Complete SEO automation engine for cannabis dispensary clients
- Data-rich content with real GLASS market data (prices, products, competitors)
- 1,500+ word location pages with 7 required sections
- 12 automated quality gates (not just 3)
- LLM-based humanizer (not find-and-replace)
- Complete schema markup (LocalBusiness, Product, FAQPage, Article, BreadcrumbList)
- Real keyword intelligence (not just static YAML lists)
- GitHub PR publishing with batch support
- Multi-client support (CH, AC, Delivery)
- Production-ready for real client sites

### What It Actually Is Right Now

| Dimension | Original Vision | Current State |
|-----------|-----------------|---------------|
| **Content length** | 1,500+ words | ✅ Achieved (LLM generates target) |
| **Quality gates** | 12 checks | ✅ Implemented (12 checks) |
| **Humanizer** | LLM-based | ✅ Implemented (rule + LLM pass) |
| **Schema markup** | Complete | ⚠️ Partial (generators exist but not fully populated) |
| **GLASS integration** | Real market data | ❌ Routes wrong, no API key |
| **Keyword intelligence** | SERP analysis, PAA, briefs | ⚠️ Briefs work, no real SERP data |
| **Multi-client** | CH, AC, Delivery | ⚠️ Only CH configured |
| **Publishing** | Batch PRs | ✅ Implemented |
| **Database** | Job tracking | ❌ Not connected |
| **Tests** | Unit tests | ❌ None exist |
| **Production use** | Live on client sites | ❌ Never published a real page |

### Brutal Assessment

**The gap is significant but bridgeable.**

SIGNAL has the right architecture. The pipeline structure is sound, the module boundaries are clean, and the code quality is acceptable. What it's missing is:

1. **Real data integration** — GLASS is not connected
2. **Configuration completeness** — Missing API keys, no supplemental context files
3. **Testing** — No unit tests, limited end-to-end testing
4. **Production hardening** — Error handling is basic, observability is minimal

**Current readiness score: ~60/100** (functional but not production-hardened)

The February 12-13 fixes addressed the P0/P1 issues from the initial review:
- ✅ LLM generation now produces 1,500+ words
- ✅ Humanizer uses LLM pass
- ✅ 12 quality gates implemented
- ✅ Schema generators complete
- ✅ Research module with keyword briefs
- ✅ Batch pipeline supported

What's left is primarily:
- **Integration work** (GLASS, GitHub)
- **Configuration** (keys, context files)
- **Hardening** (tests, error handling)

---

## Environment Variables Required

| Variable | Current Status | Required For |
|----------|----------------|--------------|
| `OPENAI_API_KEY` | ❌ Expired | Content generation (primary) |
| `NVIDIA_API_KEY` | ✅ Working | Content generation (fallback) |
| `GLASS_API_BASE_URL` | ✅ Set | Market data |
| `GLASS_API_KEY` | ❌ Not set | GLASS API authentication |
| `GITHUB_TOKEN` | ❌ Not set | PR publishing |
| `DATABASE_URL` | ❌ No local DB | Job tracking |

---

## File Structure

```
signal/
├── src/
│   ├── index.ts              # CLI entry + config schema
│   ├── config/
│   │   ├── schema.ts         # Zod validation (embedded in index.ts actually)
│   │   └── clients/
│   │       └── ch.yaml       # Cannabis Healing config
│   ├── pipeline/
│   │   ├── research.ts       # GLASS data + keyword brief
│   │   ├── generate.ts      # LLM content + templates
│   │   ├── review.ts        # 12 quality checks
│   │   ├── humanize.ts      # AI pattern removal
│   │   └── publish.ts       # GitHub PR creation
│   ├── llm/
│   │   └── openai-client.ts # Multi-provider LLM client
│   ├── glass/
│   │   ├── client.ts        # GLASS API client
│   │   └── data-injector.ts # Market data transformation
│   ├── seo/
│   │   ├── schema-markup.ts  # JSON-LD generators
│   │   ├── meta.ts          # Title/description/OG
│   │   ├── internal-links.ts # Topic clusters + breadcrumbs
│   │   └── sitemap.ts       # (exists but not wired)
│   ├── templates/
│   │   ├── location-page.ts
│   │   ├── product-page.ts
│   │   ├── market-report.ts
│   │   └── blog-post.ts
│   └── publishers/
│       └── github-pr.ts     # GitHub API integration
├── output/                   # Generated content lands here
├── package.json
├── tsconfig.json
└── SIGNAL.md                # This file
```

---

## Running Signal

### Prerequisites

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Or run in development mode
npm run dev -- generate --client ch --type location-page --target "East Boston"
```

### Typical Workflow

```bash
# 1. Check client status
signal status --client ch

# 2. Generate a single page (test mode)
signal generate --client ch --type location-page --target "East Boston" --raw

# 3. Run full pipeline (generates + reviews + humanizes + publishes)
signal pipeline --client ch --type location-page --target "East Boston"

# 4. Generate all content for client
signal pipeline --client ch --type all
```

### Output Location

Generated content appears in:
```
output/<client-slug>/<content-type>-<target>.tsx
```

Example: `output/ch/location-page-east-boston.tsx`

---

## Next Steps

1. **Immediate**: Fix GLASS client routes and get API key
2. **This week**: Add client context file with real business details  
3. **This week**: Get GITHUB_TOKEN configured
4. **Next week**: Full batch pipeline test end-to-end
5. **Ongoing**: Add unit tests, harden error handling

---

*Documentation generated February 13, 2026*
