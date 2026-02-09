# Cue (formerly Sparkplug)

**Code Repo:** `/Users/randytorres/Projects/BudtenderIncentiveAI`

## Overview
Platform for cannabis **brands AND dispensaries** to incentivize budtenders. **Feature-complete MVP** with mobile app, admin dashboard, and full backend.

**Positioning:** Retail Demand Control Layer

**Two-Sided Platform:**
- **Brands** pay to incentivize budtenders to push their products
- **Dispensaries** pay to run their own internal incentive programs (sell Flight Kits, upsell targets, etc.)
- **Budtenders** earn from both sides on the same app

---

## Important: Standalone SaaS Product

**Cue is a standalone multi-state SaaS product, NOT an AC-branded tool.**

- Cue is being tested at AC dispensaries for feedback
- Same team runs both Cue and AC, but they are separate products
- Cue should NOT mention "AC Certified" unless it's a specific campaign
- Cue can work with ANY cannabis brand, not just AC

**Relationship to AC:**
- AC is the first customer/test case
- AC's "AC Certified" partnership program is separate from Cue
- AC Certified could use Cue for budtender incentives, but Cue isn't AC-branded

**Launch Strategy:**
- Tease Cue at Superbowl event (Feb 4th): "Something big coming for budtenders"
- Separate launch campaign after Superbowl (creates two moments instead of one)
- Use Superbowl attendee list as beta audience

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Mobile | React Native + Expo 52, NativeWind |
| Admin Dashboard | React 18 + Vite + TypeScript, TanStack Query, Radix UI |
| Backend | Node.js + Express, TypeScript |
| Database | PostgreSQL (Neon serverless), Drizzle ORM |
| Queue | BullMQ + Redis |
| Auth | Phone OTP + Firebase Phone Auth, JWT |
| AI | OpenAI GPT (courses/content), Google Gemini (images) |
| Rewards | Tremendous API (gift cards) |
| Storage | Firebase Storage (proof photos) |
| Scraping | Firecrawl (brand website extraction) |

**Codebase:** ~45,800 lines across server, client, mobile

---

## Current Capabilities

### Working Features ✅

**Mobile App (Budtender)**
- Phone login with OTP verification
- Mission feed with real-time progress tracking
- Sales submission with photo proof + camera integration
- Leaderboard with WebSocket updates
- Training courses with quizzes (80% pass threshold)
- Product moments (quick tips with interactive quizzes)
- Certification badge earning
- Wallet with earnings summary
- Gift card redemption from catalog

**Admin Dashboard**
- Brand management with AI profile generation (Firecrawl extraction)
- Product CRUD with AI-generated details
- 3 mission types: Commission, Tiered, Competition
- Submission audit queue (approve/reject/dispute)
- Course creation with auto-generated content
- Budtender & dispensary management
- Rewards tracking with CSV export
- Analytics dashboard (sales trends, budtender performance, mission ROI)
- Fraud review queue
- Brand-dispensary access control

**Backend Services**
- Fraud detection (duplicate images, order ID dedup, velocity checks)
- Compliance content filtering (cannabis regulations)
- Campaign permission controls (field-level locking by status)
- Audit logging for all actions
- Rate limiting on auth endpoints

**Roles (4-tier access)**
- Platform Admin: full system access
- Brand Admin: tenant-isolated brand/mission/product management
- Dispensary Admin: local budtender/reward management
- Budtender: mobile app only

### Partially Working 🟡
- Gemini image generation (graceful fallback if API fails)
- Mobile app needs Expo build to deploy (no native binaries in repo)
- Tremendous rewards in testflight mode (not production credentials)

### Not Yet Implemented ❌
- Automated testing (zero test files)
- Email/SMS notifications (mock verification codes only)
- Job retry logic / dead-letter handling
- Budget caps per mission
- Advanced analytics / ML predictions

---

## Database Schema

19 tables including:
- `users`, `brands`, `dispensaries`, `budtenders`
- `missions`, `mission_assignments`, `sales_submissions`, `sales_submission_audits`
- `rewards`, `redemptions`
- `courses`, `course_completions`, `certifications`
- `product_moments`, `product_quiz_completions`, `products`
- `brand_dispensary_access`, `brand_access_requests`
- `refresh_tokens`, `idempotency_keys`, `audit_logs`, `fraud_checks`, `compliance_violations`

7 migrations applied.

---

## API Endpoints

**Auth:** `/api/auth/login`, `/verify`, `/refresh`, `/logout`
**Budtender:** `/api/missions`, `/training/courses`, `/wallet`, `/rewards/:id/redeem`
**Admin:** Full CRUD on `/api/admin/{brands,products,missions,submissions,courses,budtenders,dispensaries,rewards,users}`
**Analytics:** `/api/admin/analytics/{summary,sales-trends,budtender-performance,mission-effectiveness}`
**Uploads:** `/api/upload`, `/upload/signed-url`

---

## Environment Variables Required

```
DATABASE_URL                          # PostgreSQL (Neon)
REDIS_URL                            # BullMQ queue
AI_INTEGRATIONS_OPENAI_API_KEY       # GPT
NANOBANANA_API_KEY                   # Gemini
FIRECRAWL_API_KEY                    # Web scraping
FIREBASE_API_KEY                     # Auth + Storage
TREMENDOUS_API_KEY                   # Gift cards
SENTRY_DSN                           # Error tracking (optional)
JWT_SECRET                           # Token signing
SESSION_SECRET                       # Session management
```

---

## Remaining TODOs

### Pre-Production (Critical)
- [ ] Add automated tests
- [ ] Switch Tremendous to production credentials
- [ ] Set up Sentry error tracking
- [ ] Implement job retry logic / dead-letter queue
- [ ] Real SMS provider for OTP

### Infrastructure
- [ ] Separate staging environment
- [ ] Backup + restore testing
- [ ] Secrets management (not .env in prod)

### Features
- [ ] Social integration on budtender profile
- [ ] Brand categories during onboarding
- [ ] Admin ability to edit AI-generated profiles
- [ ] Email notifications for job failures
- [ ] Budget cap enforcement per mission

### Priority: Dispensary Campaigns (NEXT BUILD)
**Dispensary-created missions** — Let dispensaries create their own incentive programs alongside brand campaigns.

Examples:
- "Sell 2 Flight Kits per shift = $10 bonus" (CH use case)
- "Upsell to 7g or higher = $2 per transaction"
- "Get 5 email signups = $5"
- "Hit daily revenue target = team bonus"

**Why this matters:**
- Unlocks B2B revenue from retail side (dispensary subscriptions)
- Makes platform stickier (budtenders use daily, not just for brand promos)
- Changes the pitch: "Run YOUR incentive programs + let brands pay to train your team"
- CH is the test case for this feature

### UI Polish
- [ ] Remove emojis from UI
- [ ] Color refinement
- [ ] Budtender onboarding UX (translate swag/pizza/samples energy)

---

## Distribution Strategy

### Phase 1: Dispensary-First Approach
**Lead with dispensary value, not brand value.**

**The Pitch to Dispensaries:**
> "We built a platform that lets you run your own budtender incentive programs - Flight Kits sold, upsells, whatever you want to track. Your team earns bonuses, you get a dashboard to see who's performing. Oh, and brands can pay to run campaigns on the same app - so your budtenders get trained and rewarded without you spending a dime on the brand side."

**Why this works:**
- Dispensary gets immediate value (their own programs)
- Brand campaigns are "free money" for the dispensary's team
- Budtenders adopt because they earn from multiple sources
- Brands get access to engaged budtenders

### Phase 2: Brand Expansion
Once dispensaries are on the platform:
- Brands pay for access to those budtenders
- "We have X budtenders at Y stores already using Cue daily"
- Network effect kicks in

### Test Cases
- **CH (Cannabis Healing):** Flight Kits incentive program - first dispensary campaign
- **AC:** Brand campaigns at partner stores - first brand campaigns

---

## Demo Accounts (Dev Only)
- `demo-admin` / `000000` → Platform Admin
- `brand-admin` / `000000` → Brand Admin
- `demo` / `000000` → Budtender
