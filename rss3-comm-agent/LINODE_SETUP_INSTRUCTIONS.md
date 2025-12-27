# Linode RSS3 Node Setup Instructions

## Objective
Configure the Linode RSS3 global indexer node to send webhook events to the Railway agent, so that Twitter and Farcaster posts are indexed and forwarded to Farcaster.

## Context
- **Railway Agent URL**: `https://ai-agents-production-b0ef.up.railway.app/api/events`
- **Railway Agent Status**: Deployed and ready to receive webhooks
- **Previous Issue**: 4GB RAM was insufficient for the RSS3 node
- **Current Setup**: Need to configure webhook endpoint in RSS3 node configuration

## Tasks

### 1. SSH into Linode Server
- Connect to the Linode instance via SSH
- Locate the RSS3 node installation directory
- Check current configuration files

### 2. Locate RSS3 Node Configuration
Look for configuration files that may contain:
- Webhook/endpoint settings
- API configuration
- Indexer settings
- Environment variables or config files (`.env`, `config.yaml`, `config.json`, etc.)

Common locations:
- `/opt/rss3/` or similar installation directory
- `~/.rss3/` configuration directory
- Project root directory if installed via git/npm

### 3. Determine Configuration Location (.env vs config.yaml/config.json)

**Check both locations:**

1. **`.env` file** - Look for environment variables like:
   - `WEBHOOK_URL`
   - `EVENT_ENDPOINT`
   - `CALLBACK_URL`
   - `RSS3_WEBHOOK_URL`
   - Or similar webhook-related environment variables

2. **`config.yaml` or `config.json`** - Look for configuration sections like:
   - `webhook:` section
   - `server:` section with `endpoint:`
   - `events:` section
   - `api:` section
   - `notifications:` or `callbacks:` section

**Decision Guide:**
- **If found in `.env`**: Add/update the environment variable
- **If found in `config.yaml/config.json`**: Update the configuration file
- **If found in both**: Update the one that's actually being used (check which takes precedence)
- **If not found**: Add to `config.yaml` (most common for RSS3 nodes)

### 4. Update Configuration

**Option A: If using `.env` file:**
```bash
# Add or update in .env file
WEBHOOK_URL=https://ai-agents-production-b0ef.up.railway.app/api/events
# OR
RSS3_WEBHOOK_URL=https://ai-agents-production-b0ef.up.railway.app/api/events
# OR
EVENT_ENDPOINT=https://ai-agents-production-b0ef.up.railway.app/api/events
```

**Option B: If using `config.yaml`:**
```yaml
webhook:
  url: https://ai-agents-production-b0ef.up.railway.app/api/events
  method: POST
  headers:
    Content-Type: application/json

# OR in server section:
server:
  endpoint: https://ai-agents-production-b0ef.up.railway.app/api/events

# OR in events section:
events:
  webhook_url: https://ai-agents-production-b0ef.up.railway.app/api/events
```

**Option C: If using `config.json`:**
```json
{
  "webhook": {
    "url": "https://ai-agents-production-b0ef.up.railway.app/api/events",
    "method": "POST"
  }
}
```

**The Railway endpoint URL to configure:**
```
https://ai-agents-production-b0ef.up.railway.app/api/events
```

**After updating:**
- If using `.env`: Restart the service (environment variables are loaded at startup)
- If using config file: Restart the service to reload configuration

### 5. Verify Railway Agent Endpoint
Before configuring, verify the Railway agent is responding:
```bash
curl https://ai-agents-production-b0ef.up.railway.app/health
```

Expected response should include:
```json
{
  "status": "healthy",
  "neynar_configured": true/false,
  "signer_configured": true/false
}
```

### 6. Test Webhook Connection
After configuration:
- Restart the RSS3 node service
- Monitor logs to ensure webhook events are being sent
- Check Railway agent logs to confirm events are being received
- Test by posting on Twitter or Farcaster and verify events flow through

### 7. Event Flow
Expected flow:
1. User posts on Twitter/Farcaster
2. RSS3 global indexer detects the activity
3. RSS3 node sends webhook to Railway agent: `POST /api/events`
4. Railway agent processes event and posts to Farcaster (if configured)
5. Event is logged and indexed

## Railway Agent Event Handling
The Railway agent (`rss3-comm-agent/index.js`) handles:
- `transfer` events (Base network NFT transfers)
- `social` events (Farcaster activity)
- `collectible` events
- All events are logged for debugging

### Expected Event Format
The agent expects POST requests to `/api/events` with JSON body containing:
```json
{
  "type": "transfer|social|collectible",
  "network": "base" (for transfers),
  "platform": "farcaster" (for social),
  "from": "address",
  "to": "address",
  "metadata": {
    "name": "...",
    "content": "..."
  },
  "action": "..." (for collectibles)
}
```

The agent will:
- Log all received events
- Process and forward to Farcaster (if configured)
- Return `200 OK` with "✅ Event received and processed"

## Important Notes
- Previous 4GB RAM issue: Ensure Linode has adequate resources (8GB+ recommended)
- The Railway agent expects POST requests with JSON body
- Content-Type header should be `application/json`
- The agent returns `200 OK` with message "✅ Event received and processed"

## Troubleshooting
- Check RSS3 node logs for webhook sending errors
- Check Railway agent logs for receiving errors
- Verify network connectivity between Linode and Railway
- Ensure Railway agent is deployed (check `/health` endpoint)
- Verify environment variables are set in Railway (NEYNAR_API_KEY, NEYNAR_SIGNER_UUID for Farcaster posting)

## Files to Check on Linode

### Configuration Files (Check these first):
1. **`.env`** - Environment variables (usually in project root or `~/.rss3/`)
2. **`config.yaml`** - YAML configuration (most common for RSS3 nodes)
3. **`config.json`** - JSON configuration
4. **`config.toml`** - TOML configuration
5. **`rss3.config.js`** or similar - JavaScript config file

### How to Identify Which File to Use:
```bash
# Check for .env file
ls -la .env ~/.rss3/.env /opt/rss3/.env

# Check for config files
ls -la config.* rss3.config.* ~/.rss3/config.* /opt/rss3/config.*

# Check service files to see which config is loaded
cat /etc/systemd/system/rss3*.service  # if using systemd
# Look for EnvironmentFile= or --config= flags
```

### Other Files to Check:
- Service files (systemd, supervisor, etc.) - may reference config location
- Log files - may show which config file is being used
- Installation documentation or README - should specify config location
- Package.json or similar - may have config paths in scripts

