#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

from Crypto import Random
import support

begtag = " -- DIGIBANK ENCRYPTED BEGIN --\n"
endtag = " -- DIGIBANK ENCRYPTED ENDED --\n"

refmessage = '\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    [[[Message to be encrypted. Here we go ]]]\n\
    '

ctrlchar = "\n\r| "

# ------------------------------------------------------------------------
# corrected to handle unicode accidental

def isprint(chh):

    try:
        if ord(chh) > 127:
            return False
        if ord(chh) < 32:
            return False
        if chh in ctrlchar:
            return False
        if chh in string.printable:
            return True
    except:
        pass

    return False

# ------------------------------------------------------------------------
# Return a hex dump formatted string

def hexdump(strin, llen = 16):

    if type(strin) == str:
        strx = bytes(strin, "cp437")
    else:
        strx = strin

    outx = "" ;  lenx = len(strx)

    try:
        for aa in range(int(lenx/16)):
            outx += " "
            for bb in range(16):
                try:
                    outx += "%02x " % strx[aa * 16 + bb]
                except:
                    support.put_exception("hex ??")
                    outx +=  "?? "

            outx += " | "
            for cc in range(16):
                chh = chr(strx[aa * 16 + cc])
                if isprint(chh):
                    outx += "%c" % chh
                else:
                    outx += "."
            outx += " | \n"

        # Print remainder on last line
        remn = lenx % 16 ;   divi = int(lenx / 16)
        if remn:
            outx += " "
            for dd in range(remn):
                try:
                    outx += "%02x " % strx[divi * 16 + dd]
                except:
                    support.put_exception("hexnum ??")
                    outx +=  "?? "

            outx += " " * ((16 - remn) * 3)
            outx += " | "
            for cc in range(remn):
                chh = chr(strx[divi * 16 + cc])
                if isprint(chh):
                    outx += "%c" % chh
                else:
                    outx += "."

            outx += " " * ((16 - remn))
            outx += " | \n"
    except:
        print("Error on hexdump", sys.exc_info())
        support.put_exception("hexdump")

    return(outx)

# Generate time stamped random string

def trandstr(slen):

    sss = ""
    rrr = Random.new().read(slen)
    for aa in rrr:
        sss += "%02x" % (aa % 255)
    sss += "%08x" % int(time.time())
    #print("ttt %02x" % int(time.time()))
    rrr2 = Random.new().read(slen)
    for aa in rrr2:
        sss +="%02x" % (aa % 255)
    return sss

# Return date embedded in random str

def getrstrtme(strx):

    xlen = len(strx)
    xlen2 = xlen // 2
    return strx[xlen2-4:xlen2+4]

if __name__ == '__main__':
    hexdump("12345")




