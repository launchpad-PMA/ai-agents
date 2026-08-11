# Point the Linode RSS3 node at Maxayauwi (rss3-comm-agent)

**Target agent data / AI endpoint (public HTTPS):**  
`https://rss3-comm-agent-production.up.railway.app`

The node’s core calls **`/api/v1/health`** on that URL. Maxayauwi serves it.

---

## On the Linode (SSH or Remote-SSH)

```bash
cd /home/babajohn33/rss3-node
export NEW_AI_URL='https://rss3-comm-agent-production.up.railway.app'

# Backup
cp config/config.yaml "config/config.yaml.bak-$(date +%Y%m%d-%H%M%S)"
[ -f docker-compose.yaml ] && cp docker-compose.yaml "docker-compose.yaml.bak-$(date +%Y%m%d-%H%M%S)"

# 1) Replace old combined ai-agents host (Aragamago / former max)
sed -i "s|https://ai-agents-production-b0ef.up.railway.app|${NEW_AI_URL}|g" config/config.yaml

# 2) docker-compose: public AI endpoint (core / broadcaster / monitor)
sed -i "s|https://ai-agents-production-b0ef.up.railway.app|${NEW_AI_URL}|g" docker-compose.yaml

# 3) Optional — only if you want the node to use Maxayauwi instead of local agentdata:8887
# sed -i "s|http://rss3_node_agentdata:8887|${NEW_AI_URL}|g" docker-compose.yaml

# Verify what you have now
echo "=== config.yaml (AI / endpoint lines) ==="
grep -nE "endpoint|component\.|ai:|agentdata" config/config.yaml || grep -n "rss3-comm-agent\|ai-agents-production\|agentdata" config/config.yaml

echo "=== docker-compose NODE_COMPONENT ==="
grep -n "NODE_COMPONENT_AI_ENDPOINT\|ai-agents\|rss3-comm" docker-compose.yaml || true
```

**Manual check in `config/config.yaml`:** under **`component`** → **`ai`** → **`parameters`**, ensure:

```yaml
endpoint: https://rss3-comm-agent-production.up.railway.app
```

(no trailing slash unless your node version docs require it)

---

## Restart the stack

```bash
cd /home/babajohn33/rss3-node
docker compose up -d
# or: docker-compose up -d
```

---

## Smoke test (from Linode or your PC)

```bash
curl -s https://rss3-comm-agent-production.up.railway.app/api/v1/health
curl -s https://rss3-comm-agent-production.up.railway.app/health
```

Core logs should stop complaining about failing to reach the old host once the new URL is live and reachable from the container network.

---

## If health checks still target `rss3_node_agentdata:8887`

That means **`NODE_COMPONENT_AI_ENDPOINT`** in `docker-compose.yaml` still points at the internal container. Either:

- Point it at **`https://rss3-comm-agent-production.up.railway.app`** (public, works from Docker on Linode), or  
- Run the **`rss3_node_agentdata`** container again and keep the internal URL (see `LINODE_FIXES.md`).

For **external Maxayauwi only**, prefer the **HTTPS public URL** in compose for `NODE_COMPONENT_AI_ENDPOINT`.
