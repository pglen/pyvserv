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

    thd = pyvhash.BcData()

    arrh = thd.hasharr()
    print(arrh)

    err = thd.checkhash()
    print("normal match:", )

    arrh = thd.powarr()
    print(arrh)
    err = thd.checkpow()
    print("pow match:", err)

    err = thd.checkhash()
    print("after pow hash match:", err)

    arrp = thd.linkarr(prevh)
    print(arrp)

    err = thd.checklink()
    print("match link:", err)

    err = thd.checkpow()
    print("after link pow match:", err)

    err = thd.checkhash()
    print("after link hash match:", err)

    # Damage
    #arrp[3]["Hash"]  = "a"
    #arrp[4]["Proof"]  = "a"
    #arrp[1] = 'aa'
    #err = pyvhash.checklink(arrp)
    #print("dam match link:", err)











