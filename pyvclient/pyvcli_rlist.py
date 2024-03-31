#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat, datetime, uuid, atexit

from pyvcli_utils import *

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

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
    print( "            -s        - Start time. Format: 'Y-m-d H:M'")
    print( "            -i        - Interval in minutes. (Default: 1 day)")
    print( "            -n        - No encryption (plain)")
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
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["n",   "plain",    0,          None],      \
    ["t",   "test",     "x",        None],      \
    ["i:",  "inter",    0,          None],      \
    ["s:",  "start",    "",         None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

    #print(dir(conf))

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

    atexit.register(atexit_func, hand, conf)

    #resp3 = hand.client(["id",] , "", False)
    #print("ID Response:", resp3[1])

    #ret = ["OK",];  conf.sess_key = ""
    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])

    if conf.sess_key:
        print("Post session, session key:", conf.sess_key[:12], "...")

    resp3 = hand.client(["hello", ],  conf.sess_key, False)
    print("Hello Response:", resp3)

    cresp = hand.login("admin", "1234", conf)
    print ("Server login response:", cresp)

    # Set date range
    if conf.start:
        dd = datetime.datetime.now()
        dd = dd.strptime(conf.start, "%Y-%m-%d %H:%M")
    else:
        dd = datetime.datetime.now()
        dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)

    #print(dd)
    dd_beg = dd + datetime.timedelta(0)
    if conf.inter:
        dd_end = dd_beg + datetime.timedelta(0, conf.inter * 60)
    else:
        dd_end = dd_beg + datetime.timedelta(1)

    print("from:", dd_beg, "to:", dd_end);
    cresp = hand.client(["rcount", "vote", dd_beg.timestamp(),
                                    dd_end.timestamp()], conf.sess_key)
    print ("Server  rcount response:", cresp)

    if cresp[1] < 100:
        cresp = hand.client(["rlist", "vote", dd_beg.timestamp(),
                                    dd_end.timestamp()], conf.sess_key)
        #print ("Server  rlist response:", cresp)
        if cresp[0] == "OK":
            for aa in cresp[1]:
                #print("aa", aa)
                if aa:
                    ttt = pyservsup.uuid2date(uuid.UUID(aa))
                    print(aa, ":", ttt)

# EOF
