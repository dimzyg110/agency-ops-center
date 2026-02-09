# L-CAS Task Breakdown

## PHASE0-1: Fix model IDs in scoring_service ✅
**Priority:** P0
**Estimated time:** 15 minutes
**Dependencies:** None
**Files:** backend/services/scoring_service.py
**Status:** DONE (PR #1)

### Description
Replace placeholder/fake model IDs in scoring_service with the real configured model IDs. Ensure the service reads from a centralized config source if available.

### Acceptance Criteria
- [x] scoring_service uses valid model IDs (no placeholders) confirmed by config values
- [x] No references to fake/unknown model IDs remain in scoring_service.py

### Implementation Notes
4 replacements: `gpt-5.2` → `MODEL_SCORE`, `MODEL_CAPTION`, `MODEL_PROMPT_GEN` from ai_config.

## PHASE0-2: Fix model IDs in image_gen_service ✅
**Priority:** P0
**Estimated time:** 15 minutes
**Dependencies:** None
**Files:** backend/services/image_gen_service.py
**Status:** DONE (PR #1)

### Description
Replace placeholder/fake model IDs in image_gen_service with real model IDs. Align with centralized AI config once available.

### Acceptance Criteria
- [x] image_gen_service uses valid model IDs (no placeholders)
- [x] No references to fake/unknown model IDs remain in image_gen_service.py

### Implementation Notes
3 replacements: `gpt-5.2` → `MODEL_PROMPT_GEN`, `grok-4` → `MODEL_GROK`, `gemini-3-pro-image-preview` → `MODEL_IMAGE_GEMINI`.

## PHASE0-3: Fix React useEffect bug in BatchCreate.jsx ✅
**Priority:** P0
**Estimated time:** 20 minutes
**Dependencies:** None
**Files:** frontend/src/components/BatchCreate.jsx
**Status:** DONE (PR #1)

### Description
Fix the useEffect dependency/closure bug causing incorrect behavior in BatchCreate. Ensure effects run predictably and avoid stale state.

### Acceptance Criteria
- [x] useEffect dependencies satisfy React lint rules (or are explicitly justified)
- [x] Bug repro no longer occurs with updated hook logic

### Implementation Notes
Changed `useState(() => { fetchBrands()...` to proper `useEffect` with cleanup function and mounted flag.

## PHASE0-4: Move Firebase config to env vars ✅
**Priority:** P0
**Estimated time:** 25 minutes
**Dependencies:** None
**Files:** frontend/src/firebase.js, backend/config/*.py, .env.example
**Status:** DONE (PR #1)

### Description
Remove hardcoded Firebase keys from code and load configuration from environment variables. Update example env files and any config loader accordingly.

### Acceptance Criteria
- [x] Firebase keys are not hardcoded in repo files
- [x] App loads Firebase config from env vars (documented in .env.example)

### Implementation Notes
Backend storage_service.py now uses `os.getenv()` for all Firebase config. Added validation with warnings for missing keys.

## PHASE0-5: Create centralized ai_config.py ✅
**Priority:** P0
**Estimated time:** 20 minutes
**Dependencies:** None
**Files:** backend/config/ai_config.py, backend/services/*
**Status:** DONE (PR #1)

### Description
Introduce a single ai_config module that defines model IDs and AI-related settings. Update services to import from this module.

### Acceptance Criteria
- [x] ai_config.py exists and exports model IDs used by services
- [x] scoring_service and image_gen_service import model IDs from ai_config

### Implementation Notes
Created `backend/config/ai_config.py` with MODEL_SCORE, MODEL_CAPTION, MODEL_PROMPT_GEN, MODEL_GROK, MODEL_IMAGE_GEMINI, plus RESOLUTION_TIERS config.

## PHASE0-1b: Fix model IDs in openai_service.py ✅
**Priority:** P0
**Estimated time:** 10 minutes
**Dependencies:** PHASE0-5
**Files:** backend/services/openai_service.py
**Status:** DONE (PR #1)

### Description
Additional model ID fixes discovered during implementation - openai_service.py also had hardcoded `gpt-5.2` references.

### Acceptance Criteria
- [x] openai_service uses valid model IDs from ai_config
- [x] No references to fake/unknown model IDs remain

### Implementation Notes
3 replacements: all `gpt-5.2` → appropriate constants from ai_config.

---

## PHASE1-1: Add cost_events table schema ✅
**Priority:** P1
**Estimated time:** 25 minutes
**Dependencies:** PHASE0-5
**Files:** backend/db/database.py
**Status:** DONE (PR #2)

### Description
Add a cost_events table to record metered API usage. Include fields for brand_id, endpoint, units, cost_usd, created_at.

### Acceptance Criteria
- [x] Database schema includes cost_events table with required columns
- [x] Migration applies cleanly on a fresh database

### Implementation Notes
Used SQLite with auto-init on import. Table includes brand_id, endpoint, model, input_tokens, output_tokens, units, cost_usd, metadata, created_at. Indexed on brand_id and endpoint.

## PHASE1-2: Add brand_budgets table schema ✅
**Priority:** P1
**Estimated time:** 25 minutes
**Dependencies:** PHASE1-1
**Files:** backend/db/database.py
**Status:** DONE (PR #2)

### Description
Add a brand_budgets table to store monthly budget caps and current spend. Include brand_id, period_start, budget_usd, spent_usd.

### Acceptance Criteria
- [x] brand_budgets table exists with expected columns
- [x] Unique constraint prevents duplicate brand_id+period_start

### Implementation Notes
Added UNIQUE(brand_id, period_start) constraint. Includes alert_threshold for warnings.

## PHASE1-3: Create metered API wrapper ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE1-1
**Files:** backend/services/metered_api.py
**Status:** DONE (PR #2)

### Description
Create a wrapper that records usage/cost for AI API calls. It should accept brand_id, endpoint, usage units, and calculated cost.

### Acceptance Criteria
- [x] Wrapper records a cost_events row for each call
- [x] Existing AI calls can be routed through the wrapper without behavior changes

### Implementation Notes
Created metered_llm_call, metered_llm_call_async, record_image_cost, record_video_cost functions. Extracts usage from OpenAI-style responses automatically.

## PHASE1-4: Add budget enforcement logic ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE1-2, PHASE1-3
**Files:** backend/services/metered_api.py, backend/services/cost_service.py
**Status:** DONE (PR #2)

### Description
Block or warn when a brand exceeds its monthly budget. Implement a check that sums cost_events for the current period against brand_budgets.

### Acceptance Criteria
- [x] Requests for over-budget brands are denied or flagged per spec
- [x] Budget check uses current period spend from cost_events

### Implementation Notes
require_budget() raises BudgetExceededError. check_budget() returns status with allowed/alert flags. Period is first of month.

## PHASE1-5: Add resolution tier config ✅
**Priority:** P2
**Estimated time:** 20 minutes
**Dependencies:** PHASE0-5
**Files:** backend/config/ai_config.py
**Status:** DONE (PR #1 - already included)

### Description
Add resolution tiers (e.g., thumb/standard/hires) to configuration and use them in image generation calls.

### Acceptance Criteria
- [x] Config defines resolution tiers with sizes
- [x] Image generation can select tier without inline magic numbers

### Implementation Notes
RESOLUTION_TIERS dict in ai_config.py with thumb (512), mid (1024), hi (2048). DEFAULT_RESOLUTION_TIER = "thumb".

---

## PHASE2-1: Create Brand model/schema ✅
**Priority:** P1
**Estimated time:** 25 minutes
**Dependencies:** PHASE1-2
**Files:** backend/models/brand.py, backend/db/schema.sql (or migrations/*)
**Status:** DONE (PR #5)

### Description
Create a Brand model and corresponding database table. Include id, name, slug, status, created_at.

### Acceptance Criteria
- [x] Brand table exists and model maps to it
- [x] Basic CRUD instantiation works in a REPL/test

### Implementation Notes
Added unique constraint on slug. Full CRUD with soft delete.

## PHASE2-2: Create brand_repository service ✅
**Priority:** P1
**Estimated time:** 25 minutes
**Dependencies:** PHASE2-1
**Files:** backend/services/brand_repository.py
**Status:** DONE (PR #5)

### Description
Implement repository functions for Brand CRUD and lookup by slug/id. Provide a small interface used by endpoints.

### Acceptance Criteria
- [x] Repository exposes create/get/list/update methods
- [x] Methods return expected Brand objects

### Implementation Notes
Full CRUD with get_or_create utility.

## PHASE2-3: Remove hardcoded CH logic ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE2-2
**Files:** backend/services/*, frontend/src/*
**Status:** DONE (PR #5 - Phase 2 fixes)

### Description
Replace hardcoded "CH" brand logic with dynamic brand selection from the new Brand model. Ensure default brand is loaded from DB or config.

### Acceptance Criteria
- [x] No hardcoded "CH" strings remain in brand selection paths
- [x] Brand selection uses repository or API

### Implementation Notes
Cleaned up in brand_service.py during Phase 2 fixes.

## PHASE2-4: Add brand API endpoints ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE2-2
**Files:** backend/api/brands.py, backend/app.py
**Status:** DONE (PR #5)

### Description
Create REST endpoints for listing and retrieving brands. Use brand_repository for data access.

### Acceptance Criteria
- [x] GET /brands returns list of brands
- [x] GET /brands/{id} returns a brand or 404

### Implementation Notes
Full CRUD endpoints including POST, PATCH, DELETE.

## PHASE2-5: Update frontend brand selector
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE2-4
**Files:** frontend/src/components/BrandSelector.jsx, frontend/src/api/*

### Description
Add or update a brand selector UI that loads from the brand API. Store the selected brand in state and pass it to relevant flows.

### Acceptance Criteria
- [ ] Brands are fetched from API and shown in selector
- [ ] Selected brand is used in downstream actions

### Implementation Notes
Persist selection in local storage if existing pattern.

---

## PHASE3-1: Create prompt generation endpoint ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE1-3
**Files:** backend/api/prompts.py, backend/services/prompt_service.py
**Status:** DONE (PR #6)

### Description
Add an endpoint to generate prompt candidates based on inputs. Use prompt_service to encapsulate logic.

### Acceptance Criteria
- [x] POST /prompts/generate returns an array of prompt candidates
- [x] Endpoint validates required inputs

### Implementation Notes
Includes batch generation, cost tracking via metered_api.

## PHASE3-2: Add prompt scoring logic ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE3-1, PHASE0-1
**Files:** backend/services/prompt_service.py, backend/services/scoring_service.py
**Status:** DONE (PR #6)

### Description
Implement scoring of generated prompts using scoring_service. Return scores along with prompt text.

### Acceptance Criteria
- [x] Each generated prompt includes a numeric score
- [x] Scoring uses the real model IDs from ai_config

### Implementation Notes
Scores 0-100 based on clarity, creativity, brand fit, engagement. Uses metered_api for cost tracking.

## PHASE3-3: Create prompt selection UI ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE3-1
**Files:** frontend/src/components/PromptSelector.jsx, frontend/src/api/prompts.js
**Status:** DONE (PR #7)

### Description
Build a UI that displays generated prompt candidates and allows selection. Wire it to the prompt generation endpoint.

### Acceptance Criteria
- [x] UI loads prompt candidates from API
- [x] User can select a prompt and proceed

### Implementation Notes
PromptSelector.jsx with score badges, auto-selects highest score, Generate More button.

## PHASE3-4: Add thumbnail-first image generation ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE1-5
**Files:** backend/services/image_gen_service.py, frontend/src/components/ImageGen.jsx
**Status:** DONE (PR #6)

### Description
Generate a low-res thumbnail first, then allow user to pick for upscale. Add API support to request thumbnail tier.

### Acceptance Criteria
- [x] Thumbnail generation uses resolution tier config
- [x] UI shows thumbnails before any upscale

### Implementation Notes
tier parameter added to image generation. Default: thumb (512x512).

## PHASE3-5: Add approval workflow for upscales ✅
**Priority:** P1
**Estimated time:** 30 minutes
**Dependencies:** PHASE3-4
**Files:** frontend/src/components/ImageGen.jsx, backend/api/images.py
**Status:** DONE (PR #7)

### Description
Add explicit approval gate before triggering upscale. Require user confirmation and record approval in request payload.

### Acceptance Criteria
- [x] Upscale requests only happen after user approval action
- [x] Backend rejects upscale requests without approval flag

### Implementation Notes
ThumbnailGallery with confirmation modal, approved=true in payload.

---

## PHASE4-1: Brand Verification (outline)
**Priority:** P2
**Estimated time:** 20 minutes
**Dependencies:** PHASE2-4
**Files:** docs/brand_verification.md

### Description
Draft outline for brand verification flow, data model, and API changes. No code implementation in this task.

### Acceptance Criteria
- [ ] Documentation file outlines steps, required data, and endpoints
- [ ] Open questions list included

### Implementation Notes
Keep to 1-2 pages; link to relevant existing endpoints.

---

## PHASE5-1: Video Pipeline (outline)
**Priority:** P2
**Estimated time:** 20 minutes
**Dependencies:** PHASE3-5
**Files:** docs/video_pipeline.md

### Description
Draft outline for video generation pipeline and approval gates. Include key components and data flow only.

### Acceptance Criteria
- [ ] Documentation file describes stages and approval points
- [ ] Risks/cost controls noted

### Implementation Notes
Reference prompt factory and budget checks where applicable.
