# GROWTH PLAYBOOK — Automated Channels with CamoFox

## Objective
Build a repeatable outbound + community engine for MA dispensary operators using:
- **CamoFox browser automation** for research/monitoring/workflow assist
- **GLASS dataset** (500+ MA dispensaries: pricing/menu/location intelligence)
- **Newsletter** (market intelligence)
- **SIGNAL** (SEO content production)
- **Virtual Budtender + Cue** as downstream offers

---

## Priority Ranking (Highest ROI First)
1. **Email Outreach Automation (Channel 5)** — fastest path to meetings + demos with strongest personalization.
2. **Google Maps Review Monitoring (Channel 4)** — high-intent trigger events (negative reviews) create urgency.
3. **LinkedIn Prospecting (Channel 1)** — reliable owner/GM pipeline + relationship building.
4. **X/Twitter Community (Channel 3)** — thought leadership + distribution of GLASS insights.
5. **Reddit Community Engagement (Channel 2)** — trust-based demand capture; slower but high quality.
6. **Industry Event Networking (Channel 6)** — concentrated opportunities; episodic but strong close rates.
7. **Partnership Automation (Channel 7)** — longer cycle, high leverage once partnerships activate.

---

## Shared Automation Architecture (Applies to All Channels)

## Data Layer
- Source of truth table: `dispensaries_ma` (name, URL, social links, contacts, pricing metrics, review metrics).
- Enrichment tables: `linkedin_leads`, `reddit_threads`, `x_accounts`, `events`, `partners`, `outreach_log`.
- Scoring model fields:
  - TAM fit (MA dispensary only)
  - Pricing variance vs market (e.g., +15% above median flower price)
  - Reputation risk (recent 1–2 star reviews)
  - Engagement propensity (active social footprint)

## Orchestration Layer
- Scheduler (daily + weekly jobs)
- CamoFox workers for web flows (search, scrape, snapshot, queue updates)
- LLM template engine for personalization from structured variables only
- Human approval queue before sensitive outbound (LinkedIn DMs, Reddit posts)

## Execution Layer
- Email via Resend API
- CRM-style logging for every touchpoint
- Alerting (Slack/Discord/email) for trigger-based workflows

## Governance Layer
- Rate limits, random delays, manual review flags
- Compliance rules by channel (TOS + CAN-SPAM + platform anti-spam)
- Audit logs of every automated action

---

## Channel 1: LinkedIn Prospecting Automation

### How It Works (Step-by-Step)
1. Build target account list from GLASS (all MA dispensaries, prioritized by revenue potential + pain score).
2. Use CamoFox to assist with LinkedIn search workflows:
   - Query pattern: `"[dispensary name]" AND (Owner OR General Manager OR COO OR Director Operations)`
   - Filter geography: Massachusetts.
3. Capture candidate profiles into `linkedin_leads` with confidence score.
4. Generate personalized connection requests from account variables (no generic spam language).
5. Human approves queued requests in batches.
6. On acceptance, run 3-step follow-up sequence over 10–14 days.
7. Route engaged replies to human AE/founder for real conversation.

### Search Strategies
- Titles: Owner, Co-owner, Founder, General Manager, Operations Manager, Retail Director.
- Company-level search: known MA dispensary brands from GLASS.
- Group strategy: MA cannabis operators, dispensary owners, cannabis retail operations groups.

### What CamoFox Automates vs Human Touch
- **Automate:** lead discovery, profile metadata capture, queue prep, reminder triggers.
- **Human-required:** final send approval, nuanced replies, meeting close.

### Templates
**Connection Request (<=300 chars)**
> Hi {{first_name}} — I track MA dispensary pricing trends and noticed {{company}} is active in {{city}}. I share weekly data on pricing/margin shifts across the state. Open to connecting?

**Follow-up 1 (Day 2–3 after connect)**
> Thanks for connecting, {{first_name}}. We publish MA market snapshots (flower/vape/edible pricing by region). Happy to send your local benchmark if helpful.

**Follow-up 2 (Day 6–8)**
> Quick insight from this week: {{city_or_region}} flower pricing moved {{delta}}% vs prior period. If useful, I can send a 1-page margin snapshot for {{company}}.

**Follow-up 3 (Day 10–14)**
> If helpful, we can also share a free GLASS trial + ideas to improve conversion/review response workflows. Worth a 15-min data walk-through?

### Expected Performance
- Connection accept rate: **18–35%** (with real personalization)
- Reply rate after connect: **10–22%**
- Meeting rate from new connections: **3–8%**

### Time Investment
- Setup: 6–10 hours
- Ongoing: 3–5 hours/week human review + responses

### Revenue Impact
- 20–40 qualified conversations/month possible at scale
- 2–6 new trials/month, depending on offer quality and follow-up discipline

### Risk / Compliance
- LinkedIn TOS risk if fully automated sending at scale.
- Mitigation: human-in-the-loop sends, conservative daily caps, no fake identities, no scraping abuse.

---

## Channel 2: Reddit Community Engagement

### How It Works
1. Monitor target subreddits: `r/bostontrees`, `r/MAcannabis`, `r/weedbiz`, `r/cannabisindustry`.
2. Classify threads by intent:
   - Operator pain (pricing pressure, staffing, menu strategy)
   - Consumer sentiment (quality/price complaints)
   - Regulatory confusion (CCC updates)
3. Draft value-first comments using data snippets from GLASS.
4. Publish from real operator/brand account with non-promotional tone.
5. Weekly “insight post” with visualized, anonymized MA trend data.
6. Soft CTA only when context-fit (free benchmark/tool).

### Content That Builds Authority
- “What we’re seeing in MA pricing this week”
- “Top 3 product categories with fastest price compression”
- “How operators respond to 1-star reviews effectively”
- “CCC update summary + implications for store ops”

### “Free Tool” Post Template
> We built a free MA dispensary pricing benchmark checker using public menu data + market averages. If you run a shop in MA and want your category-level gap report, comment “benchmark” and I’ll DM it.

### Automation vs Manual
- **Automate:** thread discovery, keyword monitoring, draft suggestions, cadence reminders.
- **Manual:** final posting/commenting, community judgment, mod-rule compliance.

### Expected Performance
- Comment response rate: **8–20%**
- DM opt-in rate on useful tool posts: **3–10% of thread viewers**
- Lead conversion from Reddit interactions: **1–4%**

### Time Investment
- Setup: 4–6 hours
- Ongoing: 30–45 min/day

### Revenue Impact
- Mid-funnel trust channel; improves conversion rates in other channels.

### Risk / Compliance
- Subreddit self-promo limits are strict.
- Use 80/20 value-to-promo ratio; always read subreddit rules; avoid astroturf behavior.

---

## Channel 3: X/Twitter Cannabis Community

### How It Works
1. Build list of MA cannabis operators, journalists, regulators, B2B vendors.
2. Daily engagement routine: 15–25 meaningful interactions (reply/quote/retweet with insight).
3. Auto-produce data micro-posts from newsletter + GLASS deltas.
4. Weekly thread: “MA Market Pulse” (prices, promos, review trends, CCC notes).
5. Route profile visitors to newsletter + free benchmark CTA.

### Who to Follow
- MA dispensary operators and brands
- Cannabis retail consultants
- Cannabis business media
- CCC-adjacent policy accounts
- POS/ecommerce ecosystem players (Dutchie, Jane, Treez, Blaze communities)

### Content Templates
**Daily data post**
> MA market pulse: avg flower price in {{region}} moved {{delta}}% WoW. Most aggressive promo category: {{category}}. Operators: want your store’s position vs local market? Reply “snapshot”.

**CCC update post**
> CCC update in plain English: {{summary}}. Practical implication for dispensaries: {{ops_impact}}.

### Automation vs Manual
- **Automate:** content drafting from structured data, schedule queue, monitoring mentions.
- **Manual:** final posting, replies requiring nuance, relationship DMs.

### Expected Performance
- Engagement rate on data posts: **2–6%**
- CTA reply rate (“snapshot”): **0.5–2% of impressions**
- Lead-to-call conversion: **5–12% of inbound replies/DMs**

### Time Investment
- Setup: 5–8 hours
- Ongoing: 45–60 min/day

### Revenue Impact
- Builds consistent inbound; strong amplifier for newsletter and outbound credibility.

### Risk / Compliance
- Avoid aggressive automation of likes/follows at high volume.
- Maintain human voice; avoid repetitive patterns and duplicate content.

---

## Channel 4: Google Maps Review Monitoring

### How It Works
1. Daily scan all 500+ dispensary Google Business Profiles (via allowed APIs or compliant scraping pipeline).
2. Detect new reviews + sentiment classify (1–2 star = urgent trigger).
3. Trigger alert sequence:
   - Internal alert + account card
   - Outreach message: “noticed review risk” with response guidance
4. Generate competitor benchmark:
   - Review velocity
   - Avg rating trend
   - Common complaint themes by region
5. Offer “review response co-pilot” + GLASS market context.

### Alert Outreach Template
Subject: `{{company}} just got a new 1-star review (quick response idea)`

> Hi {{name}},
> Noticed a new 1-star review posted for {{company}} on Google.
> We track MA dispensary review trends and drafted a response framework based on common complaint patterns in your area.
> Want me to send the suggested response + 3 prevention actions?

### Automation vs Manual
- **Automate:** monitoring, sentiment detection, trigger creation, draft response suggestions.
- **Manual:** final outbound approval for high-sensitivity accounts.

### Expected Performance
- Open rates (trigger-based): **45–70%**
- Reply rates: **15–30%**
- Meeting conversion: **8–20%**

### Time Investment
- Setup: 8–12 hours
- Ongoing: 2–4 hours/week

### Revenue Impact
- High intent/problem-aware leads; likely strongest close rates among outbound plays.

### Risk / Compliance
- Ensure data collection method complies with Google terms.
- Avoid language implying invasive surveillance; keep tone helpful, factual, and consent-oriented.

---

## Channel 5: Email Outreach Automation

### How It Works
1. Build “Margin Snapshot” per dispensary from GLASS:
   - Price vs market by category
   - Promo intensity vs peers
   - Potential margin leakage estimate
2. Generate personalized email with 2–3 quantified insights.
3. Send via Resend API with domain warming + throttled cadence.
4. Drip sequence:
   - Email 1: Snapshot
   - Email 2: Newsletter invite
   - Email 3: GLASS free trial
   - Email 4: Virtual Budtender/Cue use case
5. Track opens, clicks, replies, meetings, trials.

### Email Sequence Templates
**Email 1 — Snapshot**
Subject: `{{company}} pricing snapshot vs MA market`

> Hi {{first_name}},
> We analyzed {{company}}’s public menu against MA market pricing.
> 2 highlights:
> - {{category_1}} is ~{{variance_1}}% above local median
> - {{category_2}} promo frequency is {{promo_delta}} vs nearby peers
> If useful, I can send the full 1-page margin snapshot (free).

**Email 2 — Newsletter Invite**
> Sharing this because operators told us weekly MA pricing movement is hard to track manually. We publish a concise MA dispensary market brief every week. Want in?

**Email 3 — GLASS Trial**
> If you want live category benchmarks + competitor price tracking, I can open a free GLASS trial for {{company}}.

**Email 4 — Product Expansion**
> Separate from pricing: we’re helping operators convert more web traffic using Virtual Budtender + Cue. Happy to show a quick example relevant to your menu.

### Automation vs Manual
- **Automate:** data prep, copy draft, sequencing, send scheduling, lead scoring.
- **Manual:** inbox handling for qualified replies, custom enterprise negotiations.

### Expected Performance
- Open rate: **35–55%**
- Reply rate: **6–15%**
- Meeting booked: **3–8%**
- Trial start: **2–6%**

### Time Investment
- Setup: 10–14 hours
- Ongoing: 3–4 hours/week

### Revenue Impact
- Primary direct-response engine; best controllable CAC channel.

### Risk / Compliance
- CAN-SPAM compliance: sender identity, address, unsubscribe.
- Use legitimate interest framing, avoid deceptive subject lines, respect opt-outs immediately.

---

## Channel 6: Industry Event Networking

### How It Works
1. Build event feed (CCC meetings, MassCanna events, regional trade shows).
2. Create event-specific target list (speakers, sponsors, attendees, exhibitors).
3. Pre-event outreach sequence (2 touches):
   - “Are you attending?”
   - “Want a custom MA snapshot before event?”
4. During event: live social engagement + short recap posts.
5. Post-event sequence:
   - “Great meeting” / “sorry we missed each other”
   - Send promised insight asset
   - CTA for 15-min follow-up

### Automation vs Manual
- **Automate:** event discovery, attendee list aggregation, sequence drafting, reminders.
- **Manual:** relationship-heavy outreach, on-site conversations, strategic follow-up.

### Expected Performance
- Positive response pre-event: **12–28%**
- Meeting booked from engaged contacts: **10–25%**

### Time Investment
- Setup: 3–5 hours
- Ongoing: event-dependent (2–6 hours/event)

### Revenue Impact
- High close potential due to context and urgency; less consistent volume.

### Risk / Compliance
- Respect attendee privacy and platform scraping rules.
- No unsolicited bulk messaging on event platforms if prohibited.

---

## Channel 7: Partnership Automation

### How It Works
1. Build partner target map:
   - POS/ecom: Dutchie, Jane, Treez, Blaze ecosystem agencies/apps
   - Cannabis consultants, analytics tools, menu syndicators
   - Industry publications/newsletters for guest content
2. Score partners by overlap, distribution reach, integration feasibility.
3. Run co-marketing outreach sequence:
   - Shared audience fit
   - Proposed asset (benchmark report/webinar/case study)
4. Track pipeline stages: contacted → interested → active campaign.

### Outreach Template
Subject: `Co-marketing idea: MA dispensary benchmark report`

> Hi {{name}},
> We track pricing + product trends across 500+ MA dispensaries. I think a co-branded benchmark report for operators in your network could perform well.
> If useful, I can draft an outline with shared lead capture and distribution plan.

### Automation vs Manual
- **Automate:** partner list generation, enrichment, initial draft sequencing, pipeline reminders.
- **Manual:** negotiation, co-branding terms, relationship management.

### Expected Performance
- Positive partner reply: **8–18%**
- Signed co-marketing pilot: **2–8%**

### Time Investment
- Setup: 6–8 hours
- Ongoing: 2–3 hours/week

### Revenue Impact
- Slower start, high upside via leveraged distribution and trust transfer.

### Risk / Compliance
- Clear data-sharing boundaries; avoid sharing sensitive client-specific data without permission.

---

## Tools Needed
- **CamoFox**: browsing automation, discovery, monitoring workflows
- **Resend API**: email sequences + transactional alerts
- **Data store**: Postgres/Airtable/Sheets + CRM fields
- **LLM prompt layer**: structured personalization engine
- **Scheduler**: cron/queue worker system
- **Analytics dashboard**: funnel metrics by channel
- **Optional enrichments**: Clearbit/Apollo/Clay-like enrichment (if compliant)

---

## Metrics to Track (Weekly Dashboard)

### Topline
- New leads added
- Outreach sent
- Replies
- Meetings booked
- Trials started
- Paid conversions
- CAC by channel

### Channel Metrics
- LinkedIn: invite accept %, reply %, meeting %
- Reddit: comment engagement, DM opt-ins, lead captures
- X: impressions, engagement %, CTA responses
- Reviews: negative-review alerts triggered, response rate, meetings
- Email: deliverability, open/click/reply/booked
- Events: pre-event response, event meetings, post-event conversions
- Partnerships: partner meetings, pilots launched, partner-sourced leads

### Quality Metrics
- Personalization score (template variable completeness)
- Bounce/unsubscribe/spam complaint rates
- Human QA pass rate on outgoing messages

---

## 30-Day Launch Plan

### Week 1 — Foundation
- Finalize data schema + lead scoring
- Build baseline templates for LinkedIn/email/review alerts
- Stand up tracking dashboard
- Define compliance guardrails and send limits

### Week 2 — Deploy High-ROI Channels
- Launch Email (snapshot sequence) to first 100–150 targets
- Launch Google Review trigger monitoring for all 500+
- Start LinkedIn lead capture + manual send queue

### Week 3 — Add Community + Content Distribution
- Launch X posting cadence (daily data posts + weekly thread)
- Begin Reddit monitoring + 3–5 value comments/day
- Publish first “free benchmark” CTA asset

### Week 4 — Expand + Optimize
- Launch event pipeline + pre-event sequence
- Start partner outreach to top 20 candidates
- Analyze early funnel metrics and optimize copy/targeting
- Double-down on top 2 channels by meeting-to-trial conversion

---

## Implementation Guardrails
- Keep **human-in-the-loop** for all relationship-critical or high-risk actions.
- Use automation for **research, prep, scoring, scheduling**, not for fake engagement.
- Prioritize **helpful market intelligence** over product pitching.
- Every message should answer: “What specific value does the operator get right now?”

---

## Recommended Initial Capacity Plan
- Daily send capacity (starting safe):
  - Email: 30–50/day
  - LinkedIn connection requests: 10–20/day (human-approved)
  - X engagements: 15–25/day
  - Reddit comments: 3–5/day
- Weekly goal baseline:
  - 15–25 qualified replies
  - 8–15 meetings booked
  - 4–8 GLASS trials started

This playbook should be treated as a living operating document; optimize weekly using conversion data and compliance feedback.
