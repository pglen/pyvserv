#!/usr/bin/env python3

import pytest, os, sys #, syslog
from mytest import *

from Crypto.Cipher import AES

hand = None
fname = createname(__file__)
iname = createidxname(__file__)

fname = "test.txt"
fname2 = "test.txt_local"
sess_key = ""

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

    global ip, hand

    ip = '127.0.0.1'
    hand = pyclisup.CliSup()

    try:
        resp2 = hand.connect(ip, 6666)
    except:
        #support.put_exception("On connect")
        print( "Cannot connect to:", ip + ":" , sys.exc_info()[1])
        assert 0

    org_sess_key = ""
    global sess_key
    sess_key = session(hand, org_sess_key)

    # Make sure admin is present
    resp5 = hand.client(["uini", "admin", "1234"], sess_key, False)
    print("uini:", resp5)
    #assert resp5[0] ==  "OK"

    resp = login(hand, sess_key)
    assert resp[0] == 'OK'

    resp5 = hand.client(["hello",], sess_key, False)
    #print("Hello encr:", resp5)
    assert resp5[0] ==  "OK"

    fp = open(fname, "wb")
    fp.write(b"Test Data" * 10)
    fp.close()

    resp = hand.client(["fput", fname], sess_key)
    print ("fput response:", resp)
    assert resp[0] ==  "OK"

    fp = open(fname, "rb")
    while 1:
        try:
            buf = fp.read(1024)
            #print("sending", buf)
            dstr = hand.wrapx(buf, sess_key)
            hand.sendx(dstr)
            if len(buf) == 0:
                break
        except:
            resp =  ["ERR", "Cannot send", sys.exc_info()]
            break

    resp = hand.recvx(sess_key)
    print ("fput transfer:", resp)

def test_get(capsys):

    global sess_key
    # --------------------------------------------------------------------
    # Get back the same file

    ret2 = hand.getfile(fname, fname2, sess_key)
    print ("fget transfer:", ret2)

    buff1 = open(fname, 'rb').read()
    buff2 = open(fname2, 'rb').read()
    assert buff1 == buff2

    try:
        os.remove(fname); os.remove(fname2)
    except:
        pass

    resp = hand.client(["hello"], sess_key)
    print ("Hello encr:", resp);

    hand.client(["quit"], sess_key)
    assert resp[0] == 'OK'


# EOF
