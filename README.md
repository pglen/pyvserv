#                                Python vServer

 PyvServ is a fully fledged encrypting TCP/IP server written in Python. The
encryption algorithm is bluepoint2. The server can be fully administered from
the protocol side.

 PyvServ contains protocol level encryption, which can be switched on by
instructing the server to use an encryption key.

 PyvServ contains key exchange protocol, so the new session keys
can be transmitted securely, even with zero knowledge.

 PyvServ internally generates a random key, so communication is always

 Project still in motion, not much is usable yet.

### Working so far:

 Bluepoint2. The subdir bluepy contains the 'c' code and the python binding.

    make build;    # operational
    make test;     # operational

#### Partially Working:

    Server.    subdir: server   -- Server has 50% of the commands done
    Client.    subdir: client
    Test Suite.
    Studies.   subdir: study    -- testing subsystems

####  BELOW IS OLD INFO, PLEASE WAIT FOR UPDATE (dec/2018)

 The server's user names and initial keys can only be initialized from the
loopback interface. An unconfigured server will refuse to accept logins,
but can be configured remotely via public key encryption.

 The best way to learn about the operation of the server is to look at the
sample client examples in the client source tree. (Files named pycli_*)

Versioning.

  The 'C' module has a date API, that is generated automatically. Use it to
distinguish algorythm versioning.

    print( "Builddate: ",  bluepy.builddate())







