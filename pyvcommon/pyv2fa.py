#!/usr/bin/env python

import time
import pyotp
import qrcode
import sys

#key = pyotp.random_base32()
key = "pyvserverkey"

#print(key)
#sys.exit(0)

# Obtain QR code for auth
#uri = pyotp.totp.TOTP(key).provisioning_uri(
#    name='Peter Glen',
#    issuer_name='PyVserver')
# Qr code generation step
#qrcode.make(uri).save("qr.png")

uri = "otpauth://totp/PyVserver:Peter%20Glen?secret=pyvserverkey&issuer=PyVserver"

print(uri)

"""Verifying stage starts"""

totp = pyotp.TOTP(key)

# verifying the code
while True:
  print(totp.verify(input(("Enter the Code : "))))
