import json
import os

SESSION_FILE = "session_data.json"

def save_session(data: dict):
    clean = {}
    for k, v in data.items():
        try:
            json.dumps(v)
            clean[k] = v
        except:
            pass
    with open(SESSION_FILE, 'w') as f:
        json.dump(clean, f)

def load_session() -> dict:
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    return {}

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)