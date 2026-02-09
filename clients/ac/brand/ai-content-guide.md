# AC Brand Guide for AI Content Generation

**Created:** 2026-01-07
**Purpose:** Guide for generating branded content with Nano Banana Pro, Kling, and other AI tools

---

## Logo Description (For AI Prompts)

The AC logo is a **circular metallic badge** with these elements:

### Visual Elements
- **Shape:** Circular badge/emblem, 3D metallic finish
- **Center:** Aztec/Mayan crossed axes with lotus flower and golden shield
- **Border:** Greek key (meander) pattern in blue-grey
- **Text:** "Advanced Cultivators" (top), "Est. 2020" (bottom)
- **Style:** Heritage craft meets premium luxury, Aztec warrior aesthetic

### Color Palette
| Color | Hex | Usage |
|-------|-----|-------|
| Gold | #C9A227 | Accents, shield, text highlights |
| Silver/Chrome | #C0C0C0 | Metallic elements, axes |
| Black | #1A1A1A | Background, text |
| Blue-Grey | #4A5568 | Border pattern |
| White | #FFFFFF | Clean backgrounds |

### Brand Voice Keywords
- Premium craft cannabis
- Mexican/Aztec heritage
- Tactical precision
- Controlled power (not aggressive)
- Luxury apothecary

---

## Nano Banana Pro Prompting Guide

### For Product Photography

**Base Template:**
```
[Product description], featuring Advanced Cultivators circular emblem badge with Aztec crossed axes design and Greek key border, gold and silver metallic accents, [lighting], [background], premium cannabis brand aesthetic, no competitor branding
```

**Example - Bullet Chamber:**
```
Top-down view of clear glass tube containing 7 cannabis prerolls in revolver chamber pattern, small Advanced Cultivators circular metallic badge emblem visible on cork stopper, Aztec heritage design with gold accents, dramatic gold spotlight, pure black background, luxury product photography
```

### For Lifestyle Content
```
[Scene description], subtle Advanced Cultivators branding visible, gold and black color scheme, premium craft cannabis aesthetic, Mexican heritage influences, sophisticated lighting
```

### For Motion Graphics (Kling/Veo)
```
[Motion description], Advanced Cultivators circular badge rotating slowly, metallic gold reflections, Greek key pattern border detail, premium brand reveal, black background with gold accent lighting
```

---

## Reference Images

### Logo File Locations
- Full logo: `clients/ac/brand/ac-logo-full.png`
- Icon only: `clients/ac/brand/ac-icon.png` (to be added)
- Wordmark: `clients/ac/brand/ac-wordmark.png` (to be added)

### Raw Product Photos
- Bullet chamber: `clients/ac/content/raw/bullet-raw/`
  - `top.jpeg` - Top-down chamber view (7 prerolls)
  - `angled.jpeg` - Angled view, cap off
  - `angled-with-cap.jpeg` - Sealed product
  - `side.jpeg` - Side profile, sealed
  - `side-1.jpeg` - Side profile, open

---

## Generated Content Archive

### Session: 11d6642a (2026-01-07) - BRANDED
**Type:** Bullet Chamber with AC Branding
**Model:** Nano Banana Pro (gemini-3-pro-image-preview)
**Location:** `clients/ac/content/generated/bullet-chamber-branded-2026-01-07/`

| File | Style | Notes |
|------|-------|-------|
| `6f8b69fa.png` | Product Hero | **BEST** - Glass tube, 7 prerolls, crossed axes badge on cork |
| `89542113.png` | Lifestyle Luxury | Ornate metallic case, revolver motif, Greek key wallpaper |
| `4c4a901f.png` | Abstract Close-up | "ADVANCED CULTIVATORS" text, silk backdrop, Versace vibes |
| `e712c716.png` | Minimalist | Matte black tube, gold leaf badge, dramatic lighting |

**Key Prompt Elements That Worked:**
- "embossed Advanced Cultivators circular metallic badge"
- "Aztec crossed axes design"
- "Greek key meander border pattern"
- "gold and silver metallic finish"
- "Sony A7III 85mm lens f/1.8" (camera spec for realism)
- "hyperrealistic luxury product photography"

---

### Session: 11e0d5fe (2026-01-07) - UNBRANDED
**Type:** Bullet Chamber Mockups (no branding)
**Model:** Nano Banana Pro (gemini-3-pro-image-preview)
**Location:** `clients/ac/content/generated/bullet-chamber-2026-01-07/`

| File | Style | Notes |
|------|-------|-------|
| `15c398fd.png` | Top-down, 7 radial | Good composition |
| `795be8f8.png` | Angled tube, 7 chamber | Best match to real product |
| `f1703627.png` | Top-down, 8 radial | Wrong count, has text |
| `0b607461.png` | Side angle, 7 in tube | Very realistic |

**Prompts Used:**
- Topic: "top-down view of clear glass tube containing 7 white cannabis prerolls arranged in circular revolver chamber pattern..."
- Brand profile: AC, premium tactical craft, black/gold/glass

---

## Best Practices

### Do's
- Always specify "no competitor branding, no text" unless you want AC branding
- Use "Advanced Cultivators circular badge" or "AC emblem" for brand placement
- Reference Aztec/Mayan heritage for cultural elements
- Use gold accent lighting on black backgrounds
- Specify exact preroll count (7 for bullet chamber)

### Don'ts
- Don't use generic cannabis imagery (leaves, smoke)
- Don't use competitor brand names (RAW, Cookies, etc.)
- Don't generate consumption imagery
- Don't use "marijuana" or "weed" in prompts
- Don't include prices or purchase CTAs

### Platform-Safe Copy
**Approved terms:** cannabis, prerolls, craft, premium, flower, cultivator
**Avoid:** weed, marijuana, pot, 420, stoner, high, smoke

---

## Integration Methods

### Method 1: Post-Processing (Most Reliable)
1. Generate clean product images without branding
2. Add AC logo overlay in Photoshop/Figma
3. Ensures consistent brand placement

### Method 2: Reference Image
1. Upload AC logo as reference to Nano Banana Pro
2. Use prompt: "incorporating the reference logo design"
3. Works for stylistic influence, less reliable for exact reproduction

### Method 3: Text Description
1. Describe logo elements in prompt
2. "...with circular metallic badge featuring Aztec crossed axes..."
3. Best for mood/style, not exact logo

---

## API Endpoints (Media Tool)

### Image Generation
```bash
POST /api/atlas/imagegen/prompts
{
  "topic": "...",
  "count": 4,
  "brand_profile": {
    "name": "Advanced Cultivators",
    "voice": "premium craft cannabis",
    "colors": "black, gold, glass",
    "style": "Aztec heritage meets luxury apothecary"
  }
}
```

### Video Generation (Kling via Fal.ai)
```bash
POST /api/atlas/videogen/generate
{
  "image_url": "...",
  "prompt": "slow rotation revealing product details...",
  "duration": "5",
  "model": "2.1-standard"
}
```

---

## Pricing Reference

### Nano Banana Pro (Gemini 3 Pro Image Preview)
- ~$0.03-0.13 per image (standard)
- ~$0.24 per 4K image

### Kling via Fal.ai
- 2.1-standard: $0.25/5s, $0.50/10s (budget)
- 2.6-pro: $0.45/5s, $0.90/10s (quality)

---

*Last updated: 2026-01-07*
