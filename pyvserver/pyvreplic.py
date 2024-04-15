#!/usr/bin/env python3

# Too many misc crappers like dyn properties
# pylint: disable=E1101
# pylint: disable=C0103
# pylint: disable=C0413
# pylint: disable=C0209
# pylint: disable=W0201
# pylint: disable=W0702     # Bare exceptions
# pylint: disable=W0602     # No global assignment

'''  <pre>
     Replicator, determine if  record is scheduled to replicate

     We have 3 schedules, much like the email servers.

     First:
       try  3 times (6 sec)

     Second:
       try 3 times every 4 hours

     Third:
        if attempt period period larger than a day, every 8 hours

     Removal:
        if attempt period period larger 4 days, stop trying
            delete state record
            make a note in the replicator log of giving up

     Use the -s option to turn on devel timing (for tests)
     The devel version will do:
                Stage1:     0-6
                Stage2:     7-149 timediff % 14 + 6 sec
                Stage_3:    150-199 timediff % 28
                remove if   >= 200
     The production version will do:
                Stage1:     0-6
                Stage2:     60*60*4
                Stage_3:    60*60*24
                remove if >  60*60*24*4

     </pre> '''

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

class Blank(): pass

TIMING = Blank()

class Blank():
    ''' Empth class for config data '''


def cutid(strx, beg = 13, end = 8):
    ''' Return a shortened string with '...' separator '''
    return strx[:beg] + "..." +strx[-end:]

def between(val, mmm, xxx):

    ''' Return True in number (val) is between mmm and xxx, inclusive.

    '''
    if val >= mmm and val <= xxx:
        return True
    else:
        return False

def print_handles(strx = ""):

    ''' Debug helper. Only on Linux. '''

    try:
        import fcntl
    except ImportError:
        fcntl = None
        return              # no fnctl on windows
    except:
        print(sys.exc_info())
        pass

    open_file_handles = os.listdir('/proc/self/fd')
    print(strx, 'open file handles: ' + ', '.join(map(str, open_file_handles)))

class Replicator():

    ''' This embodies the state machine of the replicator '''

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

                # Save it back as replicate stage 1
                arr['processed'] = "%05d" % (1)
                arr2 = self.packer.encode_data("", arr)
                repcore.save_data(rec[0], arr2, replace=True)

        self.process_statedata(dirname)
        del repcore

        if  self.runcount and self.runcount % 10 == 0:
            self.depclean(dirname)

    def depclean(self, dirname):

        ''' Periodically clean the replicator databases for entries
         that are done, entries that do not have any pending action.
         Databases are vacuumed if size  exceed MAX_DBSIZE.

         '''

        #if conf.pgdebug > 4:
        #    print("Dependency cleanup")

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
                canclean.append((bb, rarr['header']))

        for dd in canclean:
            if conf.pgdebug > 4:
                print("Cleaning repl rec:", dd[1])
            repcore.del_rec(dd[0])

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

        ''' Create replicator state data on a per host basis.
        This captures the current state of ihosts, and creates
        jobs descriptiond for replication.
        Ihosts added later do not have an effect on relication
        of the current data. Use pyvcli_replic.py for that.
        '''

        ret = 0
        #if self.pgdebug > 3:
        #    print("host rep", arr['header'])
        #if self.pgdebug > 5:
        #    print("host rep data", arr)

        hostcore = twincore.TwinCore(self.hfname)
        hostrec = hostcore.getdbsize()

        stname = os.path.join(pyservsup.globals.chaindir, dirname,  STATE_FNAME)
        print("state fname:", stname)

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
                    print("Create state rec:", comboname)
                # Create state record
                ttt = time.time()
                dd = datetime.datetime.fromtimestamp(ttt)
                fdt = dd.strftime(pyvhash.datefmt)
                idt = dd.isoformat()
                # New record for state data
                xarr =  {
                    "header" : arr['header'],
                    "Record" : comboname,
                    "host" : harr,
                    "stamp": ttt,  "iso": idt, "LastAttempt": fdt,
                    "orgnow" : arr['now'],
                    "orgstamp" : arr['stamp'],
                    "count": "00000",
                    "status": "00000",
                    # Sun 14.Apr.2024 removed counts
                    #"count2" : "00000",  #"count3" : "00000",
                    }

                #print("xarr:", xarr)
                xarr2 = self.packer.encode_data("", xarr)
                #print("xarr2:", xarr2)
                statecore.save_data(comboname, xarr2)
        del statecore
        del hostcore

    def process_statedata(self, dirname):

        ''' Process states for this data. When done, mark entries
        appropriately. '''

        stname = os.path.join(pyservsup.globals.chaindir, dirname,  STATE_FNAME)
        statecore = twincore.TwinCore(stname)
        staterec = statecore.getdbsize()
        remsced = []
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
                remsced.append((aa, dec['header']))
                continue

            if self.pgdebug > 6:
                print("State data:", dec)
                #print("Sdata:", dec['header'], dec['host'], dec['stamp'])
            elif self.pgdebug > 5:
                print("State data:", dec['header'], dec['host'])

            tdiff = int(time.time() - float(dec['orgstamp']))
            tdiff = (tdiff //2) * 2 # Make it even. Make sure stage numbers are even

            #if conf.pgdebug > 2:
            #    print("Scedule:", tdiff, dec['header'], dec['host'], "count:", dec['count'])

            #if conf.pgdebug > 2:
            #    print(time.time(), dec['stamp'])
            #    print("tdiff", tdiff)

            doit = False
            if tdiff <= TIMING.stage_1_lim:
                if tdiff % TIMING.stage_1_freq == 0:
                    doit = True
            elif tdiff <= TIMING.stage_2_lim:
                if tdiff % TIMING.stage_2_freq == 0:
                    if between(tdiff, tdiff, tdiff + TIMING.retrytime):
                        doit = True
            elif tdiff <= TIMING.stage_3_lim:
                 if tdiff % TIMING.stage_3_freq == 0:
                    if between(tdiff, tdiff, tdiff + TIMING.retrytime):
                            doit = True
            else:
                if conf.loglev > 0:
                    pysyslog.repliclog("Giving up:", dec['host'], dirname, dec['header'])
                remsced.append((aa, dec['header']))

            if not doit:
                continue

            if conf.verbose:
                print("Attempt at:", tdiff, dec['header'], dec['host'], "count:", dec['count'])

            # Try again ... Save attempt date
            ttt = time.time()
            dd = datetime.datetime.fromtimestamp(ttt)
            fdt = dd.strftime(pyvhash.datefmt)
            idt = dd.isoformat()

            dec['stamp'] = ttt;  dec["iso"] =  idt
            dec["LastAttempt"]= fdt
            # Increment try count
            dec["count"] = "%05d" % (int(dec['count']) + 1)

            # Make delivery attempt
            ret = self.replicate(dirname, dec)
            #print("Rep success", ret)
            if ret:
                # mark success
                dec["status"] =  "%05d" % (int(dec['status']) + 1)

            xarr3 = self.packer.encode_data("", dec)
            statecore.save_data(rec[0], xarr3, replace=True)

        for bb in remsced:
            if conf.pgdebug > 3:
                print("Removing state for:", bb[1])
            statecore.del_rec(bb[0])

        del statecore
        #print_handles()

    def replicate(self, dirname, dec):

        ''' Replicate this one entry in the state record '''

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

        ''' Transmit one particular entry to one particular host.
            Return True for successful transfer.
            Logs (if enabled) will contain success / falure report
            and the failure reason string.
        '''

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
        if conf.loglev > 0:
            pysyslog.repliclog("OK:", dec['host'], cutid(data['header']))

        # Success, mark record
        ret = True
        return ret

def dumprep():

    ''' Dump replicator data currently active. Use del flag
        to see recent actions. The recent action visibilty is limited
        to the period of last vacuum operation.
     '''

    if conf.verbose:
        print("Dump replicator databases:")

    packer = pyvpacker.packbin()
    fname = os.path.join(pyservsup.globals.chaindir, conf.kind)
    rfile = os.path.join(fname, REPLIC_FNAME)
    if conf.pgdebug > 3:
        print("rfile: ", rfile)
    try:
        repcore = twinchain.TwinCore(rfile)
        if conf.sdel:
            repcore.showdel = True
    except:
        print("No database here", rfile)
        sys.exit()

    print("Replicator data:")
    dbsize = repcore.getdbsize()
    #print("dbsize", dbsize)
    for bb in range(dbsize):
        try:
            rec = repcore.get_rec(bb)
        except:
            print("Exc on get_rec", sys.exc_info())
            continue
        if not rec:
            continue    # Deleted record

        if rec[0] == b"del":
            #print("deleted:",)
            # Shift one off for deleted values
            arr = packer.decode_data(rec[2])[0]
            #print("del arr:", arr)
        else:
            arr = packer.decode_data(rec[1])[0]
            #print("arr:", arr)

        if conf.verbose:
            print("arr:", arr)
        else:
            dd = datetime.datetime.strptime(arr['now'], pyvhash.datefmt)
            print(arr['header'], dd, "Processed:", arr['processed'])

    stname = os.path.join(pyservsup.globals.chaindir, conf.kind,  STATE_FNAME)
    statecore = twincore.TwinCore(stname)
    staterec = statecore.getdbsize()
    if conf.sdel:
            statecore.showdel = True
    if conf.pgdebug > 3:
        print("stname: ", stname)

    print("State data:")
    for cc in range(staterec):
        try:
            srec = statecore.get_rec(cc)
        except:
            pass
        if not srec:
            continue        # Deleted record

        if srec[0] == b"del":
            sarr = packer.decode_data(srec[2])[0]
        else:
            sarr = packer.decode_data(srec[1])[0]

        if conf.verbose:
            print("sarr:", sarr)
        else:
            dd = datetime.datetime.strptime(sarr['orgnow'], pyvhash.datefmt)
            print(sarr['header'], dd, sarr['host'], "Count:", sarr['count'])

optarr = []
optarr.append ( ["r:",  "dataroot=", "droot",  "pyvserver",
                        None, "Root for server data default='~/pyvserver'"] )
optarr.append ( ["m:",  "dumpdata=", "kind",  "",
                        None, "Dump replicator data for data 'kind'"] )
optarr.append ( ["e",  "showdel=", "sdel",  0,
                        None, "Show deleted records on dump"] )
optarr.append ( ["t:",  "time=", "timedel",  2,
                        None, "Time between replications default='2s'"] )
optarr.append ( ["l:",  "loglevel=", "loglev",  1,
                        None, "Log level 0=none 1=success 2=reason default='1'"] )
optarr.append ( ["s",  "ttime", "ttime",  0,
                        None, "Test timing (vs production)"] )

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
comline.setfoot("Use quote for multiple option strings.")
comline.setargs("[options] ")
comline.setprog(os.path.basename(__file__))
conf = comline.ConfigLong(optarr)

def mainfunct():

    ''' Main entry point. SETUP script will call this '''
    try:
        args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print(sys.exc_info())
        sys.exit(1)

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

    TIMING.retrytime = 6

    # Keep them even numbered
    if conf.ttime:
        tstr = "Test timing"
        TIMING.stage_1_lim = 6
        TIMING.stage_2_lim = 60
        TIMING.stage_3_lim = 120

        TIMING.stage_1_freq = 1
        TIMING.stage_2_freq = 14
        TIMING.stage_3_freq = 28
    else:
        tstr = "Prod. timing"
        TIMING.stage_1_lim = 6
        TIMING.stage_2_lim = 60*60*24
        TIMING.stage_3_lim = 60*60*24*4

        TIMING.stage_1_freq = 1
        TIMING.stage_2_freq = 60*60*4
        TIMING.stage_3_freq = 60*60*8

    if conf.verbose:
        print("Replicator started with", tstr, "at:", conf.droot)

    if conf.loglev > 0:
        pysyslog.repliclog("Started with", tstr, "at:", conf.droot)

    repl = Replicator(conf.verbose, conf.pgdebug)
    repl.rep_run()

if __name__ == '__main__':

    mainfunct()

# EOF
