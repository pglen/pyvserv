#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

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

# ------------------------------------------------------------------------
# Globals

version = 1.0

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 6666)")
    print( "            -l login  - Login Name; default: 'user'")
    print( "            -s lpass  - Login Pass; default: '1234'")
    print( "            -u user   - User Name; default: 'user'")
    print( "            -a        - Add user. Must be unique.")
    print( "            -r        - Remove user (one of add or remove needed.")
    print( "            -u user   - User Name; default: 'user'")
    print( "            -p pass   - User pssword; default: '1234' (!!! for tests only)")
    print( "            -m        - Add admin instead of regular user")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
    ["l:",  "login",    "admin",    None],      \
    ["s:",  "lpass",    "1234",    None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["m",   "admin",    0,          None],      \
    ["a",   "add",      0,          None],      \
    ["r",   "remove",    0,         None],      \
    ["u:",  "userx",    "user",     None],      \
    ["p:",  "passx",    "1234",     None],      \
    ["t",   "prompt",    0,         None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

conf = comline.Config(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def    mainfunct():

    '''if  sys.version_info[0] < 3:
        print(("Needs python 3 or better."))
        sys.exit(1)'''

    args = conf.comline(sys.argv[1:])

    if not conf.add and not conf.remove:
        print("One of Add / Remove [ -a | -r ] should be specified.")
        sys.exit()

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
    print("Sess Response:", resp3)

    resp3 = hand.client(["hello",] , conf.sess_key, False)
    print("Hello sess Response:", resp3[1])

    resp = hand.client(["user", conf.login], conf.sess_key)
    print("user Response:", resp)
    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();

    resp = hand.client(["pass", conf.lpass], conf.sess_key)
    print("pass Response:", resp)
    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        print("Error on authentication, exiting.")
        sys.exit(1)

    if conf.prompt:
        import getpass
        #print("Pass for new user %s:" % conf.userx, end = " ");
        #sys.stdout.flush()
        #strx = input()
        strx = getpass.getpass("Pass for new user %s: " % conf.userx)
        if not strx:
            print("Aborting ...")
            sys.exit(0)
        conf.passx = strx
    if conf.add:
        if conf.admin:
            resp = hand.client(["aadd", conf.userx, conf.passx], conf.sess_key)
        else:
            resp = hand.client(["uadd", conf.userx, conf.passx], conf.sess_key)
        print("uadd Response:", resp)
    elif conf.remove:
        resp = hand.client(["udel", conf.userx, conf.passx], conf.sess_key)
        print("udel Response:", resp)

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()


# EOF
