from state import load_state, save_state, mark_seen
import pet
import art
import fortune
import sys

WELCOME_BACK_LONG_MIN = 180   # 3 hours
WELCOME_BACK_SHORT_MIN = 30   # 30 minutes


def show_status(data, away_minutes=0):
    if away_minutes >= WELCOME_BACK_LONG_MIN:
        print("You've been gone a while~ Tama-chan missed you! :3")
    elif away_minutes >= WELCOME_BACK_SHORT_MIN:
        print("Tama-chan perks up as you return~")

    if data["sleeping"]:
        print(art.sleepy)
    elif data["hunger"] >= 70:
        print(art.sad)
    else:
        print(art.normal)

    print("Tama-chan's status:")
    print(f"  hunger:     {data['hunger']}")
    print(f"  happiness:  {data['happiness']}")
    print(f"  energy:     {data['energy']}")
    print(f"  sleeping:   {data['sleeping']}")


def main():
    data = load_state()

    away_minutes = pet.minutes_since_last_seen(data)
    pet.apply_time_decay(data)
    pet.update_sleep(data)

    command = sys.argv[1] if len(sys.argv) > 1 else "status"

    if command == "sleep":
        print(pet.sleep(data))
        mark_seen(data)

    elif command == "feed":
        print(pet.feed(data))
        mark_seen(data)

    elif command == "pet":
        print(pet.pet(data))
        mark_seen(data)

    elif command == "play":
        print(pet.play(data))
        mark_seen(data)

    elif command == "fortune":
        print(fortune.get_fortune())

    elif command == "status":
        show_status(data, away_minutes)

    else:
        print(art.confused)
        print(f"Tama-chan tilts her head, confused. Unknown command: {command}")
        print("Try: status, feed, pet, play, sleep, fortune")

    save_state(data)


if __name__ == "__main__":
    main()
