#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

ddd = '../keys/'
verbose = False
quiet = False
loopit = False
version = "1.0"

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

def genkey():

    if not os.path.isdir(ddd):
        os.mkdir(ddd)

    fff  = genfname()
    print( "Generating file: ", fff, "in dir", ddd)
    print ("(8192 bits) Please wait ...")

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

def help():
    print("Use: ");

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:qhvVl")
    except getopt.GetoptError as err:
        print( "Invalid option(s) on command line:", err)
        sys.exit(1)

    #print( "opts", opts, "args", args)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
                if verbose:
                    print( "Debug level:", pgdebug)
                if pgdebug > 10 or pgdebug < 0:
                    raise(Exception(ValueError, \
                        "Debug range needs to be between 0-10"))
            except:
                support.put_exception("Command line for:")
                sys.exit(3)

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-v": verbose = True
        if aa[0] == "-l": loopit = True
        if aa[0] == "-q": quiet = True
        if aa[0] == "-V":
            print( os.path.basename(sys.argv[0]), "Version", version)
            sys.exit(0)

    if loopit:
        while True:
            genkey()
            time.sleep(30)
    else:
        genkey()
    #print( "generated")




