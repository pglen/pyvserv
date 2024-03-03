#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto.Hash import SHA512
from Crypto import Random
from Crypto.Cipher import AES

import support, crysupp, support, pyvpacker

#base = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(base, '../bluepy'))
#
#import bluepy.bluepy as bluepy

# If comm is with no keys, still do some mudding

defkey = "12345678"

import inspect
if inspect.isbuiltin(time.process_time):
    time.clock = time.process_time

# ------------------------------------------------------------------------
# Wrap everything into an encrypted buffer

class   wrapper():

    def __init__(self):
        self.pb = pyvpacker.packbin()
        self.rr = Random.new()
        self.pgdebug = 0
        # Seed random;
        for aa in range(10):
            self.rr.read(5)

        #print("py version", sys.version_info[0])

    # Wrap data in a hash, compress, base64
    #@support.timeit
    def wrap_data(self, key, xddd):

        #print("wrap_data:", type(key), type(xddd))

        if sys.version_info[0] > 2:
            if  type(key) == type(""):
                key = bytes(key, "utf-8")

        if self.pgdebug > 1:
            #support.shortdump("wrap_data key:", key)
            print("wrap_data key:", base64.b64encode(key[:12]), base64.b64encode(key[-12:]))
            print("xdd", xddd)

        #randx = [self.rr.read(16)]
        #randx += xddd
        #
        ##print ("  Carrier:", support.hexstr(randx[0]));
        #
        ##print ("\nddd=", xddd, "\ntstr=", self.autotype(xddd))
        #sss = self.pb.encode_data("", *randx)
        #
        #if self.pgdebug > 2:
        #    print ("sss", sss);

        #hh = SHA512.new();

        #if sys.version_info[0] > 2:
        #    hh.update(sss.encode("utf-8"))
        #else:
        #    hh.update(sss)

        # test: damage the data
        #sss = sss[:110] + chr(ord(sss[10]) + 1) + sss[111:]

        #print ("  Hexdigest: ",hh.hexdigest())
        #dddd = [hh.hexdigest(), sss]
        #print("dddd", dddd)

        #ssss = self.pb.encode_data("", *dddd)
        ssss = self.pb.encode_data("", *xddd)
        #print(type(ssss))
        ssss  = bytes(ssss, "utf-8")

        # Compress throttled to low
        fff = zlib.compress(ssss, 1)
        #fff = ssss

        # use AES and Bluepoint
        if key:
            #fff2 = bluepy.encrypt(fff, key)
            fff2 = fff

            key2 = key[:32]; key3 = key[-8:]
            cipher = AES.new(key2, AES.MODE_CTR,
                        use_aesni=True, nonce = key3)
            fff3 = cipher.encrypt(fff2)
            #fff3 = fff2
        else:
            #fff3 = bluepy.encrypt(fff, defkey)
            fff3 = fff

        #print (len(fff), end= ' ')
        return fff3

    # --------------------------------------------------------------------
    # Unrap data in a hash, DE base64, decompress,

    #@support.timeit
    def unwrap_data(self, key, xddd):

        #print("unwrap_data:", type(key), type(xddd))

        if sys.version_info[0] > 2:
            if  type(key) == type(""):
                key = key.encode("utf-8")

        if self.pgdebug > 1:
            print("unwrap_data key:", base64.b64encode(key[:12]), base64.b64encode(key[-12:]))
            print("unwrap_data data:", xddd)

        #if sys.version_info[0] > 2:
        #    if type(xddd) != type(""):
        #        xddd = xddd.decode("utf-8")

        #fff2 = xddd.encode("utf-8")
        #fff2 = bytes(xddd, "utf-8")
        fff2 = xddd

        if key:
            key2 = key[:32]; key3 = key[-8:]
            cipher = AES.new(key2, AES.MODE_CTR,
                        use_aesni=True, nonce = key3)
            fff3 = cipher.decrypt(fff2)
            #fff3 = fff2

            #fff4 = bluepy.decrypt(fff3, key)
            fff4 = fff3
        else:
            #fff3 = bluepy.decrypt(fff2, defkey)
            fff4 = fff2

        fff = zlib.decompress(fff4)
        #fff = fff4

        #if sys.version_info[0] > 2:
        #    fff = fff.decode("utf-8")

        if self.pgdebug > 2:
            print("fff:", fff)

        sss = self.pb.decode_data(fff)

        #hh = SHA512.new();
        #hh.update(sss)

        return sss

        #print ("  Hexdigest2:", hh.hexdigest())
        #if not hh.hexdigest() == sss[0]:
        #    raise ValueError("Mismatching hashes on wrapped data")

        #ttt = time.time()
        #out = self.pb.decode_data(sss[1])
        #print ("ttt=%f"  % (ttt - time.time()))
        #print ("  Carrier:", support.hexstr(out[0]));
        return out[1:]

if __name__ == '__main__':
    print("This was meant to be used as a module.")

# eof

