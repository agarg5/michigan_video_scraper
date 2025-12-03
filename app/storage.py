import os, json
from app.config import PROCESSED_FILE, DATA_DIR

def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r") as f:
        return set(json.load(f))

def save_processed(ids):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(ids), f)
