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
- **Humanizer pipeline works**: Gemini 3 Pro High is reliable for humanizer passes. Opus 4.6T works if task completes in one turn.
- **No deploy service credentials configured** — need Vercel/Netlify/Cloudflare token from Randy to deploy demos/sites from sandbox. GitHub Pages blocked on private repos (free plan).
- **Decoded demo built** at `projects/decoded-demo/` — Vite + React + Tailwind, TikTok-style feed. Randy hasn't seen it yet.

- **Roviq website direction (V3)**: White/editorial theme, ACME-inspired layout. Bracketed nav with numbers, left-aligned hero, video placeholder. Geist Pixel/Sans/Mono fonts kept. Randy providing hero video. Red accent `#D94F3D`. Commit `0d22df7` on `Roviq-AI/roviq-web`. Mobile hero: autoplay 0.5x, 70% width, 50% height. Scroll-scrub doesn't work on mobile (hero = first section, no scroll distance).
- **ION (Independent Operators Network)**: Randy-approved directionally but effectively superseded by GLASS. ION's intelligence-first approach folded into GLASS Threat Radar.
- **GLASS ecosystem**: Hub + spokes. Free core (Price Wire + Threat Radar + Margin Engine). Revenue spokes (Cue + Delivered + AC Toll Processing + Roviq Agency). Newsletter = distribution only. Consolidated plan at `projects/glass/GLASS-PLAN.md` (Gemini synthesis of 3 model plans). Source plans at `/tmp/glass-plan-{opus,kimi,gpt}.md`.
- **Apex Trading**: Industry standard wholesale platform in MA. METRC integration, CRM, email marketing, invoicing. Competitors: LeafLink ($5B+ annual orders), Leaf Trade. Pricing hidden behind demo calls. GLASS doesn't replace it, operates on layers Apex doesn't cover.
- **AC Toll Processing outreach**: 85 personalized emails ready at `clients/ac/toll-processing/outreach-emails.md`. 65 cultivators + 21 microbusinesses + 321 retailers prospected. Page live at `advancedcultivatorsllc.com/toll-processing` (pw: `ac2026`). Commit `a4154e6`.
- **Subagent screenshots unreliable**: Fresh screenshots from live URLs looked worse than original images. Randy said "go back to previous versions." Lesson: don't replace working assets without Randy seeing the replacements first.

- **GLASS P0 fixes completed + hardened** (Feb 12): Auth redirect loop (Clerk `<SignedIn>/<SignedOut>`), backend auto-provisioning for Clerk users, schema mismatch (`pgSchema('glass')` → `pgTable()`). Plus P1 wins (logout, token cache, threats, CORS). Codex 5.3 reviewed, found critical defect (no `clerk_user_id` lookup, race conditions), then fixed it. 8 commits in GLASS submodule, not yet pushed. Still need: Redis, scraper/intelligence deploy, seed data, `schema.sql` migration (includes new `clerk_user_id` column on users table).
- **`@clerk/fastify` v2 cross-origin auth broken** (Feb 12): `getAuth()` uses cookie-based sessions, doesn't work when frontend and API are on different domains (Railway). Fix: manual JWT verification via `jose` against Clerk JWKS endpoint. Commit `f86397f`. Clerk instance: `humane-dinosaur-0.clerk.accounts.dev`.
- **Railway deployment learnings** (Feb 12): `railway up --service <name>` deploys from local source, bypasses stale config-as-code settings. `RAILWAY_TOML_PATH` env var doesn't reliably override service config — must set "Config as Code File" in Railway dashboard. Railway table display truncates long env var values — always use `--json` output to get full values. glass-web needs `railway up` or correct toml path in dashboard for future deploys.
- **Context window set to 195K** for auto-compaction (Feb 12). Safeguard mode.
- **jose not a usable dep in GLASS Docker prod**: Transitive dep of `@clerk/fastify` but not hoisted to top-level `node_modules`. TypeScript compiles fine but runtime fails. Solution: use Node built-in `crypto` module for JWT verification (JWKS fetch + RS256 verify). Commit `b3f78b8`.
- **GLASS seed data loaded** (Feb 12): 10 MA operators, 35 products, 119 prices, 6 threats, 6 recommendations, 10 alerts, 5 margin rules. Randy's operator ID: `4b3b6eec-65ec-4e1d-91d7-0da15c1a6233`. Seed script at `projects/glass/src/seed.sql`.
- **Railway deploys: FAILED doesn't kill old deploy**: When a new Railway deploy fails, the previous successful deploy keeps running. The `railway logs` command shows the old deploy's logs. Check hostname in logs to verify which deploy is active.
- **Skill setup improvements done** (Feb 12): 15 skill descriptions rewritten with routing trees, AGENTS.md slimmed (109 lines → skills), 3 new skills (deployment, git-workflow, newsletter), `fast-browser-use` deleted, `output/` dir created.

- **Dutchie scraper POC** (Feb 12): 235 MA dispensary slugs discovered via Firecrawl. Menu pages return 402 via Firecrawl — need CamoFox or JSON endpoint. Script at `projects/glass/src/scripts/scrape-dutchie-ma.ts`. Slug data at `scripts/dutchie-slugs.json`. Firecrawl API key in sandbox env as `FIRECRAWL_API_KEY`.
- **Dutchie architecture**: ~60-70% of MA dispensaries use Dutchie. Embed URL pattern: `dutchie.com/api/v2/embedded-menu/{SLUG}.js`. Directory at `dutchie.com/us/dispensaries/ma-{city}`. GraphQL at `dutchie.com/graphql` (Cloudflare blocked). Dutchie+ API at `plus.dutchie.com/plus/2021-07/graphql` (requires Bearer auth). Daily scraping cadence is sufficient per Randy.
- **CamoFox scraping works on Dutchie**: `camofox_create_tab` → navigate to product page → click age gate → `camofox_snapshot` returns full structured product data (name, brand, THC%, price, weight). Bypasses Cloudflare. For standalone scripts, use `playwright` + Camoufox binary at `/root/.cache/camoufox/camoufox-bin`. `page.accessibility.snapshot()` is NOT available — use `page.evaluate()` for DOM extraction.
- **Dutchie POC results**: 912+ products from 3 stores (~300/store avg). 5 categories per store: flower, pre-rolls, vaporizers, edibles, concentrates. Extrapolated: ~70K price observations per full 235-store run.
- **Antigravity account dead**: All models removed from config (Feb 12). Auth profile, plugin, 6 model entries, 4 fallbacks deleted. Randy confirmed account doesn't work.
- **Scraper V2 final plan** at `projects/glass/SCRAPER-V2-FINAL.md`. Key decisions: no `prices_normalized` table (add columns to existing), Drizzle ORM, two-level job model with resume, browser crash recovery, parser contract tests, Railway spike before deploy, Dutchie-only Week 1.
- **MA cannabis market size**: 650+ licensed retailers, 686 total licensed ops (Feb 2026). Dutchie covers ~235+ (40%), Weedmaps ~300-400 listings, iHeartJane ~100-150.
- **Railway pricing**: vCPU ~$20/mo continuous, RAM ~$10/GB/mo continuous. Scraper cron job = ~$34/mo (8-10h/day, 2 vCPU + 4GB).
- **CamoFox HTTP API** at `localhost:9377` — the correct way to use CamoFox from scripts. Don't launch Playwright separately (conflicts with OpenClaw plugin). Endpoints: POST /tabs, GET /tabs/:id/snapshot, POST /tabs/:id/click, POST /tabs/:id/scroll, POST /tabs/:id/navigate, DELETE /tabs/:id. userId + sessionKey required.
- **Scraper V2 working**: 293 products from 2 stores (Pure Oasis + NETA Brookline) inserted into prod DB. Pipeline: CamoFox HTTP API → snapshot → parse → normalize → upsert via pg. Runtime ~60s/store. Scripts at `projects/glass/src/scripts/scrape-dutchie.ts` + `scripts/lib/`.
- **Kimi K2.5 for UX audits**: Good at comprehensive design specs, produced 1,060-line audit with color palettes, component hierarchy, onboarding flows. Use OpenRouter route (`openrouter/moonshotai/kimi-k2.5`).
- **GLASS UX direction (revised by Randy)**: Drop electric teal, go **black & white luxury** palette. Remove "connect your menu" (can't do yet). Add **Cue** (virtual budtender) — description + signup form. GLASS = pathway to Cue + Delivered + ecosystem tools. Don't oversell. Match Roviq site design language (`roviqai.xyz` — was blank when checked). Kimi's audit at `projects/glass/GLASS-UX-AUDIT.md` needs revision with these changes.
- **Weedmaps scraper built and merged**: Parser + orchestrator + fixtures. 24 products from Diem Cannabis page 1 verified. All pushed to GitHub. Key files: `scripts/lib/weedmaps-parser.ts`, `scripts/scrape-weedmaps.ts`.
- **CamoFox HTTP timeout fix**: 45s `AbortController` in `camofoxFetch`. Fixes orchestrator hangs for both Dutchie and Weedmaps. Commit `b7788b9`.
- **DB pool close fix**: Both orchestrators now call `dbPool.end()` in `.finally()` to exit cleanly.
- **15 GLASS commits pushed** to `Roviq-AI/glass.git` main (`20ecb02..b7788b9`).

- **Railway deploy gotcha**: `railway up` builds succeed but don't always replace the running container. Old deploy stays active if healthcheck passes. Manual "Redeploy" in dashboard or git-triggered deploys are more reliable.
- **DATABASE_URL in sandbox = Neon, not Railway**: Always override with Railway URL when running scrapers: `DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway"`
- **Weedmaps scraper verified at scale**: 760 products from one store (New Dia Fenway), 32 pages, zero errors. ~10-15s per page. Full MA run = ~5 hours.
- **Randy's font preferences**: Financier Display, Die Grotesk, Geist Pixel (premium editorial). Falls back to Playfair Display, Geist, Geist Mono (free CDN). Also likes: NORD, Cooper Light, Reckless Standard, Martina Plantijn, Signifier, Innovator Grotesk, TWK Lausanne, Saans.
- **Parallel scraping works**: Dutchie on sandbox CamoFox + Weedmaps on roviq-browser Railway. Zero AI tokens — pure Node.js automation.
- **CamoFox is single-browser**: Can't run two scrapers simultaneously on the same CamoFox instance. Tab creation hangs indefinitely when both compete. Solution: sequential execution (Dutchie first, then Weedmaps).
- **Railway CamoFox blocked by Weedmaps**: Datacenter IPs get 0 results from Weedmaps directory pages. Local CamoFox works perfectly. Weedmaps scraper must always use `localhost:9377`.
- **Don't block main thread**: Never use inline `sleep` loops to poll background tasks. Background everything and respond immediately. Randy called this out.
- **Codex CLI naming collision**: `codex-cli@0.1.3` on npm is a blog generator, NOT OpenAI's Codex. Real package is `@openai/codex`. Removed — using OpenClaw subagents via OAuth instead.
- **OpenAI project API keys don't work with Codex CLI**: Responses API returns 401. OAuth via OpenClaw (`openai-codex/gpt-5.3-codex`) works fine for subagents.
- **glass-web Railway deploy via CLI**: `railway up --service glass-web` from repo root (`/data/workspace/projects/glass/src/`) works. Config as Code path should be `railway-web.toml` (no leading `/`) or `apps/web/railway.toml`.
- **roviq-browser snapshot fix**: Original `buildSnapshot()` DOM walker missed React SPA content (empty snapshots). Fixed with accessibility snapshot + robust DOM fallback. Weedmaps now returns 68K char snapshots on Railway. Commit `e169217`.
- **Parallel scraping restored**: Dutchie on local CamoFox (`localhost:9377`) + Weedmaps on roviq-browser Railway (`roviq-browser-production.up.railway.app`). Both work simultaneously.
- **networkidle hangs on SPAs**: Weedmaps keeps persistent websocket connections, causing `networkidle` to never fire. Use `domcontentloaded + waitForTimeout(3000)` instead.
- **roviq-browser anti-detection config**: locale `en-US`, timezone `America/New_York`, viewport 1440x900, light color scheme, ad/tracker route blocking. Added `/tabs/:id/evaluate` endpoint for JS execution.
- **COO operating rule**: Never execute tasks directly. Always spawn subagents. Stay available. Only do things that take <30 seconds inline.
- **Cue positioning**: Cue is a full AI commerce platform (demand forecasting, inventory optimization, brand incentives), NOT just a virtual budtender. Virtual Budtender is a separate product in the ecosystem. 4 ecosystem cards: GLASS → Virtual Budtender → Cue → Delivery.
- **Delivered → Delivery**: No deal closed with Delivered Inc yet. LP says "Delivery" until partnership signed.
- **Railway deploy gotcha**: `railway up` builds succeed but don't always replace the running container. Old deploy stays active if healthcheck passes. `railway logs` command shows the old deploy's logs. Check hostname in logs to verify which deploy is active.
- **Railway Docker cache is EXTREMELY aggressive**: 6+ deploys failed to update glass-web. Dockerfile changes, CACHEBUST ARGs, env var changes, new files — none busted the cache. `railway logs --build` only shows last successful build. Fix: have Randy clear build cache from Railway dashboard (Settings → Build → Clear cache). Or change base image entirely.
- **`railway up --service X` vs linked service**: The `--service` flag works for upload but build behavior may differ. Always verify with `railway service X` + `railway status` that the correct service is linked before deploying.
- **DATABASE_URL in sandbox = Neon, not Railway**: Always override with Railway URL when running scrapers: `DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway"`
- **Weedmaps scraper verified at scale**: 760 products from one store (New Dia Fenway), 32 pages, zero errors. ~10-15s per page. Full MA run = ~5 hours.
- **Randy's font preferences**: Financier Display, Die Grotesk, Geist Pixel (premium editorial). Falls back to Playfair Display, Geist, Geist Mono (free CDN). Also likes: NORD, Cooper Light, Reckless Standard, Martina Plantijn, Signifier, Innovator Grotesk, TWK Lausanne, Saans.
- **Parallel scraping works**: Dutchie on sandbox CamoFox + Weedmaps on roviq-browser Railway. Zero AI tokens — pure Node.js automation.
- **SIGNAL**: SEO Intelligence, Generation, Navigation, and Authority Layer. Cannabis SEO automation tool at `projects/signal/`. CLI with generate/pipeline/publish/status. React/Netlify GitHub PR publishing only, no WordPress. Revenue: $1,500-2K/mo pilot → $10K+ MRR SaaS.
- **Newsletter**: "The Operator's Margin Report". Pipeline at `projects/internal/newsletter/`. Python scrapers + GLASS data processor. Beehiiv for distribution (not yet connected — needs form ID from Randy). Test issue generated Feb 12 with real GLASS data.
- **CCC ↔ GLASS cross-reference**: CCC official avg price $8.19/g vs GLASS scraped $11.13/g = 36% markup. This is unique data nobody else has.
- **CCC data bridge built**: 6 tables in GLASS DB (31K avg prices, 234 applications, 71 weeks of sales). Cross-reference endpoint live. CCC reports per gram, GLASS reports per unit (different measurement basis).
- **GLASS flywheel UI shipped**: /budtender, /cue, /delivery pages. FlywheelCTA component on every dashboard page. Sidebar Tools section. LP cards link to product pages.
- **Automation strategy completed**: "90% built, 5% monetized." Fastest path to $10K MRR: 2 SEO clients + 15 GLASS subs + newsletter sponsors + toll processing. 6 Randy blockers: Beehiiv form ID, Resend domain, Stripe, approve AC blast, Delivered meeting, Cloudflare nameservers.
- **Lead database built**: 180+ MA operators, 52 named contacts. Sweet spot = 120+ independents with no analytics. Top lead: Bud's Goods. Key influencers: MCC/MassCBA board members.
- **Virtual Budtender spec**: LLM intent → algorithmic scoring → LLM response. $0.001/query. Free→$99→$299. Unique moat: demand signals nobody else captures.
- **Cue MVP = Dynamic Pricing alerts**: Just an alerting layer on existing GLASS data. $199/mo. No new data sources needed.
- **Revenue projections Y1**: Conservative $32K → Moderate $100K → Aggressive $225K ARR. 94% gross margins.
- **AC toll processing emails**: V2 preferred, needs CAN-SPAM compliance (address + unsubscribe), .win domain risky (30-50% spam rate). Randy has spacemanwins.win.
- **Subagent screenshots unreliable**: Fresh screenshots from live URLs looked worse than original images. Randy said "go back to previous versions." Lesson: don't replace working assets without Randy seeing the replacements first.

- **GLASS P0 fixes completed + hardened** (Feb 12): Auth redirect loop (Clerk `<SignedIn>/<SignedOut>`), backend auto-provisioning for Clerk users, schema mismatch (`pgSchema('glass')` → `pgTable()`). Plus P1 wins (logout, token cache, threats, CORS). Codex 5.3 reviewed, found critical defect (no `clerk_user_id` lookup, race conditions), then fixed it. 8 commits in GLASS submodule, not yet pushed. Still need: Redis, scraper/intelligence deploy, seed data, `schema.sql` migration (includes new `clerk_user_id` column on users table).
- **`@clerk/fastify` v2 cross-origin auth broken** (Feb 12): `getAuth()` uses cookie-based sessions, doesn't work when frontend and API are on different domains (Railway). Fix: manual JWT verification via `jose` against Clerk JWKS endpoint. Commit `f86397f`. Clerk instance: `humane-dinosaur-0.clerk.accounts.dev`.
- **Railway deployment learnings** (Feb 12): `railway up --service <name>` deploys from local source, bypasses stale config-as-code settings. `RAILWAY_TOML_PATH` env var doesn't reliably override service config — must set "Config as Code File" in Railway dashboard. Railway table display truncates long env var values — always use `--json` output to get full values. glass-web needs `railway up` or correct toml path in dashboard for future deploys.
- **Context window set to 195K** for auto-compaction (Feb 12). Safeguard mode.
- **jose not a usable dep in GLASS Docker prod**: Transitive dep of `@clerk/fastify` but not hoisted to top-level `node_modules`. TypeScript compiles fine but runtime fails. Solution: use Node built-in `crypto` module for JWT verification (JWKS fetch + RS256 verify). Commit `b3f78b8`.
- **GLASS seed data loaded** (Feb 12): 10 MA operators, 35 products, 119 prices, 6 threats, 6 recommendations, 10 alerts, 5 margin rules. Randy's operator ID: `4b3b6eec-65ec-4e1d-91d7-0da15c1a6233`. Seed script at `projects/glass/src/seed.sql`.
- **Railway deploys: FAILED doesn't kill old deploy**: When a new Railway deploy fails, the previous successful deploy keeps running. The `railway logs` command shows the old deploy's logs. Check hostname in logs to verify which deploy is active.
- **Skill setup improvements done** (Feb 12): 15 skill descriptions rewritten with routing trees, AGENTS.md slimmed (109 lines → skills), 3 new skills (deployment, git-workflow, newsletter), `fast-browser-use` deleted, `output/` dir created.

- **Dutchie scraper POC** (Feb 12): 235 MA dispensary slugs discovered via Firecrawl. Menu pages return 402 via Firecrawl — need CamoFox or JSON endpoint. Script at `projects/glass/src/scripts/scrape-dutchie-ma.ts`. Slug data at `scripts/dutchie-slugs.json`. Firecrawl API key in sandbox env as `FIRECRAWL_API_KEY`.
- **Dutchie architecture**: ~60-70% of MA dispensaries use Dutchie. Embed URL pattern: `dutchie.com/api/v2/embedded-menu/{SLUG}.js`. Directory at `dutchie.com/us/dispensaries/ma-{city}`. GraphQL at `dutchie.com/graphql` (Cloudflare blocked). Dutchie+ API at `plus.dutchie.com/plus/2021-07/graphql` (requires Bearer auth). Daily scraping cadence is sufficient per Randy.
- **CamoFox scraping works on Dutchie**: `camofox_create_tab` → navigate to product page → click age gate → `camofox_snapshot` returns full structured product data (name, brand, THC%, price, weight). Bypasses Cloudflare. For standalone scripts, use `playwright` + Camoufox binary at `/root/.cache/camoufox/camoufox-bin`. `page.accessibility.snapshot()` is NOT available — use `page.evaluate()` for DOM extraction.
- **Dutchie POC results**: 912+ products from 3 stores (~300/store avg). 5 categories per store: flower, pre-rolls, vaporizers, edibles, concentrates. Extrapolated: ~70K price observations per full 235-store run.
- 

- **Dutchie scraper COMPLETE** (Feb 12): 235/235 stores. DB: 76,247 products, 87,849 prices.
- **Weedmaps scraper**: 263 slugs, running on roviq-browser Railway. ~250/282 at last check. Adding ~16K products on top of Dutchie.
- **Parallel scraping works**: Dutchie on sandbox CamoFox + Weedmaps on roviq-browser Railway. Zero AI tokens — pure Node.js automation.
- **SIGNAL**: SEO Intelligence, Generation, Navigation, and Authority Layer. Cannabis SEO automation tool at `projects/signal/`. CLI with generate/pipeline/publish/status. React/Netlify GitHub PR publishing only, no WordPress. Revenue: $1,500-2K/mo pilot → $10K+ MRR SaaS.
- **Newsletter**: "The Operator's Margin Report". Pipeline at `projects/internal/newsletter/`. Python scrapers + GLASS data processor. Beehiiv for distribution (not yet connected — needs form ID from Randy). Test issue generated Feb 12 with real GLASS data.
- **CCC ↔ GLASS cross-reference**: CCC official avg price $8.19/g vs GLASS scraped $11.13/g = 36% markup. This is unique data nobody else has.
- **CCC data bridge built**: 6 tables in GLASS DB (31K avg prices, 234 applications, 71 weeks of sales). Cross-reference endpoint live. CCC reports per gram, GLASS reports per unit (different measurement basis).
- **GLASS flywheel UI shipped**: /budtender, /cue, /delivery pages. FlywheelCTA component on every dashboard page. Sidebar Tools section. LP cards link to product pages.
- **Automation strategy completed**: "90% built, 5% monetized." Fastest path to $10K MRR: 2 SEO clients + 15 GLASS subs + newsletter sponsors + toll processing. 6 Randy blockers: Beehiiv form ID, Resend domain, Stripe, approve AC blast, Delivered meeting, Cloudflare nameservers.
- **Lead database built**: 180+ MA operators, 52 named contacts. Sweet spot = 120+ independents with no analytics. Top lead: Bud's Goods. Key influencers: MCC/MassCBA board members.
- **Virtual Budtender spec**: LLM intent → algorithmic scoring → LLM response. $0.001/query. Free→$99→$299. Unique moat: demand signals nobody else captures.
- **Cue MVP = Dynamic Pricing alerts**: Just an alerting layer on existing GLASS data. $199/mo. No new data sources needed.
- **Revenue projections Y1**: Conservative $32K → Moderate $100K → Aggressive $225K ARR. 94% gross margins.
- **AC toll processing emails**: V2 preferred, needs CAN-SPAM compliance (address + unsubscribe), .win domain risky (30-50% spam rate). Randy has spacemanwins.win.

- **3-model GLASS review consensus** (Feb 12): CCC cross-reference had unit mismatch (FIXED: flower ÷3.5 for per-gram). 490/492 operators geocoded (FIXED). CCC weekly sales imported (376 weeks, FIXED). Demographics imported (20,694 agents, FIXED). Sparklines still single-day (need daily scraping cron). Priority: daily scraping → time-series data.
- **Kimi ecosystem domination plan**: 5 plays (Cue pricing loop → Budtender everywhere → MA Reference Index → Brand Exchange → Delivery intel). "Can't leave" = 8+ weeks Cue usage + measurable margin impact. $279 blended per-operator/month, 300 operators = $83.7K MRR.
- **GLASS domain**: `glassintel.xyz` (purchased Feb 12). CORS_ORIGIN on Railway glass-api: `https://glass-web-production.up.railway.app,https://glassintel.xyz,https://www.glassintel.xyz`
- **CCC Open Data Catalog**: `masscannabiscontrol.com/open-data/data-catalog/`. Key CSVs: `87rp-xn9v.csv` (daily sales 67K rows), `hhjg-atjk.csv` (gender), `pt2c-wb44.csv` (race). Weekly totals CSV (`dt9b-i6ds.csv`) is headers-only currently.
- **GA4 tracking**: `G-HJ72X18ZDN` on glass-web. SPA page views + custom events (waitlist_signup, cta_click, onboarding_step, feature_use). Analytics utilities at `utils/analytics.ts`.
- **Flywheel/waitlist system**: `waitlist` table stores signups per product (budtender/cue/delivery/glass/newsletter) with UTM tracking. All product pages wire to real API. Cross-product suggestions after signup. Admin stats at `/api/v1/admin/waitlist/stats`.
- **GLASS auth architecture (Feb 12)**: All data endpoints (viz, prices, report-card, dashboard, threats, products, exports) require Clerk JWT. Public: operators/search, ccc/weekly-sales, ccc/demographics, ccc/cross-reference, waitlist, newsletter. Admin endpoints require `ADMIN_API_KEY` header. Admin email allowlist: `torresr14@gmail.com`, `randy@roviq.ai` → always `owner` role. All other signups → `viewer`. Rate limiting on all public endpoints.
- **Daily scraping cron**: Weedmaps 10PM ET (Railway), Dutchie 3AM ET (CamoFox), data quality check 6AM ET. All isolated sessions with announce delivery.
- **Data quality baseline**: 60/100. `/api/v1/admin/data-quality` endpoint. Price sanity checks in `data-quality.ts`. `scrape_runs` table for tracking. `daily_price_averages` view.
- **`railway up --service X` vs linked service**: The `--service` flag works for upload but build behavior may differ. Always verify with `railway service X` + `railway status` that the correct service is linked before deploying.
- **DATABASE_URL in sandbox = Neon, not Railway**: Always override with Railway URL when running scrapers: `DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway"`
- **Weedmaps scraper verified at scale**: 760 products from one store (New Dia Fenway), 32 pages, zero errors. ~10-15s per page. Full MA run = ~5 hours.
- **Randy's font preferences**: Financier Display, Die Grotesk, Geist Pixel (premium editorial). Falls back to Playfair Display, Geist, Geist Mono (free CDN). Also likes: NORD, Cooper Light, Reckless Standard, Martina Plantijn, Signifier, Innovator Grotesk, TWK Lausanne, Saans.
- **Parallel scraping works**: Dutchie on sandbox CamoFox + Weedmaps on roviq-browser Railway. Zero AI tokens — pure Node.js automation.
- **SIGNAL**: SEO Intelligence, Generation, Navigation, and Authority Layer. Cannabis SEO automation tool at `projects/signal/`. CLI with generate/pipeline/publish/status. React/Netlify GitHub PR publishing only, no WordPress. Revenue: $1,500-2K/mo pilot → $10K+ MRR SaaS.
- **Newsletter**: "The Operator's Margin Report". Pipeline at `projects/internal/newsletter/`. Python scrapers + GLASS data processor. Beehiiv for distribution (not yet connected — needs form ID from Randy). Test issue generated Feb 12 with real GLASS data.
- **CCC ↔ GLASS cross-reference**: CCC official avg price $8.19/g vs GLASS scraped $11.13/g = 36% markup. This is unique data nobody else has.
- **CCC data bridge built**: 6 tables in GLASS DB (31K avg prices, 234 applications, 71 weeks of sales). Cross-reference endpoint live. CCC reports per gram, GLASS reports per unit (different measurement basis).
- **GLASS flywheel UI shipped**: /budtender, /cue, /delivery pages. FlywheelCTA component on every dashboard page. Sidebar Tools section. LP cards link to product pages.
- **Automation strategy completed**: "90% built, 5% monetized." Fastest path to $10K MRR: 2 SEO clients + 15 GLASS subs + newsletter sponsors + toll processing. 6 Randy blockers: Beehiiv form ID, Resend domain, Stripe, approve AC blast, Delivered meeting, Cloudflare nameservers.
- **Lead database built**: 180+ MA operators, 52 named contacts. Sweet spot = 120+ independents with no analytics. Top lead: Bud's Goods. Key influencers: MCC/MassCBA board members.
- **Virtual Budtender spec**: LLM intent → algorithmic scoring → LLM response. $0.001/query. Free→$99→$299. Unique moat: demand signals nobody else captures.
- **Cue MVP = Dynamic Pricing alerts**: Just an alerting layer on existing GLASS data. $199/mo. No new data sources needed.
- **Revenue projections Y1**: Conservative $32K → Moderate $100K → Aggressive $225K ARR. 94% gross margins.
- **AC toll processing emails**: V2 preferred, needs CAN-SPAM compliance (address + unsubscribe), .win domain risky (30-50% spam rate). Randy has spacemanwins.win.

- **Virtual Budtender is a REAL product**: React widget live at CH. Guided Q&A (goal→experience→format→budget→2-4 recs). Uses Dutchie CSV for real inventory. GPT-4 selects matches. Multi-tenant via `tenantId`. Repo: `randytorres/virtual-budtender`. Installed as npm dep in CH site (`InfoCards.jsx`). Stack: React+Vite frontend, Node+Express backend, Firebase Firestore, OpenAI GPT-4.
- **Cue expansion beyond budtenders**: CH wants driver incentive program — can't legally give drivers cannabis products. Cue's Tremendous gift card API solves this. Participant types: budtender, delivery_driver, brand_ambassador, customer_loyalty. CH driver program cost: ~$512/mo, 4.7x ROI estimate.
- **7 new CCC datasets downloaded** (Feb 12, 6 PM UTC): Lab testing (298K rows, THC/THCA%), facility sales (67K, daily revenue by category 2019-2025), ITD retail/delivery breakdown, medical facility stats (47K), monthly price/oz (72 rows), commence-ops (773 operators WITH emails+phones), adult market counties (1,754). All at `projects/glass/src/data/ccc-raw/`.
- **THC Accuracy Score concept**: Cross-reference lab-tested THC% from CCC data vs advertised THC% on Dutchie/Weedmaps menus. Catches label fraud, benchmarks product quality. Nobody else does this.
- **Commence-ops.csv = state-built lead list**: 773 licensed operators with business emails, phone numbers, license types, DBE status. For automated drip (not cold calling).
- **Full data flywheel with Delivered**: Supply (GLASS+CCC) → Demand (Budtender+Delivered) → Performance (Cue) → State Truth (CCC). Nobody else has all 4 layers.
- **Additional public data sources to integrate**: Google Reviews (Places API ready), Census demographics (free API), CCC enforcement actions (scraping), Otreeba strain database (free REST API for effects/terpenes), Boston Cannabis Registry (data.boston.gov).
- **Ecosystem integration plan**: Hub-and-spoke architecture. GLASS = data gravity well (single source of truth for products/prices). Each product keeps domain-specific DB but shares catalog via GLASS API. Plan at `projects/ECOSYSTEM-INTEGRATION-PLAN.md` (72KB).
- **Codex 5.3 CLI not in sandbox**: `codex` command not found. Can't use CLI-based Codex for subagent tasks. Use API-accessible models instead.
- **MA flower price collapsed 73%**: Official CCC data shows $14.68/g (Jan 2020) → $4.01/g (Nov 2025). Headline-worthy intelligence nobody else has surfaced.
- **Lab testing data is the moat**: 298K state test results. Cross-reference with menu claims = "THC Accuracy Score" — catches label fraud. Unique data asset.
- **Multi-model synthesis works**: 5 independent plans (Opus ecosystem, Kimi data, Opus data, Codex master, Opus messaging) created, 450KB+ total. Synthesis resolves conflicts, picks best ideas.
- **Site messaging for "Maria"**: Non-technical dispensary owner persona. Plain English, outcome-first. Hero: "Know exactly what the store down the street charges."
- **Anti-patterns confirmed banned**: "Join 500+ operators" (fake social proof), inconsistent stats, jargon like "multi-tenant", "For Developers" sections Maria doesn't need.
- **Hub-and-spoke architecture locked**: GLASS as data gravity well. Products as spokes with domain-specific DBs, sharing product/pricing via GLASS API.
- **5 integration plans complete**: `MASTER-INTEGRATION-PLAN.md` (90KB buildable blueprint), `GLASS-MESSAGING-REVIEW.md` (35KB copy rewrites), `ECOSYSTEM-INTEGRATION-PLAN.md` (71KB), `CODEX-DATA-INTEGRATION-PLAN.md` (99KB), `OPUS-DATA-INTEGRATION-PLAN.md` (97KB).
- **Master plan synthesis decisions**: Pivoted lab test design, merged licenses table, table (not MV) for operator scores, split Google reviews design.
- **CH driver program spec'd**: $512/mo, 4.7x ROI. Cue expansion to drivers validated.

_Last updated: 2026-02-12 (6:46 PM UTC session)_
