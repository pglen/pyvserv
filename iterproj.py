#!/usr/bin/env python

import os, sys, glob, string, time,  traceback, getopt, random
import subprocess, fnmatch, shlex

''' Iterate every python file in project '''

sys.path.append('pyvcommon')

import comline, support, pysyslog

version = "1.2.0"

conf = []
relarr = []
rel = "."
sumstr = ""

def gotfile(fname):

    global sumstr, conf

    #if conf.filter != "":
    #    if not conf.filter in fname:
    #        return

    basename = os.path.split(fname)[1]

    if conf.wild != "":
        #print(fname, conf.wild)
        if not fnmatch.fnmatch(basename, conf.wild):
            return

    if conf.exclude:
        for aa in conf.exclude:
            if fnmatch.fnmatch(basename, aa):
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
    gotfname = ["__pycache__", "checksums", ]
    for bb in gotfname:
        if bb in fname:
            return

    if conf.sum:
        try:
            ret = subprocess.check_output(["sha256sum", fname])
            #print("ret", ret, end="")
        except:
            ret = "Cannot sum file: %s\n", fname
            print(ret)
        sumstr += ret.decode()  #+ b'\r\n'

    elif conf.xexec != "":
        xxx = shlex.split(conf.xexec)
        xxx.append(fname)
        if conf.verbose:
            print ("executing:", xxx)
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

            was = False
            for cc in conf.excdir:
                #print("dirmtch", cc, os.path.basename(aa))
                if fnmatch.fnmatch(os.path.basename(aa), cc):
                    was = True
                    break
            if was:
                continue
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
    print( "Options:    -d level    - Debug level 0-10")
    print( "            -v          - Verbose, show file names.")
    print( "            -V          - Version.")
    print( "            -q          - Quiet.")
    print( "            -x exclude  - Exclude files.")
    print( "            -u excdir   - Exclude dir.")
    print( "            -w          - filter file names (wild card)")
    print( "            -e prog     - Execute prog on file.")
    print( "            -r          - Show prog exec exit code.")
    print( "            -m          - Generate SHA256 sum.")
    print( "            -h          - Show Help.")
    print()
    print("Use quotes for options with spaces.")
    print()
    sys.exit(0)


def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["e:",  "xexec",    "",     None],      \
    ["x:",  "exclude",  "",     None],      \
    ["u:",  "excdir",   "",     None],      \
    ["w:",  "wild",     "",     None],      \
    ["v",   "verbose",  0,      None],      \
    ["r",   "showret",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["t",   "test",     "x",    None],      \
    ["m",   "sum",      0,      None],      \
    ["s",   "showkey",  "",     None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

comline.version = "1.1"
conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunc():

    args = conf.comline(sys.argv[1:])

    if conf.verbose:
        print("args", args)

    if conf.debug > 4:
        print(conf)

    if len(args):
        os.chdir(args[0])

    if conf.exclude:
        conf.exclude = shlex.split(conf.exclude)
        print("exclude", conf.exclude)

    if conf.excdir:
        conf.excdir = shlex.split(conf.excdir)
        print("excdir", conf.excdir)

    listit()

    if conf.sum:
        print (sumstr, end="")

    #if conf.xexec != "":
    #    print ("xexec", conf.xexec)

if __name__ == '__main__':
    mainfunc()

# EOF