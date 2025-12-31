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

// RSS3 DSL API: Get activity by ID
app.get('/api/rss3/activity/:id', async (req, res) => {
  const { id } = req.params;
  const { action_limit = 50, action_page = 1 } = req.query;
  
  try {
    const response = await axios.get(`https://gi.rss3.io/decentralized/tx/${id}`, {
      params: {
        action_limit: parseInt(action_limit),
        action_page: parseInt(action_page)
      }
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('❌ Failed to fetch RSS3 activity:', error.response?.data || error.message);
    res.status(error.response?.status || 500).json({ 
      error: error.response?.data || error.message 
    });
  }
});

// Serve static files
app.use(express.static('public'));

// Root endpoint - serve website
app.get('/', (req, res) => {
  const nodeAddress = '0x0063951De34a75c25279cFe3C212F4855125Fd8f';
  const nodeEndpoint = 'http://web3.adbongo.io:8080';
  const explorerUrl = `https://explorer.rss3.io/nodes/${nodeAddress}`;
  
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maxayauwi RSS3 Node - DAO Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .info-card {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .info-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .info-card p {
            color: #666;
            word-break: break-all;
            font-family: 'Courier New', monospace;
        }
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }
        .status-online {
            background: #d4edda;
            color: #155724;
        }
        .link {
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }
        .link:hover {
            text-decoration: underline;
        }
        .dao-info {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .dao-info h3 {
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Maxayauwi RSS3 Node</h1>
            <p>DAO Communication Agent & RSS3 Data Sublayer Node</p>
        </div>
        <div class="content">
            <div class="section">
                <h2>📍 Node Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>Node Address</h3>
                        <p>${nodeAddress}</p>
                        <a href="${explorerUrl}" target="_blank" class="link">View on RSS3 Explorer →</a>
                    </div>
                    <div class="info-card">
                        <h3>Endpoint</h3>
                        <p>${nodeEndpoint}</p>
                        <span class="status-badge status-online">🟢 Online</span>
                    </div>
                    <div class="info-card">
                        <h3>Status</h3>
                        <p>Operational</p>
                        <p style="margin-top: 10px; font-size: 0.9em;">Connected to RSS3 Global Indexer</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🏛️ DAO Information</h2>
                <div class="dao-info">
                    <h3>Maxayauwi Communication Agent</h3>
                    <p style="margin-bottom: 15px;">This node serves as the communication agent for the Maxayauwi DAO, processing RSS3 events and routing messages to Farcaster.</p>
                    <p><strong>Features:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>RSS3 Event Processing</li>
                        <li>Farcaster Integration</li>
                        <li>Real-time Activity Indexing</li>
                        <li>DAO Communication Hub</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2>🔗 Quick Links</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>Node Explorer</h3>
                        <a href="${explorerUrl}" target="_blank" class="link">View Node on RSS3 Explorer</a>
                    </div>
                    <div class="info-card">
                        <h3>API Endpoints</h3>
                        <p><a href="/health" class="link">Health Check</a></p>
                        <p><a href="/api/v1/health" class="link">AI Component Health</a></p>
                    </div>
                    <div class="info-card">
                        <h3>Documentation</h3>
                        <a href="https://docs.rss3.io" target="_blank" class="link">RSS3 Documentation</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
  `);
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Maxayauwi RSS3 + Farcaster agent listening on port ${PORT}`);
  console.log(`📡 Neynar configured: ${!!NEYNAR_API_KEY}`);
  console.log(`🔐 Signer configured: ${!!NEYNAR_SIGNER_UUID}`);
});
