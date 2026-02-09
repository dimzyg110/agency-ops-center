# Revenue Discovery System v2 (Agent-Executable)

## What I Can Run Autonomously

### 1) Craigslist Opportunity Harvester (RSS + HTML fallback)
- **Sources (no account required):**
  - Craigslist RSS feeds (e.g., `https://<city>.craigslist.org/search/<category>?format=rss`)
  - Public Craigslist listing pages (HTML) as a fallback if RSS is incomplete
- **What it does:**
  - Pull new posts (gigs, labor, services, small biz, etc.)
  - Extract title, body snippet, location, date, compensation/budget keywords, contact hints
  - Deduplicate by URL + normalized title
- **Cron:** `*/15 * * * *` (every 15 minutes)

### 2) Indeed Public Listings Watcher (via Brave Search + web fetch)
- **Sources (no account required):**
  - Brave Search API queries that target Indeed listings (e.g., `site:indeed.com ("contract" OR "freelance") <keyword> <city>`)
  - Web-fetch of the resulting public listing pages (when accessible without login)
- **What it does:**
  - Finds newly indexed roles/projects that match a service offering
  - Extracts job title, company, location/remote, posted date (if present), and description snippet
  - Flags listings that are blocked behind login/paywall and logs them as “blocked”
- **Cron:** `*/30 * * * *` (every 30 minutes)

### 3) “Google-like” Market Demand Scanner (Brave Search)
- **Sources (no account required):**
  - Brave Search API (acts as the agent’s search backbone; we are not relying on Google accounts)
- **What it does:**
  - Runs saved queries for buyer-intent signals, e.g.:
    - `"looking for" <service> <city>`
    - `"need" <service> "asap" <city>`
    - `"request for proposal" <service> <state>`
    - `"small business" "seeking" <contractor/service>`
  - Collects URLs + snippets, then fetches public pages for deeper extraction
- **Cron:** `0 */3 * * *` (every 3 hours)

### 4) RSS Feed Ingestion (public feeds only)
- **Sources (no account required):**
  - Any public RSS/Atom feeds Randy provides (local business journals, city pages that expose RSS, niche job boards)
- **What it does:**
  - Normalizes items into the same Opportunity schema as Craigslist/Indeed
- **Cron:** `*/60 * * * *` (hourly)

### 5) Opportunity Normalization + Scoring (local rules, no human loop)
- **What it does:**
  - Converts all discoveries into a single record format:
    - `source`, `url`, `title`, `posted_at`, `location`, `category`, `text`, `contact_fields`, `confidence`
  - Scores opportunities using transparent heuristics (no hidden dependencies):
    - **Fit:** keyword match to service offerings
    - **Urgency:** “ASAP”, “urgent”, tight deadlines
    - **Budget signal:** explicit $ amounts or “paid/compensation” terms
    - **Contactability:** email present, contact form, phone (phone is *not callable* but still a signal)
    - **Locality:** Boston/40mi + remote (configurable)
- **Cron:** `*/10 * * * *` (every 10 minutes)

### 6) Daily/Intraday Digest to Randy (Resend → only torresr14@gmail.com)
- **Important constraint:** outbound email is currently limited to **torresr14@gmail.com** until domain verification.
- **What it does:**
  - Sends a curated digest to Randy containing:
    - Top opportunities (HOT/WARM)
    - Direct links
    - Suggested next-step message text (drafts)
    - “Blocked” list (things behind login / require human action)
- **Cron:**
  - `0 13 * * *` (13:00 UTC daily) — daily digest
  - `0 17 * * 1-5` (17:00 UTC weekdays) — optional second push

### 7) Draft Outreach Generator (drafts only until domain is verified)
- **What it does:**
  - Produces outreach drafts per opportunity:
    - Craigslist direct email (if email is present)
    - Contact-form message (if a public form exists)
    - “Apply” style message for Indeed (often requires login → marked blocked)
  - Stores drafts for Randy to review/copy-paste
- **Cron:** `*/30 * * * *` (every 30 minutes)

---

## What Requires Randy's Setup First

### A) Domain + Sending Identity (to contact leads, not just email Randy)
1. **Verify a sending domain in Resend** (e.g., `roviqai.xyz`) and enable a from-address like `ops@roviqai.xyz`.
2. Provide **approved sender name**, reply-to address, and compliance footer.
3. Confirm basic outreach policy (who to contact, what to avoid, rate limits).

### B) Targeting + Offer Definition (so scoring isn’t generic)
1. Define the **service offerings** (3–5), with keywords and exclusions.
2. Define **geo radius** + “remote allowed” rules.
3. Define **minimum budget/size** thresholds.

### C) Storage + Review Workflow (optional but recommended)
1. Choose where opportunities live (SQLite in workspace is fine, but confirm):
   - fields to store, dedupe rules, retention window
2. Decide how Randy wants to review:
   - email digest only, or a simple local dashboard file/report.

### D) Legal/ToS sanity checks (human responsibility)
- Confirm which sources are acceptable to scrape at what frequency.
- If a site blocks or forbids automated access, the system should respect that and log as “blocked.”

---

## Immediate Actions (I can do now)

1. **Stand up the “public-only” discovery pipeline** using:
   - Craigslist RSS
   - Brave Search queries for Indeed + other public pages
   - Web fetch extraction
2. **Create an initial keyword pack** (generic) for scoring until Randy supplies the real offers.
3. **Start sending Randy a daily digest** to `torresr14@gmail.com` with:
   - Top links
   - Extracted snippets
   - Recommended outreach drafts
4. **Produce a “blocked items” report** (login walls, gated apply flows, missing contact info).

---

## Blocked Until Setup

1. **Direct outreach to prospects at scale** (from an owned domain) — blocked until Resend domain verification + sender identity are set.
2. **Any channel requiring accounts or identity verification**, including:
   - LinkedIn / Sales Navigator
   - Reddit posting/DM
   - Upwork / Thumbtack
   - SAM.gov registration / bidding
3. **Phone-call follow-up** — no voice/calling capability confirmed; phone numbers can be extracted but not actioned.
4. **Anything behind login walls** (Indeed apply flows, portals, paywalled RFPs). The agent will log these as “requires human access.”
