#!/usr/bin/env python

from __future__ import print_function

import sys, os

sys.path.insert(0, os.path.abspath('./'))

import bluepy

if __name__ == '__main__':

    #print bluepy.__dict__

    print( "Version:   ", bluepy.version())
    print( "Builddate: ",  bluepy.builddate())
    
    print( "Const:     ", bluepy.OPEN)
    print( "Const:     ", bluepy.author)
    #print( bluepy.__dict__)

    for aa in bluepy.__dict__.keys():
        print( aa)
        print( bluepy.__dict__[aa].__doc__)
        print( )

# EOF





