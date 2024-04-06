#!/usr/bin/env python3

from __future__ import print_function

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

def errexit(hand, retstr, msg = "exiting"):
    print(msg, retstr)
    hand.client(["quit"], conf.sess_key);  hand.close();
    sys.exit(0)

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level    - Debug level 0-10")
    print( "            -p port     - Port to use (default: 666)")
    print( "            -l level    - Log level (default: 0)")
    print( "            -c file     - Save comm to file")
    print( "            -f dirname  - Change to directory")
    print( "            -s          - Showkey")
    print( "            -v          - Verbose")
    print( "            -q          - Quiet")
    print( "            -h          - Help")
    #print( " Needs debug level or verbose to have any output.")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
    ["f:",  "fname",    "test_1",   None],      \
    ["c:",  "comm",     "",         None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["s",   "showkey",  "",         None],      \
    ["t",   "test",     "x",        None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

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

    resp3 = hand.client(["hello",] , "", False)
    print("Hello Response:", resp3[1])

    ret = hand.start_session(conf)

    #if ret[0] == "OK":
    #    print("Sess Key ACCEPTED:",  ret[1])

    if ret[0] != "OK":
        errexit(hand, ret[1], "Error on setting session")

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])
    print("Post session, all is encrypted")

    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("Hello Response:", resp4[1])

    cresp = hand.client(["user", "admin"], conf.sess_key)
    print ("Server user response:", cresp)

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    print ("Server pass response:", cresp)

    #///////////////////////////////////////////////////////////////////////

    #cresp = hand.client(["cd", "aa"], conf.sess_key)
    #print ("Server cd response:", cresp[1])

    cresp = hand.client(["pwd",], conf.sess_key)
    print ("Server pwd response:", cresp)

    cresp = hand.client(["lsd",], conf.sess_key)
    if cresp[0] != "OK":
        errexit(hand, "Error on lsd command", cresp)
    print ("Server lsd response:", cresp)

    cresp = hand.client(["cd", "test_1"], conf.sess_key)
    print ("Server cd response:", cresp)

    cresp = hand.client(["pwd",], conf.sess_key)
    print ("Server pwd response:", cresp)

    #cresp = hand.client(["cd", "keys"], conf.sess_key)
    #print ("Server cd response:", cresp[1])

    #cresp = hand.client(["ls",], conf.sess_key)
    #if cresp[0] != "OK":
    #    errexit(hand, "Error on ls command", cresp)
    #print ("Server ls after cd response:", cresp)

    ''' Stat return values are as in python os.stat() + OK and name prefix
    "OK", fname,
    st_mode, st_ino, st_dev, st_nlink
    st_uid, st_gid, st_size
    st_atime, st_mtime, st_ctime
    st_atime_ns
    st_mtime_ns
    st_ctime_ns '''

    #print ("Server stat response:")
    #hand.listfiles(hand, cresp[1:], conf.sess_key)

    cresp = hand.client(["cd", "../test_2"], conf.sess_key)
    print ("Server cd  response:", cresp)

    cresp = hand.client(["pwd",], conf.sess_key)
    print ("Server pwd response:", cresp)

    #cresp = hand.client(["ls",], conf.sess_key)
    #print ("Server ls response:", cresp)

    cresp = hand.client(["cd", "/"], conf.sess_key)
    print ("Server cd response:", cresp)

    cresp = hand.client(["pwd",], conf.sess_key)
    print ("Server pwd response:", cresp)

    #cresp = hand.client(["ls",], conf.sess_key)
    #if cresp[0] != "OK":
    #    errexit(hand, "Error on ls command", cresp[1])
    #
    #print ("Server ls after cd / response:")
    #print (cresp)

    hand.client(["quit",],conf.sess_key)
    hand.close();

    sys.exit(0)

# EOF