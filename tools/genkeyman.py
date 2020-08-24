#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

'''from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random'''

import genkey

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

    #print("Current dir:     ", os.getcwd())
    print ("Started gen. Press Ctrl-C to abort.")
    cnt = 0

    while(True):
        cnt += 1;
        print ("Key %d ... " % cnt, end="");    sys.stdout.flush()
        genkey.genkey(8192)
        print ("OK. ")

        if cnt > 100:
            time.sleep(1000)
        elif cnt > 10:
            time.sleep(100)
        elif cnt > 5:
            time.sleep(10)
        else:
            time.sleep(0.2)

#if __name__ == '__main__':
#    print( "Generated file: ", "'" + fff + "'")





