#!/usr/bin/env python3

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

#optarr = \
#    ["c:",  "comm",     "",     None],      \
#    ["s",   "showkey",  "",     None],      \
#    ["t",   "test",     "x",    None],      \

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")

optarr = []
optarr.append ( ["c:",   "comm",     "comm",       "",
                            None, "Print time statistics."] )

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

    resp3 = hand.client(["hello", "world"] , "", False)
    print("Hello Response: ", resp3)

    ret = hand.start_session(conf)

    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    print("Sess Key ACCEPTED:",  conf.sess_key[:12], '...' )
    #print("Post session, all is encrypted")

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

