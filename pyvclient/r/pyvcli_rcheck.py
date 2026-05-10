#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

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

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong

#    ["n",   "plain",    0,          None],      \
#    ["i:",  "inter",    0,          None],      \
#    ["l:",  "login",    "admin",    None],      \
#    ["s:",  "lpass",    "1234",     None],      \
#    ["r:",  "rtest",    "",         None],      \

optarr.append ( ["n",   "plain",     "plain",       0,
                            None, "pain."] )
optarr.append ( ["i",   "inter",     "inter",       0,
                            None, "inter."] )
optarr.append ( ["l:",   "login=",     "login",       "admin",
                            None, "User to use."] )
optarr.append ( ["s:",   "lpass=",     "lpass",       "1234",
                            None, "Pass t use."] )
optarr.append ( ["r:",   "rtest=",     "rtest",    "",
                            None, "rtest."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def mainfunct():

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

    atexit.register(pyclisup.atexit_func, hand, conf)

    #resp3 = hand.client(["id",] , "", False)
    #print("ID Response:", resp3[1])

    #ret = ["OK",];  conf.sess_key = ""
    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", ret)
        hand.client(["quit"], conf.sess_key)
        hand.close();
        sys.exit(0)

    cresp = hand.login(conf.login, conf.lpass, conf)

    if cresp[0] != "OK":
        print("Error on logging in:", cresp)
        hand.client(["quit"], conf.sess_key)
        hand.close();
        sys.exit(0)

    if not conf.quiet:
        print ("Server login response:", cresp)

    # Set date range
    #if conf.start:
    #    dd = datetime.datetime.now()
    #    dd = dd.strptime(conf.start, "%Y-%m-%d %H:%M")
    #else:
    #    dd = datetime.datetime.now()
    #    dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)
    #print(dd)
    #dd_beg = dd + datetime.timedelta(0)
    #if conf.inter:
    #    dd_end = dd_beg + datetime.timedelta(0, conf.inter * 60)
    #else:
    #    dd_end = dd_beg + datetime.timedelta(1)

    cresp = hand.client(["rsize", "vote"], conf.sess_key)
    print ("rsize response:", cresp)

    if conf.rtest:
        import shlex
        zzz = shlex.split(conf.rtest)
        #print("zzz", zzz)
        cresp = hand.client(["rtest", "vote", "proof", *zzz], conf.sess_key)
        print ("rtest response:", cresp)
    else:
        cresp = hand.client(["rcheck", "vote", "proof"], conf.sess_key)
        print ("proof response:", cresp)

        cresp = hand.client(["rcheck", "vote", "hash"], conf.sess_key)
        print ("hash response:", cresp)

        cresp = hand.client(["rcheck", "vote", "data"], conf.sess_key)
        print ("data response:", cresp)
        if cresp[0] != "OK":
            sys.exit()

if __name__ == '__main__':
    mainfunct()

# EOF
