# 🔍 Findings & Discoveries

> This file captures research, discoveries, and constraints found during the project.

---

## 2026-08-14 — Git vs desktop (Antigravity / Codex)

GitHub `origin/main` is what other computers have been pushing. This clone is clean and matches that tip (`a793327`). Desktop Antigravity work is compared by pulling this history, then diffing local files.

### Two git lineages (no common ancestor)

| Lineage | Tip | What it is |
|---------|-----|------------|
| **Current `main`** (Mar–Aug 2026) | `a793327` | Antigravity BLAST + Aragamago Python bot, then Codex Railway/env hardening, then Cursor re-import of Maxayauwi |
| **2025 Cursor branches** | e.g. `cursor/distinguish-railway-agent-scope-from-vercel-deployment-e154` | Original monorepo: `divine-cleric/`, `covenant-keeper/`, `post-nft/`, root Twitter `index.js`, older `rss3-comm-agent/` |

`launchpad-PMA` has **no** separate `divine-cleric` GitHub repo. That name was a folder on the 2025 branches (mostly empty `prompts.md`). Aragamago now lives at `agents/aragamago/` on `main`.

### What each tool left on `main`

**Antigravity (Windows desktop, BLAST, ~Mar 2026)**
- `gemini.md`, `task_plan.md`, `findings.md`, `progress.md` — still frozen at Protocol 0
- Hardcoded `C:\Users\Baba\Documents\antigravity\.env` in connectors (now pointed at `runtime_env.py`)
- First `main` commit `e9aa711` (14 Mar 2026) replaced history: Aragamago Docker/Railway, Pinecone, Supabase, committed `node_modules/`

**Codex (Linux `/home/baba2-mainoffice/…`, Apr–May 2026)**
- `runtime_env.py` + `tools/export_railway_env.py` read Obsidian `Agents/Secrets/master.env`
- OpenRouter / Google OAuth / Telegram 409 runbooks
- Rapid duplicate commit messages (same subject, seconds apart, one file each)

**Cursor (11 Aug 2026, this repo tip)**
- Re-added `rss3-comm-agent/` (YouTube live, GI feed fallback, membership docs)
- Docs claimed Aragamago lived in a separate `divine-cleric` repo (incorrect)
- Did **not** restore `rss3-comm-agent/package.json` from the 2025 branch (Maxayauwi cannot `npm start` without it)

### How to compare on the desktop

From the Antigravity / Windows tree, after any local work is committed or stashed:

```bat
git fetch origin
git checkout main
git pull origin main
git status
git diff
```

To see this reconciliation branch instead of `main`:

```bat
git fetch origin
git checkout cursor/reconcile-antigravity-codex-git-818f
git pull origin cursor/reconcile-antigravity-codex-git-818f
```

To keep using the Antigravity secrets file on Windows:

```bat
set ENV_PATH=C:\Users\Baba\Documents\antigravity\.env
```

### Still true on git (follow-ups)

- Root `node_modules/` (Supabase JS) is tracked; `rss3-comm-agent/.gitignore` already ignores `node_modules/`
- Root `.env` is tracked (empty `TELEGRAM_BOT_TOKEN`); public repo
- Orphaned 2025 branches were never merged into current `main`

---

## Initialization — 2026-03-09

- B.L.A.S.T. protocol initialized.
- Awaiting user Discovery answers to define project scope.
