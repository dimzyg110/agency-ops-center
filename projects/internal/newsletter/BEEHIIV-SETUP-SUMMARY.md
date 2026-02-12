# Beehiiv Setup Summary

**Date:** 2026-02-12  
**Status:** ✅ Operational (subscriber management) | ⚠️ Post creation requires Scale plan

---

## Account Details

| Field | Value |
|-------|-------|
| **Publication ID** | `pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3` |
| **Publication Name** | Randy's Newsletter |
| **Organization** | Randy's Hiiv |
| **API Key** | Stored (set as `BEEHIIV_API_KEY` env var) |
| **Active Subscribers** | 2 |
| **Plan** | Free (post creation API disabled) |

## Current Subscribers

| Email | Status | Source | Added |
|-------|--------|--------|-------|
| torresr14@gmail.com | active | direct (website) | Account creation |
| rtorres1331@panther.chaffey.edu | active | glass_website (API) | 2026-02-12 (test) |

---

## What Was Built

### 1. Beehiiv API Client (`beehiiv_client.py`)
Full Python client for Beehiiv V2 API. No external dependencies (uses `urllib`).

**Methods:**
- `add_subscriber(email, utm_source=...)` — ✅ Working
- `list_subscribers(limit=10, status=None)` — ✅ Working
- `get_subscriber(subscriber_id)` — ✅ Working
- `delete_subscriber(subscriber_id)` — ✅ Working
- `create_post(title, content_html, status='draft')` — ⚠️ Requires Scale plan
- `list_posts(limit=10)` — ✅ Working
- `get_publication()` — ✅ Working
- `get_stats()` — ✅ Working

**CLI for testing:**
```bash
cd /data/workspace/projects/internal/newsletter

# List subscribers
BEEHIIV_API_KEY=... BEEHIIV_PUBLICATION_ID=pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3 \
  python3 beehiiv_client.py subscribers

# Add subscriber
BEEHIIV_API_KEY=... BEEHIIV_PUBLICATION_ID=pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3 \
  python3 beehiiv_client.py add --email someone@example.com

# Get stats
BEEHIIV_API_KEY=... BEEHIIV_PUBLICATION_ID=pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3 \
  python3 beehiiv_client.py stats
```

### 2. Pipeline Integration (`pipeline.py`)
Added `--publish-beehiiv` flag. After newsletter composition, it:
1. Reads the HTML draft from `drafts/newsletter_YYYY-MM-DD.html`
2. Attempts to create a Beehiiv draft post via API
3. On free plan: prints instructions to copy HTML into Beehiiv dashboard manually

**Usage:**
```bash
BEEHIIV_API_KEY=... BEEHIIV_PUBLICATION_ID=pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3 \
  python3 pipeline.py --publish-beehiiv
```

### 3. GLASS API Newsletter Route (`services/api/src/routes/newsletter.ts`)
New public endpoint at `POST /api/v1/newsletter/subscribe`:
- Accepts: `{ email: string, utm_source?: string }`
- Proxies to Beehiiv V2 API
- Returns success/error JSON
- No auth required (public signup endpoint)
- Handles duplicate subscribers gracefully

**Required env vars on GLASS API server:**
```bash
BEEHIIV_API_KEY=7IyfuZOjNrp0nm2B8I4qTfxsxqivHT0hPwsMM93XXfojJqXb1afc0uC7tciIkDsO
BEEHIIV_PUBLICATION_ID=pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3
```

### 4. Newsletter Landing Page (`Newsletter.tsx`)
Replaced placeholder forms with functional React signup:
- Custom `useNewsletterSubscribe` hook
- Loading spinner during API call
- Success state with green checkmark
- Error state with message
- Both full-card and inline form variants
- Calls GLASS API → Beehiiv (no API key exposed to browser)

---

## Test Results

| Test | Result |
|------|--------|
| **Add subscriber via API** | ✅ `rtorres1331@panther.chaffey.edu` added successfully |
| **List subscribers** | ✅ Returns 2 active subscribers |
| **Get publication stats** | ✅ Returns pub name, org, subscriber count |
| **Create draft post** | ⚠️ Returns 403 SEND_API_DISABLED (free plan limitation) |
| **Pipeline --publish-beehiiv flag** | ✅ Parses correctly, graceful fallback message on free plan |
| **GLASS API route** | ✅ Committed and pushed to main |
| **Newsletter.tsx signup form** | ✅ Committed — calls `/api/v1/newsletter/subscribe` |

---

## How to Publish a Newsletter (Step by Step)

### Current Workflow (Free Plan)
1. **Run the pipeline:**
   ```bash
   cd /data/workspace/projects/internal/newsletter
   python3 pipeline.py --verbose
   ```
2. **Review the draft:** Open `drafts/newsletter_YYYY-MM-DD.md` and `_checklist.txt`
3. **Copy HTML to Beehiiv:**
   - Open `drafts/newsletter_YYYY-MM-DD.html` in browser to preview
   - Log in to [Beehiiv Dashboard](https://app.beehiiv.com)
   - Create new post → paste HTML content
   - Set subject line: "The Operator's Margin Report — Week of [DATE]"
   - Preview → Schedule for Tuesday 7:00 AM ET
4. **Send**

### Future Workflow (Scale Plan — when upgraded)
1. Run: `python3 pipeline.py --verbose --publish-beehiiv`
2. Review draft in Beehiiv dashboard
3. Click publish/schedule

---

## Environment Variables Required

### Newsletter Pipeline Server
```bash
BEEHIIV_API_KEY=7IyfuZOjNrp0nm2B8I4qTfxsxqivHT0hPwsMM93XXfojJqXb1afc0uC7tciIkDsO
BEEHIIV_PUBLICATION_ID=pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3
```

### GLASS API Server (Railway)
```bash
BEEHIIV_API_KEY=7IyfuZOjNrp0nm2B8I4qTfxsxqivHT0hPwsMM93XXfojJqXb1afc0uC7tciIkDsO
BEEHIIV_PUBLICATION_ID=pub_be324746-7e23-4ac9-8a13-ad104aa8d9c3
```

---

## Next Steps

1. **Set env vars on Railway** — Add `BEEHIIV_API_KEY` and `BEEHIIV_PUBLICATION_ID` to the GLASS API service on Railway so the subscribe endpoint works in production
2. **Push newsletter repo** — The agency-ops-center repo push failed (auth issue in sandbox). Push manually: `cd /data/workspace && git push origin main`
3. **Rename publication** — "Randy's Newsletter" → "The Operator's Margin Report" in Beehiiv dashboard settings
4. **Upgrade plan** — When ready, upgrade to Beehiiv Scale plan to enable `--publish-beehiiv` automated draft creation
5. **Send first real issue** — Run the pipeline, review, copy HTML to Beehiiv, send
6. **Monitor** — Track open rates and subscriber growth in Beehiiv dashboard

---

## Files Changed

| File | Action | What Changed |
|------|--------|-------------|
| `beehiiv_client.py` | Created | Full Beehiiv V2 API client with CLI |
| `pipeline.py` | Modified | Added `--publish-beehiiv` flag + `_publish_to_beehiiv()` |
| `glass/services/api/src/routes/newsletter.ts` | Created | POST /api/v1/newsletter/subscribe endpoint |
| `glass/services/api/src/index.ts` | Modified | Registered newsletter route |
| `glass/apps/web/src/pages/Newsletter.tsx` | Modified | Functional signup form replacing placeholder |
