# Dev Infrastructure Plan — social-tool

Scope: Create actionable tasks for CI, testing, PR workflow, and branch protection. Follow this plan to implement dev infra in /tmp/social-tool.

---

## 1) GitHub Actions CI Pipeline
- **Priority:** P0
- **Estimated time:** 1.5–3 hours
- **Dependencies:** None (but requires basic test setup tasks #2/#3 to fully pass)
- **Files to create/modify:**
  - `.github/workflows/ci.yml` (new)
- **Acceptance criteria:**
  - CI runs on **push** to `master` and **pull_request** to `master`.
  - Jobs include:
    - Python lint (backend)
    - JS lint (frontend)
    - Backend tests (pytest)
    - Frontend tests (vitest)
  - CI passes on a clean repo after test setup is implemented.
- **Implementation notes:**
  - Use separate jobs or a matrix; ensure working directories are correct.
  - Cache dependencies (pip + npm) if feasible.
  - Example job structure (adjust for repo scripts):
    - `backend` job:
      - `python -m pip install -r backend/requirements.txt`
      - `python -m pip install -r backend/dev-requirements.txt` (or add pytest deps to requirements)
      - `python -m flake8 backend` or `ruff` (match existing lint config)
      - `pytest backend/tests`
    - `frontend` job:
      - `npm ci` in `frontend/`
      - `npm run lint`
      - `npm run test`
  - If no lint tool is configured for backend, add a minimal one (e.g., `ruff` or `flake8`) and document in task #2.

---

## 2) Backend Test Setup (FastAPI)
- **Priority:** P0
- **Estimated time:** 2–4 hours
- **Dependencies:** None
- **Files to create/modify:**
  - `backend/tests/` (new dir)
  - `backend/tests/conftest.py` (new)
  - `backend/tests/test_ai_config.py` (new)
  - `backend/tests/test_health.py` (new)
  - `backend/requirements.txt` or `backend/dev-requirements.txt` (add pytest deps)
- **Acceptance criteria:**
  - `pytest` runs successfully locally.
  - `pytest-asyncio` installed and configured if needed.
  - Tests include:
    - Import test for `ai_config` (e.g., module imports without errors)
    - API health endpoint test (FastAPI TestClient)
  - Mocks/fixtures for OpenAI + Firebase are available and used.
- **Implementation notes:**
  - Suggested deps:
    - `pytest`, `pytest-asyncio`, `httpx`, `pytest-mock` (optional)
  - `conftest.py`:
    - Provide `app` fixture (FastAPI app instance)
    - Provide `client` fixture (TestClient)
    - Provide mock fixtures for OpenAI/Firebase (e.g., monkeypatch env vars or stub functions)
  - `test_ai_config.py`:
    - Simple import test: `import backend.ai_config` (adjust path)
  - `test_health.py`:
    - Use TestClient to call `/health` (or actual health endpoint) and assert 200 + expected JSON
  - If health route is missing, add minimal endpoint as part of a code change or adjust test to existing endpoint.

---

## 3) Frontend Test Setup (React)
- **Priority:** P0
- **Estimated time:** 2–4 hours
- **Dependencies:** None
- **Files to create/modify:**
  - `frontend/src/__tests__/` (new dir)
  - `frontend/src/__tests__/App.test.tsx` (new)
  - `frontend/src/__tests__/BrandSelector.test.tsx` (new)
  - `frontend/package.json` (add test script + vitest deps)
  - `frontend/vitest.config.ts` (new) or update existing config
- **Acceptance criteria:**
  - `npm run test` executes and passes.
  - Vitest + React Testing Library installed and configured.
  - Minimum tests:
    - Component renders (e.g., App)
    - Brand selector component test (render + expected option)
- **Implementation notes:**
  - Suggested deps:
    - `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`
  - Add `test` script in package.json:
    - `vitest run` (CI) and optionally `vitest` (watch)
  - Configure `test.environment = "jsdom"` in vitest config.
  - If TypeScript, include `tsconfig` setup for tests.
  - Use RTL’s `screen.getByText` or `getByRole` to validate Brand Selector UI.

---

## 4) PR Workflow (Template + Naming)
- **Priority:** P1
- **Estimated time:** 30–60 minutes
- **Dependencies:** None
- **Files to create/modify:**
  - `.github/PULL_REQUEST_TEMPLATE.md` (new)
- **Acceptance criteria:**
  - PR template includes:
    - Description section
    - Testing notes
    - Checklist (lint/tests/docs)
  - Feature branch naming convention documented:
    - `feature/PHASE-X-description`
- **Implementation notes:**
  - Template example:
    - **Description** (what/why)
    - **Testing** (commands run)
    - **Checklist** (lint, tests, docs, changelog if needed)
  - Optionally add a short note about branch naming in template or README.

---

## 5) Branch Protection (Manual Step)
- **Priority:** P1
- **Estimated time:** 30–60 minutes
- **Dependencies:** CI workflow exists
- **Files to create/modify:**
  - None (manual GitHub settings via CLI)
- **Acceptance criteria:**
  - `master` is protected:
    - Require PR reviews
    - Require CI checks to pass
    - No direct pushes to `master`
- **Implementation notes (gh CLI):**
  - Requires GitHub CLI installed and authenticated.
  - Commands (adjust owner/repo if needed):
    ```bash
    gh api \
      -X PUT \
      repos/randytorres/social-tool/branches/master/protection \
      -f required_status_checks.strict=true \
      -f required_pull_request_reviews.required_approving_review_count=1 \
      -f enforce_admins=true \
      -f restrictions=null

    # Require specific checks (use actual workflow check names)
    gh api \
      -X PATCH \
      repos/randytorres/social-tool/branches/master/protection/required_status_checks \
      -f checks='["backend-tests","frontend-tests","lint"]'
    ```
  - Alternatively use GitHub UI: Settings → Branches → Add rule.

---

## 6) Subagent Workflow (Implementation Guide)
- **Priority:** P1
- **Estimated time:** 30–60 minutes
- **Dependencies:** None
- **Files to create/modify:**
  - `AGENTS.md` or `CONTRIBUTING.md` (optional if desired)
- **Acceptance criteria:**
  - A documented, repeatable workflow for subagents exists.
  - Steps include branch creation, tests, conventional commits, PR, peer review.
- **Implementation notes:**
  - Document the following workflow (include in README/CONTRIBUTING):
    1. Create feature branch: `git checkout -b feature/PHASE-X-description`
    2. Make changes.
    3. Run tests locally (lint + test).
    4. Commit with conventional message (e.g., `feat: add vitest setup`).
    5. Push branch and open PR.
    6. Another agent reviews & approves.
  - Add note: keep PR scope small and update CI if needed.

---

## Suggested Implementation Order
1. Backend test setup (#2)
2. Frontend test setup (#3)
3. CI pipeline (#1)
4. PR template (#4)
5. Branch protection (#5)
6. Subagent workflow doc (#6)
