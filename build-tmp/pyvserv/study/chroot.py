#!/usr/bin/python

import os, sys

# To set the current root path to /tmp/user
os.chroot("/pyvserv")
print "Changed root path successfully!!"

import os, sys

print("rootdir2: ", os.getcwd())


