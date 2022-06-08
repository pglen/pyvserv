#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

# Deprecated, pad it
time.clock = time.process_time

def genfname():

    rsize = 2; sss = ""
    rrr = Random.new().read(rsize)
    for aa in rrr:
        sss += "%x" % ord(str(aa)[0])

    sss += "%x" % int(time.time()) # % 1000000)

    rrr = Random.new().read(rsize)
    for aa in rrr:
        sss += "%x" % ord(str(aa)[0])

    #print("fname", sss)

    return sss

    #sss.decode("cp437")

def genkey(keylen):

    key = RSA.generate(keylen)
    #print ("Generated:", key, key.size())

    fff  = genfname()
    f2 = open(privdir + fff + '.pem','w')

    if sys.version_info[0] > 2:
        f2.write(key.exportKey('PEM').decode("cp437"))
    else:
        f2.write(key.exportKey('PEM'))
    f2.close()

    pkey = key.publickey()
    f3 = open(keydir + fff + '.pub','w')

    if sys.version_info[0] > 2:
        f3.write(pkey.exportKey('PEM').decode("cp437"))
    else:
        f3.write(pkey.exportKey('PEM'))
    f3.close()

    return fff

keydir = './keys/'
privdir = './private/'

rstr = Random.new().read(random.randint(14, 24))

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

    if not os.path.isdir(privdir):
        os.mkdir(privdir)

    #print("Current dir:     ", os.getcwd())
    print ("Started key gen ... (please wait) ", end=""); sys.stdout.flush()
    fname = genkey(8192)
    #fname = genkey(4096)
    print("OK, Generated files:")
    print("'" + keydir + os.sep + fname + ".pem'", "'" + privdir + os.sep + fname + ".pub'")

#if __name__ == '__main__':
#    print( "Generated file: ", "'" + fff + "'")






