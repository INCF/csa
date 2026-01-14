# This is a wrapper makefile which exists before configuration.
# It hands over to the Makefile produced by configure.

CONFIG_MK := Makefile
SPECIAL := bootstrap configure debian-package help

# If the user didn't specify any goals, default to "all"
DEFAULT_GOAL := all

.PHONY: $(SPECIAL) $(DEFAULT_GOAL)

bootstrap:
	./autogen.sh && ./configure

configure:
	./configure

debian-package:
	@if [ ! -f "$(CONFIG_MK)" ]; then \
		if [ ! -f "Makefile.in" ]; then \
			./autogen.sh; \
		fi; \
		./configure; \
	fi; \
	$(MAKE) -f "$(CONFIG_MK)" debian-package

help:
	@echo "make [TARGETS...] (after ./configure)"
	@echo "make bootstrap"		run ./autogen.sh and ./configure
	@echo "make configure"		run ./configure
	@echo "make debian-package	build and sign Debian package

# Default "make" (no args)
$(DEFAULT_GOAL):
	@if [ -f "$(CONFIG_MK)" ]; then \
		$(MAKE) -f "$(CONFIG_MK)" $(DEFAULT_GOAL); \
	else \
		echo "Not configured. Run: ./autogen.sh && ./configure"; \
		exit 1; \
	fi

# If user specified goals, forward them unless they are SPECIAL.
ifneq ($(strip $(MAKECMDGOALS)),)
# Error out if they mixed wrapper-special goals with forwarded goals (optional)
MIXED := $(filter $(SPECIAL),$(MAKECMDGOALS))
OTHER := $(filter-out $(SPECIAL),$(MAKECMDGOALS))

ifneq ($(strip $(MIXED)),)
ifneq ($(strip $(OTHER)),)
$(error Don't mix $(MIXED) with $(OTHER). Run bootstrap/configure separately.)
endif
endif

.PHONY: $(OTHER)
$(OTHER):
	@if [ -f "$(CONFIG_MK)" ]; then \
		$(MAKE) -f "$(CONFIG_MK)" $(OTHER); \
	else \
		echo "Not configured. Run: ./autogen.sh && ./configure"; \
		exit 1; \
	fi
endif
