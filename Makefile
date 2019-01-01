# Use to build modules

.PHONY: test


all:
	make -C bluepy

test:
	@make -C pyclient test




