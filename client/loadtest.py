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

from common import support, pycrypt, pyservsup, pyclisup
from common import pysyslog, comline, pypacker

for aa in range(100):
    subprocess.Popen("./pycli_ver.py")

