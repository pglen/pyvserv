#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project.

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
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] [hostname]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 6666)")
    print( "            -t flag   - Throttle on / off")
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
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
    ["t:",   "throt",   "",         None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

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

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    if conf.verbose:
        print("Hello Resp:", resp4)

    cresp = hand.client(["user", "admin"], conf.sess_key)
    #if not conf.quiet:
    #    print ("Server user response:", cresp[1])

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    if not conf.quiet:
        print ("Server pass response:", cresp)

    if not conf.throt:
        cresp = hand.client(["throt", ], conf.sess_key)
    else:
        cresp = hand.client(["throt", conf.throt,], conf.sess_key)

    print ("Server throt response:", cresp)

    if cresp[0] != "OK":
        #print("Err: ", cresp)
        cresp = hand.client(["quit", ], conf.sess_key)
        #print ("Server quit response:", cresp)
        sys.exit(0)

    cresp = hand.client(["quit", ], conf.sess_key)
    #print ("Server quit response:", cresp)

    sys.exit(0)

# EOF
