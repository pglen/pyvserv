#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Upload file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

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
    print( "            -f fname  - Send file")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["f:",  "fname",    "test.txt", None],      \
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
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

    resp3 = hand.client(["hello",] , "", False)
    if not conf.quiet:
        print("Hello Response:", resp3[1])

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    if not conf.quiet:
        print("Hello resp:", resp4)

    cresp = hand.client(["user", "admin"], conf.sess_key)
    if not conf.quiet:
        print ("Server user response:", cresp[1])

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    if not conf.quiet:
        print ("Server pass response:", cresp[1])

    if not conf.quiet:
        print("Started file ...", conf.fname)

    ttt = time.time()
    resp = hand.putfile(conf.fname, "", conf.sess_key)
    filesize = support.fsize(conf.fname)/1024
    #print("filesize", filesize)
    if resp[0] != "OK":
        print ("fput resp:", resp)
        cresp = hand.client(["quit", ], conf.sess_key)
        print ("Server quit response:", cresp)
        sys.exit()

    if conf.verbose:
        rate = filesize / (time.time() - ttt)
        print ("fput resp:", resp, " %.2f kbytes/sec" % rate)

    print("fput response:", resp)

    #cresp = hand.client(["ls", ], conf.sess_key)
    #print ("Server  ls response:", cresp)

    cresp = hand.client(["quit", ], conf.sess_key)
    #print ("Server quit response:", cresp)

    sys.exit(0)

# EOF