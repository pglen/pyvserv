#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto.Hash import SHA512

import support

# ------------------------------------------------------------------------
# Encode / decode arbitrary data in a string. Preserves type, data.
# on python 2 it is 8 bit clean.

# Int Number            i
# float Number          f
# Character             c
# String                s
# Binary                b
# Extended              x
#
# use: pb  = packbin(); pb.encode_data(formatstr, arr_of_data)
# empty string will use auto detect of types
#

class packbin():

    def __init__(self):

        # -----------------------------------------------------------------------
        # This array of functions will call the appropriate function

        self.typeact = [
                 ["i", self._got_int, self._found_int],
                 ["l", self._got_long, self._found_long],
                 ["f", self._got_float, self._found_float],
                 ["c", self._got_char, self._found_char],
                 ["s", self._got_str, self._found_str],
                 ["b", self._got_bin, self._found_bin],
                 ["x", self._got_xtend, self._found_str],
                ]

    def _got_int(self, tt, var):
        #print ("found int", var)
        return "%c%d %d " %  (tt, 4, var)

    def _got_long(self, tt, var):
        #print ("found long", var)
        return "%c%d %d " %  (tt, 8, var)

    def _got_float(self, tt, var):
        #print ("found num", "'" + str(var) + "'")
        return "%c%d %f " %  (tt, 8, var)

    def _got_char(self, tt, var):
        #print ("found char", "'" + str(var) + "'")
        return "%c%d %c " %  (tt, 1, var)

    def _got_str(self, tt, var):
        #print ("found str", "'" + var + "'")
        return "%c%d '%s' " %  (tt, len(var), var)

    def _got_bin(self, tt, var):
        enco    = base64.b64encode(var)
        #print ("found bin", "'" + enco + "'")
        return "%c%d '%s' " %  (tt, len(enco), enco)

    def _got_xtend(self, tt, var):
        #print ("found xtend", "'" + str(var) + "'")
        return "%c%d [%s] " %  (tt, len(var), var)

    # ------------------------------------------------------------------------
    # Return var and consumed number of characters

    def _found_char(self, xstr):
        idxx = 0; var = 0
        #print ("found int:", xstr)
        if xstr[1:3] != "1 ":
            print("bad encoding at ", xstr[idxx:idxx+5])
            return idxx, var

        idxx = 3
        nnn = xstr[idxx:].find(" ")
        if nnn < 0:
            print("bad encoding at ", xstr[idxx:idxx+5])
            return idxx, var

        var = ord(xstr[idxx:idxx+nnn])
        #print("char:", "'" + chr(var) + "'")
        idxx += nnn + 1;
        #print("int idxx:", idxx, "var:", var, "next:", "'" + xstr[idxx:idxx+6] + "'")
        return idxx, chr(var)

    def _found_int(self, xstr):
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

    def _found_long(self, xstr):
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

    def _found_float(self, xstr):
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

    def _found_str(self, xstr):
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

    def _found_bin(self, xstr):
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
        #print("bin:", "'" + sval + "'")
        deco    = base64.b64decode(sval)
        idxx += slen + 2
        #print("idxx:", idxx, "var:", "{" + sval + "}", "next:", "'" + xstr[idxx:idxx+6] + "'")
        return idxx, deco

    def _eval_one(self, dstr, idx2):
        #print ("eval_one", dstr[idx2:])
        nstr = dstr[idx2:idx2+1]
        #print("nstr: ", "[" + nstr + "]")
        found = False; idx3 = 1; val = None
        for cc in self.typeact:
            if cc[0] == nstr:
                #print ("found", cc[0], cc[1], formstr[idx])
                if cc[2]:
                    idx3, val = cc[2](dstr[idx2:])
                found = True
        if not found:
            # We do not raise an exception, rather inform the use
            print("Warn: Invalid char in '%c' format string" % nstr)
        return idx3, val

    # Estabilish a proper format string autmatically
    def autotype(self, xdata):
        aaa = ""
        for aa in xdata:
            #print("type", aa, type(aa).__name__)
            if type(aa).__name__ == "int":
                aaa += "i"

            if type(aa).__name__ == "long":
                aaa += "l"

            if type(aa).__name__ == "str":
                # see if binary
                bbb = False
                for bb in aa:
                    if ord(bb) > 128:
                        bbb = True
                if bbb:
                    aaa += "b"
                else:
                    if len(aa) == 1:
                        aaa += "c"
                    else:
                        aaa += "s"

            if type(aa).__name__ == "float":
                aaa += "f"

        return aaa

    ##########################################################################
    # Encode

    def encode_data(self, *formstr):

        #for aa in formstr:
        #    print("formstr", aa)

        localf = formstr[0]
        if  localf == "":
            localf = self.autotype(formstr[1:])
            #print("Autotype:", localf);

        packed_str = "pg "

        # Add the form string itself
        packed_str += self._got_str("s", localf)

        idx = 1;

        for bb in localf:
            found = 0
            #print("bb", bb, end=" ")
            for cc in self.typeact:
                if cc[0] == bb:
                    #print ("found", cc[0], cc[1], formstr[idx])
                    if cc[1]:
                        packed_str += cc[1](bb, formstr[idx])
                    idx += 1
                    found = True
            if not found:
                raise ValueError("Invalid char in '%c' format string" % bb)

        if idx < len(formstr):
            raise ValueError("More data than chars in format string")

        return packed_str

    def decode_data(self, dstr):

        #print ("---org:\n", dstr, "org---")

        if dstr[0:3] != 'pg ':
            print("error, must begin with 'pg '")
            return ""

        idx = 3
        if dstr[3:4] != 's':
            print("error, must have format string at the beginning")
            return ""

        flen = int(dstr[4])
        if flen > len(dstr) - idx:
            raise ValueError("Bad decode: (overflow) at %d", idx)

        #print("flen", flen)
        idx = 7
        fstr = dstr[idx:idx+flen]
        #print("fstr: ", "[" + fstr + "]")
        idx += flen + 2;

        try:
            arr = []
            while True:
                if idx >= len(dstr):
                    break
                idx2, val = self._eval_one(dstr, idx)
                #print("idx:", idx, "val:", val)
                idx += idx2
                arr.append(val)
        except:
            #print("Exception at:", idx, "val:", val)
            raise

        return arr

    # Wrap data in a hash, compress, base64
    def wrap_data(self, xddd):

        #print ("\nddd=", xddd, "\ntstr=", self.autotype(xddd))
        sss = self.encode_data("", *xddd)
        #print ("sss", sss);
        hh = SHA512.new(); hh.update(sss)
        #print (hhh, sss)
        dddd = [hh.hexdigest(), sss]
        #print("dddd", dddd)
        ssss = self.encode_data("sx", *dddd)

        fff = zlib.compress(ssss)
        fff2 = base64.b64encode(fff)

        return fff2

    # Unrap data in a hash, de  base64, decompress,
    def unwrap_data(self, xddd):

        fff2 = base64.b64decode(xddd)
        fff = zlib.decompress(fff2)

        #print ("\nddd=", xddd, "\ntstr=", self.autotype(xddd))
        sss = self.decode_data(fff)
        #print ("sss", sss);
        hh = SHA512.new(); hh.update(sss[1])
        #print (hhh, sss)
        #print ("2digest", [hh.hexdigest(), sss[0]])
        if not hh.hexdigest() == sss[0]:
            raise ValueError("Mismatching hashes on data")

        return sss[1]

# ------------------------------------------------------------------------
# test harness


if __name__ == '__main__':

    from Crypto import Random

    rrr =  "mTQdnL51eKnblQflLGSMvnMKDG4XjhKa9Mbgm5ZY9YLd" \
            "/SxqZZxwyKc/ZVzCVwMxiJ5X8LdX3X5VVO5zq/VBWQ=="

    print ("Should print 4 successes and a sample output")

    pb = packbin()
    #bindat = Random.new().read(64)
    #print("bindat64:\n", base64.b64encode(bindat))

    bindat = base64.b64decode(rrr)

    org = [ 33, "sub", 'd', "longer str here with \' and \" all crap", 33, 33333333.2, bindat ]
    #print ("org:\n", org)

    #eee = pb.encode_data("iscsfb", *org)
    eee = pb.encode_data("", *org)
    #print ("eee:\n", eee)

    ddd = pb.decode_data(eee)
    #print ("ddd:\n", ddd)

    if not org == ddd:
        print ("Broken decode")
        print ("eee:\n", eee)
    else:
        print ("Success ", end="")

    #sys.exit(0)

    org2 = [ 22, 444, "data", 123.456, 'a', eee]
    #print ("org2:\n", org2)
    eee2 = pb.encode_data("ilsfcx", *org2)
    #print ("eee2:\n", eee2)
    ddd2 = pb.decode_data(eee2)
    #print ("ddd2:\n", ddd2)

    if not org2 == ddd2:
        print ("Broken decode")
        print ("eee2:\n", eee2)
    else:
        print ("Success ", end="")

    fff = zlib.compress(eee)
    #print("compressed %.2f" % (float(len(fff)) / len(eee)) )
    hhh = zlib.decompress(fff)
    if not eee == hhh:
        print ("Broken unzip")

    ddd3 = pb.decode_data(eee2)
    #print("ddd3", ddd3)
    ggg = pb.decode_data(ddd3[5])
    #print("ggg", ggg)

    if not org == ggg:
        print ("Broken decode")
    else:
        print ("Success ", end="")

    www = pb.wrap_data(org)
    #print ("www", www)

    # damage the data
    zzz = www[:100] + chr(ord(www[100]) + 1) + www[101:]
    # OK data
    zzz = www[:100] + www[100:]
    #print (len(zzz), len(www), chr(ord(www[100]) + 1))


    ooo = pb.unwrap_data(zzz)
    oooo = pb.decode_data(ooo)

    if not org == oooo:
        print ("Broken unwrap")
    else:
        print ("Success ", end="")

    print()

    zzzz = support.breaklines(zzz, 75)
    print (zzzz)

# eof


