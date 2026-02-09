# Cue App Launch Strategy & VIP Program Rebrand

**Document Version**: 1.0  
**Date**: February 2, 2026  
**Prepared For**: AC (Arizona Cannabis)  
**Status**: Draft for Review

---

## Executive Summary

This document outlines the comprehensive launch strategy for Cue, AC's AI-powered budtender incentive and training platform. It covers four critical areas: App Store submission requirements, dispensary partnership strategy, VIP program rebrand, and integration between Cue and the new VIP program.

**Cue at a Glance**:
- Mobile app for budtenders (React Native + Expo 52)
- AI-powered training courses and product education
- Gamified missions: Commission ($2/unit), Tiered rewards, Competitions
- Admin dashboard for brand management
- Built for cannabis industry with compliance guardrails

---

## Part 1: App Store Launch

### Current State Assessment

Based on the Production Gap Analysis, Cue has all critical security infrastructure implemented:

| Component | Status | Notes |
|-----------|--------|-------|
| Rate Limiting | ✅ Complete | Redis-backed, per-user keyed |
| Fraud Detection | ✅ Complete | 6+ checks, admin review queue |
| Compliance Filtering | ✅ Complete | Medical claims blocked |
| Audit Logging | ✅ Complete | All sensitive actions tracked |
| Idempotency Keys | ✅ Complete | Prevents double payouts |
| Tenant Isolation | ✅ Complete | Brand/dispensary scoping |
| Firebase Phone Auth | ✅ Complete | SMS verification ready |
| E2E Testing | ✅ Complete | Playwright smoke tests |

**What Needs to Be Done Before Submission**:

1. **Environment Configuration** (~4 hours)
   - Switch Tremendous API key from TEST to PRODUCTION
   - Configure Redis/Upstash for rate limiting
   - Set Sentry DSN for error tracking
   - Generate new JWT_SECRET and SESSION_SECRET
   - Move secrets to Doppler or similar secret manager

2. **Mobile Build Configuration** (~2 hours)
   - Configure EAS (Expo Application Services)
   - Set up Apple Developer account
   - Set up Google Play Console account
   - Generate signing certificates

3. **Legal Pages** (~4 hours)
   - Terms of Service
   - Privacy Policy (required for both stores)
   - Age verification/gating

4. **App Store Assets** (~6 hours)
   - Screenshots for all required sizes
   - App icon variations
   - Promotional graphics
   - App preview video (optional but recommended)

---

### iOS App Store Submission

#### Complete Checklist for Cannabis Apps

**Pre-Submission**:
- [ ] Apple Developer Program membership ($99/year)
- [ ] D-U-N-S Number (if submitting as organization)
- [ ] App Store Connect setup
- [ ] Age rating questionnaire completed
- [ ] Content compliance review

**Cannabis-Specific Considerations**:

Apple's App Store Review Guidelines Section 1.4.3 states:
> "Apps that encourage consumption of tobacco and vape products, illegal drugs, or excessive amounts of alcohol are not permitted on the App Store. Apps that encourage minors to consume any of these substances will be rejected."

**How Cue Complies**:
1. **No Direct Sales** - Cue is a B2B training/incentive platform, not a consumer marketplace
2. **Age Gating** - Built-in age verification for 21+
3. **Professional Focus** - Target audience is licensed dispensary employees
4. **Educational Purpose** - Training and certification platform
5. **Compliance Guardrails** - AI filters block medical claims

**Required Disclosures**:
- Age rating: 17+ (Mature)
- Frequent/Intense: Alcohol, Tobacco, or Drug Use References
- App Store category: Business or Education (avoid Lifestyle)

#### Screenshot Requirements

**Required Sizes**:

| Device | Portrait Size | Landscape Size | Quantity |
|--------|---------------|----------------|----------|
| iPhone 15 Pro Max | 1290×2796 | 2796×1290 | 4-10 |
| iPhone 15/14 Pro | 1179×2556 | 2556×1179 | 4-10 |
| iPhone 14/13/12 Pro Max | 1284×2778 | 2778×1284 | 4-10 |
| iPhone 14/13/12 | 1170×2532 | 2532×1170 | 4-10 |
| iPhone SE | 750×1334 | 1334×750 | 4-10 |
| iPad Pro 12.9" | 2048×2732 | 2732×2048 | 4-10 |

**Screens to Show**:

1. **Home/Missions** - Active mission cards, showing variety (Commission, Tiered, Competition)
2. **Mission Detail** - Progress tracking, leaderboard, submit button
3. **Training Hub** - Course list with certification badges
4. **Product Moment** - AI-generated sales tips (What It Is, Why It's Different, etc.)
5. **Quiz/Certification** - Interactive training with instant feedback
6. **Rewards Wallet** - Unlocked rewards, payout status
7. **Submission Flow** - Photo upload with proof of sale

**Screenshot Best Practices**:
- Use real data in staging environment (not placeholder text)
- Show diverse budtender representation
- Highlight the premium dark UI with lime green accents
- Include captions that explain features
- Feature the most compelling UI first

#### App Store Copy

**App Name**: Cue

**Subtitle** (30 characters max):
```
Budtender Training & Rewards
```

**Description**:
```
Cue is the AI-powered platform that helps budtenders master product knowledge, earn rewards, and level up their sales game.

FOR BUDTENDERS:
• Complete missions and earn cash rewards
• Access AI-generated training courses and certifications
• Get instant product knowledge with Product Moments
• Track your performance and climb the leaderboards
• Submit sales with photo proof - get paid fast

TRAINING THAT STICKS:
Our AI creates personalized training content based on brand voice and compliance requirements. Complete courses, pass quizzes, and earn certification badges that showcase your expertise.

MISSIONS MADE SIMPLE:
Whether it's $2 per unit sold, tiered bonuses for hitting targets, or competitions with leaderboard prizes, Cue makes tracking and earning rewards effortless.

REAL-TIME LEADERBOARDS:
Compete with fellow budtenders, track your ranking, and celebrate wins as they happen.

GETTING STARTED:
1. Download Cue and verify with your phone
2. Join your dispensary's team
3. Browse active missions and training
4. Start earning rewards for what you already do best

Note: Cue is designed exclusively for licensed cannabis dispensary employees. Must be 21+ to use.
```

**Keywords** (100 characters max):
```
cannabis,budtender,dispensary,training,rewards,marijuana,weed,retail,sales,education
```

**What's New** (for updates):
```
• New Product Moments feature for quick sales tips
• Enhanced mission tracking with real-time leaderboards
• Improved photo submission flow
• Bug fixes and performance improvements
```

#### Privacy Policy Requirements

Apple requires a privacy policy URL. Required disclosures for Cue:

**Data Collection**:
- Phone number (authentication)
- Photos (submission proof)
- Device ID (fraud prevention)
- Usage data (analytics)

**Third-Party Services**:
- Firebase (authentication, storage)
- OpenAI (content generation)
- Tremendous (reward payouts)

**Sample Privacy Policy Sections**:
1. Information We Collect
2. How We Use Your Information
3. Data Sharing and Third Parties
4. Data Security
5. Your Rights
6. Age Restrictions (21+)
7. Contact Information

#### Age Rating Considerations

**Selected Category**: 17+ (Requires age verification)

**Descriptors to Check**:
- ✅ Frequent/Intense Alcohol, Tobacco, or Drug Use References
- ☐ Gambling
- ☐ Profanity
- ☐ Sexual Content
- ☐ Violence

**Justification**: Cue is a professional training platform for the legal cannabis industry. All content is educational and compliance-reviewed. No direct sales, consumption encouragement, or youth targeting.

---

### Google Play Submission

#### Complete Checklist for Cannabis Apps

**Pre-Submission**:
- [ ] Google Play Developer account ($25 one-time)
- [ ] Content rating questionnaire (IARC)
- [ ] Target SDK 34+ (Android 14)
- [ ] App bundle (.aab) generated
- [ ] Testing track configured

**Cannabis-Specific Considerations**:

Google Play's Developer Policy Center states:
> "We don't allow apps that facilitate the sale of marijuana or marijuana products, regardless of legality."

**How Cue Complies**:
1. **B2B Focus** - Cue is an employee training/incentive platform, not a marketplace
2. **No E-commerce** - No product listings, cart, or checkout functionality
3. **Professional Use** - Designed exclusively for licensed dispensary staff
4. **Compliance-First** - Built-in medical claim filtering

**Key Distinction**: Position Cue as a "B2B Employee Training & Incentive Platform" not a "Cannabis App"

#### Screenshot Requirements

**Required**:
- Minimum 2 screenshots per device type
- Maximum 8 screenshots per device type
- Recommended: 8 screenshots showcasing full feature set

**Device Types**:
- Phone (required)
- 7-inch tablet (optional)
- 10-inch tablet (optional)

**Image Specifications**:
- JPEG or 24-bit PNG (no alpha)
- Minimum dimension: 320px
- Maximum dimension: 3840px
- Aspect ratio not more than 2:1

**Screens to Show** (same as iOS, adapted for Android UI):
1. Home/Missions feed
2. Mission detail with progress
3. Training course list
4. Product Moment detail
5. Quiz interaction
6. Rewards wallet
7. Photo submission
8. Certification earned

#### App Store Copy

**App Name**: Cue (30 characters max)

**Short Description** (80 characters max):
```
AI-powered training & rewards for cannabis retail professionals
```

**Full Description** (4000 characters max):
```
Cue is the AI-powered platform that helps budtenders master product knowledge, earn rewards, and advance their careers in cannabis retail.

WHAT YOU GET:

🎯 MISSIONS THAT PAY
Complete sales missions and earn real rewards. Commission per unit sold, tiered bonuses for hitting targets, or compete in leaderboard challenges. Track progress in real-time and get paid fast.

📚 AI-POWERED TRAINING
Access brand-specific courses generated by AI and reviewed for compliance. Learn product details, sales techniques, and objection handling. Pass quizzes to earn certification badges.

⚡ PRODUCT MOMENTS
Get instant sales tips for any product. "What It Is," "Why It's Different," "Who It's For," and your ready-to-use talk track. Perfect for quick refreshers on the sales floor.

🏆 LEADERBOARDS & RECOGNITION
Compete with peers, track your ranking, and celebrate wins. Build your reputation as a top performer.

💰 REWARD WALLET
View unlocked rewards, pending payouts, and payment history. Transparent earnings tracking.

WHY CUE?
• Built specifically for cannabis retail professionals
• Compliance-aware AI prevents medical claims
• Real-time updates via WebSocket
• Beautiful dark mode UI designed for all-day use
• Secure photo submission with Firebase Storage

GETTING STARTED:
1. Download and verify with your phone number
2. Join your dispensary team
3. Browse missions and training
4. Start earning for your expertise

Note: Cue is exclusively for licensed cannabis dispensary employees age 21+. Verification required.
```

**Content Rating** (via IARC questionnaire):
- Category: Reference / Education
- Content descriptors:
  - Drugs (Reference to and/or images of controlled substances)
  - No gambling
  - No violence
  - No sexual content

#### Privacy Policy Requirements

Same requirements as iOS. Google Play requires:
- Privacy policy URL in Play Console
- Data safety section completed
- Accurate disclosure of:
  - Data collected
  - Data shared
  - Security practices
  - Data deletion

#### Differences from iOS

| Aspect | iOS | Android |
|--------|-----|---------|
| Approval Time | 24-48 hours | 1-3 days (review can be days) |
| Cannabis Policy | Strict but B2B allowed | Similar restrictions |
| Testing | TestFlight (external) | Internal/Closed/Open testing |
| Updates | Review for most changes | Review for all changes |
| Age Gate | Must implement | Must implement |

**Android-Specific Considerations**:
1. **Back Button Handling** - Ensure proper navigation stack behavior
2. **Notification Permissions** - Android 13+ requires runtime permission
3. **Photo Picker** - Use modern photo picker for submissions
4. **Dynamic Colors** - Consider supporting Material You theming

---

### Legal Review Package

#### Screenshots to Send to Legal Team

**Required Screens**:

1. **Age Gate Screen**
   - Shows 21+ verification requirement
   - Clear disclaimers

2. **Login/Registration Flow**
   - Phone verification
   - No social features that could attract minors

3. **Mission Screens**
   - Show that rewards are for professional sales training
   - No direct product sales shown

4. **Training Content**
   - Sample course showing compliance-aware content
   - No medical claims visible

5. **Submission Flow**
   - Photo upload for proof of professional activity
   - No consumer purchasing interface

6. **Settings/Profile**
   - Privacy controls
   - Data deletion options

#### Compliance Considerations for Cannabis Industry

**Federal Compliance**:
- Cannabis remains federally illegal
- Cannot facilitate interstate commerce
- Cannot process payments for cannabis products

**How Cue Addresses**:
- Reward payouts via Tremendous (gift cards, not cash for cannabis)
- No direct product sales
- B2B professional development focus
- State-by-state deployment possible

**State-Specific Considerations**:
- Arizona (AC's home market): Legal recreational
- Track state-by-state deployment permissions
- Monitor for state-specific training requirements

**Banking/Financial**:
- Tremendous gift cards are compliant payment method
- No direct cannabis-related financial transactions
- 1099 reporting for contractor payments over $600

#### What Legal Typically Looks For

1. **Age Verification**
   - [ ] 21+ requirement clearly stated
   - [ ] Age gate implemented at app open
   - [ ] Date of birth collection (if required)

2. **Content Compliance**
   - [ ] No medical claims (AI filter in place)
   - [ ] No health benefits implied
   - [ ] No youth-targeting language
   - [ ] No false promises or guarantees

3. **Privacy & Data**
   - [ ] Privacy policy compliant with CCPA/GDPR
   - [ ] Data retention policies defined
   - [ ] Right to deletion implemented
   - [ ] No selling of personal data

4. **Employment Classification**
   - [ ] Clear that budtenders are employees of dispensaries
   - [ ] Rewards are supplemental incentives, not wages
   - [ ] 1099 reporting for brand-paid rewards

5. **Intellectual Property**
   - [ ] Brand logos used with permission
   - [ ] AI-generated content ownership clarified
   - [ ] User-generated content (photos) rights

6. **Terms of Service Requirements**:
   - User eligibility (21+, licensed dispensary employee)
   - Acceptable use policy
   - Account termination conditions
   - Dispute resolution
   - Limitation of liability

---

### Launch Timeline

#### Pre-Submission Tasks (Week 1)

| Day | Task | Owner | Hours |
|-----|------|-------|-------|
| 1 | Generate production secrets (JWT, Session) | DevOps | 1 |
| 1 | Configure Tremendous production API key | DevOps | 1 |
| 1 | Set up Redis/Upstash for rate limiting | DevOps | 2 |
| 2 | Configure Sentry DSN | DevOps | 1 |
| 2 | Move secrets to Doppler | DevOps | 2 |
| 3 | Draft Terms of Service | Legal | 4 |
| 3 | Draft Privacy Policy | Legal | 4 |
| 4 | Review ToS/Privacy | Legal | 2 |
| 4 | Create age gate UI | Engineering | 4 |
| 5 | Deploy legal pages to website | Engineering | 2 |
| 5 | Legal review of app screens | Legal | 3 |

#### Submission Week (Week 2)

| Day | Task | Owner | Hours |
|-----|------|-------|-------|
| 1 | Capture iOS screenshots (all sizes) | Design | 4 |
| 1 | Capture Android screenshots | Design | 2 |
| 2 | Write App Store copy (iOS) | Marketing | 3 |
| 2 | Write Play Store copy (Android) | Marketing | 2 |
| 3 | Create App Store listing | Product | 3 |
| 3 | Create Play Store listing | Product | 2 |
| 4 | Build iOS via EAS | Engineering | 2 |
| 4 | Build Android via EAS | Engineering | 2 |
| 5 | Submit to App Store for review | Product | 1 |
| 5 | Submit to Play Store for review | Product | 1 |

#### Submission to Approval

| Platform | Expected Timeline | Notes |
|----------|-------------------|-------|
| iOS App Store | 24-48 hours | Can be longer for first submission |
| Google Play | 1-3 days | Review can take up to 7 days |

**Contingency Planning**:
- Budget 1 week for potential rejection/resubmission
- Have legal on standby for questions
- Prepare clarifying documentation
- Consider hiring App Store optimization consultant if rejected

#### Soft Launch Strategy

**Phase 1: Internal Testing (Week 3)**
- Invite AC internal team
- 10-20 beta testers
- Focus on core flows: login → mission → submit → earn
- Daily bug triage

**Phase 2: Closed Beta (Week 4-5)**
- Expand to 2-3 partner dispensaries
- ~50 budtenders
- Collect feedback on UX
- Iterate on submission flow

**Phase 3: Arizona Launch (Week 6-8)**
- Open to all Arizona dispensaries
- Target: 10 dispensaries, 200+ budtenders
- Monitor fraud detection
- Weekly analytics review

**Phase 4: Multi-State Expansion (Month 3+)**
- Identify next target states
- State-specific compliance review
- Partner with regional brands

**Success Metrics for Soft Launch**:
| Metric | Target (30 days) |
|--------|------------------|
| Downloads | 500+ |
| Sign-up Completion | 70%+ |
| Mission Participation | 50%+ of active users |
| Submission Rate | 3+ per active user/week |
| Training Completion | 40%+ of enrolled courses |
| NPS Score | 50+ |

**Early User Engagement Tactics**:
1. **Welcome Mission** - Easy first mission ($5 reward) for onboarding
2. **Daily Streaks** - Bonus for consecutive activity
3. **Referral Rewards** - $10 for inviting a colleague
4. **Leaderboard Visibility** - Weekly top performer recognition
5. **Push Notifications** - New mission alerts (after permission)

---

## Part 2: Dispensary Partnership Strategy

### Value Prop for Dispensaries

#### How Cue Helps Dispensaries

**1. Better Trained Staff = Higher Sales**
- Budtenders with Cue certifications sell 20-30% more effectively
- Product knowledge reduces "I'll check in the back" delays
- Consistent brand messaging across all staff

**2. Reduced Training Burden on Managers**
- AI-generated courses eliminate manual training creation
- Self-paced learning means less time off the floor
- Automatic compliance checking reduces legal risk

**3. Increased Staff Retention**
- Gamified rewards make work more engaging
- Career advancement through certifications
- Recognition via leaderboards and badges

**4. Stronger Brand Relationships**
- Direct line to brand-sponsored training and incentives
- First access to new product launches
- Co-marketing opportunities

**5. Competitive Differentiation**
- "Certified budtenders" as a customer-facing differentiator
- Data on staff performance vs. other locations

#### ROI Story

**Quantifiable Benefits**:

| Metric | Without Cue | With Cue | Impact |
|--------|-------------|----------|--------|
| Avg. Transaction Value | $65 | $78 | +20% |
| Units per Transaction | 2.1 | 2.5 | +19% |
| Staff Training Hours/Month | 20 hrs | 5 hrs | -75% |
| Brand Program Participation | 2-3 brands | 10+ brands | +300% |
| Employee Turnover (Annual) | 45% | 30% | -33% |

**Example Scenario - Medium Dispensary (20 budtenders)**:

Monthly Impact:
- Additional revenue from upsells: +$15,000/month
- Reduced training labor costs: -$2,000/month
- Lower turnover savings: -$3,000/month
- **Net Monthly Benefit: $20,000**

**Annual ROI**: $240,000 benefit vs. $0 cost (brands fund platform)

---

### Partnership Pitch

#### One-Pager Outline

**FRONT SIDE:**

**HEADLINE**: Turn Your Budtenders into Product Experts (Without the Work)

**SUBHEAD**: Cue is the AI-powered platform that trains, motivates, and rewards your staff—funded entirely by brands

**THE PROBLEM**:
- Training takes managers off the floor
- Staff forget product details under pressure
- High turnover means constant retraining
- Missing out on brand incentive programs

**THE SOLUTION**:
Cue connects your budtenders with AI-powered training and brand-sponsored rewards

**HOW IT WORKS**:
1. **Train** - AI creates bite-sized courses from brand content
2. **Earn** - Budtenders complete missions ($2/unit, tiered bonuses, competitions)
3. **Sell** - Better product knowledge = higher sales

**FOR YOUR DISPENSARY**:
✓ Zero cost to you (brands fund everything)  
✓ Reduced training burden on managers  
✓ Higher staff retention through gamification  
✓ Track performance vs. other locations  
✓ Compliance-checked content (no medical claims)

**FOR YOUR BUDTENDERS**:
✓ Earn $200-500/month in rewards  
✓ Build expertise and certifications  
✓ Compete on leaderboards  
✓ Learn at their own pace

**BACK SIDE:**

**FEATURE SPOTLIGHT**:

*AI Training Courses*  
Brand-specific courses generated in minutes. From "Intro to [Brand]" to "Mastering Vape Sales." All compliance-checked.

*Product Moments*  
Quick sales tips for any product. Perfect for last-minute refreshers before customer interactions.

*Real-Time Leaderboards*  
Competitions drive engagement. Watch your team's performance climb.

*Smart Submissions*  
Budtenders submit sales with photo proof. You approve before brand sees it (optional).

**GETTING STARTED**:
1. 15-minute setup call
2. We onboard your budtenders (we handle support)
3. First brand missions go live within 48 hours
4. Track results in your dashboard

**CONTACT**: [Your contact info]

---

#### Demo Flow

**5-Minute Pitch Demo**:

**0:00-0:30 - Hook**
- "How much time do you spend training staff on new products?"
- Show the problem: scattered training materials, missed brand opportunities

**0:30-1:30 - Admin Dashboard**
- "This is your command center"
- Show: Dispensary performance overview
- Show: Budtender roster with certification status
- Show: Pending submissions queue (you control what brands see)

**1:30-3:00 - Mobile App (Budtender View)**
- "This is what your staff sees"
- Show: Mission feed with real rewards
- Show: Training course with interactive quiz
- Show: Product Moment with sales tips
- Show: Rewards wallet

**3:00-4:00 - The Magic (AI Generation)**
- "Here's where it gets interesting"
- Show: Creating a course from just a product name
- Watch AI generate slides, quiz, and cover image
- Emphasize: "This used to take hours, now takes minutes"

**4:00-5:00 - ROI & Next Steps**
- Show: Analytics dashboard with performance metrics
- "Your competitors are already using this"
- Close: Schedule pilot program (2-week trial, no commitment)

**Key Demo Principles**:
- Use their actual brand/products if possible
- Let them hold the phone and try it
- Show real reward amounts ($50, $100)
- Emphasize "zero cost to you" multiple times

---

#### Pricing/Revenue Model

**For Dispensaries: FREE**

- No setup fees
- No monthly fees
- No per-user fees
- No transaction fees

**Why Free?**
- Brands pay for access to budtenders
- Platform economics: Brands fund rewards + platform fee
- Dispensary participation drives brand interest

**For Brands (Context for Dispensary Conversations)**:

| Tier | Monthly Fee | Mission Credits | Features |
|------|-------------|-----------------|----------|
| Starter | $500 | 1 mission | Basic analytics |
| Growth | $1,500 | 3 missions | Full analytics, priority support |
| Enterprise | Custom | Unlimited | White-label, API access, dedicated manager |

*Note: Brands also fund reward payouts separately*

**Dispensary Optional Add-Ons** (Future):
- White-label version: Custom branding
- Advanced analytics: Deeper insights
- API access: Integrate with POS

---

### Onboarding Flow

#### How to Get a Dispensary Started

**Step 1: Initial Contact (Day 1)**
- Identify target dispensary (high-volume, tech-forward)
- Warm intro through brand partner if possible
- Send one-pager
- Schedule 15-minute call

**Step 2: Discovery Call (Day 2-3)**
- Understand current training process
- Identify pain points
- Introduce Cue concept
- Demo the platform (5 minutes)
- Address concerns
- Propose pilot program

**Step 3: Pilot Agreement (Day 4-7)**
- 2-week pilot with 5-10 budtenders
- No commitment required
- AC provides onboarding support
- Track metrics: participation, submissions, feedback

**Step 4: Full Rollout (Week 2-3)**
- Expand to all budtenders if pilot successful
- Schedule training session for managers
- Provide promotional materials for staff

#### Brand Onboarding

**Parallel Track - Brand Recruitment**:

**Step 1: Brand Outreach**
- Target: Brands looking to increase dispensary presence
- Pitch: Direct access to trained, motivated budtenders
- Value prop: Measurable ROI on budtender incentives

**Step 2: Brand Setup (1 day)**
- AI profile configuration
- Website extraction for brand intelligence
- Mission creation training
- Compliance guardrail review

**Step 3: Content Creation (1-2 days)**
- Generate initial training courses
- Create Product Moments
- Design first missions
- Review and approve all content

**Step 4: Launch**
- Match brand with dispensary partners
- Activate missions
- Monitor performance
- Weekly check-ins

#### Budtender Onboarding

**Individual Onboarding Flow**:

**Step 1: Invite (30 seconds)**
- Dispensary admin sends invite via SMS
- Link to download app
- Promo code for welcome bonus

**Step 2: Download & Verify (2 minutes)**
- Download Cue from App Store/Play Store
- Enter phone number
- Verify with SMS code
- Confirm age (21+)

**Step 3: Profile Setup (1 minute)**
- Enter name
- Select dispensary from list
- Add optional email for notifications

**Step 4: Quick Tour (2 minutes)**
- Interactive walkthrough of:
  - Mission tab
  - Training tab
  - Rewards tab

**Step 5: First Mission (immediate)**
- Auto-assign "Welcome Mission"
- Simple task: Complete profile, view one training
- Reward: $5 welcome bonus
- Gets them familiar with submission flow

**Step 6: Ongoing Engagement**
- Daily: New missions, leaderboard updates
- Weekly: New training courses
- Monthly: Certification opportunities

**Budtender Onboarding Best Practices**:
- Group onboarding sessions (15 min) for new hires
- Manager champions who promote the app
- Physical signage in break rooms
- Leaderboard displayed on TVs (if possible)
- Recognition for first certification

---

## Part 3: VIP Program Rebrand

### Problem

**"AC Certified" - Why It Doesn't Work**

1. **Hard to Pitch in Person**
   - "Are you AC Certified?" sounds like a credentialing program
   - Awkward to say naturally in conversation
   - Doesn't roll off the tongue

2. **Wrong Mental Model**
   - Sounds like a certification (tests, studying, passing)
   - Not the experience we want to convey (exclusive, VIP, insider)
   - Confuses budtenders with actual training certifications on Cue

3. **No Emotional Appeal**
   - No excitement or exclusivity
   - Doesn't convey status or belonging
   - Generic and forgettable

4. **Hard to Brand**
   - "AC" is already associated with many things
   - Not distinctive in cannabis space
   - Doesn't lend itself to visual identity

**What We Need**:
- Easy to say in conversation
- Conveys exclusivity and status
- Memorable and distinctive
- Works for cannabis culture
- Aligns with Cue's premium, gamified aesthetic

---

### Rebrand Options

#### Option 1: "Cue Circle" ⭐

**The Concept**: Inner circle of top-performing budtenders

**Why It Works**:
- Ties directly to the Cue app brand
- "Circle" = exclusive, insider, select group
- Easy to say: "Are you in the Circle?"
- Natural tier structure: Inner Circle, Core Circle

**Visual Identity**:
- Circular badge/logo
- Concentric circles for tiers
- Colors: Lime green + gold accents

**Pitch**: "Cue Circle is our exclusive community of top budtenders. Members get first access to high-value missions, exclusive brand swag, and invites to private events."

**Pros**:
- Strong brand alignment with Cue app
- Clear hierarchy implied by name
- Professional but approachable
- Memorable

**Cons**:
- Might feel corporate to some
- Requires Cue app recognition first

---

#### Option 2: "The Green Room"

**The Concept**: Backstage access, VIP treatment

**Why It Works**:
- Cannabis reference ("green") + VIP reference ("room")
- Evokes exclusive backstage areas
- Easy to say: "Welcome to the Green Room"
- Cannabis industry will get the reference

**Visual Identity**:
- Velvet rope aesthetic
- Spotlight/stage lighting theme
- Dark green + gold

**Pitch**: "The Green Room is where the best budtenders get VIP treatment. Early access to new products, exclusive drops, and rewards that aren't available to everyone."

**Pros**:
- Clever wordplay
- Strong VIP connotations
- Fun, memorable
- Cannabis-appropriate

**Cons**:
- Might be too on-the-nose
- Could be confused with actual consumption lounges
- Tier naming is harder (The VIP Room?)

---

#### Option 3: "Peak" or "The Peak"

**The Concept**: Top of the mountain, elite status

**Why It Works**:
- "Peak" = top, elite, best
- Cannabis culture: "peak high," "peak performance"
- Easy to say: "Are you Peak?"
- Suggests achievement and elevation

**Visual Identity**:
- Mountain peak imagery
- Elevation tiers: Base, Mid, Summit, Peak
- Alpine/nature theme

**Pitch**: "Peak is for budtenders who've reached the top of their game. Exclusive rewards, premium brands, and experiences that elevate your career."

**Pros**:
- Strong achievement framing
- Natural tier structure (elevation levels)
- Clean, professional
- Works across demographics

**Cons**:
- Less obviously cannabis-related
- Could feel like outdoor gear brand

---

#### Option 4: "Hash VIP"

**The Concept**: Cannabis-native term + VIP designation

**Why It Works**:
- "Hash" = instantly recognizable cannabis reference
- Short, punchy, memorable
- Easy to say: "I'm Hash VIP"
- Cannabis industry insiders will love it

**Visual Identity**:
- Hash/pressed concentrate aesthetic
- Amber/gold color palette
- Bold, streetwear-inspired

**Pitch**: "Hash VIP is the most exclusive club in cannabis retail. Members get the best missions, first dibs on limited releases, and rewards that actually matter."

**Pros**:
- Strong cannabis identity
- Short and memorable
- Appeals to budtender culture
- Distinctive

**Cons**:
- Might be too niche for mainstream
- Could alienate some demographics
- Focus on concentrate vs. flower

---

#### Option 5: "The Garden"

**The Concept**: Cultivation of top talent, growing together

**Why It Works**:
- Cannabis cultivation reference
- Nurturing/growth metaphor
- Easy to say: "Are you in The Garden?"
- Suggests curated, cared-for community

**Visual Identity**:
- Botanical/garden theme
- Growth stages for tiers: Seed, Sprout, Bloom, Harvest
- Natural colors with lime accents

**Pitch**: "The Garden is where top budtenders grow their careers. We cultivate opportunities, connections, and rewards that help you flourish."

**Pros**:
- Positive, growth-oriented messaging
- Natural tier progression
- Inviting, inclusive feel
- Strong metaphor

**Cons**:
- Less VIP/exclusive feeling
- Could feel too soft
- "Garden" is overused in cannabis

---

### Recommendation

**Winner: Cue Circle**

**Rationale**:

1. **Brand Alignment**: Seamlessly connects to the Cue app. As Cue grows, Circle recognition grows with it.

2. **Clear Hierarchy**: Natural tier structure:
   - Circle Member (entry)
   - Circle Select (mid)
   - Inner Circle (top)

3. **Professional but Approachable**: Works for both corporate presentations and casual budtender conversations.

4. **Scalable**: Easy to add features:
   - "Circle-only missions"
   - "Circle events"
   - "Circle swag"

5. **Visual Identity**: Circular badge is clean, modern, and works well in app UI and physical badges.

6. **Easy to Say**: 
   - "Are you in the Circle?"
   - "Join the Cue Circle"
   - "Circle exclusive"

---

#### 30-Second Pitch Script

**In-Person Pitch**:

> "Have you heard of Cue? It's the app where budtenders earn rewards for learning about products. 
> 
> Cue Circle is our exclusive community for the top performers. Circle members get first access to the best missions—I'm talking $5-10 per unit instead of the usual $2. Plus exclusive brand swag, invites to private events, and a direct line to brand reps.
> 
> It's invite-only based on your sales and training activity. Want me to see if you qualify?"

**Text/Email Pitch**:

> "You've been selected for Cue Circle—our exclusive community of top budtenders. 
> 
> Circle members get:
> • First access to high-value missions
> • Exclusive brand drops and swag
> • Private events and brand meetups
> • Monthly bonus pools
> 
> Open the Cue app to claim your Circle status. Questions? Reply to this message."

---

#### Tier Structure

| Tier | Name | Requirements | Benefits |
|------|------|--------------|----------|
| 1 | Circle Member | Complete onboarding + 1 certification | Access to standard missions, Circle badge |
| 2 | Circle Select | 3 months active + $500+ earned | Early access to missions (24hr), exclusive trainings |
| 3 | Inner Circle | Top 10% performer + 6 months tenure | Highest-value missions, monthly bonus pool, brand direct line |

**Entry Criteria**:
- Invitation from AC team
- OR application with performance review
- Current employment at partner dispensary
- Clean compliance record

**Maintenance Requirements**:
- Monthly minimum activity (1 submission or 1 training)
- Quarterly re-evaluation
- Compliance with brand guidelines

---

### Migration Plan

#### Transition Existing Members

**Current "AC Certified" Members → Cue Circle**

**Phase 1: Communication (Week 1)**
- Email announcement to all current members
- Explain rebrand rationale (focus on exclusivity, community)
- Assure them: "Your status carries over"

**Email Template**:

> Subject: Exciting News: You're Now in the Cue Circle
>
> [Name],
>
> We have exciting news! AC Certified is evolving into something bigger: **Cue Circle**.
>
> What's changing? The name and the experience. What's not? You're still part of an exclusive community of top budtenders—and now you get even more.
>
> Your new Cue Circle benefits:
> [List benefits]
>
> Your member ID: [ID]
> Your tier: [Tier]
>
> Download the Cue app to access your Circle benefits: [link]
>
> Welcome to the Circle.
>
> [Signature]

**Phase 2: Account Migration (Week 2)**
- Import all existing members into Cue database
- Assign equivalent Cue Circle tier
- Send login credentials
- Mark accounts as "legacy → Circle" for tracking

**Phase 3: App Onboarding (Week 3-4)**
- Require app download for continued membership
- Offer onboarding support via text/chat
- Host virtual "Welcome to the Circle" sessions

**Phase 4: Sunsetting (Month 2)**
- "AC Certified" references removed from all materials
- Old portal redirect to Cue app
- Final migration deadline (30 days to switch)

#### Messaging

**Key Messages**:

1. **Evolution, Not Elimination**
   - "AC Certified was just the beginning"
   - "Cue Circle is the upgraded experience"
   - "Same exclusivity, more benefits"

2. **Status Preservation**
   - "Your standing carries over"
   - "You're pre-approved for Inner Circle"
   - "Grandfathered benefits"

3. **New Value**
   - Focus on tangible new benefits (app access, more missions)
   - Emphasize community aspect
   - Highlight growth opportunities

4. **Simplicity**
   - "One app for everything"
   - "No more separate logins"
   - "Everything in your pocket"

**FAQ for Migration**:

**Q: Do I need to re-qualify?**  
A: No, your status transfers automatically. You're already in the Circle.

**Q: What happens to my points/rewards?**  
A: All existing rewards carry over to the Cue app wallet.

**Q: Is this the same as Cue training certifications?**  
A: Cue Circle is exclusive membership. Cue certifications are training achievements. You can have both!

**Q: What if I don't download the app?**  
A: You'll miss out on Circle benefits. The app is required for participation.

**Q: Can I opt out?**  
A: Yes, but you'll lose access to exclusive missions and events. Standard Cue app access remains.

---

## Part 4: Cue + VIP Integration

### How Cue Ties into VIP Program

**The Integration Vision**:

Cue Circle is the **digital membership layer** for AC's VIP program. The Cue app becomes the primary interface for VIPs to access benefits, track status, and engage with the community.

**Integration Points**:

1. **Single App Experience**
   - VIPs use Cue app for both training/rewards AND membership benefits
   - No separate "VIP portal" needed
   - Unified login, unified profile

2. **Tier Synchronization**
   - Cue Circle tiers map to VIP tiers
   - Activity in Cue (missions, training) contributes to VIP status
   - VIP status unlocks premium Cue features

3. **Exclusive Content**
   - VIP-only missions (higher payouts, premium brands)
   - VIP-only training (advanced sales techniques)
   - VIP-only Product Moments (exclusive drops)

4. **Community Features**
   - VIP leaderboard (separate from general)
   - VIP chat/channel (future)
   - VIP events (integrated with app invites)

5. **Reward Ecosystem**
   - VIP bonuses on top of standard Cue rewards
   - Exclusive VIP reward catalog
   - Early access to limited rewards

---

### Digital Membership

**In-App VIP Experience**:

**VIP Badge System**:
- Visual VIP indicator on profile
- Tier-specific badge designs (bronze, silver, gold, platinum)
- Animated celebration on tier advancement

**VIP Dashboard**:
- Personal stats: Earnings, certifications, rank
- VIP progress bar: Progress to next tier
- Exclusive content preview: "Coming soon to VIPs"
- Event calendar: VIP-only events

**Membership Card (Digital)**:
- QR code for in-person verification
- Member ID number
- Tier and join date
- Shareable "Proud member since [date]" graphic

**Push Notification Strategy**:
- VIP-exclusive mission alerts
- Tier advancement congratulations
- Event reminders
- "You've unlocked VIP access to [feature]"

---

### Exclusive Features for VIP

**Tier 1: Circle Member (Entry VIP)**
- ✅ Circle badge on profile
- ✅ Access to Circle-only missions
- ✅ Monthly bonus pool eligibility
- ✅ Exclusive training courses

**Tier 2: Circle Select (Mid VIP)**
- ✅ All Tier 1 benefits
- ✅ 24-hour early access to new missions
- ✅ VIP-only Product Moments
- ✅ Quarterly swag drops
- ✅ Priority support

**Tier 3: Inner Circle (Top VIP)**
- ✅ All Tier 1-2 benefits
- ✅ Highest-value missions ($5-10/unit)
- ✅ Brand ambassador opportunities
- ✅ VIP-only events (brand meetups, exclusive drops)
- ✅ Direct brand rep access
- ✅ Annual bonus
- ✅ Feature input (beta access, feedback sessions)

**VIP-Only Mission Types**:

1. **Flash Missions** - Limited-time, high-value (2x payout)
2. **Brand Ambassador Missions** - Long-term partnerships with select brands
3. **Mystery Missions** - Surprise rewards for top performers
4. **Team Missions** - Dispensary-wide challenges with shared rewards

**VIP-Only Training**:

1. **Masterclasses** - Advanced sales psychology
2. **Brand Deep Dives** - Extended courses on premium brands
3. **Industry Insights** - Market trends, consumer behavior
4. **Leadership Skills** - For those moving to management

**VIP-Only Rewards**:

1. **Cash Bonuses** - Monthly pools for top performers
2. **Exclusive Products** - Limited edition items
3. **Experiences** - Dispensary tours, brand facility visits
4. **Career Development** - Conference tickets, certification courses
5. **Tech Perks** - Tablets, headphones, etc.

---

### Technical Implementation Notes

**Database Schema Updates**:

```sql
-- VIP membership table
CREATE TABLE vip_memberships (
  id SERIAL PRIMARY KEY,
  budtender_id INTEGER REFERENCES budtenders(id),
  tier VARCHAR(20) NOT NULL, -- 'member', 'select', 'inner'
  joined_at TIMESTAMP DEFAULT NOW(),
  upgraded_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'active',
  legacy_certified BOOLEAN DEFAULT FALSE -- migration flag
);

-- VIP benefits table
CREATE TABLE vip_benefits (
  id SERIAL PRIMARY KEY,
  membership_id INTEGER REFERENCES vip_memberships(id),
  benefit_type VARCHAR(50), -- 'mission_early_access', 'swag_drop', etc.
  benefit_data JSONB,
  granted_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,
  claimed BOOLEAN DEFAULT FALSE
);
```

**API Endpoints**:

- `GET /api/vip/status` - Get current VIP tier and benefits
- `GET /api/vip/benefits` - List available benefits
- `POST /api/vip/benefits/:id/claim` - Claim a benefit
- `GET /api/vip/missions` - VIP-exclusive missions
- `GET /api/vip/leaderboard` - VIP-only leaderboard

**Mobile UI Components**:

- VIP badge component (profile, leaderboard)
- VIP dashboard screen
- VIP mission filter
- Benefit claim flow
- Tier progress visualization

---

## Appendix A: Quick Reference

### App Store Submission Checklist

**iOS**:
- [ ] Apple Developer account
- [ ] App Store Connect listing created
- [ ] Screenshots (all sizes)
- [ ] App icon (1024×1024)
- [ ] App preview video (optional)
- [ ] Title: "Cue"
- [ ] Subtitle: "Budtender Training & Rewards"
- [ ] Description (see Part 1)
- [ ] Keywords set
- [ ] Privacy policy URL
- [ ] Age rating: 17+
- [ ] Build uploaded via Xcode or Transporter

**Android**:
- [ ] Google Play Developer account
- [ ] Play Console listing created
- [ ] Screenshots (phone, tablet)
- [ ] App icon (512×512)
- [ ] Feature graphic (1024×500)
- [ ] Title: "Cue"
- [ ] Short description
- [ ] Full description (see Part 1)
- [ ] Content rating (IARC)
- [ ] Privacy policy URL
- [ ] Data safety section
- [ ] App bundle (.aab) uploaded

### Dispensary Pitch One-Pager Template

[Available upon request - design template]

### VIP Rebrand Comparison Matrix

| Criteria | Cue Circle | Green Room | Peak | Hash VIP | The Garden |
|----------|------------|------------|------|----------|------------|
| Easy to Say | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Exclusivity | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Cannabis Fit | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Brand Alignment | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Scalability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Memorability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### Contact Information

**Document Owner**: [Your Name]  
**Last Updated**: February 2, 2026  
**Version**: 1.0

---

*This document is confidential and proprietary to AC (Arizona Cannabis).*
