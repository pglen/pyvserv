#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base, '../'))

import pyvhash, support, crysupp
import pyvpacker

from testx import *

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    # The hash field will be overridden
    arrx  =  [123, "hello", {"Hash":12},]
    arrx2 =  [123, "hello", ]

    thd = pyvhash.BcData()
    print(thd.datax)

    ret = thd.checkhash()
    print("1 unhash match: [False]", ret, end = " "); diff(False, ret)

    thd.hasharr()
    #print(thd.datax)

    ret = thd.checkhash()
    print("2 normal match: [True]", ret, end = " "); diff(True, ret)

    thd.hasharr()

    ret = thd.checkhash()
    print("3 rehash match: [True]", ret, end = " "); diff(True, ret)

    #print("Modified: (ucase H) [False]")
    thd.addpayload({"Hello": 0})
    ret = thd.checkhash()
    print("4 modded match: [False]", ret, end = " "); diff(False, ret)

    thd.hasharr()
    ret = thd.checkhash()
    print("5 recalc match: [True]", ret, end = " "); diff(True, ret)

    #print(thd.datax)
    thd2 = pyvhash.BcData(thd)
    thd3 = pyvhash.BcData({"Test": 0})
    thd4 = pyvhash.BcData(["Array", 1])
    thd4 = pyvhash.BcData(["Array", 1])

# EOF

