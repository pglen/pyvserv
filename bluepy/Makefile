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

# We build with buildutils

# ------------------------------------------------------------------------

all:
	@echo Targets: build test test3 git clean deb

# the .so targets

bluepy_c.so:  bluepy_c.c bluepoint2.c
	@python buildme.py

bluepy3_c.so: bluepy_c.c  bluepoint2.c
	@python3 buildme3.py

# Building modules:

build: bluepy_c.so

build3: bluepy3_c.so

# Testing modules:

test: build
	@echo Diffs should be silent
	@python bluetest.py >cc
	@diff -w test.org cc
	@python bluefile.py -e -f -p 1111 Makefile aa
	@python bluefile.py -d -f -p 1111 aa bb
	@diff Makefile bb
	@rm -f aa bb cc dd ee

test3: build3
	@echo Diffs should be silent
	@python3  bluetest.py >cc
	@diff -w test.org cc
	@python3 ./bluefile.py -e -f -p 1111 Makefile aa
	@python3 ./bluefile.py -d -f -p 1111 aa bb
	@diff Makefile bb
	@rm -f aa bb cc dd ee

git:
	@git add .
	@git commit -m autocheck

clean:
	@rm -f aa bb cc dd ee
	@rm -f *.o
	@rm -f *.so
	@rm -f *.pyd
	@rm -f *.dll
	@rm -f *.pyc
	@rm -rf ./build/*

# EOF