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
    pass

def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    pass
    #assert 0

def test_func(capsys):

    thd = pyvhash.BcData()

    # Hypothetical old hash
    prevh = pyvhash.shahex(b"1234")

    arrh = thd.hasharr()
    ret = thd.checkhash()
    assert ret == True

    arrp = thd.powarr()
    ret = thd.checkpow()
    assert ret == True

    arrl = thd.linkarr(prevh)

    ret = thd.checklink()
    assert ret == True

    # Post link checks
    ret = thd.checkpow()
    assert ret == True

    ret = thd.checkhash()
    assert ret == True

    thd.addpayload({"Hello": 1234})

    ret = thd.checklink()
    assert ret == False

# EOF


