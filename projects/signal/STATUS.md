# SIGNAL Status Report

**Date:** February 13, 2026  
**Tested by:** Subagent opus-signal-ch-blog

---

## Does It Work End-to-End?

**Partially.** The pipeline runs without crashing, but produces low-quality content due to missing integrations.

### What Works ✅
- **CLI** — `signal status`, `signal generate`, `signal pipeline` commands all execute correctly
- **Config loading** — CH YAML config loads and validates via Zod
- **Template rendering** — TSX output is structurally valid with proper schema markup, breadcrumbs, internal links, FAQs
- **LLM integration** — Generates content via OpenAI-compatible APIs (tested with NVIDIA API as fallback)
- **Research module** — Google Autocomplete fetching works; LLM keyword brief generation works
- **Review module** — 12 quality checks run and report results
- **TypeScript** — Clean compile in strict mode (`npx tsc --noEmit` passes)

### What's Broken or Missing ❌

1. **GLASS API routes don't match** — Signal expects `/operators`, `/prices`, `/products` at the GLASS API base URL, but the actual GLASS API uses `/api/v1/operators` (and requires auth). The GLASS client needs to be updated to match the real API routes.

2. **OpenAI API key is expired/invalid** — The `OPENAI_API_KEY` in the environment returns 401. Workaround: Used NVIDIA API (`meta/llama-3.3-70b-instruct`) as an OpenAI-compatible drop-in replacement. The LLM client was patched to support this.

3. **No GLASS_API_KEY configured** — Even with correct routes, the GLASS API requires authentication (`GLASS_API_KEY` env var). Without it, all market data is empty.

4. **Content quality without data is poor** — Without GLASS data, the LLM generates generic filler ("we have 0 products in stock across 0 categories"). The templates show empty pricing tables and meaningless competitor comparisons.

5. **GitHub publishing untested** — No `GITHUB_TOKEN` available to test PR creation. The publish step would fail.

6. **Database not connected** — `DATABASE_URL` points to localhost PostgreSQL which isn't available. The DB layer (Drizzle ORM) hasn't been tested.

---

## Environment Variables Needed

| Variable | Status | Required For |
|----------|--------|-------------|
| `OPENAI_API_KEY` | ❌ Expired/invalid | Content generation, humanizer, research |
| `NVIDIA_API_KEY` | ✅ Working | Fallback LLM (patched in) |
| `GLASS_API_BASE_URL` | ✅ Set but routes 404 | Market data, pricing, products |
| `GLASS_API_KEY` | ❌ Not set | GLASS API authentication |
| `GITHUB_TOKEN` | ❌ Not set | PR publishing |
| `DATABASE_URL` | ❌ No local DB | Job tracking, content history |

---

## Fixes Applied During This Session

### 1. GLASS failure resilience (research.ts)
- **Before:** `runResearch()` threw immediately if GLASS API returned errors
- **After:** Catches GLASS failures and proceeds with empty market data, logs warning
- **Impact:** Pipeline no longer crashes when GLASS is unavailable

### 2. Multi-provider LLM support (openai-client.ts)
- **Before:** Only supported OpenAI API (`OPENAI_API_KEY` required)
- **After:** Detects NVIDIA API key and uses it as OpenAI-compatible endpoint with appropriate model mapping
- **Models:** NVIDIA `meta/llama-3.3-70b-instruct` for content, `meta/llama-3.1-8b-instruct` for research/humanizer
- **Impact:** Pipeline works even when OpenAI key is expired

### 3. LLM availability detection (research.ts, generate.ts)
- **Before:** Research keyword brief and FAQ generation checked only `OPENAI_API_KEY`
- **After:** Checks for either `OPENAI_API_KEY` or `NVIDIA_API_KEY`
- **Impact:** LLM-powered keyword briefs and FAQ answers work with NVIDIA fallback

---

## What Needs to Be Fixed for Production

### P0 — Must Fix
1. **Get a valid OpenAI API key** or formalize NVIDIA as the production LLM provider
2. **Fix GLASS client routes** — Update `src/glass/client.ts` to use `/api/v1/operators`, `/api/v1/prices`, `/api/v1/products` (or whatever the actual GLASS API routes are)
3. **Configure GLASS_API_KEY** — Get an auth token for the GLASS API
4. **Content quality** — The LLM-generated content is generic without real data. Even with GLASS data, the prompts need CH-specific context (real product names, actual Flight Kit details, store hours, address) that should come from config or a supplemental data file

### P1 — Important
5. **Add client-specific context file** — Create a `src/config/clients/ch-context.md` or similar that feeds real business details (address, hours, products, Flight Kit pricing, brand names) into the LLM prompt so content isn't generic
6. **GitHub token for publishing** — Get a token with repo write access for `randytorres/ch-web`
7. **Humanizer needs JSX awareness** — The LLM humanizer can sometimes strip or mangle JSX tags. The safety check only looks for `<article` but should validate full JSX integrity
8. **Review module word count** — The review should count actual text words, not HTML tag "words"

### P2 — Nice to Have
9. **Database setup** — Set up PostgreSQL (Railway or local) for job tracking and content history
10. **Batch mode testing** — `signal pipeline --client ch --type all` hasn't been tested end-to-end
11. **Unit tests** — No tests exist for any module
12. **CI/CD** — No GitHub Actions or deployment pipeline

---

## First CH Blog Post Outcome

Since Signal couldn't produce publication-quality content (due to missing GLASS data and generic LLM output), the first CH blog post was created manually using:
- Signal's TSX template structure and schema markup generation
- The existing hand-written draft from `clients/ch/seo-content/post-1-logan-airport-guide.md`
- CH-specific details from the content brief, SEO strategy, and content calendar

**Output saved to:**
- `/data/workspace/projects/signal/output/ch/blog-post-logan-airport-guide.tsx` (raw)
- `/data/workspace/clients/ch/seo-content/signal-post-1-logan-guide.tsx` (review-ready)
- `/data/workspace/clients/ch/seo-content/REVIEW-NOTE-POST-1.md` (cover note for Brian)

---

*Status report generated February 13, 2026*
