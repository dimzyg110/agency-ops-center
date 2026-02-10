# DECODED SHOP — Strategy Plans Review
## Senior Reviewer Assessment | February 10, 2026
**Reviewer:** Roviq Internal QA  
**Plans Reviewed:** Plan 1 (Opus 4.6T), Plan 2 (GPT-5.2), Plan 3 (Gemini)  
**Verdict:** Not ready to send. Major gaps, budget fantasies, and a glaring omission that would embarrass us.

---

## 0. THE ELEPHANT IN THE ROOM: SUBSCRIPTION BOXES

**All three plans completely ignore quarterly subscription boxes.** The client explicitly expressed interest. Randy flagged it. It's in the LEAD file. And not a single plan mentions it — not even in passing, not even as a future phase. This is a proposal-killing omission.

If I'm the client and I told you I was interested in subscription boxes and your 30-page plan doesn't mention them once, I assume you weren't listening. This must be fixed before anything goes out.

---

## 1. Subscription Box Integration (What Should Have Been Written)

**Gap severity: CRITICAL**

None of the three plans address this. All three focus exclusively on drops + app + VIP tiers as the revenue model. The subscription box is a distinct revenue stream that should be woven into the app architecture, the community tiers, and the retainer scope. Here's what's missing from each:

- **Plan 1** has the most developed VIP tier system (Decoded / Noir / Elite) but never considers how a physical quarterly box fits into those tiers. The Noir membership at $15/month is structured around digital access — early drops, exclusive content, behind-the-scenes. A subscription box would fundamentally change the economics and value proposition of that tier.

- **Plan 2** mentions "game/content experiments" in the retainer but has no physical product strategy beyond drops. The subscription box is a physical touchpoint that would reinforce everything the app is trying to do digitally.

- **Plan 3** has the most creative ideas (NFC cards, geo-fenced drops, "The Glitch") but is entirely digital. A quarterly box would be the one physical artifact that bridges the app experience into the real world — and Plan 3's creative energy should have been pointed at this.

**What all three should have included:**
- Box as an app-integrated experience (unboxing codes, AR reveals, in-app countdown to box ship date)
- Box contents tied to VIP tier (Noir members get a Noir box, standard members get a standard box)
- Box as a retention anchor (quarterly commitment = 4 guaranteed touchpoints/year)
- Box as a content engine (unboxing videos = UGC = TikTok/IG content)
- Box revenue modeling (even rough: 200 subscribers × $75/quarter = $60K/year)

See Section 9 below for the full subscription box strategy that should be integrated into the final proposal.

---

## 2. Pricing Reality

**Is $7,500–$10K realistic for what's being proposed?**

**Short answer: No.**

Let me itemize what Plan 1 promises for $7,500:

| Component | Realistic Solo Dev Cost | Notes |
|-----------|------------------------|-------|
| Cinematic onboarding (3 screens, custom animations, audio) | $1,500–$2,500 | Custom animations with sound are not trivial. Lottie/After Effects work, audio integration, auto-advance logic. |
| Home screen with dynamic hero + countdown + hidden element | $1,000–$1,500 | Dynamic content management, countdown logic, easter egg mechanics |
| Drop Zone (live drops, timers, locked/VIP, archive) | $2,000–$3,000 | Real-time inventory, conditional access by tier, countdown UX |
| The Vault (custom arcade game + leaderboard + rewards) | $3,000–$5,000 | **This alone could eat the entire budget.** A custom driving game with scoring, leaderboard, reward distribution, and quarterly rotation architecture is not a weekend project. |
| Noir Lounge (VIP content feed + gating) | $1,000–$1,500 | Content management, tier verification, exclusive product routing |
| Shop (Shopify sync + product pages + cart + checkout) | $2,000–$3,000 | Storefront API integration, real-time inventory, checkout webview/SDK |
| Profile (order history + tiers + game stats + referrals) | $1,000–$2,000 | Multiple data sources, referral tracking system |
| Push notifications (segmented by tier + behavior) | $1,000–$2,000 | FCM + APNs setup, segmentation logic, notification service |
| Backend (Node.js server for game logic, auth, push, membership) | $2,000–$3,000 | API design, database schema, auth flows, deployment |
| App Store submission (both platforms) | $500–$1,000 | Screenshots, metadata, review process, potential rejections |
| **TOTAL** | **$15,000–$24,000** | |

Plan 1 is promising ~$20K worth of work for $7,500. Plan 3 is slightly more honest at $10K but still underquoting.

**Plan 2's $5,000–$10,000 range is the worst offender** because the low end ($5K) is pure fantasy. You cannot build a React Native app with a custom embedded game, Shopify integration, push notification segmentation, and VIP tier gating for $5,000. Full stop.

**What should actually happen for $7,500–$10K (V1 scoped to budget):**

| Keep in V1 | Cut from V1 |
|------------|-------------|
| Cinematic onboarding (simplified — 2 screens, motion graphics, no custom audio) | Custom audio/engine sounds (use stock) |
| Home screen with dynamic hero + countdown | Hidden element / easter egg mechanics (Phase 2) |
| Basic drop view (countdown + product + buy) | Drop archive, locked/VIP drops |
| Shop with Shopify sync + checkout | "Complete the look" recommendations |
| Basic push notifications (broadcast, not segmented) | Segmented push by tier/behavior |
| Basic profile (order history + tier display) | Game stats, referral tracking, notification prefs |
| Noir section (gated product access) | Content feed, behind-the-scenes, founder Q&As |
| **ONE simple game** (not a driving game — a tap/swipe mechanic with score tracking) | Custom arcade game with leaderboard + quarterly rotation |

**The game is the riskiest line item.** A proper custom arcade game (Plan 1's "driving-themed" or Plan 3's "Midnight Run") with physics, scoring, leaderboard, and reward distribution is a $3K–$5K feature by itself. For V1, do a simpler mechanic — a tap-to-decode puzzle, a reaction-time challenge, something that can be built in 1–2 days, not 2 weeks. Save the cinematic driving game for V2 (quote it as an add-on at $2K–$3K).

**Bottom line:** The budget works if you aggressively scope V1 down. As currently written, all three plans are selling $15K–$25K apps at $7.5K–$10K prices. That either means we eat the cost, deliver something worse than promised, or miss the deadline. None of those are acceptable.

---

## 3. Technical Feasibility

**Can one developer build this in 6–8 weeks?**

Let me map the realistic timeline for a **scoped-down V1** (see cuts above):

| Week | Deliverable |
|------|-------------|
| 1 | Project setup, navigation skeleton, Shopify Storefront API integration, auth flow |
| 2 | Onboarding screens (motion design), home screen, countdown components |
| 3 | Shop screens (product list, product detail, cart), Shopify checkout integration |
| 4 | Drop view, push notification setup (FCM + APNs), basic notification triggers |
| 5 | Simple game mechanic + score tracking, Noir gated section |
| 6 | Profile screen, tier logic, polish + bug fixes |
| 7 | Testing on both platforms, App Store assets + submission |
| 8 | Buffer for App Store review, rejections, last-minute fixes |

**This is tight but doable IF:**
- The game is simple (not a custom driving game)
- Push notifications are broadcast-only (not segmented by behavior)
- No custom backend analytics dashboard
- Checkout uses Shopify's webview (not a custom checkout flow)
- "Dynamic hero" content is managed via a simple CMS or Firebase, not a custom content management system
- The developer has prior React Native + Shopify Storefront API experience

**What's NOT feasible in 6–8 weeks for one developer:**
- Plan 1's full scope (7 major screens + custom game + segmented push + leaderboard + referral system)
- Plan 3's "two to three mini-games" — building even ONE proper game is 1–2 weeks
- Plan 3's "The Glitch" random price-drop mechanic — this requires server-side timing, inventory holds, abuse prevention, and is a legal/business risk
- Plan 3's geo-fenced drops — requires location permissions, geo-fencing logic, and server-side validation
- Real-time inventory sync with conflict resolution (what happens when two people add the last item to cart simultaneously?)

**The App Store is its own timeline risk.** Apple review can take 1–7 days, and first-time submissions for apps with in-app purchases or game mechanics get extra scrutiny. Plan for at least one rejection and resubmission cycle. None of the plans mention this.

---

## 4. Missing Elements (All 3 Plans)

Things a real client would ask about that none of the plans address:

### 4.1 — Quarterly Subscription Boxes
Already covered. This is the #1 miss.

### 4.2 — Website
All three plans mention "the app is the play" but the client also needs a website. LEAD.md says "They also need a website but the app is the main event." Plan 1 lists a website overhaul as a $2,500 add-on. Plan 2 and Plan 3 barely mention it. None of them present a clear website scope, timeline, or how it relates to the app.

The client is going to ask: "So what about my website?" And the answer can't be "it's an add-on." It needs to be part of the conversation — even if it's Phase 1 triage (as Plan 1 suggests) rather than a full rebuild.

### 4.3 — App Maintenance & Updates After V1
What happens when iOS 19 drops and breaks something? What happens when Shopify changes their API? What happens when the game has a bug? The retainer mentions "bug fixes" but doesn't specify response times, included hours, or what counts as "minor" vs. "major." A client will (rightly) want to know what they're paying for.

### 4.4 — Analytics & Reporting Specifics
Plan 1 mentions "basic Firebase analytics." Plan 2 mentions "basic analytics." Plan 3 doesn't mention analytics at all. The client is going to ask: "How do I know if this is working?" None of the plans define what metrics will be tracked, how they'll be reported, or what the baseline goals are.

### 4.5 — Content Creation Responsibility
Who creates the content for the app? The cinematic hero images for each drop, the Noir Lounge behind-the-scenes content, the product photography — is that the client's job or Roviq's? None of the plans clearly delineate this. Plan 1's retainer includes "home screen hero updates" but doesn't address who creates the visual assets.

### 4.6 — Legal / Compliance
- **Apple's App Store guidelines** on real-money rewards from games (discount codes tied to game scores could be classified as gambling mechanics in some jurisdictions)
- **Privacy policy** for push notifications and data collection
- **Terms of service** for the app
- **Refund policy** for Noir membership if it becomes a paid tier
- Plan 3's "$0.00 plus shipping" Glitch mechanic — is this a promotional offer? Does it require FTC disclosure? What prevents abuse (bots, screenshots, multiple accounts)?

### 4.7 — Onboarding the Client
None of the plans describe how the client will manage the app day-to-day. Can the owner update drop schedules? Upload products? Send push notifications? Or is every change a request to Roviq? This dramatically affects the retainer value proposition.

### 4.8 — Offline / Poor Connectivity
What happens when someone opens the app with no signal? Streetwear audiences skew young and mobile-first — they'll open this on subway platforms and in crowded venues. None of the plans address offline states or graceful degradation.

### 4.9 — Location Confusion
The LEAD.md says "Boston area" and corrects that "806 area code was misleading." The RESEARCH-SUMMARY says "Texas-based (806/Panhandle)." Plan 3 includes "Geo-Fenced Drops (The 806 Exclusive)" for the 806 area code AND mentions "Boston/Texas." **We don't even know where this client is located.** This needs to be clarified before any geo-specific strategy is proposed.

### 4.10 — App Download Projections
Plan 1 estimates 500–1,000 installs in the first 2 weeks (5% of 20K IG followers). That's optimistic. Industry benchmarks for IG-to-app-install conversion for non-gaming apps are 1–3%. A more realistic estimate is 200–600 installs in month one. None of the plans model what happens if installs are lower than expected.

---

## 5. Contradictions Between Plans

### 5.1 — Pricing
| Plan | V1 Price | Monthly Retainer |
|------|----------|------------------|
| Plan 1 | $7,500 flat | $1,500/month |
| Plan 2 | $5,000–$10,000 range | $2,000–$4,000/month |
| Plan 3 | $10,000 flat | $2,500–$4,000/month |

Plan 2 giving a $5K–$10K range is unprofessional — that's a 100% variance. Pick a number. Plan 1 is the most specific but also the most underpriced relative to scope. Plan 3 is the most honest on price but the most unrealistic on scope for that price.

**Retainer contradiction:** Plan 1 says $1,500/month. Plan 3 says $2,500–$4,000/month. That's a 2.5× difference. The client will notice if these numbers appear anywhere in the final proposal. **Who's right?** Probably Plan 2/3's range. $1,500/month for drop campaign management + push notification strategy + app content updates + game management + analytics + Instagram strategy + bug fixes + monthly call is underpricing. That's easily $2,500–$3,000/month worth of work.

### 5.2 — Scope Philosophy
- **Plan 1** says: Build a comprehensive app with structured drop mechanics, measured VIP tiers, and data-driven growth. It's methodical.
- **Plan 3** says: Build an art piece. The app IS the brand. Games, glitches, $0 drops, burning unsold inventory on livestream.
- **Plan 2** splits the difference but leans toward Plan 1's structure.

**The tension:** Plan 1 wants a reliable business tool. Plan 3 wants a viral cultural artifact. These are fundamentally different apps with different development approaches, risk profiles, and maintenance needs. The final proposal needs to pick a lane — or explicitly phase them (V1 = Plan 1's foundation, V2+ = Plan 3's creative ideas layered on top).

### 5.3 — Game Complexity
- **Plan 1:** One driving-themed arcade game, quarterly rotation
- **Plan 2:** One Space Invaders-style game + "Turbo Run" + weekly mystery game drops
- **Plan 3:** Two to three games (Midnight Run racer + The Confessional text adventure + weekly "Glitch" mechanic)

Plan 2 and Plan 3 both propose multiple games and then quote $5K–$10K. Multiple games in V1 is budget suicide. **Plan 1 is right:** one game, keep it simple, rotate quarterly.

### 5.4 — VIP Tier Structure
- **Plan 1:** Three tiers (Decoded free / Noir $15/month or $300 lifetime / Elite earned)
- **Plan 2:** Two tiers (basic vs. "Decoded Rank" based on engagement — vague)
- **Plan 3:** No formal tier structure — access is earned through game performance and spending

**Plan 1 is right** on tier structure — it's the most thought-through. But the $15/month Noir membership needs rethinking if subscription boxes are added (the box changes the value equation entirely).

### 5.5 — Research Summary vs. All Plans
The RESEARCH-SUMMARY recommends **Vajro ($150/month) over custom build ($100K+)** and explicitly says "the mobile app request is premature." All three plans ignore this and proceed with a custom build at $7.5K–$10K. The disconnect is jarring — the research says "don't do this yet" and every plan says "here's how we do it."

To be fair, Randy overrode the research recommendation (LEAD.md makes clear the app IS the play and Randy builds it). But the plans should at least acknowledge the research finding and explain why the custom build makes sense despite it. Otherwise it looks like the research and the plans were done by different teams who didn't talk to each other — which is exactly what happened.

---

## 6. Generic vs. Specific

### Generic (Could Apply to ANY Streetwear Brand)

**Plan 1:**
- "Install Klaviyo" — this is in every DTC playbook
- "Launch TikTok" — every brand gets this advice
- "Add product descriptions" — basic e-commerce hygiene
- "Cinematic onboarding" — this is described in abstract. What makes it DECODED's onboarding vs. any luxury brand's onboarding? The engine sound is a nice touch but it's one detail in a sea of generics.
- "Surprise-first. Hidden content. Easter eggs." — every gamification consultant says this

**Plan 2:**
- Almost the entire Phase 1 section is generic DTC advice
- "Hero carousel for active drop" — every app has a hero carousel
- The feature spec reads like a template with "Decoded" find-and-replaced in
- "Lean + targeted" paid acquisition — says nothing specific

**Plan 3:**
- Least generic of the three — the Confessional game (806 The Show podcast lore + bible verses) is genuinely Decoded-specific
- Geo-fenced drops for 806 area code — specific (but may be wrong area, see location confusion above)
- "Kill Switch" burn mechanic — specific and bold
- BUT: "Midnight Run" driving game is generic car culture, not specifically Decoded's brand

### Actually Specific to Decoded
- Plan 1: Two-tier brand architecture analysis (Decoded vs. Noir), the 911 Turbo aesthetic throughout onboarding, "Hand of God" / "Kingdom Has Fallen" product name analysis
- Plan 2: "806 The Show" podcast integration, "Choose your lane: Decoded / Decoded Noir" onboarding fork
- Plan 3: "The Confessional" puzzle game using podcast lore and bible verses, NFC physical keys for top spenders

**Verdict:** Plan 3 is the most Decoded-specific. Plan 2 is the most generic. Plan 1 falls in between — strong brand analysis but generic tactical recommendations.

---

## 7. Best Ideas Per Plan (MUST Include in Final Proposal)

### Plan 1: **Structured Drop Mechanics with Push Notification Sequences**
The Pre-Drop → Drop Day → Drop Live → Post-Drop push notification cadence (72h → 1h → live → 24h follow-up) is the most operationally useful thing across all three plans. It's a repeatable playbook the client can actually execute. The three drop templates (Standard / Noir / Vault) are ready to use on day one. This is the backbone of the retainer value.

### Plan 2: **"Choose Your Lane" Onboarding Fork**
Splitting the onboarding into Decoded vs. Decoded Noir paths is smart because it immediately segments the user base and lets the app personalize from the first interaction. None of the other plans do this. It also validates the two-tier brand architecture in real-time — if 80% choose Noir, that tells the client where to invest.

### Plan 3: **"The Confessional" Podcast-Integrated Puzzle**
Using "806 The Show" podcast content as actual game mechanics (answer questions based on episodes, enter verbal codes from the show) is the most genuinely Decoded-specific idea across all three plans AND it solves the cross-platform engagement problem. It forces podcast listeners to download the app and app users to listen to the podcast. This is a real flywheel, not a buzzword.

---

## 8. Worst Ideas Per Plan (Should Be Cut)

### Plan 1: **"Decoded Radio" — Hidden Audio Player with Curated Playlists**
This is scope creep disguised as atmosphere. Building a music player — even a "hidden" one — adds development time, licensing concerns (even for curated playlists), and ongoing maintenance for zero revenue impact. If the client wants music integration, link to a Spotify playlist. Don't build a media player inside a shopping app.

### Plan 2: **"Noir Signals" Community Feed + User-Generated Photo Wall**
Building a social feed inside the app is a rabbit hole. Content moderation, reporting systems, upload infrastructure, feed algorithms — this is Instagram's job. At Decoded's scale (20K followers, likely hundreds of app users at launch), a community feed will be a ghost town that makes the brand look dead. Cut it entirely. Use Instagram for community.

### Plan 3: **"The Glitch" — Random $0.00 Pricing Mechanic**
This is the most dangerous idea across all three plans. Randomly setting Noir collection prices to $0.00 (even for 10 minutes) has catastrophic potential:
- **Bot abuse:** Automated scripts monitoring for the glitch and buying instantly
- **Inventory loss:** Giving away $120–$150 items for shipping cost only
- **Legal risk:** Is this a sweepstakes? A promotion? Does it need FTC disclosure?
- **Brand damage:** Luxury brands do NOT give product away for free. It undermines the $150 price point.
- **Technical complexity:** Server-side randomized pricing, abuse prevention, inventory holds, rollback logic
- **Customer anger:** "I paid $150 yesterday and someone got it for $0 today"

If you want surprise mechanics, do surprise discounts (20–30% off for 10 minutes) on select items, not $0 pricing on the luxury line. Or do surprise unlocks (hidden product access) rather than surprise pricing.

---

## 9. Subscription Box Strategy (The Missing Section)

This is what should have been in all three plans.

### 9.1 — What Goes in the Box

**Tiered approach:**

**"Decoded Drop Box" — $65/quarter ($260/year)**
- 1 exclusive tee or accessory (not available anywhere else — box-only design)
- 1 mystery item from recent drops (overstock or variant)
- 1 branded accessory (sticker pack, keychain, patch, car freshener with Decoded branding)
- A physical "Vault Card" with a one-time code that unlocks something in the app (discount, hidden product, game skin)
- Lookbook / zine insert with upcoming drop previews

**"Decoded Noir Box" — $120/quarter ($480/year)**
- Everything in the Drop Box, PLUS:
- 1 Noir-tier item (exclusive Noir colorway or material, box-only)
- Premium packaging (matte black, foil stamp, magnetic closure)
- NFC-enabled card granting 48-hour early access to the next Noir drop
- Handwritten note or voice memo QR code from the founder
- First look at next season's Noir designs (printed lookbook, not digital)

**"Decoded Elite Crate" — $200/quarter ($800/year, invite-only)**
- Everything in the Noir Box, PLUS:
- 1 limited-run item (numbered, 50 units max)
- 1 collab item or 1-of-1 prototype
- VIP event access (virtual or in-person if local)
- Direct input on next quarter's box contents (vote via app)

### 9.2 — App Integration

The subscription box should be deeply woven into the app experience:

- **"My Box" section in Profile:** Subscribers see their upcoming box status, ship date countdown, and past box contents.
- **Unboxing Codes:** Each box contains a physical card with a QR code. Scanning it in the app triggers an "unboxing experience" — a cinematic reveal of what's in the box, unlocking the items in the user's in-app collection/profile. This creates a ritual and generates shareable content.
- **Box-Only Vault Access:** Each box contains a unique code that unlocks a limited-time section of The Vault — a mini-game variant, a hidden product, or a discount stack.
- **Box Countdown on Home Screen:** For subscribers, the home screen shows a countdown to the next box ship date alongside drop countdowns. Two reasons to keep opening the app.
- **"Box Preview" in Noir Lounge:** Noir and Elite subscribers get a blurred preview of next quarter's box 2 weeks before it ships. Builds anticipation and reduces churn.

### 9.3 — Pricing Analysis

| Tier | Price/Quarter | Est. COGS | Margin | Break-Even Subscribers |
|------|--------------|-----------|--------|----------------------|
| Drop Box | $65 | $25–$30 | 54–62% | 50 (to justify logistics) |
| Noir Box | $120 | $45–$55 | 54–63% | 25 |
| Elite Crate | $200 | $70–$90 | 55–65% | 10 |

**Revenue projection (conservative):**
- 100 Drop Box subscribers × $65 = $6,500/quarter
- 30 Noir Box subscribers × $120 = $3,600/quarter
- 10 Elite Crate subscribers × $200 = $2,000/quarter
- **Total: ~$12,100/quarter = ~$48,400/year in subscription revenue**

This is meaningful for a brand doing $100K–$500K/year. It's also predictable recurring revenue vs. unpredictable drop revenue.

### 9.4 — Connection to Noir Membership

**Critical decision:** Is the Noir Box separate from Noir membership, or bundled?

**Recommendation: Separate, but discounted for Noir members.**

- Noir membership ($15/month) = digital access (early drops, exclusive content, VIP lounge)
- Noir Box ($120/quarter) = physical product subscription
- Noir members get the Noir Box at $99/quarter (17% discount) as a perk
- This keeps the membership affordable for digital-only users while incentivizing upgrade to box

Alternatively, bundle them: $45/month gets you Noir membership + quarterly box (= $540/year vs. $180 + $480 = $660 separately). The bundle creates a clean, premium offer.

### 9.5 — Retainer Scope

**The subscription box is NOT part of the standard retainer.** It's a separate workstream:

- **Box curation and design:** Selecting items, designing box-exclusive products, packaging design — this is the client's responsibility with Roviq advisory input
- **App integration (one-time):** Building the "My Box" section, QR code scanning, unboxing experience — quote as $1,500–$2,500 add-on to V1 or V2
- **Ongoing box-related app updates:** Updating box preview content, managing codes, tracking subscriber data — included in retainer if retainer is $2,500+/month
- **Box fulfillment:** Entirely the client's responsibility (or a 3PL they contract). Roviq does not handle physical logistics.

### 9.6 — Launch Timing

Don't launch the box with the app. Launch the box in Quarter 2 (after the app has 200+ active users). Use the app launch period to gauge interest:
- Add a "Coming Soon: Decoded Drop Box" teaser in the app
- Collect waitlist signups (email capture → also feeds email marketing)
- Use waitlist size to determine initial box quantities
- First box ships 3 months after app launch

---

## 10. Final Verdict

### If I Were the Client, Would I Sign This?

**Plan 1:** I'd be impressed by the depth and feel like you understand my brand. I'd hesitate on the $7,500 price because the scope feels too good to be true — and I'd be right. I'd also notice you never mentioned subscription boxes, which I told you I was interested in. I'd ask: "Did you read my notes?"

**Plan 2:** I'd feel like you used a template. The feature spec is solid but the prose feels generic. The $5K–$10K range makes me think you don't know what this costs, which makes me wonder if you've done this before. The retainer range ($2K–$4K) is even vaguer. I'd want a firm number.

**Plan 3:** I'd be excited by the creativity but terrified by the execution risk. Burning unsold inventory? $0 pricing? Geo-fenced drops? This feels like ideas from someone who's never shipped a product. But "The Confessional" game using my podcast is brilliant and shows you actually researched my brand. I'd want this energy with Plan 1's structure.

### What Would Make Me Hesitate

1. **No subscription box mention** — I told you I wanted this. Did you listen?
2. **Vague pricing** — Give me one number, not a range. If you don't know what it costs, how do I trust you to build it?
3. **Unrealistic scope for budget** — I've gotten enough quotes to know $7,500 doesn't buy what you're describing. Either you're going to cut corners or you're going to come back asking for more money. Neither is good.
4. **No website plan** — I need a website too. Where is it?
5. **Who's building this?** — Is it one developer? A team? Offshore? I want to know who's touching my brand.
6. **What if the app flops?** — 200 downloads instead of 1,000. Then what? None of the plans have a contingency.

### What Would Make Me Sign

1. A single, unified proposal that combines Plan 1's structure, Plan 2's technical specificity, and Plan 3's creative energy
2. An honest scope for $7,500–$10K with clear "V1 vs. V2" delineation — don't promise what you can't deliver at this price
3. The subscription box strategy integrated from the start
4. A firm price on the retainer with clear deliverables (not ranges)
5. A realistic timeline with milestones and check-ins (not "6–8 weeks, trust us")
6. Proof that you built the AC Blacksite app — screenshots, download numbers, anything concrete

---

## Summary Scorecard

| Criterion | Plan 1 (Opus) | Plan 2 (GPT) | Plan 3 (Gemini) |
|-----------|:---:|:---:|:---:|
| Subscription Box Integration | ❌ Missing | ❌ Missing | ❌ Missing |
| Pricing Honesty | ⚠️ Underpriced | ❌ Vague range | ⚠️ Most honest |
| Technical Feasibility | ⚠️ Ambitious | ❌ Overscoped | ❌ Fantasy |
| Brand Specificity | ✅ Good | ⚠️ Generic | ✅ Strong |
| Operational Usefulness | ✅ Best | ⚠️ Decent | ❌ No playbooks |
| Creative Energy | ⚠️ Safe | ⚠️ Template | ✅ Best |
| Client Readiness | ⚠️ Close | ❌ Not ready | ❌ Not ready |

**Overall:** Plan 1 is the closest to sendable but still needs significant work. The final proposal should use Plan 1 as the skeleton, inject Plan 3's best creative ideas (Confessional, podcast integration, NFC keys as a future phase), add Plan 2's "Choose Your Lane" onboarding fork, integrate the subscription box strategy, and be brutally honest about what $7,500–$10K actually buys.

None of these plans are ready to send as-is. Merge, fix the gaps, and review again.

---

*Review completed: February 10, 2026*  
*Reviewer: Roviq Senior Review (Internal QA)*
