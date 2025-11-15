# Use it to build modules, generate service files, install sevices
#
# These scripts work on the default configuration

.PHONY: tests clean docs

all:
	@echo Targets: git tests clean -- for more targets see: make help

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

cleansubs:
	@make -C pyvclient clean
	@make -C pyvserver clean
	@make -C pyvcommon clean
	@make -C pyvtools clean

clean:
	echo Clean ...
	@rm -f aa bb cc pyvserv.deb
	@-find .  -type f  -name  "*.pyc" -exec rm -rf {} \;
	@-find .  -type d  -name "__pycache__" -exec rm -rf {}  \;
	@rm -rf build-tmp/*
	@rm -rf  dist/*
	@rm -rf  build/*
	@rm -f pyvserv.service
	@rm -rf pip_pyvserv/*

cleanall:
	@rm -rf ~/pyvserver/*

cleanalt:
	@rm -rf ~/pyvserver_alt/*

cleankeys:
	@rm -rf ~/pyvserver/keys/*
	@rm -rf ~/pyvserver/private/*

tests:
	@  ./isalive.py
	@echo "Executing tests in the pyvclient directory"
	cd pyvclient/tests; pytest; cd ..
	@echo "Warning: On empty database this test created demo credentials."
	@echo "It is recommended to delete all test generated data"

ARG1=$(shell pwd)/../pyvguicom/pyvguicom
ARG2=$(shell pwd)/pyvcommon

XPATH=PYTHONPATH=${ARG1}:${ARG2} python3 -W ignore::DeprecationWarning `which pdoc` --force --html
#FILES=$(wildcard *.py)

docs:
	@#echo ${FILES}
	@#${XPATH}  -o pyvgui/guilib/docs pyvgui/guilib/mainwin.py
	@${XPATH}  -o pyvgui/guilib/docs pyvgui/guilib/mainwinpeople.py
	@${XPATH}  -o pyvgui/guilib/docs pyvgui/guilib/mainwinballot.py
	@${XPATH}  -o pyvgui/guilib/docs pyvgui/guilib/mainwinvote.py
	@#${XPATH} -o pyvgui/guilib/docs pyvgui/guilib/mainwintally.py

	@${XPATH}  -o pyvgui/docs pyvgui/pyvpeople.py
	@${XPATH}  -o pyvgui/docs pyvgui/pyvservui.py
	@${XPATH}  -o pyvgui/docs pyvgui/pyvballot.py
	@${XPATH}  -o pyvgui/docs pyvgui/pyvvote.py
	@${XPATH}  -o pyvgui/docs pyvgui/pyvtally.py
	@${XPATH}  -o pyvgui/docs pyvgui/pyvcpanel.py

	@${XPATH}  -o pyvtools/docs pyvtools/pyvgenkeys.py
	@${XPATH}  -o pyvtools/docs pyvtools/pyvgenkey.py

checksum:
	@echo "Checking SHA256 sums; No output if OK."
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

disableservice:
	sudo systemctl disable --now pyvserv.service

# The pyvserv may be installed in a virtual environment.
# Control it from here

install:
	./pyvserv_install.sh

uninstall:
	./pyvserv_uninstall.sh

installvirt:
	./pyvserv_venv_install.sh

startvirt:
	./pyvserv_venv.sh

git2:
	@$(eval AAA=$(shell zenity --entry --text "Enter Git Commit Message:"))
	git add .
	git commit -m "${AAA}"
	git push

testinput:
	@$(eval AAA=$(shell zenity --entry --text "Shell Prompt:"))
	@echo Typed text: \"${AAA}\"

# EOF
