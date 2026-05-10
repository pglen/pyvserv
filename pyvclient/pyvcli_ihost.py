#!/usr/bin/env python3

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, uuid

from Crypto import Random

# This repairs the path from local run to pip run.
try:
    from pyvcommon import support

    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    #print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))

except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    from pyvcommon import support

from pyvcommon import support, pycrypt, pyservsup, pyclisup, pyvhash
from pyvcommon import pysyslog, comline

import pyvpacker

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")
optarr = comline.optarrlong

#    ["c:",  "comm",     "",         None],      \
#    ["l:",  "login",    "admin",    None],      \
#    ["s:",  "lpass",    "1234",     None],      \
#    ["t",   "lprompt",  0,          None],      \
#    ["n:",  "numrec",   1,          None],      \
#    ["A:",  "addx",      "",        None],      \
#    ["D:",  "delx",      "",        None],      \
#    ["S",   "showx",     0,         None],      \

optarr.append ( ["c:",   "comm=",     "comm",       "",
                            None, "Communication."] )
optarr.append ( ["l:",   "login=",     "login",       "admin",
                            None, "User to use."] )
optarr.append ( ["s:",   "lpass=",     "lpass",       "1234",
                            None, "Pass t use."] )
optarr.append ( ["t:",   "lprompt=",     "lprompt",     0,
                            None, "Create user with prompt."] )
optarr.append ( ["n:",   "numrec=",     "numrec",       0,
                            None, "Pass t use."] )
optarr.append ( ["A:",   "addx=",     "addx",    "",
                            None, "Addx."] )
optarr.append ( ["D:",   "delx=",     "delx",    "",
                            None, "delx."] )
optarr.append ( ["S",   "showx",     "showx",    0,
                            None, "showx."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

    try:
        opts, args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print(sys.exc_info())
        sys.exit(1)

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if conf.lprompt:
        import getpass
        strx = getpass.getpass("Pass for login %s: " % conf.login)
        if not strx:
            print("Cannot login with empty pass, aborting ...")
            sys.exit(0)
        conf.lpass = strx

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

    if conf.verbose:
        resp3 = hand.client(["hello",] , "", False)
        print("Hello Resp:", resp3)

    #resp4 = hand.client(["tout", "30",], conf.sess_key)
    #print("Server tout Response:", resp4)

    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  conf.sess_key[:12], '...' )
    #print(" ----- Post session, all is encrypted ----- ")

    #resp4 = hand.client(["tout", "30",], conf.sess_key)
    #print("Server tout Response:", resp4)

    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("Server hello resp:", resp4[1])

    cresp = hand.login(conf.login, conf.lpass, conf)
    if cresp[0] != 'OK':
        print("Login Error:", cresp)
        sys.exit(0)

    cresp = hand.client(["dmode",], conf.sess_key)
    #print("dmode", cresp)
    if cresp[1] == '0':
        print("Enter twofa code: (ret to skip)", end = "")
        sesscode = input()
        if sesscode:
            cresp = hand.client(["twofa", sesscode], conf.sess_key)
            print ("Server twofa resp:", cresp)
            if cresp[0] != "OK":
                print ("Server twofa failed")
                sys.exit(0)

    if conf.showx:
        cresp = hand.client(["ihost", "list", "",], conf.sess_key)
    elif conf.addx:
        # Now the server will do it
        #if conf.addx.find(":") < 0:
        #    print("Missing ':' (colon). Entry must be in host:port format.")
        #    sys.exit(1)
        cresp = hand.client(["ihost", "add", conf.addx,], conf.sess_key)
    elif conf.delx:
        cresp = hand.client(["ihost", "del", conf.delx,], conf.sess_key)
    else:
       pass
       cresp = hand.client(["ihost", "add", "localhost:5555",], conf.sess_key)

    if not conf.quiet:
        print ("ihost resp:", end = " ")
    print (cresp)

    cresp = hand.client(["quit",],conf.sess_key)
    if conf.verbose:
        print ("Quit  Resp:", cresp)
    hand.close();

    sys.exit(0)

# EOF

