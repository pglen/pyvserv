#!/usr/bin/env python

from __future__ import print_function

import sys, os

sys.path.insert(0, os.path.abspath('./'))

import bluepy

if __name__ == '__main__':

    #print bluepy.__dict__

    print( "Version:   ", bluepy.version())
    print( "Builddate: ",  bluepy.builddate())
    print()
    
    buff = "Hello, this is a test string.";
    passw = "1234"

    if  len(sys.argv) > 1:
        buff = sys.argv[1]
    if  len(sys.argv) > 2:
        passw = sys.argv[2]
    
    print( "org:", "'" + buff + "'")              
    
    enc = bluepy.encrypt( buff, passw)
    #print( "enc:", "'" + enc + "'")
    
    hexenc = bluepy.tohex(enc)
    #print("enc:", "'" +  hexenc + "'")
    
    uex = bluepy.fromhex(hexenc)
    
    dec = bluepy.decrypt(uex, passw)
    print("dec:", "'" + dec + "'")
    
    #hexx = bluepy.tohex(buff)
    #print( "hex:   ", hexx)
    #print( "unhex:",  "'" +  uex +"'")
    
    bluepy.destroy(enc)
    #print( "enc dest", "'" + enc.decode("cp437") + "'")
    print()
    #print( "enc destroyed:", "'" + bluepy.tohex(enc) + "'")
           
    err = 0
    if dec != buff:
        print( "Test FAILED", file=sys.stderr)
        err = 1 
    
    sys.exit(err)

# EOF








