# Cue Platform Strategy & AC Inner Circle Integration

**For:** Advanced Cultivators (AC)  
**Created:** February 2, 2026  
**Updated:** February 2, 2026 (incorporating Cue platform architecture)  
**Goal:** Deploy Cue as AC's budtender incentive platform and launch AC Inner Circle

---

## 🚨 CRITICAL UPDATE: Cue Platform Architecture

Cue is **NOT** a simple branded app. It is a **full SaaS platform** with multi-brand support that AC can deploy as its anchor customer.

### What Cue Actually Is

| Aspect | Previous Assumption | Reality |
|--------|---------------------|---------|
| **Architecture** | Single-brand AC app | Multi-tenant SaaS platform |
| **User Roles** | AC partners only | Platform Admin, Brand Admin, Dispensary Admin, Budtender |
| **Payments** | None | Real gift card payouts via Tremendous/Reloadly |
| **AI Features** | Basic content | Full course generation, quizzes, product moments |
| **Fraud Detection** | None | SHA-256 image hashing, velocity checks, audit trails |
| **Compliance** | Basic | Medical claim filtering, audit logging |
| **Business Model** | Free value-add | SaaS platform fees |

### Cue Platform Features (Production-Ready)

**🎯 Mission System**
- **Commission**: $2/unit (or custom) payouts
- **Tiered**: Hit thresholds for rewards (10 units = $20, 25 = $50)
- **Competition**: Ranked leaderboards with prizes

**📚 AI-Powered Training**
- Brand Foundation courses (auto-generated from website)
- Category Playbooks (Flower, Vape, Edible, etc.)
- Product Courses with certifications
- Product Moments (quick sales tips)
- AI-generated quizzes with configurable passing scores

**🤖 AI Content Generation**
- Course slides, quiz questions, cheat sheets
- Product moment content (What It Is, Why Different, Who It's For)
- Cover images and badges via Google Gemini
- Brand profile extraction via Firecrawl (evidence-based, no hallucinations)

**📱 Mobile App (React Native + Expo)**
- Mission progress with real-time leaderboards
- Photo proof submissions
- Training courses with certifications
- Reward tracking and redemption

**💼 Admin Dashboard**
- Brand management with AI profile setup
- Campaign (mission) creation and analytics
- Submission audit queue with fraud flags
- Reward tracking and payout export
- MQ Pipeline monitoring for background jobs

**🔒 Security & Compliance**
- Rate limiting (Redis-backed)
- Idempotency keys (prevents double payouts)
- Audit logging (all actions tracked)
- Fraud detection (duplicate images, velocity spikes, suspicious hours)
- Compliance filtering (blocks medical claims)
- Tenant isolation (brand/dispensary scoping)

---

## Part 1: Cue Platform Deployment for AC

### Deployment Strategy

AC has **three options** for using Cue:

#### Option A: AC as Anchor Tenant on Cue Platform
AC is the first brand on the Cue SaaS platform. Other brands may be added later.

**Pros:**
- Fastest deployment (use existing platform)
- No infrastructure costs for AC
- Continuous platform updates
- Future revenue if other brands join

**Cons:**
- "Powered by Cue" branding visible
- Less control over roadmap
- Platform fees ongoing

**Best For:** AC wants to launch quickly and doesn't need exclusive branding

---

#### Option B: White-Label Cue (Recommended)
AC licenses Cue technology and runs it as "AC Inner Circle" with full AC branding.

**Pros:**
- Full AC brand control
- No "Cue" visibility
- Custom features for AC only
- Competitive moat (other brands can't use same platform)

**Cons:**
- Higher upfront cost
- AC responsible for infrastructure
- Maintenance overhead

**Best For:** AC wants exclusive technology advantage and full brand control

---

#### Option C: Hybrid: AC-Exclusive Instance
AC gets dedicated Cue instance, but maintained by Cue team. No other brands.

**Pros:**
- AC-exclusive (no other brands)
- Cue team handles maintenance
- Custom integrations possible

**Cons:**
- Higher monthly cost
- Still dependent on Cue team

**Best For:** AC wants exclusivity without operational burden

### Recommendation: Start with Option A, Migrate to B

**Phase 1 (Months 1-3): Anchor Tenant**
- Deploy quickly on Cue platform
- Validate product-market fit
- Work out operational kinks

**Phase 2 (Months 4-6): Evaluate White-Label**
- If ROI positive, negotiate white-label license
- Build AC-exclusive features
- Full rebrand to "AC Inner Circle"

---

### App Store Submission (Cue Platform)

#### iOS App Store

**App Name Options:**
1. "Cue" (if Cue submits as platform)
2. "AC Inner Circle" (if white-label)
3. "Cue: Budtender Rewards" (descriptive)

**Category:** Business or Education (NOT Shopping)

**Content Rating:** 17+ (Mandatory for cannabis)

**Key Compliance Points:**
- NO direct cannabis sales (confirmed: Cue only tracks incentives)
- NO medical claims (Cue has compliance filtering)
- Age gate required (21+)
- State restrictions (Massachusetts focus)

**Screenshots Needed:**
| Screen | What to Show |
|--------|--------------|
| 1 | Mission feed (commission/tiered/competition cards) |
| 2 | Submit sale with photo upload |
| 3 | Training course with AI-generated slides |
| 4 | Real-time leaderboard |
| 5 | Rewards wallet with gift card redemption |
| 6 | Certification badges earned |

#### Google Play Store

**⚠️ Critical Policy Compliance:**

Google Play bans apps that "facilitate the sale of marijuana." Cue is compliant because:
- No sales transactions
- No product ordering
- Only incentive tracking and training

**Positioning for Google Play:**
> "Staff training and incentive platform for cannabis retail professionals. Track performance, complete training courses, and earn rewards."

---

### Legal Review Package for Cue

#### Screenshots for Legal Team

**Core Flow (Age Gate → Missions → Submit → Rewards):**
1. **Age Verification Screen** — Hard gate, 21+, state selection
2. **Mission Feed** — Available campaigns with earnings potential
3. **Mission Detail** — Rules, progress, leaderboard
4. **Submit Sale** — Photo upload, unit count, notes
5. **Training Course** — AI-generated content with compliance filtering
6. **Rewards Wallet** — Gift card redemption (Tremendous/Reloadly)
7. **Profile/Settings** — Privacy controls, terms access

#### Compliance Documentation

**Fraud Prevention (Show Legal):**
- Duplicate image detection (SHA-256 hashing)
- Submission velocity limits (30/hour, 100/day)
- Volume spike detection (5x average flags review)
- Suspicious hours flagging (3-5 AM submissions)

**Audit Trail:**
- Every action logged with userId, timestamp, IP
- Money events tracked (submission → approval → reward → payout)
- Admin actions logged (approvals, rejections, overrides)

**Compliance Filtering:**
- Medical claims blocked (treats, cures, therapy)
- Health benefit filtering (cancer, epilepsy, anxiety cure)
- Youth targeting prevention (kids, children, teens)
- False promise detection (guaranteed, 100% safe)

#### Required Legal Documents

1. **Privacy Policy**
   - Data collection: Phone, photos, sales data, training progress
   - Third parties: Firebase, Tremendous/Reloadly, OpenAI
   - User rights: Access, deletion, export
   - MA-specific privacy compliance

2. **Terms of Service**
   - Eligibility: 21+, licensed dispensary staff
   - Reward terms: Gift cards not cash, tax responsibility
   - Fraud consequences: Account termination, clawback
   - Dispute resolution

3. **Budtender Agreement**
   - Photo release (training photos may be used)
   - Accurate sales reporting
   - Confidentiality of brand content

4. **Dispensary Agreement**
   - Staff participation authorization
   - Data sharing consent
   - Co-marketing terms

---

### Launch Timeline

#### Pre-Launch (Weeks -4 to -1)

**Week -4: Infrastructure**
- [ ] Set production Tremendous/Reloadly API keys
- [ ] Configure Redis for rate limiting
- [ ] Set Sentry DSN for error tracking
- [ ] Generate production JWT secrets
- [ ] Configure Firebase Phone Auth

**Week -3: AC Setup on Platform**
- [ ] Create AC brand profile
- [ ] Run AI brand extraction (Firecrawl on advancedcultivators.com)
- [ ] Configure brand voice, positioning, compliance guardrails
- [ ] Upload AC product catalog (CSV import)
- [ ] Set up AC admin users

**Week -2: Content Creation**
- [ ] Generate Brand Foundation course (AI)
- [ ] Generate Category Playbooks (Flower, Pre-Roll, etc.)
- [ ] Create Product Moments for key SKUs
- [ ] Design first missions (commission structure)

**Week -1: Pilot Testing**
- [ ] Onboard 1-2 pilot dispensaries (Cannabis Healing?)
- [ ] Test full flow: mission → submit → approve → reward
- [ ] Verify gift card delivery
- [ ] Test fraud detection
- [ ] Legal review of all materials

#### App Store Submission (Weeks 1-3)

**Week 1: Submit**
- [ ] Build mobile app with EAS
- [ ] Submit to App Store for review
- [ ] Submit to Google Play for review
- [ ] Prepare demo accounts for reviewers

**Week 2-3: Review Cycle**
- [ ] Respond to reviewer questions
- [ ] Make required changes
- [ ] Resubmit if rejected
- [ ] **Expect 2-3 review cycles for cannabis-adjacent app**

#### Soft Launch (Week 4-6)

**Pilot: 3-5 AC Certified Stores**
- Cannabis Healing (Brian)
- CNA Stores (strong relationship)
- Kush Groove (high volume)
- Firebrand (Boston area)
- Peak Cannabis (if interested)

**Metrics to Track:**
- App download rate
- Mission participation rate
- Submission approval rate
- Training completion rate
- Reward redemption rate
- Fraud flag rate

#### Full Launch (Week 7+)

**Rollout to All AC Inner Circle Partners**
- 20-30 dispensaries
- Tiered onboarding (Inner Circle first, then Partners)
- Weekly check-ins with managers
- Monthly business reviews

---

## Part 2: AC Inner Circle + Cue Integration

### Program Structure

AC Inner Circle is **powered by Cue**. The Cue platform enables all Inner Circle benefits.

| Inner Circle Benefit | Cue Feature Enabling It |
|---------------------|------------------------|
| Staff training | AI-generated courses + certifications |
| Priority on drops | Mission notifications + early access campaigns |
| Pop-up support | Event missions with location-based submissions |
| Direct AC access | In-app messaging (future) + support portal |
| Marketing assets | Product Moments (downloadable content) |
| Staff incentives | Commission/tiered/competition missions |
| Performance tracking | Analytics dashboard |

### Tier System via Cue

**Tier 1: AC Inner Circle** (Minimum $5K/month orders)
- Unlimited budtender seats on Cue
- All mission types unlocked
- Priority support
- Custom training content requests
- Exclusive "Inner Circle only" missions
- Co-branded marketing assets

**Tier 2: AC Partner** (Minimum $2,500/month orders)
- Up to 10 budtender seats
- Standard missions
- Shared support
- Standard training content

**Tier 3: AC Retail** (Transactional)
- Up to 3 budtender seats
- Basic missions only
- Email support

### Cue Mission Strategy for AC

#### Mission Type 1: Commission (Always Active)
**Structure:** $2 per unit sold (or $3 for premium strains)

**Example:**
> "Sell any AC flower and earn $2/unit. Submit photo of receipt or stack. Max 50 units/week."

**Why it works:**
- Simple, easy to understand
- Immediate reward (no waiting for thresholds)
- Scales with effort

---

#### Mission Type 2: Tiered (Monthly)
**Structure:** Hit sales thresholds for bonus rewards

**Example:**
> "AC Flower Sales Challenge - December"
> - Sell 10 units → $20 bonus
> - Sell 25 units → $50 bonus
> - Sell 50 units → $100 bonus + AC swag box

**Why it works:**
- Encourages sustained effort
- Creates milestones to celebrate
- Top tier gets recognition + swag

---

#### Mission Type 3: Competition (Limited Time)
**Structure:** Ranked leaderboard with prizes

**Example:**
> "Mexican Haze Launch Week - Top Seller Wins!"
> - 1st place: $100 + strain-specific swag
> - 2nd place: $50
> - 3rd place: $25
> - All participants: Badge + entry in raffle

**Why it works:**
- Creates urgency (limited time)
- Gamification drives engagement
- Recognition for top performers
- Everyone gets something (participation reward)

---

#### Mission Type 4: Training Rewards
**Structure:** Complete training, earn reward

**Example:**
> "AC Brand Certification"
> - Complete 5-minute course
> - Pass quiz (80%)
> - Earn $5 + certification badge

**Why it works:**
- Ensures product knowledge
- Low time commitment
- Immediate reward for learning
- Badge creates credential

---

### AI Training Content Strategy

#### Auto-Generated Courses

**1. Brand Foundation** (Generated from AC website)
- AC origin story
- Mexican/Aztec heritage
- Quality philosophy
- Product overview

**2. Category Playbooks**
- Flower selling guide
- Pre-roll positioning
- Concentrate basics
- Edible guidance

**3. Product Deep Dives**
Per-strain courses:
- Genetics and lineage
- Terpene profile
- Effects and best uses
- Talk track for customers
- Common objections handling

#### Product Moments (Quick Tips)

For each key SKU, generate:
- **What It Is** — Product description
- **Why It's Different** — Key differentiators
- **Who It's For** — Ideal customer types
- **When to Recommend** — Sales scenarios
- **Your Talk Track** — Ready-to-use pitch

**Example: Mexican Haze**
> **What It Is:** A sativa-dominant strain with Mexican landrace genetics, 22% THC.
> 
> **Why It's Different:** We sourced original genetics from Oaxaca and cultivated it using our signature slow-cure process.
> 
> **Who It's For:** Creative professionals, social users, anyone who wants energy without anxiety.
> 
> **When to Recommend:** Morning/daytime use, before creative work, social gatherings.
> 
> **Talk Track:** *"If you want something that gets you going without the raciness, Mexican Haze is it. It's like coffee but smoother—great for when you need to be productive but chill."*

---

### Onboarding Flow

#### For Dispensary Managers

**Step 1: Partnership Agreement**
- Sign AC Inner Circle agreement
- Designate "Cue Admin" (manager)
- Provide staff phone numbers

**Step 2: Cue Account Setup (AC Internal)**
- Create dispensary in Cue admin
- Assign to AC brand
- Set tier level (Inner Circle/Partner/Retail)
- Upload staff list

**Step 3: Manager Onboarding Call (30 min)**
- Walk through Cue admin dashboard
- Show how to view staff progress
- Explain mission types
- Set goals for adoption

**Step 4: Staff Invite**
- Automatic SMS invites sent to staff
- Download link + verification code
- Manager announcement (email template provided)

#### For Budtenders

**Step 1: Download App**
- iOS: App Store
- Android: Google Play

**Step 2: Sign Up**
- Phone number
- Verification code (Firebase SMS)
- Name and dispensary selection

**Step 3: Age Verification**
- Confirm 21+
- Select state (Massachusetts)
- Accept terms

**Step 4: Welcome Mission**
- Complete "Getting Started" training
- Earn $5 welcome bonus
- See how missions work

**Step 5: Start Earning**
- Browse available missions
- Submit first sale
- Earn first reward

---

### Fraud Prevention Strategy

**Budtender Safeguards:**
| Risk | Cue Protection |
|------|---------------|
| Fake receipts | Photo proof required, manual audit |
| Double submission | Order ID tracking, idempotency keys |
| Volume manipulation | Velocity limits (30/hour), spike detection |
| After-hours fraud | 3-5 AM submissions flagged |
| Image reuse | SHA-256 hash detection (90-day window) |

**AC Admin Responsibilities:**
- Review flagged submissions daily (15 min)
- Audit random sample of approved submissions
- Monitor for collusion patterns
- Respond to disputes within 24 hours

---

## Part 3: Business Model & ROI

### Cue Platform Costs (Estimated)

**Option A: Anchor Tenant**
| Cost Component | Estimated Monthly |
|----------------|-------------------|
| Platform fee | $1,000-2,000 |
| Per-budtender fee | $5-10/user |
| AI generation | $200-500 (usage-based) |
| Gift card fees | 3-5% of reward volume |
| **Total (50 budtenders)** | **$2,500-4,000/mo** |

**Option B: White-Label License**
| Cost Component | Estimated |
|----------------|-----------|
| Setup fee | $10,000-25,000 |
| Monthly license | $3,000-5,000 |
| Infrastructure | $500-1,000 |
| Maintenance | Included or $1,000/mo |
| **Year 1 Total** | **$60,000-100,000** |

### AC Investment vs Return

**Assumptions:**
- 30 dispensary partners
- 5 budtenders per store = 150 active users
- Average mission: $2/unit, 10 units/month per budtender
- Training rewards: $5 per certification, 4 certifications/year

**Monthly Investment:**
| Item | Cost |
|------|------|
| Cue platform fees | $3,000 |
| Reward payouts (commissions) | $3,000 (150 users × 10 units × $2) |
| Training rewards | $250 |
| **Total Monthly** | **$6,250** |

**Expected Return:**
| Metric | Value |
|--------|-------|
| Sales lift vs non-incentivized | 25-40% |
| Incremental revenue (avg $500/order) | $15,000-25,000/month |
| Staff knowledge improvement | Measurable via quiz scores |
| Brand preference increase | Track AC vs competitor sales |
| **ROI** | **2-4x** |

### Break-Even Analysis

**Scenario: 20 Inner Circle stores, 100 budtenders**
- Monthly Cue cost: $4,000
- Monthly reward budget: $4,000
- **Total: $8,000/month = $96,000/year**

**Break-even:** $96,000 ÷ 25% lift = Need $384,000 in baseline AC sales across participating stores

**Reality Check:** If average store orders $10K/month, 20 stores = $200K/month baseline
- 25% lift = $50K additional monthly revenue
- $600K additional annual revenue
- **ROI: 6.25x** (spend $96K, gain $600K)

---

## Part 4: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Technical Setup:**
- [ ] Finalize Cue deployment option (A, B, or C)
- [ ] Configure production environment
- [ ] Set up gift card provider (Reloadly recommended)
- [ ] Configure Firebase Phone Auth
- [ ] Set Sentry error tracking

**AC Setup:**
- [ ] Create AC brand profile on Cue
- [ ] Run AI extraction on AC website
- [ ] Configure brand voice (Premium, Craft, Confident)
- [ ] Upload product catalog
- [ ] Set compliance guardrails

### Phase 2: Content Creation (Weeks 3-4)

**AI-Generated Content:**
- [ ] Generate Brand Foundation course
- [ ] Generate Category Playbooks (4 categories)
- [ ] Generate Product Moments for top 10 SKUs
- [ ] Create certification badges
- [ ] Design mission templates

**Legal/Compliance:**
- [ ] Legal review of AI-generated content
- [ ] Finalize privacy policy and terms
- [ ] Create budtender agreement
- [ ] Create dispensary partnership agreement

### Phase 3: Pilot (Weeks 5-6)

**Pilot Stores (3-5):**
- [ ] Cannabis Healing
- [ ] CNA Stores
- [ ] Kush Groove
- [ ] One additional TBD

**Pilot Activities:**
- [ ] Onboard managers
- [ ] Invite budtenders
- [ ] Launch first commission mission
- [ ] Launch first training course
- [ ] Daily check-ins for first week
- [ ] Weekly business reviews

**Metrics:**
- Download rate target: 70% of staff
- Mission participation: 50% active
- Submission approval rate: >90%
- Training completion: 60%

### Phase 4: App Store Launch (Weeks 7-9)

- [ ] Submit to App Store
- [ ] Submit to Google Play
- [ ] Handle review feedback
- [ ] Get approval

### Phase 5: Full Rollout (Weeks 10-12)

**AC Inner Circle Launch:**
- [ ] Announce at Superbowl event (Feb 8)
- [ ] Email to all AC Certified partners
- [ ] Onboard 20 stores over 4 weeks
- [ ] Weekly webinars for managers

**Ongoing:**
- [ ] Monthly new missions
- [ ] Quarterly training updates
- [ ] Continuous optimization based on data

---

## Part 5: Positioning & Messaging

### For Dispensary Managers

**Email Subject:** Earn More with AC: Introducing Cue

**Body:**
> [Manager Name],
> 
> Your budtenders are already selling AC product. Now they can get rewarded for it.
> 
> **Cue** is a new platform that lets your staff:
> - Earn cash rewards for every AC unit they sell
> - Get certified on AC products with quick training courses
> - Compete for bonuses and prizes
> - Access exclusive AC drops before anyone else
> 
> **For you:** Higher AC sales, better staff product knowledge, and zero cost.
> 
> **For your budtenders:** Extra income, bragging rights, and first access to limited strains.
> 
> We're rolling this out to our AC Inner Circle partners first. Want in?
> 
> Reply to this email and I'll send you the onboarding link.
> 
> — [AC Rep Name]

### For Budtenders

**In-Store Flyer:**
> 💰 **Sell AC, Get Paid**
> 
> Download Cue and start earning today:
> 1. Complete 5-minute AC training → **Earn $5**
> 2. Sell AC flower → **Earn $2/unit**
> 3. Hit monthly targets → **Earn up to $100 bonus**
> 
> **Plus:** First access to limited drops, exclusive swag, and competitions.
> 
> Ask your manager for the invite code or download now:
> [App Store] [Google Play]

### 30-Second Pitch (AC Sales Rep)

> "We're launching AC Inner Circle—it's our new partner program powered by Cue, a platform that trains your staff and pays them for selling AC. Your budtenders download the app, complete quick training, and earn cash for every unit they sell. We've seen 25-40% sales lifts in pilot stores. It's free for you, extra income for them, and more AC sales for everyone. Want to be one of our launch partners?"

---

## Part 6: Success Metrics

### Platform Metrics (Track Weekly)

| Metric | Target Month 1 | Target Month 3 |
|--------|---------------|----------------|
| Active budtenders | 50 | 150 |
| Monthly active rate | 60% | 70% |
| Mission participation | 40% | 60% |
| Submission approval rate | 90% | 95% |
| Training completion | 50% | 70% |
| Fraud flag rate | <5% | <3% |

### Business Metrics (Track Monthly)

| Metric | Target Month 3 | Target Month 6 |
|--------|---------------|----------------|
| AC sales lift (vs control) | 20% | 30% |
| Reorder velocity increase | 15% | 25% |
| New account conversions | 5 stores | 15 stores |
| Staff knowledge score | 75% | 85% |
| Net Promoter Score | 50 | 60 |

### ROI Metrics (Track Quarterly)

| Metric | Target |
|--------|--------|
| Platform cost as % of incremental revenue | <20% |
| Cost per incentivized sale | <$0.50 |
| Training cost per certified budtender | <$10 |
| Break-even month | Month 2-3 |

---

## Appendix

### A. Cue Technical Specs

**Backend:** Node.js + Express + TypeScript  
**Database:** PostgreSQL (Neon) + Drizzle ORM  
**AI:** OpenAI GPT-4 + Google Gemini  
**Queue:** BullMQ + Redis  
**Admin:** React + Vite + Radix UI  
**Mobile:** React Native + Expo 52  
**Auth:** Firebase Phone Auth + JWT  
**Storage:** Firebase Storage  

### B. Required Integrations

**Gift Cards (Choose One):**
- **Reloadly** (Recommended): Self-serve, instant, global
- **Tremendous**: Enterprise, requires approval

**Firebase:**
- Phone Auth enabled
- Storage bucket configured
- APNs key (iOS) / SHA fingerprints (Android)

**Optional:**
- Sentry (error tracking)
- Upstash (managed Redis)

### C. Demo Accounts for Testing

| Account | Type | Code |
|---------|------|------|
| demo-admin | Platform Admin | 000000 |
| brand-admin | Brand Admin (AC) | 000000 |
| demo | Budtender | 000000 |

### D. Key Contacts

| Role | Contact | For |
|------|---------|-----|
| Cue Platform | [To be filled] | Technical issues |
| AC Legal | [To be filled] | Compliance review |
| AC Sales | Randy | Partner onboarding |

---

**Document Status:** Updated with Cue platform architecture  
**Next Review:** Post-pilot analysis (Week 6)
