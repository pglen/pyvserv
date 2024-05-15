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
from Crypto.Hash import SHA256

#import pyvpacker

from pyvcommon import support, pyservsup, pyclisup, pysyslog, pyvhash, pyvindex
from pyvserver import pyvstate

from pydbase import twincore

from pyvfuncsup import  *
from pyvfuncr   import  *
from pyvfuncf   import  *

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

# ------------------------------------------------------------------------
# State transition and action functions

def get_exit_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_exit_func()", strx)

    # Clean up logouts
    if self.resp.user:
        pyservsup.SHARED_LOGINS.deldat(self.resp.user)

    if pyservsup.globals.conf.pglog > 0:
        stry = "Quit", wr(self.resp.user), str(self.resp.client_address)
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
    repsize = repcore.getdbsize()

    if strx[1] == 'add':

        # Check duplicate
        for aa in range(repsize-1, -1, -1):
            rec = repcore.get_rec(aa)
            if not rec:
                continue
            #print("rec:", rec)
            try:
                dec = self.pb.decode_data(rec[1])[0]['PayLoad']
            except:
                dec['host'] = ""
            #print("dec", dec)
            if dec['host'] == strx[2]:
                response = [ERR, "Duplicate entry.", strx[2]]
                self.resp.datahandler.putencode(response, self.resp.ekey)
                return

        uuu = str(uuid.uuid1())
        now = datetime.datetime.now().replace(microsecond=0).isoformat()
        undec = {"host" : strx[2], "header" : uuu,
                  "now": now, "oper": self.resp.user }
        #print("undec", undec)
        pvh = pyvhash.BcData()
        pvh.addpayload(undec)
        #pvh.hasharr()
        #while not pvh.powarr():
        #    pass

        ddd = self.pb.encode_data("", pvh.datax)
        ret = repcore.save_data(uuu, ddd)
        if self.pgdebug > 8:
            print("repcore save:", ret, ddd)

        response = [OK, "Added replication host:port.", strx[2]]
        self.resp.datahandler.putencode(response, self.resp.ekey)

    elif strx[1] == 'del':

        found = -1
        for aa in range(repsize-1, -1, -1):
            rec = repcore.get_rec(aa)
            if not rec:
                continue
            #print("rec:", rec)
            try:
                dec = self.pb.decode_data(rec[1])[0]['PayLoad']
            except:
                dec['host'] = ""
            #print("dec", dec)
            if dec['host'] == strx[2]:
                found = aa

        if found < 0:
            response = [ERR, "Cannot delete, entry not found.", strx[2]]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return

        #print("del found:", found)

        if self.pgdebug > 4:
            print("delete ihost rec:", strx[2])

        ret = repcore.del_rec(found)
        response = [OK, "Deleted replication host:port.", strx[2]]
        self.resp.datahandler.putencode(response, self.resp.ekey)

    elif strx[1] == 'list':
        arr = []
        for aa in range(repcore.getdbsize()-1, -1, -1):
            rec = repcore.get_rec(aa)
            if not rec:
                continue
            try:
                dec = self.pb.decode_data(rec[1])[0]['PayLoad']
            except:
                dec['host'] = ""
            #print("dec", dec)

            if dec['host']:
                arr.append(dec['host'])

        #print("got recs", arr)
        response = [OK,  arr]
        self.resp.datahandler.putencode(response, self.resp.ekey)
    else:
        response = [ERR, "Operation must be 'add', 'del or list'.", strx[2]]
        self.resp.datahandler.putencode(response, self.resp.ekey)

# ------------------------------------------------------------------------

def get_ver_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_ver_func()", strx)

    res = [OK, "%s" % pyservsup.VERSION,
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


def get_lout_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_lout_func()", strx)

    if not self.resp.user:
        response = [ERR, "Not logged in.", strx[0], ]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if pyservsup.globals.conf.pglog > 0:
        stry = "Logout", wr(self.resp.user), \
                str(self.resp.client_address)
        pysyslog.syslog(*stry)

    if self.pgdebug > 3:
        print("logout", self.resp.user)

    if self.resp.user:
        pyservsup.SHARED_LOGINS.deldat(self.resp.user)

    olduser = self.resp.user
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
        stry = "Attempted login", wr(self.resp.preuser), \
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
            stry = "No such user", wr(self.resp.preuser), \
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
            stry = "Successful login", wr(self.resp.preuser),  \
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
            stry = "Error on login", wr(self.resp.preuser), \
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
        stry = "chpass", wr(self.resp.user), \
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
            stry = "Pass changed", wr(resp.user), \
                str(self.resp.client_address)
            pysyslog.syslog(*stry)
        ret = [OK, "Pass changed", strx[1]]
    elif xret[0] == 3:
        if pyservsup.globals.conf.pglog > 1:
            stry = "No such user", wr(strx[1]),  \
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
            stry = "Error on login", wr(strx[1]), \
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
