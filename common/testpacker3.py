#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base, '../bluepy'))
sys.path.append(os.path.join(base, '../common'))
sys.path.append(os.path.join(base,  '../../pycommon'))

import support, pypacker

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
            "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ==" + "b" * 100000

    pb = pypacker.packbin();
    pb.verbose = 0

    #bindat = Random.new().read(64)
    #print("bindat64:\n", base64.b64encode(bindat))

    bindat = base64.b64decode(rrr)

    org = [ 33, "sub", 'd', "longer str here with \' and \" all crap",  33, 33333333.2,
                {"test": 1111, "test2": 1112, }, bindat, "a" * 2000000 ]

    if pb.verbose > 0:
        print ("org:\n", org)

    ttt = time.time()

    eeenc = pb.encode_data("", *org)
    if pb.verbose > 2:
        print("eeenc:\n", "{" + eeenc + "}")

    dddec = pb.decode_data(eeenc)
    if pb.verbose > 1:
        print("dddec:\n",  "{" + str(dddec) + "}")

    if org == dddec:
        #print("Data matches OK.")
        pass
    else:
        print("MISMATCH:")

    #sys.exit(0)

    print ("ttt=%f"  % (ttt - time.time()))

    eee = pb.encode_data("", *org)
    if pb.verbose > 2:
        print ("eee:\n", eee)

    ddd = pb.decode_data(eee)
    if pb.verbose > 2:
        print ("ddd:\n", ddd)

    if not org == ddd:
        print ("Broken decode")
        print ("eee:\n", eee)
    else:
        pass
        #print ("Success1 ", end="")

    print ("ttt=%f"  % (ttt - time.time()))


# EOF
