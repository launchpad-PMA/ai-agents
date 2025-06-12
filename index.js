const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

app.post('/api/events', (req, res) => {
  const event = req.body;

  console.log('🔔 New RSS3 Event Received:', event);

  // TODO: Route logic to Lens/Farcaster/X/Substack

  res.status(200).send({ status: 'received', agent: 'Maxayauwi' });
});

app.get('/', (req, res) => {
  res.send('🦌 Maxayauwi Comm Agent listening...');
});

app.listen(PORT, () => {
  console.log(`🟢 Maxayauwi live on port ${PORT}`);
});
