"""
Aragamago — Telegram Bot Handshake Test
Reads token from .env and calls getMe to verify the bot is reachable.
"""
import urllib.request
import json

env_path = r"C:\Users\Baba\Documents\antigravity\.env"
token = None

with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            token = line.split("=", 1)[1]
            break

if not token:
    print("TELEGRAM_BOT_TOKEN not found in .env")
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
