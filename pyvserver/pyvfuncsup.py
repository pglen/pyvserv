#!/usr/bin/env python

try:
    import pyotp
except:
    pyotp = None

import os, sys, getopt, signal, select, string
import datetime,  time, stat, base64, uuid

#import pyvpacker

from pyvcommon import support, pyservsup, pyclisup, pysyslog, pyvhash, pyvindex
from pyvserver import pyvstate

OK = "OK"
ERR = "ERR"

def wr(strx):
    ''' Wrap string with single quotes '''
    return "'" + strx + "'"

def _print_handles(self):
        ''' Debug helper '''
        open_file_handles = os.listdir('/proc/self/fd')
        print('open file handles: ' + ', '.join(map(str, open_file_handles)))

def check_chain_path(self, strp):

    chainp = os.path.normpath(pyservsup.globals.chaindir)
    #print("check:", strp)
    #print("root:", chainp)
    dpath = os.path.normpath(strp)
    #print("dpath", dpath)
    if dpath[:len(chainp)] != chainp:
        dpath = None
    return dpath

def check_payload_path(self, strp):

    paypath = os.path.normpath(pyservsup.globals.paydir)
    #print("check:", strp)
    #print("root:", chainp)
    dpath = os.path.normpath(strp)
    #print("dpath", dpath)
    if dpath[:len(paypath)] != paypath:
        dpath = None
    return dpath

def contain_path(self, strp):

    '''
        Make sure the path is pointing to our universe
    '''
    dname = support.unescape(strp);

    #print("dname", dname)
    #print("self.resp.dir", self.resp.dir)
    #print("self.resp.cwd", self.resp.cwd)

    self.resp.dir = support.dirclean(self.resp.dir)
    self.resp.cwd = support.dirclean(self.resp.cwd)

    # Absolute path?
    if len(strp) > 0 and strp[0] == os.sep:
        dname2 = os.path.join(self.resp.cwd, dname)
    else:
        dname2 = os.path.join(self.resp.cwd, self.resp.dir, dname)

    #print("dname2", dname2)

    dname3 = support.dirclean(dname2)
    #print("dname3", dname3)

    dname4 = os.path.abspath(dname3)

    #print("base dir", self.resp.cwd)
    #print("resp_dir", self.resp.dir)

    #print("dname4", dname4)
    #print("slice", dname4[:len(self.resp.cwd)])

    # Compare roots
    if dname4[:len(self.resp.cwd)] != self.resp.cwd:
        return None

    return dname4


