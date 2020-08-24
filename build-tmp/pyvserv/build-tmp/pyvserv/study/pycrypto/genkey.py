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

keydir = './keys/'

if __name__ == '__main__':

    script_home = os.path.dirname(os.path.realpath(__file__)) + "/../data/"
    #print ("Script home:     ", script_home)

    try:
        if not os.path.isdir(script_home):
            os.mkdir(script_home)
    except:
        print( "Cannot make script home dir", sys.exc_info())
        sys.exit(1)

    os.chdir(script_home)

    if not os.path.isdir(keydir):
        os.mkdir(keydir)

    print("Current dir:     ", os.getcwd())
    print ("Started gen ...")

    #key = RSA.generate(2048)
    key = RSA.generate(4096)
    #print ("Generated:", key, key.size())

    fff  = genfname()
    f = open(ddd + fff + '.pem','w')
    f.write(key.exportKey('PEM'))
    f.close()

    pkey = key.publickey()
    f3 = open(ddd + fff + '.pub','w')
    f3.write(pkey.exportKey('PEM'))
    f3.close()

#if __name__ == '__main__':
#    print( "Generated file: ", "'" + fff + "'")




