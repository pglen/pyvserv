#!/usr/bin/env python

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

#print(sys.version_info)

if sys.version_info[0] < 3:
    import bluepy_c
else:
    from array import array
    import bluepy3 as bluepy_c

# Mirror 'c'  function versions

def version():
    return bluepy_c.version()

def builddate():
    return bluepy_c.builddate()

def encrypt(buff, passwd):
    rrr = bluepy_c.encrypt(buff, passwd)
    return rrr

def decrypt(buff, passwd):
    rrr = bluepy_c.decrypt(buff, passwd)
    return rrr

def tohex(buff):
    rrr = bluepy_c.tohex(buff);   #//buff.encode("cp437"))
    return rrr

def fromhex(buff):
    rrr = bluepy_c.fromhex(buff)
    return rrr

def destroy(buff, fill = 0):
    bluepy_c.destroy(buff, fill)
    pass

OPEN = bluepy_c.OPEN
author = bluepy_c.author
dict = bluepy_c.__dict__



