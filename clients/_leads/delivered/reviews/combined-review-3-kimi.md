# Combined Review: PROPOSAL-DRAFT.md + plan-3-full.md
**Reviewer:** Kimi (Subagent Reviewer #3)  
**Date:** February 10, 2026  
**Verdict:** Needs Revisions (with critical gaps flagged)

---

## Executive Summary

This is a compelling proposal with genuine strategic insight, but it suffers from **three critical blind spots** that could derail the partnership: (1) unverified payment integration assumptions, (2) Dutchie dependency without confirmation, and (3) aspirational brand positioning that may not match operational reality. The brand vision I authored is ambitious—perhaps overly so for a bootstrapped Clinton MA operation.

---

## 1. Payment Integration Gap — CRITICAL ISSUE

**The Problem:** The proposal casually states "Payment: ACH, PIN-debit, and cash" and cites Dutchie "Pay by Bank" as the solution. This is a dangerous assumption.

**What the proposal gets wrong:**
- Dutchie's Pay by Bank documentation states it works across "delivery, e-commerce, mobile app, kiosk, register"—but this refers to Dutchie's **own** branded ecosystem (the Dutchie app/embed), not custom third-party apps
- Dutchie does not publish a public API for "Pay by Bank" that can be integrated into a custom React Native app
- If Pay by Bank is unavailable, the app needs its own ACH processor (Aeropay, Hypur, CanPay, or direct Plaid integration)
- **Cost reality check:** Direct Plaid integration runs $0.30-0.50/transaction + monthly fees. Aeropay/Hypur charge setup fees ($500-2,000) + per-transaction fees. This adds **$5,000-15,000 in development costs** and **ongoing operational costs** not accounted for in the budget.

**Required Action:** Verify with Dutchie whether Pay by Bank API is available for custom apps. If not, scope and budget a separate payment integration. This could add 2-4 weeks to the timeline.

---

## 2. Dutchie API Dependency — HIGH RISK

**The Problem:** The proposal assumes "Dutchie/POS integration" for inventory/menu sync without confirming Delivered's actual setup.

**Critical questions unanswered:**
- Does Delivered currently use Dutchie at all, or just embed the Dutchie iframe on their website?
- Dutchie Ecommerce Pro API access requires an enterprise subscription—typically $1,000+/month minimum
- Dutchie's API is designed for dispensaries, not delivery operators. Menu logic (delivery zones, driver inventory, dynamic availability) may not map cleanly
- The proposal mentions "real-time inventory verification"—this requires webhook infrastructure that may not exist

**Self-critique:** The brand vision assumes seamless inventory sync as table stakes. If Delivered is manually managing inventory or using a different POS (Leaf Logix, Metrc direct, etc.), the entire "streamlined ordering" value proposition collapses.

**Required Action:** Audit Delivered's current tech stack before committing to the 12-week timeline.

---

## 3. Self-Critique: Does the Brand Vision Overpromise?

**Yes. In three specific ways:**

### A. "Midnight Cannabis Lounge" Aesthetic
The brand vision describes a "Brooklyn cocktail bar meets Massachusetts craft cannabis" aesthetic with "deep charcoal, matte gold, soft sage." For a bootstrapped delivery company operating out of Clinton MA with a compromised WordPress site and casino spam SEO issues, this feels disconnected from reality. The visual sophistication implied requires:
- Professional photography ($2,000-5,000)
- Custom packaging design ($5,000-10,000)
- App UI/UX polish that takes time

**The reality:** Delivered is fighting for survival (license renewal in 3 weeks, hacked website, no app). The brand vision should prioritize "trustworthy and functional" over "cocktail bar chic."

### B. "Premium Practical" Positioning
The vision states the app should feel like "unboxing an Apple product." This sets an expectation bar that a 12-week MVP cannot meet. A more honest framing: "like ordering from your favorite local coffee shop" is achievable; "Apple-level polish" is not.

### C. The 60-Second Promise
The vision promises users can "place their first order within 60 seconds of downloading." This requires:
- Streamlined age verification (compliance risk if too fast)
- Pre-populated location data
- No account creation friction
- Instant product loading

**Reality check:** Cannabis compliance requires deliberate age-gating. Dutchie integrations (if they work) add latency. A 60-second first order is a stretch goal, not a promise.

---

## 4. Zone Expansion Budget: $11,500/zone — Realistic?

**The budget breakdown (from Section 4):**
| Category | Amount |
|----------|--------|
| Paid Social | $3,000 |
| Influencer | $1,500 |
| Promotions | $3,500 |
| Content Creation | $1,500 |
| Local Events | $1,000 |
| Buffer | $1,000 |
| **Total** | **$11,500** |

**The unasked question:** Where does this money come from?

Delivered is described as "bootstrapped" with current revenue estimated at $40,000-65,000/month. The proposal recommends launching 3-5 zones in Year 1. That's **$34,500-57,500 in expansion marketing spend**—nearly a month's revenue.

**Missing from the proposal:**
- Who funds zone expansion? Roviq? Delivered? Split?
- The revenue share model (5% above $75K/month) suggests Roviq only benefits after Delivered is already doing well—but zone expansion requires upfront investment
- If Delivered can't fund expansion, does Roviq cover it? Against what return?

**The timeline mismatch:** The proposal says revenue share starts at $75K/month. But zone expansion is required to reach $75K/month. This is a chicken-and-egg problem not addressed.

---

## 5. Social Media Targets: 1,123 → 10K in 12 Months — Realistic?

**The claim:** 10,000+ Instagram followers in 12 months (from Section 8 of plan-3-full.md).

**The reality of cannabis social media:**
- Instagram algorithmically suppresses cannabis content
- Shadowbanning is common
- Paid promotion options are severely limited
- Follower growth in cannabis typically plateaus at 2-3K without paid amplification

**The proposal's own admission:** "Social media strategy adapted for algorithmic suppression of cannabis content — organic reach is limited."

**Yet the target assumes 790% growth.** Even with $2,000/month in paid promotion (mentioned as Month 7-12), this is optimistic. Rolling Releaf—the proposal's cited example—has 235 Instagram followers despite "dominating Boston search rankings." Their SEO works *because* they don't rely on social.

**Recommendation:** Set 5,000 followers as the 12-month target, with 10K as a stretch. Focus on email/SMS (owned channels) where the proposal's 2,000-5,000 subscriber targets are more realistic.

---

## 6. Cross-Document Inconsistencies Found

| Issue | PROPOSAL-DRAFT.md | plan-3-full.md | Conflict |
|-------|-------------------|----------------|----------|
| **Equity range** | 8-12% (Option A), 4-6% (Option B) | Mentions "8-12%" in intro, doesn't detail Option B | Inconsistent presentation |
| **Retainer start** | Month 7 (Option A), Month 2 (Option B) | Not detailed | Missing in brand doc |
| **Revenue share trigger** | Above $75K/month (Option A), "app-driven only" (Option B) | Not mentioned | Critical term absent |
| **Timeline for equity vesting** | 4 years, 1-year cliff | Not mentioned | Key term missing |
| **Instagram target** | "2,500 at 90 days, 5,000 at 6 months, 10,000+ at 12 months" | Same numbers | ✅ Consistent |
| **First app claim** | "First cannabis delivery app in Massachusetts" | "First mobile app in a market of 27 licensed operators" | ✅ Consistent |
| **Programmatic SEO pages** | "50-100 page-one rankings" | "300-400 pages" (annual) | 50-100 vs 300-400 |
| **Content frequency** | Not specified in detail | "10-13 pieces/week, 550-650 annually" | Brand doc more detailed |

**The most significant gap:** The brand vision document (plan-3-full.md) omits all partnership terms—equity, revenue share, vesting, dissolution. If this is the "definitive brand playbook," it should reference the partnership structure or link to the proposal.

---

## 7. The "First Cannabis Delivery App in MA" Claim — Defensible?

**The claim:** "Not a single delivery operator in Massachusetts has a mobile app." / "The first native cannabis delivery app in Massachusetts."

**Assessment:** This is **defensible but fragile.**

**Why it's defensible now:**
- Zyp Run has $2.6M funding but only a website (zyp.run)
- Rolling Releaf has no app
- Checked: No "Delivered" or competitor apps in App Store for cannabis delivery in MA

**Why it's fragile:**
- Zyp Run has a dev team and funding. If they see this proposal, they could accelerate app development
- 12 weeks is a realistic MVP timeline, but App Store approval for cannabis apps takes 2-4 weeks (per proposal)
- A 12-week development + 4-week approval = 16 weeks total. Zyp Run could launch in that window if they started today

**Recommendation:** Frame as "the first to market with a native app" rather than "the only one without competition." The exclusivity window is months, not years.

---

## 8. The Founder's "No" — Devil's Advocate

If I were Ruben, Eddy, or Tut, here's what would make me say no:

### A. "You're asking for 8-12% equity for an unproven app"
- The proposal admits no MA delivery operator has an app—because it's hard, not because it's obviously valuable
- The founders have survived 2.5 years without one
- What if the app doesn't drive meaningful adoption? Roviq still keeps vested equity

### B. "The revenue share kicks in after we're already successful"
- At $75K/month, Delivered is already a viable business
- The proposal says "If Randy disappears after 6 months, he retains only ~1.5-3%"—but that's still equity in a company I built
- The revenue share (5% above $75K) means Roviq benefits from Delivered's existing growth trajectory, not just the app contribution

### C. "You haven't proven the payment integration works"
- The Dutchie/ACH assumption is a red flag
- If payments don't work, the app is useless
- I'd want a working payment prototype before signing equity away

### D. "The brand vision feels like it was written for a different company"
- "Midnight Cannabis Lounge," "Apple product unboxing," "Brooklyn cocktail bar"—this doesn't match Clinton MA or our operational reality
- It feels aspirational to the point of being disconnected from what we can actually execute

### E. "You're proposing to build us into a VC-fundable company, but we might not want that"
- The proposal emphasizes Seed round preparation ($1-3M raise)
- But Delivered is a bootstrapped, social equity business with specific community commitments
- VC pressure for hypergrowth could conflict with social equity values

---

## Final Recommendation

**Verdict: Needs Revisions**

The proposal should move forward, but with these pre-conditions:

1. **Payment verification milestone:** Before signing LOI, confirm Dutchie Pay by Bank API availability or scope alternative ACH integration. Document the cost and timeline impact.

2. **Tech stack audit:** Confirm Delivered's current POS/menu system. If not Dutchie, revise integration assumptions.

3. **Brand positioning reset:** Replace "Midnight Cannabis Lounge" with "Trusted Local Delivery." Save premium aesthetic for Phase 2 when revenue supports it.

4. **Zone expansion funding clarity:** Specify who pays for zone expansion and how. If Roviq contributes, structure as convertible note or additional equity, not "partnership goodwill."

5. **Social targets revised:** Reduce Instagram target to 5,000 at 12 months. Emphasize email/SMS where the business has more control.

6. **Founder protections:** Add performance milestones to equity vesting (not just time-based). If app adoption is below X% at 6 months, vesting pauses.

**The core insight is sound:** First-mover app advantage + programmatic SEO + AC supply chain = differentiated position. But the execution plan needs grounding in verified technical reality, not assumed integrations.

---

**Review completed by:** Kimi (Subagent Reviewer #3)  
**Saved to:** /data/workspace/clients/_leads/delivered/reviews/combined-review-3-kimi.md
