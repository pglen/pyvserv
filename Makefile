#
# Used to build modules, generate service file, install sevice file
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
	@echo  "\tfreshdata   --  clean all data !!! Warning: !!!      "
	@echo  "\tgensun      --  genetrate SHA256 hashes              "
	@echo  "\tchecsum     --  check hashes                         "
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

# untested
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
	@rm -f pyvserv.service

freshdata:
	@rm -rf ~/pyvserver/*

cleanall:
	@rm -rf ~/pyvserver/*

cleankeys:
	@rm -rf ~/pyvserver/keys/*
	@rm -rf ~/pyvserver/private/*

tests:
	echo No tests, look at pyvclient directory

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

checksum:
	@echo Checking SHA256 sums
	@sha256sum -c --quiet shasum.txt

gensum:
	@#echo Started SHA256 gen ... please wait
	./iterproj.py -x shasum.txt -m > shasum.txt

# Generate service file
genservice:
	@./make_servfile.py > tmp
	@# the secondline is executed if file is generated
	@cp tmp pyvserv.service
	@rm -f tmp

# Generate service file
genservice_virt:
	@./make_servfile_virt.py > tmp
	@# the secondline is executed if file is generated
	@cp tmp pyvserv.service
	@rm -f tmp

# Install sevice file; needs sudo
instservice:
	@sudo systemctl stop pyvserv.service
	@sudo cp pyvserv.service /etc/systemd/system
	@sudo systemctl daemon-reload
	@sudo systemctl enable --now  pyvserv.service
	@echo "You may now use systemctl start/stop/disable pyvserv.servce"

# Stat service
statservice:
	systemctl status pyvserv.service

startservice:
	sudo systemctl start pyvserv.service

stopservice:
	sudo systemctl stop pyvserv.service

installvirt:
	./pyvserv_venv_install.sh

startvirt:
	./pyvserv_venv.sh


# EOF
