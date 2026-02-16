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
                    │   Port 8080          │
                    │   COO & Revenue      │
                    └──────┬──────┬────────┘
                           │      │
              dispatches   │      │   dispatches
                           ▼      ▼
              ┌────────────────┐  ┌──────────────────────┐
              │  @glass        │  │  @clients             │
              │  (Builder)     │  │  (Creative)           │
              │  Port 8081     │  │  Port 8082            │
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

| Agent | Discord | Port | Role | Owns |
|-------|---------|------|------|------|
| **zeroclaw-roviq** | `@roviq` | 8080 | Operator — COO & Revenue | Strategy, revenue pipeline, lead funnel, agent coordination, dashboard/memory |
| **zeroclaw-glass** | `@glass` | 8081 | Builder — CTO & Engineer | GLASS platform, SIGNAL engine, API, scrapers, data, infrastructure, DevOps |
| **zeroclaw-roviq-clients** | `@clients` | 8082 | Creative — CD & Account Mgr | All client deliverables (AC, CH, HOP), design, content, social, websites, SEO |

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

## Services

| Service | Description | Port |
|---------|-------------|------|
| **bot-bus** | Message relay + Discord forwarding (Express + SSE) | 3000 |
| **zeroclaw-roviq** | Agency operations — see [Operator README](./zeroclaw-roviq/README.md) | 8080 |
| **zeroclaw-glass** | Technical infrastructure — see [Builder README](./zeroclaw-glass/README.md) | 8081 |
| **zeroclaw-roviq-clients** | Client delivery — see [Creative README](./zeroclaw-roviq-clients/README.md) | 8082 |

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

# ZeroClaw (each agent needs separate Discord bot tokens)
DISCORD_TOKEN_ROVIQ=your_roviq_bot_token
DISCORD_TOKEN_GLASS=your_glass_bot_token
DISCORD_TOKEN_CLIENTS=your_clients_bot_token

# Shared
OPENROUTER_API_KEY=your_api_key
```

See `ENV.md` for full variable list.

---

## Bot-Bus API

The bot-bus relays messages between agents and forwards to Discord.

**Send message:**
```bash
curl -X POST http://localhost:3000/relay \
  -H "Content-Type: application/json" \
  -d '{"from": "zeroclaw-roviq", "to": "zeroclaw-glass", "text": "Hello"}'
```

**Subscribe to messages (SSE):**
```bash
curl -N http://localhost:3000/subscribe?bot=zeroclaw-glass
```

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
