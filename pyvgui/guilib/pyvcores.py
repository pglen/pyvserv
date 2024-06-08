#!/usr/bin/env python

import os, sys, getopt, signal, random, time, base64
import string, warnings, uuid, datetime, struct, io

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

from pyvguicom import pgutils

# Add this path to find local modules
base = os.path.dirname(pgutils.__file__)
sys.path.append(base)

from pyvguicom import pgbox
from pyvguicom import pgsimp
from pyvguicom import pggui
from pyvguicom import pgentry
from pyvguicom import pgtests

from pymenu import  *
from pgui import  *

import pyvrecsel, pgcal, config, passdlg, pymisc

from pyvcommon import pydata, pyservsup,  pyvhash, crysupp, pyvindex

from pydbase import twincore, twinchain

import pyvpacker

from Crypto.Cipher import AES

def votercore(dbname):

    ''' We let the core carry index reletedvars;
            make sure they do not collide. '''

    vcore = twincore.TwinCore(dbname, 0)
    vcore.hashname  = os.path.splitext(vcore.fname)[0] + ".hash.id"
    vcore.hashname2 = os.path.splitext(vcore.fname)[0] + ".hash.name"
    vcore.hashname3 = os.path.splitext(vcore.fname)[0] + ".hash.phone"
    vcore.hashname4 = os.path.splitext(vcore.fname)[0] + ".hash.email"
    return vcore

def votersave(vcore, uuu, enc):

    # Add index
    def callb(c2, id2):
        # Replicate fields from local data
        dddd = [uuu, enc.encode()]
        #print("dddd:", dddd)
        try:
            pyvindex.append_index(c2, vcore.hashname,  pyvindex.hash_id, dddd)
        except:
            print("exc save callb hash", sys.exc_info())
        try:
            pyvindex.append_index(c2, vcore.hashname2, pyvindex.hash_name, dddd)
        except:
            print("exc save callb name", sys.exc_info())
            #pgutils.put_exception("save idx")
        try:
            pyvindex.append_index(c2, vcore.hashname3, pyvindex.hash_email, dddd)
        except:
            print("exc save callb email", sys.exc_info())

        try:
            pyvindex.append_index(c2, vcore.hashname4, pyvindex.hash_phone, dddd)
        except:
            print("exc save callb phone", sys.exc_info())
    try:
        vcore.postexec = callb
        ret = vcore.save_data(uuu, enc)
    except:
        pass
        print("save", sys.exc_info())
        ret = -1
    finally:
        vcore.postexec = None

    return ret

def ballotcore(dbname):

    ''' We let the core carry vars; make sure they do not collide '''

    bcore = twincore.TwinCore(dbname, 0)
    bcore.hashname  = os.path.splitext(bcore.fname)[0] + ".hash.id"
    bcore.hashname2 = os.path.splitext(bcore.fname)[0] + ".hash.name"

    return bcore

def saveballot(bcore, uuu, enc):

    ret = 0
    def callb(c2, id2):
        # Replicate saved locally
        dddd = [uuu, enc.encode()]
        #print("dddd:", dddd)
        try:
            pyvindex.append_index(c2, c2.hashname, pyvindex.hash_id, dddd)
        except:
            print("exc save callb hash", sys.exc_info())
        try:
            pyvindex.append_index(c2, c2.hashname2, pyvindex.hash_name, dddd)
        except:
            print("exc save callb name", sys.exc_info())
    try:
        bcore.postexec = callb
        ret = bcore.save_data(uuu, enc)
    except:
        pass
        print("save", sys.exc_info())
    finally:
        bcore.postexec = None

    return ret

def votecore(dbname):

    vcore = twincore.TwinCore(dbname, 0)
    vcore.hashname  = os.path.splitext(vcore.fname)[0] + ".hash.id"
    vcore.hashname2 = os.path.splitext(vcore.fname)[0] + ".hash.uid"
    vcore.hashname3 = os.path.splitext(vcore.fname)[0] + ".hash.bid"
    vcore.hashname4 = os.path.splitext(vcore.fname)[0] + ".hash.bname"

    return vcore

def votesave(votecore, uuu, enc):

    ret = 0
    def callb2(c2, id2):# EOF
        # Replicate saved locally
        dddd = [uuu, enc.encode()]
        #print("dddd:", dddd)
        try:
            pyvindex.append_index(c2, c2.hashname, pyvindex.hash_id, dddd)
        except:
            print("exc save callb hash", sys.exc_info())
        try:
            pyvindex.append_index(c2, c2.hashname2, pyvindex.hash_nuuid, dddd)
        except:
            print("exc save callb name", sys.exc_info())
        try:
            pyvindex.append_index(c2, c2.hashname3, pyvindex.hash_buuid, dddd)
        except:
            print("exc save callb ballot", sys.exc_info())
        try:
            pyvindex.append_index(c2, c2.hashname4, pyvindex.hash_bname, dddd)
        except:
            print("exc save callb bname", sys.exc_info())
            #support.put_exception("save callb")
    try:
        votecore.postexec = callb2
        ret = votecore.save_data(uuu, enc)
    except:
        print("exc save", sys.exc_info())
    finally:
        votecore.postexec = None

    return ret

# EOF
