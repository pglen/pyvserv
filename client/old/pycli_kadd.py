#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

#sys.path.append('../common')
#import support, pycrypt, pyservsup, pyclisup, syslog
#import comline, pypacker, crysupp

# Set parent as module include path
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from common import support, pycrypt, pyservsup, pyclisup
from common import pysyslog, comline, pypacker

# ------------------------------------------------------------------------
# Globals

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
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s1.connect((ip, conf.port))
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    hand = pyclisup.CliSup(s1)
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    ret = hand.client(["ver",])
    print("ver ret", ret)

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", ret)
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    print("Session, with key:", conf.sess_key[:12], "...")

    ret =  hand.login(conf, "admin", "1234")
    if ret[0] != "OK":
        print ("Server login fail:", ret)
        raise ValueError("Not authorized")

    hand.client("kadd k2 1234")

    xkey = "1234"
    resp = hand.set_xkey("k2", "")
    print (resp)
    hand.client("ver", xkey)
    hand.client("quit", xkey)
    s1.close();

    sys.exit(0)

# EOF




