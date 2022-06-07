#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

#sys.path.append('..')
#sys.path.append('../bluepy')
sys.path.append('../common')
import support, pycrypt, pyservsup, pyclisup, syslog, comline

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
conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

    '''if  sys.version_info[0] < 3:
        print(("Needs python 3 or better."))
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
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    resp3 = hand.client(["hello",] , "", False)
    print("Hello Response:", resp3[1])

    resp3 = pyclisup.start_session(hand, conf)
    print("Sess Response:", resp3[1])

    resp3 = hand.client(["hello",] , conf.sess_key, False)
    print("Hello Response:", resp3[1])

    resp = hand.client(["user", "peter"], conf.sess_key)
    print("user Response:", resp[1])
    if resp[1].split()[0] != "OK":
        raise ValueError("No user", resp[1])

    resp = hand.client(["pass", "1234"], conf.sess_key)
    print("pass Response:", resp[1])
    if resp[1].split()[0] != "OK":
        raise ValueError("Not authorized", resp[1])

    resp = hand.client(["udel", "peter2", "1234"], conf.sess_key)
    print("udel Response:", resp[1])
    if resp[1].split()[0] != "OK":
        raise ValueError("udel peter2 error", resp[1])

    resp = hand.client(["udel", "peter3,comma", "1234"], conf.sess_key)
    print("udel Response:", resp[1])
    if resp[1].split()[0] != "OK":
        raise ValueError("udel user error", resp[1])

    resp = hand.client(["udel", "peter4 space", "1234"], conf.sess_key)
    print("udel Response:", resp[1])
    if resp[1].split()[0] != "OK":
        raise ValueError("udel user error", resp[1])

    #resp = hand.client(["udel", "peter", "1234"], conf.sess_key)
    #print("udel Response:", resp[1])
    #if resp[1].split()[0] != "OK":
    #    raise ValueError("udel user error", resp[1])

    hand.client(["quit"], conf.sess_key)

    hand.close();

    sys.exit(0)





















