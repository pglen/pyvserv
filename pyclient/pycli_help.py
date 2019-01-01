#!/usr/bin/env python3

# ------------------------------------------------------------------------
# Test client for the pyserv project. User add.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

sys.path.append('..')
from common import support, pycrypt, pyservsup, pyclisup, syslog

# ------------------------------------------------------------------------
# Globals 

myhandler = None
mydathand = None
pgdebug = 0
verbose = 0
port    = 9999
version = 1.0

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 9999)")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print( " Needs debug level or verbose to have any output.")
    sys.exit(0)


def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     9999,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = pyclisup.Config(optarr)

# Send out our special buffer (short)len + (str)message

def sendx(sock, message):
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

# ------------------------------------------------------------------------

def help():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 9999)")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    if  sys.version_info[0] < 3:
        print("Needs python 3 or better.")
        sys.exit(1)

    args = conf.comline(sys.argv[1:])        
    
    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1' 
    else:
        ip = args[0]
    
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #mydathand  = pydata.xHandler(s1)
    #myhandler  = pydata.DataHandler()     
    
    try:
        s1.connect((ip, port))
    except:
        print( "Cannot connect to:", ip + ":" + str(port), sys.exc_info()[1])
        sys.exit(1)

    hand = pyclisup.CliSup(s1)
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug
    
    hand.client("user peter")
    hand.client("pass 1234")
    
    hand.client("help")
    hand.client("help uadd")
    hand.client("help udel")
    
    hand.client("quit")
    s1.close();
    
    sys.exit(0)















