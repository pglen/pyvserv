#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto.Hash import SHA512
from Crypto import Random
#from Crypto import StrongRandom

import support, crysupp, support

sys.path.append('../bluepy')
import bluepy

__doc__ =   \
'''
Encode / decode arbitrary data in a string. Preserves type, data.
on python 2 it is 8 bit clean.

Int Number            i         Float Number          f
Character             c         String                s
Binary                b
Extended              x         encoded as new packer string
List                  t         gets encoded as extended

use: pb  = packbin(); newdata = pb.encode_data(formatstr, arr_of_data)
orgdata  = pb.decode_data(newdata)

Empty format string string will use auto detect of types
'''

__all = ("autotype", "encode_data", "decode_data", "wrap_data", "unwrap_data", "verbose")


class InvalidType(Exception):

    def __init__(self, message):
         self.message = message

    def __str__(self):
        return(self.message)

# ------------------------------------------------------------------------

class packbin():

    def __init__(self):

        # -----------------------------------------------------------------------
        # This array of functions will call the appropriate function
        # Note the p' and 'g' are not in this type list, they denote
        # extended list

        self.typeact = [
                 ["i", self._got_int, self._found_int],
                 ["l", self._got_long, self._found_long],
                 ["f", self._got_float, self._found_float],
                 ["c", self._got_char, self._found_char],
                 ["s", self._got_str, self._found_str],
                 ["b", self._got_bin, self._found_bin],
                 ["t", self._got_list, self._found_list],
                 ["x", self._got_xtend, self._found_ext],

                 # No dictionary support (for now)
                 #["d", self._got_dict, self._found_dict],
                ]

        self.verbose = 0

    # These functions contain the ations on encode

    def _got_int(self, tt, var):
        #print ("got int", var)
        return "%c%d %d " %  (tt, 4, var)

    def _got_long(self, tt, var):
        #print ("got long", var)
        return "%c%d %d " %  (tt, 8, var)

    def _got_float(self, tt, var):
        #print ("got num", "'" + str(var) + "'")
        return "%c%d %f " %  (tt, 8, var)

    def _got_char(self, tt, var):
        #print ("got char", "'" + str(var) + "'")
        return "%c%d %c " %  (tt, 1, var)

    def _got_str(self, tt, var):
        #print ("got str", "'" + var + "'")
        return "%c%d '%s' " %  (tt, len(var), var)

    def _got_bin(self, tt, var):
        enco    = base64.b64encode(var)
        if sys.version_info[0] > 2:
            enco  = enco.decode("cp437")
        #print ("got bin", "'" + enco + "'")
        return "%c%d '%s' " %  (tt, len(enco), enco)

    def _got_list(self, tt, var):
        #print ("got list", "'" + str(var) + "'")
        enco = self.encode_data("", *var)
        return "%c%d '%s' " %  (tt, len(enco), enco)

    def _got_xtend(self, tt, var):
        #print ("got xtend", "'" + str(var) + "'")
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
        var = int(xstr[idxx:idxx+nnn])
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

    def _found_ext(self, xstr):
        idxx = 0
        #print ("found ext:", xstr)
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
        #print("ext:", "'" + sval + "'")
        idxx += slen + 2
        #print("idxx:", idxx, "var:", "{" + sval + "}", "next:", "'" + xstr[idxx:idxx+6] + "'")
        return idxx, sval

    def _found_bin(self, xstr):
        idxx = 0
        #print ("found bin:", xstr)
        idxx = 1
        nnn = xstr[idxx:].find(" ")
        if nnn < 0:
            print("bad encoding at ", xstr[idxx:idxx+5])
        slen = int(xstr[idxx:idxx+nnn])
        #print("slen", slen)
        if slen >= len(xstr):
            print("bad encoding at ", xstr[idxx:idxx+5])
        idxx += nnn + 2
        sval = str(xstr[idxx:idxx+slen])
        #print("bin:",  sval )
        deco   = base64.b64decode(sval)
        idxx += slen + 2
        #print("idxx:", idxx, "var:", "{" + sval + "}", "next:", "'" + xstr[idxx:idxx+6] + "'")
        return idxx, deco

    def _found_list(self, xstr):
        idxx = 0
        #print ("found list:", xstr)
        idxx = 1
        nnn = xstr[idxx:].find(" ")
        if nnn < 0:
            print("bad encoding at ", xstr[idxx:idxx+5])
        slen = int(xstr[idxx:idxx+nnn])
        #print("slen", slen)
        if slen >= len(xstr):
            print("bad encoding at ", xstr[idxx:idxx+5])
        idxx += nnn + 2
        sval = str(xstr[idxx:idxx+slen])
        deco = self.decode_data(sval)
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
            #print("typename:", type(aa).__name__)
            if type(aa).__name__ == "int":
                #print (aa)
                aaa += "i"

            elif type(aa).__name__ == "long":
                #print (aa)
                aaa += "l"

            elif type(aa).__name__ == "str":
                #print(crysupp.hexdump(aa, len(aa)))
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

            # Py 2 does not have tis ... safe to test in both
            elif type(aa).__name__ == "bytes":
                #print(crysupp.hexdump(aa, len(aa)))
                aaa += "b"

            elif type(aa).__name__ == "float":
                #print (aa)
                aaa += "f"
            elif type(aa).__name__ == "list":
                #print ("adding list")
                aaa += "t"

            #elif type(aa).__name__ == "dict":
            #    print ("adding dict")
            #    aaa += "d"

            else:
                raise InvalidType( "Unsupported type: "  + str(type(aa).__name__ ))

        #print("autotype res", aaa)
        return aaa

    ##########################################################################
    # Encode data into a string
    # Pass format string as the first element. Empty string switches on
    # autotype

    def encode_data(self, *formstr):

        if self.verbose > 4:
            print("formatstr:", formstr[0])

        if self.verbose > 3:
            for aa in formstr:
                print("got str:", aa)

        localf = formstr[0]
        if  localf == "":
            localf = self.autotype(formstr[1:])
            if self.verbose > 4:
                print("Autotype '" + localf + "'");

        packed_str = "pg "

        # Add the form string itself
        packed_str += self._got_str("s", localf)

        idx = 1;
        for bb in localf:
            found = 0
            #print("encoding item: ", type(formstr[idx]) )
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
            raise ValueError("Cannot decode, must begin with pg sequence")
            #print("pypacker decode: Error, must begin with 'pg '")
            #return ""

        idx = 3
        if dstr[3:4] != 's':
            raise ValueError("pypacker decode: Error, must have format string at the beginning")
            return ""

        flen = int(dstr[4])
        if flen > len(dstr) - idx:
            raise ValueError("pypacker decode: Error, bad decode: (overflow) at %d", idx)

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

# EOF