# ai-agents

Divine agents of the Launchpad.

This public repo currently holds **both** living agents. There is no separate `divine-cleric` GitHub repository under `launchpad-PMA`.

## What lives here (git `main`)

| Path | Agent | Runtime | Railway |
|------|--------|---------|---------|
| **`agents/aragamago/`** | **Aragamago** (Telegram / Sacred Library Guardian) | Python (`Dockerfile`, root `railway.toml`) | `https://ai-agents-production-b0ef.up.railway.app` |
| **`rss3-comm-agent/`** | **Maxayauwi** (RSS3 webhooks, Farcaster, dashboard) | Node (`rss3-comm-agent/package.json`) | `https://rss3-comm-agent-production.up.railway.app` |

Root `railway.toml` starts **Aragamago** (`python agents/aragamago/bot.py`), not Maxayauwi. For Maxayauwi, set Railway **Root Directory** to `rss3-comm-agent`.

See `rss3-comm-agent/RAILWAY_URLS.md` for public vs private URLs and Linode webhook targets.

## Two git lineages

Current `main` does **not** share history with the 2025 Cursor branches (`cursor/distinguish-railway-agent-scope-from-vercel-deployment-e154` and siblings). Those branches still contain the original monorepo layout (`divine-cleric/`, `covenant-keeper/`, `post-nft/`, root Twitter `index.js`).

`main` was replaced in March 2026 with the Antigravity / BLAST Aragamago tree, then Codex hardened Railway env loading, then Cursor (11 Aug 2026) re-imported the Maxayauwi `rss3-comm-agent/` tree.

Local secrets: set `ENV_PATH` or use the Codex default `master.env`. The old Antigravity Windows path (`C:\Users\Baba\Documents\antigravity\.env`) is no longer hardcoded.

On the desktop, stash or commit local Antigravity work, then `git pull origin main` and diff. Details: `findings.md`.

## Membership & initiation (DAO / Soul Pod / Aragamago)

Product guides:
- **`rss3-comm-agent/docs/GENESIS_SIGIL_MEMBERSHIP_GUIDE.md`** — steward covenant, Ifá initiation, Soul Pod, Aragamago
- **`rss3-comm-agent/docs/HATS_TRAITS_AI_PROTOCOL_PLAN.md`** — Hats roles (clergy, elders, kin), NFT traits, agreement binding, AI Protocol mimic
