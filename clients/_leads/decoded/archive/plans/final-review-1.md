# FINAL QUALITY GATE REVIEW — PROPOSAL-DRAFT.md
## Decoded Shop × Roviq
### Reviewer: Subagent (proposal-reviewer-1) | Date: 2026-02-10

**Verdict: NOT READY FOR DELIVERY — requires fixes before Randy presents.**

There is strong work here. The creative vision is genuinely exciting and the tone is right for the audience. But there are factual errors, math problems, scope dishonesty, and missing pieces that would cost Roviq credibility or the deal itself. Below is everything, organized by severity.

---

## 🔴 CRITICAL — Must Fix Before Delivery

### 1. Texas / Location Error in RESEARCH-SUMMARY.md Is Leaking Into Proposal Context

**The RESEARCH-SUMMARY.md still says:**
> "Decoded Shop is a **Texas-based (806/Panhandle)** luxury streetwear brand"

And under White Space:
> "**Elevated Texas Streetwear** — nobody owns this positioning"
> "**806/Panhandle geography** — untapped identity in streetwear"
> "**Women's luxury streetwear in Texas** — empty category"

**The LEAD.md explicitly corrects this:**
> "Location: Boston area (NOT Texas — 806 area code was misleading)"

The proposal itself does NOT contain any Texas references — good. However, "806" appears in the proposal three times, always correctly referring to the podcast "806 The Show." **The proposal passes on this check.** But the RESEARCH-SUMMARY.md that feeds this pipeline is still poisoned with the Texas error and should be corrected before anyone else reads it.

**Action:** Fix RESEARCH-SUMMARY.md. Not a proposal blocker, but a credibility risk if the client ever sees supporting documents.

---

### 2. The $8,500 Price Does NOT Include Subscription Box Integration — But the Proposal Reads Like It Does

The pricing section lists the subscription box integration as a **separate $2,000 add-on:**

> **SUBSCRIPTION BOX ADD-ON — $2,000 (One-Time)**
> App integration for "The Cache": "My Box" profile section, QR scanning / NFC unboxing experience, Box countdown on home screen, Box preview in Noir Lounge, Waitlist capture flow

But the **App Screens (V1) section in §4.3** lists ALL of those features as part of the V1 app spec:

> - `Subscription box ship date countdown (subscribers)` — on Home Screen
> - `"My Box" — subscription box status, ship date countdown, past box contents, QR unboxing` — on Profile
> - `Subscription box preview (blurred, 2 weeks before ship — Noir/Elite subscribers only)` — in Noir Lounge
> - `Waitlist Signup — "Coming Soon: The Cache" banner + email capture` — on Home Screen

**The problem:** The client reads §4.3 and sees subscription box features baked into the V1 app. Then they get to pricing and see a $2,000 add-on for the same features. This will feel like a bait-and-switch. Either:

**(a)** Remove subscription box references from the V1 screen spec and mark them as "Cache Add-On features," OR
**(b)** Roll the $2,000 into the $8,500 (making it $10,500 total build), OR
**(c)** Clearly annotate the V1 screen spec with "[Cache Add-On]" labels next to each subscription feature so the reader knows they're part of the separate line item.

**Recommendation:** Option (c) is the cleanest. The features are already designed — just label them. And bump the total to $10,500 in the summary table so there's no ambiguity.

**Current total table says:**
| V1 App Build | $8,500 |
| Subscription Box App Integration | $2,000 |
| Monthly Retainer (12 months) | $30,000 |
| **Total** | **$40,500** |

This math is correct ($8,500 + $2,000 + $30,000 = $40,500). But the emotional read is "$8,500 for the app" when it's really "$10,500 for everything you described." The header "V1 BUILD — $8,500" is doing damage because the V1 spec includes Cache features. Fix the labeling or fix the price.

---

### 3. Scope vs. Timeline: Two Games in 8 Weeks Is a Red Flag

The V1 scope includes:
- Full Shopify website triage (Weeks 1–2)
- Cinematic onboarding with custom animations (Week 2)
- Full shopping experience with Shopify Storefront API (Week 3)
- Drop Zone with multiple complex mechanics (Week 4)
- Push notification system with segmented tiers (Week 4)
- **"Midnight Run" — a 2D sprite racing game with scoring, leaderboards, and reward triggers (Week 5)**
- **"The Confessional" — a podcast trivia/puzzle game (Week 6)**
- Noir Lounge with gated content (Week 6)
- Profile with order history, tier status, game stats, referral codes (Week 6)
- App Store submission with assets, screenshots, preview video (Week 7)
- QA and review buffer (Week 8)

**For one developer (Randy), this is extremely aggressive.** Let me break down Week 5 alone:

"Midnight Run" requires:
- 2D sprite art (car, obstacles, road)
- Game physics/collision detection
- Scoring system
- Persistent leaderboard (Firebase writes/reads)
- "Check Engine" reward trigger at 5,000 points → unlocks hidden product collection
- "Driver's License" shareable scorecard image generator (designed for IG Stories)
- SpriteKit or equivalent framework integration

That's not a one-week task for a solo developer. That's 2–3 weeks minimum, especially with the shareable scorecard and reward-trigger integration into the shop.

**Week 6 asks for:**
- "The Confessional" game (entirely different mechanic — quiz/puzzle, not arcade)
- Noir Lounge (content gating, tier checks, preview blurring)
- Full Profile screen (order history via Shopify API, tier logic, game stats aggregation, referral system, notification preferences)
- "Polish"

Week 6 is 3–4 weeks of work compressed into one.

**Total honest estimate for this scope:** 12–16 weeks for a solo developer, not 8.

**Recommendation:**
- **Cut one game from V1.** Ship "Midnight Run" in V1, move "The Confessional" to the retainer period (Month 2). This is the single biggest de-risk move.
- **Simplify the Driver's License scorecard** — V1 can be a screenshot prompt, not a custom image generator.
- **Move Versus Drops to post-launch.** The mechanic (vote, lock loser, sell winner) requires real-time voting UI, timer logic, and inventory manipulation. It's a feature, not a detail. It can ship in Month 2.
- **Be explicit about what's "V1" vs. "V1.1" (first retainer month).**

If Randy disagrees and wants to keep the 8-week timeline, the proposal should at minimum note that certain features may ship in a Day 1 patch during Week 9–10 rather than promising everything by App Store submission.

---

### 4. The "Kill Switch" Is a Legal and Brand Liability

> "If a drop doesn't sell out within 48 hours, the remaining inventory gets burned. Literally. Livestreamed on Instagram and in the app."

Problems:
1. **FTC concerns.** If Decoded ever *doesn't* actually burn the inventory but claims to, that's deceptive advertising. The proposal should note that if this mechanic is used, it must be genuine and documented.
2. **Environmental optics.** In 2026, "we burn unsold clothes" is a PR landmine. Burberry got destroyed for this in 2018. Fashion brands have moved aggressively toward sustainability messaging. A luxury streetwear brand livestreaming garment destruction could generate exactly the wrong kind of viral attention.
3. **Financial stupidity at current scale.** With ~$68 AOV and margins of 60–65%, burning inventory is burning real profit. At Decoded's revenue scale ($100K–$500K/year), this isn't a flex — it's waste.

**Recommendation:** Reframe as "THE VAULT LOCK" — unsold inventory gets pulled from sale permanently and locked in "The Vault," potentially resurfacing as mystery items in subscription boxes or earned rewards. Same scarcity psychology, no fire, no PR risk, and the inventory still generates value.

---

## 🟡 SIGNIFICANT — Should Fix Before Delivery

### 5. Revenue Projections Are Optimistic and Missing Key Assumptions

**Subscription box projections:**

> | Drop Box ($65) | 100 subscribers | $6,500/quarter | $26,000/year |
> | Noir Box ($120) | 30 subscribers | $3,600/quarter | $14,400/year |
> | Elite Crate ($200) | 10 subscribers | $2,000/quarter | $8,000/year |
> | **Total** | **140** | **$12,100** | **$48,400** |

These are labeled "conservative," but 140 subscribers from a base of ~200 app users (the stated green-light threshold) is a **70% conversion rate to a paid subscription.** That's not conservative — that's fantasy. Even best-in-class DTC subscription boxes convert 5–15% of engaged audiences.

At 200 active app users × 10% conversion = 20 subscribers. That's ~$1,700/quarter, not $12,100.

For 140 subscribers, you'd need ~1,400–2,800 active app users (at 5–10% conversion). The proposal projects 300–600 installs in Month 1. Even at 600 installs, with a typical 30% 30-day retention rate, you'd have ~180 active users after Month 1. Getting to 1,400+ active users likely takes 6–12 months.

**The "at scale" projection is even more aggressive:**
> "At scale (200+ subscribers), this revenue stream reaches $56,000+/year"

200 subscribers is *barely* above the "conservative" 140. The jump from $48,400 to $56,000 doesn't correspond to going from 140 to 200 subscribers with the given tier pricing. Let me check:

At 200 subscribers, if the tier distribution stays proportional (71% Drop, 21% Noir, 7% Elite):
- 142 × $65 = $9,230/quarter
- 42 × $120 = $5,040/quarter
- 14 × $200 = $2,800/quarter (but Elite is capped at 10 per the invite-only structure)

So: $9,230 + $5,040 + $2,000 (Elite capped at 10) = $16,270/quarter = $65,080/year. OK, $56,000+ is actually *under*-stated here if Elite stays at 10. But the underlying subscriber count assumption is still the problem.

**Recommendation:** Reframe projections with clear assumptions. Show a "ramp" model:
- Month 3–6 (launch): 20–40 subscribers → $1,700–$3,500/quarter
- Month 6–12: 60–100 subscribers → $5,000–$8,500/quarter
- Year 2 target: 140+ subscribers → $12,100/quarter

This is more honest, still impressive, and doesn't risk the client calling BS.

---

### 6. The "Noir Membership" Revenue Projection Contradicts the Tier Structure

The Year 1 revenue projection says:
> "Noir membership revenue: $5,400+ (30 members × $15/month × 12)"

But §4.7 says Noir auto-unlocks at $300 lifetime spend:
> "**NOIR** ($15/month **or auto-unlock at $300 lifetime spend**)"

So some Noir members are paying $15/month and some are free (they spent $300+). The revenue projection assumes all 30 are paying $15/month. In reality, your most valuable customers — the ones spending $300+ — get Noir for free. The paying Noir members are the ones who *haven't* spent enough yet.

**This could be a hard conversation with the client:** "Wait, my best customers get the VIP tier for free, and the ones who haven't bought much pay $15/month for early access to... buy more?"

**Recommendation:**
- Reframe auto-unlock as a perk, not a replacement. E.g., "Noir membership is $15/month. Customers who reach $300 lifetime spend earn a complimentary upgrade." This way the revenue projection stays valid — most Noir members are paying.
- OR remove auto-unlock and make it spend-threshold + subscription. E.g., you must both subscribe AND have spent $300+ to reach a higher tier. This is cleaner but less generous.
- Regardless, adjust the revenue projection to account for free auto-unlock members.

---

### 7. "Shopify" vs. "Square Online" Platform Confusion

The LEAD.md says:
> "Website: https://decodedshop.myshopify.com/ (Square Online, not Shopify — per social audit)"

But the entire proposal is built around **Shopify Storefront API**, Shopify checkout, and Shopify integrations. If the store is actually on Square Online:
- The Storefront API won't work
- Shopify checkout integration won't work
- Klaviyo integration may differ
- Product sync architecture is completely different

**This is potentially a foundation-level error.** If the store is Square, not Shopify, the entire technical architecture section needs revision.

**However:** The `.myshopify.com` URL strongly suggests it IS Shopify (Square Online uses `squareup.com` or custom domains). The LEAD.md parenthetical may be wrong. This needs to be verified before the proposal goes out.

**Recommendation:** Verify the platform. Visit the URL, check the page source. If it's Shopify, correct the LEAD.md note. If it's actually Square, the proposal has a serious technical problem.

---

### 8. The Research Summary Recommended AGAINST a Custom App — The Proposal Ignores This

The RESEARCH-SUMMARY.md has an entire section:

> **MOBILE APP ASSESSMENT (Opus 4.6T)**
> Recommendation: Vajro ($150/mo) over custom build ($100K+)
> Year 1 total cost: ~$2K vs $100K+ custom
> **BUT: website fundamentals must be fixed first**

And the concluding consensus:
> **⚠️ EVERY AGENT AGREES ON THIS**
> **Build the brand before building the app.** The mobile app request is premature.

The proposal goes in the complete opposite direction: a custom-built app at $8,500, as the centerpiece.

**This is not necessarily wrong** — Randy overrode the research agents' recommendation, and the LEAD.md confirms his direction: "Randy builds the mobile app — this IS the core offering." But the proposal should not be blind to the tension. If the client has done their own research and seen that Vajro-style solutions exist for $150/month, they'll wonder why they're paying $8,500+.

**Recommendation:** Add a brief "Why custom, not off-the-shelf?" section (2–3 sentences) in the technical architecture or "Why Roviq" section. Something like: "Platforms like Vajro or Tapcart can put a basic shopping app in the App Store for $150/month. But they can't build a hidden game that unlocks products. They can't build a cinematic onboarding sequence. They can't integrate podcast codes or subscription box NFC experiences. What we're building isn't a mobile storefront — it's a platform. That requires custom architecture."

---

### 9. Retainer Scaling Clause Is Vague and Could Cause Conflict

> "If Decoded's monthly revenue exceeds $30K, retainer increases to $3,500/month"

Questions the client will ask:
1. **Total revenue or app-attributable revenue?** If Decoded already does $30K/month from their website (their estimated annual is $100K–$500K, so $8K–$42K/month), they might ALREADY be over $30K. Does the retainer jump to $3,500 immediately?
2. **Who measures this?** Does Roviq get Shopify access to verify revenue? What's the reporting mechanism?
3. **Is this cumulative or per-month?** One good month at $31K, then back to $20K — does it stay at $3,500?

**Recommendation:** Define "revenue" precisely. Suggest: "If average monthly revenue over any rolling 3-month period exceeds $30K (measured via Shopify/Square analytics dashboard shared with Roviq), the retainer adjusts to $3,500/month starting the following month." This is fair, measurable, and non-punitive for one-off spikes.

---

### 10. No Mention of NFC Implementation Complexity

The proposal casually references NFC multiple times:
- "NFC artifacts that unlock in-app experiences" (§2)
- "NFC-enabled card granting 48-hour early access to the next Noir drop" (§5.2 Noir Box)
- "QR scanning / NFC unboxing experience" (§9 Pricing)

NFC on iOS requires:
- Core NFC framework (available since iOS 13, but with restrictions)
- NDEF tag reading (supported) vs. tag writing (limited)
- Background tag reading only on iPhone 7+
- The physical NFC tags/cards must be sourced, encoded, and integrated into the fulfillment pipeline

This is not trivial. The proposal prices NFC integration into a $2,000 add-on that also covers QR scanning, box countdowns, Noir Lounge previews, and waitlist capture. NFC alone could eat that budget.

**Recommendation:** Either (a) scope NFC as a separate line item or Phase 5 feature, or (b) simplify V1 to QR-only (which is much simpler — it's just a URL scan) and position NFC as a premium upgrade for the Noir/Elite box tiers in a future quarter.

---

## 🟢 MINOR — Nice to Fix

### 11. Golden Ticket Compliance Note Is Incomplete

> "1 in every 50 boxes — across all tiers — contains a Black Card. A physical metal card worth $500 in Decoded credit."

§11 mentions "Golden Ticket disclosures" under FTC compliance, but doesn't specify what's required. At minimum:
- Official rules must be posted (likely in-app and on website)
- "No purchase necessary" alternative entry method may be required depending on state law (this is a sweepstakes/prize structure)
- The $500 credit value and odds (1:50) must be disclosed clearly in subscription terms
- Massachusetts (Boston) has specific promotional contest regulations

**Recommendation:** Add a line: "Golden Ticket mechanics will be reviewed with legal counsel prior to launch to ensure compliance with Massachusetts promotional regulations and FTC guidelines."

---

### 12. Inconsistent Terminology: "Noir Flash Sale" vs. "The Glitch"

> §4.6: **THE NOIR FLASH SALE (replaces "The Glitch")**

This parenthetical "(replaces 'The Glitch')" is internal revision language that should not appear in the client-facing proposal. The client has never seen "The Glitch" — they don't know what's being replaced.

**Action:** Remove "(replaces 'The Glitch')".

---

### 13. App-Exclusive Drops Frequency Claim Contradicts Itself

§4.4 says:
> "1–2 drops per quarter available ONLY in the app."

§6.5 (contingency for low downloads) says:
> "Increase app-exclusive drop frequency to force IG followers into the app"

If the contingency is to increase frequency, the 1–2/quarter number should be labeled as the baseline, not a fixed plan. Minor, but a sharp client would notice.

---

### 14. Missing Pieces — What the Client Will Ask

1. **"What happens to my existing customers?"** No migration plan for current buyers. Do they get auto-Noir status? Do they get early app access? A "Founding Members" program for existing customers is an obvious win that's not mentioned.

2. **"Who hosts the app backend? What are my ongoing infrastructure costs?"** Firebase/Supabase free tiers will be exceeded quickly with push notifications and game data. The proposal doesn't mention hosting costs. Rough estimate: $50–$200/month for Firebase/Supabase + hosting. This should be disclosed.

3. **"What if you disappear? Do I own the code?"** No mention of IP ownership or code repository access. Standard in any app development contract. Must be in the SOW.

4. **"Android?"** Mentioned in passing in §4.1 and §7.3 (Quarter 2–3, $4,000–$6,000) but never addressed directly. 50%+ of US streetwear consumers are on Android. The client will ask.

5. **"How do I update the app content myself?"** The retainer covers content updates, but what if they want to change a hero image or add a product between drops? Is there a CMS? Or is every change a Roviq request? This affects the retainer value proposition.

---

### 15. Formatting & Grammar

1. **§4.1 header says "Option A (Primary): Swift / Native iOS"** but there's no clear recommendation statement. It reads like Randy's preference, which is fine internally, but to the client it should read as a firm recommendation with rationale.

2. **The Vault Games in §4.3** — the tree structure uses monospace text that may not render well in all PDF/print formats. Consider converting to a table or clean bullet list for the final deliverable.

3. **§5.5 Revenue Projection table** — "Subscribers (Conservative)" column header should be "Subscribers (Year 1 Target)" since "conservative" is debatable per my analysis above.

4. **§9 Payment Terms** — "50% on App Store submission" is unusual. Industry standard is 50% on delivery/acceptance, not submission. Submission means the client pays before knowing if Apple approves. Consider: "50% on successful App Store approval" or "50% on delivery of code-complete build."

5. **§12 Next Steps** — "App development begins Day 3" — why Day 3, not Day 1? If it's because Days 1–2 are website triage, say that. Otherwise it reads arbitrary.

---

## ✅ WHAT'S WORKING WELL

Credit where it's due — this proposal has serious strengths:

1. **The "Digital Speakeasy" framing is excellent.** It's the kind of concept that makes a brand owner lean forward. It differentiates from every other "we'll build you an app" pitch.

2. **The tone is perfect for the audience.** This reads like a pitch from someone who gets streetwear culture, not a generic agency deck. Lines like *"10,000 streetwear brands have a Shopify store. None of them have a speakeasy"* are deal-closers.

3. **The diagnosis is honest and specific.** Grading the current state D-/F with concrete evidence (zero product descriptions, no email capture, no custom domain) builds trust. The client knows Roviq actually looked at their business.

4. **Content responsibilities table (§8) is outstanding.** Clear delineation of who does what prevents the #1 source of agency-client conflict. This alone shows professionalism.

5. **The Drop Architecture (§4.4) is genuinely creative.** Flash Raids, Versus Drops, podcast codes — these aren't generic gamification suggestions. They're specific, actionable, and tied to Decoded's existing behavior (frequent drops, podcast).

6. **The contingency plan (§6.5) shows maturity.** Most proposals don't address "what if this doesn't work?" Including a plan for low downloads builds trust.

7. **App Store submission reality check (§4.8) is smart.** Flagging potential rejection and building buffer time shows experience.

---

## 📋 SUMMARY OF REQUIRED CHANGES

| # | Issue | Severity | Action |
|---|-------|----------|--------|
| 1 | Texas error in RESEARCH-SUMMARY.md | 🔴 Critical (context doc) | Fix the source file |
| 2 | Subscription box features in V1 spec vs. $2K add-on pricing | 🔴 Critical | Label features as "[Cache Add-On]" in §4.3 |
| 3 | Two games + full app in 8 weeks | 🔴 Critical | Cut Confessional to Month 2, simplify scope |
| 4 | Kill Switch liability | 🔴 Critical | Reframe as "Vault Lock" |
| 5 | Subscription revenue projections unrealistic | 🟡 Significant | Add ramp model with assumptions |
| 6 | Noir auto-unlock contradicts revenue math | 🟡 Significant | Clarify and adjust projection |
| 7 | Shopify vs. Square platform confusion | 🟡 Significant | Verify before sending |
| 8 | No "why custom vs. off-the-shelf" justification | 🟡 Significant | Add 2–3 sentence section |
| 9 | Retainer scaling clause vague | 🟡 Significant | Define terms precisely |
| 10 | NFC complexity underestimated | 🟡 Significant | Simplify to QR-only for V1 |
| 11 | Golden Ticket compliance incomplete | 🟢 Minor | Add legal review note |
| 12 | "(replaces 'The Glitch')" internal language | 🟢 Minor | Remove |
| 13 | App-exclusive drop frequency inconsistency | 🟢 Minor | Label as "baseline" |
| 14 | Missing pieces (migration, hosting, IP, Android, CMS) | 🟡 Significant | Add FAQ or address in sections |
| 15 | Formatting/grammar items | 🟢 Minor | Fix per notes above |

---

## 🎯 THE "WOULD I SIGN THIS?" TEST

**As Decoded's owner, what would make me sign:**
- The speakeasy concept is genuinely exciting — it makes me feel like my brand could be the next MSCHF
- The diagnosis shows Roviq actually did their homework
- The AC Blacksite reference proves this isn't theoretical
- The content responsibilities table gives me confidence about what I'm responsible for
- The pricing is approachable for what's being promised

**What would make me walk:**
- If I notice the subscription box features are described twice (once in the app, once as an add-on), I'd feel nickel-and-dimed
- If I'm told 8 weeks and it takes 16, trust is broken on Month 1
- If I ask "what about Android?" and there's no clear answer, I'd worry about half my audience
- If I Google "Vajro" and see I can get a basic app for $150/month, I'd want to know why I'm paying $8,500+ — and the proposal doesn't pre-empt that question
- If I realize the subscription revenue projections are 5–10x overstated, I'd question everything else in the document

**Bottom line:** This proposal is 80% of the way to excellent. The creative vision and tone are deal-closers. The remaining 20% is math, scope honesty, and defensive writing that prevents the client from finding holes. Fix the critical items and this is a strong pitch.

---

*Review complete. Recommend revision cycle before delivery to Randy.*
