#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base, '../'))
sys.path.append(os.path.join(base, '../../'))
#sys.path.append(os.path.join(base,  '../../../pypacker'))

import pyvhash, support, crysupp
import pyvpacker

from testx import *

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    thd = pyvhash.BcData()
    while 1:
        thd.powarr()
        ret = thd.checkpow()
        print(" %8d  %d" % (thd.cnt, ret))

    #print("Time: %f cnt = %d" %  (time.clock_gettime(time.CLOCK_BOOTTIME) - sss, thd.cnt))
    #print("4 match pow: [True] cnt =", thd.cnt, ret, end = " "); diff(True, ret)

# EOF
