# Decoded Shop — Website & Digital Presence Audit

**Audit Date:** February 9, 2026  
**Prepared by:** Roviq Digital Intelligence  
**URL:** https://decodedshop.myshopify.com/  
**Instagram:** @decoded.shop  
**Location:** Texas (806 area code — Lubbock/Amarillo/TX Panhandle region)  
**Industry:** Luxury streetwear / DTC fashion  
**Platform:** Shopify (standard plan, `.myshopify.com` subdomain — no custom domain active)

---

## STEP 1 — SCRAPE & CATALOG

### Sitemap Structure

The site is extremely thin. Total indexed sitemap sections:

| Sitemap Type | Count | Notes |
|---|---|---|
| Products | 37 | Single products sitemap file |
| Collections | 3 | `frontpage`, `decoded-noir`, `decoded` |
| Pages | 1 | `/pages/contact` (shipping policy only) |
| Blog | 1 | `/blogs/news` — **completely empty**, zero posts |

**Total unique pages:** ~42 (home + 37 products + 3 collections + 1 page + 1 empty blog)

This is an extremely small footprint. No About page, no FAQ, no lookbooks, no size guide, no returns policy page (separate from contact), no brand story page.

### Product Catalog (37 items)

**DECODED Collection (mainstream line):**

| Product | Price | Category | Images | Description |
|---|---|---|---|---|
| The Profile Rottie Tee | ~$45-65 | Tee | 1 | None |
| Kingdom has Fallen | ~$45-65 | Tee | 1 | None |
| SINNERS TALK | $65.00 | Tee | 1 | None |
| Pin head tee | $60.00 | Tee | 1 | None |
| 911 Turbo Shirt Black | $45.00 | Tee | 1 | None |
| 911 Turbo Sweatshirt | $120.00 | Sweatshirt | 1 | None |
| Velocity Sweatshirt | $120.00 | Sweatshirt | 2 | None |
| World Tour '25 | $45.00 | Tee | 2 | None |
| Desperado | $45.00 | Tee | 2 | None |
| Velocity | $45.00 | Tee | 2 | None |
| 911 Turbo White | $45.00 | Tee | 1 | None |
| Rush Black | $45.00 | Tee | 1 | None |
| Rush White | $45.00 | Tee | 1 | None |
| Motor Cross White | $45.00 | Tee | 1 | None |
| Motor Cross Black | $45.00 | Tee | 1 | None |
| Holster Tee Cream | TBD | Tee | 1 | None |
| Holster Tee Red | TBD | Tee | 1 | None |
| Ain't Ralph Tho Tee | TBD | Tee | 1 | None |
| Drive The Legacy Tee | TBD | Tee | 1 | None |
| Stop Soliciting Tee | TBD | Tee | 1 | None |
| We The Roses | TBD | Tee | 1 | None |
| Homeless Rich Zip Up | TBD | Outerwear | 1 | None |
| Decoded Angels Hoodie | TBD | Hoodie | 1 | None |
| Decoded Angels Tee | TBD | Tee | 1 | None |
| DAWG Hoodie | TBD | Hoodie | 1 | None |
| DAWG Youth Athletic Tee | TBD | Tee (Youth) | 1 | None |
| DAWG Adult Tee | TBD | Tee | 1 | None |
| Friday is Forever | TBD | TBD | 1 | None |
| Hand of God | TBD | TBD | 1 | None |
| Lone Wolf Tee | $45.00 | Tee | 1 | None |
| Lone Wolf Hoodie | $80.00 | Hoodie | 1 | None |

**DECODED NOIR Collection (luxury tier):**

| Product | Price | Category | Images | Description |
|---|---|---|---|---|
| Noir Eclipse | $130.00 | TBD | 1 | None — **ALL SIZES SOLD OUT** |
| All Glory Tan | TBD | TBD | 1 | None |
| All Glory Black | TBD | TBD | 1 | None |
| Broke Tee Yellow | $125.00 | Tee | 1 | None |
| Broke Tee Black | $125.00 | Tee | 1 | None |
| Noir Strata White Top | $150.00 | Top | 1 | None |
| Noir Strata White Bottom | $130.00 | Bottom | 1 | None |
| Noir Strata Black Top | $120.00 | Top | 1 | None |
| Noir Strata Black Bottom | $150.00 | Bottom | 1 | None |

### Pricing Summary
- **Decoded line:** $45–$120 (tees at $45–$65, sweatshirts at $120)
- **Decoded Noir line:** $120–$150 (positioning as luxury)
- **Hoodies:** $80

### Critical Finding: ZERO Product Descriptions
Not a single product in the entire catalog has a `body_html` description. Every single product description field is empty (`""`). This is catastrophic for SEO and conversion. A buyer sees a product image, a price, and a size selector. Nothing else. No fabric info, no fit guide, no story, no materials, no care instructions. Nothing.

### CTAs & Conversion Paths
- **Primary CTA on homepage:** "SHOP DECODED NOIR" → links to collection
- **No email signup** anywhere on the site
- **No SMS capture**
- **No pop-up** for first-time visitors
- **No loyalty program**
- **No referral program**
- **No newsletter**
- **Contact page** contains only a shipping policy (no contact form, no email, no phone)

### Navigation Structure
The navigation is minimal (likely just: Home, Collections, Contact). The theme appears to be a default or near-default Shopify free theme.

### Footer
- Payment method badges (Amex, Apple Pay, Diners Club, Discover, Google Pay, Mastercard, PayPal, Shop Pay, Visa)
- "Powered by Shopify" badge (not removed — screams amateur)
- © 2026 Decoded
- **No social media links visible in footer** (Instagram, TikTok, etc. not linked)
- **No legal pages** (Privacy Policy, Terms of Service not linked)

### Blog/Content Hub
- `/blogs/news` exists but is **100% empty**. Zero articles. Zero content. This is just a default Shopify blog sitting there doing nothing.

---

## STEP 2 — TECHNICAL ANALYSIS

### Platform & Tech Stack
- **Platform:** Shopify (standard plan)
- **Domain:** Still on `decodedshop.myshopify.com` — **no custom domain**
- **Note:** A custom domain `shopdecode.us` was previously associated but now returns a Shopify "This store does not exist" page — the domain has lapsed or been disconnected
- **Theme:** Appears to be a free/default Shopify theme with minimal customization
- **Analytics:** Unknown — no visible third-party analytics tags from fetch (likely just default Shopify analytics, no GA4, no Meta Pixel visible)
- **SSL:** ✅ Valid (Shopify-provided, automatic)
- **CDN:** Shopify CDN (cdn.shopify.com) — standard

### Page Load Performance
- Homepage response: **234ms** server response time (fast — Shopify CDN doing its job)
- Product pages: **150-200ms** response time
- The site is lightweight because there's almost nothing on it. Fast by default when there's nothing to load.

### Mobile Responsiveness
- Shopify free themes are mobile-responsive by default. The site will technically "work" on mobile.
- However, with only 1 product image per listing, no descriptions, and minimal navigation — the mobile experience is functional but barren.

### Broken Links / Issues
- **`shopdecode.us`** — the presumed custom domain — is **dead**. Returns Shopify expired domain page. This is a major issue if they've been sharing this URL on Instagram or anywhere else.
- **Noir Eclipse** — listed at $130 but **all sizes show "Variant sold out or unavailable."** This is a dead product sitting on the site. Either restock or remove.
- **Blog page** — exists but empty. Looks abandoned.

### ADA Accessibility
- **Alt text:** Shopify auto-generates alt text from product titles. Most image:caption fields are empty. Bare minimum coverage.
- **Contrast:** Without visual inspection, cannot fully assess, but free Shopify themes generally meet basic contrast requirements.
- **Keyboard navigation:** Default Shopify theme, should be functional.
- **Overall ADA grade:** Bare minimum. No proactive accessibility work done.

### Security Headers
- Standard Shopify-provided headers. Nothing custom configured. Adequate for a Shopify store.

---

## STEP 3 — DESIGN & UX EVALUATION

### Visual Design Quality: 3/10
The site uses what appears to be a stock/free Shopify theme with minimal customization. The homepage is essentially a single hero text block ("This isn't just fashion. This is DECODED NOIR...") with a button. There's no hero image, no video, no lookbook, no brand photography. The brand copy talks about "luxury" and "precision" but the site design communicates "just launched last weekend." The gap between brand aspiration and execution is enormous. This looks like a Shopify store someone set up in an afternoon — because it is.

### Brand Consistency: 4/10
The brand voice is strong and consistent in the limited copy that exists ("speaks in silence," "unapologetic," "move different"). The Decoded vs. Decoded Noir distinction shows brand architecture thinking. However, there's no visible logo treatment, no consistent color palette beyond black/white, no typography system, and no brand guidelines applied to the site. The product imagery is inconsistent — some are flat-lay photos, some appear to be renders, some are iPhone-quality shots. No cohesive visual language.

### Information Architecture: 4/10
With only 3 collections and 37 products, navigation should be trivially easy. And it is — in the sense that there isn't much to navigate. A first-time visitor can find products in 2 clicks. But the IA fails because:
- No filtering or sorting on collection pages
- No product categories beyond the two collections
- No "About" page to understand the brand
- No way to contact the brand (the "contact" page is just a shipping policy)
- No size guide (critical for clothing)

### Trust Signals: 1/10
This is the single biggest failure on the site. There are:
- **Zero reviews** on any product
- **No about page** — who makes this? Who designs it? Where is it made?
- **No press mentions**
- **No customer testimonials**
- **No team/founder photos**
- **No social proof** of any kind
- **No return policy** (only shipping policy, which states "all sales final" energy)
- **No certifications**
- Still on `.myshopify.com` subdomain — signals "not a real business" to many consumers

A customer is being asked to spend $45-$150 on clothing from a brand they've never heard of, with no reviews, no brand story, no return policy, no way to contact anyone, and no custom domain. That's an enormous ask.

### Imagery Quality: 4/10
Product imagery is mixed:
- Some products have **only 1 image** (most of them)
- Some images are flat-lay product shots (acceptable)
- Some appear to be graphic mockups/renders
- Image quality varies — some are 540x540px (very low for a clothing store), others are 1400x1400
- **Zero lifestyle/lookbook imagery** — no models, no styled shots, no context
- **Zero on-body photography** visible from the data
- For a brand claiming "luxury," the imagery does not deliver luxury

### Call-to-Action Clarity: 3/10
- Homepage has one CTA: "SHOP DECODED NOIR"
- Product pages have standard Shopify "Add to Cart" button
- No urgency elements (no "limited stock," no countdown timers)
- No cross-selling or upselling
- No "complete the look" suggestions
- No post-purchase CTA
- The site doesn't guide the user journey — it just presents a catalog

---

## STEP 4 — CONVERSION PATH ANALYSIS

### Primary User Journey

```
Land on homepage
  → Read one paragraph of brand copy
    → Click "SHOP DECODED NOIR" (or navigate to a collection)
      → See product thumbnails (no descriptions visible)
        → Click a product
          → See 1 image, a price, a size selector
            → Add to cart? (with zero supporting information)
              → Checkout (Shopify standard)
```

### Friction Points

1. **No product descriptions:** The single biggest conversion killer. A visitor cannot make an informed purchase decision. What fabric? What fit? What's the weight? How does it run? Is it oversized? True to size? Nothing.

2. **Single product images:** Most products have only ONE image. For a clothing brand, this is unacceptable. Customers need to see front, back, detail, and on-body shots. The industry standard is 4-8 images per product minimum.

3. **No size guide:** Selling clothing online without a size guide is asking customers to gamble. This directly increases cart abandonment and returns.

4. **No reviews:** Zero social proof. No way to know if anyone has ever bought or liked these products.

5. **No custom domain:** `decodedshop.myshopify.com` signals this isn't a serious operation. The previous domain `shopdecode.us` is dead.

6. **Sold-out products still visible:** Noir Eclipse shows all sizes as sold out. This is a dead end that wastes user attention.

7. **$13 flat-rate shipping:** For $45 tees, a $13 shipping cost is 29% of the product price. No free shipping threshold mentioned on the site (though the shipping policy mentions "full price mainline orders" get standard shipping — the language is confusing).

8. **No lead capture anywhere:** If someone leaves without buying, they're gone forever. No email popup, no SMS, no exit intent, no discount for first purchase. Zero remarketing infrastructure.

### Lead Capture & Follow-up
- **Email signup:** None
- **SMS capture:** None
- **Exit intent popup:** None
- **First-purchase discount:** None
- **Abandoned cart recovery:** Unknown (Shopify has basic built-in, but no evidence of enhanced flows)
- **Post-purchase automation:** No evidence of any

### Competitive Conversion Path Comparison

**Heights District (theheightsdistrict.com) — Dallas, TX luxury streetwear:**
- Custom domain ✅
- Product reviews (93 reviews on featured product) ✅
- Detailed product descriptions (weight, fit guide, model measurements) ✅
- Multiple product images ✅
- Physical retail location / pickup option ✅
- Free shipping threshold ($150) ✅
- Professional photography with models ✅

**For The South (forthesouth.com) — Texas streetwear:**
- Custom domain ✅
- Multiple collections with clear categories ✅
- Signature/hero products featured prominently ✅
- Email signup ✅
- Clear shipping/returns info ✅
- Brand storytelling throughout ✅
- Professional photography ✅

**Decoded Shop:**
- Custom domain ❌ (dead)
- Product reviews ❌
- Product descriptions ❌
- Multiple product images ❌ (mostly 1 per product)
- Retail location ❌
- Free shipping ❌
- Email/SMS capture ❌
- Brand story/about page ❌
- Professional photography ❌ (mixed quality)

---

## STEP 5 — COMPETITIVE COMPARISON

### Competitor 1: Heights District
- **URL:** https://www.theheightsdistrict.com/
- **Location:** Dallas, TX (Dallas Design District)
- **Design Quality:** 7/10
- **Mobile Experience:** Strong — responsive Shopify theme with good customization
- **Unique Features:** Physical flagship store with in-store pickup, hand-drawn custom artwork, 9oz premium blanks, cut-and-sew construction, model measurements on every product, review system with 90+ reviews
- **Price Range:** $60 tees (similar to Decoded)
- **What they do BETTER than Decoded:**
  - Professional product photography with model shots and measurements
  - Detailed product descriptions (fabric weight, fit guidance, construction details)
  - Customer review system with significant review volume
  - Custom domain with professional branding
  - Physical retail presence builds trust
  - Free shipping threshold
  - Clear brand identity and premium positioning backed by actual premium details
- **What Decoded does better:**
  - Decoded has a stronger two-tier brand architecture (Decoded + Decoded Noir)
  - Product naming is more evocative and storytelling-oriented

### Competitor 2: For The South (MITS)
- **URL:** https://forthesouth.com/
- **Location:** Texas (Southern US)
- **Design Quality:** 6/10
- **Mobile Experience:** Good — well-organized Shopify theme
- **Unique Features:** Strong Southern identity, vintage 1-of-1 pieces, workwear crossover, multiple curated collections, clear brand DNA
- **Price Range:** $35-$80 (slightly below Decoded)
- **What they do BETTER than Decoded:**
  - Deep brand storytelling woven throughout the site
  - Multiple well-organized collections (Signature, Vintage, Graphic, Workwear, Accessories)
  - Content-rich homepage with multiple editorial sections
  - Contact email prominently displayed
  - Clear shipping and returns messaging
  - Consistent visual identity
  - Accessories category (hats, snapbacks) for lower price point entry
- **What Decoded does better:**
  - Decoded's brand voice has more edge and premium aspiration
  - The Noir line at $120-150 positions higher-end

### Competitor 3: Corteiz (CRTZRTW)
- **URL:** https://www.corteiz.com/
- **Location:** London (global DTC)
- **Design Quality:** 8/10
- **Mobile Experience:** Excellent — minimal, intentional design
- **Unique Features:** Extreme scarcity model (drops sell out instantly), massive social media presence, guerrilla marketing, community-driven brand
- **Price Range:** $95-$295 (higher tier)
- **What they do BETTER than Decoded:**
  - Masterclass in brand mystique and scarcity
  - Professional product photography
  - Clean, minimal web design that matches brand energy
  - Massive organic social proof (millions of followers)
  - Custom domain with branded experience
  - Strategic use of "sold out" as a feature, not a bug
- **What Decoded does better:**
  - Decoded's product range is broader and more accessible price-wise
  - More available inventory (Corteiz is often completely sold out)

### Competitive Summary Table

| Factor | Decoded | Heights District | For The South | Corteiz |
|---|---|---|---|---|
| Custom Domain | ❌ | ✅ | ✅ | ✅ |
| Product Descriptions | ❌ | ✅ | ✅ | Minimal |
| Product Photography | 4/10 | 8/10 | 7/10 | 9/10 |
| Reviews/Social Proof | ❌ | ✅ (90+) | Limited | Organic |
| Email/SMS Capture | ❌ | ✅ | ✅ | ✅ |
| Brand Storytelling | Minimal | Good | Strong | Excellent |
| About/Team Page | ❌ | ✅ | ✅ | Minimal |
| Size Guide | ❌ | ✅ | ❌ | ❌ |
| Price Range | $45-150 | $60-80 | $35-80 | $95-295 |
| Blog/Content | ❌ (empty) | ❌ | ❌ | ❌ |

---

## STEP 6 — VERDICT

### Overall Grade: D-

This is a brand with genuine identity and aspiration running on a website that actively undermines both. The brand copy talks about "luxury," "precision," "power," and "exclusivity" — but the site screams "hobby project." There is a massive disconnect between the brand's self-image and its digital execution.

### Top 3 Things That Are Working

1. **Brand voice and naming:** The copy that exists is strong. "Decoded Noir," "speaks in silence and moves in Power," the product names (Desperado, Kingdom has Fallen, Noir Eclipse) — there's a real brand identity here. The two-tier architecture (Decoded for accessible, Noir for luxury) shows strategic thinking.

2. **Price architecture:** The $45-65 tee range is competitive and accessible. The $120-150 Noir range creates aspiration. This is smart tiering.

3. **Active product development:** The catalog shows consistent product additions from Feb 2024 through Jan 2026. The DAWG line (including youth sizing) and the Noir Strata sets (top + bottom) show the brand is experimenting and growing. The newest products (Lone Wolf, DAWG, Angels line) suggest momentum.

### Top 3 Things Actively Hurting Them

1. **No custom domain + dead previous domain:** The `decodedshop.myshopify.com` URL is the single most damaging credibility issue. The fact that `shopdecode.us` is dead means any previous marketing linking to that domain is now broken. This is a business-critical issue that should have been fixed yesterday.

2. **Zero product descriptions on EVERY product:** This is not an oversight on a few items — it's a systematic failure across all 37 products. For SEO, this means Google has essentially nothing to index. For conversion, buyers have zero information to make a purchasing decision. This alone is probably costing them 50%+ of potential sales.

3. **No lead capture or remarketing infrastructure:** No email signup, no SMS, no popups, no first-purchase incentive. Every visitor who doesn't buy on their first visit is permanently lost. For a brand at this stage, building an owned audience list should be the #1 priority after fixing the site basics.

### Single Biggest Missed Opportunity

**Brand storytelling.** This brand clearly has a founder with vision and taste — the product names, the brand copy, the two-tier architecture all show it. But there's zero brand story on the site. No About page, no founder story, no "why" behind the brand. In the indie streetwear space, the story IS the product. Brands like Corteiz, Madhappy, and Fear of God didn't grow because of their website UX — they grew because they had compelling stories and community. Decoded has the raw ingredients for a story (TX roots, luxury aspiration, edgy product names, the Noir concept) but none of it is being told. An About page, a founder video, Instagram content linked to the site, and brand storytelling throughout the shopping experience would transform this store.

### Estimated Effort to Fix

**Medium rebuild — NOT a full tear-down.**

The good news: the Shopify infrastructure is fine. The product catalog exists. The brand identity exists. This doesn't need to be rebuilt from scratch. But it needs significant work:

**Immediate fixes (1-2 weeks, no cost):**
- Get a custom domain connected and working ($15/year)
- Remove "Powered by Shopify" from footer
- Write product descriptions for all 37 products
- Add social media links to footer/header
- Remove or hide sold-out products (Noir Eclipse)
- Add an About page with brand story
- Add a Returns/Exchange policy page
- Add a size guide page
- Set up basic email capture (Shopify built-in or free Klaviyo tier)

**Short-term improvements (2-4 weeks, $500-2,000):**
- Upgrade to a premium Shopify theme that matches brand positioning
- Professional product photography (minimum 4 images per product, including on-body)
- Install review app (Judge.me free tier or Loox)
- Set up Klaviyo or similar for email/SMS marketing flows
- Add Meta Pixel and GA4 tracking
- Create a homepage that actually sells (hero imagery, featured products, brand story sections)

**Medium-term growth (1-3 months, $2,000-5,000):**
- Lookbook/editorial photography
- Launch blog with brand content
- Build email welcome series and abandoned cart flows
- Create a launch/drop marketing system
- Instagram integration and shoppable posts
- Consider custom domain that matches the brand better

**The ask was for a mobile app + growth plan.** An app is premature. The website fundamentals need to be fixed first. No app can compensate for a store with no product descriptions, no reviews, no brand story, and a broken domain. Fix the house before you build an addition.

---

*Audit completed by Roviq Digital Intelligence — February 9, 2026*
