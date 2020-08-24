#!/usr/bin/env python

from __future__ import print_function

import os, sys, glob, string, time,  traceback, getopt, random
import subprocess

sys.path.append('common')
import support, pysyslog

relarr = []
rel = "."
sumstr = ""

def gotfile(fname):

    global sumstr, conf

    if conf.filter != "":
        if not conf.filter in fname:
            return

    if conf.verbose:
        print ("file:", fname)

    # filter extensions
    gotext = [".pyc", ".o", ".so", ".pem", ".pub", ]
    eee = os.path.splitext(fname)
    for aa in gotext:
        if aa == eee[1]:
            return

    gotfname = ["__pycache__", "md5sums", ]

    # filter names
    for bb in gotfname:
        if bb in fname:
            return

    if conf.md5:
        try:
            ret = subprocess.check_output(["md5sum", fname])
            #print("ret", ret, end="")

        except:
            ret = "Cannot sum file: %s\n", fname
            print(ret)

        sumstr += ret
    elif conf.xexec != "":
        xxx = string.split(conf.xexec)
        xxx.append(fname)
        #print ("executing:", xxx)
        try:
            ret = subprocess.check_output(xxx)
            print(ret, end="")
        except subprocess.CalledProcessError as err:
            if conf.showret:
                ret = "Ret code of '%s %s' = %d" % \
                            (conf.xexec, fname, err.returncode)
                print(ret)
        except:
            ret = "Cannot execute '%s' on: %s" % \
                        (conf.xexec, fname)
            print(ret)

    else:
        print (fname )

    #if ret.returncode:
    #    print ("camnnot exec", fname)


def listit():
    global rel

    arr = glob.glob(rel + "/*")
    #print(arr)

    for aa in arr:
        bb = rel + "/" + os.path.basename(aa)
        if not os.path.isdir(bb):
            gotfile(bb)

    for aa in arr:
        #print ("aa", aa)
        bb = rel + "/" +  os.path.basename(aa)
        if os.path.isdir(bb):
            #print  ("got dir", bb)
            relarr.append(rel)
            rel += "/" + os.path.basename(aa)
            listit();
            rel = relarr.pop()
        else:
            #print  ("file", os.getcwd(), aa)
            #gotfile(rel + "/" + aa)
            pass

    # option, var_name, initial_val, function

# ------------------------------------------------------------------------
# Functions from command line

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] startdir")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -v        - Verbose, show file names")
    print( "            -q        - Quiet")
    print( "            -m        - Do md5 sum")
    print( "            -e prog   - Execute prog on file (use quotes for prog options)")
    print( "            -r        - Show prog exec exit code")
    print( "            -f        - filter (match) to file name ")
    print( "            -w        - filter (wild card) to file name ")
    print( "            -m        - Do md5 sum")
    print( "            -h        - Help")

    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", support.version)
    sys.exit(0)

optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["e:",  "xexec",    "",     None],      \
    ["f:",  "filter",   "",     None],      \
    ["w:",  "wild",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["r",   "showret",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["m",   "md5",      0,      None],      \
    ["s",   "showkey",  "",     None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = support.Config(optarr)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    args = conf.comline(sys.argv[1:])
    if len(args):
        os.chdir(args[0])

    listit()

    if conf.md5:
        print (sumstr, end="")

    #if conf.xexec != "":
    #    print ("xexec", conf.xexec)



