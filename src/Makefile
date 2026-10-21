# Only escalate with sudo for the parts that actually need root (/bin).
# Do NOT run the whole `make install` under sudo, because
# that would make $(HOME) resolve to /root instead of your real home dir
# and leave the python files owned by root, unreadable at runtime.

ifneq ($(SUDO_USER),)
$(error Don't run this with sudo. Run plain 'make $(MAKECMDGOALS)'; it asks for your password itself, only where needed)
endif

BINDIR ?= /bin
DATADIR := $(HOME)/.config/tama-chan
FILES := main.py pet.py state.py art.py fortune.py achievements.py update.py

# Root already? Doing a staged/packaged install via DESTDIR? Then don't sudo.
SUDO := $(shell if [ -z "$(DESTDIR)" ] && [ "$$(id -u)" != "0" ]; then echo sudo; fi)

.PHONY: install install-data install-bin uninstall purge

install: install-data install-bin
	@echo "Installed. Run 'tama' from anywhere (make sure $(BINDIR) is on your PATH)."

# Lives entirely under home dir -> never needs root.
# (state.json and achievements.json are NOT in FILES, so reinstalling never touches her save.)
install-data:
	install -d $(DESTDIR)$(DATADIR)
	install -m 644 $(FILES) $(DESTDIR)$(DATADIR)

# Only this part touches a system directory -> needs root.
install-bin:
	$(SUDO) install -d $(DESTDIR)$(BINDIR)
	printf '#!/bin/sh\nexec python3 $(DATADIR)/main.py "$$@"\n' | $(SUDO) tee $(DESTDIR)$(BINDIR)/tama > /dev/null
	$(SUDO) chmod 755 $(DESTDIR)$(BINDIR)/tama

# Removes the program but KEEPS Tama-chan's save files (state.json, achievements.json).
uninstall:
	$(SUDO) rm -f $(DESTDIR)$(BINDIR)/tama
	rm -f $(addprefix $(DESTDIR)$(DATADIR)/,$(FILES))
	rm -rf $(DESTDIR)$(DATADIR)/__pycache__
	@rmdir $(DESTDIR)$(DATADIR) 2>/dev/null || true

# Uninstall AND delete her save files. She will be gone forever. :(
purge: uninstall
	rm -rf $(DESTDIR)$(DATADIR)
