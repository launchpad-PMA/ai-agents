const express = require('express');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());

// Webhook endpoint
app.post('/api/events', (req, res) => {
  const event = req.body;

  console.log('📨 Received RSS3 event:', JSON.stringify(event, null, 2));

  // TODO: Add routing logic, NFT lookup, Farcaster posting, etc.

  res.status(200).send('✅ Event received');
});

// Root endpoint
app.get('/', (req, res) => {
  res.send('🧠 Maxayauwi RSS3 Comm Agent is running');
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Maxayauwi agent listening on port ${PORT}`);
});
