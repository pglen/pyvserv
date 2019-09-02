#                                Python vServer

 PyvServ is a fully fledged encrypting TCP/IP server written in Python. The
encryption algorithm is bluepoint2. The server can be fully administered from
the protocol side.

 PyvServ contains protocol level encryption, which can be switched on by
instructing the server to use an encryption key.

 PyvServ contains key exchange protocol, so the new session keys
can be transmitted securely, even with zero knowledge.

 PyvServ internally generates random keys, and spools aymmetric key generation,
so communication data is always distinctive.

 Project still in motion, not much is usable yet.

### Working so far:

 Bluepoint2. The subdir bluepy contains the 'c' code and the python binding.

    make build;    # operational
    make test;     # operational

    Both py2 and py3 supported. Current focus: py2

#### Partially Working:

    Server.     subdir: server      -- Server has 50% of the commands done
    Client.     subdir: client
    Test Suite. subdir: test

    Studies.    subdir: study       -- testing subsystems
                subdir: pycrypto    -- test crypto functions

#### Versioning.

  The 'C' module has a date API, that is generated automatically. Use it to
distinguish algorythm versioning.

    print( "Builddate: ",  bluepy.builddate())

Quick start:

  open terminal window
  navigate to server subdir
  type ./pyserv.py

  open another terminal window
  navigate to client subdir
  type ./pycli_hello.py

The following should be printed on command line:

    > ./pycli_hello.py
    > Server initial: OK pyserv ready
    > Server response: OK Hello

 The best way to learn about the operation of the server is to look at the
sample client examples in the client source tree. (Files named pycli_*)

All tests are base on python2, some modules function on both py2 and py3.







