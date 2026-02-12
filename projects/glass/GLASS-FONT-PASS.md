# GLASS Frontend Typography Reskin — Font Pass Summary

## Design Direction
Premium editorial B&W luxury typography system.

## Font Scheme Implemented

### 1. Headlines/Display
- **Primary**: Financier Display (premium Klim font — for future self-hosting)
- **Fallback**: Playfair Display (Google Fonts)
- **Final fallback**: Georgia, serif

### 2. UI/Body Text
- **Primary**: Die Grotesk (premium — for future self-hosting)
- **Fallback**: Geist (Vercel CDN)
- **Final fallback**: system-ui, -apple-system, sans-serif

### 3. Data/Labels/Nav/Mono
- **Primary**: Geist Pixel (premium — for future self-hosting)
- **Fallback**: Geist Mono (Vercel CDN)
- **Final fallback**: JetBrains Mono, monospace

## Files Modified

### 1. `/src/apps/web/index.html`
- Removed Google Fonts link for Inter, JetBrains Mono, Playfair Display
- Added Google Fonts link for Playfair Display only (headline fallback)
- Added comment explaining the font stack strategy

### 2. `/src/apps/web/tailwind.config.ts`
- Updated `fontFamily.display`: `['Financier Display', 'Playfair Display', 'Georgia', 'serif']`
- Updated `fontFamily.sans`: `['Die Grotesk', 'Geist', 'system-ui', '-apple-system', 'sans-serif']`
- Updated `fontFamily.mono`: `['Geist Pixel', 'Geist Mono', 'JetBrains Mono', 'monospace']`

### 3. `/src/apps/web/src/index.css`
- Removed Google Fonts @import for Inter, JetBrains Mono, Playfair Display
- Added @font-face declarations for Geist (weights: 400, 500, 600, 700) from Vercel CDN
- Added @font-face declarations for Geist Mono (weights: 400, 500, 600) from Vercel CDN
- Added Google Fonts @import for JetBrains Mono as additional fallback
- Updated `html` font-family rule: `'Die Grotesk', 'Geist', system-ui, -apple-system, sans-serif`
- All existing utility classes (glass-card, glass-btn, etc.) preserved unchanged

### 4. `/src/apps/web/src/components/PriceTable.tsx`
- Added `font-mono` class to price cell (`<td className="px-4 py-3 font-mono">`)
- This ensures prices display in Geist Pixel → Geist Mono → JetBrains Mono

### 5. `/src/apps/web/src/components/StatCard.tsx`
- Added `font-mono` class to stat value (`<p className="mt-2 font-mono text-3xl font-bold text-glass-text">`)
- Added `font-mono` class to trend percentage (`<span className={cn('font-mono text-sm font-medium', ...)>`)

### 6. `/src/apps/web/src/components/TopBar.tsx`
- Added `font-mono` class to unread alerts badge (`<span className="... font-mono text-xs font-medium text-white">`)

### 7. `/src/apps/web/src/components/Sidebar.tsx`
- No changes needed — `| GLΛSS |` logo already uses `font-mono` class

### 8. `/src/apps/web/src/components/MiniChart.tsx`
- No changes needed — no data text labels requiring mono font

### 9. `/src/apps/web/src/pages/Landing.tsx`
- No changes needed — already uses:
  - `font-display` for hero headline (Financier Display → Playfair Display)
  - `font-mono` for section labels via `section-marker`/`section-marker-dark` classes
  - Default `font-sans` for body text (Die Grotesk → Geist)

## Font Loading Strategy

### CDN Resources
1. **Google Fonts**: Playfair Display (headline fallback)
2. **Vercel CDN**: Geist + Geist Mono (body/mono fallbacks)
3. **Google Fonts**: JetBrains Mono (additional mono fallback)

### Premium Fonts (Future Self-Hosting)
- Financier Display (Klim Type Foundry)
- Die Grotesk (Commercial license required)
- Geist Pixel (Vercel/Commercial)

When premium fonts are self-hosted, simply add @font-face declarations before the existing ones in `index.css` — the CSS font-family stacks are already configured to use them first.

## Verification Checklist

- [x] `index.html` — Google Fonts link updated to Playfair Display only
- [x] `tailwind.config.ts` — fontFamily stacks updated with premium + fallback fonts
- [x] `index.css` — @font-face declarations for Geist/Geist Mono from Vercel CDN
- [x] `index.css` — html font-family rule updated
- [x] `PriceTable.tsx` — price cells use `font-mono`
- [x] `StatCard.tsx` — stat values and trends use `font-mono`
- [x] `TopBar.tsx` — alert badge uses `font-mono`
- [x] `Sidebar.tsx` — logo already uses `font-mono` (no change)
- [x] `Landing.tsx` — hero uses `font-display`, labels use `font-mono`

## No Changes Required

- Colors — preserved existing B&W luxury palette
- Layout — all spacing and positioning unchanged
- Component logic — no functional changes
- CSS utility classes — glass-card, glass-btn, etc. preserved

## Result

The GLASS frontend now uses a premium editorial typography system:
- **Display/Headlines**: Financier Display → Playfair Display (elegant serif)
- **Body/UI**: Die Grotesk → Geist (clean, modern sans-serif)
- **Data/Mono**: Geist Pixel → Geist Mono (technical, precise monospace)

All numeric data (prices, percentages, stats, alert counts) now render in monospace for improved readability and a technical/editorial aesthetic.
