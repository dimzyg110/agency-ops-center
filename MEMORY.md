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

_Last updated: 2026-02-12 (2:50 AM UTC session)_
