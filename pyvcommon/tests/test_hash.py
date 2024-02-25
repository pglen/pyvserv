#!/usr/bin/env python3

import pytest, os, sys
#from mytest import *

# Set parent as module include path
base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base,  '../pyvcommon'))

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

    thd = pyvhash.BcData()

    #print(arrx2)
    err = thd.checkhash()
    #print("unhashed match:", err)
    assert err == False

    arrh = thd.hasharr()
    err = thd.checkhash()
    assert err == True

    arrh2 = thd.hasharr()
    #print("Modified: (ucase H)")
    arrh2[1] = "Hello"
    err = thd.checkhash()
    assert err == False

# EOF


