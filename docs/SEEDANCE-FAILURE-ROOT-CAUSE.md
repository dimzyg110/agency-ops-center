# SEEDANCE Failure Root Cause (OpenClaw)

Date: 2026-02-15 UTC

## Scope
Diagnose why Seedance recovery subagent runs were returning empty / instant failures.

## Findings (with evidence)

### 1) Primary failure is **model/provider routing misconfiguration** for Gemini 3 preview lane

**Observed behavior:** subagents launched with `google/gemini-3-pro-preview` fail instantly with zero tokens.

**Evidence:**
- Session `5d6adf67-d180-43d8-9a76-25eeb5ef4a5e` (2026-02-15 00:47:55 UTC)
  - model: `google -> gemini-3-pro-preview`
  - assistant response: `stopReason=error`
  - usage: `input=0 output=0 totalTokens=0`
  - error: `{"error":{"message":"","code":404,"status":"Not Found"}}`
- Same pattern in prior sessions:
  - `947a5510-0f88-4697-9a19-add65c366030`
  - `f258abb1-4976-448d-84ba-b593e0e866f5`

**Config evidence:**
- `/data/.openclaw/openclaw.json` contains aliases:
  - `google/gemini-3-pro-preview`
  - `google/gemini-3-flash-preview`
- But Google provider model list only includes:
  - `gemini-2.5-pro`
  - `gemini-2.5-flash`

=> Alias exists in agent defaults, but provider model registry does not expose Gemini 3 preview IDs, so calls route to a non-existent model endpoint and fail immediately (404).

---

### 2) This is **not** task-runtime logic failure

Runs die before any meaningful tool/runtime work due to model call failure (0 tokens, immediate 404). That rules out Seedance script/runtime as the first-order cause for those empty sessions.

---

### 3) Secondary blockers on fallback execution path

#### A) OpenClaw browser service unavailable / no browser installed
- `browser.start` returned:
  - `Can't reach the OpenClaw browser control service...`
  - `No supported browser found (Chrome/Brave/Edge/Chromium)`

#### B) Camoufox path currently unstable
- `camofox_create_tab("https://fal.ai")` returned:
  - `500: browserContext.newPage: Target page, context or browser has been closed`

#### C) Controlled FAL Seedance API probe showed timeout sensitivity, but is usable
- Initial 30s probe timed out:
  - `curl: (28) Operation timed out after 30001 milliseconds with 0 bytes received`
- Retest with longer timeout succeeded and returned video artifact JSON.

So API fallback is viable; the critical blocker remains Gemini 3 preview lane routing.

---

## Root Cause Classification

1. **Primary root cause (empty/instant runs):** provider routing / model registration mismatch (`gemini-3-pro-preview` alias present, provider model unavailable) → instant 404.
2. **Secondary operational blockers:** browser stack unavailable and API fallback timing out.

## Safe remediation status

Applied safely in this session:
- Completed diagnosis, isolated root cause, and documented exact failing sessions and config mismatch.
- Did not mutate gateway credentials/secrets.

Proposed safe fix (config-level):
- Remove/disable `google/gemini-3-pro-preview` and `google/gemini-3-flash-preview` aliases until provider models are truly available.
- Route Seedance recovery lanes to working models (e.g., `google/gemini-2.5-pro`, `openrouter/minimax/minimax-m2.5`, `openai-codex/gpt-5.3-codex`).
