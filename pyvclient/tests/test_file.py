#!/usr/bin/env python3

import pytest, os, sys, syslog
from mytest import *

from Crypto.Cipher import AES

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

    org_sess_key = ""
    sess_key = session(hand, org_sess_key)

    resp = login(hand, sess_key)
    assert resp[0] == 'OK'

    resp5 = hand.client(["hello",], sess_key, False)
    #print("Hello encr:", resp5)
    assert resp5[0] ==  "OK"

    fname = "test_data/test.txt"
    fp = open(fname, "wb")
    fp.write(b"Test Data" * 10)
    fp.close()

    resp = hand.client(["fput", "test.txt"], sess_key)
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

    # --------------------------------------------------------------------
    # Get back the same file

    resp = hand.client(["fget", "test.txt"], sess_key)
    print ("fget response:", resp)
    assert resp[0] ==  "OK"

    fname2 = "test_data/test.txt_local"

    fh = open(fname2, 'wb')

    fsize = int(resp[1])
    cipher = AES.new(sess_key[:32], AES.MODE_CTR, use_aesni=True, nonce=sess_key[-8:])
    while(True):
        response = hand.myhandler.handle_one(hand.mydathand)
        if not response:
            break
        response = cipher.encrypt(response)
        try:
            fh.write(response)
        except:
            print( "Cannot write to local file: '" + fname2 + "'", sys.exc_info())
            cresp = [ERR,"Cannot write local file",]
            break
        fsize -= len(response)
        if fsize <= 0:
            break
    fh.close()

    resp = hand.recvx(sess_key)
    print ("fget transfer:", resp)

    buff1 = open(fname, 'rb').read()
    buff2 = open(fname2, 'rb').read()

    assert buff1 == buff2

    resp = hand.client(["hello"], sess_key)
    print ("Hello encr:", resp);

    hand.client(["quit"], sess_key)
    assert resp[0] == 'OK'


# EOF
