# Use this to build and test modules

.PHONY: testx  testx2  tests  docs

all:
	@echo Targets: tests test testopt hello clean docs

init:
	rm -rf ../data/.pyvserv/passwd.secret
	-python3 ./pyvcli_uini.py -q

tests:
	@cd tests; pytest

#OPT="-V"
OPT=""

test:
	@-python3 ./pyvcli_hello.py ${OPT}
	@-python3 ./pyvcli_ping.py ${OPT}
	@-python3 ./pyvcli_ver.py  ${OPT}
	@-python3 ./pyvcli_gethelp.py  ${OPT}
	@-python3 ./pyvcli_akey.py  ${OPT}
	@-python3 ./pyvcli_sess.py  ${OPT}
	@-python3 ./pyvcli_pass.py  ${OPT}
	@-python3 ./pyvcli_ls.py  ${OPT}
	@-python3 ./pyvcli_lsd.py  ${OPT}
	@-python3 ./pyvcli_fdel.py  ${OPT}
	@-python3 ./pyvcli_fput.py  ${OPT}
	@-python3 ./pyvcli_fget.py  ${OPT}
	@-python3 ./pyvcli_uadd.py  ${OPT}
	@-python3 ./pyvcli_uini.py  ${OPT}
	@-python3 ./pyvcli_cli.py -x ls ${OPT}

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
	@rm -f test.txt*

PPP=PYTHONPATH=../pyvcommon:../  python -W ignore::DeprecationWarning `which pdoc` --force --html
#PPP=PYTHONPATH=../pyvcommon:../  pdoc --html

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
