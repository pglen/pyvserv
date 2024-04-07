#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512

base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base, '../'))
#sys.path.append(os.path.join(base, '../../'))

import support, crysupp, pysyslog
import pyvpacker

# ------------------------------------------------------------------------
# Test harness

if __name__ == '__main__':

    pysyslog.init_loggers(("system", "system.log"), ("replic", "replic.log"))

    pysyslog.syslog("Hello syslog", level = pysyslog.WARN)
    pysyslog.syslog("Hello syslog", level = pysyslog.DEBUG)
    pysyslog.syslog("Hello syslog", level = pysyslog.INFO)
    pysyslog.syslog("New entry")

    pysyslog.repliclog("Hello repliclog", level = pysyslog.WARN)
    pysyslog.repliclog("Hello repliclog", level = pysyslog.DEBUG)
    pysyslog.repliclog("Hello repliclog", level = pysyslog.INFO)
    pysyslog.repliclog("New entry")

# EOF
