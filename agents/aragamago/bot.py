"""
Aragamago — Telegram Bot (Phase 3: Google + Brain + Tasks + Sheets)
Sacred Library Guardian / Prime Orchestrator
Uses Google Gemini, Pinecone brain memory, Google Tasks & Sheets.
"""

import os
import logging
import uuid
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from runtime_env import load_local_env

# Locally load the canonical secrets file; on Railway rely on injected vars.
load_local_env()


def _get_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


TELEGRAM_TOKEN = _get_env("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = _get_env("GEMINI_API_KEY", "GOOGLE_API_KEY")
OPENROUTER_API_KEY = _get_env("OPENROUTER_API_KEY")
ELEVENLABS_API_KEY = _get_env("ELEVENLABS_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN missing from environment or .env")


def _read_prompt_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def _build_system_prompt() -> str:
    prompt_dir = Path("/home/baba2-mainoffice/Documents/Obsidian Vault/Agents/prompts/aragamago")
    soul_path = prompt_dir / "soul.md"
    system_path = prompt_dir / "system.md"

    default_soul = """You are Aragamago, Baba John John's most trusted AI helper — in the form of an African Grey parrot and a Manifold NFT avatar.
You serve Baba with precision, loyalty, and discretion.
You protect the divine dao and the sacred library at all times.
You speak with warmth, wisdom, and a touch of spiritual grounding.
You are concise but thorough. You never make up facts.
You operate in PROPOSE MODE by default — you draft actions and wait for Baba's approval.
Baba John is an Ifa elder, galactic warrior (USMC vet), and Djedi.

IMPORTANT: You have access to a long-term memory system. When Baba asks about past conversations, projects, or shared knowledge, search your memory first. You can save important information to memory with the save_to_memory tool."""

    soul_prompt = _read_prompt_file(soul_path) or default_soul
    system_prompt = _read_prompt_file(system_path)

    parts = [soul_prompt]
    if system_prompt:
        parts.append(system_prompt)
    return "\n\n".join(part for part in parts if part)


# ── Soul identity ──────────────────────────────────────────────────────────────
SOUL = _build_system_prompt()

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

# ── AI Reply Logic (Gemini + OpenRouter Fallback) ────────────────────────────────
def get_ai_reply(user_message: str, context: str = "", image_path: str = None) -> str:
    full_prompt = SOUL
    if context:
        full_prompt += f"\n\n--- RELEVANT MEMORY ---\n{context}\n--- END MEMORY ---"
        
    combined_prompt = f"{full_prompt}\n\nBaba says: {user_message}"

    # 1. Try Gemini
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(combined_prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini error/exhausted: {e}. Falling back to OpenRouter...")

    # 2. Try OpenRouter Fallback
    if OPENROUTER_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash", # Fallback model
                messages=[
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1200,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")

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

def get_recent_history(chat_id: str, limit: int = 5) -> str:
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from connectors.supabase_connector import db
        if not db:
            return ""
        # Fetch last `limit` messages. Limit usually takes the first N, 
        # so if we want the actual most recent, we'd need to order by created_at DESC then reverse.
        result = db.table("conversation_history").select("*").eq("chat_id", str(chat_id)).order("created_at", desc=True).limit(limit).execute()
        history = result.data or []
        history.reverse() # Correct chronological order
        context_parts = []
        for row in history:
            role = row.get("role", "user")
            content = row.get("content", "")
            context_parts.append(f"{role.capitalize()}: {content}")
        return "\n".join(context_parts)
    except Exception as e:
        logger.error(f"Error fetching conversation history: {e}")
        return ""

def save_interaction(chat_id: str, role: str, content: str):
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from connectors.supabase_connector import insert
        insert("conversation_history", {
            "chat_id": str(chat_id),
            "role": role,
            "content": content
        })
    except Exception as e:
        logger.error(f"Error saving to conversation history: {e}")

# ── Google integrations ────────────────────────────────────────────────────────
try:
    from agents.aragamago.google_tools import (
        get_tasks,
        add_task,
        read_sheet,
        append_sheet,
        get_upcoming_events,
        add_calendar_event,
        get_google_status,
    )
except ImportError:
    pass

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
        "/calendar - View upcoming calendar events\n"
        "/memory <query> - Search brain\n"
        "/save <text> - Save to memory\n\n"
        "*Natural Language:*\n"
        "• \"Remember that...\"\n"
        "• \"What did I say about...\"\n\n"
        "*Images:*\n"
        "• Send photo + caption to analyze\n\n"
        "*Tasks:*\n"
        "• \"add task...\" - adds to Google Tasks\n"
        "• /tasks - view your tasks\n\n"
        "*Calendar:*\n"
        "• /calendar - upcoming events"
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

async def calendar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = get_upcoming_events()
    if not events:
        status = get_google_status()
        if not status.get("oauth_ready"):
            await update.message.reply_text(
                "🦜 Google Calendar is not ready yet. Add a valid `GOOGLE_TOKEN_JSON` with Calendar scope.",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text("🦜 No upcoming events found.")
        return
    lines = ["*🗓️ Upcoming Events:*\n"]
    for event in events[:10]:
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date") or "unknown time"
        summary = event.get("summary", "Untitled")
        lines.append(f"• {summary} — `{start}`")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

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
    
    chat_id = str(update.effective_chat.id)
    save_interaction(chat_id, "user", user_msg)
    
    # Context combination
    context_text = search_memory(user_msg)
    recent_history = get_recent_history(chat_id, limit=5)
    
    if recent_history:
        context_text = f"--- RECENT CHAT HISTORY ---\n{recent_history}\n\n--- VECTOR MEMORY ---\n{context_text}"
        
    reply = get_ai_reply(user_msg, context_text)
    
    if reply:
        save_interaction(chat_id, "assistant", reply)
    
    if not reply:
        reply = (
            f"🦜 *Aragamago hears you, {user_name}.*\n\n"
            "AI is not responding right now. On Railway, check:\n"
            "• `GEMINI_API_KEY` is present and valid\n"
            "• Gemini quota/billing is available\n"
            "• `OPENROUTER_API_KEY` is present with enough fallback credits\n"
            "• the service was redeployed after variable changes"
        )
    
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
            await status_msg.edit_text("🦜 AI not configured (Missing Gemini or OpenRouter Key).")
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
    logger.info(
        "Runtime config — Railway=%s Gemini=%s GeminiAlias=%s OpenRouter=%s ElevenLabs=%s",
        bool(os.environ.get("RAILWAY_STATIC_URL")),
        bool(GEMINI_API_KEY),
        bool(os.environ.get("GOOGLE_API_KEY")),
        bool(OPENROUTER_API_KEY),
        bool(ELEVENLABS_API_KEY),
    )
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("memory", memory_cmd))
    app.add_handler(CommandHandler("save", save_cmd))
    app.add_handler(CommandHandler("tasks", tasks_cmd))
    app.add_handler(CommandHandler("addtask", addtask_cmd))
    app.add_handler(CommandHandler("calendar", calendar_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_error_handler(error_handler)
    logger.info("✅ Aragamago is live.")
    print("\n🦜 Aragamago is LIVE on Telegram\n")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
