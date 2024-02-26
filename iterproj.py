#!/usr/bin/env python

import os, sys, glob, string, time,  traceback, getopt, random
import subprocess, fnmatch, shlex

''' Iterate every python file in project '''

sys.path.append('pyvcommon')

import comline, support, pysyslog

version = "1.1.0"

relarr = []
rel = "."
sumstr = ""

def gotfile(fname):

    global sumstr, conf

    #if conf.filter != "":
    #    if not conf.filter in fname:
    #        return

    if conf.wild != "":
        #print(fname, conf.wild)

        if not fnmatch.fnmatch(os.path.split(fname)[1], conf.wild):
            return

    if conf.verbose:
        print ("file:", fname)

    eee = os.path.splitext(fname)
    #print(eee)

    # Filter non py files
    #if eee[1] != ".py":
    #    return

    # Filter extensions
    gotext = [".pyc", ".o", ".so", ".pem", ".pub", ]
    for aa in gotext:
        if aa == eee[1]:
            return

    # Filter common garbage names
    gotfname = ["__pycache__", "md5sums", ]
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
        sumstr += ret.decode()  #+ b'\r\n'

    elif conf.xexec != "":
        xxx = shlex.split(conf.xexec)
        xxx.append(fname)
        #print ("executing:", xxx)
        try:
            ret = subprocess.check_output(xxx)
            print(ret.decode(), end = "") #, end="")
        except subprocess.CalledProcessError as err:
            if conf.showret:
                ret = "Ret code of '%s %s' = %d" % \
                            (conf.xexec, fname, err.returncode)
                print(ret.decode())
        except:
            ret = "Cannot execute '%s' on: %s" % \
                        (conf.xexec, fname)
            print("dd", ret.decode())
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
    print( "Execute options on every selected file in subtree. Default is to ")
    print( "print file names.")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -v        - Verbose, show file names")
    print( "            -V        - Version")
    print( "            -q        - Quiet")
    print( "            -m        - Do MD5 sum")
    print( "            -e prog   - Execute prog on file (use quotes for prog options)")
    print( "            -r        - Show prog exec exit code")
    #print( "            -f        - filter (match) to file name ")
    print( "            -w        - filter (wild card) to file name ")
    print( "            -m        - Do MD5 sum")
    print( "            -h        - Help")
    print()

    sys.exit(0)

def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

#    ["f:",  "filter",   "",     None],      \

optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["e:",  "xexec",    "",     None],      \
    ["w:",  "wild",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["r",   "showret",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["m",   "md5",      0,      None],      \
    ["s",   "showkey",  "",     None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

comline.version = "1.1"
conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunc():

    args = conf.comline(sys.argv[1:])
    #print("args", args)
    if len(args):
        os.chdir(args[0])

    listit()

    if conf.md5:
        print (sumstr, end="")

    #if conf.xexec != "":
    #    print ("xexec", conf.xexec)

if __name__ == '__main__':
    mainfunc()

# EOF