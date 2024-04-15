#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time,  traceback, getopt
import random, glob, base64, datetime, stat

try:
    import psutil
except:
    psutil = None

# No dependents, so import can get parent dir

# ------------------------------------------------------------------------
# Globals

version = 1.0
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

def exc_last():
    a,b,c = sys.exc_info()
    ttt = traceback.extract_tb(c)
    aa = ttt[0]
    sss = (os.path.basename(aa[0]), aa[1], aa[2])
    return sss

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

# Flatten iterable into a string

def list2str(strin, sep = " "):
    strx = ""
    for aa in strin:
        strx += str(aa)
        if aa != strin[-1]:
            strx += sep

    return strx

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
        elif aa == ",":
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

def dirclean(strx):

    '''  Remove duplicate //

      History:
        Mon 01.Apr.2024 added c: path exception for MSYS2
    '''

    rrr = ""; aaa = strx.split("/")
    for aa in aaa:
        if len(aa) > 1 and aa[1] == ":":
            rrr += aa
        elif aa != "":
            rrr += "/" + aa
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
        #print("Cannot unlink lockfile.", lockfile, sys.exc_info())

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
            if psutil:
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
    fh.write(str(pid) );
    fh.close()

def shortdump(msg, strx):
    print(msg, str(base64.b64encode(strx[:12])) + " ... " + str(base64.b64encode(strx[-12:])))

# ------------------------------------------------------------------------
def mode2str(mode):

    #print mode, oct(mode), hex(mode)

    dstr = "-"
    if mode & 0x4000:
        dstr = "d"

    estr = ""
    for aa in range(3):
        xstr = ""
        if mode & 0x4: xstr += "r"
        else:        xstr += "-"
        if mode & 0x2: xstr += "w"
        else:        xstr += "-"
        if mode & 0x1: xstr += "x"
        else:        xstr += "-"
        mode = mode >> 3
        estr = xstr + estr  # Reverse

    estr = dstr + estr
    return estr

def fsize(fname):
    try:
        flen = os.stat(fname)[stat.ST_SIZE]
    except:
        print("stat", sys.exc_info())
        flen = 0

    return flen

def timeit(fn):
    def wrapped(*args, **keyw):
        ttt = time.time()
        ret = fn(*args, **keyw)
        print("  %s %.4f" % (fn.__name__, (time.time() - ttt)*1000))
        return ret
    return wrapped

def timeit2(fn):
    def wrapped(*args, **keyw):
        ttt = time.time()
        ret = fn(*args, **keyw)
        print("    %s %s %.4f" % (fn.__name__, args[1][0], (time.time() - ttt)*1000))
        return ret
    return wrapped

if __name__ == '__main__':
    lr = listrec("..")
    lr.noext = [".pyc", ".o", ".so", ".pem", ".pub", ]
    #lr.fill("..")

    #print ("startdir:", lr.startdir)
    for aa in lr.filearr:
        print(aa)

    #print ("filearr:", lr.filearr)

