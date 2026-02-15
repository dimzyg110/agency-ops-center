# Seedance Fallback Execution Report

**Date:** 2026-02-15  
**Status:** ✅ PARTIAL SUCCESS - FAL.ai API Working (Seedance 1.0 Lite)

---

## Executive Summary

- **Official ByteDance API:** ❌ NOT AVAILABLE (expected Feb 24, 2026)
- **FAL.ai API (Seedance 1.0 Lite):** ✅ WORKING
- **Browser Automation:** ❌ FAILED (environment limitations)

---

## 1. Official API Path Verification

### BytePlus/ByteDance Official API
| Attribute | Status |
|-----------|--------|
| **Availability** | ❌ NOT YET LAUNCHED |
| **Expected Launch** | February 24, 2026 |
| **Platform** | BytePlus (enterprise) |
| **Verification Method** | Web search + curl tests |

**Search Results Confirmed:**
- "The official ByteDance API is expected around February 24, 2026"
- "Volcengine: Not yet officially launched; online debugging is available in the console"
- Dreamina/CapCut access expected late February 2026

### Curl Test Results
```bash
# Tested BytePlus endpoint
curl -s -o /dev/null -w "%{http_code}" "https://www.byteplus.com/"
# Result: 307 (redirect, but no Seedance 2.0 API available)
```

---

## 2. Third-Party API (FAL.ai) - WORKING ✅

### Test Execution

**Endpoint:** `https://queue.fal.run/fal-ai/bytedance/seedance/v1/lite/text-to-video`

**Request:**
```bash
curl -s -X POST "al.run/falhttps://queue.f-ai/bytedance/seedance/v1/lite/text-to-video" \
  -H "Authorization: Key dfa16904-6500-4930-84b6-de04ca8e34df:904d653e3d3d88527c359a3b7ecab0f4" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cat walking in the park", "num_frames": 25}'
```

**Response:**
```json
{
  "status": "IN_QUEUE",
  "request_id": "7751809d-badb-4e8d-86a6-ee81f5d2eb24",
  "status_url": "https://queue.fal.run/fal-ai/bytedance/requests/7751809d-badb-4e8d-86a6-ee81f5d2eb24/status"
}
```

**Completed Response (~30 seconds):**
```json
{
  "video": {
    "url": "https://v3b.fal.media/files/b/0a8e829f/lcD-KHJI9C26B6uG-qEyd_video.mp4",
    "content_type": "video/mp4",
    "file_size": 9872755
  },
  "seed": 234756220
}
```

### Output Artifact

| Field | Value |
|-------|-------|
| **File Path** | `/data/workspace/output/seedance-test/video.mp4` |
| **Size** | 9,872,755 bytes (~9.4 MB) |
| **Format** | MP4 (video/mp4) |
| **Model Used** | Seedance 1.0 Lite (not 2.0) |

---

## 3. Browser Automation Attempt - FAILED ❌

### Attempts Made

| Target | Result | Error |
|--------|--------|-------|
| dreamina.bytedance.com | ❌ Failed | NS_ERROR_UNKNOWN_HOST |
| jimeng.jinritemai.com | ❌ Failed | NS_ERROR_UNKNOWN_HOST |
| seedanceapi.org | ❌ Failed | Internal Server Error |
| laozhang.ai | ❌ Failed | Browser context closed |

### Environment Limitations
- **Camoufox:** Browser context closed unexpectedly
- **OpenClaw Browser:** Gateway service not available in this environment
- **Chrome Relay:** No tabs attached

---

## 4. Reproducible Steps

### Using FAL.ai API (Working)

```bash
# 1. Set your FAL.ai API key
export FAL_API_KEY="dfa16904-6500-4930-84b6-de04ca8e34df:904d653e3d3d88527c359a3b7ecab0f4"

# 2. Submit a video generation request
curl -s -X POST "https://queue.fal.run/fal-ai/bytedance/seedance/v1/lite/text-to-video" \
  -H "Authorization: Key $FAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt here", "num_frames": 25}'

# 3. Check status (replace REQUEST_ID)
curl -s -X GET "https://queue.fal.run/fal-ai/bytedance/requests/YOUR_REQUEST_ID/status" \
  -H "Authorization: Key $FAL_API_KEY"

# 4. Download result when complete
curl -s -o output.mp4 "VIDEO_URL_FROM_RESPONSE"
```

### Alternative: Using Python Client
```python
from fal import fal

result = await fal.subscribe(
    "fal-ai/bytedance/seedance/v1/lite/text-to-video",
    input={"prompt": "A cat walking in the park"}
)
print(result["video"]["url"])
```

---

## 5. Known Limitations

1. **Seedance 2.0 Not Available:** FAL.ai currently only offers Seedance 1.0 Lite and Pro (not 2.0)
2. **Browser Automation Blocked:** Chinese platforms (Dreamina, Jimeng) not accessible from this environment
3. **Third-Party Services Unreliable:** seedanceapi.org had internal server errors

---

## 6. Next Steps Recommendations

1. **Wait for Official API** (Feb 24, 2026) - BytePlus launch expected
2. **Continue with FAL.ai** - Works for Seedance 1.0 Lite/Pro, can migrate to official later
3. **Monitor Dreamina** - Check late February 2026 for international access

---

## 7. Files Created

| File | Path |
|------|------|
| Output Video | `/data/workspace/output/seedance-test/video.mp4` |
| This Report | `/data/workspace/docs/SEEDANCE-FALLBACK-EXECUTION.md` |
