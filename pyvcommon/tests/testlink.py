#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base, '../'))
sys.path.append(os.path.join(base, '../../'))
sys.path.append(os.path.join(base,  '../../../pypacker'))

import pyvhash, support, crysupp
import pyvpacker

from testx import *

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    # Hypothetical old hash
    prevh = pyvhash.shahex(b"1234")

    # The hash field will be ovretidden
    arrx =  [123, "hello", ]

    exc = 0
    try:
        arrp = pyvhash.linkarr(arrx, prevh)
        print(arrp)
    except:
        #print(sys.exc_info())
        #print("No power")
        exc = True
        pass

    assert exc == True

    thd = pyvhash.BcData()
    thd.hasharr()
    #print(thd.datax)

    ret = thd.checkhash()
    print("1 normal match: [True]", ret, end = " "); diff(True, ret)

    thd.powarr()
    ret = thd.checkpow()
    print("2 power  match: [True]", ret, end = " "); diff(True, ret)

    thd.linkarr(prevh)

    ret = thd.checklink()
    print("3  match  link: [True]", ret, end = " "); diff(True, ret)

    ret = thd.checkpow()
    print("4 after  power: [True]", ret, end = " "); diff(True, ret)

    ret = thd.checkhash()
    print("5 after  link:  [True]", ret, end = " "); diff(True, ret)

# EOF
