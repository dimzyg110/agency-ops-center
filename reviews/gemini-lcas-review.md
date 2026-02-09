# L-CAS Code Review

## 1. Executive Summary
**Grade: D-**

The codebase contains critical "P0" bugs that will prevent core functionality from working (non-existent model references like `gpt-5.2`, `grok-4`, `gemini-3`), severe security vulnerabilities (committed API keys), and architectural limitations (hardcoded branding). While the structure is logical and type hinting is used, the application is currently not production-ready and will likely fail immediately upon execution of AI services.

## 2. P0 Issues (Must Fix Before Production)
These issues will cause the application to crash or behave incorrectly.

*   **Non-Existent Model References**: The backend attempts to call models that do not exist (`gpt-5.2`, `grok-4`, `gemini-3-pro-image-preview`). This will result in 400/404 errors from the APIs.
*   **React State Initialization Bug**: `BatchCreate.jsx` incorrectly uses `useState` for a side effect (API call), which is an anti-pattern and can lead to race conditions or unexpected behavior.
*   **Hardcoded API Credentials**: Live Firebase API keys are hardcoded in the source code.

## 3. P1 Issues (Fix Soon)
*   **Hardcoded Brand Logic**: The `brand_service.py` is hardcoded to "Cannabis Healing" (CH). This makes the tool unusable for other clients without code changes.
*   **Logging**: Use of `print()` statements instead of a proper logging library makes debugging in production difficult.
*   **Missing Error Propagation**: Some services catch exceptions and print them, potentially hiding failures from the caller or returning fallback data without indication of failure.

## 4. P2 Issues (Nice to Have)
*   **Redundant Imports**: `image_gen_service.py` imports `base64` twice.
*   **Hardcoded Configuration**: Various timeouts and limits are hardcoded in the services.

## 5. Architecture Recommendations
*   **Multi-Brand Support**:
    *   Deprecate `CH_BRAND_PRESET` hardcoding in `brand_service.py`.
    *   Move brand configurations to a database or a configuration file (YAML/JSON) loaded at runtime.
    *   Implement a proper `Brand` model and repository.
*   **Configuration Management**:
    *   Move all API keys and environment-specific configs to `.env` (already partially done, but Firebase is missed).
    *   Use Pydantic `BaseSettings` for validation.
*   **Service Layer**:
    *   Abstract the LLM provider to a generic interface to switch between GPT-4o, Claude 3.5, etc., easily without hunting for model strings.

## 6. Specific Code Fixes

### A. Fix Model References (Backend)

**File:** `backend/services/scoring_service.py`
**Line 98, 229, 549, 646**: Change `gpt-5.2` to `gpt-4o` or `gpt-4o-mini`.

```python
# Line 98
model="gpt-4o-mini",  # Corrected from gpt-5.2

# Line 229
model="gpt-4o-mini",

# Line 549
model="gpt-4o",  # Better reasoning

# Line 646
model="gpt-4o",
```

**File:** `backend/services/image_gen_service.py`
**Line 116**: Change `gpt-5.2` to `gpt-4o`.
**Line 140**: Change `grok-4` to `grok-beta` or supported model.
**Line 239**: Change `gemini-3-pro-image-preview` to `imagen-3.0-generate-001` or valid Gemini model.

```python
# backend/services/image_gen_service.py

# Line 116
model="gpt-4o",

# Line 140
model="grok-beta", # Check xAI docs for latest

# Line 239
model='imagen-3.0-generate-001', # Or valid Google GenAI model
```

### B. Security: Remove Hardcoded Keys

**File:** `backend/services/storage_service.py`
**Lines 19-27**: Replace hardcoded dictionary with environment variables.

```python
# backend/services/storage_service.py

FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}
```

### C. Fix React Hook Usage

**File:** `frontend/src/components/BatchCreate.jsx`
**Line 19**: Replace `useState` with `useEffect` for data fetching.

```javascript
// frontend/src/components/BatchCreate.jsx

// OLD (Incorrect)
// useState(() => {
//   fetchBrands().then(setBrands).catch(console.error);
// }, []);

// NEW (Correct)
import { useEffect } from 'react'; // Add import

useEffect(() => {
  fetchBrands().then(setBrands).catch(console.error);
}, []);
```

### D. Fix Hardcoded Brand

**File:** `backend/services/brand_service.py`
**Line 132-145**: Remove the forceful override for CH brand.

```python
# backend/services/brand_service.py

# Remove or comment out:
# if is_ch_brand(name):
#     preset = CH_BRAND_PRESET.copy()
#     preset["name"] = name
#     return preset

# Instead, prefer the AI generation or DB lookup for all brands.
```
