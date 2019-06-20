#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

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

def isprint(chh):
    if ord(chh) > 127:
        return False
    if ord(chh) < 32:
        return False
    if chh in ctrlchar:
        return False
    if chh in string.printable:
        return True
    return False

# ------------------------------------------------------------------------
# Return a hex dump formatted string

def hexdump(strx, llen = 16):
    lenx = len(strx)
    outx = ""
    for aa in range(lenx/16):
        outx += " "
        for bb in range(16):
            outx += "%02x " % ord(strx[aa * 16 + bb])
        outx += " | "
        for cc in range(16):
            chh = strx[aa * 16 + cc]
            if isprint(chh):
                outx += "%c" % chh
            else:
                outx += "."
        outx += " | \n"

    # Print remainder on last line
    remn = lenx % 16 ;   divi = lenx / 16
    if remn:
        outx += " "
        for dd in range(remn):
            outx += "%02x " % ord(strx[divi * 16 + dd])
        outx += " " * ((16 - remn) * 3)
        outx += " | "
        for cc in range(remn):
            chh = strx[divi * 16 + cc]
            if isprint(chh):
                outx += "%c" % chh
            else:
                outx += "."
        outx += " " * ((16 - remn))
        outx += " | \n"


    return(outx)


