# Farcaster Integration Setup

## Overview
The RSS3 node includes a Farcaster worker that indexes Farcaster network activity. This document describes the Farcaster setup and integration with the AI agent.

## Current Status

### RSS3 Node Farcaster Worker
- **Status**: Unhealthy (Farcaster Hub not running)
- **Worker ID**: `farcaster-core`
- **Network**: farcaster
- **Endpoint Required**: Farcaster Hub API endpoint

The RSS3 node Farcaster worker requires a Farcaster Hub to be running and accessible. Currently, the worker is configured but cannot connect because:
- The Farcaster Hub endpoint in config is: `http://172.232.129.170:3001` (private IP)
- No Farcaster Hub service is currently running on the server

### Separate Farcaster Agent
We have a separate AI agent specifically for Farcaster operations that handles:
- Receiving RSS3 events related to Farcaster activity
- Posting to Farcaster via Neynar API
- Processing social activity events

This agent is separate from the RSS3 node Farcaster worker and runs independently.

## Configuration

### RSS3 Node Config
The RSS3 node `config.yaml` includes endpoints for Farcaster (if needed):
```yaml
endpoints:
  farcaster:
    url: http://172.232.129.170:3001  # Requires Farcaster Hub
```

### AI Agent Integration
The AI agent (Railway) receives webhooks from the RSS3 node for Farcaster events:
- Webhook endpoint: `/api/events`
- Processes events with `type: 'social'` and `platform: 'farcaster'`
- Uses Neynar API for Farcaster interactions

## Future Setup (If Needed)

To enable Farcaster indexing in the RSS3 node:

1. **Deploy Farcaster Hub**
   - Run a Farcaster Hub instance
   - Make it accessible to the RSS3 node
   - Update `config.yaml` endpoints.farcaster.url

2. **Update Configuration**
   - Ensure the endpoint is publicly accessible or on the same network
   - Restart RSS3 node services after configuration changes

3. **Verify Worker Status**
   - Check `/operators/workers_status` endpoint
   - Worker should show "Indexing" status when healthy

## Notes
- The separate Farcaster agent can operate independently of the RSS3 node Farcaster worker
- The RSS3 node Farcaster worker is optional for earning RSS3 rewards (Ethereum indexing is the primary focus)
- Current priority: Keep Ethereum worker indexing successfully (currently working ✅)

