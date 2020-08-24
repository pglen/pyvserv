#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time,  traceback, getopt, random, glob, base64

# ------------------------------------------------------------------------
# Globals

version = 1.0
keydir = '../keys/'
random.seed()

for aa in range(random.randint(1, 10)):
    rr = random.randint(0, 100)
    #print("rr", rr)

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

def hexstr(strin):
    outx = ""
    if sys.version_info[0] < 3:
        strx = strin
    else:
        if type(strin) == str:
            strx = bytes(strin, "cp437")
        else:
            strx = strin

    for aa in range(len(strx)):
        if sys.version_info[0] < 3:
            outx += "%02x " % ord(strx[aa])
        else:
            outx += "%02x " % strx[aa]
    return outx

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
        self.noext = []
        self._rel = "."
        self._relarr = []
        self.startdir = os.getcwd()

        if dirx != "":
            self.fill(dirx)

    def _gotfile(self, fname):
        # filter extensions
        if len(self.noext):
            eee = os.path.splitext(fname)
            for aa in self.noext:
                if aa == eee[1]:
                    return

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

# ------------------------------------------------------------------------

def unlock_process(lockfile):
    try:
        os.unlink(lockfile)
    except:
        pass
        print("Cannot unlink lockfile.")



def lock_process(lockfile):

    closeit = 0; pidstr = ""
    pid = os.getpid()

    try:
        fh = open(lockfile, "r")
        if fh:
            pidstr = fh.read()
            fh.close()
            closeit = 1
    except:
        pass

    pidint = 0;

    try:
        pidint = int(pidstr)
    except:
        pass

    if closeit:
        # Examine if it is still running:
        was = False
        if pidstr != "":
            for proc in psutil.process_iter():
                if proc.pid == pidint:
                    was = True
        if not was:
            print("Lockfile active, no process ... breaking in")
            os.unlink(lockfile)
        else:
            print("Server running already.")
            #if verbose:
            #    print("Lockfile '%s' pid '%s'" % (lockfile, pidstr))
            sys.exit(2)

    fh = open(lockfile, "w");
    fh.write( str() );
    fh.close()

def shortdump(msg, strx):
    print(msg, str(base64.b64encode(strx[:12])) + " ... " + str(base64.b64encode(strx[-12:])))

if __name__ == '__main__':
    lr = listrec("..")
    lr.noext = [".pyc", ".o", ".so", ".pem", ".pub", ]
    #lr.fill("..")

    #print ("startdir:", lr.startdir)
    for aa in lr.filearr:
        print(aa)

    #print ("filearr:", lr.filearr)

