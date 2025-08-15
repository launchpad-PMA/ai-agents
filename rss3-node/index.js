const express = require('express');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

// Health check for Railway
app.get('/healthz', (_req, res) => {
  res.status(200).send('OK');
});

// Optional: root
app.get('/', (_req, res) => {
  res.status(200).send('RSS3 Node is running');
});

// RSS3 webhook endpoint
app.post('/api/events', (req, res) => {
  const event = req.body;
  console.log('📨 Received RSS3 event:', JSON.stringify(event, null, 2));
  res.status(200).send('✅ Event received');
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ RSS3 Node listening on ${PORT}`);
});