# Railway deployment URLs

Two Railway services, two codebases:

| Railway / Git | Agent name | Role | Public URL |
|---------------|------------|------|------------|
| **`rss3-comm-agent`** (this folder) | **Maxayauwi** | RSS3 webhooks, Farcaster, `/api/v1/health`, dashboard | `https://rss3-comm-agent-production.up.railway.app` |
| **`agents/aragamago/`** (this repo) | **Aragamago** | Telegram bot / Sacred Library Guardian | `https://ai-agents-production-b0ef.up.railway.app` |

## What gets deployed where

- **Push / connect to Railway for Maxayauwi:** the **`rss3-comm-agent`** app only (this directory).  
  In Railway: either set **Root Directory** to `rss3-comm-agent` on the monorepo, or connect a repo that contains only this app — **not** the old single `ai-agents` root as the deploy source for this service.
- **Aragamago:** lives in this repo at **`agents/aragamago/`** (Python). Root `railway.toml` / `Dockerfile` deploy it to **`https://ai-agents-production-b0ef.up.railway.app`**. There is no separate `divine-cleric` GitHub repo in `launchpad-PMA`; that name was a folder on the orphaned 2025 branches.

## Private URL (same Railway project only)

From **another Railway service in the same project**, you can call the comm agent on the private network (no public internet, lower latency):

- **Hostname:** `rss3-comm-agent.railway.internal`  
  *(not `…internalate` — Railway uses `.railway.internal`)*

Examples (use your comm agent’s **`PORT`** from Railway, often `3000` or whatever `process.env.PORT` is):

```text
http://rss3-comm-agent.railway.internal:3000/health
http://rss3-comm-agent.railway.internal:3000/api/events
http://rss3-comm-agent.railway.internal:3000/api/v1/health
```

If Railway gives you a single private base URL in the dashboard, prefer that. **Linode / browsers / the public internet cannot reach** `.railway.internal` — only other services in the project.

## Point the RSS3 node (Linode) here

In `config/config.yaml` (or wherever `component.ai` / endpoint is set), use the **rss3-comm-agent** URL:

- **AI / agent endpoint:** `https://rss3-comm-agent-production.up.railway.app`
- **Webhooks:** `POST https://rss3-comm-agent-production.up.railway.app/api/events`

**Step-by-step (sed + restart):** see **`LINODE_POINT_TO_MAXAYAUWI.md`** and optional script **`scripts/point-linode-to-maxayauwi.sh`** (run on the Linode).

## Health checks

```bash
curl -s https://rss3-comm-agent-production.up.railway.app/health
curl -s https://rss3-comm-agent-production.up.railway.app/api/v1/health
```

## Local health script

```bash
node check-health.js https://rss3-comm-agent-production.up.railway.app
```

## Aragamago — production host

```bash
curl -s https://ai-agents-production-b0ef.up.railway.app/health
```
