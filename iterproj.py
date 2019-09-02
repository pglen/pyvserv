#!/usr/bin/env python

from __future__ import print_function

import os, sys, glob, string, time,  traceback, getopt, random
import subprocess

#!/usr/bin/env python

relarr = []
rel = "."


def gotfile(fname):

    print ("got file", fname)
    gotext = [".pyc", ".o", ".so", ".pem", ".pub", ]
    eee = os.path.splitext(fname)
    for aa in gotext:
        if aa == eee[1]:
            return

    if "__pycache__" in fname:
        return

    #ret = subprocess.Popen(["md5sum", os.path.basename(fname)])
    #if ret.returncode:
    #    print ("camnnot exec", fname)


def listit(cc):
    global rel

    print("listit", cc)

    arr = glob.glob(cc + "/*")
    print(arr)
    for aa in arr:
        bb = rel + "/" + os.path.basename(aa)
        if not os.path.isdir(bb):
            gotfile(bb)

    for aa in arr:
        #print ("aa", aa)
        bb = rel + "/" + os.path.basename(aa)
        ss =  os.stat(bb)
        if os.path.isdir(bb):
            pass
            #print  ("dir", aa)
            relarr.append(rel)
            rel += "/" + aa
            #os.chdir(aa)
            listit(rel);
            rel = relarr.pop()
            #os.chdir("..")
        else:
            #print  ("file", os.getcwd(), aa)
            #gotfile(rel + "/" + aa)
            pass

if __name__ == '__main__':
    listit("./")
