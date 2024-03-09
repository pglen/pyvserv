#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, uuid

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..'))

from pyvcommon import support, pycrypt, pyservsup, pyclisup, pyvhash
from pyvcommon import pysyslog, comline

import pyvpacker

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
    print( "            -n        - Number of records to put")
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
    ["p:",  "port",     6666,   None],      \
    ["c:",  "comm",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["s",   "showkey",  "",     None],      \
    ["n:",   "numrec",   1,     None],      \
    ["t",   "test",     "x",    None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])
    #print(vars(conf))

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

    ttt = time.time()
    pvh = pyvhash.BcData()
    pvh.addpayload({"Vote": '0', "UID":  str(uuid.uuid1()), })
    #print(pvh.datax)

    pvh.hasharr()
    pvh.powarr()
    #if not pvh.checkhash():
    #    print("Error on hashing payload .. retrying ...")
    #elif not pvh.checkpow():
    #    print("Error on POW payload .. retrying ...")

    pvh.num_zeros = 3
    maxcnt = 20
    while True:
        if maxcnt == 0:
            print("Cannot produce hash")
            sys.exit()
        pvh.hasharr()
        pvh.powarr()
        if not pvh.checkhash():
            print("Error on hashing payload .. retrying ...")
        elif not pvh.checkpow():
            print("Error on POW payload .. retrying ...")
        else:
            break
        maxcnt -= 1
    print("Chain cnt", pvh.cnt)
    print("chain %.3fms" % ((time.time() - ttt) * 1000) )

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    resp3 = hand.client(["hello", "world"] , "", False)
    print("Hello Resp:", resp3)

    resp4 = hand.client(["tout", "30",], conf.sess_key)
    print("Server tout Response:", resp4)

    ret = hand.start_session(conf)

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  conf.sess_key[:12], '...' )
    print(" ----- Post session, all is encrypted ----- ")

    resp4 = hand.client(["tout", "30",], conf.sess_key)
    print("Server tout Response:", resp4)

    ttt = time.time()
    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    print("hello %.3fms" % ((time.time() - ttt) * 1000) )
    print("Server hello resp:", resp4[1])

    ttt = time.time()
    cresp = hand.client(["user", "admin"], conf.sess_key)
    print("user %.3fms" % ((time.time() - ttt) * 1000) )
    print ("Server user respo:", cresp)

    ttt = time.time()
    cresp = hand.client(["pass", "1234"], conf.sess_key)
    print("pass %.3fms" % ((time.time() - ttt) * 1000) )
    print ("Server pass resp:", cresp)

    cresp = hand.client(["dmode",], conf.sess_key)
    #print("dmode", cresp)
    if cresp[1] == '0':
        print("Enter twofa code: (ret to skip)", end = "")
        sesscode = input()
        if sesscode:
            cresp = hand.client(["twofa", sesscode], conf.sess_key)
            print ("Server twofa resp:", cresp)
            if cresp[0] != OK:
                print ("Server twofa failed")
                sys.exit(0)

    # Interactive, need more time
    tout = hand.client(["tout", "200",], conf.sess_key)
    #print (tout)

    #pvh2 = pyvhash.BcData(pvh)
    #pvh2.addpayload({"Added New": "new stuff"})
    #pvh2.hasharr();     pvh2.powarr()
    #print(pvh2.datax)
    #i2 not pvh2.checkpow() or not pvh2.checkhash():
    #     print("Error on hashing pyload2")

    if conf.pgdebug > 2:
        print(pvh.datax)

    if hand.verbose:
        print("Sending Data:", pvh.datax)

    ttt = time.time()
    for aa in range(conf.numrec):
        cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
        print ("Server rput response:", cresp)
    print("rput %.3fms" % ((time.time() - ttt) * 1000) )

    cresp = hand.client(["quit",],conf.sess_key)
    print ("Server quit  response:", cresp)
    hand.close();

    sys.exit(0)

# EOF

