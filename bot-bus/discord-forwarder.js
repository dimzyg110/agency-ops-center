import fetch from 'node-fetch';

export async function forwardToDiscord(message) {
  const webhookUrl = process.env.DISCORD_WEBHOOK_URL;
  
  if (!webhookUrl) {
    console.log('[discord] No webhook URL configured, skipping');
    return;
  }
  
  try {
    await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: message,
        username: 'Bot Bus',
      }),
    });
  } catch (err) {
    console.error('[discord] Forward failed:', err.message);
  }
}
