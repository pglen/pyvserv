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

    # Hypothetical old hash
    prevh = pyvhash.shahex(b"1234")

    thd = pyvhash.BcData()
    #print (thd.datax)

    thd.addpayload({1:1,2:2, "delx":99, "new": 1234})
    #print (thd.datax)

    thd.allarr(prevh)
    print(thd.datax)

    err = thd.checklink()
    print("match link:", err)

    err = thd.checkpow()
    print("match pow:", err)

    thd.delpayload("Default")
    thd.delpayload("delx")
    thd.delpayload(1)
    thd.delpayload(2)
    thd.addpayload({"Default": "Immutable"})

    print(thd.datax)









