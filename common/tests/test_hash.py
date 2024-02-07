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

    arrx =  [123, "hello", {"Hash":12},]
    arrx2 =  [123, "hello"]

    #print(arrx2)
    err = pyvhash.checkhash(arrx2)
    #print("unhashed match:", err)
    assert err == False

    arrh = pyvhash.hasharr(arrx)
    err = pyvhash.checkhash(arrh)
    assert err == True

    arrh2 = pyvhash.hasharr(arrx2)
    #print("Modified: (ucase H)")
    arrh2[1] = "Hello"
    err = pyvhash.checkhash(arrh2)
    assert err == False

# EOF


