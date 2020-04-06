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

    pb = pypacker.packbin();
    '''
    pb.verbose = 3

    zorg = { 334 : "subx", 'x' : 123 }
    xorg = ["val1", "val2", "val3"]
    yorg = ["1", "2", "3"]

    sorg_var = [ 334, "subx", 'x', xorg, yorg]
    #sorg_var = [ 334, "subx", 'x', xorg, zorg]

    if pb.verbose > 2:
        print ("sorg_var:\n", sorg_var)

    eee_var = pb.encode_data("", *sorg_var)
    if pb.verbose > 2:
        print ("eee_var type", type(eee_var).__name__, ":\n", eee_var)

    fff_var = pb.decode_data(eee_var)
    if pb.verbose > 2:
        print ("fff_var:\n", fff_var)

    if  sorg_var != fff_var:
        print("Error on compare")

    #sys.exit(0)
    '''

    #bindat = Random.new().read(64)
    #print("bindat64:\n", base64.b64encode(bindat))

    bindat = base64.b64decode(rrr)

    org = [ 33, "sub", 'd', "longer str here with \' and \" all crap",  33, 33333333.2, bindat ]

    if pb.verbose > 2:
        print ("org:\n", org)
    eee = pb.encode_data("", *org)
    if pb.verbose > 2:
        print("eee:\n", "{" + eee + "}")

    ddd = pb.decode_data(eee)
    if pb.verbose > 2:
        print("ddd:\n",  "{" + str(ddd) + "}")

    if org == ddd:
        #print("Data matches OK.")
        pass
    else:
        print("MISMATCH:")

    #print ("Should print 4 successes and a sample output")
    print ("Should print 4 successes")
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
        print ("Success1 ", end="")

    org2 = [ 22, 444, "data", 123.456, 'a', eee]
    #print ("org2:\n", org2)
    #eee2 = pb.encode_data("ilsfcx", *org2)
    eee2 = pb.encode_data("ilsfcx", *org2)
    #print ("eee2:\n", eee2)
    ddd2 = pb.decode_data(eee2)
    #print ("ddd2:\n", ddd2)

    if not org2 == ddd2:
        print ("Broken decode")
        print ("eee2:\n", eee2)
    else:
        print ("Success2 ", end="")

    if sys.version_info[0] > 2:
        eee  = eee.encode("cp437")

    fff = zlib.compress(eee)

    #print("compressed %.2f" % (float(len(fff)) / len(eee)) )

    hhh = zlib.decompress(fff)
    if not eee == hhh:
        print ("Broken unzip")
    else:
        pass
        #print("Unzip OK")

    ddd3 = pb.decode_data(eee2)
    #print("ddd3", ddd3)
    ggg = pb.decode_data(ddd3[5])
    #print("ggg", ggg)

    if not org == ggg:
        print ("Broken decode")
    else:
        print ("Success3 ", end="")

    www = pb.wrap_data(org)

    #if sys.version_info[0] > 2:
    #    www  = eee.decode("cp437")

    # damage the data
    #www = www[:110] + chr(ord(www[10]) + 1) + www[111:]
    #print ("www", www)

    ooo = pb.unwrap_data(www)
    if not org == ooo:
        print ("Broken unwrap")
    else:
        print ("Success4 ", end="")

    #zzzz = support.breaklines(ooo, 75)
    #print (zzzz)
    print()

    '''oooo = pb.decode_data(ooo)
    if not org == oooo:
        print ("Broken unwrap final")
    else:
        print ("Success5 ", end="")
    '''









