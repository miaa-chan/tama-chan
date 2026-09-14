import datetime
import json
import os

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


def default_state():
    return {
        "hunger": 0,
        "happiness": 100,
        "energy": 100,
        "sleeping": False,
        "sleep_started": None,
        "last_seen": datetime.datetime.now().isoformat(),
    }


def load_state():
    """Load saved state from disk, or start fresh if none exists yet."""
    if not os.path.exists(STATE_FILE):
        return default_state()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        # corrupted or unreadable save file -> don't crash, just start over
        return default_state()


def save_state(data):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json_dump(data, f, indent=4)

def mark_seen(data):
    data["last_seen"] = datetime.datetime.now().isoformat()
