#!/usr/bin/env python3

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

import bluepy2

# Mirror 'c'  function versions

def version():
    return bluepy2.version()

def builddate():
    return bluepy2.builddate()

def encrypt(buff, passwd):
    rrr = bluepy2.encrypt2(buff.encode("cp437"), passwd.encode("cp437"))
    return rrr

def decrypt(buff, passwd):
    rrr = bluepy2.decrypt2(buff, passwd.encode("cp437"))
    return rrr.decode("cp437")

def tohex(buff):
    rrr = bluepy2.tohex(buff.encode("cp437"))
    return rrr
    
def fromhex(buff):
    rrr = bluepy2.fromhex(buff.encode("cp437"))
    return rrr.decode("cp437")
           
def destroy(buff, fill = 0):
    bluepy2.destroy(buff, fill)
    pass


