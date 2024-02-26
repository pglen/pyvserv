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
	#make clean
	git add .
	git commit -m auto
	git push
	#git push local

hello:
	@make -C client hello

deb:  build build3
	./build-deb.sh

clean:
	@make -C pyvclient clean
	@make -C pyvserver clean
	@make -C pyvcommon clean
	@rm -f aa bb cc pyvserv.deb
	@rm -rf ./build-tmp

freshdata:
	@rm -rf ~/pyvserver/*

cleankeys:
	@rm -rf ~/pyvserver/keys

md5:
	echo md5












