#!/usr/bin/env python

try:
    import pyotp
except:
    pyotp = None

import os, sys, getopt, signal, select, string
import datetime,  time, stat, base64, uuid

import pyvpacker

from pyvcommon import support, pyservsup, pyclisup, pysyslog, pyvhash, pyvindex
from pyvserver import pyvstate

from pydbase import twincore

from pyvfuncsup import  *

__doc__ = ''' Chain record related functions '''

# Globals

def get_rcheck_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rcheck_func()", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify link or sum", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    ret = pyservsup.gl_passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = [ERR, "Only admin can check integrity", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    if not os.path.isdir(dname):
        response = [ERR, "Directory does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    core = twincore.TwinCore(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)

    errx = False; cnt = -1; arrx = []
    sss = core.getdbsize()
    packer = pyvpacker.packbin()

    if  strx[2] == "data":
        for aa in range(sss-1, -1, -1):
            offs = core.idx2offs(aa)
            ppp = core.check_rec(offs, aa)
            if not ppp:
                arrx.append(aa)

    elif strx[2] == "proof":
        for aa in range(sss-1, -1, -1):
            ddd = core.get_rec(aa)
            if not ddd:
                continue # Deleted
            #print("ddd", ddd)
            dec = packer.decode_data(ddd[1])[0]
            pvh = pyvhash.BcData(dec)
            #print("pvh:", pvh.datax)
            if not pvh.checkpow():
                arrx.append(aa)

    elif strx[2] == "hash":
        for aa in range(sss-1, -1, -1):
            ddd = core.get_rec(aa)
            if not ddd:
                continue # Deleted
            dec = packer.decode_data(ddd[1])[0]
            pvh = pyvhash.BcData(dec)
            if not pvh.checkhash():
                arrx.append(aa)
    else:
        response = [ERR, "One of 'proof' or 'hash' or 'data' is required.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(arrx):
        response = [ERR,  arrx, len(arrx), "errors", strx[2], sss, "total"]
    else:
        response = [OK,  "No errors.", strx[2], sss, "total"]
    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_rsize_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rsize_func()", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    if not os.path.isdir(dname):
        response = [ERR, "Directory does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("db op1 %.3f" % ((time.time() - ttt) * 1000) )
    core = twincore.TwinCore(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )

    dbsize = core.getdbsize()

    response = [OK,  dbsize, "records"]
    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_rcount_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rcount_func()", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify starting point.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 4:
        response = [ERR, "Must specify ending point.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if pyservsup.globals.conf.pgdebug > 3:
        print("list: start", strx[2], "end", strx[3])

    if pyservsup.globals.conf.pgdebug > 2:
        print("rlist begin:", datetime.datetime.fromtimestamp(strx[2]),
                            "end:", datetime.datetime.fromtimestamp(strx[3]) )

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    if not os.path.isdir(dname):
        response = [ERR, "Directory does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("db op1 %.3f" % ((time.time() - ttt) * 1000) )
    core = twincore.TwinCore(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )

    arr = []
    rcnt = 0
    dbsize = core.getdbsize()
    for aa in range(dbsize - 1, -1, -1):
        rec = core.get_rec(aa)
        ddd = pyservsup.uuid2timestamp(uuid.UUID(rec[0].decode()))
        #ttt = pyservsup.uuid2date(uuid.UUID(rec))
        #print(ddd, ttt)

        if ddd >= strx[2] and ddd <= strx[3]:
            rcnt += 1

    if self.pgdebug > 2:
        print("rcnt", "total: %d records" % dbsize, "got: %d records" % rcnt)

    response = [OK,  rcnt, "records"]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rlist_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rlisr_func()", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify starting point.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 4:
        response = [ERR, "Must specify ending point.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if pyservsup.globals.conf.pgdebug > 3:
        print("list: start", strx[2], "end", strx[3])

    if pyservsup.globals.conf.pgdebug > 2:
        print("rlist begin:", datetime.datetime.fromtimestamp(strx[2]),
                            "end:", datetime.datetime.fromtimestamp(strx[3]) )

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    if not os.path.isdir(dname):
        response = [ERR, "Directory does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("db op1 %.3f" % ((time.time() - ttt) * 1000) )
    core = twincore.TwinCore(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )

    arr = []
    dbsize = core.getdbsize()
    for aa in range(dbsize-1, -1, -1):
        rec = core.get_rec(aa)
        #print("rlist rec:")
        uuu = rec[0].decode()
        ddd = pyservsup.uuid2timestamp(uuid.UUID(uuu))
        #ttt = pyservsup.uuid2date(uuid.UUID(rec))
        #print(ddd, ttt)

        if ddd > strx[2] and ddd < strx[3]:
            arr.append(uuu)
        if len(arr) > 100:
            break

    #print("rec", "%d records" % dbsize, "got: %d" % len(arr))

    # Prevent overload from
    if len(arr) > 100:
        # Return error and some data
        response = [ERR,  "Too many records, narrow date range.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    response = [OK,  arr]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rhave_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rhave_func()", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify data header.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if pyservsup.globals.conf.pgdebug > 3:
        print("dname", dname)

    if not os.path.isdir(dname):
        response = [ERR, "Blockchain 'kind' directory does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    core = twincore.TwinCore(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )
    ddd = []
    try:
        # use the faster hash based function
        ddd = core.retrieve(strx[2])
    except:
        pass
    if len(ddd) == 0:
        response = [ERR, "Data not found.", strx[2],]
    else:
        response = [OK, "Data found", strx[2],]

    #_print_handles(self)
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rabs_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rabs_func()", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify absolute position.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("dname", dname)
    if not os.path.isdir(dname):
        response = [ERR, "Blockchain 'kind' directory does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if pyservsup.globals.conf.pgdebug > 2:
        print("rabs", strx[1], strx[2])

    core = twincore.TwinCore(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )
    datax = []
    dbsize = core.getdbsize()
    for aa in strx[2:]:
        aa = int(aa)
        #convert to offsets
        if aa < 0:
            aa = dbsize + aa
        #print("aa", aa)
        #if not core.checkdata(aa):
        #    data = [ERR, "Invalid Record, bad checksum.", aa]
        #    self.resp.datahandler.putencode(data, self.resp.ekey)
        #    return
        #
        #if not core.linkintegrity(aa):
        #    data = [ERR, "Invalid Record, link damaged.", aa]
        #    self.resp.datahandler.putencode(data, self.resp.ekey)
        #    return
        try:
            data = core.get_rec(aa)
        except:
            data = ""
            print(str(sys.exc_info()))

        if self.pgdebug > 4:
            print("rec data", data)
        if not data:
            response = [ERR, "Record not found.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        datax.append(data)
        #print("data:", data)

    response = [OK, len(datax), "records", datax]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rget_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rget_func()", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify data header.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("dname", dname)
    if not os.path.isdir(dname):
        response = [ERR, "Blockchain 'kind' directory does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if pyservsup.globals.conf.pgdebug > 2:
        print("rget", strx[1], strx[2])

    core = twincore.TwinCore(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )
    datax = []
    if type(strx[2]) == type(""):
        strx[2] = strx[2].split()

    for aa in strx[2]:
        #print("aa", aa)
        # Validate uuid
        try:
            uuidx = uuid.UUID(aa)
        except:
            #print("exc getting UUID", sys.exc_info())
            response = [ERR, "Header must be a real UUID.", strx[2],]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
            #continue

        data = []; ddd = []
        try:
            ddd = core.findrecpos(aa)
            if pyservsup.globals.conf.pgdebug > 2:
                    print("ddd", ddd)
        except:
            pass
        if len(ddd) == 0:
            response = [ERR, "Data not found.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        try:
            data = core.get_rec(ddd[0])
        except:
            print(sys.exc_info())

        if not data:
            response = [ERR, "Cannot get data.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        if self.pgdebug > 2:
            print("got data", data)

        #if not core.checkdata(ddd[0]):
        #    data = [ERR, "Invalid Record, bad checksum.", aa]
        #    self.resp.datahandler.putencode(data, self.resp.ekey)
        #    return
        #
        #if not core.linkintegrity(ddd[0]):
        #    data = [ERR, "Invalid Record, link damaged.", aa]
        #    self.resp.datahandler.putencode(data, self.resp.ekey)
        #    return
        #
        #try:
        #    data = core.get_rec(ddd[0])
        #except:
        #    data = ""
        #    print(str(sys.exc_info()))

        if self.pgdebug > 4:
            print("rec data", data)
        if not data:
            response = [ERR, "Record not found.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        datax.append(data)

    response = [OK, len(datax), "records", datax,]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rput_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rput_func()")

    if len(strx) < 3:
        response = [ERR, "Must specify blockchain kind and data.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("strx[1]", strx[1])
    #print('curr', self.resp.dir)

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)
    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("dname", dname)
    if not os.path.isdir(dname):
        try:
            os.mkdir(dname)
        except:
            support.put_exception("rput")
            response = [ERR, "Cannot make directory.", strx[0]]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

    #ttt = time.time()
    #print("rput strx[2]", strx[2])
    if pyservsup.globals.conf.pgdebug > 0:
        print("rput", strx[1], strx[2]['header'])
    try:
        uuu = uuid.UUID(strx[2]['header'])
    except:
        response = [ERR, "Header must be a valid UUID, not saved", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    pvh = pyvhash.BcData(strx[2])
    #print("pvh", pvh.datax)
    #print("check", pvh.checkpow(), pvh.datax['_Proof'])

    if not pvh.checkhash():
        response = [ERR, "Error on block hash.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    strength = pvh.getstrength()
    if not pyservsup.globals.conf.test and strength < 4:
        #print("strength:", strength)
        response = [ERR, "Insufficient hash strength (%x)" % strength, strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if not pvh.checkpow():
        response = [ERR, "Error on block PROW.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    cfname = os.path.join(dname, pyservsup.chainfname + ".pydb")
    #print("cfname", cfname)
    savecore = twincore.TwinCore(cfname)
    savecore.hashname  = os.path.splitext(cfname)[0] + ".hash.id"
    savecore.packer = pyvpacker.packbin()
    #print("hashname:", savecore.hashname)

    #dbsize = savecore.getdbsize()
    #print("rput %d current size" % dbsize)

    ttt = time.time()

    # Do we have it already?:
    # Search normally: (250 ms / 13000 records)
    #retoffs = savecore.get_payoffs_bykey(strx[2]['header'])
    # Use index:
    # Find it via index (0.2 ms / 13000 records)
    retoffs = pyvindex.search_index(savecore, savecore.hashname,
                                strx[2]['header'], pyvindex.hash_id)

    #print("index", retoffs)
    #print("db get offs  %.3f ms" % ((time.time() - ttt) * 1000) )
    if retoffs:
        if self.pgdebug > 2:
            print("Duplicate block, retoffs", retoffs[0])
        response = [ERR, "Duplicate block, not saved.", strx[2]['header'], retoffs[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    undec = self.pb.encode_data("", strx[2])

    if  self.pgdebug > 5:
        print("Save_data header:", strx[2]["header"])

    if self.pgdebug > 7:
        print("Save data:", undec)

    # Add index
    def callb(c2, id2):
        #print("callb", c2, id2)
        # Replicate fields from local data
        try:
            pyvindex.append_index(c2, c2.hashname,  pyvindex.hash_id, strx[2]['header'])
        except:
            print("exc save callb hash", sys.exc_info())
    try:
        #savecore.pgdebug = 10
        savecore.postexec = callb
        #ret = savecore.appendwith(strx[2]['header'], undec)
        ret = savecore.save_data(strx[2]['header'], undec)
    except:
        del savecore
        print("exc save_data", sys.exc_info()[1])
        response = [ERR, "Cannot save record.", str(sys.exc_info()[1]) ]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    finally:
        #savecore.postexec = None
        #del savecore
        pass

    # if it is not replicated already, add replicate request
    #if not strx[2]["Replicated"]:

    # Thu 16.May.2024  add replicate request, always
    if True:
        # Prepare data. Do strings so it can be re-written in place
        rrr = {
                # Sun 14.Apr.2024 removed counts, shifted to state data
                #'count1': "00000", 'count2' : "00000", 'count3' : "00000",
                'header' : strx[2]['header'],
                'now' : strx[2]['now'], 'iso' : strx[2]['iso'],
                'stamp' : strx[2]['stamp'],
                "processed" : "00000",
                }

        if self.pgdebug > 3:
            print("replic req", rrr)

        undec2 = self.pb.encode_data("", rrr)
        frname = os.path.join(dname, pyservsup.REPFNAME + ".pydb")
        #print("Saving at", frname)
        repcore = twincore.TwinCore(frname, 0)
        #if self.pgdebug > 5:
        #print("repl save_data", strx[2]["Header"], undec2)
        try:
            ret = repcore.save_data(rrr['header'], undec2)
        except:
            del repcore
            print("exc on save_data", sys.exc_info()[1])
            support.put_exception("save_data")
            # Thu 16.May.2024 ignore replicator error
            #response = [ERR,  "Cannot save replicator.",  str(sys.exc_info()[1]) ]
            #self.resp.datahandler.putencode(response, self.resp.ekey)
            #return

        del repcore
    else:
        if self.pgdebug > 3:
            print("Not replicating", strx[2]['header'])
        pass

        #print("db op3 %.3f" % ((time.time() - ttt) * 1000) )
        #dbsize = repcore.getdbsize()
        #print("replicator %d total records" % dbsize)

    response = [OK,  "Blockchain data added.",  strx[2]['header']]
    self.resp.datahandler.putencode(response, self.resp.ekey)

    #open_file_handles = os.listdir('/proc/self/fd')
    #print('open file handles: ' + ', '.join(map(str, open_file_handles)))

    if pyservsup.globals.conf.pglog > 1:
        stry = "Block Chain Data %s" % strx[2]['header'], \
                wr(self.resp.user), str(self.resp.client_address)
        pysyslog.syslog(*stry)

# EOF
