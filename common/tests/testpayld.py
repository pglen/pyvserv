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
    arrx =  [123, "hello", {"PayLoad": {"Date":1, "Time":2}},]

    #arrh = pyvhash.hasharr(arrx)
    ##print(arrh)
    #err = pyvhash.checkhash(arrh)
    #print("normal match:", err)
    #arrh = pyvhash.powarr(arrh)
    ##print(arrh)

    var = None
    for aa in range(len(arrx)):
        #print(type(arrx[aa]), type({}), arrx[aa])
        if type(arrx[aa]) == type({}):
            #print(arrx[aa])
            if "PayLoad" in arrx[aa]:
                #print("payload")
                var = arrx[aa]["PayLoad"]

    print (var)
    var |= {1:1,2:2, "delx":99}
    print (var)
    del var["delx"]
    print (var)

    arrp = pyvhash.allarr(arrx, prevh)
    print(arrp)

    err = pyvhash.checklink(arrp)
    print("match link:", err)










