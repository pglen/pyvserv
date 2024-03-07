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
            if pyservsup.globals.conf.norepl:
                #print("No replication")
                continue

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

    # Scan chain dir for replication data
    def scandir(self, dirname):

        fname = os.path.join(pyservsup.globals.paydir, dirname)
        rfile = os.path.join(fname, replicname)
        #print("rfile: ", rfile)
        repcore = self.softcreate(self.dbfarr, rfile, twinchain.TwinCore)

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
            #print("head:", rec[0], "arr:", rec[1])
            arr = self.packer.decode_data(rec[1])[0]

            # Increment count:
            cntstr = "%05d" % (int(arr['count1']) + 1)
            arr['count1'] = cntstr

            #print("arr:", arr)
            if  not int(arr['count2']):
                if  int(cntstr) > 1  and int(cntstr) < 4:
                    success = self.replicate(dirname, rec[0])
                    if success:
                        print("Succeeded")
                         # Increment success count:
                        cntstr2 = "%05d" % (int(arr['count2']) + 1)
                        arr['count2'] = cntstr2
            else:
                pass
                #print("Marked done")

            strx = str(self.packer.encode_data("", arr))
            ret = repcore.save_data(rec[0], strx, True)
            repcore.flush()

            if int(cntstr) > 6:
                print("del rec:", rec[0])
                ret = repcore.del_rec_bykey(rec[0])
                repcore.flush()

    # Replicate this to all the hosts in the list
    def replicate(self, dirname, recx):
        print("replicate", dirname, recx)
        ret = 0
        fname = os.path.join(pyservsup.globals.paydir, dirname)
        dfname = os.path.join(fname, datafname)

        #print("dfname: ", dfname)
        #if not os.path.isfile(dfname):
        #    return
        datacore = self.softcreate(self.dbdarr, dfname, twinchain.TwinChain)
        #print("dbsize", datacore.getdbsize())
        #print("recx", recx)
        rec = datacore.get_(recx)
        if not rec:
            print("Empty record on replicate")
            return
        #print("rec", rec)
        arr = self.packer.decode_data(rec[0][1])[0]
        print("arr", arr)
        if 'replicate' in arr:
            arr['Replicated'] += 1
        else:
            arr['Replicated'] = 1
        #print("arr", arr)

        # Relicate on a per host basis
        hfname = os.path.join(pyservsup.globals.myhome, ihostfname)
        hostcore = self.softcreate(self.hostdarr, hfname, twinchain.TwinChain)
        ret = 0
        for bb in range(hostcore.getdbsize()):
            try:
                rec = hostcore.get_rec(bb)
            except:
                pass
            if not rec:
                continue;   # Deleted record
            #print("host", rec[0])
            self.transmit(rec[0].decode(), dirname, arr)
            ret = True
        return ret

    def transmit(self, hostport, dirname, data):

        ret = 0
        hp = hostport.split(":")

        print("Replicating to Host", hp, "dirname", dirname)
        print("Data", data)

        hand = pyclisup.CliSup()
        try:
            respc = hand.connect(hp[0], int(hp[1]))
        except:
            print( "Cannot connect to:", hp, sys.exc_info()[1])
            return 0

        class Blank(): pass
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

        cresp = hand.client(["rput", dirname, data] , conf.sess_key, False)
        if cresp[0]  != "OK":
            print("rput ERR Resp:", cresp)
            return ret
        print ("Server rput resp:", cresp)

        cresp = hand.client(["quit"], conf.sess_key, False)
        print ("Server quit resp:", cresp)

        # Success, mark record
        ret = True
        return ret

# EOF
