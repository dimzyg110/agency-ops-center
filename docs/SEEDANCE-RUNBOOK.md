# SEEDANCE Runbook (Recovery + Verification)

## 1) Fast triage checklist

1. Check for instant model failure in session logs:
   - Look for `totalTokens=0` + `404 Not Found` on first assistant turn.
2. Confirm model registry mismatch:
   - In `/data/.openclaw/openclaw.json`, verify whether lane aliases reference models absent from provider model list.
3. Check fallback execution stack:
   - Browser service status (`browser.status/start`)
   - Camoufox tab creation
   - API probe to Seedance provider endpoint

---

## 2) Known-good diagnosis commands

```bash
# Find seedance/gemini failures in session history
grep -RIn "seedance\|gemini-3-pro-preview\|Not Found\|totalTokens\":0" /data/.openclaw/agents/main/sessions | head -n 200

# Verify aliases in active config
grep -n "gemini-3-pro-preview\|gemini-3-flash-preview" /data/.openclaw/openclaw.json

# Verify Google provider actually exposes those model IDs (it currently does not)
# (inspect google models list in openclaw.json / models.json)
```

---

## 3) Remediation (safe)

### A. Fix model routing
- Remove or comment out:
  - `google/gemini-3-pro-preview`
  - `google/gemini-3-flash-preview`
- Use supported lanes:
  - `google/gemini-2.5-pro`
  - `google/gemini-2.5-flash`
  - `openrouter/minimax/minimax-m2.5`
  - `openai-codex/gpt-5.3-codex`

### B. Browser fallback recovery
1. Ensure supported browser exists (Chrome/Chromium/Brave/Edge).
2. Restart gateway.
3. Re-check:
   - `browser.status`
   - `browser.start`
4. If using Camoufox, verify `camofox_create_tab` works before task automation.

### C. API fallback recovery (FAL)
Use async/poll flow (preferred) and allow longer wait than 30s.

Example probe payload:
```json
{
  "prompt": "A static shot of a blue circle on white background.",
  "duration": "4",
  "resolution": "480p",
  "aspect_ratio": "1:1",
  "generate_audio": false
}
```

Example probe command used in this investigation:
```bash
curl -sS --connect-timeout 10 --max-time 30 \
  -X POST "https://fal.run/fal-ai/bytedance/seedance/v1.5/pro/text-to-video" \
  -H "Authorization: Key $FAL_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/seedance_payload.json
```

Observed behavior:
- 30s timeout can fail (`curl 28`).
- 180s window succeeded and returned:
  - local response file: `/tmp/seedance-fal-test-response.json`
  - sample artifact URL: `https://v3b.fal.media/files/b/0a8e82a2/GAnr31gdbCw6pLegn2Mzy_video.mp4`

---

## 4) Failure modes and interpretation

- **Instant 404 + 0 tokens:** routing/model registration issue (not runtime logic).
- **Browser start failure + no supported browser:** environment capability issue.
- **Camoufox context closed:** local browser-runtime instability.
- **API timeout:** provider/network latency or endpoint incompatibility; switch to queue/poll pattern and longer timeout.

---

## 5) Definition of done

Recovery is complete only when all are true:
1. Subagent no longer fails instantly on model startup.
2. One controlled Seedance generation succeeds.
3. Output artifact path/URL captured in status doc.
4. Reproducible command sequence documented and validated.
