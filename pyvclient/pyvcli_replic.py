#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat, datetime, atexit

# This repairs the path from local run to pip run.

try:
    from pyvcommon import support
    #print("sf", sf)
    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
except:
    #print("pathching")
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    from pyvcommon import support

import support, pycrypt, pyservsup, pyclisup
import pysyslog, comline, pyvhash

hand = None
hand2 = None
replic = 0

# ------------------------------------------------------------------------
# Globals

version = "1.0.0"

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 6666)")
    print( "            -P        - Second server port to use (default: 5555)")
    print( "            -l login  - Login Name; default: 'admin'")
    print( "            -s lpass  - Login Pass; default: '1234' (for !!testing only!!)")
    print( "            -L login2 - Login Name; Second server. default: 'admin'")
    print( "            -S lpass2 - Login Pass; Second server. default: '1234' ")
    print( "            -b        - Begin time. Format: 'Y-m-d H:M' Default: now")
    print( "            -i        - Interval in minutes. (Default: 1 day)")
    print( "            -a        - Replicate all records. See notes.")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
    ["P:",  "port2",    5555,       None],      \
    ["l:",  "login",    "admin",    None],      \
    ["s:",  "lpass",    "1234",     None],      \
    ["L:",  "login2",   "admin",    None],      \
    ["S:",  "lpass2",   "1234",     None],      \
    ["b:",  "start",     "",        None],      \
    ["i:",  "inter",    0,          None],      \
    ["a",   "all",      0,          None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

conf = comline.Config(optarr)
conf2 = comline.Config(optarr)

def scanall(hand, hand2):
    cresp = hand.client(["rsize", "vote",], conf.sess_key)
    #print ("Server  rsize response:", cresp)
    if cresp[0] != "OK":
        print("Cannot get records size")
        return

    for aa in range(cresp[1]):
        got = hand.client(["rabs", "vote", str(aa)], conf.sess_key)
        #print("got:", got[3])
        if got[0] != "OK":
            print("error:", got)
            continue

        dec = hand.pb.decode_data(got[3][0][1])[0]
        if conf.pgdebug > 3:
            print("dec:", dec)
        pay = hand.pb.decode_data(dec['payload'])[0]
        #print("pay:", pay['PayLoad'])
        if conf.pgdebug > 2:
            print("payload:", pay)
        if conf.pgdebug > 1:
            print("pay:", pay['PayLoad'])

        put = hand2.client(["rput", "vote", pay, ], conf2.sess_key)
        if put[0] != "OK":
            #print("put:", put)
            # Duplicate is normal
            if not "Duplicate" in put[1]:
                print("on put:", put)
        else:
            global replic
            replic += 1
            if not conf.quiet:
                print("replicated:", pay['header'])


def scanfordays(handx, handx2):

    global hand, hand2
    hand    = handx
    hand2   = handx2

    # Set beginning date range
    dd = datetime.datetime.now()
    dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)

    maxdays = 5; dayx = 0

    dd = datetime.datetime.now()
    dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)
    dd = dd - datetime.timedelta(maxdays)

    # Scan which days have records
    while True:
        dd_beg = dd + datetime.timedelta(dayx)
        dd_end = dd_beg + datetime.timedelta(1)

        cresp = hand.client(["rcount", "vote", dd_beg.timestamp(),
                                        dd_end.timestamp()], conf.sess_key)
        if cresp[1] > 0:
            print("from:", dd_beg, "to:", dd_end);
            print ("Server rcount response:", cresp)

            if cresp[1] >= 100:
                scanhours(maxdays - dayx)
            else:
                print("getting day:", dd_beg, "-", dd_end)

        #if cresp[1] > 100:
        #    #print("record with more", cresp[1])
        #    pass

        dayx += 1
        # We end one day late to include all timezone deviations
        if dayx >= maxdays + 1:
            break

# Scan which hours of days that have records
def scanhours(dayx):

    # Set beginning date range
    dd = datetime.datetime.now()
    dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)
    dd = dd - datetime.timedelta(dayx)

    maxhours = 24; hourx = 0

    while True:
        dd_beg = dd + datetime.timedelta(0, hourx * 3600)
        dd_end = dd_beg + datetime.timedelta(0, 1 * 3600)

        cresp = hand.client(["rcount", "vote", dd_beg.timestamp(),
                                        dd_end.timestamp()], conf.sess_key)
        if cresp[1] > 0:
            print(" from:", dd_beg, "to:", dd_end);
            print(" Server hour rcount response:", cresp)
            if cresp[1] >= 100:
                scanminutes(dayx, hourx)
            else:
                print(" getting hour:", dd_beg, " - ", dd_end)
                cresp = hand.client(["rlist", "vote", dd_beg.timestamp(),
                                    dd_end.timestamp()], conf.sess_key)
        hourx += 1
        if hourx > maxhours:
            break

def scanminutes(dayx, hourx):

    # Set beginning date range
    dd = datetime.datetime.now()
    dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)
    dd = dd - datetime.timedelta(dayx)
    dd = dd + datetime.timedelta(0, hourx * 3600)

    maxmins = 60; minx = 0

    while True:
        dd_beg = dd + datetime.timedelta(0, minx * 60)
        dd_end = dd_beg + datetime.timedelta(0, 60)

        cresp = hand.client(["rcount", "vote", dd_beg.timestamp(),
                                        dd_end.timestamp()], conf.sess_key)
        if cresp[1] > 0:
            print("    from:", dd_beg, "to:", dd_end);
            print("    Server min  rcount response:", cresp)

            if cresp[1] >= 100:
                print("    ----------- big rec count")
            else:
                #print("    getting minutes:", dd_beg, "-", dd_end)
                cresp = hand.client(["rlist", "vote", dd_beg.timestamp(),
                                    dd_end.timestamp()], conf.sess_key)
                if cresp[0] == "OK":
                    crespr = hand.client(["rget", "vote", cresp[1]], conf.sess_key)
                    #print("rget", crespr)
                    for aa in crespr[1]:
                        #print("aa", aa)
                        dec = hand.pb.decode_data(aa[1])[0]
                        #print("dec", dec)
                        print(dec['header'], dec['payload'])

                    #for aa in cresp[1]:
                    #    #print("head", aa)
                    #    #crespg = hand2.client(["rhave", "vote", aa], conf2.sess_key)
                    #    #print("rhave", crespg)
                    #    if 1: #crespg[0] != "OK":
                    #        crespr = hand.client(["rget", "vote", aa], conf.sess_key)
                    #        #print("Rec", crespr[1])
                    #        cresp3 = hand2.client(
                    #                ["rput", "vote", crespr[1][0], ], conf2.sess_key)
                    #        if cresp3[0] == 'OK':
                    #            print("rput", cresp3)
                #print(cresp)

        minx += 1
        if minx > maxmins:
            break

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
        ip2 = '127.0.0.1'
    elif len(args) == 1:
        print("Must specify second server for replication.")
        sys.exit()
    else:
        ip = args[0]
        ip2 = args[1]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    hand2 = pyclisup.CliSup()
    hand2.verbose = conf.verbose
    hand2.pgdebug = conf.pgdebug

    atexit.register(pyclisup.atexit_func, hand, conf)

    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    #resp3 = hand.client(["hello", ],  conf.sess_key, False)
    #print("Hello  Resp:", resp3)

    try:
        respc = hand2.connect(ip, conf.port2)
    except:
        print( "Cannot connect to second server:", ip2 + ":" + str(conf.port2), sys.exc_info()[1])
        sys.exit(1)

    atexit.register(pyclisup.atexit_func, hand2, conf2)

    ret2 = hand2.start_session(conf2)
    if ret2[0] != "OK":
        print("Error on setting session2:", ret2[1])
        hand2.client(["quit"])
        hand2.close();
        sys.exit(0)

    #resp3 = hand2.client(["hello", ],  conf2.sess_key, False)
    #print("Hello2 Resp:", resp3)

    cresp = hand.login(conf.login, conf.lpass, conf)
    #print ("Server login response:", cresp)
    if cresp[0] != "OK":
        print("Cannot login to server", cresp)
        sys.exit(0)

    if conf.verbose:
        print ("Server  login response:", cresp)

    cresp = hand.client(["rsize", "vote",], conf.sess_key)
    if not conf.quiet:
        print ("Server  rsize response:", cresp)

    cresp = hand2.login(conf.login2, conf.lpass2, conf2)
    if cresp[0] != "OK":
        print("Cannot login to server2", cresp)
        sys.exit(0)

    if conf.verbose:
        print ("Server2 login response:", cresp)

    cresp2 = hand2.client(["rsize", "vote",], conf2.sess_key)
    if not conf.quiet:
        print ("Server2 rsize response:", cresp2)

    if conf.all:
        scanall(hand, hand2)
    else:
        scanfordays(hand, hand2)

    print("Replicated", replic, "records.")

# EOF
