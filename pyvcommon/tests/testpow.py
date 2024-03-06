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

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    # The hash field will be overridden
    arrx =  [123, "hello", {"Hash": 12},]

    thd = pyvhash.BcData()

    ret = thd.checkhash()
    print("1 match hash: [False]", ret)

    ret = thd.checkpow()
    print("2 match  pow: [False]", ret)

    thd.hasharr()
    ret = thd.checkhash()
    print("3 match hash: [True]", ret)

    thd.powarr()
    ret = thd.checkpow()
    print("4 match  pow: [True]", ret)

    thd.hasharr()
    ret = thd.checkhash()
    print("5 match hash: [True]", ret)

    #print(thd.datax)

    # Damage sums
    thd.addpayload({"testkey":"test"})

    ret = thd.checkhash()
    print("6 match hash: [False]", ret)

    ret = thd.checkpow()
    print("7 match pow: [False]", ret)

    thd.hasharr()
    ret = thd.checkhash()
    print("8 match hash: [True]", ret)

    thd.powarr()
    ret = thd.checkpow()
    print("9 match  pow: [True]", ret)

    ret = thd.checkhash()
    print("0 match hash: [True]", ret)

# EOF

