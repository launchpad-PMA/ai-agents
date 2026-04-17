import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# ── Load local .env only if running locally ─────────────────────────────────────
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

# Required scopes for Tasks and Sheets
SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/spreadsheets"
]

def main():
    print("🦜 Welcome to the Google Auth Linker 🦜")
    
    # Check if credentials exist in env
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    
    if not creds_json:
        print("❌ GOOGLE_CREDENTIALS_JSON not found in environment!")
        print("Please download 'credentials.json' from Google Cloud Console as a Desktop App,")
        print("and set its contents as the GOOGLE_CREDENTIALS_JSON environment variable.")
        return

    try:
        creds_dict = json.loads(creds_json)
    except json.JSONDecodeError:
        print("❌ GOOGLE_CREDENTIALS_JSON is not valid JSON!")
        return

    # Write temporarily to file for InstalledAppFlow (it expects a file)
    with open("temp_credentials.json", "w") as f:
        json.dump(creds_dict, f)

    try:
        flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        
        print("\n✅ Authentication Successful!\n")
        print("👇 Copy the following JSON block and save it as GOOGLE_TOKEN_JSON in your Railway Variables or .env 👇\n")
        print(json.dumps(token_data))
        print("\n👆 Copy from the first { to the last } 👆\n")
        
    finally:
        if os.path.exists("temp_credentials.json"):
            os.remove("temp_credentials.json")

if __name__ == "__main__":
    main()
