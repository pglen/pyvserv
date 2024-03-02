# Use this to build and test modules

.PHONY: testx, testx2, tests

all:
	@echo Targets: server tests test test2 hello clean cleandata init

server:
	@# Start server
	@-cd ../server; python ./pyvserv.py &

init:
	rm -rf ../data/.pyvserv/passwd.secret
	-python3 ./pycli_uini.py -q

tests:
	@cd tests
	@pytest

test:
	-python3 ./pycli_ping.py
	-python3 ./pycli_hello.py
	-python3 ./pycli_ver.py
	-python3 ./pycli_gethelp.py
	-python3 ./pycli_akey.py
	-python3 ./pycli_sess.py
	-python3 ./pycli_pass.py
	-python3 ./pycli_ls.py
	-python3 ./pycli_lsd.py
	-python3 ./pycli_fdel.py -q
	-python3 ./pycli_fput.py -q
	-python3 ./pycli_fget.py -q

# This is optional (untested)
test2:
	-python3 ./pycli_kadd.py -q
	-python3 ./pycli_kini.py -q
	-python3 ./pycli_uadd.py -q
	-python3 ./pycli_uini.py -q
	-python3 ./pycli_down.py -q
	-python3 ./pycli_enc.py -q
	-python3 ./pycli_up.py -q
	-python3 ./killserv.sh

# "ps xa | grep "pyserv.py" | grep python")
#	@-cd ../server; python ./pyserv.py &
#	@-./pycli_hello.py -q
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

cleandata:
	@rm -rf ~/pyvserver/payload/*

















