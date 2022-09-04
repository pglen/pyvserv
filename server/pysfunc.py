#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time, stat, base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Hash import SHA512
from Crypto import Random

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base, '../bluepy'))
sys.path.append(os.path.join(base, '../common'))
sys.path.append(os.path.join(base,  '../../pycommon'))

import support, pyservsup, pyclisup, crysupp, pysyslog, pystate
import bluepy

pgdebug = 0

# ------------------------------------------------------------------------
# State transition and action functions

def get_lsd_func(self, strx):

    sss = ""
    dname2 = self.resp.cwd + os.sep + self.resp.dir + os.sep
    dname2 = support.dirclean(dname2)

    if pgdebug > 1:
        print("get_lsd_func", dname2)
    response = ["OK"]
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
        response = ["ERR" + str(sys.exc_info()[1] )]

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

    response = ["OK"]
    try:
        ddd = os.listdir(dname2)
        for aa in ddd:
            try:
                aaa = dname2 + os.sep + aa
                if not stat.S_ISDIR(os.stat(aaa)[stat.ST_MODE]):
                    # Escape spaces
                    response.append(aa) #support.escape(aa))
            except:
                print( "Cannot stat ", aaa, str(sys.exc_info()[1]) )

    except:
        support.put_exception("ls ")
        response = ["ERR", "No such directory."]

    #print("response", response)
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_fget_func(self, strx):
    dname = ""
    if len(strx) == 1:
        response = ["ERR", "Must specify file name."]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    dname = support.unescape(strx[1]);
    dname2 = self.resp.cwd + os.sep + self.resp.dir + os.sep + dname
    dname2 = support.dirclean(dname2)
    if not os.path.isfile(dname2):
        response = ["ERR", "File does not exist.", dname]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    flen = 0
    try:
        flen = os.stat(dname2)[stat.ST_SIZE]
        fh = open(dname2, "rb")
    except:
        support.put_exception("fget")
        response = ["ERR", "Cannot open file.", dname]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    response = ["OK", str(flen)]
    self.resp.datahandler.putencode(response, self.resp.ekey)
    # Loop, break when file end or transmission error

    while 1:
        try:
            buff = fh.read(pyservsup.buffsize)
            blen = len(buff)
        except:
            print("Cannot read local file", sys.exc_info())
            break

        try:
            ret = self.resp.datahandler.putencode([str(blen), buff,], self.resp.ekey, False)
        except:
            break;

        if ret == 0:
            break
        if blen == 0:
            break

    # Lof and set state to IDLE
    xstr = "Sent file: '" + dname + \
                "' " + str(flen) + " bytes"

    #print(xstr)
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
    if dname2 == "": dname2 = os.sep
    response = ["OK",  dname2]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_cd_func(self, strx):
    org = self.resp.dir
    try:
        dname = support.unescape(strx[1]);
        if dname == "..":
            self.resp.dir = support.chup(self.resp.dir)
        elif dname[0] == os.sep:
            self.resp.dir = dname
        else:
            self.resp.dir += os.sep + dname

        self.resp.dir = support.dirclean(self.resp.dir)
        dname2 = self.resp.cwd + os.sep + self.resp.dir
        dname2 = support.dirclean(dname2)
        if os.path.isdir(dname2):
            response = ["OK ", self.resp.dir]
        else:
            # Back out
            self.resp.dir = org
            response = ["ERR", "Directory does not exist"]
    except:
        support.put_exception("cd")
        response = ["ERR", "Must specify directory name"]
    self.resp.datahandler.putencode(response, self.resp.ekey)

# ------------------------------------------------------------------------

def get_ver_func(self, strx):
    if pgdebug > 1:
        print( "get_ver_func()", strx)
    res = []
    res.append("OK");    res.append("%s" % pyservsup.version)
    if pgdebug > 2:
        print( "get_ver_func->output", "'" + res + "'")
    self.resp.datahandler.putencode(res, self.resp.ekey)

def get_id_func(self, strx):
    if pgdebug > 1:
        print( "get_id_func()", strx)
    res = []
    res.append("OK");    res.append("%s" % pyservsup.globals.siteid)
    if pgdebug > 2:
        print( "get_ver_func->output", "'" + res + "'")
    self.resp.datahandler.putencode(res, self.resp.ekey)

def get_hello_func(self, strx):
    if pgdebug > 1:
        print( "get_hello_func()", strx)
    strres = ["OK", "Hello", str(pyservsup.globals.siteid)]
    if pgdebug > 2:
        print( "get_hello_func->output", "'" + str(strres) + "'")
    self.resp.datahandler.putencode(strres, self.resp.ekey)


def get_stat_func(self, strx):

    fname = ""; aaa = " "
    #print("stat_func", strx[1])

    dname = support.unescape(strx[1]);
    #print("stat_func", strx[1], dname)

    dname2 = self.resp.cwd + os.sep + self.resp.dir + os.sep + dname
    dname2 = support.dirclean(dname2)

    response = ["OK"]
    response.append(strx[1])

    try:
        sss = os.stat(dname2)
        for aa in sss:
            response.append(str(aa))

    except OSError:
        support.put_exception("stat")
        #print( sys.exc_info())
        response = ["ERR", str(sys.exc_info()[1]) ]
    except:
        response = ["ERR", "Must specify file name"]
        #print( sys.exc_info())

    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_user_func(self, strx):
    if len(strx) < 2:
        self.resp.datahandler.putencode(["ERR", "must specify user name"], self.resp.ekey)
        return True
    self.resp.user = strx[1]
    self.resp.datahandler.putencode(["OK", "send pass ..."], self.resp.ekey)

# ------------------------------------------------------------------------

def get_sess_func(self, strx):

    #if pgdebug > 4:
    #    print("get_sess_func() called")

    if pgdebug > 5:
        print("strx", strx)

    if len(strx) < 4:
        self.resp.datahandler.putencode(["ERR", "not enough arguments."], self.resp.ekey)
        return

    if pgdebug > 4:
        print("Got session key command.")

    sss = SHA512.new(); sss.update(strx[3])

    # Arrived safely?
    if strx[2] != sss.hexdigest():
        self.resp.datahandler.putencode(["ERR", "session key damaged on transport."], self.resp.ekey)
        return

    dsize = SHA.digest_size
    sentinel = Random.new().read(dsize)
    message2 = self.priv_cipher.decrypt(strx[3], sentinel)

    # Decoded OK?
    ttt = SHA512.new(); ttt.update(message2)

    if pgdebug > 3:
        print("Hash1:", strx[1])
        print("Hash2:",   ttt.hexdigest())

    if ttt.hexdigest() != strx[1]:
        self.resp.datahandler.putencode(["ERR", "session key damaged on decoding."], self.resp.ekey)
        return

    self.resp.datahandler.putencode(["OK", "Session estabilished."], self.resp.ekey)
    self.resp.ekey = message2

    if pgdebug > 1:
        support.shortdump("session key:", self.resp.ekey )

# ------------------------------------------------------------------------

def get_akey_func(self, strx):

    if pgdebug > 1:
        print("get_akey_func() called")

    ddd = os.path.abspath("keys")
    ppp = os.path.abspath("private")

    try:
        self.keyfroot = pyservsup.pickkey(ddd)
    except:
        print("No keys generated yet.", sys.exc_info()[1])
        support.put_exception("no keys yet")
        rrr = ["ERR", "No keys yet. Run keygen"]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    if pgdebug > 2:
       print("self.keyfroot", self.keyfroot)

    if pgdebug > 2:
        print("fname", ddd + os.sep + self.keyfroot + ".pub")

    try:
        # Do public import
        fp = open(ddd + os.sep + self.keyfroot + ".pub", "rb")
        self.keyx = fp.read()
        fp.close()

        if pgdebug > 4:
            print("Key read: \n'" + self.keyx.decode("cp437") + "'\n")

    except:
        print("Cannot read key:", self.keyfroot, sys.exc_info()[1])
        support.put_exception("read key")
        rrr = ["ERR", "cannot open keyfile."]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)

    try:
        self.pubkey = RSA.importKey(self.keyx)
    except:
        print("Cannot read key:", self.keyx[:12], sys.exc_info()[1])
        support.put_exception("import  key")
        rrr = ["ERR", "Cannot read public key"]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    # Do private import; we are handleing it here, so key signals errors
    fp2 = open(ppp + os.sep + self.keyfroot + ".pem", "rb")
    self.keyx2 = fp2.read()
    fp2.close()

    try:
        self.privkey = RSA.importKey(self.keyx2)
        self.priv_cipher = PKCS1_v1_5.new(self.privkey)
    except:
        print("Cannot create private key:", self.keyx2[:12], sys.exc_info()[1])
        support.put_exception("import private key")
        rrr = ["ERR", "Cannot create private key"]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return

    # Clean private key from memory
    # cccc

    hh = SHA512.new(); hh.update(self.keyx)
    if pgdebug > 3:
        print("Key digest: \n'" + hh.hexdigest() + "'\n")

    # Deliver the answer in two parts:
    rrr = ["OK", "%s" % hh.hexdigest(), self.keyx]
    self.resp.datahandler.putencode(rrr, self.resp.ekey)

def get_pass_func(self, strx):

    ret = "";  retval = True

    # Make sure there is a trace of the attempt
    stry = "Logon  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
    pysyslog.syslog(stry)

    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_DIS:
        rrr = ["ERR", "this user is temporarily disabled"]
        self.resp.datahandler.putencode(rrr, self.resp.ekey)
        return retval

    xret = pyservsup.passwd.auth(self.resp.user, strx[1], 0, pyservsup.USER_AUTH)
    rrr = []
    if xret[0] == 3:
        stry = "No such user  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)
        rrr = ["ERR", "No such user"]
    elif xret[0] == 1:
        stry = "Successful logon  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)

        #print("Authenticated", pyservsup.globals.paydir)
        self.resp.cwd = pyservsup.globals.paydir
        #try:
        #    os.chdir(self.resp.cwd)
        #except:
        #    print("Cannot change to payload dir.")
        #    pass

        rrr = ["OK", self.resp.user + " Authenticated."]

        retval = False
    else:
        stry = "Error on logon  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)
        rrr = ["ERR",  xret[1]]

    self.resp.datahandler.putencode(rrr, self.resp.ekey)
    return retval

def get_chpass_func(self, strx):

    ret = "";  retval = True

    if len(strx) < 2:
        self.resp.datahandler.putdata("ERR must specify new_pass", self.resp.ekey)
        return True

    #print("chpass", strx[1], strx[2])

    # Make sure there is a trace of the attempt
    stry = "chpass  '" + self.resp.user + "' " + \
                str(self.resp.client_address)
    pysyslog.syslog(stry)

    #xret = pyservsup.passwd.auth(self.resp.user, strx[1], 0, pyservsup.USER_AUTH)
    #if xret[0] != 1:
    #    self.resp.datahandler.putdata("ERR old pass must match", self.resp.ekey)
    #    return True

    xret = pyservsup.passwd.auth(self.resp.user, strx[1], 0, pyservsup.USER_CHPASS)

    if xret[0] == 5:
        stry = "Pass changed '" + self.resp.user + "' " + \
                str(self.resp.client_address)
        pysyslog.syslog(stry)
        ret = "OK Pass changed"
    elif xret[0] == 3:
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

    retval = 0
    #print("uadd", strx)

    # Are we allowed to add users?
    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = "ERR only admin can add/delete users"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return retval

    if len(strx) < 3:
        response = "ERR must specify user name and pass"
        self.resp.datahandler.putdata(ret, self.resp.ekey)
        return retval

    # Add this user in not exist
    ret = pyservsup.passwd.auth(strx[1], strx[2], 0, pyservsup.USER_ADD)
    if ret[0] == 0:
        response = "ERR " + ret[1]
    elif ret[0] == 1:
        response = "ERR user already exists, no changes "
    elif ret[0] == 2:
        response = "OK added user '" + strx[1] + "'"
    else:
        response = "ERR " + ret[1]

    self.resp.datahandler.putdata(response, self.resp.ekey)

# Add Admin
def get_aadd_func(self, strx):

    retval = 0
    # Are we allowed to add users?
    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = ["ERR", "only admin can add/delete users"]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if len(strx) < 3:
        response = ["ERR", "must specify user name and pass"]
        self.resp.datahandler.putencode(ret, self.resp.ekey)
        return retval

    # Add this user in not exist
    ret = pyservsup.passwd.auth(strx[1], strx[2], pyservsup.PERM_ADMIN, pyservsup.USER_ADD)
    if ret[0] == 0:
        response = "ERR", ret[1]
    elif ret[0] == 1:
        response = "ERR", "user already exists, no changes."
    elif ret[0] == 2:
        response = ["OK added user ", strx[1]]
    else:
        response = ["ERR", ret[1]]

    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_uena_func(self, strx):

    retval = 0

    # Are we allowed to add users?
    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = "ERR", "only admin can modify users."
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if len(strx) < 2:
        response = "ERR", "must specify user name and flag"
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    if strx[2] == "enable":
        mode = pyservsup.PERM_DIS  | pyservsup.RESET_MODE
    elif strx[2] == "disable":
        mode = pyservsup.PERM_DIS
    else:
        response = ["ERR", "must specify 'enable' or 'disable'"]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return retval

    # Add this user in not exist
    ret = pyservsup.passwd.auth(strx[1], strx[2], mode, pyservsup.USER_CHMOD)

    if ret[0] == 0:
        response = "ERR", ret[1]
    elif ret[0] == 8:
        response = "OK",  strx[1], strx[2] + "d"
    else:
        response = "ERR", ret[1]

    self.resp.datahandler.putencode(response, self.resp.ekey)


def get_uini_func(self, strx):

    # Test for local client
    if str(self.resp.client_address[0]) != "127.0.0.1":
        response = ["ERR",  "must connect from loopback for user ini"]

    elif  pyservsup.passwd.count() != 0:
        response = ["ERR", "already has initial user"]

    elif len(strx) < 3:
        response = ["ERR", "must specify user name and pass"]
    else:
        ret = pyservsup.passwd.auth(strx[1], strx[2],
                    pyservsup.PERM_INI | pyservsup.PERM_ADMIN,
                        pyservsup.USER_ADD)
        if ret[0] == 0:
            response = ["ERR", ret[1]]
        elif ret[0] == 1:
            response = ["ERR", "user already exists, no change. Use pass function."];
        elif ret[0] == 2:
            response = ["OK", "added initial user", strx[1]]
        else:
            response = ["ERR", ret[1]]

    self.resp.datahandler.putencode(response, self.resp.ekey)

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

    retval = 0
     # Are we allowed to add users?
    ret = pyservsup.passwd.perms(self.resp.user)
    if int(ret[2]) & pyservsup.PERM_ADMIN != pyservsup.PERM_ADMIN:
        response = "ERR only admin can add/delete users"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return retval

    if len(strx) < 3:
        response = "ERR must specify user name and pass"
        self.resp.datahandler.putdata(response, self.resp.ekey)
        return retval

    # Delete user
    ret = pyservsup.passwd.auth(strx[1], strx[2],
                    pyservsup.PERM_NONE, pyservsup.USER_DEL)

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
        response = ["OK", "Send file", self.resp.fname]
    except:
        response = ["ERR",  "Must specify file name"]
    self.resp.datahandler.putencode(response, self.resp.ekey)

def get_data_func(self, strx):
    if self.resp.fname == "":
        response = ["ERR", "No filename for data"]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    try:
       self.resp.dlen = int(strx[1])
    except:
        response = ["ERR", "Must specify file name"]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    try:
        fh = open(self.resp.fname, "wb")
    except:
        response = ["ERR", "Cannot save file on server"]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    self.resp.datahandler.putencode(["OK", "Send data"], self.resp.ekey)

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

    if pgdebug > 1:
        print( "get_help_func()", strx)

    harr = []
    if len(strx) == 1:
        harr.append("OK")
        for aa in pystate.state_table:
            harr.append(aa[0])
    else:
        ff = False
        for aa in pystate.state_table:
            if strx[1] == aa[0]:
                harr.append("OK")
                harr.append(aa[4])
                ff = True
                break
        if not ff:
                harr.append("ERR")
                harr.append("No such command")

    if pgdebug > 2:
        print( "get_help_func->output", "[" + harr + "]")

    self.resp.datahandler.putencode(harr, self.resp.ekey)

# EOF