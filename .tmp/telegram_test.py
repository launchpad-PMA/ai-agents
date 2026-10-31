"""
Aragamago — Telegram Bot Handshake Test
Loads env via runtime_env (ENV_PATH or master.env) and calls getMe to verify the bot is reachable.
Run from repo root: python3 .tmp/telegram_test.py
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime_env import load_local_env  # noqa: E402

load_local_env()
token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

if not token:
    print("TELEGRAM_BOT_TOKEN not set (check ENV_PATH / master.env)")
    sys.exit(1)

url = f"https://api.telegram.org/bot{token}/getMe"

try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
    if data.get("ok"):
        bot = data["result"]
        print("SUCCESS")
        print(f"Bot name : {bot.get('first_name')}")
        print(f"Username : @{bot.get('username')}")
        print(f"Bot ID   : {bot.get('id')}")
    else:
        print(f"FAIL: {data}")
except Exception as e:
    print(f"ERROR: {e}")
