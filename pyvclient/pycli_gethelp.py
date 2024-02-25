#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

# ------------------------------------------------------------------------
# Globals

myhandler = None
mydathand = None
pgdebug = 0
subhelp = ""
verbose = 0
port    = 6666
version = 1.0

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print( "            -s str    - Subhelp string")
    print()
    print( " Needs debug level or verbose to have any output.")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

optarr = \
    ["d:",  "pgdebug",  0,       None],      \
    ["p:",  "port",     6666,    None],      \
    ["v",   "verbose",  0,       None],      \
    ["q",   "quiet",    0,       None],      \
    ["t",   "test",     "x",     None],      \
    ["s:",  "subhelp",  subhelp, None],      \
    ["V",   None,       None,    pversion],  \
    ["h",   None,       None,    phelp]      \

conf = comline.Config(optarr)

# Send out our special buffer (short)len + (str)message

'''def sendx(sock, message):
    strx = struct.pack("!h", len(message)) + message
    sock.send(strx)

def sendfile(s1, fname, toname):

    response = ""
    try:
        flen = os.stat(fname)[stat.ST_SIZE]
        fh = open(fname)
    except:
        print( "Cannot open file", sys.exc_info()[1])
        return

    client(s1, "file " + toname)
    client(s1, "data " + str(flen))
    while 1:
        buff = fh.read(pyservsup.buffsize)
        if len(buff) == 0:
            break
        sendx(s1, buff)
    response = myhandler.handle_one(mydathand)

    if verbose:
        print( "Received: '%s'" % response)

    return response

# ------------------------------------------------------------------------

def client(sock, message):

    sendx(sock, message)
    if verbose:
        print( "Sent: '%s'" % message)

    response = myhandler.handle_one(mydathand)
    if verbose:
        print( "Received: '%s'" % response)

    return response
'''

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    #print("subhelp", conf.subhelp);

    try:
        resp2 = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    #if conf.quiet == False:
    #    print ("Server initial:", resp2[1])

    if conf.subhelp:
        resp = hand.client(["help", conf.subhelp])
    else:
        resp = hand.client(["help",])

    if conf.quiet == False:
        print ("Server response:", resp)

    hand.client(["quit",])
    hand.close();

    sys.exit(0)

# EOF









