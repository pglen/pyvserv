# ------------------------------------------------------------------------
# Makefile for bluepoint python module. Python 2 version.
#
# a.) Simplified for CentOS compile. Edit path for your system.
# b.) Rebilding on MSYS2
#

#COPT =  -DNDEBUG -m32 -g -O3 -Wall -Wstrict-prototypes -fPIC -DMAJOR_VERSION=1 \
#    -DMS_WIN32 -DMINOR_VERSION=0 -I/mingw32/include/python2.7
#
# This way inference rules can be used.
#CFLAGS=${COPT}

.PHONY: docs clean

# ------------------------------------------------------------------------

all:
	@echo Targets: clean cleanpayload cleandata docs

# This is used in replication testing
cleanalt:
	@rm -rf ~/pyvserver_alt/

cleanall:
	@rm -rf ~/pyvserver/

cleanpayload:
	@rm -rf ~/pyvserver/payload/*

cleanchain:
	@rm -rf ~/pyvserver/chain/*

clean:
	@rm -f aa bb cc dd ee
	@rm -f *.o
	@rm -f *.so
	@rm -f *.pyd
	@rm -f *.pyc
	@rm -rf __pycache__/*
	@rm -rf build/*
	@rm -rf dist/*

test:
	@echo No tests

XPATH=PYTHONPATH=../pyvcommon:../  python -W ignore::DeprecationWarning `which pdoc3` --force --html
docs:
	@${XPATH} -o docs pyvserv.py
	@${XPATH} -o docs pyvfunc.py
	@${XPATH} -o docs pyvreplic.py
	@${XPATH} -o docs pyvstate.py
	@${XPATH} -o docs pyvfunc.py

# EOF