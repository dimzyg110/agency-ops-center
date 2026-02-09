# The Operator's Margin Report

Weekly newsletter for Massachusetts cannabis dispensary operators. Scrapes news, events, market data, and Reddit — then composes a newsletter with editorial analysis, margin tips, and compliance reminders.

**Tagline:** _Survival intel for Massachusetts cannabis operators. Less headlines, more margin._

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (requires Brave Search API key)
cp ../.env .env  # or ensure BRAVE_API_KEY and OPENAI_API_KEY are set

# Run the full pipeline
python pipeline.py

# Output: drafts/newsletter_YYYY-MM-DD.md + .html
```

---

## Pipeline

9-stage pipeline orchestrated by `pipeline.py`:

| Stage         | Script                              | What it does                                    |
| ------------- | ----------------------------------- | ----------------------------------------------- |
| 1. News       | `scrapers/news_scraper.py`          | Brave Search → MA cannabis news articles        |
| 2. Events     | `scrapers/events_scraper.py`        | Brave Search → upcoming cannabis events         |
| 3. Social     | `scrapers/social_scraper.py`        | Reddit (r/bostontrees, r/mainetrees)            |
| 4. Tools      | `scrapers/tools_scraper.py`         | Brave Search → cannabis industry tools          |
| 5. CCC Ingest | `scrapers/ccc_ingest.py`            | CCC open datasets → demographics/trends         |
| 6. Market     | `scrapers/market_data_processor.py` | Lead-tool signals + CCC snapshot → market pulse |
| 7. Validate   | `content_validator.py`              | Check data quality (non-blocking)               |
| 8. Compose    | `composer.py`                       | All data → newsletter draft (MD + HTML)         |
| 9. Quality    | `quality_checker.py`                | Link check, duplicate check (non-blocking)      |

### Data Flow

```
Brave Search API ──→ news/events/tools JSON ──┐
Reddit API ────────→ reddit JSON ─────────────┤
CCC Open Data ─────→ ccc_ingest JSON ─────────┤
Lead-tool signals ─→ market_pulse JSON ────────┤
CCC snapshot ──────→ operator count (934) ─────┤
                                               ▼
                                         composer.py
                                               │
                                   ┌───────────┼───────────┐
                                   ▼           ▼           ▼
                              .md draft    .html draft   checklist
```

---

## Project Structure

```
newsletter/
├── README.md                  ← you are here
├── BRANDING.md                ← colors, fonts, design system
├── requirements.txt           ← python dependencies
│
├── pipeline.py                ← orchestrator (run this)
├── composer.py                ← newsletter generator (MD + HTML)
├── content_validator.py       ← data quality checks
├── quality_checker.py         ← draft quality checks
├── data_contract.py           ← expected data schema
│
├── scrapers/
│   ├── brave_client.py        ← shared Brave Search API client
│   ├── news_scraper.py        ← news articles (Brave)
│   ├── events_scraper.py      ← events (Brave)
│   ├── tools_scraper.py       ← industry tools (Brave)
│   ├── social_scraper.py      ← Reddit scraper
│   ├── ccc_ingest.py          ← CCC open data ingestion
│   ├── market_data_processor.py ← market pulse generation
│   ├── http_client.py         ← shared HTTP utilities
│   ├── relevance.py           ← relevance scoring
│   └── source_registry.py     ← source URL management
│
├── config/sources/            ← source URLs (YAML)
├── data/                      ← runtime data (gitignored)
│   ├── *.json                 ← scraped data files
│   └── ccc/                   ← raw CCC datasets (~355MB)
│
├── drafts/                    ← generated newsletters
│   ├── newsletter_YYYY-MM-DD.md   ← latest output
│   ├── newsletter_ma_v1.md        ← reference: first MA draft
│   └── newsletter_v2_real.md      ← reference: AI editorial version
│
└── landing/
    └── index-human.html       ← subscriber landing page
```

---

## Environment Variables

| Variable                        | Required | Description                             |
| ------------------------------- | -------- | --------------------------------------- |
| `BRAVE_API_KEY`                 | Yes      | Brave Search API key                    |
| `OPENAI_API_KEY`                | Yes      | OpenAI API key (for editorial rewrites) |
| `NEWSLETTER_ENABLE_LLM_REWRITE` | No       | `1` to enable (default), `0` to disable |
| `NEWSLETTER_REWRITE_MODEL`      | No       | OpenAI model (default: `gpt-4.1-mini`)  |

---

## Newsletter Sections

Each issue includes:

| Section                | Source           | Content                                                          |
| ---------------------- | ---------------- | ---------------------------------------------------------------- |
| 🔥 Top Story           | News scraper     | LLM editorial analysis of top MA cannabis story                  |
| 📊 The Number          | CCC snapshot     | Rotating stat (934 active operators, new licenses, hiring, etc.) |
| 📈 Market Pulse        | Market processor | License activity, hiring heat, review momentum                   |
| 🌍 Demographic Signal  | CCC ingest       | Equity/demographic trends from CCC data                          |
| 📋 License Watch       | News + Reddit    | Licensing news and updates                                       |
| 🛠️ Tool of the Week    | Tools scraper    | Featured cannabis industry tool                                  |
| 📅 Upcoming Events     | Events scraper   | Cannabis events (conferences, expos, roundtables)                |
| ⚡ Quick Hits          | News scraper     | 3 additional news items                                          |
| 💡 Margin Tip          | Rotating library | MA-specific, actionable margin improvement advice                |
| 📋 Compliance Reminder | Rotating library | CCC compliance tips (Metrc, surveillance, limits)                |

---

## Key Data Sources

- **CCC Snapshot** (`lead-tool/data/snapshots/ccc_snapshot_*.json`): License counts, operator status. Currently shows **934 active licenses** out of 1,693 total.
- **Signals Pack** (`lead-tool/output/ma_operator_signals_pack_*.csv`): Top-150 operator prospecting list with distress scores, hiring signals.
- **CCC Open Data** (`data/ccc/`): Raw datasets from masscannabiscontrol.com — applications, sales, pricing, demographics.
- **Brave Search**: Real-time news, events, and tool discovery.

---

## Content Quality Controls

- **News scoring** prioritizes MA-local + cannabis articles (MA mentions without cannabis context are penalized)
- **Junk filtering** removes navigation text, short titles, and non-article results
- **THE NUMBER** rotates weekly through 5 data points (operators, licenses, hiring, distress, reviews) — never static
- **Margin tips** are 8 MA-specific, detailed tips with title/body/action format
- **Compliance reminders** rotate through 4 CCC-focused topics weekly

---

## Reference Newsletters

Two reference files in `drafts/` show the quality targets:

- **`newsletter_ma_v1.md`** (308 lines) — Rich MA-local content with CCC watchlist, pricing index, town hall spotlights
- **`newsletter_v2_real.md`** (149 lines) — AI-generated editorial with real sourced data ($1.65B sales, $14.20/eighth, etc.)
