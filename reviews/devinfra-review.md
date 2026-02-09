# Dev Infra Review — /tmp/social-tool

## Summary
Reviewed backend/ frontend test setup, CI workflow, and PR templates. Everything exists and is largely consistent. CI should run both suites successfully with current files.

## File Check
- ✅ `backend/tests/conftest.py` — fixtures for env + FastAPI TestClient; path injection ok.
- ✅ `backend/tests/test_ai_config.py` — basic config import/asserts.
- ✅ `backend/tests/test_health.py` — health endpoint smoke test.
- ✅ `backend/requirements.txt` — pytest deps added.
- ✅ `frontend/vitest.config.js` — jsdom + setup file.
- ✅ `frontend/src/test/setup.js` — jest-dom setup.
- ✅ `frontend/src/__tests__/App.test.jsx` — smoke test.
- ✅ `frontend/package.json` — test scripts + deps.
- ✅ `.github/workflows/ci.yml` — backend + frontend jobs.
- ✅ `.github/PULL_REQUEST_TEMPLATE.md` — present.
- ✅ `CONTRIBUTING.md` — present.

## CI Workflow Compatibility
- Backend job installs requirements and runs `pytest` with required env vars set; should pass.
- Frontend job uses Node 20 + `npm ci`, runs lint and vitest; `package-lock.json` present, so `npm ci` will work.

## Issues / Missing Pieces
1. **Duplicate dependency**: `httpx` appears twice in `backend/requirements.txt` with different minimums (`>=0.26.0` and `>=0.24.0`). This is harmless but noisy; recommend keeping one entry (prefer the higher minimum) to avoid confusion.
2. **Minor test assertion** (optional): `App.test.jsx` currently asserts `document.body` exists, which will always be true in jsdom even if the component fails to render. Consider asserting a known element/text from `App` for a more meaningful smoke test.

## Ready to Commit?
✅ Yes. No blocking issues. Recommend minor cleanup of duplicated `httpx` entry and optional test improvement, but CI should pass as-is.
