# Aragamago operations

Checked Oct 31, 2026, 10:36 AM CT. This page is documentation. It does not change Railway, tokens, DNS, or the running container.

PR #7 is merged. Aragamago is answering. Leave the current deployment in place until Baba approves a later change.

Company and repo checklists live in the Google Tasks list named Master. This file is how to run the bot. It is not that master list. The existing 15 Google Task lists were left as they were. `/tasks` still reads `Projects list`.

Merging this file onto `main` is not free. Railway rebuilds the bot on every push to `main`. That rebuild replaces the container that is answering now. Do not merge until that rebuild is an accepted step.

## 1. Known-good checkpoint, smoke tests, and rollback

### Known-good

| Item | Value |
|------|--------|
| `main` | `8d0b3326f0ba6e797d8eff1f12a587b6d3d206bf` |
| What that commit is | Merge of PR #7, 9:52 AM CT Oct 31, 2026 |
| Railway project | `Root-Pool` (`1b7ddd13-9d51-445b-8561-f338444f29b7`) |
| Environment | `production` |
| Service | `aragamago-telegram` (`1135865f-bd02-409b-a330-fefe4f59efc5`) |
| Public URL | `https://rss3-comm-agent-production.up.railway.app/health` |
| Running deployment | `9981cc0b-4daf-404d-af8f-32e9bb46bf37` |
| Deployment created | 10:29 AM CT Oct 31, 2026, status `SUCCESS` |
| How it was shipped | Railway CLI upload. It has no git commit attached. |
| Process | Dockerfile, one replica, `python agents/aragamago/bot.py` |
| Health at 10:36 AM CT | HTTP 200, `ok: true`, `telegram_configured: true`, `polling: true`, `mode: bot+health` |

The CLI image is newer than `main`. It includes reply logging, direct Google Tasks and Calendar answers, and the ElevenLabs package from PR #9, which is not merged. Railway variables are separate from the image. They already include `OPENROUTER_MODEL=openrouter/free`, `AI_PROVIDER_ORDER=openrouter,gemini`, and `GEMINI_MODEL=gemini-3.5-flash`. A GitHub deploy of `main` keeps those variables and drops the unmerged code.

Last GitHub deployment of PR #7, now removed because the CLI upload replaced it: `08b045a2-6a4f-4e77-9bfb-74ce27377320` on commit `8d0b332`.

### Smoke tests

Read-only health check:

```bash
curl -fsS https://rss3-comm-agent-production.up.railway.app/health
```

Pass: HTTP 200 and JSON with `"ok": true`, `"polling": true`, `"telegram_configured": true`.

Tests that do not call Telegram or OpenRouter, from a checkout of `main`:

```bash
PYTHONPATH=. python3 -m unittest tests.test_aragamago_health tests.test_chat_memory tests.test_provider_keys tests.test_log_safety
```

Pass: all of those tests succeed.

Live Telegram check, one person, after any future deploy:

1. Send a short text. A reply arrives, or the bot's own "not responding" message if both OpenRouter and Gemini refuse.
2. Send a second text that refers to the first. The reply shows it still has that turn.
3. Railway logs show one `409 Conflict` at most, during container handoff, and no further `409` after 30 seconds.

### Rollback

Do not roll back as part of this document.

1. Open the `aragamago-telegram` service in Railway. Use **Redeploy** on `9981cc0b-4daf-404d-af8f-32e9bb46bf37`. Do not deploy the latest GitHub commit.
2. If that deployment cannot be redeployed, redeploy `08b045a2-6a4f-4e77-9bfb-74ce27377320` (PR #7 on `main`). Variables stay. Unmerged CLI-only code does not.
3. Run the health check and the two Telegram messages before calling the rollback done.

## 2. Telegram-to-OpenRouter tests

There is no automated test yet that sends a Telegram update through to OpenRouter. This document does not add one. A later code change should add tests that use fakes, not the live bot and not the live key.

The test has to cover both outcomes:

| Case | Expected |
|------|----------|
| OpenRouter returns a normal completion | The handler returns that text and records the user turn and the assistant turn |
| OpenRouter returns 429 | At most two retries, then the next provider in `AI_PROVIDER_ORDER` |
| OpenRouter returns 402 or another payment error | Stop. Do not switch to a paid model and do not buy credits |
| OpenRouter is down and Gemini can answer | The reply still arrives |
| Both providers fail | The user gets the explicit unavailable message, and the process stays up |

Manual stand-in, already used Oct 31: "Yo" and "Are you working now" each got an OpenRouter HTTP 200 after one or two 429s. A third text, "Can you connect to google", stayed on 429 and did not get an OpenRouter completion. That was a free-pool limit, not a broken token.

## 3. Conversation memory beyond 12 in-process turns

What PR #7 shipped, and what is running:

- The transcript is a `deque` in the bot process, `maxlen` 12 (`agents/aragamago/chat_memory.py`).
- A text reply inserts the last 5 turns. A voice reply inserts the default 6.
- A new Railway deploy or crash drops the whole transcript.
- Supabase is not on this path. Pinecone is not written on a normal chat turn. Obsidian notes were tried and removed.

Required next design, not part of this PR:

- Store the transcript somewhere that survives a restart.
- A missing or failing store must not block the reply (section 4).
- The store is not Supabase-only, Pinecone, or an Obsidian vault. Those can be extra copies later.
- More than 12 turns have to be available to the next reply after a restart.
- One replica only, until the store can be shared. Two replicas would each keep a different deque.

## 4. Replies when Supabase, Pinecone, or Obsidian fails

A normal text must still get a model reply when all three are down.

Current behavior on the merged bot:

- Chat history does not call Supabase. A dead `SUPABASE_URL` logs a warning and is skipped.
- Pinecone failing logs `Brain not available`. `/memory` and `/save` fail. Ordinary chat still runs.
- Obsidian is not called.

Do not add a Supabase leader lock, audit log, or chat write that the reply waits on. A later memory store has to time out and continue with the current message.

## 5. Free-model preference, bounded retries, paid usage

- Prefer `openrouter/free`. A non-empty `OPENROUTER_MODEL` wins over `AI_MODEL`. The word `openrouter` in `AI_MODEL` is the provider name, not a model slug.
- Live order is `openrouter`, then `gemini`. Gemini uses `gemini-3.5-flash`. Direct OpenAI is off because the key in `OPENAI_API_KEY` is an OpenRouter key.
- On HTTP 429 the client retries twice (`retry 1 of 2`, `retry 2 of 2`) and then the next provider runs.
- Buying OpenRouter credits, raising `max_tokens`, or changing `OPENROUTER_MODEL` to a paid slug needs Baba's explicit approval. This PR does not do that.

## 6. Telegram token rotation and redacted logs

The bot is answering, so Telegram is accepting the token on `aragamago-telegram`. This PR does not rotate it and does not print it.

PR #7 already stops new leaks:

- `httpx` and `httpcore` log at `WARNING`.
- A filter rewrites `/bot<id>:<token>` to `/bot<redacted>`.
- `tests.test_log_safety` checks that filter.

Logs from before that filter can still hold a token. Treat old log exports as secrets.

Rotation, only when Baba asks for it:

1. BotFather `/token` or `/revoke` for this bot.
2. Put the new value in `TELEGRAM_BOT_TOKEN` on `aragamago-telegram` only.
3. Put the same value in the password manager and in `master.env` (outside git, mode `600`).
4. Redeploy that one service.
5. Run the smoke tests in section 1.
6. Confirm no other machine and no other Railway service still has the old token. A second poller is a `409`.

## 7. One JARVIS backend, one Telegram poller

One service answers Telegram, and later the Galaxy and the glasses. Those surfaces are clients. They do not run `bot.py`.

| Surface | Role now |
|---------|----------|
| Telegram | The only poller. Service `aragamago-telegram`, `numReplicas` 1 |
| Galaxy S26 | Chrome → `cursor.com/agents` → Add to Home screen. Not a second bot |
| Meta glasses | Not connected. A later web client of the same backend |
| JARVIS PWA in `jarvis/` | Prototype. `railway.toml` does not start it |
| Laptop or desktop | Do not run `agents/aragamago/bot.py` while Railway holds the token |

A `409` in the first few seconds of a deploy is the old container and the new one overlapping. A `409` that continues means a second poller. Stop the extra process. Do not solve that with a second token, and do not solve it with a Supabase lock that chat depends on.

## 8. Backup and restore

What exists today:

| Data | Backup |
|------|--------|
| Code on `main` | Git, commit `8d0b332` |
| Running image | Railway deployment `9981cc0b-4daf-404d-af8f-32e9bb46bf37` |
| Railway variable names | `.env.example` section 2. Values stay in Railway, the password manager, and `master.env` |
| Chat transcript | None. It lives in RAM and dies on restart |
| Google Tasks and Calendar | Google's own account, not this repo |

Backup procedure, when Baba asks. Do not run it for this PR.

1. Record `git rev-parse origin/main` and the active Railway deployment id.
2. From a trusted machine, run `python3 tools/export_railway_env.py` and store the output in the password manager. Do not commit it.
3. Copy `master.env` to the password manager. Keep it out of the Obsidian sync if that vault is shared.

Restore procedure:

1. Redeploy the known-good deployment id from section 1. Do not type tokens into git or chat.
2. If variables were wiped, paste them from the password manager into that one service, then redeploy once.
3. Run the health check and the two Telegram messages.
4. Expect the chat transcript from before the restart to be gone until section 3 is built.

## 9. Verification of RSS3 and infrastructure claims

Checked read-only on Oct 31, 2026. Nothing here was changed.

| Claim | Result |
|-------|--------|
| PR #7 is on `main` | Confirmed. `8d0b332`, 9:52 AM CT |
| Bot health URL responds | Confirmed. HTTP 200, polling true, 10:36 AM CT |
| Only one Railway service in this project | Confirmed earlier Oct 31. Service name is `aragamago-telegram`. The hostname still says `rss3-comm-agent-production`. No second service was visible to rename or delete |
| `https://www.adbongo.io/` | HTTP 200, Cloudflare, Substack |
| `http://adbongo.io/` | 301 to `https://adbongo.io/` |
| `https://adbongo.io/` | TLS handshake failure. The bare-domain certificate problem is still real |
| `web3.adbongo.io` | DNS `172.232.129.170`. HTTPS returns 200 from nginx. HTML `last-modified` Aug 23, 2026 |
| RSS3 VSL halted and assets moved toward Ethereum | Confirmed from public pages, not from a wallet. [The Next Stage of RSS3](https://rss3.io/blog/the-next-stage-of-rss3.html) describes the VSL and DSL migration, a 23:1 `$POWER` conversion, and a DSL operator snapshot. [rss3.io/migration](https://rss3.io/migration/) says VSL assets have been migrated to Ethereum. L2BEAT records the VSL halt on Apr 24, 2026. A completion post dated Apr 30, 2026 is quoted by a third-party mirror. This check did not connect a wallet, did not claim tokens, and did not prove the Linode node is stopped |
| `ai-agents-production-b0ef.up.railway.app` | Previously 404. Not rechecked as a deploy target. Do not point the bot at it |
| Duplicate Railway service `ai-agents` holding a token | Not found in the visible project. Do not delete `aragamago-telegram` trying to remove it |

## 10. Acceptance criteria

This document passes when all of the following are true. The live bot already meets the rows marked pass. The rows marked open are the next build, not a reason to redeploy now.

| # | Check | How to measure | Oct 31 |
|---|--------|----------------|--------|
| 1 | Known-good deploy is recorded and still the one running | Deployment id `9981cc0b-4daf-404d-af8f-32e9bb46bf37` is `SUCCESS` and health is 200 | Pass |
| 2 | Health smoke test | `curl` in section 1 returns `"polling": true` | Pass |
| 3 | Offline unit tests | The four `unittest` modules in section 1 pass on `main` | Pass on the merged code. Not re-run for this doc edit |
| 4 | Two live texts get replies | Second reply can use the first turn | Pass before the 10:29 AM CT image. Re-check after any future deploy |
| 5 | OpenRouter failure test exists and uses fakes | Section 2 table is implemented under `tests/` without live keys | Open |
| 6 | Transcript survives a restart and holds more than 12 turns | Restart the service, ask it for a turn from before the restart | Open. Today it forgets on restart |
| 7 | Supabase, Pinecone, and Obsidian can fail | Logs may warn. A text still gets a model reply | Pass for the merged chat path |
| 8 | Free model and bounded retries | First request is `openrouter/free`. A 429 shows at most two retries, then Gemini. No paid slug | Pass for the live variables |
| 9 | Paid use stays gated | No credit purchase and no paid model change without Baba's yes | Pass. This PR does not buy anything |
| 10 | New logs hide the bot token | `tests.test_log_safety` and no `/bot<id>:<token>` in new lines | Pass in PR #7 code |
| 11 | One poller | `numReplicas` is 1, and a `409` does not continue past the deploy handoff | Pass at 10:36 AM CT, after one handoff error |
| 12 | Galaxy and glasses are not pollers | No `bot.py` on the phone or glasses | Pass. They are not connected |
| 13 | Restore path is written down | Section 8 names the deployment to redeploy and says the transcript is not in the backup | Pass as documentation |
| 14 | Infrastructure claims match section 9 | Re-run the read-only checks. Bare `https://adbongo.io/` still fails TLS | Pass for the checks above |
