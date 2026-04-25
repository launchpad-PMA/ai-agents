# Telegram 409 Recovery

This runbook is for the Railway deployment case where Aragamago starts but Telegram returns:

- `409 Conflict: terminated by other getUpdates request`

That error means the bot token is valid, but more than one process is polling Telegram with the same token.

## What We Already Confirmed

- Local secrets contain a valid `TELEGRAM_BOT_TOKEN`
- Local secrets contain a valid `GEMINI_API_KEY`
- The bot code reads both values correctly
- No local Python process in this workspace is polling Telegram right now

## Most Likely Causes

- Another Railway service or environment is still running the same bot token
- Another machine is running an older local bot session
- A second deployment was created from a backup or duplicate repo

## Fastest Fix

1. Open Railway and find every service that could be running Aragamago.
2. In each service, open logs and search for `getUpdates` or `409 Conflict`.
3. Stop or delete every duplicate service except the one you want to keep.
4. Redeploy only the primary Aragamago service.
5. Send the bot a plain text Telegram message and confirm it replies.

## If You Cannot Find The Duplicate

Rotate the Telegram bot token in BotFather, then update only the primary service:

1. In Telegram, open BotFather.
2. Run `/token`.
3. Select the Aragamago bot.
4. Copy the new token.
5. Update `TELEGRAM_BOT_TOKEN` in Railway.
6. Update `Secrets/master.env` locally.
7. Redeploy Railway.

This invalidates any hidden old poller immediately.

## Recommended Railway Checks

- Verify only one Railway project has the Aragamago variables
- Verify preview/staging environments are not also starting the bot
- Verify no old service still points at the same repository
- Verify the latest deployment has the current env vars, not stale ones

## Useful Local Command

From the repo root:

```bash
python3 tools/export_railway_env.py
```

That prints the exact env block to paste into Railway Raw Editor.
