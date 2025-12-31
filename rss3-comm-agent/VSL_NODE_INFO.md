# VSL (Value Sublayer) RPC Node

## What is VSL?
The VSL (Value Sublayer) RPC Node is a component of the RSS3 network that handles value-related operations and provides RPC access to the RSS3 Value Sublayer.

## Current Status
- **Status**: Configured but not running
- **Location**: `/home/babajohn33/VSL-RPC-Node` on Linode server
- **Configuration**: Ready (secrets generated, .env configured)

## When Will We Need It?

### Primary Use Cases:
1. **Value-Related Queries**: If you need to query value/transaction data from RSS3's Value Sublayer
2. **Enhanced Node Rewards**: Some RSS3 network rewards may require VSL node participation
3. **Full Network Participation**: To participate in both Data Sublayer (DSL - current) and Value Sublayer (VSL)

### Current Priority:
**We DON'T need it right now** because:
- ✅ Our primary goal (earning RSS3 rewards) is achieved through DSL node indexing
- ✅ Ethereum worker is successfully indexing and earning rewards
- ✅ VSL is a separate layer - not required for basic DSL node operations

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

