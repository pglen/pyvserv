#!/usr/bin/env python

import os, crypt, getpass, pwd, spwd, sys
from Crypto import Random

while 1:
    sess_key = Random.new().read(1)
    print(sess_key)

#fp = open("randnumbers", "wb")
#fp.write(sess_key)
#fp.close()


