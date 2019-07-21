#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

# ------------------------------------------------------------------------
# Encode / decode arbitrary data in a string. Preserves type, data.
# on python 2 it is 8 bit clean.

# Int Number            i
# float Number          f
# Character             c
# String                s
# Binary                b
# Extended              x

def got_int(tt, var):
    #print ("found int", var)
    return "%c%d %d " %  (tt, 4, var)

def got_long(tt, var):
    #print ("found int", var)
    return "%c%d %d " %  (tt, 8, var)

def got_float(tt, var):
    #print ("found num", "'" + str(var) + "'")
    return "%c%d %f " %  (tt, 8, var)

def got_char(tt, var):
    #print ("found char", "'" + str(var) + "'")
    return "%c%d %c " %  (tt, 1, var)

def got_str(tt, var):
    #print ("found str", "'" + var + "'")
    return "%c%d '%s' " %  (tt, len(var), var)

def got_xtend(tt, var):
    #print ("found xtend", "'" + str(var) + "'")
    return "%c%d [%s] " %  (tt, len(var), var)


# ------------------------------------------------------------------------
# Return var and consumed number of characters

def found_char(xstr):
    idxx = 0; var = 0
    #print ("found int:", xstr)
    if xstr[1:3] != "1 ":
        print("bad encoding at ", xstr[idxx:idxx+5])
    idxx = 3
    nnn = xstr[idxx:].find(" ")
    if nnn < 0:
        print("bad encoding at ", xstr[idxx:idxx+5])
    var = ord(xstr[idxx:idxx+nnn])
    #print("char:", "'" + chr(var) + "'")
    idxx += nnn + 1;
    #print("int idxx:", idxx, "var:", var, "next:", "'" + xstr[idxx:idxx+6] + "'")
    return idxx, var

def found_int(xstr):
    idxx = 0; var = 0
    #print ("found int:", xstr)
    if xstr[1:3] != "4 ":
        print("bad encoding at ", xstr[idxx:idxx+5])
    idxx = 3
    nnn = xstr[idxx:].find(" ")
    if nnn < 0:
        print("bad encoding at ", xstr[idxx:idxx+5])
    var = int(xstr[idxx:idxx+nnn])
    #print("int:", var)
    idxx += nnn + 1;
    #print("int idxx:", idxx, "var:", var, "next:", "'" + xstr[idxx:idxx+6] + "'")
    return idxx, var

def found_long(xstr):
    idxx = 0; var = 0
    #print ("found long:", xstr)
    if xstr[1:3] != "8 ":
        print("bad encoding at ", xstr[idxx:idxx+5])
    idxx = 3
    nnn = xstr[idxx:].find(" ")
    if nnn < 0:
        print("bad encoding at ", xstr[idxx:idxx+5])
    var = long(xstr[idxx:idxx+nnn])
    #print("long:", var)
    idxx += nnn + 1;
    #print("long idxx:", idxx, "var:", var, "next:", "'" + xstr[idxx:idxx+6] + "'")
    return idxx, var

def found_float(xstr):
    idxx = 0; var = 0
    #print ("found long:", xstr)
    if xstr[1:3] != "8 ":
        print("bad encoding at ", xstr[idxx:idxx+5])
    idxx = 3
    nnn = xstr[idxx:].find(" ")
    if nnn < 0:
        print("bad encoding at ", xstr[idxx:idxx+5])
    var = float(xstr[idxx:idxx+nnn])
    #print("float:", var)
    idxx += nnn + 1;
    #print("float idxx:", idxx, "var:", var, "next:", "'" + xstr[idxx:idxx+6] + "'")
    return idxx, var

def found_str(xstr):
    idxx = 0
    #print ("found str:", xstr)
    idxx = 1
    nnn = xstr[idxx:].find(" ")
    if nnn < 0:
        print("bad encoding at ", xstr[idxx:idxx+5])
    slen = int(xstr[idxx:idxx+nnn])
    #print("slen", slen)
    if slen >= len(xstr):
        print("bad encoding at ", xstr[idxx:idxx+5])
    idxx += nnn + 2
    sval = xstr[idxx:idxx+slen]
    #print("str:", "'" + sval + "'")
    idxx += slen + 2
    #print("idxx:", idxx, "var:", "{" + sval + "}", "next:", "'" + xstr[idxx:idxx+6] + "'")
    return idxx, sval

# -----------------------------------------------------------------------
# This will call the appropriate function

typeact = [
         ["i", got_int, found_int],
         ["l", got_long, found_long],
         ["f", got_float, found_float],
         ["c", got_char, found_char],
         ["s", got_str, found_str],
         ["x", got_xtend, found_str],
        ]

def eval_one(dstr, idx2):
    #print ("eval_one", dstr[idx2:])
    nstr = dstr[idx2:idx2+1]
    #print("nstr: ", "[" + nstr + "]")
    idx3 = 1; val = None
    for cc in typeact:
        if cc[0] == nstr:
            #print ("found", cc[0], cc[1], formstr[idx])
            if cc[2]:
                idx3, val = cc[2](dstr[idx2:])
            found = True
    if not found:
        print("Warn: Invalid char in '%c' format string" % bb)
    return idx3, val

##########################################################################
# Encode

def encode_data(*formstr):

    #for aa in formstr:
    #    print("formstr", aa)

    packed_str = "pg "

    # Add the form string itself
    packed_str += got_str("s", formstr[0])

    idx = 1;
    for bb in formstr[0]:
        found = 0
        #print("bb", bb, end=" ")
        for cc in typeact:
            if cc[0] == bb:
                #print ("found", cc[0], cc[1], formstr[idx])
                if cc[1]:
                    packed_str += cc[1](bb, formstr[idx])
                idx += 1
                found = True
        if not found:
            print("Warn: Invalid char in '%c' format string" % bb)

    return packed_str


def decode_data(dstr):

    print ("---org:\n", dstr)
    print ("---org.")

    if dstr[0:3] != 'pg ':
        print("error, must begin with 'pg '")
        return ""
    idx = 3
    if dstr[3:4] != 's':
        print("error, must have format string at the beginning")
        return ""

    flen = int(dstr[4])
    if flen > len(dstr) - idx:
        print("Bad decode (overflow)")
        return ""

    #print("flen", flen)
    idx = 7
    fstr = dstr[idx:idx+flen]
    #print("fstr: ", "[" + fstr + "]")
    idx += flen + 2;

    arr = []
    while True:
        if idx >= len(dstr):
            break
        idx2, val = eval_one(dstr, idx)
        #print("idx:", idx, "val:", val)
        idx += idx2
        arr.append(val)
    return arr

sss = encode_data("iss", 33, "sub", "longer str here with \' and \" all crap")
eee = encode_data("ilsfcx", 22, 444, "data", 123.456, "a", sss)
fff = zlib.compress(eee)
print("compressed", len(eee), "->", len(fff))
ggg = zlib.compress(fff)
ddd = decode_data(eee)

print(ddd)

ggg = decode_data(ddd[5])

print(ggg)


