#!/usr/bin/env python

try:
    import pyotp
except:
    pyotp = None

import os, sys, getopt, signal, select, string
import datetime,  time, stat, base64, uuid

from pyvecc.Key import Key

from Crypto import Random
from Crypto.Cipher import AES
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

fields_help =  '''
    stat fields2:
       1.  ST_MODE Inode protection mode.
       2.  ST_INO Inode number.
       3.  ST_DEV Device inode resides on.
       4.  ST_NLINK  Number of links to the inode.
       5.  ST_UID User id of the owner.
       6.  ST_GID Group id of the owner.
       7.  ST_SIZE Size in bytes of a plain file.
       8.  ST_ATIME Time of last access.
       9.  ST_MTIME Time of last modification.
       10. ST_CTIME Time of last metadata change.
    '''
repfname = "replic"

OK = "OK"
ERR = "ERR"

#pgdebug = 0

def _wr(strx):
    ''' Wrap string with single quotes '''
    return "'" + strx + "'"

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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_exit_func()", strx)

    # Clean up logouts
    if self.resp.user:
        pyservsup.SHARED_LOGINS.deldat(self.resp.user)

    if pyservsup.globals.conf.pglog > 0:
        stry = "Quit", _wr(self.resp.user), str(self.resp.client_address)
        pysyslog.syslog(*stry)

    # This instance will go away, but just to make sure
    self.resp.user = ""

    self.resp.datahandler.putencode([OK, "Bye", self.name], self.resp.ekey)

    # Cancel **after** sending bye
    if self.resp.datahandler.tout:
        self.resp.datahandler.tout.cancel()

    return True

# ------------------------------------------------------------------------
# Also stop timeouts

def get_tout_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_tout_func()", strx)

    tout = self.resp.datahandler.timeout
    if len(strx) > 1:
        try:
            tout = int(strx[1])
            self.resp.datahandler.timeout = tout
            resp = [OK, "Timeout set to ", str(tout)],
        except:
            resp = [OK, "Timeout value must be an integer", strx[1]],
    else:
        resp = [OK, "Current timeout", str(self.resp.datahandler.timeout)],

    #if self.resp.datahandler.tout:
    #    self.resp.datahandler.tout.cancel()

    self.resp.datahandler.putencode(resp, self.resp.ekey)

def get_mkdir_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_mkdir_func()", strx)

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
        os.mkdir(dname)
        response = [OK, "Made directory:", strx[1]]
    except:
        response = [ERR, "Cannot make directory.", strx[1]]

    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rmdir_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rmdir_func()", strx)

    if len(strx) == 1:
        response = [ERR, "Must specify directory name.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    dname = contain_path(self, strx[1])

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    #print("remove dir", dname)

    if not os.path.isdir(dname):
        response = [ERR, "Directory does not exist.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    try:
        os.rmdir(dname)
        response = [OK, "Deleted directory:", strx[1]]
    except:
        response = [ERR, "Cannot delete directory.", str(sys.exc_info()[1]), strx[1]]

    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_throt_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_throt_func()", strx)

    if len(strx) < 2:
        if pyservsup.gl_throttle.getflag():
            boolstr = "ON"
        else:
            boolstr = "OFF"
        rrr = [OK, "Throttle is", boolstr]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    ret = pyservsup.gl_passwd.perms(self.resp.user)
    if not int(ret[2]) & pyservsup.PERM_ADMIN:
        rrr = [ERR, "Only admin can control throttle"]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    boolx = pyservsup.str2bool(strx[1], True)
    #print("boolx:", boolx, strx[1], hex(id(strx[1])))
    if  boolx:
        boolstr = "ON"
        pyservsup.gl_throttle.setflag(True)
    else:
        boolstr = "OFF"
        pyservsup.gl_throttle.setflag(False)

    rrr = [OK, "Throttle turned %s" %  boolstr]
    self.resp.datahandler.putencode(rrr, self.resp.ekey)

def get_buff_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_buff_func()", strx)

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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_lsd_func()", strx)

    sss = ""
    dname2 = self.resp.cwd + os.sep + self.resp.dir + os.sep
    dname2 = support.dirclean(dname2)

    if pyservsup.globals.conf.pgdebug > 3:
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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_ls_func()", strx)

    dname = ""; sss = ""
    if len(strx) < 2:
        strx.append(".")
    try:
        dname = support.unescape(strx[1]);
    except:
        pass

    dname2 = self.resp.cwd + os.sep + self.resp.dir + os.sep + dname
    #print("dname2", dname2)

    dname2 = support.dirclean(dname2)
    #print("dname2c", dname2)

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
        # Perhaps the user meant the file:
        if os.path.isfile(dname2):
            response = [OK, strx[1], strx[0]]
        else:
            support.put_exception("ls ")
            response = [ERR, "No such directory.", strx[1]]

    #print("response", response)
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_fget_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print("get_fget_func()", strx)

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

    #if pyservsup.globals.conf.pglog > 1:
    #    stry = "Server sent file: '" + dname + "' " + str(flen) + " bytes",
    #    pysyslog.syslog(stry)

    response = [OK, "Server sent file", strx[1]]
    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_fput_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_fput_func()", strx)

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
    response = [OK, "Server received file.", strx[1]]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_pwd_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_pwd_func()", strx)

    dname2 = self.resp.dir
    dname2 = support.dirclean(dname2)
    if dname2 == "": dname2 = os.sep
    response = [OK,  dname2]
    self.resp.datahandler.putencode(response, self.resp.ekey)

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

    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)

    errx = False; cnt = -1; arrx = []
    sss = core.getdbsize()
    if  strx[2] == "sum":
        for aa in range(sss-1, -1, -1):
            ppp = core.checkdata(aa)
            if not ppp:
                arrx.append(aa)
    elif strx[2] == "link":
        for aa in range(sss-1, -1, -1):
            ppp2 = core.linkintegrity(aa)
            if not ppp2:
                arrx.append(aa)
    else:
        response = [ERR, "One of 'link' or 'sum' is required.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(arrx):
        response = [ERR,  arrx, len(arrx), "errors", strx[2], sss, "total"]
    else:
        response = [OK,  "No errors.", strx[2], sss, "total"]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_rtest_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rtest_func()", strx[:4])

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify link or sum", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 4:
        response = [ERR, "Must specify record id or ids", strx[0]]
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

    if  strx[2] == "sum":
        funcx = core.checkdata
    elif strx[2] == "link":
        funcx = core.linkintegrity
    else:
        response = [ERR, "One of 'link' or 'sum' is required.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    errx = False; cnt = -1; arrx = []
    sss = len(strx[3:])
    for aa in strx[3:]:
        #print("test:", aa)
        try:
            ddd = core.get_payoffs_bykey(aa)
        except:
            pass
        if len(ddd) == 0:
            response = [ERR, "Data not found.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        if self.pgdebug > 4:
            try:
                rec = core.get_rec(ddd[0])
                print("rec:", rec)
            except:
                print("exc: get_header", sys.exc_info())
                raise
        ppp = funcx(ddd[0])
        if not ppp:
            arrx.append(aa)

    if len(arrx):
        response = [ERR,  arrx, len(arrx), "errors", strx[2]]
    else:
        response = [OK,  "No errors.", strx[2], sss, "records checked."]
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
    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
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

    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
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

    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
    #print("db op2 %.3f" % ((time.time() - ttt) * 1000) )
    datax = []
    dbsize = core.getdbsize()
    for aa in strx[2:]:
        aa = int(aa)
        #convert to offsets
        if aa < 0:
            aa = dbsize + aa
        #print("aa", aa)
        if not core.checkdata(aa):
            data = [ERR, "Invalid Record, bad checksum.", aa]
            self.resp.datahandler.putencode(data, self.resp.ekey)
            return

        if not core.linkintegrity(aa):
            data = [ERR, "Invalid Record, link damaged.", aa]
            self.resp.datahandler.putencode(data, self.resp.ekey)
            return
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

    core = twinchain.TwinChain(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)
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
            print("getting UUID", sys.exc_info())
            #response = [ERR, "Header must be a real UUID.", strx[2],]
            #self.resp.datahandler.putencode(response, self.resp.ekey)
            #return
            continue

        data = []; ddd = []
        try:
            ddd = core.get_payoffs_bykey(aa)
            if pyservsup.globals.conf.pgdebug > 2:
                    print("ddd", ddd)
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
            self.resp.datahandler.putencode(data, self.resp.ekey)
            return

        if not core.linkintegrity(ddd[0]):
            data = [ERR, "Invalid Record, link damaged.", aa]
            self.resp.datahandler.putencode(data, self.resp.ekey)
            return

        try:
            data = core.get_rec(ddd[0])
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
    retoffs = savecore.get_payoffs_bykey(strx[2]['header'])
    #print("db get offs  %.3f" % ((time.time() - ttt) * 1000) )
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

    # if it is not replicated already, add replicate request
    if not strx[2]["Replicated"]:
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
                _wr(self.resp.user), str(self.resp.client_address)
        pysyslog.syslog(*stry)


def get_ihost_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_ihost_func()", strx)

    if len(strx) < 2:
        response = [ERR, "Must specify operation (add / remove).", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    ret = pyservsup.gl_passwd.perms(self.resp.user)
    if not int(ret[2]) & pyservsup.PERM_ADMIN:
        rrr = [ERR, "Only admin can control / view ihosts"]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    if strx[1] != 'list':
        if len(strx) < 3:
            response = [ERR, "Must specify host:port.", strx[0]]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        if strx[2].find(":") < 0:
            response = [ERR, "Entry must be in host:port format.", strx[2]]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

    ihname = os.path.realpath("ihosts.pydb")
    if self.pgdebug > 2:
        print("ihost:", ihname)
    repcore = twincore.TwinCore(ihname)
    #repcore.pgdebug = 10

    if strx[1] == 'add':
        ddd = self.pb.encode_data("", strx[2])
        rec = repcore.retrieve(strx[2])
        if self.pgdebug > 9:
            print("rec:", rec)
        if rec:
            if rec[0][0].decode() == strx[2]:
                #print("Identical", rec[0][0])
                response = [ERR, "Duplicate entry.", strx[2]]
                self.resp.datahandler.putencode(response, self.resp.ekey)
                return
        ret = repcore.save_data(strx[2], ddd)
        if self.pgdebug > 8:
            print("repcore save:", ret, ddd)
        response = [OK, "Added replication host:port.", strx[2]]
        self.resp.datahandler.putencode(response, self.resp.ekey)

    elif strx[1] == 'del':
        rec = repcore.retrieve(strx[2])
        if not rec:
            response = [ERR, "This entry is not in the list.", strx[2]]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        if self.pgdebug > 4:
            print("delete ihost rec:", strx[2])
        ret = repcore.del_rec_bykey(strx[2])
        response = [OK, "Deleted replication host:port.", strx[2]]
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

def get_cd_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_cd_func()", strx)

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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_del_func()", strx)

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
                        "%s" % pyservsup.globals.siteid, self.name]

    if pyservsup.globals.conf.pgdebug > 4:
        print( "get_ver_func->output", res)

    self.resp.datahandler.putencode(res, self.resp.ekey)

def get_id_func(self, strx):
    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_id_func()", strx)

    res = [OK, str(pyservsup.globals.siteid), str(self.name)]
    self.resp.datahandler.putencode(res, self.resp.ekey)

#@support.timeit
def get_hello_func(self, strx):
    if pyservsup.globals.conf.pgdebug > 3:
        print( "get_hello_func()", strx)
    strres = [OK, "Hello", str(pyservsup.globals.siteid), self.name]
    self.resp.datahandler.putencode(strres, self.resp.ekey)

def get_stat_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_stat_func()", strx)

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

def get_lout_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_lout_func()", strx)

    if not self.resp.user:
        response = [ERR, "Not logged in.", strx[0], ]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if pyservsup.globals.conf.pglog > 0:
        stry = "Logout", _wr(resp.user), \
                str(self.resp.client_address)
        pysyslog.syslog(*stry)

    if self.pgdebug > 3:
        print("logout", self.resp.user)

    if resp.user:
        pyservsup.SHARED_LOGINS.deldat(resp.user)

    self.resp.user = ""

    response = [OK, "Logged out.", olduser, ]
    self.resp.datahandler.putencode(response, self.resp.ekey)

#@support.timeit
def get_user_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_user_func()", strx)

    if len(strx) < 2:
        resp = [ERR, "Must specify user name.", strx[0]]
        self.resp.datahandler.putencode(resp, self.resp.ekey)
        return

    if self.resp.user:
        self.resp.datahandler.putencode([ERR, "Already logged in"], self.resp.ekey)
        return

    self.resp.preuser = strx[1]
    self.resp.datahandler.putencode([OK, "Send pass for", strx[1]], self.resp.ekey)

# ------------------------------------------------------------------------

def get_sess_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_sess_func()")

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

    if pyservsup.globals.conf.pgdebug > 6:
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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_akey_func()", strx)

    ttt = time.time()

    if pyservsup.globals.conf.pgdebug > 4:
        print("get_akey_func() called")

    ddd = os.path.abspath("keys")
    ppp = os.path.abspath("private")

    try:
        self.keyfroot = pyservsup.pickkey(ddd)
    except:
        if self.verbose:
            print("No keys generated yet.", sys.exc_info()[1])

        if self.pgdebug > 2:
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

        if pyservsup.globals.conf.pgdebug > 7:
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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_pass_func()")

    ret = "";  retval = True

    #ttt = time.time()

    if len(strx) < 2:
        self.resp.datahandler.putencode(
                [ERR, "Must specify pass.", strx[0]], self.resp.ekey)
        return retval

    # Make sure there is a trace of the attempt
    if pyservsup.globals.conf.pglog > 0:
        stry = "Attempted login", _wr(self.resp.preuser), \
                str(self.resp.client_address)
        pysyslog.syslog(*stry)

    #print("pass 1 %.3f" % ((time.time() - ttt) * 1000) )

    ret = pyservsup.gl_passwd.perms(self.resp.preuser)
    #print("pass 2 %.3f" % ((time.time() - ttt) * 1000) )

    if int(ret[2]) & pyservsup.PERM_DIS:
        rrr = [ERR, "this user is temporarily disabled", strx[1]]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return retval

    xret = pyservsup.gl_passwd.auth(self.resp.preuser, strx[1], 0, pyservsup.USER_AUTH)
    #print("pass 3 %.3f" % ((time.time() - ttt) * 1000) )

    rrr = []
    if xret[0] == 3:
        if pyservsup.globals.conf.pglog > 0:
            stry = "No such user", _wr(self.resp.preuser), \
                str(self.resp.client_address)
            pysyslog.syslog(*stry)
        rrr = [ERR, "No such user.", self.resp.preuser]
    elif xret[0] == 1:

        if self.pgdebug > 3:
            print("Authenticated", self.resp.preuser)

        userdir2 = pyservsup.globals.paydir + os.sep + self.resp.preuser
        self.userdir = check_payload_path(self, userdir2)
        #print("Contained",  self.userdir)
        if not self.userdir:
            rrr = [ERR, "No access to this path", userdir2]
            self.resp.datahandler.putencode(rrr, self.resp.ekey)
            return

        if not os.path.isdir(self.userdir):
            os.mkdir(self.userdir)
        self.resp.cwd = self.userdir

        if pyservsup.globals.conf.pglog > 0:
            stry = "Successful login", _wr(self.resp.preuser),  \
                            str(self.resp.client_address)
            pysyslog.syslog(*stry)

        # Commit  user
        self.resp.user = self.resp.preuser
        self.resp.preuser = ""

        # Anounce it to global stats
        if self.resp.user:
            logttt = time.time()
            pyservsup.SHARED_LOGINS.setdat(self.resp.user, logttt)

        rrr = [OK,  "Authenticated.", self.resp.user]
        retval = False
    else:
        if pyservsup.globals.conf.pglog > 0:
            stry = "Error on login", _wr(self.resp.preuser), \
                str(self.resp.client_address)
            pysyslog.syslog(*stry)
        rrr = [ERR,  xret[1], strx[0]]

    self.resp.datahandler.putencode(rrr, self.resp.ekey)
    return retval

def get_chpass_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_chpass_func()")

    if len(strx) < 2:
        response = [ERR, "Must specify user to change.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify old_pass.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 4:
        response = [ERR, "Must specify new_pass.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    #print("chpass", strx)
    # Make sure there is a trace of the attempt
    if pyservsup.globals.conf.pglog > 1:
        stry = "chpass", _wr(self.resp.user), \
                 str(self.resp.client_address)
        pysyslog.syslog(*stry)

    # Are we allowed to change pass?
    ret = pyservsup.gl_passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        # Authenticate
        if strx[1] !=  self.resp.user:
            response = [ERR, "Non admins can only change their own password.", strx[0]]
            self.resp.datahandler.putencode(response, self.resp.ekey )
            return

        xret = pyservsup.gl_passwd.auth(strx[1], strx[2], 0, pyservsup.USER_AUTH)
        if xret[0] != 1:
            response = [ERR, "Old pass must match", strx[0]]
            self.resp.datahandler.putencode(response, self.resp.ekey )
            return
    # Change
    xret = pyservsup.gl_passwd.auth(strx[1], strx[3], 0, pyservsup.USER_CHPASS)

    ret = ""
    if xret[0] == 5:
        if pyservsup.globals.conf.pglog > 1:
            stry = "Pass changed", _wr(resp.user), \
                str(self.resp.client_address)
            pysyslog.syslog(*stry)
        ret = [OK, "Pass changed", strx[1]]
    elif xret[0] == 3:
        if pyservsup.globals.conf.pglog > 1:
            stry = "No such user", _wr(strx[1]),  \
                str(self.resp.client_address)
            pysyslog.syslog(*stry)
        ret = [ERR, "No such user.", strx[1]]
    elif xret[0] == 1:
        if pyservsup.globals.conf.pglog > 1:
            stry = "Successful login", strx[1], \
                           str(self.resp.client_address)
            pysyslog.syslog(*stry)
        ret = ["OK ", self.resp.user, " Authenticated."]
        retval = False
    else:
        if pyservsup.globals.conf.pglog > 1:
            stry = "Error on login", _wr(strx[1]), \
                    str(self.resp.client_address)
            pysyslog.syslog(*stry)
        ret = [ERR, xret[1], strx[0]]

    self.resp.datahandler.putencode(ret, self.resp.ekey)
    return

def get_uadd_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_uadd_func()", strx)

    if len(strx) < 3:
        response = ERR, "Must specify user name and pass.", strx[0]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    #print("uadd", strx)

    # Are we allowed to add users?
    ret = pyservsup.gl_passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = [ERR, "Only admin can add/delete users", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    # Add this user if not exist
    ret = pyservsup.gl_passwd.auth(strx[1], strx[2], 0, pyservsup.USER_ADD)
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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_aadd_func()", strx)

    # Are we allowed to add users?
    ret = pyservsup.gl_passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = [ERR, "only admin can add/delete users.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if len(strx) < 3:
        response = [ERR, "must specify user name and pass.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    # Add this admin in not exist
    ret = pyservsup.gl_passwd.auth(strx[1], strx[2], pyservsup.PERM_ADMIN, pyservsup.USER_ADD)
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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_uena_func()", strx)

    retval = 0

    # Are we allowed to add users?
    ret = pyservsup.gl_passwd.perms(self.resp.user)
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
        response = [ERR, "Must specify 'enable' or 'disable'", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    # Add this user in not exist
    ret = pyservsup.gl_passwd.auth(strx[1], strx[2], mode, pyservsup.USER_CHMOD)

    if ret[0] == 0:
        response = ERR, ret[1], strx[1]
    elif ret[0] == 8:
        response = OK,  strx[1], strx[2] + "d"
    else:
        response = ERR, ret[1], strx[1]

    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_ulist_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_ulist_func()", strx)

    retval = 0

    # Are we allowed to add users?
    ret = pyservsup.gl_passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = ERR, "only admin can view users.", strx[0]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if len(strx) < 2:
        response = ERR, "Must specify user / admin flag", strx[0]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if strx[1] == "user":
        mode = pyservsup.PERM_NONE
    elif strx[1] == "admin":
        mode = pyservsup.PERM_ADMIN
    elif strx[1] == "initial":
        mode = pyservsup.PERM_INI
    elif strx[1] == "disabled":
        mode = pyservsup.PERM_DIS
    else:
        response = [ERR, "Must specify 'user' or 'admin' or 'disabled' or 'initial'", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    response = pyservsup.gl_passwd.listusers(mode)

    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_uini_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_uini_func()")

    # Test for local client
    if str(self.resp.client_address[0]) != "127.0.0.1":
        response = [ERR,  "Must connect from loopback interface.", strx[0]]

    elif  pyservsup.gl_passwd.count() != 0:
        response = [ERR, "Already has initial user", strx[0]]

    elif len(strx) < 3:
        response = [ERR, "Must specify user name and pass.", strx[0]]
    else:
        ret = pyservsup.gl_passwd.auth(strx[1], strx[2],
                    pyservsup.PERM_INI | pyservsup.PERM_ADMIN,
                        pyservsup.USER_ADD)
        if ret[0] == 0:
            response = [ERR, ret[1], strx[0]]
        elif ret[0] == 1:
            response = [ERR,
            "User already exists, no change. Use pass function.", strx[0]];
        elif ret[0] == 2:

            if pyservsup.globals.conf.pglog > 1:
                stry = "Added initial user",  strx[1], \
                        str(self.resp.client_address)
                pysyslog.syslog(*stry)
            response = [OK, "Added initial user", strx[1]]
        else:
            response = [ERR, ret[1], strx[0]]

    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_udel_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_udel_func()", strx)

    retval = 0
     # Are we allowed to add users?
    ret = pyservsup.gl_passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = ERR, "Only admin can add/delete users", strx[0]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval
    if len(strx) < 2:
        response = [ERR, "Must specify user name to delete", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval
    # Delete user
    ret = pyservsup.gl_passwd.auth(strx[1], "",
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

    if pyservsup.globals.conf.pgdebug > 1:
        print( "put_file_func()", strx)

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

    self.resp.datahandler.putencode(response, self.resp.ekey)

def put_data_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "put_data_func()", strx)

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

    #xstr = "Received chunk: '" + self.resp.fname + \
    #            "'" + str(dlen) + " bytes"
    #print( xstr)

    self.resp.datahandler.putencode([OK,  "Got data"], self.resp.ekey)

def get_qr_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print("get_qr_func()", len(strx))

    #print("cwd:", self.resp.cwd)
    if len(strx) == 1:
        try:
            fp = open('qr.png', 'rb')
            buff = fp.read()
            fp.close()
            self.resp.datahandler.putencode([OK, buff], self.resp.ekey)
        except:
            self.resp.datahandler.putencode([ERR, "No QR image on server"], self.resp.ekey)
    else:
        ret = pyservsup.gl_passwd.perms(self.resp.user)
        if not int(ret[2]) & pyservsup.PERM_ADMIN:
            rrr = [ERR, "Only admin can upload QR image", self.name]
            self.resp.datahandler.putencode(rrr, self.resp.ekey)

        if type(strx[1]) != type(b""):
            strx[1] = strx[1].encode()
        try:
            fp = open('qr.png', 'wb')
            fp.write(strx[1])
            fp.close()
            self.resp.datahandler.putencode([OK, "Written new QR image", len(strx[1])], self.resp.ekey)
        except:
            self.resp.datahandler.putencode([ERR, "Cannot save QR image"], self.resp.ekey)

def get_twofa_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print("get_twofa_func called")

    retval = True
    if len(strx) < 2:
        response = [ERR, "Must pass 2fa code.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    key = "pyvserverkey"

    if not pyotp:
        self.resp.datahandler.putencode(["ERR", "2FA lib not installed"],  self.resp.ekey)
        return

    totp = pyotp.TOTP(key)
    res = totp.verify(strx[1])

    if not res:
        self.resp.datahandler.putencode(["ERR", "Invalid 2FA code"],  self.resp.ekey)
    else:
        self.resp.datahandler.putencode(["OK", "Code Auth OK",],  self.resp.ekey)
        retval = False

    return retval

def get_dmode_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "getdmode_func()", strx)

    flag = not pyservsup.globals.conf.pmode
    self.resp.datahandler.putencode(["OK", "%d" % flag],  self.resp.ekey)

def get_help_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_help_func()", strx)

    harr = []
    if len(strx) == 1:
        harr.append(OK)
        for aa in pyvstate.state_table:
            harr.append(aa[0])
        harr.append("fields")
    else:
        ff = False
        for aa in pyvstate.state_table:
            if strx[1] == aa[0]:
                harr = [OK, aa[5], ]
                ff = True
                break
        if not ff:
            if strx[1] == "fields":
                harr = [OK, fields_help, ]
            else:
                harr = [ERR, "No such command", strx[1], ]

    if pyservsup.globals.conf.pgdebug > 2:
        print( "get_help_func->output", harr)

    self.resp.datahandler.putencode(harr, self.resp.ekey)

if __name__ == '__main__':
    print("This module was not meant to use as main")
    pass

# EOF
