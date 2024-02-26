# Use to build modules

# These scripts work on the default installation

.PHONY: test clean

#@echo Target \'init\' generates an initial key.
#@echo Target \'cleankeys\' deletes all keys.
#@echo Target \'freshdata\' deletes all data.

all:
	@echo Targets: git test clean deb init cleankeys \
            freshdata md5 genmd5 checkmd5

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
	@rm -rf ~/pyvserver/keys/*
	@rm -rf ~/pyvserver/private/*

md5:
	@cat md5sum.txt

checkmd5:
	@md5sum -c --quiet md5sum.txt

genmd5:
	./iterproj.py -m > md5sum.txt

# EOF