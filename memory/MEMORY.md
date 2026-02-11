# Long-Term Memory

_Curated patterns, preferences, and lessons. Updated weekly from daily logs._

---

## Randy's Preferences

- Hates traditional sales — never suggest cold calling, pitching, or chasing
- Loves cinematic content — everything should feel premium, not generic
- Moves fast — needs help staying focused on revenue-generating work
- Direct communication only — no corporate speak, no filler
- Cannabis industry expertise — understands the market deeply

## Client Patterns

- **AC:** Creative client, values aesthetic and storytelling. Debbie and Clarice execute. Generate concepts → Randy curates → they produce.
- **CH:** Practical client, needs data-driven results. Brian is the point of contact. Growth through SEO, automations, and partner channels.
- **HOP:** Launch-phase client. Kam is the partner. Needs full GTM before anything else.

## Operations Patterns

- Newsletter is the core funnel — everything feeds into it
- Margin Snapshots are the best lead magnet — free, specific, proves capability
- Multi-model reviews catch different issues — always use 2+ models for review
- Sprint pricing ($3K) is the sweet spot for initial engagement
- Content automation for social is the biggest time sink — needs systemization

## What Works

- Value-first approach > any sales tactic
- AI-generated content + Randy curation > pure AI output
- Ecosystem thinking > isolated projects
- Weekly rhythm > ad-hoc work

## What Doesn't Work

- Cold outreach (Randy won't do it, clients don't respond)
- Over-building before validation (too many ideas, not enough shipped)
- Manual social posting (time sink, should be automated)

## GLASS Deployment Learnings (2026-02-11)

### Railway Deployment
- **railway.toml Dockerfile path bug**: Railway kept reverting to wrong Dockerfile (`apps/web/Dockerfile` instead of `services/api/Dockerfile`). Fixed by explicitly setting in root railway.toml and committing.
- **Clerk authentication requires BOTH keys**: `@clerk/fastify` plugin needs `secretKey` AND `publishableKey` in config. Missing publishable key causes 500 errors on all requests including `/health`.
- **Database migrations from sandbox blocked**: Railway Postgres rejects connections from OpenClaw sandbox (network restrictions). Must run via `railway run --service <name> '<command>'` or from authorized environment.
- **Multi-service deployment**: Each service needs its own railway.toml with correct dockerfilePath. Root repo railway.toml controls which service builds.

### Scraper Architecture
- **Playwright requires custom base image**: Use `mcr.microsoft.com/playwright:v1.50.1-jammy` as base, install Node.js separately.
- **10 MA dispensaries configured**: Cannabis Healing (client) + 9 competitors, all on Dutchie platform.
- **Test scrape successful**: Firecrawl captured full HTML (240KB) from Cannabis Healing menu.

### Model Configuration
- **Opus 4.6 models unreliable**: Listed in config, simple tests pass, but complex tasks fail with "Request contains an invalid argument" API error. Falls back to Sonnet 4.5. Only use for trivial single-turn tasks.
- **Codex 5.3 CLI doesn't exist**: `/usr/local/bin/codex` is a blog tool (codex-cli npm package), not OpenAI Codex. No `codex exec` command available. TOOLS.md reference is incorrect. Use `openai/gpt-5.2-codex` via API instead.
- **OpenClaw OAuth for Codex**: Store credentials in `auth-profiles.json`, valid until 2026-12-20.

---

_Last updated: 2026-02-11 21:06 UTC (GLASS auth broken, 3 fix attempts failed, backend also broken now)_
