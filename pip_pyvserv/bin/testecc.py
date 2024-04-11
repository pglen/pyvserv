#!/home/peterglen/pgpygtk/pyvserv/pip_pyvserv/bin/python3
# coding=utf-8

import os, sys, time, base64

from Crypto import Random

from collections import OrderedDict

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  'pyvecc'))

from pyvecc.Key import Key

#org = b'random test string ' * 10
org2 = Random.new().read(30)
org = base64.b64encode(org2)

def mainfunc():

    ttt = time.time()
    k = Key.generate(256)
    print("key gen time %.3fms" % ((time.time() - ttt) * 1000) )

    print("org:")
    print(org2)

    ttt = time.time()
    sss = k.encrypt(org)
    print("encrypt time %.3fms" % ((time.time() - ttt) * 1000) )

    #print(s)

    ttt = time.time()
    ddd = k.decrypt(sss)
    print("decypt time %.3fms" % ((time.time() - ttt) * 1000) )

    ddd2 = base64.b64decode(ddd)
    print("dec:")
    print(ddd2)

if __name__ == '__main__':
    mainfunc()

# EOF

