#!/usr/bin/env python

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

sys.path.append('../common')
import support, pycrypt, pyservsup, pyclisup, syslog, comline, pypacker

version = "1.0"

optarr =  comline.optarr
optarr.append ( ["p:",  "port",  9999,   None, "Port to use (default: 9999)"] )

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

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
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    print ("Server initial:", resp2[1])

    resp = hand.client(["ver"])

    if conf.quiet == False:
        print ("Server ver response:", resp[1])

    ret = pyclisup.start_session(hand, conf)
    if ret[0] == "OK":
        print("Sess Key ACCEPTED:",  ret[1])

    resp = hand.client(["ver"], conf.sess_key)

    if conf.quiet == False:
        print ("Server ver response:", resp[1])

    print("Wating for timeout ..")
    response = hand.getreply(conf.sess_key)

    print ("Server timeout response:", response[1])

    #qr = hand.client(["quit"])
    #hand.close()
    #print ("Server quit response:", qr[1])

    sys.exit(0)

# EOF













