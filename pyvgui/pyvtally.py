#!/usr/bin/env python3

import os, sys

if  sys.version_info[0] < 3:
        print("Needs python 3 or better.")
        sys.exit(1)

import getopt, signal, select, socket, time, struct
import random, string, stat, base64, random, datetime

import pyvpacker

# This repairs the path from local run to pip run.
# Remove pip version for local tests
try:
    from pyvcommon import support

    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf )
    #print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
    sys.path.append(os.path.join(sf, "pyvgui"))
    sys.path.append(os.path.join(sf, "pyvgui", "guilib"))

except:
    base = os.path.dirname(__file__)
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    sys.path.append(os.path.join(base,  "..", "pyvgui"))
    sys.path.append(os.path.join(base,  "..", "pyvgui", "guilib"))
    from pyvcommon import support

from pyvguicom import pgutils
# Get Parent of module root
sf = os.path.dirname(pgutils.__file__)
sys.path.append(os.path.join(sf, "..", "pyvguicom"))

#print("Load:", sys.path[-1])

from pyvcommon import support, comline, pywrap
from pyvcommon import pydata, pyservsup,  crysupp
from pyvserver import pyvstate
from pyvserver import pyvfunc
from guilib import mainwintally

# -----------------------------------------------------------------------
# Globals

version = "1.00"

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 9999)")
    print( "            -v        - Verbose")
    print( "            -V        - Version")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

# ------------------------------------------------------------------------
def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "debug=",   "pgdebug",  0,      None],      \
    ["p:",  "port=",    "port",     9999,   None],      \
    ["v",   "verbose",  "verbose",  0,      None],      \
    ["q",   "quiet",    "quiet",    0,      None],      \
    ["r:",  "dataroot=", "droot",   "pyvserver",     None],      \
    ["V",   "version",  None,       None,   pversion],  \
    ["h",   "help",     None,       None,   phelp]      \

conf = comline.ConfigLong(optarr)

def mainfunct():
    #print("pyvcpanel started ...")
    args = conf.comline(sys.argv[1:])
    #print("args", args)

    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf

    mw = mainwintally.MainWin()
    mw.main()
    sys.exit(0)

if __name__ == '__main__':

    mainfunct()

# EOF
