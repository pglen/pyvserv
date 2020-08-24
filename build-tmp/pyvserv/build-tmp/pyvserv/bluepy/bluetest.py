#!/usr/bin/env python3

from __future__ import print_function

import sys, os

sys.path.insert(0, os.path.abspath('./'))

def dumpx(ctrx):
    bb = ""
    if sys.version_info[0] < 3:
        for aa in ctrx:
            bb += "%02x" % ord(aa)
    else:
        for aa in ctrx:
            bb += "%02x" % aa
    return bb

import bluepy

if __name__ == '__main__':

    #print bluepy.__dict__

    #print( "Python Version:    ", "%d.%d.%d" % sys.version_info[:3])
    print( "Bluepoint Version: ", bluepy.version())
    print( "Builddate:         ",  bluepy.builddate())
    print()

    buff = "Hello, this is a test string.";
    passw = "1234"

    if  len(sys.argv) > 1:
        buff = sys.argv[1]
    if  len(sys.argv) > 2:
        passw = sys.argv[2]

    print( "org:", "'" + buff + "'")
    enc = bluepy.encrypt( buff, passw)

    #print("enz: '" + dumpx(enc) + "'")
    hexenc = bluepy.tohex(enc)
    print("enc:", "'" +  hexenc + "'")

    '''uex = bluepy.fromhex(hexenc)
    print("enc: '" + dumpx(uex) + "'")'''

    dec = bluepy.decrypt(enc, passw)
    if sys.version_info[0] >= 3:
        dec = dec.decode("cp437")
    print("dec:", "'" + dec + "'")
    #de2 = bluepy.decrypt(enc, passw)
    #print("de2:", "'" + dec + "'")

    #hexx = bluepy.tohex(buff)
    #print( "hex:   ", hexx)
    #print( "unhex:",  "'" +  uex +"'")

    bluepy.destroy(enc)
    #print( "edd:", "'" + bluepy.tohex(enc) + "'")

    err = 0
    if dec != buff:
        print( "Test FAILED", file=sys.stderr)
        err = 1

    sys.exit(err)

# EOF










