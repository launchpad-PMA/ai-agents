"""
Aragamago — Telegram Bot (Phase 2: Link)
Sacred Library Guardian / Prime Orchestrator
Reads token from .env, listens for messages, replies via OpenAI.
If no OPENAI_API_KEY is set, falls back to a smart canned response.
"""

import os
import logging
import base64
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ── Load env ───────────────────────────────────────────────────────────────────
from dotenv import load_dotenv, find_dotenv

def _load_env():
    # Aggressively load all known .env locations to solve the multiple .env issue
    load_dotenv(find_dotenv()) # Local project root
    load_dotenv(r"C:\Users\Baba\Documents\antigravity\.env", override=True) # App config
    load_dotenv(r"C:\Users\Baba\.env", override=True) # Global config
    
_load_env()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN missing from environment or .env")

import io

# ── Dynamic Soul Identity ───────────────────────────────────────────────────
def _get_soul() -> str:
    # Continuously read the exact SOUL file the user manages before every prompt
    soul_path = r"C:\Users\Baba\Documents\openclaw\agents\aragamago\SOUL.md.txt"
    try:
        with io.open(soul_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "You are Aragamago, Baba John's most trusted AI helper. (Fallback activated)"

# We compute this dynamically in get_ai_reply to guarantee it updates instantly

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

# ── OpenAI reply (if key present) ──────────────────────────────────────────
def get_ai_reply(user_message: str, image_b64: str = None) -> str:
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Build message payload
        content = []
        if user_message:
            content.append({"type": "text", "text": user_message})
        if image_b64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
            })
            
        messages = [
            {"role": "system", "content": _get_soul()},
            {"role": "user", "content": content}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
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
    logger.info(f"Message from {user_name}: {user_msg}")

    # Try AI reply first
    reply = get_ai_reply(user_msg)

    # Fallback if no OpenAI key
    if not reply:
        reply = (
            f"🦜 *Aragamago hears you, {user_name}.*\n\n"
            f"You said: _{user_msg}_\n\n"
            "I am online and listening. To unlock my full AI reasoning, "
            "add your `OPENAI_API_KEY` to the `.env` file."
        )

    await update.message.reply_text(reply, parse_mode="Markdown")

async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    logger.info("🦜 Aragamago starting...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("✅ Aragamago is live. Listening for messages...")
    print("\n🦜 Aragamago is LIVE on Telegram — send him a message at @aragamago_bot\n")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
