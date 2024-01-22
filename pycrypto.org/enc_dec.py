#!/usr/bin/env python3

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

#from crysupp import *

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

message = '\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    '
# ------------------------------------------------------------------------

def test_one():

    dsize = SHA.digest_size

    hh = SHA.new(message.encode("cp437"))

    #print (hexdump(message))

    print ("org:")
    print( message)

    pukey = RSA.importKey(open("e1bb5e9f931c9c86.pub").read())
    cipher = PKCS1_v1_5.new(pukey)

    #messaged = message + hh.digest()
    #print ("deco:", messaged)

    ciphertext = cipher.encrypt(message.encode("cp437"))

    pstr = base64.b64encode(ciphertext)
    plen = len(pstr)
    xstr = b""
    for aa in range(plen//64 + 1):
        xstr += pstr[aa * 64: (aa+1) * 64] + b"\n"

    f2 = open("encrypted",'wb')
    f2.write(xstr)
    f2.close()

    #print ("enc:", ciphertext)

    prkey = RSA.importKey(open("e1bb5e9f931c9c86.pem").read())

    sentinel = Random.new().read(dsize)      # Let's assume that average data length is 15

    #print (hexdump(sentinel))

    #print("sentinel", sentinel)

    cipher2 = PKCS1_v1_5.new(prkey)
    message2 = cipher2.decrypt(ciphertext, sentinel)

    #print ("decr:", message2)

    digest2 = SHA.new(message2[:-dsize]).digest()

    #print ("digest2:", digest2)

    '''if digest2 == message2[-dsize:]:                # Note how we DO NOT look for the sentinel
        print("Decr:")
        print (message2[:-dsize])
        print ("Encryption was correct.", len(message), "bytes")
    else:
        print ("Encryption was not correct.")
    '''

    print (message2.decode("cp437"))

    if message == message2.decode("cp437"):
        print("enc / dec cycle OK")

if __name__ == '__main__':
    test_one()









