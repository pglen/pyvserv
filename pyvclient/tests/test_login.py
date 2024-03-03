#!/usr/bin/env python3

import pytest, os, sys, base64
from mytest import *

from pyvecc.Key import Key
from Crypto.Hash import SHA256
from Crypto import Random

hand = None
fname = createname(__file__)
iname = createidxname(__file__)

# ------------------------------------------------------------------------

def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    global hand

    start_server()
    try:
        # Fresh start
        os.remove(fname)
        os.remove(iname)
    except:
        #print(sys.exc_info())
        pass

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
        sys.exit(1)
        assert 0

    #print(hand)
    #assert 0

    org_sess_key = ""
    sess_key = session(hand, org_sess_key)

    resp = login(hand, sess_key)
    assert resp[0] == 'OK'

    resp5 = hand.client(["hello",], sess_key, False)
    #print("Hello encr:", resp5)
    assert resp5[0] ==  "OK"

    resp = hand.client(["quit"], sess_key)
    assert resp[0] == 'OK'


# EOF
