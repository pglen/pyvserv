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

    resp3 = hand.client(["hello",] , "", False)
    print("Hello Response:", resp3[1])

    #if conf.quiet == False:
    #    print ("Server initial:", resp2)

    resp = hand.client(["akey"])
    kkk = resp[1].split()

    if kkk[0] != "OK":
        print("Error on getting key:", resp[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    if conf.verbose:
        print("Got hash:", "'" + kkk[1] + "'")
        pass

    resp2 = hand.getreply()

    if conf.pgdebug > 4:
        print ("Server response2:\n" +  "'" + resp2[1].decode("cp437") +  "'\n")

    hhh = SHA512.new(); hhh.update(resp2[1])

    if conf.pgdebug > 3:
        print("Hash1:  '" + kkk[2] + "'")
        print("Hash2:  '" + hhh.hexdigest() + "'")

    # Remember key
    if hhh.hexdigest() !=  kkk[2]:
        print("Tainted key, aborting.")
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    hand.pkey = resp2[1]
    if conf.quiet == False:
         print("Key response:", kkk[0], kkk[2][:32], "...")

    if conf.pgdebug > 4:
         print(hand.pkey)

    if conf.pgdebug > 2:
        print ("Server response:", "'" + hhh.hexdigest() + "'")

    if conf.showkey or conf.pgdebug > 5:
        #print("Key:")
        print(hand.pkey)

    try:
        hand.pubkey = RSA.importKey(hand.pkey)
        if conf.pgdebug > 4:
            print (hand.pubkey)
    except:
        print("Cannot import public key.")
        support.put_exception("import key")
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    if conf.pgdebug > 1:
        print("Got ", hand.pubkey, "size =", hand.pubkey.size())

    # Generate communication key
    conf.sess_key = Random.new().read(512)
    sss = SHA512.new(); sss.update(conf.sess_key)

    cipher = PKCS1_v1_5.new(hand.pubkey)
    #print ("cipher", cipher.can_encrypt())

    if conf.pgdebug > 2:
        support.shortdump("conf.sess_key", conf.sess_key )

    sess_keyx = cipher.encrypt(conf.sess_key)
    ttt = SHA512.new(); ttt.update(sess_keyx)

    if conf.pgdebug > 2:
        support.shortdump("sess_keyx", sess_keyx )

    #print("Key Hexdigest", ttt.hexdigest()[:16])

    resp3 = hand.client(["sess", sss.hexdigest(), ttt.hexdigest(), sess_keyx], "", False)

    print("Sess Response:", resp3[1])

    kkk = resp3[1].split()

    if kkk[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    print("Sess Key ACCEPTED:",  resp3[1])
    print("Post session, all is encrypted")

    # Session estabilished, try a simple command
    resp4 = hand.client(["hello",], conf.sess_key)
    print("Hello Response:", resp4[1])

    hand.client(["quit",],conf.sess_key)
    hand.close();

    sys.exit(0)

# EOF

