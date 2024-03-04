#!/usr/bin/env python3

import os, sys, threading, time

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..'))

from pyvcommon import pyservsup
import twinchain
import pyvpacker

def start_replication():
    #print("start")
    replic_thread = threading.Thread(target=rep_run)
    replic_thread.daemon = True
    replic_thread.start()

def rep_run():

    #print("Repl start", time.time())

    pp = pyvpacker.packbin()

    while True:

        time.sleep(2)

        print("Repl active", time.time())

        ddd = os.listdir(pyservsup.globals.paydir)
        for aa in ddd:
            aaa = os.path.join(pyservsup.globals.paydir, aa)
            print(aaa)
            if not os.path.isdir(aaa):
                continue

            fname = os.path.join(aaa, "replic.pydb")
            if not os.path.isfile(fname):
                continue

            repcore = twinchain.TwinCore(os.path.join(fname), 0)
            #print("replic:", aa)

            for bb in range(repcore.getdbsize()):
                rec = repcore.get_rec(bb)
                arr = pp.decode_data(rec[1])[0]
                print("rec:", rec[0], arr[0], arr[1], arr[2])
                #print("head:", rec[0], "arr:", arr[0])
                arr[0] = "%05d" % (int(arr[0]) + 1)
                strx = str(pp.encode_data("", arr))
                #print("strx:", strx)
                rec = repcore.save_data(rec[0], strx, True)

            #del(repcore)

# EOF
