"""
Aragamago — Telegram Bot Handshake Test
Reads token from the environment (Railway) or local secrets via runtime_env.
"""
import os
import sys
import urllib.request
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime_env import clean_env_value, load_local_env

load_local_env()
token = clean_env_value(os.environ.get("TELEGRAM_BOT_TOKEN", ""))

if not token:
    print("TELEGRAM_BOT_TOKEN not found in environment or ENV_PATH secrets file")
    exit(1)

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
