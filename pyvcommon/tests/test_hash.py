#!/usr/bin/env python3

import pytest, os, sys
#from mytest import *

# Set parent as module include path
base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base,  '../../pyvcommon'))

import pyvhash
hand = None

#fname = createname(__file__)
#iname = createidxname(__file__)

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

    global thd
    thd = pyvhash.BcData()

    #print("unhashed match:", ret)
    assert False == thd.checkhash()

    thd.hasharr()
    assert True == thd.checkhash()

    thd.hasharr()
    assert True == thd.checkhash()

    #print(thd.datax)
    assert thd.datax['payload'] != None

    assert thd.checkhash() == True

    #print(thd.datax)

def test_modulate(capsys):

    print(thd.datax)
    pvh2 = pyvhash.BcData(thd)
    assert pvh2.checkhash() == True

    pvh2.addpayload({"Added New": "new stuff"})
    print(pvh2.datax)

    assert pvh2.checkhash() == False

    pvh2.hasharr()

    assert pvh2.checkhash() == True
    assert thd.checkhash() == True

def test_paydel(capsys):

    return

    delkey = "May Delete"
    pvh2 = pyvhash.BcData(thd)
    pvh2.addpayload({"Added New": "new stuff again"})
    pvh2.addpayload({delkey: "deletable stuff"})
    #print(pvh2.datax)

    assert pvh2._getpayvar()[delkey] != None
    pvh2.delpayload(delkey)
    #print(pvh2._getpayvar())

    # Test for raised exception
    exc = False
    try:
        ddd = pvh2._getpayvar()[delkey]
    except:
        print(sys.exc_info())
        exc = True

    assert exc == True

# EOF

