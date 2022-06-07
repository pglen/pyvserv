#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

sys.path.append('../common')
import support, pycrypt, pyservsup, pyclisup, syslog
import comline, pypacker, crysupp

sys.path.append('../bluepy')
import bluepy

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
    print( "            -p port   - Port to use (default: 9999)")
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
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     9999,   None],      \
    ["c:",  "comm",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["s",   "showkey",  "",     None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

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

    resp3 = hand.client(["hello", "world"] , "", False)
    print("Hello Response: ", resp3)

    ret = pyclisup.start_session(hand, conf)

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    print("Sess Key ACCEPTED:",  ret[1])
    print("Post session, all is encrypted")

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    print("Server hello Response:", resp4[1])

    cresp = hand.client(["user", "admin"], conf.sess_key)
    print ("Server user  response:", cresp)

    cresp = hand.client(["pass", "1234"], conf.sess_key)
    print ("Server pass  response:", cresp)

    #resp = hand.client(["pass", "12345"], conf.sess_key)
    #print ("Server pass  response:", cresp)

    #resp = hand.client(["pass", "12345"], conf.sess_key)
    #print ("Server pass response:", cresp)

    #cresp = hand.client(["pass", "12345"], conf.sess_key)
    #print ("Server pass response:", cresp[1])
    #if(cresp[1][:2] != "OK"): sys.exit(1)

    #cresp = hand.client(["pass", "1234"], conf.sess_key)
    #print ("Server pass  response:", cresp[1])

    #cresp = hand.client(["hello", "1234"], conf.sess_key)
    #print ("Server hello response:", cresp[1])

    cresp = hand.client(["quit",],conf.sess_key)
    print ("Server quit  response:", cresp[1])
    hand.close();

    sys.exit(0)

# EOF

