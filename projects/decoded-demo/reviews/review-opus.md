# DECODED Demo — Senior UI/UX Design Review

**Reviewer:** Opus (Senior UI/UX Designer)
**Date:** 2026-02-10
**Asset:** TikTok-style vertical feed — luxury streetwear mobile app
**Live URL:** https://roviq-ai.github.io/decoded-demo/

---

## Overall Impression

This is a strong first pass. The core concept (full-bleed video cards, dark theme, gold accents, drop countdowns) is the right direction for luxury streetwear. The TikTok scroll mechanic is smart — it's what the target demographic already lives in. But the execution has gaps that a brand owner will notice, especially one who's seen SNKRS, Confirmed, and the KITH app. The demo currently reads more "talented developer built this over a weekend" than "we spent three months perfecting every pixel."

Below is a breakdown by category with scores, specific issues, and code-level fixes.

---

## 1. Visual Hierarchy — 6/10

### What works
- **Product name dominance.** The massive `clamp(38px, 11vw, 56px)` title is correctly the loudest element. Good.
- **Bottom-anchored content.** Stacking info at the bottom with a gradient fade-up mirrors TikTok/Reels conventions. Users know where to look.
- **Scarcity tag above the title.** Correct placement — it primes the viewer before they read the name.

### What doesn't work

**The price is visually lost.** At `font-weight: 200` and `fontSize: 30`, the price floats between the title and countdown without enough presence. For a $120-$150 product, the price IS the conversion signal. It needs more weight or a different treatment.

```jsx
// CURRENT — too light, blends into the noise
fontWeight: 200, fontSize: 30

// FIX — give it just enough weight to anchor
fontWeight: 300, fontSize: 28, 
// OR: make the dollar sign and number the same weight,
// drop the "USD" suffix entirely (it's unnecessary clutter)
```

**The countdown competes with the price.** Both are roughly the same visual weight and sit next to each other. The eye doesn't know which to read first. The countdown should be subordinate to the price, not equal.

**The subtitle is nearly invisible.** `color: rgba(245,240,232,0.35)` at `fontSize: 13` is too dim. Subtitles like "Black Top" and "Hoodie" tell the customer what the product actually IS. If it's important enough to include, it's important enough to read. Bump to `0.45` opacity minimum.

**Right-side action buttons lack a visual anchor.** The fire/skull/share column floats at `right: 14` with no background container and no relationship to the content below. On bright video frames, those 5% opacity circles will vanish. They need either a persistent subtle backdrop or stronger borders.

**Missing: product category/type indicator.** A customer scrolling fast needs to know "is this a tee, hoodie, or jacket?" at a glance. The subtitle tries to do this but it's too subtle and inconsistent (some products have no subtitle at all).

---

## 2. Animation Quality — 7/10

### Premium animations
- **Ken Burns video zoom** (`slow-zoom 12s`). Subtle, cinematic, correct. The 1.08 scale endpoint is restrained. This is good.
- **Gold divider fade-in.** The staggered `reveal()` system with `cubic-bezier(0.16,1,0.3,1)` is a nice touch — that easing curve gives a satisfying deceleration.
- **Glass button breathe** (`glass-glow-breathe 3.5s`). The multi-layered box-shadow animation is genuinely well done. It feels like real glass catching light.
- **Draw-check animation** on vault confirmation. Small detail, feels polished.

### Animations that cheapen the experience
- **Gold dust particles.** Six dots floating upward on a loop reads more "birthday card" than "luxury." The particle size (1-2.5px), count (6), and linear trajectory are too simple. Either commit to a proper particle system with varying velocities, drift, and fade curves, or remove them entirely. Half-done particles are worse than no particles.
- **Sparkles on the countdown.** Random 2-3px dots popping around the timer every 350ms is distracting and unnecessary. The countdown is already gold on dark — it doesn't need sparkles to draw attention. This is the single most "cheap" feeling element. **Remove entirely.**
- **FireBurst on reaction tap.** 10 radial particles in 3 colors (orange, gold, cream) — the concept is fine but the execution is too mechanical. All particles launch simultaneously from center and die at the same time. Real fire bursts have staggered timing and varying decay rates. Either invest in the physics or simplify to a single ring pulse.
- **Letter-breathe on the DECODED watermark.** The letter-spacing animation from `0.4em` to `0.55em` is distracting. Luxury brands don't animate their wordmarks like breathing exercises. Make it static or use a very slow opacity fade (8+ seconds, between 0.12 and 0.18 opacity).
- **Ticker animation at 24s.** The scrolling banner feels like a stock ticker from 2005. The text at 9px is too small to read at speed. For a drop countdown banner, a static centered treatment would feel more premium.

### Missing animations
- **No haptic feedback patterns.** On mobile, the reaction buttons should trigger `navigator.vibrate()` on tap. This is table stakes for luxury app feel.
- **No scroll-linked parallax.** The video backgrounds could shift slightly during scroll transitions to add depth. Currently the snap is abrupt.
- **No exit animation.** Cards enter with `reveal()` but have no exit. When scrolling away, content should gracefully fade/slide, not just disappear.

---

## 3. Typography — 5/10

This is the weakest area.

### The problem: Inter for everything

Inter is a good UI font. It is not a luxury font. Using Inter at weight 900 for product titles, weight 600 for labels, weight 200 for prices — you're asking one workhorse font to do jobs it wasn't designed for. Every luxury streetwear brand (Fear of God, Rhude, Amiri, Off-White) uses display typefaces for product names and clean sans-serifs for supporting text. Inter for titles reads "SaaS dashboard," not "exclusive drop."

```css
/* SUGGESTED TYPE STACK */
/* Titles: A condensed or display face */
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
/* OR for more luxury: use a locally hosted version of Monument Extended, 
   Neue Machina, or PPNeueMontreal */

/* Body/UI: Inter is fine here */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
```

### Specific issues

**Product title tracking is too tight.** `letterSpacing: -0.035em` at 900 weight creates a cramped, heavy block. For stacked two-line names like "NOIR\nSTRATA," you need either tighter line-height with looser tracking, or a condensed typeface that naturally reads at tight spacing.

**Too many font sizes.** I count at least 8 distinct sizes: 8px, 9px, 10px, 12px, 13px, 14px, 16px, 30px, 38-56px. That's a type scale with no scale. Pick 5 sizes max and commit:
- Display: 48px (product name)
- Title: 28px (price)
- Body: 14px (tags, labels)
- Caption: 11px (counts, metadata)
- Micro: 9px (ticker, watermark)

**The "USD" suffix on the price.** Nobody in streetwear writes "USD" after a price. It's either "$120" or "120 USD" on a luxury e-com site, but the way it's styled here (12px, 0.25 opacity, 0.1em tracking) makes it look like a rendering artifact. Remove it.

**Countdown label "LEFT" / "EXPIRED".** At 8px and 0.2 opacity, this is functionally invisible. Either make it readable (10px, 0.4 opacity) or integrate it into the countdown design properly.

---

## 4. Interaction Design — 6/10

### What works
- **Vault button state machine.** The idle → pulse → done → idle cycle with a 2.8s cooldown is well-thought-out. The glass button treatment with the refraction drift and shine sweep is the best-executed element in the entire demo.
- **Scroll snap behavior.** `scroll-snap-type: y mandatory` with `scroll-snap-stop: always` ensures each card gets full attention. Correct for this format.
- **Debounced reaction buttons.** The 500ms cooldown on fire/skull prevents spam. Good.

### What doesn't work

**No size selection.** You can "Add to Vault" but you can't pick a size. For apparel, this is a blocking UX gap. Even if this is a demo, a brand owner will immediately ask "where do they pick their size?" Add a size selector (S/M/L/XL chips) above the vault button, or make the vault action open a bottom sheet.

**No product image.** Video backgrounds are great for mood, but customers need to see the actual garment clearly. There should be a way to tap and see a static product shot, or the video should include a clean product reveal moment. Right now, users have no idea what the product looks like.

**The share button does nothing visible.** No state change, no feedback, no animation. It's a dead button. At minimum, add the same ring-expand animation as fire/skull, or show a share sheet mock.

**Swipe indicator is too subtle.** Two chevrons at 0.4 and 0.25 opacity won't register for first-time users. The swipe-up affordance needs more presence on the first card, then can fade after the first scroll.

**No way to scroll back up.** Snap scrolling with `always` stop means overshooting a card and going back is frustrating. Consider adding dot indicators on the side (like Instagram Stories) so users know where they are and can orient.

**"Built by Roviq" on the last card.** This is fine for a demo pitch deck, but it should be barely visible, not in the content area. Move it to a fixed footer that appears only on the last card, outside the content flow.

---

## 5. Color Palette — 7/10

### What works
- **The core palette is correct.** `#0D0D0D` charcoal, `#C9A84C` matte gold, `#F5F0E8` warm offwhite — this is a proven luxury combination. It works for the same reason it works on Audemars Piguet and Tom Ford packaging.
- **Per-card gradient tinting.** Each product has a unique background gradient (purple tint for Noir Strata, teal for Hand of God, etc.). This is a smart way to differentiate cards while maintaining the dark theme. The tints are subtle enough to not clash with the gold.
- **Gold at low opacity for UI elements.** Tags, countdown borders, and ambient shapes use gold at 0.04-0.15 opacity. This maintains the gold identity without overwhelming.

### What needs adjustment

**The orange in FireBurst (`#FF6B35`) is jarring.** It's the only warm-bright color in the entire palette and it clashes with the matte gold. Replace with a warmer amber:

```jsx
// CURRENT
color: i % 3 === 0 ? '#FF6B35' : ...

// FIX — stay in the gold family
color: i % 3 === 0 ? '#D4A03C' : i % 3 === 1 ? '#C9A84C' : '#E8D48B'
```

**No accent color for urgency.** When a countdown is under 2 hours (like "BROKE TEE" at 1h48m), the timer should shift to a warm red or amber to signal urgency. Currently all countdowns look the same regardless of time remaining.

**The vignette is too uniform.** `rgba(0,0,0,0.35)` across the entire card makes the center feel muddy on some videos. Consider reducing it to 0.2 or making it more concentrated at the edges.

---

## 6. What's Missing — Critical Gaps

### Must-have for a luxury app pitch

1. **Product imagery.** Without a clear shot of the garment, this is a mood board, not a shopping experience. Add a product image layer that sits between the video and the UI, or add a "tap to view" detail overlay.

2. **Size selection UI.** Even as a demo, omitting sizes signals "we haven't thought about the purchase flow." Add a row of size chips.

3. **Cart/bag indicator.** After "Add to Vault," where does it go? There's no bag icon, no count badge, no way to see what you've saved. Add a subtle bag icon in the top-right with a gold dot when items are added.

4. **Navigation.** No bottom nav, no way to get to a profile, search, or collection view. A luxury app needs at minimum: Feed / Search / Vault / Profile. Even ghost icons would show the brand owner "we've planned the full experience."

5. **Loading states.** Videos load asynchronously and the `videoLoaded` flag handles opacity, but there's no skeleton or shimmer placeholder while loading. On slow connections, users see a flat gradient for 2-5 seconds with no indication that content is coming.

6. **Brand story moment.** Luxury streetwear is about narrative. There's no "about this drop" text, no designer note, no collection story. Even 2 lines of copy per product would add depth.

7. **Sound design hint.** The best luxury apps (SNKRS, Confirmed) use subtle audio cues. Consider adding a muted speaker icon that implies audio is available, even if the demo doesn't implement it.

8. **Pull-to-refresh.** Standard mobile pattern. Its absence feels like a web page pretending to be an app.

---

## 7. What to Remove — Things That Cheapen It

1. **Sparkles component.** Remove entirely. Random dots popping near the countdown look like a Web 1.0 effect. The countdown is already gold, already has border shimmer. Sparkles dilute the luxury feel.

2. **Gold dust particles.** In their current form (6 tiny dots on a linear path), they look cheap. Either invest in a proper GPU-accelerated particle system with 20+ particles, varying velocities, and organic drift patterns, or cut them. Half-measures read as amateur.

3. **The ticker banner.** A scrolling marquee at 9px font is too small to read and too reminiscent of stock tickers or sale banners. Replace with a static, centered drop announcement bar:

```jsx
// Instead of scrolling ticker, do a static centered bar:
<div style={{
  height: 36,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'linear-gradient(180deg, rgba(13,13,13,0.9) 0%, transparent 100%)',
}}>
  <span style={{
    fontFamily: "'Inter', sans-serif",
    fontWeight: 500,
    fontSize: 10,
    letterSpacing: '0.25em',
    color: '#C9A84C',
    opacity: 0.6,
  }}>
    DECODED NOIR — DROPS IN 3D 14H
  </span>
</div>
```

4. **The "◈" diamond characters in the ticker.** These Unicode decorators feel like a forum signature from 2012. Use nothing, or use a tiny SVG brand mark.

5. **The skull reaction.** Fire is on-brand for streetwear. A skull is generically "edgy." Consider replacing with something more DECODED-specific (a brand icon, a chain link, a lock symbol for "vault"). Or use a simple heart — it's more universal and doesn't alienate potential customers who find skulls off-putting.

6. **The `Sparkles` component's `setInterval` at 350ms.** Beyond the visual issue, this is a performance concern — it triggers re-renders every 350ms on every active card. On lower-end phones (which IS part of the streetwear demographic), this will cause jank.

---

## Summary Scorecard

| Area | Score | Notes |
|------|-------|-------|
| Visual Hierarchy | 6/10 | Good structure, price and subtitle need more presence |
| Animation Quality | 7/10 | Glass button and Ken Burns are great; particles and sparkles hurt |
| Typography | 5/10 | Inter everywhere is the biggest miss. Need a display face for titles |
| Interaction Design | 6/10 | Vault button is excellent; missing size select, cart, and nav |
| Color Palette | 7/10 | Core palette is right; orange burst and uniform vignette need fixes |
| Completeness | 4/10 | No product images, no sizes, no nav, no cart |
| Polish | 6/10 | Some elements are very refined (glass button), others feel rushed |

**Overall: 5.9/10**

### Pitch-readiness assessment

In its current state, this demo will impress a brand owner for about 15 seconds — the video backgrounds, the snap scrolling, and the dark-gold palette will land. But within a minute, they'll start asking: "Where do I see the shirt? How do I pick a size? What happens after I vault it?" And those questions will shift the conversation from "wow, this is cool" to "this is just a mood board."

### Top 3 changes to make before the pitch

1. **Add a display typeface for product names.** This single change will shift the entire feel from "tech demo" to "luxury brand." Bebas Neue is free and would work. Monument Extended or Druk Wide would be ideal if licensing allows.

2. **Kill the sparkles and simplify the particles.** Every unnecessary animation erodes trust. The glass button and Ken Burns zoom prove you can do premium animation. Let those carry the experience.

3. **Add a product image or detail view.** Even a static PNG overlay that appears on tap would show the brand owner "we've thought about the full purchase flow, not just the scroll."

---

*Review by Opus — 2026-02-10*
