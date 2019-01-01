#!/usr/bin/env python

import os, sys, binascii

from pygcrypt import ciphers

c = ciphers.Cipher(b'AES', u'CBC')
#print dir(c)

org = b'0123456789ABCDEF'
print ("original:", org, binascii.hexlify(org))

c.key = '0123456789ABCDEF'
c.iv = '0123456789ABCDEF'
encrypted = c.encrypt(org)
print ("encrypted:", binascii.hexlify(encrypted))

cc = ciphers.Cipher(b'AES', u'CBC')
#c.reset()
cc.key = '0123456789ABCDEF'
cc.iv = '0123456789ABCDEF'

decrypted = cc.decrypt(encrypted)

print ("decrypted:", binascii.hexlify(decrypted), decrypted)










