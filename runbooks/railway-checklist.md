# Railway Checklist

Use this when Aragamago is deployed but not responding.

## 1. Confirm Variables

Paste the current local source of truth into Railway:

```bash
python3 tools/export_railway_env.py
```

The key list is section **2. ARAGAMAGO** of `.env.example` — don't maintain a copy here.
Required: `TELEGRAM_BOT_TOKEN` plus at least one of `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`.

## 2. Confirm Bot Startup

In Railway logs, look for:

- `Aragamago starting...`
- `Runtime config`
- `Aragamago is LIVE on Telegram`

## 3. Interpret Common Failures

- `TELEGRAM_BOT_TOKEN missing`: env problem
- `409 Conflict`: duplicate Telegram poller
- Gemini or OpenRouter auth errors: AI provider env or quota problem

## 4. Best Order To Debug

1. Fix `409 Conflict` first
2. Test plain text Telegram reply
3. Test Gemini reply
4. Test Tasks / Calendar / Sheets
