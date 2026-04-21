# Runbook: Deploying Aragamago to Railway

This guide walks you through deploying the Aragamago Telegram bot to Railway.app so it runs 24/7.
All the necessary configuration files (`Dockerfile`, `railway.toml`, `requirements.txt`) have already been created for you.

## 1. Create the Railway Project
1. Go to [railway.app](https://railway.app) and log in.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your `aragamago` repository.
4. Railway will automatically detect the `Dockerfile` and `railway.toml` and start configuring the build.

## 2. Add Environment Variables
The bot needs its API keys to function. It will crash until these are provided.
1. In your Railway project, click on the **Aragamago** service.
2. Go to the **Variables** tab.
3. Click **Raw Editor** or add them one by one. You need to add the following keys from your local `.env`:
   - `TELEGRAM_BOT_TOKEN`
   - `GEMINI_API_KEY`
   - `OPENROUTER_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_PUBLISHABLE_KEY`
   - `SUPABASE_SECRET_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_HOST`
   - `PINECONE_INDEX_NAME`
   - `GOOGLE_SERVICE_ACCOUNT_JSON`
   - `GOOGLE_SHEET_ID`

Optional, depending on features you want enabled:

- `GOOGLE_SHEET_URL` if you prefer to store the full Google Sheets link instead of only the raw ID
- `GOOGLE_TOKEN_JSON` for Google Tasks and Calendar access
- `GOOGLE_CREDENTIALS_JSON` if you need to generate a fresh `GOOGLE_TOKEN_JSON`
- `GOOGLE_CALENDAR_ID` if not using the default `primary` calendar
- `ELEVENLABS_VOICE_ID` if you want a configurable voice ID later

Notes:

- Sheets can run with a service account.
- Google Tasks and Google Calendar currently require OAuth user credentials via `GOOGLE_TOKEN_JSON`.
- Do not set `ENV_PATH` on Railway; Railway should inject the actual variables directly.

## 3. Deploy
1. Once the variables are added, Railway should automatically trigger a new deployment.
2. If it doesn't, click the **Deploy** button manually.
3. Wait for the build process to finish.

## 4. Verify
1. Go to the **Deployments** tab and click on the latest successful deployment.
2. Click on **View Logs** to open the deployment logs.
3. You should see Python output indicating the bot has started (e.g. `Application started`).
4. Send a message to Aragamago on Telegram to verify it's responsive!
