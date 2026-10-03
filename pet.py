import datetime
import random
import time
import art

SLEEP_DURATION = 60 * 60

# how fast Tama-chan's needs drift while she's awake and unattended
HUNGER_RATE_PER_MIN = 1 / 5               # +1 hunger every 5 minutes awake
ENERGY_RATE_PER_MIN = 1 / 7               # -1 energy every 7 minutes awake
NEGLECT_HAPPINESS_RATE_PER_MIN = 1 / 20   # happiness decreases if she's left starving
NEGLECT_HUNGER_LEVEL = 80

SLEEPY_BELOW = 70            # she only agrees to sleep under this energy
LOW_ENERGY_THRESHOLD = 15    # too tired to play
TIRED_THRESHOLD = 30         # too tired to be poked or hugged

# command responses
FEED_MESSAGES = [
    "Tama-chan happily eats. :3",
    "Nom nom nom~ Tama-chan is satisfied.",
    "Tama-chan devours the snack in record time!",
]

PET_MESSAGES = [
    "Tama-chan seems happy. :3",
    "Tama-chan nuzzles into your hand~",
    "Tama-chan purrs contentedly.",
]

PLAY_MESSAGES = [
    "Tama-chan had fun playing! >:3",
    "Tama-chan pounces around gleefully~",
    "Tama-chan chases her tail in circles, giggling.",
]

POKE_MESSAGES = [
    "You poked Tama-chan. She seems amused.",
    "You poked Tama-chan. She pokes you back. :3",
    "You poked Tama-chan. She wiggles happily. <3",
]

HUG_MESSAGES = [
    "Tama-chan enjoyed the hug. <3",
    "Tama-chan happily cuddles back. :3",
    "Tama-chan feels loved. :3",
    "Tama-chan snuggles into the hug. >w<",
]


def _clamp(value, low=0, high=100):
    return max(low, min(high, value))


def _parse_time(value):
    try:
        return datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def minutes_since_last_seen(data, now=None):
    now = now or datetime.datetime.now()
    last_seen = _parse_time(data.get("last_seen"))
    if last_seen is None:
        return 0

    return max(0, (now - last_seen).total_seconds() / 60)


def tick(data, now=None):
    """Bring Tama-chan's needs up to date. Call once per run.

    - While she's asleep nothing decays, and she wakes up once SLEEP_DURATION has passed.
    - Only time she was actually AWAKE counts as decay, including the stretch after she woke up on her own.
    - Stats stay as unrounded floats so frequent check-ins can't swallow the fractions; round only when displaying.
    """
    now = now or datetime.datetime.now()
    awake_from = _parse_time(data.get("last_tick")) or now

    if data.get("sleeping", False):
        wake_at = datetime.datetime.fromtimestamp(data["sleep_started"] + SLEEP_DURATION)

        if now < wake_at:
            data["last_tick"] = now.isoformat()
            return

        data["sleeping"] = False
        data["sleep_started"] = None
        data["energy"] = 100
        awake_from = max(awake_from, wake_at)

    minutes = max(0, (now - awake_from).total_seconds() / 60)

    if minutes > 0:
        data["hunger"] = _clamp(data["hunger"] + minutes * HUNGER_RATE_PER_MIN)
        data["energy"] = _clamp(data["energy"] - minutes * ENERGY_RATE_PER_MIN)

        if data["hunger"] >= NEGLECT_HUNGER_LEVEL:
            data["happiness"] = _clamp(
                data["happiness"] - minutes * NEGLECT_HAPPINESS_RATE_PER_MIN
            )

    data["last_tick"] = now.isoformat()


def _sleeping_reply(data):
    """If she's asleep, show her sleeping and return a message; otherwise None."""
    if data.get("sleeping", False):
        print(art.sleepy)
        return "Shh... Tama-chan is sleeping. zzz..."
    return None


# feed
def feed(data):
    asleep = _sleeping_reply(data)
    if asleep:
        return asleep

    if data["hunger"] < 1:
        print(art.shy)
        return "Tama-chan isn't hungry yet."

    data["hunger"] = _clamp(data["hunger"] - 10)
    print(art.happy)
    return random.choice(FEED_MESSAGES)


# pet
def pet(data):
    asleep = _sleeping_reply(data)
    if asleep:
        return asleep

    data["happiness"] = _clamp(data["happiness"] + 5)
    print(art.loved)
    return random.choice(PET_MESSAGES)


# play
def play(data):
    asleep = _sleeping_reply(data)
    if asleep:
        return asleep

    if data["energy"] <= LOW_ENERGY_THRESHOLD:
        print(art.sleepy)
        return "Tama-chan is too tired to play right now... maybe let her sleep? :("

    data["happiness"] = _clamp(data["happiness"] + 10)
    data["energy"] = _clamp(data["energy"] - 10)
    data["hunger"] = _clamp(data["hunger"] + 10)
    print(art.excited)
    return random.choice(PLAY_MESSAGES)


# sleep
def sleep(data):
    if data.get("sleeping", False):
        print(art.sleepy)
        return "Tama-chan is already asleep. zzz..."

    if data["energy"] >= SLEEPY_BELOW:
        print(art.shy)
        return "Tama-chan isn't sleepy yet."

    data["sleeping"] = True
    data["sleep_started"] = time.time()

    print(art.sleepy)
    return "Tama-chan went to sleep. zzz..."


# poke
def poke(data):
    asleep = _sleeping_reply(data)
    if asleep:
        return asleep

    if data["energy"] <= TIRED_THRESHOLD:
        print(art.annoyed)
        data["happiness"] = _clamp(data["happiness"] - 5)
        return "You poked Tama-chan. She looks annoyed. She's too tired for this right now."

    print(art.happy)
    data["happiness"] = _clamp(data["happiness"] + 10)
    return random.choice(POKE_MESSAGES)


# hug
def hug(data):
    asleep = _sleeping_reply(data)
    if asleep:
        return asleep

    if data["energy"] <= TIRED_THRESHOLD:
        print(art.annoyed)
        data["happiness"] = _clamp(data["happiness"] - 10)
        return "Tama-chan doesn't want any hugs. She's sleepy."

    print(art.loved)
    data["happiness"] = _clamp(data["happiness"] + 20)
    return random.choice(HUG_MESSAGES)
