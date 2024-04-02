#!/usr/bin/env python

# ------------------------------------------------------------------------
import sys
if  sys.version_info[0] < 3:
    print(("Needs python 3 or better."))
    sys.exit(1)

__doc__ =\
'''
    Test client for the pyvserv project. Default user initialiser.
    This command can only be used from the local network, loopback
    interface. The command is used to create the initial user,
    and will not do anything if there is a user present already.

'''
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
    print( "Options:    -d level  - Debug level 0-10 default: 0")
    print( "            -p        - Port to use (default: 6666)")
    print( "            -v        - Verbose. Present more info")
    print( "            -u user   - User Name; default: 'admin'")
    print( "            -p pass   - Password; default: '1234' (!!! for tests only)")
    print( "            -q        - Quiet. Prrsent less info")
    print( "            -h        - Help (this screen)")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["u:",  "userx",    "admin",    None],      \
    ["p:",  "passx",    "1234",     None],      \
    ["t",   "test",     "x",        None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

conf = comline.Config(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def    mainfunct():

    ''' Initialize test user 'admin' with password '1234'
    Naturally, this is for testing. '''


    args = conf.comline(sys.argv[1:])

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

    #print("Connect Response:", respc)

    resp3 = hand.start_session(conf)
    print("Sess Response:", resp3)

    resp3 = hand.client(["hello",] , conf.sess_key, False)
    #print("Hello sess Response:", resp3[1])

    resp = hand.client(["uini", conf.userx, conf.passx], conf.sess_key)
    print("resp", resp)

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
