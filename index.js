require('dotenv').config();
const express = require('express');
const { TwitterApi } = require('twitter-api-v2');
const axios = require('axios');

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

// Neynar API setup
const NEYNAR_API_KEY = process.env.NEYNAR_API_KEY;
const NEYNAR_API_URL = 'https://api.neynar.com/v2/farcaster';

app.get('/health', (_req, res) => res.json({ ok: true, mode: 'oauth1a-user' }));

app.post('/api/events', async (req, res) => {
  try {
    const { agent = 'maxayauwi', message, platforms = ['twitter'] } = req.body || {};
    if (!message) return res.status(400).json({ status: 'error', message: 'message is required' });

    const results = {};
    const formattedMessage = `[${agent}] says: ${message}`;

    // Post to Twitter if requested
    if (platforms.includes('twitter')) {
      try {
        const { data } = await twitter.v2.tweet(formattedMessage);
        results.twitter = { status: 'success', tweet: data };
      } catch (err) {
        const api = err?.data || err?.response?.data;
        console.error('❌ Twitter post failed:', api ?? err);
        results.twitter = { 
          status: 'error', 
          message: api?.title || err.message || 'Twitter post failed' 
        };
      }
    }

    // Post to Farcaster if requested and configured
    if (platforms.includes('farcaster') && NEYNAR_API_KEY && process.env.NEYNAR_SIGNER_UUID) {
      try {
        const response = await axios.post(`${NEYNAR_API_URL}/cast`, {
          text: formattedMessage,
          signer_uuid: process.env.NEYNAR_SIGNER_UUID
        }, {
          headers: {
            'Content-Type': 'application/json',
            'api_key': NEYNAR_API_KEY
          }
        });
        results.farcaster = { status: 'success', cast: response.data };
      } catch (err) {
        console.error('❌ Farcaster post failed:', err.response?.data || err.message);
        results.farcaster = { 
          status: 'error', 
          message: err.response?.data?.message || 'Farcaster post failed' 
        };
      }
    }

    return res.json({ status: 'success', results });
  } catch (err) {
    console.error('❌ General error:', err);
    return res.status(500).json({
      status: 'error',
      message: err.message || 'unknown error'
    });
  }
});

// ---- Placeholders for OAuth 2.0 (later) ----
// Add TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET, TWITTER_REDIRECT_URI
// and we’ll wire /api/twitter/auth + /api/twitter/callback when ready.

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`✅ Agent listening on ${PORT}`));

