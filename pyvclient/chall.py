#!/usr/bin/env python3

from __future__ import print_function

import sys

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat
import argparse

parser = argparse.ArgumentParser(description='Change string in files from_str to to_str.')

parser.add_argument("-V", '--version', dest='version',
                    default=0,  action='count',
                    help='Show version number.')

parser.add_argument("from_str", help="String to find")
parser.add_argument("to_str", help="String to change to")
parser.add_argument("filenames", nargs="+", help="File name or wildcard")

parser.add_argument("-v", '--verbose', dest='verbose',
                    default=0,  action='count',
                    help='verbocity on (default: off)')

parser.add_argument("-t", '--test', dest='test',
                    default=0,  action='store_true',
                    help='see what would be done')

parser.add_argument("-n", '--noback', dest='noback',
                    default=0,  action='store_true',
                    help='do not do backups')

parser.add_argument("-b", '--backup', dest='backup',
                    default='backup',  action='store',
                    help='backup dir (default: backup)')


version = "1.0.0"

def mainfunct():

    if sys.argv[1] == "-V":
        print("Version number: %s" % version)
        sys.exit(0)

    args = parser.parse_args()
    #print(args)

    if args.test:
        print("Test mode")

    if args.verbose > 0:
        print("Change: ", args.from_str, "to:", args.to_str)

    # copy to backup
    if not args.noback and not args.test:
        bbb = "backup"
        if not os.path.isdir(bbb):
            os.mkdir(bbb)
        for aa in args.filenames:
            if os.path.isfile(aa):
                bbtmp = bbb + os.sep + aa
                if args.verbose > 1:
                    print ("Backup:", aa, "to:", bbtmp)
                if not args.test:
                    fh = open(aa, 'rt')
                    fh2 = open(bbtmp, 'wt')
                    while True:
                        buff = fh.readline()
                        if not buff:
                            break
                        fh2.write(buff)
                    fh.close();  fh2.close()

        print()

    #sys.exit()

    for aa in args.filenames:
        if os.path.isfile(aa):
            if args.verbose:
                print ("Processing:", aa)
            aatmp = aa + ".tmp"
            fh = open(aa, 'rt')
            if not args.test:
                fh2 = open(aatmp, 'wt')

            cnt = 0
            while True:
                was = 0
                buff = fh.readline()
                if not buff:
                    break
                org = buff[:]
                idx = 0
                for cc in range(10):
                    idx = buff.find(args.from_str, idx)
                    if idx  >= 0:
                        buff = buff[:idx] + args.to_str + buff[idx+len(args.from_str):]
                        cnt += 1
                        was += 1
                    else:
                        break

                if was:
                    if args.verbose:
                        print (org,  end = "")
                        print (buff, end = "")

                if not args.test:
                    fh2.write(buff)

            fh.close();
            if not args.test:
                fh2.close()

            if cnt:
                ss = os.stat(aa)
                print ("Processed:", aa, cnt, "\n")

                if not args.test:
                    os.unlink(aa)
                    os.rename(aatmp, aa)
                    os.chmod(aa, ss.st_mode)

            else:
                if not args.test:
                    os.unlink(aatmp)

if __name__ == '__main__':
    mainfunct()

# EOF