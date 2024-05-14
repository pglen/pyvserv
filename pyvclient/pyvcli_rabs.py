#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat, datetime

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
    print( "            -l login  - Login Name; default: 'admin'")
    print( "            -s lpass  - Login Pass; default: '1234' (for !!testing only!!)")
    print( "            -t        - prompt for login pass")
    print( "            -a recpos - Absolute positions. Negative for end offsets.")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    print("  Use quotes for multiple arguments. (like: -a \"-1 -2 -3\") -- lists last 3")
    print()

    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
    ["l:",  "login",    "admin",    None],      \
    ["s:",  "lpass",    "1234",     None],      \
    ["t",   "lprompt",  0,          None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["a:",  "rabs",     "",         None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def    mainfunct():

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

    if conf.lprompt:
        import getpass
        strx = getpass.getpass("Pass for login %s: " % conf.login)
        if not strx:
            print("Cannot login with empty pass, aborting ...")
            sys.exit(0)
        conf.lpass = strx

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    #ret = ["OK",];  conf.sess_key = ""
    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    #resp3 = hand.client(["hello", ],  conf.sess_key, False)
    #print("Hello Response:", resp3)

    cresp = hand.login(conf.login, conf.lpass, conf)
    #print ("Server login response:", cresp)
    if cresp[0] != "OK":
        print("Error on logging in:", cresp)
        hand.client(["quit"], conf.sess_key)
        hand.close();
        sys.exit(0)

    if conf.rabs:
        arrx = conf.rabs.split()
        #print("getting", arrx)
        cresp2 = hand.client(["rabs", "vote", *arrx], conf.sess_key)
        #print("rabs got:", cresp2)
        if cresp2[0] != "OK":
            print("Cannot get rabs:", cresp2)
            cresp = hand.client(["quit", ], conf.sess_key)
            sys.exit()
        for aa in cresp2[3]:
            print("aa", aa)
            #pyclisup.show_onerec(hand, aa, conf)
    else:
        # Get last record
        cresp = hand.client(["rsize", "vote"], conf.sess_key)
        if not conf.quiet:
            print ("Server rsize response:", cresp)
        # Offset is one less than count
        cresp2 = hand.client(["rabs", "vote", cresp[1] - 1], conf.sess_key)
        #print ("Server rabs response:", cresp2)
        for aa in cresp2[3]:
            #pyclisup.show_onerec(hand, aa, conf)
            #print(aa)
            dec = hand.pb.decode_data(aa[1])[0]
            print("Last Record:")
            if conf.verbose:
                print("dec:", dec)
            else:
                print("pay:", dec['PayLoad'])

    cresp = hand.client(["quit", ], conf.sess_key)
    #print ("Server quit response:", cresp)

if __name__ == '__main__':
    mainfunct()

# EOF
