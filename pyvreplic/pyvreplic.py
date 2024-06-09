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
import signal

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

from pydbase import twincore

import pyvrepsup

REPLIC_FNAME  = "replic.pydb"
DATA_FNAME    = "initial.pydb"
IHOST_FNAME   = "ihosts.pydb"
STATE_FNAME   = "rstate.pydb"
COMP_FNAME    = "rcomp.pydb"

MAX_DBSIZE = 20                 # Size of DB when vacuum

TIMING = pyvrepsup.BlankClass()

try:
    import fcntl
except ImportError:
    fcntl = None
    #return
    # no fnctl on windows
except:
    print(sys.exc_info())
    pass

class Replicator():

    ''' This embodies the state machine of the replicator '''

    def __init__(self):
        self.dbfarr = []
        self.dbdarr = []
        self.hostdarr = []
        self.hfname = os.path.join(pyservsup.globals.myhome, IHOST_FNAME)
        self.runcount = 1

    def repall(self, kind):
        print("Retransmitting:")

        rfile = os.path.join(pyservsup.globals.chaindir, conf.rkind, REPLIC_FNAME)
        print("rfile", rfile)
        repcore = twincore.TwinCore(rfile)
        repdbsize = repcore.getdbsize()

        fname = os.path.join(pyservsup.globals.chaindir, conf.rkind, DATA_FNAME)
        #print("data file", fname)
        datacore = twincore.TwinCore(fname)
        datasize = datacore.getdbsize()
        #print("dbsize", datasize)

        # Scan database, create sub replicator entries for all hosts
        for bb in range(datasize-1, -1, -1):
            try:
                rec = datacore.get_rec(bb)
            except:
                print("Exc on get_rec", sys.exc_info())
                continue
            if not rec:
                continue   # Deleted record

            arr = conf.packer.decode_data(rec[1])[0]
            #print(arr['header'])
            # Create sub entry
            # Save replicator
            ttt = time.time()
            dd = datetime.datetime.fromtimestamp(ttt)
            idt = dd.isoformat()
            now = dd.strftime(pyvhash.datefmt)
            # Prepare data. Do strings so it can be re-written in place
            rrr = {
                    'header' : arr['header'],
                    'now' : now,
                    # Human readable
                    'iso' : idt,
                    'stamp' : ttt,
                    "processed" : "00000",
                    "retrans" : "00001",
                    }
            if conf.pgdebug > 3:
                print("replic req", rrr)

            undec2 = conf.packer.encode_data("", rrr)
            try:
                ret = repcore.save_data(arr['header'], undec2)
            except:
                print("exc on save_data", sys.exc_info()[1])
        del repcore
        del datacore

        #sys.exit(0)

    def rep_run(self):

        ''' Main entry point for replication. '''

        if conf.rkind:
            self.repall(conf.rkind)

        while True:
            # Replicate for all kinds
            try:
                ddd = os.listdir(pyservsup.globals.chaindir)
            except:
                ddd = []

            for aa in ddd:
                aaa = os.path.join(pyservsup.globals.chaindir, aa)
                if not os.path.isdir(aaa):
                    continue
                fname = os.path.join(aaa, REPLIC_FNAME)
                #print("fname", fname, "aa", aa)
                if not os.path.isfile(fname):
                    continue
                self.scandir(aa)
            self.runcount += 1
            # Testing for leaks
            #pyvrepsup.print_handles()
            time.sleep(conf.timedel)

    def scandir(self, dirname):

        ''' Scan chain dir for replication data. '''

        if conf.pgdebug > 9:
            print()
            print("Replicator cycle", "%.3f "% time.time(), dirname)

        wastrans = False
        rfile = os.path.join(pyservsup.globals.chaindir, dirname, REPLIC_FNAME)
        if conf.pgdebug > 9:
            print("scandir rfile: ", rfile)

        repcore = twincore.TwinCore(rfile)
        repdbsize = repcore.getdbsize()

        # Scan database, create sub replicator entries for all hosts
        for bb in range(repdbsize-1, -1, -1):
            try:
                rec = repcore.get_rec(bb)
            except:
                print("Exc on get_rec", sys.exc_info())
                continue
            if not rec:
                continue   # Deleted record

            if conf.pgdebug > 9:
                print("rec:", rec)

            arr = conf.packer.decode_data(rec[1])[0]
            #print("repdb rec arr:", arr)
            #print("repdb rec arr:", arr['header'])

            try:
                val = int(arr.get('processed', 0))
            except:
                val = 0
                #print ("exc processed", sys.exc_info())

            if not val:
                #print("Processed:", arr['processed'], "retrans:", retrans)
                if conf.pgdebug > 7:
                    print("head:", rec[0], "arr:", arr)
                self.create_perhost(dirname, arr)
                # Save it back as replicate stage 1
                arr['processed'] = "%05d" % (1)
                arr2 = conf.packer.encode_data("", arr)
                repcore.save_data(rec[0], arr2, replace=True)

        # Only one scan for retrans
        conf.retrans = False
        self.process_statedata(dirname)
        del repcore

        # Run after we have done forwardingin this session
        if  self.runcount % 10 == 0:
            self.depclean(dirname)

    def create_perhost(self, dirname, arr):

        '''
        Create replicator state data on a per host basis.
        This captures the current state of ihosts, and creates
        jobs descriptions for replication.
        The ihosts added later do not have an effect on replication
        of the current data. Use pyvcli_replic.py for that.
        The feature option -a is meant to take care of re-transmission
        to all hosts.
        '''

        ret = 0

        #if conf.pgdebug > 5:
        #    print("create_perhost()", "dirname:", dirname, " data", arr)

        hostcore = twincore.TwinCore(self.hfname)
        hostbdsize = hostcore.getdbsize()

        stname = os.path.join(pyservsup.globals.chaindir, dirname, STATE_FNAME)

        if conf.pgdebug > 9:
            print("state fname:", stname)

        statecore = twincore.TwinCore(stname)
        staterec = statecore.getdbsize()

        sum = []
        for bb in range(hostbdsize-1, -1, -1):
            try:
                hrec = hostcore.get_rec(bb)
            except:
                print("get host name", sys.exc_info())
                pass
            if not hrec:
                continue        # Deleted record
            #print("hrec", hrec)
            if hrec[0] in sum:
                continue
            sum.append(hrec[0])
            #print("hrec",  hrec)
            harr = conf.packer.decode_data(hrec[1])[0]['PayLoad']

            if conf.pgdebug > 4:
                print("host entry:", harr)

            # Create state record if none
            comboname =  arr['header'] + "_" + harr['host']

            if conf.pgdebug > 4:
                print("Comboname:", comboname)

            exists = False
            for cc in range(staterec-1, -1, -1):
                rec = statecore.get_rec(cc)
                if not rec:
                    continue
                #print("staterec:", rec)
                if rec[0] == comboname:
                    exists = True

            #print("exists", exists)
            if not exists:
                if conf.pgdebug > 2:
                    print("Create record:", comboname)

                # Create state record
                ttt = time.time()
                dd = datetime.datetime.fromtimestamp(ttt)
                fdt = dd.strftime(pyvhash.datefmt)
                idt = dd.isoformat()
                # New record for state data
                xarr =  {
                    "header" :  arr['header'],
                    "Record" :  comboname,
                    "host" :    harr['host'],
                    "stamp":    ttt,  "iso": idt, "LastAttempt": fdt,
                    "orgnow" :  arr['now'],
                    "orgstamp": arr['stamp'],
                    "message" : " " * 32,
                    "count":    "00000",
                    "status":   "00000",
                    "all":      "00000",
                    # Sun 14.Apr.2024 removed counts
                    #"count2" : "00000",  #"count3" : "00000",
                    }

                #print("xarr:", xarr)
                xarr2 = conf.packer.encode_data("", xarr)
                #print("xarr2:", xarr2)
                statecore.save_data(comboname, xarr2)
        del statecore
        del hostcore

    def process_statedata(self, dirname):

        ''' Process states for this data. When done, mark entries
        appropriately. '''

        stname = os.path.join(pyservsup.globals.chaindir, dirname,  STATE_FNAME)

        if conf.pgdebug > 9:
            print("state data file", stname)

        statecore = twincore.TwinCore(stname)
        staterec = statecore.getdbsize()
        remsced = []
        for aa in range(staterec):
            rec = statecore.get_rec(aa)
            if not rec:
                continue
            # Process it
            dec =  conf.packer.decode_data(rec[1])[0]

            # if it succeeded already, do not replicate, remove from database
            if int(dec['status']) != 0:
                if conf.pgdebug > 1:
                    print("Replicated already", dec['host'], dec['header'])
                remsced.append((aa, dec['header']))
                continue

            if conf.pgdebug > 8:
                print("State data:", dec)
            elif conf.pgdebug > 6:
                print("State data:", dec['header'], dec['host'], dec['stamp'])
            elif conf.pgdebug > 5:
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
                    if pyvrepsup.between(tdiff, tdiff, tdiff + TIMING.retrytime):
                        doit = True
            elif tdiff <= TIMING.stage_3_lim:
                 if tdiff % TIMING.stage_3_freq == 0:
                    if pyvrepsup.between(tdiff, tdiff, tdiff + TIMING.retrytime):
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
            ret, msg = pyvrepsup.replicate(tdiff, DATA_FNAME, dirname, dec, conf)

            # This is throttling transmission time by 50 msec ... remove if appropriate
            time.sleep(0.05)

            #print("Replicate ret", ret)
            if ret == True or ret == -1:
                # Mark success or permanent failure
                dec["status"] =  "%05d" % (int(dec['status']) + 1)

            dec['message'] = "%32s" % msg
            xarr3 = conf.packer.encode_data("", dec)
            statecore.save_data(rec[0], xarr3, replace=True)

        for bb in remsced:
            if conf.pgdebug > 3:
                print("Removing state for:", bb[1])
            statecore.del_rec(bb[0])

        del statecore

    def depclean(self, dirname):

        ''' Periodically clean the replicator databases for entries
         that are done, entries that do not have any pending action.
         Databases are vacuumed if size  exceed MAX_DBSIZE.

         '''

        if conf.pgdebug > 8:
            print("Dependency cleanup.", dirname)

        rfile = os.path.join(pyservsup.globals.chaindir, dirname, REPLIC_FNAME)
        repcore = twincore.TwinCore(rfile)
        dbsize = repcore.getdbsize()

        stname = os.path.join(pyservsup.globals.chaindir, dirname,  STATE_FNAME)
        statecore = twincore.TwinCore(stname)
        staterec = statecore.getdbsize()
        canclean = []
        for bb in range(dbsize-1, -1, -1):
            try:
                rec = repcore.get_rec(bb)
            except:
                continue
            if not rec:
                continue   # Deleted record
            rarr = conf.packer.decode_data(rec[1])[0]

            found = False
            for cc in range(staterec):
                try:
                    srec = statecore.get_rec(cc)
                except:
                    pass
                if not srec:
                    continue        # Deleted record
                sarr = conf.packer.decode_data(srec[1])[0]
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
            if conf.pgdebug > 2:
                print("vacuuming repl", dbsize)
            if conf.pgdebug > 5:
                ttt = time.time()
            repcore.vacuum()
            if conf.pgdebug > 5:
                print("db vacuum %.3f" % ((time.time() - ttt) * 1000) )

        if staterec > MAX_DBSIZE:
            if conf.pgdebug > 2:
                print("vacuuming state", staterec)
            if conf.pgdebug > 5:
                ttt = time.time()
            statecore.vacuum()
            if conf.pgdebug > 5:
                print("db vacuum %.3f" % ((time.time() - ttt) * 1000) )

        #del repcore
        #del statecore

# ------------------------------------------------------------------------

optarr = []
optarr.append ( ["c",  "client=", "client",  0,
                        None, "Assume client mode with droot='~/pyvclient'"] )
optarr.append ( ["r:",  "dataroot=", "droot",  "pyvserver",
                        None, "Root for server data default='~/pyvserver'"] )
optarr.append ( ["t:",  "timedel=", "timedel",  2,
                        None, "Time between replications default='2s'"] )
optarr.append ( ["l:",  "loglevel=", "loglev",  1,
                        None, "Log level 0=none 1=auth 2=failures default='1'"] )
optarr.append ( ["s",  "ttime", "ttime",  0,
                        None, "Tester timing (vs production)"] )
optarr.append ( ["m:",  "dumpdata=", "kind",  "",
                        None, "Dump replicator data for data 'kind'"] )
optarr.append ( ["M:",  "state=", "skind",  "",
                        None, "Dump replicator state data for data 'kind'"] )
optarr.append ( ["e",  "showdel=", "sdel",  0,
                        None, "Show deleted records on dump"] )
optarr.append ( ["p",  "dumphost", "dhosts",  0,
                        None, "Dump ihost list"] )
optarr.append ( ["a:",  "retrans=", "rkind",  "",
                        None, "Retransmit all data for 'rkind'. Advanced."], )

optarr += comline.optarrlong

# Replace option string on port
for aa in range(len(optarr)):
    if optarr[aa][0] == "p:":
        #optarr[aa] = ["p:", "port=", "port", "6666",
        #None, "Host port to replicate to"]
        del optarr[aa]
        break

#print(optarr)
comline.sethead("Replicate to ihosts directly from pyvserv server / client databases.")
comline.setfoot("Client mode has precedence, overrides dataroot.")
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

    if conf.pgdebug > 9:
        conf.printvars()

    # Carry it aroung in global
    conf.packer = pyvpacker.packbin()

    if conf.client:
        conf.droot = "pyvclient"

    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf
    pyservsup.globals.lockfname += ".replic"

    #print("locking", pyservsup.globals.lockfname)
    support.lock_process(pyservsup.globals.lockfname, "Replicator")

    if conf.pgdebug > 9:
        ddd = dir(pyservsup.globals)
        for aa in ddd:
            if aa[:1] == "_":
                continue
            attr = getattr(pyservsup.globals, aa)
            if type(attr) == type(""):
                print(aa, "=", attr)

    #if conf.verbose:
    #    print("Myhome:", pyservsup.globals.myhome)

    slogfile = os.path.join(pyservsup.globals.myhome, "log", "pyvserver.log")
    rlogfile = os.path.join(pyservsup.globals.myhome, "log", "pyvreplic.log")
    pysyslog.init_loggers(
            ("system", slogfile), ("replic", rlogfile))

    TIMING.retrytime = 6

    # Keep them even numbered
    if conf.ttime:
        tstr = "tester timing"
        TIMING.stage_1_lim = 6
        TIMING.stage_2_lim = 60
        TIMING.stage_3_lim = 120

        TIMING.stage_1_freq = 1
        TIMING.stage_2_freq = 14
        TIMING.stage_3_freq = 28
    else:
        tstr = "production timing"
        TIMING.stage_1_lim = 6
        TIMING.stage_2_lim = 60*60*24
        TIMING.stage_3_lim = 60*60*24*4

        TIMING.stage_1_freq = 1
        TIMING.stage_2_freq = 60*60*4
        TIMING.stage_3_freq = 60*60*8

    if conf.kind or conf.skind:
        if conf.kind:
            pyvrepsup.dumpreplic(conf, REPLIC_FNAME)
        if conf.skind:
            pyvrepsup.dumpstate(conf, STATE_FNAME)

        sys.exit()

    if conf.verbose:
        print("Replicator started with", tstr, "interval:",
                                        conf.timedel, "sec, at:", conf.droot)
    if conf.loglev > 0:
        pysyslog.repliclog("Started with", tstr, "interval:",
                                        conf.timedel, "at:", conf.droot)
    if conf.dhosts:
        if conf.verbose:
            print("Dumping ihosts:")
        hfname = os.path.join(pyservsup.globals.myhome, IHOST_FNAME)
        if conf.pgdebug > 3:
            print("hfname", hfname)

        hostcore = twincore.TwinCore(hfname)
        hostbdsize = hostcore.getdbsize()
        sumh = []
        for bb in range(hostbdsize-1, -1, -1):
            try:
                hrec = hostcore.get_rec(bb)
            except:
                print("exc get host name", sys.exc_info())
                pass
            if not hrec:
                continue        # Deleted record
            #print("hrec", hrec)
            if hrec[0] in sumh:
                continue
            sumh.append(hrec[0])

            harr = conf.packer.decode_data(hrec[1])[0]['PayLoad']
            if conf.verbose:
                print("host entry:", harr)
            else:
                print("host =", "'" + harr['host'] + "'", "header =", harr['header'], )

            host = harr['host']
            # Create state record if none
            comboname = harr['header'] + "_" + host
            if conf.pgdebug > 5:
                print("Entry combo name:", comboname)

        sys.exit()

    if conf.verbose:
        print("Data from:", pyservsup.globals.chaindir)
        print("debug level =", conf.pgdebug)

    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, soft_terminate)
    #signal.signal(signal.SIGKILL, kill_terminate)

    repl = Replicator()
    repl.rep_run()
    print("Exiting")

def terminate(arg1 = 0, arg2 = 0):
    #print("Term")
    support.unlock_process(pyservsup.globals.lockfname)
    sys.exit(2)
    pass

def soft_terminate(arg1 = 0, arg2 = 0):
    print("Ctrl-C")
    terminate()
    pass

def kill_terminate(arg1 = 0, arg2 = 0):
    #print("Kill")
    pass

if __name__ == '__main__':

    #print(dir(signal))
    #pyvrepsup.print_handles()

    mainfunct()

# EOF
