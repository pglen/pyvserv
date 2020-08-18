#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto.Hash import SHA512
from Crypto import Random
#from Crypto import StrongRandom

import support, crysupp, support, pypacker

sys.path.append('../bluepy')
import bluepy

# If comm is with no keys, still do some mudding

defkey = "12345678"

# ------------------------------------------------------------------------
# Wrap everything into an encrypted buffer

class   wrapper():

    def __init__(self):
        self.pb = pypacker.packbin()
        self.rr = Random.new()

        # Seed random;
        for aa in range(10):
            self.rr.read(5)

        #print("py version", sys.version_info[0])


    # Wrap data in a hash, compress, base64
    def wrap_data(self, key, xddd):

        randx = [self.rr.read(16)]
        randx += xddd

        #print ("  Carrier:", support.hexstr(randx[0]));

        #print ("\nddd=", xddd, "\ntstr=", self.autotype(xddd))
        sss = self.pb.encode_data("", *randx)

        #print ("sss", sss);

        hh = SHA512.new();

        if sys.version_info[0] > 2:
            hh.update(sss.encode("cp437"))
        else:
            hh.update(sss)

        # test: damage the data
        #sss = sss[:110] + chr(ord(sss[10]) + 1) + sss[111:]

        #print ("  Hexdigest: ",hh.hexdigest())
        dddd = [hh.hexdigest(), sss]
        #print("dddd", dddd)

        ssss = self.pb.encode_data("", *dddd)

        if sys.version_info[0] > 2:
            ssss  = ssss.encode("cp437")

        fff = zlib.compress(ssss)

        if key:
            fff3 = bluepy.encrypt(fff, key)
        else:
            fff3 = bluepy.encrypt(fff, defkey)

        fff2 = base64.b64encode(fff3)

        #if sys.version_info[0] > 2:
        #   fff2 = fff2.decode("cp437")
        return fff2

    # Unrap data in a hash, de  base64, decompress,
    def unwrap_data(self, key, xddd):

        #print("unwrap_data", type(xddd), xddd)

        if sys.version_info[0] > 2:
            if type(xddd) == type(str):
                xddd = xddd.decode("cp437")

        fff2 = base64.b64decode(xddd)

        if key:
            fff3 = bluepy.decrypt(fff2, key)
        else:
            fff3 = bluepy.decrypt(fff2, defkey)

        fff = None
        try:
            fff = zlib.decompress(fff3)
        except:
            raise(ValueError("Cannot unzip received data"))

        if sys.version_info[0] > 2:
            fff = fff.decode("cp437")

        #print("fff:", fff)

        sss = self.pb.decode_data(fff)

        hh = SHA512.new();
        if sys.version_info[0] > 2:
            hh.update(sss[1].encode("cp437"))
        else:
            hh.update(sss[1])

        #print ("  Hexdigest2:", hh.hexdigest())
        if not hh.hexdigest() == sss[0]:
            raise ValueError("Mismatching hashes on wrapped data")

        #if sys.version_info[0] > 2:
        #    sss[1] = sss[1].decode("cp437")

        out = self.pb.decode_data(sss[1])
        #print ("  Carrier:", support.hexstr(out[0]));
        return out[1:]


if __name__ == '__main__':
    print("This was meant to be used as a module.")

# eof

