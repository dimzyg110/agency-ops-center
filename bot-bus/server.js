import express from 'express';
import { forwardToDiscord } from './discord-forwarder.js';

const app = express();
app.use(express.json());

// In-memory message store for SSE
const clients = new Map();

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Relay endpoint - receive message from a bot and distribute
app.post('/relay', async (req, res) => {
  const { text, from, to, channelId } = req.body;
  
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
});
