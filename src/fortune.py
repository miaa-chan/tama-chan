# Tama-chan's fortune file.
# All of her fortunes are stored here.

import random
import art

NORMAL_FORTUNES = [
    "nya :3",
    "Your next bug will be caused by something obvious.",
    "Sometimes the best solution is to close the terminal.",
    "Take a break, your code will still be broken later.",
    "Sometimes the best solution is to turn it off and turn it back on.",
    "You should probably read the documentation.",
    "Perhaps you should finish your existing projects.",
]

TUX_FORTUNES = [
    "Tux approves of your terminal usage.",
    "Tux is not responsible for what happens after sudo.",
    "Tux is watching. He's always watching.",
    "A penguin walks into your terminal. He already has root.",
    "Tux does not judge your distro. He has standards, so do I. :3",
    "Tux says your system is fine. Do not reboot.",
    "Tux strongly recommends never removing 'The French Language Pack'. Your computer will appreciate it."
]

LINUX_FORTUNES = [
    "Linux is free. Your time debugging it isn't.",
    "Linux gives you freedom. It also gives you a lot of configuration files. Lots of them.",
    "Your package manager has a plan. You probably shouldn't ask what it is.",
    "Linux wisdom: if it works, document what you changed, even if you changed nothing.",
    "You wanted a simple system. You now have full control over it.",
]

X11_FORTUNES = [
    "X11 has been around for decades. It has seen things.",
    "X11: It works. That is enough.",
    "X11 doesn't need your fancy new protocols. It has suffering.",
]

WAYLAND_FORTUNES = [
    "Wayland is the future. The future is still being implemented.",
    "Wayland has arrived. Your ancient X11 app has not.",
    "Wayland gives applications less power. Your security model approves.",
]

FORTUNES = (
    NORMAL_FORTUNES
    + TUX_FORTUNES
    + LINUX_FORTUNES
    + X11_FORTUNES
    + WAYLAND_FORTUNES
)


def get_fortune():
    print(art.normal)
    return random.choice(FORTUNES)
