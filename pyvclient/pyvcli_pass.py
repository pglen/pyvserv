#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

from Crypto import Random

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline


'''
# test encrypt with large keys
rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
        "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ=="
sss = bluepy.encrypt(rrr, conf.sess_key)
ttt = bluepy.decrypt(sss, conf.sess_key)
print (rrr)
print (ttt)
'''

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p port   - Port to use (default: 6666)")
    print( "            -l level  - Log level (default: 0)")
    print( "            -c file   - Save comm to file")
    print( "            -s        - Showkey")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    #print( " Needs debug level or verbose to have any output.")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

    # option, var_name, initial_val, function
#optarr = \
#    ["c:",  "comm",     "",     None],      \
#    ["s",   "showkey",  "",     None],      \
#    ["t",   "test",     "x",    None],      \
#conf = comline.Config(optarr)

# For this file
VERSION = "1.0.0"

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")

optarr = []
optarr.append ( ["c:",   "comm",     "comm",       "",
                            None, "comm"] )
optarr.append ( ["s:",   "showkey",     "showkey",       "",
                            None, "Show key"] )
optarr.append ( ["t:",   "test",     "test",       "",
                            None, "test"] )
optarr += comline.optarrlong
conf = comline.ConfigLong(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    opts, args = conf.comline(sys.argv[1:])

    if conf.comm:
        print("Save to filename", conf.comm)

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

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    resp3 = hand.client(["hello",] , "", False)
    print("Hello Response:", resp3[1])

    ret = hand.start_session(conf)

    #if ret[0] == "OK":
    #    print("Sess Key ACCEPTED:",  ret[1])

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])
    print("Post session, all is encrypted")

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    print("Hello sess Response:", resp4)

    cresp = hand.client(["user", "admin"], conf.sess_key)
    print ("Server user response:", cresp[1])

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    print ("Server pass response:", cresp[1])

    #cresp = hand.client(["chpass", "1234"], conf.sess_key)
    #print ("Server chpass response:", cresp[1])

    hand.client(["quit",], conf.sess_key)
    hand.close();

    sys.exit(0)

# EOF

