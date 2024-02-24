#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, subprocess

from Crypto import Random

# Set parent as module include path
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument("-c", '--count', dest='count', type=int,
                    default=3,
                    help='Number of processes default: 3)')

parser.add_argument("-v", '--verbose', dest='verbose',
                    default=0,  action='count',
                    help='verbocity on (default: off)')

parser.add_argument("-f", '--file', dest='file',  nargs='?',
                    default="./pycli_ver.py", help='start file')

args = parser.parse_args()

from common import support, pycrypt, pyservsup, pyclisup
from common import pysyslog, comline

for aa in range(args.count):
    subprocess.Popen(args.file)

