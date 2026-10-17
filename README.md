# tama-chan

A tiny terminal Tamagotchi. She gets hungry, she gets sleepy, and she notices when you're gone. :3

## Installation

Clone repository by downloading it as a .zip file or by using:
`git clone https://github.com/miaa-chan/tama-chan.git`

Change directory and install Tama-chan:
`make install`

Do NOT run it with sudo. The Makefile asks for your password itself only for
the one step that needs it (the launcher in `/bin`). If the whole thing runs as
root, `$HOME` becomes `/root` and her files end up somewhere you can't read.

Requires Python.

## Usage

After installing, run:
`tama`

Take care of her, check on her, and enjoy! :3

Current commands:

`tama status` (also what plain `tama` does)
`tama feed`
`tama pet`
`tama play`
`tama poke`
`tama hug`
`tama sleep`
`tama fortune`
`tama achievements`
`tama trick`

Sleeping takes about an hour, and nothing changes while she naps.
Tired Tama-chan won't play, and doesn't appreciate pokes or hugs.

## Achievements

Tama-chan keeps track of how you treat her! Unlock achievements by caring for her
(and sometimes by being a little naughty), and earn candy for most of them.
Check your progress with `tama achievements`. Some are secret... :3

Only actions that actually did something count, so spamming `tama feed` on a full
tummy won't get you anywhere. Visits count too, but only if they're at least 10
minutes apart.

## Uninstall

`make uninstall` removes the program but keeps her save files (`state.json` and `achievements.json`).
`make purge` removes everything, including her. She will be gone forever. :(

## License
Tama-chan is licensed under Apache 2.0
See LICENSE for the full text.
