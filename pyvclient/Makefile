# Use this to build and test modules

.PHONY: testx, testx2, tests

all:
	@echo Targets: server tests test test2 hello clean  init

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

















