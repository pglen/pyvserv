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

version = "1.0.0"
#progn = os.path.basename(sys.argv[0])
progn = os.path.basename(__file__)

cdoc  = '''\
The pyvserv file manager.
Usage: %s  [options] [hostname]
  hostname: host to connect to. (default: 127.0.0.1)
  options:  -d level  - Debug level 0-10
            -p        - Port to use (default: 6666)
            -l login  - Login Name; default: 'admin'
            -s lpass  - Login Pass; default: '1234' (for !!testing only!!)
            -t        - Prompt for login pass
            -m dname  - Make directory    -|-  -r dname  - Remove directory
            -u fname  - Upload file       -|-  -n fname  - Download file
            -e fname  - Delete file       -|-  -a fname  - Stat file
            -i        - List files        -|-  -I        - List directories
            -g        - Long listings     -|-  -v        - Verbose
            -V        - Print version     -|-  -q        - Quiet
            -h        - Help (this screen)
If no action is specified, command defaults to list files. ''' \
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

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

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
    if conf.verbose:
        print("Sess Resp:", resp3)

    resp = hand.login(conf.login, conf.lpass, conf)
    if not conf.quiet:
        print("login Resp:", resp)
    if resp[0] != "OK":
        print("Login failed, exiting.", resp)
        hand.client(["quit"], conf.sess_key)
        hand.close();
        sys.exit(1)

    # Execute commands

    if conf.dname:
        resp = hand.getfile(conf.dname, "", conf.sess_key)
        print("download Resp:", resp)
    elif conf.fname:
        resp = hand.putfile(conf.fname, "", conf.sess_key)
        print("upload Resp:", resp)
    elif conf.delname:
        resp = hand.client(["del", conf.delname], conf.sess_key)
        print ("del Resp:", resp)
    elif conf.stname:
        resp = hand.client(["stat", conf.stname], conf.sess_key)
        #print ("stat Resp:", resp)
        print(pyclisup.formatstat(resp))
    elif conf.mdname:
        resp = hand.client(["mkdir", conf.mdname], conf.sess_key)
        print ("mkdir Resp:", resp)
    elif conf.rdname:
        resp = hand.client(["rmdir", conf.rdname], conf.sess_key)
        print ("rdmdir Resp:", resp)
    elif conf.dlist:
        resp = hand.client(["lsd", ], conf.sess_key)
        if conf.long:
            for aa in resp[1:]:
                resp2 = hand.client(["stat", aa], conf.sess_key)
                print(pyclisup.formatstat(resp2))
        else:
            print("lsd Resp:", resp)
    else:
        #if conf.list:
        resp = hand.client(["ls", ], conf.sess_key)
        if conf.long:
            for aa in resp[1:]:
                resp2 = hand.client(["stat", aa], conf.sess_key)
                print(pyclisup.formatstat(resp2))
        else:
            print("ls Resp:", resp)

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
