# Tama-chan's updater

import os
import shutil
import subprocess
import tempfile

REPO = "https://github.com/miaa-chan/tama-chan.git"

def run():
    if not (shutil.which("git") and shutil.which("make")):
        print("Tama-chan needs git and make to update. :<")
        return

    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(["git", "clone", "--depth", "1", "-q", REPO, tmp],
                           check=True, timeout=60, env=env)
            subprocess.run(["make", "install-data"], cwd=tmp, check=True)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("Update failed... her old files are safe though! :<")
            return

    print("Tama-chan got a shiny update! >:3")
