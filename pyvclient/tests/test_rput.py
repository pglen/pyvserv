#!/usr/bin/env python3

import pytest, os, sys, subprocess, time, uuid
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

    pvh = pyvhash.BcData()
    pvh.addpayload({"Vote": random.randint(0, 10), "UID":  str(uuid.uuid1()), })
    pvh.addpayload({"SubVote": random.randint(0, 10), "TUID":  str(uuid.uuid1()), })
    pvh.addpayload({"Action": act , "RUID":  str(uuid.uuid1()), })
    pvh.addpayload({"TEST": "Do NOT use", })
    pvh.hasharr();  pvh.powarr()

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

    #ttt = time.time()
    cresp = hand.client(["pass", "1234"], conf.sess_key)
    #print("pass %.3fms" % ((time.time() - ttt) * 1000) )
    print ("Server pass resp:", cresp)
    assert cresp[0] == 'OK'

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

    cresp = hand.client(["rput", "vote", pvh.datax], conf.sess_key)
    print ("Server rput response:", cresp)
    assert cresp[0] == 'OK'

    qresp = hand.client(["quit"], conf.sess_key)
    hand.close()
    assert qresp[0] == 'OK'

    #assert 0

# EOF
