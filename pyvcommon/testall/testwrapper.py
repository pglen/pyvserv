#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

base = os.path.dirname(os.path.realpath(__file__))

# Fudge the include path so test succeeds
sys.path.append(os.path.join(base, '../'))
sys.path.append(os.path.join(base, '../../'))
sys.path.append(os.path.join(base,  '../../../pypacker'))
#sys.path.append(os.path.join(base,  '../../pycommon'))

import pyvpacker, pywrap

#key = b"12345"
key = Random.new().read(512)

rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
        "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ=="

bindat = base64.b64decode(rrr)

org = [ 33, "sub", 'd', "longer str here with \' and \" all crap",  \
        33, 33333333.2, bindat, ]

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    #print ("Should print success")
    #print("org", org);

    xlen = len(org)
    wr = pywrap.wrapper()
    #wr.pgdebug = 2

    ttt = time.time()
    www = wr.wrap_data(key, org)
    #print ("ttt=%f"  % (ttt - time.time()))
    print ("encode ttt=%.2f kBytes/s" % (xlen / (time.time() - ttt)))

    #print(" ----- ", www)
    # test: damage the data
    #www = www[:110] + chr(ord(www[10]) + 1) + www[111:]

    #print("www", www);

    ttt = time.time()
    #ooo = wr.unwrap_data(key, www.decode("cp437"))
    ooo = wr.unwrap_data(key, www)
    #print ("ttt=%f"  % (ttt - time.time()))
    print ("decode ttt=%.2f kBytes/s" % (xlen / (time.time() - ttt)))

    #print("ooo", ooo);

    if org != ooo:
        print ("Broken unwrap")
    else:
        print ("Success ", end="")
        #print(org)
        #print(ooo)
    print()

# EOF