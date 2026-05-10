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

#    ["f:",  "fname",    "test_1",   None],      \
#    ["c:",  "comm",     "",         None],      \
#    ["s",   "showkey",  "",         None],      \
#    ["t",   "test",     "x",        None],      \

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong
optarr.append ( ["f:",   "fname=",     "fname",       "test_1",
                            None, "fname."] )
optarr.append ( ["c:",   "comm=",     "comm",       "",
                            None, "Pass t use."] )
optarr.append ( ["s:",   "showkey=",     "showkey",    "",
                            None, "showkey."] )
optarr.append ( ["t:",   "test=",     "test",       "",
                            None, "test."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

    opts, args = conf.comline(sys.argv[1:])

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
    #print("Post session, all is encrypted")

    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("Hello Response:", resp4[1])

    cresp = hand.client(["user", "admin"], conf.sess_key)
    #print ("Server user response:", cresp)

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    #print ("Server pass response:", cresp)

    if cresp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        #raise ValueError("Not authorized", resp[1])
        print("Not authorized.")
        sys.exit(0)

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