import random
import art

FORTUNES = [
    "nya :3",
    "Your next bug will be caused by something obvious.",
    "Sometimes the best solution is to close the terminal.",
    "Take a break, your code will still be broken later.",
    "Sometimes the best solution is to turn it off and turn it back on.",
    "You should probably read the documentation.",
    "Tux approves of your terminal usage.",
    "Tux is not responsible of what happens after sudo.",
]

def get_fortune():
    print(art.normal)
    return random.choice(FORTUNES)
