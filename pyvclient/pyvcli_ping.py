#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")

optarr = comline.optarrlong
conf = comline.ConfigLong(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    #if  sys.version_info[0] < 3:
    #    print("Needs python 3 or better.")
    #    sys.exit(1)
    #
    opts, args = conf.comline(sys.argv[1:])

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug
    hand.quiet = conf.quiet

    try:
        resp2 = hand.connect(ip, conf.port)
        if conf.quiet == False:
            #print ("Server initial:", resp2[1])
            respini = hand.pb.decode_data(resp2[1])[0]
            print ("Server initial:", respini)

    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    hand.client(["quit"])
    hand.close()

    sys.exit(0)

# EOF