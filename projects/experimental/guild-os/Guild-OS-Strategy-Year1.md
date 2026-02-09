# Guild OS Strategy Doc (Year 1)

**Date:** February 8, 2026  
**Owner:** Randy / Founding team  
**Thesis:** The social layer is the product. Guild OS wins by becoming the operating system for alliance coordination, reputation, and diplomacy across games.

---

## 1) Executive Summary

Guild OS should launch as a **Discord-native command center** for high-coordination strategy guilds, starting with **Game of Thrones: Conquest (GOTC)** and expanding to Rise of Kingdoms/Lords Mobile after PMF signals.

The Year 1 goal is not just "build software." The goal is to build a **distribution moat**:

- Make Guild OS the default ops stack for top alliances.
- Own the most valuable social data: contribution, reliability, leadership, diplomacy behavior.
- Convert that data into a portable reputation graph players carry across games.

### Year 1 success target (aggressive but achievable)

- **1,500 guilds created**
- **250,000 registered players**
- **75,000 MAU**
- **12,000 WAU guild leaders/officers**
- **5%+ paid guild conversion** by month 12
- **<$2 blended CAC per activated user** (mostly organic/community channels)

---

## 2) The Opportunity (Why Now)

Guild OS sits at the intersection of 3 validated trends:

- Large and stable game demand, with global games revenue still growing ([Newzoo 2025](https://newzoo.com/resources/blog/global-games-market-to-hit-189-billion-in-2025)).
- Community infrastructure concentration in Discord, including high gaming MAU and explicit ad/quest products targeting game discovery ([Discord press](https://discord.com/press-releases/discord-launches-newest-ad-format-and-partners-with-appsflyer-gamesight-for-ads-measurement), [Discord Quests](https://discord.com/quests)).
- Proof that habit loops + social gamification scale revenue in adjacent categories ([Duolingo IR](https://investors.duolingo.com/news-releases/news-release-details/duolingo-finishes-2024-51-daus-growth-more-40-million-daus-and), [Roblox IR](https://ir.roblox.com/news/news-details/2025/Roblox-Reports-Fourth-Quarter-and-Full-Year-2024-Financial-Results/)).

Key structural gap: guilds run high-stakes operations on fragmented tools (Discord channels, bots, sheets, docs), and Discord server caps/structure create real operational friction at scale ([Discord server caps](https://support.discord.com/hc/en-us/articles/33694251638295-Discord-Account-Caps-Server-Caps-and-More)).

---

## 3) Product Strategy: What Guild OS Should Look Like

## Product principle

**Do not replace Discord in Year 1.** Overlay and augment it.  
Guild OS should feel like "the war room Discord is missing."

## Core product layers

### Layer A: Command Center (must-have)

- War calendar (rallies, KvK windows, seat timers, migration prep).
- Attendance + RSVP by timezone.
- Role assignment and auto-reminders.
- Event after-action reports.

### Layer B: Contribution Intelligence (must-have)

- Individual and squad contribution scoring.
- Fair-share logic (participation vs rewards).
- Officer dashboard for under-contributors and top performers.
- Exportable reports for leadership councils.

### Layer C: Diplomacy Workspace (must-have for top guilds)

- NAP registry and treaty terms with expiration alerts.
- Relationship map (ally/neutral/enemy/risky).
- Incident log (violations, disputes, resolution outcomes).
- Controlled intel rooms with granular permissions.

### Layer D: Reputation Graph (moat)

- Portable player profile across servers/guilds.
- Verified reliability metrics (attendance, rally completion, donations, tenure).
- Leadership track record (roles held, conflict outcomes, retention impact).
- Anti-gaming signals (suspicious behavior, low-confidence scoring flags).

### Layer E: AI Officer Copilot (differentiator)

- Event planning assistant from historical guild patterns.
- Suggested comp/formation checklists (meta-aware, game-specific).
- Diplomacy draft assistant (NAP language, escalation templates).
- "What changed" summaries after wars and migrations.

---

## 4) MVP Scope (First 90 Days)

## Must ship

- Discord OAuth + guild onboarding wizard.
- Event calendar + RSVP + timezone support.
- Participation tracking and contribution dashboard.
- Officer roles/permissions.
- Basic reputation score v0 (single-game).
- Weekly digest for leaders (email + Discord webhook).

## Should ship if velocity allows

- NAP tracker v0.
- AI after-action summary.
- Role recommendations for events.

## Do not ship in MVP

- Full in-app chat replacement.
- Complex economy/token systems.
- Multi-game rating before single-game PMF.

---

## 5) Target Audience (ICP and Persona Breakdown)

## ICP Tier 1 (beachhead)

- Competitive GOTC allegiances with 60-100 members.
- Existing officer structure (R5 + active R4 bench).
- Already uses bots/spreadsheets/manual tracking.
- Pain level high enough to adopt quickly.

## ICP Tier 2 (expansion)

- Midcore alliances 30-80 members trying to become competitive.
- Pain: organization and free-rider issues.
- Needs simpler onboarding and templates.

## ICP Tier 3 (later)

- Multi-game gaming communities and creator-led guild networks.
- Needs cross-game identity and shared reputation.

## Buying committee inside each guild

- **Economic buyer:** R5/leader.
- **Champion:** R4 ops officer.
- **Power users:** war leads/event coordinators/recruiters.
- **End users:** all members.

## Core persona jobs-to-be-done

- "Help me coordinate 100 people across timezones without chaos."
- "Help me identify reliable players and remove free-rider conflict."
- "Help me run diplomacy with less drama and better records."
- "Help me recruit better because I can verify reputation fast."

---

## 6) Positioning and Message Stack

## Category position

**Guild OS = Alliance Operations Platform** (not "another bot," not "another Discord server tool")

## Primary promise

"Run your alliance like an elite team, not a messy group chat."

## Proof points

- Faster rally coordination.
- Clear contribution fairness.
- Better officer visibility.
- Better retention for strong contributors.

## Messaging hierarchy

- Level 1: Save officer time.
- Level 2: Win more coordinated events.
- Level 3: Build portable reputation and long-term guild advantage.

---

## 7) GTM Strategy (Year 1)

## Go-to-market model

**PLG + Community-led growth + Founder-led guild sales.**

### Motion 1: Discord-native distribution

- Launch official Discord bot + webhook integration.
- Trigger product moments inside existing alliance workflows.
- Push weekly "Guild Readiness Score" reports into Discord channels.

### Motion 2: Officer-first sales

- Founder/rev lead closes top guilds manually in DMs and calls.
- Offer concierge onboarding for top 100 target guilds.
- Convert officer pain into visible wins within 7 days.

### Motion 3: Reputation-led network effects

- Allow players to claim portable profile early.
- Make profile links useful for recruiting and alliance transfers.
- Create referral incentives for bringing entire allied guild clusters.

### Motion 4: Strategic game expansion

- Start GOTC.
- Expand to Rise of Kingdoms once 3 PMF gates are met:
  - NPS >= 40 among officers.
  - 30-day guild retention >= 55%.
  - 5%+ paid conversion in beachhead segment.

---

## 8) Pricing and Monetization (Year 1)

## Packaging

### Free

- Up to 40 members tracked.
- Basic event calendar.
- Basic contribution dashboard.
- Limited history window.

### Pro Guild ($19-$39/month)

- Full member limits.
- Advanced analytics and reports.
- Officer workflows and automation.
- Reputation profile enhancements.

### Elite Guild ($99-$199/month)

- Diplomacy workspace.
- AI officer copilot.
- Multi-server federation and advanced permissions.
- Priority support + migration/onboarding concierge.

## Add-ons

- AI credits for advanced strategy analysis.
- Premium recruiting intelligence exports.

## Pricing principle

Charge at the guild level first. Avoid per-seat in Year 1.

---

## 9) Guerrilla Growth Plan (Massive Year 1 User Acquisition)

## Growth objective

Create compounding loops where every onboarded guild produces 2-3 additional guild opportunities.

## Guerrilla tactic stack (high impact, low paid spend)

### 1) "War Room Makeover" campaign

- Offer free 7-day operations overhaul for top alliances.
- Before/after metrics published as case studies.
- Deliverable includes event cadence, role structure, dashboard setup.

### 2) "Officer Burnout Rescue" offer

- Position product as time-saver for R4/R5 leadership burnout.
- Promise: save X hours/week in coordination overhead.

### 3) Shadow leaderboard drop

- Publish public cross-guild leaderboard (coordination score, attendance health).
- Rankings trigger rivalry and social sharing.

### 4) Migration season playbooks

- Release tactical kits during migration windows.
- Embed Guild OS templates for intake, screening, and diplomacy tracking.

### 5) Rival guild challenge

- Invite two rival guilds into measured "Ops Efficiency Showdown."
- Publicly compare event readiness and participation consistency.

### 6) Alliance intelligence brief

- Weekly "State of the Kingdom" email + Discord digest.
- Includes macro trends, event windows, and anonymized benchmarks.

### 7) Memetic content factory

- Short-form clips/memes around alliance drama truths.
- CTA always points to officer toolkit and scorecard.

### 8) "Recruit Like a Pro" pack

- Free templates for interviews, trial periods, score rubrics.
- Gate download behind Discord install + profile claim.

### 9) Founder office hours

- Weekly tactical sessions for officers.
- Use sessions to identify product friction and convert attendees.

### 10) Creator/strategist ambassador program

- Partner with respected war leads and Discord mods.
- Reward by referred activated guilds, not impressions.

### 11) Tactical teardown content

- Analyze public war outcomes and ops mistakes (respectfully anonymized where needed).
- Educates the market while proving product expertise.

### 12) Guild cluster referrals

- Incentivize onboarding entire ally coalitions (3+ guild packs).
- Give coalition-level insights as unique value.

## Channel priority (Year 1)

- Discord communities (primary).
- YouTube/TikTok strategy creators.
- Reddit game communities.
- Niche podcasts and alliance leader circles.
- Direct officer DMs.

## Paid spend policy

- Paid acquisition only for retargeting and high-intent lookalikes after month 4.
- Cap paid spend to <=25% of new activations in Year 1.

---

## 10) Growth Loops and Funnel Design

## Loop A: Officer utility loop

- Officer installs Guild OS.
- Gains immediate event coordination value.
- Invites officers/members.
- Participation data improves dashboards.
- Dashboards increase officer dependence.

## Loop B: Reputation loop

- Players claim profiles.
- Profiles used in recruiting/transfers.
- More guilds request profile compatibility.
- More players adopt to stay competitive.

## Loop C: Rivalry loop

- Public metrics trigger competition.
- Rival guilds onboard to compare performance.
- Comparative content draws more guild leads.

## Funnel metrics target by month 12

- Visitor to guild install: 12%
- Guild install to activation (first event tracked): 55%
- Activated guild to 30-day retained: 60%
- Retained guild to paid: 5-8%

---

## 11) Year 1 Operating Plan (Quarter-by-Quarter)

## Q1 (Months 1-3): Wedge + PMF Discovery

- Ship MVP.
- Recruit first 50 design-partner guilds (GOTC).
- Run concierge onboarding on every partner guild.
- Target: 5,000 registered users, 1,500 MAU.

## Q2 (Months 4-6): Repeatability + Core Loop Strength

- Harden onboarding and role templates.
- Launch public leaderboard and weekly intelligence brief.
- Add pricing and paid conversion paths.
- Target: 25,000 registered users, 8,000 MAU, 150 paid guilds.

## Q3 (Months 7-9): Scale + Cross-Guild Expansion

- Launch diplomacy workspace v1 and reputation profile v1.
- Expand referral mechanics to guild clusters.
- Pilot second game adapter if PMF gates are met.
- Target: 90,000 registered users, 30,000 MAU.

## Q4 (Months 10-12): Moat + Multi-game Footprint

- Launch cross-game profile and recruiting mode.
- Roll out AI officer copilot for Elite tier.
- Expand ambassador network and partner channels.
- Target: 250,000 registered users, 75,000 MAU, 700+ paid guilds.

---

## 12) Team and Resource Plan

## Core team (lean)

- 1 Product lead/founder.
- 2 full-stack engineers.
- 1 data/ML engineer.
- 1 community/GTM operator.
- 1 part-time content producer.

## Budget envelope (lean)

- Product and infra: $180k-$320k
- Community/GTM and creator bounties: $80k-$180k
- Ops/tools/legal: $40k-$100k
- Total Year 1: **$300k-$600k**

---

## 13) Risks and Mitigations

## Risk: Discord platform dependency

- Mitigation: Build exportable identity and data portability from day one.

## Risk: Reputation abuse/gaming

- Mitigation: Confidence scoring, anomaly detection, and officer verification workflows.

## Risk: Low willingness to pay

- Mitigation: Quantify time saved and event win-rate lift; keep free tier useful but constrained.

## Risk: Expansion too early

- Mitigation: Enforce PMF gates before second-game scaling.

## Risk: Community trust failure

- Mitigation: Transparent moderation policy and clear privacy controls.

---

## 14) KPI Dashboard (What to Track Weekly)

- New guild installs
- Activated guilds (first event tracked)
- WAU/MAU (guild leaders + members)
- 7-day and 30-day guild retention
- Average officer actions per week
- Average events coordinated per active guild
- Referral-driven installs (%)
- Paid conversion and MRR
- Churn by guild tier
- NPS (officer segment)

---

## 15) 90-Day Action Plan (Immediate Execution)

## Week 1-2

- Finalize messaging and landing page.
- Build target list of 200 high-value GOTC guilds.
- Start officer interviews and concierge outreach.

## Week 3-6

- Ship MVP alpha with 15-20 guilds.
- Instrument activation and retention analytics.
- Publish first 3 case studies.

## Week 7-10

- Roll into closed beta for 50+ guilds.
- Launch leaderboard and weekly guild brief.
- Activate ambassador pipeline.

## Week 11-13

- Launch paid tiers for pilot cohort.
- Optimize onboarding flows from observed friction.
- Decide go/no-go for expansion prep.

---

## 16) Decision Gates for "Build the Game Next"

Only begin own game build when all are true for 2 consecutive quarters:

- 75,000+ MAU
- 1,000+ retained guilds
- Net revenue retention >= 110% (guild cohorts)
- Clear evidence that reputation graph drives defensible retention

If gates are met, Guild OS becomes the distribution and social substrate for the future AI-native strategy game.

---

## Appendix: Market Signals Used

- Newzoo global games market trend update (2025): [https://newzoo.com/resources/blog/global-games-market-to-hit-189-billion-in-2025](https://newzoo.com/resources/blog/global-games-market-to-hit-189-billion-in-2025)
- Discord account/server caps (official support): [https://support.discord.com/hc/en-us/articles/33694251638295-Discord-Account-Caps-Server-Caps-and-More](https://support.discord.com/hc/en-us/articles/33694251638295-Discord-Account-Caps-Server-Caps-and-More)
- Discord ads and MAU context (official press): [https://discord.com/press-releases/discord-launches-newest-ad-format-and-partners-with-appsflyer-gamesight-for-ads-measurement](https://discord.com/press-releases/discord-launches-newest-ad-format-and-partners-with-appsflyer-gamesight-for-ads-measurement)
- Discord Quests product page: [https://discord.com/quests](https://discord.com/quests)
- Duolingo growth and monetization signals (IR): [https://investors.duolingo.com/news-releases/news-release-details/duolingo-finishes-2024-51-daus-growth-more-40-million-daus-and](https://investors.duolingo.com/news-releases/news-release-details/duolingo-finishes-2024-51-daus-growth-more-40-million-daus-and)
- Roblox platform economics reference (IR): [https://ir.roblox.com/news/news-details/2025/Roblox-Reports-Fourth-Quarter-and-Full-Year-2024-Financial-Results/](https://ir.roblox.com/news/news-details/2025/Roblox-Reports-Fourth-Quarter-and-Full-Year-2024-Financial-Results/)

