#!/usr/bin/env python

import sys, os, readline, shutil, shlex, fnmatch , re

print("bulkrename", "from", sys.argv[1], "to", sys.argv[2])

lll = os.listdir(".")

xx = re.compile(sys.argv[1])
for aa in lll:
    #if fnmatch.fnmatch(aa, sys.argv[1]):

    #if regexfnmatch.fnmatch(aa, sys.argv[1]):
    mm = xx.match(aa)
    if mm:
        sss = mm.span()
        nnn = aa[:sss[0]] + \
                    sys.argv[2] + aa[sss[1]:]
        print("from:", aa)
        print("to", nnn)
        os.rename(aa, nnn)

