#!/usr/bin/env python3

# ------------------------------------------------------------------------
# Test client for the pyserv project.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

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

# For this file
version = "1.0.0"

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print( "The pyvserv version query.")
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] [hostname]")
    print( "  hostname: host to connect to. (default: 127.0.0.1)")
    print( "  options:    -d level  - Debug level 0-10")
    print( "              -p port   - Port to use (default: 6666)")
    print( "              -v        - Verbose")
    print( "              -V        - Version")
    print( "              -q        - Quiet")
    print( "              -h        - Help")
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunct():

    if sys.version_info[0] < 3:
        print("Warning! This script was meant for python 3.x")
        sys.exit()

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

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    try:
        resp2 = hand.connect(ip, conf.port)
    except:
        #support.put_exception("On connect")
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    if conf.verbose:
        respini = hand.pb.decode_data(resp2[1])[0]
        print ("Server initial:", respini)

    resp = hand.client(["ver"])
    print ("Version resp:", resp)

    resp = hand.client(["quit"])
    if conf.verbose:
        print ("Server quit resp:", resp)
    hand.close()

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
