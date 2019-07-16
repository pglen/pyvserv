# Use to build modules

.PHONY: test clean

all:
	@echo Targets: all git build test clean

git:
	git add .
	git commit -m auto
	git push

build:
	@make -C bluepy build
	@make -C bluepy build3

test:
	@make -C client test

clean:
	@make -C client clean
	@make -C bluepy clean
	@make -C server clean
	@make -C common clean










