#!/usr/bin/env python3

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

sys.path.append('..')
sys.path.append('../bluepy')

sys.path.append('..')
from common import support, pycrypt, pyservsup, pyclisup, syslog

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
    
conf = pyclisup.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    if  sys.version_info[0] < 3:
        print(("Needs python 3 or better."))
        sys.exit(1)

    args = conf.comline(sys.argv[1:])

    if len(args) == 0:
        ip = '127.0.0.1' 
    else:
        ip = args[0]
    
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s1.connect((ip, conf.port))
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    hand = pyclisup.CliSup(s1)
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug
    
    hand.client("ver")

    hand.client("user peter")
    resp = hand.client("pass 1234")
    if resp.split()[0] != "OK":
        raise ValueError("Not authorized")

    #xkey = hand.set_key("1234", "")
    xkey = ""
    
    hand.client("uadd peter2  1234", xkey)
    hand.client("uadd peter2  1234", xkey)
    hand.client("uadd peter4  1234", xkey)
    hand.client("uadd peter5  1234", xkey)
    
    #hand.client("udel peter 1234", xkey)
    hand.client("udel peter2 1234", xkey)
    hand.client("udel peter3 1234", xkey)
    
    hand.client("quit", xkey)
    
    s1.close();
    
    sys.exit(0)



















