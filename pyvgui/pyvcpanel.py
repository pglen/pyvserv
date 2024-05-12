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
    sf = os.path.dirname(sf)
    #print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
    sys.path.append(os.path.join(sf, "pyvgui"))
    sys.path.append(os.path.join(sf, "pyvgui", "guilib"))

except:
    base = os.path.dirname(__file__)
    #print("base:", base)
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
from guilib import mainwin

# -----------------------------------------------------------------------
# Globals

VERSION = "1.00"

def phelp():

    ''' Display help '''

    comline.phelplong()

    if sys.stdout.isatty():
        sys.exit(0)

def pversion():

    ''' Show vwersion info '''

    comline.pversion(VERSION)
    if sys.stdout.isatty():
        sys.exit(0)

# ------------------------------------------------------------------------
# option, var_name, initial_val, function, helpstr

optarr = [\
    ["d:",  "debug=",       "pgdebug",  0,              None,
                                        "Debug level 0-10", ],
    ["r:",  "dataroot=",    "droot",    "pyvclient",    None,
                                        "Directory for data. Default: ~/pyvclient", ],
    ["u:",  "user=",        "user",     "admin",        None,
                                        "User Name. Default: 'admin'", ],
    ["a:",  "pass=",        "apass",    "1234",         None,
                                        "Password. For test only. Default: '1234'", ],
    ["t",   "prompt",    "prompt",   0,          None,
                                        "Prompt for password on command line.", ],
    ["z",   "testx",        "testx",    0,              None,
                                        "Test mode. Extra buttons.", ],
    ["v",   "verbose",      "verbose",  0,              None,
                                        "Verbose. Print more info.", ],
    ["q",   "quiet",        "quiet",    0,              None,
                                        "Quiet. Less printing.", ],
    ["V",   "version",      None,       None,           pversion,
                                        "Print version number.", ],
    ["h",   "help",         None,       None,           phelp,
                                        "Help (This screen)", ],
    ]

comline.setprog(os.path.basename(__file__) + " [options]" )
comline.sethead("PyvServer adminstration panel.")
comline.setfoot("Wlii use default settings to monitor.")

conf = comline.ConfigLong(optarr)

def mainfunct():
    #print("pyvcpanel started ...")
    args = conf.comline(sys.argv[1:])
    #print("args", args)

    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf

    mw = mainwin.MainWin()
    mw.main()
    sys.exit(0)

if __name__ == '__main__':

    mainfunct()

# EOF
