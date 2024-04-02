#!/usr/bin/env python

import sys, os
import readline

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

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

version = 1.0

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 6666)")
    print( "            -f file   - Upload new QR image file")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -n        - No encryption (plain)")
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
    ["f:",  "file",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["n",   "plain",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunct():

    args = conf.comline(sys.argv[1:])

    #print(vars(conf))
    #if conf.comm:
    #    print("Save to filename", conf.comm)

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

    conf.sess_key = ""
    #ret = ["OK",];  conf.sess_key = ""
    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        sys.exit(0)

    if conf.file:
        fp = open(conf.file, "rb")
        buff = fp.read()
        fp.close()
        #print("len:", len(buff))
        resp3 = hand.client(["qr", buff], conf.sess_key, False)
        print("QR UP Response:", resp3)
    else:
        resp3 = hand.client(["qr",], conf.sess_key, False)
        #print("QR Response:", resp3)
        fp = open("qr.png", 'wb')
        if type(resp3[1]) != type(b""):
            resp3[1] = resp3[1].encode()
        fp.write(resp3[1])
        fp.close()

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
