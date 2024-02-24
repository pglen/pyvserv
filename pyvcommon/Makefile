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
	@echo Targets: test test3 clean

#diffit:

test:
	@cd tests; make test

test2:
	@echo Diffs should be silent
	@python2 pypacker.py >cc
	@diff -w test.org cc
	@rm -f aa bb cc dd ee

test3:
	@echo Diffs should be silent
	@python3 pypacker.py >cc
	@diff -w test.org cc
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

























