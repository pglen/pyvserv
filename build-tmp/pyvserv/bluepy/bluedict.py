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
    
    #print( bluepy.dict)
    '''for aa in bluepy.dict.keys():
        print( aa )
        #print( bluepy.dict[aa].__doc__)
        #print( )
    '''
    
# EOF






