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

version = "1.0.0"

def phelp():

    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] [hostname]")
    print( "  hostname: host to connect to. (default: 127.0.0.1)")
    print( "  options:    -d level  - Debug level 0-10 default: 0")
    print( "              -p        - Port to use (default: 6666)")
    print( "              -v        - Verbose. Present more info.")
    print( "              -q        - Quiet. Present less info.")
    print( "              -u user   - User Name; default: 'admin'")
    print( "              -l pass   - Password; default: '1234' (!! for tests only !!)")
    print( "              -t        - Prompt for password.")
    print( "              -f        - Force, No prompt for demo.")
    print( "              -h        - Help (this screen)")
    print( "The user will be prompted for confirmation if demosystem is created.")
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
    ["l:",  "passx",    "1234",     None],      \
    ["t",   "prompt",    0,         None],      \
    ["f",   "noprompt",  0,         None],      \
    ["V",   None,        None,      pversion],  \
    ["h",   None,        None,      phelp]      \

conf = comline.Config(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def    mainfunct():

    ''' Initialize test user 'admin' with password '1234'
        Naturally, this is for testing.
        On production server, add a real password.
    '''

    try:
        args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print(sys.exc_info())
        sys.exit(1)

    if conf.verbose and conf.pgdebug:
        print("Debug level", conf.pgdebug)

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if conf.prompt:
        import getpass
        strx = getpass.getpass("Enter Pass for initial user: ")
        if not strx:
            print("Empty pass, aborting ...")
            sys.exit(0)
        conf.passx =  strx

    if conf.passx == "1234":

        if not conf.noprompt:
            print("This creates credentials for a demo / test system.")
            print("Are you sure? (y/N) ", end = ""); sys.stdout.flush()
            sss = input().strip().lower()
            #print(sss)
            if sss != "y" and sss != "yes":
                print("You may use the -t option for password prompt. Exiting ...")
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

    #print("Connect Response:", respc)

    resp3 = hand.start_session(conf)
    if not conf.quiet:
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
