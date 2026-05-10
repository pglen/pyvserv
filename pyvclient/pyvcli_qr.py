#!/usr/bin/env python

import sys, os
import readline

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

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

#optarr = \
#    ["f:",  "file",     "",     None],      \
#conf = comline.Config(optarr)

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong
optarr.append ( ["f:",   "file=",     "file",       "",
                            None, "File."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

def mainfunct():

    try:
        opts, args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print(sys.exc_info())
        sys.exit(1)

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
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        sys.exit(0)

    if conf.verbose:
        resp = hand.client(["hello"], conf.sess_key)
        print("Hello resp:", resp)

    if conf.file:
        resp = hand.login("admin", "1234", conf)
        if resp[0] != "OK":
            print("Login Response:", resp)
            sys.exit()

        fp = open(conf.file, "rb")
        buff = fp.read()
        fp.close()
        #print("len:", len(buff))
        resp3 = hand.client(["qr", buff], conf.sess_key, False)
        print("QR UP Response:", resp3)
    else:
        resp3 = hand.client(["qr",], conf.sess_key, False)
        if resp3[0] != "OK":
            print("QR Response:", resp3)
            sys.exit()

        # Save
        fp = open("qr.png", 'wb')
        if type(resp3[1]) != type(b""):
            resp3[1] = resp3[1].encode()
        fp.write(resp3[1])
        fp.close()
        if not conf.quiet:
            print("Downloaded QR code, saved to 'qr.png'", len(resp3[1]), "bytes")

    rrr = hand.client(["quit"], conf.sess_key)
    if conf.verbose:
        print("Quit resp:", rrr)
    hand.close();

    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
