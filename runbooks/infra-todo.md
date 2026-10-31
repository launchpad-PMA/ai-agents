# Infra Todo

Open work for Adbongo Group LLC: phone, GitHub, Railway, butler AI, domain, social, career.
State corrected Oct 31, 2026, 10:36 AM CT.

PR #7 is merged and Aragamago is answering. Do not redeploy, rotate the Telegram token, rename the Railway service, or delete a service from this list. Those steps would replace the working bot. The checkpoint, smoke tests, rollback, and acceptance criteria are in `runbooks/aragamago-operations.md`.

## Where things live

| What | Where |
|------|-------|
| Main phone | Galaxy S26 (Android) — replaces the old iPhone |
| Glasses (coming) | Meta Ray-Ban Display |
| Code | GitHub org `launchpad-PMA`: `ai-agents`, `daomaker`, `docs`, `templates` — **all public** |
| Telegram bot (Aragamago) | Railway project `Root-Pool`, service `aragamago-telegram`. Public host is still `rss3-comm-agent-production.up.railway.app`. One replica. Health was HTTP 200 at 10:36 AM CT Oct 31 |
| Duplicate bot | Not visible in that project on Oct 31. Do not delete `aragamago-telegram` |
| JARVIS voice PWA | In `jarvis/` on `main` after PR #7. Not the process Railway starts |
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
  - [x] #7 JARVIS Phase 1 + bot `/health` — merged 9:52 AM CT Oct 31 (`8d0b332`)
  - [ ] #8 this todo list — documentation only. Merging it to `main` makes Railway rebuild the bot. See `aragamago-operations.md` before merging
  - [ ] #6 Antigravity/Codex reconcile (Aug 14 — likely stale; review and close)
- [ ] Delete stale branches from closed/merged PRs: `cursor/debug-railway-deployment-healthcheck-failure-e4fc`,
      `cursor/distinguish-railway-agent-scope-from-vercel-deployment-e154`,
      `cursor/scan-public-repo-for-exposed-credentials-31b1`, `railway/code-change-Og0UQH`, `railway/fix-deploy-cd51a3`.
- [ ] Fix stale docs: `README.md` and `rss3-comm-agent/RAILWAY_URLS.md` still point at `divine-cleric`
      and `ai-agents-production-b0ef` (gone).

### Railway cleanup

Do not rename or delete the working service. The bot that is answering is `aragamago-telegram` in project `Root-Pool`. Its public hostname still contains `rss3-comm-agent`. Renaming it changes hosts and forces a new deploy.

- [ ] Leave `aragamago-telegram` running. A rename is a later, approved change, not part of this document.
- [ ] If a second service with `TELEGRAM_BOT_TOKEN` ever shows up, remove that token. Two pollers on one token return `409 Conflict` (`telegram-409-recovery.md`). None was visible Oct 31.
- [ ] One service = one job = one root directory. Bot: repo root. A future comm agent would be its own service with root `rss3-comm-agent/`, and it must not get the Telegram token.
- [ ] Add Railway deploy notifications (project webhook) → phone, so a failed deploy shows up on the Galaxy.
- [ ] Keep a project-scoped Railway token for Cloud Agents. Never paste it in chat or git.

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

- [ ] Reads are automatic. Every write, post, spend, or delete needs an Approve tap on the phone or glasses.
- [ ] A chat reply must still go out when Supabase, Pinecone, and Obsidian are down (`aragamago-operations.md` section 4). Do not make the reply wait on a Supabase audit log.
- [ ] Secrets live in Railway and a password manager. Never in git, chat, or the glasses app.
- [ ] Paid model changes and OpenRouter credit purchases need Baba's explicit yes.

### Build order

- [x] Merge PR #7. The Telegram bot is the live service. The JARVIS PWA is not deployed.
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
- [ ] One Telegram poller, without a Supabase lock. Today that means `numReplicas` 1 on `aragamago-telegram` and no local `bot.py`. A standby may exist only after it cannot poll until the primary has stopped. Chat must still answer if Supabase is down.
- [ ] Nightly backup of secrets and the git commit, as in `aragamago-operations.md` section 8. The chat transcript is not in that backup yet.
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

The Oct 30 crash-loop notes are historical. On Oct 31 the bot is answering and `/health` is HTTP 200. Do not paste a token or click Deploy from this section.

- [x] PR #7 merged. `httpx` is at `WARNING`, and new logs redact `/bot<id>:<token>`.
- [x] `/health` answers on `https://rss3-comm-agent-production.up.railway.app/health`.
- [ ] Token rotation stays a separate approved step. Procedure: `aragamago-operations.md` section 6. Old logs from before the filter can still contain a token. Treat them as secrets.
- [ ] Master copy of every secret in a password manager. Local copy in `master.env` outside git, mode `600`.
- [ ] Pinecone still logs `Brain not available` because `requirements.txt` has `pinecone-client`. Chat does not need it. Change that package only in a later approved deploy.
- [ ] `OPENAI_API_KEY` is an OpenRouter-shaped key, and the live provider order does not call OpenAI with it. Leave it until a paid-key change is approved.

## 7. RSS3 (rechecked Oct 31, 2026)

Public sources agree on the migration story. This check did not connect a wallet, did not claim tokens, and did not prove the Linode process is stopped. Details and the other infrastructure checks are in `aragamago-operations.md` section 9.

- [The Next Stage of RSS3](https://rss3.io/blog/the-next-stage-of-rss3.html) says VSL hands over to Ethereum, DSL folds into RSSHub, `$POWER` converts at 23:1, and DSL operator rewards are covered by an on-chain snapshot.
- [rss3.io/migration](https://rss3.io/migration/) says VSL assets have been migrated to Ethereum.
- L2BEAT records the VSL halt on Apr 24, 2026. A third-party mirror quotes a completion post dated Apr 30, 2026.
- [ ] Claim migrated `$RSS3` only from `rss3.io/migration`, and only when Baba chooses to. Connect the wallet. Never type a seed phrase into a site, and do not do it from this PR.
- [ ] `web3.adbongo.io` answered HTTPS 200 from nginx on Oct 31 (DNS `172.232.129.170`). Do not delete that machine from this list.
- [ ] Leave `NODE_*` and `RSS3_ACCESS_TOKEN` on the bot until `/rss3status` is retired in an approved change. Removing them is a production edit.

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
