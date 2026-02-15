# SEEDANCE Status

Date: 2026-02-15 UTC

## Overall
**Partially running**.
- Gemini 3 preview lane is blocked.
- Controlled Seedance API generation via FAL succeeded (artifact captured).

## Current state by lane

1. **Gemini 3 preview orchestration lane:** **Hard-blocked**
   - Instant failure on launch.
   - Error: `404 Not Found` with `totalTokens=0`.
   - Cause: model alias configured but provider model not actually registered.

2. **Browser fallback lane:** **Blocked**
   - OpenClaw browser control cannot start due to missing supported browser.
   - Camoufox tab creation returned browser context closed error.

3. **API fallback lane (FAL Seedance 1.5 Pro probe):** **Running**
   - First short probe timed out at 30s (`curl 28`).
   - Retest with longer timeout succeeded.

## Controlled test attempt (required)

- Path: API
- Endpoint: `https://fal.run/fal-ai/bytedance/seedance/v1.5/pro/text-to-video`
- Payload file: `/tmp/seedance_payload.json`
- Local response artifact: `/tmp/seedance-fal-test-response.json`
- Generated video URL (artifact):
  - `https://v3b.fal.media/files/b/0a8e82a2/GAnr31gdbCw6pLegn2Mzy_video.mp4`
- Outcome: successful generation (`EXIT:0`, response size 178 bytes, includes `video.url` + `seed`).

## Next action to reach fully "running"

1. Remove/disable Gemini 3 preview aliases and route to known-good models.
2. Restore browser capability (install supported Chromium/Chrome + restart gateway) **or** stabilize API path with longer async/polling flow.
3. Re-run controlled test and capture output URL/file path.

---

## 2026-02-15 00:59 UTC - Test Run Summary

### Status: ✅ PASS (API Fallback Successful)

| Test | Result | Notes |
|------|--------|-------|
| Official ByteDance API | ❌ FAIL | Not available (expected Feb 24, 2026) |
| FAL.ai API (Seedance 1.0 Lite) | ✅ PASS | Video generated successfully |
| Browser Automation | ❌ FAIL | Environment limitations |

### Test Details
- **API Used:** FAL.ai (`fal-ai/bytedance/seedance/v1/lite/text-to-video`)
- **Prompt:** "A cat walking in the park"
- **Generation Time:** ~30 seconds
- **Output File:** `/data/workspace/output/seedance-test/video.mp4` (9.4 MB)
- **Video URL:** `https://v3b.fal.media/files/b/0a8e829f/lcD-KHJI9C26B6uG-qEyd_video.mp4`

### Reproducible Steps
See `/data/workspace/docs/SEEDANCE-FALLBACK-EXECUTION.md` for complete documentation.
