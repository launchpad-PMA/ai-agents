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
// Public URL of this Railway service (Maxayauwi comm agent); override in Railway Variables if needed
const PUBLIC_AGENT_URL = process.env.PUBLIC_AGENT_URL || 'https://rss3-comm-agent-production.up.railway.app';

const NODE_ADDRESS =
  process.env.RSS3_NODE_ADDRESS || '0x0063951De34a75c25279cFe3C212F4855125Fd8f';
const RSS3_FEED_ACCOUNT = process.env.RSS3_FEED_ACCOUNT || NODE_ADDRESS;
const RSS3_NODE_PUBLIC_URL =
  process.env.RSS3_NODE_PUBLIC_URL || 'http://web3.adbongo.io:8080';
const RSS3_GLOBAL_INDEXER_URL =
  (process.env.RSS3_GLOBAL_INDEXER_URL || 'https://gi.rss3.io').replace(/\/$/, '');

const YOUTUBE_API_KEY = (process.env.YOUTUBE_API_KEY || '').trim();
const YOUTUBE_CHANNEL_ID = (process.env.YOUTUBE_CHANNEL_ID || '').trim();
const YOUTUBE_CHANNEL_URL = (process.env.YOUTUBE_CHANNEL_URL || '').trim();
const YOUTUBE_POLL_INTERVAL_MS = parseInt(process.env.YOUTUBE_POLL_INTERVAL_MS || '0', 10);

let lastAnnouncedLiveVideoId = null;

async function fetchDslActivities(account, params) {
  const path = `/decentralized/${account}`;
  try {
    return await axios.get(`${RSS3_GLOBAL_INDEXER_URL}${path}`, {
      params,
      timeout: 12000,
    });
  } catch (giError) {
    console.warn(
      '⚠️ Global Indexer unavailable, falling back to node:',
      giError.response?.status || giError.message,
    );
    return axios.get(`${RSS3_NODE_PUBLIC_URL}${path}`, {
      params,
      timeout: 12000,
    });
  }
}

async function checkYouTubeLive() {
  if (!YOUTUBE_API_KEY || !YOUTUBE_CHANNEL_ID) {
    return { configured: false, live: false };
  }

  const response = await axios.get('https://www.googleapis.com/youtube/v3/search', {
    params: {
      part: 'snippet',
      channelId: YOUTUBE_CHANNEL_ID,
      type: 'video',
      eventType: 'live',
      maxResults: 1,
      key: YOUTUBE_API_KEY,
    },
    timeout: 12000,
  });

  const item = response.data?.items?.[0];
  if (!item) {
    return { configured: true, live: false };
  }

  return {
    configured: true,
    live: true,
    videoId: item.id?.videoId,
    title: item.snippet?.title,
    url: item.id?.videoId
      ? `https://www.youtube.com/watch?v=${item.id.videoId}`
      : YOUTUBE_CHANNEL_URL || null,
  };
}

async function announceStream(liveInfo, force = false) {
  if (!liveInfo?.live || !liveInfo.url) {
    return null;
  }
  if (!force && liveInfo.videoId && liveInfo.videoId === lastAnnouncedLiveVideoId) {
    return null;
  }

  const message =
    `🔴 Live now on YouTube${liveInfo.title ? `: ${liveInfo.title}` : ''}\n${liveInfo.url}`;
  const cast = await postToFarcaster(message);
  if (cast && liveInfo.videoId) {
    lastAnnouncedLiveVideoId = liveInfo.videoId;
  }
  return cast;
}

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
    signer_configured: !!NEYNAR_SIGNER_UUID,
    youtube_configured: !!(YOUTUBE_API_KEY && YOUTUBE_CHANNEL_ID),
    global_indexer_url: RSS3_GLOBAL_INDEXER_URL,
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
  
  // Build query params object, only include if they have valid values
  const params = {};
  
  // Validate and parse action_limit (must be 1-100)
  if (req.query.action_limit) {
    const action_limit = parseInt(req.query.action_limit);
    if (!isNaN(action_limit) && action_limit >= 1 && action_limit <= 100) {
      params.action_limit = action_limit;
    }
  }
  
  // Validate and parse action_page (must be >= 1)
  if (req.query.action_page) {
    const action_page = parseInt(req.query.action_page);
    if (!isNaN(action_page) && action_page >= 1) {
      params.action_page = action_page;
    }
  }
  
  try {
    let response;
    try {
      response = await axios.get(`${RSS3_GLOBAL_INDEXER_URL}/decentralized/tx/${id}`, {
        params,
        timeout: 12000,
      });
    } catch (giError) {
      response = await axios.get(`${RSS3_NODE_PUBLIC_URL}/decentralized/tx/${id}`, {
        params,
        timeout: 12000,
      });
    }

    res.json(response.data);
  } catch (error) {
    console.error('❌ Failed to fetch RSS3 activity:', error.response?.data || error.message);
    res.status(error.response?.status || 500).json({ 
      error: error.response?.data || error.message 
    });
  }
});

// JSON for Adbongo landing (social URLs, node links)
app.get('/api/site-config', (req, res) => {
  const explorerUrl = `https://explorer.rss3.io/nodes/${NODE_ADDRESS}`;
  res.json({
    brand: 'Adbongo',
    tagline:
      'Nearly twenty years of consulting across industries. We help founders and operators upgrade the legal, social, financial, and technical layers of their organizations—especially digital and decentralized ones.',
    /** Public site hostname (static landing + same host as RSS3 stack on Linode) */
    marketingSiteUrl: (process.env.ADBONGO_SITE_URL || 'https://web3.adbongo.io').trim(),
    nodeAddress: NODE_ADDRESS,
    explorerNodeUrl: explorerUrl,
    rss3NodeUrl: RSS3_NODE_PUBLIC_URL,
    commAgentUrl: PUBLIC_AGENT_URL,
    feedAccount: RSS3_FEED_ACCOUNT,
    social: {
      farcaster: (process.env.SOCIAL_FARCASTER_URL || '').trim(),
      warpcast: (process.env.SOCIAL_WARPCAST_URL || '').trim(),
      x: (process.env.SOCIAL_X_URL || '').trim(),
      youtube: YOUTUBE_CHANNEL_URL,
    },
    streaming: {
      youtubeConfigured: !!(YOUTUBE_API_KEY && YOUTUBE_CHANNEL_ID),
      youtubeChannelId: YOUTUBE_CHANNEL_ID || null,
    },
    rss3: {
      globalIndexerUrl: RSS3_GLOBAL_INDEXER_URL,
      nodeUrl: RSS3_NODE_PUBLIC_URL,
    },
    contactHref: (process.env.ADBONGO_CONTACT_HREF || 'mailto:adbongorocks@gmail.com').trim(),
    podcast: {
      title: 'Golden Age Gurus ✨',
      spotifyUrl: (process.env.PODCAST_SPOTIFY_URL || 'https://open.spotify.com/show/003jiO8jmRfAk3GrKPy8C7').trim(),
      appleUrl: (process.env.PODCAST_APPLE_URL || 'https://podcasts.apple.com/us/podcast/golden-age-gurus/id1591599337').trim(),
      siteUrl: (process.env.PODCAST_SITE_URL || 'https://www.adbongo.io/podcast').trim(),
      rssUrl: (process.env.PODCAST_RSS_URL || 'https://api.substack.com/feed/podcast/587547.rss').trim(),
    },
  });
});

// RSS3 Global Indexer: activities for configured account (feed on landing page)
app.get('/api/rss3/feed', async (req, res) => {
  const limit = Math.min(
    100,
    Math.max(1, parseInt(String(req.query.limit || '24'), 10) || 24),
  );
  const params = { limit, action_limit: 8 };
  if (req.query.cursor) {
    params.cursor = String(req.query.cursor);
  }
  if (req.query.tag) {
    params.tag = String(req.query.tag);
  }
  if (req.query.platform) {
    params.platform = String(req.query.platform);
  }
  try {
    const response = await fetchDslActivities(RSS3_FEED_ACCOUNT, params);
    res.json({
      ...response.data,
      meta: {
        ...(response.data?.meta || {}),
        source: response.config?.url?.includes(RSS3_GLOBAL_INDEXER_URL)
          ? 'global_indexer'
          : 'node',
      },
    });
  } catch (error) {
    console.error('❌ RSS3 feed proxy:', error.response?.data || error.message);
    res.status(error.response?.status || 502).json({
      data: [],
      meta: { source: 'none' },
      error:
        error.response?.data?.message ||
        error.response?.data ||
        error.message ||
        'Feed unavailable (Global Indexer and node both unreachable)',
    });
  }
});

// YouTube live status (for stream overlays / manual checks)
app.get('/api/youtube/status', async (req, res) => {
  try {
    const status = await checkYouTubeLive();
    res.json(status);
  } catch (error) {
    res.status(502).json({
      configured: !!(YOUTUBE_API_KEY && YOUTUBE_CHANNEL_ID),
      live: false,
      error: error.response?.data || error.message,
    });
  }
});

// Announce current YouTube live stream to Farcaster (POST body: { force: true } to re-post)
app.post('/api/youtube/announce', async (req, res) => {
  try {
    const live = await checkYouTubeLive();
    if (!live.configured) {
      return res.status(503).json({
        error: 'Set YOUTUBE_API_KEY and YOUTUBE_CHANNEL_ID on Railway',
      });
    }
    if (!live.live) {
      return res.status(404).json({ error: 'No live stream detected', live });
    }
    const cast = await announceStream(live, !!req.body?.force);
    res.json({ success: !!cast, live, cast });
  } catch (error) {
    res.status(502).json({ error: error.response?.data || error.message });
  }
});

// Maxayauwi / node ops dashboard (was previously at /)
app.get('/node', (req, res) => {
  const nodeAddress = NODE_ADDRESS;
  const nodeEndpoint = RSS3_NODE_PUBLIC_URL;
  const commAgentUrl = PUBLIC_AGENT_URL;
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
            <p style="text-align:center;margin-bottom:20px"><a href="/" class="link">← Adbongo home</a></p>
            <div class="section">
                <h2>📍 Node Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>Node Address</h3>
                        <p>${nodeAddress}</p>
                        <a href="${explorerUrl}" target="_blank" class="link">View on RSS3 Explorer →</a>
                    </div>
                    <div class="info-card">
                        <h3>RSS3 node (Linode)</h3>
                        <p>${nodeEndpoint}</p>
                        <span class="status-badge status-online">🟢 Online</span>
                    </div>
                    <div class="info-card">
                        <h3>Comm agent (this service)</h3>
                        <p>${commAgentUrl}</p>
                        <p style="margin-top: 8px; font-size: 0.85em;">Webhooks: <code>/api/events</code></p>
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

app.use(express.static('public'));

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Maxayauwi RSS3 + Farcaster agent listening on port ${PORT}`);
  console.log(`📡 Neynar configured: ${!!NEYNAR_API_KEY}`);
  console.log(`🔐 Signer configured: ${!!NEYNAR_SIGNER_UUID}`);
  console.log(`📺 YouTube configured: ${!!(YOUTUBE_API_KEY && YOUTUBE_CHANNEL_ID)}`);
  console.log(`🌐 Global Indexer: ${RSS3_GLOBAL_INDEXER_URL}`);

  if (YOUTUBE_POLL_INTERVAL_MS > 0 && YOUTUBE_API_KEY && YOUTUBE_CHANNEL_ID) {
    setInterval(async () => {
      try {
        const live = await checkYouTubeLive();
        if (live.live) {
          await announceStream(live);
        } else {
          lastAnnouncedLiveVideoId = null;
        }
      } catch (error) {
        console.error('❌ YouTube poll error:', error.message);
      }
    }, YOUTUBE_POLL_INTERVAL_MS);
    console.log(`⏱️ YouTube live poll every ${YOUTUBE_POLL_INTERVAL_MS}ms`);
  }
});
