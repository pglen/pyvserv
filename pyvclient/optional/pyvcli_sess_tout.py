#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, base64

from Crypto.Hash import SHA256
from Crypto import Random

from pyvecc.Key import Key

# This repairs the path from local run to pip run.
try:
    from pyvcommon import support
    base = os.path.dirname(os.path.realpath(support.__file__))
    sys.path.append(os.path.join(base, "."))
except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    from pyvcommon import support

from pyvcommon import support, pycrypt, pyclisup
from pyvcommon import pysyslog, comline

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
    print( "            -l level  - Log level (default: 0)")
    print( "            -c file   - Save comm to file")
    print( "            -s        - Showkey")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    #print( " Needs debug level or verbose to have any output.")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["c:",  "comm",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["s",   "showkey",  "",     None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

    if conf.comm:
        print("Save to filename", conf.comm)

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug
    hand.comm  = conf.comm

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    #print("IP:", ip, respc);
    #print("Initial:", respc);

    resp = hand.client(["akey"])
    #print("akey response", resp)

    if resp[0] != "OK":
        print("Error on getting key:", resp[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    if conf.verbose:
        print("Got akey hash:", "'" + resp[1] + "'")
        pass

    #if conf.pgdebug > 4:
    #    print ("Server response2:\n" +  "'" + resp[1].decode("cp437") +  "'\n")

    hhh = SHA256.new();
    hhh.update(resp[2].encode())
    #hhh.update(bytes(resp[2], "cp437"))

    if conf.pgdebug > 3:
        print("Hash1:  '" + resp[1] + "'")
        print("Hash2:  '" + hhh.hexdigest() + "'")

    # Remember key
    if hhh.hexdigest() !=  resp[1]:
        print("Tainted key, aborting.")
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    hand.pkey = resp[2]

    #if conf.quiet == False:
    #     print("Key response:", resp[0], resp[2][:32], "...")

    if conf.pgdebug > 4:
         print(hand.pkey)

    if conf.pgdebug > 2:
        print ("Server response:", "'" + hhh.hexdigest() + "'")

    if conf.showkey or conf.pgdebug > 5:
        #print("Key:")
        print(hand.pkey)

    try:
        #hand.pubkey = RSA.importKey(hand.pkey)
        hand.pubkey = Key.import_pub(hand.pkey)

        if conf.pgdebug > 4:
            print (hand.pubkey)
    except:
        print("Cannot import public key.")
        support.put_exception("import key")
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    resp0 = hand.client(["hello",], )
    print("Hello (unencrypted) Response:", resp0[1])

    #if conf.pgdebug > 1:
    #    print("Got pub key", hand.pubkey, "size =", hand.pubkey.size_in_bits())

    # Generate communication key
    conf.sess_key = base64.b64encode(Random.new().read(128))
    sss = SHA256.new(); sss.update(conf.sess_key)

    if conf.pgdebug > 2:
        support.shortdump("conf.sess_key", conf.sess_key )

    sess_keyx  = hand.pubkey.encrypt(conf.sess_key)
    ttt = SHA256.new(); ttt.update(sess_keyx.encode())

    if conf.pgdebug > 2:
        support.shortdump("sess_keyx", sess_keyx )

    resp3 = hand.client(["sess", sss.hexdigest(), ttt.hexdigest(), sess_keyx], "", False)
    #print("Sess Response:", resp3)

    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print(resp3[1])
    support.shortdump(" All is encrypted with", conf.sess_key )

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    print("Hello (encrypted) Response:", resp4[:2])

    # --------------------------------------------------------------------
    # Generate communication key, second session and second run

    conf.sess_key2 = base64.b64encode(Random.new().read(128))
    sss2 = SHA256.new(); sss2.update(conf.sess_key2)

    if conf.pgdebug > 2:
        support.shortdump("conf.sess_key2", conf.sess_key2 )

    sess_keyx2  = hand.pubkey.encrypt(conf.sess_key2)
    ttt2 = SHA256.new(); ttt2.update(sess_keyx2.encode())

    if conf.pgdebug > 2:
        support.shortdump("sess_keyx", sess_keyx )

    #print("Key Hexdigest", ttt2.hexdigest()[:16])

    resp4 = hand.client(["sess", sss2.hexdigest(), ttt2.hexdigest(), sess_keyx2],
                                conf.sess_key, False)

    if resp4[0] != "OK":
        print("Err: ", resp4)
        cresp = hand.client(["quit", ], conf.sess_key)
        print ("Server quit response:", cresp)
        sys.exit(0)

    # Make a note of the session key
    #print(resp4[1])
    support.shortdump(" All is encrypted with", conf.sess_key2 )

    # Session estabilished, try a simple command
    resp5 = hand.client(["hello",], conf.sess_key2)
    print("Hello (encrypted2) Response:", resp5[:2])

    print("Waiting for timeout ...    ", end="")
    for aa in range(22, -1, -1):
        print("\b\b\b%2d " % aa, end = "" )
        sys.stdout.flush()
        time.sleep(1)
    print()

    resp5 = hand.client(["hello", ], conf.sess_key2)
    print("Hello (encrypted2) Response:", resp5[:2])
    if resp5[0] != "OK":
        sys.exit()

    hand.client(["quit",],conf.sess_key2)
    hand.close();

    sys.exit(0)

# EOF
