#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

# ------------------------------------------------------------------------
# Globals

version = "1.0.0"

#optarr = \
#    ["d:",  "pgdebug",  0,      None],      \
#    ["p:",  "port",     6666,   None],      \
#    ["v",   "verbose",  0,      None],      \
#    ["q",   "quiet",    0,      None],      \
#    ["t",   "test",     "x",    None],      \
#    ["V",   None,       None,   pversion],  \
#    ["h",   None,       None,   phelp]      \
#conf = comline.Config(optarr)

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong
optarr.append ( ["u:",   "userx",     "userx",       "admin",
                            None, "Create user with name."] )
optarr.append ( ["l:",   "passx",     "passx",       "1234",
                            None, "Create user with pass."] )
optarr.append ( ["t:",   "prompt",     "prompt",       0,
                            None, "Create user with prompt."] )
optarr.append ( ["f",   "noprompt",     "noprompt",       0,
                            None, "Create user with noprompt."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

    if  sys.version_info[0] < 3:
        print(("Needs python 3 or better."))
        sys.exit(1)

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

    resp3 = hand.client(["hello",] , "", False)
    print("Hello Response:", resp3)

    resp3 = hand.start_session(conf)
    print("Sess Response:", resp3)

    resp3 = hand.client(["hello",] , conf.sess_key, False)
    print("Hello sess Response:", resp3[1])

    resp = hand.client(["user", "admin"], conf.sess_key)
    print("user Response:", resp)
    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        raise ValueError("No user", resp[1])

    resp = hand.client(["pass", "1234"], conf.sess_key)
    print("pass Response:", resp)
    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        raise ValueError("Not authorized", resp[1])

    resp = hand.client(["uadd", "peter3", "1234"], conf.sess_key)
    print("uadd Response:", resp)

    resp = hand.client(["uadd", "peter2", "1234"], conf.sess_key)
    print("uadd Response:", resp)

    resp = hand.client(["uadd", "peter3,comma", "1234"], conf.sess_key)
    print("uadd Response:", resp)

    resp = hand.client(["uadd", "peter4 space", "1234"], conf.sess_key)
    print("uadd Response:", resp)

    resp = hand.client(["aadd", "admin2", "1234"], conf.sess_key)
    print("aadd Response:", resp)

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

# EOF
