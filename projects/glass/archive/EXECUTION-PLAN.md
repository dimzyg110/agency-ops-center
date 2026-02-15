# GLASS Execution Plan
**Created:** February 12, 2026 — 11:15 PM UTC  
**Author:** COO, Roviq  
**Status:** ACTIVE — Execute against this document daily  
**Target:** First paying customer by February 26, 2026

---

## Table of Contents
1. [Situation Assessment](#situation-assessment)
2. [Phase 1: Immediate Cleanup (Tonight → Feb 13 EOD)](#phase-1-immediate-cleanup)
3. [Phase 2: First Revenue Sprint (Feb 13–26, 14 days)](#phase-2-first-revenue)
4. [Phase 3: Product-Market Fit (Feb 27 – Apr 13, 30-60 days)](#phase-3-product-market-fit)
5. [Phase 4: Scale (Apr 14 – May 13, 60-90 days)](#phase-4-scale)
6. [Daily Schedule: Days 1–7](#daily-schedule)
7. [Dependency Map](#dependency-map)
8. [Revenue Milestones](#revenue-milestones)
9. [Risk Register](#risk-register)
10. [Decision Points for Randy](#decision-points)
11. [Model Assignment Matrix](#model-assignment-matrix)

---

## Situation Assessment

### What's Actually Sellable Right Now
The Store Report Card. That's it. And it's good enough.

Three independent reviewers converged: the Report Card with green/yellow/red scoring and dollar-value opportunity estimates is the single most compelling thing in the product. An operator sees "🔴 Prerolls: -16.3% below market — leaving ~$87/week on the table" and understands it in 2 seconds.

### What Blocks Revenue TODAY
1. **Recommendations page contradicts the Report Card** — tells operators to *lower* prices while the RC says "raise them." If an operator sees both, trust is destroyed. This is a P0 blocker.
2. **Landing page hero still says old copy** — needs "Find the $5,000/month hiding in your menu"
3. **Outreach emails have 4 issues** — #25 weak data, #23 tone, #11 duplicate, domain verification
4. **Weedmaps scraper at 5.8%** — 58% of the market is invisible. Operators will check their competitors and find gaps.
5. **No payment flow** — even if someone wants to pay, they can't

### The Brutal Math
- 772 licensed operators with emails in our database
- 25 personalized outreach emails ready (with fixes needed)
- Target conversion: 25 emails → 8-12 signups → 2-3 paying @ $199/mo = $400-600 MRR
- Then: second batch of 50 emails → repeat
- 14 days to first dollar. Not 14 days to perfect product.

---

## Phase 1: Immediate Cleanup
**Timeline:** Tonight (Feb 12) through Feb 13 EOD  
**Goal:** Remove all contradictions, fix outreach emails, ship landing page update  
**Principle:** Nothing goes out the door that contradicts itself

### Task 1.1: Kill Recommendations Contradictions ⛔ BLOCKER
**Priority:** P0 — do this FIRST  
**Assignee:** Codex 5.3  
**Time:** 2-3 hours  
**What:** 
- Remove or replace ALL seed data in the Recommendations page that suggests lowering prices
- Every recommendation must align with Report Card logic: if below market → "opportunity to earn more"; if above market → "premium position, monitor velocity"  
- Specifically fix: "2-pack preroll bundle: $19 → $17", "1g vape cart: $72 → $68", "Gummy: $34 → $31" — all must be inverted or replaced
- If recommendations can't be generated from real data yet, show an honest empty state: "Recommendations generate after 7 days of price tracking. Your Report Card is ready now."
**Acceptance criteria:** Zero instances of "lower"/"reduce"/"decrease" price language anywhere in the Recommendations page. Manual audit of every recommendation shown to operators.
**Depends on:** Nothing  
**Blocks:** Outreach emails (cannot send operators to a product that contradicts itself)

### Task 1.2: Landing Page Hero + CTA Update
**Priority:** P0  
**Assignee:** Kimi K2.5  
**Time:** 1-2 hours  
**What:**
- Hero headline → "Find the $5,000/month hiding in your menu"
- Subheadline → "GLASS tracks every price at every MA dispensary. See where you're leaving money on the table — for free."
- Primary CTA → "See Your Store's Report Card — Free"
- Remove any remaining "Coming Soon" feature cards that don't link to live functionality
- Kill the ecosystem section at the bottom (GLASS + Budtender + Cue + Delivery). Just GLASS. One product, one promise.
- If Threat Radar, Morning Brief, or Cue are shown, either remove them or move them to a subtle "Coming Soon" roadmap section below the fold
**Acceptance criteria:** Above-the-fold shows ONLY: headline, subheadline, CTA button, and maybe one social proof stat ("Tracking 100K+ products across 500+ MA dispensaries"). No dead links, no vaporware.
**Depends on:** Nothing  
**Blocks:** Outreach emails (emails link to landing page)

### Task 1.3: Fix Outreach Emails (4 specific issues)
**Priority:** P0  
**Assignee:** Gemini 2.5 Flash (bulk text revision)  
**Time:** 1-2 hours  
**What:**
- **Email #25**: Strengthen with real data — pull operator's actual category pricing from the database, replace weak/generic claims with specific dollar amounts
- **Email #23**: Remove "dollar store" tone — rewrite to be professional, data-driven, respectful. These are business owners.
- **Email #11**: Remove duplicate content (likely copy-paste artifact)
- **ALL 25 emails**: Verify every URL points to `glassintel.xyz` (not `glassintel.com` or other domains). Verify every public report card link is `glassintel.xyz/report/{slug}` and the slug exists in the database.
- **ALL 25 emails**: Verify the CTA "See Your Store's Report Card" links to the operator's actual public report card page, and that page loads correctly
**Acceptance criteria:** All 25 emails reviewed, 4 specific fixes applied, all URLs verified against production. Save updated batch to `outreach/emails-batch-1-final.md`
**Depends on:** Task 1.1 (Recs fix — don't send people to broken product)  
**Blocks:** Phase 2 email send

### Task 1.4: Operator Scoring Run
**Priority:** P1  
**Assignee:** Codex 5.3  
**Time:** 1-2 hours  
**What:**
- Execute the scoring algorithm to populate `operator_scores` table
- Score all 473 operators based on: product count, price positioning vs market, category coverage, data freshness
- Create materialized views `mv_operator_health` and `mv_thc_integrity`
- Verify scores appear correctly on Report Card pages
**Acceptance criteria:** `operator_scores` table has ≥400 rows. At least 10 sample report cards spot-checked for accurate scoring.
**Depends on:** Nothing  
**Blocks:** Report Card accuracy for outreach targets

### Task 1.5: Public Report Card Smoke Test
**Priority:** P1  
**Assignee:** Manual (Randy or COO)  
**Time:** 30 minutes  
**What:**
- Open 5 of the 25 outreach target operator public report card pages in incognito
- Verify: page loads, data is populated, green/yellow/red indicators render, CTA to signup works, no broken layouts
- Test on mobile (most operators will check email on their phone)
- Document any failures
**Acceptance criteria:** All 5 pages load correctly on desktop and mobile. CTA button works.
**Depends on:** Tasks 1.1, 1.4  
**Blocks:** Email send

---

## Phase 2: First Revenue Sprint
**Timeline:** Feb 13–26 (14 days)  
**Goal:** First paying customer at $199/mo  
**Strategy:** Send outreach → free signups → demonstrate value via Report Card → convert to paid via Stripe  

### Week 1 (Feb 13-19): Outreach + Stripe + Scraper Fix

#### Task 2.1: Send First Email Batch (25 operators)
**Priority:** P0  
**Assignee:** Randy (via Resend or Gmail — personal touch)  
**Time:** Day 1 (Feb 13), 30 minutes  
**What:**
- Send all 25 personalized outreach emails
- Use Resend for deliverability (already configured)
- Send between 9-11 AM ET (operators checking email before store opens at 10 AM)
- Subject line format: "[Store Name] — you're leaving $X/month on the table"
- Each email links to that operator's public report card page
**Acceptance criteria:** 25 emails sent, delivery confirmed (no bounces), open rates trackable
**Depends on:** Phase 1 Tasks 1.1-1.5 all complete  
**Blocks:** Everything downstream — this is the revenue trigger

#### Task 2.2: Stripe Integration — Minimum Viable Payment
**Priority:** P0  
**Assignee:** Codex 5.3  
**Time:** 4-6 hours  
**What:**
- Integrate Stripe Checkout (not custom payment forms — use Stripe's hosted page)
- Create two products in Stripe: "GLASS Free" ($0) and "GLASS Pro" ($199/mo)
- Add upgrade CTA inside the authenticated dashboard: "Unlock full competitive intelligence — $199/mo"
- Free tier shows: Report Card (limited — top 3 categories only), basic market stats
- Paid tier unlocks: Full Report Card (all categories), Price Wire with CSV export, Threat Radar, competitor detail views
- Webhook handler: on `checkout.session.completed`, update user record with `plan: 'pro'`, `stripe_customer_id`, `stripe_subscription_id`
- Webhook handler: on `customer.subscription.deleted`, downgrade to free
- Add middleware to check plan on gated endpoints
**Implementation specifics:**
- Use `stripe` npm package
- Checkout success redirect → `/dashboard?upgraded=true` with a toast "Welcome to GLASS Pro!"
- Checkout cancel redirect → `/pricing` 
- Create `/api/v1/billing/create-checkout-session` endpoint
- Create `/api/v1/billing/webhook` endpoint (verify Stripe signature)
- Create `/api/v1/billing/portal` endpoint (redirect to Stripe Customer Portal for subscription management)
**Acceptance criteria:** End-to-end test: create checkout → complete payment (test mode) → user record updated → gated content unlocked → manage subscription via portal
**Depends on:** Nothing (can run parallel with outreach)  
**Blocks:** Paid conversions

#### Task 2.3: Weedmaps Scraper Fix — Target 50%+ Success
**Priority:** P0  
**Assignee:** Codex 5.3  
**Time:** 4-6 hours  
**What (specific technical fixes based on WEEDMAPS-FIX-PLAN.md):**
1. **Force local CamoFox for Weedmaps** — add `WEEDMAPS_CAMOFOX_URL = 'http://localhost:9377'` in config. Weedmaps blocks datacenter IPs; Railway's IP gets blocked. The scraper must route through local CamoFox.
2. **Fix discovery endpoint** — the GraphQL listing query returns 0 slugs in production. The issue is likely: (a) different GraphQL schema in production vs local, (b) rate limiting on the listing endpoint, or (c) missing headers/cookies. Fix: add retry logic with exponential backoff (3 retries, 2s/4s/8s), rotate User-Agent strings, add `Accept-Language` and `Referer` headers matching real browser.
3. **Add per-dispensary retry with circuit breaker** — if a dispensary fails 3 times consecutively, skip it for 24 hours (don't waste requests on stores that consistently block us)
4. **Implement residential proxy rotation** — if CamoFox alone isn't enough, add proxy support via `WEEDMAPS_PROXY_URL` env var. Options: BrightData residential ($0.60/GB), or SmartProxy ($0.50/GB). Budget: $20/month max.
5. **Target:** Go from 10/173 (5.8%) to at least 87/173 (50%+) dispensaries successfully scraped
6. **Validate:** After fix, run a manual scrape of 20 known Weedmaps-only dispensaries and verify product data appears in the database
**Acceptance criteria:** Single scrape run hits ≥50% success rate on Weedmaps dispensaries. Products from Weedmaps-only stores appear in database.
**Depends on:** Nothing (run parallel)  
**Blocks:** Market coverage (without this, operators near Weedmaps-only competitors see gaps)

#### Task 2.4: Free vs. Paid Tier Gating in Frontend
**Priority:** P1  
**Assignee:** Kimi K2.5  
**Time:** 3-4 hours  
**What:**
- Add plan-aware gating throughout the dashboard
- Free tier users see: Report Card (top 3 categories + blur/lock on rest), market summary stats, 1 competitor visible
- Paid tier users see: Full Report Card, all competitors, Price Wire with filters + CSV export, Threat Radar detail
- Upgrade prompts at every gate: "See all 5 categories — Upgrade to Pro" with direct link to Stripe Checkout
- The upgrade prompt should show the SPECIFIC dollar opportunity they're missing: "You have 2 more categories with potential savings — unlock for $199/mo"
**Acceptance criteria:** Free user sees gated content with clear upgrade path. Paid user sees everything. No broken states.
**Depends on:** Task 2.2 (Stripe integration)  
**Blocks:** Conversion optimization

#### Task 2.5: GA4 Event Tracking
**Priority:** P1  
**Assignee:** Kimi K2.5  
**Time:** 1-2 hours  
**What:**
- Verify GA4 is firing on all pages (landing, signup, dashboard, report card)
- Add custom events: `report_card_view`, `signup_start`, `signup_complete`, `upgrade_click`, `checkout_start`, `checkout_complete`, `outreach_email_click` (UTM parameter on email links)
- Add UTM parameters to all outreach email links: `?utm_source=outreach&utm_medium=email&utm_campaign=batch1`
**Acceptance criteria:** GA4 Real-Time view shows events when testing. UTM params visible in GA4 traffic sources.
**Depends on:** Nothing  
**Blocks:** Measuring outreach effectiveness

### Week 2 (Feb 20-26): Follow-Up + Convert + Second Batch

#### Task 2.6: Follow-Up Sequence for Non-Responders
**Priority:** P0  
**Assignee:** Gemini 2.5 Flash (draft) → Randy (send)  
**Time:** 2 hours draft, 30 min send  
**When:** Feb 17 (Day 4 after initial send)  
**What:**
- For operators who opened email but didn't sign up: send follow-up with a different angle. Example: "Last week we showed you your pricing position. Here's what changed: [competitor X] adjusted their flower prices. Here's your updated report card."
- For operators who signed up but haven't logged in: send "Your Report Card is ready" email with a screenshot of their actual Report Card embedded in the email
- For operators who logged in: send nothing (they're already engaged — let the product work)
**Acceptance criteria:** Follow-up emails drafted, personalized with real data, approved by Randy before send
**Depends on:** Task 2.1 (initial send) + 3-4 days of response data

#### Task 2.7: Second Outreach Batch (50 operators)
**Priority:** P0  
**Assignee:** Gemini 2.5 Flash (generate) → Gemini 2.5 Pro (review) → Randy (approve + send)  
**Time:** 4-6 hours generation, 2 hours review  
**When:** Feb 18-19  
**What:**
- Generate 50 more personalized outreach emails using the same template that worked in Batch 1
- Prioritize operators: (a) in areas with high Dutchie coverage (we have good data), (b) with the highest dollar-value opportunities visible in their Report Card, (c) single-store operators (more likely to convert at $199/mo)
- Learn from Batch 1 metrics: which subject lines got opens? Which CTAs got clicks? Adjust.
**Acceptance criteria:** 50 emails generated, reviewed, URLs verified, ready to send
**Depends on:** Batch 1 results (at least open/click data)

#### Task 2.8: Cue Alert MVP (Daily Price Change Emails)
**Priority:** P1 (Maria's #1 request — but not blocking first revenue)  
**Assignee:** Codex 5.3  
**Time:** 6-8 hours  
**What:**
- Build a daily email digest: "Here's what changed in your market yesterday"
- Content: competitor price changes (up/down by category), new products listed, products removed
- Trigger: cron job runs at 7 AM ET daily (after 6 AM quality check completes)
- Send via Resend to all operators with `alert_preferences.daily_digest = true`
- Template: clean, mobile-first HTML email with Report Card summary at top, changes below
- Default: all new signups get daily digest ON (can unsubscribe)
**Implementation:**
- New endpoint: `POST /api/v1/alerts/generate-daily` (internal, cron-triggered)
- Query: `SELECT * FROM prices WHERE created_at > NOW() - INTERVAL '24 hours'` joined with operator's competitor set
- Diff against previous day's prices for same products
- Resend batch API for sending
**Acceptance criteria:** Manual trigger sends a correctly formatted email to a test address with real price change data
**Depends on:** 7+ days of scraping data (won't have meaningful diffs until ~Feb 19)  
**Blocks:** Maria's conversion (she said this is her #1 request)

#### Task 2.9: Pricing Page
**Priority:** P1  
**Assignee:** Kimi K2.5  
**Time:** 2-3 hours  
**What:**
- Create `/pricing` page with two tiers:
  - **Free**: Report Card (limited), market overview, public report card link
  - **Pro — $199/mo**: Full Report Card, Price Wire + CSV export, Cue daily alerts, Threat Radar, priority support
- Include FAQ: "Can I cancel anytime?" (yes), "What data do you track?" (every Dutchie + Weedmaps menu in MA), "How fresh is the data?" (updated daily)
- Social proof section (even if placeholder): "Tracking 100K+ products across 500+ MA dispensaries"
- CTA: "Start Free" (→ signup) and "Upgrade to Pro" (→ Stripe Checkout)
**Acceptance criteria:** Clean pricing page, both CTAs work, mobile responsive
**Depends on:** Task 2.2 (Stripe)

### Phase 2 Revenue Target
- **25 outreach emails → 8-12 free signups → 2-3 paid conversions = $400-600 MRR**
- **50 more emails → 15-20 signups → 3-5 more paid = $600-1,000 additional MRR**
- **Phase 2 exit target: $1,000-1,600 MRR (5-8 paying customers)**

---

## Phase 3: Product-Market Fit
**Timeline:** Feb 27 – Apr 13 (30-60 days)  
**Goal:** 15-25 paying customers, $3,000-5,000 MRR, validated that operators retain and use the product weekly  
**Strategy:** Ship the features reviewers said would 2x willingness to pay, build retention loops

### Task 3.1: Morning Brief Email (Maria's #1 Feature)
**Priority:** P0  
**Assignee:** Codex 5.3 (backend) + Kimi K2.5 (email template)  
**Time:** 8-10 hours total  
**What:**
- Daily email at 7 AM ET with: (a) Report Card summary (top 3 opportunities), (b) competitor changes in last 24h, (c) new threats (license applications in their area), (d) one actionable recommendation
- This is NOT the same as Cue alerts — Morning Brief is a curated daily summary, not raw change notifications
- Personalized per operator: their store name, their competitors, their categories
- "Reply to this email with any questions" → goes to Randy's inbox (personal touch at this scale)
**Acceptance criteria:** 5 test emails sent to Randy's address, each for a different operator profile, all with accurate real data
**Depends on:** 14+ days of scraping data, Cue Alert MVP (Task 2.8) as foundation  
**Why this matters:** Maria explicitly said "if I got this every morning at 6:30 AM, I'd pay $199/mo without thinking"

### Task 3.2: THC Accuracy Score
**Priority:** P1  
**Assignee:** Codex 5.3  
**Time:** 6-8 hours  
**What:**
- Cross-reference 147K CCC lab tests against menu listings
- For each product on an operator's menu, find matching lab test results
- Calculate discrepancy: if menu says "THC: 28%" but lab test says 22%, flag it
- Show on Report Card: "THC Accuracy Score: 73% — 12 of 44 products show THC claims that don't match lab data"
- This is a REGULATORY RISK feature — operators can get fined for inaccurate THC claims
- Massive differentiation: nobody else cross-references lab data against menus
**Acceptance criteria:** THC Accuracy Score calculated for ≥100 operators. Score visible on Report Card. Flagged products listed with specific discrepancy amounts.
**Depends on:** Lab test data imported (done — 147K rows), product matching logic
**Why this matters:** Derek rated this as one of his top 5 milestones. Regulatory compliance is a "hair on fire" problem.

### Task 3.3: Competitor Deep Dive View
**Priority:** P1  
**Assignee:** Kimi K2.5 (frontend) + Codex 5.3 (API endpoint)  
**Time:** 6-8 hours  
**What:**
- From the Report Card, click any competitor to see: their full menu, their pricing by category, their price changes over time, their THC accuracy score
- Side-by-side comparison: "Your flower avg: $35. Their flower avg: $31. They have 12 more SKUs than you."
- Product-level comparison: "Your Blue Dream 3.5g: $45. Their Blue Dream 3.5g: $38."
- This is what Maria and Derek both asked for — specific, not averages
**Acceptance criteria:** Competitor detail page loads with real data for any of the 473 operators
**Depends on:** 14+ days of price data for trend lines

### Task 3.4: Area/Radius Filtering
**Priority:** P1  
**Assignee:** Codex 5.3 (backend) + Kimi K2.5 (frontend)  
**Time:** 6-8 hours  
**What:**
- Add radius filter to all views: "Show competitors within X miles" (default: 5 miles)
- Maria's #1 complaint: "I don't care about statewide averages. Show me East Boston."
- Use existing geocoded operator data (490/492 done)
- Market averages recalculate based on radius (not statewide)
- Report Card recalculates: "Your flower is 9.4% below average *in your area*" (not statewide)
**Acceptance criteria:** Filter works, Report Card recalculates with area data, map view shows radius
**Depends on:** Geocoding (done)

### Task 3.5: Multi-Location Support (Derek's Dealbreaker)
**Priority:** P1 — but schedule for Week 4-5, not Week 1  
**Assignee:** Codex 5.3 (backend schema + API) + Kimi K2.5 (frontend)  
**Time:** 12-16 hours total  
**What:**
- Allow one account to claim multiple dispensaries
- Portfolio dashboard: side-by-side Report Cards for all locations
- Aggregated opportunity: "Across your 4 stores, you're leaving $X/month on the table"
- Per-store drill-down
- Database: add `user_operators` junction table (many-to-many between users and operators)
- Onboarding: after claiming first store, prompt "Do you have other locations?"
- Pricing: $999/mo annual for multi-location (but don't build this tier into Stripe until at least 1 multi-location customer is ready to pay)
**Acceptance criteria:** One account can claim 4 stores, see all 4 Report Cards, aggregate opportunity shown
**Depends on:** Core Report Card accuracy, Stripe integration  
**Why this matters:** Derek said this is his #1 dealbreaker. He's a $999/mo annual customer ($12K/year). Worth the investment.

### Task 3.6: Scraper Reliability — Target 80%+ Both Sources
**Priority:** P1 (ongoing)  
**Assignee:** Codex 5.3  
**Time:** Ongoing, 2-3 hours/week maintenance  
**What:**
- Dutchie: maintain 83%+ success rate, investigate remaining 40 failures (likely: stores that closed, invalid URLs, stores with no menu)
- Weedmaps: after Phase 2 fix gets to 50%, iterate to 80%+ by adding: proxy rotation, better session management, handling of Cloudflare challenges
- Add monitoring: daily Slack/Discord notification with scrape success rates
- Add data quality checks: if a store's product count drops by >50% in one day, flag for review (likely scraper failure, not real menu change)
**Acceptance criteria:** 7-day rolling average: Dutchie ≥85%, Weedmaps ≥70%
**Depends on:** Task 2.3 (initial Weedmaps fix)

### Task 3.7: Outreach Scaling — 200 More Emails
**Priority:** P0  
**Assignee:** Gemini 2.5 Flash (bulk generation) → Gemini 2.5 Pro (quality review)  
**Time:** 8-10 hours total  
**When:** Staggered, 50/week over 4 weeks  
**What:**
- Generate personalized outreach for the next 200 operators (prioritized by opportunity size and data coverage)
- A/B test subject lines based on Batch 1+2 data
- Include public report card links for each operator
- Segment: single-store operators get the $199/mo pitch, multi-store operators get "we're building portfolio view — early access" pitch
**Acceptance criteria:** 200 emails generated, reviewed, URLs verified, segmented, ready for staggered send
**Depends on:** Batch 1+2 results for optimization data

### Phase 3 Revenue Target
- **200 additional outreach emails → 60-80 free signups → 15-20 paid conversions**
- **Retention: ≥80% of Month 1 paid customers retain into Month 2**
- **Phase 3 exit target: $3,000-5,000 MRR (15-25 paying customers)**

---

## Phase 4: Scale
**Timeline:** Apr 14 – May 13 (60-90 days)  
**Goal:** $5,000-7,000 MRR, 25-35 paying customers, sustainable growth engine  
**Strategy:** Product sells itself via word-of-mouth + content marketing + the data moat compounds daily

### Task 4.1: Newsletter / Content Flywheel
**Priority:** P0  
**Assignee:** Gemini 2.5 Pro (write) → Randy (approve)  
**Time:** 4 hours/week ongoing  
**What:**
- Weekly "MA Cannabis Market Intelligence" newsletter via Beehiiv (already partially set up)
- Content: market price trends, category analysis, new license applications, regulatory updates
- Free for anyone — this is the top-of-funnel
- Every issue includes: "Want this for YOUR store? See your personalized Report Card → [link]"
- Data source: GLASS's own database (unique content nobody else can write)
- Target: 500 subscribers in 30 days (push to all 772 licensed operator emails + LinkedIn)
**Acceptance criteria:** First 4 issues drafted and scheduled, Beehiiv flow working
**Why this matters:** Inbound. Randy hates sales. The newsletter IS the sales team.

### Task 4.2: Google Reviews Integration
**Priority:** P2  
**Assignee:** Codex 5.3  
**Time:** 8-10 hours  
**What:**
- Pull Google Reviews for all 473 operators via Google Places API (already active)
- Add to Report Card: "Your store: 4.2★ (127 reviews). Market avg: 4.1★. Nearest competitor: 4.5★ (89 reviews)"
- Sentiment analysis on recent reviews: "Customers mention 'wait time' 3x more than your competitors"
- This is a retention feature — gives operators another reason to check GLASS daily
**Acceptance criteria:** Reviews data populated for ≥300 operators, visible on Report Card

### Task 4.3: Census Demographics Import
**Priority:** P2  
**Assignee:** Codex 5.3  
**Time:** 4-6 hours  
**What:**
- Import Census data for MA zip codes: household income, age distribution, population density
- Add to operator profiles: "Your store is in a zip code with median household income $72K. Average cannabis spend correlates to income — consider premium product mix."
- This enriches recommendations and helps operators understand WHY certain pricing works
**Acceptance criteria:** Census data imported and linked to operator zip codes

### Task 4.4: Agency Sprint Revenue Stream
**Priority:** P1  
**Assignee:** Randy (deliver) + Opus 4.6 (strategy/analysis)  
**Time:** Per-engagement  
**What:**
- For operators who want deeper analysis: offer $3K "Market Position Sprint" — 2-week deep dive with custom report, product mix recommendations, competitor analysis, pricing strategy
- Deliver using GLASS data + AI analysis (Opus 4.6 for strategy, Gemini 2.5 Pro for data analysis)
- Target: 1 sprint/month = $3K additional revenue
- Pipeline from highest-engagement GLASS Pro users
**Acceptance criteria:** Sprint offering page live, first sprint delivered

### Task 4.5: Enterprise Tier for Multi-Location
**Priority:** P1  
**Assignee:** Codex 5.3 (billing) + Kimi K2.5 (dashboard)  
**Time:** 8-10 hours  
**What:**
- Formalize multi-location pricing in Stripe: $999/mo annual ($11,988/year)
- Portfolio analytics dashboard: cross-store performance, best/worst performing locations, unified recommendations
- Dedicated onboarding for enterprise customers
- Target: Derek as first enterprise customer
**Acceptance criteria:** Enterprise tier in Stripe, portfolio dashboard functional, Derek contacted for pilot

### Phase 4 Revenue Target
- **SaaS MRR: $5,000-7,000 (25-35 customers)**
- **Agency sprints: $3,000-6,000/quarter**
- **Newsletter sponsorships: exploring (need 1,000+ subscribers first)**
- **Phase 4 exit target: $7,000-10,000 total monthly revenue**

---

## Daily Schedule: Days 1–7

### Day 1 — Thursday, Feb 13
| Time (ET) | Task | Who | Duration |
|-----------|------|-----|----------|
| 8:00 AM | Deploy Recommendations fix (Task 1.1) | Codex 5.3 | Already running overnight |
| 9:00 AM | Deploy landing page update (Task 1.2) | Kimi K2.5 | Already running overnight |
| 9:30 AM | Run operator scoring (Task 1.4) | Codex 5.3 | 1 hour |
| 10:00 AM | Smoke test 5 public report cards (Task 1.5) | Randy | 30 min |
| 10:30 AM | Final email review + domain verification (Task 1.3) | Gemini 2.5 Flash | 1 hour |
| 11:30 AM | **SEND 25 OUTREACH EMAILS** (Task 2.1) | Randy via Resend | 30 min |
| 12:00 PM | Start Stripe integration (Task 2.2) | Codex 5.3 | Begin |
| 1:00 PM | Start Weedmaps scraper fix (Task 2.3) | Codex 5.3 (if bandwidth) or queue for tomorrow | Begin |
| 3:00 PM | GA4 event tracking setup (Task 2.5) | Kimi K2.5 | 2 hours |
| 5:00 PM | **EOD check:** Emails sent? Open rate? Any bounces? | Randy | 15 min |

### Day 2 — Friday, Feb 14
| Time (ET) | Task | Who | Duration |
|-----------|------|-----|----------|
| 8:00 AM | Check email open rates from Day 1 send | Randy | 15 min |
| 8:30 AM | Continue Stripe integration (Task 2.2) | Codex 5.3 | 4 hours |
| 9:00 AM | Weedmaps scraper fix — full focus (Task 2.3) | Codex 5.3 (2nd agent) | 4-6 hours |
| 1:00 PM | Stripe integration testing (test mode end-to-end) | Randy + Codex 5.3 | 2 hours |
| 3:00 PM | Free/paid tier gating in frontend (Task 2.4) | Kimi K2.5 | 3-4 hours |
| 5:00 PM | **EOD check:** Stripe working? Weedmaps progress? Any signups from outreach? | Randy | 15 min |

### Day 3 — Saturday, Feb 15
| Time (ET) | Task | Who | Duration |
|-----------|------|-----|----------|
| Morning | Light day — check metrics only | Randy | 30 min |
| 10:00 AM | Weedmaps scraper fix — complete + test run (Task 2.3) | Codex 5.3 | 3 hours |
| 1:00 PM | Pricing page build (Task 2.9) | Kimi K2.5 | 2-3 hours |
| 3:00 PM | Run full scrape cycle — verify both Dutchie + Weedmaps | Automated | Monitor |
| Evening | Review: any operator signups? Report card page views? | Randy | 15 min |

### Day 4 — Sunday, Feb 16
| Time (ET) | Task | Who | Duration |
|-----------|------|-----|----------|
| Rest day | Monitor only — check for signups, respond to any operator emails | Randy | 30 min total |
| Background | Scrapers running (automated crons) | Automated | — |

### Day 5 — Monday, Feb 17
| Time (ET) | Task | Who | Duration |
|-----------|------|-----|----------|
| 8:00 AM | Week 1 metrics review: opens, clicks, signups, logins | Randy | 30 min |
| 9:00 AM | Draft follow-up emails for non-responders (Task 2.6) | Gemini 2.5 Flash | 2 hours |
| 11:00 AM | Start second batch email generation (Task 2.7) — 50 operators | Gemini 2.5 Flash | 4 hours |
| 2:00 PM | Send follow-up emails to Day 1 non-responders | Randy | 30 min |
| 3:00 PM | Begin Cue Alert MVP backend (Task 2.8) | Codex 5.3 | Start |
| 5:00 PM | **Decision point:** Is Stripe live? Any paid signups? If not, what's blocking? | Randy | 30 min |

### Day 6 — Tuesday, Feb 18
| Time (ET) | Task | Who | Duration |
|-----------|------|-----|----------|
| 8:00 AM | Continue Cue Alert MVP (Task 2.8) | Codex 5.3 | 4 hours |
| 9:00 AM | Review second batch emails (Task 2.7) | Gemini 2.5 Pro | 2 hours |
| 11:00 AM | Send second batch — first 25 of 50 | Randy | 30 min |
| 1:00 PM | Cue Alert email template design | Kimi K2.5 | 2 hours |
| 3:00 PM | Respond to any operator questions/feedback (personal replies) | Randy | As needed |
| 5:00 PM | **EOD:** Track total signups, engagement patterns, any payment attempts | Randy | 15 min |

### Day 7 — Wednesday, Feb 19
| Time (ET) | Task | Who | Duration |
|-----------|------|-----|----------|
| 8:00 AM | Send second batch — remaining 25 of 50 | Randy | 30 min |
| 9:00 AM | Complete Cue Alert MVP — test with real data | Codex 5.3 | 3 hours |
| 12:00 PM | **WEEK 1 RETROSPECTIVE** | Randy + COO | 1 hour |
| Items to review: | (1) Outreach metrics: opens, clicks, signups, paid conversions | | |
| | (2) Scraper reliability: Dutchie + Weedmaps success rates over 7 days | | |
| | (3) Product feedback: any operator replies, feature requests, complaints | | |
| | (4) Revenue: any paying customers? If not, what's the blocker? | | |
| | (5) Decision: adjust pricing? Change outreach angle? Double down? | | |
| 2:00 PM | Act on retrospective decisions | All | Rest of day |

---

## Dependency Map

```
Phase 1 (Cleanup)                          Phase 2 (Revenue)
┌──────────────────┐                       ┌──────────────────┐
│ 1.1 Fix Recs     │──────────────────────▶│ 2.1 Send Emails  │
│ (Codex, P0)      │                       │ (Randy, P0)      │
└──────────────────┘                       └────────┬─────────┘
┌──────────────────┐                                │
│ 1.2 Landing Page │──────────────────────▶         │
│ (Kimi, P0)       │                                │
└──────────────────┘                                │
┌──────────────────┐                                │
│ 1.3 Fix Emails   │──────────────────────▶         │
│ (Gemini, P0)     │                                │
└──────────────────┘                                │
┌──────────────────┐                                │
│ 1.4 Scoring Run  │──┐                             │
│ (Codex, P1)      │  │                             │
└──────────────────┘  │  ┌──────────────────┐       │
┌──────────────────┐  ├─▶│ 1.5 Smoke Test   │──────▶│
│                  │  │  │ (Randy, P1)      │       │
└──────────────────┘  │  └──────────────────┘       │
                      │                              │
                      │  ┌──────────────────┐       │
                      │  │ 2.2 Stripe       │───────┤──▶ 2.4 Tier Gating
                      │  │ (Codex, P0)      │       │    (Kimi, P1)
                      │  └──────────────────┘       │         │
                      │  ┌──────────────────┐       │         ▼
                      │  │ 2.3 Weedmaps Fix │       │    2.9 Pricing Page
                      │  │ (Codex, P0)      │       │    (Kimi, P1)
                      │  └──────────────────┘       │
                      │                              │
                      │                              ▼
                      │                         2.6 Follow-up
                      │                         (Gemini→Randy)
                      │                              │
                      │                              ▼
                      │                         2.7 Batch 2
                      │                         (Gemini→Randy)
                      │                              │
                      │  ┌──────────────────┐       │
                      │  │ 2.8 Cue Alert    │◀──────┘ (needs 7 days data)
                      │  │ (Codex, P1)      │
                      │  └──────────────────┘
                      │           │
                      ▼           ▼
                Phase 3: PMF
                ┌──────────────────┐
                │ 3.1 Morning Brief│ (depends on Cue Alert foundation)
                │ 3.2 THC Score    │ (depends on scoring run)
                │ 3.3 Competitor   │ (depends on 14+ days data)
                │ 3.4 Radius Filter│ (depends on geocoding — done)
                │ 3.5 Multi-Loc    │ (depends on Stripe + core RC)
                │ 3.6 Scraper 80%+ │ (depends on Task 2.3)
                │ 3.7 200 Emails   │ (depends on Batch 1+2 results)
                └──────────────────┘
```

---

## Revenue Milestones

| Date | Milestone | Target MRR | Validation |
|------|-----------|-----------|------------|
| Feb 13 | 25 outreach emails sent | $0 | Emails delivered, no bounces |
| Feb 16 | First free signup from outreach | $0 | Operator creates account + views Report Card |
| Feb 19 | Stripe live, pricing page up | $0 | End-to-end payment test passes |
| Feb 20 | 50 more outreach emails sent | $0 | Total 75 operators contacted |
| Feb 23 | **FIRST PAYING CUSTOMER** | $199 | Someone subscribes to Pro tier |
| Feb 26 | 5 paying customers | $995 | Phase 2 complete |
| Mar 13 | 15 paying customers | $2,985 | Phase 3 midpoint |
| Mar 26 | Morning Brief live, THC Score live | $2,985+ | Retention features shipping |
| Apr 13 | 25 paying customers | $4,975 | Phase 3 complete, PMF validated |
| Apr 27 | First enterprise customer (Derek?) | $5,974+ | Multi-location live, $999/mo annual |
| May 13 | 35 paying customers + 1 enterprise | $7,973 | Phase 4 complete |

### What "PMF Validated" Means
- ≥80% Month 1 → Month 2 retention
- ≥3 operators who voluntarily refer another operator
- NPS ≥40 (measured via simple email survey)
- Daily active usage ≥30% of paid base (they check at least 2x/week)

---

## Risk Register

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| R1 | Weedmaps scraper stays broken (<20% success) | Medium | High — 58% of market invisible, operators see gaps | Invest in residential proxies ($20/mo). If still broken after 2 weeks, consider Weedmaps API partnership or manual data entry for top 50 stores |
| R2 | Zero paid conversions from first 75 emails | Low-Medium | High — revenue timeline slips | Analyze: are operators signing up but not paying? (→ pricing problem, adjust to $99/mo or extend free trial). Not signing up? (→ messaging problem, rewrite outreach). Not opening? (→ deliverability problem, check spam scores) |
| R3 | Stripe integration delayed past Feb 19 | Low | High — operators want to pay but can't | Use Stripe Payment Links as a manual fallback. Randy can send a payment link via email to any operator who wants to upgrade. Takes 5 minutes to set up in Stripe dashboard. |
| R4 | CCC data goes stale (no new imports) | Low | Medium — regulatory data loses freshness | Set up quarterly CCC data import cron. CCC publishes monthly — automate the download and import |
| R5 | Operator sees contradiction between Recs and Report Card | High (until fixed) | Critical — instant trust destruction | Task 1.1 is P0 for this reason. If it's not fixed by 9 AM Feb 13, DO NOT send outreach emails. Delay by 1 day. |
| R6 | Competitor launches similar MA-focused tool | Low (short-term) | Medium | Our moat is 7 years of CCC data + daily scraping + operator relationship. Time-series data compounds. First-mover advantage in MA. |
| R7 | Scraping gets blocked entirely (Dutchie changes API) | Medium | Critical — no fresh data = no product | Maintain scraper diversity (API + browser rendering). Build relationships with data providers. Consider Dutchie partnership (they have a partner program). Keep 30-day data cache. |
| R8 | Randy burns out from manual outreach | Medium | High — he hates sales, this is unsustainable | After first 75 emails, automate: Resend drip sequences with personalized data. Randy only handles replies. Target: by Week 3, outreach is 90% automated. |
| R9 | Email deliverability issues (glassintel.xyz domain new) | Medium | High — emails go to spam | Warm up domain: send 5-10 emails/day first week, increase gradually. Use Resend's deliverability tools. Set up DKIM, SPF, DMARC if not already done. |
| R10 | Codex 5.3 OAuth rate limited during sprint | Low-Medium | Medium — backend work slows | Queue tasks by priority. Use GLM-5 as fallback for simpler coding tasks. Stagger API calls. |

---

## Decision Points for Randy

### Decision 1: Email Send Timing (Feb 13 morning)
**Question:** Are all Phase 1 blockers resolved? Is it safe to send outreach?  
**Gate:** Task 1.1 (Recs fix) MUST be deployed. Task 1.2 (landing page) MUST be deployed. Task 1.5 (smoke test) MUST pass.  
**If NO:** Delay outreach by 24 hours. Don't send operators to a broken product.  
**If YES:** Send at 9:30 AM ET. Operators check email before opening at 10 AM.

### Decision 2: Pricing Tier (Feb 14-15)
**Question:** Should Free tier show full Report Card or gated?  
**Option A:** Full Report Card free, pay for Price Wire + Cue alerts (upsell on depth)  
**Option B:** Limited Report Card free (3 categories), pay for full RC + everything (upsell on breadth)  
**Recommendation:** Option B. The Report Card IS the product. Gate it to create urgency. Show 3 categories free with a clear "$X more hiding in 2 locked categories — $199/mo to unlock."  
**Deadline:** Decide before Stripe goes live.

### Decision 3: Weedmaps Investment (Feb 17)
**Question:** After scraper fix attempt, is Weedmaps worth continued investment?  
**If ≥50% success:** Keep iterating, target 80% by end of month  
**If <30% success:** Consider: (a) residential proxy ($20/mo), (b) reaching out to Weedmaps for API access, (c) accepting Dutchie-only coverage and being transparent about it  
**Note:** 195/235 Dutchie coverage is already good. Weedmaps adds 173 more dispensaries. Worth fixing, but don't let it block revenue.

### Decision 4: Follow-Up Strategy (Feb 17)
**Question:** Based on Batch 1 results, what's the follow-up approach?  
**If >30% open rate + some signups:** Follow-up email to non-openers with different subject line  
**If <15% open rate:** Deliverability problem — check spam, try different sending approach (personal Gmail?)  
**If signups but no paid:** Product or pricing issue — reach out personally to 3 signups and ask "what would make you pay?"

### Decision 5: First Enterprise Outreach (Mar 15)
**Question:** Is multi-location support ready for Derek?  
**Gate:** Task 3.5 must be complete + tested with 4 stores  
**If YES:** Personal email to Derek: "You told us multi-location was your dealbreaker. It's live. Here's your portfolio view."  
**If NO:** Don't reach out. Derek specifically said this was the dealbreaker. Showing him the product without it would be worse than waiting.

### Decision 6: Pricing Adjustment (Mar 1)
**Question:** After 2 weeks of data, is $199/mo the right price?  
**If conversion rate >5% of signups:** Price is fine, maybe even low. Consider testing $249/mo for new signups.  
**If conversion rate 2-5%:** Price is okay. Focus on product value, not price.  
**If conversion rate <2%:** Consider: (a) $99/mo intro offer, (b) first month free, (c) "pay what it's worth" for first 10 customers to learn willingness-to-pay

---

## Model Assignment Matrix

| Task Category | Primary Model | Fallback | Cost Estimate |
|---------------|--------------|----------|---------------|
| Backend development (APIs, DB, scrapers) | Codex 5.3 (free OAuth) | GLM-5 ($1/$3.20) | $0 primary |
| Frontend development (React, UI, pages) | Kimi K2.5 (free NVIDIA) | GLM-5 ($1/$3.20) | $0 primary |
| Bulk text generation (emails, content) | Gemini 2.5 Flash ($0.15/$0.60) | — | ~$2-5/batch |
| Quality review (email review, QA) | Gemini 2.5 Pro ($1.25/$10) | Gemini 2.5 Flash | ~$5-10/review |
| Strategy + architecture decisions | Opus 4.6 ($5/$25) | Gemini 2.5 Pro | $10-20/session |
| Code review + QA passes | Codex 5.3 (free OAuth) | Gemini 2.5 Pro | $0 primary |

### Budget Estimate (14-day sprint)
- AI model costs: ~$30-50 (mostly Gemini for email generation + reviews)
- Residential proxy (if needed): $20/mo
- Resend email: free tier (100 emails/day)
- Stripe: 2.9% + $0.30 per transaction (paid by revenue)
- **Total additional spend: ~$50-70 for the entire 14-day sprint**

---

## What We Are NOT Doing (Kill List)

These are explicitly deprioritized. Do not work on them unless all Phase 2 tasks are complete:

1. ~~Virtual Budtender development~~ — Pause until 50+ active operators
2. ~~Brand Marketplace~~ — Year 2+, zero liquidity
3. ~~Delivery product~~ — No partnership, no demand signal
4. ~~Complex time-series visualizations~~ — Need 30+ days of data
5. ~~Census demographics~~ — Nice-to-have, Phase 4 earliest
6. ~~Google Reviews~~ — Phase 4
7. ~~Mobile app~~ — Nobody asked for this, 27 delivery operators isn't a market
8. ~~Additional state expansion~~ — Nail MA first, then consider
9. ~~API for third-party developers~~ — No demand signal
10. ~~Fake sparklines / trend lines~~ — Remove, don't fix. Show honest "data collecting" states.

---

## Success Criteria — How We Know This Plan Worked

### Week 1 (Feb 13-19)
- [ ] 25 outreach emails sent with no contradictions in product
- [ ] Stripe integration live (test mode confirmed, ready for real payments)
- [ ] Weedmaps scraper ≥50% success rate
- [ ] GA4 tracking events firing
- [ ] ≥5 free signups from outreach

### Week 2 (Feb 20-26)
- [ ] 50 more outreach emails sent (75 total)
- [ ] ≥15 total free signups
- [ ] **≥1 paying customer** (THE milestone)
- [ ] Cue Alert MVP functional
- [ ] Pricing page live

### Month 1 (Feb 13 – Mar 13)
- [ ] ≥5 paying customers ($995+ MRR)
- [ ] Morning Brief in development
- [ ] THC Accuracy Score in development
- [ ] ≥80% scraper reliability both sources
- [ ] 200+ operators contacted

### Month 2 (Mar 13 – Apr 13)
- [ ] ≥20 paying customers ($3,980+ MRR)
- [ ] Morning Brief live
- [ ] THC Accuracy Score live
- [ ] Multi-location support live
- [ ] ≥80% Month 1 retention

### Month 3 (Apr 13 – May 13)
- [ ] ≥30 paying customers + 1 enterprise ($6,974+ MRR)
- [ ] Newsletter with 500+ subscribers
- [ ] First agency sprint delivered ($3K)
- [ ] Word-of-mouth referrals happening organically

---

*This plan is a living document. Update it every Monday during the weekly retrospective. The plan serves the goal (first revenue), not the other way around. If something isn't working, change the plan, not the goal.*

**The one sentence version: Fix the contradictions tonight, send the emails tomorrow morning, get Stripe live by Friday, and don't touch anything else until those three things are done.**
