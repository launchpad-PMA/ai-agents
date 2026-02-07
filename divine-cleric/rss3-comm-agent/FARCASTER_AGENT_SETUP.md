# Farcaster Agent Setup Instructions

## Overview
This document provides instructions for setting up a separate Farcaster agent/service to work with the RSS3 node infrastructure.

## Two Separate Farcaster Systems

### 1. RSS3 Node Farcaster Worker (DSL Node)
- **Purpose**: Indexes Farcaster network data for the RSS3 network
- **Status**: Currently unhealthy (requires Farcaster Hub)
- **Location**: RSS3 DSL Node on Linode server

### 2. Separate Farcaster Agent (Your Service)
- **Purpose**: Receives RSS3 events and posts to Farcaster via Neynar
- **Status**: Should be configured with Neynar API
- **Location**: Your separate agent/service

## What the Separate Farcaster Agent Needs

### Neynar API Configuration

The separate Farcaster agent needs these Neynar credentials:

1. **Neynar API Key**
   - Get from: https://neynar.com
   - Used for: API authentication to interact with Farcaster

2. **Neynar Signer UUID**
   - Get from: https://neynar.com (create a signer)
   - Used for: Posting casts to Farcaster on behalf of the agent

### Environment Variables Needed

```env
NEYNAR_API_KEY=your_neynar_api_key_here
NEYNAR_SIGNER_UUID=your_neynar_signer_uuid_here
```

### Neynar API Endpoints to Use

- **Base URL**: `https://api.neynar.com/v2/farcaster`
- **Post Cast**: `POST /cast`
- **Get User**: `GET /user/by_fid/{fid}`

### Example Configuration

The agent should be configured to:
1. Receive webhooks/events from RSS3 node or other sources
2. Use Neynar API to post casts to Farcaster
3. Use Neynar API to look up Farcaster user information

## RSS3 Node Farcaster Worker Setup (If Needed)

If you want the RSS3 node's Farcaster worker to work, you need:

### Farcaster Hub

The RSS3 node Farcaster worker requires a Farcaster Hub to be running. This is different from your agent.

**Current Configuration:**
```yaml
endpoints:
  farcaster:
    url: http://172.232.129.170:3001  # Requires Farcaster Hub running here
```

**To Get It Working:**
1. Deploy a Farcaster Hub instance
2. Make it accessible at the configured endpoint
3. Update the URL in `config.yaml` if needed
4. Restart RSS3 node services

**Note**: This is OPTIONAL - the RSS3 node Farcaster worker is not required for:
- Your separate Farcaster agent to work
- Earning RSS3 rewards (Ethereum worker is primary)
- Processing and posting Farcaster events via your agent

## Recommended Setup

### For Your Separate Farcaster Agent:

✅ **Required:**
- Neynar API Key
- Neynar Signer UUID
- Ability to receive events (webhooks, API calls, etc.)
- Code to post to Farcaster via Neynar API

❌ **NOT Required:**
- Farcaster Hub (only needed for RSS3 node worker)
- RSS3 node Farcaster worker (optional for indexing)

### Integration Points

Your separate Farcaster agent can:
1. **Receive RSS3 Events**: 
   - Via webhooks from RSS3 node (if configured)
   - Via API calls to RSS3 Global Indexer
   - Via direct database queries (if shared database)

2. **Post to Farcaster**:
   - Use Neynar API to post casts
   - Format messages based on RSS3 event data
   - Handle Farcaster-specific formatting

## Neynar Setup Steps

1. **Create Neynar Account**
   - Go to https://neynar.com
   - Sign up for an account

2. **Get API Key**
   - Navigate to API keys section
   - Generate a new API key
   - Save it securely

3. **Create Signer**
   - In Neynar dashboard, create a new signer
   - This generates a Signer UUID
   - The signer allows posting casts

4. **Configure Agent**
   - Add `NEYNAR_API_KEY` environment variable
   - Add `NEYNAR_SIGNER_UUID` environment variable
   - Implement Neynar API client in your code

## Current Setup Status

**RSS3 Node:**
- ✅ Ethereum worker: Indexing successfully
- ⚠️ Farcaster worker: Unhealthy (needs Hub - optional)

**Your Separate Agent:**
- Should have Neynar credentials configured
- Can post to Farcaster independently
- Does NOT require RSS3 node Farcaster worker to function

## Key Points to Remember

1. **Your Farcaster agent is independent** - it doesn't need the RSS3 node Farcaster worker
2. **Neynar is for posting** - you need API key + Signer UUID
3. **Farcaster Hub is only for RSS3 node worker** - optional for your use case
4. **RSS3 node Farcaster worker is optional** - Ethereum indexing is what matters for rewards

## Questions to Ask the Other Agent Developer

1. Do you have Neynar API credentials?
2. Do you need help setting up Neynar signer?
3. How will the agent receive RSS3 events? (webhook, API, database?)
4. What's the endpoint/URL where the agent is running?
5. Do you need access to the RSS3 node webhook configuration?

