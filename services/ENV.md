# Environment Variables

## Global (set in Railway Project Settings)

These apply to ALL services:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key (default AI provider) | Yes |
| `OPENROUTER_BASE_URL` | OpenRouter base URL (optional) | No |
| `ANTHROPIC_API_KEY` | Anthropic API key | No |
| `DISCORD_WEBHOOK_URL` | Discord webhook for bot-bus | Yes |
| `DISCORD_TOKEN` | Discord bot token for all agents | Yes |

## Service-Specific

### bot-bus
| Variable | Description |
|----------|-------------|
| `DISCORD_WEBHOOK_URL` | Where to forward messages |

### All ZeroClaw agents
| Variable | Description |
|----------|-------------|
| `DISCORD_TOKEN` | Bot token to connect to Discord |
| `OPENROUTER_API_KEY` | AI provider |
| `ANTHROPIC_API_KEY` | Alternative AI provider |

## Recommended: Set at Project Level

In Railway → Project → Variables, add:

```
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DISCORD_TOKEN=your_bot_token
```

Then each service inherits these automatically.

## Per-Service Overrides

If needed, you can override per service:
- bot-bus
- zeroclaw-roviq
- zeroclaw-glass
- zeroclaw-roviq-clients
