#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Upload file.

import os, sys, getopt, signal, select
import socket, time, struct, random, stat

sys.path.append('../common')
import support, pycrypt, pyservsup, pyclisup, syslog

# ------------------------------------------------------------------------
# Globals

version = 1.0

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print
    print "Usage: " + os.path.basename(sys.argv[0]) + " [options]"
    print
    print "Options:    -d level  - Debug level 0-10"
    print "            -p port   - Port to use (default: 9999)"
    print "            -v        - Verbose"
    print "            -q        - Quiet"
    print "            -h        - Help"
    print
    sys.exit(0)

def pversion():
    print os.path.basename(sys.argv[0]), "Version", version
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

conf = support.Config(optarr)


def  set_key(aa, bb, cc):
    return "key here"

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
        hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)


    # Auth Key
    xkey = set_key(hand, "k1", "")
    hand.client("user peter", xkey)
    hand.client("pass 1234", xkey)

    #sendfile(hand, "aa", "bb", xkey)

    # New key, new file
    xkey = set_key(hand, "1111", xkey)
    #sendfile(hand, "bb", "cc", xkey)

    # Back to clear text
    xkey = set_key(hand, "", xkey)
    hand.client("ver", xkey)
    hand.client("quit", xkey)

    hand.close();

    sys.exit(0)


















