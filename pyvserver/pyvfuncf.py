#!/usr/bin/env python

try:
    import pyotp
except:
    pyotp = None

import os, sys, getopt, signal, select, string
import datetime,  time, stat, base64, uuid

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

import pyvpacker

from pyvcommon import support, pyservsup, pyclisup, pysyslog, pyvhash, pyvindex
from pyvserver import pyvstate

from pydbase import twincore

from pyvfuncsup import  *

__doc__ = ''' file and data related functions '''


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

# EOF
