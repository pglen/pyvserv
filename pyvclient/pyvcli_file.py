#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

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
# Globals

version = "1.0.0"

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 6666)")
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

    ret = hand.start_session(conf)

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    if not conf.quiet:
        print("Hello (plain) Resp:", resp4)

    cresp = hand.client(["user", "admin"], conf.sess_key)
    if not conf.quiet:
        print ("Server user response:", cresp[1])

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    if not conf.quiet:
        print ("Server pass response:", cresp[1])

    cresp = hand.client(["ls", ], conf.sess_key)
    if not conf.quiet:
        print ("Server ls response:", cresp)

    cresp = hand.client(["file", "test.txt"], conf.sess_key)
    print ("Server file response:", cresp)
    if cresp[0] != "OK":
        cresp = hand.client(["quit", ], conf.sess_key)
        #print ("Server quit response:", cresp)
        sys.exit(0)

    fp = open("test.txt_local", "rb")
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

# EOF
