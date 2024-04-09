#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

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
# Functions from command line

def phelp():

    print( "The pyvserv help program.")
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] [hostname]")
    print( "  hostname: host to connect to. (default: 127.0.0.1)")
    print( "  options:  -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
    print( "            -s str    - Subhelp string")
    print( "            -v        - Verbose")
    print( "            -V        - Print version number")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["t",   "test",     "x",        None],      \
    ["s:",  "subhelp",  "",         None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunct():

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

    if conf.subhelp:
        if conf.verbose:
            print("subhelp", conf.subhelp);

    try:
        resp2 = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    if conf.verbose:
        print ("Server initial:", hand.pb.decode_data(resp2[1])[0])

    if conf.subhelp:
        resp = hand.client(["help", conf.subhelp])
    else:
        resp = hand.client(["help",])

    print ("help resp:", resp)

    hand.client(["quit",])
    hand.close();

    sys.exit(0)

#def mainfunct():

if __name__ == '__main__':
    mainfunct()

# EOF
