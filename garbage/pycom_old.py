#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time,  traceback, getopt, random, glob


try:
        opts, args = getopt.getopt(sys.argv[1:], "d:l:qhvVer:",
                ["debug=", "log=", "quiet", "help", "verbose", "version", "detach", "root"])

    except getopt.GetoptError as err:
        print( "Invalid option(s) on command line:", err)
        sys.exit(1)

    #print( "opts", opts, "args", args)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
                if verbose:
                    print( "Debug level:", pgdebug)
                if pgdebug > 10 or pgdebug < 0:
                    raise(Exception(ValueError, \
                        "Debug range needs to be between 0-10"))
            except:
                support.put_exception("Command line for:")
                sys.exit(3)

        if aa[0] == "-l" or aa[0] == "--log":
            try:
                pglog = int(aa[1])
                if verbose:
                    print( "Log level:", pglog)
                if pglog > 10 or pglog < 0:
                    raise(Exception(ValueError, \
                        "Log range needs to be between 0-10"))
            except:
                support.put_exception("Command line for:")
                sys.exit(3)

        if aa[0] == "-r" or aa[0] == "--root":
            try:
                dataroot = aa[1]
                if verbose:
                    print( "Data root directory '%s'" % dataroot)
                rrr = os.path.realpath(dataroot)
                if not os.path.isdir(rrr):
                    raise(Exception(InvalidArg, \
                        "Data root '%s' must exist." % dataroot))
            except:
                support.put_exception("Command line for:")
                sys.exit(3)

        if aa[0] == "-e" or aa[0] == "--detach": detach = True
        if aa[0] == "-h" or aa[0] == "--help": help();  exit(1)
        if aa[0] == "-v" or aa[0] == "--verbose": verbose = True
        if aa[0] == "-q" or aa[0] == "--quiet": quiet = True
        if aa[0] == "-V" or aa[0] == "--version":
            print( os.path.basename(sys.argv[0]), "Version", version)
            sys.exit(0)


def help():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level --debug  level - Debug level. (0-10) default: 0")
    print( "            -l level --log    level - Log level. (0-10) default: 0")
    print( "            -r dir   --root   dir   - Data directory. default: ./")
    print( "            -e       --detach       - Detach")
    print( "            -v       --verbose      - Verbose")
    print( "            -V       --version      - Version")
    print( "            -q       --quiet        - Quiet")
    print( "            -h       --help         - Help")
    print()
    sys.exit(0)


