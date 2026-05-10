#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

#    ["c:",  "fname",    "test_dir", None],    \

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong
optarr.append ( ["c:",   "fname=",     "fname",       "test_dir",
                            None, "Directory to remove."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

    opts, args = conf.comline(sys.argv[1:])

    #print(dir(conf))

    #if conf.comm:
    #    print("Save to filename", conf.comm)

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

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    if not conf.quiet:
        print("Session key:", conf.sess_key[:12], "...")

    #resp3 = hand.client(["hello", ],  conf.sess_key, False)
    #if not conf.quiet:
    #    print("Hello Response:", resp3)

    cresp = hand.login("admin", "1234", conf)
    if not conf.quiet:
        print ("Server login response:", cresp)
    if cresp[0] != "OK":
        print("Error on login, exiting.", cresp)
        sys.exit(0)

    #cresp = hand.client(["buff", "10", ], conf.sess_key)
    #print ("Server buff response:", cresp)
    #if cresp[0] != "OK":
    #    print("Error on buff command", cresp[1])
    #    hand.client(["quit"], conf.sess_key)
    #    hand.close();
    #    sys.exit(0)

    ret2 = hand.client(["rmdir", conf.fname], conf.sess_key)
    print ("Server rmdir response:", ret2)

    cresp = hand.client(["quit", ], conf.sess_key)
    #print ("Server quit response:", cresp)

    sys.exit(0)

# EOF
