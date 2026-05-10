#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

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

from pyvcommon import support, pycrypt, pyclisup
from pyvcommon import pysyslog, comline

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")

optarr = comline.optarrlong
optarr.append ( ["f:",   "fname=",     "fname",       "test.txt",
                            None, "Recive file name. (test.txt)"] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

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

    if conf.verbose:
        resp3 = hand.client(["hello",] , "", False)
        print("Hello Response:", resp3[1])

    ret = hand.start_session(conf)

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    if not conf.quiet:
        print("Hello (plain) Resp:", resp4)

    cresp = hand.client(["user", "admin"], conf.sess_key)
    if not conf.quiet:
        print ("Server user response:", cresp[1])

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    if not conf.quiet:
        print ("Server pass response:", cresp[1])

    if cresp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        #raise ValueError("Not authorized", resp[1])
        print("Not authorized.")
        sys.exit(0)

    #cresp = hand.client(["ls", ], conf.sess_key)
    #if not conf.quiet:
    #    print ("Server ls response:", cresp)

    cresp = hand.client(["file", conf.fname], conf.sess_key)
    print ("Server file response:", cresp)
    #if cresp[0] != "OK":
    #    cresp = hand.client(["quit", ], conf.sess_key)
    #    #print ("Server quit response:", cresp)
    #    sys.exit(0)

    ret2 = hand.getfile(conf.fname, conf.fname + "_local", conf.sess_key)
    print ("Server getfile response:", ret2)

    fp = open(conf.fname + "_local", "rb")
    offs = 0
    while 1:
        buf = fp.read(1024)
        #print("sending", buf)
        cresp = hand.client(["data", offs, buf], conf.sess_key)
        if conf.verbose:
            print ("Server data response:", cresp)
        if cresp[0] != "OK":
            print("Cannot send", cresp)
            break
        blen = len(buf)
        if blen == 0:
            break

        offs += blen

    cresp = hand.client(["quit", ], conf.sess_key)
    print ("Server quit response:", cresp)

    sys.exit(0)

# EOF
