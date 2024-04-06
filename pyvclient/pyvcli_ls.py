#!/usr/bin/env python3

from __future__ import print_function

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, datetime

from Crypto import Random

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
    print( "            -l level  - Log level (default: 0)")
    print( "            -c file   - Save comm to file")
    print( "            -s        - Showkey")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
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
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

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

    resp3 = hand.client(["hello",] , conf.sess_key, False)
    if not conf.quiet:
        print("Hello Response:", resp3)

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3)
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Session Key ACCEPTED:",  ret, )
    if not conf.quiet:
        print("Session, with key:", conf.sess_key[:12], "...")

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    if not conf.quiet:
        print("Sess Response:", resp4)

    ret =  hand.login("admin", "1234", conf)
    if ret[0] != "OK":
        print ("Server login fail:", ret)
        hand.client(["quit"], conf.sess_key)
        hand.close();
        sys.exit(0)

    cresp = hand.client(["buff", "10000000",], conf.sess_key)
    print ("Server buff response:", cresp)
    if cresp[0] != "OK":
        print("Error on buff command", cresp[1])
        hand.client(["quit"], conf.sess_key)
        hand.close();
        sys.exit(0)

    cresp = hand.client(["ls", ], conf.sess_key)
    print ("Server  ls response:", cresp)
    if cresp[0] != "OK":
        print("Error on listing directory:", cresp[1])
        hand.client(["quit"], conf.sess_key)
        hand.close();
        sys.exit(0)

    ''' Stat return values are as in python os.stat() + OK and name prefix
    "OK", fname (1),
    st_mode (2), st_ino, st_dev, st_nlink
    st_uid, st_gid, st_size (8)
    st_atime (9), st_mtime, st_ctime
    st_atime_ns
    st_mtime_ns
    st_ctime_ns '''

    print ("Server stat response:")
    for aa in cresp[1:]:
        bb = support.unescape(aa)
        cresp2 = hand.client(["stat", aa], conf.sess_key)
        #print("cresp2", cresp2)
        if cresp2[0] != "OK":
            print("Bad entry from remote", cresp2)
        else:
            ddd = datetime.datetime.fromtimestamp(int(cresp2[10]))
            print ("%s %-24s %-8d %s" %
                (
                support.mode2str(int(cresp2[2])), support.unescape(cresp2[1]),
                        int(cresp2[8]), ddd)
                )
            #int(cresp2[9]), int(cresp2[10]), int(cresp2[11])
            #print(ddd)

    hand.client(["quit",],conf.sess_key)
    hand.close();

    sys.exit(0)

# EOF

