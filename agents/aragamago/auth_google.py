import os
import json
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from runtime_env import load_local_env

# This helper is for local linking only. Railway should receive GOOGLE_TOKEN_JSON directly.
load_local_env()

# Required scopes for Tasks and Sheets
SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar"
]

def main():
    print("🦜 Welcome to the Google Auth Linker 🦜")
    print("This local helper uses GOOGLE_CREDENTIALS_JSON to open a Google sign-in flow")
    print("and prints a GOOGLE_TOKEN_JSON blob for your local env or Railway variables.\n")
    
    # Check if credentials exist in env
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    
    if not creds_json:
        print("❌ GOOGLE_CREDENTIALS_JSON not found in environment!")
        print("Please download 'credentials.json' from Google Cloud Console as a Desktop App,")
        print("and set its contents as the GOOGLE_CREDENTIALS_JSON environment variable.")
        return

    try:
        candidates = [creds_json]
        candidates.append(creds_json.replace('\\"', '"'))
        if len(creds_json) >= 2 and ((creds_json[0] == creds_json[-1] == '"') or (creds_json[0] == creds_json[-1] == "'")):
            inner = creds_json[1:-1]
            candidates.append(inner)
            candidates.append(inner.replace('\\"', '"'))

        creds_dict = None
        for candidate in candidates:
            try:
                creds_dict = json.loads(candidate)
                break
            except json.JSONDecodeError:
                continue
        if isinstance(creds_dict, str):
            print("❌ GOOGLE_CREDENTIALS_JSON is a plain string, not an OAuth client JSON object.")
            print("Paste the full Desktop App credentials JSON from Google Cloud Console,")
            print("including the top-level 'installed' object, as the env value.")
            return
        if isinstance(creds_dict, dict) and "installed" not in creds_dict and "web" not in creds_dict:
            print("❌ GOOGLE_CREDENTIALS_JSON must be an OAuth client JSON object.")
            print("Expected a top-level 'installed' or 'web' key from Google Cloud Console.")
            return
        if creds_dict is None:
            raise json.JSONDecodeError("Invalid OAuth client JSON", creds_json, 0)
    except json.JSONDecodeError:
        print("❌ GOOGLE_CREDENTIALS_JSON is not valid JSON!")
        return

    # Write temporarily to file for InstalledAppFlow (it expects a file)
    with open("temp_credentials.json", "w") as f:
        json.dump(creds_dict, f)

    try:
        flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)
        no_browser = "--no-browser" in sys.argv
        if no_browser:
            creds = flow.run_local_server(port=0, open_browser=False, authorization_prompt_message="Open this URL in your browser:\n{url}\n")
        else:
            print("Opening the browser for Google sign-in...")
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
