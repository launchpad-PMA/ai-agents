# RSS3 Workers Guide

## What is a Worker?

A **worker** is the most basic unit of an RSS3 Node that includes a set of logics to:
- Index Open Information from Open Data Protocols (ODP)
- Structure the indexed information using rule-based interpretation
- Store the structured data in the Node's database

According to the [RSS3 Worker Documentation](https://docs.rss3.io/guide/dsl/worker), workers are the core components that enable nodes to process and serve open information.

## Worker Workflow

A worker follows this simple workflow:

1. **Monitor**: Continuously monitors a specific Open Data Protocol (ODP)
   - Access to ODP is configured in the Node's `config.yaml`

2. **Index**: Indexes Open Information from the ODP when there is an update

3. **Structure**: Follows rule-based interpretation to structure the indexed information

4. **Store**: Stores the structured data in the Node's database

## Our Current Workers

### Ethereum Core Worker
- **Worker ID**: `ethereum-core`
- **Network**: ethereum
- **Status**: ✅ **Indexing** (Healthy)
- **Indexed State**: 21,529,339+ blocks
- **Index Count**: 467,325+ activities
- **Coverage**: All Ethereum data except data covered by specialized workers (uniswap, aave, etc.)

### Farcaster Core Worker
- **Worker ID**: `farcaster-core`
- **Network**: farcaster
- **Status**: ⚠️ **Unhealthy**
- **Issue**: Cannot connect to Farcaster Hub (not running)
- **Note**: This worker requires a Farcaster Hub instance to be operational

### Core Worker Behavior
The **core** worker covers all data on the open data protocol where it operates, **except** for data already covered by specialized workers. This means:
- `ethereum-core` indexes general Ethereum transactions
- Specialized workers (uniswap, aave, etc.) handle their specific protocols
- Core worker fills in the gaps for uncovered data

## Available Workers

RSS3 supports many workers across different networks. Here are some key ones:

### Supported Networks
- **Ethereum**: 21 workers (including core, uniswap, aave, curve, opensea, etc.)
- **Base**: 11 workers
- **Polygon**: 14 workers
- **Arbitrum**: 12 workers
- **Optimism**: 13 workers
- **Farcaster**: 1 worker (core)
- **And many more...**

### Worker Types
1. **Core Workers**: Cover general data for a network
2. **Specialized Workers**: Handle specific protocols (e.g., uniswap, aave, opensea)

## Worker Status Monitoring

You can check worker status via:
```bash
curl http://web3.adbongo.io:8080/operators/workers_status
```

This returns:
- Worker ID and network
- Status (Indexing, Unhealthy, etc.)
- Remote state (block height or timestamp)
- Indexed state (what the worker has processed)
- Index count (number of activities indexed)

## Adding New Workers

Workers are community-maintained. If you need a worker that doesn't exist:
1. Fork the RSS3 Node repository
2. Submit pull requests for contributions
3. See the [Contributing a New Worker guide](https://docs.rss3.io/guide/dsl/worker/contributing)

## Configuration

Workers are configured in `config.yaml`. Key settings include:
- Network endpoints (RPC URLs, API endpoints)
- Worker-specific parameters
- Database connections
- Coverage periods

## How Workers Impact Rewards

Workers directly impact your node's rewards through:

1. **Work Rate**: More workers = more indexing activity = higher work rate
2. **Coverage**: Workers index data that can be served to users
3. **Request Processing**: When request fees are implemented, workers process queries and earn fees
4. **Network Rewards**: Work rate (which includes worker activity) impacts final network rewards

## Current Status Summary

✅ **Ethereum Core Worker**: Healthy and actively indexing
- This is your primary worker for earning RSS3 rewards
- Processing Ethereum transactions and activities successfully

⚠️ **Farcaster Core Worker**: Unhealthy
- Not critical for current rewards (Ethereum is primary)
- Requires Farcaster Hub to be deployed if you want it active
- Can be addressed later if needed

## Documentation Reference
- [RSS3 Worker Documentation](https://docs.rss3.io/guide/dsl/worker)
- [Contributing a New Worker](https://docs.rss3.io/guide/dsl/worker/contributing)

