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
import pyvpacker, comline

from testx import *

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    testarg = ["hello", "world", "-v"]
    conf = comline.ConfigLong(comline.optarrlong)
    print(conf)
    opts, args = conf.comline(testarg)
    print("opts:", opts, "args:", args)
    conf.printvars()

# EOF
