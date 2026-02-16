# Roviq Agency Services

Infrastructure for running three specialized AI agents with inter-communication via Discord.

---

## Architecture

```
                        Randy (human founder)
                              │
                              │ priorities & approvals
                              ▼
                    ┌─────────────────────┐
                    │   @roviq (Operator)  │
                    │   PORT from env      │
                    │   COO & Revenue      │
                    └──────┬──────┬────────┘
                           │      │
              dispatches   │      │   dispatches
                           ▼      ▼
              ┌────────────────┐  ┌──────────────────────┐
              │  @glass        │  │  @clients             │
              │  (Builder)     │  │  (Creative)           │
              │  PORT from env │  │  PORT from env        │
              │  CTO/Engineer  │  │  Creative Director    │
              └───────┬────────┘  └──────────┬───────────┘
                      │                      │
                      │   data/APIs/code     │
                      └──────────────────────┘
                         direct coordination
```

All three agents share a Discord server for communication. They tag each other with structured messages for task dispatch, status updates, blockers, and handoffs.

---

## Agent Roles

| Agent | Discord | Runtime Port | Role | Owns |
|-------|---------|--------------|------|------|
| **zeroclaw-roviq** | `@roviq` | env `PORT` (default 8080) | Operator — COO & Revenue | Strategy, revenue pipeline, lead funnel, agent coordination, dashboard/memory |
| **zeroclaw-glass** | `@glass` | env `PORT` (default 8080) | Builder — CTO & Engineer | GLASS platform, SIGNAL engine, API, scrapers, data, infrastructure, DevOps |
| **zeroclaw-roviq-clients** | `@clients` | env `PORT` (default 8080) | Creative — CD & Account Mgr | All client deliverables (AC, CH, HOP), design, content, social, websites, SEO |

### Separation of Concerns

- **@roviq** never writes code, designs, or creates content — it orchestrates and drives revenue
- **@glass** never talks to clients or makes business decisions — it builds and maintains tech
- **@clients** never touches infrastructure or makes revenue decisions — it creates client-facing work
- **@glass** and **@clients** can coordinate directly on day-to-day handoffs (data for content, bug fixes, etc.)
- All strategic decisions and client communications route through **@roviq**

---

## Communication Protocol

### Discord Message Format

```
@[agent] [TYPE] Brief description
What: Detailed explanation
Priority: P0/P1/P2
Deadline: Date or timeframe
Context: Links to relevant files or docs
Dependencies: What needs to happen first (or "None")
```

**Types:**
- `[TASK]` — New work assignment
- `[REQUEST]` — Asking another agent for something
- `[STATUS]` — Progress update or completion report
- `[BLOCKED]` — Can't proceed, needs help or approval
- `[DONE]` — Task complete with deliverable details

### Flow Rules

1. **@roviq dispatches** → @glass and @clients receive and execute
2. **@glass ↔ @clients coordinate** on technical handoffs (SIGNAL content, website updates, bug fixes)
3. **Blockers route to @roviq** → who escalates to Randy if needed
4. **No agent self-assigns strategic work** — @roviq prioritizes the backlog

---

## Model Strategy (Randy-Approved, Locked)

All agents use model diversity to catch different failure modes. The specialist that creates work and the reviewer that checks it MUST be different models.

| Tier | Model | Route | Best For | Cost |
|------|-------|-------|----------|------|
| **T1 — Architect** | GPT 5.3 Codex | `openai-codex/gpt-5.3-codex` | Architecture, complex code, DB design, code review | OAuth (free) |
| **T2 — Senior** | Claude Opus 4.6 | `anthropic/claude-opus-4-6` | Strategy, orchestration, nuanced judgment, long writes | $5/$25 |
| **T3 — Workhorse** | MiniMax M2.5 | `openrouter/minimax/minimax-m2.5` | Clear-scoped tasks, fast execution, reviews, research | $1/$4 |
| **T4 — Specialist** | Kimi K2.5 | `openrouter/moonshotai/kimi-k2.5` | Frontend, long-context reads, large file writes | $0.60/$2.50 |
| **Imagen** | Gemini 2.0 Flash | `google/gemini-2.0-flash-exp-image-generation` | Image generation ONLY | — |

**See each agent's README for their specific model assignments.**

---

## Quality Pipeline

Every deliverable follows: `REQUEST → DECOMPOSE → ASSIGN → EXECUTE → REVIEW → INTEGRATE → DELIVER`

Non-negotiable rules:
- Every deliverable gets **2 independent reviews from different models**
- Every client-facing piece of content gets a **humanizer pass** (24+ AI patterns checked)
- Every piece of code goes through **PR workflow** (feature branch → review → merge)
- Cannabis compliance is checked on **all public-facing content** (no medical claims, 21+ gates, state-compliant)
- **@roviq dispatches** and synthesizes reviews — agents don't self-approve

---

## Services

| Service | Description | Port |
|---------|-------------|------|
| **bot-bus** | Message relay + Discord forwarding (Express + SSE) | 3000 |
| **zeroclaw-roviq** | Agency operations — see [Operator README](./zeroclaw-roviq/README.md) | env `PORT` (default 8080) |
| **zeroclaw-glass** | Technical infrastructure — see [Builder README](./zeroclaw-glass/README.md) | env `PORT` (default 8080) |
| **zeroclaw-roviq-clients** | Client delivery — see [Creative README](./zeroclaw-roviq-clients/README.md) | env `PORT` (default 8080) |

---

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/Roviq-AI/agency-ops-center.git
cd agency-ops-center

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your API keys and tokens (each agent needs its own Discord bot token)

# 4. Run all services
docker compose -f services/docker-compose.yml up -d
```

## Environment Variables

Create `.env` file:

```bash
# Bot Bus
DISCORD_WEBHOOK_URL=your_discord_webhook_url
DISCORD_MIRROR_ENABLED=true
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_MIRROR_SOURCE_CHANNEL_ID=your_shared_group_channel_id
DISCORD_MIRROR_TO_BUS_ENABLED=true
DISCORD_MIRROR_BOTS=zeroclaw-roviq,zeroclaw-glass,zeroclaw-roviq-clients
RELAY_MAX_HOPS=5
SSE_KEEPALIVE_MS=15000

# Optional fallback (if bus shows "-> 0 bot(s)")
DISCORD_MIRROR_MENTION_FALLBACK=true
DISCORD_MIRROR_MENTION_USER_IDS=1467196508209156148,1472663591843926207,1472663903900274788

# True wiring (set on each zeroclaw-* service)
BUS_SUBSCRIBE_ENABLED=true
BUS_URL=http://bot-bus:8080
BUS_BOT_NAME=zeroclaw-roviq   # or zeroclaw-glass / zeroclaw-roviq-clients

# ZeroClaw (each agent needs separate Discord bot tokens)
DISCORD_TOKEN_ROVIQ=your_roviq_bot_token
DISCORD_TOKEN_GLASS=your_glass_bot_token
DISCORD_TOKEN_ROVIQ_CLIENTS=your_clients_bot_token

# Shared
OPENROUTER_API_KEY=your_api_key
```

See `ENV.md` for full variable list.

---

## Bot-Bus API

The bot-bus relays messages between agents, forwards to Discord, and can fanout human Discord messages to all bots.

**Send direct message:**
```bash
curl -X POST http://localhost:3000/relay \
  -H "Content-Type: application/json" \
  -d '{"from": "zeroclaw-roviq", "to": "zeroclaw-glass", "text": "Hello"}'
```

**Send to all subscribers:**
```bash
curl -X POST http://localhost:3000/relay \
  -H "Content-Type: application/json" \
  -d '{"from": "coo", "to": "all", "text": "Standup in 5"}'
```

**Explicit broadcast endpoint:**
```bash
curl -X POST http://localhost:3000/broadcast \
  -H "Content-Type: application/json" \
  -d '{"from":"discord-human","text":"sanity check","targets":["zeroclaw-roviq","zeroclaw-glass","zeroclaw-roviq-clients"]}'
```

**Subscribe to messages (SSE):**
```bash
curl -N http://localhost:3000/subscribe?bot=zeroclaw-glass
```

**Discord group → bus fanout mode:**
- Enable `DISCORD_MIRROR_ENABLED=true`
- Set `DISCORD_MIRROR_SOURCE_CHANNEL_ID` to your shared Discord channel
- Enable `DISCORD_MIRROR_TO_BUS_ENABLED=true`
- Set `DISCORD_MIRROR_BOTS` with comma-separated bot ids
- Human messages in that channel are published to all listed bots (no tagging required)
- If no bot subscribers are connected, optional mention fallback can ping bots directly (`DISCORD_MIRROR_MENTION_FALLBACK=true`)
- Loop guard is enforced via `RELAY_MAX_HOPS` (default 5)

---

## Adding New Agents

```bash
# 1. Copy any existing agent folder
cp -r services/zeroclaw-roviq services/zeroclaw-newagent

# 2. Update the README.md with the new agent's role definition
# 3. Add to docker-compose.yml with unique port
# 4. Create a new Discord bot app and add token to .env
# 5. Invite the bot to the shared Discord server
```

---

## Railway Deployment

### 1. Set Global Variables

In Railway → Your Project → **Variables**, add API keys and tokens. These apply to ALL services.

### 2. Deploy Each Service

Each folder has `railway.toml` — deploy via GitHub integration (recommended) or Railway CLI.

---

## Local Development

```bash
# Run single service
docker compose -f services/docker-compose.yml up bot-bus

# View logs
docker compose -f services/docker-compose.yml logs -f

# Stop all
docker compose -f services/docker-compose.yml down
```
