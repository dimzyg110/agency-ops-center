# Roviq Automation & Revenue Strategy — The Operational Playbook

**Date:** February 12, 2026  
**Classification:** Internal — Roviq Strategic Planning  
**Author:** Senior Business Strategist & Automation Architect  
**Scope:** Full ecosystem audit + automation playbook + 30/60/90-day action plan

---

## Executive Summary

Roviq has built, in roughly two weeks, an asset base that most cannabis-tech companies would take 6–12 months and $500K+ to assemble:

- **GLASS**: 500+ MA dispensaries scraped daily, 20K+ products, 21K+ prices, 19 premium visualizations, public market page, premium dashboard behind Clerk auth.
- **SIGNAL**: AI-powered SEO engine that generates location pages, product pages, market reports, and blog posts from GLASS data. Multi-client. React/Netlify publishing via GitHub PRs.
- **Newsletter Pipeline**: Python-based "Operator's Margin Report" with CCC data integration, Price Wire, Threat Radar, Brand Movers. Beehiiv distribution (not yet connected).
- **Scraping Infrastructure**: roviq-browser (Railway, anti-detection) + CamoFox (local, anti-detection). Dutchie + Weedmaps coverage. Zero AI tokens for scraping — pure Node.js.
- **AC Toll Processing**: 85 personalized emails ready, landing page live, targeting 65 cultivators + 21 microbusinesses.
- **Delivered Proposal**: Full partnership proposal delivered. React Native delivery app plan. First operator-branded cannabis delivery app in MA.
- **Lead Tool**: 150 operators enriched with distress scores, contact info, outreach sequences.

**The problem is not capability. The problem is that almost nothing is generating revenue yet.** The ecosystem is 90% built and 5% monetized. Randy is building, not selling. The tools are powerful, but they're sitting idle while revenue targets slip.

**The core thesis of this playbook:** Stop building new things. Wire what exists into automated revenue loops that run without Randy doing sales.

### The Three Automations That Matter Most (This Week)

1. **AC Toll Processing Email Blast** — 85 emails ready. Randy approves. Resend sends. $750 + 2% per conversion. Expected: 3–5 clients = $2,250–$3,750 + ongoing rev share.
2. **Newsletter → Beehiiv Auto-Publish** — Connect pipeline to Beehiiv API. GLASS data auto-populates. Schedule Tuesday 6 AM. Zero human touch after setup. Builds audience for everything else.
3. **GLASS Public /market Page → Newsletter Signup → Operator Claim Flow** — Live public data attracts operators via SEO. Newsletter captures them. "Claim your dashboard" converts to GLASS premium.

**Revenue projection:** $10K MRR is achievable within 60 days if we execute the automation loops described in this document. $25K MRR within 90 days with SIGNAL client expansion.

---

## 1. Revenue Automation — Making Money While Sleeping

### 1.1 Immediate Revenue (This Week, $0 Additional Build)

#### A. AC Toll Processing Blast

**Status:** 85 personalized emails sitting in `/clients/ac/toll-processing/outreach-emails.md`. Landing page live at `advancedcultivatorsllc.com/toll-processing`.

**Automation workflow:**
1. Randy approves the email sample (already in Gmail)
2. Load emails into Resend (domain: `spacemanwins.win` — verified, or wait for `roviqai.xyz`)
3. Batch send: 20 emails/day over 4 days (avoid spam triggers)
4. Auto-follow-up sequence: Day 3 (value add), Day 7 (case study), Day 14 (final)
5. Track opens/clicks via Resend webhooks → log to file for COO review

**Revenue model:** $750 setup + 2% ongoing per toll client. Conservative: 3 conversions from 85 emails (3.5% rate) = **$2,250 + recurring 2% rev share**.

**What to automate:**
```
# Resend batch script (Node.js)
# For each email in outreach-emails.md:
#   1. Parse recipient, subject, body
#   2. Send via Resend API with 30-second delay between sends
#   3. Log send status + timestamp
#   4. Schedule follow-up at Day 3, Day 7 if no reply
```

**Blocker:** Randy must approve the email sample. This is the single highest-ROI action pending.

#### B. CH SEO Retainer Activation

**Status:** CH Growth Roadmap delivered. SEO scaling plan delivered. SIGNAL built for exactly this use case.

**Revenue:** $1,500–2,000/mo retainer. CH is the ideal pilot client:
- 53% of traffic from organic search with ZERO intentional SEO
- No conversion tracking (we fix this Day 1)
- Competitor BOUTIQ is outranking them on key terms
- Blog system already built in React (`src/data/blogPosts.js`)

**Automation workflow:**
1. SIGNAL generates 4 blog posts/week for CH from GLASS data
2. Auto-creates GitHub PRs to `randytorres/ch-web` repo
3. Randy (or auto-merge after review) deploys via Netlify
4. Google Search Console API submits new URLs for indexing
5. Monthly report auto-generated from GSC + GA4 data

**Action required:** Randy pitches Brian (CH contact) on $1,500/mo SEO retainer. Pitch angle: "Your organic traffic is 53% of all visits with zero effort. We can 5x it. Here's the plan we already wrote."

#### C. Newsletter Launch (Zero-Touch After Setup)

**Status:** Pipeline functional. GLASS data integration designed. Beehiiv partially set up.

**Automation workflow (one-time setup → runs forever):**
1. Connect `pipeline.py` to Beehiiv API (need form ID from Randy)
2. Fix validation gate (currently doesn't block — set `GATE_STAGES = {'validate', 'quality'}`)
3. Fix events scraper (broken — returns news articles as events)
4. Add GLASS Price Wire section (template in PIPELINE-AUDIT.md)
5. Schedule cron: Monday 4 AM → scrape → compose → validate → quality check → Beehiiv draft
6. Tuesday 6 AM → auto-send if quality passed; flag for manual review if not
7. Newsletter footer: "Powered by GLASS — claim your free dashboard"

**Revenue (indirect):** Newsletter is the top of funnel. Every subscriber is a potential:
- GLASS premium user ($399/mo)
- Agency client ($2,500/mo+)
- Toll processing lead
- SIGNAL pilot client

**Target:** 200 subscribers in 30 days, 500 in 60 days, 1,000 in 90 days.

### 1.2 Short-Term Revenue (30 Days)

#### D. GLASS Premium Subscriptions

**Pricing strategy (validated against competitors):**

| Tier | Price | What They Get | Target |
|------|-------|---------------|--------|
| **Free** | $0 | Public /market page, weekly newsletter, category averages | Everyone — for network effect |
| **Operator** | $199/mo | Full dashboard, Price Wire alerts, Threat Radar, competitor tracking for 5-mile radius | Dispensary owners |
| **Pro** | $399/mo | Everything in Operator + Margin Engine recommendations, CSV exports, API access | Multi-location operators |
| **Enterprise** | Custom | White-label, custom alerts, dedicated support | Chains (NETA, Curaleaf, etc.) |

**Why $199 not $399 for base tier:** $399 is a committee decision for most single-location dispensaries doing $35–65K/mo. $199 is an owner's credit card swipe. Once they see value, upsell to Pro.

**Conversion funnel automation:**
1. Operator sees their store on /market page (public, free)
2. CTA: "See your full competitive dashboard — free for 14 days"
3. Clerk signup → auto-provision dashboard with their data (already built)
4. Day 3: automated email with their top 3 pricing insights (Resend)
5. Day 7: "Your competitors changed prices this week" alert
6. Day 12: "Your trial ends in 2 days — here's what you'll lose" email
7. Day 14: Convert or downgrade to free

**Revenue projection:** 10 Operator subscribers in 60 days = **$1,990/mo MRR**. 25 in 90 days = **$4,975/mo**.

#### E. SIGNAL Managed SEO Service

**Phase 1 pricing (service model — we run SIGNAL for them):**

| Service | Price | Deliverables |
|---------|-------|-------------|
| SEO Audit + Setup | $2,500 one-time | Technical audit, GA4 + GSC setup, keyword strategy, initial content batch |
| Monthly SEO | $1,500/mo | 16 blog posts, 4 market reports, schema markup, rank tracking, monthly report |
| Premium SEO | $2,500/mo | Above + location pages, product pages, competitor monitoring, bi-weekly strategy calls |

**Pipeline:**
- CH: $1,500/mo (immediate)
- AC: $1,500/mo (after toll processing lands)
- Delivered: $2,500/mo (bundled with partnership if closed)
- New clients from GLASS funnel: $2,500 setup + $1,500/mo each

**Revenue projection:** 2 clients in 30 days = **$3,000/mo MRR**. 4 clients in 60 days = **$6,000/mo**.

### 1.3 Passive Income Streams (60–90 Days)

#### F. GLASS Market Reports (Automated Product)

**Concept:** Weekly/monthly MA cannabis market intelligence reports, auto-generated from GLASS data.

| Report | Price | Audience | Frequency |
|--------|-------|----------|-----------|
| MA Price Index Weekly | Free (newsletter) | Operators | Weekly |
| MA Market Intelligence Report | $99/mo | Brands, investors, consultants | Monthly |
| Regional Deep Dive | $199/report | Operators expanding to new regions | On-demand |
| Custom Competitive Analysis | $499/report | Any operator who wants to know their market position | On-demand |

**Automation:** GLASS data → Python report generator → PDF (already have pdf skill) → Stripe payment → email delivery. Zero human touch.

**Revenue projection:** 10 monthly subscribers + 5 one-off reports/mo = **$1,490/mo** with zero marginal cost.

#### G. Newsletter Sponsorships

Once newsletter hits 500+ subscribers (all MA cannabis operators — extremely targeted):

| Sponsor Type | Price | Format |
|-------------|-------|--------|
| **Featured Brand** | $500/issue | "Sponsored by [Brand]" banner + 100-word feature |
| **Product Spotlight** | $250/issue | Single product callout in Price Wire section |
| **Newsletter Takeover** | $1,000/issue | Full issue sponsor + custom section |

**Revenue projection at 500 subs:** 2 sponsors/mo × $500 = **$1,000/mo**. At 1,000 subs: **$2,000+/mo**.

**Audience value context:** Cannabis brand marketing is severely constrained (no Google Ads, limited social). A newsletter that goes directly to 500 dispensary operators is worth more per subscriber than almost any other channel.

---

## 2. Client Acquisition Automation — Never Cold Call Again

### 2.1 The GLASS Magnet (Operators Come to You)

This is the single most powerful acquisition loop in the entire ecosystem:

**The Loop:**
```
GLASS scrapes dispensary → We have their data
  → Public /market page shows aggregate data
    → Operator Googles "MA cannabis market data" → finds our page
      → Sees their region's pricing → wants their specific data
        → Signs up for free trial → sees their full dashboard
          → Dashboard shows: "Your prices are 12% above market avg"
            → They need help → "Schedule a Roviq strategy call"
              → Agency client ($2,500/mo)
```

**Auto-invite automation (the killer feature):**
```
For each new dispensary scraped by GLASS:
  1. Look up operator email (CCC license records have owner names)
  2. Generate personalized "margin snapshot" from their scraped prices
  3. Send email: "We're tracking 500+ MA dispensaries. Here's your pricing position."
  4. Include: their avg price vs. market avg, category breakdown, one actionable insight
  5. CTA: "Claim your free GLASS dashboard"
  6. Follow-up Day 5: "Your competitor [X] just changed prices. See what happened."
```

**This is not cold outreach.** This is: "We already have your data. Here's a taste. Want the full picture?" Every operator in MA who gets this email will click. It's their own business data.

**Tools needed:** Resend API + GLASS DB queries + CCC license database (public) + template engine.

**Volume:** 500+ dispensaries scraped. Even at 10% open rate and 2% conversion = 10 free signups → 2–3 paid conversions.

### 2.2 LinkedIn Automation (Passive, Value-First)

**NOT cold outreach.** This is content-driven authority building using CamoFox.

**Weekly automation:**
1. CamoFox navigates to LinkedIn
2. Search: "dispensary owner Massachusetts" / "cannabis operator MA" / "dispensary manager Boston"
3. Scrape profile URLs + names + companies
4. Cross-reference with GLASS operator database
5. Generate personalized connection requests: "Hey [Name], I run the GLASS cannabis market intelligence platform. We're tracking [their dispensary name]'s pricing vs. 500 competitors. Thought you might find this useful: [link to /market page]"
6. Send 5 connection requests/day (LinkedIn limit safe)
7. For connections who accept: auto-send GLASS dashboard invite after 3 days

**Important:** Randy doesn't do this. The COO coordinates it. CamoFox executes it. Randy sees the inbound leads.

### 2.3 Google Maps Scraping (Build the Master List)

**Automation:**
1. CamoFox → Google Maps → "dispensary" in each MA city
2. Extract: name, address, phone, website, hours, rating, review count
3. Cross-reference with CCC license database and GLASS operator table
4. Flag gaps: dispensaries we scrape but haven't contacted
5. Enrich with email (website scraping) and owner name (CCC records)
6. Output: master prospect database at `/data/workspace/projects/internal/prospect-db.json`

**Volume:** ~650 licensed retailers in MA. We should have contact info for all of them.

### 2.4 Reddit/X Monitoring (Pain Point Detection)

**Automated monitoring script:**
```python
# Run daily via cron
# Reddit: r/bostontrees, r/MAbusiness, r/weedbiz, r/cannabiscultivation
# X/Twitter: "dispensary problems" OR "cannabis pricing" OR "MA dispensary"
# 
# For each post/tweet:
#   1. Score relevance (is this an operator complaining about margins/competition/pricing?)
#   2. If score > 0.7: log to prospect database with context
#   3. If score > 0.9: flag for Randy to engage (organic comment, not pitch)
#   4. Weekly digest: "5 operators posted about pricing problems this week"
```

**Reddit is already working** — the newsletter scraper pulls from r/bostontrees. Extend it to monitor for operator pain points specifically.

### 2.5 Competitor Monitoring (Automated Alerts for Clients)

**For existing clients (AC, CH):**
1. GLASS already tracks competitor prices daily
2. Automate weekly report: "Here's what your competitors did this week"
3. Format: simple email with 3–5 bullet points + chart
4. This is pure retention value — clients stay because we're watching their market for them

**Automation:**
```
Every Monday 7 AM:
  1. Query GLASS for price changes within 5 miles of each client
  2. Filter for significant moves (>5% change or new products)
  3. Generate personalized report per client
  4. Send via Resend
```

---

## 3. Existing Client Revenue Expansion

### 3.1 AC (Advanced Cultivators)

**Current revenue:** Active client (content, social, video, brand strategy)

**Expansion opportunities:**

| Opportunity | Revenue | Effort | Timeline |
|-------------|---------|--------|----------|
| Toll Processing Outreach (blast the 85 emails) | $2,250+ initial + 2% ongoing | Low (emails ready) | This week |
| SIGNAL SEO for AC website | $1,500/mo | Medium (setup SIGNAL for AC tenant) | 30 days |
| GLASS Operator subscription for AC's retail location | $199/mo | Low (they're already an operator) | When retail opens (4/20) |
| Cue platform deployment (brand incentives via AC) | Revenue TBD (legal pending) | High (legal approval needed) | 60+ days |
| YouTube channel automation (SIGNAL generates video scripts) | $500/mo add-on | Medium | 45 days |
| Weekly competitive pricing report (automated from GLASS) | $250/mo add-on | Low | 14 days |

**Key play:** AC's 4/20 retail launch is the forcing function. By then, GLASS should show them real-time competitor pricing for Lowell-area dispensaries. Toll processing revenue should be flowing. SIGNAL should be generating content for their site.

**Estimated AC expansion:** +$2,950/mo recurring within 60 days.

### 3.2 CH (Cannabis Healing)

**Current revenue:** Active client (marketing, design, growth)

**Expansion opportunities:**

| Opportunity | Revenue | Effort | Timeline |
|-------------|---------|--------|----------|
| SIGNAL SEO retainer | $1,500/mo | Medium (CH is the pilot client) | 2 weeks |
| GLASS Operator subscription | $199/mo | Low (auto-provision their dashboard) | 30 days |
| Automated weekly competitor report | $250/mo add-on | Low | 14 days |
| Newsletter sponsorship slot (promote AC products to CH customers) | $500/issue (paid by AC) | Low | When newsletter launches |
| Dutchie menu optimization (photos, descriptions) | $1,000 one-time | Medium | 30 days |
| Evening campaign automation (Alpine IQ integration) | $500/mo add-on | Medium | 45 days |

**Key play:** The SEO retainer is the immediate play. CH's organic traffic is 53% of total with zero effort. We've already written the plan. Brian (CH's contact) just needs to see the pitch and the numbers.

**Estimated CH expansion:** +$2,449/mo recurring within 60 days.

### 3.3 Delivered Inc (Partnership)

**Status:** Proposal delivered. Waiting on second meeting. License expires 3/5/2026.

**Closing automation:**
1. Send license renewal reminder email (urgent — it's 21 days away)
2. Include: "We can help with compliance prep right now, free of charge"
3. This creates goodwill + urgency. If they miss renewal, the entire deal dies.
4. Attach a 1-page "what you're leaving on the table" summary with GLASS market data showing the delivery market opportunity

**If deal closes (Option A):**
- $5,000 upfront (immediate)
- 8–12% equity (long-term)
- 5% rev share above $75K/mo (months 6+)
- $0 retainer for 6 months

**Supporting automation:**
- Programmatic SEO pages for every town Delivered serves (SIGNAL builds these)
- Hack cleanup (immediate goodwill gesture)
- GLASS integration: "Toggle delivery ON/OFF" for zip codes

**Estimated Delivered revenue (Year 1):** $5,000 upfront + equity position. Revenue share kicks in ~Month 6.

### 3.4 HOP (House of Pride)

**Status:** GTM strategy needed, website copy needed, labels blocked on Randy.

**Quick wins:**
- SIGNAL generates website copy from brand brief
- GLASS data informs market positioning (edibles pricing, competitor landscape)
- Once labels finalized → SIGNAL generates product pages

**Revenue:** GTM retainer $2,500/mo after launch.

---

## 4. Product Growth Automation

### 4.1 GLASS Growth Engine

#### Auto-Invite Operators (The Trojan Horse)

This is the single most important growth automation:

```
TRIGGER: New dispensary scraped by GLASS (or existing dispensary with no user account)

STEP 1: Query CCC license database for owner/operator name and email
STEP 2: Generate personalized margin snapshot:
  - Their average price vs. market average (by category)
  - Number of products we're tracking for them
  - One insight: "Your flower prices are X% above/below the East Boston average"
STEP 3: Send email via Resend:
  Subject: "We're tracking {dispensary_name}'s prices vs. 500 MA dispensaries"
  Body: Margin snapshot + "Claim your free GLASS dashboard"
STEP 4: If they sign up → auto-provision dashboard (Clerk + backend already built)
STEP 5: Day 3 follow-up: "3 things that changed in your market this week"
STEP 6: Day 7: "Your competitors changed prices — see what happened" (only if true)
STEP 7: Day 14: Trial expiry warning with conversion CTA

RESULT: Every dispensary in MA gets a personalized, data-rich invitation
that proves our value before they spend a dollar.
```

**Why this works:** It's not a "lead magnet." It's their own data. Every operator cares about their competitive position. We already have the data. We're just showing it to them.

#### CCC ↔ GLASS Cross-Reference (Unique Data Moat)

From MEMORY.md: "CCC official avg price $8.19/g vs GLASS scraped $11.13/g = 36% markup."

**Nobody else has this cross-reference.** CCC publishes wholesale/reported averages. GLASS scrapes actual shelf prices. The gap between them is the story every operator and journalist wants.

**Automation:**
- Weekly calculation: CCC reported avg vs. GLASS actual avg, by category
- Auto-publish to /market page
- Auto-include in newsletter as "The Markup Index"
- This becomes a citable metric that earns backlinks

#### GLASS Dashboard Stickiness Automation

```
DAILY (6 AM):
  - Morning Brief email to all subscribed operators
  - "3 things that matter today": competitor price changes, new threats, margin opportunities
  - 1 personalized recommendation from Margin Engine

WEEKLY:
  - Full competitive report (top 10 price movers in 5-mile radius)
  - New dispensary openings/closings
  - Regulatory changes affecting them

MONTHLY:
  - "Your month in review": price position trend, market share estimate, opportunities missed
  - Upsell prompt for Pro tier if on Operator tier
```

### 4.2 Newsletter Growth Automation

**Full zero-touch pipeline:**

```
CRON: Every Monday 4 AM EST

STEP 1: GLASS data processor runs
  - Pull latest prices, top movers, category trends from GLASS DB
  - Generate Price Wire section (automated)
  - Generate Threat Radar section (CCC data, automated)
  - Generate Brand Movers section (product launches, automated)

STEP 2: Newsletter scrapers run
  - Brave Search → top 5 MA cannabis news stories
  - Reddit → top 3 operator-relevant posts
  - CCC → regulatory updates

STEP 3: Composer assembles sections
  - Apply editorial voice from BRANDING.md
  - Insert THE NUMBER (rotating metric from GLASS)
  - Add Margin Tip (rotating library)
  - Add Compliance Reminder (rotating library)

STEP 4: Validation gate
  - Check all links are live (HTTP 200)
  - Check no duplicate content from prior issues
  - Check source credibility (filter dontlegalizedrugs.com etc.)
  - Check no past events listed as upcoming

STEP 5: Quality gate
  - Readability score check
  - MA-relevance score (all content must be MA-specific)
  - Data accuracy spot check (price numbers match GLASS DB)

STEP 6: Beehiiv API → create draft
  - If quality passed: auto-schedule for Tuesday 6 AM
  - If quality failed: flag for manual review, notify COO

STEP 7: Post-send tracking
  - Log open rate, click rate
  - Auto-segment: engaged vs. unengaged
  - Trigger GLASS invite for highly engaged readers who aren't GLASS users
```

### 4.3 SIGNAL SEO Automation

**Automated content pipeline per client:**

```
WEEKLY SCHEDULE (per tenant):

MONDAY: 4 blog posts generated
  - 2 × "data-driven" posts using GLASS data (e.g., "Best Edible Prices in East Boston This Week")
  - 1 × "educational" post (strain guides, dosing guides)
  - 1 × "local" post (events, news, community)

TUESDAY: Location pages updated
  - Refresh all location page data (prices, product counts, hours) from GLASS
  - If new towns added to coverage → generate new pages automatically

WEDNESDAY: Product pages generated
  - New products found in GLASS → auto-generate SEO product pages
  - Existing product pages → update prices

THURSDAY: GitHub PRs created
  - All content batched into single PR per client
  - Auto-merge if quality gate passes (or flag for review)

FRIDAY: Performance monitoring
  - Pull GSC data for all client pages
  - Flag any page losing rank (>5 position drop)
  - Generate weekly performance email to client

ZERO TOUCH AFTER SETUP. Randy reviews PRs only if flagged.
```

### 4.4 Cue — AI Commerce Platform

**MVP positioning (from memory):** Cue is a full AI commerce platform (demand forecasting, inventory optimization, brand incentives). NOT just a virtual budtender.

**Pre-sell strategy:**
1. Build a landing page on roviqai.xyz/cue with the ecosystem vision
2. "Join the waitlist — founding operators get 50% off Year 1"
3. Use GLASS operators as the funnel: "You've been using GLASS. Cue takes it further."
4. Waitlist = email list = warm leads when MVP ships

**MVP scope (smallest thing that gets revenue):**
- Virtual Budtender widget (embeds on any dispensary site)
- Uses GLASS product data to answer customer questions
- "What's a good strain for sleep?" → recommends from their menu
- Pricing: $99/mo per location
- Build time: 2–3 weeks (ChatGPT/Claude API + GLASS data + embeddable widget)

**Revenue projection:** 10 locations × $99/mo = **$990/mo** within 90 days of launch.

---

## 5. Sales Automation — Randy Never Cold Calls

### 5.1 Value-First Outreach Sequences

**Principle:** Never ask for money first. Always give value first. The sale happens because they realize they need more of what you already gave them for free.

#### Sequence 1: "Your Market Position" (For Any MA Dispensary)

```
EMAIL 1 (Day 0): Subject: "Your pricing vs. 500 MA dispensaries"
  Body: Personalized margin snapshot generated from GLASS data
  CTA: "See your full competitive dashboard (free for 14 days)"
  [NO ASK — pure value]

EMAIL 2 (Day 3): Subject: "3 price changes near {dispensary_name} this week"
  Body: Specific competitor moves within 5 miles
  CTA: "Get these alerts automatically with GLASS"
  [SOFT ASK — free trial]

EMAIL 3 (Day 7): Subject: "Your competitors' most popular products"
  Body: Top-selling categories in their region from GLASS data
  CTA: "See the full product intelligence report"
  [MEDIUM ASK — subscribe to GLASS]

EMAIL 4 (Day 14): Subject: "How {similar_dispensary} increased margins by 8%"
  Body: Case study / anonymized data story from GLASS
  CTA: "Want us to do this analysis for your store? Schedule a 15-min call"
  [AGENCY ASK — only after 3 value touches]
```

**Automation:** GLASS data → template engine → Resend API → track opens → trigger next email based on engagement.

#### Sequence 2: "Your Competitor Intelligence" (For Existing Newsletter Subscribers)

```
Trigger: Subscriber has opened 3+ newsletters

EMAIL 1: "Here's your personalized weekly competitor briefing (free sample)"
  - Attached: PDF with 5-mile competitive analysis from GLASS
  - CTA: "Get this every week with GLASS Operator ($199/mo)"

If they don't convert in 14 days:

EMAIL 2: "Your market is shifting — here's what we see"
  - 3 specific changes that affect their business
  - CTA: "Let us build your growth strategy (free 30-min call)"

If they book a call → they're a warm agency lead.
```

### 5.2 Automated Margin Snapshots

**The most powerful sales tool in the ecosystem:**

A margin snapshot is a 1-page analysis of a specific dispensary's pricing vs. the market. Generated 100% automatically from GLASS data.

```
MARGIN SNAPSHOT — {Dispensary Name}
Generated: {date}

YOUR PRICING POSITION:
  Flower avg: $XX/g (Market avg: $YY/g — you're Z% above/below)
  Edibles avg: $XX/ea (Market avg: $YY/ea)
  Vapes avg: $XX (Market avg: $YY)

COMPETITIVE LANDSCAPE (5-mile radius):
  {N} dispensaries tracked
  Cheapest flower: {competitor} at $XX/g
  Your position: #{rank} of {N}

TOP OPPORTUNITY:
  "{Product category} is priced {X}% above your local average.
   Adjusting could capture an estimated {Y} additional units/week."

THREATS:
  {N} new license applications pending within 5 miles
  {Competitor} dropped prices by {Z}% last week

Powered by GLASS — Massachusetts Cannabis Intelligence
Claim your free dashboard: glass.roviq.com
```

**Distribution automation:**
1. Generate for every dispensary in GLASS database (500+)
2. Email to operator with personalized subject line
3. Track who opens → they're interested → follow up
4. Track who clicks "claim dashboard" → they're hot → nurture

### 5.3 "Your Competitors Are Doing X" Alerts

**Automated competitive alerts (no human involvement):**

```
TRIGGER: GLASS detects significant competitor activity for a target operator
  - Competitor drops prices >10% on a major category
  - New dispensary opens within 3 miles
  - Competitor adds a new product category
  - Competitor's menu expands significantly (>20 new products)

ACTION:
  1. Generate alert email: "Alert: {Competitor} just dropped flower prices by 15%"
  2. Include context: "Here's what this means for {your_dispensary}"
  3. If recipient is a GLASS user → direct to dashboard
  4. If recipient is NOT a GLASS user → "Get alerts like this automatically with GLASS"
```

**This converts prospects without any sales effort.** The alerts are genuinely useful and prove our data advantage.

### 5.4 Referral Program

**"Operator Refers Operator" Program:**

```
CURRENT GLASS USER refers a new operator who subscribes:
  - Referrer gets: 1 month free on their current plan
  - New user gets: Extended 30-day trial (instead of 14)
  
CURRENT CLIENT refers a new agency client:
  - Referrer gets: $500 credit on next invoice
  - New client gets: Free GLASS Operator subscription for 3 months

AUTOMATION:
  1. Unique referral link per GLASS user (tracked via Clerk metadata)
  2. When referred user signs up → auto-credit referrer
  3. Monthly email to active users: "Know an operator who'd benefit from GLASS?"
```

### 5.5 Partnership Automation

**Cannabis industry partnerships (automated outreach):**

| Partner Type | Value Exchange | Outreach Template |
|-------------|---------------|-------------------|
| **POS companies** (Dutchie, Treez, Flowhub) | They get data-driven content featuring their integrations; we get product data access | "We're tracking 500+ MA dispensaries. Your merchants would benefit from our pricing intelligence. Let's explore an integration." |
| **Cannabis attorneys** | They refer operator clients to us for marketing; we refer to them for compliance | Mutual referral agreement |
| **Cannabis accountants/CPAs** | Same mutual referral | Mutual referral agreement |
| **Cannabis PR firms** | They feature GLASS data in press releases; we get backlinks + credibility | "Use our market data in your next press release — it's the most comprehensive in MA" |
| **Industry associations (MassCann, CCC)** | We provide market data for their reports; they promote GLASS to members | "We'd like to sponsor your next report with real-time market data" |

---

## 6. Bold Plays

### 6.1 The Biggest Untapped Opportunity: GLASS as the Bloomberg Terminal of Cannabis

**Nobody in Massachusetts cannabis has real-time, comprehensive market intelligence.** Not Headset (they focus on national). Not BDSA (they sell to VCs, not operators). Not Leafly or Weedmaps (they're marketplace platforms, not intelligence platforms).

GLASS has:
- Real-time pricing from 500+ dispensaries
- 70K+ product price observations per scrape cycle
- CCC regulatory data cross-referenced with shelf prices
- The 36% markup gap between CCC reported and actual shelf prices

**The Bloomberg play:**
- Position GLASS as "the Bloomberg Terminal for cannabis"
- Tier 1: Operators ($199/mo) — competitive intelligence
- Tier 2: Brands ($499/mo) — distribution intelligence, pricing benchmarks
- Tier 3: Investors/M&A ($999/mo) — market analytics, distress signals, deal flow
- Tier 4: Data licensing ($2,500/mo) — raw data API for research firms, media

**Why brands pay more:** A cannabis brand selling to 50 dispensaries cares about pricing across ALL of them. Their budget is 10x an individual operator's.

**Why investors pay even more:** M&A firms, VCs, and MSOs spend $10K+ on cannabis market reports. GLASS data is more current and comprehensive than anything they can buy today.

**Revenue potential of brand + investor tiers:** 5 brands × $499 + 3 investors × $999 = **$5,492/mo** with zero additional build (same data, different dashboards).

### 6.2 What to Build Next: GLASS API (Data-as-a-Service)

**Don't just build dashboards. Sell the data itself.**

```
GLASS API Pricing:
  /api/v1/prices       → current prices, any dispensary     → $0.01/request
  /api/v1/products     → full product catalog                → $0.01/request
  /api/v1/trends       → historical price trends             → $0.02/request
  /api/v1/competitors  → competitive analysis for a location → $0.05/request
  /api/v1/market       → market aggregates                   → $0.01/request
  
  Or: flat rate $299/mo for 10K requests
```

**Who buys this:**
- Cannabis tech companies building their own tools
- Media companies writing market reports
- Research firms and academics
- POS companies wanting to offer market data to their merchants
- Cannabis holding companies monitoring their portfolio

**Build effort:** API already exists (Fastify backend). Add rate limiting + Stripe billing + API key management. 2–3 day project.

### 6.3 The Fastest Path to $10K MRR

Here's the exact math:

```
Revenue Source                                    MRR
─────────────────────────────────────────────────────
CH SEO retainer (SIGNAL)                      $1,500
AC SEO retainer (SIGNAL)                      $1,500
AC Toll Processing (3 conversions × rev share)   $500 (est.)
GLASS Operator subscriptions (15 × $199)      $2,985
GLASS Pro subscriptions (3 × $399)            $1,197
Newsletter sponsorships (2 × $500)            $1,000
GLASS Market Reports (10 × $99)                 $990
Cue Virtual Budtender (5 × $99)                 $495
─────────────────────────────────────────────────────
TOTAL                                         $10,167
```

**Every single line item above uses tools that already exist.** No new product development required. The gap is:
1. Connecting Beehiiv (newsletter → audience)
2. Connecting Stripe (GLASS → payment)
3. Setting up auto-invite emails (GLASS → operators)
4. Pitching CH and AC on SEO retainers (Randy conversations)
5. Building Cue MVP (2–3 week project)

### 6.4 Competitor Weaknesses to Exploit

| Competitor | Their Weakness | Our Exploitation |
|-----------|---------------|------------------|
| **Headset** | National focus, expensive ($thousands/mo), no MA-specific depth | GLASS is MA-specific, 10x cheaper, more granular |
| **BDSA** | Sells to VCs/MSOs, doesn't serve individual operators | GLASS serves the operator directly |
| **Leafly/Weedmaps** | They're marketplaces, not intelligence platforms. No competitive analysis. | GLASS is purpose-built for operator intelligence |
| **Dutchie** | POS company. They have the data but don't sell intelligence. | We scrape their data and add the intelligence layer they won't build |
| **BOUTIQ** (CH's competitor) | SEO-strong but no data intelligence. Generic content. | SIGNAL generates data-driven content BOUTIQ can't match because they don't have GLASS |
| **Cannabis marketing agencies** | Manual work, no proprietary data, can't scale | AI-first + GLASS data = 10x output at 1/3 the price |

### 6.5 The "Midnight Play": Stealth Data Dominance

**Right now, while everyone sleeps, GLASS is scraping.**

Every hour that passes, GLASS accumulates more historical price data. By Month 6, we'll have 6 months of daily pricing for 500+ dispensaries. Nobody else will have this. It's our moat. The data compounds.

**Specific plays only historical data enables:**
- Seasonal pricing models (4/20 price drops, holiday premiums)
- Brand velocity tracking (which brands are gaining/losing shelf space)
- Price elasticity modeling (when competitors drop prices, what happens to their neighbors?)
- Distress detection (consistent price drops = struggling operator = M&A target)
- Market predictions (ML models trained on 6 months of data)

**By Month 12:** 365 days × 500 dispensaries × ~300 products = 55M+ price data points. This dataset alone is worth millions to the right buyer.

---

## 7. 30/60/90 Day Action Plan

### Days 1–30: "Wire It Up"

**Goal:** Go from $0 automated revenue to first dollars flowing. Connect existing tools into revenue loops.

| Week | Action | Owner | Revenue Impact |
|------|--------|-------|----------------|
| **1** | Randy approves AC toll processing email blast | Randy | $2,250+ one-time |
| **1** | Connect newsletter pipeline to Beehiiv API (need form ID) | COO + dev subagent | Indirect (audience building) |
| **1** | Fix newsletter validation gate + events scraper | Dev subagent | Newsletter quality → retention |
| **1** | Send Delivered license renewal reminder + compliance help offer | Randy (email) | Goodwill → deal progression |
| **1** | Set up Stripe account + connect to GLASS for subscriptions | Randy (Stripe) + dev subagent | Enables $199/mo revenue |
| **2** | Launch GLASS auto-invite emails to first 50 operators | COO + dev subagent | 5–10 free signups → conversions |
| **2** | Pitch CH on $1,500/mo SEO retainer (plan already written) | Randy (15-min call with Brian) | $1,500/mo MRR |
| **2** | Deploy GLASS /market page (public) with newsletter signup | Dev subagent | SEO traffic + email capture |
| **2** | Generate first batch of CH blog posts via SIGNAL | Dev subagent | SEO rankings start climbing |
| **3** | First automated newsletter sent via Beehiiv | Automated | Audience growth |
| **3** | Begin LinkedIn connection automation (5/day) via CamoFox | COO | 150 connections/month pipeline |
| **3** | Auto-generate margin snapshots for top 50 operators | Dev subagent | Outreach ammunition |
| **3** | Pitch AC on SEO retainer + competitive pricing reports | Randy (conversation with Debbie/Clarice) | $1,750/mo MRR |
| **4** | Review first month metrics: emails sent, opens, signups, revenue | COO | Course correction |
| **4** | Launch GLASS free trial (14-day) for all auto-invited operators | Automated | Conversion pipeline begins |
| **4** | First newsletter sponsorship outreach to cannabis brands | COO + email automation | $500+/mo pipeline |

**Day 30 target: $5,000+ MRR** (CH retainer + AC retainer + first GLASS subscribers + toll processing conversions)

### Days 31–60: "Scale the Loops"

**Goal:** Scale what's working. Add brand/investor tiers to GLASS. Close Delivered deal. Hit $10K MRR.

| Week | Action | Owner | Revenue Impact |
|------|--------|-------|----------------|
| **5** | Launch GLASS Brand tier ($499/mo) — target 3 cannabis brands | COO + outreach automation | $1,497/mo MRR |
| **5** | Automated competitor reports live for CH + AC | Dev subagent | Client retention + upsell |
| **5** | Newsletter hits 200+ subscribers → first sponsor outreach | COO | $500/mo pipeline |
| **6** | Delivered deal: second meeting (Randy + founders) | Randy | $5K upfront + equity |
| **6** | SIGNAL generates first 30 location pages for CH | Dev subagent (auto) | SEO compound effect |
| **6** | Begin Cue MVP development (Virtual Budtender widget) | Dev subagent | $990/mo in 90 days |
| **7** | GLASS auto-invite wave 2: next 100 operators | Automated | 10–20 new free signups |
| **7** | Launch GLASS market reports ($99/mo subscription) | Dev subagent | $990/mo pipeline |
| **7** | Google Maps scrape all 650 MA dispensaries → master prospect DB | CamoFox automation | Complete market coverage |
| **8** | Second client for SIGNAL SEO (AC or new lead from GLASS) | Randy (warm lead) | $1,500/mo MRR |
| **8** | Referral program launches for GLASS users | Dev subagent | Organic growth |

**Day 60 target: $10,000+ MRR** (2 SEO clients + 20 GLASS subscribers + sponsors + reports + toll processing ongoing)

### Days 61–90: "Compound and Expand"

**Goal:** Establish GLASS as the MA standard. Productize SIGNAL for self-serve. Prepare for scale.

| Week | Action | Owner | Revenue Impact |
|------|--------|-------|----------------|
| **9** | Launch GLASS Investor tier ($999/mo) — target 2 firms | COO + outreach | $1,998/mo MRR |
| **9** | Cue Virtual Budtender MVP ships → first 5 installs | Dev subagent | $495/mo MRR |
| **9** | Newsletter at 500+ subscribers → premium sponsor rates | Automated growth | $1,000/mo sponsors |
| **10** | GLASS API (Data-as-a-Service) soft launch | Dev subagent | $299/mo per API customer |
| **10** | SIGNAL self-serve dashboard prototype | Dev subagent | Prep for $500/mo SaaS tier |
| **10** | Third SEO client (from GLASS funnel or referral) | Inbound | $1,500/mo MRR |
| **11** | Partnership outreach: POS companies, attorneys, CPAs | COO + automation | Referral pipeline |
| **11** | Begin CT/RI market expansion planning (GLASS + SIGNAL) | COO | Multi-state revenue |
| **12** | Full ecosystem review: what's working, what's not | COO + Randy | Strategic planning |
| **12** | Prepare investor materials if needed (GLASS data makes the pitch) | COO | Optionality |

**Day 90 target: $25,000+ MRR** (4 SEO clients + 40 GLASS subscribers across tiers + sponsors + reports + Cue + API + toll processing)

---

## 8. Revenue Projections Summary

### Conservative Scenario

| Revenue Stream | Day 30 | Day 60 | Day 90 |
|---------------|--------|--------|--------|
| SIGNAL SEO Retainers (clients) | $1,500 | $3,000 | $4,500 |
| GLASS Operator ($199/mo) | $995 | $2,985 | $4,975 |
| GLASS Pro ($399/mo) | $0 | $798 | $1,596 |
| GLASS Brand ($499/mo) | $0 | $499 | $1,497 |
| GLASS Investor ($999/mo) | $0 | $0 | $999 |
| AC Toll Processing (ongoing) | $500 | $750 | $1,000 |
| Newsletter Sponsorships | $0 | $500 | $1,000 |
| Market Reports ($99/mo) | $0 | $495 | $990 |
| Cue Virtual Budtender ($99/mo) | $0 | $0 | $495 |
| GLASS API | $0 | $0 | $299 |
| **TOTAL MRR** | **$2,995** | **$9,027** | **$17,351** |

### Base Scenario (Execution on Track)

| Revenue Stream | Day 30 | Day 60 | Day 90 |
|---------------|--------|--------|--------|
| SIGNAL SEO Retainers | $1,500 | $4,500 | $7,500 |
| GLASS Operator | $1,592 | $3,980 | $6,965 |
| GLASS Pro | $399 | $1,596 | $2,793 |
| GLASS Brand | $0 | $1,497 | $2,994 |
| GLASS Investor | $0 | $999 | $1,998 |
| AC Toll Processing | $750 | $1,000 | $1,500 |
| Newsletter Sponsorships | $0 | $1,000 | $2,000 |
| Market Reports | $297 | $990 | $1,485 |
| Cue Virtual Budtender | $0 | $0 | $990 |
| GLASS API | $0 | $0 | $598 |
| **TOTAL MRR** | **$4,538** | **$15,562** | **$28,823** |

### Key Assumptions

- GLASS auto-invite emails convert at 2% signup rate, 20% of signups convert to paid
- Newsletter grows 50 subscribers/week after launch
- SEO retainer clients found from existing relationships (CH, AC) + GLASS funnel
- Toll processing converts 3–5 of 85 emailed prospects
- Brand/investor tiers require active outreach (not automated — COO manages)
- Cue ships by Day 75

---

## 9. Technical Dependencies & Blockers

### Must Happen This Week (Randy)

| # | Blocker | Who | Impact if Delayed |
|---|---------|-----|-------------------|
| 1 | Approve AC toll processing email blast | Randy | $2,250+ delayed per week |
| 2 | Provide Beehiiv form ID for API integration | Randy | Newsletter can't auto-send |
| 3 | Verify `roviqai.xyz` on Resend (or approve `spacemanwins.win` for outreach) | Randy | All email automation blocked |
| 4 | Set up Stripe account for GLASS subscriptions | Randy | Can't charge for GLASS |
| 5 | Schedule Delivered second meeting | Randy | License expires 3/5, deal at risk |
| 6 | Cloudflare nameserver setup (Namecheap → Cloudflare) | Randy | Email deliverability issues |

### Must Happen This Week (Dev)

| # | Task | Effort | Impact |
|---|------|--------|--------|
| 1 | Connect newsletter pipeline → Beehiiv API | 4 hours | Newsletter goes live |
| 2 | Fix newsletter events scraper (returns news as events) | 2 hours | Newsletter quality |
| 3 | Add GLASS Price Wire section to newsletter | 4 hours | Killer differentiator |
| 4 | Set newsletter validation gate to blocking | 1 hour | Quality assurance |
| 5 | Build auto-invite email generator from GLASS data | 8 hours | Operator acquisition |
| 6 | Add Stripe checkout to GLASS dashboard | 8 hours | Revenue collection |
| 7 | Push GLASS submodule changes (8 commits pending) | 30 min | Unblock further work |

---

## 10. Operating Principles

1. **Revenue before features.** Don't build the next cool thing until the current thing is making money.
2. **Automate the boring stuff.** Every manual process that runs weekly should be automated within 2 weeks of discovery.
3. **Data is the moat.** Every day GLASS runs, the historical dataset becomes more valuable. Protect scraping uptime above all.
4. **Never cold call.** Every outreach starts with value delivered. The margin snapshot is the handshake.
5. **Ecosystem > products.** Don't sell GLASS or SIGNAL alone. Sell the ecosystem: intelligence → content → commerce.
6. **Randy builds, COO operates.** Randy's time is best spent on product and creative. Everything else should be automated or delegated.
7. **Compound, don't scatter.** 3 revenue streams at $5K/mo beats 10 revenue streams at $500/mo. Focus.

---

*This document is a living playbook. Review weekly. Update monthly. Execute daily.*

*Generated: February 12, 2026 | Next review: February 19, 2026*
