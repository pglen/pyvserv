# Makefile for pyvcommon tests

.PHONY: tests testall

# ------------------------------------------------------------------------

all:
	@echo Targets: test testall clean

tests:
	@cd tests; pytest

testall:
	cd testall; ./testall.sh

clean:
	@rm -f aa bb cc dd ee
	@rm -f *.o
	@rm -f *.so
	@rm -f *.pyd
	@rm -f *.dll
	@rm -f *.pyc

# EOF
