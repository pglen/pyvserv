#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

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
    #print("pip inc")
    base = os.path.dirname(__file__)
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    sys.path.append(os.path.join(base, "..", "pyvgui"))
    sys.path.append(os.path.join(base, "..", "pyvgui", "guilib"))
    from pyvcommon import support

from pyvguicom import pgutils
# Get Parent of module root
sf = os.path.dirname(pgutils.__file__)
sys.path.append(os.path.join(sf, "..", "pyvguicom"))

from pyvcommon import support, comline, pywrap
from pyvcommon import pydata, pyservsup,  crysupp

from guilib import mainwinrep
import pyvpacker

# ------------------------------------------------------------------------
# Globals

version = "0.00"

# ------------------------------------------------------------------------

def phelp():

    comline.phelplong()

    if sys.stdout.isatty():
        sys.exit(0)

# ------------------------------------------------------------------------
def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

# option, long_opt, var_name, initial_val, function, help_str

optarr = [\
 ["d:",  "debug=",    "pgdebug",  0,          None,
                                        "Debug Level. 0=None 9=Noisy", ],
 ["r:",  "dataroot=", "droot",    "pyvclient",None,
                                        "Directory for data. Default: ~/pyvclient", ],
 ["u:",  "user=",     "user",     "admin",    None,
                                        "User name. Default: admin",     ],
 ["a:",  "pass=",     "apass",    "1234",     None,
                                        "Password. Default: 1234 For tests only.",],
 ["t",   "prompt",    "prompt",   0,          None,
                                        "Prompt for password on command line.", ],
 ["s",   "sound",     "soundx",   0,          None,
                                        "Turn off sound",     ],
 ["v",   "verbose",   "verbose",  0,          None,
                                        "Print more information",     ],
 ["w",   "weak",         "weak",     0,              None,
                                        "Weak POW generation. Test only", ],
 ["K",   "kind",         "kind",     "vote",              None,
                                        "Kind of repliation to monitor", ],
 ["q",   "quiet",     "quiet",    0,          None,
                                        "Print less information",     ],
 ["z",   "test",      "testx",    0,          None,
                                        "Display test buttons",     ],
 ["V",   "version",    None,       None,      pversion,
                                        "Show program version", ],
 ["h",   "help",       None,       None,      phelp,
                                        "Show help. (this screen)",  ],
]

conf = comline.ConfigLong(optarr)

def mainfunct():

    args = conf.comline(sys.argv[1:])

    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf
    pyservsup.globals.softmkdir(pyservsup.globals.myhome)

    # Change directory to the data dir
    os.chdir(pyservsup.globals.myhome)
    if conf.verbose:
        print("cwd", os.getcwd())

    # Patch passdir for client
    pyservsup.globals.passdir   =  pyservsup.globals.myhome + ".pyvclient" + os.sep
    pyservsup.globals.softmkdir(pyservsup.globals.passdir)
    pyservsup.globals.passfile = pyservsup.globals.passdir + os.sep + pyservsup.globals._passfile

    # Patch idfile for client
    pyservsup.globals.idfile = pyservsup.globals.myhome + os.sep + "pyvclient.init"

    # Create support objects
    pyservsup.globals.config(pyservsup.globals.myhome, conf)

    Vd = os.path.join(pyservsup.globals.chaindir, "vote")
    pyservsup.globals.softmkdir(Vd)

    # To know where the icon files are
    conf.me = __file__
    conf.packer = pyvpacker.packbin()

    mw = mainwinrep.MainWin(pyservsup.globals)
    mw.main()
    sys.exit(0)

if __name__ == '__main__':
    mainfunct()

# EOF
