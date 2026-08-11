#!/usr/bin/env bash
# Run on Linode: cd /home/babajohn33/rss3-node && bash /path/to/check-linode-node.sh
set -euo pipefail
cd /home/babajohn33/rss3-node 2>/dev/null || { echo "Missing /home/babajohn33/rss3-node"; exit 1; }

echo "== docker-compose ps =="
docker-compose ps
echo
echo "== workers_status =="
curl -s --max-time 15 http://127.0.0.1:8080/operators/workers_status || echo "core not reachable on :8080"
echo
echo
echo "== agentdata health =="
curl -s --max-time 10 http://127.0.0.1:8887/api/v1/health || echo "agentdata not reachable on :8887"
echo
echo
echo "== containers (rss3 only) =="
docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep -E "rss3_node_|node-ethereum|node-farcaster" || true
echo
echo "== recent core errors =="
docker-compose logs --tail=20 rss3_node_core 2>&1 | grep -iE "error|fatal" || echo "(none in last 20 lines)"
echo
echo "== recent ethereum errors =="
docker-compose logs --tail=20 node-ethereum-core 2>&1 | grep -iE "error|fatal|space" || echo "(none in last 20 lines)"
