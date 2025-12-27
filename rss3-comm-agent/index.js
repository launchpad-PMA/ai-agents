const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());

// Neynar API configuration
const NEYNAR_API_KEY = process.env.NEYNAR_API_KEY;
const NEYNAR_API_URL = 'https://api.neynar.com/v2/farcaster';
const NEYNAR_SIGNER_UUID = process.env.NEYNAR_SIGNER_UUID;

// Helper function to post to Farcaster
async function postToFarcaster(message) {
  if (!NEYNAR_API_KEY || !NEYNAR_SIGNER_UUID) {
    console.log('⚠️ Neynar not configured, skipping Farcaster post');
    return null;
  }

  try {
    const response = await axios.post(`${NEYNAR_API_URL}/cast`, {
      text: message,
      signer_uuid: NEYNAR_SIGNER_UUID
    }, {
      headers: {
        'Content-Type': 'application/json',
        'api_key': NEYNAR_API_KEY
      }
    });
    
    console.log('✅ Posted to Farcaster:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to post to Farcaster:', error.response?.data || error.message);
    return null;
  }
}

// Helper function to get Neynar user info
async function getNeynarUser(fid) {
  if (!NEYNAR_API_KEY) {
    return null;
  }

  try {
    const response = await axios.get(`${NEYNAR_API_URL}/user/bulk?fids=${fid}`, {
      headers: {
        'api_key': NEYNAR_API_KEY
      }
    });
    return response.data.users[0] || null;
  } catch (error) {
    console.error('❌ Failed to get Neynar user:', error.response?.data || error.message);
    return null;
  }
}

// RSS3 webhook endpoint
app.post('/api/events', async (req, res) => {
  const event = req.body;

  console.log('📨 Received RSS3 event:', JSON.stringify(event, null, 2));

  // Process different types of RSS3 events
  try {
    if (event.type === 'transfer' && event.network === 'base') {
      // NFT transfer event
      const message = `🔄 NFT Transfer detected!\n` +
                     `Token: ${event.metadata?.name || 'Unknown NFT'}\n` +
                     `From: ${event.from}\n` +
                     `To: ${event.to}\n` +
                     `Network: Base`;
      
      await postToFarcaster(message);
    } 
    else if (event.type === 'social' && event.platform === 'farcaster') {
      // Farcaster activity event
      const message = `📱 Farcaster Activity:\n${event.metadata?.content || 'New activity detected'}`;
      console.log('📱 Farcaster event processed:', message);
    }
    else if (event.type === 'collectible') {
      // General collectible event
      const message = `🎨 Collectible Activity:\n` +
                     `Action: ${event.action}\n` +
                     `Item: ${event.metadata?.name || 'Unknown Item'}`;
      
      await postToFarcaster(message);
    }
    else {
      console.log('📝 Unhandled event type:', event.type);
    }

  } catch (error) {
    console.error('❌ Error processing RSS3 event:', error);
  }

  res.status(200).send('✅ Event received and processed');
});

// Farcaster user lookup endpoint
app.get('/api/farcaster/user/:fid', async (req, res) => {
  const { fid } = req.params;
  
  try {
    const user = await getNeynarUser(parseInt(fid));
    if (user) {
      res.json(user);
    } else {
      res.status(404).json({ error: 'User not found' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Manual Farcaster post endpoint
app.post('/api/farcaster/cast', async (req, res) => {
  const { message } = req.body;
  
  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  try {
    const result = await postToFarcaster(message);
    if (result) {
      res.json({ success: true, cast: result });
    } else {
      res.status(500).json({ error: 'Failed to post to Farcaster' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    neynar_configured: !!NEYNAR_API_KEY,
    signer_configured: !!NEYNAR_SIGNER_UUID
  });
});

// RSS3 AI component health endpoint (required by RSS3 node)
app.get('/api/v1/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    neynar_configured: !!NEYNAR_API_KEY,
    signer_configured: !!NEYNAR_SIGNER_UUID
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.send('🧠 Maxayauwi RSS3 + Farcaster Comm Agent is running');
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Maxayauwi RSS3 + Farcaster agent listening on port ${PORT}`);
  console.log(`📡 Neynar configured: ${!!NEYNAR_API_KEY}`);
  console.log(`🔐 Signer configured: ${!!NEYNAR_SIGNER_UUID}`);
});
