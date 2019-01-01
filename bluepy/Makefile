# ------------------------------------------------------------------------
# Makefile for bluepoint2 python module
#
# a.) Simplified for CentOS compile. Edit path for your system.
# b.) Rebilding on MSYS2
#

COPT =  -DNDEBUG -m32 -g -O3 -Wall -Wstrict-prototypes -fPIC -DMAJOR_VERSION=1 \
    -DMS_WIN32 -DMINOR_VERSION=0 -I/mingw32/include/python2.7 
                
# This way inference rules can be used.                
CFLAGS=${COPT}

# ------------------------------------------------------------------------

all:
	python3 buildme.py

test: all
	@./bluetest.py >cc
	@./bluefile.py -e -f -p 1111 Makefile aa
	@./bluefile.py -d -f -p 1111 aa bb
	@echo Diff should be silent
	@diff Makefile bb
	@rm -f aa bb cc

clean:
	rm -f *.o
	rm -f *.so
	rm -f *.pyd
	rm -f *.dll













