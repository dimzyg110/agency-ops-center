# Environment Variables

## Global (set in Railway Project Settings)

These apply to ALL services:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key (default AI provider) | Yes |
| `DISCORD_WEBHOOK_URL` | Discord webhook for bot-bus | Yes |
| `DISCORD_TOKEN` | Discord bot token | Yes (can use same for all) |

## Do You Need Multiple Discord Tokens?

**No** - One token works for all agents:
- All ZeroClaw agents can share `DISCORD_TOKEN`
- Bot-bus forwards all messages to the same Discord channel

**Yes** - If you want each agent to appear as a different user:
- Create separate Discord apps at https://discord.com/developers/applications
- Each gets own token
- Update each agent's `config.yaml` with different token

## Example: One Token for All

```yaml
# In Railway Project Variables
DISCORD_TOKEN=one_bot_token_for_all_agents
OPENROUTER_API_KEY=your_key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

All agents in `config.yaml`:
```yaml
[channels_config.discord]
token = "${DISCORD_TOKEN}"
```
