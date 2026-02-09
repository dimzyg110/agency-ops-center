# L-CAS Code Review – Roviq Multi‑Client Platform

## 1. Executive Summary (Grade: **D**)
Core ideas are promising, but there are **production‑blocking P0s** (non‑existent model IDs, hardcoded Firebase keys, and a React hook bug that prevents brand loading). The codebase is also **single‑brand hardcoded** in multiple places and lacks consistent error handling and configuration boundaries needed for multi‑client scale.

---

## 2. P0 Issues (must fix before production)

### P0‑1: **Non‑existent model references** (runtime failures)
- **File:** `backend/services/scoring_service.py`
  - **Lines 105–107:** `model="gpt-5.2"` (does not exist)
  - **Lines 303–305:** `model="gpt-5.2"` (does not exist)
  - **Lines 421–423:** `model="gpt-5.2"` (does not exist)
- **File:** `backend/services/image_gen_service.py`
  - **Lines 101–104 / 131–133:** GPT prompt generation uses `model="gpt-5.2"` (non‑existent)
  - **Lines 156–168:** Grok uses `model="grok-4"` (non‑existent)
  - **Lines 271–275 (in `generate_image`, beyond snippet):** uses Gemini image model `gemini-3-pro-image-preview` (non‑existent)

**Impact:** immediate API failures in scoring, prompt generation, caption enhancement, and image generation. This is a hard stop for production.

---

### P0‑2: **React hook bug prevents brand loading**
- **File:** `frontend/src/components/BatchCreate.jsx`
  - **Lines 19–22:** `useState(() => { fetchBrands()... }, [])` is incorrect. Side‑effects must use **useEffect**, not useState.

**Impact:** `fetchBrands()` never runs or runs unpredictably. UI brand dropdown empty → no batch can be created.

---

### P0‑3: **Hardcoded Firebase keys and project identifiers**
- **File:** `backend/services/storage_service.py`
  - **Lines 21–29:** `FIREBASE_CONFIG` contains live API key + project IDs.

**Impact:** security exposure, no environment isolation, no safe multi‑tenant deployment; risk of key misuse and accidental data exposure.

---

## 3. P1 Issues (fix soon)

### P1‑1: **Hardcoded Cannabis Healing (CH) logic blocks multi‑brand scaling**
- **File:** `backend/services/brand_service.py`
  - **Lines 19–141:** `CH_BRAND_PRESET` hardcoded as global canonical preset.
  - **Lines 144–163:** `is_ch_brand()` + `generate_brand_preset()` hardcode brand detection + forced CH return.

**Impact:** This is effectively a **single‑client product**. Multi‑client onboarding requires database‑driven presets with per‑brand compliance rules, not heuristics.

---

### P1‑2: **OpenAI client created at import time**
- **File:** `backend/services/scoring_service.py` (line 19)
- **File:** `backend/services/brand_service.py` (line 14)

**Impact:** Import‑time initialization makes testing/worker restarts brittle and ignores per‑request API keys or tenant contexts. Also crashes startup if env not present.

---

### P1‑3: **Weak error handling for third‑party model JSON**
- **File:** `backend/services/scoring_service.py`
  - **Lines 116–123:** naive JSON extraction; no schema validation, no fallback for malformed partial arrays.
- **File:** `backend/services/image_gen_service.py`
  - **Lines 177–187:** JSON extraction via regex; no strict validation of prompt object shape.

**Impact:** malformed model responses may crash or silently degrade, causing unpredictable scheduling/scoring behavior.

---

## 4. P2 Issues (nice to have)

- **Backend main.py health endpoint** only checks OpenAI/Pexels (lines 85–92). Missing Gemini/Fal/XAI checks → incomplete status reporting.
- **Batch upload UX**: progress is just “files uploaded”, not actual file‑level progress (no streaming / per‑file callback).
- **Type safety**: many dicts are untyped and silently default; consider Pydantic models to enforce schema integrity.

---

## 5. Architecture Recommendations (multi‑brand support)

1. **Move brand presets to a data store** (DB or config service). No hardcoded CH in Python module.
2. **Introduce a Brand Registry layer**:
   - `Brand` model: `id, name, compliance_rules, tone, accounts, content_types, assets`
   - Lookup by `brand_id` from requests, not by fuzzy name match.
3. **Tenant‑scoped configuration**:
   - Each brand has a `config.json` or DB record; load at runtime with caching.
4. **Feature flags per brand**:
   - Some brands may allow image generation or GPT scoring; others may not.
5. **Centralized AI provider router**:
   - Single module for model names, fallbacks, and policy to avoid hardcoded model strings scattered across files.

---

## 6. Specific Code Fixes (Before / After)

### Fix 1 — Replace invalid model IDs & centralize config
**Before** (`scoring_service.py` line 105):
```python
response = client.chat.completions.create(
    model="gpt-5.2",
    ...
)
```

**After** (example with env‑driven defaults):
```python
MODEL_SCORE = os.getenv("MODEL_SCORE", "gpt-4o-mini")
response = client.chat.completions.create(
    model=MODEL_SCORE,
    ...
)
```

**Also update** image generation:
```python
# image_gen_service.py
MODEL_PROMPTS = os.getenv("MODEL_PROMPTS", "gpt-4o-mini")
MODEL_GROK = os.getenv("MODEL_GROK", "grok-beta")  # if actually supported
MODEL_IMAGE = os.getenv("MODEL_IMAGE", "gemini-2.0-flash-image")
```

---

### Fix 2 — React useEffect for side‑effects
**Before** (`BatchCreate.jsx` lines 19–22):
```jsx
useState(() => {
  fetchBrands().then(setBrands).catch(console.error);
}, []);
```

**After**:
```jsx
import { useState, useEffect, useCallback, useRef } from 'react';

useEffect(() => {
  let mounted = true;
  fetchBrands()
    .then((data) => { if (mounted) setBrands(data); })
    .catch(console.error);
  return () => { mounted = false; };
}, []);
```

---

### Fix 3 — Move Firebase config to env
**Before** (`storage_service.py` lines 21–33):
```python
FIREBASE_CONFIG = {
  "apiKey": "AIza...",
  "projectId": "social-fa0fa",
  ...
}
```

**After**:
```python
FIREBASE_CONFIG = {
  "apiKey": os.getenv("FIREBASE_API_KEY", ""),
  "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
  "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
  "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
  "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
  "appId": os.getenv("FIREBASE_APP_ID", ""),
  "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", ""),
}
```

---

### Fix 4 — Remove hardcoded CH branch
**Before** (`brand_service.py` lines 144–163):
```python
if is_ch_brand(name):
    preset = CH_BRAND_PRESET.copy()
    preset["name"] = name
    return preset
```

**After** (outline):
```python
preset = brand_repo.get_by_name(name)
if preset:
    return preset
return generate_brand_preset_via_ai(...)
```

---

## Final Note
The platform **cannot ship** until model IDs and secret management are fixed. The single‑brand design also blocks the stated multi‑client goal. After P0 fixes, prioritize brand registry + AI provider router to remove hardcoded assumptions and enable true multi‑tenant scaling.
