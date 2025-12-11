#!/usr/bin/env python3

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512

import os, sys, getopt, signal, select, socket, time, struct
import random, stat, subprocess
import argparse

from Crypto import Random

# This repairs the path from local run to pip run.
try:
    from pyvcommon import support
    base = os.path.dirname(os.path.realpath(support.__file__))
    sys.path.append(os.path.join(base, "."))
except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    from pyvcommon import support

from pyvcommon import support, pycrypt, pyclisup
from pyvcommon import pysyslog, comline

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument("-c", '--count', dest='count', type=int,
                    default=3,
                    help='Number of processes default: 3)')

parser.add_argument("-v", '--verbose', dest='verbose',
                    default=0,  action='count',
                    help='verbocity on (default: off)')

parser.add_argument("-f", '--file', dest='file',  nargs='?',
                    default="./pyvcli_ver.py", help='start file')

args = parser.parse_args()

def mainfunct():
    if sys.version_info[0] < 3:
        print("Warning! This script was meant for python 3.x")
        sys.exit()
    for aa in range(args.count):
        subprocess.Popen([args.file,])

    #print("Done")

if __name__ == '__main__':
    mainfunct()

# EOF
