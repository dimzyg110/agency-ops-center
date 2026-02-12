# GLASS UX Revision — Randy's Direction

_Revisions to Kimi's UX Audit (GLASS-UX-AUDIT.md) based on Randy's feedback._

---

## Changes from Original Plan

### 1. Color Palette — Black & White Luxury
**Kill:** Electric teal `#00F0C8`, all neon accents
**New palette:**
```
--glass-bg:        #000000     /* Pure black backgrounds */
--glass-surface:   #0A0A0A     /* Cards, panels */
--glass-border:    #1A1A1A     /* Subtle borders */
--glass-muted:     #666666     /* Secondary text */
--glass-text:      #FFFFFF     /* Primary text */
--glass-accent:    #FFFFFF     /* CTAs and highlights — white on black */
--glass-subtle:    #F5F5F5     /* Inverted sections (white bg, black text) */
```
Fits the "GLASS" name — transparent, clean, luxury. Think: high-end watch brand, not fintech dashboard.

### 2. Remove "Connect Your Menu" 
- **Delete** the Dutchie/Weedmaps menu connection from onboarding flow
- We scrape menus ourselves — operators don't need to connect anything
- Onboarding becomes: Sign up → Select your dispensary → See your data
- Simpler, faster, no false promises

### 3. Add Cue (Virtual Budtender)
- **New section** on landing page below GLASS features
- Short description: "Cue — your AI budtender. Recommends the right product to every customer based on real-time inventory, pricing, and preference data."
- **Signup form** — email + dispensary name, "Get early access"
- No full LP yet — just enough to capture interest
- Cue is positioned as a tool POWERED BY GLASS data

### 4. Ecosystem Pathway
GLASS landing page should make clear this is the foundation:
- **GLASS** → Market intelligence (live now)
- **Cue** → Virtual budtender (coming soon)  
- **Delivered** → Cannabis delivery app (coming soon)
- Show these as a connected ecosystem, not separate products
- Honest labels: "Live" vs "Coming Soon"

### 5. Don't Oversell
- Remove any features we can't deliver today
- Price Wire, Threat Radar = live (backed by real scraper data)
- Newsletter, Margin Reports = coming soon
- No fake dashboards or mockup data presented as real

### 6. Match Roviq Design Language
From roviqai.xyz:
- **Fonts**: Inter (body) + JetBrains Mono (code/data) + Playfair Display (headlines)
- **Layout**: Editorial, generous whitespace, left-aligned
- **Vibe**: Premium, understated, not flashy
- Black & white primary, minimal color accents
- Schema.org structured data, clean SEO

---

## What Stays from Kimi's Plan
- ✅ "GLΛSS" wordmark with lambda
- ✅ 60-second time-to-value goal
- ✅ Dark mode as brand identity (now pure black, not teal-tinted)
- ✅ Landing page → signup → dashboard flow
- ✅ Morning Brief email concept
- ✅ Data density philosophy ("operators want info, not whitespace")
- ✅ Mobile: monitoring. Desktop: action.
- ✅ Performance target: <2s load

## What Changes
- ❌ Electric teal accent → white/black only
- ❌ "Connect your menu" onboarding step → removed
- ❌ Teal gradient backgrounds → pure black
- ➕ Cue virtual budtender section + signup
- ➕ Ecosystem pathway (GLASS → Cue → Delivered)
- ➕ Honest "Live" vs "Coming Soon" labels
- ➕ Match Roviq site typography (Inter/JetBrains/Playfair)
