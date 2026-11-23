# tui.py: responsible for tama-chan's UI :3
# (press q to quit)

import curses
import locale

# lets terminal draw unicode (rounded corners, kaomoji, etc.)
locale.setlocale(locale.LC_ALL, "")


def draw_box(win, y, x, h, w, title=""):
    win.addstr(y, x, "╭" + "─" * (w - 2) + "╮")
    for row in range(y + 1, y + h - 1):
        win.addstr(row, x, "│" + " " * (w - 2) + "│")
    win.addstr(y + h - 1, x, "╰" + "─" * (w - 2) + "╯")
    if title:
        win.addstr(y, x + 2, f"┤ {title} ├")


def main(stdscr):
    curses.curs_set(0)  # hide blinking cursor

    while True:
        stdscr.erase()  # wipe the grid so it doesn't flicker
        height, width = stdscr.getmaxyx()

        if height < 8 or width < 30:
            stdscr.addstr(0, 0, "Too small, please make your terminal bigger >.<"[: width - 1])
        else:
            # box is inset by 1 (writing there makes curses raise an error >.>)
            draw_box(stdscr, 1, 1, height - 2, width - 2, "tama")

            msg = "hello curses! :3"
            stdscr.addstr(height // 2, (width - len(msg)) // 2, msg)
            stdscr.addstr(height - 3, 3, "Press q to quit")

        stdscr.refresh()

        key = stdscr.getch()  # waits for a key (a terminal resize also wakes it up)
        if key == ord("q"):
            break


# wrapper sets curses up, runs main(), and ALWAYS restores your terminal after
curses.wrapper(main)
