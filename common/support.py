#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time,  traceback, getopt, random, glob

# ------------------------------------------------------------------------
# Globals

version = 1.0
keydir = '../keys/'

# ------------------------------------------------------------------------
# A more informative exception print

def put_debug(xstr):
    try:
        if os.isatty(sys.stdout.fileno()):
            print( xstr)
        else:
            syslog.syslog(xstr)
    except:
        print( "Failed on debug output.")
        print( sys.exc_info())

def put_exception(xstr):

    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        "  Line: " + str(aa[1]) + "\n" +  \
                        "    Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())

    put_debug(cumm)
    #syslog.syslog("%s %s %s" % (xstr, a, b))

def put_exception2(xstr):

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
            print( "Could not print trace stack. ", sys.exc_info())

    put_debug(cumm)
    #syslog.syslog("%s %s %s" % (xstr, a, b))

# ------------------------------------------------------------------------
# Helper functions.
# Escape spaces to %20 and misc chars

def escape(strx):

    aaa = "";
    for aa in strx:
        if aa == "%":
            aaa += aa + aa
        elif aa == " ":
            aaa += "%%%x" % ord(aa)
        elif aa == "\"":
            aaa += "%%%x" % ord(aa)
        elif aa == "\'":
            aaa += "%%%x" % ord(aa)
        else:
            aaa += aa
    return aaa

# Run through a state machine to descramble

def unescape(strx):

    aaa = ""; back = ""; state = 0; chh = ""

    for aa in strx:
        if state == 3:
            aaa += back; back = ""; state = 0; chh = ""

        if state == 2:
            if aa >= "0" and aa <= "9":
                back = ""; state = 3; chh += aa
                aaa += chr(int(chh, 16))
            else:
                back += aa; state = 3

        if state == 1:
            if aa >= "0" and aa <= "9":
               state = 2; chh += aa
            elif aa == "%":
                aaa += "%"; back = ""; state = 3
            else:
                back += aa; state = 3

        if state == 0:
            if aa == "%":
                state = 1; back += aa
            else:
                aaa += aa

    return aaa

# ------------------------------------------------------------------------
# Remove dup //

def dirclean(strx):
    rrr = ""; aaa = strx.split("/")
    for aa in aaa:
        if aa != "": rrr += "/" + aa
    return rrr

# ------------------------------------------------------------------------
# Change directory to up (..)

def chup(strx):
    # Stage 1: clean
    rrr2 = ""; rrr = dirclean(strx)
    # Stage 2: cut end
    for aa in rrr.split("/")[:-1]:
        rrr2 += "/" + aa
    return rrr2

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream

   def write(self, data):
       self.stream.write(data)
       self.stream.flush()

   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()

   def __getattr__(self, attr):
       return getattr(self.stream, attr)

# ------------------------------------------------------------------------
# Handle command line. Interpret optarray and decorate the class

class Config:

    def __init__(self, optarr):
        self.optarr = optarr
        self.verbose = False
        self.debug = False

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
            put_exception("comline")
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



# Return basename for key file

def pickkey():

    dl = os.listdir(keydir)
    dust = random.randint(0, len(dl)-1)
    eee = os.path.splitext(os.path.basename(dl[dust]))
    #print("picking key", eee[0])
    return eee[0]

def  breaklines(xstr, xlen):
    ystr = ""
    for aa in range(len(xstr)):
        ystr += xstr[aa]
        if aa % xlen == xlen-1:
            ystr += "\n"
    return ystr

def catbegend(xstr):
    pass


# ------------------------------------------------------------------------
# Create a list of recursive names

class listrec():

    def __init__(self, dirx = ""):
        self.filearr = []

        self._rel = "."
        self._relarr = []
        self.startdir = os.getcwd()

        if dirx != "":
            self.fill(dirx)

    def _gotfile(self, fname):
        self.filearr.append(fname)

    def _listit(self):
        #print ( "_listit at: ", self._rel)
        arr = glob.glob(self._rel + "/*")
        #print ("arr", arr)
        for aa in arr:
            bb = self._rel + "/" +  os.path.basename(aa)
            if os.path.isdir(bb):
                #print ( "got dir", bb)
                self._relarr.append(self._rel)
                self._rel += "/" + os.path.basename(aa)
                self._listit()
                self._rel = self._relarr.pop()

        for aa in arr:
            bb = self._rel + "/" + os.path.basename(aa)
            if not os.path.isdir(bb):
                #print ("file aa", aa)
                self._gotfile(bb)

    def fill(self, dirx = ""):
        self.startdir = os.getcwd()
        self._rel = dirx
        self._relarr = []
        self._relarr.append(self._rel)
        self.filearr = []
        self._listit()

if __name__ == '__main__':
    lr = listrec("..")
    #lr.fill("..")

    #print ("startdir:", lr.startdir)
    for aa in lr.filearr:
        print(aa)

    #print ("filearr:", lr.filearr)



