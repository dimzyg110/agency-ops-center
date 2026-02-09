# AC Prompt Library - Modular Components

**Purpose:** Pick, combine, and customize prompts for Nano Banana Pro generation
**CRITICAL:** Always upload AC logo as reference image - text descriptions alone won't work

---

## How To Use

1. Pick a **BASE** (product/scene type)
2. Add **BRANDING** component (requires logo upload)
3. Add **LIGHTING**
4. Add **BACKGROUND**
5. Add **CAMERA/QUALITY** specs
6. Combine into final prompt

---

## BASES (Pick One)

### Bullet Chamber Product Shots

```
BC-01: Top-down view of clear glass tube containing 7 cannabis prerolls arranged in circular revolver chamber pattern, 6 around the edge with 1 in center, cork stopper removed and placed beside tube
```

```
BC-02: Angled hero shot of glass tube with cork stopper, 7 prerolls visible through clear glass in revolver chamber arrangement, tube lying at 30-degree angle
```

```
BC-03: Straight-on side view of glass tube standing upright, 7 prerolls visible through glass, natural cork stopper on top
```

```
BC-04: Close-up of cork stopper being removed from glass tube, fingers gripping cork, prerolls visible inside
```

```
BC-05: Single preroll being drawn from glass tube chamber, 6 remaining prerolls visible, extraction moment
```

```
BC-06: Glass tube with cork removed, top-down into the chamber showing preroll arrangement like looking into a revolver cylinder
```

### Packaging/Display Shots

```
PK-01: Glass tube centered on display pedestal, museum-style presentation
```

```
PK-02: Glass tube nestled in custom foam insert inside matte black rigid box
```

```
PK-03: Multiple glass tubes arranged in grid pattern, wholesale display
```

```
PK-04: Glass tube with tissue paper and branded ribbon, unboxing moment
```

### Lifestyle/Context Shots

```
LS-01: Glass tube on polished black marble surface, luxury interior setting
```

```
LS-02: Glass tube on raw concrete surface, industrial minimalist
```

```
LS-03: Glass tube on weathered wood surface, craft/heritage feel
```

```
LS-04: Glass tube on brushed stainless steel surface, modern precision
```

---

## BRANDING (REQUIRED - Must Upload Logo)

**CRITICAL: These only work if AC logo PNG is uploaded as reference image**

### Logo Placement Options

```
BR-01: [UPLOAD LOGO] Circular metallic badge from reference image embossed on cork stopper top, maintaining exact design with Aztec crossed axes and Greek key border
```

```
BR-02: [UPLOAD LOGO] Brand emblem from reference image as subtle laser-etched mark on glass tube near base
```

```
BR-03: [UPLOAD LOGO] Metallic badge from reference image on black label wrapped around tube center
```

```
BR-04: [UPLOAD LOGO] Brand logo from reference appearing on small hang tag attached to cork with black ribbon
```

```
BR-05: [UPLOAD LOGO] Logo from reference image appearing on background surface as subtle watermark/impression
```

### Without Logo Upload (Fallback - Less Accurate)

```
BR-TEXT-01: Embossed circular metallic badge featuring crossed Aztec axes, lotus flower center with golden shield, Greek key meander border pattern, "Advanced Cultivators" text curved at top, "Est. 2020" at bottom, gold and silver metallic finish
```

---

## LIGHTING (Pick One)

### Dramatic/Hero

```
LT-01: Single dramatic overhead spotlight creating circular pool of light, deep shadows, high contrast
```

```
LT-02: Golden hour warm side lighting from left, long shadows, warm color temperature
```

```
LT-03: Dual rim lighting from behind, edge glow effect, product silhouette emphasis
```

```
LT-04: Hard flash photography, harsh direct light, strong reflections on glass
```

### Soft/Luxe

```
LT-05: Soft diffused studio lighting, minimal shadows, even illumination
```

```
LT-06: Soft golden accent lighting, warm tones, subtle highlights on glass surfaces
```

```
LT-07: Natural window light from side, soft shadows, lifestyle feel
```

### Moody/Editorial

```
LT-08: Low-key lighting, mostly shadows with selective highlights on product
```

```
LT-09: Colored gel lighting, gold and blue tones, editorial fashion aesthetic
```

```
LT-10: Backlit with light flares, ethereal glow around edges
```

---

## BACKGROUNDS (Pick One)

### Solid/Clean

```
BG-01: Pure matte black background, no texture, infinite black
```

```
BG-02: Deep charcoal grey seamless background
```

```
BG-03: Clean white background, high-key product photography
```

```
BG-04: Gradient from black to dark gold, subtle transition
```

### Textured

```
BG-05: Black velvet surface, subtle texture visible
```

```
BG-06: Polished black marble with subtle grey veining
```

```
BG-07: Brushed stainless steel surface, industrial
```

```
BG-08: Raw concrete, minimalist industrial
```

```
BG-09: Weathered dark wood, heritage craft feel
```

### Themed

```
BG-10: Greek key pattern visible in background, brand heritage
```

```
BG-11: Aztec/Mayan geometric pattern, subtle in background
```

```
BG-12: Gold foil accents scattered in background, luxury
```

---

## CAMERA/QUALITY (Pick One)

### High-End Photo Specs

```
CAM-01: Sony A7III 85mm f/1.8, shallow depth of field, professional product photography
```

```
CAM-02: Hasselblad medium format, extremely sharp detail, commercial quality
```

```
CAM-03: Canon 5D Mark IV 100mm macro, extreme close-up detail, sharp focus
```

```
CAM-04: Phase One IQ4, ultra high resolution, advertising quality
```

### Style Specs

```
CAM-05: Hyperrealistic, 8K detail, photorealistic rendering
```

```
CAM-06: Editorial fashion photography style, high contrast, dramatic
```

```
CAM-07: Luxury watch advertisement aesthetic, precision and elegance
```

```
CAM-08: Premium spirits bottle photography style, glass reflections, sophistication
```

### Quality Modifiers

```
Q-01: Contact shadows on surface, realistic grounding
```

```
Q-02: Subtle vignette at edges, focus on center
```

```
Q-03: Realistic glass reflections and refractions
```

```
Q-04: Fine detail on cork texture visible
```

```
Q-05: No text, no watermarks, no artifacts
```

---

## EXAMPLE COMBINATIONS

### Hero Product Shot
```
BC-01 + BR-01 + LT-01 + BG-01 + CAM-01 + Q-01 + Q-05

"Top-down view of clear glass tube containing 7 cannabis prerolls arranged in circular revolver chamber pattern, 6 around the edge with 1 in center, cork stopper removed and placed beside tube. [UPLOAD LOGO] Circular metallic badge from reference image embossed on cork stopper top, maintaining exact design with Aztec crossed axes and Greek key border. Single dramatic overhead spotlight creating circular pool of light, deep shadows, high contrast. Pure matte black background, no texture, infinite black. Sony A7III 85mm f/1.8, shallow depth of field, professional product photography. Contact shadows on surface, realistic grounding. No text, no watermarks, no artifacts."
```

### Lifestyle Luxury
```
BC-02 + BR-01 + LT-06 + BG-06 + CAM-07 + Q-03

"Angled hero shot of glass tube with cork stopper, 7 prerolls visible through clear glass in revolver chamber arrangement, tube lying at 30-degree angle. [UPLOAD LOGO] Circular metallic badge from reference image embossed on cork stopper top. Soft golden accent lighting, warm tones, subtle highlights on glass surfaces. Polished black marble with subtle grey veining. Luxury watch advertisement aesthetic, precision and elegance. Realistic glass reflections and refractions."
```

### Editorial Close-up
```
BC-04 + BR-01 + LT-09 + BG-05 + CAM-06

"Close-up of cork stopper being removed from glass tube, fingers gripping cork, prerolls visible inside. [UPLOAD LOGO] Metallic badge from reference image on cork top. Colored gel lighting, gold and blue tones, editorial fashion aesthetic. Black velvet surface, subtle texture visible. Editorial fashion photography style, high contrast, dramatic."
```

### Minimalist Product
```
BC-03 + BR-02 + LT-05 + BG-01 + CAM-05 + Q-05

"Straight-on side view of glass tube standing upright, 7 prerolls visible through glass, natural cork stopper on top. [UPLOAD LOGO] Brand emblem from reference image as subtle laser-etched mark on glass tube near base. Soft diffused studio lighting, minimal shadows, even illumination. Pure matte black background. Hyperrealistic, 8K detail, photorealistic rendering. No text, no watermarks, no artifacts."
```

---

## NEGATIVE PROMPTS (Always Include)

```
NEGATIVE: blurry, low quality, distorted, watermark, text overlay, logo text, brand names, competitor branding, RAW branding, Cookies branding, hands unless specified, faces, smoke, fire, consumption, cartoon, illustration, 3D render look, plastic looking, cheap looking
```

---

## WORKFLOW CHECKLIST

Before generating:
- [ ] AC logo PNG file ready for upload
- [ ] Base prompt selected
- [ ] Branding component selected (BR-01 through BR-05)
- [ ] Lighting selected
- [ ] Background selected
- [ ] Camera/quality specs selected
- [ ] Negative prompt included
- [ ] Reference image upload confirmed in API call

---

## API CALL TEMPLATE

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)

# CRITICAL: Load logo as reference
logo_image = types.Part.from_image(
    types.Image.from_file("/path/to/ac-logo.png")
)

# Combined prompt from library
prompt = """
[Your combined prompt here]

IMPORTANT: Use the brand logo from the uploaded reference image exactly as shown.
Maintain the circular badge shape, Aztec crossed axes, Greek key border, and metallic finish.
Do not alter the logo design. Seamless integration with product.
"""

response = client.models.generate_content(
    model='gemini-3-pro-image-preview',
    contents=[logo_image, prompt],
)
```

---

## NOTES

1. **Logo upload is NON-NEGOTIABLE** - Text descriptions will never match the actual logo
2. **Test one combination at a time** - Don't batch until you have a winning formula
3. **Save what works** - Document exact prompts that produce good results
4. **Be critical** - If it doesn't look like the real product with real branding, it's useless
5. **Iterate** - First gen is rarely final, refine and regenerate
