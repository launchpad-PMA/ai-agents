# JARVIS Phase 1 — Inventory, Aragamago diagnosis, voice prototype

Date: 30 Oct 2026 (America/Chicago). No production deploys. No services deleted. No secrets printed.

## Galaxy S26 + Cursor: correct flow

There is no native Cursor Android IDE. Do not look for a Play Store “Cursor desktop” app for the Galaxy S26.

Correct loop:

1. On the phone, open Chrome (not the in-app Samsung browser if Chrome is available).
2. Sign in at [cursor.com/agents](https://cursor.com/agents) with the same Cursor account that owns `launchpad-PMA/ai-agents`.
3. Chrome menu → **Add to Home screen** / **Install app**. That PWA is how you talk to Cloud Agents from Android.
4. Start or follow Cloud Agents from the phone. They run on Cursor’s VMs, not on the S26. You can leave the chat; the run continues.
5. Review diffs and PRs in that same surface, or in GitHub mobile.
6. Use Slack `@cursor` if you want completion pings. The Android PWA does not match iOS push/Remote Control.

JARVIS itself is a separate PWA in this repo (`jarvis/`). After you approve a host, install **that** app from Chrome the same way: open the JARVIS URL → Add to Home screen. Microphone permission must be granted to Chrome.

This Cloud Agent can keep building while you use the S26 to send follow-ups. It cannot flash firmware, install Cursor as a system app, or control the phone.

## Repository inventory

Connected to this Cloud Agent environment:

| Repo | Role |
|------|------|
| [launchpad-PMA/ai-agents](https://github.com/launchpad-PMA/ai-agents) | Only linked repo. Monorepo for Aragamago (Python Telegram bot), Maxayauwi (`rss3-comm-agent/`), AdBongo/LexClinic/Temple marketing pages, Railway runbooks. |

Visible to `gh` for `launchpad-PMA` but **not** mounted here:

| Repo | Notes |
|------|--------|
| `daomaker` | HTML, updated 2026-08-22 |
| `docs` | org docs, 2025-11 |
| `templates` | LexClinic templates, 2025-02 |

Not found as a GitHub repo under this org:

- `divine-cleric` — mentioned in `README.md` and `rss3-comm-agent/RAILWAY_URLS.md` as the Aragamago home. Confirmed stale: **Aragamago's source of truth is `agents/aragamago/` in this repo**, alongside Maxayauwi (`rss3-comm-agent/`). Railway deployed the bot from here (PRs #4/#5).

Root `railway.toml` / `Dockerfile` still start the Python bot. If the Maxayauwi Railway service builds from the repo root instead of `rss3-comm-agent/`, it runs the Telegram poller, which never binds `PORT` — a likely cause of Maxayauwi's 502. `rss3-comm-agent/` also has no `package.json` in git.

In-tree map:

```
agents/aragamago/     Telegram bot, Google tools, RSS3 diagnostics
connectors/           Pinecone + Supabase helpers (legacy Windows env paths)
rss3-comm-agent/      Maxayauwi Node comm agent + public AdBongo site
runbooks/             Railway deploy + Telegram 409 recovery
jarvis/               Phase 1 voice PWA (this branch)
```

Related properties referenced in code/content (not modified):

- RSS3 Node #97 / `web3.adbongo.io:8080`
- Maxayauwi Railway `https://rss3-comm-agent-production.up.railway.app`
- Former Aragamago host `https://ai-agents-production-b0ef.up.railway.app`
- AdBongo, Advocacy Launchpad, Temple of Roots, LexClinic pages under `rss3-comm-agent/public/`
- Farcaster via Neynar in `rss3-comm-agent/index.js`
- Supabase / Pinecone / Google / ElevenLabs / OpenRouter in bot env docs

## Aragamago diagnosis

### Where it lives

- **Code:** `agents/aragamago/bot.py` in this repo, Dockerized by root `Dockerfile` + `railway.toml` (`python agents/aragamago/bot.py`).
- **Transport:** `app.run_polling()` (Telegram `getUpdates`). No webhook. No HTTP server before this branch.
- **Documented production URL:** `https://ai-agents-production-b0ef.up.railway.app`
- **Railway MCP:** not signed in from this agent. Dashboard history/logs were **not** pulled. Public HTTP probes only.

### Public probes (read-only, 30 Oct 2026)

| Target | Result |
|--------|--------|
| `ai-agents-production-b0ef.up.railway.app` | **HTTP 404** `Application not found` — Railway no longer has this public app (deleted service, unbound domain, or project gone). |
| `rss3-comm-agent-production.up.railway.app/health` | **HTTP 502** `Application failed to respond` — hostname exists; process is not answering. |
| `web3.adbongo.io:8080` | Connection refused |
| `gi.rss3.io` | DNS failed from this environment |

Workspace `.env` has `TELEGRAM_BOT_TOKEN` **empty**. Local handshake script `.tmp/telegram_test.py` points at a Windows path that is not on this VM. Canonical secrets path in code is Baba’s Obsidian `master.env`, which is also not on this VM.

### Why it stopped (most likely, in order)

1. **The Railway public app for Aragamago is gone (404).** Polling bots can still run without a public URL, but this hostname is the one the repo documents. Combined with an empty token in the Cloud workspace, there is no evidence a replica is healthy.
2. **Long polling + multiple replicas = Telegram 409.** Already documented in `runbooks/telegram-409-recovery.md`. `getUpdates` allows only one poller per token. Duplicate Railway services, preview envs, or a laptop still running `bot.py` will kill the “official” bot even if the token is valid.
3. **No HTTP health listener.** Historical PRs #4/#5 removed healthchecks because the bot did not bind `PORT`. Railway can mark the service failed or keep restarting it. That matches “it worked, then it didn’t” after platform policy changes.
4. **Import-time crash if `TELEGRAM_BOT_TOKEN` is missing.** The process never stayed up long enough to inspect.
5. **Split-brain docs.** README says Aragamago is `divine-cleric`; this monorepo still contains the bot and the Railway Docker start command. Deploying the wrong root directory would start the Python bot on the Maxayauwi service (or the reverse). Maxayauwi’s 502 is consistent with a Node app that is not listening (and `rss3-comm-agent/` has **no** `package.json` in git).
6. **Hardcoded machine paths** for soul prompts and some connectors (`/home/baba2-mainoffice/...`, `C:\Users\Baba\...`). On Railway those files are absent; the bot falls back to the in-file soul prompt, which is OK, but Google/Pinecone helpers may still look at the wrong env file.

### Repair vs refactor vs reuse

| Choice | Verdict |
|--------|---------|
| **Repair** | **Do this first** for Telegram. The bot is real, feature-rich (Gemini/OpenRouter/OpenAI, voice notes, Google, Pinecone, `/rss3status`). Add `/health`, one replica, one token, restore env on a single Railway service **after you approve**. |
| **Refactor** | After repair: webhook instead of polling (eliminates 409), drop machine-local paths, stop using the repo root as both Maxayauwi static site and Aragamago Docker app. |
| **Reuse** | Reuse soul/prompt, Google tools, RSS3 diagnostics, and Pinecone/Supabase connectors as **JARVIS tools behind auth**. Do not keep JARVIS secrets in the Telegram poller. |

**Do not deploy this branch until you say so.**

## Tested fix on this branch (not deployed)

- `agents/aragamago/health_server.py` binds `PORT` and serves `GET /health`.
- `bot.py` no longer raises at import when the token is missing; it serves health-only instead of crash-looping.
- Unit test: `python3 -m unittest tests.test_aragamago_health`.

Still needed after your approval: Railway project access, a single replica, token present, decide webhook vs polling, and a Maxayauwi-specific Node start (separate service, `package.json`).

## Voice-interface prototype (mock tools)

Run locally (or on a future approved host):

```bash
cd jarvis
JARVIS_ACCESS_CODE='your-passcode' node server/index.js
```

Then on the S26: Chrome → that URL → Allow microphone → Add to Home screen.

Behavior now:

- Push-to-talk (Galaxy Chrome `webkitSpeechRecognition`)
- Spoken replies via `speechSynthesis`
- Backend auth session; access code never stored in source
- Conversation history + memory toggle
- Command dashboard of typed tools
- OpenAI Realtime: server mints a session **only if** `OPENAI_API_KEY` is in the environment. Otherwise mock mode. The browser never gets the API key.
- Tools are **mocks**. They report the probes above. Privileged `agents.delegate` requires “authorize”. Social drafts are not posted.

## Later phases (not started)

- Live RSS3 / Railway / Linode / Supabase adapters with least-privilege tokens
- Approval cards on the phone before any write
- Audit log in Supabase
- Webhook Telegram bridge so JARVIS and Aragamago share one token without 409
- Rollback: previous Railway deployment + this git branch revert
