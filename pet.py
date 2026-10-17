import datetime
import random
import time
import art

SLEEP_DURATION = 60 * 60

# how fast Tama-chan's needs drift while she's awake and unattended
HUNGER_RATE_PER_MIN = 1 / 10               # +1 hunger every 10 minutes awake
ENERGY_RATE_PER_MIN = 1 / 15               # -1 energy every 15 minutes awake
NEGLECT_HAPPINESS_RATE_PER_MIN = 1 / 20   # happiness decreases if she's left starving
NEGLECT_HUNGER_LEVEL = 80

SLEEPY_BELOW = 70            # she only agrees to sleep under this energy
LOW_ENERGY_THRESHOLD = 15    # too tired to play
TIRED_THRESHOLD = 30         # too tired to be poked or hugged

# dices 
TRICK_DICE = random.randint(0, 1)
CANDY_DICE = random.randint(0, 1)

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

# If trick dice's value is 1
GOOD_TRICK_MESSAGES = [
    "Tama-chan went trick-or-treating. She got some candy. :3",
    "Tama-chan found a house giving a lot of candy and got a whole handful of it. :3",
]

# If trick dice's value is 0
BAD_TRICK_MESSAGES = [
    "Tama-chan went trick-or-treating. Nobody answered the door. :<",
    "Tama-chan went trick-or-treating. The house was empty. :<",
    "Tama-chan went trick-or-treating. She knocked... nothing. She returns disappointed. :<",
    "Tama-chan went trick-or-treating. She got scared by a Halloween decoration and ran away.",
]

CANDY_MESSAGES = [
    "Tama-chan happily eats her obtained candy. :3",
    "Nom nom nom~ Tama-chan is satisfied with the candy.",
    "Tama-chan devours the candy in record time!",
]

# maximum and minimum values
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

    if (CANDY_DICE == 1) and (data["candy"] > 0):
        data["hunger"] = _clamp(data["hunger"] - 10)
        data["candy"] = (data["candy"] - 1)
        print(art.happy)
        return random.choice(CANDY_MESSAGES)

    else:
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
        data["happiness"] = _clamp(data["happiness"] - 2)
        return "You poked Tama-chan. She looks annoyed. She's too tired for this right now."

    print(art.happy)
    data["happiness"] = _clamp(data["happiness"] + 5)
    return random.choice(POKE_MESSAGES)


# hug
def hug(data):
    asleep = _sleeping_reply(data)
    if asleep:
        return asleep

    if data["energy"] <= TIRED_THRESHOLD:
        print(art.annoyed)
        data["happiness"] = _clamp(data["happiness"] - 2)
        return "Tama-chan doesn't want any hugs. She's sleepy."

    print(art.loved)
    data["happiness"] = _clamp(data["happiness"] + 5)
    return random.choice(HUG_MESSAGES)

# trick
def trick(data):
    asleep = _sleeping_reply(data)
    if asleep:
        return asleep

    if data["energy"] <= TIRED_THRESHOLD:
        print(art.annoyed)
        data["happiness"] = _clamp(data["happiness"] - 2)
        return "Tama-chan is too tired to go trick-or-treating."

    if TRICK_DICE == 1:
        print (art.happy)
        data["happiness"] = _clamp(data["happiness"] + 5)
        data["candy"] = (data["candy"] + 3)
        return random.choice(GOOD_TRICK_MESSAGES)
    else:
        print(art.sad)
        data["happiness"] = _clamp(data["happiness"] - 5)
        return random.choice(BAD_TRICK_MESSAGES)
