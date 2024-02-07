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

    rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
            "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ=="

    # The hash field will be overridden
    arrx =  [123, "hello", {"Hash":12},]
    arrx2 =  [123, "hello", ]

    print(arrx2)
    err = pyvhash.checkhash(arrx2)
    print("unhashed match:", err)

    arrh = pyvhash.hasharr(arrx)
    print(arrh)

    err = pyvhash.checkhash(arrh)
    print("normal match:", err)

    arrh2 = pyvhash.hasharr(arrh)
    print(arrh2)

    print("Modified: (ucase H)")
    arrh2[1] = "Hello"
    print(arrh2)
    err = pyvhash.checkhash(arrh2)
    print("modded match:", err)










