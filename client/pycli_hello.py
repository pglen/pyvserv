#!/usr/bin/env python

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

sys.path.append('../common')
import support, pycrypt, pyservsup, pyclisup, syslog, comline, pypacker

# ------------------------------------------------------------------------
# Functions from command line

optarr =  comline.optarr
optarr.append ( ["p:",  "port",     9999,   None, "Port to use (default: 9999)"] )

#print (optarr)

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

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

    try:
        resp2 = hand.connect(ip, conf.port)
    except:
        #support.put_exception("On connect")
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    if conf.quiet == False:
        print ("Server initial:", resp2[1])

    resp = hand.client(["hello"])
    if conf.quiet == False:
        print ("Server response:", resp[1])

    resp2 = hand.client(["quit"])
    if conf.quiet == False:
        print ("Server quit response:", resp2[1])

    hand.close();

    sys.exit(0)

# EOF













