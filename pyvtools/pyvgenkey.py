#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, threading

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..'))

from pyvcommon import pyservsup

import argparse

parser = argparse.ArgumentParser(description='Genetrate RSA keypair.')

parser.add_argument("-v", '--verbose', dest='verbose',
                    default=0,  action='count',
                    help='verbocity on (default: off)')

parser.add_argument("-b:", '--bits', dest='bits',
                    default=4096,  action='store', type=int,
                    help='Key to generate (default: 4096)')

# Deprecated, pad it
time.clock = time.process_time

# ------------------------------------------------------------------------

def is_power_of_two(n):
    return (n != 0) and (n & (n-1) == 0)

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

stopthread = 0
gl_keylen = 8
gl_key = None

def genkey_thread():

    global stopthread, gl_keylen, gl_key

    gl_key = RSA.generate(gl_keylen)
    stopthread = True
    time.sleep(1)

def genkey(keylen):

    ''' Generate key, give feedback '''

    global stopthread, gl_keylen, gl_key

    fff  = genfname()
    gl_keylen = keylen
    fb_thread = threading.Thread(target=genkey_thread)
    fb_thread.daemon = True
    fb_thread.start()
    print(fff, end = " ")
    while True:
        if stopthread:
            break
        print(".", end = "")
        sys.stdout.flush()
        time.sleep(2)

    if fb_thread.is_alive():
        fb_thread.join(1)
    print()    ; sys.stdout.flush()
    stopthread = False

    #print ("Generated:", key, key.size())

    f2 = open(privdir + fff + '.pem','w')

    if sys.version_info[0] > 2:
        f2.write(gl_key.exportKey('PEM').decode("cp437"))
    else:
        f2.write(gl_key.exportKey('PEM'))
    f2.close()

    pkey = gl_key.publickey()
    f3 = open(keydir + fff + '.pub','w')

    if sys.version_info[0] > 2:
        f3.write(pkey.exportKey('PEM').decode("cp437"))
    else:
        f3.write(pkey.exportKey('PEM'))
    f3.close()

    return fff

keydir = './keys/'
privdir = './private/'

def position():

    global_vars = pyservsup.Global_Vars(__file__)
    global_vars._mkdir(global_vars.myhome)
    os.chdir(global_vars.myhome)
    if not os.path.isdir(global_vars.keydir):
        os.mkdir(global_vars.keydir)
    if not os.path.isdir(global_vars.privdir):
        os.mkdir(global_vars.privdir)

#rstr = Random.new().read(random.randint(14, 24))

def mainfunct():

    args = parser.parse_args()

    if not is_power_of_two(args.bits):
        print("Bitness must be a power of 2")
        sys.exit(1)

    #script_home = os.path.dirname(os.path.realpath(__file__)) + "/../data/"
    #print ("Script home:     ", script_home)

    position()

    #print("Current dir:     ", os.getcwd())
    print ("Started pyvserv keygen - (long wait for [", args.bits, " bits]) "); sys.stdout.flush()
    fname = genkey(args.bits)
    print("OK, Generated files:")
    print("'" + keydir + os.sep + fname + ".pem'", "'" + privdir + os.sep + fname + ".pub'")
    sys.exit(0)

if __name__ == '__main__':
    mainfunct()


# EOF

