#!/usr/bin/env python3

# pylint: disable=C0103
# pylint: disable=E1101
# pylint: disable=C0410

import os, sys, getopt, signal

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

from guilib import mainwinvote, pymisc

# -----------------------------------------------------------------------
# Globals

VERSION = "1.00"

# ------------------------------------------------------------------------

def print_stats():

    ''' breakout '''
    if conf.verbose:
        print("Serve exe path:  ", pyservsup.globals.script_home)
        print("Data root:       ", pyservsup.globals.myhome)
        print("Pass Dir:        ", pyservsup.globals.passdir)
        print("Key Dir:         ", pyservsup.globals.keydir)
        print("Payload Dir:     ", pyservsup.globals.paydir)
        print("Lock file:       ", pyservsup.globals.lockfname)
        print("ID file:         ", pyservsup.globals.idfile)
        #print("Passfile:        ", pyservsup.globals.passfile)

def phelp():

    ''' Display help '''

    comline.phelplong()

    if sys.stdout.isatty():
        sys.exit(0)

# ------------------------------------------------------------------------

def pversion():

    ''' Show vwersion info '''

    comline.pversion(VERSION)

    if sys.stdout.isatty():
        sys.exit(0)

# option, long_opt/var_name, initial_val, function, help

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
 ["q",   "quiet",     "quiet",    0,          None,
                                        "Print less information",     ],
 ["z",   "test",      "testx",    0,          None,
                                        "Display test buttons",     ],
 ["V",   "version",    None,       None,      pversion,
                                        "Show program version", ],
 ["h",   "help",       None,       None,      phelp,
                                        "Show help. (this screen)",  ],
]

comline.setprog(os.path.basename(__file__))
comline.sethead("Create / Administer / Delete Votes.")
comline.setfoot("User / Password is needed.")
conf = comline.ConfigLong(optarr)

def mainfunct():

    ''' Main entry point '''

    try:
        args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit()
    except:
        print(sys.exc_info())

    if conf.pgdebug > 4:
        print("args", args)

    # To know where the icon files are
    conf.me = __file__
    if conf.pgdebug > 4:
        conf.printvars()

    if not conf.soundx:
        conf.playsound = pymisc.Soundx()
    else:
        conf.playsound = None

    if conf.prompt:
        if sys.stdout.isatty():
            def soft_terminate(arg2, arg3):
                print("Ctrl-C pressed, exiting ...")
                sys.exit(0)
            signal.signal(signal.SIGINT, soft_terminate)
            import getpass
            strx = getpass.getpass("Enter Pass: ")
            if not strx:
                print("Empty pass, aborting ...")
                sys.exit(0)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            conf.apass  = strx
        else:
            conf.apass = ""

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

    print_stats()

    pyservsup.gl_passwd = pyservsup.Passwd()

    #phelploc()

    mw = mainwinvote.MainWin(pyservsup.globals)
    mw.main()
    #sys.exit(0)

if __name__ == '__main__':

    mainfunct()
    sys.exit(1)

# EOF
