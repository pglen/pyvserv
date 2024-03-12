#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, uuid

from Crypto import Random

# This repairs the path from local run to pip run.
# Remove pip version for local tests
try:
    from pyvcommon import support

    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
    #sys.path.append(os.path.join(sf, "pyvgui"))
    #sys.path.append(os.path.join(sf, "pyvgui", "guilib"))

except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    #sys.path.append(os.path.join(base, "..", "pyvgui"))
    #sys.path.append(os.path.join(base, "..", "pyvgui", "guilib"))
    from pyvcommon import support

from pyvcommon import support, pycrypt, pyservsup, pyclisup, pyvhash
from pyvcommon import pysyslog, comline

import pyvpacker

'''
# test encrypt with large keys
rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
        "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ=="
sss = bluepy.encrypt(rrr, conf.sess_key)
ttt = bluepy.decrypt(sss, conf.sess_key)
print (rrr)
print (ttt)
'''

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level        - Debug level 0-10")
    print( "            -p port         - Port to use (default: 6666)")
    print( "            -l level        - Log level (default: 0)")
    print( "            -A  host/port   - Add host/port to replicate to")
    print( "            -D  host/port   - Delete host/port to replicate to")
    print( "            -S              - Show (list) remote replication hosts")
    print( "            -n              - Number of records to put")
    print( "            -v              - Verbose")
    print( "            -q              - Quiet")
    print( "            -h              - Help")
    #print( " Needs debug level or verbose to have any output.")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["c:",  "comm",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["s",   "showkey",  "",     None],      \
    ["n:",  "numrec",   1,     None],      \
    ["A:",  "addx",      "",    None],      \
    ["D:",  "delx",      "",    None],      \
    ["S",   "showx",     0,    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])
    #print(vars(conf))

    if conf.comm:
        print("Save to filename", conf.comm)

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug
    hand.comm  = conf.comm

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    resp3 = hand.client(["hello", "world"] , "", False)
    print("Hello Resp:", resp3)

    resp4 = hand.client(["tout", "30",], conf.sess_key)
    print("Server tout Response:", resp4)

    ret = hand.start_session(conf)

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  conf.sess_key[:12], '...' )
    print(" ----- Post session, all is encrypted ----- ")

    resp4 = hand.client(["tout", "30",], conf.sess_key)
    print("Server tout Response:", resp4)

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    print("Server hello resp:", resp4[1])

    cresp = hand.client(["user", "admin"], conf.sess_key)
    print ("Server user respo:", cresp)

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    print ("Server pass resp:", cresp)

    cresp = hand.client(["dmode",], conf.sess_key)
    #print("dmode", cresp)
    if cresp[1] == '0':
        print("Enter twofa code: (ret to skip)", end = "")
        sesscode = input()
        if sesscode:
            cresp = hand.client(["twofa", sesscode], conf.sess_key)
            print ("Server twofa resp:", cresp)
            if cresp[0] != "OK":
                print ("Server twofa failed")
                sys.exit(0)

    # Interactive, need more time
    tout = hand.client(["tout", "200",], conf.sess_key)
    #print (tout)

    if conf.showx:
        cresp = hand.client(["ihost", "list", "",], conf.sess_key)
    elif conf.addx:
        cresp = hand.client(["ihost", "add", conf.addx,], conf.sess_key)
    elif conf.delx:
        cresp = hand.client(["ihost", "del", conf.delx,], conf.sess_key)
    else:
        cresp = hand.client(["ihost", "add", "localhost:5555",], conf.sess_key)

    print ("Server ihost response:", cresp)

    cresp = hand.client(["quit",],conf.sess_key)
    print ("Server quit  response:", cresp)
    hand.close();

    sys.exit(0)

# EOF

