#!/usr/bin/env python3

# Too many misc crappers like dyn properties
# pylint: disable=E1101
# pylint: disable=C0103
# pylint: disable=C0413
# pylint: disable=C0209
# pylint: disable=W0201
# pylint: disable=W0702     # Bare exceptions
# pylint: disable=W0602     # No global assignment

''' Replicator '''

import os, sys

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

import getopt
import time
import datetime
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
from pyvcommon import pysyslog, comline, pyvhash

from pydbase import twincore, twinchain

REPLIC_FNAME  = "replic.pydb"
DATA_FNAME    = "initial.pydb"
IHOST_FNAME   = "ihosts.pydb"
STATE_FNAME   = "rstate.pydb"

MAX_DBSIZE = 20                 # Size of DB when vacuum

class Blank():
    ''' For conf '''

def cutid(strx):
    return strx[:13] + "..." +strx[-8:]

def between(val, mmm, xxx):
    if val >= mmm and val <= xxx:
        return True
    else:
        return False

def print_handles(strx = ""):

    ''' Debug helper '''
    open_file_handles = os.listdir('/proc/self/fd')
    print(strx, 'open file handles: ' + ', '.join(map(str, open_file_handles)))


class Replicator():

    def __init__(self, verbose = 0, pgdebug = 0):
        self.verbose = verbose
        self.pgdebug = pgdebug
        self.packer = pyvpacker.packbin()
        self.dbfarr = []
        self.dbdarr = []
        self.hostdarr = []
        self.hfname = os.path.join(pyservsup.globals.myhome, IHOST_FNAME)
        self.runcount = 0

    def rep_run(self):

        ''' Main entry point for replication. '''

        while True:
            # Replicate for all kinds
            ddd = os.listdir(pyservsup.globals.chaindir )
            for aa in ddd:
                aaa = os.path.join(pyservsup.globals.chaindir, aa)
                if not os.path.isdir(aaa):
                    continue
                #print(aaa)
                fname = os.path.join(aaa, REPLIC_FNAME)
                if not os.path.isfile(fname):
                    continue
                self.scandir(aa)
            self.runcount += 1
            time.sleep(conf.timedel)

    def scandir(self, dirname):

        ''' Scan chain dir for replication data. '''

        if self.pgdebug > 5:
            print()
            print("Replicator cycle", "%.3f "% time.time(), dirname)

        wastrans = False
        fname = os.path.join(pyservsup.globals.chaindir, dirname)
        rfile = os.path.join(fname, REPLIC_FNAME)
        #print("rfile: ", rfile)
        repcore = twinchain.TwinCore(rfile)
        dbsize = repcore.getdbsize()
        #repcore.pgdebug = conf.pgdebug
        #repcore.core_verbose = 5
        #if conf.pgdebug > 6:
        #    repcore.showdel = True

        #if conf.pgdebug > 3:
        #    print("dbname:", rfile, "dbsize:", dbsize)

        # Scan database, create sub replicator entries for all hosts
        for bb in range(dbsize):
            try:
                rec = repcore.get_rec(bb)
            except:
                print("Exc on get_rec", sys.exc_info())
                continue
            if not rec:
                continue   # Deleted record

            if conf.pgdebug > 9:
                print("rec:", rec)
            arr = self.packer.decode_data(rec[1])[0]

            if conf.pgdebug > 7:
                print("head:", rec[0], "arr:", arr)

            if not int(arr['processed']):
                #print("Processed:", arr['processed'])
                self.create_perhost(dirname, arr)

                # Save it back as relicate stage 1
                arr['processed'] = "%05d" % 1
                arr2 = self.packer.encode_data("", arr)
                repcore.save_data(rec[0], arr2, replace=True)

        self.process_statedata(dirname)
        del repcore

        if  self.runcount and self.runcount % 10 == 0:
            self.depclean(dirname)

    def depclean(self, dirname):

        #print("Exec dependency cleanup")

        fname = os.path.join(pyservsup.globals.chaindir, dirname)
        rfile = os.path.join(fname, REPLIC_FNAME)
        repcore = twinchain.TwinCore(rfile)
        dbsize = repcore.getdbsize()

        stname = os.path.join(pyservsup.globals.chaindir, dirname,  STATE_FNAME)
        statecore = twincore.TwinCore(stname)
        staterec = statecore.getdbsize()
        canclean = []
        for bb in range(dbsize):
            try:
                rec = repcore.get_rec(bb)
            except:
                continue
            if not rec:
                continue   # Deleted record
            rarr = self.packer.decode_data(rec[1])[0]

            found = False
            for cc in range(staterec):
                try:
                    srec = statecore.get_rec(cc)
                except:
                    pass
                if not srec:
                    continue        # Deleted record
                sarr = self.packer.decode_data(srec[1])[0]
                #print("cleanup", rarr['header'], sarr['header'])
                if rarr['header'] == sarr['header']:
                    found = True
            if not found:
                #print("Can clean:", rarr['header'])
                canclean.append(bb)

        for dd in canclean:
            repcore.del_rec(dd)

        if dbsize > MAX_DBSIZE:
            if self.pgdebug > 2:
                print("vacuuming repl", dbsize)
            if self.pgdebug > 5:
                ttt = time.time()
            repcore.vacuum()
            if self.pgdebug > 5:
                print("db vacuum %.3f" % ((time.time() - ttt) * 1000) )

        if staterec > MAX_DBSIZE:
            if self.pgdebug > 2:
                print("vacuuming state", staterec)
            if self.pgdebug > 5:
                ttt = time.time()
            statecore.vacuum()
            if self.pgdebug > 5:
                print("db vacuum %.3f" % ((time.time() - ttt) * 1000) )

        del repcore
        del statecore



    def create_perhost(self, dirname, arr):

        ''' Replicator state data  on a per host basis '''

        ret = 0
        #if self.pgdebug > 3:
        #    print("host rep", arr['header'])
        #if self.pgdebug > 5:
        #    print("host rep data", arr)

        hostcore = twincore.TwinCore(self.hfname)
        hostrec = hostcore.getdbsize()

        stname = os.path.join(pyservsup.globals.chaindir, dirname,  STATE_FNAME)
        statecore = twincore.TwinCore(stname)
        staterec = statecore.getdbsize()

        for bb in range(hostrec):
            try:
                hrec = hostcore.get_rec(bb)
            except:
                print("get host name", sys.exc_info())
                pass
            if not hrec:
                continue        # Deleted record
            harr = self.packer.decode_data(hrec[1])[0]
            #if self.pgdebug > 4:
            #    #print("host header:", arr['header'])
            #    print("host entry:", harr)

            # Create state record if none
            comboname = arr['header'] + "_" + harr
            exists = statecore.retrieve(comboname)
            if not exists:
                if self.pgdebug > 4:
                    print("Create rec", comboname)
                # Create state record
                ttt = time.time()
                dd = datetime.datetime.fromtimestamp(ttt)
                fdt = dd.strftime(pyvhash.datefmt)
                idt = dd.isoformat()
                xarr = {
                        "header" : arr['header'], "Record" : comboname,
                        "host" : harr,
                        "stamp": ttt,  "iso": idt, "LastAttempt": fdt,
                        "orgnow" : arr['now'],
                        "orgstamp" : arr['stamp'],
                        "count1": "00000", "count2" : "00000",
                        "count3" : "00000",
                        "status" : "00000",
                       }
                #print("xarr:", xarr)
                xarr2 = self.packer.encode_data("", xarr)
                #print("xarr2:", xarr2)
                statecore.save_data(comboname, xarr2)
        del statecore
        del hostcore

    def process_statedata(self, dirname):

        ''' Process states for this data '''

        stname = os.path.join(pyservsup.globals.chaindir, dirname,  STATE_FNAME)
        statecore = twincore.TwinCore(stname)
        staterec = statecore.getdbsize()

        remsced  = []

        for aa in range(staterec):
            rec = statecore.get_rec(aa)
            if not rec:
                continue
            # Process it
            dec =  self.packer.decode_data(rec[1])[0]

            # if it succeeded already, do not replicate, remove from database
            if int(dec['status']) != 0:
                if self.pgdebug > 1:
                    print("Replicated already", dec['host'], dec['header'])
                remsced.append(aa)
                continue

            if self.pgdebug > 6:
                print("State data:", dec)
                #print("Sdata:", dec['header'], dec['host'], dec['stamp'])
            elif self.pgdebug > 4:
                print("State data:", dec['header'], dec['host'])

            # See if we are scheduled to replicate
            # We have 3 scedules, much like the email servers
            # First:
            #   try  3 times (6 sec)
            #
            # Second:
            #   try 3 times every 4 hours
            #
            # Third:
            #   if attemp period period larger than a day, every 8 hours
            #
            # Removal:
            #   if attemp period period larger 4 days, stop trying ...
            #   .. and delete record with a note in replic log
            #
            # The dev version will do:
            #            Stage1:    0-6
            #            Stage2:    7-149 timediff % 14 + 6 sec
            #            Stage_3:   150-199 timediff % 28
            #            remove:    >= 200
            # The production version will do:
            #            Stage1:    0-6
            #            Stage2:    60*60*4
            #            Stage_3:   60*60*24
            #           remove >    60*60*24*4

            tdiff = int(time.time() - float(dec['orgstamp']))
            tdiff = (tdiff //2) * 2 # Make it even

            #if conf.pgdebug > 2:
            #    print("Scedule:", tdiff, dec['header'], dec['host'], "count1:", dec['count1'])

            #print(time.time(), dec['stamp'])
            #if conf.pgdebug > 2:
            #    print("tdiff", tdiff)

            doit = False
            if tdiff < 6:
                #if between(tdiff, 0, 5):
                doit = True
            elif tdiff < 100:
                if tdiff % 14 == 0:
                    if between(tdiff, tdiff, tdiff + 6):
                        doit = True
            elif tdiff < 150:
                 if tdiff % 28 == 0:
                    if between(tdiff, tdiff, tdiff + 6):
                            doit = True
            else:
                if conf.loglev > 0:
                    pysyslog.repliclog("Giving up:", dec['host'], dirname, dec['header'])
                remsced.append(aa)

            if not doit:
                continue

            if conf.verbose:
                print("Attempt:", tdiff, dec['header'], dec['host'], "count1:", dec['count1'])

            # Try again ... Save attempt date
            ttt = time.time()
            dd = datetime.datetime.fromtimestamp(ttt)
            fdt = dd.strftime(pyvhash.datefmt)
            idt = dd.isoformat()

            dec['stamp'] = ttt;  dec["iso"] =  idt
            dec["LastAttempt"]= fdt
            # Increment try count
            dec["count1"] = "%05d" % (int(dec['count1']) + 1)

            # Make delivery attempt
            ret = self.replicate(dirname, dec)
            #print("Rep success", ret)
            if ret:
                # mark success
                dec["status"] =  "%05d" % (int(dec['status']) + 1)

            xarr3 = self.packer.encode_data("", dec)
            statecore.save_data(rec[0], xarr3, replace=True)

        for bb in remsced:
            #print("removal sceduled", aa)
            statecore.del_rec(bb)

        del statecore
        #print_handles()

    def replicate(self, dirname, dec):

        ''' Replicate this one host in the state record '''

        #if self.pgdebug > 2:
        #    print("replicate to:", dec['header'])
        #    print("replicate host:", dec['host'])

        ret = 0; rec = []
        fname = os.path.join(pyservsup.globals.chaindir, dirname)
        dfname = os.path.join(fname, DATA_FNAME)
        datacore = twinchain.TwinChain(dfname)
        #print("dbsize", datacore.getdbsize())
        try:
            rec = datacore.get_data_bykey(dec['header'])
        except:
            print("Replicate: cannot get record", sys.exc_info())

        if not rec:
            print("Empty record on replicate.")
            return ret

        del datacore

        #if self.pgdebug > 8:
        #    print("rec", rec)

        arr = self.packer.decode_data(rec[0][1][1])
        # Decorate 'replicated' variable

        if arr[0]['Replicated']:
            print("This entry is replicated already", dec['header'])
            return True

        arr[0]['Replicated'] = arr[0].get("Replicated") + 1
        if self.pgdebug > 9:
            print("payload arr", arr)
        pvh = pyvhash.BcData(arr[0])
        #if self.pgdebug > 7:
        #    print("Checks:", pvh.checkhash(), pvh.checkpow())

        #if self.pgdebug > 5:
        #    print("pyvhash", pvh.datax, pvh.checkhash(), pvh.checkpow())

        ret = self.transmit(dirname, dec, pvh.datax)

        return ret


    def transmit(self, dirname, dec, data):

        ''' Transmit to one particular host, Return True for success '''

        if conf.loglev > 1:
            pysyslog.repliclog("Try:", dec['host'], dirname, data['header'])

        hostx, portx = dec['host'].split(":")

        #if self.pgdebug > 2:
        #    print("Transmitting:", hostx, portx, dirname, data['header'])

        ret = False
        hand = pyclisup.CliSup()
        try:
            respc = hand.connect(hostx, int(portx))
        except:
            errx = str(sys.exc_info()[1]).split(']')[1]

            if self.pgdebug > 1:
                print( "Cannot connect to:", dec['host'], errx)

            # Failure, log it
            if conf.loglev > 1:
                pysyslog.repliclog("Cannot Connect:", dec['host'], errx)
            return ret

        confx = Blank()
        hand.start_session(confx)
        #print(confx.sess_key[:24])
        cresp = hand.login("admin", "1234", confx)
        if self.pgdebug > 5:
            print ("Server logon resp:", cresp)
        if cresp[0]  != "OK":
            print("Error logging in", cresp)
            if conf.loglev > 1:
                pysyslog.repliclog("Fail:", dec['host'], "Error on logging in")
            cresp = hand.client(["quit"], confx.sess_key, False)
            hand.close()
            return ret
        cresp = hand.client(["rput", dirname, data] , confx.sess_key, False)
        if cresp[0]  != "OK":
            print("rput error resp:", cresp)
            if conf.loglev > 1:
                pysyslog.repliclog("Fail:", dec['host'], "Duplicate record.",)
            cresp = hand.client(["quit"], confx.sess_key, False)
            hand.close()
            return ret
        cresp = hand.client(["quit"], confx.sess_key, False)
        hand.close()
        if self.pgdebug > 2:
            print("Success on transmit", dec['host'])

        # Success, log it
        if conf.loglev > 1:
            pysyslog.repliclog("OK:", dec['host'], cutid(data['header']))

        # Success, mark record
        ret = True
        return ret

def dumprep():

    print("Dump replicator databases:")
    packer = pyvpacker.packbin()
    fname = os.path.join(pyservsup.globals.chaindir, conf.kind)
    rfile = os.path.join(fname, REPLIC_FNAME)
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
        if conf.verbose:
            print("arr:", arr)
        else:
            print("header:", arr['header'], arr['now'], dd)

optarr = []
optarr.append ( ["r:",  "dataroot=", "droot",  "pyvserver",
                        None, "Root for server data"] )
optarr.append ( ["m:",  "dumpdata=", "kind",  "",
                        None, "Dump replicator data for 'kind'"] )
optarr.append ( ["t:",  "time=", "timedel",  2,
                        None, "Time delay between replications"] )
optarr.append ( ["l:",  "loglevel=", "loglev",  0,
                        None, "Log level for replicator"] )
optarr += comline.optarrlong
# Replace help string on port
for aa in range(len(optarr)):
    if optarr[aa][0] == "p:":
        #optarr[aa] = ["p:", "port=", "port", "6666",
        #None, "Host port to replicate to"]
        del optarr[aa]
        break
#print(optarr)
comline.sethead("Replicate to hosts by pulling directly from pyvserv database.")
#comline.setfoot("Use quote for multiple option strings.")
comline.setargs("[options] ")
comline.setprog(os.path.basename(__file__))
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
    #if conf.pgdebug > 9:
    #    conf.printvars()

    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf

    slogfile = os.path.join(pyservsup.globals.myhome, "log", "pyvserver.log")
    rlogfile = os.path.join(pyservsup.globals.myhome, "log", "pyvreplic.log")
    pysyslog.init_loggers(
            ("system", slogfile), ("replic", rlogfile))

    if conf.kind:
        dumprep()
        sys.exit()

    if conf.verbose:
        print("Started replicator ... ")

    if conf.loglev:
        pysyslog.repliclog("Replicator started")

    repl = Replicator(conf.verbose, conf.pgdebug)
    repl.rep_run()

if __name__ == '__main__':

    mainfunct()

# EOF
