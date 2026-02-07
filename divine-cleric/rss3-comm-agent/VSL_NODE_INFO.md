# VSL (Value Sublayer) RPC Node

## What is VSL?
The VSL (Value Sublayer) RPC Node is a component of the RSS3 network that handles value-related operations and provides RPC access to the RSS3 Value Sublayer.

## Important Architecture Clarification

### How Global Indexer Works with VSL vs DSL Nodes

**Key Distinction:**
- **Global Indexer (GI)** itself interacts with VSL - it's a centralized service run by RSS3
- **DSL Nodes** (like ours) communicate with the Global Indexer, NOT directly with VSL
- **VSL RPC Nodes** are separate infrastructure - you run them if you want to provide VSL RPC services to others

**How GI Indexes DSL Nodes:**
- The Global Indexer's core functions (monitoring nodes, enforcing rules, structuring activities) focus on the Data Sublayer
- GI monitors DSL nodes by checking their `/operators` endpoint and worker status
- GI can index and coordinate among DSL nodes - this is its primary function
- GI engages with VSL centrally for value-related operations (payments, rewards, settlements)
- **Individual DSL nodes don't need to run VSL** - the GI handles VSL interactions on behalf of the network

**Our Current Setup:**
- ✅ DSL Node (running) - indexes data, communicates with GI via `/operators` endpoint
- ✅ Global Indexer - coordinates nodes, handles VSL interactions centrally (RSS3's infrastructure)
- ❌ VSL RPC Node (not needed for DSL operation) - only needed if you want to provide VSL RPC services

## Current Status
- **Status**: Configured but not running (not required for DSL node operation)
- **Location**: `/home/babajohn33/VSL-RPC-Node` on Linode server
- **Configuration**: Ready (secrets generated, .env configured)

## When Will We Need It?

### Primary Use Cases:
1. **Providing VSL RPC Services**: If you want to run a VSL RPC endpoint for others to use
2. **Direct VSL Queries**: If you need to query VSL data directly (rather than through GI)
3. **Advanced Network Participation**: If RSS3 introduces requirements for node operators to run both DSL and VSL

### Current Priority:
**We DON'T need it for DSL node operation** because:
- ✅ DSL nodes communicate with Global Indexer (not VSL directly)
- ✅ Global Indexer (RSS3's infrastructure) handles VSL interactions centrally
- ✅ Our node is being indexed by GI without VSL running (proof: node shows as indexed)
- ✅ Our primary goal (earning RSS3 rewards) is achieved through DSL node indexing
- ✅ Ethereum worker is successfully indexing and earning rewards

## If We Need to Deploy It:

The VSL RPC Node is already configured and ready to start:

1. **Start the VSL Node:**
   ```bash
   cd /home/babajohn33/VSL-RPC-Node
   docker-compose up -d
   ```

2. **Monitor Logs:**
   ```bash
   docker-compose logs -f --tail 100
   ```

3. **Verify It's Running:**
   ```bash
   curl -d '{"id":0,"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",false]}' \
        -H "Content-Type: application/json" \
        http://localhost:8545
   ```

## Configuration
- **Network**: mainnet
- **L1 Ethereum RPC**: https://ethereum-rpc.publicnode.com
- **NEAR DA Network**: Mainnet
- **Port**: 8545 (default RPC port)

## Documentation
Official VSL deployment guide: https://docs.rss3.io/guide/vsl/deployment

## Recommendation
**Keep it configured but not running** until:
- RSS3 network requirements change to include VSL participation
- You specifically need to query VSL data
- You want to maximize network participation and rewards

