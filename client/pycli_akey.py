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
import support, pycrypt, pyservsup, pyclisup, pywrap
import pysyslog, crysupp, pypacker, comline

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 9999)")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -s        - Showkey")
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

    if conf.quiet == False:
        print ("Server initial:", hand.pb.decode_data(resp2[1])[0])

    resp = hand.client(["akey"])

    if conf.verbose:
        print("got response: ", resp[0:3])

    if conf.pgdebug > 2:
        print("Got hash:", "'" + resp[2] + "'")

    if conf.pgdebug > 2:
        print ("Server pub key response:\n" +  "'" + str(resp[3]) +  "'\n")

    hhh = SHA512.new(); hhh.update(resp[3])
    ddd = hhh.hexdigest()

    if conf.pgdebug > 1:
        print("Hash1:\n" + resp[2], "\nHash2:\n" + ddd + "\n")

    # Remember key
    if ddd !=  resp[2]:
        print("Tainted key")
    else:
        hand.pkey = resp[3]
        if conf.quiet == False:
             print("Key OK")

    if conf.showkey:
        print("Key:")
        print(hand.pkey.decode("cp437"))

    try:
        hand.pubkey = RSA.importKey(hand.pkey)
        if conf.pgdebug > 0:
            print (hand.pubkey)
    except:
        print("Cannot import public key.")
        support.put_exception("import key")

    print("Got ", hand.pubkey, "size =", hand.pubkey.size())

    hand.client(["quit"])
    hand.close();

    sys.exit(0)

# EOF









