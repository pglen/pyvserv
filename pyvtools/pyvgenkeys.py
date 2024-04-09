#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

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
    #sys.path.append(os.path.join(sf, "pyvgui"))
    #sys.path.append(os.path.join(sf, "pyvgui", "guilib"))

except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    #sys.path.append(os.path.join(base, "..", "pyvgui"))
    #sys.path.append(os.path.join(base, "..", "pyvgui", "guilib"))
    from pyvcommon import support

#for aa in sys.path:
#    print(aa)

#print("Load:", sys.path[-1])

import pyvgenkey
import argparse

parser = argparse.ArgumentParser(description='Genetrate ECC keypair for pyvserv.')

parser.add_argument("-v", '--verbose', dest='verbose',
                    default=0,  action='count',
                    help='verbocity on (default: off)')

parser.add_argument("-x:", '--max', dest='mxcount',
                    default=25, type=int,
                    help='Max mumber of keys. Default 25')

parser.add_argument("-m:", '--homedir', dest='homedir',
                    default="pyvserver",  action='store',
                    help='pyvserv home directory (default: ~/pyvserver)')

def mainfunct():

    args = parser.parse_args()

    #if not pyvgenkey.is_power_of_two(args.bits):
    #    print("Bitness must be a power of 2")
    #    sys.exit(1)

    pyvgenkey.position(args)
    #print("Current dir:     ", os.getcwd())
    print ("Started pyvserv continuous keygen. Press Ctrl-C to abort.")
    cnt = 0
    while(True):
        if cnt >= args.mxcount:
            break
        cnt += 1;
        sys.stdout.flush()
        files = pyvgenkey.genkey()
        print ("\rKey %-4d %s %s " % (cnt, files[0], files[1]), end="");
        # Ease on hogging the system
        sleepy  = 0.2
        if cnt > 100:
            sleepy = 1
        elif cnt > 10:
            sleepy = .5
        time.sleep(sleepy)
    print()

if __name__ == '__main__':
    mainfunct()

# EOF