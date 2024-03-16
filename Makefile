# Use to build modules

# These scripts work on the default installation

.PHONY: tests clean docs

#@echo Target \'init\' generates an initial key.
#@echo Target \'cleankeys\' deletes all keys.
#@echo Target \'freshdata\' deletes all data.

all:
	@echo Targets: git tests clean deb init cleankeys \
            freshdata md5 genmd5 checkmd5 docs

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

tests:
	echo No tests

docs:
	@#PYTHONPATH=pyvcommon pdoc  --force --html -o docs pyvserver/pyvserv.py
	@#PYTHONPATH=pyvcommon pdoc  --force --html -o docs pyvserver/pyvfunc.py
	@#PYTHONPATH=pyvcommon pdoc  --force --html -o docs pyvserver/pyvreplic.py
	@#PYTHONPATH=pyvcommon pdoc  --force --html -o docs pyvserver/pyvstate.py
	@#PYTHONPATH=pyvcommon pdoc  --force --html -o docs pyvtools/pyvgenkeys.py
	@#PYTHONPATH=pyvcommon pdoc  --force --html -o docs pyvtools/pyvgenkey.py
	@PYTHONPATH=pyvcommon:../pyvguicom:pyvgui/guilib  pdoc  --force --html -o docs pyvgui/pyvcpanel.py
	@PYTHONPATH=pyvcommon:../pyvguicom:pyvgui/guilib  pdoc  --force --html -o docs pyvgui/pyvservui.py
	@PYTHONPATH=pyvcommon:../pyvguicom:pyvgui/guilib  pdoc  --force --html -o docs pyvgui/pyvtally.py
	@PYTHONPATH=pyvcommon:../pyvguicom:pyvgui/guilib  pdoc  --force --html -o docs pyvgui/guilib/mainwin.py
	@PYTHONPATH=pyvcommon:../pyvguicom:pyvgui/guilib  pdoc  --force --html -o docs pyvgui/guilib/pgui.py

md5:
	@cat md5sum.txt

checkmd5:
	@md5sum -c --quiet md5sum.txt

genmd5:
	./iterproj.py -m > md5sum.txt

# EOF
