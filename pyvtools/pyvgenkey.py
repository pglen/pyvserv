#!/usr/bin/env python

#from __future__ import print_function

'''
    Small ECC keys have the equivalent strength of larger RSA keys because of
    the algorithm used to generate them. For example, a 256-bit ECC key is
    equivalent to a 3072-bit RSA key and a 384-bit ECC key is equivalent to a
    7680-bit RSA key.
'''

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, threading

if sys.version_info[0] < 3:
    print("needs py 3")
    sys.exit(0)

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  'pyvecc'))

from pyvecc.Key import Key

from Crypto.PublicKey import ECC
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

parser.add_argument("-r:", '--rsa', dest='use_rsa',
                    default=False,  action='store_true',
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

    gl_key = Key.generate(256)

    stopthread = True
    time.sleep(.1)

def genkey(keylen, use_rsa):

    ''' Generate key, give optional feedback '''

    global stopthread, gl_keylen, gl_key

    fff  = genfname()
    gl_keylen = keylen

    #fb_thread = threading.Thread(target=genkey_thread)
    #fb_thread.daemon = True
    #fb_thread.start()
    #print(fff, end = " ")
    #while True:
    #    if stopthread:
    #        break
    #    print(".", end = "")
    #    sys.stdout.flush()
    #    time.sleep(.5)
    #
    #if fb_thread.is_alive():
    #    fb_thread.join(1)
    #print()    ; sys.stdout.flush()
    #stopthread = False

    genkey_thread()

    #print ("Generated:", key, key.size())

    # Private key
    privname = privdir + fff + '.pem'
    f2 = open(privname,'w')
    f2.write(gl_key.export_priv())
    f2.close()

    # Public Key
    pubname = keydir + fff + '.pub'
    f3 = open(pubname,'w')
    f3.write(gl_key.export_pub())
    f3.close()

    return privname, pubname

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

    position()

    #print("Current dir:     ", os.getcwd())
    print ("Started pyvserv keygen, ECC 384"); sys.stdout.flush()
    fnames = genkey(args.bits, args.use_rsa)
    print("Generated files:")
    print("'" + fnames[0] + "'",  "'" + fnames[1] + "'")
    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
