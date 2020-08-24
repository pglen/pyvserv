#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

from Crypto.Hash import SHA512
import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, subprocess

from Crypto import Random

sys.path.append('../common')
import support, pycrypt, pyservsup, pyclisup
import pysyslog, crysupp, pypacker


for aa in range(1000):
    subprocess.Popen("./pycli_ver.py")

