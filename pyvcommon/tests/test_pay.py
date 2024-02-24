#!/usr/bin/env python3

import pytest, os, sys
#from mytest import *

# Set parent as module include path
base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base,  '..'))
sys.path.append(os.path.join(base,  '../../../pypacker'))

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

def test_func(capsys):

    # Hypothetical old hash
    prevh = pyvhash.shahex(b"1234")

    thd = pyvhash.BcData()

    thd.addpayload({1:1,2:2, "delx":99})

    thd.allarr(prevh)

    err = thd.checklink()
    assert err == True

    err = thd.checkpow()
    assert err == True

    #thd.delpayload("Default")
    thd.delpayload("delx")
    thd.delpayload(1)
    thd.delpayload(2)
    thd.addpayload({"Default":99})
    var = thd._getpayvar()
    #print(var)
    assert var == {'Default': 99}

    err = thd.checkpow()
    assert err == False

    thd.allarr(prevh)

    err = thd.checklink()
    assert err == True


# EOF


