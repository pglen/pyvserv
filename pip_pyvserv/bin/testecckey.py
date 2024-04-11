#!/home/peterglen/pgpygtk/pyvserv/pip_pyvserv/bin/python3
# coding=utf-8

import os, sys, time, base64

from collections import OrderedDict

#base = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(base,  'pyvecc'))
sys.path.append(os.path.join('pyvecc'))

from pyvecc.Key import Key

def mainfunc():

    k = Key.generate(256)

    xp = k.export_pub()
    print("pub:")
    print(xp)
    kkk = Key.import_pub(xp)
    print(kkk)
    print("valid:", kkk.validate())

    print("priv:")
    xpp = k.export_priv()
    print(xpp)
    kkkk = Key.import_priv(xpp)
    print(kkkk)
    print("valid:", kkkk.validate())

    print("fin print:", k.fingerprint())
    print("fin print:", kkkk.fingerprint())
    print("kid:", k.keyid())

    #print("pub:", k._pub)
    #print("priv:", k._priv)

if __name__ == '__main__':
    mainfunc()

