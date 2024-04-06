#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

from pyvecc.Key import Key

from Crypto.Hash import SHA512
from Crypto.Hash import SHA256
from Crypto import Random

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
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
    ["p:",  "port",     6666,   None],      \
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

    #print(dir(RSA))
    #print(dir(RSA.RsaKey))
    #sys.exit(0)

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
    if resp[0] != "OK":
        print("key resp", resp)
        sys.exit(1)

    if conf.verbose:
        print("got response to akey: ", resp)

    if conf.pgdebug > 2:
        print("Got hash:", "'" + resp[1] + "'")

    if conf.pgdebug > 3:
        print ("Server pub key response:\n" +  "'" + str(resp[2]) +  "'\n")

    hhh = SHA256.new(); hhh.update(resp[2].encode())
    ddd = hhh.hexdigest()

    if conf.pgdebug > 1:
        print("Hash1:\n" + str(resp[2]), "\nHash2:\n" + str(ddd) + "\n")

    # Remember key
    if ddd !=  resp[1]:
        print("Tainted key")
    else:
        hand.pkey = resp[2]
        if conf.quiet == False:
             print("Key OK")

    if conf.showkey:
        print("Key:")
        print(hand.pkey)

    try:
        #hand.pubkey = RSA.importKey(hand.pkey)
        hand.pubkey = Key.import_pub(hand.pkey)
        if conf.pgdebug > 0:
            print (hand.pubkey)
    except:
        print("Cannot import public key.")
        support.put_exception("import key")

    #print("Got ", hand.pubkey )
    #print(hand.pubkey.size_in_bits(), "bits", hand.pubkey.export_key()[27:48])
    #print(hand.pubkey.size_in_bits(), "bits, Hash: ",  ddd[:24])
    #for aa in dir(hand.pubkey):
    #    print("Got ", aa, hand.pubkey.__getattribute__(aa))

    hand.client(["quit"])
    hand.close();

    sys.exit(0)

# EOF









