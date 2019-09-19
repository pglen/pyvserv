# Use to build modules

.PHONY: test

test:
	# Start server
	@-cd ../server; python ./pyserv.py &
	@-./pycli_ping.py -q
	@-./pycli_hello.py -q
	@-./pycli_ver.py -q
	@-./pycli_gethelp.py -q
	@-./pycli_key.py -q
	@#-./pycli_kadd.py -q
	@#-./pycli_kini.py -q
	#@-./pycli_uadd.py -q
	#@-./pycli_uini.py -q
	@#-./pycli_down.py -q
	@#-./pycli_enc.py -q
	@#-./pycli_up.py -q
	@-./killserv.sh

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















