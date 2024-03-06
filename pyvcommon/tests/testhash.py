#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base, '../'))
#sys.path.append(os.path.join(base, '../../'))
#sys.path.append(os.path.join(base,  '../../../pypacker'))

import pyvhash, support, crysupp
import pyvpacker

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    # The hash field will be overridden
    arrx  =  [123, "hello", {"Hash":12},]
    arrx2 =  [123, "hello", ]

    thd = pyvhash.BcData()
    #print(thd.datax)

    ret = thd.checkhash()
    print("1 unhash match: [False]", ret)

    thd.hasharr()
    #print(thd.datax)

    ret = thd.checkhash()
    print("2 normal match: [True]", ret)

    thd.hasharr()

    ret = thd.checkhash()
    print("3 rehash match: [True]", ret)

    #print("Modified: (ucase H) [False]")
    thd.addpayload({"Hello": 0})
    ret = thd.checkhash()
    print("4 modded match: [False]", ret)

    thd.hasharr()
    ret = thd.checkhash()
    print("5 recalc match: [True]", ret)

# EOF

