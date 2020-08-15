#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

sys.path.append('../common')
import support, pycrypt, pyservsup, pyclisup
import pysyslog, crysupp, pypacker, comline

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 9999)")
    print( "            -l level  - Log level (default: 0)")
    print( "            -v        - Verbose")
    print( "            -s        - Showkey")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print( " Needs debug level or verbose to have any output.")
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     9999,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["s",   "showkey",  "",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    try:
        resp2 = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    resp3 = hand.client(["hello",] , "", False)
    print("Hello Response:", resp3)

    #if conf.quiet == False:
    #    print ("Server initial:", resp2)

    resp = hand.client(["akey"])
    kkk = resp.split()

    if kkk[0] != "OK":
        print("Error on getting key:", resp)
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    #if conf.verbose:
    #    print ("Server response:", "'" + kkk + "'")

    if conf.verbose:
        print("Got hash:", "'" + kkk[1] + "'")
        print()

    resp2 = hand.getreply()

    if conf.pgdebug > 4:
        print ("Server response2:\n" +  "'" + resp2.decode("cp437") +  "'\n")

    hhh = SHA512.new(); hhh.update(resp2)

    if conf.pgdebug > 3:
        print("Hash1:  '" + kkk[2] + "'")
        print("Hash2:  '" + hhh.hexdigest() + "'")

    # Remember key
    if hhh.hexdigest() !=  kkk[2]:
        print("Tainted key, aborting.")
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    hand.pkey = resp2
    if conf.quiet == False:
         print("Key response:", kkk[0], kkk[2][:16], "...")

    if conf.pgdebug > 4:
         print(hand.pkey)

    if conf.pgdebug > 2:
        print ("Server response:", "'" + hhh.hexdigest() + "'")

    if conf.showkey or conf.pgdebug > 5:
        print("Key:")
        print(hand.pkey)

    try:
        hand.pubkey = RSA.importKey(hand.pkey)
        if conf.pgdebug > 4:
            print (hand.pubkey)
    except:
        print("Cannot import public key.")
        support.put_exception("import key")
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    if conf.pgdebug > 1:
        print("Got ", hand.pubkey, "size =", hand.pubkey.size())

    # Generate communication key
    conf.sess_key = Random.new().read(512)
    sss = SHA512.new(); sss.update(conf.sess_key)

    if conf.pgdebug > 1:
        print("Session key dump:")
        print(crysupp.hexdump(conf.sess_key[:16]))

    cipher = PKCS1_v1_5.new(hand.pubkey)
    #print ("cipher", cipher.can_encrypt())

    sess_keyx = cipher.encrypt(conf.sess_key)
    ttt = SHA512.new(); ttt.update(sess_keyx)

    if conf.pgdebug > 3:
        print("sess_keyx")
        print(crysupp.hexdump(sess_keyx))

    resp = hand.client(["sess", sss.hexdigest(), ttt.hexdigest(), sess_keyx], "", False)
    #print("Sess Response:", resp)

    kkk = resp.split()

    if kkk[0] != "OK":
        print("Error on setting session:", resp)
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    print("Sess Key ACCEPTED:",  resp)

    # Session estabilished, try a simple command
    resp3 = hand.client(["hello",], conf.sess_key, False)

    #resp3 = hand.client(["hello",] , "", False)
    print("Post session Hello Response:", resp3)

    hand.client(["quit",])
    hand.close();

    sys.exit(0)

# EOF

