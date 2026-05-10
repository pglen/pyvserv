#!/usr/bin/env python

# ------------------------------------------------------------------------
# Test client for the pyserv project. User change pass.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..' + os.sep + 'pyvcommon'))

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline

comline.cpm.setprog(os.path.basename(__file__))
comline.cpm.setver(pyclisup.VERSION)
comline.cpm.setargs("[options] [hostname]")
comline.cpm.setfoot("The hostname defaults to 'localhost'")

optarr = comline.optarrlong
#optarr.append ( ["l:",   "login=",     "login",       "admin",
#                            None, "User to use."] )
#optarr.append ( ["s:",   "lpass=",     "lpass",       "1234",
#                            None, "Pass t use."] )
#optarr.append ( ["x:",   "comm=",     "comm",    "",
#                            None, "comm."] )
#optarr.append ( ["t:",   "prompt=",     "prompt",       0,
#                            None, "Create user with prompt."] )
conf = comline.ConfigLong(optarr)
conf.sess_key = ""

# ------------------------------------------------------------------------

if __name__ == '__main__':

    opts, args = conf.comline(sys.argv[1:])

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

    resp3 = hand.client(["hello",] , "", False)
    if not conf.quiet:
        print("Hello Response:", resp3)

    resp3 = hand.start_session(conf)
    if not conf.quiet:
        print("Sess Response:", resp3)

    resp = hand.client(["user", "admin"], conf.sess_key)
    if not conf.quiet:
        print("user Response:", resp)

    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        raise ValueError("No user", resp[1])

    resp = hand.client(["pass", "1234"], conf.sess_key)
    if not conf.quiet:
        print("pass Response:", resp)

    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        #raise ValueError("Not authorized", resp[1])
        print("Not authorized.")
        sys.exit(0)

    if resp[0] != "OK":
        hand.client(["quit"], conf.sess_key)
        hand.close();
        raise ValueError("Not authorized", resp[1])

    resp = hand.client(["udel", "test_admin", "1234"], conf.sess_key)
    if not conf.quiet:
        print("udel Response:", resp)
    pyclisup.expect(resp[0], "ERR", context = "udel test_admin")

    resp = hand.client(["aadd", "test_admin", "1234"], conf.sess_key)
    if not conf.quiet:
       print("aadd Response:", resp)
    pyclisup.expect(resp[0], "OK", context = "aadd test_admin")

    resp = hand.client(["udel", "test_user", "1234"], conf.sess_key)
    if not conf.quiet:
        print("udel Response:", resp)
    pyclisup.expect(resp[0], "ERR", context = "udel test_user")

    resp = hand.client(["uadd", "test_user", "1234"], conf.sess_key)
    if not conf.quiet:
        print("uadd Response:", resp)

    resp = hand.client(["logout",], conf.sess_key)
    if not conf.quiet:
        print("logout Response:", resp)

    resp = hand.login("test_user", "1234", conf)
    if not conf.quiet:
        print("login Response:", resp)
    pyclisup.expect(resp[0], "OK", context = "login test_user")

    resp = hand.client(["chpass", "test_user", "1234", "12345"], conf.sess_key)
    if not conf.quiet:
        print("chpass Response:", resp)
    pyclisup.expect(resp[0], "OK", context = "chpass test_user")

    # Login with the newly modified user
    resp = hand.client(["logout",], conf.sess_key)
    if not conf.quiet:
        print("logout Response:", resp)

    resp = hand.login("test_user", "12345", conf)
    if not conf.quiet:
        print("login Response:", resp)
    pyclisup.expect(resp[0], "OK", context = "login test_user")

    resp3 = hand.client(["hello",] , conf.sess_key, False)
    if not conf.quiet:
        print("Hello Response:", resp3)

    resp = hand.client(["logout",], conf.sess_key)
    if not conf.quiet:
        print("logout Response:", resp)

    resp = hand.login("test_admin", "1234", conf)
    if not conf.quiet:
        print("login Response:", resp)
    pyclisup.expect(resp[0], "OK", context = "login test_admin")

    resp = hand.client(["chpass", "test_admin", "1234", "12345"], conf.sess_key)
    if not conf.quiet:
        print("chpass Response:", resp)
    pyclisup.expect(resp[0], "OK", context = "chpass test_admin")

    resp = hand.client(["logout",], conf.sess_key)
    if not conf.quiet:
        print("logout Response:", resp)
    pyclisup.expect(resp[0], "OK", context = "logout test_admin")

    resp = hand.login("test_admin", "12345", conf)
    if not conf.quiet:
        print("login test_admin Response:", resp)
    pyclisup.expect(resp[0], "OK", context = "login test_admin")

    resp = hand.client(["udel", "test_user", "1234"], conf.sess_key)
    if not conf.quiet:
        print("udel Response:", resp)
    pyclisup.expect(resp[0], "OK")

    resp = hand.client(["udel", "test_admin", "1234"], conf.sess_key)
    if not conf.quiet:
        print("udel Response:", resp)
    pyclisup.expect(resp[0], "OK")

    hand.client(["quit"], conf.sess_key)
    hand.close();

    sys.exit(0)

# EOF
