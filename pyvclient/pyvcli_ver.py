#!/usr/bin/env python3

from __future__ import print_function

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

version = "1,0"

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

    if sys.version_info[0] < 3:
        print("Warning! This script was meant for python 3.x")
        time.sleep(1)

    #if  sys.version_info[0] < 3:
    #    print("Needs python 3 or better.")
    #    sys.exit(1)
    #
    args = conf.comline(sys.argv[1:])

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    try:
        resp2 = hand.connect(ip, conf.port)
    except:
        support.put_exception("On connect")
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    #if conf.quiet == False:
    #    print ("Server initial:", resp2)

    resp = hand.client(["ver"])

    if conf.quiet == False:
        print ("Server response:", resp)

    hand.client(["quit"])
    hand.close()

    sys.exit(0)

# EOF












