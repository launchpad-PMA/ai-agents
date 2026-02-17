# Deployment Architecture

This project uses a multi-deployment strategy to separate concerns and optimize for different use cases.

## Overview

- **Vercel**: Hosts the Farcaster-specific functionality (RSS3 + Farcaster integration)
- **Railway**: Hosts the entire agent system including all components

## Components

### 1. Twitter Agent (Root)
- **Location**: `/index.js`
- **Purpose**: Posts to Twitter using OAuth 1.0a
- **Deployed to**: Railway only

### 2. RSS3 + Farcaster Agent
- **Location**: `/rss3-comm-agent/`
- **Purpose**: 
  - Receives RSS3 event webhooks
  - Posts to Farcaster via Neynar API
  - Provides Farcaster user lookup
- **Deployed to**: Both Vercel (standalone) and Railway (as part of system)

### 3. Other Agents
- **Covenant Keeper**: `/covenant-keeper/` (future implementation)
- **Divine Cleric**: `/divine-cleric/` (future implementation)
- **Post NFT**: `/post-nft/` (future implementation)

## Deployment Instructions

### Vercel Deployment (Farcaster Only)

1. Connect your GitHub repository to Vercel
2. The `vercel.json` is already configured to deploy the RSS3/Farcaster agent
3. Add these environment variables in Vercel dashboard:
   - `NEYNAR_API_KEY`
   - `NEYNAR_SIGNER_UUID`

### Railway Deployment (Complete System)

1. Connect your GitHub repository to Railway
2. The `railway.json` is configured for the main deployment
3. Add these environment variables in Railway dashboard:
   - All Twitter API credentials (see `.env.example`)
   - All Neynar/Farcaster credentials
   - Any additional agent-specific credentials

## Environment Variables

See `.env.example` for all required environment variables.

## API Endpoints

### Farcaster Agent (Vercel)
- `POST /api/events` - RSS3 webhook endpoint
- `POST /api/farcaster/cast` - Manual Farcaster posting
- `GET /api/farcaster/user/:fid` - Farcaster user lookup
- `GET /health` - Health check

### Twitter Agent (Railway)
- `POST /api/events` - Twitter posting endpoint
- `GET /health` - Health check

## Notes

- The Farcaster functionality is isolated on Vercel for optimal performance and scaling
- Railway hosts the complete system for comprehensive agent capabilities
- Both deployments can operate independently