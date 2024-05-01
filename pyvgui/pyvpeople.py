#!/usr/bin/env python3

# pylint: disable=C0103
# pylint: disable=E1101
# pylint: disable=C0410

import os, sys

if  sys.version_info[0] < 3:
    print("Needs python 3 or better.")
    sys.exit(1)

''' Voter admin user interface '''

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
    #print("base", base)
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    sys.path.append(os.path.join(base,  "..", "pyvgui"))
    sys.path.append(os.path.join(base,  "..", "pyvgui", "guilib"))
    from pyvcommon import support

from pyvcommon import support, comline, pyservsup

from guilib import mainwinpeople

# -----------------------------------------------------------------------
# Globals

version = "1.00"

# ------------------------------------------------------------------------

def phelp():

    ''' Display help '''

    print( "Voter adminstration utility. Add / Review / Delete voters.")
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -v        - Verbose. Print more info.")
    print( "            -u        - User Name. Defult: 'admin'")
    print( "            -a        - Clear text password. For test only. Default: '1234'")
    print( "            -V        - Print version number.")
    print( "            -t        - Test mode. Extra buttons.")
    print( "            -q        - Quiet. Less printing.")
    print( "            -h        - Help (This screen)")
    sys.exit(0)

    #print( "            -p        - Port to use (default: 6666)")

# ------------------------------------------------------------------------
def pversion():

    ''' Show vwersion info '''

    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "debug=",       "pgdebug",  0,              None],      \
    ["p:",  "port=",        "port",     6666,           None],      \
    ["v",   "verbose",      "verbose",  0,              None],      \
    ["q",   "quiet",        "quiet",    0,              None],      \
    ["u:",  "user=",        "user",     "admin",        None],      \
    ["a:",  "pass=",        "apass",    "1234",         None],      \
    ["t",   "testx",        "testx",    0,              None],      \
    ["r:",  "dataroot=",    "droot",    "pyvclient",    None],      \
    ["V",   "version",      None,       None,           pversion],  \
    ["h",   "help",         None,       None,           phelp]      \

conf = comline.ConfigLong(optarr)

def mainfunct():

    ''' Main entry point '''

    #print("pyvcpanel started ...")
    args = conf.comline(sys.argv[1:])
    #print("args", args)

    # To know where the icon file is
    conf.me = __file__
    #print(dir(conf))

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

    pyservsup.gl_passwd = pyservsup.Passwd()

    mw = mainwinpeople.MainWin(pyservsup.globals)
    mw.main()
    sys.exit(0)

if __name__ == '__main__':

    mainfunct()

# EOF
