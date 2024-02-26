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
import argparse

parser = argparse.ArgumentParser(description='Genetrate RSA keypair.')

parser.add_argument("-v", '--verbose', dest='verbose',
                    default=0,  action='count',
                    help='verbocity on (default: off)')

parser.add_argument("-b:", '--bits', dest='bits',
                    default=4096,  action='store', type=int,
                    help='Key to generate (default: 4096)')


def mainfunct():

    args = parser.parse_args()

    if not pyvgenkey.is_power_of_two(args.bits):
        print("Bitness must be a power of 2")
        sys.exit(1)

    pyvgenkey.position()
    #print("Current dir:     ", os.getcwd())
    print ("Started pyvserv continuous keygen. Press Ctrl-C to abort.")
    cnt = 0
    while(True):
        cnt += 1;
        #print ("Key %d ... " % cnt, end="");    sys.stdout.flush()
        pyvgenkey.genkey(args.bits)
        #print ("OK. ")

        sleepy  = 0.2
        # Ease on hogging the system
        if cnt > 100:
            sleepy = 200
        elif cnt > 10:
            sleepy = 100
        elif cnt > 5:
            sleepy = 10

        time.sleep(sleepy)

if __name__ == '__main__':
    mainfunct()

# EOF