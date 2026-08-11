# Replace Railway Postgres with Supabase

Use this to point the RSS3 node (and agentdata) on Linode at a Supabase Postgres database instead of Railway.

---

## This project's Supabase DB

- **Project URL:** https://jnaqvazcdorrjlualmym.supabase.co  
- **Project ref:** `jnaqvazcdorrjlualmym`

**Connection string templates** (replace `[YOUR-PASSWORD]` with your DB password from Supabase → Project Settings → Database):

- **Direct (IPv6 or with IPv4 add-on):**
  ```text
  postgresql://postgres:[YOUR-PASSWORD]@db.jnaqvazcdorrjlualmym.supabase.co:5432/postgres?sslmode=require
  ```
  (Without `?sslmode=require` the node may fail with TLS/connection errors.)
- **Session pooler (recommended for Linode IPv4):**  
  Get the exact URI from Dashboard → **Connect** → **Session mode**, then add `?sslmode=require` if missing. It looks like:
  ```text
  postgresql://postgres.jnaqvazcdorrjlualmym:[YOUR-PASSWORD]@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require
  ```

---

## 1. Get your Supabase connection string

1. Create a project at [Supabase Dashboard](https://supabase.com/dashboard) (or use an existing one).
2. Go to **Project Settings → Database** (or click **Connect** on the project).
3. Under **Connection string**, choose:
   - **URI**: Use **Session mode** (pooler) if your Linode has IPv4 only — recommended.
   - Copy the URI; it looks like:
     ```text
     postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
     ```
   - Append SSL: add `?sslmode=require` so the final URI is:
     ```text
     postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require
     ```
   - If the copied URI already has `?sslmode=...`, leave it or set to `sslmode=require`.

**Important:** Replace `[YOUR-PASSWORD]` with your actual database password (the one you set for the project). If it contains special characters, URL-encode them (e.g. `@` → `%40`, `#` → `%23`).

---

## 2. Update Linode: config and .env

SSH into the Linode and run the commands below. Set `SUPABASE_URI` to your full Supabase URI (with `?sslmode=require`).

```bash
ssh root@172.232.129.170
cd /home/babajohn33/rss3-node

# Set your Supabase URI once (no spaces around =)
export SUPABASE_URI='postgresql://postgres.xxxx:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require'

# Backup
cp config/config.yaml config/config.yaml.bak-$(date +%Y%m%d)
cp .env .env.bak-$(date +%Y%m%d)

# Update config.yaml: database.uri
sed -i "s|uri: postgresql://postgres:.*@trolley.proxy.rlwy.net:31631/railway?sslmode=require|uri: $SUPABASE_URI|" config/config.yaml

# Update config.yaml: agentdata_db_url (same URI)
sed -i "s|agentdata_db_url: postgresql://postgres:.*@trolley.proxy.rlwy.net:31631/railway?sslmode=require|agentdata_db_url: $SUPABASE_URI|" config/config.yaml

# Update .env
sed -i "s|DB_CONNECTION=postgresql://postgres:.*@trolley.proxy.rlwy.net:31631/railway?sslmode=require|DB_CONNECTION=$SUPABASE_URI|" .env
sed -i "s|DATABASE_URI=postgresql://postgres:.*@trolley.proxy.rlwy.net:31631/railway?sslmode=require|DATABASE_URI=$SUPABASE_URI|" .env

# Verify (no Railway host should remain)
grep -E "uri:|agentdata_db_url:|DB_CONNECTION|DATABASE_URI" config/config.yaml .env
```

---

## 3. Restart the RSS3 stack

```bash
cd /home/babajohn33/rss3-node
docker-compose down
docker-compose up -d
```

Check that core and workers stay up and can reach the DB:

```bash
docker-compose ps
docker-compose logs --tail=30 rss3_node_core
curl -s http://127.0.0.1:8080/operators/workers_status | head -c 500
```

---

## 4. Railway agent (if it uses the same DB)

If your AI agent on Railway (e.g. `rss3-comm-agent-production.up.railway.app` for Maxayauwi) uses the same Postgres for agentdata or app DB:

- In **Railway → your project → Variables**, set:
  - `DATABASE_URL` or `DB_CONNECTION` (whatever the app expects) to the **same Supabase URI**.
- Redeploy the service so it picks up the new variable.

---

## 5. Summary of what uses the DB

| Place              | What to set                                      |
|--------------------|--------------------------------------------------|
| Linode `config.yaml` | `database.uri`, `component.ai.parameters.agentdata_db_url` |
| Linode `.env`        | `DB_CONNECTION`, `DATABASE_URI`                  |
| Railway (if applicable) | `DATABASE_URL` or `DB_CONNECTION`            |

All must point to the same Supabase Postgres URI with `?sslmode=require`.

---

## Quick apply (from this repo)

With your DB password set in the URI, run from the repo root:

```bash
# Direct connection (replace YOUR_PASSWORD)
SUPABASE_URI='postgresql://postgres:YOUR_PASSWORD@db.jnaqvazcdorrjlualmym.supabase.co:5432/postgres?sslmode=require' \
  REMOTE=1 ./scripts/switch-to-supabase.sh
```

Or use Session pooler URI from Supabase Dashboard → Connect → Session mode, then:

```bash
SUPABASE_URI='postgresql://postgres.jnaqvazcdorrjlualmym:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres?sslmode=require' \
  REMOTE=1 ./scripts/switch-to-supabase.sh
```
