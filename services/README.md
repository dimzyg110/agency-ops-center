# Roviq Agency Services

Infrastructure for running multiple AI agents with inter-communication.

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/Roviq-AI/agency-ops-center.git
cd agency-ops-center

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your API keys and tokens

# 4. Run all services
docker compose -f services/docker-compose.yml up -d
```

## Services

| Service | Description | Port |
|---------|-------------|------|
| **bot-bus** | Message relay + Discord forwarding | 3000 |
| **zeroclaw-roviq** | Roviq agency operations | 8080 |
| **zeroclaw-glass** | GLASS data/operations | 8081 |
| **zeroclaw-roviq-clients** | Client-facing agent | 8082 |

## Agents

### zeroclaw-roviq
Internal agency operations - coordinates all Roviq work.

### zeroclaw-glass  
GLASS platform operations - manages scrapers, data, API.

### zeroclaw-roviq-clients
Client-facing agent - handles client communications.

## Environment Variables

Create `.env` file:

```bash
# Bot Bus
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# ZeroClaw (each agent)
DISCORD_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key
```

## Adding New Agents

```bash
# 1. Copy template
cp -r services/zeroclaw-template services/zeroclaw-myagent

# 2. Edit config.yaml - change name
# 3. Add to docker-compose.yml
```

## Railway Deployment

### 1. Set Global Variables

In Railway → Your Project → **Variables**, add:

```
OPENROUTER_API_KEY=your_key_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DISCORD_TOKEN=your_bot_token
```

These apply to ALL services automatically.

### 2. Deploy Each Service

Each folder has `railway.toml` - deploy via:
- GitHub integration (recommended)
- Railway CLI: `railway up`

See `ENV.md` for full variable list.

## Bot-to-Bot Communication

All agents communicate through bot-bus:

```
[zeroclaw-roviq]     --> [Bot Bus] --> [Discord]
[zeroclaw-glass]     --> [Bot Bus] --> [Discord]  
[zeroclaw-clients]  --> [Bot Bus] --> [Discord]
[COO (OpenClaw)]    --> [Bot Bus] --> [Discord]
```

### API

**Send message:**
```bash
curl -X POST http://localhost:3000/relay \
  -H "Content-Type: application/json" \
  -d '{"from": "zeroclaw-roviq", "to": "zeroclaw-glass", "text": "Hello"}'
```

**Subscribe to messages:**
```bash
curl -N http://localhost:3000/subscribe?bot=zeroclaw-glass
```

## Local Development

```bash
# Run single service
docker compose -f services/docker-compose.yml up bot-bus

# View logs
docker compose -f services/docker-compose.yml logs -f

# Stop all
docker compose -f services/docker-compose.yml down
```
