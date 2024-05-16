#!/usr/bin/env python3

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, uuid, atexit, datetime

from Crypto import Random

# This repairs the path from local run to pip run.
# Remove pip version for local tests

try:
    from pyvcommon import support
    #print("sf", sf)
    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
except:
    #print("pathching")
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    from pyvcommon import support

from pyvcommon import support, pycrypt, pyservsup, pyclisup, pyvhash
from pyvcommon import pysyslog, comline, pyvgenr

from pyvguicom import pgutils, pgtests

# ------------------------------------------------------------------------
# Functions from command line

#print( "            -n        - Number of records to put")

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
    print( "            -k keyval - Put this key")
    print( "            -n numrec - Put this many records")
    print( "            -t        - Test. Weak hash for testing")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["c:",  "comm",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["k:",  "putkey",   "",     None],      \
    ["n:",  "numrec",   1,     None],      \
    ["t",   "test",     0,    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunct():

    args = conf.comline(sys.argv[1:])
    #print(vars(conf))

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug
    hand.comm  = conf.comm

    pvh = pyvgenr.genvrec()

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    atexit.register(pyclisup.atexit_func, hand, conf)

    #resp3 = hand.client(["hello", "world"] , "", False)
    #print("Hello Resp:", resp3)

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        sys.exit(0)

    #ttt = time.time()
    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("hello %.3fms" % ((time.time() - ttt) * 1000) )
    #if resp4[0] != "OK":
    #    print("Server hello resp:", resp4[1])
    #    sys.exit()

    #ttt = time.time()
    cresp = hand.client(["user", "admin"], conf.sess_key)
    #print("user %.3fms" % ((time.time() - ttt) * 1000) )
    #print ("Server user respo:", cresp)
    #ttt = time.time()
    cresp = hand.client(["pass", "1234"], conf.sess_key)
    #print("pass %.3fms" % ((time.time() - ttt) * 1000) )
    if cresp[0] != "OK":
        print("Cannot log on")
        sys.exit(1)
    if not conf.quiet:
        print ("Server pass resp:", cresp)

    cresp = hand.client(["dmode",], conf.sess_key)
    #print("dmode", cresp)
    if cresp[1] == '0':
        print("Enter twofa code: (ret to skip)", end = "")
        sesscode = input()
        if sesscode:
            cresp = hand.client(["twofa", sesscode], conf.sess_key)
            print ("Server twofa resp:", cresp)
            if cresp[0] != OK:
                print ("Server twofa failed")
                sys.exit(0)

    if conf.numrec == 1:
        #print("putkey:", conf.putkey)
        pvh = pyvgenr.genvrec(conf.putkey)

        pvh.hasharr()
        print("Calculating PROW ....", end = " "); sys.stdout.flush()
        while not pvh.powarr():
            pass
        print("OK")

        if conf.pgdebug > 2:
            print(pvh.datax)

        if hand.verbose:
            print("Sending Data:", pvh.datax)

        cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
        if not conf.quiet:
            print ("resp:", cresp)
    else:
        for aa in range(conf.numrec):
            pvh = pyvgenr.genvrec()
            pvh.hasharr()
            print("Calculating PROW ....", end = " "); sys.stdout.flush()
            while not pvh.powarr():
                pass
            print("OK")

            ttt = time.time()
            cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
            if not conf.quiet:
                print("putrec: %s  %.3fms" % (cresp[0], (time.time() - ttt) * 1000) )
            #print ("rput resp:", cresp)

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF

