#!/usr/bin/env python3

import os, sys, threading, time

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  '..'))

from pyvcommon import pyservsup, pyclisup

import twinchain, twincore
import pyvpacker

replicname = "replic.pydb"
datafname = "initial.pydb"
ihostfname = "ihosts.pydb"

class Replicator():

    def __init__(self, verbose = 0, pgdebug = 0):
        self.verbose = verbose
        self. pgdebug = pgdebug
        self.packer = pyvpacker.packbin()
        self.start_replication()
        self.dbfarr = []
        self.dbdarr = []
        self.hostdarr = []

    def start_replication(self):
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
            time.sleep(2)
            if self.pgdebug > 5:
                print("Replicator cycle", time.time())
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

    # Scan chain dir for replication data
    def scandir(self, dirname):

        fname = os.path.join(pyservsup.globals.paydir, dirname)

        rfile = os.path.join(fname, replicname)
        #print("rfile: ", rfile)
        repcore = self.softcreate(self.dbfarr, rfile, twinchain.TwinCore)
        #print(repcore)

        if self.pgdebug > 5:
            ttt = time.time()
        for bb in range(repcore.getdbsize()):
            try:
                rec = repcore.get_rec(bb)
            except:
                print("Database", sys.exc_info())
                continue

            if not rec:
                continue;   # Deleted record

            # Increment count:
            arr = self.packer.decode_data(rec[1])[0]
            #print("head:", rec[0], "arr:", arr[0])
            arr[0] = "%05d" % (int(arr[0]) + 1)
            strx = str(self.packer.encode_data("", arr))
            ret = repcore.save_data(rec[0], strx, True)
            repcore.flush()

            if int(arr[0]) < 4:
                #print("rec:", rec[0], arr[0], arr[1], arr[2])
                success = self.replicate(dirname, rec[0])

            #if int(arr[0]) < 14 and int(arr[0]) > 10:
            #    print("rec:", rec[0], arr[0], arr[1], arr[2])
            #    self.replicate(rec[0])

            if int(arr[0]) > 6:
                print("del rec:", rec[0], arr[0], arr[1], arr[2])
                ret = repcore.del_rec_bykey(rec[0])
                repcore.flush()

        #if self.pgdebug > 5:
        #    print("db repl %.3f" % ((time.time() - ttt) * 1000) )

    # Replicate this to all the hostsin the list
    def replicate(self, dirname, recx):
        ret = 0
        fname = os.path.join(pyservsup.globals.paydir, dirname)
        dfname = os.path.join(fname, datafname)
        #print("dfname: ", dfname)
        datacore = self.softcreate(self.dbdarr, dfname, twinchain.TwinChain)
        #print("dbsize", datacore.getdbsize())
        #print("recx", recx)
        rec = datacore.retrieve(recx, 1)
        #print("rec", rec[0][1])

        arr = self.packer.decode_data(rec[0][1])[0]
        #print("arr", arr)

        dicx = {}
        for aa in range(len(arr)//2):
            dicx[arr[2*aa]] = arr[2*aa+1]

        if not dicx.get('replicated'):
            dicx['replicated'] = 1
        else:
            dicx['replicated'] += 1
        rec2 =  [recx, dicx]
        #print("rec2", rec2)
        #print("dicx", dicx)
        #arr2 = self.packer.encode_data("", recx, dicx)
        #print(arr2)

        # Relicate on a per host basis
        hfname = os.path.join(pyservsup.globals.myhome, ihostfname)
        pyservsup.globals.paydir
        print("hfname: ", hfname)
        hostcore = self.softcreate(self.hostdarr, hfname, twinchain.TwinChain)
        ret = 0
        for bb in range(hostcore.getdbsize()):
            try:
                rec = hostcore.get_rec(bb)
                #print(bb, "rec", rec)
            except:
                #print("Database EXC", sys.exc_info())
                pass
            if not rec:
                continue;   # Deleted record
            self.transmit(rec[0].decode(), dirname, rec2)
        return ret

    def transmit(self, hostport, dirname, data):

        ret = 0
        hp = hostport.split(":")

        print("Replicating to Host", hp, "dirname", dirname)

        hand = pyclisup.CliSup()
        try:
            respc = hand.connect(hp[0], int(hp[1]))
        except:
            print( "Cannot connect to:", hp, sys.exc_info()[1])
            return 0

        class Blank(): pass
        conf = Blank()
        hand.start_session(conf)
        print(conf.sess_key[:24])
        #resp3 = hand.client(["hello", "world"] , conf.sess_key, False)
        #if resp3[0]  != "OK":
        #    print("Hello ERR Resp:", resp3)
        #    return ret
        #print("Hello Resp:", resp3)

        cresp = hand.client(["user", "admin"], conf.sess_key)
        print ("Server user respo:", cresp)

        cresp = hand.client(["pass", "1234"], conf.sess_key)
        print ("Server pass resp:", cresp)

        resp3 = hand.client(["rput", dirname, data] , conf.sess_key, False)
        if resp3[0]  != "OK":
            print("rput ERR Resp:", resp3)
            return ret
        print ("Server rput resp:", cresp)

        resp3 = hand.client(["quit"], conf.sess_key, False)
        print ("Server quit resp:", cresp)

        # Success, mark record
        ret = True
        return ret

# EOF
