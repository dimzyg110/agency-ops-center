# GLASS Consumer Site — UX/UI Design Review

**Reviewer:** Senior Frontend Engineer  
**Date:** 2026-02-15  
**Scope:** `/prices` page, DealCard component, layout, and overall visual system

---

## Executive Summary

The current design suffers from **"AI tool syndrome"** — heavy use of glassmorphism, neon glows, and monospace labels that signal "tech demo" rather than "professional product." The dark mode feels harsh and unpolished. Cards are oversized and information-dense without clear hierarchy. Trust signals are absent despite being a price comparison tool where credibility is paramount.

---

## 1. Specific Problems Found

### A. Dark Mode — Unprofessional/Harsh
| Issue | Current | Problem |
|-------|---------|---------|
| Background | `#06090D` (near-black blue) | Too dark, feels like a coding IDE, not a consumer product |
| Surface layers | `white/5`, `white/10` | Creates muddy grays that read as "dirty" rather than "premium" |
| Accent colors | `#00E5A0` (neon teal) + `#FFB020` (amber) | High-saturation gradient screams "crypto/AI tool" |
| Glow effects | `shadow-[0_0_40px_-12px_rgba(255,176,32,0.25)]` | Dated glassmorphism trend, not Apple-level refinement |

**Apple-level dark mode characteristics:**
- Background: `#000000` pure black OR `#1C1C1E` (iOS dark gray) — never blue-tinted
- Surfaces: Distinct elevation steps with subtle borders, not transparency
- Accents: Desaturated, purposeful (SF Blue `#0A84FF`, mint at ~70% saturation)
- No glow effects — use subtle shadows and borders instead

### B. Cards — Too Large, Poor Information Density
| Element | Current Size | Recommended |
|---------|--------------|-------------|
| Card padding | `p-5` (20px) | `p-4` (16px) |
| Hero savings number | `text-3xl` (~30px) | `text-xl` (~20px) |
| Savings label | Full text "potential savings" | Icon + compact label |
| Card border radius | `rounded-2xl` (16px) | `rounded-xl` (12px) |
| Gap between cards | `gap-4` (16px) | `gap-3` (12px) |

**Current card problems:**
1. The savings amount dominates visually but isn't actionable
2. Too much vertical spacing between elements (4 separate `mb-*` margins)
3. "Compare X prices" CTA is full-width but low contrast — poor affordance
4. Product image missing from DealCard (present in PriceCard but unused)

### C. Site Feels Plain/Empty
| Issue | Evidence | Impact |
|-------|----------|--------|
| No product imagery | `image_url` exists in type but not rendered in DealCard | Looks like a database viewer, not a shopping tool |
| Generic headings | "Shop smarter. Save every cart." | Marketing fluff, no concrete value |
| Monospace overuse | "Consumer Price Radar", nav links, badges | Signals "developer tool" not "consumer app" |
| Empty states | Just "No products found." | Missed opportunity for guidance |

### D. Generic AI Look — Missing Human Psychology
**Current signals:**
- `font-mono` on 8+ elements (labels, nav, prices, badges)
- Gradient text/bar everywhere (`from-[#00E5A0] to-[#FFB020]`)
- Glassmorphism cards with backdrop blur
- "Intelligence" language in copy

**Human psychology design principles missing:**
- **Social proof:** No user counts, reviews, or "X people saved today"
- **Scarcity/urgency:** No "Price updated 2 hours ago" prominence
- **Authority:** No data source credibility, no "Official MA dispensary data"
- **Tangible outcomes:** "Save $23" vs abstract "Shop smarter"

### E. Missing Trust Signals (Critical for GTM)
**Required per GTM brief:** "Verified Products • Post-Tax Prices"

**Current state:**
- Only trust element: `text-[10px] text-glass-subtle` disclaimer buried at bottom of card
- No verification badges on products
- No explanation of data sources
- No security/privacy indicators
- No "last updated" timestamps visible to user

**Apple/Facebook trust patterns:**
- Clear data provenance ("Data from official MA CCC listings")
- Verification badges (checkmarks, "Verified" chips)
- Transparent pricing ("Tax included" vs "+ tax at checkout")
- Security indicators (HTTPS badge, privacy links)

---

## 2. Recommended Changes

### Color System Refactor
```css
/* Current → Recommended */
--bg-primary: #06090D → #0A0A0A      /* Pure dark gray, no blue tint */
--bg-elevated: white/5 → #141414      /* Solid surface, no transparency */
--accent-primary: #00E5A0 → #34C759   /* Apple-style mint green, desaturated */
--accent-secondary: #FFB020 → #FF9500 /* Warmer, less saturated amber */
--border: white/10 → #262626          /* Visible but subtle borders */
```

### Card Redesign
```
┌─────────────────────────────────────┐
│ [IMG]  Brand Name          💰 Save $23 │
│        Strain Name         at Best Store│
│        3.5g • Flower                   │
│ ─────────────────────────────────── │
│ $32 ───────●────────────── $45      │
│ Best          Avg           High    │
│                                     │
│ [✓ Verified] [Updated 2h ago]       │
│                                     │
│ [      Compare 12 Prices      ]     │
└─────────────────────────────────────┘
```

**Specific changes:**
1. **Add product image** — 48x48px rounded, left-aligned with text
2. **Compress savings display** — "Save $23 at [Store Name]" inline, not hero
3. **Price bar clarity** — Show "Best/Avg/High" labels, not just min/max
4. **Add trust chips** — "✓ Verified", "Updated X ago" as pill badges
5. **Improve CTA** — Solid background `#1C1C1E` → `#34C759` on hover

### Typography Cleanup
| Element | Current | Recommended |
|---------|---------|-------------|
| Category labels | `font-mono uppercase tracking-[0.2em]` | `font-sans text-xs font-medium text-muted` |
| Nav links | `font-mono` | `font-sans font-medium` |
| Price displays | `font-mono` | `font-sans tabular-nums` |
| Hero heading | `font-display text-4xl` | Keep, but reduce to `text-3xl` |

### Trust Signals (Add Everywhere)
1. **Global trust bar** below nav:
   ```
   ✓ Verified Products  •  Post-Tax Prices  •  Updated Hourly  •  MA Dispensary Data
   ```

2. **Card-level trust:**
   - "✓ Verified" badge on each product
   - "Updated 2h ago" freshness (move from small text to pill badge)
   - Store count with icon: "🏪 12 stores"

3. **Footer additions:**
   - Data source attribution
   - "How we verify prices" link
   - Privacy/security badges

### Layout Improvements
1. **Reduce card size** — 3 columns on desktop (currently 2)
2. **Add product grid** — Consistent image thumbnails
3. **Hero simplification** — Remove gradient glow, use solid background `#141414`
4. **Search prominence** — Make search bar larger, more central
5. **Add filter sidebar** — Categories, price range, distance (desktop)

---

## 3. Prioritized Fix List

### P0 — Critical (Do First)
1. **Add trust bar** — "Verified Products • Post-Tax Prices" below navigation
2. **Fix background color** — Change `#06090D` → `#0A0A0A` (pure dark)
3. **Add product images to DealCard** — Currently missing despite data available
4. **Remove excessive glow effects** — Replace with subtle borders

### P1 — High Impact
5. **Reduce card padding** — `p-5` → `p-4`, shrink savings display
6. **Fix typography** — Remove `font-mono` from nav/labels, keep only for data
7. **Desaturate accents** — `#00E5A0` → `#34C759`, `#FFB020` → `#FF9500`
8. **Add "Updated X ago" badges** — Make freshness visible, not hidden

### P2 — Polish
9. **3-column grid on desktop** — Better information density
10. **Improve empty states** — Add helpful guidance, not just "No products"
11. **Add filter sidebar** — Category, price, distance filters
12. **Social proof elements** — "X people compared prices today"

### P3 — Future
13. **Price alert CTA** — "Get notified when price drops"
14. **Favorite/save functionality** — Heart icon on cards
15. **Store detail pages** — Full dispensary profiles

---

## 4. Before/After Comparison

| Aspect | Current (AI Tool) | Target (Apple/Facebook) |
|--------|-------------------|-------------------------|
| **Color** | Neon teal/amber on dark blue-black | Muted mint/orange on pure black |
| **Effects** | Glows, blurs, gradients | Solid surfaces, subtle shadows |
| **Typography** | Monospace everywhere, wide tracking | Clean sans-serif, tight hierarchy |
| **Cards** | Large, hero numbers, dense | Compact, scannable, image-led |
| **Trust** | Buried disclaimer | Prominent verification badges |
| **Value prop** | Abstract "intelligence" | Concrete savings, verified data |

---

## 5. Implementation Notes

**Files to modify (in order):**
1. `app/globals.css` — Fix color tokens, remove glow effects
2. `tailwind.config.ts` — Update accent colors
3. `app/layout.tsx` — Add trust bar component
4. `components/deal-card.tsx` — Redesign layout, add images, compress savings display
5. `app/prices/page.tsx` — 3-column grid, reduce hero size
6. `components/nav.tsx` — Remove monospace, simplify

**Key metrics to watch:**
- Time-to-first-product-scan (should decrease with smaller cards)
- Click-through rate on "Compare" buttons (should increase with better CTA design)
- Bounce rate (should decrease with trust signals)

---

*End of Review*
