import os
import json
import logging
import re
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from runtime_env import load_local_env

logger = logging.getLogger(__name__)
load_local_env()

GOOGLE_TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON", "")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
GOOGLE_SERVICE_ACCOUNT_EMAIL = os.environ.get("GOOGLE_SERVICE_ACCOUNT_EMAIL", "")
GOOGLE_PRIVATE_KEY = os.environ.get("GOOGLE_PRIVATE_KEY", "")
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
GOOGLE_SHEET_URL = os.environ.get("GOOGLE_SHEET_URL", "")

OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
]

SERVICE_ACCOUNT_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
]


def get_google_credentials(require_oauth: bool = False):
    def _parse_json_blob(raw: str):
        raw = raw.strip()
        if not raw:
            return None
        candidates = [raw]
        # Common Railway/env paste shape: escaped quotes inside a one-line blob.
        candidates.append(raw.replace('\\"', '"'))
        if len(raw) >= 2 and ((raw[0] == raw[-1] == '"') or (raw[0] == raw[-1] == "'")):
            inner = raw[1:-1]
            candidates.append(inner)
            candidates.append(inner.replace('\\"', '"'))
        for candidate in candidates:
            try:
                return json.loads(candidate)
            except Exception:
                continue
        raise json.JSONDecodeError("Could not decode JSON blob", raw, 0)

    if GOOGLE_TOKEN_JSON:
        try:
            token_data = _parse_json_blob(GOOGLE_TOKEN_JSON)
            return Credentials.from_authorized_user_info(token_data, scopes=OAUTH_SCOPES)
        except Exception as e:
            logger.error(f"Failed to load OAuth Google credentials: {e}")
            if require_oauth:
                return None

    if GOOGLE_SERVICE_ACCOUNT_JSON and not require_oauth:
        try:
            service_account_data = _parse_json_blob(GOOGLE_SERVICE_ACCOUNT_JSON)
            return ServiceAccountCredentials.from_service_account_info(
                service_account_data,
                scopes=SERVICE_ACCOUNT_SCOPES,
            )
        except Exception as e:
            logger.error(f"Failed to load service-account Google credentials: {e}")

    if GOOGLE_SERVICE_ACCOUNT_EMAIL and GOOGLE_PRIVATE_KEY and not require_oauth:
        try:
            service_account_data = {
                "type": "service_account",
                "project_id": "aragamago",
                "private_key": GOOGLE_PRIVATE_KEY.replace("\\n", "\n"),
                "client_email": GOOGLE_SERVICE_ACCOUNT_EMAIL,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            return ServiceAccountCredentials.from_service_account_info(
                service_account_data,
                scopes=SERVICE_ACCOUNT_SCOPES,
            )
        except Exception as e:
            logger.error(f"Failed to build service-account credentials from split env vars: {e}")
            return None

    if require_oauth:
        logger.warning("GOOGLE_TOKEN_JSON not configured.")
    else:
        logger.warning("No usable Google credentials configured.")
    return None


def get_google_oauth_credentials():
    return get_google_credentials(require_oauth=True)


def _extract_sheet_id(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", raw)
    if match:
        return match.group(1)
    return raw


def get_google_sheet_id() -> str:
    return (
        _extract_sheet_id(GOOGLE_SHEET_ID)
        or _extract_sheet_id(GOOGLE_SHEET_URL)
        or "1HqVMvobDTfno8g2mHLPqbbQbMQyStVfoDNkvXxhwmcs"
    )


def get_calendar_id() -> str:
    return os.environ.get("GOOGLE_CALENDAR_ID", "primary")


def get_google_status() -> dict:
    oauth_ready = get_google_oauth_credentials() is not None
    service_ready = get_google_credentials(require_oauth=False) is not None
    return {
        "oauth_ready": oauth_ready,
        "service_ready": service_ready,
        "sheet_id": get_google_sheet_id(),
        "calendar_id": get_calendar_id(),
    }

# ── Tasks ────────────────────────────────────────────────────────────────ــــ
def _get_tasks_service():
    creds = get_google_oauth_credentials()
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
    creds = get_google_credentials(require_oauth=False)
    if not creds: return None
    try:
        return build("sheets", "v4", credentials=creds)
    except Exception as e:
        logger.error(f"Google Sheets build error: {e}")
        return None

def read_sheet(range_name: str = "Sheet1!A1:Z50") -> list:
    sheet_id = get_google_sheet_id()
    service = _get_sheets_service()
    if not service: return []
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=range_name
        ).execute()
        return result.get("values", [])
    except Exception as e:
        logger.error(f"Read sheet error: {e}")
        return []

def append_sheet(values: list, range_name: str = "Sheet1!A1") -> bool:
    sheet_id = get_google_sheet_id()
    service = _get_sheets_service()
    if not service: return False
    try:
        body = {"values": [values]}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        return True
    except Exception as e:
        logger.error(f"Append sheet error: {e}")
        return False


# ── Calendar ─────────────────────────────────────────────────────────────────
def _get_calendar_service():
    creds = get_google_oauth_credentials()
    if not creds:
        return None
    try:
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        logger.error(f"Google Calendar build error: {e}")
        return None


def get_upcoming_events(max_results: int = 10) -> list:
    service = _get_calendar_service()
    if not service:
        return []
    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        events = service.events().list(
            calendarId=get_calendar_id(),
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        return events.get("items", [])
    except Exception as e:
        logger.error(f"Get calendar events error: {e}")
        return []


def add_calendar_event(summary: str, start_iso: str, end_iso: str, description: str = "") -> bool:
    service = _get_calendar_service()
    if not service:
        return False
    try:
        body = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_iso},
            "end": {"dateTime": end_iso},
        }
        service.events().insert(calendarId=get_calendar_id(), body=body).execute()
        return True
    except Exception as e:
        logger.error(f"Add calendar event error: {e}")
        return False
