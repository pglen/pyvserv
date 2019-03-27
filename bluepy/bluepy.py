#!/usr/bin/env python

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

#if sys.version_info[0] < 3:
import bluepy_c

# Mirror 'c'  function versions

def version():
    return bluepy_c.version()

def builddate():
    return bluepy_c.builddate()

def encrypt(buff, passwd):
    rrr = bluepy_c.encrypt(buff.encode("cp437"), passwd.encode("cp437"))
    return rrr

def decrypt(buff, passwd):
    rrr = bluepy_c.decrypt(buff.encode("cp437"), passwd.encode("cp437"))
    return rrr.decode("cp437")

def tohex(buff):
    rrr = bluepy_c.tohex(buff);   #//buff.encode("cp437"))
    return rrr
    
def fromhex(buff):
    rrr = bluepy_c.fromhex(buff.encode("cp437"))
    return rrr.decode("cp437")
           
def destroy(buff, fill = 0):
    bluepy_c.destroy(buff, fill)
    pass





