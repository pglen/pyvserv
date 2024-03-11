#!/usr/bin/env python

import sys, os
import readline

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

# This repairs the path from local run to pip run.
# Remove pip version for local tests
try:
    from pyvcommon import support

    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
    #sys.path.append(os.path.join(sf, "pyvgui"))
    #sys.path.append(os.path.join(sf, "pyvgui", "guilib"))

except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    #sys.path.append(os.path.join(base, "..", "pyvgui"))
    #sys.path.append(os.path.join(base, "..", "pyvgui", "guilib"))
    from pyvcommon import support

print("Load:", sys.path[-1])


base = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(base,  '../pyvcommon'))
sys.path.append(os.path.join(base,  '..'))

from pyvcommon import support, pycrypt, pyclisup
from pyvcommon import pysyslog, comline

# ------------------------------------------------------------------------
# Globals

version = 1.0

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 9999)")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -n        - No encryption (plain)")
    print( "            -h        - Help")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["f:",  "file",     6666,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["n",   "plain",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunct():

    args = conf.comline(sys.argv[1:])

    #print(vars(conf))

    #if conf.comm:
    #    print("Save to filename", conf.comm)

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

    conf.sess_key = ""
    #ret = ["OK",];  conf.sess_key = ""
    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])

    if conf.sess_key:
        print(" ------ Post session, session key:", conf.sess_key[:12], "...")

    resp3 = hand.client(["hello", ],  conf.sess_key, False)
    print("Hello Resp:", resp3)

    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("Hello Response:", resp4[1])

    cresp = hand.login(conf, "admin", "1234")
    print ("Login resp:", cresp)

    # Start a new session for the rest of the work
    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    if conf.sess_key:
        print(" ------ Post session, session key:", conf.sess_key[:12], "...")

    resp3 = hand.client(["hello", ],  conf.sess_key, False)
    print("Hello2 Resp:", resp3)

    # Interactive, need more time
    hand.client(["tout", "30",], conf.sess_key)

    print ("Enter commands, Ctrl-C or 'done' to quit. Prefix local commands with '!'")

    mainloop(conf, hand)

    #ret2 = hand.getfile("zeros", "zeros_local", conf.sess_key)
    #print ("Server  fget response:", ret2)
    #bfile ="bigfile"
    #print("Started bigfile ...", bfile)
    #ttt = time.time()
    #ret = hand.getfile(bfile, bfile + "_local", conf.sess_key)
    #filesize = support.fsize(bfile+ "_local")/1024
    #print("filesize", filesize)
    #rate = filesize / (time.time() - ttt)
    #print ("Server fget response:", ret, "time %.2f kbytes/sec" % rate)

    cresp = hand.client(["quit", ], conf.sess_key)
    print ("Server quit response:", cresp)
    hand.sock.shutdown(socket.SHUT_RDWR)
    sys.exit(0)


def mainloop(conf, hand):

    cresp = ""
    while(True):
        try:
            onecom = input(">> ")
            #print ("'" + onecom.split() + "'")
            ss = onecom.split()
            if ss  != []:

                # process commands that need additional data

                if ss[0] == "quit":
                    break
                elif ss[0] == "sess":
                    cresp = hand.start_session(conf)
                    if conf.sess_key:
                        print("Post session, session key:", conf.sess_key[:12], "...")

                elif ss[0] == "fget":
                    if len(ss) < 2:
                        print("Use: fget fname")
                        continue
                    ret2 = hand.getfile(ss[1], ss[1] + "_local", conf.sess_key)
                    print ("Server fget response:", ret2)
                    continue

                elif ss[0] == "fput":
                    if len(ss) < 2:
                        print("Use: fput fname")
                        continue
                    ret2 = hand.putfile(ss[1], "", conf.sess_key)
                    print ("Server fput response:", ret2)
                    continue

                elif ss[0] == "file":
                    if not os.path.isfile(ss[1]):
                        print("File must exist.")
                        continue
                    cresp = hand.start_session(conf)
                    if conf.sess_key:
                        print("Post session, session key:", conf.sess_key[:12], "...")
                    continue

                elif ss[0][0] == "!":
                    #print ("local command")
                    os.system(ss[0][1:] + " " + " ".join(ss[1:]))
                    continue
                else:
                    # No wrapper needed
                    cresp = hand.client(ss, conf.sess_key)
                    # post process
                    print ("Server response:", cresp)
        except:
            print(sys.exc_info())
            break

if __name__ == '__main__':
    mainfunct()
