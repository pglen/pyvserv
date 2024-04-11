#!/home/peterglen/pgpygtk/pyvserv/pip_pyvserv/bin/python3

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

#sys.path.append( "..")
import pyvpacker

# {pg s7 'iscsifd' i4 33 s3 'sub' c1 d s37
# 'longer str here with ' and " all crap' i4 33 f8 33333333.200000 d101 'pg s1 'a' a84 'pg s2 'tt' t29 'pg s2 'si' s4 'test' i4 1111 ' t30 'pg s2 'si' s5 'test2' i4 1112 ' ' ' }

# ------------------------------------------------------------------------
# Test harness

def mainfunc():

    pb = pyvpacker.packbin();
    pb.verbose = 3

    org = [ 33, "sub", 'd', "longer str here with \' and \" all crap",  33, 33333333.2,
                {"test": 1111, "test2": 1112, } ]

    if pb.verbose > 2:
        print ("Orgiginal data:\n", org)

    eeenc = pb.encode_data("", *org)

    if pb.verbose > 3:
        print("eeenc:\n", "{" + eeenc + "}")

    dddec = pb.decode_data(eeenc)
    if pb.verbose > 2:
        print("Decoded data:\n", str(dddec))

    if org == dddec:
        print("Data matches OK.")
    else:
        print("MISMATCH:", dddec)
        sys.exit(1)

if __name__ == '__main__':
    mainfunc()

