#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. File Manipulation.

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
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] [hostname]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 6666)")
    print( "            -l login  - Login Name; default: 'admin'")
    print( "            -s lpass  - Login Pass; default: '1234'")
    print( "            -t        - prompt for login pass")
    print( "            -u fname  - Upload file")
    print( "            -n fname  - Download file")
    print( "            -m dname  - Make directory")
    print( "            -r dname  - Remove directory")
    print( "            -a fname  - Stat file")
    print( "            -i        - List (dir) files")
    print( "            -I        - List (dir) directories")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    print( " If no action is specified, it defauts to ls (dir).")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",      0,          None],      \
    ["p:",  "port",         6666,       None],      \
    ["l:",  "login",        "admin",    None],      \
    ["s:",  "lpass",        "1234",     None],      \
    ["u:",  "fname",        "",         None],      \
    ["n:",  "dname",        "",         None],      \
    ["t",   "lprompt",      0,          None],      \
    ["i",   "list",         0,          None],      \
    ["I",   "dlist",        0,          None],      \
    ["v",   "verbose",      0,          None],      \
    ["q",   "quiet",        0,          None],      \
    ["V",   None,           None,       pversion],  \
    ["h",   None,           None,       phelp]      \

conf = comline.Config(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def    mainfunct():

    '''if  sys.version_info[0] < 3:
        print(("Needs python 3 or better."))
        sys.exit(1)'''

    args = conf.comline(sys.argv[1:])

    #if not conf.add and not conf.remove and not conf.encomm \
    #            and not conf.listx and not conf.change:
    #if not conf.list and not conf.dlist and not conf.fname:
    #    print( " One of Upload / Download / Mkdir / Rmdir / List option is needed.")
    #    #print("Use [ -a | -r | -p | -e  | -i ] options or the -h option for help.")
    #    sys.exit()

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    if conf.lprompt:
        import getpass
        strx = getpass.getpass("Pass for login %s: " % conf.login)
        if not strx:
            print("Cnnot login with empty pass, aborting ...")
            sys.exit(0)
        conf.lpass = strx

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    resp3 = hand.start_session(conf)
    if not conf.quiet:
        print("Sess Response:", resp3)
    resp = hand.login(conf.login, conf.lpass, conf)
    if not conf.quiet:
        print("login Response:", resp)
    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        print("Error on authentication, exiting.")
        sys.exit(1)

    # Execute commands

    if conf.dname:
        resp = hand.getfile(conf.dname, "", conf.sess_key)
        print("download Response:", resp)
    elif conf.fname:
        resp = hand.putfile(conf.fname, "", conf.sess_key)
        print("upload Response:", resp)
    elif conf.dlist:
        resp = hand.client(["lsd", ], conf.sess_key)
        print("lsd Response:", resp)
    else:
        #if conf.list:
        resp = hand.client(["ls", ], conf.sess_key)
        print("ls Response:", resp)

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()


# EOF
