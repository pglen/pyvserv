#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Initial user add.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

sys.path.append('../common')
import support, pycrypt, pyservsup, pyclisup, syslog
import comline, pypacker, crysupp

# ------------------------------------------------------------------------
# Globals

version = 1.0

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
    ["p:",  "port",     9999,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    '''if  sys.version_info[0] < 3:
        print("Needs python 3 or better.")
        sys.exit(1)'''

    args = conf.comline(sys.argv[1:])

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    try:
        hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    ret = hand.client(["ver",])
    print(ret)
    ret = hand.start_session(conf)
    print (ret)

    if ret[0] != "OK":
        print("Error on setting session:", resp3)
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Session Key ACCEPTED:",  ret, )
    print("Session, with key:", conf.sess_key[:12], "...")

    #ret = hand.client(["ver",])
    #print(ret)

    #ret = hand.client(["uini",]) # "peter", "1234"])
    #print (ret)

    hand.client(["quit",])
    hand.close();

    sys.exit(0)

# EOF























