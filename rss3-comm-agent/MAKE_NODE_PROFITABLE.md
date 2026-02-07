# Making the RSS3 Node Profitable (Not Parasitic)

## The Problem
Your node is:
- ✅ Indexing data (15.9M activities processed)
- ❌ **NOT saving data** (database full)
- ❌ **NOT earning rewards** (can't save = no work credit)
- 💸 **Costing money** (Railway database, server costs)

## How RSS3 Nodes Earn Money

### Current Earnings (v2.0):
1. **Network Rewards**: Based on work rate (indexing + serving requests)
   - Your node indexes but can't save → **no work credit**
   - Workers show indexed but data not persisted → **no reward**

2. **Request Fees** (Coming Soon):
   - When fees are implemented, you earn for serving queries
   - But first you need **data to serve** → requires working database

### The Reality:
**Right now: Your node is costing money and earning NOTHING because it can't save data.**

## Solution: Fix the Database

### Option 1: Clear the Database (Start Fresh)
Since you said there's no real data anyway:
1. Go to Railway dashboard
2. Delete/clear the Postgres database
3. Restart the node
4. Let it start fresh and actually save data

### Option 2: Upgrade Railway Database
1. Check Railway database usage
2. Upgrade to larger plan if needed
3. Keep existing data (if any is valuable)

### Option 3: Use Different Database
1. Move to self-hosted Postgres (Linode)
2. More control, potentially cheaper long-term
3. But requires setup

## Steps to Make It Work & Earn

1. **Fix Database First** (choose one above)
2. **Verify Node Can Save Data**:
   ```bash
   # Check if workers can save
   curl http://web3.adbongo.io:8080/operators/workers_status
   # Look for index_count increasing AND being saved
   ```

3. **Monitor Earnings**:
   - Check RSS3 explorer: https://explorer.rss3.io/nodes/0x0063951De34a75C25279CfE3C212f4855125fD8f
   - Track work rate and rewards
   - RSS3 rewards may be distributed periodically (check their docs)

4. **Ensure Node is Serving**:
   - Node must be publicly accessible (✅ you have this)
   - Must respond to queries (✅ /operators endpoint works)
   - Must have data to serve (❌ **THIS IS THE PROBLEM**)

## Current Status

### What Works:
- ✅ Node indexing Ethereum (15.9M activities processed)
- ✅ Broadcasting to Global Indexer
- ✅ Public endpoint accessible
- ✅ Workers running

### What's Broken:
- ❌ **Database full → can't save data**
- ❌ **No data saved → no work credit → no rewards**
- ❌ **Costing money without earning**

## Decision Point

**You have 3 options:**

### 1. Fix and Keep Running (If You Want RSS3 Rewards)
- Clear/upgrade database
- Let node actually save data
- Wait for RSS3 reward distribution
- **Risk**: May not earn enough to cover costs

### 2. Stop Running (Save Money)
- Shut down the node
- Stop paying for Railway database
- **Saves money, earns nothing**

### 3. Minimal Setup (Wait for Fees)
- Keep database minimal
- Don't let it fill up
- Wait for request fees to be implemented
- **Lower cost, potential future earnings**

## Volume Full (e.g. 80GB) – What to Do

If Railway says **volume ran out of space** (e.g. at 80GB):

### Option A: Free space inside Postgres (keep data)
From Railway Postgres **Query** or any client connected to `DATABASE_URL`:

```sql
-- Reclaim space from dead rows and compact tables (run during low traffic)
VACUUM FULL;

-- Or per table if FULL is too heavy:
VACUUM ANALYZE;
```

Then in Railway: **Postgres service → Settings → Volumes**. Check if you can **increase volume size** (if the plan allows). If not, you must free more space or move data.

### Option B: Wipe and start fresh (no need to keep data)
See **"How to wipe/reset the DB"** below.

After a wipe, the node will re-index from scratch. With an 80GB cap, it will fill again unless you either **upgrade volume size** or **move to self-hosted Postgres** (e.g. Linode) with a larger or expandable disk.

### Option C: Move to self-hosted Postgres (Linode)
- Provision a Linode with enough disk (e.g. 100GB+ or expandable).
- Install Postgres, create a DB and user, allow connections from the node (and optionally from Railway if the app stays there).
- Set the node’s `DATABASE_URL` to the Linode Postgres.
- Then you can decommission the Railway Postgres volume to stop paying for it and avoid the 80GB limit.

---

## How to wipe/reset the DB

### Method 1: Railway dashboard (if available)
1. Go to [railway.app](https://railway.app) → your project.
2. Click the **Postgres** service (database icon).
3. Open **Settings** (or the gear icon).
4. Scroll to **Danger** / **Data** / **Volume**.
5. Look for **Reset database**, **Clear data**, **Remove volume**, or **Delete all data**.
6. Confirm. The volume may be recreated empty; if not, use Method 2.

*(If you don’t see a reset option, use Method 2.)*

### Method 2: Wipe via SQL (always works)
1. In Railway: **Postgres** service → **Data** or **Query** tab (or **Connect** to get connection details).
2. If there’s a **Query** tab, use it. Otherwise copy **Connection URL** (e.g. `postgresql://user:pass@host:port/railway`) and use `psql` or any Postgres client.
3. Run this to **drop every user table and free space** (replace `public` if your app uses another schema):

```sql
-- Disconnect other sessions (optional; may need to run as superuser)
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();

-- Drop all tables in public schema (wipes all data)
DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
    EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
  END LOOP;
END $$;
```

4. Reclaim disk space (so the volume shows free space):

```sql
VACUUM FULL;
```

5. Restart your **RSS3 node** (or app) so it recreates tables and starts indexing again. No need to change `DATABASE_URL` if you only wiped data.

### Method 3: New Postgres service (nuclear option)
1. In the same project, click **+ New** → **Database** → **PostgreSQL** (add a new Postgres).
2. In the new service, open **Variables** or **Connect** and copy the new **`DATABASE_URL`**.
3. In your **RSS3 node** (or app) service, set **Variables** → `DATABASE_URL` = new URL.
4. Redeploy/restart the node.
5. Delete the **old** Postgres service (and its volume) so you stop paying for it.

Use Method 2 when the volume is full and you just want to wipe and keep using the same DB. Use Method 3 when you want a brand‑new database and are okay switching the connection URL.

## Immediate Action Required

**If you want it to work:**
1. **Clear the Railway database** (since there's no real data) – see "Volume Full" section above – or run `VACUUM FULL` if you want to keep data.
2. **Restart the node**
3. **Monitor if it starts saving data**
4. **Check if index_count in database matches worker status**

**If you're done with it:**
- Just shut it down and save the money
- RSS3 rewards might not be worth the costs right now

## Bottom Line

**Your node is "parasitic" because:**
- It consumes resources (database space, server)
- But can't complete its job (save data)
- So it earns nothing

**To make it profitable:**
- Fix the database issue
- Let it actually save data
- Then it can earn RSS3 rewards based on work rate

**But be realistic**: RSS3 rewards might not cover costs yet. Request fees aren't live. You might be running it at a loss.

