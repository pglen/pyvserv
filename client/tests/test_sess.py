#!/usr/bin/env python3

import pytest, os, sys

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

from mytest import *

# Set parent as module include path
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from common import support, pycrypt, pyservsup, pyclisup
from common import pysyslog, comline, pypacker

hand = None
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

    respx = hand.client(["hello",] , "", False)

    resp = hand.client(["akey"])
    assert resp[0] == 'OK'

    hhh = SHA512.new(); hhh.update(resp[2])

    # Remember key
    if hhh.hexdigest() != resp[1]:
        print("Tainted key, aborting.")
        hand.client(["quit"])
        hand.close();
        assert 0

    hhh = SHA512.new(); hhh.update(resp[2])
    ddd = hhh.hexdigest()
    assert ddd  == resp[1]

    try:
        hand.pubkey = RSA.importKey(resp[2])
    except:
        print("Cannot import public key.")
        support.put_exception("import key")
        print ("cipher", cipher.can_encrypt())
        hand.client(["quit"])
        hand.close();
        assert 0

    cipher = PKCS1_v1_5.new(hand.pubkey)

    # Generate communication key
    sess_key = Random.new().read(512)
    sss = SHA512.new(); sss.update(sess_key)

    sess_keyx = cipher.encrypt(sess_key)
    ttt = SHA512.new(); ttt.update(sess_keyx)

    resp3 = hand.client(["sess", sss.hexdigest(), ttt.hexdigest(), sess_keyx], "", False)
    assert resp3[0] ==  "OK"

    resp = hand.client(["quit",], sess_key)
    hand.close()

    assert resp[0] == 'OK'


# EOF
