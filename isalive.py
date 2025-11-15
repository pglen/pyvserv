#!/usr/bin/env python3
import sys
sys.path.append("pyvcommon")
import pyclisup
ip = '127.0.0.1'
hand = pyclisup.CliSup()
ret = 1
try:
    resp2 = hand.connect(ip, 6666)
    ret = 0
except:
    print("Server Not alive")
    pass
sys.exit(ret)
# eof