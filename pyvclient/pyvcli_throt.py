#!/usr/bin/env python

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

#optarr = \
#    ["t:",   "throt",   "",         None],      \
#
#conf = comline.Config(optarr)

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong
optarr.append ( ["t:",   "throt=",     "throt",       "",
                            None, "Throttle on or off."] )
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

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    if conf.verbose:
        print("Hello Resp:", resp4)

    cresp = hand.client(["user", "admin"], conf.sess_key)
    #if not conf.quiet:
    #    print ("Server user response:", cresp[1])

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    #if not conf.quiet:
    #    print ("Server pass response:", cresp)

    if not conf.throt:
        cresp = hand.client(["throt", ], conf.sess_key)
    else:
        print("arg", conf.throt)
        cresp = hand.client(["throt", conf.throt,], conf.sess_key)

    print ("Server throt response:", cresp)

    if cresp[0] != "OK":
        #print("Err: ", cresp)
        cresp = hand.client(["quit", ], conf.sess_key)
        #print ("Server quit response:", cresp)
        sys.exit(0)

    cresp = hand.client(["quit", ], conf.sess_key)
    #print ("Server quit response:", cresp)

    sys.exit(0)

# EOF
