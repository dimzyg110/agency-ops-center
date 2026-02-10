# DECODED × ROVIQ

## *"10,000 streetwear brands have a Shopify store. None of them have a speakeasy."*

---

**Prepared for:** Decoded Shop
**Prepared by:** Roviq
**Date:** February 2026
**Classification:** Confidential

---

# 1. THE DIAGNOSIS

We audited Decoded's website, social presence, SEO, paid media, and revenue infrastructure. The findings were consistent.

| Dimension | Grade | The Problem |
|-----------|-------|-------------|
| Website & Digital | **D-** | No custom domain. Zero product descriptions. No About page. No brand story. No size guide. Default Shopify template. "Powered by Shopify" in the footer. |
| Social & Content | **D** | Instagram-only. No TikTok. 0.27% engagement on 20.4K followers. No content strategy. |
| Retention | **F** | $0 revenue from email. $0 from SMS. No capture mechanism. Every customer who buys is lost immediately. |
| Paid Advertising | **N/A** | Nothing running. Zero paid acquisition. |
| Revenue Infrastructure | **Critical** | AOV ~$68. No upsells. No bundles. No abandoned cart recovery. |

**Traffic isn't the problem. The problem is retention.**

Visitors who don't buy disappear. There is no email to follow up. No push notification to announce the next drop. No community to pull them back. The business model is to acquire a customer at full cost, sell them one item, then never speak to them again.

But the audit also showed the brand DNA is real. "Decoded Noir." "Hand of God." "Kingdom Has Fallen." The automotive and faith aesthetic. The 911 Turbo visual language. "806 The Show" as a cultural anchor. These aren't manufactured. They are genuine. Genuine brand identity is the one thing money can't buy.

The gap isn't identity. It is infrastructure.

---

# 2. THE VISION: THE DIGITAL SPEAKEASY

Most brands would fix the Shopify store and run ads.

We aren't doing that.

Decoded needs to stop competing as a clothing brand and start operating as a **digital speakeasy**. This is an invite-only world where the app isn't a store. It is the front door to a culture. The clothes are trophies you earn by being inside.

**The model:** MSCHF built a $200M+ brand on one principle. Every time you open the app, something different happens. You never know what you'll find. That creates compulsive engagement. People open the app to see what is happening. The buying follows.

Decoded's frequent drops are the perfect fuel for this. Most brands struggle to create reasons for people to open their app. Decoded's owner drops constantly. That is the engine.

**The plan:**
- A cinematic boot sequence that feels like starting a 911 Turbo
- Real arcade games hidden inside the app
- 15-minute "Flash Raid" drop windows that appear without warning
- Podcast episodes with verbal codes that unlock hidden content
- "The Vault Lock" where unsold inventory gets permanently pulled
- Quarterly subscription boxes with NFC artifacts
- A tiered community where the deepest levels are earned

The website becomes a clean, dark storefront that drives traffic to the app. The app is where the world lives.

**Nobody at Decoded's level has this.**

---

# 3. PHASE 1: WEBSITE TRIAGE — Weeks 1–2

The Shopify store isn't the main play, but it can't embarrass the brand while we build the app. This phase is surgical. We fix critical issues, establish the aesthetic, and add a clear funnel to the app.

### Deliverables

| Action | Why | Timeline |
|--------|-----|----------|
| **Custom domain** | `decodedshop.myshopify.com` signals "hobby project." A custom domain costs $15/year. | Day 1 |
| **Luxury-minimal redesign** | The website should feel like a high-end boutique at night. Clean. Dark. Sparse. | Week 1 |
| **Product descriptions** | Zero descriptions is a conversion killer. This alone can lift conversion 30%+. | Week 1–2 |
| **Brand story** | The founder's story is the brand. Automotive roots. Faith. One cinematic page. | Week 1 |
| **"Get the App" banner** | The website is a front window. The app is the store. Every page must funnel toward the download. | Week 1 |
| **Trust layer** | Size guide, returns policy, social links. Remove "Powered by Shopify." | Week 1 |
| **Email capture** | Klaviyo popup and welcome flow. Captures visitors who aren't ready to buy yet. | Week 2 |
| **Hide sold-out SKUs** | Remove dead-end pages that waste attention. | Day 1 |

**What this phase is NOT:** A full website rebuild. We aren't redesigning the entire Shopify experience. We are applying a skin, fixing critical gaps, and turning the site into an app funnel. The investment goes to the app.

**Phase 1 Cost:** Included in the project scope.

---

# 4. PHASE 2: THE APP — Weeks 2–8

This isn't a mobile-optimized website in a wrapper. It is a world.

### 4.1 — Technical Architecture

**Stack: Native iOS (Swift)**

Randy built the AC Blacksite app in Swift. It has cinematic onboarding and a hidden Space Invaders game. Swift is his strength. For Decoded, native iOS is the right call.

- **Cinematic experience:** SpriteKit for 2D games and Core Animation for fluid transitions. The onboarding sequence and drop animations perform better in native Swift.
- **Game performance:** The Vault's arcade games need responsive gameplay. Native delivers this.
- **Apple-favored:** The review team treats native apps favorably. This means smoother review and better featuring potential.
- **Skillset:** Randy knows Swift. Execution starts immediately.

**Why iOS-first?**

Decoded's target demographic skews heavily iOS. This is data.

- iOS users spend **2–3x more on luxury mobile commerce** than Android users
- Streetwear's core audience over-indexes on iPhone
- Supporting both platforms doubles complexity without doubling revenue

**Our recommendation:** Build native iOS first. Deliver the best experience to the audience most likely to buy. Once the app has traction, an Android version can be scoped.

We would rather give 100% of the right audience a world-class experience than give everyone a compromised one.

**Backend:**
- Shopify Storefront API for catalog and checkout
- Firebase/Supabase for user profiles and game scores
- Firebase Cloud Messaging (FCM) + APNs for push notifications
- Node.js server for game logic
- Hosted on Vercel or Railway

### 4.2 — The Cold Start: Cinematic Onboarding

When someone opens the app, they don't see a login form. They see a movie.

**Screen 1 — THE IGNITION**
A 911 Turbo tachometer fills the screen. The needle climbs to redline. Engine audio fades in. The Decoded logo burns into frame.

Text: *"This isn't a store."*

**Screen 2 — THE WORLD**
Split-screen montage. Porsche in motion. Noir Strata fabric close-up. Hands in prayer. City night aerial.

Text: *"This is a world. You're in it or you're watching."*

**Screen 3 — THE GATE**
Dark screen. A fingerprint scanner icon pulses. The user holds it until the vault unlocks. Then: "Choose Your Lane."

Two paths appear:

| **DECODED** | **DECODED NOIR** |
|-------------|-----------------|
| The main line. $25–$70. Streetwear with edge. | The luxury tier. $120–$150. Elevated. Exclusive. |
| *"I'm here for the drops."* | *"I'm here for the culture."* |

This fork segments the user base and validates the two-tier brand architecture. If 80% choose Noir, Decoded knows where to invest.

**Screen 4 — ENTER THE CODE**
Dark input field. Label: *"Enter your code name."*
Email capture below. CTA: **"DECODE."**
Push notification permission triggers after entry.

### 4.3 — App Screens (V1)

```
┌─────────────────────────────────────────────────────────┐
│                    DECODED APP — V1                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  HOME SCREEN — "THE DASHBOARD"                           │
│  ├── Dynamic hero (changes with each drop)               │
│  ├── Next drop countdown timer                           │
│  ├── Hidden element: Decoded logo pulses every 30s.      │
│  │   Tap it to discover "The Vault".                     │
│  └── Quick nav: Shop / Noir Lounge / Profile             │
│                                                          │
│  THE DROP ZONE                                           │
│  ├── Live drops with countdown timers                    │
│  ├── "Flash Raid" 15-minute windows                      │
│  ├── "Versus Drops" — two colorways, users vote,         │
│  │   loser gets locked                                   │
│  ├── Noir-only early access drops                        │
│  ├── App-exclusive drops                                 │
│  └── Real-time stock meter                               │
│                                                          │
│  THE VAULT — Hidden Games                                │
│  ├── "Midnight Run" — 2D top-down racer                  │
│  │   └── Score 5,000+ → "Check Engine" light triggers    │
│  │       access to a hidden product collection            │
│  ├── "The Confessional" — noir puzzle game                │
│  │   └── Answer questions from "806 The Show" podcast     │
│  │   └── Correct answers → 1-hour access code to a       │
│  │       flash discount                                   │
│  ├── Global leaderboard                                  │
│  └── "Driver's License" — shareable scorecard graphic     │
│                                                          │
│  SHOP                                                    │
│  ├── Full Shopify catalog sync                           │
│  ├── Product pages with descriptions and size guide       │
│  ├── Cart + Shopify checkout                              │
│  └── Real-time inventory sync                            │
│                                                          │
│  NOIR LOUNGE — VIP Section                               │
│  ├── Noir-exclusive content                              │
│  ├── Noir-only drops and colorways                       │
│  ├── Founder Q&A events                                  │
│  └── Membership tier display                             │
│                                                          │
│  PROFILE — "MY DECODED"                                  │
│  ├── Order history                                       │
│  ├── Membership tier + status                            │
│  ├── Game stats + earned rewards                         │
│  ├── Referral code                                       │
│  └── Push notification preferences                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4.4 — Drop Architecture

Decoded's drops are the app's heartbeat. Every drop follows a cadence:

**THE STANDARD DROP**
```
T-72 hours:  Push notification — "Something's coming. 72 hours."
             Blurred teaser on home screen.

T-1 hour:    Push notification — "1 hour. Are you ready?"
             App enters "Drop Mode." Dark theme intensifies.

T-0:         Push notification — "IT'S LIVE. GO."
             Product pages unlock. 10-minute cart timer.

T+24 hours:  Push to non-buyers — "You missed it. [X] pieces left."
             Push to buyers — "Your drop shipped. Welcome to the code."
             If sold out — "Gone. Next one's in [X] days."
```

**THE FLASH RAID**
No warning. Push notification hits: *"THE WINDOW IS OPEN. 15 MINUTES."*
The app opens to a countdown. When it hits zero, the Buy button appears. 15 minutes later, the button detonates. Miss it and it is gone.

**THE VERSUS DROP**
Two colorways drop simultaneously. Users vote. After 24 hours, the loser gets locked. The winner gets sold. This forces community interaction and creates tribalism.

**THE VAULT LOCK**
If a drop doesn't sell out within 48 hours, the remaining inventory gets vaulted. A cinematic "vault sealing" animation plays as the pieces disappear. "If you didn't grab it, it's gone." These vaulted pieces can resurface later in subscription boxes.

**APP-EXCLUSIVE DROPS**
1–2 drops per quarter available ONLY in the app. When followers see "APP ONLY" on IG, they download. This drives installs.

### 4.5 — Podcast Integration

"806 The Show" is an untapped engine. Here is how the app and podcast feed each other:

- **Verbal codes:** During episodes, the host drops a code word. Entering it in the app triggers an easter egg. A hidden discount or product unlocks.
- **"The Confessional" game:** Questions are drawn from podcast lore. This forces app users to listen and podcast listeners to download.
- **Episode drop sync:** New drops are teased at the end of episodes.

**The result:** A closed loop. Podcast drives app downloads. App drives podcast listens.

### 4.6 — Surprise Mechanics

**THE NOIR FLASH SALE**
Randomly, select Noir items flash at 20–30% off inside the app. No warning. No schedule. A push notification fires: *"NOIR FLASH. 10 MINUTES."* Users who are in the app see it.

**HIDDEN CONTENT**
Certain products are ONLY discoverable through exploration. They don't appear in the main shop grid. Tap the right element or score high enough in a game to see them. This rewards the obsessive fans.

### 4.7 — Community Tiers

| Tier | Access | How You Get In |
|------|--------|----------------|
| **DECODED** (Free) | Shop, drops, basic game, notifications | Download the app |
| **NOIR** ($15/month or $300 lifetime spend) | 24-hour early access. Noir Lounge. Noir-only drops. Free shipping. Birthday drop. Founder Q&A. | Subscribe or spend $300+ |
| **ELITE** (Earned — top 1%) | Vote on colorways. Exclusive "Elite" product line. Direct founder access. Name in credits. | Top game scorers. Invitation only. |

### 4.8 — App Store Submission

First-time app submissions receive extra scrutiny from Apple. The timeline accounts for this:
- 1–2 week review cycle
- Buffer for rejection-and-resubmission
- Required privacy policy and terms
- App Store screenshots and metadata

This is built into the Week 7–8 timeline. The app is code-complete by Week 6.

---

# 5. FUTURE EXPANSION: "THE CACHE" (Quarter 2+)

> *This section outlines a future revenue expansion. It is not part of the V1 build.*

Once the app has traction, "The Cache" launches.

### 5.1 — Concept

"The Cache" is not a box of clothes. It is a **physical DLC pack**. Every box contains an artifact that interacts with the app.

### 5.2 — Tiers

**DROP BOX — $65/quarter**
- 1 exclusive tee or accessory
- 1 mystery item
- 1 branded artifact
- Physical QR card that triggers an in-app unboxing animation

**NOIR BOX — $120/quarter**
- Everything in the Drop Box
- 1 Noir-tier item
- Premium packaging
- NFC-enabled card for early access
- Founder voice memo

**ELITE CRATE — $200/quarter (invite-only)**
- Everything in the Noir Box
- 1 limited-run numbered item
- 1 collab item
- VIP event access

### 5.3 — The Golden Ticket

1 in every 50 boxes contains a **Black Card**. This is metal and worth $500 in Decoded credit. Unboxing videos become content.

### 5.4 — Revenue Projection

| Tier | Subscribers | Annual Revenue |
|------|------------|----------------|
| Drop Box ($65) | 100 | $26,000 |
| Noir Box ($120) | 30 | $14,400 |
| Elite Crate ($200) | 10 | $8,000 |
| **Total** | **140** | **$48,400** |

At 200 subscribers, this stream reaches **$56,000+/year**.

---

# 6. PHASE 3: LAUNCH & GROWTH — Weeks 8–12

### 6.1 — App Launch Campaign

**Week 1 — The Tease:**
- Instagram Stories: daily 3-second clips. Dark. Moody. *"Coming."*
- TikTok: 15-second cinematic trailer.
- Podcast: "806 The Show" episode dedicated to the app. First verbal code dropped.
- Email blast: *"You're getting early access."*

**Week 2 — The Drop:**
- Launch day: simultaneous app-exclusive drop.
- Instagram Reel: screen-record of the onboarding.
- Push notification: *"The first drop is live."*

**Target:** 300–600 installs in Month 1.

### 6.2 — Instagram → App Funnel

The Instagram account becomes an app-install machine:

| Tactic | Mechanic |
|--------|----------|
| **Bio link** | Swap Shopify link for app download. |
| **"APP ONLY" drops** | Post teasers with "APP ONLY" watermark. |
| **Vault leaderboard** | "Top scorer wins a free Noir piece." |
| **Hidden codes** | Hide a code in a post image. |

### 6.3 — TikTok Launch

- Secure `@decoded.shop` or `@decodednoir`
- Content: Cinematic product clips and "I found a secret store" videos.
- Goal: Discovery. Find the audience that will download the app.

### 6.4 — Paid Acquisition (Month 3+)

**Not before the app proves it converts.**

| Channel | Monthly Budget | Creative |
|---------|---------------|----------|
| Meta (IG/FB) | $1,500 | Cinematic 15s app trailer. |
| TikTok | $750 | UGC-style: "I found a hidden game." |
| Retargeting | $500 | Website visitors who didn't buy. |

---

# 7. PHASE 4: LONG-TERM VISION — Month 3+

### 7.1 — App as Primary Sales Channel

By Month 6, the target is **60% of revenue through the app**. The website becomes the front window. Instagram becomes the megaphone.

### 7.2 — Data-Driven Drops

The app generates intelligence.
- Know which drops generate excitement BEFORE producing
- Schedule drops for peak engagement windows
- Quantify revenue lift of VIP tier
- Identify pricing issues instantly

### 7.3 — The Moat

The app becomes the thing competitors can't replicate.
- **Switching cost:** Game scores and Noir status mean moving to another brand is starting from zero.
- **Network effect:** More users means better leaderboards.
- **Identity:** "I'm Decoded Elite" becomes part of the customer's self-image.

---

# 8. RESPONSIBILITIES

| Content Type | Who Creates It | Who Manages It |
|-------------|---------------|----------------|
| Product photography | **Decoded** | Roviq formats for app |
| Product descriptions | **Roviq** | Decoded updates |
| Push notification copy | **Roviq** | Roviq sends |
| App hero images | **Roviq** designs | Roviq updates |
| Noir Lounge content | **Decoded** creates | Roviq publishes |
| Podcast verbal codes | **Decoded** drops code | Roviq programs unlock |
| Social media posts | **Decoded** films | Roviq advises |
| Game design | **Roviq** | Roviq maintains |

---

# 9. PRICING

Firm numbers.

### V1 BUILD — $8,500 (One-Time)

| Component | What's Included |
|-----------|----------------|
| **Website Triage** | Custom domain, luxury-minimal theme, product descriptions, About page, email capture. |
| **Cinematic Onboarding** | Tachometer boot sequence, "Hold to Unlock" gate, code name entry. |
| **Home Screen** | Dynamic hero, drop countdown, hidden Vault entry. |
| **Drop Zone** | Live drops, Flash Raid support, Versus Drop, Noir gating. |
| **The Vault** | "Midnight Run" racer + "The Confessional" puzzle game. Leaderboards. |
| **Shop** | Full Shopify sync. Cart. Checkout. |
| **Noir Lounge** | VIP content section. Tier display. |
| **Push System** | Drop alerts. Flash Raid alerts. Segmented by tier. |
| **Backend** | User data, game scores, memberships. |
| **App Store Submission** | Screenshots, metadata, privacy policy. |

**Payment terms:** 50% upfront ($4,250) / 50% on App Store submission ($4,250).

**Timeline:** 8 weeks.

### MONTHLY RETAINER — $2,500/month

| Deliverable | Details |
|------------|---------|
| **Drop Management** | Push notification sequences for every drop. |
| **Push Strategy** | Copywriting, segmentation, scheduling. |
| **App Content** | Hero updates. Noir Lounge publishing. |
| **Game Management** | Leaderboard monitoring. Reward coordination. |
| **Podcast Sync** | Programming verbal code unlocks. |
| **Analytics** | Monthly report: installs, conversion, game engagement. |
| **Social Strategy** | Content calendar tied to app. |
| **Maintenance** | Bug fixes, Shopify sync. |

**Minimum commitment:** 3 months.

**Scaling model:** If Decoded's monthly revenue exceeds $30K, retainer increases to $3,500/month. We charge more when we help generate more.

### TOTAL YEAR 1 INVESTMENT

| Item | Cost |
|------|------|
| V1 App Build | $8,500 |
| Monthly Retainer (12 months) | $30,000 |
| **Total** | **$38,500** |

**Projected Year 1 revenue:**
- Email/SMS flows: $15,000–$30,000
- App-driven sales: $40,000–$80,000
- Noir membership: $5,400+
- **Conservative total: $60,000–$115,000**

The investment pays for itself within the first two quarters.

---

# 10. WHY ROVIQ

### We've built this before.

Randy built the **AC Blacksite app**. It has a hidden Space Invaders game, cinematic onboarding, and native Swift UX. This isn't a concept. It is a proven playbook.

### Culture fit matters.

Roviq isn't a generic dev shop. We understand why MSCHF works. We understand that streetwear is about identity and scarcity. The Decoded app isn't a shopping cart with a game. It is a world.

### One team.

Most agencies give you a creative team that can't code or a dev shop with no brand sense. Roviq is strategy, design, and technology. We design the experience, build the app, and launch the campaigns. One partner.

### We succeed when Decoded succeeds.

The retainer model means we are in the war room for every drop. When the app drives its first $50K quarter, that is our win too.

---

# 11. NEXT STEPS

**One action:** Schedule a 30-minute call to align on Phase 1 kickoff.

Upon agreement:
1. Roviq sends SOW + invoice for 50% deposit ($4,250)
2. Website triage begins Day 1
3. App development begins Day 3

---

*10,000 streetwear brands have a Shopify store.*
*Nobody has a speakeasy.*
*Let's build yours.*

---

**Roviq — Strategy. Design. Technology.**
February 2026
