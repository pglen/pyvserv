#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

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
    print( "            -v        - Verbose")
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

    if sys.version_info[0] < 3:
        print("Warning! This script was meant for python 3.x")
        time.sleep(1)

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
        print ("Server initial:", resp2[1])

    resp = hand.client(["ekey"])

    #print(resp)

    rrr = resp[1].split()
    if rrr[0] == "ERR":
        print(resp[1])
    elif rrr[0] == "OK":
        resp2 = hand.getreply()
        print ("Server response2:",  "'" + resp2 +  "'")

        hh = SHA512.new(); hh.update(resp2[1].encode())
        #print("Hashes: ", "\n" + hhh, "\n" + hh.hexdigest())

        hand.pkey = resp2;

        if hhh !=  hh.hexdigest():
            if conf.quiet == False:
                print("Tainted key")
        else:
            if conf.quiet == False:
                print("Key OK")

        if conf.showkey:
            #print("Key:")
            print(hand.pkey)
    else:
        print("Invalid response:", "'" + resp[1] + "'")

    hand.client("quit")
    hand.close();

    sys.exit(0)

# EOF











