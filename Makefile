# Use to build modules

.PHONY: test clean

all:
	@echo Targets: git build test clean deb init cleankeys
	@echo Target \'build\' makes the \'C\' libs
	@echo Target \'init\' generates an initial key.
	@echo Target \'cleankeys\' deletes all keys.

init:
	@python3 ./tools/genkey.py

git:
	git add .
	git commit -m auto
	git push
	git push local

build:
	#obsolete, build for py3 only
	#@make -C bluepy build
	@make -C bluepy build3

build3:
	@make -C bluepy build3

test:
	@make -C client test

hello:
	@make -C client hello

deb:  build build3
	./build-deb.sh

clean:
	@make -C client clean
	@make -C bluepy clean
	@make -C server clean
	@make -C common clean
	@rm -f aa bb cc pyvserv.deb
	@rm -rf ./build-tmp

cleankeys:
	@rm -rf ./data/keys

md5:













