#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

#from Crypto.PublicKey import RSA
#from Crypto.Cipher import PKCS1_v1_5
#from Crypto.PublicKey import RSA
#from Crypto.Hash import SHA

from Crypto import Random

import pyvgenkey

if __name__ == '__main__':

    # Randomize
    #rstr = Random.new().read(random.randint(14, 64))

    pyvgenkey.position()
    #print("Current dir:     ", os.getcwd())
    print ("Started pyvserv continuous keygen. Press Ctrl-C to abort.")
    cnt = 0
    while(True):
        cnt += 1;
        #print ("Key %d ... " % cnt, end="");    sys.stdout.flush()
        pyvgenkey.genkey(8192)
        #print ("OK. ")

        # Ease on hogging the system
        if cnt > 100:
            time.sleep(1000)
        elif cnt > 10:
            time.sleep(100)
        elif cnt > 5:
            time.sleep(10)
        else:
            time.sleep(0.2)





