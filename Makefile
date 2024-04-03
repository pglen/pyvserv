#
# Use to build modules, generate service file, install sevice file
#

# These scripts work on the default installation

.PHONY: tests clean docs

all:
	@echo Targets: git tests clean deb -- for more targets see make help

help:
	@echo  "\tgit         --  checkin to git (for developers)      "
	@echo  "\ttests       --  execute tests                        "
	@echo  "\tclean       --  clean python temporaries             "
	@echo  "\tcleankeys   --  clean keys                           "
	@echo  "\tfreshdata   --  clean all data !!! Warning: !!!     "
	@echo  "\tmd5         --  show md5 hashes                      "
	@echo  "\tgenmd5      --  genetate md5 hashes                  "
	@echo  "\tcheckmd5    --  check md5 hashes                     "
	@echo  "\tdocs        --  generate documents                   "
	@echo  "\tgensevice   --  generate sevice file                 "
	@echo  "\tinstservice --  install service                      "
	@echo  "\tstatservice --  see service status                   "

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
	@#make -C pyvclient clean
	@#make -C pyvserver clean
	@#make -C pyvcommon clean
	@rm -f aa bb cc pyvserv.deb
	@rm -rf build-tmp/*
	@rm -rf  dist/*
	@rm -rf  build/*

freshdata:
	@rm -rf ~/pyvserver/*

cleankeys:
	@rm -rf ~/pyvserver/keys/*
	@rm -rf ~/pyvserver/private/*

tests:
	echo No tests

XPATH="pyvcommon,../pyvguicom,pyvgui/guilib "
XPATH2="pyvcommon:../pyvguicom:../pyvguicom/pyvguicom:pyvgui/guilib"

docs:
	@#PYTHONPATH=pyvcommon pdoc --force --html -o docs pyvserver/pyvserv.py
	@#PYTHONPATH=pyvcommon pdoc --force --html -o docs pyvserver/pyvfunc.py
	@#PYTHONPATH=pyvcommon pdoc --force --html -o docs pyvserver/pyvreplic.py
	@#PYTHONPATH=pyvcommon pdoc --force --html -o docs pyvserver/pyvstate.py
	@#PYTHONPATH=pyvcommon pdoc --force --html -o docs pyvtools/pyvgenkeys.py
	@#PYTHONPATH=pyvcommon pdoc --force --html -o docs pyvtools/pyvgenkey.py
	@PYTHONPATH=${XPATH} pdoc --force --html -o docs pyvgui/pyvcpanel.py
	@PYTHONPATH=${XPATH} pdoc --force --html -o docs pyvgui/pyvservui.py
	@PYTHONPATH=${XPATH} pdoc --force --html -o docs pyvgui/pyvtally.py
	@PYTHONPATH=${XPATH2} pdoc --force --html -o docs pyvgui/guilib/mainwin.py
	@PYTHONPATH=${XPATH2} pdoc --force --html -o docs pyvgui/guilib/mainwinserv.py
	@PYTHONPATH=${XPATH2} pdoc --force --html -o docs pyvgui/guilib/mainwintally.py

md5:
	@cat md5sum.txt

checkmd5:
	@echo The 'md5sum.txt' should fail, but no others
	@md5sum -c --quiet md5sum.txt

genmd5:
	@#echo Started md5 gen ... please wait
	./iterproj.py -m > md5sum.txt

# Generate service file
gensevice:
	@./make_servfile.py > tmp
	@# the secondline is executed if file is generated
	@cp tmp pyvserv.service

# Install sevice file; needs sudo
instsevice:
	sudo cp pyvserv.service /etc/systemd/system
	sudo systemctl enable --now  pyvserv.service

# Stat service
statservice:
	systemctl status pyvserv.service

# EOF
