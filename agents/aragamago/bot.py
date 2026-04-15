"""
Aragamago — Telegram Bot (Phase 3: Google + Brain + Tasks + Sheets)
Sacred Library Guardian / Prime Orchestrator
Uses Google Gemini, Pinecone brain memory, Google Tasks & Sheets.
"""

import os
import logging
import uuid
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ── Load local .env only if running locally (not on Railway) ──────────────────
if not os.environ.get("RAILWAY_STATIC_URL"):
    def _load_env():
        env_path = os.environ.get("ENV_PATH", r"C:\Users\Baba\.env")
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
        except FileNotFoundError:
            pass
    _load_env()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
GOOGLE_SERVICE_ACCOUNT_EMAIL = os.environ.get("GOOGLE_SERVICE_ACCOUNT_EMAIL", "")
GOOGLE_PRIVATE_KEY = os.environ.get("GOOGLE_PRIVATE_KEY", "")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN missing from environment or .env")

# ── Soul identity ──────────────────────────────────────────────────────────────
SOUL = """You are Aragamago, Baba John John's most trusted AI helper — in the form of an African Grey parrot and a Manifold NFT avatar.
You serve Baba with precision, loyalty, and discretion.
You protect the divine dao and the sacred library at all times.
You speak with warmth, wisdom, and a touch of spiritual grounding.
You are concise but thorough. You never make up facts.
You operate in PROPOSE MODE by default — you draft actions and wait for Baba's approval.
Baba John is an Ifa elder, galactic warrior (USMC vet), and Djedi.

IMPORTANT: You have access to a long-term memory system. When Baba asks about past conversations, projects, or shared knowledge, search your memory first. You can save important information to memory with the save_to_memory tool."""

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

# ── Google Gemini Reply ─────────────────────────────────────────────────────────
def get_ai_reply(user_message: str, context: str = "", image_path: str = None) -> str:
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        full_prompt = SOUL
        if context:
            full_prompt += f"\n\n--- RELEVANT MEMORY ---\n{context}\n--- END MEMORY ---"
        full_prompt += f"\n\nBaba says: {user_message}"
        
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None

def get_ai_reply_image(user_message: str, context: str, image_bytes) -> str:
    """Handle messages with images - accepts BytesIO object"""
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        from PIL import Image
        import io
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        full_prompt = SOUL
        if context:
            full_prompt += f"\n\n--- RELEVANT MEMORY ---\n{context}\n--- END MEMORY ---"
        
        image_bytes.seek(0)
        image = Image.open(image_bytes)
        content_parts = [full_prompt, image, f"\n\nBaba says: {user_message}"]
        response = model.generate_content(content_parts)
        
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini image error: {e}")
        return None

# ── Voice Processing ───────────────────────────────────────────────────────────
async def get_transcription(file_path: str) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        audio_file = genai.upload_file(path=file_path)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content([
            "Please transcribe this audio message.",
            audio_file
        ])
        return response.text.strip()
    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        return ""

def generate_voice(text: str) -> str:
    if not ELEVENLABS_API_KEY:
        return None
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio_generator = client.generate(
            text=text,
            voice="nPczCjzI2devNBz1zQrb",
            model="eleven_multilingual_v2"
        )
        output_path = "reply.mp3"
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)
        return output_path
    except Exception as e:
        logger.error(f"ElevenLabs TTS error: {e}")
        return None

# ── Brain Memory ───────────────────────────────────────────────────────────────
def _get_brain():
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from connectors.pinecone_connector import query_brain, upsert_to_brain
        return query_brain, upsert_to_brain
    except Exception as e:
        logger.warning(f"Brain not available: {e}")
        return None, None

query_brain, upsert_to_brain = _get_brain()

def search_memory(query: str, top_k: int = 5) -> str:
    if query_brain is None:
        return ""
    try:
        results = query_brain(query, top_k=top_k)
        if not results:
            return ""
        context_parts = []
        for match in results:
            if match.get("metadata", {}).get("text"):
                source = match["metadata"].get("source", "unknown")
                text = match["metadata"]["text"][:500]
                context_parts.append(f"[{source}]: {text}...")
        return "\n\n".join(context_parts) if context_parts else ""
    except Exception as e:
        logger.error(f"Memory search error: {e}")
        return ""

def save_to_memory(text: str, source: str = "telegram") -> bool:
    if upsert_to_brain is None:
        return False
    try:
        doc_id = f"telegram_{uuid.uuid4().hex[:12]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        metadata = {
            "text": text,
            "source": source,
            "date": datetime.now().isoformat(),
            "user": "baba"
        }
        return upsert_to_brain(doc_id, text, metadata)
    except Exception as e:
        logger.error(f"Save memory error: {e}")
        return False

# ── Google Tasks (Service Account) ─────────────────────────────────────────────
def _get_tasks_service():
    if not GOOGLE_SERVICE_ACCOUNT_EMAIL or not GOOGLE_PRIVATE_KEY:
        logger.warning("Google Service Account not configured")
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials = service_account.Credentials.from_service_account_info({
            "type": "service_account",
            "client_email": GOOGLE_SERVICE_ACCOUNT_EMAIL,
            "private_key": GOOGLE_PRIVATE_KEY.replace("\\n", "\n"),
        }, scopes=["https://www.googleapis.com/auth/tasks"])
        
        return build("tasks", "v1", credentials=credentials)
    except Exception as e:
        logger.error(f"Google Tasks error: {e}")
        return None

def get_tasks() -> list:
    service = _get_tasks_service()
    if service is None:
        return []
    try:
        results = service.tasklists().list().execute()
        return results.get("items", [])
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        return []

def add_task(title: str, notes: str = "") -> bool:
    """Add a task to the default task list"""
    service = _get_tasks_service()
    if service is None:
        return False
    try:
        tasklist_id = "@default"
        task = {"title": title}
        if notes:
            task["notes"] = notes
        service.tasks().insert(tasklist=tasklist_id, body=task).execute()
        return True
    except Exception as e:
        logger.error(f"Add task error: {e}")
        return False

# ── Google Sheets (Service Account) ─────────────────────────────────────────────
def _get_sheets_service():
    if not GOOGLE_SERVICE_ACCOUNT_EMAIL or not GOOGLE_PRIVATE_KEY:
        logger.warning("Google Service Account not configured")
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials = service_account.Credentials.from_service_account_info({
            "type": "service_account",
            "client_email": GOOGLE_SERVICE_ACCOUNT_EMAIL,
            "private_key": GOOGLE_PRIVATE_KEY.replace("\\n", "\n"),
        }, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        
        return build("sheets", "v4", credentials=credentials)
    except Exception as e:
        logger.error(f"Google Sheets error: {e}")
        return None

def read_sheet(spreadsheet_id: str, range_name: str = "Sheet1!A1:Z100") -> list:
    service = _get_sheets_service()
    if service is None:
        return []
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()
        return result.get("values", [])
    except Exception as e:
        logger.error(f"Read sheet error: {e}")
        return []

# ── Handlers ───────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦜 *Aragamago online.*\n\n"
        "Sacred Library Guardian at your service, Baba.\n"
        "I now have:\n"
        "• Long-term memory (Brain)\n"
        "• Google Tasks integration\n"
        "• Image analysis\n\n"
        "How may I assist you?",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*🦜 Commands*\n\n"
        "/start - Begin\n"
        "/help - This message\n"
        "/tasks - View tasks\n"
        "/memory <query> - Search brain\n"
        "/save <text> - Save to memory\n\n"
        "*Natural Language:*\n"
        "• \"Remember that...\"\n"
        "• \"What did I say about...\"\n\n"
        "*Images:*\n"
        "• Send photo + caption to analyze\n\n"
        "*Tasks:*\n"
        "• \"add task...\" - adds to Google Tasks\n"
        "• /tasks - view your tasks"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def memory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /memory <search query>")
        return
    query = " ".join(context.args)
    context_text = search_memory(query)
    if context_text:
        await update.message.reply_text(f"*🧠 Memory:*\n\n{context_text}", parse_mode="Markdown")
    else:
        await update.message.reply_text("🦜 Nothing found in memory.")

async def save_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /save <text>")
        return
    text = " ".join(context.args)
    if save_to_memory(text):
        await update.message.reply_text(f"🦜 *Saved:* _{text}_", parse_mode="Markdown")
    else:
        await update.message.reply_text("🦜 Memory unavailable.")

async def tasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = get_tasks()
    if not tasks:
        await update.message.reply_text("🦜 No tasks found or not configured.")
        return
    task_text = "*📋 Tasks:*\n\n"
    for task in tasks[:10]:
        task_text += f"• {task.get('title', 'Untitled')}\n"
    await update.message.reply_text(task_text, parse_mode="Markdown")

async def addtask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /addtask <task title>")
        return
    title = " ".join(context.args)
    if add_task(title):
        await update.message.reply_text(f"🦜 *Task added:* _{title}_", parse_mode="Markdown")
    else:
        await update.message.reply_text("🦜 Could not add task. Check Google Tasks config.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "traveler"
    user_msg = update.message.caption or "What's in this image?"
    logger.info(f"Photo from {user_name}: {user_msg}")
    status_msg = await update.message.reply_text("🦜 *Analyzing image...*", parse_mode="Markdown")
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        
        # Download to bytes (works on Railway's ephemeral filesystem)
        import io
        image_bytes = io.BytesIO()
        await file.download_to_memory(image_bytes)
        image_bytes.seek(0)
        
        context_text = search_memory(user_msg)
        reply = get_ai_reply_image(user_msg, context_text, image_bytes)
        
        if not reply:
            reply = "🦜 I see the image but cannot process it right now."
        await status_msg.edit_text(reply, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await status_msg.edit_text("🦜 Something disrupted the signal.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    user_name = update.effective_user.first_name or "traveler"
    logger.info(f"Message from {user_name}: {user_msg}")
    
    lower_msg = user_msg.lower()
    if lower_msg.startswith("remember that") or lower_msg.startswith("save this"):
        save_text = user_msg.split(":", 1)[-1].strip() if ":" in user_msg else user_msg
        save_text = save_text.replace("remember that ", "").replace("save this ", "").strip()
        if save_to_memory(save_text):
            await update.message.reply_text(f"🦜 *Saved:* _{save_text}_", parse_mode="Markdown")
        else:
            await update.message.reply_text("🦜 Memory unavailable.")
        return
    
    if "what did i say about" in lower_msg or "search memory for" in lower_msg:
        query = user_msg.split("about")[-1].strip() if "about" in user_msg else user_msg.split("for")[-1].strip()
        context_text = search_memory(query)
        if context_text:
            await update.message.reply_text(context_text, parse_mode="Markdown")
        else:
            await update.message.reply_text("🦜 Nothing found in memory.")
        return
    
    # Natural language task addition
    if lower_msg.startswith("add task") or lower_msg.startswith("create task") or lower_msg.startswith("new task"):
        task_title = user_msg
        for prefix in ["add task", "create task", "new task"]:
            task_title = task_title.replace(prefix, "", 1).strip()
        task_title = task_title.lstrip(": ").strip()
        if task_title and add_task(task_title):
            await update.message.reply_text(f"🦜 *Task added:* _{task_title}_", parse_mode="Markdown")
        else:
            await update.message.reply_text("🦜 Could not add task. Check Google Tasks config.")
        return
    
    context_text = search_memory(user_msg)
    reply = get_ai_reply(user_msg, context_text)
    
    if not reply:
        reply = f"🦜 *Aragamago hears you, {user_name}.*\n\nAdd `GEMINI_API_KEY` to enable AI responses."
    
    await update.message.reply_text(reply, parse_mode="Markdown")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "traveler"
    status_msg = await update.message.reply_text("🦜 *Listening...*", parse_mode="Markdown")
    try:
        voice_file = await update.message.voice.get_file()
        input_path = "user_voice.ogg"
        await voice_file.download_to_drive(input_path)
        await status_msg.edit_text("🦜 *Transcribing...*", parse_mode="Markdown")
        user_msg = await get_transcription(input_path)
        if not user_msg:
            await status_msg.edit_text("🦜 I couldn't hear you clearly.")
            return
        await status_msg.edit_text(f"🦜 *Heard:* _{user_msg}_\n*Thinking...*", parse_mode="Markdown")
        reply_text = get_ai_reply(user_msg)
        if not reply_text:
            await status_msg.edit_text("🦜 Gemini not configured.")
            return
        if ELEVENLABS_API_KEY:
            await status_msg.edit_text("🦜 *Speaking...*", parse_mode="Markdown")
            audio_path = generate_voice(reply_text)
            if audio_path:
                with open(audio_path, "rb") as voice_data:
                    await update.message.reply_voice(voice=voice_data, caption=reply_text, parse_mode="Markdown")
                await status_msg.delete()
                if os.path.exists(input_path): os.remove(input_path)
                if os.path.exists(audio_path): os.remove(audio_path)
                return
        await status_msg.edit_text(reply_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Voice handler error: {e}")
        await status_msg.edit_text("🦜 Something disrupted the signal.")

async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    logger.info("🦜 Aragamago starting...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("memory", memory_cmd))
    app.add_handler(CommandHandler("save", save_cmd))
    app.add_handler(CommandHandler("tasks", tasks_cmd))
    app.add_handler(CommandHandler("addtask", addtask_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_error_handler(error_handler)
    logger.info("✅ Aragamago is live.")
    print("\n🦜 Aragamago is LIVE on Telegram\n")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
