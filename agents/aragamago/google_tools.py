import os
import json
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON", "")
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")

def get_google_credentials():
    if not GOOGLE_TOKEN_JSON:
        logger.warning("GOOGLE_TOKEN_JSON not configured.")
        return None
    try:
        token_data = json.loads(GOOGLE_TOKEN_JSON)
        return Credentials.from_authorized_user_info(token_data)
    except Exception as e:
        logger.error(f"Failed to load Google credentials: {e}")
        return None

# ── Tasks ────────────────────────────────────────────────────────────────ــــ
def _get_tasks_service():
    creds = get_google_credentials()
    if not creds: return None
    try:
        return build("tasks", "v1", credentials=creds)
    except Exception as e:
        logger.error(f"Google Tasks build error: {e}")
        return None

def get_tasks() -> list:
    service = _get_tasks_service()
    if not service: return []
    try:
        results = service.tasks().list(tasklist="@default", showCompleted=False).execute()
        return results.get("items", [])
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        return []

def add_task(title: str, notes: str = "") -> bool:
    service = _get_tasks_service()
    if not service: return False
    try:
        task = {"title": title}
        if notes: task["notes"] = notes
        service.tasks().insert(tasklist="@default", body=task).execute()
        return True
    except Exception as e:
        logger.error(f"Add task error: {e}")
        return False

# ── Sheets ───────────────────────────────────────────────────────────────────
def _get_sheets_service():
    creds = get_google_credentials()
    if not creds: return None
    try:
        return build("sheets", "v4", credentials=creds)
    except Exception as e:
        logger.error(f"Google Sheets build error: {e}")
        return None

def read_sheet(range_name: str = "Sheet1!A1:Z50") -> list:
    if not GOOGLE_SHEET_ID:
        logger.warning("GOOGLE_SHEET_ID not configured.")
        return []
    service = _get_sheets_service()
    if not service: return []
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEET_ID, range=range_name
        ).execute()
        return result.get("values", [])
    except Exception as e:
        logger.error(f"Read sheet error: {e}")
        return []

def append_sheet(values: list, range_name: str = "Sheet1!A1") -> bool:
    if not GOOGLE_SHEET_ID:
        return False
    service = _get_sheets_service()
    if not service: return False
    try:
        body = {"values": [values]}
        service.spreadsheets().values().append(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        return True
    except Exception as e:
        logger.error(f"Append sheet error: {e}")
        return False
