#!/usr/bin/env python3

import pytest, os, sys, subprocess, time, datetime, uuid

from mytest import *

hand = None
fname = createname(__file__)
iname = createidxname(__file__)

from pyvguicom import pgtests

import pyvhash

actstr = ["register", "unregister", "cast", "uncast", ]
act = actstr[random.randint(0, len(actstr)-1)]

# ------------------------------------------------------------------------

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global hand
    try:
        # Fresh start
        os.remove(fname)
        os.remove(iname)
    except:
        #print(sys.exc_info())
        pass
    start_server()

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    try:
        # No dangling data
        #os.remove(fname)
        #os.remove(iname)
        pass
    except:
        #print(sys.exc_info())
        #assert 0
        pass
    #stop_server()
    #assert 0

def test_func(capsys):

    global ip

    #ip = "192.168.1.22"
    ip = '127.0.0.1'
    hand = pyclisup.CliSup()

    try:
        resp2 = hand.connect(ip, 6666)
    except:
        #support.put_exception("On connect")
        print( "Cannot connect to:", ip + ":" , sys.exc_info()[1])
        #sys.exit(1)
        assert 0

    resp = hand.client(["hello"])
    #print ("Server response:", resp); assert 0
    assert resp[0] == 'OK'

    class Blank(): pass;
    conf = Blank()

    ret = hand.start_session(conf)

    cresp = login(hand, conf.sess_key, "admin", "1234")
    #print("pass %.3fms" % ((time.time() - ttt) * 1000) )
    print ("Server pass resp:", cresp)
    if cresp[0] != "OK":
        resp5 = hand.client(["uini", "admin", "1234", ], conf.sess_key, False)
        print("uini resp:", resp5)
        cresp = login(hand, conf.sess_key, "admin", "1234")
        print ("Server pass resp:", cresp)
        if cresp != "OK":
            print("Cannot log on", cresp)
            sys.exit(1)

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
                sys.exit(1)

    # Get some back
    dd = datetime.datetime.now()
    dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)

    dd_beg = dd + datetime.timedelta(0)
    dd_end = dd_beg + datetime.timedelta(1)
    print("from:", dd_beg, "to:", dd_end);

    cresp = hand.client(["rlist", "vote", dd_beg.timestamp(),
                         dd_end.timestamp()], conf.sess_key)

    print ("Server rlist response:", cresp)

    if cresp[0] != "OK" or len(cresp[1]) < 1:
        # Put one, if none exist
        pvh = pyvhash.BcData()
        pvh.addpayload({'nuuid': str(uuid.uuid1()) })
        pvh.addpayload({'name': pgtests.simname(12) })
        pvh.addpayload({'ndob': pgtests.randate() })
        pvh.addpayload({'nnow': pgtests.randisodate() })
        pvh.addpayload({'noper': pgtests.randstr(random.randint(6, 22)) })
        pvh.addpayload({'uuid':  str(uuid.uuid1()) })
        pvh.addpayload({'vguid': str(uuid.uuid1()) })
        pvh.addpayload({'vouid': str(uuid.uuid1()) })
        pvh.hasharr()
        pvh.powarr()

        cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
        print ("Server rput response:", cresp)
        assert cresp[0] == 'OK'

        cresp = hand.client(["rlist", "vote", dd_beg.timestamp(),
                             dd_end.timestamp()], conf.sess_key)
        #print ("Server  rlist response:", cresp)

    cresp = hand.client(["rget", "vote", cresp[1]], conf.sess_key)
    #print ("Server rget response:", cresp)
    assert cresp[0] == 'OK'
    #print("cresp:", cresp)

    dec = hand.pb.decode_data(cresp[3][0][1])[0]
    #print("dec:", dec)
    print("pay:", dec['PayLoad'])

    #pay = hand.pb.decode_data(dec['payload'])[0]
    #print("pay:", pay['PayLoad'])

    # See if we uuid
    assert dec['PayLoad']['uuid'] != None

    resp = hand.client(["quit"], conf.sess_key)
    hand.close()
    #assert resp[0] == 'OK'

    #assert 0

# EOF
