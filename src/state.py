# Tama-chan's state file.
# Responsible of handling Tama-chan's saves.

import datetime
import json
import math
import os

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

STAT_KEYS = ("hunger", "happiness", "energy")


def default_state():
    now = datetime.datetime.now().isoformat()
    return {
        "hunger": 0,
        "happiness": 100,
        "energy": 100,
        "sleeping": False,
        "sleep_started": None,
        "last_seen": now,
        "last_tick": now,
        "candy": 0,
    }


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _repair(loaded):
    # fill in anything missing so old/partial saves do not cause crashes
    state = default_state()
    if not isinstance(loaded, dict):
        return state

    for key in state:
        if key in loaded:
            state[key] = loaded[key]

    # saves from before the decay clock existed: start it at the last visit
    if "last_tick" not in loaded and "last_seen" in loaded:
        state["last_tick"] = loaded["last_seen"]

    defaults = default_state()
    for key in STAT_KEYS:
        if _is_number(state[key]):
            state[key] = max(0, min(100, state[key]))
        else:
            state[key] = defaults[key]

    # candy is a whole number from 0-64; anything else resets back to 0
    candy = state["candy"]
    if _is_number(candy) and math.isfinite(candy):
        state["candy"] = max(0, min(64, int(candy)))
    else:
        state["candy"] = defaults["candy"]

    # sleep checker
    if not isinstance(state["sleeping"], bool):
        state["sleeping"] = False

    # if "sleeping" start time can't be resolved -> just wake her up
    if state["sleeping"] and not _is_number(state["sleep_started"]):
        state["sleeping"] = False
    if not state["sleeping"]:
        state["sleep_started"] = None

    return state


def load_state():
    # load saved state from disk, or start fresh if none exists yet
    if not os.path.exists(STATE_FILE):
        return default_state()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return _repair(json.load(file))
    except (json.JSONDecodeError, OSError):
        # corrupted or unreadable save file -> don't crash, just start over
        return default_state()


def save_state(data):
    # write to a temp file then swap it in, so a crash mid-write
    # can't leave her save file half-written
    tmp_path = STATE_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    os.replace(tmp_path, STATE_FILE)


def mark_seen(data):
    data["last_seen"] = datetime.datetime.now().isoformat()
