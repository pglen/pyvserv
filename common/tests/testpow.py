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

    thd = pyvhash.BcData()

    err = thd.checkhash()
    print("match hash:", err)

    err = thd.checkhash()
    print("match pow:", err)

    arrh = thd.hasharr()
    print(arrh)

    arrp = thd.powarr()
    print(arrp)

    err = thd.checkhash()
    print("match hash:", err)

    err = thd.checkpow()
    print("match pow:", err)

    # Damage
    #arrp[3]["Hash"]  = "a"
    #arrp[4]["Proof"]  = "a"
    arrp[1] = 'aa'

    err = thd.checkhash()
    print("dam match hash:", err)

    err = thd.checkpow()
    print("dam match pow:", err)











