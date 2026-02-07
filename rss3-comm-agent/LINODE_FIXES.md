# Linode RSS3 Node – Fixes to Apply

Run these on your Linode (SSH as root) once disk space is available.

---

## 1. Fix Database URIs in `.env`

The `.env` had incorrect database names and SSL settings. Run:

```bash
cd /home/babajohn33/rss3-node

# Fix DB_CONNECTION (agent_data → railway, sslmode=require)
sed -i 's|agent_data?sslmode=disable|railway?sslmode=require|g' .env

# Fix DATABASE_URI (sslmode=disable → sslmode=require)
sed -i 's|railway?sslmode=disable|railway?sslmode=require|g' .env

# Verify
grep -E "DB_CONNECTION|DATABASE_URI" .env
```

Expected result:
- `DB_CONNECTION=...trolley.proxy.rlwy.net:31631/railway?sslmode=require`
- `DATABASE_URI=...trolley.proxy.rlwy.net:31631/railway?sslmode=require`

---

## 2. Fix AgentData / AI Component

**Problem:** The RSS3 core probes `http://rss3_node_agentdata:8887/api/v1/health` but that container is not running. Config has `endpoint: https://ai-agents-production-b0ef.up.railway.app`, but the Node expects an internal `rss3_node_agentdata` container when the AI component is configured.

**Solution:** Regenerate `docker-compose.yaml` with the Node Automated Deployer so it includes the `rss3_node_agentdata` container, then restart services.

```bash
cd /home/babajohn33/rss3-node

# Ensure config has component.ai (it does – endpoint + agentdata_db_url)
# Run the deployer to regenerate docker-compose.yaml
export NODE_VERSION=v2.0.0
./node-automated-deployer > docker-compose.yaml

# Check that rss3_node_agentdata is in the generated compose
grep -A2 "agentdata" docker-compose.yaml

# Restart everything (deployer does down + up -d, or manually:)
docker-compose down   # or: docker compose down
docker-compose up -d  # or: docker compose up -d

# Verify agentdata is running
docker ps | grep agentdata
```

**Alternative:** If the deployer does not add agentdata (or you prefer using the external Railway agent only), you may need to remove or comment out the `component.ai` block from `config/config.yaml` so the core stops probing for `rss3_node_agentdata`. That would stop the "failed to fetch AI health" errors but would disable the AI/AgentData indexing on the node.

---

## 3. After Fixes – Restart and Check

```bash
cd /home/babajohn33/rss3-node
docker restart rss3_node_core node-ethereum-core rss3_node_agentdata 2>/dev/null

# Check logs
docker logs node-ethereum-core --tail 30
docker logs rss3_node_core --tail 30
```

Look for:
- `successfully saved activities and checkpoint` (Ethereum worker)
- No more "failed to fetch AI health" (if agentdata is running)
- No "connection reset by peer" or "recovery mode" (database)

---

## 4. If Linode Disk Is Full

Free space before editing files:

```bash
# Check disk usage
df -h
du -sh /var/lib/docker/*

# Remove unused Docker data (images, containers, volumes)
docker system prune -a --volumes  # WARNING: removes unused Docker data

# Or target specific large dirs
docker image prune -a
docker volume prune
```

---

## Summary

| Fix | Purpose |
|-----|---------|
| `.env` DB URIs | Use `railway` DB and `sslmode=require` for Railway Postgres |
| Deployer / agentdata | Bring back `rss3_node_agentdata` so core health checks pass |
| Restart | Ensure all services use the updated config |
