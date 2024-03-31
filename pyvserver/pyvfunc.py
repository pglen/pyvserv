#!/usr/bin/env python

#from __future__ import print_function
#from __future__ import absolute_import

import pyotp

import os, sys, getopt, signal, select, string
import datetime,  time, stat, base64, uuid

from pyvecc.Key import Key

#from Crypto.Cipher import PKCS1_v1_5
#from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES
#from Crypto.Hash import SHA
#from Crypto.Hash import SHA512
from Crypto.Hash import SHA256

import pyvpacker

from pyvcommon import support, pyservsup, pyclisup, pysyslog, pyvhash
from pyvserver import pyvstate

from pydbase import twincore, twinchain

__doc__ = \
'''
    Server functions. The pyvstate calls routines from this module. The reason
    this is not made into a class is for speed. (Class was too big, and we are still
    adding functions for new commands.)
    This module executes the functions corresponding to keywords.
    The keyword is embedded into the function name.
'''

#chainfname = "initial"
repfname = "replic"

OK = "OK"
ERR = "ERR"

#pgdebug = 0

def _print_handles(self):
        ''' Debug helper '''
        open_file_handles = os.listdir('/proc/self/fd')
        print('open file handles: ' + ', '.join(map(str, open_file_handles)))

def check_chain_path(self, strp):

    chainp = os.path.normpath(pyservsup.globals.chaindir)
    #print("check:", strp)
    #print("root:", chainp)
    dpath = os.path.normpath(strp)
    #print("dpath", dpath)
    if dpath[:len(chainp)] != chainp:
        dpath = None
    return dpath

def check_payload_path(self, strp):

    paypath = os.path.normpath(pyservsup.globals.paydir)
    #print("check:", strp)
    #print("root:", chainp)
    dpath = os.path.normpath(strp)
    #print("dpath", dpath)
    if dpath[:len(paypath)] != paypath:
        dpath = None
    return dpath

def contain_path(self, strp):

    '''
        Make sure the path is pointing to our universe
    '''
    dname = support.unescape(strp);

    #print("dname", dname)
    #print("self.resp.dir", self.resp.dir)
    #print("self.resp.cwd", self.resp.cwd)

    self.resp.dir = support.dirclean(self.resp.dir)
    self.resp.cwd = support.dirclean(self.resp.cwd)

    # Absolute path?
    if len(strp) > 0 and strp[0] == os.sep:
        dname2 = os.path.join(self.resp.cwd, dname)
    else:
        dname2 = os.path.join(self.resp.cwd, self.resp.dir, dname)

    #print("dname2", dname2)

    dname3 = support.dirclean(dname2)
    #print("dname3", dname3)

    dname4 = os.path.abspath(dname3)

    #print("base dir", self.resp.cwd)
    #print("resp_dir", self.resp.dir)

    #print("dname4", dname4)
    #print("slice", dname4[:len(self.resp.cwd)])

    # Compare roots
    if dname4[:len(self.resp.cwd)] != self.resp.cwd:
        return None

    return dname4

# ------------------------------------------------------------------------
# State transition and action functions

def get_exit_func(self, strx):
    #print( "get_exit_func", strx)
    self.resp.datahandler.putencode([OK, "Bye", self.name], self.resp.ekey)
    #self.resp.datahandler.par.shutdown(socket.SHUT_RDWR)

    # Cancel **after** sending bye
    if self.resp.datahandler.tout:
        self.resp.datahandler.tout.cancel()

    return True

# ------------------------------------------------------------------------
# Also stop timeouts

def get_tout_func(self, strx):

    tout = self.resp.datahandler.timeout
    if len(strx) > 1:
        tout = int(strx[1])
        self.resp.datahandler.timeout = tout
        resp = [OK, "Timeout set to ", str(tout)],
    else:
        resp = [OK, "Current timeout", str(self.resp.datahandler.timeout)],

    #if self.resp.datahandler.tout:
    #    self.resp.datahandler.tout.cancel()

    self.resp.datahandler.putencode(resp, self.resp.ekey)


def get_mkdir_func(self, strx):
    #print("make dir", strx[1])

    if len(strx) == 1:
        response = [ERR, "Must specify directory name.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    dname = contain_path(self, strx[1])

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("make dir", dname)

    if os.path.isdir(dname):
        response = [ERR, "Directory already exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    try:
        response = [OK, "Made directory:", strx[1]]
        os.mkdir(dname)
    except:
        response = [ERR, "Cannot make directory.", strx[1]]

    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_buff_func(self, strx):
    #print("buffer str", strx[1])

    if len(strx) < 2:
        response = [ERR, "Must specify buffer size.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    # Set to an number that most short based (2 bytes) routines can handle
    num = int(strx[1])
    if num <= 0:
        num = 1
    elif num > 0xf000:
        num = 0xf000

    if pyservsup.globals.conf.pgdebug > 2:
        print("buffer set to %d" % num)

    self.buffsize = num
    response = [OK, "Buffer set to:", pyservsup.buffsize]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_lsd_func(self, strx):

    sss = ""
    dname2 = self.resp.cwd + os.sep + self.resp.dir + os.sep
    dname2 = support.dirclean(dname2)

    if pyservsup.globals.conf.pgdebug > 1:
        print("get_lsd_func", dname2)

    response = [ OK, ]

    try:
        ddd = os.listdir(dname2)
        for aa in ddd:
            try:
                aaa = dname2 + os.sep + aa
                if stat.S_ISDIR(os.stat(aaa)[stat.ST_MODE]):
                    # Escape spaces
                    response.append(aa) #support.escape(aa))
            except:
                print( "Cannot stat ", aaa, str(sys.exc_info()[1]) )
    except:
        support.put_exception("lsd")
        response = [ERR, str(sys.exc_info()[1] ), strx[0]]

    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_ls_func(self, strx):

    dname = ""; sss = ""
    if len(strx) < 2:
        strx.append(".")
    try:
        dname = support.unescape(strx[1]);
    except:
        pass
    dname2 = self.resp.cwd + os.sep + self.resp.dir + os.sep + dname
    dname2 = support.dirclean(dname2)

    #print("dname2", dname2)

    response = [OK]
    try:
        ddd = os.listdir(dname2)
        for aa in ddd:
            try:
                aaa = dname2 + os.sep + aa
                if stat.S_ISREG(os.stat(aaa)[stat.ST_MODE]):
                    # Escape spaces
                    response.append(aa) #support.escape(aa))
            except:
                print( "Cannot stat ", aaa, str(sys.exc_info()[1]) )

    except:
        support.put_exception("ls ")
        response = [ERR, "No such directory.", strx[0]]

    #print("response", response)
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_fget_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print("fget strx", strx)

    dname = ""
    if len(strx) == 1:
        response = [ERR, "Must specify file name.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    dname = contain_path(self, strx[1])
    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if not os.path.isfile(dname):
        response = [ERR, "File does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    try:
        flen = os.stat(dname)[stat.ST_SIZE]
    except:
        flen = 0

    response = [OK, str(flen), strx[1]]
    self.resp.datahandler.putencode(response, self.resp.ekey)

    try:
        fh = open(dname, "rb")
    except:
        support.put_exception("fget")
        response = [ERR, "Cannot open file.", dname, strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    cipher = AES.new(self.resp.ekey[:32].encode(), AES.MODE_CTR,
                        use_aesni=True, nonce = self.resp.ekey[-8:].encode() )
    prog = 0

    # Loop, break when file end or transmission error
    while 1:
        try:
            buff = fh.read(self.buffsize)
            blen = len(buff)
            if pyservsup.globals.conf.pgdebug > 3:
                print("fread", blen, buff[:12])
        except:
            #print("Cannot read local file", sys.exc_info())
            put_exception("Cannot read file")
            break

        buff = cipher.encrypt(buff)
        try:
            if pyservsup.globals.conf.pgdebug > 5:
                print("putraw", len(buff), buff[:12])
            #ret = self.resp.datahandler.putencode([str(blen), buff,],
            #            self.resp.ekey, False)
            #dstr = self.resp.datahandler.wrapx(buf, key)
            ret = self.resp.datahandler.putraw(buff)
        except:
            #print(sys.exc_info())
            suppport.put_exception("fget")
            break;

        #prog += blen
        #if prog >= flen:
        #    break

        if ret == 0:
            break
        if blen == 0:
            break

    response = [OK, "Sent File", strx[1]]
    self.resp.datahandler.putencode(response, self.resp.ekey)

    #ret = self.resp.datahandler.wfile.write(b" ")
    #self.resp.datahandler.wfile.flush()

    # Lof and set state to IDLE
    xstr = "Sent file: '" + dname + \
                "' " + str(flen) + " bytes"

    #print(xstr)
    pysyslog.syslog(xstr)

def get_fput_func(self, strx):
    #print("fput strx", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify file name.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    dname = contain_path(self, strx[1])
    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if os.path.isfile(dname):
        was = False
        for aa in range(3):
            tmpname = "%s_%d" % (dname, aa)
            if not os.path.isfile(tmpname):
                #print("Saving to backup: %s", tmpname)
                was = True
                try:
                    os.rename(dname, tmpname)
                except:
                    print(sys.exc_info())
                break
        if not was:
            # Wrap around
            tmpname = "%s_%d" % (dname, 0)
            #print("Forced back 0", tmpname)
            try:
                os.remove(tmpname)
                os.rename(dname, tmpname)
            except:
                print(sys.exc_info())

        #response = [ERR, "File exists. Please delete first", strx[1]]
        #self.resp.datahandler.putencode(response, self.resp.ekey)
        #return

    response = [OK, "Send file", strx[1]]
    self.resp.datahandler.putencode(response, self.resp.ekey)

    try:
        fh = open(dname, "wb")
    except:
        support.put_exception("fput")
        response = [ERR, "Cannot create file.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    # Loop, break when EOF or transmission error
    while 1:
        data = self.resp.datahandler.handle_one(self.resp)
        #print("data", data)
        if not data:
            break
        dstr = self.wr.unwrap_data(self.resp.ekey, data)
        #print("dstr[1]", dstr[1])
        if not dstr[1]:
            break
        fh.write(dstr[1])

    fh.close()
    response = [OK, "File received.", strx[1]]
    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_ekey_func(self, strx):

    oldkey = self.resp.ekey[:]
    response = ERR ,  "Not implemented."
    self.resp.datahandler.putencode(response, oldkey)
    return

    if len(strx) < 2:
        self.resp.ekey = ""
        response = OK ,  "Key reset (no encryption)"
    else:
        self.resp.ekey = strx[1]
        response = OK ,  "Key Set"

    # Encrypt reply to ekey with old the key
    self.resp.datahandler.putencode(response, oldkey)

def get_xkey_func(self, strx):
    oldkey = self.resp.ekey[:]

    oldkey = self.resp.ekey[:]
    response = ERR ,  "Not implemented."
    self.resp.datahandler.putencode(response, oldkey)
    return

    if len(strx) < 2:
        self.resp.ekey = ""
        response = OK ,  "Key reset (no encryption)"
    else:
        # Lookup if it is a named key:
        retx = pyservsup.kauth(strx[1], "", 0)
        if retx[0] == 1:
            print( "key set", "'" + retx[1] + "'")
            self.resp.ekey = retx[1]
            response = OK,  "Key Set"
        else:
            response = ERR, strx[1], strx[0]

    # Encrypt reply to xkey with old the key
    self.resp.datahandler.putencode(response, oldkey)

def get_pwd_func(self, strx):
    dname2 = self.resp.dir
    dname2 = support.dirclean(dname2)
    if dname2 == "": dname2 = os.sep
    response = [OK,  dname2]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rcheck_func(self, strx):

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify link or sum", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    if not os.path.isdir(dname):
        response = [ERR, "Directory does not exis.t", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)

    errx = False; cnt = -1; arrx = []
    sss = core.getdbsize()
    for aa in range(sss-1, 0, -1):
        if  strx[2] == "sum":
            ppp = core.checkdata(aa)
            if not ppp:
                arrx.append(aa)
        elif strx[2] == "link":
            ppp = core.linkintegrity(aa)
            if not ppp:
                arrx.append(aa)
        else:
            response = [ERR, "One of 'link' or 'sum' is required.", strx[0]]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

    if len(arrx):
        response = [ERR,  arrx, len(arrx), "errors", strx[2]]
    else:
        response = [OK,  "No errors.", strx[2]]
    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_rsize_func(self, strx):

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
    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )

    dbsize = core.getdbsize()

    response = [OK,  dbsize, "records"]
    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_rcount_func(self, strx):

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
    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )

    arr = []
    rcnt = 0
    dbsize = core.getdbsize()
    for aa in range(dbsize - 1, -1, -1):
        rec = core.get_header(aa)
        ddd = pyservsup.uuid2timestamp(uuid.UUID(rec))
        #ttt = pyservsup.uuid2date(uuid.UUID(rec))
        #print(ddd, ttt)

        if ddd > strx[2] and ddd < strx[3]:
            rcnt += 1

    if self.pgdebug > 2:
        print("rcnt", "total: %d records" % dbsize, "got: %d records" % rcnt)

    response = [OK,  rcnt, "records"]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rlist_func(self, strx):

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
    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )

    arr = []
    dbsize = core.getdbsize()
    for aa in range(dbsize-1, -1, -1):
        rec = core.get_header(aa)
        ddd = pyservsup.uuid2timestamp(uuid.UUID(rec))
        #ttt = pyservsup.uuid2date(uuid.UUID(rec))
        #print(ddd, ttt)

        if ddd > strx[2] and ddd < strx[3]:
            arr.append(rec)
        if len(arr) > 100:
            break

    #print("rec", "%d records" % dbsize, "got: %d" % len(arr))

    # Prevent overload from
    if len(arr) > 100:
        response = [ERR,  "Too many records, narrow date range."]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    response = [OK,  arr]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rhave_func(self, strx):

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

    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )
    ddd = []
    try:
        ddd = core.get_payoffs_bykey(strx[2])
    except:
        pass
    if len(ddd) == 0:
        response = [ERR, "Data not found.", strx[2],]
    else:
        response = [OK, "Data found", strx[2],]

    #_print_handles(self)

    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rget_func(self, strx):

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

    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )
    datax = []
    for aa in strx[2]:
        data = []; ddd = []
        try:
            ddd = core.get_payoffs_bykey(aa)
        except:
            pass
        if len(ddd) == 0:
            response = [ERR, "Data not found.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        try:
            rechead = core.get_header(ddd[0])
        except:
            print(sys.exc_info())

        if not rechead:
            response = [ERR, "Cannot get data.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        if self.pgdebug > 2:
            print("got rechead", rechead)

        if not core.checkdata(ddd[0]):
            data = [ERR, "Invalid Record, bad checksum.", aa]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        if not core.linkintegrity(ddd[0]):
            data = [ERR, "Invalid Record, link damaged.", aa]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        else:
            try:
                data = core.get_payload(ddd[0])
            except:
                data = "error on get data.", str(sys.exc_info())
            if self.pgdebug > 4:
                print("rec data", data)
        if not data:
            response = [ERR, "Record not found.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        datax.append(data)

    response = [OK, datax, datax, len(datax), "records"]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rput_func(self, strx):

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

    pvh = pyvhash.BcData(strx[2])
    #print("pvh", pvh.datax)
    if not pvh.checkhash():
        response = [ERR, "Error on block hash.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if not pvh.checkpow():
        response = [ERR, "Error on block POW.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    cfname = os.path.join(dname, pyservsup.chainfname + ".pydb")
    #print("cfname", cfname)
    savecore = twinchain.TwinChain(cfname)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )

    #print("Got:", strx[2])

    # Do we have it already?:
    #ttt = time.time()
    #rethas = savecore.get_data_bykey(strx[2]['header'])
    #print("db get data  %.3f" % ((time.time() - ttt) * 1000) )
    #if rethas:
    #    if self.pgdebug > 1:
    #        print("Duplicate block, rethas", rethas[0][0])
    #    response = [ERR, "Duplicate block, not saved.", strx[0]]
    #    self.resp.datahandler.putencode(response, self.resp.ekey)
    #    return

    #ttt = time.time()
    retoffs = savecore.get_payoffs_bykey(strx[2]['header'])
    #print("db get offs  %.3f" % ((time.time() - ttt) * 1000) )
    if retoffs:
        if self.pgdebug > 2:
            print("Duplicate block, retoffs", retoffs)
        response = [ERR, "Duplicate block, not saved.", strx[2]['header']]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    undec = self.pb.encode_data("", strx[2])

    if  self.pgdebug > 5:
        print("Save_data header:", strx[2]["header"])

    if self.pgdebug > 7:
        print("Save data:", undec)

    try:
        #savecore.pgdebug = 10
        ret = savecore.appendwith(strx[2]['header'], undec)
    except:
        del savecore
        print("exc save_data", sys.exc_info()[1])
        response = [ERR, "Cannot save record.", str(sys.exc_info()[1]) ]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    del savecore

    # if it no replicated, replicate
    if not strx[2]["Replicated"]:
        # Prepare data. Do strings so it can be re-written in place
        rrr = {'count1': "00000", 'count2' : "00000",
                        'count3' : "00000",  'header' : strx[2]['header'],
                            'now' : strx[2]['now'],}
        if self.pgdebug > 2:
            print("replic", rrr)

        undec2 = self.pb.encode_data("", rrr)
        frname = os.path.join(dname, repfname + ".pydb")
        #print("Saving at", frname)
        repcore = twincore.TwinCore(frname, 0)
        #if self.pgdebug > 5:
        #print("repl save_data", strx[2]["Header"], undec2)
        try:
            ret = repcore.save_data(rrr['header'], undec2)
        except:
            del repcore
            print("exc on save_data", sys.exc_info()[1])
            response = [ERR,  "Cannot save replicator.",  str(sys.exc_info()[1]) ]
            support.put_exception("save_data")
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        del repcore
    else:
        if self.pgdebug > 2:
            print("Not replicating", strx[2]['header'])
        pass

        #print("db op3 %.3f" % ((time.time() - ttt) * 1000) )
        #dbsize = repcore.getdbsize()
        #print("replicator %d total records" % dbsize)

    response = [OK,  "Blockchain data added.",  strx[2]['header']]
    self.resp.datahandler.putencode(response, self.resp.ekey)

    #open_file_handles = os.listdir('/proc/self/fd')
    #print('open file handles: ' + ', '.join(map(str, open_file_handles)))

    pysyslog.syslog("BCD %s" % strx[2]['header'])


def get_ihost_func(self, strx):

    if len(strx) < 2:
        response = [ERR, "Must specify operation (add / remove).", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify host/port.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print(strx)
    ihname = "ihosts.pydb"
    repcore = twincore.TwinCore(ihname)

    if strx[1] == 'add':
        ddd = self.pb.encode_data("", strx[2])
        rec = repcore.retrieve(strx[2])
        if rec:
            if rec[0][0].decode() == strx[2]:
                #print("Identical", rec[0][0])
                response = [ERR, "This entry is already in the list.", strx[2]]
                self.resp.datahandler.putencode(response, self.resp.ekey)
                return
        ret = repcore.save_data(strx[2], ddd, True)
        response = [OK, "Added replication host/port.", strx[2]]
        self.resp.datahandler.putencode(response, self.resp.ekey)

    elif strx[1] == 'del':
        rec = repcore.retrieve(strx[2])
        if not rec:
            response = [ERR, "This entry does not exist.", strx[2]]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        ret = repcore.del_rec_bykey(strx[2])
        #print("del ret", ret, strx[2])
        response = [OK, "Deleted replication host/port.", strx[2]]
        self.resp.datahandler.putencode(response, self.resp.ekey)

    elif strx[1] == 'list':
        arr = []
        for aa in range(repcore.getdbsize()-1, -1, -1):
            ddd = repcore.get_rec(aa)
            if ddd:
                arr.append(str(ddd[0]))
        #print("got recs", arr)
        response = [OK,  arr, strx[2]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
    else:
        response = [ERR, "Operation must be 'add' or 'del or list'.", strx[2]]
        self.resp.datahandler.putencode(response, self.resp.ekey)


def get_ihave_func(self, strx):

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify record header.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    uuid = uuid.UUID(strx[2])

    print("ihave", strx[1], strx[2])
    response = [OK,  "Ihave processed", strx[0], ]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_cd_func(self, strx):

    if len(strx) < 2:
        response = [ERR, "Directory name cannot be empty.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    dname = contain_path(self, strx[1])

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("dname", dname)
    try:
        if os.path.isdir(dname):
            self.resp.dir = dname[len(self.resp.cwd):]
            response = [OK, self.resp.dir]
        else:
            # Back out
            #self.resp.dir = org
            response = [ERR, "Directory does not exist", strx[1]]
    except:
        support.put_exception("cd")
        response = [ERR, "Must specify directory name.", strx[0]]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_del_func(self, strx):

    if len(strx) == 1:
        response = [ERR, "Must specify file name to delete.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    try:
        dname = contain_path(self, strx[1])
        if not dname:
            response = [ERR, "No Access to directory.", strx[1]]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        #print("dname", dname)
        if os.path.isfile(dname):
            try:
                os.unlink(dname)
                response = [OK, "File deleted", strx[1], ]
            except:
                response = [ERR, "Could not delete file.", strx[1]]
        else:
            # Say no file
            response = [ERR, "No Such File.", strx[1]]
    except:
        support.put_exception("del")
        response = [ERR, "Must specify file name to delete.", strx[0]]
    self.resp.datahandler.putencode(response, self.resp.ekey)

# ------------------------------------------------------------------------

def get_ver_func(self, strx):
    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_ver_func()", strx)

    res = [OK, "%s" % pyservsup.version,
                        "%s" % pyservsup.globals.siteid]

    if pyservsup.globals.conf.pgdebug > 2:
        print( "get_ver_func->output", res)

    self.resp.datahandler.putencode(res, self.resp.ekey)


def get_id_func(self, strx):
    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_id_func()", strx)
    res = []
    res.append(OK);    res.append("%s" % pyservsup.globals.siteid)
    if pyservsup.globals.conf.pgdebug > 2:
        print( "get_ver_func->output", "'" + res + "'")
    self.resp.datahandler.putencode(res, self.resp.ekey)

#@support.timeit
def get_hello_func(self, strx):
    if pyservsup.globals.conf.pgdebug > 3:
        print( "get_hello_func()", strx)
    strres = [OK, "Hello", str(pyservsup.globals.siteid), self.name]
    if pyservsup.globals.conf.pgdebug > 4:
        print( "get_hello_func->output", "'" + str(strres) + "'")
    self.resp.datahandler.putencode(strres, self.resp.ekey)

def get_stat_func(self, strx):

    if len(strx) < 2:
        response = [ERR, "Must specify file name.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    fname = ""; aaa = " "
    #print("stat_func", strx[1])

    dname = support.unescape(strx[1]);
    #print("stat_func", strx[1], dname)

    dname2 = self.resp.cwd + os.sep + self.resp.dir + os.sep + dname
    dname2 = support.dirclean(dname2)

    response = [OK]
    response.append(strx[1])

    try:
        sss = os.stat(dname2)
        for aa in sss:
            response.append(str(aa))

    except OSError:
        support.put_exception("stat")
        #print( sys.exc_info())
        response = [ERR, str(sys.exc_info()[1]) , strx[0]]
    except:
        response = [ERR, "Must specify file name.", strx[0]]
        #print( sys.exc_info())

    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_logout_func(self, strx):

    if not self.resp.user:
        response = [ERR, "Not logged in.", strx[0], ]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    olduser = self.resp.user
    self.resp.user = ""
    #print("logout", self.resp.user)

    response = [OK, "Logged out.", olduser, ]
    self.resp.datahandler.putencode(response, self.resp.ekey)

#@support.timeit
def get_user_func(self, strx):
    if len(strx) < 2:
        self.resp.datahandler.putencode(
                [ERR, "Must specify user name.", strx[0]], self.resp.ekey)
        return
    self.resp.user = strx[1]
    self.resp.datahandler.putencode([OK, "Send pass ..."], self.resp.ekey)

# ------------------------------------------------------------------------

def get_sess_func(self, strx):

    if len(strx) < 4:
        response = [ERR, "Not enough arguments for session."]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #sss = SHA512.new(); sss.update(bytes(strx[3], "cp437"))
    sss = SHA256.new(); sss.update(strx[3].encode())

    # Arrived safely?
    if strx[2] != sss.hexdigest():
        self.resp.datahandler.putencode([ERR, "session key damaged on transport."], self.resp.ekey)
        return

    # Re init cypher (test)
    #self.privkey = Key.import_priv(self.keyx2)
    #self.priv_cipher = self.privkey

    message2 = self.priv_cipher.decrypt(strx[3])

    #print("sess_key", message2[:24])

    # Decoded OK?
    ttt = SHA256.new(); ttt.update(message2.encode())

    if pyservsup.globals.conf.pgdebug > 4:
        print("Hash1:", strx[1])
        print("Hash2:", ttt.hexdigest())

    if ttt.hexdigest() != strx[1]:
        self.resp.datahandler.putencode(\
            [ERR, "session key damaged on decoding."], self.resp.ekey, strx[0])
        return

    self.resp.datahandler.putencode([OK, "Session estabilished."], self.resp.ekey)
    self.resp.ekey = message2

    if pyservsup.globals.conf.pgdebug > 3:
        support.shortdump("session key:", self.resp.ekey.encode() )

# ------------------------------------------------------------------------

#@support.timeit
def get_akey_func(self, strx):

    ttt = time.time()

    if pyservsup.globals.conf.pgdebug > 4:
        print("get_akey_func() called")

    ddd = os.path.abspath("keys")
    ppp = os.path.abspath("private")

    try:
        self.keyfroot = pyservsup.pickkey(ddd)
    except:
        print("No keys generated yet.", sys.exc_info()[1])
        support.put_exception("no keys yet")
        rrr = [ERR, "No keys yet. Run keygen.", strx[0]]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    if pyservsup.globals.conf.pgdebug > 4:
       print("self.keyfroot", self.keyfroot)

    if pyservsup.globals.conf.pgdebug > 4:
        print("fname", ddd + os.sep + self.keyfroot + ".pub")

    #print("akey 1 %.3f" % ((time.time() - ttt) * 1000) )

    try:
        # Do public import
        fp = open(ddd + os.sep + self.keyfroot + ".pub", "rt")
        self.keyx = fp.read()
        fp.close()

        if pyservsup.globals.conf.pgdebug > 4:
            print("Key read: \n'" + self.keyx + "'\n")
    except:
        print("Cannot read key:", self.keyfroot, sys.exc_info()[1])
        support.put_exception("read key")
        rrr = [ERR, "cannot open keyfile.", strx[0]]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)

    try:
        #self.pubkey = RSA.importKey(self.keyx)
        #self.pubkey = ECC.import_key(self.keyx)
        self.pubkey = Key.import_pub(self.keyx)
        #print("validate", self.pubkey.validate())
        #print("finger", self.pubkey.fingerprint())

    except:
        print("Cannot read key:", self.keyx[:12], sys.exc_info()[1])
        support.put_exception("import  key")
        rrr = [ERR, "Cannot read public key.", strx[0]]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    #print("akey 2 %.3f" % ((time.time() - ttt) * 1000) )

    # Do private import; we are handleing it here, so key signals errors
    fp2 = open(ppp + os.sep + self.keyfroot + ".pem", "rt")
    self.keyx2 = fp2.read()
    fp2.close()

    #print(self.keyx2)

    #print("akey 3 %.3f" % ((time.time() - ttt) * 1000) )

    try:
        #self.privkey = RSA.importKey(self.keyx2)
        #self.privkey = ECC.import_key(self.keyx2)
        self.privkey = Key.import_priv(self.keyx2)
        #print("akey 3.1 %.3f" % ((time.time() - ttt) * 1000) )
        #self.priv_cipher = PKCS1_v1_5.new(self.privkey)
        # Bypass
        self.priv_cipher = self.privkey

    except:
        print("Cannot create private key:", self.keyx2[:12], sys.exc_info()[1])
        support.put_exception("import private key")
        rrr = [ERR, "Cannot create private key.", strx[0]]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    #print("akey 4 %.3f" % ((time.time() - ttt) * 1000) )

    # Clean private key from memory
    hh = SHA256.new(); hh.update(self.keyx.encode())
    if pyservsup.globals.conf.pgdebug > 3:
        print("Key digest: \n'" + hh.hexdigest() + "'\n")

    # Deliver the answer in two parts:
    rrr = [OK, "%s" % hh.hexdigest(), self.keyx]
    self.resp.datahandler.putencode(rrr, self.resp.ekey)

#@support.timeit
def get_pass_func(self, strx):

    ret = "";  retval = True

    #ttt = time.time()

    if len(strx) < 2:
        self.resp.datahandler.putencode(
                [ERR, "Must specify pass.", strx[0]], self.resp.ekey)
        return retval
    # Make sure there is a trace of the attempt
    stry = "Logon  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
    pysyslog.syslog(stry)

    #print("pass 1 %.3f" % ((time.time() - ttt) * 1000) )

    ret = pyservsup.passwd.perms(self.resp.user)
    #print("pass 2 %.3f" % ((time.time() - ttt) * 1000) )

    if int(ret[2]) & pyservsup.PERM_DIS:
        rrr = [ERR, "this user is temporarily disabled", strx[1]]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return retval

    xret = pyservsup.passwd.auth(self.resp.user, strx[1], 0, pyservsup.USER_AUTH)
    #print("pass 3 %.3f" % ((time.time() - ttt) * 1000) )

    rrr = []
    if xret[0] == 3:
        stry = "No such user  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)
        rrr = [ERR, "No such user.", self.resp.user]
    elif xret[0] == 1:
        stry = "Successful logon '" + self.resp.user + "' " + \
                            str(self.resp.client_address)
        pysyslog.syslog(stry)

        if self.pgdebug > 3:
            print("Authenticated", self.resp.user)

        userdir2 = pyservsup.globals.paydir + os.sep + self.resp.user
        self.userdir = check_payload_path(self, userdir2)
        #print("Contained",  self.userdir)
        if not self.userdir:
            rrr = [ERR, "No access to this path", userdir2]
            self.resp.datahandler.putencode(rrr, self.resp.ekey)
            return

        if not os.path.isdir(self.userdir):
            os.mkdir(self.userdir)
        self.resp.cwd = self.userdir
        rrr = [OK,  "Authenticated.", self.resp.user]
        retval = False
    else:
        stry = "Error on logon  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)
        rrr = [ERR,  xret[1], strx[0]]

    self.resp.datahandler.putencode(rrr, self.resp.ekey)
    return retval

def get_chpass_func(self, strx):

    if len(strx) < 1:
        response = [ERR, "Must specify old_pass.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 2:
        response = [ERR, "Must specify new_pass.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("chpass", strx[1], strx[2])

    # Make sure there is a trace of the attempt
    stry = "chpass  '" + self.resp.user + "' " + str(self.resp.client_address)
    pysyslog.syslog(stry)

    # Authenticate
    xret = pyservsup.passwd.auth(self.resp.user, strx[1], 0, pyservsup.USER_AUTH)
    if xret[0] != 1:
        response = [ERR, "Old pass must match", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey )
        return

    # Change
    xret = pyservsup.passwd.auth(self.resp.user, strx[2], 0, pyservsup.USER_CHPASS)

    ret = ""
    if xret[0] == 5:
        stry = "Pass changed '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)
        ret = [OK, "Pass changed", self.resp.user]
    elif xret[0] == 3:
        stry = "No such user  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)
        ret = [ERR, "No such user.", self.resp.user]
    elif xret[0] == 1:
        pysyslog.syslog("Successful logon", self.resp.user,
                                            str(self.resp.client_address))
        ret = ["OK ", self.resp.user, " Authenticated."]
        retval = False
    else:
        stry = "Error on logon  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)
        ret = [ERR, xret[1], strx[0]]

    self.resp.datahandler.putencode(ret, self.resp.ekey)
    return

def get_uadd_func(self, strx):

    if len(strx) < 3:
        response = ERR, "Must specify user name and pass.", strx[0]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    #print("uadd", strx)

    # Are we allowed to add users?
    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = [ERR, "Only admin can add/delete users", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    # Add this user if not exist
    ret = pyservsup.passwd.auth(strx[1], strx[2], 0, pyservsup.USER_ADD)
    if ret[0] <= 0:
        response = [ERR, ret[1], strx[1]]
    elif ret[0] == 1:
        response = [ERR, "User already exists.", strx[1]]
    elif ret[0] == 2:
        response = ["OK", "Added user.", strx[1]]
    else:
        response = [ERR, ret[1], strx[1]]

    self.resp.datahandler.putencode(response, self.resp.ekey)

# Add Admin

def get_aadd_func(self, strx):

    # Are we allowed to add users?
    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = [ERR, "only admin can add/delete users.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if len(strx) < 3:
        response = [ERR, "must specify user name and pass.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    # Add this admin in not exist
    ret = pyservsup.passwd.auth(strx[1], strx[2], pyservsup.PERM_ADMIN, pyservsup.USER_ADD)
    if ret[0] <= 0:
        response = [ERR, ret[1], strx[0]]
    elif ret[0] == 1:
        response = ERR, ["Admin already exists.", strx[1]]
    elif ret[0] == 2:
        response = [OK, "Added admin.", strx[1]]
    else:
        response = [ERR, ret[1], strx[1]]

    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_uena_func(self, strx):

    retval = 0

    # Are we allowed to add users?
    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = ERR, "only admin can modify users.", strx[0]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if len(strx) < 2:
        response = ERR, "Must specify user name and flag.", strx[0]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if strx[2] == "enable":
        mode = pyservsup.PERM_DIS  | pyservsup.RESET_MODE
    elif strx[2] == "disable":
        mode = pyservsup.PERM_DIS
    else:
        response = [ERR, "Must specify 'enable' or 'disable'.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    # Add this user in not exist
    ret = pyservsup.passwd.auth(strx[1], strx[2], mode, pyservsup.USER_CHMOD)

    if ret[0] == 0:
        response = ERR, ret[1], strx[1]
    elif ret[0] == 8:
        response = OK,  strx[1], strx[2] + "d"
    else:
        response = ERR, ret[1], strx[1]

    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_uini_func(self, strx):

    # Test for local client
    if str(self.resp.client_address[0]) != "127.0.0.1":
        response = [ERR,  "Must connect from loopback interface.", strx[0]]

    elif  pyservsup.passwd.count() != 0:
        response = [ERR, "Already has initial user", strx[0]]

    elif len(strx) < 3:
        response = [ERR, "Must specify user name and pass.", strx[0]]
    else:
        ret = pyservsup.passwd.auth(strx[1], strx[2],
                    pyservsup.PERM_INI | pyservsup.PERM_ADMIN,
                        pyservsup.USER_ADD)
        if ret[0] == 0:
            response = [ERR, ret[1], strx[0]]
        elif ret[0] == 1:
            response = [ERR,
            "User already exists, no change. Use pass function.", strx[0]];
        elif ret[0] == 2:
            response = [OK, "Added initial user", strx[1]]
        else:
            response = [ERR, ret[1], strx[0]]

    self.resp.datahandler.putencode(response, self.resp.ekey)

#def get_kini_func(self, strx):
#
#    # Test for local client
#    if str(self.resp.client_address[0]) != "127.0.0.1":
#        response = ERR, "Must connect from loopback.", strx[0]
#    elif len(strx) < 3:
#        response = ERR, "Must specify key_name and key_value.", strx[0]
#    else:
#        # See if there is a key file
#        if os.path.isfile(pyservsup.keyfile):
#            response = ERR, "Initial key already exists", strx[0]
#        else:
#            #tmp2 = bluepy.bluepy.decrypt(self.resp.passwd, "1234")
#            #tmp = bluepy.bluepy.encrypt(strx[2], tmp2)
#            #ret = pyservsup.kauth(strx[1], tmp, 1)
#            ret = pyservsup.kauth(strx[1], strx[2], 1)
#            #bluepy.bluepy.destroy(tmp)
#
#            if ret[0] == 0:
#                response = OK, "Added key",  strx[1]
#            else:
#                response = ERR, ret[1], strx[0]
#    self.resp.datahandler.putencode(response, self.resp.ekey)
#
#def get_kadd_func(self, strx):
#
#    response = ERR, "Not Implemented", strx[0]
#    self.resp.datahandler.putencode(response, self.resp.ekey)
#    return
#
#    if not os.path.isfile(pyservsup.keyfile):
#        response = ERR, "No initial keys yet. Please add some.", strx[0]
#    if len(strx) < 3:
#        response = ERR, "Must specify key_name and key_value.", strx[0]
#    else:
#        # See if there is a key by this name
#        ret = pyservsup.kauth(strx[1], strx[2], 1)
#        if ret[0]  < 0:
#            response = ERR, ret[1], strx[0]
#        elif ret[0] == 2:
#            response = ERR, "Key already exists, no keys are changed ", strx[0]
#        elif ret[0] == 0:
#            response = "OK added key '" + strx[1] + "'"
#        else:
#            response = ERR, "Invalid return code from auth.", strx[0]
#    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_udel_func(self, strx):

    retval = 0
     # Are we allowed to add users?
    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = ERR, "Only admin can add/delete users", strx[0]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval
    if len(strx) < 2:
        response = [ERR, "Must specify user name to delete", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval
    # Delete user
    ret = pyservsup.passwd.auth(strx[1], "",
                    pyservsup.PERM_NONE, pyservsup.USER_DEL)
    #print("udel ret", ret)
    if ret[0] == 0:
        response = [ERR, ret[1], strx[1]]
    elif ret[0] == 4:
        response = [OK, "deleted user", strx[1]]
    else:
        response = [ERR, ret[1], strx[1]]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def put_file_func(self, strx):

    if len(strx) == 1:
        response = [ERR, "Must specify file name.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    # Close possible pending
    if  self.resp.fh:
        self.resp.fh.close()
        self.resp.fh = None

    dname = contain_path(self, strx[1])
    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if os.path.isfile(dname):
        response = [ERR, "File exists. Delete first.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    try:
        try:
            # Create handle
            self.resp.fh = open(dname, "wb")
            self.resp.fname = strx[1]
            response = [OK, "Send file", self.resp.fname]
        except:
            response = [ERR, "Cannot create file", self.resp.fname, strx[0]]
    except:
        response = [ERR,  "Must specify file name", strx[0]]
    #pysyslog.syslog("Opened", xstr[1])
    self.resp.datahandler.putencode(response, self.resp.ekey)

def put_data_func(self, strx):

    #print("fname", self.resp.fname, "data:", strx)

    if self.resp.fname == "":
        response = [ERR, "No filename for data", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    try:
        dlen = len(strx[2])
        if dlen == 0:
            response = [OK, "Empty Data, assuming EOF; Closing file", strx[0]]
            if  self.resp.fh:
                self.resp.fh.close()
                self.resp.fh = None
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
            pass
    except:
        #print("file", sys.exc_info())
        response = [ERR, "Must send some data", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    try:
        self.resp.fh.seek(strx[1], os.SEEK_SET)
        self.resp.fh.write(strx[2])
    except:
        #print(sys.exc_info())
        response = [ERR, "Cannot save data on server", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    xstr = "Received chunk: '" + self.resp.fname + \
                "' " + str(dlen) + " bytes"
    #print( xstr)
    #pysyslog.syslog(xstr)
    #self.resp.datahandler.putencode("OK Got data", self.resp.ekey)
    self.resp.datahandler.putencode([OK,  "Got data"], self.resp.ekey)

def get_qr_func(self, strx):

    #print("QRfunc called")

    fp = open('qr.png', 'rb')
    buff = fp.read()
    fp.close()
    self.resp.datahandler.putencode([OK, buff], self.resp.ekey)

def get_twofa_func(self, strx):

    #print("get_twofa_func called")

    retval = True
    if len(strx) < 2:
        response = [ERR, "Must pass 2fa code.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    key = "pyvserverkey"
    totp = pyotp.TOTP(key)
    res = totp.verify(strx[1])
    if not res:
        self.resp.datahandler.putencode(["ERR", "Invalid 2FA code"],  self.resp.ekey)
    else:
        self.resp.datahandler.putencode(["OK", "Code Auth OK",],  self.resp.ekey)
        retval = False

    return retval

def get_dmode_func(self, strx):

    flag = pyservsup.globals.conf.dmode
    self.resp.datahandler.putencode(["OK", "%d" % flag],  self.resp.ekey)

def get_help_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_help_func()", strx)

    harr = []
    if len(strx) == 1:
        harr.append(OK)
        for aa in pyvstate.state_table:
            harr.append(aa[0])
    else:
        ff = False
        for aa in pyvstate.state_table:
            if strx[1] == aa[0]:
                harr.append(OK)
                harr.append(aa[5])
                ff = True
                break
        if not ff:
                harr.append(ERR)
                harr.append("No such command")
                harr.appnd(strx[0])

    if pyservsup.globals.conf.pgdebug > 2:
        print( "get_help_func->output", harr)

    self.resp.datahandler.putencode(harr, self.resp.ekey)

if __name__ == '__main__':
    pass

# EOF