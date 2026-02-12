# LP Overhaul Summary (GLASS Landing Page)

## Completed

### 1) Replaced giant feature placeholders with real preview images + graceful fallback
- Updated `apps/web/src/pages/Landing.tsx` feature cards for:
  - Price Wire → `/images/preview-pricewire.jpg`
  - Threat Radar → `/images/preview-threats.jpg`
  - Morning Brief → `/images/preview-morning.jpg`
- Added SEO/perf attributes:
  - `alt` text (descriptive)
  - `loading="lazy"`
  - styling: `rounded-2xl object-cover w-full` + subtle border
- Added intentional gradient fallback if image file is missing (using `onError` state), so no empty dark placeholder boxes appear.

### 2) Corrected inaccurate numbers and claims
- Updated feature bullet:
  - `Track 2,500+ products` → `Track 100,000+ products across 490+ dispensaries`
- Removed unsupported social-proof claim:
  - Replaced “Join 50+ Massachusetts operators…” with:
  - **“Built for Massachusetts operators. Free forever for the core dashboard.”**

### 3) SEO optimization (dynamic + base HTML)
- Added landing-page SEO tags dynamically in `Landing.tsx` `useEffect` (upsert behavior):
  - `description`
  - `keywords`
  - `og:title`, `og:description`, `og:type`, `og:url`, `og:image`
  - `twitter:card`, `twitter:title`, `twitter:description`
  - canonical link (`https://glassintel.xyz`)
- Updated `document.title` for landing page to `GLASS — Cannabis Market Intelligence`.
- Updated `apps/web/index.html` base SEO:
  - stronger description
  - canonical link

### 4) Interactive/link behavior verification + fixes
- Hero email form still uses waitlist hook with product `'glass'`:
  - `useWaitlistSignup('glass', 'landing_get_started')`
- On successful hero submit, route now goes to `/signup`.
- Confirmed CTAs/links on Landing page:
  - “Start Free” → `/signup`
  - Nav “Market Data” → `/market`
  - Ecosystem card links:
    - GLASS → `/signup`
    - Others → `/budtender`, `/cue`, `/delivery`
  - “The Operator’s Margin Report” → `/newsletter`
  - Public Market Intelligence link → `/market`
- No `alert()` or dead `#` links found in Landing page.

### 5) Copy polish + coming-soon clarity
- Added explicit “Coming Soon” badge to feature sections where status is not live:
  - Threat Radar
  - Morning Brief
- Kept tone factual and less salesy.

### 6) Performance/mobile meta updates
- Added lazy-loading to feature preview images.
- Updated viewport/mobile meta in `index.html`:
  - `width=device-width, initial-scale=1, viewport-fit=cover`
  - mobile web app capability tags
- Added font preload for Playfair stylesheet URL, while keeping preconnect links.

## Files Changed
- `/data/workspace/projects/glass/src/apps/web/src/pages/Landing.tsx`
- `/data/workspace/projects/glass/src/apps/web/index.html`

## Notes / Blockers
- Local lint/build could not be executed because dependencies/tools are missing in this environment:
  - `eslint: not found`
  - `vite: not found`
- Preview image files are not present yet in `apps/web/public/images`; fallback gradient now handles this gracefully until generated assets are added.

## Pending Runbook Commands (not executed in this session)
```bash
cd /data/workspace/projects/glass/src
git add -A
git commit -m "fix: LP overhaul — SEO meta, real numbers, placeholder images, form verification, copy polish"
git push origin main

railway service glass-web && railway up
```
