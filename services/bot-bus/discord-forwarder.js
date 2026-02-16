import fetch from 'node-fetch';

export async function forwardToDiscord(message, options = {}) {
  const webhookUrl = process.env.DISCORD_WEBHOOK_URL;

  if (!webhookUrl) {
    console.log('[discord] No webhook URL configured, skipping');
    return;
  }

  const payload = {
    content: message,
    username: 'Bot Bus',
  };

  if (Array.isArray(options.mentionUserIds) && options.mentionUserIds.length > 0) {
    payload.allowed_mentions = {
      users: options.mentionUserIds,
      parse: [],
    };
  }

  try {
    await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.error('[discord] Forward failed:', err.message);
  }
}
