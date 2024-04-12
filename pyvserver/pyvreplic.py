#!/usr/bin/env python3

import os, sys

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

import getopt, signal, select, string, time
import tarfile, subprocess, struct, platform, datetime
import socket, threading, tracemalloc, inspect, socketserver

import pyvpacker

# This repairs the path from local run to pip run.
# Remove pip version for local tests
try:
    from pyvcommon import support
    # Get Parent of module root
    base = os.path.dirname(os.path.realpath(support.__file__))
    #print("base", base)
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base, "..", "pyvcommon"))
    sys.path.append(os.path.join(base, "..", "pyvserver"))

except:
    base = os.path.dirname(os.path.realpath(__file__))
    #print("local base", base)
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    from pyvcommon import support

from pyvcommon import support, pyservsup, pyclisup
from pyvcommon import pydata, pysyslog, comline, pyvhash

from pydbase import twincore, twinchain

replicname = "replic.pydb"
datafname = "initial.pydb"
ihostfname = "ihosts.pydb"

MAX_DBSIZE = 20                 # Size of DB when vacuum

class Blank(): pass

class Replicator():

    def __init__(self, verbose = 0, pgdebug = 0):
        self.verbose = verbose
        self.pgdebug = pgdebug
        self.packer = pyvpacker.packbin()
        self.dbfarr = []
        self.dbdarr = []
        self.hostdarr = []

    def _print_handles(self):

        ''' Debug helper '''
        open_file_handles = os.listdir('/proc/self/fd')
        print('open file handles: ' + ', '.join(map(str, open_file_handles)))

    def rep_run(self):

        ''' Main entry point for replication. '''

        while True:

            ddd = os.listdir(pyservsup.globals.chaindir )
            for aa in ddd:
                aaa = os.path.join(pyservsup.globals.chaindir, aa)
                if not os.path.isdir(aaa):
                    continue
                #print(aaa)
                fname = os.path.join(aaa, replicname)
                if not os.path.isfile(fname):
                    continue
                self.scandir(aa)
            time.sleep(1)

    def scandir(self, dirname):

        ''' Scan chain dir for replication data. '''

        if self.pgdebug > 9:
            print("Replicator cycle", "%.3f "% time.time(), dirname)

        wastrans = False
        fname = os.path.join(pyservsup.globals.chaindir, dirname)
        rfile = os.path.join(fname, replicname)
        #print("rfile: ", rfile)
        repcore = twinchain.TwinCore(rfile)
        #repcore.pgdebug = 10
        #repcore.core_verbose = 5
        dbsize = repcore.getdbsize()
        if conf.pgdebug > 6:
            repcore.showdel = True

        if conf.pgdebug > 3:
            print("dbname:", rfile, "dbsize:", dbsize)
        for bb in range(dbsize):
            try:
                rec = repcore.get_rec(bb)
            except:
                print("Exc on get_rec", sys.exc_info())
                continue
            if not rec:
                continue;   # Deleted record
            print("head:", rec[0], "arr:", rec[1])
            arr = self.packer.decode_data(rec[1])[0]
            #print("arr:", arr)
            # Increment count:
            cntstr2 = "00000"
            cntstr3 = "00000"
            cntstr = "%05d" % (int(arr['count1']) + 1)
            arr['count1'] = cntstr
            #print("arr:", arr)
            if  not int(arr['count2']):
                #if  int(cntstr) > 1  and int(cntstr) < 4:

                # condition for transmit try
                tryit =  int(arr['count3'])  > 0 and int(cntstr) == 6
                tryit |= int(arr['count3']) == 0 and int(cntstr) == 1

                if tryit:
                    wastrans = True
                    success = self.replicate(dirname, rec[0])
                    if success:
                        if self.pgdebug > 5:
                            print("Succeeded", rec[0])
                         # Increment success count:
                        cntstr2 = "%05d" % (int(arr['count2']) + 1)
                        arr['count2'] = cntstr2
                    else:
                        if self.pgdebug > 0:
                            print("Failed", rec[0])
                         # Increment failure count:
                        cntstr3 = "%05d" % (int(arr['count3']) + 1)
                        arr['count3'] = cntstr3
                        arr['count1'] = 0
            else:
                if self.pgdebug > 2:
                    print("Marked done", arr['header'])

            strx = str(self.packer.encode_data("", arr))
            #print("Save rep", rec[0], strx)
            #ttt = time.time()
            ret = repcore.save_data(rec[0], strx, True)
            #print("db save %.3f" % ((time.time() - ttt) * 1000) )

            # Failed? Keep it for a while
            delok = 0
            if int(cntstr3) == 0:
                if int(cntstr) > 6:
                    #print("del rec:", rec[0])
                    delok = True
            else:
                if int(cntstr3) > 3:
                    delok = True
            if delok:
                ret = repcore.del_rec_bykey(rec[0])

        if dbsize > MAX_DBSIZE:

            if self.pgdebug > 2:
                print("vacuuming", dbsize)
            if self.pgdebug > 5:
                ttt = time.time()
            repcore.vacuum()
            if self.pgdebug > 5:
                print("db vacuum %.3f" % ((time.time() - ttt) * 1000) )

        del repcore

        if wastrans:
            if self.pgdebug > 5:
                self._print_handles()

    def replicate(self, dirname, recx):

        ''' Replicate this to all the hosts in the list. '''

        if self.pgdebug > 2:
            print("replicate", dirname, recx)
        if type(recx) == type(b""):
            recx = recx.decode()
        ret = 0
        fname = os.path.join(pyservsup.globals.chaindir, dirname)
        dfname = os.path.join(fname, datafname)

        #print("dfname: ", dfname)
        #if not os.path.isfile(dfname):
        #    return
        #datacore = self.softcreate(self.dbdarr, dfname, twinchain.TwinChain)
        datacore = twinchain.TwinChain(dfname)

        #print("dbsize", datacore.getdbsize())
        #print("recx", recx)
        try:
            rec = datacore.get_data_bykey(recx)
        except:
            print("Replicate: cannot get record", sys.exc_info)
        if not rec:
            #print("Empty record on replicate")
            return
        if self.pgdebug > 8:
            print("rec", rec)
        #print("rex", rec[0][1][1])
        arr = self.packer.decode_data(rec[0][1][1])

        # Decorate 'replicated' variable
        try:
            arr[0]['Replicated'] += 1
        except:
            pass
        #print(arr)

        del datacore

        pvh = pyvhash.BcData(arr[0])
        #pvh.hasharr(); pvh.powarr()
        if self.pgdebug > 5:
            print("pyvhash", pvh.datax, pvh.checkhash(), pvh.checkpow())

        # Replicate on a per host basis
        hfname = os.path.join(pyservsup.globals.myhome, ihostfname)
        #print("hfname", hfname)
        #hostcore = self.softcreate(self.hostdarr, hfname, twincore.TwinCore)
        hostcore = twincore.TwinCore(hfname)

        hostrec = hostcore.getdbsize()
        if hostrec == 0:
            print("No hosts to replicate to.")
            del hostcore
            return

        ret = 0
        for bb in range(hostrec):
            try:
                hrec = hostcore.get_rec(bb)
            except:
                pass
            if not hrec:
                continue;       # Deleted record

            if self.pgdebug > 5:
                print("transmit to host", hrec, dirname, pvh.datax['header'])

            ret = self.transmit(hrec[0], dirname, pvh.datax)
        del hostcore
        return ret

    def transmit(self, hostport, dirname, data):

        ''' Transmit to one particular host, Return True for success '''

        if self.pgdebug > 0:
            print("Transmitting:", hostport, dirname, data['header'])

        hp = hostport.decode().split(":")
        ret = 0
        hand = pyclisup.CliSup()
        try:
            respc = hand.connect(hp[0], int(hp[1]))
        except:
            print( "Cannot connect to:", hp, sys.exc_info()[1])
            # Failure, log it
            pysyslog.repliclog("Cannot Connect:", hostport.decode(), dirname, data['header'])
            return False

        conf = Blank()
        hand.start_session(conf)
        #print(conf.sess_key[:24])
        cresp = hand.client(["user", "admin"], conf.sess_key)
        if self.pgdebug > 5:
            print ("Server user respo:", cresp)
        cresp = hand.client(["pass", "1234"], conf.sess_key)
        if self.pgdebug > 5:
            print ("Server pass resp:", cresp)
        if cresp[0]  != "OK":
            print("Error on connecting, invalid pass")
            cresp = hand.client(["quit"], conf.sess_key, False)
            hand.close()
            return ret
        cresp = hand.client(["rput", dirname, data] , conf.sess_key, False)
        if cresp[0]  != "OK":
            print("rput ERR Resp:", cresp)
            cresp = hand.client(["quit"], conf.sess_key, False)
            hand.close()
            return ret
        if self.pgdebug > 2:
            print ("Server rput resp:", cresp)
        cresp = hand.client(["quit"], conf.sess_key, False)
        #print ("Server quit resp:", cresp)
        hand.close()

        # Success, log it
        pysyslog.repliclog("Replicated", hostport.decode(), dirname, data['header'])

        # Success, mark record
        ret = True
        return ret

optarr = []
optarr.append ( ["r:",  "dataroot=", "droot",  "pyvserver",  None, "Root for server data"] )
optarr.append ( ["m:",  "dumpdata=", "kind",  "",  None, "Dump replicator data for 'kind'"] )

optarr += comline.optarrlong

# Replace help sting on pprt
for aa in range(len(optarr)):
    if optarr[aa][0] == "p:":
        optarr[aa] = ["p:", "port=", "port", "6666", None, "Host port to replicate to"]

#print(optarr)

comline.sethead("Pull directly from database for replication.")
comline.setfoot("Use quote for multiple option strings.")
comline.setargs("[options] [hostname_to]")
comline.setprog(os.path.basename(sys.argv[0]))
conf = comline.ConfigLong(optarr)

def mainfunct():

    try:
        args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print(sys.exc_info())
        sys.exit(1)

    # Comline processed, go

    if conf.pgdebug > 9:
        conf.printvars()

    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf

    slogfile = os.path.join(pyservsup.globals.myhome, "log", "pyvserver.log")
    rlogfile = os.path.join(pyservsup.globals.myhome, "log", "pyvreplic.log")
    pysyslog.init_loggers(
            ("system", slogfile), ("replic", rlogfile))

    pysyslog.repliclog("Replicator started")

    if conf.kind:
        print("Dump replicator database:")
        packer = pyvpacker.packbin()
        fname = os.path.join(pyservsup.globals.chaindir, conf.kind)
        rfile = os.path.join(fname, replicname)
        print("rfile: ", rfile)
        try:
            repcore = twinchain.TwinCore(rfile)
            repcore.showdel = True
        except:
            print("No database here", rfile)
            sys.exit()

        dbsize = repcore.getdbsize()
        #print("dbsize", dbsize)
        for bb in range(dbsize):
            try:
                rec = repcore.get_rec(bb)
            except:
                print("Exc on get_rec", sys.exc_info())
                continue
            if rec[0] == b"del":
                #print("deleted:", rec[1])
                # Shift one off for deleted values
                arr = packer.decode_data(rec[2])[0]
                #print("del arr:", arr)
            else:
                arr = packer.decode_data(rec[1])[0]
                #print("arr:", arr)

            dd = datetime.datetime.strptime(arr['now'], pyvhash.datefmt)
            print("header:", arr['header'], arr['now'], dd)

        sys.exit()

    if conf.verbose:
        print("Started replicator ... ")
    repl = Replicator(conf.verbose, conf.pgdebug)
    repl.rep_run()

if __name__ == '__main__':

    mainfunct()

# EOF
