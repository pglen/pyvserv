#!/usr/bin/env python

from __future__ import print_function

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Hash import SHA512
from Crypto import Random

import os, sys, getopt, signal, select, string, time, stat, base64

sys.path.append('..')
sys.path.append('../bluepy')
import bluepy

sys.path.append('../common')
import support, pyservsup, pyclisup, crysupp, pysyslog, pystate

pgdebug = 0

# ------------------------------------------------------------------------
# State transition and action functions

def get_lsd_func(self, strx):
    dname = ""; sss = ""
    try:
       dname = strx[1];
    except:
       pass
    dname2 = self.resp.cwd + "/" + self.resp.dir + "/" + dname

    dname2 = support.dirclean(dname2)
    try:
        ddd = os.listdir(dname2)
        for aa in ddd:
            if stat.S_ISDIR(os.stat(aa)[stat.ST_MODE]):
                # Escape spaces
                sss += support.escape(aa) + " "
        response = "OK " + sss
    except:
        #support.put_exception("lsd")
        response = "ERR " + str(sys.exc_info()[1] )
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_ls_func(self, strx):

    dname = ""; sss = ""
    if len(strx) < 2:
        strx.append(".")
    try:
        dname = pyservsup.unescape(strx[1]);
    except:
        pass
    dname2 = self.resp.cwd + "/" + self.resp.dir + "/" + dname
    dname2 = support.dirclean(dname2)
    #print("dname2", dname2)

    try:
        ddd = os.listdir(dname2)
        for aa in ddd:
            try:
                aaa = dname2 + "/" + aa
                if not stat.S_ISDIR(os.stat(aaa)[stat.ST_MODE]):
                    # Escape spaces
                    sss += support.escape(aa) + " "
            except:
                print( "Cannot stat ", aaa, str(sys.exc_info()[1]) )

        response = "OK " + sss
    except:
        support.put_exception("ls ")
        response = "ERR No such directory"
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_fget_func(self, strx):
    dname = ""
    if len(strx) == 1:
        response = "ERR Must specify file name"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return
    dname = pyservsup.unescape(strx[1]);
    dname2 = self.resp.cwd + "/" + self.resp.dir + "/" + dname
    dname2 = support.dirclean(dname2)
    flen = 0
    try:
        flen = os.stat(dname2)[stat.ST_SIZE]
        fh = open(dname2)
    except:
        support.put_exception("cd")
        response = "ERR Cannot open file '" + dname + "'"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return
    response = "OK " + str(flen)
    self.resp.datahandler.putdata(response, self.resp.ekey)
    # Loop, break when file end or transmission error
    while 1:
        buff = fh.read(pyservsup.buffsize)
        if len(buff) == 0:
            break
        ret = self.resp.datahandler.putdata(buff, self.resp.ekey, False)
        if ret == 0:
            break
    # Lof and set state to IDLE
    xstr = "Sent file: '" + dname + \
                "' " + str(flen) + " bytes"
    print( xstr)
    pysyslog.syslog(xstr)

def get_ekey_func(self, strx):
    oldkey = self.resp.ekey[:]
    if len(strx) < 2:
        self.resp.ekey = ""
        response = "OK " +  "Key reset (no encryption)"
    else:
        self.resp.ekey = strx[1]
        response = "OK " +  "Key Set"
    # Encrypt reply to ekey with old the key
    self.resp.datahandler.putdata(response, oldkey)

def get_xkey_func(self, strx):
    oldkey = self.resp.ekey[:]
    if len(strx) < 2:
        self.resp.ekey = ""
        response = "OK " +  "Key reset (no encryption)"
    else:
        # Lookup if it is a named key:
        retx = pyservsup.kauth(strx[1], "", 0)
        if retx[0] == 1:
            print( "key set", "'" + retx[1] + "'")
            self.resp.ekey = retx[1]
            response = "OK " +  "Key Set"
        else:
            response = "ERR " + strx[1]
    # Encrypt reply to xkey with old the key
    self.resp.datahandler.putdata(response, oldkey)

def get_pwd_func(self, strx):
    dname2 = self.resp.dir
    dname2 = support.dirclean(dname2)
    if dname2 == "": dname2 = "/"
    response = "OK " +  dname2
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_ver_func(self, strx):
    response = "OK Version %s" % pyservsup.version
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_hello_func(self, strx):
    response = "OK Hello"
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_cd_func(self, strx):
    org = self.resp.dir
    try:
        dname = pyservsup.unescape(strx[1]);
        if dname == "..":
            self.resp.dir = pyservsup.chup(self.resp.dir)
        else:
            self.resp.dir += "/" + dname

        self.resp.dir = support.dirclean(self.resp.dir)
        dname2 = self.resp.cwd + "/" + self.resp.dir
        dname2 = support.dirclean(dname2)
        if os.path.isdir(dname2):
            response = "OK " + self.resp.dir
        else:
            # Back out
            self.resp.dir = org
            response = "ERR Directory does not exist"
    except:
        support.put_exception("cd")
        response = "ERR Must specify directory name"
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_stat_func(self, strx):
    fname = ""; aaa = " "
    try:
        fname = strx[1]; sss = os.stat(strx[1])
        for aa in sss:
            aaa += str(aa) + " "
        response = "OK " + fname + aaa
    except OSError:
        support.put_exception("cd")
        print( sys.exc_info())
        response = "ERR " + str(sys.exc_info()[1] )
    except:
        response = "ERR Must specify file name"
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_user_func(self, strx):
    if len(strx) < 2:
        self.resp.datahandler.putdata("ERR must specify user name", self.resp.ekey)
        return True
    self.resp.user = strx[1]
    #self.resp.datahandler.putdata("OK Enter pass for '" + self.resp.user + "'", self.resp.ekey)
    self.resp.datahandler.putdata("OK send pass ...", self.resp.ekey)

# ------------------------------------------------------------------------

def get_sess_func(self, strx):

    #if pgdebug > 4:
    #    print("get_sess_func() called")

    if pgdebug > 5:
        print("strx", strx)

    if len(strx) < 4:
        self.resp.datahandler.putdata("ERR not enough arguments.", self.resp.ekey)
        return

    if pgdebug > 4:
        print("Got session key command.")

    sss = SHA512.new(); sss.update(strx[3])

    # Arrived safely?
    if strx[2] != sss.hexdigest():
        self.resp.datahandler.putdata("ERR session key damaged on transport.", self.resp.ekey)
        return

    dsize = SHA.digest_size
    sentinel = Random.new().read(dsize)
    message2 = self.priv_cipher.decrypt(strx[3], sentinel)

    # Decoded OK?
    ttt = SHA512.new(); ttt.update(message2)

    if pgdebug > 2:
        print("Hash1:", strx[1])
        print("Hash2:",   ttt.hexdigest())

    if ttt.hexdigest() != strx[1]:
        self.resp.datahandler.putdata("ERR session key damaged on decoding.", self.resp.ekey)
        return

    self.resp.datahandler.putdata("OK Session estabilished.", self.resp.ekey)
    self.resp.ekey = message2
    key =  self.resp.ekey

    if pgdebug > 1:
        support.shortdump("session key:", key)

# ------------------------------------------------------------------------

def get_akey_func(self, strx):

    if pgdebug > 1:
        print("get_akey_func() called")

    ddd = os.path.abspath("keys")

    try:
        self.keyfroot = pyservsup.pickkey(ddd)
    except:
        print("No keys generated yet.", sys.exc_info()[1])
        support.put_exception("no keys  key")
        self.resp.datahandler.putdata("ERR no keys yet. Run keygen", self.resp.ekey)

    if pgdebug > 2:
       print("self.keyfroot", self.keyfroot)

    try:
        # Do public import
        fp = open(ddd + "/" + self.keyfroot + ".pub", "rb")
        self.keyx = fp.read()
        fp.close()

        try:
            self.pubkey = RSA.importKey(self.keyx)
        except:
            print("Cannot create key:", self.keyx[:12], sys.exc_info()[1])
            support.put_exception("import  key")
            self.resp.datahandler.putdata("ERR Cannot create public key", self.resp.ekey)
            return

        if pgdebug > 5:
            print("Key read: \n'" + self.keyx.decode("cp437") + "'\n")

        # Do private import; we are handleing it here, so key signals errors
        fp2 = open(ddd + "/" + self.keyfroot + ".pem", "rb")
        self.keyx2 = fp2.read()
        fp2.close()

        try:
            self.privkey = RSA.importKey(self.keyx2)
            self.priv_cipher = PKCS1_v1_5.new(self.privkey)
        except:
            print("Cannot create private key:", self.keyx2[:12], sys.exc_info()[1])
            support.put_exception("import private key")
            self.resp.datahandler.putdata("ERR Cannot create private key", self.resp.ekey)
            return

        if pgdebug > 5:
            print("Key read: \n'" + self.keyx.decode("cp437") + "'\n")

        hh = SHA512.new(); hh.update(self.keyx)
        if pgdebug > 1:
            print("Key digest: \n'" + hh.hexdigest() + "'\n")

        # Deliver the answer in two parts:
        self.resp.datahandler.putdata("OK Hash: %s " % hh.hexdigest(), self.resp.ekey)
        self.resp.datahandler.putdata(self.keyx, self.resp.ekey)
    except:
        print("Cannot read key:", self.keyfroot, sys.exc_info()[1])
        support.put_exception("read key")
        self.resp.datahandler.putdata("ERR cannot open keyfile.", self.resp.ekey)

def get_pass_func(self, strx):

    ret = "";  retval = True

    # Make sure there is a trace of the attempt
    stry = "Logon  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
    pysyslog.syslog(stry)

    if not os.path.isfile(pyservsup.globals.passfile):
        ret = "ERR " + "No initial user(s) yet"
    else:
        xret = pyservsup.auth(self.resp.user, strx[1])
        if xret[0] == 3:
            stry = "No such user  '" + self.resp.user + "' " + \
                    str(self.resp.client_address)
            pysyslog.syslog(stry)
            ret = "ERR No such user"
        elif xret[0] == 1:
            stry = "Successful logon  '" + self.resp.user + "' " + \
                    str(self.resp.client_address)
            pysyslog.syslog(stry)
            ret = "OK " + self.resp.user + " Authenticated."
            retval = False
        else:
            stry = "Error on logon  '" + self.resp.user + "' " + \
                    str(self.resp.client_address)
            pysyslog.syslog(stry)
            ret = "ERR " + xret[1]
    self.resp.datahandler.putdata(ret, self.resp.ekey)
    return retval

def get_uadd_func(self, strx):
    if not os.path.isfile(pyservsup.globals.passfile):
        response = "ERR " + "No initial users yet"
    elif len(strx) < 3:
        response = "ERR must specify user name and pass"
    else:
        # See if there is a user by this name
        ret = pyservsup.auth(strx[1], strx[2], 1)
        if ret[0] == 0:
            response = "ERR " + ret[1]
        elif ret[0] == 1:
            response = "ERR user already exists, no changes "
        elif ret[0] == 2:
            response = "OK added user '" + strx[1] + "'"
        else:
            response = "ERR " + ret[1]
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_uini_func(self, strx):
    # Test for local client
    if str(self.resp.client_address[0]) != "127.0.0.1":
        response = "ERR must connect from loopback for user ini"
    elif len(strx) < 3:
        response = "ERR must specify user name and pass"
    else:
        # See if there is a password file
        if os.path.isfile(pyservsup.globals.passfile):
            response = "ERR " + "Initial user already exists"
        else:
            ret = pyservsup.auth(strx[1], strx[2], 1)
            if ret[0] == 0:
                response = "ERR " + ret[1]
            elif ret[0] == 1:
                response = "ERR user already exists, no pass changed "
            elif ret[0] == 2:
                response = "OK added user '" + strx[1] + "'"
            else:
                response = "ERR " + ret[1]
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_kini_func(self, strx):
    # Test for local client
    if str(self.resp.client_address[0]) != "127.0.0.1":
        response = "ERR must connect from loopback for keyini"
    elif len(strx) < 3:
        response = "ERR must specify key_name and key_value"
    else:
        # See if there is a key file
        if os.path.isfile(pyservsup.keyfile):
            response = "ERR " + "Initial key already exists"
        else:
            #tmp2 = bluepy.bluepy.decrypt(self.resp.passwd, "1234")
            #tmp = bluepy.bluepy.encrypt(strx[2], tmp2)
            #ret = pyservsup.kauth(strx[1], tmp, 1)
            ret = pyservsup.kauth(strx[1], strx[2], 1)
            #bluepy.bluepy.destroy(tmp)

            if ret[0] == 0:
                response = "OK added key '" + strx[1] + "'"
            else:
                response = "ERR " + ret[1]
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_kadd_func(self, strx):
    if not os.path.isfile(pyservsup.keyfile):
        response = "ERR " + "No initial keys yet"
    if len(strx) < 3:
        response = "ERR must specify key_name and key_value"
    else:
        # See if there is a key by this name
        ret = pyservsup.kauth(strx[1], strx[2], 1)
        if ret[0]  < 0:
            response = "ERR " + ret[1]
        elif ret[0] == 2:
            response = "ERR key already exists, no keys are changed "
        elif ret[0] == 0:
            response = "OK added key '" + strx[1] + "'"
        else:
            response = "ERR " + "invalid return code"
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_udel_func(self, strx):
    if not os.path.isfile(pyservsup.globals.passfile):
        response = "ERR " + "No users yet"
    elif len(strx) < 3:
        response = "ERR must specify user name and pass"
    else:
        # Delete user
        ret = pyservsup.auth(strx[1], strx[2], 2)
        if ret[0] == 0:
            response = "ERR " + ret[1]
        elif ret[0] == 4:
            response = "OK deleted user '" + strx[1] + "'"
        else:
            response = "ERR " + ret[1]
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_fname_func(self, strx):
    try:
        self.resp.fname = strx[1]
        response = "OK Send file '" + self.resp.fname + "'"
    except:
        response = "ERR Must specify file name"
    self.resp.datahandler.putdata(response, self.resp.ekey)

def get_data_func(self, strx):
    if self.resp.fname == "":
        response = "ERR No filename for data"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return
    try:
       self.resp.dlen = int(strx[1])
    except:
        response = "ERR Must specify file name"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return
    try:
        fh = open(self.resp.fname, "w")
    except:
        response = "ERR Cannot save file on server"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return
    self.resp.datahandler.putdata("OK Send data", self.resp.ekey)

    # Consume buffers until we got all
    mylen = 0
    while mylen < self.resp.dlen:
        need = min(pyservsup.buffsize,  self.resp.dlen - mylen)
        need = max(need, 0)
        data = self.resp.datahandler.handle_one(self.resp)
        if self.resp.ekey != "":
            data2 = bluepy.bluepy.decrypt(data, self.resp.ekey)
        else:
            data2 = data
        try:
            fh.write(data2)
        except:
            response = "ERR Cannot write data on server"
            self.resp.datahandler.putdata(response, self.resp.ekey, False)
            fh.close()
            return
        mylen += len(data)
        # Faulty transport, abort
        if len(data) == 0:
            break
    fh.close()
    if  mylen != self.resp.dlen:
        response = "ERR faulty amount of data arrived"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return
    xstr = "Received file: '" + self.resp.fname + \
                "' " + str(self.resp.dlen) + " bytes"
    print( xstr)
    pysyslog.syslog(xstr)
    self.resp.datahandler.putdata("OK Got data", self.resp.ekey)

def get_help_func(self, strx):

    #print( "get_help_func", strx)
    hstr = "OK "
    if len(strx) == 1:
        for aa in pystate.state_table:
            hstr += aa[0] + " "
    else:
        for aa in pystate.state_table:
            if strx[1] == aa[0]:
                hstr = "OK " + aa[4]
                break
        if hstr == "OK ":
            hstr = "ERR no help for command '" + strx[1] + "'"

    self.resp.datahandler.putdata(hstr, self.resp.ekey)







