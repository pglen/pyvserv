#!/usr/bin/env python3

from __future__ import print_function

import sys
import bluepy

if __name__ == '__main__':

    #print bluepy.__dict__

    print( "Version:   ", bluepy.version())
    print( "Builddate: ",  bluepy.builddate())
    #print( "Const:     ", bluepy.OPEN)
    #print( "Const:     ", bluepy.author)
    #print( bluepy.__dict__)

    '''for aa in bluepy.__dict__.keys():
        print( aa)
        print( bluepy.__dict__[aa].__doc__)
        print( )

    print( bluepy.destroy.__doc__)'''

    buff = "Hello, this is a test string ";
    passw = "1234"

    if  len(sys.argv) > 1:
        buff = sys.argv[1]
    if  len(sys.argv) > 2:
        passw = sys.argv[2]
    
    print( "'" + "org" + "'", "'" + buff + "'\n")              
    
    enc = bluepy.encrypt( buff, passw)
    print( "'" + "enc "+ "'", enc)
    
    dec = bluepy.decrypt(enc, passw)
    print( "'" + "dec"+ "'", "'" + dec + "'")
    
    hex = bluepy.tohex(buff)
    print( "hex:   ", hex)
    uex = bluepy.fromhex(hex)
    print( "unhex: '" +  uex +"'")
    
    bluepy.destroy(enc)
    #print( "enc dest", "'" + enc.decode("cp437") + "'")
    print( "enc dest", "'" + str(enc) + "'")
           
    err = 0
    if dec != buff:
        print( "Test FAILED", file=sys.stderr)
        err = 1 
    
    sys.exit(err)

# EOF


