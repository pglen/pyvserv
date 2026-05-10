#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat, datetime

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

import pyvpacker

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")

optarr = comline.optarrlong

#    ["f:",  "fname",    "test.txt", None],      \
#    ["n",   "plain",    0,          None],      \
#    ["r:",  "rget",     "",         None],      \
#    ["b:",  "begin",    "",        None],      \
#    ["i:",  "inter",    0,          None],      \

optarr.append ( ["f:",   "fname=",     "fname",       "test.txt",
                            None, "fname"] )
optarr.append ( ["n",   "plain",     "plain",       0,
                            None, "plain"] )
optarr.append ( ["r:",   "rget=",     "rget",    "",
                            None, "rget."] )
optarr.append ( ["b:",   "begin=",     "begin",    "",
        None, "Start / Begin time. See format below. Default:today."] )
optarr.append ( ["i:",   "inter=",     "inter",       0,
                            None, "inter."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def    mainfunct():

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

    #resp3 = hand.client(["id",] , "", False)
    #print("ID Response:", resp3[1])

    #ret = ["OK",];  conf.sess_key = ""
    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])

    #if conf.sess_key:
    #    print("Post session, session key:", conf.sess_key[:12], "...")

    resp3 = hand.client(["hello", ],  conf.sess_key, False)
    #print("Hello Response:", resp3)

    cresp = hand.login("admin", "1234", conf)
    #print ("Server login response:", cresp)

    dd_beg, dd_end = pyclisup.inter_date(conf.begin, conf.inter)
    print("date from:", dd_beg, "to:", dd_end);

    packer = pyvpacker.packbin()

    if conf.rget:
        rgetarr = conf.rget.split()
        #print("rgetarr:", rgetarr)
        cresp = hand.client(["rget", "vote", rgetarr], conf.sess_key)
        if cresp[0] == "OK":
            #print("rget resp:", cresp)
            for aa in cresp[3]:
                #pyclisup.show_onerec(hand, aa, conf)

                dec = packer.decode_data(aa[1])[0]
                if conf.verbose:
                    print("dec:", dec)
                else:
                    print("pay:", dec['PayLoad'])
    else:
        cresp = hand.client(["rlist", "vote", dd_beg.timestamp(),
                         dd_end.timestamp()], conf.sess_key)
        #print ("Server  rlist response:", cresp)
        if cresp[0] != "OK":
            print("Cannot get rlist", cresp)
            cresp = hand.client(["quit", ], conf.sess_key)
            sys.exit(0)
        #print("rlist got", len(cresp[1]), "records")
        for aaa in cresp[1]:
            cresp2 = hand.client(["rget", "vote", [aaa]], conf.sess_key)
            if cresp2[0] != "OK":
                print("Cannot get record", cresp2)
                continue
            #print("cresp2:", cresp2)
            for aa in cresp2[3]:
                #pyclisup.show_onerec(hand, aa, conf)
                dec = packer.decode_data(aa[1])[0]
                if conf.verbose:
                    print("dec:", dec)
                else:
                    print("pay:", dec['PayLoad'])

        print("Listed", len(cresp[1]), "records.")

    cresp = hand.client(["quit", ], conf.sess_key)
    #print ("Server quit response:", cresp)

if __name__ == '__main__':
    mainfunct()

# EOF
