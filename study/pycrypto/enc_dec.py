#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

gl_step  = 200
gl_step2 = 512

#gl_step2 = 512 * 4 / 3 + 2

#gl_c1 = ""
#gl_c2 = ""

# ------------------------------------------------------------------------
# package data into a counted buffer

def  enc_data(ppkey, message):

    #print("encrypt", message[:12] + " ...")
    #global gl_c1, gl_c2

    hhh = SHA.new(message)
    ddd = base64.b64encode(hhh.digest())

    ciphertext = ""; loopx = 0;  encstep = ppkey.size() / 8 / 3
    lll = len(message)
    #print("len, step, digest", lll, encstep, ddd)

    cipher = PKCS1_v1_5.new(ppkey)
    while True:
        if loopx >= lll:
            break
        frag = message[loopx:loopx + encstep]
        if len(frag) < encstep:
            frag += " " * (encstep - len(frag))
        loopx += encstep
        tmp = cipher.encrypt(frag)
        #print("enc", len(tmp))
        ciphertext += tmp

    #gl_c1 =  ciphertext
    eee = base64.b64encode(ciphertext)

    #print ("eee", eee)
    form = "iiii%ds%ds" % (len(ddd), len(eee))
    #print("f1", form)

    # Pack into a comprehensive unit
    res = struct.pack(form, len(message), encstep, len(ddd), len(eee), ddd,  eee)

    #print("res", res)
    return res

# ------------------------------------------------------------------------

def  dec_data(pxkey, res):

    #print("decrypt")
    #global gl_c1, gl_c2

    # Reproduce format string:
    xlen, xstep, dddlen, eeelen = struct.unpack("iiii", res[0:16])

    form = "iiii%ds%ds" % (dddlen, eeelen)
    #print("f2", form)

    # Unpack into components
    tmp1, tmp2, tmp3, tmp4, ddd, ciphertext2 = struct.unpack(form, res)

    #print ("len, step, digest", xlen, xstep, ddd)
    #print ("eee", ciphertext2 )
    ciphertext = base64.b64decode(ciphertext2)
    lll = len(ciphertext)

    #c2 = ciphertext

    message = "";  loopx = 0;  decstep = pxkey.size() / 8 + 1
    sentinel = Random.new().read(SHA.digest_size)

    #print("senti", sentinel)
    #print("decstep", decstep)
    cipher2 = PKCS1_v1_5.new(pxkey)
    while True:
        if loopx >= lll:
            break
        frag = ciphertext[loopx:loopx + decstep]
        if len(frag) < decstep:
            #print ("dec partial", frag)
            frag += " " * (decstep - len(frag))

        #print("dec", len(frag)) #, frag)
        tmp = cipher2.decrypt(frag, sentinel)

        if(sentinel == tmp):
            print("Bad decryption");
        loopx += decstep
        message += tmp

    fin = message[0:xlen]
    hhh2 = SHA.new(fin)
    ddd2 = base64.b64encode(hhh2.digest())

    #print("digests:", ddd, ddd2)
    if ddd != ddd2:
        print ("bad digest")

    return  fin


# read key file, convert to "\n"
def getfile(kname):
    kkk = open(kname, 'rb').read()
    # Convert line end
    sss = str.split(kkk, "\r\n")
    rrr = "";
    for aa in sss:
        rrr += aa + "\n"
    #print ("got key:", rrr )
    return rrr

message = "\
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
[[[Message to be encrypted. Here we go ]]]\n\
"

#print("plain len", len(message))

dsize = SHA.digest_size

#print ("deco:", messaged)

bname = "keys/436c5c2b080d484c"

privname = bname + '.pem'
pubname =  bname + '.pub'

gl_pkey = RSA.importKey(getfile(pubname))
gl_xkey = RSA.importKey(getfile(privname))

ciphertext = enc_data(gl_pkey, message)

#print ("enc:", ciphertext)

message2 = dec_data(gl_xkey, ciphertext)

#print ("gl_c1", gl_c1)
#print ("gl_c2", gl_c2)

'''
if gl_c1 == gl_c2:
    print ("Cy Text delivery OK")
else:
    print ("Cy Text delivery ERR")
'''

#print ("decr:", message2)

#message3 = message2[:-dsize]

#print("orig:\n" +  "'" + message + "'")
#print("decr:\n" +  "'" + message2 + "'")

if message == message2:
    print ("Text delivery OK")
else:
    print ("Text delivery ERROR")


digest2 = SHA.new(message2[:-dsize]).digest()

#print ("digest2:", digest2)

#
#if digest2 == message2[-dsize:]:                # Note how we DO NOT look for the sentinel
#    print ("Encryption was correct.")
#else:
#    print ("Encryption was not correct.")
#

if __name__ == '__main__':
    pass
    #print( "test")






