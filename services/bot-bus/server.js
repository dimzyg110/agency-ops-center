import express from 'express';
import { Client, GatewayIntentBits, Partials } from 'discord.js';
import { forwardToDiscord } from './discord-forwarder.js';

const app = express();
app.use(express.json());

// In-memory message store for SSE subscribers
// Map<botName, ServerResponse>
const clients = new Map();

const MIRROR_ENABLED = String(process.env.DISCORD_MIRROR_ENABLED || '').toLowerCase() === 'true';
const MIRROR_TOKEN = process.env.DISCORD_BOT_TOKEN;
const MIRROR_SOURCE_CHANNEL_ID = process.env.DISCORD_MIRROR_SOURCE_CHANNEL_ID;
const MIRROR_TARGET_USER_ID = process.env.DISCORD_MIRROR_TARGET_USER_ID;

// Bus fanout mode: take a human Discord message and broadcast to all listed bots
const MIRROR_BUS_ENABLED = String(process.env.DISCORD_MIRROR_TO_BUS_ENABLED || '').toLowerCase() === 'true';
const MIRROR_BUS_BOTS = (process.env.DISCORD_MIRROR_BOTS || '')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

// Loop guard for agent-to-agent relays
const RELAY_MAX_HOPS = Number(process.env.RELAY_MAX_HOPS || 5);

function buildJumpLink(guildId, channelId, messageId) {
  if (!guildId || !channelId || !messageId) return null;
  return `https://discord.com/channels/${guildId}/${channelId}/${messageId}`;
}

function subscribedBots() {
  return Array.from(clients.keys());
}

function resolveBroadcastTargets() {
  if (MIRROR_BUS_BOTS.length > 0) return MIRROR_BUS_BOTS;
  return subscribedBots();
}

function sendToBot(bot, payload) {
  const clientRes = clients.get(bot);
  if (!clientRes) return false;
  clientRes.write(`data: ${JSON.stringify(payload)}\n\n`);
  return true;
}

function broadcastToBots(payload, targets = resolveBroadcastTargets()) {
  let delivered = 0;
  for (const bot of targets) {
    if (sendToBot(bot, payload)) delivered += 1;
  }
  return delivered;
}

function initDiscordMirror() {
  if (!MIRROR_ENABLED) {
    console.log('[mirror] disabled');
    return;
  }
  if (!MIRROR_TOKEN || !MIRROR_SOURCE_CHANNEL_ID) {
    console.log('[mirror] missing DISCORD_BOT_TOKEN / DISCORD_MIRROR_SOURCE_CHANNEL_ID');
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

      const jump = buildJumpLink(msg.guildId, msg.channelId, msg.id);

      // Optional DM mirror for human visibility
      if (MIRROR_TARGET_USER_ID) {
        const target = await client.users.fetch(MIRROR_TARGET_USER_ID);
        const body = [
          `🔔 #${msg.channel?.name ?? 'channel'}`,
          `**${msg.author?.username ?? 'unknown'}**: ${msg.content || '(no text)'}`,
        ];
        if (jump) body.push(jump);
        await target.send(body.join('\n'));
      }

      // Optional bus fanout: publish the human message to all configured bots
      if (MIRROR_BUS_ENABLED) {
        const delivered = broadcastToBots(
          {
            from: 'discord-human',
            text: msg.content || '',
            meta: {
              source: 'discord',
              guildId: msg.guildId || null,
              channelId: msg.channelId,
              messageId: msg.id,
              authorId: msg.author?.id || null,
              authorName: msg.author?.username || null,
              jump,
            },
            hops: 0,
          },
          resolveBroadcastTargets()
        );
        console.log(`[mirror] bus fanout message ${msg.id} -> ${delivered} bot(s)`);
      }

      console.log(`[mirror] processed message ${msg.id}`);
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
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    mirror: MIRROR_ENABLED,
    mirrorBus: MIRROR_BUS_ENABLED,
    subscribers: subscribedBots(),
  });
});

// Relay endpoint - receive message from a bot and distribute
app.post('/relay', async (req, res) => {
  const { text = '', from = 'unknown', to, meta = {}, hops = 0 } = req.body || {};
  const nextHops = Number(hops) + 1;

  if (nextHops > RELAY_MAX_HOPS) {
    console.warn(`[relay] dropped loop from=${from} to=${to || '*'} hops=${nextHops}`);
    return res.status(202).json({ success: false, dropped: 'max_hops', maxHops: RELAY_MAX_HOPS });
  }

  console.log(`[relay] ${from} -> ${to || '*'}: ${text}`);

  // Forward to Discord for human visibility
  if (process.env.DISCORD_WEBHOOK_URL) {
    await forwardToDiscord(`**${from}**: ${text}`);
  }

  let delivered = 0;

  if (to === '*' || to === 'all') {
    delivered = broadcastToBots({ from, text, meta, hops: nextHops });
  } else if (to) {
    delivered = sendToBot(to, { from, text, meta, hops: nextHops }) ? 1 : 0;
  }

  res.json({ success: true, delivered, hops: nextHops, maxHops: RELAY_MAX_HOPS });
});

// Explicit broadcast endpoint
app.post('/broadcast', (req, res) => {
  const { text = '', from = 'unknown', targets, meta = {}, hops = 0 } = req.body || {};
  const nextHops = Number(hops) + 1;

  if (nextHops > RELAY_MAX_HOPS) {
    return res.status(202).json({ success: false, dropped: 'max_hops', maxHops: RELAY_MAX_HOPS });
  }

  const resolvedTargets = Array.isArray(targets) && targets.length > 0 ? targets : resolveBroadcastTargets();
  const delivered = broadcastToBots({ from, text, meta, hops: nextHops }, resolvedTargets);
  res.json({ success: true, delivered, targets: resolvedTargets, hops: nextHops, maxHops: RELAY_MAX_HOPS });
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
  console.log(`[subscribe] ${bot} connected (${clients.size} total)`);

  res.on('close', () => {
    clients.delete(bot);
    console.log(`[subscribe] ${bot} disconnected (${clients.size} total)`);
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Bot bus listening on port ${PORT}`);
  initDiscordMirror();
});
