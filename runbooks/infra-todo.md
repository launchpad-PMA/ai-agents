# Infra Todo

Open work for Adbongo Group LLC: phone, GitHub, Railway, butler AI, domain, social, career.
State as of Oct 30, 2026. Work top to bottom.

## Where things live

| What | Where |
|------|-------|
| Main phone | Galaxy S26 (Android) — replaces the old iPhone |
| Glasses (coming) | Meta Ray-Ban Display |
| Code | GitHub org `launchpad-PMA`: `ai-agents`, `daomaker`, `docs`, `templates` — **all public** |
| Telegram bot (Aragamago) | Railway project `Root-Pool`, service `rss3-comm-agent` (misnamed) |
| Duplicate bot | Railway service `ai-agents` — last deploy FAILED |
| JARVIS voice PWA | Branch `cursor/jarvis-phase1-voice-prototype-ad5d` (PR #7), not deployed |
| `www.adbongo.io` | Substack (behind Cloudflare) |
| `adbongo.io` (bare) | GoDaddy domain forwarding — **HTTPS broken** |
| `web3.adbongo.io` | Linode `172.232.129.170`, nginx — serves `rss3-comm-agent/public/index.html` |
| RSS3 node | Same Linode — paused |
| DNS / registrar | GoDaddy |
| Email | Google Workspace |

---

## 1. PRIORITY — GitHub + Railway organized on the Galaxy

### On the phone

- [ ] Install **GitHub** (Play Store). Sign in, turn on notifications for PRs and reviews in `launchpad-PMA`.
- [ ] Chrome → `cursor.com/agents` → menu → **Add to Home screen** (Cursor Cloud Agents; no native Android app).
- [ ] Chrome → `railway.com` → **Add to Home screen** (no Android app).
- [ ] 2FA (authenticator or passkeys) on GitHub, Railway, Cursor, GoDaddy, Google before anything else.

### GitHub cleanup

- [ ] Decide public vs private for each repo. `ai-agents` holds bot code, infra notes, and runbooks;
      nothing is served from GitHub Pages, so making it **private** doesn't break the site.
- [ ] Protect `main`: require a PR, block force-push. Railway auto-deploys from `main`, so every merge ships.
- [ ] Turn on **Automatically delete head branches** (currently off).
- [ ] Merge or close open PRs:
  - [ ] #8 this todo list
  - [ ] #7 JARVIS Phase 1 + bot `/health` server (needed before the bot redeploy in section 6)
  - [ ] #6 Antigravity/Codex reconcile (Aug 14 — likely stale; review and close)
- [ ] Delete stale branches from closed/merged PRs: `cursor/debug-railway-deployment-healthcheck-failure-e4fc`,
      `cursor/distinguish-railway-agent-scope-from-vercel-deployment-e154`,
      `cursor/scan-public-repo-for-exposed-credentials-31b1`, `railway/code-change-Og0UQH`, `railway/fix-deploy-cd51a3`.
- [ ] Fix stale docs: `README.md` and `rss3-comm-agent/RAILWAY_URLS.md` still point at `divine-cleric`
      and `ai-agents-production-b0ef` (gone).

### Railway cleanup

- [ ] Rename project `Root-Pool` → `launchpad-agents`.
- [ ] Rename service `rss3-comm-agent` → `aragamago-telegram-bot` (renaming changes its `*.railway.internal` host).
- [ ] Service `ai-agents`: remove `TELEGRAM_BOT_TOKEN` or delete it. Two pollers on one token = `409 Conflict`
      (`telegram-409-recovery.md`).
- [ ] One service = one job = one root directory. Bot: repo root. Future RSS3/comm agent: `rss3-comm-agent/`.
- [ ] Add Railway deploy notifications (project webhook) → Telegram/phone, so failed deploys show up on the Galaxy.
- [ ] Keep a project-scoped Railway token for Cloud Agents (read-only work); never paste it in chat or git.

---

## 2. Galaxy S26 setup

### Move off the iPhone (in this order)

- [ ] Move **2FA / authenticator codes** first (export or re-enroll each account). Keep the iPhone until every login works.
- [ ] Update the phone number on Apple ID / other 2FA if the number moves.
- [ ] **Samsung Smart Switch** for contacts, photos, messages, call log.
- [ ] Chats: Telegram (just sign in), WhatsApp (iPhone → Android transfer), Signal (transfer during setup).
- [ ] Google Photos + Google Drive backup.
- [ ] Turn off iMessage/FaceTime before moving the SIM (or Apple's "Deregister iMessage" page).
- [ ] **Android Work profile** (or Secure Folder) to separate Adbongo business from personal.
- [ ] Wipe the iPhone only after everything above is confirmed.

### Apps

- [ ] Telegram (Aragamago), Meta AI app (pairs the glasses), Google Workspace apps.
- [ ] Social: X, Farcaster (formerly Warpcast), YouTube Studio, Substack.
- [ ] Password manager.
- [ ] Optional: Folo (RSS3's reader).

---

## 3. Butler AI (JARVIS) — one brain, every surface

Goal: one assistant that runs the day — briefings, tasks, calendar, email triage, social drafts,
infra health — reachable from phone, Telegram, voice, and glasses, with backups on home machines.

### Surfaces

| Surface | How |
|---------|-----|
| Telegram | Aragamago (already live) |
| Voice on the Galaxy | JARVIS PWA (PR #7) → Chrome → Add to Home screen |
| Meta Ray-Ban Display | **Web App** (HTML/JS over HTTPS, runs on the glasses) — reuse the JARVIS front end. Native option: Meta Wearables Device Access Toolkit 1.0 (Android) for camera/mic. |
| Coding work | Cursor Cloud Agents from the phone |

### Rules

- [ ] Reads are automatic; **every write/post/spend/delete needs an Approve tap** on phone or glasses.
- [ ] Audit log of every action in Supabase.
- [ ] Secrets live in Railway/host env and a password manager — never in git, chat, or the glasses app.

### Build order

- [ ] Merge PR #7, deploy JARVIS behind its access code (one Railway service).
- [ ] Replace JARVIS mock tools with real ones: Google Calendar/Tasks/Gmail (read), Railway status, site health.
- [ ] Morning briefing to Telegram + glasses: calendar, tasks, failed deploys, mentions.
- [ ] Glasses Web App: briefing card, approve/reject buttons, "next meeting", quick capture.
- [ ] Connect social drafting (section 4).

### Redundancy on your own computers

| Device | Role | Failover order |
|--------|------|----------------|
| Railway | Primary: bot + JARVIS + comm agent | 1 |
| Ubuntu desktop (likely `baba2-mainoffice`) | Always-on standby node: Docker copy of bot/JARVIS, nightly Supabase backup, local AI model fallback (e.g. Ollama) if cloud AI keys fail | 2 |
| Windows PC laptop (`C:\Users\Baba`) | Main work machine (Cursor desktop). WSL2 + Docker standby only while awake | 3 |
| Laptop (OS? — confirm) | Travel/dev machine; mesh member, no standby by default | — |
| Galaxy S26 | Control surface: approvals, voice, notifications, hosts the Meta AI app for the glasses | — |
| iPhone (old) | Keep as 2FA/recovery backup until the Galaxy move is confirmed; then wipe, or keep Wi-Fi-only for testing JARVIS on iOS | — |

- [ ] Confirm the second laptop's OS and which machines stay on 24/7.
- [ ] Install Tailscale (private mesh) on Ubuntu desktop, both laptops, and the Galaxy — no open ports at home.
- [ ] Ubuntu desktop: Docker + the same image as Railway, set to start on boot, standby mode.
- [ ] Remove hardcoded machine paths from code (`/home/baba2-mainoffice/...`, `C:\Users\Baba\...`) so the
      same image runs anywhere; config comes from env vars only.
- [ ] **Leader lock** in Supabase: only one copy polls Telegram at a time; the standby takes over when the
      primary's heartbeat stops. (Avoids `409 Conflict`.) Long term: switch Telegram to webhooks.
- [ ] State in Supabase (single source of truth) + nightly backup to a home node.
- [ ] External uptime check on `/health` → alert to phone.

---

## 4. Social media automation (draft → approve on phone → post)

| Channel | Status |
|---------|--------|
| Farcaster | `rss3-comm-agent/index.js` posts via Neynar. **Not deployed.** |
| YouTube | Live check + announce to Farcaster in `index.js`. Needs `YOUTUBE_API_KEY`, `YOUTUBE_CHANNEL_ID`. |
| X | Keys exist on Railway; **no code posts to X yet**. |
| Substack | No posting API — manual. |

- [ ] **Security first:** add a shared-secret check to `/api/farcaster/cast`, `/api/events`,
      `/api/youtube/announce` before deploying — today anyone who finds the URL could post.
- [ ] Deploy the comm agent as its own service (section 8).
- [ ] `/draft <topic>` in Aragamago/JARVIS → per-channel drafts → **Approve / Edit / Reject**.
- [ ] On Approve → comm agent (private URL + secret) → Farcaster; add X API v2 posting (check plan write limits).
- [ ] Log every post to Supabase. Later: scheduling, Substack cross-post reminders, YouTube live auto-announce.

---

## 5. Fix HTTPS on `adbongo.io`

`http://adbongo.io` 301s to `https://adbongo.io`, which fails the TLS handshake (no certificate),
so it never reaches `www`. No CAA record blocks issuance.

- [ ] GoDaddy → `adbongo.io` → DNS → **Forwarding**: forward to `https://www.adbongo.io`,
      **Permanent (301)**, **Forward only** (no masking).
- [ ] If it already exists and HTTPS still fails, delete and re-add it (re-triggers the certificate; allow 24–48 h).
- [ ] Verify:

  ```bash
  curl -sI http://adbongo.io/  | grep -i location   # expect https://www.adbongo.io/
  curl -sI https://adbongo.io/ | grep -i location   # expect https://www.adbongo.io/, no TLS error
  curl -sI https://www.adbongo.io/ | head -1        # expect 200
  ```

- [ ] Fallback: move DNS to Cloudflare (free) with a redirect rule `adbongo.io/*` → `https://www.adbongo.io/$1`.
      Re-create Google MX, Substack CNAME, `web3` A record, and ENS TXT first.

## 6. Telegram bot fixes

- [x] Rotate the Telegram bot token in BotFather (done Oct 30; old token revoked).
- [ ] Paste the **new** token into `TELEGRAM_BOT_TOKEN` on the bot service and click **Deploy** to apply.
      As of 1:50 PM CDT Oct 30 Railway still had the revoked token → `InvalidToken` crash loop.
- [ ] Remove `TELEGRAM_BOT_TOKEN` from the spare `ai-agents` service (it also holds the revoked token).
- [ ] Master copy of every secret in a password manager; local copy in
      `~/Documents/Obsidian Vault/Agents/Secrets/master.env` (outside git, `chmod 600`,
      vault folder not synced anywhere public).
- [ ] Stop logging the token: set the `httpx` logger to `WARNING` in `agents/aragamago/bot.py`.
- [ ] Redeploy after PR #7 merges so `/health` answers (live deploy is `9d1b5f8`; public URL returns 502).
- [ ] Replace `pinecone-client` with `pinecone` in `requirements.txt` ("Brain not available").
- [ ] `OPENAI_API_KEY` holds an OpenRouter key (`sk-or-…`): add a real OpenAI key or drop `openai`
      from `AI_PROVIDER_ORDER`.

## 7. RSS3 (checked Oct 30, 2026)

- RSS3 retired its VSL chain (Apr 24, 2026) and moved `$RSS3` to Ethereum (complete Apr 30);
  `$POWER` converted 23:1. Source: `rss3.io/blog/the-next-stage-of-rss3.html`.
- **No new Ethereum node to run.** DSL is being folded into RSSHub; `rss3-network/node` is still
  v2.0.1 (Apr 2025). DSL operators' earned rewards are covered by an on-chain snapshot.
- [ ] Claim migrated `$RSS3` at `rss3.io/migration` with the operator/staking wallet. Connect the
      wallet only — never type a seed phrase into any site.
- [ ] Keep node containers stopped. Don't delete the Linode — it serves `web3.adbongo.io`.
- [ ] Remove `NODE_CONFIG_*`, `NODE_DATABASE_URL`, `RSS3_ACCESS_TOKEN` from the bot when `/rss3status` is retired.

## 8. Comm agent on Railway (when needed)

- [ ] Add `rss3-comm-agent/package.json` (`express`, `body-parser`, `axios`, `dotenv`).
- [ ] New service, Root Directory `rss3-comm-agent`, start `node index.js`.
- [ ] Only its own vars (`NEYNAR_*`, `YOUTUBE_*`, `PUBLIC_AGENT_URL`, post secret) — no Telegram token.

## 9. Legal engineer career path

- [ ] Bar admission status / next steps.
- [ ] Portfolio: LexClinic AI as the flagship, with UPL/ethics guardrails (attorney review before advice).
- [ ] Skills to show: document automation (e.g. Docassemble), contract templates (`launchpad-PMA/templates`),
      Python/JS automation, AI with human review.
- [ ] Update LinkedIn / Adbongo bio: JD, legal engineer, Adbongo founder.
- [ ] Communities: Legal Hackers, Stanford CodeX, local bar tech committee.
- [ ] Target roles: legal engineer, legal ops / legal tech product, innovation counsel.

## 10. Later: Regen Civics + LexClinic AI

- [ ] Get the Regen Civics GitHub org/repo URL (not found under `launchpad-PMA` or GitHub search)
      and give Cursor Cloud Agents access.
- [ ] Locate the LexClinic AI repo/host; `launchpad-PMA/templates` holds LexClinic templates.
- [ ] Least-privilege connection to the butler; no client data in the Telegram bot.
