#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat, datetime, atexit, uuid

# This repairs the path from local run to pip run.
try:
    from pyvcommon import support
    base = os.path.dirname(os.path.realpath(support.__file__))
    sys.path.append(os.path.join(base, "."))
except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    from pyvcommon import support

from pyvcommon import support, pycrypt, pyclisup
from pyvcommon import pysyslog, comline, pyvhash, pyvgenr

import pyvpacker

# ------------------------------------------------------------------------
# Globals

packer = pyvpacker.packbin()

version = "1.0.0"
#progn = os.path.basename(sys.argv[0])
progn = os.path.basename(__file__)

cdoc = '''\
The pyvserv record manager.
Usage: %s [options] [hostname]
  hostname: host to connect to. (default: 127.0.0.1)
  options:   -d level  - Debug level 0-10
             -p        - Port to use (default: 6666)
             -l login  - Login Name; default: 'admin'
             -s lpass  - Login Pass; default: '1234' (for !!testing only!!)
             -t        - prompt for login pass")
             -a recpos - Get record by absolute pos. Negative for pos. from end
             -r recids - Record IDs to get
             -b date   - Start / Begin time. See format below. default:today
             -i mins   - Interval in minutes. (default: 1 day)
             -c        - Get records between specified dates
             -u        - Upload record (randomly generated)
             -o        - Count records in date range
             -z        - Get remote database size
             -v        - Verbose          -|-  -V        - Print version number
             -q        - Quiet            -|-  -h        - Help (this screen)
Use quotes for multiple arguments. (example: -a \"-1 -2 -3\" -- lists last 3)
Possible date Formats: 'Y-m-d+H:M' 'Y-m-d' 'm-d' 'm-d+H-M'  '''  \
% (progn)

__doc__= "<pre>" + cdoc + "</pre>"

# ------------------------------------------------------------------------

def phelp():
    ''' Present command line help '''
    print(cdoc)
    sys.exit(0)

def pversion():
    ''' Display Version information '''
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,          None],      \
    ["p:",  "port",     6666,       None],      \
    ["l:",  "login",    "admin",    None],      \
    ["s:",  "lpass",    "1234",     None],      \
    ["t",   "lprompt",  0,          None],      \
    ["v",   "verbose",  0,          None],      \
    ["q",   "quiet",    0,          None],      \
    ["u",   "upload",   0,          None],      \
    ["c",   "cget",     0,          None],      \
    ["z",   "size",    0,          None],       \
    ["r:",  "rget",     "",         None],      \
    ["a:",  "rabs",     "",         None],      \
    ["b:",  "begin",     "",        None],      \
    ["i:",  "inter",    0,          None],      \
    ["o",   "count",    0,          None],      \
    ["V",   None,       None,       pversion],  \
    ["h",   None,       None,       phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def    mainfunct():

    ''' Entry point for pip script '''

    try:
        args = conf.comline(sys.argv[1:])

    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        #print(sys.exc_info())
        sys.exit(1)

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    dd_beg, dd_end = pyclisup.inter_date(conf.begin, conf.inter)
    if conf.verbose:
        print("Date begin:", dd_beg, "Date end", dd_end)
    if conf.lprompt:
        import getpass
        strx = getpass.getpass("Pass for login %s: " % conf.login)
        if not strx:
            print("Cannot login with empty pass, aborting ...")
            sys.exit(0)
        conf.lpass = strx
    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    atexit.register(pyclisup.atexit_func, hand, conf)

    #ret = ["OK",];  conf.sess_key = ""
    ret = hand.start_session(conf)
    if ret[0] != "OK":
        print("Error on setting session:", resp3[1])
        hand.client(["quit"])
        hand.close();
        sys.exit(0)

    cresp = hand.login(conf.login, conf.lpass, conf)
    #print ("Server login response:", cresp)
    if cresp[0] != "OK":
        print("Error on logging in:", cresp)
        hand.client(["quit"], conf.sess_key)
        hand.close();
        sys.exit(0)

    if conf.upload:
        #actstr = ["register", "unregister", "cast", "uncast", ]
        #act = actstr[random.randint(0, len(actstr)-1)]
        pvh = pyvgenr.genvrec()
        pvh.hasharr()
        print("Calculating PROW ....", end = " "); sys.stdout.flush()
        while not pvh.powarr():
            pass
        print("OK")
        cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
        print ("rput resp:", cresp)

    elif conf.cget:
        import shlex
        shlex.split(conf.rget)
        cresp = hand.client(["rlist", "vote", dd_beg.timestamp(),
                         dd_end.timestamp()], conf.sess_key)

        if cresp[0] != "OK":
            print("Cannot get rlist", cresp)
        else:
            #print("cresp", cresp)
            for aaa in cresp[1]:
                cresp2 = hand.client(["rget", "vote", [aaa]], conf.sess_key)
                if cresp2[0] != "OK":
                    print("Cannot get record", cresp2)
                    continue
                #print("cresp2:", cresp2)
                for aa in cresp2[3]:
                    pyclisup.show_onerec(hand, aa, conf)
                    dec = packer.decode_data(aa[1])[0]
                    if conf.verbose:
                        print("dec:", dec)
                    else:
                        print("pay:", dec['PayLoad'])
            print("Listed", len(cresp[1]), "records.")

    elif conf.rabs:
        arrx = conf.rabs.split()
        #print("getting", arrx)
        cresp2 = hand.client(["rabs", "vote", *arrx], conf.sess_key)
        #print("rabs got:", cresp2)
        if cresp2[0] != "OK":
            print("Cannot get rabs:", cresp2)
            cresp = hand.client(["quit", ], conf.sess_key)
            sys.exit()
        for aa in cresp2[3]:
            #print("aa", aa)
            #pyclisup.show_onerec(hand, aa, conf)
            dec = packer.decode_data(aa[1])[0]
            if conf.verbose:
                print("dec:", dec)
            else:
                print("pay:", dec['PayLoad'])


        print("Listed", len(cresp2[3]), "records.")

    elif conf.count:
        cresp = hand.client(["rcount", "vote", dd_beg.timestamp(),
                         dd_end.timestamp()], conf.sess_key)

        #cresp = hand.client(["rcount", "vote"], conf.sess_key)
        print ("Server rcount response:", cresp)

    elif conf.size:
        cresp = hand.client(["rsize", "vote"], conf.sess_key)
        print ("Server rsize response:", cresp)

    elif conf.rget:
        arrx = conf.rget.split()
        print("getting", arrx)
        cresp2 = hand.client(["rget", "vote", arrx], conf.sess_key)
        #print("rabs got:", cresp2)
        if cresp2[0] != "OK":
            print("Error on rget:", cresp2)
            sys.exit()

        for aa in cresp2[3]:
            #print("aa", aa)
            #pyclisup.show_onerec(hand, aa, conf)
            dec = packer.decode_data(aa[1])[0]
            if conf.verbose:
                print("dec:", dec)
            else:
                print("pay:", dec['PayLoad'])
        print("Listed", len(cresp2[3]), "records.")
    else:
        # Get last record
        cresp = hand.client(["rsize", "vote"], conf.sess_key)
        #if not conf.quiet:
        #    print ("Server rsize response:", cresp)

        # Offset is one less than count
        cresp2 = hand.client(["rabs", "vote", cresp[1] - 1], conf.sess_key)
        #print ("Server rabs response:", cresp2)
        #pyclisup.show_onerec(hand, cresp2[3], conf)
        #print("cresp2[3]", cresp2[3])
        dec = packer.decode_data(cresp2[3][0][1])[0]
        if conf.verbose:
            print("dec:", dec)
        else:
            print("pay:", dec['PayLoad'])

    cresp = hand.client(["quit", ], conf.sess_key)
    #print ("Server quit response:", cresp)

if __name__ == '__main__':
    mainfunct()

# EOF
