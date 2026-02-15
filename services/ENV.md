# Environment Variables

## Required in Railway

### Global
| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key (all agents) |
| `DISCORD_WEBHOOK_URL` | Bot-bus Discord webhook |

### Per-Agent Discord Tokens (create separate Discord apps)
| Agent | Variable | Discord App |
|-------|---------|-------------|
| zeroclaw-roviq | `DISCORD_TOKEN_ROVIQ` | Create new app |
| zeroclaw-glass | `DISCORD_TOKEN_GLASS` | Create new app |
| zeroclaw-roviq-clients | `DISCORD_TOKEN_ROVIQ_CLIENTS` | Create new app |

## How to Create Discord Bots

1. Go to https://discord.com/developers/applications
2. Create New Application (one per agent)
3. Bot → Reset Token → Copy
4. Enable "Message Content Intent" in Bot settings
5. Generate OAuth2 URL to invite bot to server

## Set in Railway

```
# Global
OPENROUTER_API_KEY=your_openrouter_key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Per-agent tokens
DISCORD_TOKEN_ROVIQ=token_for_roviq_agent
DISCORD_TOKEN_GLASS=token_for_glass_agent
DISCORD_TOKEN_ROVIQ_CLIENTS=token_for_clients_agent
```
