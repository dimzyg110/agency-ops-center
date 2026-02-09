# Phase 0 Model ID Fixes Review

## Summary
- Reviewed `backend/services/scoring_service.py` and `backend/services/image_gen_service.py` for model constant imports and replacements.
- Grepped repo for remaining fake model IDs.
- Python syntax appears valid in both files.

## Findings
### ✅ scoring_service.py
- Imports `MODEL_SCORE`, `MODEL_CAPTION`, `MODEL_PROMPT_GEN` from `config.ai_config` ✅
- Uses constants for model selection ✅
- No literal `gpt-5.2` strings found in this file ✅

### ✅ image_gen_service.py
- Imports `MODEL_PROMPT_GEN`, `MODEL_GROK`, `MODEL_IMAGE_GEMINI` from `config.ai_config` ✅
- Model usage switched to constants (`MODEL_PROMPT_GEN`, `MODEL_GROK`, `MODEL_IMAGE_GEMINI`) ✅

### ❗ Remaining fake model IDs in repo
`grep -R "gpt-5.2|grok-4|gemini-3" -n /tmp/social-tool` returns:
- `backend/services/openai_service.py:305` → `model="gpt-5.2"`
- `backend/services/openai_service.py:381` → `model="gpt-5.2"`
- `backend/services/openai_service.py:824` → `model="gpt-5.2"`

These should be replaced with constants if Phase 0 requires eliminating fake IDs repo-wide.

### ⚠️ Minor (strings only)
- `image_gen_service.py` contains user-facing log/docstring text mentioning “GPT-5.2” (uppercase). Not a model ID used in API calls, but could be updated for consistency if desired.

## Status
Phase 0 **not fully complete** until remaining `gpt-5.2` usages in `openai_service.py` are addressed.

If those are out-of-scope, the two target files are fixed and syntax-valid, and Phase 0 could proceed once confirmed.