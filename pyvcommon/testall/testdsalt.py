#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time, traceback, random, uuid, datetime, base64

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..'))

import pyservsup

from testx import *

pyservsup.globals  = pyservsup.Global_Vars(__file__, "hello")

pwd = pyservsup.Passwd()

print (pwd)
hhh = pwd._dblsalt("hello")
print(hhh)
yyy = pwd._unsalt("hello", hhh)
print(yyy)

print("Hash compare: [True]",  hhh == yyy, end = " "); diff(True, hhh == yyy)

