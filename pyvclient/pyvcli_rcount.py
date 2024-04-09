#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat, datetime, uuid, atexit

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

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

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
    print( "            -b        - Start / Begin time. See format below. Default:today")
    print( "            -i        - Interval in minutes. (Default: 1 day)")
    print( "            -h        - Help")
    print()
    print("  Possible date Formats: 'Y-m-d+H:M' 'Y-m-d' 'm-d' 'm-d+H-M'")
    print()
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
    ["b:",  "begin",    "",         None],      \
    ["i:",  "inter",    0,          None],      \
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

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    atexit.register(pyclisup.atexit_func, hand, conf)

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    cresp = hand.login("admin", "1234", conf)
    #if not conf.quiet:
    #    print ("Server login response:", cresp)
    if cresp[0] != pyclisup.OK:
        print("Error on login", cresp)
        sys.exit(1)

    dd_beg, dd_end = pyclisup.inter_date(conf.begin, conf.inter)

    cresp = hand.client(["rsize", "vote"], conf.sess_key)
    if not conf.quiet:
        print ("Server rsize response:", cresp)

    if not conf.quiet:
        print("Records from:", dd_beg, "to:", dd_end);

    cresp = hand.client(["rcount", "vote", dd_beg.timestamp(),
                                    dd_end.timestamp()], conf.sess_key)
    print ("Server  rcount response:", cresp)
    if cresp[0] != "OK":
        sys.exit()


if __name__ == '__main__':
    mainfunct()

# EOF
