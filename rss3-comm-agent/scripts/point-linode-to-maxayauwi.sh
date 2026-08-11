#!/usr/bin/env bash
# Run ON THE LINODE in /home/babajohn33/rss3-node (or set RSS3_NODE_DIR).
# Points RSS3 node config + docker-compose at Maxayauwi on Railway.

set -euo pipefail
NEW_AI_URL="${MAXAYAUWI_URL:-https://rss3-comm-agent-production.up.railway.app}"
RSS3_NODE_DIR="${RSS3_NODE_DIR:-/home/babajohn33/rss3-node}"

cd "$RSS3_NODE_DIR" || { echo "Cannot cd to $RSS3_NODE_DIR"; exit 1; }

ts="$(date +%Y%m%d-%H%M%S)"
cp config/config.yaml "config/config.yaml.bak-$ts"
[ -f docker-compose.yaml ] && cp docker-compose.yaml "docker-compose.yaml.bak-$ts"

# Old public hosts → Maxayauwi
sed -i "s|https://ai-agents-production-b0ef.up.railway.app|${NEW_AI_URL}|g" config/config.yaml
# Optional: internal agentdata → public Maxayauwi (uncomment if you want to force external AI only)
# sed -i "s|http://rss3_node_agentdata:8887|${NEW_AI_URL}|g" docker-compose.yaml

sed -i "s|https://ai-agents-production-b0ef.up.railway.app|${NEW_AI_URL}|g" docker-compose.yaml 2>/dev/null || true

echo "Updated files. Grep check:"
grep -nE "endpoint:|NODE_COMPONENT_AI_ENDPOINT" config/config.yaml docker-compose.yaml 2>/dev/null || true
echo
echo "Next: docker compose up -d   (from $RSS3_NODE_DIR)"
echo "Test: curl -s ${NEW_AI_URL}/api/v1/health"
