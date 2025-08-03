require('dotenv').config();
const express = require('express');
const { TwitterApi } = require('twitter-api-v2');

const app = express();
app.use(express.json());

// Setup Twitter client using env secrets
const twitter = new TwitterApi({
  appKey: process.env.TWITTER_API_KEY,
  appSecret: process.env.TWITTER_API_SECRET,
  accessToken: process.env.TWITTER_ACCESS_TOKEN,
  accessSecret: process.env.TWITTER_ACCESS_SECRET,
});

// Webhook endpoint
app.post('/api/events', async (req, res) => {
  const { agent, message } = req.body;

  try {
    const { data } = await twitter.v2.tweet(`[${agent}] says: ${message}`);
    res.json({ status: 'success', tweet: data });
  } catch (err) {
    console.error('❌ Twitter Error:', err);
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// Start the agent
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`✅ Agent is live on port ${PORT}`);
});

