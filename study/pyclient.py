#!/usr/bin/env python3

# ------------------------------------------------------------------------
# Test client for the pyserv project

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

import  pyserv.pydata  #, pyserv.pyservsup, bluepy.bluepy
import  pyserv.pyclisup 

# ------------------------------------------------------------------------
# Globals 

pgdebug = 0
verbose = 0
port    = 9999
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

# ------------------------------------------------------------------------
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
    
conf = pyserv.pyclisup.Config(optarr)

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])
    
    pyserv.pyclisup.verbose = conf.verbose
    pyserv.pyclisup.pgdebug = conf.pgdebug
    
    if len(args) == 0:                                  
        ip = '127.0.0.1' 
    else:
        ip = args[0]
    
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pyserv.pyclisup.init_handler(s1)

    try:
        s1.connect((ip, port))
    except:
        print( "Cannot connect to:", ip + ":" + str(port), sys.exc_info()[1])
        sys.exit(1)
        
    xkey = "1234"
    pyserv.pyclisup.set_xkey(s1, "k2", "")
    client(s1, "ver", xkey)
    client(s1, "user peter", xkey)
    
    resp = client(s1, "pass 1234", xkey)
    if resp.split(" ")[0] != "OK":
        print( "Cannot authenticate: ", resp)
        sys.exit(2)

    resp = client(s1, "lsd", xkey)
    got = resp.split()
    if got[0] == "OK":
        for aa in got[1:]:
            client(s1, "cd " + aa, xkey)
            resp = client(s1, "pwd", xkey)
            print( resp.split()[1] + ":",)
            resp = client(s1, "ls", xkey)
            got2 = resp.split()
            if got2[0] == "OK":
                for bb in got2[1:]:
                    print( bb,)
            client(s1, "cd ..", xkey)
            print( )
        client(s1, "pwd", xkey)
    
    client(s1, "quit", xkey)
    s1.close();
    
    sys.exit(0)

