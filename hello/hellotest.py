#!/usr/bin/env python

import sys

import hello

if __name__ == '__main__':

    #print hello.__dict__
    
    print "Version:   ", hello.version()
    print "Builddate: ",  hello.builddate()
    #print "Const:     ", bluepy.bluepy.OPEN
    #print "Const:     ", bluepy.bluepy.author
    #print bluepy.bluepy.__dict__
    #print bluepy.bluepy.destroy.__doc__
    '''
    buff = "Hello, this is a test string ";  
    passw = "1234"
    
    if  len(sys.argv) > 1:
        buff = sys.argv[1]
    if  len(sys.argv) > 2:
        passw = sys.argv[2]
    
    print "'" + "org" + "'", "'" + buff + "'"
    enc = bluepy.bluepy.encrypt(buff, passw)
    print "'" + "enc"+ "'", enc
    hex = bluepy.bluepy.tohex(enc)
    print "hex", hex
    uex = bluepy.bluepy.fromhex(hex)
    print "uex", uex
    dec = bluepy.bluepy.decrypt(enc, passw)
    print "'" + "dec"+ "'", "'" + dec + "'"
    bluepy.bluepy.destroy(enc)
    print "enc", "'" + enc + "'"
    '''







