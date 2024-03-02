#!/usr/bin/env python3

import os, string, random, sys, subprocess, time, signal
sys.path.append("..")

# Set parent as module include path
base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..', '..' ))

from pyvcommon import support, pycrypt, pyservsup, pyclisup
from pyvcommon import pysyslog, comline

fdirx = "/home/peterglen/pyvserver/"
lockname = "tmp/lockfile"
exename = "../../pyvserver/pyvserv.py"

def start_server():
    # Start server if needed
    if not os.path.isfile(fdirx + lockname):
        print("lockfile", os.path.isfile(fdirx + lockname))
        print("servfile", os.path.isfile(exename))
        print("servfile", exename)
        subprocess.Popen([exename, "-D"])
        time.sleep(1)

def stop_server():
    # Start server if needed
    if os.path.isfile(fdirx + lockname):
        print("lockfile", os.path.isfile(fdirx + lockname))
        fp = open(fdirx + lockname)
        buff = fp.read()
        print("buff:", buff)
        fp.close()
        os.kill(int(buff), signal.SIGINT)
        time.sleep(1)

# Return a random string based upon length
allstr =  string.ascii_lowercase +  string.ascii_uppercase

def randstr(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(allstr)-1)
        rr = allstr[ridx]
        strx += str(rr)
    return strx

# ------------------------------------------------------------------------

test_dir = "test_data"

if not os.path.isdir(test_dir):
    os.mkdir(test_dir)

tmpfile = ""

#tmpfile = os.path.splitext(os.path.basename(__file__))[0]
#tmpfile = randstr(8)

# This one will get the last one
for mm in sys.modules:
    if "test_" in mm:
        #print("mod", mm)
        tmpfile = mm

#print("tmpfile", tmpfile)


baseall = os.path.join(test_dir, tmpfile)
print("baseall", baseall)
#assert 0

def createname(file):
    datafile = os.path.splitext(os.path.basename(file))[0]
    return test_dir + os.sep + datafile + ".pydb"

def createidxname(file):
    datafile = os.path.splitext(os.path.basename(file))[0]
    return test_dir + os.sep + datafile + ".pidx"

def create_db(fname = ""):

    core = None

    if fname == "":
       fname = baseall + ".pydb"

    try:
        # Fresh start
        os.remove(fname)
        pass
    except:
        pass

    try:
        core = twincore.TwinCore(fname)
        #print(core)
        #assert 0
    except:
        print(sys.exc_info())

    return core

def uncreate_db(fname = ""):

    if fname == "":
       fname = baseall + ".pydb"
       iname = baseall + ".pidx"
    try:
        # Fresh start for next run
        os.remove(fname)
        os.remove(iname)
        pass
    except:
        pass

# ------------------------------------------------------------------------
# Support utilities

# Return a random string based upon length

def randbin(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, 255)
        strx += chr(ridx)
    return strx.encode("cp437", errors="ignore")

# EOF

