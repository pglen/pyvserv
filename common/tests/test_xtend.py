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
    err = thd.checkhash()
    assert err == True

    arrp = thd.powarr()
    err = thd.checkpow()
    assert err == True

    arrl = thd.linkarr(prevh)
    err = thd.checklink()
    assert err == True

    # Post link checks
    err = thd.checkpow()
    assert err == True

    err = thd.checkhash()
    assert err == True

    thd.datax[1] = 'aa'
    err = thd.checklink()
    assert err == False

# EOF


