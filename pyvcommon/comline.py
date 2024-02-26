#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time,  traceback, getopt, random, glob

version = 1.0

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
        except getopt.GetoptError as err:
            print( "Invalid option(s) on command line:", err)
            raise
            return ()
        except:
            print(sys.exc_info())

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

# ------------------------------------------------------------------------
# Handle command line. Interpret optarray and decorate the class;
# Uses UNIX getopt for compatibility;
#
# Option parameters:
#
# option, long_option,  var_name,   initial_value, function
#
# Option with parameters:   add trailing colon (:)
# Long opt with parameters: add training equal sign (=)
#
# Example:
#
#optarr = \
#    ["d:",    "debug=",      "pgdebug",  0,              None],      \
#    ["p:",    "port",        "port",     9999,           None],      \
#    ["v",     "verbose",     "verbose",  0,              None],      \
#    ["t",     "test",        "test",     "x",            None],      \
#    ["V",     "version",     None,       None,           pversion],  \
#    ["h",     "help",        None,       None,           phelp],     \
#    ["i:",    "input=",      "input",      "-",          None],     \

class ConfigLong:

    def __init__(self, optarr):
        self.optarr = optarr
        self.err = None

        # Create defaults:
        for bb in range(len(self.optarr)):
            if self.optarr[bb][2]:
                #print("init", optarr[bb][2], optarr[bb][3])
                # Coerse type
                if type(self.optarr[bb][2]) == type(0):
                    self.__dict__[self.optarr[bb][2]] = int(self.optarr[bb][3])
                else:
                    self.__dict__[self.optarr[bb][2]] = str(self.optarr[bb][3])

    def printvars(self):
        for aa in dir(self):
            try:
                if aa[:2] != "__" and aa != "optarr" and  aa != "comline" and \
                                    aa != "printvars" :
                    ff = getattr(self, aa)
                    if type(ff) == type(self.printvars):
                        ff = "function"
                    print(aa, ff)
            except:
                pass

    def comline(self, argv):
        optletters = "";  longopt = []
        for aa in self.optarr:
            if aa[0] in optletters:
                print ("Warning: duplicate option", "'" + aa[0] + "'")
            #if len(aa[0]) > 1 and aa[0][1] != ':':
            optletters += aa[0]
            longopt.append(aa[1])

        #print("optleters", optletters, "longopt", longopt)

        try:
            opts, args = getopt.getopt(argv, optletters, longopt)
        #except getopt.GetoptError, err:
        except getopt.GetoptError as err:
            self.err =  str("Invalid option(s) on command line: %s" % err)
            return None

        #print ("opts", opts, "args", args)
        for aa in opts:
            for bb in range(len(self.optarr)):
                ddd = None
                if aa[0][1] == "-":
                    ddd = "--" + self.optarr[bb][0]
                    eee = "--" + self.optarr[bb][1]
                elif aa[0][0] == "-":
                    ddd = "-" + self.optarr[bb][0]
                    eee = "-" + self.optarr[bb][1]
                else:
                    ddd = self.optarr[bb]
                if ddd[-1:] == "=":
                    ddd = ddd[:-1]
                    eee = eee[:-1]
                if ddd[-1:] == ":":
                    ddd = ddd[:-1]
                    eee = eee[:-1]

                #print ("aa",  aa, "one opt", self.optarr[bb][:-1], ddd, eee)
                if aa[0] == ddd or aa[0] == eee:
                    #print ("match", aa, ddd)
                    if len(self.optarr[bb][0]) > 1:
                        #print ("arg", self.optarr[bb][2], self.optarr[bb][3], aa)
                        if self.optarr[bb][3] != None:
                            if type(self.optarr[bb][3]) == type(0):
                                if aa[1][:2] == "0x" or aa[1][:2] == "0X":
                                    self.__dict__[self.optarr[bb][2]] = int(aa[1][2:], 16)
                                else:
                                    self.__dict__[self.optarr[bb][2]] = int(aa[1])
                                    pass

                            elif type(self.optarr[bb][2]) == type(""):
                                self.__dict__[self.optarr[bb][2]] = str(aa[1])
                    else:
                        #print ("set", self.optarr[bb][1], self.optarr[bb][2])
                        if self.optarr[bb][3] != None:
                            self.__dict__[self.optarr[bb][1]] = 1
                        #print ("call", self.optarr[bb][3])
                        if self.optarr[bb][4] != None:
                            self.optarr[bb][4]()
        return args

# ------------------------------------------------------------------------
# Print an exception as the system would print it

def print_exception(xstr):
    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print ("Could not print trace stack. ", sys.exc_info())
    print (cumm)

# EOF
