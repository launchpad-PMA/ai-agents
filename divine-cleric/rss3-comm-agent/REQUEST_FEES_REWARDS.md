# RSS3 Request Fees and Network Rewards

## Overview
Understanding how request fees work and how they impact node rewards is crucial for RSS3 node operators.

## Request Fee Model

### Current Status
- **All requests are currently FREE** - no fees are charged
- This is expected to change soon (requires an REP proposal)
- When implemented, developers will pay fees in $RSS3 for requests processed by DSL nodes

### Fee Distribution (When Implemented)
- **100% of request fees** go to:
  - Node Operators (like us)
  - Owners of the information requested
  
- Distribution ratio between operators and owners will be determined by an REP (RSS3 Enhancement Proposal)

### Purpose
This model aims to promote an **Ownership Economy** where:
- Node operators are rewarded for processing requests
- Data/information owners are compensated for their content
- The network becomes self-sustaining through fee-based economics

## Impact on Node Rewards

### Critical Relationship
**The amount of request fee directly reflects the work rate of a Node and has a very important impact on the final network reward received by the Node.**

This means:
- More requests processed = Higher work rate = More fees earned = Higher network rewards
- Your node's ability to handle and process requests directly impacts your earnings
- Request fees are a key metric for calculating overall network rewards

### What This Means for Our Node
- ✅ Currently: Focus on indexing and maintaining high uptime (Ethereum worker is indexing successfully)
- ✅ Future: When fees are implemented, our node will earn:
  - Request fees from developers using our node
  - Network rewards based on work rate (which includes request fees)
  
- 📊 **Current Work Rate Indicators:**
  - Ethereum worker: `indexed_state: 21,529,339+`, `index_count: 467,325+`
  - Node status: Indexing and operational
  - These metrics contribute to work rate calculations

## Documentation Reference
Official documentation: https://docs.rss3.io/guide/core/concepts/request-fee

## Takeaways for Node Operators

1. **Keep Your Node Healthy**: High uptime and successful indexing = better work rate
2. **Monitor Request Processing**: When fees are implemented, processing more requests = more earnings
3. **Network Rewards Depend on Work Rate**: Request fees are a key component of work rate calculation
4. **Stay Updated**: Watch for REP proposals that will define fee structure and distribution ratios

