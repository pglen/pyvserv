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

from Crypto import Random

# This repairs the path from local run to pip run.
# Remove pip version for local tests
try:
    from pyvcommon import support

    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    #print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))

except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    from pyvcommon import support

#print("Load:", sys.path[-1])

from pyvcommon import pyservsup

import argparse

parser = argparse.ArgumentParser(description='Genetrate ECC keypair for pyvserv')

parser.add_argument("-v", '--verbose', dest='verbose',
                    default=0,  action='count',
                    help='verbocity on (default: off)')

#parser.add_argument("-b:", '--bits', dest='bits',
#                    default=4096,  action='store', type=int,
#                    help='Key to generate (default: 4096)')
#
#parser.add_argument("-r:", '--rsa', dest='use_rsa',
#                    default=False,  action='store_true',
#                    help='Key to generate (default: 4096)')

parser.add_argument("-m:", '--homedir', dest='homedir',
                    default="pyvserver",  action='store',
                    help='pyvserv home directory (default: ~/pyvserver)')

parser.add_argument("-q:", '--quiet', dest='quiet',
                    default=0,  action='store_true',
                    help='Display less information. Default: off')

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

def genkey():

    ''' Generate key, give optional feedback '''

    global stopthread, gl_keylen, gl_key

    fff  = genfname()
    #gl_keylen = keylen

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

def position(args):

    global_vars = pyservsup.Global_Vars(__file__, args.homedir)
    global_vars._softmkdir(global_vars.myhome)

    if args.verbose:
        print("dir", global_vars.myhome)

    os.chdir(global_vars.myhome)
    if not os.path.isdir(global_vars.keydir):
        os.mkdir(global_vars.keydir)
    if not os.path.isdir(global_vars.privdir):
        os.mkdir(global_vars.privdir)

#rstr = Random.new().read(random.randint(14, 24))

def mainfunct():

    #global args
    args = parser.parse_args()

    #if not is_power_of_two(args.bits):
    #    print("Bitness must be a power of 2")
    #    sys.exit(1)

    position(args)

    #print("Current dir:     ", os.getcwd())
    if not args.quiet:
        print ("Started pyvserv keygen, ECC 384"); sys.stdout.flush()
    fnames = genkey()
    if not args.quiet:
        print("Generated files:")
        print("'" + fnames[0] + "'",  "'" + fnames[1] + "'")
    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
