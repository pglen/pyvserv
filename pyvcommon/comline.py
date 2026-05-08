#!/usr/bin/env python

#from __future__ import print_function

import os, sys, string, time,  traceback, getopt
import random, glob, warnings

VERSION  = "1.0.0"
PROGNAME = "progname"

#warnings.simplefilter("ignore")
#warnings.simplefilter("default")
#warnings.simplefilter("always")

comdebug = 0        # Show internals

class cpm():

    glargs = ""
    glhead = ""
    glfoot = ""
    glprog = PROGNAME
    glver = VERSION
    gloptarr = []
    glsoptarr = []

    def pversion():
        print(cpm.glprog, "Version", cpm.glver)

        if sys.stdout.isatty():
            sys.exit(0)

    # ------------------------------------------------------------------------
    # Long form help

    def phelplong():

        if cpm.glhead:
            print(cpm.glhead)

        print( "Usage:", cpm.glprog, cpm.glargs)
        #print( "  options:")
        try:
            for aa in cpm.gloptarr:
                longop = aa[1].replace("=", "")
                if "=" in aa[1]:
                    arg = aa[2]
                else:
                    arg = " "

                pad  = " " * (8 - len(longop))
                pad2 = " " * (8 - len(arg))

                print("   ", "-" + aa[0][0], " ",
                                "--" + longop, pad, arg, pad2,"- ", aa[5])
            if cpm.glfoot:
                print(cpm.glfoot)
        except:
            pass

        # Sat 11.May.2024 only exit if real stdout
        if sys.stdout.isatty():
            sys.exit(0)

    def setargs(args):
        cpm.glargs = args

    def setfoot(args):
        cpm.glfoot = args

    def sethead(args):
        cpm.glhead = args

    def setprog(args):
        cpm.glprog = args

    def setver(args):
        cpm.glver = args

def dupoptcheck(optarr):
        optdup = {}
        for bb in range(len(optarr)):
            kkk = optarr[bb][0][0]
            try:
                optdup[kkk] += 1
            except KeyError:
                optdup[kkk] = 1
            except:
                print(sys.exc_info())
        #print(optdup)
        found = False
        for cc in optdup.keys():
            if optdup[cc] > 1:
                #print("found dup", cc)
                found = cc
        return found

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

# option [:], long_option[=],  var_name,   initial_value, function, helpstr
optarrlong = [\
 ["d:",  "debug=",  "pgdebug",  0,      None,       "Debug level. 0=none 10=noisy. Default: 0" ],
 ["p:",  "port=",   "port",     6666,   None,       "Listen on port. Default: 6666"],
 ["v",   "verbose", "verbose",  0,      None,       "Verbose. Show more info."],
 ["q",   "quiet",   "quiet",    0,      None,       "Quiet. Show less info."],
 ["V",   "version", "version",  None,   cpm.pversion,   "Print Version string."],
 ["h",   "help",    "help",     None,   cpm.phelplong,  "Show Help. (this screen)"]
]

class ConfigLong:

    def __init__(self, optarr):
        self._optarr = optarr
        ddd = dupoptcheck(self._optarr)
        if ddd:
            #for aa in self._optarr:
            #    print("%s" % aa)
            raise ValueError("Duplicate options on comline: '%s'" % ddd)

        cpm.gloptarr = self._optarr
        self.args = []
        self.err = None

        # Create defaults:
        for bb in range(len(self._optarr)):
            if self._optarr[bb][2]:
                #print("init", self._optarr[bb][2],
                #            self._optarr[bb][3], type(self._optarr[bb][3]))
                # Coerse type
                if  self._optarr[bb][3] == None:
                    self.__dict__[self._optarr[bb][2]] = None
                elif type(self._optarr[bb][3]) == type(0):
                    self.__dict__[self._optarr[bb][2]] = int(self._optarr[bb][3])
                elif type(self._optarr[bb][3]) == type(0.):
                    self.__dict__[self._optarr[bb][2]] = float(self._optarr[bb][3])
                elif type(self._optarr[bb][3]) == type(""):
                    self.__dict__[self._optarr[bb][2]] = str(self._optarr[bb][3])
                else:
                    print("Can only have int and str type; not", type(self._optarr[bb][3]))
                    raise ValueError("Can only None, int, float and string type - not %s" \
                                             % (type(self._optarr[bb][3])))

    def printvars(self):
        print("Variables -----")
        for aa in dir(self):
            try:
                if aa[:2] == "__" :
                    continue
                if  aa != "_optarr" and  aa != "comline" and \
                            aa != "printvars" :
                    ff = getattr(self, aa)
                    if type(ff) == type(self.printvars):
                        fff = "function"
                    else:
                        fff = type(ff)
                    print(aa, ff, fff)
            except:
                pass
        print("End Variables -----")

    def comline(self, argv):

        ''' Parse what is coming from the command line '''

        #print("feed argv", argv)

        optletters = "";  longopt = []
        for aa in self._optarr:
            if aa[0] in optletters:
                print ("Warning: duplicate option", "'" + aa[0] + "'")
            #if len(aa[0]) > 1 and aa[0][1] != ':':
            optletters += aa[0]
            longopt.append(aa[1])

        if comdebug:
           print("optleters:", optletters)
           print("longopt:", longopt)
        try:
            opts, self.args = getopt.gnu_getopt(argv, optletters, longopt)
        #except getopt.GetoptError, err:
        except getopt.GetoptError as err:
            print("Invalid option(s) on command line: %s" % err)
            raise

        if comdebug > 1:
            print ("opts", opts, "args", args)

        for aa in opts:
            found = 0
            if comdebug > 0:
                print("process opt:", aa)
            for bb in range(len(self._optarr)):
                #if comdebug > 0:
                #    print("  ", self._optarr[bb])
                ddd = None
                if aa[0][1] == "-":
                    ddd = "--" + self._optarr[bb][0]
                    eee = "--" + self._optarr[bb][1]
                elif aa[0][0] == "-":
                    ddd = "-" + self._optarr[bb][0]
                    eee = "-" + self._optarr[bb][1]
                else:
                    ddd = self._optarr[bb]

                if ddd[-1:] == "=":
                    ddd = ddd[:-1]
                    eee = eee[:-1]
                if ddd[-1:] == ":":
                    ddd = ddd[:-1]
                    eee = eee[:-1]

                if comdebug > 1:
                    print ("aa",  aa, "bb", bb,
                            "one opt =", self._optarr[bb][:-1], ddd, eee)
                if aa[0] == ddd or aa[0] == eee:
                    if comdebug > 1:
                        print ("match", aa, ddd)
                    found = True
                    if len(self._optarr[bb][0]) > 1:
                        if comdebug:
                            print ("arg", self._optarr[bb][2], self._optarr[bb][3], aa)
                        if self._optarr[bb][3] != None:
                            if type(self._optarr[bb][3]) == type(0):
                                if aa[1][:2] == "0x" or aa[1][:2] == "0X":
                                    self.__dict__[self._optarr[bb][2]] = int(aa[1][2:], 16)
                                else:
                                    self.__dict__[self._optarr[bb][2]] = int(aa[1])
                                    pass

                            elif type(self._optarr[bb][2]) == type(""):
                                self.__dict__[self._optarr[bb][2]] = str(aa[1])
                    else:
                        if comdebug > 1:
                            print ( "set 1", self._optarr[bb][1],
                                    "set 2", self._optarr[bb][2],
                                    "set 3", self._optarr[bb][3])

                        if self._optarr[bb][3] != None:
                            self.__dict__[self._optarr[bb][2]] += 1
                        #print ("call", self.optarr[bb][3])
                        if self._optarr[bb][4] != None:
                            self._optarr[bb][4]()
            if not found:
                print("add arg", ddd)
                self.args.append(ddd)

        return opts, self.args

if __name__ == '__main__':

    #print("Test comline.")
    optarr = optarrlong
    cpm.setprog(os.path.basename(__file__) + " [options] ")
    cpm.sethead("The main pyvserv server excutable.")

    conf = ConfigLong(optarr)
    opts, args = conf.comline(sys.argv[1:])
    print("opts:", opts, "args:", args)
    conf.printvars()
    #print(dir(conf))

# EOF
