import datetime
import random
import time
import art

SLEEP_DURATION = 60 * 60  # 1 hour, in seconds

# how fast Tama-chan's needs drift while she's awake and unattended
HUNGER_RATE_PER_MIN = 1 / 10          # +1 hunger every 10 minutes awake
ENERGY_RATE_PER_MIN = 1 / 15          # -1 energy every 15 minutes awake
NEGLECT_HAPPINESS_RATE_PER_MIN = 1 / 20  # happiness dips if she's left starving

LOW_ENERGY_THRESHOLD = 15

FEED_MESSAGES = [
    "Tama-chan happily eats. :3",
    "Nom nom nom~ Tama-chan is satisfied.",
    "Tama-chan devours the snack in record time!",
]

PET_MESSAGES = [
    "Tama-chan seems happy. :3",
    "Tama-chan nuzzles into your hand~ ♡",
    "Tama-chan purrs contentedly.",
]

PLAY_MESSAGES = [
    "Tama-chan had fun playing! >:3",
    "Tama-chan pounces around gleefully~",
    "Tama-chan chases her tail in circles, giggling.",
]


def minutes_since_last_seen(data):
    last_seen = data.get("last_seen")
    if not last_seen:
        return 0

    try:
        elapsed = datetime.datetime.now() - datetime.datetime.fromisoformat(last_seen)
    except ValueError:
        return 0

    return max(0, elapsed.total_seconds() / 60)


def apply_time_decay(data):
    """Let hunger/energy drift based on how long Tama-chan was left alone.
    Skipped while she's asleep, since sleeping is how she recovers."""
    if data.get("sleeping", False):
        return

    elapsed_minutes = minutes_since_last_seen(data)
    if elapsed_minutes <= 0:
        return

    data["hunger"] = min(100, data["hunger"] + elapsed_minutes * HUNGER_RATE_PER_MIN)
    data["energy"] = max(0, data["energy"] - elapsed_minutes * ENERGY_RATE_PER_MIN)

    if data["hunger"] >= 80:
        data["happiness"] = max(
            0, data["happiness"] - elapsed_minutes * NEGLECT_HAPPINESS_RATE_PER_MIN
        )

    data["hunger"] = round(data["hunger"])
    data["energy"] = round(data["energy"])
    data["happiness"] = round(data["happiness"])


# feed
def feed(data):
    if data["hunger"] == 0:
        print(art.shy)
        return "Tama-chan isn't hungry yet."

    data["hunger"] = max(0, data["hunger"] - 10)
    print(art.happy)
    return random.choice(FEED_MESSAGES)


# pet
def pet(data):
    data["happiness"] = min(100, data["happiness"] + 5)
    print(art.loved)
    return random.choice(PET_MESSAGES)


def play(data):
    if data["energy"] <= LOW_ENERGY_THRESHOLD:
        print(art.sleepy)
        return "Tama-chan is too tired to play right now... maybe let her sleep? :("

    data["happiness"] = min(100, data["happiness"] + 10)
    data["energy"] = max(0, data["energy"] - 10)
    data["hunger"] = min(100, data["hunger"] + 10)
    print(art.excited)
    return random.choice(PLAY_MESSAGES)


# sleep
def sleep(data):
    if data["energy"] >= 70:
        print(art.shy)
        return "Tama-chan isn't sleepy yet."

    data["sleeping"] = True
    data["sleep_started"] = time.time()

    print(art.sleepy)
    return "Tama-chan went to sleep. zzz..."


def update_sleep(data):
    if not data.get("sleeping", False):
        return

    elapsed = time.time() - data["sleep_started"]

    if elapsed >= SLEEP_DURATION:
        data["sleeping"] = False
        data["sleep_started"] = None
        data["energy"] = 100
