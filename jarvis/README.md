# JARVIS prototype

Android-friendly PWA. API secrets stay in server env vars.

```bash
JARVIS_ACCESS_CODE='choose-a-code' node server/index.js
```

Defaults to port `8787`. Open the URL in Chrome on the Galaxy S26, allow the microphone, then **Add to Home screen**.

Tests:

```bash
node --test test/*.test.js
```
