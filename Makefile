# Only escalate with sudo for the parts that actually need root (/bin).
# Do NOT run the whole `make install` under sudo, because
# that would make $(HOME) resolve to /root instead of your real home dir
# and leave the python files owned by root, unreadable at runtime.
BINDIR ?= /bin
DATADIR := $(HOME)/.config/tama-chan
FILES := main.py pet.py state.py art.py fortune.py

# Root already? Doing a staged/packaged install via DESTDIR? Then don't sudo.
SUDO := $(shell if [ -z "$(DESTDIR)" ] && [ "$$(id -u)" != "0" ]; then echo sudo; fi)

.PHONY: install install-data install-bin uninstall

install: install-data install-bin
	@echo "Installed. Run 'tama' from anywhere (make sure $(BINDIR) is on your PATH)."

# Lives entirely under home dir -> never needs root.
install-data:
	install -d $(DESTDIR)$(DATADIR)
	install -m 644 $(FILES) $(DESTDIR)$(DATADIR)

# Only this part touches a system directory -> needs root.
install-bin:
	$(SUDO) install -d $(DESTDIR)$(BINDIR)
	printf '#!/bin/sh\nexec python3 $(DATADIR)/main.py "$$@"\n' | $(SUDO) tee $(DESTDIR)$(BINDIR)/tama > /dev/null
	$(SUDO) chmod 755 $(DESTDIR)$(BINDIR)/tama

uninstall:
	$(SUDO) rm -f $(DESTDIR)$(BINDIR)/tama
	rm -rf $(DESTDIR)$(DATADIR)
