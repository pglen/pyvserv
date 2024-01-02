#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

# Set parent as module include path
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from common import support, pycrypt, pyservsup, pyclisup
from common import pysyslog, comline, pypacker

# ------------------------------------------------------------------------
# Globals

version = 1.0

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 9999)")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
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
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    if conf.verbose:
        resp3 = hand.client(["hello",] , "", False)
        print("Hello Response:", resp3[1])

    #conf.sess_key = ""    #ret = ["OK",]
    ret = hand.start_session(conf)

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])
    #print("Post session, all is encrypted")

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    if conf.verbose:
        print("Hello (plain) Response:", resp4)
        #print("Hello (encrypted) Response:", resp4[1])

    cresp = hand.client(["user", "admin"], conf.sess_key)
    #print ("Server user response:", cresp[1])

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    #print ("Server pass response:", cresp[1])

    if conf.verbose:
        cresp = hand.client(["ls", ], conf.sess_key)
        print ("Server  ls response:", cresp)

    cresp = hand.client(["file", "zeros"], conf.sess_key)
    print ("Server file response:", cresp)
    if cresp[0] != "OK":
        #print("Err: ", cresp)
        cresp = hand.client(["quit", ], conf.sess_key)
        print ("Server quit response:", cresp)
        sys.exit(0)

    fp = open("zeros_local", "rb")
    offs = 0
    while 1:
        buf = fp.read(1024)
        #print("sending", buf)
        cresp = hand.client(["data", offs, buf], conf.sess_key)
        if conf.verbose:
            print ("Server data response:", cresp)
        if cresp[0] != "OK":
            print("Cannot send", cresp)
            break
        blen = len(buf)
        if blen == 0:
            break

        offs += blen

    cresp = hand.client(["quit", ], conf.sess_key)
    print ("Server quit response:", cresp)

    sys.exit(0)







