# Cue Legal Review Package

**Prepared for:** AC Legal Team
**Date:** January 25, 2026
**Prepared by:** Randy Torres

---

## Executive Summary

Cue is a **standalone SaaS platform** that enables cannabis brands to incentivize budtenders at dispensaries through missions, training, and rewards. It is **not** an AC-branded product - AC is the first customer/test case, but Cue is designed to work with any cannabis brand.

**Key Legal Considerations:**

1. Budtender compensation/incentive compliance
2. Cannabis advertising/marketing regulations
3. Data privacy (budtender PII)
4. Gift card/rewards tax implications
5. Independent contractor vs employee classification
6. Multi-state regulatory variations

---

## What Cue Does

### For Dispensaries (PRIMARY)

- **Create internal incentive programs** (sell Flight Kits, upsell targets, email signups)
- Dashboard to track budtender performance on YOUR goals
- Approve/manage which brands can run programs with your team
- Your team earns extra money = better retention, better performance

### For Brands (Like AC)

- Create "missions" that pay budtenders for verified sales
- Build training courses that educate budtenders on products
- Track which budtenders are selling their products
- Distribute rewards (gift cards) for completed missions
- Access budtenders at dispensaries already using Cue

### For Budtenders

- Earn extra money from BOTH dispensary programs AND brand campaigns
- Submit proof of sale (photo of receipt + product)
- Complete training courses for bonuses
- Redeem earnings for gift cards
- Single app for all incentives

### Two-Sided Revenue Model

| Side       | Who Pays              | For What                                                         |
| ---------- | --------------------- | ---------------------------------------------------------------- |
| Dispensary | Store owners/managers | Internal incentive programs, performance tracking                |
| Brand      | Cannabis brands       | Access to budtenders, campaign management, training distribution |
| Budtender  | Nobody                | Free to use, they EARN money                                     |

---

## Platform Structure

### Roles & Access

| Role             | Access                                         | Who                   |
| ---------------- | ---------------------------------------------- | --------------------- |
| Platform Admin   | Full system access                             | Cue team              |
| Brand Admin      | Their brand's missions, products, submissions  | AC, other brands      |
| Dispensary Admin | Their store's budtenders, approve brand access | Store managers        |
| Budtender        | Mobile app only - missions, training, wallet   | Individual budtenders |

### Data Collected

**Budtender Data:**

- Phone number (for login)
- Name
- Dispensary affiliation
- Sales submissions (product, order ID, photo proof)
- Training completions
- Earnings/redemptions

**Brand Data:**

- Brand profile
- Products
- Mission configurations
- Submission audit history

**Dispensary Data:**

- Store name, location
- Budtender roster
- Brand access approvals

---

## Legal Questions to Address

### 1. Budtender Compensation Compliance

**Question:** Are third-party incentives to budtenders legal in MA and other target states?

**Considerations:**

- Budtenders are employees of the dispensary, not Cue or the brand
- Payments go directly to budtenders, not through the dispensary
- This is similar to "spiff" programs common in other retail industries
- Some states may have specific rules about cannabis employee compensation

**Research needed:**

- MA CCC regulations on budtender compensation
- Comparison to alcohol/tobacco industry spiff rules
- Any state-specific restrictions on third-party payments to dispensary employees

### 2. Cannabis Marketing/Advertising Rules

**Question:** Does Cue's platform constitute "advertising" under cannabis regulations?

**Considerations:**

- Cue is B2B (brand → budtender), not B2C (brand → consumer)
- No consumer-facing advertising
- Training content is educational, not promotional
- Brands cannot make health claims in training materials

**Guardrails built into platform:**

- Compliance content filtering (blocks prohibited claims)
- All training content reviewed before publishing
- No consumer-facing components

### 3. Data Privacy

**Question:** What are our obligations for budtender PII?

**Considerations:**

- Phone numbers, names, earnings data
- MA data privacy requirements
- CCPA if operating in California
- Need Terms of Service and Privacy Policy

**Current state:**

- Data stored in Neon PostgreSQL (cloud-hosted)
- Firebase for auth and photo storage
- No formal privacy policy written yet

**Needed:**

- Privacy Policy
- Terms of Service
- Data retention policy
- Budtender consent flow in app

### 4. Gift Card/Rewards Tax Implications

**Question:** Are rewards taxable income for budtenders?

**Considerations:**

- Gift cards are generally taxable income
- If budtender earns >$600/year, may need 1099
- Tremendous (our rewards provider) may handle some reporting

**Research needed:**

- 1099 threshold and reporting requirements
- Whether Tremendous handles tax reporting
- Budtender acknowledgment of tax responsibility

### 5. Fraud & Disputes

**Question:** What happens when a submission is disputed or fraudulent?

**Current system:**

- Photo proof required for all sales submissions
- Order ID deduplication (can't submit same order twice)
- Velocity checks (too many submissions too fast = flagged)
- Brand admins can approve/reject/dispute submissions
- Fraud review queue for flagged submissions

**Needed:**

- Dispute resolution process documented
- Budtender appeal mechanism
- Clear terms on fraudulent submissions (account termination)

### 6. Dispensary Relationship

**Question:** Do we need dispensary consent to run programs with their budtenders?

**Current system:**

- Dispensaries can see which brands are active
- Dispensaries can approve/deny brand access
- Budtenders self-affiliate with dispensaries

**Consideration:**

- Some dispensaries may not want third-party incentives
- Need clear opt-in/opt-out mechanism
- May need dispensary agreement/terms

### 7. Multi-State Considerations

**Question:** What changes state-to-state?

**Considerations:**

- Cannabis regulations vary significantly by state
- MA is launch state, but Cue designed for multi-state
- Each state may have different:
  - Budtender licensing requirements
  - Third-party compensation rules
  - Marketing restrictions
  - Data privacy laws

**Recommendation:**

- Launch MA-only initially
- Research each new state before expansion
- Build state-specific compliance checks into platform

---

## Corporate Structure Questions

### Cue vs AC Relationship

**Current state:**

- Same team runs both
- AC is first customer
- Cue is separate product, not AC-branded

**Questions for legal:**

1. Should Cue be a separate legal entity?
2. What's the IP ownership structure?
3. If AC invests in Cue, what's the relationship?
4. Liability separation between AC and Cue?

### Revenue Model

| Revenue Stream          | Description                                 | Priority   |
| ----------------------- | ------------------------------------------- | ---------- |
| Dispensary subscription | Monthly fee for internal incentive programs | **LAUNCH** |
| Brand subscription      | Monthly fee for campaign access             | LAUNCH     |
| Per-mission fee         | % of rewards distributed                    | LAUNCH     |
| Enterprise/MSO pricing  | Multi-location packages                     | LATER      |

**Pricing TBD but rough model:**

- Dispensary: $99-299/mo depending on budtender count
- Brand: $299-999/mo depending on store access + per-mission %
- Budtender: Free (they're the product AND the customer)

**Questions:**

- Any licensing requirements for operating this type of platform?
- Payment processing compliance (we use Tremendous for rewards)

---

## Documents Needed

### Before Launch

1. [ ] **Terms of Service** - Platform usage terms
2. [ ] **Privacy Policy** - Data handling, PII protection
3. [ ] **Budtender Agreement** - Consent, tax acknowledgment, fraud terms
4. [ ] **Brand Agreement** - Platform usage, content guidelines, payment terms
5. [ ] **Dispensary Agreement** - Opt-in/opt-out, data access terms

### For Expansion

6. [ ] **State-by-state compliance checklist**
7. [ ] **1099 reporting process** (if >$600 threshold)
8. [ ] **Insurance review** (liability coverage)

---

## Technical Security

| Area            | Current State                                        |
| --------------- | ---------------------------------------------------- |
| Authentication  | Phone OTP + JWT tokens                               |
| Data encryption | HTTPS in transit, encrypted at rest (Neon)           |
| Access control  | Role-based (4 tiers)                                 |
| Audit logging   | All admin actions logged                             |
| Photo storage   | Firebase Storage (secure URLs)                       |
| Fraud detection | Duplicate check, velocity check, manual review queue |

**Needed:**

- Penetration testing before launch
- SOC 2 compliance (long-term)
- Formal security policy

---

## Recommended Next Steps

1. **Legal review of MA budtender compensation rules** - Can brands pay budtenders directly?
2. **Draft Terms of Service and Privacy Policy** - Standard SaaS terms + cannabis-specific provisions
3. **Define Cue corporate structure** - Separate entity or AC subsidiary?
4. **Review Tremendous tax reporting** - Do they issue 1099s?
5. **Create budtender consent flow** - In-app agreement before earning

---

## Appendix: Platform Screenshots

### 1. Login Page (Web)

The phone-based authentication entry point for all users.

![Login Page](./screenshots/01_login_page.png)

### 2. Admin Dashboard

Main analytics dashboard showing platform overview, active campaigns, and performance metrics.

![Admin Dashboard](./screenshots/02_admin_dashboard.png)

### 3. Campaigns Page

Where brands create and manage incentive campaigns (missions) for budtenders.

![Campaigns Page](./screenshots/03_campaigns_page.png)

### 4. Product Library

Centralized product catalog where brands manage their product information.

![Products Page](./screenshots/04_products_page.png)

### 5. Submission Audit (Results)

Where brand admins approve/reject budtender sales submissions with proof verification.

![Results Page](./screenshots/05_results_page.png)

### 6. Training Courses

AI-generated training modules that educate budtenders on brand products.

![Training Page](./screenshots/06_training_page.png)

### 7. Reward Approvals

Where admins monitor and approve budtender reward redemptions.

![Rewards Page](./screenshots/07_rewards_page.png)

## Appendix: Data Flow Diagram

```
Budtender (Mobile App)
    ↓ submits sale
Cue Backend
    ↓ validates (fraud check, dedup)
Brand Admin (Dashboard)
    ↓ approves/rejects
Cue Backend
    ↓ credits wallet
Budtender (Mobile App)
    ↓ redeems reward
Tremendous API
    ↓ issues gift card
Budtender receives gift card
```

---

_This document is for internal review purposes. Not legal advice._
