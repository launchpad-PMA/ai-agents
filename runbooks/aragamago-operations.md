# Aragamago operations

Checked Oct 31, 2026, 11:18 AM CT. This page is documentation. It does not change Railway, tokens, DNS, or the running container.

PR #7, PR #9, and PR #8 are on `main`. Aragamago is answering. The running image is commit `968ddf2`.

Company and repo checklists live in the Google Tasks list named Master. This file is how to run the bot. It is not that master list. The existing 15 Google Task lists were left as they were. `/tasks` still reads `Projects list`.

A change that only edits this file does not match the service watch paths, so merging it should not build a new image. See "Documentation does not redeploy" below. Do not merge this update until Baba says so. After it merges, the newest deployment should still be `adf62e8f-8c0f-4e87-9d35-0253cae92618`.

## 1. Known-good checkpoint, smoke tests, and rollback

### Known-good

| Item | Value |
|------|--------|
| `main` | `968ddf25c554f461a618793612d128285430d447` |
| What that commit is | Merge of PR #8, 10:57 AM CT Oct 31, 2026. It contains the PR #9 bot (`117125f`, 10:38 AM CT) and the PR #7 merge (`8d0b332`, 9:52 AM CT) |
| Railway project | `Root-Pool` (`1b7ddd13-9d51-445b-8561-f338444f29b7`) |
| Environment | `production` |
| Service | `aragamago-telegram` (`1135865f-bd02-409b-a330-fefe4f59efc5`) |
| Public URL | `https://rss3-comm-agent-production.up.railway.app/health` |
| Running deployment | `adf62e8f-8c0f-4e87-9d35-0253cae92618` |
| Deployment created | 11:17 AM CT Oct 31, 2026, status `SUCCESS` |
| Image | `sha256:52c1442ea30fb6a2706ac1d2c5b72229896bc8b4d18438502d2da153ed915f39` |
| How it was shipped | Same commit and same image as `502d99e5`. Saving the service watch paths redeployed that image. It did not compile a different image |
| Process | Dockerfile, one replica in `us-east4`, `python agents/aragamago/bot.py` |
| Runtime config at start | `ProviderOrder=openrouter,gemini`. OpenRouter, Gemini, ElevenLabs, and Telegram are set. Direct OpenAI is off |
| Health at 11:18 AM CT | HTTP 200, `ok: true`, `telegram_configured: true`, `polling: true`, `mode: bot+health` |
| Handoff | One Telegram `409` at 11:17 AM CT. The logs after that do not show a second `409` |

Railway variables are separate from the image. The live names are `OPENROUTER_MODEL=openrouter/free`, `AI_PROVIDER_ORDER=openrouter,gemini`, and `GEMINI_MODEL=gemini-3.5-flash`. `AI_MODEL` is unset.

Same image, previous deployment, removed and still redeployable: `502d99e5-07ed-4f9b-822d-3e3a5b6de45f`. Created 10:57 AM CT, commit `968ddf2`, digest `sha256:52c1442ea30fb6a2706ac1d2c5b72229896bc8b4d18438502d2da153ed915f39`. `canRedeploy` and `canRollback` are both true.

Previous different image, the PR #9 GitHub deploy: `7ddd8f0f-c396-4666-b2f9-65c9a74db5b4`. Created 10:38 AM CT, commit `117125f`, digest `sha256:ce5801440ecc1f4683f509a20b50eff2d7b1c1531ab746e7f3b125316a9b80a5`. Status `REMOVED`. `canRedeploy` and `canRollback` are both true.

### Documentation does not redeploy

Service `build.watchPatterns` on production, saved at 11:17 AM CT:

- `/agents/**`
- `/connectors/**`
- `/requirements.txt`
- `/Dockerfile`
- `/railway.toml`
- `/runtime_env.py`
- `/tools/**`
- `/.dockerignore`

Railway creates a deployment only when a push to `main` changes one of those paths. These do not create one:

- `runbooks/`
- `TODO.md`
- `tests/`
- `docs/`
- `jarvis/`
- `rss3-comm-agent/`
- `vercel.json`
- other markdown

`railway.toml` does not list watch patterns. The service setting is what skips creating a deployment. A deployment that has already started still reads `railway.toml` for the builder, Dockerfile path, start command, and restart policy. Those file values override the dashboard for that deployment only. Editing `railway.toml` matches a watch path, so that commit deploys once. Do not add watch patterns to `railway.toml` inside a documentation commit.

Saving the service setting committed environment config, and Railway redeployed the current commit. That is why the running id changed from `502d99e5` to `adf62e8f` with the same image digest. A later markdown merge should not do that again.

This file is the check. After Baba merges it, the deployment list should still show `adf62e8f` as the newest deployment. A newer row means the watch paths did not skip the push.

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

Do not roll back as part of this document. The ids below were queried read-only on Oct 31, 2026, 11:18 AM CT. `deploymentRedeploy` was not called. `railway deployment redeploy` with no id restarts the latest deployment and can cause another `409`. Do not use that command to reach an older id.

1. To return to the image that is running now, redeploy `adf62e8f-8c0f-4e87-9d35-0253cae92618` from the Railway deployment page. The same image is also `502d99e5-07ed-4f9b-822d-3e3a5b6de45f`.
2. To return to the PR #9 image from before the documentation merge, redeploy `7ddd8f0f-c396-4666-b2f9-65c9a74db5b4`. Variables stay. That digest is `sha256:ce5801440ecc1f4683f509a20b50eff2d7b1c1531ab746e7f3b125316a9b80a5`.
3. Run the health check and the two Telegram messages before calling the rollback done.

`adf62e8f`, `502d99e5`, and `7ddd8f0f` each reported `canRedeploy: true` and `canRollback: true`.

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
| Code on `main` | Git, commit `968ddf2` |
| Running image | Railway deployment `adf62e8f-8c0f-4e87-9d35-0253cae92618`, digest `sha256:52c1442ea30fb6a2706ac1d2c5b72229896bc8b4d18438502d2da153ed915f39` |
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
| PR #7, PR #9, and PR #8 are on `main` | Confirmed. `8d0b332` at 9:52 AM CT, `117125f` at 10:38 AM CT, `968ddf2` at 10:57 AM CT |
| Bot health URL responds | Confirmed. HTTP 200, polling true, 11:18 AM CT, after the watch-path redeploy |
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
| 1 | Known-good deploy is recorded and still the one running | Deployment id `adf62e8f-8c0f-4e87-9d35-0253cae92618` is `SUCCESS`, image digest matches `502d99e5`, and health is 200 | Pass at 11:18 AM CT |
| 2 | Health smoke test | `curl` in section 1 returns `"polling": true` | Pass at 11:18 AM CT |
| 3 | Offline unit tests | The four `unittest` modules in section 1 pass on `main` | Pass on the merged code. Not re-run for this doc edit |
| 4 | Two live texts get replies | Second reply can use the first turn | Not re-sent after the 11:17 AM CT restart. A photo at 11:12 AM CT got HTTP 429 from OpenRouter and from Gemini and did not get a reply |
| 5 | OpenRouter failure test exists and uses fakes | Section 2 table is implemented under `tests/` without live keys | Open |
| 6 | Transcript survives a restart and holds more than 12 turns | Restart the service, ask it for a turn from before the restart | Open. Today it forgets on restart |
| 7 | Supabase, Pinecone, and Obsidian can fail | Logs may warn. A text still gets a model reply | Pass for the merged chat path |
| 8 | Free model and bounded retries | First request is `openrouter/free`. A 429 shows at most two retries, then Gemini. No paid slug | Pass for the live variables |
| 9 | Paid use stays gated | No credit purchase and no paid model change without Baba's yes | Pass. This PR does not buy anything |
| 10 | New logs hide the bot token | `tests.test_log_safety` and no `/bot<id>:<token>` in new lines | Pass in PR #7 code |
| 11 | One poller | `numReplicas` is 1, and a `409` does not continue past the deploy handoff | Pass at 11:18 AM CT. One handoff `409` at 11:17 AM CT, then none |
| 12 | Galaxy and glasses are not pollers | No `bot.py` on the phone or glasses | Pass. They are not connected |
| 13 | Restore path is written down | Section 8 names the deployment to redeploy and says the transcript is not in the backup | Pass as documentation |
| 14 | Infrastructure claims match section 9 | Re-run the read-only checks. Bare `https://adbongo.io/` still fails TLS | Pass for the checks above |
