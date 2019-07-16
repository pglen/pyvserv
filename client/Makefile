# Use to build modules

.PHONY: test

test:
	# Start server
	#@-cd ../server; python ./pyserv.py &
	@-./pycli_ping.py -v
	@-./pycli_hello.py -v
	@-./pycli_ver.py -v
	@-./pycli_gethelp.py -v
	@-./pycli_kadd.py -v
	@-./pycli_kini.py -v
	@-./pycli_uadd.py -v
	@-./pycli_uini.py -v
	#@-./pycli_down.py -v
	#@-./pycli_enc.py -v
	#@-./pycli_up.py -v
	#@-./killserv.sh

clean:
	@rm -f aa bb cc dd ee
	@rm -f *.o
	@rm -f *.so
	@rm -f *.pyd
	@rm -f *.dll
	@rm -f *.pyc










