# Use this to build and test modules

.PHONY: testx  testx2  tests  docs

all:
	@echo Targets: tests test testopt hello clean docs

init:
	@-python3 ./pyvcli_uini.py -q

deinit:
	@-python3 ./pyvcli_uini.py -q

tests:
	@cd tests; pytest

#OPT="-V"
OPT=""

SSS += $(wildcard f/pyv*.py)
SSS += $(wildcard r/pyv*.py)
SSS += $(wildcard u/pyv*.py)
SSS += $(wildcard optional/pyv*.py)
SSS += $(wildcard pyv*.py)

CWD = $(shell pwd)

#   PYTHONPATH=. python3 $$ii ; \
#   echo  $$ii ; \
#   python3 $$ii ; \

test:
	@for ii in $(SSS); do \
        ./doone.sh $$ii ; \
    done

clean:
	@rm -f aa bb cc dd ee
	@rm -f *.o
	@rm -f *.so
	@rm -f *.pyd
	@rm -f *.dll
	@rm -f *.pyc
	@rm -f *_local
	@rm -rf __pycache__
	@rm -f bigfile*
	@#rm -f test.txt_*
	@rm -f pydbase.p*

PPP=PYTHONPATH=../pyvcommon:../  python -W ignore::DeprecationWarning `which pdoc` --force --html
#PPP=PYTHONPATH=../pyvcommon:../  pdoc --html

# Shortcut to make current doc
onedoc:
	@-${PPP} -o docs  pyvcli_replic.py

docs:
	@-${PPP} -o docs  pyvcli_akey.py
	@-${PPP} -o docs  pyvcli_bigget.py
	@-${PPP} -o docs  pyvcli_cd.py
	@-${PPP} -o docs  pyvcli_cli.py
	@-${PPP} -o docs  pyvcli_fdel.py
	@-${PPP} -o docs  pyvcli_fget.py
	@-${PPP} -o docs  pyvcli_file.py
	@-${PPP} -o docs  pyvcli_fman.py
	@-${PPP} -o docs  pyvcli_fput.py
	@-${PPP} -o docs  pyvcli_gethelp.py
	@-${PPP} -o docs  pyvcli_hello.py
	@-${PPP} -o docs  pyvcli_id.py
	@-${PPP} -o docs  pyvcli_ihost.py
	@-${PPP} -o docs  pyvcli_login.py
	@-${PPP} -o docs  pyvcli_lsd.py
	@-${PPP} -o docs  pyvcli_ls.py
	@-${PPP} -o docs  pyvcli_mkdir.py
	@-${PPP} -o docs  pyvcli_pass.py
	@-${PPP} -o docs  pyvcli_ping.py
	@-${PPP} -o docs  pyvcli_qr.py
	@-${PPP} -o docs  pyvcli_rabs.py
	@-${PPP} -o docs  pyvcli_rcheck.py
	@-${PPP} -o docs  pyvcli_rcount.py
	@-${PPP} -o docs  pyvcli_replic.py
	@-${PPP} -o docs  pyvcli_rget.py
	@-${PPP} -o docs  pyvcli_rlist.py
	@-${PPP} -o docs  pyvcli_rman.py
	@-${PPP} -o docs  pyvcli_rmdir.py
	@-${PPP} -o docs  pyvcli_rput.py
	@-${PPP} -o docs  pyvcli_sess.py
	@-${PPP} -o docs  pyvcli_throt.py
	@-${PPP} -o docs  pyvcli_uadd.py
	@-${PPP} -o docs  pyvcli_uchpass.py
	@-${PPP} -o docs  pyvcli_udel.py
	@-${PPP} -o docs  pyvcli_uena.py
	@-${PPP} -o docs  pyvcli_uini.py
	@-${PPP} -o docs  pyvcli_uman.py
	@-${PPP} -o docs  pyvcli_ver.py
	@-${PPP} -o docs  optional/pyvcli_acc.py
	@-${PPP} -o docs  optional/pyvcli_tout.py
	@-${PPP} -o docs  optional/pyvcli_sess_tout.py

docs_man:
	@-${PPP} -o docs  pyvcli_rman.py
	@-${PPP} -o docs  pyvcli_uman.py
	@-${PPP} -o docs  pyvcli_fman.py

tryx:
	echo `which pdoc`

# EOF
