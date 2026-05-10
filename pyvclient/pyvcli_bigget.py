#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

#optarr = \
#    ["f:",  "file",     6666,   None],      \
#conf = comline.Config(optarr)

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong
optarr.append ( ["f:",   "file=",     "file",       "bigtext",
                            None, "Create user with prompt."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

    opts, args = conf.comline(sys.argv[1:])

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    #hand.comm  = conf.comm

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    #resp3 = hand.client(["id",] , "", False)
    #print("ID Response:", resp3[1])

    #ret = ["OK",];  conf.sess_key = ""
    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])

    #if conf.sess_key:
    #    if not conf.quiet:
    #        print("Post session, session key:", conf.sess_key[:12], "...")

    #resp3 = hand.client(["hello", ],  conf.sess_key, False)
    #if not conf.quiet:
    #    print("Hello Response:", resp3)

    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("Hello Response:", resp4[1])

    cresp = hand.login("admin", "1234", conf)
    if not cresp[0] == "OK":
        print("Cannot login", cresp)
        sys.exit()

    if not conf.quiet:
        print ("Server login response:", cresp)

    bigfname = "bigfile"    # Use this name for cleaning it
    bigbuff = b"abcdef" * 1024
    # Create bigfile
    fp = open(bigfname, "wb")
    for aa in range(1024 * 10):
        fp.write(bigbuff)
    fp.close()

    # Put big file up
    if not conf.quiet:
        print("Started file UP ...", )
    ttt = time.time()
    resp = hand.putfile(bigfname, "", conf.sess_key)
    filesize = support.fsize(bigfname)
    rate = filesize / (time.time() - ttt)
    if not conf.quiet:
        print("filesize", filesize)
    if resp[0] != "OK":
        print ("fput resp:", resp)
        cresp = hand.client(["quit", ], conf.sess_key)
        print ("Server quit response:", cresp)
        sys.exit()
    print ("fput response:", resp, "time %.2f kbytes/sec" % (rate/1024))

    if not conf.quiet:
        print("Started bigfile DOWN")
    ttt = time.time()
    ret = hand.getfile(bigfname, bigfname + "_local", conf.sess_key)
    filesize = support.fsize(bigfname + "_local")
    if not conf.quiet:
        print("filesize", filesize)
    rate = filesize / (time.time() - ttt)
    print ("fget response:", ret, "time %.2f kbytes/sec" % (rate/1024))

    cresp = hand.client(["quit", ], conf.sess_key)
    #print ("Server quit response:", cresp)

    ret = os.system("diff " + bigfname + " " + bigfname + "_local")
    if ret:
        print("Error: Files Differ", ret)
    else:
        print("Files Compare OK")

    #os.remove(bigfname)
    #os.remove(bigfname + "_local")

    sys.exit(0)

 # EOF
