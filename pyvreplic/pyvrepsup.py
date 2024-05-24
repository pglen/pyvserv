#!/usr/bin/env python3

import sys
import os
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

from pydbase import twincore

class BlankClass():
    ''' Empty class for config data '''
    pass

def replicate(tdiff, dfname, dirname, dec, conf):

    ''' Replicate this one entry in the state record.
        Return tuple of error code and message.

        Error codes:
            True    -- Success
            False   -- Fail             message has reason hint
            -1      -- Permanent failure
    '''

    if conf.pgdebug > 2:
        print("replicate:", dec['host'], dec['header'])

    ret = 0; rec = []
    fname = os.path.join(pyservsup.globals.chaindir, dirname, dfname)
    #print("try data", fname)
    datacore = twincore.TwinCore(fname)
    #print("dbsize", datacore.getdbsize())
    try:
        rec = datacore.retrieve(dec['header'])
        #print("Got rec", rec)
    except:
        print("Replicate: cannot get record", sys.exc_info())

    if not rec:
        print("Empty record on replicate:", dec['header'])

        ret = -1        # Indicate permanent failure
        return ret, "Empty record"

    #print("vote:", rec)
    #del datacore

    #if conf.pgdebug > 8:
    #    print("rec", rec)

    try:
        arr = conf.packer.decode_data(rec[0][1])[0]
        #print("vote:", arr)

        # Decorate 'replicated' variable
        if arr['Replicated'] > 2:
            print("This entry is replicated already (%d)" % arr['Replicated'],
                                            dec['header'], )
            return True, "OK"

        arr['Replicated'] = arr.get("Replicated") + 1
        if conf.pgdebug > 9:
            print("payload arr", arr)
        pvh = pyvhash.BcData(arr)
        #if conf.pgdebug > 7:
        #    print("Checks:", pvh.checkhash(), pvh.checkpow())
        #if conf.pgdebug > 5:
        #    print("pyvhash", pvh.datax, pvh.checkhash(), pvh.checkpow())
    except:
        print("err on decoding", sys.exc_info())

    ret, msg = transmit(tdiff, dirname, dec, pvh.datax, conf)
    return ret, msg

def transmit(tdiff, dirname, dec, data, conf):

    ''' Transmit one particular entry to one particular host.
        Return True for successful transfer, -1 for duplicate (permanent fail)
        Logs (if enabled) will contain success / falure report
        and the failure reason string.
    '''

    kind = os.path.basename(dirname)

    #print("transmit()", data)

    if conf.loglev > 1:
        pysyslog.repliclog("Try at:", tdiff, kind, data['header'], dec['host'])

    if not conf.quiet:
        print("Attempt at:", tdiff, kind, data['header'], dec['host'], )

    hostx, portx = dec['host'].split(":")

    #if conf.pgdebug > 2:
    #    print("Transmitting:", hostx, portx, dirname, data['header'])

    ret = False
    hand = pyclisup.CliSup()
    try:
        respc = hand.connect(hostx, int(portx))
    except:
        errx = str(sys.exc_info()[1]).split(']')[1]

        if conf.pgdebug > 1:
            print( "Cannot connect to:", dec['host'], errx)

        # Failure, log it
        if conf.loglev > 1:
            pysyslog.repliclog("Cannot Connect:", dec['host'], errx)

        if not conf.quiet:
            print("Cannot Connect.")
        return ret, "Cannot Connect"

    # Assume success, mark record
    ret = True; msg = "OK"

    confx = BlankClass()
    hand.start_session(confx)
    #print(confx.sess_key[:24])
    cresp = hand.login("admin", "1234", confx)
    if conf.pgdebug > 5:
        print ("Server logon resp:", cresp)
    if cresp[0]  != "OK":
        if not conf.quiet:
            print("Error creating session", cresp)
        if conf.loglev > 1:
            pysyslog.repliclog("Fail:", dec['host'], "Error creating session")
        cresp = hand.client(["quit"], confx.sess_key)
        hand.close()
        ret = False
        return ret, "Cannot Create Session"

    #print("dirname:", dirname, "kind:", kind)
    cresp = hand.client(["rput", kind, data] , confx.sess_key)
    if cresp[0]  != "OK":
        ret = False
        if not conf.quiet:
            print("rput error resp:", cresp)

        hand.client(["quit"], confx.sess_key)
        hand.close()

        if "Duplicate" in cresp[1]:
            if conf.loglev > 1:
                pysyslog.repliclog("Fail:", dec['host'], "Duplicate record.",)
            #print("Permanent stop")
            ret = -1
            return ret, "Duplicate record"
        else:
            if conf.loglev > 1:
                pysyslog.repliclog("Fail:", dec['host'], cresp[1],)
            return ret, "Error Transmitting"

    hand.client(["quit"], confx.sess_key)
    hand.close()

    if conf.pgdebug > 2:
        print("Success on transmit to:", dec['host'])

    # Success, log it
    if conf.loglev > 0:
        pysyslog.repliclog("OK:", dec['host'], cutid(data['header']))

    if not conf.quiet:
        print("Success.")

    return ret, msg

def dumpreplic(conf, rfname):

    ''' Dump replicator data currently active. Use del flag
        to see recent actions. The recent action visibilty is limited
        to the period of last vacuum operation.
     '''

    #if conf.verbose:
    print("Replic data:")

    rfile = os.path.join(pyservsup.globals.chaindir, conf.kind, rfname)
    if conf.pgdebug > 3:
        print("Replicator file: ", rfile)
    try:
        repcore = twincore.TwinCore(rfile)
        if conf.sdel:
            repcore.showdel = True
    except:
        print("No database here", rfile, sys.exc_info())
        sys.exit()

    #print("Replicator data:")
    dbsize = repcore.getdbsize()
    if conf.pgdebug > 3:
        print("Repl size: ", dbsize, "records")

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
            arr = conf.packer.decode_data(rec[2])[0]
            if conf.verbose:
                print("del arr:", arr)
            else:
                dd = datetime.datetime.strptime(arr['now'], pyvhash.datefmt)
                print(arr['header'], dd, "Processed:", arr['processed'])
        else:
            arr = conf.packer.decode_data(rec[1])[0]
            #print("arr:", arr)

        if conf.verbose:
            print("arr:", arr)
        else:
            dd = datetime.datetime.strptime(arr['now'], pyvhash.datefmt)
            print(arr['header'], dd, "Processed:", arr['processed'])

def dumpstate(conf, sfname):

    ''' Dump replicator state data currently active. Use del flag
        to see recent actions. The recent action visibilty is limited
        to the period of last vacuum operation.
     '''

    #if conf.verbose:
    print("State data:")

    stname = os.path.join(pyservsup.globals.chaindir, conf.skind, sfname)

    statecore = twincore.TwinCore(stname)
    staterec = statecore.getdbsize()

    if conf.sdel:
        statecore.showdel = True

    if conf.pgdebug > 3:
        print("State data file:", stname)

    if conf.pgdebug > 3:
        print("State data:", staterec, "records")

    for cc in range(staterec):
        try:
            srec = statecore.get_rec(cc)
        except:
            pass
        if not srec:
            continue        # Deleted record

        if srec[0] == b"del":
            sarr = conf.packer.decode_data(srec[2])[0]
            if conf.verbose:
                print("del sarr:", sarr)
            else:
                dd = datetime.datetime.strptime(sarr['orgnow'], pyvhash.datefmt)
                #print(pyvrepsup.cutid(sarr['header']), dd, sarr['host'], sarr['count'])
                print("del:", sarr['header'], sarr['host'], sarr['count'])
        else:
            sarr = conf.packer.decode_data(srec[1])[0]

            if conf.verbose:
                print("sarr:", sarr)
            else:
                #dd = datetime.datetime.strptime(sarr['orgnow'], pyvhash.datefmt)
                #print(pyvrepsup.cutid(sarr['header']), dd, sarr['host'], sarr['count'])
                print(srec[0], sarr['header'], sarr['host'], sarr['count'])

def cutid(strx, beg = 13, end = 8):
    ''' Return a shortened string with '...' separator '''
    return strx[:beg] + "..." +strx[-end:]

def padstr(strx):
    return "'" + strx + "'"

def print_handles(strx = ""):

    ''' Debug helper. Only on Linux. '''

    open_file_handles = os.listdir('/proc/self/fd')
    print(strx, 'open file handles: ' + ', '.join(map(str, open_file_handles)))

def between(val, mmm, xxx):

    ''' Return True in number (val) is between mmm and xxx, inclusive.

    '''
    if val >= mmm and val <= xxx:
        return True
    else:
        return False

if __name__ == '__main__':
    print("This module was not meant to be used as main.")

# EOF
