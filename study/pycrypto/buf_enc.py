#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random


# Int Number            i
# float Number          f
# Character             c
# String                s
# Binary                b

def encode_data(*formstr):

    for aa in formstr:
        print("formstr", aa)

    for bb in formstr[0]:
        print("bb", bb,)



