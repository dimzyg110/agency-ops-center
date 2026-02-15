# GLASS Product Image Fallback Plan

**Date:** 2026-02-15  
**Purpose:** Solve 70% missing product images with minimal engineering effort

---

## 1. Current State Analysis

### Image Extraction by Source

| Source   | Images Extracted? | How |
| -------- | ----------------- |-----|
| **Dutchie** | ✅ Yes | DOM scraping (`img` tags, data-src, currentSrc) - lines 79-82, 240-272 in `scrapers/dutchie/index.ts` |
| **Leafly** | ✅ Yes | DOM scraping (same method) - lines 240-272 in `scrapers/leafly/index.ts` |
| **Jane** | ❌ No | Code references `item.raw.imageUrl` but never actually extracts it from the page |

### Database Schema
- `public.products` table has `image_url` TEXT column (added via migration 005)
- No brand logo columns exist in current schema
- `brand_authority` table has 1,001 brands but no logo URLs

### The Problem
- 70% of product cards are missing images
- Jane scraper doesn't extract images at all
- Even Dutchie/Leafly captures may be incomplete due to lazy loading, CAPTCHAs, etc.

---

## 2. Evaluation of Fallback Options

### Option A: Brand Logos as Fallback
**Approach:** Use brand logo images when product image is missing

| Factor | Assessment |
|--------|------------|
| Implementation | ❌ Complex - no logo URLs in current DB, would need to scrape brand pages |
| Data sourcing | ❌ Would require new scraping (Leafly/Weedmaps brand directories) |
| Maintenance | ❌ Logos change, would need periodic re-scraping |
| Time to implement | 2-3 weeks (new scraper + data pipeline) |

**Verdict:** Over-engineered for immediate need

---

### Option B: Category-Based Placeholder Images ✅ RECOMMENDED
**Approach:** Show a styled placeholder/icon based on product category

| Factor | Assessment |
|--------|------------|
| Implementation | ✅ Simple - frontend change only |
| Data required | ✅ Already available (`products.category` field) |
| Maintenance | ✅ Zero - static assets |
| Time to implement | 1-2 days |

**Categories to support (from existing data):**
- Flower 🌸
- Edibles 🍫
- Concentrates 💎
- Vape/Tinctures 💨
- Topicals 🧴
- Pre-rolls 🚬
- Accessories 🎯
- Other/Missing ❓

**Implementation:**
1. Create SVG icons or colored placeholders for each category
2. Update frontend to show category placeholder when `image_url` is null
3. Add subtle brand name overlay if brand is known

---

### Option C: One-Time AI Image Gathering
**Approach:** Use AI to generate/retrieve images for top 500 products only

| Factor | Assessment |
|--------|------------|
| Implementation | ❌ Complex - requires AI API calls, image hosting |
| Rate limits | ❌ Would hit provider limits at scale |
| Quality | ⚠️ Mixed - AI-generated cannabis images often look fake |
| Maintenance | ❌ No ongoing source for new products |

**Verdict:** Not practical for product imagery (unlike logos which are simple)

---

### Option D: Hybrid (Recommended Extended)
**Approach:** Combine Option B with future Option A

| Phase | Action |
|-------|--------|
| **Now** | Deploy category placeholders (2 days) |
| **Future** | Add brand logo scraping for top 100 brands only (if needed) |

---

## 3. Recommended Implementation Plan

### Phase 1: Category Placeholders (Do This Week)

```
Frontend Changes:
├── Create /assets/images/categories/ folder
│   ├── flower.svg (purple bud icon)
│   ├── edibles.svg (brown chocolate icon)
│   ├── concentrates.svg (gold shatter icon)
│   ├── vape.svg (gray pen icon)
│   ├── topical.svg (cream tube icon)
│   ├── preroll.svg (joint icon)
│   └── default.svg (gray question mark)
└── Update ProductCard component:
    └── If !image_url → show category icon with brand name overlay
```

**CSS Styling:**
- Rounded corners matching product card design
- Gradient background by category (subtle, not distracting)
- Brand name in corner overlay
- Hover state shows "View Product" - doesn't need image

### Phase 2: Optional Enhancement (Future)
- Add brand logo fetching for top 50 brands only
- Store in `brand_authority.logo_url` column
- Priority: Low (category placeholders solve 90% of UX)

---

## 4. Why Not Build Image Scraping Pipeline?

**Arguments for building it:**
- "Would solve the problem permanently"
- "Competitors have product images"

**Arguments against:**
1. **Bot detection arms race** - Dutchie/Leafly will block eventually
2. **Rate limits** - 160K products = massive scraping job
3. **Maintenance burden** - Site changes break scrapers constantly
4. **Law灰色地带** - Some dispensaries don't allow scraping
5. **ROI unclear** - Do users actually leave due to missing images?

**Category placeholders solve:**
- ✅ Visual consistency
- ✅ Brand identification
- ✅ Zero maintenance
- ✅ Fastest path to launch

---

## 5. Action Items

| Owner | Task | Estimate |
|-------|------|----------|
| Frontend | Create category SVG assets | 4 hours |
| Frontend | Update ProductCard to show placeholders | 4 hours |
| Frontend | Add brand name overlay on placeholder | 2 hours |
| QA | Test across all categories | 2 hours |

**Total:** ~1 day of dev time

---

## 6. Summary

**Recommended:** **Option B - Category-Based Placeholders**

- Fastest to implement (1 day vs 2-3 weeks)
- Solves 70% image gap immediately  
- Zero ongoing maintenance
- Can enhance with brand logos later if needed

Don't build a complex image scraping pipeline when:
- 70% of your catalog is still missing brands entirely (per GLASS-STATE.md)
- Category placeholders provide equivalent UX for product discovery
- Bot detection will always be an arms race
