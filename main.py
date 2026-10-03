from state import load_state, save_state, mark_seen
import pet
import art
import fortune
import sys

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

    # stats are floats internally
    print("Tama-chan's status:")
    print(f"  hunger:     {round(data['hunger'])}")
    print(f"  happiness:  {round(data['happiness'])}")
    print(f"  energy:     {round(data['energy'])}")
    print(f"  sleeping:   {data['sleeping']}")


def main():
    data = load_state()

    # measured BEFORE this visit gets recorded, for the welcome-back message
    away_minutes = pet.minutes_since_last_seen(data)
    pet.tick(data)

    command = sys.argv[1].lower() if len(sys.argv) > 1 else "status"

    if command in ACTIONS:
        print(ACTIONS[command](data))
        mark_seen(data)

    elif command == "fortune":
        print(fortune.get_fortune())

    elif command == "status":
        show_status(data, away_minutes)

    else:
        print(art.confused)
        print(f"Tama-chan tilts her head, confused. Unknown command: {command}")
        print("Try: status, feed, pet, play, sleep, fortune, poke, hug")

    save_state(data)


if __name__ == "__main__":
    main()
