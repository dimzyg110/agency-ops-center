# GLASS Public Pages Review (Logged Out)

**Date:** 2026-02-13  
**Reviewer:** Automated QA Subagent  
**Pages Tested:** Homepage, Pricing, Report Card (Canna Provisions Holyoke)

---

## Executive Summary

All three pages load successfully with no HTTP errors. The site is visually polished with a clean, professional design. However, there are several data accuracy issues, layout/CSS problems, and UX gaps that should be addressed before broader marketing pushes.

**Critical Issues:** 3  
**Moderate Issues:** 8  
**Minor Issues:** 5  

---

## 1. Homepage — https://glassintel.xyz/

### ✅ What Works
- Page loads quickly (200 OK)
- Hero section is clean and compelling: "Market intelligence that operators can trust"
- Email capture + "Get Early Access" CTA is prominent and functional
- Stats cards render correctly: **301 operators tracked**, **109.9K products tracked**, **132.9K price observations**
- CCC × GLASS cross-reference table is a killer feature — well-presented with 7 categories
- Price Index table mirrors the cross-reference data correctly
- Weekly Sales Tracker chart renders with historical data ($8.8B total, $1.65B in 2025)
- License Pipeline section shows 234 pending applications with bar chart breakdown
- FAQ section is clear and answers obvious questions
- Newsletter CTA is present
- Footer renders with social links and copyright

### ❌ What Doesn't Work

#### 🔴 CRITICAL: "Pending license applications" shows "0" heading but "234" in body
- The snapshot shows a large "0" prominently displayed, then below it says "234 license applications in the pipeline"
- This is confusing and contradictory — the "0" appears to be a rendering bug or misplaced counter
- **Impact:** Makes the data look broken/untrustworthy

#### 🟡 MODERATE: Layout issues — content is right-aligned/offset
- All page content appears shifted to the right side of the viewport
- The left ~35-40% of the screen is empty/unused on multiple sections
- On the CCC × GLASS table, the "Retail premium" and "Observations" columns are cut off (not visible without horizontal scroll)
- The Price Index table's "Unit", "WoW", and "Trend" columns are partially cut off at the right edge

#### 🟡 MODERATE: All WoW/Trend data shows "— New"
- Every category in the Price Index table shows "— New" for week-over-week and trend columns
- The footnote explains this ("Week-over-week and month-over-month trends available after 7 days of data"), which is reasonable for launch
- However, "New" as a trend label could confuse users — consider "Collecting data" or hiding the column until data exists

#### 🟡 MODERATE: Tincture and Topical have very low observation counts
- Tincture: 11 observations
- Topical: 13 observations  
- These sample sizes are too small for reliable averages — consider hiding categories below a threshold (e.g., <50 observations) or adding a "low confidence" marker

#### 🟡 MINOR: "Updated Just now" timestamp
- The timestamp always says "Updated Just now" — this isn't useful. Should show an actual date/time (e.g., "Updated Feb 12, 2026 at 3:45 PM")
- The second timestamp footer correctly shows "As of Feb 12, 2026" — good

#### 🟡 MINOR: Sales chart only shows 2022-2025
- The text says "Adult-use sales since 2018" but the chart's x-axis only labels 2022, 2023, 2024, 2025
- The chart appears to start around mid-2021 visually — it may include earlier data but the axis labels are misleading

### Data Accuracy Assessment

| Category | GLASS Retail Avg | Reasonable? | Notes |
|----------|-----------------|-------------|-------|
| Concentrate | $41.73/g | ✅ Yes | Typical MA range $30-60/g |
| Edible | $17.86/unit | ✅ Yes | Typical MA range $10-25 |
| Flower | $9.96/g | ✅ Yes | ~$35/eighth ÷ 3.5g = $10/g is right for MA |
| Preroll | $18.90/unit | ✅ Yes | Typical MA range $10-25 |
| Tincture | $51.64/unit | ⚠️ Questionable | Only 11 observations — too few for reliable avg |
| Topical | $30.49/unit | ⚠️ Questionable | Only 13 observations — too few for reliable avg |
| Vape | $35.34/unit | ✅ Yes | Typical MA range $30-50 for 0.5g cart |

CCC Transfer Average for Flower: **$4.01/g** — this is plausible for wholesale/transfer pricing.  
Retail Premium of **+148.4%** for flower — reasonable (transfer → retail markup).

### Link Audit
| Link | Target | Status |
|------|--------|--------|
| GLΛSS logo | / | ✅ Works |
| Market Data nav | / | ✅ Works |
| Pricing nav | /pricing | ✅ Works |
| Login nav | /login | ✅ Works |
| Sign Up nav | /signup | ✅ Works |
| Get Weekly Report | /newsletter | ✅ Works |
| See Pricing | /pricing | ✅ Works |
| See your store's report card | /signup | ✅ Works |
| Subscribe to Weekly Report | /newsletter | ✅ Works |
| Twitter footer | twitter.com/roviq | ✅ Resolves to x.com/roviq |
| LinkedIn footer | linkedin.com/company/roviq | ✅ Works |
| Email footer | mailto:hello@roviq.ai | ✅ Works |

---

## 2. Pricing Page — https://glassintel.xyz/pricing

### ✅ What Works
- Page loads correctly (200 OK)
- Clean, focused layout: "Simple, transparent pricing"
- Single plan clearly shown: **GLASS Pro — $199/month**
- Feature list is comprehensive (8 items with checkmarks)
- "Start Free Trial" CTA button is prominent
- Stripe checkout link is properly formatted
- 30-day money-back guarantee is clearly stated
- FAQ section addresses 5 common questions
- "Still have questions?" section with email link
- Contact email is **hello@glassintel.xyz** (correct for GLASS-specific inquiries)

### ❌ What Doesn't Work

#### 🟡 MODERATE: Layout push — content shifted right
- Same layout issue as homepage — content is pushed to the right ~35-40% of viewport
- The heading "Simple, transparent pricing" is cut off at the right edge ("Simple, transparen...")
- Feature list items are cut off at the right edge ("Unlimited c...", "Real-time p...", etc.)
- This is a responsive/CSS issue — appears to be a left sidebar or padding taking up too much space

#### 🟡 MODERATE: Email inconsistency between footer and contact section
- Pricing page contact section: **hello@glassintel.xyz**
- Footer email link: **mailto:hello@roviq.ai**
- These are two different email domains — confusing for users
- Should be consistent: recommend using hello@glassintel.xyz everywhere on the GLASS site

#### 🟡 MODERATE: "View public market data" link goes to /market → redirects to /
- The bottom of pricing page has a link "View public market data" pointing to `/market`
- `/market` doesn't exist as a distinct page — it redirects to the homepage `/`
- This isn't broken but is misleading — the link should either go directly to `/` or anchor to a specific section of the homepage

#### 🟡 MINOR: "API access (coming soon)" in feature list
- Having a "coming soon" feature in the paid plan's feature list may set expectations prematurely
- Consider moving this to a separate "Roadmap" note below the features

### Pricing Assessment
- **$199/month** is reasonable for B2B cannabis intelligence SaaS
- Comparable tools (Headset, Leafly Business, etc.) range from $99-$500/month
- Single-tier pricing is clean and simple — reduces decision friction
- 30-day money-back is a good trust signal
- Free trial via Stripe link is good conversion path

### FAQ Quality
All 5 FAQ items are clear and well-written:
1. ✅ "Is there a free trial?" — Good answer, references public data
2. ✅ "Can I cancel anytime?" — Direct, no-nonsense
3. ✅ "What payment methods?" — Clear
4. ✅ "Discounts for multiple locations?" — Smart upsell mention (3+ locations)
5. ✅ "Is my data secure?" — Good trust builder

---

## 3. Report Card — https://glassintel.xyz/report/canna-provisions-holyoke

### ✅ What Works
- Page loads correctly (200 OK)
- Report card concept is compelling — personalized competitive intelligence as a teaser
- Overall Grade: **C** ("Some Things to Watch") — reasonable for a dispensary with mixed pricing
- Pricing section shows 5 categories with clear above/below market indicators
- Color coding is effective (red dots for below market, green for above)
- Category-level insights are actionable ("24.7% below market — potential opportunity")
- Competition section present with "Needs Attention" status
- Assortment section shows "On Track" with 2,454 products
- CTA at bottom: "See Your Full Report Card — Free" → /signup (good conversion funnel)

### ❌ What Doesn't Work

#### 🔴 CRITICAL: Wrong city displayed — "AMHERST" should be "HOLYOKE"
- The URL is `/report/canna-provisions-holyoke`
- The title correctly says "Canna Provisions Holyoke"
- But the subtitle/location shows **"AMHERST"** instead of **"HOLYOKE"**
- Canna Provisions has locations in both Holyoke and Lee, MA (and Amherst) — the data may be pulling from the wrong location record
- **Impact:** This is a credibility killer — if a dispensary owner sees their own location wrong, they won't trust any other data

#### 🔴 CRITICAL: Nearby Competitors shows "0"
- For a dispensary in Holyoke, MA — a city with multiple dispensaries — showing 0 nearby competitors is clearly wrong
- This makes the Competition "Needs Attention" grade seem arbitrary
- Holyoke has at least 3-4 other dispensaries (e.g., Apothecary Farms, Green Meadows)
- **Impact:** Undermines the competitive intelligence value proposition entirely

#### 🟡 MODERATE: Market Average shows "0" in Assortment section
- "Your Products: 2,454" but "Market Average: 0"
- If market average is truly 0, the comparison is meaningless
- This suggests the market average calculation isn't working

#### 🟡 MODERATE: No navigation bar on report card page
- Unlike homepage and pricing, the report card page has NO header navigation
- No way to navigate back to homepage, pricing, or other pages without browser back button
- No GLASS logo/branding in a clickable header
- The entire left side of the page is blank

#### 🟡 MODERATE: Content pushed to the right side
- The layout issue is even more pronounced on this page
- All content is confined to the right ~60% of the screen
- The left ~40% is completely empty (dark background, no content)
- This wastes screen real estate and looks unfinished

#### 🟡 MODERATE: Page doesn't scroll properly / limited content
- The page appeared stuck at certain scroll positions
- The "Competition" section seems to be the last visible section before the CTA
- No footer visible on this page

#### 🟡 MINOR: Category color coding inconsistency
- Flower: -24.7% below market → 🔴 red dot — makes sense (below market = potential revenue loss)
- Edible: +11.7% above market → 🟢 green dot — makes sense (premium pricing)
- BUT: Being "below market" is flagged as "potential opportunity" (to raise prices), which is actually positive advice — the red dot suggests something bad
- The color coding should match the recommendation tone, not just the direction

### Pricing Data Assessment (Report Card)

| Category | vs Market | Reasonable? | Notes |
|----------|-----------|-------------|-------|
| Flower | -24.7% below | ✅ Plausible | Canna Provisions known for competitive pricing |
| Preroll | +10.7% above | ✅ Plausible | Premium preroll positioning is common |
| Edible | +11.7% above | ✅ Plausible | Premium edible positioning |
| Concentrate | -36.8% below | ⚠️ Check | -36.8% is a big gap — verify this isn't an outlier |
| Vape | -12.1% below | ✅ Plausible | Moderate below-market is common |

---

## Cross-Page Issues

### 1. Consistent Layout Problem (All Pages)
- All three pages have content shifted right, with significant empty space on the left
- This appears to be a CSS grid/flexbox issue — possibly a left sidebar placeholder that's empty for logged-out users
- **Recommendation:** Check if a sidebar component is rendering empty on public pages; it should collapse to 0 width when not needed

### 2. Email Domain Inconsistency
- Homepage footer: hello@roviq.ai
- Pricing contact: hello@glassintel.xyz
- **Recommendation:** Use hello@glassintel.xyz consistently on the GLASS site

### 3. No Meta Tags / SEO Concerns
- All three pages return the same generic title "GLASS | Cannabis Market Intelligence"
- The pricing page and report card should have unique titles for SEO:
  - Pricing: "GLASS Pricing — $199/month Cannabis Market Intelligence"
  - Report: "Canna Provisions Holyoke Report Card — GLASS"

### 4. Client-Side Rendering Only
- All pages are pure client-side rendered (server returns empty shell)
- This means: no SEO indexing of content, no social media previews (OG tags), slow perceived load for content
- **Recommendation:** Implement SSR/SSG for at least the homepage and pricing page

---

## Priority Fix List

### 🔴 P0 — Fix Before Any Marketing Push
1. **Fix "AMHERST" → "HOLYOKE"** on report card — wrong city is a credibility killer
2. **Fix "Nearby Competitors: 0"** on report card — defeats the value proposition
3. **Fix "Pending applications: 0" display bug** on homepage — contradicts the "234" text

### 🟡 P1 — Fix This Week
4. Fix CSS layout — content shifted right / left empty space on all pages
5. Fix email domain inconsistency (use hello@glassintel.xyz everywhere)
6. Fix "Market Average: 0" in report card assortment section
7. Add navigation header to report card page
8. Fix /market link to go directly to homepage (or create proper /market route)

### 🟢 P2 — Fix Soon
9. Add "low confidence" markers for categories with <50 observations (Tincture, Topical)
10. Replace "Updated Just now" with actual timestamp
11. Fix table column truncation on homepage (Retail premium, Observations columns)
12. Add unique page titles/meta tags for SEO
13. Consider SSR for public pages (SEO, social sharing)
14. Add footer to report card page
15. Clarify sales chart x-axis (says "since 2018" but axis starts ~2021)
16. Move "API access (coming soon)" out of feature checklist into a roadmap note

---

## Overall Assessment

**Grade: B-**

The core product concept is strong — the CCC × GLASS cross-reference is genuinely valuable and unique. Data quality is generally good across major categories. The design is professional and the information architecture makes sense.

However, the three critical issues (wrong city on report card, 0 competitors, 0 pending licenses display bug) would undermine credibility with a cannabis operator who knows their own market. These must be fixed before sharing report card links with prospects or running any marketing campaigns.

The layout/CSS issues (content shifted right) are cosmetic but make the product look unfinished. Combined with the data issues, a first-time visitor might question whether GLASS is production-ready.

**Bottom line:** Fix the 3 P0 issues and the CSS layout, and this is a very solid public-facing product.
