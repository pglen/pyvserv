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

version = "1.0.0"
#progn = os.path.basename(sys.argv[0])
progn = os.path.basename(__file__)

cdoc = '''\
The pyvserv user manager.
Usage: %s [options] [hostname]
  hostname: host to connect to. (default: 127.0.0.1)
  options:  -d level  - Debug level 0-10
            -p        - Port to use (default: 6666)
            -l login  - Login Name; default: 'admin'
            -s lpass  - Login Pass; default: '1234' (for !!testing only!!)
            -t        - prompt for login pass
            -u user   - New/Op User Name; default: 'test_user'
            -x npass  - New/Op User Pass; default: '1234'
            -a        - Add user flag. Must be a unique user name
            -m        - Add admin flag. Add admin instead of a regular user
            -i kind   - List users. (kind = user / admin / disabled / initial)
            -e enflag - Enable / Disable user flag
            -T        - Prompt for new/op user pass / change pass
            -r        - Remove user flag -|-  -c        - Change pass flag
            -v        - Verbose          -|-  -V        - Print version number
            -q        - Quiet            -|-  -h        - Help (this screen)
If no action is specified, defaults to list users. ''' \
 % (progn)

__doc__= "<pre>" + cdoc + "</pre>"

def phelp():
    ''' Present command line help '''
    print(cdoc)
    sys.exit(0)

def pversion():
    ''' Display Version information '''
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",      0,              None],      \
    ["p:",  "port",         6666,           None],      \
    ["l:",  "login",        "admin",        None],      \
    ["s:",  "lpass",        "1234",         None],      \
    ["t",   "lprompt",      0,              None],      \
    ["v",   "verbose",      0,              None],      \
    ["q",   "quiet",        0,              None],      \
    ["m",   "admin",        0,              None],      \
    ["a",   "add",          0,              None],      \
    ["r",   "remove",       0,              None],      \
    ["c",   "change",       "",             None],      \
    ["u:",  "userx",        "test_user",    None],      \
    ["x:",  "passx",        "1234",         None],      \
    ["X:",  "chpass",       "",             None],      \
    ["T",   "prompt",       0,              None],      \
    ["e:",  "encomm",       "",             None],      \
    ["i:",  "listx",        "",             None],  \
    ["V",   None,           None,           pversion],  \
    ["h",   None,           None,           phelp]      \

conf = comline.Config(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def    mainfunct():

    ''' Entry point for pip script '''
    try:
        args = conf.comline(sys.argv[1:])

    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print(sys.exc_info())
        sys.exit(1)

    #if not conf.add and not conf.remove and not conf.encomm \
    #            and not conf.listx and not conf.change:
    #    print("One of: Add / Remove / Change / Enable / List option should be specified.")
    #    print("Use [ -a | -r | -p | -e  | -i ] options or the -h option for help.")
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

    #resp3 = hand.client(["hello",] , conf.sess_key, False)
    #if not conf.quiet:
    #    print("Hello sess Response:", resp3[1])

    resp = hand.client(["user", conf.login], conf.sess_key)
    if not conf.quiet:
        print("user Response:", resp)
    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();

    resp = hand.client(["pass", conf.lpass], conf.sess_key)
    if not conf.quiet:
        print("pass Response:", resp)
    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        print("Error on login, exiting.", resp)
        sys.exit(1)

    if conf.prompt:
        import getpass
        strx = getpass.getpass("Pass for new user %s: " % conf.userx)
        if not strx:
            print("Empty pass, aborting ...")
            sys.exit(0)
        conf.passx = strx

    if conf.encomm:
        resp = hand.client(["uena", conf.userx, conf.encomm, ], conf.sess_key)
        print("uen Response:", resp)
    elif conf.add:
        if conf.admin:
            resp = hand.client(["aadd", conf.userx, conf.passx], conf.sess_key)
        else:
            resp = hand.client(["uadd", conf.userx, conf.passx], conf.sess_key)
        print("uadd Response:", resp)
    elif conf.remove:
        resp = hand.client(["udel", conf.userx, conf.passx], conf.sess_key)
        print("udel Response:", resp)
    elif conf.change:
        if not conf.chpass:
            import getpass
            strx = getpass.getpass("Pass for change pass %s: " % conf.userx)
            if not strx:
                print("Empty pass, aborting ...")
                sys.exit(0)
            conf.chpass = strx
        resp = hand.client(["chpass", conf.userx, conf.passx, conf.chpass, ], conf.sess_key)
        print("uchpass Response:", resp)
    else:
        if not conf.listx:
            conf.listx = "user"
        resp = hand.client(["ulist", conf.listx], conf.sess_key)
        print("ulist Response:", resp)

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()


# EOF
