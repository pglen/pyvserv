#!/usr/bin/env python

import os, sys, binascii

from pygcrypt import hashcontext

h = hashcontext.HashContext(algo='sha256')

#print dir(h)

print (binascii.hexlify(h.read()))

h.reset()
h.write("Hello")
print (binascii.hexlify(h.read()))

h.reset()
h.write("Hello2")
print (binascii.hexlify(h.read()))








