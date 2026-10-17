import datetime
import json
import os
import pet

ACHIEVEMENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "achievements.json")

MESSAGE = "Cheating is for the weak."

# events that always count as a visit-worthy action, whatever state she was in
ALWAYS_COUNTED = ("pet", "feed", "play", "trick", "sleep", "hug", "poke", "fortune", "unknown")

# a "visit" only counts if it's at least this long after the previous one
VISIT_GAP_MIN = 10


# definitions

def _counter(name, desc, key, goal, candy, secret=False):
    """Unlocks once counters[key] reaches goal."""
    return {
        "name": name, "desc": desc, "candy": candy, "secret": secret,
        "goal": goal,
        "progress": lambda ach: ach["counters"].get(key, 0),
        "check": None,
    }


def _streak(name, desc, goal, candy):
    # unlocks after visiting on X or Y days in a row
    return {
        "name": name, "desc": desc, "candy": candy, "secret": False,
        "goal": goal,
        "progress": lambda ach: ach["streak"],
        "check": None,
    }


def _event(name, desc, check, candy, secret=False):
    # unlocks when check(ach, ctx) is true during a visit
    return {
        "name": name, "desc": desc, "candy": candy, "secret": secret,
        "goal": None, "progress": None,
        "check": check,
    }


def _night_owl(ach, ctx):
    return ctx["now"].hour < 5


def _early_bird(ach, ctx):
    return 5 <= ctx["now"].hour < 8


def _missed_you(ach, ctx):
    return ctx.get("away_minutes", 0) >= 24 * 60


def _starving(ach, ctx):
    # looked at how she was when you ARRIVED, not after you fed her
    before = ctx.get("before") or {}
    return before.get("hunger", 0) >= 90 and not before.get("sleeping", False)


def _perfect_care(ach, ctx):
    after = ctx.get("after") or {}
    return (
        ach["counters"].get("visit", 0) >= 10
        and after.get("hunger", 100) <= 10
        and after.get("happiness", 0) >= 95
        and after.get("energy", 0) >= 90
    )


# order here is the order they show up in `tama achievements`
ACHIEVEMENTS = {
    # feeding
    "first_meal": _counter("First Bite", "Feed Tama-chan for the first time.", "feed", 1, 1),
    "snack_master": _counter("Snack Master", "Feed Tama-chan 25 times.", "feed", 25, 3),
    # petting
    "first_pet": _counter("Gentle Hands", "Pet Tama-chan for the first time.", "pet", 1, 1),
    "pet_pro": _counter("Professional Petter", "Pet Tama-chan 50 times.", "pet", 50, 3),
    # playing
    "first_play": _counter("Playtime!", "Play with Tama-chan for the first time.", "play", 1, 1),
    "playmate": _counter("Playmate", "Play with Tama-chan 25 times.", "play", 25, 3),
    # poking & hugging
    "poke_10": _counter("Poke Poke Poke", "Poke Tama-chan 10 times.", "poke", 10, 2),
    "first_hug": _counter("Warm Fuzzies", "Hug Tama-chan for the first time.", "hug", 1, 1),
    "hug_10": _counter("Cuddle Expert", "Hug Tama-chan 10 times.", "hug", 10, 3),
    # sleeping
    "first_nap": _counter("Nap Time", "Put Tama-chan to sleep.", "sleep", 1, 1),
    "sweet_dreams": _counter("Sweet Dreams", "Let Tama-chan wake up on her own.", "woke", 1, 2),
    # fortunes
    "fortune_10": _counter("Fortune Seeker", "Read 10 fortunes.", "fortune", 10, 2),
    # showing up
    "regular": _counter("Regular Visitor", f"Visit Tama-chan 10 times ({VISIT_GAP_MIN}+ min apart).", "visit", 10, 2),
    "bff": _counter("Best Friends Forever", f"Visit Tama-chan 100 times ({VISIT_GAP_MIN}+ min apart).", "visit", 100, 5),
    "streak_3": _streak("Three Days Strong", "Visit Tama-chan 3 days in a row.", 3, 3),
    "streak_7": _streak("One Whole Week", "Visit Tama-chan 7 days in a row.", 7, 5),
    "early_bird": _event("Early Bird", "Visit Tama-chan early in the morning (5-8am).", _early_bird, 2),
    "perfect_care": _event(
        "Perfect Care", "Well-fed, happy AND rested, once you've visited her 10 times.",
        _perfect_care, 5,
    ),
    # secrets
    "night_owl": _event("Night Owl", "Visit Tama-chan in the middle of the night.", _night_owl, 2, secret=True),
    "missed_you": _event(
        "Absence Makes the Heart Grow Fonder", "Come back after being away for a whole day.",
        _missed_you, 2, secret=True,
    ),
    "lost": _counter(
        "Lost in Translation", "Give Tama-chan 3 commands she doesn't understand.",
        "unknown", 3, 1, secret=True,
    ),
    # the "oops" ones don't give candy
    "snack_time": _event(
        "Oops... Snack Time!", "Find Tama-chan absolutely starving.", _starving, 0, secret=True,
    ),
    "rude": _counter(
        "Rude!", "Poke or hug Tama-chan while she's too tired for it.",
        "annoyed", 1, 0, secret=True,
    ),
}


# the file

def default_achievements():
    return {
        "_message": MESSAGE,
        "unlocked": {},
        "counters": {},
        "streak": 0,
        "last_day": None,
        "candy": 0,
    }


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _parse_day(value):
    try:
        return datetime.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _repair(loaded):
    # fill in anything missing or nonsensical so a bad file can't cause crashes
    ach = default_achievements()
    if not isinstance(loaded, dict):
        return ach

    unlocked = loaded.get("unlocked")
    if isinstance(unlocked, dict):
        ach["unlocked"] = {
            key: value for key, value in unlocked.items()
            if isinstance(key, str) and isinstance(value, str)
        }

    counters = loaded.get("counters")
    if isinstance(counters, dict):
        ach["counters"] = {
            key: int(value) for key, value in counters.items()
            if isinstance(key, str) and _is_number(value) and value >= 0
        }

    if _is_number(loaded.get("streak")) and loaded["streak"] >= 0:
        ach["streak"] = int(loaded["streak"])

    if _parse_day(loaded.get("last_day")):
        ach["last_day"] = loaded["last_day"]

    if _is_number(loaded.get("candy")) and loaded["candy"] >= 0:
        ach["candy"] = int(loaded["candy"])

    return ach


def load_achievements():
    # load saved achievements from disk or start over if none exists yet
    if not os.path.exists(ACHIEVEMENT_FILE):
        return default_achievements()

    try:
        with open(ACHIEVEMENT_FILE, "r", encoding="utf-8") as file:
            return _repair(json.load(file))
    except (json.JSONDecodeError, OSError):
        # corrupted or unreadable file -> don't crash, just start over
        return default_achievements()


def save_achievements(ach):
    # write to a temp file then swap it in, so a crash mid-write can't leave the file half-written
    tmp_path = ACHIEVEMENT_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as file:
        json.dump(ach, file, indent=4)
    os.replace(tmp_path, ACHIEVEMENT_FILE)


# tracking

def _bump(ach, key):
    ach["counters"][key] = ach["counters"].get(key, 0) + 1


def _counts(event, ctx):
    """Did this command actually DO something? Spamming `feed` on a full
    Tama-chan (or poking her while she sleeps) shouldn't farm achievements."""
    before = ctx.get("before") or {}
    after = ctx.get("after") or {}

    if event == "feed":
        return after.get("hunger", 0) < before.get("hunger", 0)
    if event == "play":
        return after.get("energy", 0) < before.get("energy", 0)
    if event == "sleep":
        return bool(after.get("sleeping")) and not before.get("sleeping", False)
    if event in ("pet", "poke", "hug"):
        return not before.get("sleeping", False)
    return event in ALWAYS_COUNTED


def _was_rude(event, ctx):
    before = ctx.get("before") or {}
    return (
        event in ("poke", "hug")
        and not before.get("sleeping", False)
        and before.get("energy", 100) <= pet.TIRED_THRESHOLD
    )


def _update_streak(ach, today):
    last = _parse_day(ach["last_day"])
    if last == today:
        return

    if last is not None and (today - last).days == 1:
        ach["streak"] += 1
    else:
        ach["streak"] = 1  # first visit ever, a gap, or a clock that went backwards

    ach["last_day"] = today.isoformat()


def _met(defn, ach, ctx):
    if defn["goal"] is not None:
        return defn["progress"](ach) >= defn["goal"]
    return bool(defn["check"](ach, ctx))


def record(ach, event, ctx=None):
    """Record one visit/command and return the ids of newly unlocked achievements.

    event: the command name ("feed", "pet", ... or "unknown")
    ctx (all optional):
        before / after  - Tama-chan's state dict from before and after the command
        away_minutes    - how long you were gone (visits need a gap, see VISIT_GAP_MIN)
        woke            - True if she woke up on her own this visit
        now             - datetime (defaults to now)
    """
    ctx = dict(ctx or {})
    now = ctx.setdefault("now", datetime.datetime.now())

    away = ctx.get("away_minutes")
    if ach["counters"].get("visit", 0) == 0 or away is None or away >= VISIT_GAP_MIN:
        _bump(ach, "visit")
    if _counts(event, ctx):
        _bump(ach, event)
    if ctx.get("woke"):
        _bump(ach, "woke")
    if _was_rude(event, ctx):
        _bump(ach, "annoyed")
    _update_streak(ach, now.date())

    newly_unlocked = []
    for achievement_id, defn in ACHIEVEMENTS.items():
        if achievement_id in ach["unlocked"]:
            continue
        if _met(defn, ach, ctx):
            ach["unlocked"][achievement_id] = now.isoformat()
            ach["candy"] += defn["candy"]
            newly_unlocked.append(achievement_id)

    return newly_unlocked


# display

def format_unlock(achievement_id):
    defn = ACHIEVEMENTS[achievement_id]
    candy = f" (+{defn['candy']} candy)" if defn["candy"] else ""
    return f"★  Achievement unlocked: {defn['name']}\n  {defn['desc']}{candy}"


def format_list(ach):
    unlocked_here = [aid for aid in ACHIEVEMENTS if aid in ach["unlocked"]]
    lines = [
        f"Achievements ({len(unlocked_here)}/{len(ACHIEVEMENTS)})   candy: {ach['candy']}",
        "",
    ]

    for achievement_id, defn in ACHIEVEMENTS.items():
        if achievement_id in ach["unlocked"]:
            lines.append(f"  ★ {defn['name']} - {defn['desc']}")
        elif defn["secret"]:
            lines.append("  ???  (a secret... keep an eye out)")
        else:
            progress = ""
            if defn["goal"] is not None and defn["goal"] > 1:
                progress = f"  ({min(defn['progress'](ach), defn['goal'])}/{defn['goal']})"
            lines.append(f"  {defn['name']} - {defn['desc']}{progress}")

    return "\n".join(lines)
