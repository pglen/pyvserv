# Use this to build and test modules

.PHONY: testx, testx2, tests, docs

all:
	@echo Targets: server tests test test2 hello clean docs

server:
	@# Start server
	@-cd ../server; python ./pyvserv.py &

init:
	rm -rf ../data/.pyvserv/passwd.secret
	-python3 ./pyvcli_uini.py -q

tests:
	@cd tests; pytest

test:
	-python3 ./pyvcli_ping.py
	-python3 ./pyvcli_hello.py
	-python3 ./pyvcli_ver.py
	-python3 ./pyvcli_gethelp.py
	-python3 ./pyvcli_akey.py
	-python3 ./pyvcli_sess.py
	-python3 ./pyvcli_pass.py
	-python3 ./pyvcli_ls.py
	-python3 ./pyvcli_lsd.py
	-python3 ./pyvcli_fdel.py -q
	-python3 ./pyvcli_fput.py -q
	-python3 ./pyvcli_fget.py -q

# This is optional (untested)
test2:
	-python3 ./pyvcli_kadd.py -q
	-python3 ./pyvcli_kini.py -q
	-python3 ./pyvcli_uadd.py -q
	-python3 ./pyvcli_uini.py -q
	-python3 ./pyvcli_down.py -q
	-python3 ./pyvcli_enc.py -q
	-python3 ./pyvcli_up.py -q
	-python3 ./killserv.sh

# "ps xa | grep "pyserv.py" | grep python")
#	@-cd ../server; python ./pyserv.py &
#	@-./pyvcli_hello.py -q
#	@-./killserv.sh

hello:
	@./testhello.sh

clean:
	@rm -f aa bb cc dd ee
	@rm -f *.o
	@rm -f *.so
	@rm -f *.pyd
	@rm -f *.dll
	@rm -f *.pyc
	@rm -f *_local

#cleandata:
#	@rm -rf ~/pyvserver/payload/*

docs:
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_qr.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_rput.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_cd.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_ls.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_uena.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_cli.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_mkdir.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_uini.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_fdel.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_pass.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_ver.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_fget.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_ping.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_file.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_fput.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_rget.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_gethelp.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_rlist.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_hello.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_rput.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_id.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_sess.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_acc.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_ihost.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_sess_tout.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_akey.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_login.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_tout.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_bigget.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_lsd.py
	@-PYTHONPATH=../pyvcommon pdoc  --force --html -o docs  pyvcli_uadd.py

# EOF
