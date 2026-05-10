#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat, datetime, uuid, atexit

# This repairs the path from local run to pip run.
try:
    from pyvcommon import support
    base = os.path.dirname(os.path.realpath(support.__file__))
    sys.path.append(os.path.join(base, "."))
except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    from pyvcommon import support

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

#    ["t",   "test",     "x",        None],      \
#    ["b:",  "begin",    "",         None],      \
#    ["i:",  "inter",    0,          None],      \

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")

optarr = comline.optarrlong
optarr.append ( ["t",   "test",     "test",       0,
                            None, "test"] )
optarr.append ( ["b:",   "begin=",     "begin",    "",
                            None, "begin."] )
optarr.append ( ["i:",   "inter=",     "inter",       0,
                            None, "inter."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def mainfunct():

    opts, args = conf.comline(sys.argv[1:])

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

    atexit.register(pyclisup.atexit_func, hand, conf)

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    cresp = hand.login("admin", "1234", conf)
    #if not conf.quiet:
    #    print ("Server login response:", cresp)
    if cresp[0] != pyclisup.OK:
        print("Error on login", cresp)
        sys.exit(0)

    dd_beg, dd_end = pyclisup.inter_date(conf.begin, conf.inter)

    cresp = hand.client(["rsize", "vote"], conf.sess_key)
    if not conf.quiet:
        print ("Server rsize response:", cresp)

    if not conf.quiet:
        print("Records from:", dd_beg, "to:", dd_end);

    cresp = hand.client(["rcount", "vote", dd_beg.timestamp(),
                                    dd_end.timestamp()], conf.sess_key)
    print ("Server  rcount response:", cresp)
    if cresp[0] != "OK":
        sys.exit()


if __name__ == '__main__':
    mainfunct()

# EOF
