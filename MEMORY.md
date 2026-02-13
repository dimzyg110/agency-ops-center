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

- **AC:** Creative client, values aesthetic and storytelling. Debbie and Clarice execute. Generate concepts → Randy curates → they produce. Active cultivator license (Indoor Tier 2, 5-10K sqft, Lowell). Has prerolls license. Pending manufacturer license (edibles/concentrates — incomplete). First Latino-owned rec cultivator in MA. Physical retail location coming soon.
- **CH:** Practical client, needs data-driven results. Brian is the point of contact. Growth through SEO, automations, and partner channels. Retailer in East Boston (MR283634). No delivery license. Website repo: `randytorres/ch-web` (React + Vite + Tailwind, Netlify deploy). Blog posts in `src/data/blogPosts.js`.
- **HOP:** Launch-phase client. Kam is the partner. Needs full GTM before anything else. Sells cannabis products through AC's license (white labeled).
- **Delivered Inc (Lead):** Licensed delivery operator (MD1303), Clinton MA, ~30 towns Central MA. Founders: Ruben Seyde, Eddy Twal, Tut Liu. Social equity. Can expand statewide. Site hacked (casino spam — confirmed live by 3 agents, 5 URLs in sitemap, WordPress compromised Oct 2022-Aug 2023). Partnership deal: equity + rev share + small upfront. App play = first operator-branded cannabis delivery app in MA. AC supplies wholesale. Exclusivity until April 2029. **Jointly partnership**: Delivered currently fulfills for Jointly (third-party AI shopping app) — building own app = owning the customer. License expires 3/5/2026 (renewal should have been filed by 12/5/2025, they're late). Renewal = 4-step process + $10K fee, NOT just a payment. Google Play bans cannabis sales apps (Android blocked). Lantern tried in 2022, died in 2 months.

## Operations Patterns

- Newsletter is the core funnel — everything feeds into it
- Margin Snapshots are the best lead magnet — free, specific, proves capability
- Multi-model reviews catch different issues — always use 2+ models for review
- Sprint pricing ($3K) is the sweet spot for initial engagement
- Content automation for social is the biggest time sink — needs systemization
- **When research reveals a competitor tool/platform, the COO move is "build our own" — don't just report, propose the play across all clients** (learned 2026-02-10, Prometheus incident)
- **Cross-client pattern recognition is mandatory** — every finding should be scanned against CH, AC, HOP, and pipeline leads
- **Every insight has two layers: client impact AND Roviq growth** — client work is a means to grow Roviq. If we build a tool for one client, ask: can we sell this to 26 others? Is this a new vertical? Does this reposition Roviq in the market? (clarified 2026-02-10)

## What Works

- Value-first approach > any sales tactic
- AI-generated content + Randy curation > pure AI output
- Ecosystem thinking > isolated projects
- Weekly rhythm > ad-hoc work

## What Doesn't Work

- Cold outreach (Randy won't do it, clients don't respond)
- Over-building before validation (too many ideas, not enough shipped)
- Manual social posting (time sink, should be automated)
- WordPress for client sites — Randy builds in React, each client has unique brand identity. Blog generator should produce React-compatible content, not WP posts.
- **"Lead magnets" as a concept** — Randy rejected the Margin Snapshot Portal (Feb 11). "Feels old school and not helpful." Wants infrastructure that creates ongoing relationships, not funnel tricks. Build things operators depend on daily, not PDFs they download once.
- **Competing feature-for-feature with established SaaS** — Apex Trading is the MA wholesale standard (METRC integration, CRM, multi-state). Don't replicate. Differentiate on layers they don't cover (delivery, demand gen, local intelligence).
- **Opus 4.6T subagent bug**: Works as main session model but fails on multi-turn subagent sessions (thinking.signature field required error). Single-turn subagent tasks work. Large consolidation tasks also crash (terminated before writing output). Fallback: Gemini 3 Pro High for subagents needing long writes or multi-turn.
- **Opus 4.6 (non-thinking)**: Returns 404 on Antigravity — model not available without thinking enabled.
- **Antigravity Opus models removed from config** (Feb 12) — all unavailable, causing instant subagent failures. Gemini + Sonnet Antigravity models kept.
- **CamoFox browser plugin installed** (Feb 12) — `@askjo/camofox-browser`, anti-detection Firefox fork. Good for scraping bot-protected dispensary sites. Gateway restart needed to activate.
- Kimi K2.5 for large file writes — NVIDIA proxy truncates at ~8K chars. **FIXED: use `openrouter/moonshotai/kimi-k2.5` instead.** OpenRouter handles 48K+ in a single write. NVIDIA route still works for small tasks (free). Moonshot direct (`moonshot/kimi-k2.5`) requires balance top-up.
- **iOS Safari video autoplay**: `muted + playsInline + autoPlay` should work without user gesture. Common failure causes: (1) conditional rendering that destroys/recreates video elements (breaks autoplay), (2) too many simultaneous videos, (3) Low Power Mode, (4) video at tiny size (1x1px won't autoplay), (5) wrong H.264 profile. Use baseline profile level 3.1 for maximum iOS compatibility. Only render one video at a time (active card).
- **Canvas video rendering** to avoid native play button: works but video must be full-size for iOS to autoplay it. Canvas approach adds CPU overhead on mobile.
- **archive.org for music**: Direct CDN URLs work (`ia800608.us.archive.org`), redirect URLs don't work for cross-origin audio. Many mainstream tracks are "dark" (restricted). Video uploads sometimes have accessible audio that can be extracted with ffmpeg.
- **GitHub Pages video hosting**: Works but cache-control is only 10 min (`max-age=600`). Not as fast as R2 CDN but avoids cross-origin issues. Deploy takes ~45-60s after push.
- **ffmpeg video compression**: CRF 25, H.264 baseline profile, 1080p, `movflags +faststart` gives good mobile results. 87MB → 7MB (92% reduction) while keeping acceptable quality.

## Tech Stack for Client Work

- **Delivered**: Blaze POS (open API at `apidocs.blaze.me`, BPN partner network). App = React Native frontend, Blaze = backend. Blaze handles dispatch, driver app, payments, manifests, inventory. App only needs to be the customer experience layer.
- **CH**: React + Vite + Tailwind on Netlify. Blog posts in `src/data/blogPosts.js`. Repo: `randytorres/ch-web` (private).
- **AC**: Swift native iOS (AC Blacksite app — Randy built). Cinematic UX.
- **All clients**: React-based sites, unique brand identities, NO WordPress.

## Delivered Partnership — Key Facts

- Blaze POS is their platform (they approached Blaze for partnership too)
- License MD1303 covers statewide delivery — scaling is operational, not regulatory
- Social equity exclusivity locked until April 2029 (CCC voted 4-0)
- Only 27 delivery operators in MA — no one has a mobile app
- Midnight Cannabis Lounge = the brand direction (premium launch standard)
- React Native for cross-platform (iOS + Android), 12-week MVP, Delivered owns app IP
- AC supplies wholesale (house brand "Delivered Collection" at 35%+ margins)
- Proposal V2 final: `clients/_leads/delivered/PROPOSAL-DRAFT.md` (commit `32a4e39`)
- Brand vision in reserve: `clients/_leads/delivered/plans/plan-3-full.md` (63K, Kimi)

---

- **19 skills from skills.sh installed** (Feb 10): programmatic-seo, seo-audit, content-strategy, copywriting, copy-editing, email-sequence, social-content, schema-markup, analytics-tracking, vercel-react-native-skills, competitor-alternatives, referral-program, docx, pdf, pptx, xlsx, doc-coauthoring, webapp-testing, web-design-guidelines. In `~/.agents/skills/`.
- **Humanizer pipeline works**: MiniMax M2.5 is reliable and fast for humanizer passes. Opus 4.6T works if task completes in one turn.
- **Gemini is Imagen ONLY**: Removed from all task/review/research roles (Randy directive Feb 13). Use `gemini-2.0-flash-exp-image-generation` for image gen via `generateContent` API with `responseModalities: ["IMAGE","TEXT"]`. The old `imagen-3.0-generate-002` model 404s.
- **MiniMax M2.5 is the workhorse**: Fast, smart, cheap ($1/$4 per M tokens), 1M context, 65K output. Use for anything with clear requirements. Route: `openrouter/minimax/minimax-m2.5`.
- **COO must NEVER execute client work directly**: Even "quick" tasks like image generation must be spawned to subagents. Randy called this out Feb 13.
- **Auto-review pipeline**: When spawning work agents, immediately spawn 2 reviewers (different models) without waiting. Codex (T1) + MiniMax (T3) is the standard reviewer pair.
- **Branch protection on GLASS**: GitHub Teams, PR required, push restricted to `randytorres` + `randyt1444-arch`. COO merges after review.
- **migration_log table**: `glass.migration_log` tracks all applied migrations. Always log after applying.
- **GitHub Enterprise quirk**: Roviq-AI org shows `plan.name: "free"` on REST API even with Enterprise Cloud ($42/mo). Enterprise features work via UI but some API calls fail. Enterprise slug = `roviq`.
- **No deploy service credentials configured** — need Vercel/Netlify/Cloudflare token from Randy to deploy demos/sites from sandbox. GitHub Pages blocked on private repos (free plan).
- **Decoded demo built** at `projects/decoded-demo/` — Vite + React + Tailwind, TikTok-style feed. Randy hasn't seen it yet.

- **Roviq website direction (V3)**: White/editorial theme, ACME-inspired layout. Bracketed nav with numbers, left-aligned hero, video placeholder. Geist Pixel/Sans/Mono fonts kept. Randy providing hero video. Red accent `#D94F3D`. Commit `0d22df7` on `Roviq-AI/roviq-web`. Mobile hero: autoplay 0.5x, 70% width, 50% height. Scroll-scrub doesn't work on mobile (hero = first section, no scroll distance).
- **ION (Independent Operators Network)**: Randy-approved directionally but effectively superseded by GLASS. ION's intelligence-first approach folded into GLASS Threat Radar.
- **GLASS ecosystem**: Hub + spokes. Free core (Price Wire + Threat Radar + Margin Engine). Revenue spokes (Cue + Delivered + AC Toll Processing + Roviq Agency). Newsletter = distribution only. Consolidated plan at `projects/glass/GLASS-PLAN.md` (Gemini synthesis of 3 model plans). Source plans at `/tmp/glass-plan-{opus,kimi,gpt}.md`.
- **Apex Trading**: Industry standard wholesale platform in MA. METRC integration, CRM, email marketing, invoicing. Competitors: LeafLink ($5B+ annual orders), Leaf Trade. Pricing hidden behind demo calls. GLASS doesn't replace it, operates on layers Apex doesn't cover.
- **AC Toll Processing outreach**: 85 personalized emails ready at `clients/ac/toll-processing/outreach-emails.md`. 65 cultivators + 21 microbusinesses + 321 retailers prospected. Page live at `advancedcultivatorsllc.com/toll-processing` (pw: `ac2026`). Commit `a4154e6`.
- **Subagent screenshots unreliable**: Fresh screenshots from live URLs looked worse than original images. Randy said "go back to previous versions." Lesson: don't replace working assets without Randy seeing the replacements first.

## GLASS Scraper (DEFINITIVE — Feb 13 cleanup)

- **⚠️ READ `projects/glass/src/scripts/SCRAPER-ARCHITECTURE.md` FIRST** — full architecture, run commands, and troubleshooting.
- **The ONLY Dutchie scraper is `scrape-dutchie.ts`** using CamoFox BrowserPool (HTTP API at localhost:9377). Firecrawl is NOT used. The old `scrape-dutchie-ma.ts` was REMOVED Feb 13.
- **CamoFox HTTP API** at `localhost:9377` — managed by OpenClaw plugin (`autoStart: true`). Don't launch Playwright separately. Endpoints: POST /tabs, GET /tabs/:id/snapshot, POST /tabs/:id/click, POST /tabs/:id/scroll, POST /tabs/:id/navigate, DELETE /tabs/:id.
- **DATABASE_URL in sandbox = Neon, not Railway**: Always override: `DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway"`
- **Run command**: `DATABASE_URL=<railway-url> bash scripts/run-daily-dutchie.sh` or `npx tsx scripts/scrape-dutchie.ts --skip-discovery --db`
- **Benchmarks** (Feb 12): 235 stores, 195 succeeded (83%), 57,514 prices, ~5.2 hours.
- **CamoFox crashes**: Zombie processes pile up, port 9377 goes dead. Fix: `cd /data/.openclaw/extensions/camofox-browser && node server.js &` or gateway restart. Use `--resume <run-id>` after crash.
- **CamoFox is single-browser**: Can't run two scrapers simultaneously. Sequential execution only.
- **Zombie tsx processes from subagents**: After heavy subagent usage (10+ spawns), 40+ defunct `npm exec tsx` processes fill process table. Causes EAGAIN on fork, Node thread assertion failures. Sandbox restart required to clear. SOLVED: scrapers moved to Railway services (no shared process space).
- **Leafly Cloudflare protection (Feb 13)**: HTTP API approach (`consumer-api.leafly.com`) now returns 429 with Cloudflare challenge page. SOLVED: Leafly Railway service uses embedded CamoFox + `page.request.fetch()` to carry browser cookies to API calls.
- **Railway cron behavior**: If previous run still active, Railway SKIPS the next cron trigger (does NOT queue). Hard timeout on every scraper is mandatory.
- **Playwright version pinning**: Dockerfile base image version MUST match package.json playwright version or CamoFox→Firefox fallback breaks.
- **page.evaluate(fetch()) vs page.request.fetch()**: page.evaluate does NOT carry Cloudflare cookies cross-subdomain. Always use page.request.fetch() for API calls that need browser cookie jar.
- **PostgreSQL advisory locks for run isolation**: `pg_try_advisory_lock(hashtext(platform || current_date))` — session-scoped, auto-releases on crash, prevents duplicate runs. Better than row-level locks for Railway cron services.
- **Signal tool at 60% production readiness**: Architecture solid but missing GLASS API integration (routes mismatched), client context files, API keys (OpenAI expired, GITHUB_TOKEN, GLASS_API_KEY not set), zero unit tests. Audit doc at `projects/signal/SIGNAL.md`.
- **Weedmaps scraper**: `scripts/scrape-weedmaps.ts`. Uses `WEEDMAPS_CAMOFOX_URL` env var, defaults to `https://roviq-browser-production.up.railway.app`. Railway works fine for Weedmaps (tested Feb 13 — age gate dismissal needed, but products load). Runs in parallel with Dutchie (Dutchie=local CamoFox, Weedmaps=Railway).
- **MA cannabis market size**: 650+ licensed retailers. Dutchie ~235+ (40%), Weedmaps ~300-400, iHeartJane ~100-150.
- **Daily scraping cron**: Dutchie 3AM ET (CamoFox), Weedmaps 10PM ET, data quality check 6AM ET.

## GLASS Product & Ecosystem

- **Antigravity account dead**: All models removed from config (Feb 12).
- **Kimi K2.5 for UX audits**: Good at comprehensive design specs. Use OpenRouter route (`openrouter/moonshotai/kimi-k2.5`).
- **GLASS UX direction (revised by Randy)**: Black & white luxury palette. Remove "connect your menu". Add Cue. Match Roviq design language.
- **Cue positioning**: Full AI commerce platform (demand forecasting, inventory, brand incentives), NOT just a virtual budtender. 4 ecosystem cards: GLASS → Virtual Budtender → Cue → Delivery.
- **Delivered → Delivery**: No deal closed with Delivered Inc yet. LP says "Delivery" until partnership signed.

## Railway & Deploy

- **Railway deploy gotcha**: `railway up` builds succeed but don't always replace the running container. Old deploy stays active if healthcheck passes. Check hostname in runtime logs (not build logs).
- **Railway Docker cache is EXTREMELY aggressive**: Dockerfile changes, CACHEBUST ARGs, env var changes don't bust cache. Fix: Randy clears build cache from dashboard.
- **`railway up --service X`**: Works for upload but always verify correct service is linked. `railway env var changes trigger redeploy.
- **glass-web deploy**: `railway up --service glass-web` from `/data/workspace/projects/glass/src/`. Config path: `railway-web.toml` or `apps/web/railway.toml`.

## Operational Rules

- **Don't block main thread**: Never use inline `sleep` loops to poll. Background everything. Randy called this out.
- **COO operating rule**: Never execute tasks directly. Always spawn subagents. Stay available.
- **Subagent screenshots unreliable**: Don't replace working assets without Randy seeing replacements first.
- **networkidle hangs on SPAs**: Weedmaps keeps persistent websocket connections. Use `domcontentloaded + waitForTimeout(3000)`.

## Design & Fonts

- **Randy's font preferences**: Financier Display, Die Grotesk, Geist Pixel (premium editorial). Falls back to Playfair Display, Geist, Geist Mono (free CDN). Also likes: NORD, Cooper Light, Reckless Standard, Martina Plantijn, Signifier, Innovator Grotesk, TWK Lausanne, Saans.

## Products & Revenue

- **SIGNAL**: SEO automation tool at `projects/signal/`. Revenue: $1,500-2K/mo pilot → $10K+ MRR SaaS.
- **Newsletter**: "The Operator's Margin Report". Pipeline at `projects/internal/newsletter/`. Beehiiv distribution (needs form ID from Randy).
- **CCC ↔ GLASS cross-reference**: CCC official avg $8.19/g vs GLASS scraped $11.13/g = 36% markup. Unique data.
- **CCC data bridge**: 6 tables (31K avg prices, 234 applications, 71 weeks of sales). CCC reports per gram, GLASS per unit.
- **GLASS flywheel UI shipped**: /budtender, /cue, /delivery pages. FlywheelCTA on every dashboard page.
- **Revenue path**: 2 SEO clients + 15 GLASS subs + newsletter sponsors + toll processing. 6 Randy blockers outstanding.
- **Lead database**: 180+ MA operators, 52 named contacts. Sweet spot = 120+ independents with no analytics.
- **Virtual Budtender spec**: LLM intent → algorithmic scoring → response. $0.001/query. Free→$99→$299.
- **Cue MVP**: Dynamic Pricing alerts on existing GLASS data. $199/mo.
- **Revenue Y1**: Conservative $32K → Moderate $100K → Aggressive $225K ARR. 94% margins.
- **AC toll processing emails**: V2 preferred, CAN-SPAM compliance needed.

## Dev Tools

- **Codex CLI naming collision**: `codex-cli@0.1.3` is a blog generator, NOT OpenAI's Codex. Use `@openai/codex` or OpenClaw OAuth subagents.
- **roviq-browser**: Accessibility snapshot + DOM fallback for Railway-hosted scraping. Anti-detection config.

## GLASS Infrastructure (Feb 12)

- **GLASS P0 fixes**: Auth redirect loop, backend auto-provisioning, schema mismatch — all fixed. Codex 5.3 reviewed and hardened.
- **Clerk auth**: Manual JWT verification via `jose`/`crypto` (not `@clerk/fastify` `getAuth()` — broken cross-origin). Clerk instance: `humane-dinosaur-0.clerk.accounts.dev`.
- **GLASS seed data**: 10 MA operators, 35 products, 119 prices. Randy's operator ID: `4b3b6eec-65ec-4e1d-91d7-0da15c1a6233`.
- **GLASS auth**: Data endpoints require Clerk JWT. Public: operators/search, ccc/*, waitlist, newsletter. Admin: `ADMIN_API_KEY`. Admin emails: `torresr14@gmail.com`, `randy@roviq.ai` → `owner`.
- **GLASS domain**: `glassintel.xyz`. GA4: `G-HJ72X18ZDN`.
- **Flywheel/waitlist**: Signups per product with UTM tracking. Admin stats at `/api/v1/admin/waitlist/stats`.
- **Data quality**: 60/100 baseline. `/api/v1/admin/data-quality` endpoint.

## GLASS Data & Intelligence

- **3-model review consensus**: CCC cross-reference unit mismatch FIXED (flower ÷3.5). 490/492 geocoded. CCC weekly sales + demographics imported.
- **Kimi ecosystem plan**: 5 plays, $279 blended per-operator/month, 300 operators = $83.7K MRR.
- **CCC Open Data Catalog**: `masscannabiscontrol.com/open-data/data-catalog/`. Key CSVs: daily sales (67K), gender, race, weekly totals (headers-only).
- **7 CCC datasets**: Lab testing (298K rows), facility sales (67K), commence-ops (773 operators WITH emails+phones), monthly price/oz (72 rows), adult market counties (1,754). All at `projects/glass/src/data/ccc-raw/`.
- **MA flower price collapsed 73%**: $14.68/g (Jan 2020) → $4.01/g (Nov 2025). Headline-worthy.

## Ecosystem Products

- **Virtual Budtender**: React widget live at CH. Guided Q&A → GPT-4 recs from Dutchie CSV. Multi-tenant via `tenantId`. Repo: `randytorres/virtual-budtender`. Stack: React+Vite, Node+Express, Firebase, OpenAI.
- **Cue expansion**: CH driver incentive program via Tremendous gift card API. $512/mo, 4.7x ROI.
- **THC Accuracy Score**: Cross-reference lab-tested THC% (CCC 298K rows) vs menu claims. Catches label fraud. Unique moat.
- **Commence-ops.csv**: 773 licensed operators with emails, phones, license types, DBE status. State-built lead list.
- **Full data flywheel**: Supply (GLASS+CCC) → Demand (Budtender+Delivered) → Performance (Cue) → State Truth (CCC).
- **Additional data sources**: Google Reviews (Places API), Census demographics, CCC enforcement, Otreeba strains, Boston Cannabis Registry.
- **Hub-and-spoke architecture**: GLASS = data gravity well. Plan at `projects/ECOSYSTEM-INTEGRATION-PLAN.md` (72KB).
- **Codex 5.3 CLI not in sandbox**: Use API-accessible models/subagents instead.
- **Site messaging for "Maria"**: Non-technical dispensary owner persona. Plain English, outcome-first. Hero: "Know exactly what the store down the street charges."
- **Anti-patterns confirmed banned**: "Join 500+ operators" (fake social proof), inconsistent stats, jargon like "multi-tenant", "For Developers" sections Maria doesn't need.
- **Hub-and-spoke architecture locked**: GLASS as data gravity well. Products as spokes with domain-specific DBs, sharing product/pricing via GLASS API.
- **5 integration plans complete**: `MASTER-INTEGRATION-PLAN.md` (90KB buildable blueprint), `GLASS-MESSAGING-REVIEW.md` (35KB copy rewrites), `ECOSYSTEM-INTEGRATION-PLAN.md` (71KB), `CODEX-DATA-INTEGRATION-PLAN.md` (99KB), `OPUS-DATA-INTEGRATION-PLAN.md` (97KB).
- **Master plan synthesis decisions**: Pivoted lab test design, merged licenses table, table (not MV) for operator scores, split Google reviews design.
- **CH driver program spec'd**: $512/mo, 4.7x ROI. Cue expansion to drivers validated.

- **Fastify duplicate route = silent deploy kill**: If two route files register the same path, Fastify throws `FST_ERR_DUPLICATED_ROUTE` on startup. Railway blue-green keeps old container running, so you see "health ok" but new routes are 404. Always check runtime logs, not just build logs.
- **ESM + `require()` = crash**: With `module: "NodeNext"` in tsconfig, `require()` is not available. Use `await import()` for dynamic imports. Top-level `await` works in ESM but can cause issues in some build pipelines.
- **Stripe restricted keys**: `rk_live_` keys have limited permissions. Can't create products/prices directly but CAN create payment links with inline `price_data` (auto-creates the price). Workaround for limited API key scopes.
- **Railway env var changes trigger redeploy**: Setting vars via `railway variables --set` automatically triggers a new deploy using the latest uploaded source.
- **Codex subagent JSON escaping bug**: Large multi-line TypeScript file writes via `edit` tool crash with "Unterminated string in JSON" error. Workaround: use `write` for new files, break schema changes into smaller chunks, or use shell commands for complex edits.
- **Gemini 2.5 Flash = new cheap workhorse**: $0.15/$0.60 per M tokens, 1M context, reasoning. Built a 542-line React component in 52s for $0.05. 33x cheaper than Opus on input. Use for: reviews, frontend builds, bulk tasks.
- **Gemini agents inject stray unicode**: Gemini 2.5 Flash/Pro can inject random unicode characters (e.g., Arabic `رو`) into code edits. Always verify output of Gemini-spawned file edits.
- **Gemini agents assume APIs exist**: Unlike Codex/Opus which check first, Gemini agents assume helper functions exist without verifying. Add explicit "verify this function exists or create it" to task descriptions.
- **OpenRouter credits deplete silently**: Agents fail with 402 on first API call. No warning. GLM-5 and Kimi K2.5 (OpenRouter route) both affected. NVIDIA free tier also flaky — DeepSeek R1 returns empty responses. Always have fallback model (Google Gemini, Anthropic) ready.
- **Google AI provider configured**: `google-generative-ai` API type, models at `google/gemini-2.5-pro` and `google/gemini-2.5-flash`. API key from Randy's Google AI Studio.
- **glassintel.xyz**: GLASS production domain (used in outreach emails). Needs verification with Randy that this is correct and deployed.
- **Public report card endpoint**: `GET /api/v1/public/report-card/:slug` — slug-based lookup, 10 req/min rate limit, redacted data (market_avg zeroed, competitor names removed). Frontend at `/report/:slug`.
- **Outreach batch 1**: 25 personalized emails at `projects/glass/outreach/emails-batch-1.md`. 22 unique recipients. Real per-category pricing data. Reviewed 8/10 + 9/10. Minor revisions needed (#25 weak data, #23 tone, #11 duplicate, URL verification).
- **Stripe payment link LIVE**: `https://buy.stripe.com/5kQ4gA8YR8pYc8H0jmcfK0b` ($199/mo, product: GLASS Intelligence Pro, price: `price_1T0CC0KK80En8Nbqo2ZiPosE`). Webhook at `we_1T0CAQKK80En8NbqnF5J3Xg4`.
- **ROVIQ_SERVICE_API_KEYS**: `20b92d41-c871-4ee3-a5d0-e58083613550` (VB → GLASS service key, set on Railway).
- **Randy wants operator-focused UI, not trader dashboard**: Product intelligence per-SKU, local competitor pricing, actionable alerts in plain English, table-first dense UI. "Operators don't give af about fancy dashboards."
- **CCC monthly prices = flower only**: That's all CCC publishes. Cross-reference endpoint needed LEFT JOIN to show all GLASS categories.

## GLASS Consumer-First Strategy (Feb 13 Pivot)

- **Advisor feedback doc**: `projects/glass/ADVISOR-FEEDBACK.md` — 4 landmines + 3 hell yes elements
- **Master strategy v2**: `projects/glass/GLASS-MASTER-STRATEGY.md` — 47KB definitive war plan, supersedes all prior strategy docs
- **GPID accuracy plan**: `projects/glass/GPID-ACCURACY-PLAN.md` — 1,068 lines, path to 95%
- **Key thesis**: "He who owns the consumer demand, owns the industry." Yelp/Zillow/GasBuddy playbook.
- **Step 0**: Top 500 hand-verified SKUs. "We track the 500 most popular cannabis products in MA." Accuracy over breadth.
- **4 Landmines**: (1) GPID can't be byproduct — it IS the product, (2) Pre-tax vs post-tax normalization is Day 1, (3) "Verified X hours ago" + auto-hide >24hr, (4) SEO sandbox = social-first for 3-6 months
- **THC Accuracy Score = nuclear moat**: CCC 298K lab tests vs menu claims. "30% of MA dispensaries inflate THC" → Boston Globe exclusive.
- **Dispensary tag mechanic**: Tag stores in social posts → they claim their page within 60 seconds of seeing overcharging
- **Dutchie WAF counter-attack**: Consumer traffic forces dispensaries to share API keys when POS platforms block scrapers
- **Hoodie Analytics = #1 threat**: $9.4M raised, 36 employees, High Times partnership. 6-12 month window. Every decision must answer "how does this beat Hoodie?"

## GLASS DB State (Feb 13)

- **All migrations applied**: 001-009 + matching engine to `glass` schema (27 tables)
- **Extensions**: `unaccent`, `pg_trgm`, `fuzzystrmatch` in `public` schema
- **search_path fix**: `db.ts` sets `glass, public` on every connection
- **Data state**: 10 seed operators, 0 products, 0 prices in `glass` schema. Today's scrape data lost (went to wrong schema). Need re-run.
- **Migration 004 (merge duplicates) failed**: `operator_scores` unique constraint conflict. Non-critical.
- **`makeSKU()` still has platform prefix** — needs fix to `GPID-{hash}` for cross-platform matching
- **Brand dictionary**: table exists but empty, needs seeding

## CH SEO Campaign (Feb 13)

- **CH repo**: `randytorres/ch-web` (private), cloned at `/tmp/ch-web`. React + Vite + Tailwind, Netlify deploy.
- **NEVER push to master/main** — Randy does that manually. Feature branches only. Netlify auto-generates preview links.
- **BOUTIQ dominates**: 8+ Logan-adjacent pages, 750+ Google reviews (4.9 stars). CH barely on page 1.
- **CH nuclear weapon**: Flight Kit (no competitor has traveler-specific products)
- **"5 min by Uber" beats "one stop on Blue Line"** — travelers with luggage prefer rideshare
- **New pages being built** (branch `feat/seo-airport-content`): TravelersGuide, AirportFAQ, EastBoston neighborhood + 2 blog posts
- **Signal tool**: CLI at `/data/workspace/projects/signal/`. Works but OPENAI_API_KEY expired, GLASS API routes mismatched. NVIDIA API as fallback. Produces filler without real data.

_Last updated: 2026-02-13 (3:40 PM UTC — DB migrations, advisor feedback, consumer strategy, CH SEO sprint)_
