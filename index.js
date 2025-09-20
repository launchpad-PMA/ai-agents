require('dotenv').config();
const express = require('express');
const { TwitterApi } = require('twitter-api-v2');

const app = express();
app.use(express.json());

// ---- Require OAuth 1.0a user context (tweet now) ----
function need(name) {
  const v = process.env[name];
  if (!v || !v.trim()) throw new Error(`Missing env: ${name}`);
  return v.trim();
}

const twitter = new TwitterApi({
  appKey:     need('TWITTER_API_KEY'),
  appSecret:  need('TWITTER_API_SECRET'),
  accessToken: need('TWITTER_ACCESS_TOKEN'),
  accessSecret: need('TWITTER_ACCESS_SECRET'),
}).readWrite;

app.get('/health', (_req, res) => res.json({ ok: true, mode: 'oauth1a-user' }));

app.post('/api/events', async (req, res) => {
  try {
    const { agent = 'maxayauwi', message } = req.body || {};
    if (!message) return res.status(400).json({ status: 'error', message: 'message is required' });

    const { data } = await twitter.v2.tweet(`[${agent}] says: ${message}`);
    return res.json({ status: 'success', tweet: data });
  } catch (err) {
    const api = err?.data || err?.response?.data;
    console.error('❌ Twitter post failed:', api ?? err);
    return res.status(500).json({
      status: 'error',
      message: api?.title || err.message || 'unknown error',
      detail: api || undefined
    });
  }
});

// ---- Placeholders for OAuth 2.0 (later) ----
// Add TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET, TWITTER_REDIRECT_URI
// and we’ll wire /api/twitter/auth + /api/twitter/callback when ready.

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`✅ Agent listening on ${PORT}`));

