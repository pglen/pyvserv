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

    err = pyvhash.checkhash(arrx)
    print("match hash:", err)

    err = pyvhash.checkhash(arrx)
    print("match pow:", err)

    arrh = pyvhash.hasharr(arrx)
    print(arrh)

    arrp = pyvhash.powarr(arrh)
    print(arrp)

    err = pyvhash.checkhash(arrp)
    print("match hash:", err)

    err = pyvhash.checkpow(arrp)
    print("match pow:", err)

    # Damage
    #arrp[3]["Hash"]  = "a"
    #arrp[4]["Proof"]  = "a"
    arrp[1] = 'aa'

    err = pyvhash.checkhash(arrp)
    print("dam match hash:", err)

    err = pyvhash.checkpow(arrp)
    print("dam match pow:", err)











