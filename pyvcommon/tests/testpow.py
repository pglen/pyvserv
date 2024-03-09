#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base, '../'))
sys.path.append(os.path.join(base, '../../'))
#sys.path.append(os.path.join(base,  '../../../pypacker'))

import pyvhash, support, crysupp
import pyvpacker

from testx import *

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    # The hash field will be overridden
    arrx =  {"hello" : "wwww", "Hash": 12,}
    thd = pyvhash.BcData(arrx)

    #ddd = { "Hello": 1234 }
    #thd = pyvhash.BcData(arrx)
    #thd = pyvhash.BcData()

    print(thd.datax)

    #thd = pyvhash.BcData()

    ret = thd.checkhash()
    print("1 uncal hash: [False]", ret, end = " "); diff(False, ret)

    ret = thd.checkpow()
    print("2 uncal  pow: [False]", ret, end = " "); diff(False, ret)

    thd.hasharr()
    ret = thd.checkhash()
    print("3 match hash: [True]", ret, end = " "); diff(True, ret)

    thd.powarr()
    ret = thd.checkpow()
    print("4 match  pow: [True]", ret, end = " "); diff(True, ret)

    thd.hasharr()
    ret = thd.checkhash()
    print("5 match hash: [True]", ret, end = " "); diff(True, ret)

    thd.powarr()
    ret = thd.checkpow()
    print("6 match  pow: [True]", ret, end = " "); diff(True, ret)

    #print(thd.datax)

    # Damage sums
    thd.addpayload({"testkey":"test"})

    ret = thd.checkhash()
    print("7 match hash: [False]", ret, end = " "); diff(False, ret)

    ret = thd.checkpow()
    print("8 match  pow: [False]", ret, end = " "); diff(False, ret)

    thd.hasharr()
    ret = thd.checkhash()
    print("9 match hash: [True]", ret, end = " "); diff(True, ret)

    thd.powarr()
    ret = thd.checkpow()
    print("0 match  pow: [True]", ret, end = " "); diff(True, ret)

    ret = thd.checkhash()
    print("1 match hash: [True]", ret, end = " "); diff(True, ret)

# EOF

