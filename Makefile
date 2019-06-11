# Use to build modules

.PHONY: test clean

all:
	@echo Targets: all git build test

git:
	git add .
	git commit -m auto
	git push

build:
	@make -C bluepy build

test:
	@make -C pyclient test

clean:
	@make -C pyclient clean
	@make -C bluepy clean
	@make -C server clean
	@make -C common clean









