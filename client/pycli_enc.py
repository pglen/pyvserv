#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

# Set parent as module include path
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from common import support, pycrypt, pyservsup, pyclisup
from common import pysyslog, comline, pypacker

#sys.path.append('../common')
#import support, pycrypt, pyservsup, pyclisup, syslog

# ------------------------------------------------------------------------
# Globals

version = 1.0

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
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
    ["p:",  "port",     6666,   None],      \
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

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    #s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #init_handler(s1)
    #try:
    #    s1.connect((ip, conf.port))
    #except:
    #    print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
    #    sys.exit(1)

    try:
        resp2 = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    #print ("Server initial:", resp2)

    resp = hand.client(["ver"])

    resp = hand.client(["ver"])
    print(resp)

    resp = hand.client(["user", "peter"])
    print(resp)

    resp = hand.client(["pass", "1234"])
    print(resp)

    #xkey = set_key( "1234", "")
    #
    #hand.client([ "tout 14", xkey)
    #hand.client([ "ver ", xkey)
    #hand.client([ "help ", xkey)
    #
    #hand.client(["ekey ", xkey)
    #xkey = ""
    #hand.client(["ver ", xkey)
    #hand.client([ "quit", xkey)
    #hand.close();

    sys.exit(0)




















