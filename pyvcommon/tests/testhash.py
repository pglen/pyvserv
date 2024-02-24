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

import pyvhash, support, pypacker, crysupp

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    # The hash field will be overridden
    arrx =  [123, "hello", {"Hash":12},]
    arrx2 =  [123, "hello", ]

    thd = pyvhash.BcData()

    #print(arrx2)
    err = thd.checkhash()
    print("unhashed match:", err)

    arrh = thd.hasharr()
    print(arrh)

    err = thd.checkhash()
    print("normal match:", err)

    arrh2 = thd.hasharr()
    print(arrh2)

    print("Modified: (ucase H)")
    arrh2[1] = "Hello"
    print(arrh2)
    err = thd.checkhash()
    print("modded match:", err)










