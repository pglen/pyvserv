#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

import support, pypacker

key = "" #"1235"

rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
        "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ=="

bindat = base64.b64decode(rrr)

org = [ 33, "sub", 'd', "longer str here with \' and \" all crap",  33, 33333333.2, bindat ]

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    #print ("Should print success")

    #print("org", org);

    wr = pypacker.wrapper()
    www = wr.wrap_data(key, org)

    print(" ----- ", www)

    # test: damage the data
    #www = www[:110] + chr(ord(www[10]) + 1) + www[111:]

    #print("www", www);

    ooo = wr.unwrap_data(key, www)

    #print("ooo", ooo);

    if not org == ooo:
        print ("Broken unwrap")
    else:
        print ("Success ", end="")

    print()

# EOF