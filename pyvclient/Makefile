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

#    PYTHONPATH=. python3 $$ii ; \
        #echo  $$ii ; \
        #python3 $$ii ; \

testx:
	@for ii in $(SSS); do \
        ./doone.sh $$ii ; \
    done

test2:
	@python3 ./u/pyvcli_uadd.py
	@python3 ./u/pyvcli_uchpass.py
	@python3 ./u/pyvcli_uman.py
	@python3 ./u/pyvcli_uini.py
	@python3 ./u/pyvcli_uena.py
	@python3 ./u/pyvcli_udel.py
	@python3 ./pyvcli_login.py
	@python3 ./pyvcli_ihost.py
	@python3 ./pyvcli_qr.py
	@python3 ./pyvcli_load.py
	@python3 ./f/pyvcli_fdel.py
	@python3 ./f/pyvcli_fman.py
	@python3 ./f/pyvcli_file.py
	@python3 ./f/pyvcli_fput.py
	@python3 ./f/pyvcli_fget.py
	@python3 ./pyvcli_akey.py
	@python3 ./pyvcli_sess.py
	@python3 ./pyvcli_id.py
	@python3 ./pyvcli_cd.py
	@python3 ./pyvcli_gethelp.py
	@python3 ./pyvcli_throt.py
	@python3 ./pyvcli_hello.py
	@python3 ./pyvcli_cli.py
	@python3 ./pyvcli_ping.py
	@python3 ./optional/pyvcli_tout.py
	@python3 ./optional/pyvcli_acc.py
	@python3 ./optional/pyvcli_sess_tout.py
	@python3 ./pyvcli_pass.py
	@python3 ./pyvcli_ls.py
	@python3 ./pyvcli_bigget.py
	@python3 ./r/pyvcli_rcount.py
	@python3 ./r/pyvcli_rabs.py
	@python3 ./r/pyvcli_rman.py
	@python3 ./r/pyvcli_rlist.py
	@python3 ./r/pyvcli_rput.py
	@python3 ./r/pyvcli_rcheck.py
	@python3 ./r/pyvcli_rget.py
	@python3 ./r/pyvcli_rmdir.py
	@python3 ./pyvcli_lsd.py
	@python3 ./pyvcli_ver.py
	@python3 ./pyvcli_mkdir.py

test3:
	python3 ./pyvcli_akey.py
	python3 ./pyvcli_hello.py
	python3 ./pyvcli_qr.py
	python3 ./pyvcli_throt.py
	python3 ./pyvcli_bigget.py
	python3 ./pyvcli_id.py
	python3 ./pyvcli_rabs.py
	python3 ./pyvcli_uadd.py
	python3 ./pyvcli_cd.py
	python3 ./pyvcli_ihost.py
	python3 ./pyvcli_rcheck.py
	python3 ./pyvcli_uchpass.py
	#python3 ./pyvcli_cli.py
	python3 ./pyvcli_load.py
	python3 ./pyvcli_rcount.py
	python3 ./pyvcli_udel.py
	python3 ./pyvcli_fdel.py
	python3 ./pyvcli_login.py
	python3 ./pyvcli_rget.py
	python3 ./pyvcli_uena.py
	python3 ./pyvcli_fget.py
	python3 ./pyvcli_lsd.py
	python3 ./pyvcli_rlist.py
	#python3 ./pyvcli_uini.py
	python3 ./pyvcli_file.py
	python3 ./pyvcli_ls.py
	python3 ./pyvcli_rman.py
	python3 ./pyvcli_uman.py
	#python3 ./pyvcli_fman.py
	python3 ./pyvcli_mkdir.py
	python3 ./pyvcli_rmdir.py
	python3 ./pyvcli_ver.py
	python3 ./pyvcli_fput.py
	python3 ./pyvcli_pass.py
	python3 ./pyvcli_rput.py
	python3 ./pyvcli_gethelp.py
	python3 ./pyvcli_ping.py
	python3 ./pyvcli_sess.py
	@echo "End of tests"

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
