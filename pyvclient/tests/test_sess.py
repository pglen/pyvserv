#!/usr/bin/env python3

import pytest, os, sys, base64

from pyvecc.Key import Key
from Crypto.Hash import SHA256
from Crypto import Random

from mytest import *

hand = None
sess_key = ""
fname = createname(__file__)
iname = createidxname(__file__)

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

    #assert 0

def test_func(capsys):

    global ip

    #ip = "192.168.1.22"
    ip = '127.0.0.1'
    global hand
    hand = pyclisup.CliSup()

    try:
        resp2 = hand.connect(ip, 6666)
    except:
        #support.put_exception("On connect")
        print( "Cannot connect to:", ip + ":" , sys.exc_info()[1])
        assert 0

    #print(hand)
    #assert 0

    resp = hand.client(["hello",] , "", False)
    print("Hello plain:", resp)
    assert resp[0] == 'OK'

    global sess_key
    sess_key = session(hand, sess_key)
    print("Sess key", sess_key[:24], "...")

    resp5 = hand.client(["hello",], sess_key, False)
    print("Hello crypt3", resp5)
    assert resp5[0] ==  "OK"

    #assert 0

def test_sec_sess():

    global hand, sess_key

    # Generate communication key2
    sess_key2 = session(hand, sess_key)
    print("Sess key", sess_key[:24], "...")

    resp5 = hand.client(["hello",], sess_key2, False)
    print("Hello (encrypted3) Response:", resp5[1])
    assert resp5[0] ==  "OK"

    resp = hand.client(["quit",], sess_key2)

    assert resp[0] == 'OK'

# EOF
