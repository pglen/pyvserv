#!/usr/bin/env python

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

message = '[[[Message to be encrypted. Here we go ]]]'
dsize = SHA.digest_size

hh = SHA.new(message)

print ("org:", message)

#key = RSA.importKey(open('pubkey.der').read())
cipher = PKCS1_v1_5.new(pkey)

messaged = message + hh.digest()
print ("deco:", messaged)

ciphertext = cipher.encrypt(messaged)

print ("enc:", ciphertext)

#key = RSA.importKey(open('privkey.der').read())

sentinel = Random.new().read(dsize)      # Let's assume that average data length is 15

print("sentinel", sentinel)

cipher2 = PKCS1_v1_5.new(key)
message2 = cipher2.decrypt(ciphertext, sentinel)

print ("decr:", message2)

digest2 = SHA.new(message2[:-dsize]).digest()

print ("digest2:", digest2)

if digest2 == message2[-dsize:]:                # Note how we DO NOT look for the sentinel
    print "Encryption was correct.", message2[:-dsize]
else:
    print "Encryption was not correct.", message2[:-dsize]



if __name__ == '__main__':
    print( "test")




