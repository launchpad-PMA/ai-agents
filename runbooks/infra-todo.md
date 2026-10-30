# Infra Todo

Open work across the Adbongo domain, Railway, and the Linode server.
State as of Oct 30, 2026.

## Where things live

| What | Host |
|------|------|
| `adbongo.io` (bare domain) | GoDaddy domain forwarding (`3.231.35.217`, AWS-hosted) — **HTTPS broken** |
| `www.adbongo.io` | Substack (CNAME `target.substack-custom-domains.com`, behind Cloudflare) |
| `web3.adbongo.io` | Linode `172.232.129.170`, nginx — serves `rss3-comm-agent/public/index.html` |
| DNS / registrar | GoDaddy (`ns21`/`ns22.domaincontrol.com`) |
| Email | Google Workspace (MX `aspmx.l.google.com`) |
| Telegram bot (Aragamago) | Railway project `Root-Pool`, service `rss3-comm-agent` |
| RSS3 node | Linode (see `rss3-comm-agent/docker-compose-railway.yaml`) |

## 1. Fix HTTPS on `adbongo.io` (priority)

Today `http://adbongo.io` 301s to `https://adbongo.io`, and that HTTPS request fails the
TLS handshake (no certificate for the bare domain). It never reaches `www`.
No CAA record is blocking certificate issuance.

- [ ] GoDaddy → My Products → `adbongo.io` → DNS → **Forwarding**: check the domain forward.
- [ ] Set forward to `https://www.adbongo.io`, type **Permanent (301)**, **Forward only** (no masking).
- [ ] If a forward already exists and HTTPS still fails, delete it and add it again —
      that re-triggers GoDaddy's certificate for the forward. Allow up to 24–48 h.
- [ ] Confirm the `A @` record is GoDaddy's forwarding address after saving (GoDaddy manages it;
      don't point it anywhere else).
- [ ] Verify:

  ```bash
  curl -sI http://adbongo.io/  | grep -i location   # expect https://www.adbongo.io/
  curl -sI https://adbongo.io/ | grep -i location   # expect https://www.adbongo.io/, no TLS error
  curl -sI https://www.adbongo.io/ | head -1        # expect 200
  ```

- [ ] If GoDaddy forwarding still won't serve HTTPS, fallback: move DNS to Cloudflare (free)
      and use a redirect rule `adbongo.io/*` → `https://www.adbongo.io/$1`.
      Re-create the Google MX, Substack CNAME, `web3` A record, and ENS TXT record first.

## 2. Telegram bot security

- [ ] Rotate the Telegram bot token in BotFather — the current one is printed in Railway logs.
- [ ] Update `TELEGRAM_BOT_TOKEN` on Railway service `rss3-comm-agent` only.
- [ ] Stop logging the token: set the `httpx` logger to `WARNING` in `agents/aragamago/bot.py`.

## 3. Railway cleanup

- [ ] Rename service `rss3-comm-agent` → `aragamago-telegram-bot` (it runs the bot, not RSS3).
      Renaming changes its `*.railway.internal` hostname.
- [ ] `ai-agents` is a duplicate bot (last deploy FAILED). Remove `TELEGRAM_BOT_TOKEN` from it
      before any redeploy, or delete the service. Two pollers on one token = `409 Conflict`
      (see `telegram-409-recovery.md`).
- [ ] Redeploy the bot from current `main` so `/health` answers (live deploy is commit `9d1b5f8`,
      which predates `health_server.py`; public URL returns 502).

## 4. Bot code fixes

- [ ] Replace `pinecone-client` with `pinecone` in `requirements.txt` (logs: "Brain not available").
- [ ] `OPENAI_API_KEY` holds an OpenRouter key (`sk-or-…`), so direct OpenAI is off.
      Either add a real OpenAI key or drop `openai` from `AI_PROVIDER_ORDER`.

## 5. RSS3 agent (later, if moved to Railway)

- [ ] Add `rss3-comm-agent/package.json` (`express`, `body-parser`, `axios`, `dotenv`).
- [ ] New service with Root Directory `rss3-comm-agent`, start `node index.js`.
- [ ] Give it only RSS3 vars (`NEYNAR_*`, `RSS3_*`, `NODE_*`, `YOUTUBE_*`, `PUBLIC_AGENT_URL`) — no Telegram token.
