# Use to build modules

.PHONY: test clean

all:
	@echo Targets: all git blue test

git:
	git add .
	git commit -m auto
	git push

blue:
	@make -C bluepy build

test:
	@make -C pyclient test

clean:
	@make -C pyclient clean
	@make -C bluepy clean
	@make -C pyserv clean
	@make -C common clean







