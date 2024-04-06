#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. File Manipulation.

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
    print( "            -s lpass  - Login Pass; default: '1234' (for !!testing only!!)")
    print( "            -t        - prompt for login pass")
    print( "            -m dname  - Make directory")
    print( "            -r dname  - Remove directory")
    print( "            -u fname  - Upload file")
    print( "            -n fname  - Download file")
    print( "            -e fname  - Delete file")
    print( "            -a fname  - Stat file")
    print( "            -i        - List files")
    print( "            -I        - List directories")
    print( "            -g        - Long listings")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    print( " If no action is specified, command defauts to list files.")
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
    ["m:",  "mdname",       "",         None],      \
    ["r:",  "rdname",       "",         None],      \
    ["n:",  "dname",        "",         None],      \
    ["e:",  "delname",      "",         None],      \
    ["a:",  "stname",       "",         None],      \
    ["t",   "lprompt",      0,          None],      \
    ["i",   "list",         0,          None],      \
    ["I",   "dlist",        0,          None],      \
    ["g",   "long",         0,          None],      \
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
            print("Cannot login with empty pass, aborting ...")
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
    elif conf.delname:
        resp = hand.client(["del", conf.delname], conf.sess_key)
        print ("del response:", resp)
    elif conf.stname:
        resp = hand.client(["stat", conf.stname], conf.sess_key)
        #print ("stat response:", resp)
        print(pyclisup.formatstat(resp))
    elif conf.mdname:
        resp = hand.client(["mkdir", conf.mdname], conf.sess_key)
        print ("mkdir response:", resp)
    elif conf.rdname:
        resp = hand.client(["rmdir", conf.rdname], conf.sess_key)
        print ("rdmdir response:", resp)
    elif conf.dlist:
        resp = hand.client(["lsd", ], conf.sess_key)
        if conf.long:
            for aa in resp[1:]:
                resp2 = hand.client(["stat", aa], conf.sess_key)
                print(pyclisup.formatstat(resp2))
        else:
            print("lsd Response:", resp)
    else:
        #if conf.list:
        resp = hand.client(["ls", ], conf.sess_key)
        if conf.long:
            for aa in resp[1:]:
                resp2 = hand.client(["stat", aa], conf.sess_key)
                print(pyclisup.formatstat(resp2))
        else:
            print("ls Response:", resp)

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
