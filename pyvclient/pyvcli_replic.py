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

phelpstr = '''\
The pyvserv get / put replicator client.
Usage: %s [options] [sourcehost targethost]
  options:
    -d level  - Debug level 0-10
    -p        - Port to use for source server (default: 6666)
    -P        - Port to use for target server (default: 5555)
    -l login  - Login Name; Source server. default: 'admin'
    -s lpass  - Login Pass; (default: '1234') [for !!testing only!!]
    -L login2 - Login Name; Target server. (default: 'admin')
    -S lpass2 - Login Pass;  (default: '1234') [for !!testing only!!]
    -t        - Prompt for source server pass
    -T        - Prompt for target server pass
    -b time   - Begin time. Format: 'Y-m-d H:M' (default: now)
    -i time   - Interval in minutes. (default: 1 day)
    -y msec   - Delay after every operation. (default: 0.1 sec)
    -a        - Replicate all source server records. (may take long)
    -v        - Verbose. More info on screen.
    -q        - Quiet. Less info on screen.
    -h        - Help. (this screen)''' \
 % (os.path.basename(__file__))

__doc__ = "<pre>" + phelpstr + "</pre>"

def phelp():
    ''' Deliver help '''
    print(phelpstr)
    sys.exit(0)

def pversion():
    ''' Print version '''
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
    ["t",   "prompt",   0,          None],      \
    ["T",   "prompt2",  0,          None],      \
    ["b:",  "start",    "",         None],      \
    ["i:",  "inter",    0,          None],      \
    ["y:",  "delay",    0.1,        None],      \
    ["a",   "allrec",   0,          None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

conf = comline.Config(optarr)
conf2 = comline.Config(optarr)

def replicarr(count, hand, hand2):

    ''' Replicate from database count '''

    for aa in range(count):
        got = hand.client(["rabs", "vote", str(aa)], conf.sess_key)
        #print("got:", got)
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

        # Check if data is OK
        pvh = pyvhash.BcData(pay)
        if conf.pgdebug > 2:
            print(pvh.datax)
        if conf.pgdebug > 3:
            print("pvh checks:", pvh.checkhash(), pvh.checkpow())

        put = hand2.client(["rput", "vote", pay, ], conf2.sess_key)
        if put[0] != "OK":
            #print("put:", put)
            # Duplicate is normal
            if not "Duplicate" in put[1]:
                print("Error on put:", put)
        else:
            global replic
            replic += 1
            if not conf.quiet:
                print("replicated:", pay['header'])

        #print("delay:", conf.delay)
        time.sleep(conf.delay)


def scanall(hand, hand2):

    ''' Scan all data fron source server '''

    cresp = hand.client(["rsize", "vote",], conf.sess_key)
    #print ("Server  rsize response:", cresp)
    if cresp[0] != "OK":
        print("Cannot get records size")
        return

    replicarr(cresp[1], hand, hand2)


def scanfordays(handx, handx2):

    ''' Progressively dig down the timeline '''

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

                cresp = hand.client(["rcount", "vote", dd_beg.timestamp(),
                                        dd_end.timestamp()], conf.sess_key)
                if cresp[1] > 0:
                    print(" from:", dd_beg, "to:", dd_end);
                    print("Server rcount response:", cresp)
                    cresp2 = hand.client(["rlist", "vote", dd_beg.timestamp(),
                                        dd_end.timestamp()], conf.sess_key)
                    #print(" Server rlist response:", cresp2)
                    for aa in cresp2[1]:
                        print("rr:", aa)
                        crespr = hand.client(["rget", "vote", aa], conf.sess_key)
                        if cresp[0] == "OK":
                            print("rget", crespr)
                            #print("aa", aa)
                            dec = hand.pb.decode_data(aa[1])[0]
                            #print("dec", dec)
                            print(dec['header'], dec['payload'])
           # Get


        #if cresp[1] > 100:
        #    #print("record with more", cresp[1])
        #    pass

        dayx += 1
        # We end one day late to include all timezone deviations
        if dayx >= maxdays + 1:
            break

# Scan which hours of days that have records
def scanhours(dayx):

    ''' Progressively dig down the timeline, per hour '''

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

    ''' Progressively dig down the timeline per minute '''

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

def    mainfunct():

    ''' Called by the SETUP script '''

    try:
        args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print(sys.exc_info())
        sys.exit(1)

    # Convert to seconds for sleep
    #Mon 15.Apr.2024 added float to comline
    #conf.delay = conf.delay / 1000

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

    atexit.register(pyclisup.atexit_func, hand, conf)
    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session on source:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    #resp3 = hand.client(["hello", ],  conf.sess_key, False)
    #print("Hello  Resp:", resp3)

    hand2 = pyclisup.CliSup()
    hand2.verbose = conf.verbose
    hand2.pgdebug = conf.pgdebug

    try:
        respc = hand2.connect(ip2, conf.port2)
    except:
        print( "Cannot connect to second server:", ip2 + ":" + str(conf.port2), sys.exc_info()[1])
        sys.exit(1)

    atexit.register(pyclisup.atexit_func, hand2, conf2)

    ret2 = hand2.start_session(conf2)
    if ret2[0] != "OK":
        print("Error on setting session on target:", ret2[1])
        hand2.client(["quit"])
        hand2.close();
        sys.exit(0)

    #resp3 = hand2.client(["hello", ],  conf2.sess_key, False)
    #print("Hello2 Resp:", resp3)

    if conf.prompt:
        import getpass
        strx = getpass.getpass("Enter Pass for source server: ")
        if not strx:
            print("Aborting ...")
            sys.exit(0)
        conf.lpass  = strx

    cresp = hand.login(conf.login, conf.lpass, conf)
    #print ("Server login response:", cresp)
    if cresp[0] != "OK":
        print("Cannot login to server", cresp)
        sys.exit(0)

    if conf.verbose:
        print ("Server login response:", cresp)

    if conf.prompt2:
        import getpass
        strx = getpass.getpass("Enter Pass for target server: ")
        if not strx:
            print("Aborting ...")
            sys.exit(0)
        conf.lpass2  = strx

    cresp = hand2.login(conf.login2, conf.lpass2, conf2)
    if cresp[0] != "OK":
        print("Cannot login to server2", cresp)
        sys.exit(0)

    if conf.verbose:
        print ("Server2 login response:", cresp)

    cresp = hand.client(["rsize", "vote",], conf.sess_key)
    if not conf.quiet:
        print ("Server  rsize response:", cresp)

    cresp2 = hand2.client(["rsize", "vote",], conf2.sess_key)
    if not conf.quiet:
        print ("Server2 rsize response:", cresp2)

    if conf.allrec:
        scanall(hand, hand2)
    else:
        scanfordays(hand, hand2)

    print("Replicated", replic, "record(s).")

if __name__ == '__main__':
    mainfunct()

# EOF
