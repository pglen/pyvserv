#!/usr/bin/env python3

from __future__ import print_function

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

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

# ------------------------------------------------------------------------
# Functions from command line

optarr =  comline.optarr
optarr.append ( ["p:",  "port",  6666,   None, "Port to use (default: 6666)"] )

#print (optarr)

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunct():

    if sys.version_info[0] < 3:
        print("Warning! This script was meant for python 3.x")
        time.sleep(1)

    args = conf.comline(sys.argv[1:])

    #for aa in vars(conf):
    #    print(aa, getattr(conf, aa))

    pyclisup.verbose = conf.verbose

    if conf.verbose and conf.pgdebug:
        print("Debug level", conf.pgdebug)

    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    #print("dir".__doc__)

    try:
        resp2 = hand.connect(ip, conf.port)
    except:
        #support.put_exception("On connect")
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    if conf.quiet == False:
        respini = hand.pb.decode_data(resp2[1])[0]
        print ("Server initial:", respini)

    resp = hand.client(["id"])
    if conf.quiet == False:
        print("resp", resp)

    resp2 = hand.client(["quit"])
    if conf.quiet == False:
        print ("Server quit response:", resp2)

    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF