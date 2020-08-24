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

def checkref():

    dsize = SHA.digest_size

    f2 = open("encrypted.ref",'rb')
    ciphertext = f2.read()
    f2.close()

    idx = ciphertext.index(begtag)
    idx2 = ciphertext.rindex(endtag)

    # Remove headers / trailers
    pstr = ciphertext[idx + len(begtag):idx2]

    #print ("org:\n", pstr)
    #print (hexdump(pstr))

    pstr = base64.b64decode(pstr)
    prkey = RSA.importKey(open("testkey.pem").read())

    sentinel = Random.new().read(dsize)      # Let's assume that average data length is 15

    #print ("sentinel:" , hexdump(sentinel))
    #print("sentinel", sentinel)

    cipher2 = PKCS1_v1_5.new(prkey)
    message2 = cipher2.decrypt(pstr, sentinel)

    #print ("decr:", message2)

    digest2 = SHA.new(message2[:-dsize]).digest()

    #print ("digest2:", digest2)

    if digest2 == message2[-dsize:]:                # Note how we DO NOT look for the sentinel
        #print("Decr:")
        #print (message2[:-dsize])
        print ("Decryption was correct, and ", end="")

        if message2[:-dsize] == refmessage:
            print ("buffers compare OK.")
        else:
            print ("buffers compare FAIL.")

        return 0
    else:
        print ("Decryption was NOT correct.")
        #print (message2[:-dsize])
        return 1

    return ret

if __name__ == '__main__':
    ret = checkref()
    sys.exit(ret)







