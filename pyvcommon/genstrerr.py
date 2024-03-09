#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

def errhash(strx):
    ret = 0
    for aa in strx:
        #print(aa)
        if aa.isalnum():
            bb = ord(aa)
            ret += bb
    return ret
    #return hex(ret)[2:]

errx = "No such file."
errx2 = "No such file"
erry = "Cannot open file"
errz = "Timeout occured, disconnecting."

print("Generating error numbers from strings")
print(errhash(errx),    errx, )
print(errhash(errx2),    errx2, )
print(errhash(erry),    erry, )
print(errhash(errz),    errz, )

