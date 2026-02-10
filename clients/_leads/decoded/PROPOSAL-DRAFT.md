# DECODED × ROVIQ

## *"10,000 streetwear brands have a Shopify store. None of them have a speakeasy."*

---

**Prepared for:** Decoded Shop  
**Prepared by:** Roviq  
**Date:** February 2026  
**Classification:** Confidential

---

# 1. THE DIAGNOSIS

We audited every layer of Decoded's digital presence: website, social, SEO, local search, paid media, competitive position, and revenue infrastructure. The findings were bad across the board.

| Dimension | Grade | The Problem |
|-----------|-------|-------------|
| Website & Digital Presence | **D-** | No custom domain. Zero product descriptions across 37+ SKUs. No About page. No brand story. No size guide. Default Shopify template. "Powered by Shopify" in the footer. |
| Social Media & Content | **D** | Instagram-only brand. No TikTok. 0.27% engagement on 20.4K followers. No content strategy. |
| Email / SMS / Retention | **F** | $0 revenue from email. $0 from SMS. No capture mechanism anywhere. Every customer who buys is immediately lost. |
| Paid Advertising | **N/A** | Nothing running. Zero paid acquisition. |
| Revenue Infrastructure | **Critical** | AOV ~$68. No upsells. No bundles. No abandoned cart recovery. No post-purchase flows. |

**The core problem isn't traffic. It's that Decoded has no way to keep the people who already care.**

Every visitor who doesn't buy on their first visit disappears forever. No email to follow up. No push notification to announce the next drop. No community to pull them back. The business model right now is: acquire a customer at full cost, sell them one item, never speak to them again.

But here's what the audit also showed: **the brand DNA is real.** "Decoded Noir." "Hand of God." "Kingdom Has Fallen." The automotive × faith × luxury aesthetic. The two-tier pricing architecture. The 911 Turbo visual language. "806 The Show" as a cultural anchor. These aren't manufactured. And genuine brand identity is the one thing money can't buy.

The gap isn't identity. It's infrastructure.

---

# 2. THE VISION: THE DIGITAL SPEAKEASY

Most brands would fix the Shopify store, run some Meta ads, and call it a day.

We're not proposing that.

We're proposing that Decoded stop competing as a clothing brand and start operating as a **digital speakeasy**: an invite-only, experience-first world where the app isn't a store, it's the front door to a culture. The clothes aren't products. They're trophies you earn by being inside.

**The model:** MSCHF built a $200M+ brand on one principle: every time you open the app, something different happens. You never know what you'll find. That creates compulsive engagement. People open the app not to buy, but to *see what's happening.* The buying follows naturally.

Decoded's frequent drops are the perfect fuel for this. Most brands struggle to create enough reasons for people to open their app. Decoded's owner drops constantly, and that's the engine.

**What this looks like in practice:**
- A cinematic boot sequence that feels like starting a 911 Turbo
- Real games hidden inside the app, not loyalty points. Actual arcade games.
- 15-minute "Flash Raid" drop windows that appear without warning
- Podcast episodes that contain verbal codes unlocking hidden app content
- "The Vault Lock," where unsold inventory gets permanently pulled and vaulted, never sold again
- Quarterly subscription boxes with NFC artifacts that unlock in-app experiences
- A tiered community where the deepest levels are earned, not bought

The website becomes a clean, dark, minimal luxury storefront (think Balenciaga) that exists to drive traffic to the app. The app is where the world lives.

**Nobody at Decoded's level has this. That's the point.**

---

# 3. PHASE 1: WEBSITE TRIAGE — Weeks 1–2

The current Shopify store isn't the main play, but it can't actively embarrass the brand while we build the app. This phase is surgical: fix the critical issues, establish the look, and add a clear funnel to the app.

### Deliverables

| Action | Why | Timeline |
|--------|-----|----------|
| **Custom domain** — acquire and connect `decoded.shop` or equivalent | `decodedshop.myshopify.com` signals "hobby project." A custom domain costs $15/year. | Day 1 |
| **Dark luxury redesign** — dark theme, sparse layout, full-bleed imagery | The website should feel like walking into a high-end boutique at night. Clean. Dark. Sparse. Think Balenciaga, not Zumiez. | Week 1 |
| **Product descriptions** — all 37+ SKUs get copy (fabric, fit, story, care) | Zero descriptions across the entire catalog is the single biggest conversion killer. This alone can lift conversion 30%+. | Week 1–2 |
| **Brand story / About page** | The founder's story IS the brand. Automotive roots. Faith. Why "Decoded." Why "Noir." One page. Cinematic. | Week 1 |
| **"Get the App" banner** — persistent CTA driving to app download | The website's job is to be a front window. The app is the store. Every page should funnel toward the download. | Week 1 |
| **Trust layer** — size guide, returns policy, social links, remove "Powered by Shopify" | Table stakes for selling $150 items online. | Week 1 |
| **Email capture** — Klaviyo popup + footer form + welcome flow | Bridges the gap until the app launches. Captures visitors who aren't ready to buy yet. 30–40% of DTC revenue comes from email. | Week 2 |
| **Hide sold-out SKUs** and clean up dead inventory | Removes dead-end pages that waste attention. | Day 1 |

**What this phase is NOT:** A full website rebuild. We're applying a dark luxury skin, fixing critical gaps, and turning the site into an app funnel. The app is where the real investment goes.

**Phase 1 Cost:** Included in the project scope (see Pricing).

---

# 4. PHASE 2: THE APP — Weeks 2–8

This is the core of the engagement. Not a mobile-optimized website in a wrapper. A world.

### 4.1 — Technical Architecture

**Stack: Native iOS (Swift)**

Randy built the AC Blacksite app in Swift: cinematic onboarding, a hidden Space Invaders game, premium native UX. Swift is his strength, and for Decoded, native iOS is the right call.

Why native matters here: SpriteKit handles the 2D games, Core Animation drives fluid transitions, and native haptics make interactions feel physical. The onboarding sequence, the Vault games, the drop animations, all of this runs significantly better in native Swift than in any cross-platform framework. The arcade games (Midnight Run, The Confessional) need responsive, smooth gameplay that native delivers without compromise. Apple's review team treats native apps more favorably, too. Smoother review, better featuring potential, cleaner integration with iOS APIs for NFC, push notifications, and haptics. And since Randy built AC Blacksite in Swift, there's no ramp-up time. Execution starts immediately.

**Why iOS-first (not both platforms)?**

Decoded's target demographic (luxury streetwear buyers, "the cool crowd," $120–$150 Noir-tier consumers) skews heavily iOS. This isn't opinion:

- iOS users spend 2–3x more on premium/luxury mobile commerce than Android users
- Streetwear's core audience (18–34, urban, culturally engaged) over-indexes on iPhone
- Supporting both platforms simultaneously doubles development complexity, testing surface, and maintenance cost without doubling revenue

React Native offers cross-platform convenience and OTA updates, but at the cost of native functionality. Games, cinematic animations, and haptics all take a hit. For an app where the *experience is the product*, that's a real tradeoff.

**Our recommendation:** Build native iOS first. Deliver the best possible experience to the audience most likely to buy. Once the app has traction and there's demonstrated demand from Android users, an Android version can be scoped as a future expansion, either as a Kotlin native build or a React Native port.

We'd rather give 100% of the right audience a great experience than give 100% of all audiences a mediocre one.

**Backend:**
- Shopify Storefront API for product catalog, inventory, and checkout
- Firebase/Supabase for user profiles, game scores, membership tiers, push tokens
- Firebase Cloud Messaging (FCM) + APNs for push notifications
- Lightweight Node.js server for game logic, drop scheduling, and notification orchestration
- Hosted on Vercel or Railway

### 4.2 — The Cold Start: Cinematic Onboarding

When someone opens the app for the first time, they don't see a login form. They see a movie.

**Screen 1 — THE IGNITION**
A 911 Turbo tachometer fills the screen. The needle climbs from 0 to redline. Engine audio fades in, low, throbbing, real. The Decoded logo burns into frame, letter by letter.

Text: *"This isn't a store."*

**Screen 2 — THE WORLD**
Split-screen montage: Porsche in motion / Noir Strata fabric close-up / hands in prayer / city night aerial. Quick cuts. Cinematic.

Text: *"This is a world. You're either in it, or you're watching."*

**Screen 3 — THE GATE**
Dark screen. A fingerprint scanner icon pulses. The user holds it until the vault unlocks, a heavy, physical-feeling interaction. Then: "Choose Your Lane."

Two paths appear:

| **DECODED** | **DECODED NOIR** |
|-------------|-----------------|
| The main line. $25–$70. Streetwear with edge. | The luxury tier. $120–$150. Elevated. Exclusive. |
| *"I'm here for the drops."* | *"I'm here for the culture."* |

This fork immediately segments the user base, personalizes the experience from the first interaction, and validates the two-tier brand architecture in real time. If 80% choose Noir, that tells Decoded where to invest.

**Screen 4 — ENTER THE CODE**
Dark input field. Blinking cursor. Label: *"Enter your code name."*
Email capture below. CTA: **"DECODE."**
Push notification permission triggers after entry.

### 4.3 — App Screens (V1)

```
┌─────────────────────────────────────────────────────────┐
│                    DECODED APP — V1                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  HOME SCREEN — "THE DASHBOARD"                           │
│  ├── Dynamic hero (changes with each drop/event)         │
│  ├── Next drop countdown timer                           │
│  ├── Hidden element: Decoded logo pulses every 30s —     │
│  │   tap it to discover "The Vault" (game entrance)      │
│  └── Quick nav: Shop / Noir Lounge / Profile             │
│                                                          │
│  THE DROP ZONE                                           │
│  ├── Live drops with countdown timers                    │
│  ├── "Flash Raid" 15-minute windows (surprise drops)     │
│  ├── "Versus Drops" — two colorways, users vote,         │
│  │   loser gets locked                                   │
│  ├── Noir-only early access drops (24hr head start)      │
│  ├── App-exclusive drops (never on website)              │
│  └── Real-time stock meter (true scarcity)               │
│                                                          │
│  THE VAULT — Hidden Games                                │
│  ├── "Midnight Run" — 2D top-down racer (911 Turbo       │
│  │   sprite dodging traffic on a dark highway)            │
│  │   └── Score 5,000+ → "Check Engine" light triggers    │
│  │       access to a hidden product collection            │
│  ├── "The Confessional" — noir puzzle game                │
│  │   └── Answer questions from "806 The Show" podcast     │
│  │       lore and biblical references in the designs      │
│  │   └── Correct answers → 1-hour access code to a       │
│  │       flash discount (20–30% off select items)         │
│  ├── Global leaderboard                                  │
│  └── "Driver's License" — shareable scorecard graphic     │
│      with user handle + score (designed for IG Stories)   │
│                                                          │
│  SHOP                                                    │
│  ├── Full Shopify catalog sync (Storefront API)           │
│  ├── Product pages with descriptions, multiple images,    │
│  │   size guide                                          │
│  ├── Cart + Shopify checkout (web view or native SDK)     │
│  └── Real-time inventory sync across app + website        │
│                                                          │
│  NOIR LOUNGE — VIP Section                               │
│  ├── Noir-exclusive content (design process,              │
│  │   fabric sourcing, founder notes)                     │
│  ├── Noir-only drops and colorways                       │
│  ├── Founder Q&A events (quarterly, in-app)              │
│  └── Membership tier display + progress                  │
│                                                          │
│  PROFILE — "MY DECODED"                                  │
│  ├── Order history                                       │
│  ├── Membership tier + status                            │
│  ├── Game stats + earned rewards                         │
│  ├── Referral code + invite tracking                     │
│  └── Push notification preferences                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4.4 — Drop Architecture

Decoded's frequent drops are the app's heartbeat. Every drop follows a structured cadence:

**THE STANDARD DROP**
```
T-72 hours:  Push notification — "Something's coming. 72 hours."
             Blurred teaser on home screen hero.
             Noir Lounge: unblurred preview for VIP members.

T-1 hour:    Push notification — "1 hour. Are you ready?"
             App enters "Drop Mode" — dark theme intensifies,
             ambient sound shifts, countdown dominates.
             Live viewer count shows how many people are waiting.

T-0:         Push notification — "IT'S LIVE. GO."
             Product pages unlock. Sizes + quantities visible.
             10-minute cart timer (urgency without manipulation).

T+24 hours:  Push to non-buyers — "You missed it. [X] pieces left."
             Push to buyers — "Your drop shipped. Welcome to the code."
             If sold out — "Gone. Next one's in [X] days."
```

**THE FLASH RAID**
No warning. Push notification hits: *"THE WINDOW IS OPEN. 15 MINUTES."*
The app opens directly to a countdown. When it hits zero, the Buy button appears. 15 minutes later, the button detonates (animation) and the product vanishes. Miss it, it's gone.

**THE VERSUS DROP**
Two colorways drop simultaneously. Users vote by tapping their side. After 24 hours, the loser gets locked, permanently unavailable. The winner gets sold. Forces community interaction, creates tribalism, generates organic debate content on social.

**THE VAULT LOCK**
If a drop doesn't sell out within 48 hours, the remaining inventory gets permanently pulled and vaulted. Never sold again. A cinematic "vault sealing" animation plays in the app as the pieces disappear from the catalog. "If you didn't grab it, it's gone forever." These vaulted pieces can resurface later as exclusive inclusions in subscription boxes, giving them a second life as collector's items. Every drop feels urgent because the alternative isn't a sale, it's permanent removal.

**APP-EXCLUSIVE DROPS**
1–2 drops per quarter available ONLY in the app. Not on the website. Not on Instagram. When followers see "APP ONLY" on IG, they download. This is the #1 driver for installs.

### 4.5 — Podcast Integration: The Cross-Platform Flywheel

"806 The Show" is an untapped engagement engine. Here's how the app and podcast feed each other:

**Verbal codes:** During episodes, the host drops a code word (e.g., *"Romans 12:2"*). Entering it in the app's search bar triggers an easter egg: the screen shifts, a hidden discount or exclusive product unlocks for a limited time.

**"The Confessional" game:** Questions are drawn directly from podcast lore and biblical references in the designs. This forces app users to listen to the podcast and podcast listeners to download the app.

**Episode drop sync:** New drops are teased at the end of podcast episodes. "If you're listening right now, the code is live in the app for the next hour."

The result: a closed loop where each platform drives the other. Podcast feeds app downloads. The app feeds podcast listens. Both feed purchases.

### 4.6 — Surprise Mechanics

**THE NOIR FLASH SALE (replaces "The Glitch")**
Randomly, once per week, for exactly 10 minutes, select Noir items flash at 20–30% off inside the app. No warning. No schedule. A push notification fires: *"NOIR FLASH. 10 MINUTES."* Users who are in the app see it. Users who aren't, miss it. This creates compulsive app-checking behavior without the financial and brand risk of giving product away at $0.

**HIDDEN CONTENT**
Certain products are ONLY discoverable through exploration. They don't appear in the main shop grid. Tap the right element, enter the right code, score high enough in a game, and they appear. Rewards the obsessive fans.

### 4.7 — Community Tiers

| Tier | Access | How You Get In |
|------|--------|----------------|
| **DECODED** (Free) | Shop, drops, basic game, push notifications | Download the app |
| **NOIR** ($15/month or auto-unlock at $300 lifetime spend) | 24-hour early access to ALL drops. Noir Lounge (exclusive content, behind-the-scenes, founder notes). Noir-only drops and colorways. Free standard shipping. Birthday drop. Quarterly founder Q&A. Discounted subscription boxes. | Subscribe or spend $300+ |
| **ELITE** (Earned — top 1%) | Vote on next colorway. Input on drop names. Exclusive "Elite" product line (ultra-limited, 10–20 units). Direct founder access. Name in app credits. | Top game scorers + highest lifetime spend. Invitation only. |

### 4.8 — App Store Submission

First-time app submissions with game mechanics and in-app purchases get extra scrutiny from Apple. The timeline accounts for this:
- 1–2 week review cycle
- Buffer for a rejection-and-resubmission round if needed
- Required privacy policy, terms of service, and age rating
- App Store screenshots, preview video, and metadata

This is built into the Week 7–8 timeline. The app is code-complete by Week 6; Weeks 7–8 are testing, submission, and review buffer.

---

# 5. FUTURE EXPANSION: "THE CACHE" — Quarterly Subscription Boxes (Quarter 2+)

> *This section outlines a future revenue expansion available once the app has traction. It is not part of the V1 build. It's a roadmap for where the platform goes next.*

Once the app is live and building an engaged user base (200+ active users), subscription boxes become a natural next step. The app collects the waitlist from Day 1, and when demand is validated, The Cache launches as an add-on revenue stream.

### 5.1 — Concept

"The Cache" is not a box of clothes. It's a **physical DLC pack** for the app, a quarterly supply drop that bridges the digital speakeasy into the real world. Every box contains a physical artifact that interacts with the app, turning the unboxing into a ritual, not just a delivery.

### 5.2 — Tiers

**DROP BOX — $65/quarter**
- 1 exclusive tee or accessory (box-only design, never sold elsewhere)
- 1 mystery item from recent drops (variant or overstock)
- 1 branded artifact (sticker pack, car freshener, enamel pin with Decoded branding)
- Physical QR card that triggers a cinematic unboxing animation in-app and unlocks a one-time discount code or hidden product access
- Printed lookbook/zine with upcoming drop previews

**NOIR BOX — $120/quarter**
- Everything in the Drop Box, PLUS:
- 1 Noir-tier item (exclusive Noir colorway or material, box-only)
- Premium packaging (matte black, foil stamp, magnetic closure)
- NFC-enabled card granting 48-hour early access to the next Noir drop
- QR code linking to a founder voice memo or video note
- Printed first-look at next season's Noir designs

**ELITE CRATE — $200/quarter (invite-only)**
- Everything in the Noir Box, PLUS:
- 1 limited-run numbered item (50 units max)
- 1 collab item or prototype piece
- VIP event access (virtual or local in-person)
- Direct vote on next quarter's box contents via app

### 5.3 — The Golden Ticket

1 in every 50 boxes, across all tiers, contains a **Black Card.** A physical metal card worth $500 in Decoded credit. This creates "Charlie and the Chocolate Factory" energy: unboxing videos become content. Social media explodes. Every box feels like it could be THE box.

### 5.4 — Future App Integration

When The Cache launches, these features get added to the app:

| Feature | Where It Lives |
|---------|---------------|
| **"My Box"** — subscription status, ship countdown, past box contents | Profile screen |
| **QR Unboxing Experience** — scan the card, trigger cinematic in-app reveal | Camera / QR scanner |
| **Box Countdown** — days until next box ships | Home screen (for subscribers) |
| **Box Preview** — blurred look at next quarter's box contents, 2 weeks before ship | Noir Lounge |
| **Waitlist Signup** — "Coming Soon: The Cache" banner + email capture | Home screen (pre-launch) |
| **"Cache Member" Badge** — visible on profile | Profile screen |

*App integration for The Cache will be scoped and priced separately when Decoded is ready to launch it.*

### 5.5 — Revenue Projection

| Tier | Subscribers (Conservative) | Revenue/Quarter | Annual |
|------|---------------------------|----------------|--------|
| Drop Box ($65) | 100 | $6,500 | $26,000 |
| Noir Box ($120) | 30 | $3,600 | $14,400 |
| Elite Crate ($200) | 10 | $2,000 | $8,000 |
| **Total** | **140** | **$12,100** | **$48,400** |

At scale (200+ subscribers), this revenue stream reaches $56,000+/year. Predictable, recurring, and separate from volatile drop revenue.

### 5.6 — Noir Member Discount

Subscription boxes are separate from Noir membership, but Noir members get a 15% discount on any box tier. This incentivizes both subscriptions and creates a natural upsell path.

### 5.7 — Recommended Launch Sequence (When Ready)

1. **App launch (Week 8):** "Coming Soon: The Cache" teaser appears in-app. Waitlist signup begins.
2. **Month 2–3:** Waitlist builds. 200+ signups = green light.
3. **Month 3:** First box ships. Unboxing content floods social.
4. **Ongoing:** Quarterly cadence. Each box is designed 6 weeks in advance. Box curation and fulfillment is Decoded's responsibility (or a 3PL); Roviq handles app integration, QR/NFC experiences, and marketing.

---

# 6. PHASE 3: LAUNCH & GROWTH — Weeks 8–12

### 6.1 — App Launch Campaign

**Week 1 — The Tease (pre-launch):**
- Instagram Stories: daily 3-second clips of app screens. Dark. Moody. No explanation. Just *"Coming."*
- TikTok: 15-second cinematic trailer with engine sound, app screens flashing, game footage. Text: *"Everything changes [date]."*
- Podcast: "806 The Show" episode dedicated to the app. First verbal code dropped: "Download the app and enter [code] in the first 48 hours for something nobody else gets."
- Email blast to Klaviyo list: *"You're getting early access. No one else."* App Store link 24 hours before public.

**Week 2 — The Drop:**
- Launch day: simultaneous app-exclusive drop. First product in the app is available NOWHERE ELSE.
- Instagram Reel: screen-record of the full onboarding experience. Authentic. Real.
- Live download counter on IG Stories: *"[X] people are in. Are you?"*
- Push notification to all Day 1 users: *"The first drop is live. You're the first to see it."*

**Target:** 300–600 installs in Month 1 (1.5–3% of 20K IG followers, conservative and industry-benchmarked). At 500 installs with 15–25% install-to-purchase conversion, that's 75–125 first-month orders through the app.

### 6.2 — Instagram → App Funnel

The Instagram account (20.4K followers) becomes an app-install machine:

| Tactic | Mechanic |
|--------|----------|
| **Bio link** | Swap Shopify link for app download link. The app IS the store now. |
| **"APP ONLY" drops** | Post product teasers on IG with "APP ONLY" watermark. Curiosity drives downloads. |
| **Vault leaderboard screenshots** | "Top scorer this week wins a free Noir piece. Play in the app." Competitive energy drives installs. |
| **Hidden codes in IG content** | Hide a 4-digit code in an Instagram post image. Enter it in the app for a surprise. Cross-platform engagement. |
| **Driver's License shares** | Game scorecard graphics designed for IG Stories. Users share their scores, others see the app. Organic discovery loop. |
| **Every Story ends with the app CTA** | Consistency compounds. |

### 6.3 — TikTok Launch

Secure `@decoded.shop` or `@decodednoir`. Content pillars: cinematic product clips with Noir aesthetic, night drives, moody lighting. "I found a secret store" videos showing hidden app features. Drop teasers with mystery, blurred reveals, countdowns. Unboxing content when subscription boxes launch.

Format: dark, moody, 7–15 second loops. Bass-heavy audio. Minimal text. The goal is discovery, not direct sales. Find the audience that will download the app.

### 6.4 — Paid Acquisition (Month 3+)

**Not before the app proves it converts.** Once baseline metrics are established:

| Channel | Monthly Budget | Creative |
|---------|---------------|----------|
| Meta (IG/FB) App Install Ads | $1,500 | Cinematic 15s app trailer. Audience: 18–34, streetwear + car culture interests, Boston metro + national. |
| TikTok App Install Ads | $750 | UGC-style: "I found a hidden game inside a streetwear app." |
| Retargeting | $500 | Website visitors who didn't buy → app install CTA. IG engagers → app install CTA. |

**Expected CPI:** $2–$5. At $68 AOV and 15–25% install-to-purchase rate, break-even happens on the first order.

### 6.5 — Contingency: Slower Adoption

If installs are lower than projected:
- Double down on podcast integration (free, high-conversion channel)
- Run a "founding member" campaign: first 200 app users get permanent Elite-tier pricing on subscription boxes
- Increase app-exclusive drop frequency to force IG followers into the app
- Reallocate paid budget from awareness to retargeting warm audiences
- Consider a strategic collab with a Boston-area artist or car culture figure (10K–50K followers) for a co-branded app-exclusive drop

200 engaged users with high LTV beats 2,000 passive downloads. The model works at smaller scale. It just takes longer to compound.

---

# 7. PHASE 4: LONG-TERM VISION — Month 3+

### 7.1 — App as Primary Sales Channel

By Month 6, the target:
- **60% of revenue through the app** (vs. website)
- Website becomes the "front window" for SEO and Google discovery
- Instagram becomes the megaphone driving awareness; the app drives conversion and retention

### 7.2 — Data-Driven Drops

The app generates intelligence the website never could:

| Data Point | Strategic Use |
|-----------|--------------|
| Push notification open rates by product category | Know which drops generate excitement BEFORE producing |
| Game engagement by time of day | Schedule drops for peak engagement windows |
| Noir Lounge vs. free tier purchase rates | Quantify revenue lift of VIP tier |
| "Choose Your Lane" onboarding split | Real-time market signal on where to invest |
| Product page views that don't convert | Identify pricing or sizing issues instantly |
| Referral code tracking | Know exactly which customers bring in new customers |
| App open frequency per user | Identify at-risk users for re-engagement pushes |

### 7.3 — Expanding the Experience

| Feature | Timeline | Investment |
|---------|----------|------------|
| Vault Game Season 2 (new mechanic, new rewards) | Quarter 2 | $2,000 |
| Android version (based on client demand) | Quarter 2–3 | $4,000–$6,000 |
| NFC-enabled physical "Black Card" artifacts for Elite tier | Quarter 3 | $1,500 |
| AR virtual try-on | Month 6+ | $3,000 |
| Community challenges ("Decoded Days," collective goals) | Quarter 2 | Included in retainer |

### 7.4 — The Moat

Long-term, the app becomes the thing competitors can't replicate.

**Switching cost.** Game scores, Noir status, earned rewards, referral networks, purchase history. Moving to another brand means starting from zero.

**Network effect.** More users means better leaderboards, more competition, more engagement.

**Content lock-in.** Behind-the-scenes content, founder Q&As, Noir exclusives exist nowhere else.

**Identity.** "I'm Decoded Elite" becomes part of how a customer sees themselves. No competitor can buy that.

---

# 8. CONTENT CREATION RESPONSIBILITIES

Clear delineation, no ambiguity:

| Content Type | Who Creates It | Who Manages It |
|-------------|---------------|----------------|
| Product photography / drop imagery | **Decoded** (owner shoots) | Roviq formats for app |
| Product descriptions + copy | **Roviq** (V1 website + app) | Decoded updates ongoing |
| Push notification copy | **Roviq** | Roviq sends |
| App hero images per drop | **Roviq** designs, using Decoded's product photos | Roviq updates |
| Noir Lounge content (BTS, founder notes) | **Decoded** creates raw content | Roviq curates and publishes |
| Podcast verbal codes | **Decoded** drops the code on-air | Roviq programs the unlock in-app |
| Social media posts (IG/TikTok) | **Decoded** films; Roviq provides templates + strategy | Roviq advises; Decoded posts |
| Subscription box curation + fulfillment (future) | **Decoded** (or 3PL) | Roviq handles app integration when launched |
| Game design + updates | **Roviq** | Roviq maintains |

---

# 9. PRICING

No ranges. Firm numbers.

### V1 BUILD — $8,500 (One-Time)

| Component | What's Included |
|-----------|----------------|
| **Website Triage** | Custom domain, luxury-minimal theme, product descriptions for all SKUs, About/brand story page, size guide, returns policy, email capture (Klaviyo), "Get the App" funnel |
| **Cinematic Onboarding** | Tachometer boot sequence, "Hold to Unlock" gate, "Choose Your Lane" fork, code name entry, push notification opt-in |
| **Home Screen** | Dynamic hero, drop countdown, hidden Vault entry |
| **Drop Zone** | Live drops with timers, Flash Raid support, Versus Drop mechanic, Noir early access gating, real-time stock display |
| **The Vault** | "Midnight Run" 2D sprite racer + "The Confessional" podcast puzzle game. Global leaderboard. Driver's License scorecard generator. |
| **Shop** | Full Shopify catalog sync via Storefront API. Product pages. Cart. Checkout. Real-time inventory sync. |
| **Noir Lounge** | VIP content section. Noir-only drops. Tier display. |
| **Profile / My Decoded** | Order history. Tier + status. Game stats. Referral code. Notification preferences. |
| **Push Notification System** | Drop alerts (72h → 1h → live → post-drop cadence). Flash Raid alerts. Noir Flash Sale alerts. Segmented by tier. |
| **Backend** | Firebase/Supabase for user data, game scores, memberships. Node.js for game logic and notification orchestration. |
| **App Store Submission** | iOS App Store. Screenshots, metadata, privacy policy, review cycle buffer. |

**Payment terms:** 50% upfront ($4,250) / 50% on App Store submission ($4,250).

**Timeline:** 8 weeks from kickoff to App Store submission.

| Week | Milestone |
|------|-----------|
| 1 | Project setup. Shopify API integration. Navigation skeleton. Website triage begins. |
| 2 | Onboarding screens (motion + design). Home screen. Countdown components. Website triage complete. |
| 3 | Shop screens (product list, detail, cart). Shopify checkout integration. |
| 4 | Drop Zone. Push notification setup (FCM + APNs). Notification triggers. |
| 5 | Midnight Run game (2D sprites + scoring + leaderboard). |
| 6 | The Confessional game. Noir Lounge. Profile. Polish. |
| 7 | Testing on device. App Store asset creation. Submission. |
| 8 | App Store review buffer. Bug fixes. Potential resubmission. |

### MONTHLY RETAINER — $2,500/month

| Deliverable | Details |
|------------|---------|
| **Drop Campaign Management** | Full push notification sequences for every drop (standard, Noir, Flash Raid, Versus). Campaign templates executed. |
| **Push Notification Strategy** | Copywriting, segmentation, scheduling, A/B testing. 8–12 pushes/month. |
| **App Content Updates** | Home screen hero updates per drop. Noir Lounge content publishing (2–4 pieces/month). Drop Zone management. |
| **Game Management** | Leaderboard monitoring. Reward fulfillment coordination. Quarterly rotation planning. |
| **Podcast Sync** | Programming verbal code unlocks for each "806 The Show" episode. |
| **Analytics & Reporting** | Monthly report: installs, DAU/MAU, push performance, conversion by drop, game engagement, Noir growth. |
| **Social Strategy** | Content calendar tied to app + drop schedule. Templates and copy for 3–4 IG posts/week. TikTok content direction. |
| **App Maintenance** | Bug fixes, minor feature additions, Shopify sync maintenance, OS update compatibility. |
| **Monthly Strategy Call** | 30-minute call. Review metrics, plan next month's drops, discuss roadmap. |

**Minimum commitment:** 3 months. Month-to-month after that.

**Scaling model:** If Decoded's monthly revenue exceeds $30K, retainer increases to $3,500/month to match expanded scope (more drops, more content, paid ad management included). We only charge more when we've helped generate more.

### TOTAL YEAR 1 INVESTMENT

| Item | Cost |
|------|------|
| V1 App Build | $8,500 |
| Monthly Retainer (12 months) | $30,000 |
| **Total** | **$38,500** |

*Subscription box app integration ("The Cache") is available as a future expansion once the app has traction. Pricing will be scoped separately when Decoded is ready to launch it.*

**Projected Year 1 revenue generated:**
- Email/SMS flows (basic Klaviyo): $15,000–$30,000
- App-driven sales (push notifications + drop urgency): $40,000–$80,000
- Noir membership revenue: $5,400+ (30 members × $15/month × 12)
- Subscription box revenue (if launched Q2+): $48,000+ potential
- **Conservative total: $60,000–$115,000 in directly attributable revenue (excluding subscription boxes)**
- **With subscription boxes (Q2+ launch): $108,000–$163,000+**

The investment pays for itself within the first two quarters, before subscription boxes even enter the picture.

---

# 10. WHY ROVIQ

### We've built this before.

Randy built the **AC Blacksite app**: a cinematic, gamified iOS experience with a hidden Space Invaders game, full cinematic onboarding flow with custom animation, premium home screen and event view. Native Swift, built to a high standard.

The Decoded app is the same philosophy applied to a different brand. This isn't a concept from a team that's never shipped. It's a proven playbook.

### Culture fit matters.

Roviq isn't a generic dev shop. We understand why MSCHF works. We understand why Corteiz does scavenger hunts. We understand why Hellstar's founder story is more valuable than their product line. Streetwear isn't about clothes. It's about identity, scarcity, and belonging. The Decoded app isn't a shopping cart with a game bolted on. It's a world built on those principles.

### One team. No handoffs.

Most agencies give you one of three things: a creative team that can't code, or a dev shop with no brand sense, or a marketing firm that doesn't understand product. Roviq does strategy, design, and technology in one team. We design the experience, build the app, launch the campaigns, read the analytics, and iterate. One partner. One vision.

### We win when Decoded wins.

The retainer model means we're in the war room for every drop, optimizing every push notification, watching every metric. When the app drives its first $50K quarter, that's our win too. The performance-based retainer scaling keeps our incentives aligned.

---

# 11. LEGAL & COMPLIANCE NOTES

Items we handle as part of the build:
- **Privacy policy** for data collection, push notifications, and analytics
- **Terms of service** for the app
- **App Store compliance** — game reward mechanics structured to avoid gambling classification (discount codes, not cash prizes; no purchase required to play)
- **FTC compliance** for promotional mechanics (Flash Sales, Golden Ticket disclosures)
- **Subscription auto-renewal disclosures** for Noir membership (required by Apple and Google)
- **Noir membership refund policy** — clear terms before launch

---

# 12. NEXT STEPS

**One action:** Schedule a 30-minute call to walk through this proposal, answer questions, and align on Phase 1 kickoff.

Upon agreement:
1. Roviq sends SOW + invoice for 50% deposit ($4,250)
2. Website triage begins Day 1
3. App development begins Day 3
4. First milestone check-in: end of Week 2

---

*10,000 streetwear brands have a Shopify store.*
*Nobody has a speakeasy.*
*Let's build yours.*

---

**Roviq**
February 2026
