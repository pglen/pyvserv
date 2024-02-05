#!/usr/bin/env python3

from __future__ import print_function

import sys

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat

if len(sys.argv) < 3:
    print("use: chall.py from to files | wildcard");
    sys.exit(0)

# copy to backup
bbb = "backup"
if not os.path.isdir(bbb):
    os.mkdir(bbb)
for aa in sys.argv[2:]:
    if os.path.isfile(aa):
        #print (aa)
        bbtmp = bbb+os.sep + aa
        fh = open(aa, 'rt')
        fh2 = open(bbtmp, 'wt')
        while True:
            buff = fh.readline()
            if not buff:
                break
            fh2.write(buff)
        fh.close();  fh2.close()

#sys.exit()

for aa in sys.argv[2:]:
    if os.path.isfile(aa):
        #print (aa)
        aatmp= aa+".tmp"
        fh = open(aa, 'rt')
        fh2 = open(aatmp, 'wt')
        cnt = 0
        while True:
            buff = fh.readline()
            if not buff:
                break

            idx = 0
            for cc in range(10):
                idx = buff.find(sys.argv[1], idx)
                if idx  >= 0:
                    buff = buff[:idx] + sys.argv[2] + buff[idx+len(sys.argv[1]):]
                    #print (buff, end="")
                    cnt += 1
                else:
                    break

            fh2.write(buff)

        fh.close();  fh2.close()
        if cnt:
            ss = os.stat(aa)
            print (aa, cnt)
            os.unlink(aa)
            os.rename(aatmp, aa)
            os.chmod(aa, ss.st_mode)

        else:
            os.unlink(aatmp)

