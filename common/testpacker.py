#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

import support, pypacker

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
            "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ=="

    print ("Should print 4 successes and a sample output")

    pb = pypacker.packbin(); pb.verbose = 3

    '''sorg = [ 334, "subx", 'x', ]
    if pb.verbose > 2:
        print ("org:\n", sorg)
    eee = pb.encode_data("", *sorg)
    if pb.verbose > 2:
        print ("eee:\n", eee)
    sys.exit(0)'''

    #bindat = Random.new().read(64)
    #print("bindat64:\n", base64.b64encode(bindat))

    bindat = base64.b64decode(rrr)

    org = [ 33, "sub", 'd', "longer str here with \' and \" all crap", 33, 33333333.2, bindat ]


    if pb.verbose > 2:
        print ("org:\n", org)

    eee = pb.encode_data("", *org)

    sys.exit(0)

                          #iscsifb
    #eee = pb.encode_data("iscsfb", *org)
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
        print ("Success ", end="")

    #sys.exit(0)

    org2 = [ 22, 444, "data", 123.456, 'a', eee]
    #print ("org2:\n", org2)
    eee2 = pb.encode_data("ilsfcx", *org2)
    #print ("eee2:\n", eee2)
    ddd2 = pb.decode_data(eee2)
    #print ("ddd2:\n", ddd2)

    if not org2 == ddd2:
        print ("Broken decode")
        print ("eee2:\n", eee2)
    else:
        print ("Success ", end="")

    fff = zlib.compress(eee)
    #print("compressed %.2f" % (float(len(fff)) / len(eee)) )
    hhh = zlib.decompress(fff)
    if not eee == hhh:
        print ("Broken unzip")

    ddd3 = pb.decode_data(eee2)
    #print("ddd3", ddd3)
    ggg = pb.decode_data(ddd3[5])
    #print("ggg", ggg)

    if not org == ggg:
        print ("Broken decode")
    else:
        print ("Success ", end="")

    www = pb.wrap_data(org)
    #print ("www", www)

    # damage the data
    zzz = www[:100] + chr(ord(www[100]) + 1) + www[101:]
    # OK data
    zzz = www[:100] + www[100:]
    #print (len(zzz), len(www), chr(ord(www[100]) + 1))

    ooo = pb.unwrap_data(zzz)
    oooo = pb.decode_data(ooo)

    if not org == oooo:
        print ("Broken unwrap")
    else:
        print ("Success ", end="")

    print()

    zzzz = support.breaklines(zzz, 75)
    print (zzzz)





