import express from 'express';
import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { forwardToDiscord } from './discord-forwarder.js';

const app = express();
app.use(express.json());

// In-memory message store for SSE
const clients = new Map();

const MIRROR_ENABLED = String(process.env.DISCORD_MIRROR_ENABLED || '').toLowerCase() === 'true';
const MIRROR_TOKEN = process.env.DISCORD_BOT_TOKEN;
const MIRROR_SOURCE_CHANNEL_ID = process.env.DISCORD_MIRROR_SOURCE_CHANNEL_ID;
const MIRROR_TARGET_USER_ID = process.env.DISCORD_MIRROR_TARGET_USER_ID;

function buildJumpLink(guildId, channelId, messageId) {
  if (!guildId || !channelId || !messageId) return null;
  return `https://discord.com/channels/${guildId}/${channelId}/${messageId}`;
}

function initDiscordMirror() {
  if (!MIRROR_ENABLED) {
    console.log('[mirror] disabled');
    return;
  }
  if (!MIRROR_TOKEN || !MIRROR_SOURCE_CHANNEL_ID || !MIRROR_TARGET_USER_ID) {
    console.log('[mirror] missing DISCORD_BOT_TOKEN / DISCORD_MIRROR_SOURCE_CHANNEL_ID / DISCORD_MIRROR_TARGET_USER_ID');
    return;
  }

  const client = new Client({
    intents: [
      GatewayIntentBits.Guilds,
      GatewayIntentBits.GuildMessages,
      GatewayIntentBits.MessageContent,
      GatewayIntentBits.DirectMessages,
    ],
    partials: [Partials.Channel],
  });

  client.on('ready', () => {
    console.log(`[mirror] connected as ${client.user?.tag ?? 'unknown'}`);
  });

  client.on('messageCreate', async (msg) => {
    try {
      if (!msg || msg.channelId !== MIRROR_SOURCE_CHANNEL_ID) return;
      if (msg.author?.bot) return;

      const target = await client.users.fetch(MIRROR_TARGET_USER_ID);
      const jump = buildJumpLink(msg.guildId, msg.channelId, msg.id);
      const body = [`🔔 #${msg.channel?.name ?? 'channel'}`, `**${msg.author?.username ?? 'unknown'}**: ${msg.content || '(no text)'}`];
      if (jump) body.push(jump);

      await target.send(body.join('\n'));
      console.log(`[mirror] forwarded message ${msg.id} to ${MIRROR_TARGET_USER_ID}`);
    } catch (err) {
      console.error('[mirror] forward failed:', err?.message || err);
    }
  });

  client.login(MIRROR_TOKEN).catch((err) => {
    console.error('[mirror] login failed:', err?.message || err);
  });
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString(), mirror: MIRROR_ENABLED });
});

// Relay endpoint - receive message from a bot and distribute
app.post('/relay', async (req, res) => {
  const { text, from, to } = req.body;

  console.log(`[relay] ${from} -> ${to}: ${text}`);

  // Forward to Discord for human visibility
  if (process.env.DISCORD_WEBHOOK_URL) {
    await forwardToDiscord(`**${from}**: ${text}`);
  }

  // Push to subscribed bot via SSE
  if (to && clients.has(to)) {
    const clientRes = clients.get(to);
    clientRes.write(`data: ${JSON.stringify({ from, text })}\n\n`);
  }

  res.json({ success: true });
});

// SSE endpoint - bots subscribe to messages
app.get('/subscribe', (req, res) => {
  const { bot } = req.query;

  if (!bot) {
    return res.status(400).json({ error: 'bot parameter required' });
  }

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  clients.set(bot, res);

  res.on('close', () => {
    clients.delete(bot);
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Bot bus listening on port ${PORT}`);
  initDiscordMirror();
});
