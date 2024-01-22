#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

from crysupp import *

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

# ------------------------------------------------------------------------

def genref():

    dsize = SHA.digest_size

    hh = SHA.new(refmessage)

    pukey = RSA.importKey(open("testkey.pub").read())
    cipher = PKCS1_v1_5.new(pukey)

    messaged = refmessage + hh.digest()
    ciphertext = cipher.encrypt(messaged)

    # Convert to editable
    pstr = base64.b64encode(ciphertext)
    plen = len(pstr)

    # Add lines on 64 boundary
    xstr = begtag
    for aa in range(plen/64 + 1):
        xstr += pstr[aa * 64: (aa+1) * 64] + "\n"
    xstr += endtag

    fname = "encrypted.ref"
    if os.path.isfile(fname):
        print("Refusing to write, file already exists.");
    else:
        f2 = open("encrypted.ref",'wb')
        f2.write(xstr)
        f2.close()

if __name__ == '__main__':
    genref()

