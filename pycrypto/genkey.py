#!/usr/bin/env python

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

#key = RSA.generate(2048)
key = RSA.generate(4096)
#print (key, key.size())

fff  = genfname()
f = open(ddd + fff + '.pem','w')
f.write(key.exportKey('PEM'))
f.close()

pkey = key.publickey()
f3 = open(ddd + fff + '.pub','w')
f3.write(pkey.exportKey('PEM'))
f3.close()

if __name__ == '__main__':
    print( "generated file ", fff)


