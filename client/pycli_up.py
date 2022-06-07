#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base, '../bluepy'))
sys.path.append(os.path.join(base, '../common'))
sys.path.append(os.path.join(base,  '../../pycommon'))

import support, pycrypt, pyservsup, pyclisup, syslog
import comline, pypacker, crysupp
import bluepy

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

    args = conf.comline(sys.argv[1:])

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
    #hand.comm  = conf.comm

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    resp3 = hand.client(["hello",] , "", False)
    print("Hello Response:", resp3[1])

    ret = pyclisup.start_session(hand, conf)

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])
    print("Post session, all is encrypted")

    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("Hello Response:", resp4[1])

    cresp = hand.client(["user", "admin"], conf.sess_key)
    #print ("Server user response:", cresp[1])

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    #print ("Server pass response:", cresp[1])

    cresp = hand.client(["ls", ], conf.sess_key)
    print ("Server  ls response:", cresp)

    #hand.getfile("ref", "ref_local", conf.sess_key)

    cresp = hand.client(["quit", ], conf.sess_key)
    print ("Server quit response:", cresp)


    sys.exit(0)







