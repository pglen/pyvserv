# Use to build and test modules

.PHONY: test

all:
	@echo Targets: server test test2 hello clean

server:
	@# Start server
	@-cd ../server; python ./pyvserv.py &

test:
	-python3 ./pycli_ping.py
	-python3 ./pycli_hello.py
	-python3 ./pycli_ver.py
	-python3 ./pycli_gethelp.py
	-python3 ./pycli_akey.py
	-python3 ./pycli_sess.py
	#-python3 ./pycli_pass.py
	#-python3 ./pycli_ls.py

test2:
	#@-python3 ./pycli_key.py
	#@-python3 ./pycli_kadd.py -q
	#@-python3 ./pycli_kini.py -q
	#@-python3 ./pycli_uadd.py -q
	#@-python3 ./pycli_uini.py -q
	#@-python3 ./pycli_down.py -q
	#@-python3 ./pycli_enc.py -q
	#@-python3 ./pycli_up.py -q
	#@-python3 ./killserv.sh

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

















