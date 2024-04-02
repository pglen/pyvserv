#!/usr/bin/env python3

import pytest, os, sys, subprocess, time, datetime, uuid
from mytest import *

hand = None
fname = createname(__file__)
iname = createidxname(__file__)

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

    # Pre - generated for speed
    bbb = \
    {'header': 'bb5e117e-de0f-11ee-bb2d-0b98efd166b2',
        'payload': {'Default': 'None'},
        '_Hash': 'c14bda859bdebf5b87bd9d852bb4074ae825b64113d80feda5f988790f2693a5',
         '_PowRand': b'\x170<\x9bz\x7f\xca\xf6\xb8t\\\xd8',
         '_Proof': '0c707fed756a318029db92859d1f0d78782c822a949b51d926b577d85156a000'}

    pvh = pyvhash.BcData(bbb)

    #pvh.hasharr();  pvh.powarr()
    #print(pvh.datax)
    #assert 0

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

    class Blank(): pass
    conf = Blank()

    ret = hand.start_session(conf)

    cresp = hand.client(["user", "admin"], conf.sess_key)
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

    # Put one
    pvh = pyvhash.BcData()
    pvh.addpayload({"Vote": random.randint(0, 10), "UID":  str(uuid.uuid1()), })
    pvh.addpayload({"SubVote": random.randint(0, 10), "TUID":  str(uuid.uuid1()), })
    pvh.addpayload({"Action": act , "RUID":  str(uuid.uuid1()), })
    pvh.hasharr();  pvh.powarr()
    cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
    print ("Server rput response:", cresp)
    assert cresp[0] == 'OK'

    # Get some back
    dd = datetime.datetime.now()
    dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)

    dd_beg = dd + datetime.timedelta(0)
    dd_end = dd_beg + datetime.timedelta(1)
    print("from:", dd_beg, "to:", dd_end);

    cresp = hand.client(["rlist", "vote", dd_beg.timestamp(),
                         dd_end.timestamp()], conf.sess_key)
    #print ("Server  rlist response:", cresp)

    cresp = hand.client(["rget", "vote", cresp[1]], conf.sess_key)
    #print ("Server rget response:", cresp)
    assert cresp[0] == 'OK'
    #print(cresp)

    dec = hand.pb.decode_data(cresp[1][0][1])
    #print("dec:", dec[0]['header'], dec[0]['now'], dec[0]['payload'])
    #print("dec:", dec)

    # See if we have a vote int there
    assert dec[0]['payload']['Vote'] != ""

    resp = hand.client(["quit"], conf.sess_key)
    hand.close()
    assert resp[0] == 'OK'

    #assert 0

# EOF
