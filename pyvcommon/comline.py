#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time,  traceback, getopt, random, glob

version = 1

# ------------------------------------------------------------------------

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:")

    for aa in optarr:
        pad = " " * (9 - len(aa[1]))
        print("        ", "-" + aa[0][0], " ", aa[1], pad, " - ", aa[4])

    print()

    sys.exit(0)

# ------------------------------------------------------------------------
# option [:], var_name, initial_val, function, helpstr
# Add colon ':' to option with argument.

optarr = [\
    ["d:",  "pgdebug",  0,      None,       "Debug level 0-10" ], \
    ["p:",  "port",     6666,   None,       "Listen on port"],    \
    ["v",   "verbose",  0,      None,       "Verbose"],           \
    ["q",   "quiet",    0,      None,       "Quiet"],             \
    ["V",   "version",  None,   pversion,   "Print Version"],     \
    ["h",   "help",     None,   phelp,      "Show Help"]          \
    ]

# ------------------------------------------------------------------------
# Handle command line. Interpret optarray and decorate the class
# This allows a lot of sub utils to have a common set of options.

class Config:

    def __init__(self, optarr):
        self.optarr = optarr
        self.verbose = False
        self.debug = False
        self.sess_key = ""

    def comline(self, argv):
        optletters = ""
        for aa in self.optarr:
            optletters += aa[0]
        #print( optletters    )
        # Create defaults:
        err = 0
        for bb in range(len(self.optarr)):
            if self.optarr[bb][1]:
                # Coerse type
                if type(self.optarr[bb][2]) == type(0):
                    self.__dict__[self.optarr[bb][1]] = int(self.optarr[bb][2])
                if type(self.optarr[bb][2]) == type(""):
                    self.__dict__[self.optarr[bb][1]] = str(self.optarr[bb][2])
        try:
            opts, args = getopt.getopt(argv, optletters)
        #except getopt.GetoptError, err:
        except:
            print( "Invalid option(s) on command line:", err)
            #support.put_exception("comline")
            return ()

        #print( "opts", opts, "args", args)
        for aa in opts:
            for bb in range(len(self.optarr)):
                if aa[0][1] == self.optarr[bb][0][0]:
                    #print( "match", aa, self.optarr[bb])
                    if len(self.optarr[bb][0]) > 1:
                        #print( "arg", self.optarr[bb][1], aa[1])
                        if self.optarr[bb][2] != None:
                            if type(self.optarr[bb][2]) == type(0):
                                self.__dict__[self.optarr[bb][1]] = int(aa[1])
                            if type(self.optarr[bb][2]) == type(""):
                                self.__dict__[self.optarr[bb][1]] = str(aa[1])
                    else:
                        #print( "set", self.optarr[bb][1], self.optarr[bb][2])
                        if self.optarr[bb][2] != None:
                            self.__dict__[self.optarr[bb][1]] = 1
                        #print( "call", self.optarr[bb][3])
                        if self.optarr[bb][3] != None:
                            self.optarr[bb][3]()
        return args





