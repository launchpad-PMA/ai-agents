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

**Problem:** The RSS3 core probes `http://rss3_node_agentdata:8887/api/v1/health` but that container is not running. Config may have `endpoint: https://rss3-comm-agent-production.up.railway.app` (Maxayauwi comm agent), but the Node expects an internal `rss3_node_agentdata` container when the AI component is configured.

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

## Restart stack and check logs (after node is working)

Production RSS3 files on the server live under **`/home/babajohn33/rss3-node`** — that path is the source of truth for `.env` and `config/config.yaml`, not your laptop copy until you sync.

**Always `docker-compose down` before `docker-compose up -d`.** Skipping `down` leaves old containers, networks, and names around (“phantoms”). The node may then try to resolve hostnames from a **previous** compose project (e.g. `rss3-node-redis-1`) while your current file expects **`redis`**, which shows up as `lookup … no such host` in core logs. A full `down` clears that mismatch.

Recycle the stack:

```bash
cd /home/babajohn33/rss3-node

docker-compose down
docker-compose up -d
```

If you renamed services or switched compose files, also remove orphans once:

```bash
docker-compose down --remove-orphans
docker-compose up -d
```

### Redis host in `.env`

If core logs show `lookup rss3-node-redis-1 … no such host`, **`NODE_REDIS_ENDPOINT` in `.env` is wrong** (leftover from an old Compose project name). Set:

```bash
NODE_REDIS_ENDPOINT=redis:6379
NODE_REDIS_PORT=6379
```

The service in `docker-compose.yaml` is reachable as hostname **`redis`** on the default network.

### Database URI and `${VAR}` in `config.yaml`

RSS3 Node **v2.0.x does not expand** `${DATABASE_URI}` (and similar) inside the mounted YAML; it tries to parse the literal string. After editing `.env`, either:

- Put the full Postgres URI directly in `config/config.yaml` on the server, or  
- Keep a template with `${…}` in git and **render** before each `up`:

```bash
cd /home/babajohn33/rss3-node
python3 scripts/render-rss3-node-config-from-env.py   # expands ${VAR} from .env into config/config.yaml
docker-compose down
docker-compose up -d
```

Rendering **overwrites** `config/config.yaml` with concrete values; keep the template copy in git and re-copy or pull before re-rendering if you need placeholders again.

Wait ~15 seconds for Redis health checks, then:

```bash
docker-compose ps
```

Inspect recent logs (adjust `--tail` as needed):

```bash
docker-compose logs --tail=50 rss3_node_core
docker-compose logs --tail=40 rss3_node_agentdata
docker-compose logs --tail=30 node-ethereum-core
docker-compose logs --tail=30 node-farcaster-core
```

Follow one service live:

```bash
docker-compose logs -f --tail=100 rss3_node_core
```

**Note:** Many Linode images only provide **`docker-compose`** (hyphen), not `docker compose` (space).

Optional HTTP check if **8080** is reachable:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://web3.adbongo.io:8080/
```

---

## Summary

| Fix | Purpose |
|-----|---------|
| `.env` DB URIs | Use `railway` DB and `sslmode=require` for Railway Postgres |
| Deployer / agentdata | Bring back `rss3_node_agentdata` so core health checks pass |
| Restart | Ensure all services use the updated config |
