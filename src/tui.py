# Tama-chan's TUI file.
# Opened by typing `tama` with no arguments (see main.py).
#
# This file only DISPLAYS things. Every action goes through main.run_command,
# so the CLI and the TUI share the exact same logic, saves and achievements.

import contextlib
import curses
import io
import locale
import textwrap
import time
import achievements
import art
import pet
from state import load_state

# lets the terminal draw unicode in general
locale.setlocale(locale.LC_ALL, "")

HUNGRY_FACE_AT = 70      # same value as in main.py
CANDY_MAX = 64           # same cap as state.py / main.py
REACTION_SECONDS = 3     # how long an action's face stays before she goes idle
FRAME_MS = 250           # redraw 4 times per second
MIN_H, MIN_W = 20, 60    # smaller than this -> "too small" message
LOG_LIMIT = 200          # log lines kept in memory
TOP_H = 9                # height of the top row of boxes

# key -> command (the names of the commands in main.py)
KEYS = {
    ord("f"): "feed",
    ord("p"): "pet",
    ord("l"): "play",
    ord("s"): "sleep",
    ord("k"): "poke",
    ord("h"): "hug",
    ord("t"): "trick",
    ord("o"): "fortune",
}
FOOTER = " f feed  p pet  l play  s sleep  k poke  h hug  t trick  o fortune  q quit"

# color pairs
GREEN, YELLOW, RED, PINK, DIM = 1, 2, 3, 4, 5


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    pink = 213 if curses.COLORS >= 256 else curses.COLOR_MAGENTA
    colors = (curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_RED, pink, curses.COLOR_CYAN)
    for pair, color in enumerate(colors, start=1):
        curses.init_pair(pair, color, -1)


# small drawing helpers :3
def put(win, y, x, text, pair=0):
    height, width = win.getmaxyx()
    if y < 0 or y >= height or x < 0 or x >= width:
        return
    try:
        win.addstr(y, x, text[: width - x], curses.color_pair(pair))
    except curses.error:
        pass


def draw_box(win, y, x, h, w, title="", pair=0):
    put(win, y, x, "╭" + "─" * (w - 2) + "╮", pair)
    for row in range(y + 1, y + h - 1):
        put(win, row, x, "│", pair)
        put(win, row, x + w - 1, "│", pair)
    put(win, y + h - 1, x, "╰" + "─" * (w - 2) + "╯", pair)
    if title:
        put(win, y, x + 2, f"┤ {title} ├", pair)


def gauge(value, maximum, width):
    filled = max(0, min(width, round(width * value / maximum)))
    return "█" * filled + "░" * (width - filled)


def level_color(value, bad_when_high=False):
    score = 100 - value if bad_when_high else value
    if score >= 60:
        return GREEN
    if score >= 30:
        return YELLOW
    return RED


# which face is she making? idk, so this code here resolves our doubt, probably, pls help me

def idle_face(data):
    if data["sleeping"]:
        return "sleepy"
    if data["hunger"] >= HUNGRY_FACE_AT:
        return "sad"
    return "normal"


def run_captured(run_command, command):
    """Run a command with stdout captured, so print() can't mess up the screen.
    Returns (reaction_face, text). The face is whichever sprite from art.ART
    the command printed; it's removed from the text so only messages are left.
    """

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_command(command)
    text = buf.getvalue()

    reaction = None
    for name, sprite in art.ART.items():
        if sprite in text:
            reaction = name
            text = text.replace(sprite, "")
            break
    return reaction, text


def add_log(log, text):
    for line in text.splitlines():
        if line.strip():
            log.append(line.rstrip())
    del log[:-LOG_LIMIT]


# panels

def draw_sprite_panel(win, y, x, h, w, face):
    draw_box(win, y, x, h, w, "tama", PINK)
    lines = textwrap.dedent(art.ART[face]).strip("\n").splitlines()
    art_w = max(len(line) for line in lines)
    top = y + (h - len(lines)) // 2
    left = x + (w - art_w) // 2
    for i, line in enumerate(lines):
        put(win, top + i, left, line, PINK)


def draw_stats_panel(win, y, x, h, w, data):
    draw_box(win, y, x, h, w, "stats", PINK)
    gauge_w = max(5, w - 2 - 11 - 5 - 2)   # borders, label, number, margins

    rows = (
        ("hunger", data["hunger"], 100, level_color(data["hunger"], bad_when_high=True)),
        ("happiness", data["happiness"], 100, level_color(data["happiness"])),
        ("energy", data["energy"], 100, level_color(data["energy"])),
        ("candy", data["candy"], CANDY_MAX, PINK),
    )
    for i, (label, value, maximum, pair) in enumerate(rows):
        row = y + 1 + i
        put(win, row, x + 2, f"{label:<10}")
        put(win, row, x + 13, gauge(value, maximum, gauge_w), pair)
        put(win, row, x + 13 + gauge_w, f" {round(value):>3}")

    if data["sleeping"]:
        wake_at = data["sleep_started"] + pet.SLEEP_DURATION
        minutes = max(0, round((wake_at - time.time()) / 60))
        put(win, y + 6, x + 2, f"sleeping... zzz  (wakes in ~{minutes} min)", DIM)
    else:
        put(win, y + 6, x + 2, "awake", DIM)


def draw_achievements_panel(win, y, x, h, w, ach, scroll):
    total = len(achievements.ACHIEVEMENTS)
    draw_box(win, y, x, h, w, f"achievements {len(ach['unlocked'])}/{total}", PINK)

    rows = []
    for aid, defn in achievements.ACHIEVEMENTS.items():
        if aid in ach["unlocked"]:
            rows.append((f"★ {defn['name']}", PINK))
        elif defn["secret"]:
            rows.append(("??? (a secret...)", DIM))
        else:
            text = defn["name"]
            if defn["goal"] and defn["goal"] > 1:
                # TODO: draw a little gauge() here instead of plain numbers :3
                text += f"  {min(defn['progress'](ach), defn['goal'])}/{defn['goal']}"
            rows.append((text, 0))

    visible = h - 2
    scroll = max(0, min(scroll, len(rows) - visible))
    for i, (text, pair) in enumerate(rows[scroll: scroll + visible]):
        put(win, y + 1 + i, x + 2, text[: w - 4], pair)
    return scroll   # clamped, so main loop doesn't continue past the end


def draw_log_panel(win, y, x, h, w, log):
    draw_box(win, y, x, h, w, "log", PINK)
    inner = w - 4
    wrapped = []
    for entry in log:
        pair = PINK if "★" in entry else 0
        for line in textwrap.wrap(entry, inner) or [""]:
            wrapped.append((line, pair))
    for i, (line, pair) in enumerate(wrapped[-(h - 2):]):
        put(win, y + 1 + i, x + 2, line, pair)


# the main loop
def run(run_command):
    curses.wrapper(_main, run_command)


def _main(stdscr, run_command):
    curses.curs_set(0)
    init_colors()
    stdscr.timeout(FRAME_MS)

    log = []
    reaction, reaction_until = None, 0.0
    scroll = 0

    # opening the TUI counts as a visit.
    # only the welcome-back line goes to the log (the panels already show the stats).
    _, text = run_captured(run_command, "status")
    add_log(log, "\n".join(
        line for line in text.splitlines()
        if line.strip() and not line.startswith(" ") and "status:" not in line
    ))

    while True:
        data = load_state()
        pet.tick(data)
        ach = achievements.load_achievements()

        height, width = stdscr.getmaxyx()
        stdscr.erase()

        if height < MIN_H or width < MIN_W:
            put(stdscr, 0, 0, f"too small ({width}x{height}), need {MIN_W}x{MIN_H} >.<")
        else:
            if reaction and time.time() < reaction_until:
                face = reaction
            else:
                face = idle_face(data)

            left_w = width // 2
            bottom_h = height - TOP_H - 1

            draw_sprite_panel(stdscr, 0, 0, TOP_H, left_w, face)
            draw_stats_panel(stdscr, 0, left_w, TOP_H, width - left_w, data)
            scroll = draw_achievements_panel(stdscr, TOP_H, 0, bottom_h, left_w, ach, scroll)
            draw_log_panel(stdscr, TOP_H, left_w, bottom_h, width - left_w, log)
            put(stdscr, height - 1, 0, FOOTER, DIM)

        stdscr.refresh()

        key = stdscr.getch()   # -1 when it times out
        if 0 < key < 256:
            key = ord(chr(key).lower())   # so caps lock doesn't break things

        if key == ord("q"):
            break
        elif key in KEYS:
            reaction, text = run_captured(run_command, KEYS[key])
            reaction_until = time.time() + REACTION_SECONDS
            add_log(log, text)
        elif key == curses.KEY_DOWN:
            scroll += 1
        elif key == curses.KEY_UP:
            scroll = max(0, scroll - 1)
