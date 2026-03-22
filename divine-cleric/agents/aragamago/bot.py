"""
Aragamago — Telegram Bot (Phase 2: Link)
Sacred Library Guardian / Prime Orchestrator
Reads token from .env, listens for messages, replies via OpenAI.
If no OPENAI_API_KEY is set, falls back to a smart canned response.
"""

import os
import sys
import logging
import base64
import threading
import time
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

# Move logger definition to the top for early diagnostics
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ── Load env ───────────────────────────────────────────────────────────────────
from dotenv import load_dotenv, find_dotenv

def _load_env():
    # Load .env relative to the project root
    load_dotenv(find_dotenv())
    
    # Only try absolute Windows paths if running locally on Windows
    if os.name == 'nt':
        load_dotenv(r"C:\Users\Baba\Documents\antigravity\.env", override=True) # App config
        load_dotenv(r"C:\Users\Baba\.env", override=True) # Global config
    
_load_env()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
# Allow ANY OpenRouter model (e.g. anthropic/claude-3.5-sonnet, google/gemini-2.0-flash, etc.)
AI_MODEL = os.environ.get("AI_MODEL", "openai/gpt-4o-mini").strip()

if not TELEGRAM_TOKEN:
    logger.error("❌ CRITICAL: TELEGRAM_BOT_TOKEN IS MISSING!")
    time.sleep(30)
    raise ValueError("TELEGRAM_BOT_TOKEN missing from environment or .env")

import io

# ── Dynamic Soul Identity ───────────────────────────────────────────────────
def _get_soul() -> str:
    # Use relative path for the container, fallback to absolute for local Windows
    soul_filename = "SOUL.md.txt"
    soul_paths = [
        soul_filename,
        os.path.join("divine-cleric", soul_filename),
        os.path.join("agents", "aragamago", soul_filename)
    ]
    
    if os.name == 'nt':
        soul_paths.append(r"C:\Users\Baba\Documents\openclaw\agents\aragamago\SOUL.md.txt")

    for path in soul_paths:
        try:
            with io.open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            continue
            
    return "You are Aragamago, Baba John's most trusted AI helper. (Fallback activated)"

# We compute this dynamically in get_ai_reply to guarantee it updates instantly

# ── OpenAI reply (if key present) ──────────────────────────────────────────
def get_ai_reply(user_message: str, image_b64: str = None) -> str:
    if not OPENAI_API_KEY:
        logger.warning("No OPENAI_API_KEY available.")
        return None
        
    # Log key prefix for debugging (safe, only first 10 chars)
    key_prefix = OPENAI_API_KEY[:10] if OPENAI_API_KEY else "None"
    logger.info(f"Attempting AI reply with key prefix: {key_prefix}... (Total length: {len(OPENAI_API_KEY)})")

    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "HTTP-Referer": "https://railway.app", 
            "X-Title": "Aragamago Bot",
            "Content-Type": "application/json"
        }
        
        # Build message payload
        messages = [{"role": "system", "content": _get_soul()}]
        
        user_content = []
        if user_message:
            user_content.append({"type": "text", "text": user_message})
        if image_b64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
            })
            
        messages.append({"role": "user", "content": user_content})
        
        payload = {
            "model": AI_MODEL,
            "messages": messages,
            "max_tokens": 600,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"❌ AI Provider Error (OpenRouter {response.status_code}): {response.text}")
            return None
            
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
        
    except Exception as e:
        logger.error(f"❌ Internal AI request error: {type(e).__name__} — {e}")
        return None

# ── Handlers ───────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦜 *Aragamago online.*\n\n"
        "Sacred Library Guardian at your service, Baba.\n"
        "I am here — watching, protecting, and ready to serve.\n\n"
        "How may I assist you?",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    user_name = update.effective_user.first_name or "traveler"
    chat_id = update.effective_chat.id
    logger.info(f"📥 RECEIVED MESSAGE from {user_name} (Chat: {chat_id}): {user_msg}")

    # Try AI reply first
    logger.info(f"🤖 Requesting AI reply for: '{user_msg[:50]}...' using model {AI_MODEL}")
    reply = get_ai_reply(user_msg)
    logger.info(f"📤 AI RESPONSE generated (length: {len(reply) if reply else 0})")

    # Fallback if no AI reply (due to quota, key, or provider error)
    if not reply:
        reply = (
            f"🦜 *Aragamago hears you, {user_name}.*\n\n"
            f"You said: _{user_msg}_\n\n"
            "I am currently having trouble reaching my AI reasoning unit at OpenRouter. "
            "Please check the Railway logs to see the specific error (quota, billing, or invalid key)."
        )

    sent_msg = await update.message.reply_text(reply, parse_mode="Markdown")
    logger.info(f"✅ TELEGRAM REPLY SENT (Msg ID: {sent_msg.message_id})")

async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ── Dummy Web Server for Railway Healthcheck ───────────────────────────────
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK - Bot is healthy!")
    def log_message(self, format, *args):
        pass # Suppress logs so it doesn't spam the console

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Started dummy healthcheck server on port {port}")
    server.serve_forever()

def heartbeat():
    while True:
        logger.info("💓 HEARTBEAT: Aragamago is still breathing...")
        time.sleep(60)

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    # Spin up the background web server IMMEDIATELY to satisfy Railway
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # Heartbeat to prove we haven't hung
    threading.Thread(target=heartbeat, daemon=True).start()
    
    # Give the thread a moment to bind to the port
    time.sleep(2)
    
    logger.info("🦜 Aragamago is online.")
    
    if not TELEGRAM_TOKEN:
        logger.error("❌ CRITICAL: TELEGRAM_BOT_TOKEN missing! Environment might not be configured correctly.")
        # We don't exit immediately to let the healthcheck server stay up briefly for debugging
        time.sleep(30)
        raise ValueError("TELEGRAM_BOT_TOKEN missing from environment or .env")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("✅ Aragamago is live. Listening for messages...")
    print("\n🦜 Aragamago is LIVE on Telegram — send him a message at @aragamago_bot\n")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
