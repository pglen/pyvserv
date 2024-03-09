#!/usr/bin/env python3

import os, sys, threading, time

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..'))

import sys

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

import os, getopt, signal, select, string, time
import tarfile, subprocess, struct, platform
import socket, threading, tracemalloc, inspect

if sys.version_info[0] < 3:
    import SocketServer as socketserver
else:
    import socketserver

from pyvcommon import support
from pyvcommon import pyservsup
from pyvcommon import pyclisup
from pyvcommon import pydata
from pyvcommon import pysyslog
from pyvcommon import comline
from pyvcommon import pyvhash

from pyvcommon import pyservsup, pyclisup

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join("..",  'pydbase'))

from pydbase import twincore, twinchain

import pyvpacker

replicname = "replic.pydb"
datafname = "initial.pydb"
ihostfname = "ihosts.pydb"

class Blank(): pass

class Replicator():

    def __init__(self, verbose = 0, pgdebug = 0):
        self.verbose = verbose
        self. pgdebug = pgdebug
        self.packer = pyvpacker.packbin()
        self.start_replication()
        self.dbfarr = []
        self.dbdarr = []
        self.hostdarr = []

    def _print_handles(self):
        open_file_handles = os.listdir('/proc/self/fd')
        print('open file handles: ' + ', '.join(map(str, open_file_handles)))

    def start_replication(self):
        return    # disabled Thu 07.Mar.2024
        if self.pgdebug > 3:
            print("start_replication()")
        replic_thread = threading.Thread(target=self.rep_run)
        replic_thread.daemon = True
        replic_thread.start()

    # create only once
    def softcreate(self, dbarr, fname, dbcreator):
        xcore = None
        for aa in dbarr:
            if aa[0] == fname:
                xcore = aa[1]
                break
        if not xcore:
            xcore = dbcreator(fname)
            dbarr.append((fname, xcore))
        return xcore

    def rep_run(self):

        while True:
            if pyservsup.globals.conf.norepl:
                #print("No replication")
                continue

            #print("Rep cycle", time.time())

            #if self.pgdebug > 5:
            #    print("Replicator cycle", time.time())
            ddd = os.listdir(pyservsup.globals.paydir)
            for aa in ddd:
                aaa = os.path.join(pyservsup.globals.paydir, aa)
                if not os.path.isdir(aaa):
                    continue
                #print(aaa)
                fname = os.path.join(aaa, replicname)
                if not os.path.isfile(fname):
                    continue
                self.scandir(aa)

            time.sleep(1)

    # Scan chain dir for replication data
    def scandir(self, dirname):

        was = False
        fname = os.path.join(pyservsup.globals.paydir, dirname)
        rfile = os.path.join(fname, replicname)
        #print("rfile: ", rfile)
        repcore = self.softcreate(self.dbfarr, rfile, twinchain.TwinCore)
        #repcore.pgdebug = 0
        #repcore.core_verbose = 5
        #print("dbsize", repcore.getdbsize())

        for bb in range(repcore.getdbsize()):
            try:
                rec = repcore.get_rec(bb)
            except:
                print("Exc on get_rec", sys.exc_info())
                continue
            if not rec:
                continue;   # Deleted record
            #print("head:", rec[0], "arr:", rec[1])
            arr = self.packer.decode_data(rec[1])[0]
            #print("arr", arr)
            # Increment count:
            cntstr = "%05d" % (int(arr['count1']) + 1)
            arr['count1'] = cntstr

            #print("arr:", arr)
            if  not int(arr['count2']):
                #if  int(cntstr) > 1  and int(cntstr) < 4:
                if  int(cntstr) == 1:
                    was = True
                    success = self.replicate(dirname, rec[0])
                    if success:
                        print("Succeeded")
                         # Increment success count:
                        cntstr2 = "%05d" % (int(arr['count2']) + 1)
                        arr['count2'] = cntstr2
                    else:
                        print("Failed")
            else:
                pass
                #print("Marked done")

            strx = str(self.packer.encode_data("", arr))
            ttt = time.time()
            ret = repcore.save_data(rec[0], strx, True)
            #print("db op1 %.3f" % ((time.time() - ttt) * 1000) )

            repcore.flush()

            if int(cntstr) > 6:
                #print("del rec:", rec[0])
                ret = repcore.del_rec_bykey(rec[0])
                repcore.flush()

        del repcore
        if was:
            self._print_handles()

    # Replicate this to all the hosts in the list
    def replicate(self, dirname, recx):
        print("replicate", dirname, recx)
        if type(recx) == type(b""):
            recx = recx.decode()

        ret = 0
        fname = os.path.join(pyservsup.globals.paydir, dirname)
        dfname = os.path.join(fname, datafname)

        #print("dfname: ", dfname)
        #if not os.path.isfile(dfname):
        #    return
        datacore = self.softcreate(self.dbdarr, dfname, twinchain.TwinChain)
        #print("dbsize", datacore.getdbsize())
        #print("recx", recx)
        try:
            rec = datacore.get_data_bykey(recx)
        except:
            print("cannot get record", sys.exc_info)
        if not rec:
            #print("Empty record on replicate")
            return

        #print("rec", rec)
        #print("rex", rec[0][1][1])

        arr = self.packer.decode_data(rec[0][1][1])[0]
        if 'replicate' in arr:
            arr['Replicated'] += 1
        else:
            arr['Replicated'] = 1
        #print(arr)
        pvh = pyvhash.BcData(arr)
        pvh.hasharr()
        pvh.powarr()
        print("pyvhash" , pvh.datax, pvh.checkhash(), pvh.checkpow())

        #sss = self.packer.encode_data("", arr)
        #arr2 = []
        #arr2.append(rec[0][0])
        #arr2.append(sss)
        #print("arr2",  arr2)
        del datacore

        # Replicate on a per host basis
        hfname = os.path.join(pyservsup.globals.myhome, ihostfname)
        #print("hfname", hfname)
        hostcore = self.softcreate(self.hostdarr, hfname, twincore.TwinCore)
        ret = 0
        for bb in range(hostcore.getdbsize()):
            try:
                hrec = hostcore.get_rec(bb)
            except:
                pass
            if not hrec:
                continue;       # Deleted record
            #print("host", hrec)
            ret = self.transmit(hrec[0], dirname, pvh.datax)
        del hostcore
        return ret

    def transmit(self, hostport, dirname, data):

        print("Transmitting to Host", hostport, "dirname", dirname, data['header'])
        #print("Data", data)
        #return   # test

        hp = hostport.decode().split(":")
        ret = 0
        hand = pyclisup.CliSup()
        try:
            respc = hand.connect(hp[0], int(hp[1]))
        except:
            print( "Cannot connect to:", hp, sys.exc_info()[1])
            return 0

        conf = Blank()
        hand.start_session(conf)

        #print(conf.sess_key[:24])
        #resp3 = hand.client(["hello", "world"] , conf.sess_key, False)
        #if resp3[0]  != "OK":
        #    print("Hello ERR Resp:", resp3)
        #    return ret
        #print("Hello Resp:", resp3)

        cresp = hand.client(["user", "admin"], conf.sess_key)
        print ("Server user respo:", cresp)

        cresp = hand.client(["pass", "1234"], conf.sess_key)
        print ("Server pass resp:", cresp)

        #print("rput", data)
        cresp = hand.client(["rput", dirname, data] , conf.sess_key, False)
        if cresp[0]  != "OK":
            print("rput ERR Resp:", cresp)
            cresp = hand.client(["quit"], conf.sess_key, False)
            print ("Server quit resp:", cresp)
            return ret

        print ("Server rput resp:", cresp)

        cresp = hand.client(["quit"], conf.sess_key, False)
        print ("Server quit resp:", cresp)

        # Success, mark record
        ret = True
        return ret

optarr =  comline.optarrlong

optarr.append ( ["N",   "norepl",    "norepl",      0,       None, "No replication (for test)"] )
optarr.append ( ["r:",  "dataroot=", "droot",  "pyvserver",  None, "Root for server data"] )

if __name__ == '__main__':

    conf = comline.ConfigLong(optarr)
    # Comline processed, go

    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf

    print("Started replicator")
    repl = Replicator(conf.verbose, conf.pgdebug)
    repl.rep_run()

# EOF
