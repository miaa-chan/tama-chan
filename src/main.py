from state import load_state, save_state, mark_seen
import achievements
import pet
import art
import update
import fortune
import datetime
import sys

VERSION = "1.2.2"

WELCOME_BACK_LONG_MIN = 180   # 3 hours
WELCOME_BACK_SHORT_MIN = 30   # 30 minutes
HUNGRY_FACE_AT = 70

# commands that act on Tama-chan and return a message to print
ACTIONS = {
    "sleep": pet.sleep,
    "feed": pet.feed,
    "pet": pet.pet,
    "play": pet.play,
    "poke": pet.poke,
    "hug": pet.hug,
    "trick": pet.trick,
}


def show_status(data, away_minutes=0):
    if away_minutes >= WELCOME_BACK_LONG_MIN:
        print("You've been gone a while~ Tama-chan missed you! :3")
    elif away_minutes >= WELCOME_BACK_SHORT_MIN:
        print("Tama-chan perks up as you return~")

    if data["sleeping"]:
        print(art.sleepy)
    elif data["hunger"] >= HUNGRY_FACE_AT:
        print(art.sad)
    else:
        print(art.normal)

    # stats are floats internally; show them as whole numbers
    print("Tama-chan's status:")
    print(f"  hunger:     {round(data['hunger'])}")
    print(f"  happiness:  {round(data['happiness'])}")
    print(f"  energy:     {round(data['energy'])}")
    print(f"  sleeping:   {data['sleeping']}")


def main():
    data = load_state()
    ach = achievements.load_achievements()

    # measured BEFORE this visit gets recorded, for the welcome-back message
    away_minutes = pet.minutes_since_last_seen(data)

    was_sleeping = data["sleeping"]
    pet.tick(data)
    woke = was_sleeping and not data["sleeping"]

    command = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    before = dict(data)  # her state on arrival, so achievements can tell what changed

    if command in ACTIONS:
        print(ACTIONS[command](data))
        mark_seen(data)

    elif command == "fortune":
        print(fortune.get_fortune())

    elif command == "status":
        show_status(data, away_minutes)

    elif command == "achievements":
        print(art.normal)

    elif command == "version":
        print(art.normal)
        print(f"Tama-chan v{VERSION}")

    elif command == "update":
        update.run()
        return

    else:
        print(art.confused)
        print(f"Tama-chan tilts her head, confused. Unknown command: {command}")
        print("Try: status, feed, pet, play, sleep, fortune, poke, hug, trick, achievements")
        command = "unknown"
        away_minutes = 0

    # one candy pool: the pet's candy is what achievements pay into and feed spends
    ach["candy"] = data.get("candy", 0)

    unlocked = achievements.record(ach, command, {
        "before": before,
        "after": data,
        "away_minutes": away_minutes,
        "woke": woke,
        "now": datetime.datetime.now(),
    })

    ach["candy"] = max(0, min(64, ach["candy"]))
    data["candy"] = ach["candy"]

    if command == "achievements":
        print(achievements.format_list(ach))

    for achievement_id in unlocked:
        print()
        print(achievements.format_unlock(achievement_id))

    save_state(data)
    achievements.save_achievements(ach)


if __name__ == "__main__":
    main()
