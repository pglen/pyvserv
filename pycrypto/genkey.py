#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

def genfname():
    rsize = 2; sss = ""
    rrr = Random.new().read(rsize)
    for aa in rrr:
        sss += "%x" % ord(aa)
    sss += "%x" % int(time.time()) # % 1000000)
    rrr = Random.new().read(rsize)
    for aa in rrr:
        sss += "%x" % ord(aa)
    return sss

ddd = './keys/'

if not os.path.isdir(ddd):
    os.mkdir(ddd)


fff  = genfname()
print( "generating file ", fff, "...",)

key = RSA.generate(8192)
#key = RSA.generate(4096)
#key = RSA.generate(2048)
#print (key, key.size())

prkey = key.exportKey('PEM')
f2 = open(ddd + fff + '.pem','wb')
f2.write(prkey)
f2.close()

pkey = key.publickey()
f3 = open(ddd + fff + '.pub','wb')
f3.write(pkey.exportKey('PEM'))
f3.close()

if __name__ == '__main__':
    print( "generated")



