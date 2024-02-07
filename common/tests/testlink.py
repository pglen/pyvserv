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

    # The hash field will be overridden
    arrx =  [123, "hello", ]

    try:
        arrp = pyvhash.linkarr(arrx, prevh)
        print(arrp)
    except:
        #print(sys.exc_info())
        pass

    arrh = pyvhash.hasharr(arrx)
    print(arrh)

    err = pyvhash.checkhash(arrh)
    print("normal match:", err)

    arrh = pyvhash.powarr(arrh)
    print(arrh)
    err = pyvhash.checkpow(arrh)
    print("pow match:", err)

    err = pyvhash.checkhash(arrh)
    print("after pow hash match:", err)

    arrp = pyvhash.linkarr(arrh, prevh)
    print(arrp)

    err = pyvhash.checklink(arrp)
    print("match link:", err)

    err = pyvhash.checkpow(arrp)
    print("after link pow match:", err)

    err = pyvhash.checkhash(arrp)
    print("after link hash match:", err)

    # Damage
    #arrp[3]["Hash"]  = "a"
    #arrp[4]["Proof"]  = "a"
    #arrp[1] = 'aa'
    #err = pyvhash.checklink(arrp)
    #print("dam match link:", err)











