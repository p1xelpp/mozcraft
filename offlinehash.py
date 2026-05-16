import os
import json
import uuid

IDENTITY_FILE = "identity.json"
PREFIX = "offline_"  # u can change the prefix

def load_or_create_identity():
    if os.path.exists(IDENTITY_FILE):
        try:
            with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "id" in data and isinstance(data["id"], str) and len(data["id"]) > 0:
                return data["id"]
        except Exception:
            pass  # if file is gone = new name

    identity = uuid.uuid4().hex[:8]
    with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump({"id": identity}, f, indent=2)
    return identity

def get_username():
    identity = load_or_create_identity()
    return f"{PREFIX}{identity}"

if __name__ == "__main__":
    print(get_username())