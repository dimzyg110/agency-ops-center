# GLASS UX/UI Cleanup Plan

## Executive Summary
Clean up GLASS (glassintel.xyz) to achieve: **professional, instantly useful, visual clarity**

---

## Phase 1: Research Findings

### Current State
- **Redirect**: Home `/` → `/prices` (good, gets users to value fast)
- **Colors**: Teal (#00E5A0) + Amber (#FFB020) + copper (#C45A3C)
- **Theme**: Dark components on light background (CRITICAL BUG)
- **Typography**: Playfair Display (display) + Geist (sans) + JetBrains Mono
- **Pages**: Prices, Store, Brands
- **Navigation**: Minimal - only Prices + Brands

### Critical Issues

| Priority | Issue | Impact |
|----------|-------|--------|
| P0 | Theme mismatch (light class, dark components) | Visual breakage |
| P0 | No hero CTA | Users don't know what to do |
| P0 | Minimal footer missing links | No trust/legibility |
| P1 | Color palette not cannabis-appropriate | Brand confusion |
| P1 | Navigation gaps (no About/How-it-works) | No context |
| P2 | Inconsistent border styling | Visual noise |
| P2 | Mobile nav could be better | UX friction |

---

## Phase 2: Visual Design Plan

### Color Palette Recommendation

**Option A: Cannabis-Industry Appropriate (Recommended)**
```
Primary: #22C55E (Green - trust, cannabis)
Secondary: #F59E0B (Amber - deals, savings)
Background: #0A0A0A (Black - premium dark)
Surface: #111111 (Elevated dark)
Text: #FFFFFF / #A1A1AA (White/muted)
Accent: #8B5CF6 (Purple - differentiation)
```

**Option B: Keep Current, Fix Execution**
- Keep teal (#00E5A0) + amber (#FFB020)
- Make dark mode consistent
- Add green (#22C55E) as "cannabis" signal

### Typography
- **Display**: Playfair Display (keep - elegant)
- **Sans**: Geist (keep - clean, modern)
- **Mono**: Keep for prices/stats
- Add: Proper size scale (xs, sm, base, lg, xl, 2xl, 3xl, 4xl)

### Spacing System
- Consistent 4px base unit
- Cards: 16px (p-4), 20px (p-5), 24px (p-6)
- Section gaps: 24px, 32px, 48px

---

## Phase 3: UX Improvements

### Hero Section (First 3 Seconds)
**Current**: Search form dominates but no clear message
**Goal**: User immediately understands value proposition

```
┌─────────────────────────────────────────┐
│  ✓ Verified Products  ✓ Post-Tax      │  <- Trust bar (keep)
│                                         │
│  Shop smarter. Save every cart.        │  <- H1 (keep)
│  Compare live cannabis prices...       │  <- Subtitle (keep)
│                                         │
│  [Search form here]                    │  <- Primary action
│                                         │
│  1,247 products • 4,500 prices         │  <- Stats (keep)
└─────────────────────────────────────────┘
```

**Add**: Clear CTA button "Start Comparing" or make search more prominent

### Search/Filter Experience
- Keep current search + category pills (working well)
- Add: Clear visual feedback on active filters
- Add: Result count / "X products found"

### Product Cards
- Keep current card design (good)
- Add: Hover states already present ✓
- Improve: Border consistency

### Navigation
- Add: "How it Works" or "About" link
- Add: Mobile hamburger menu already present ✓
- Consider: Breadcrumbs on store/product pages

### Mobile Experience
- Verify: Touch targets (44px minimum)
- Verify: Font legibility at small sizes
- Add: Sticky search/categories on scroll

---

## Phase 4: Implementation Plan

### Quick Wins (Execute First)

1. **Fix theme mismatch** - Change `className="light"` to proper dark mode
2. **Add hero CTA** - "Start Comparing" button or make search primary
3. **Expand footer** - Add links: About, How-it-works, Privacy, Terms

### Medium Effort

4. **Color refinement** - Adjust palette toward cannabis-appropriate
5. **Navigation improvements** - Add missing links
6. **Border/spacing consistency** - Standardize card borders
7. **Mobile polish** - Touch targets, legibility

### Lower Priority

8. **New components** - How-it-works page, about page
9. **Animation polish** - Refine transitions
10. **Loading states** - Skeleton improvements

---

## Files to Edit

```
consumer-web/
├── app/
│   ├── layout.tsx          <- Theme fix, nav adjustments
│   ├── page.tsx            <- (redirects to prices)
│   ├── globals.css         <- Theme variables, spacing
│   ├── prices/page.tsx    <- Hero CTA, results improvement
│   └── footer.tsx          <- Expanded footer
├── components/
│   ├── nav.tsx             <- Additional links
│   ├── footer.tsx          <- New footer content
│   ├── search-form.tsx     <- CTA improvements
│   └── deal-card.tsx       <- Border consistency
└── tailwind.config.ts      <- Color palette updates
```

---

## Success Metrics

- [x] Theme is consistent (dark mode works)
- [x] Hero clearly communicates value in 3 seconds
- [x] Users can immediately start searching/comparing
- [x] Footer provides navigation + trust signals
- [ ] Mobile experience is solid (needs testing)
- [ ] No visual clutter or confusion (partially - more work needed)
- [ ] Professional, clean aesthetic (improved)

---

## Rollout

1. [x] Quick fixes first (theme, CTA, footer)
2. [ ] Test on mobile
3. [ ] Refine colors/spacing
4. [ ] Full review
5. [ ] Ship to production
