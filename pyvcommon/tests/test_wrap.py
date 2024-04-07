#!/usr/bin/env python3

import pytest, os, sys
#from mytest import *

# Set parent as module include path
base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base,  '../../pyvcommon'))

import pywrap

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

key = "1234567890123456789012345678901234567890"
data = [b"data " * 4 ]
dddd =  b'\x1e6Y5\xfaa>\xf0\x1d[\x87\x9b\xbe`\xa2=2\x83\xa8\xe5\xc4\xe6' + \
           b'\x0e\x7f\xb7-\xce\xd6Y\x08\xe6\x176\x14z\xa9\xfcQ$gp\xd9\xe3' + \
           b'\xc0$\xd4\x93P\x84'

def test_func(capsys):

    wrap = pywrap.wrapper()

    #print("data:", data)
    ddd = wrap.wrap_data(key, data)
    #print("ddd:", ddd)
    assert dddd == ddd
    uuu = wrap.unwrap_data(key, ddd)
    assert uuu == data
    #print("uuu:", uuu)

    #assert 0


data2 = ["00000" * 10000]

def test_big(capsys):

    wrap = pywrap.wrapper()

    #print("data:", data)
    ddd2 = wrap.wrap_data(key, data2)
    uuu2 = wrap.unwrap_data(key, ddd2)
    assert uuu2 == data2

    #assert 0


# EOF

