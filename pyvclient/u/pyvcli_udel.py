#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

#    ["t",   "test",     "x",    None],      \

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong

optarr.append ( ["u:",   "user=",     "user",       "",
                            None, "Delete this user."] )

conf = comline.ConfigLong(optarr)

conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

    '''if  sys.version_info[0] < 3:
        print(("Needs python 3 or better."))
        sys.exit(1)'''

    opts, args = conf.comline(sys.argv[1:])

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

    resp3 = hand.start_session(conf)
    #print("Sess Response:", resp3)

    resp = hand.client(["user", "admin"], conf.sess_key)
    #print("user Response:", resp)
    if resp[0] != "OK":
        raise ValueError("No user", resp[1])

    resp = hand.client(["pass", "1234"], conf.sess_key)
    #print("pass Response:", resp)
    #if resp[0] != "OK":
    #    raise ValueError("Not authorized", resp[1])
    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        #raise ValueError("Not authorized", resp[1])
        print("Not authorized.")
        sys.exit(0)

    if conf.user:
        resp = hand.client(["udel", conf.user], conf.sess_key)
        print("udel Response:", resp)
    else:
        # Just delete likely test users
        resp = hand.client(["udel", "peter3",], conf.sess_key)
        print("udel Response:", resp)

        resp = hand.client(["udel", "peter2",], conf.sess_key)
        print("udel Response:", resp)

        resp = hand.client(["udel", "peter3,comma"], conf.sess_key)
        print("udel Response:", resp)

        resp = hand.client(["udel", "peter4 space", ], conf.sess_key)
        print("udel Response:", resp)

        resp = hand.client(["udel", "admin2", "1234"], conf.sess_key)
        print("udel Response:", resp)

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

 # EOF
