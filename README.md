#  PyvServer
## 	Python fully encrypted TCP/IP server

 &nbsp; &nbsp; PyvServ is a fully fledged encrypting TCP/IP server written in Python. The
encryption algorithm is AES. The server can be fully administered from
the protocol side.

 &nbsp; &nbsp; PyvServ contains protocol level encryption, which can be switched on by
instructing the server to use an encryption (session) key.

 &nbsp; &nbsp; PyvServ contains a key exchange protocol, so the new session keys
can be transmitted securely. The key exchange is based on ECC.

 PyvServ has utilities to generate encryption keys. At least one
key needs to be generated before use. (now automatic) The server picks from
a pool of keys, so communication data is always distinctive. Make sure you
generate them with the 'pyvgenkeys' utility.

 PyvServ has blockchain enpowered back end. The new data is linked to the
previous record. Utilities to verify the data are also provided.
(dbaseadm and chainadm)

 PyvServ has file upload / download capabilities with encrypted transport.

 PyvServ has replication facilities via a client based 'I have You have'
 mechanism featuring encrypted transport. It is also capable of replication
 on a replicate when received mechanism. The replicted records are marked,
 so replication does not enter looping.

 Project is still in motion, but a lot of it is usable.

#### Installation:

    pip install pyvserv

 Dependencies:

 Most linux system have all the dependencies by default. Some dependencies
 are added automatically on installation.

     pydbase, pyvpacker, pyvecc

 The firewall needs to be opened for incoming connections on port xxxx

For example (assuming port 6666):

    sudo iptables -A INPUT -p tcp --dport 6666
    sudo iptables -A INPUT -p tcp --sport 6666

#### Working parts:

    Server.     subdir: pyvserver       -- Server has 90% of the commands done
    Client.     subdir: pyvclient       -- 90% the commands
    Tool Suite. subdir: pyvtools        -- Key generation etc ...
    Test Suite. subdir: pyvclient/tests -- Test pass
    Studies.    subdir: study           -- testing/learning subsystems (ignore it)

#### Quick start:

 One can mimic global connectivity on a single machine. This would allow the study
of the client / server interaction before live deployment. This
chapter assumes installation from github, replicating directory
structure on the local drive.

    open terminal window
    navigate to the server's pyvserver subdir
    type ./pyvserv.py

    open another terminal window
    navigate to the pyvclient subdir
    type ./pycli_hello.py

The following (and more) should be printed on command line:

    ./pycli_hello.py
    Server initial: ['OK', 'pyvserv 1.0 ready']
    resp ['OK', 'Hello', '6ccdaaf1-a22d-4140-9608-8fb93a8845af', '11812']
    Server quit response: ['OK', 'Bye', '11812']

Quick rundown of the above test: 1.) Server responds to connection
2.) Delivers OK status, hello message, server serial number, unique id
3.) Server signs off. This interaction is typical of all the commands.

 The best way to learn about the operation of the server is to look at the
sample client examples in the client source tree. (Files named pycli_*)

## Testing:

 All pytest cases pass. Note that the for the pytest client tests one needs to
 start the 'pyvserv.py' server.
 The server --port and --dataroot option can ba used to start the server in an alternate
 universe.  Please make sure it does not interfere with production.

   More test coming soon ....

    ============================= test session starts ==============================
    platform linux -- Python 3.10.12, pytest-7.4.3, pluggy-1.0.0
    rootdir: /home/peterglen/pgpygtk/pyvserv
    collected 9 items

    test_afirst.py .                                                         [ 11%]
    test_file.py .                                                           [ 22%]
    test_help.py .                                                           [ 33%]
    test_id.py .                                                             [ 44%]
    test_key.py .                                                            [ 55%]
    test_login.py .                                                          [ 66%]
    test_sess.py ..                                                          [ 88%]
    test_ver.py .                                                            [100%]

    ============================== 9 passed in 1.35s ===============================

Additional tests can ve found in the test directory.

## History:

    1.0.0.  4/12/22		       No py2 support (no release yet)
    1.0.0   Sun 03.Mar.2024    Beta ready
    1.0.0   Mon 11.Mar.2024    PIP installation with utils

Written by Peter Glen

// EOF


