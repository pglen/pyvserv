#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time, traceback, random, uuid
import datetime, base64, fcntl

#base = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(base, '../pyvcommon'))

import support, pyclisup, crysupp, pysyslog

#from Crypto.Hash import SHA512
from Crypto.Hash import SHA256
from Crypto import Random

# Globals and configurables

version = "1.0"

# Actions
USER_AUTH  = 0;  USER_ADD = 1;   USER_DEL = 2;   USER_CHPASS = 3;
USER_CHMOD = 4;

# Permissions
PERM_NONE = 0;  PERM_INI = 1;   PERM_ADMIN = 2;   PERM_DIS = 4;
PERM_NON = 8;

# Modes
RESET_MODE = 0x80;

pgdebug = 0

#buffsize = 1024;
buffsize = 4096;

chainfname  = "initial"
repfname    = "pyvreplic"
logfname    = "pyvserver"

lock_pgdebug = 0
lock_locktout = 5

class   Global_Vars:

    def __init__(self, scriptname, dataroot):

        # Underscore names are definitions - others are calculated

        self.verbose = 0
        self._script_home = scriptname    # where the original script lives

        self._dataroot  =   dataroot
        self._passfile  =  "passwd.secret"
        self._keyfile   =  "keys.secret"
        self._idfile    =  "pyservid.init"

        if self._dataroot[0] != os.sep:
            self.myhome     =  os.path.expanduser(
                                "~" + os.sep + self._dataroot + os.sep)
        else:
            self.myhome     =  self._dataroot + os.sep

        self.myhome    = os.path.normpath(self.myhome) + os.sep

        if self.verbose:
            print("myhome", self.myhome)

        # make sure it exists
        self._softmkdir(self.myhome)

        if self.verbose:
            print("myhome dir:", self.myhome)

        self.passdir   =  self.myhome + ".pyvserv" + os.sep
        self.keydir    =  self.myhome + "keys"  + os.sep
        self.privdir   =  self.myhome + "private"  + os.sep
        self.paydir    =  self.myhome + "payload"  + os.sep
        self.chaindir  =  self.myhome + "chain" + os.sep
        self.tmpdir    =  self.myhome + "tmp"  + os.sep
        self.logdir    =  self.myhome + "log"  + os.sep

        self.passdir    = os.path.normpath(self.passdir)
        self.keydir     = os.path.normpath(self.keydir)
        self.privdir    = os.path.normpath(self.privdir)
        self.paydir     = os.path.normpath(self.paydir)
        self.chaindir   = os.path.normpath(self.chaindir)
        self.tmpdir     = os.path.normpath(self.tmpdir)
        self.logdir     = os.path.normpath(self.logdir)

        self._softmkdir(self.passdir, "Pass dir")
        self._softmkdir(self.keydir, "Key dir")
        self._softmkdir(self.privdir, "Private dir")
        self._softmkdir(self.paydir, "Payload dir")
        self._softmkdir(self.chaindir, "Chain dir")
        self._softmkdir(self.tmpdir, "Temporary dir")
        self._softmkdir(self.logdir, "Log dir")

        self.lockfname = self.tmpdir + os.sep + "lockfile"
        self.passfile = self.passdir + os.sep + self._passfile
        self.idfile = self.myhome + self._idfile

        self.siteid     =  None
        self.throttle   =  10       # seconds
        self.instance   =  15       # max instace from one IP/host
        self.maxthdat   =  100      # max data in throttle var

        #print("init globals");
        #global globals
        #globals = self
        pass

    # Soft make dir
    def _softmkdir(self, ddd, fff="data"):

        if not os.path.isdir(ddd):
            try:
                os.mkdir(ddd, 0o700)
            except:
                print( "Cannot make " + ddd + " " + fff + " dir", sys.exc_info())
                sys.exit(1)

    # --------------------------------------------------------------------

    def config(self, realp, conf):

        self.verbose = conf.verbose
        self.pgdebug = conf.pgdebug

        #if conf.verbose:
        #    print("Script home:     ", self._script_home)

        if conf.pgdebug:
                print ("Debug level:     ", conf.pgdebug)

        #self._datadir = self.script_home + self._datadir

# ------------------------------------------------------------------------
# This will create the server's UUID

def  create_read_idfile(fname):

    # Create globals file, read it if exists
    if  not os.path.isfile(fname):
        try:
            nnn = datetime.datetime.today()
            fp = open(fname, "w+")
            fp.write("# Server Identification String for pyvserv.py.\n#     !!! DO NOT DELETE !!!\n")
            fp.write("# Server ID created on: " + str(nnn) + "\n\n")
            iii = uuid.uuid4()
            fp.write(str(iii) + "\n")
            iii2 = uuid.uuid4()
            fp.write(str(iii2) + "\n\n")
            fp.close()

            xxx = str(iii) + "\n" + str(iii2) + "\n"
            yyy = base64.b64encode(xxx.encode("utf-8"))

            fp3 = open(fname + ".backup", "w+")
            fp3.write("# Server ID backup as Base64 of the two NL terminated UUIDs\n")
            fp3.write("# ID created on: " + str(nnn) + "\n\n")
            fp3.write("-------- BASE64 BEG --------\n" +
                        yyy.decode("utf-8") +
                    "\n-------- BASE64 END --------\n")
            fp3.close()

        except:
            print("Cannot create server ID file")
            raise

    uuuu = None
    fp2 = open(fname)
    strx = fp2.read()
    for aa in strx.split("\n"):
        if len(aa):
            # Skip spaces
            idx = 0
            for bb in aa:
                if bb == " ":
                    idx += 1
                else:
                    break

            # Comments
            if aa[idx] == "#":
                continue
            try:
                uuuu = uuid.UUID(aa[idx:])
            except:
                #print("Badly formed UUID");
                pass
            break
    fp2.close

    return uuuu

# ------------------------------------------------------------------------

class   FileLock():

    ''' A working file lock in Linux '''

    def __init__(self):

        ''' Create the lock file '''
        self.lockname = None

    def waitlock(self):

        if not self.lockname:
            self.lockname = globals.passfile + ".lock"
            #print("lockname", self.lockname)

            try:
                self.fpx = open(self.lockname, "rb+")
            except:
                try:
                    self.fpx = open(self.lockname, "wb+")
                except:
                    if lock_pgdebug > 1:
                        print("Cannot create lock file")
                    raise

        if lock_pgdebug > 1:
            print("Waitlock", self.lockname)

        cnt = 0
        while True:
            try:
                buff = self.fpx.read()
                self.fpx.seek(0, os.SEEK_SET)
                self.fpx.write(buff)
                break;
            except:
                if lock_pgdebug > 1:
                    print("waiting", sys.exc_info())

            if cnt > lock_locktout :
                # Taking too long; break in
                if 1: #lock_pgdebug > 1:
                    print("Lock held too long pid =", os.getpid(), cnt)
                self.unlock()
                break
            cnt += 1
            time.sleep(1)
        # Lock NOW
        fcntl.lockf(self.fpx, fcntl.LOCK_EX)

    def unlock(self):
        fcntl.lockf(self.fpx, fcntl.LOCK_UN)

# ------------------------------------------------------------------------
# This class will maintain a passwd database, similar to
#  the system database

class Passwd():

    def __init__(self):
        self.pgdebug = 0
        self.verbose = 0
        global lock_pgdebug
        lock_pgdebug = 0
        self.lock = FileLock()

    def     _xjoin(self, iterx, charx):
        sss = ""
        try:
            for aa in iterx:
                if sss != "":
                    sss += charx
                if type(aa) != str:
                    aa = aa.decode("utf-8")
                sss += aa
        except:
            print(sys.exc_info())
        return sss

    # Use fast hash, imitate salt by random numvber at the end

    def     _dblsalt(self, upass):

        rstr = Random.new().read(4)
        hstr = ""
        for aa in rstr:
            hstr += "%02x" % aa
        hhh = SHA256.new();
        hhh.update(bytes(upass, "utf-8") + bytes(hstr, "utf-8"))
        #print(hstr)
        ddd = hhh.hexdigest()
        upass2 = ddd  + hstr
        return upass2

    def    _unsalt(self, upass, oldhash):

        hstr = oldhash[-8:]
        hhh = SHA256.new();
        hhh.update(bytes(upass, "utf-8") + bytes(hstr, "utf-8"))
        #print(hstr)
        upass2 = hhh.hexdigest()  + hstr
        return upass2

    def     _deluser(self, passdb, userx, upass):

        delok = 0
        # Delete userx
        pname3 = globals.passfile + ".tmp"
        try:
            fh3 = open(pname3, "w+")
        except:
            ret = -1, "Cannot open " + pname3 + " for writing"
            return ret

        for line in passdb:
            fields = line.split(",")
            if fields[0] == userx:
                delok = 1
                pass
            else:
                fh3.write(line)
        fh3.close()
        # Rename
        try:
            os.remove(globals.passfile)
        except:
            ret = 0, "Cannot remove " + globals.passfile
            return ret
        try:
            os.rename(pname3, globals.passfile)
        except:
            ret = 0, "Cannot rename from " + pname3
            return ret
        if delok:
            ret = 4, "User deleted"
        else:
            ret = 0, "User NOT deleted"

        return ret

    def     _chpass(self, passdb, userx, upass):

        renok = 0

        # Filter onto temp file
        pname3 = globals.passfile + ".tmp"
        try:
            fh3 = open(pname3, "w+")
        except:
            ret = (-1, "Cannot open " + pname3 + " for writing")
            return ret

        for line in passdb:
            fields = line.split(",")
            if fields[0] == userx:
                fields[2] = self._dblsalt(upass) + '\n'
            line2 = self._xjoin(fields, ",")
            fh3.write(line2)
        fh3.close()

        # Rename
        try:
            os.remove(globals.passfile)
            renok = True
        except:
            ret = 0, "Cannot remove " + globals.passfile
            return ret
        try:
            os.rename(pname3, globals.passfile)
        except:
            ret = 0, "Cannot rename from " + pname3
            return ret

        if renok:
            ret = 5, "New Pass set"
        else:
            ret = 0, "Pass NOT set"

        return ret

    def _auth(self, passdb, userx, upass):

        ret = [0, "Bad User or Bad Pass"]
        for line in passdb:
           fields = line.split(",")
           if fields[0] == userx:
               fff = fields[2].rstrip()
               #print("this user", fields)
               c2 = self._unsalt(upass, fff)
               if c2 == fff:
                   if self.verbose:
                       print ("Auth OK for ", userx)
                   ret = [1, "Authenicated", userx]
                   break
        return ret

    def     _chmod(self, passdb, userx, umode):

        modeok = 0

        # Filter onto temp file
        pname3 = globals.passfile + ".tmp"
        try:
            fh3 = open(pname3, "w+")
        except:
            ret = (0, "Cannot open " + pname3 + " for writing")
            return ret

        for line in passdb:
            fields = line.split(",")
            if fields[0] == userx:
                fff = int(fields[1])
                if umode & RESET_MODE:
                    fff &= ~umode
                else:
                    fff |= umode
                fields[1] = str(fff)

            line2 = self._xjoin(fields, ",")
            fh3.write(line2)
        fh3.close()

        # Rename
        try:
            os.remove(globals.passfile)
            modeok = True
        except:
            ret = 0, "Cannot remove " + globals.passfile
            return ret
        try:
            os.rename(pname3, globals.passfile)
        except:
            ret = 0, "Cannot rename from " + pname3
            return ret

        if modeok:
            ret = 8, "New Mode set"
        else:
            ret = 0, "Mode NOT set"

        return ret

    # Return user count
    def     count(self):

        if self.pgdebug:
            print("usingpassfile:", os.getcwd(), globals.passfile)

        if not os.path.isfile(globals.passfile):
            return 0
        try:
            fh = open(globals.passfile, "r")
        except:
            return 0
        passdb = fh.readlines()
        fh.close()
        return len(passdb)

    # ------------------------------------------------------------------------
    # Authenticate from local file. Return err code and cause.
    #
    #   uadd = 0 -> Authenticate
    #   uadd = 1 -> add
    #   uadd = 2 -> delete
    #   uadd = 3 -> chpass
    #
    #   flags = 0 -> none
    #   flags = 1 -> uini user
    #   flags = 2 -> admin user
    #   flags = 4 -> disabled
    #
    # Return negative for error
    #        0 for user added
    #        0 for bad user or bad pass
    #        1 for user match
    #        2 for duplicate
    #        3 for no user
    #        4 for user deleted
    #        5 for user pass changed
    #        6 Duplicate user
    #        7 Permission OK
    #        8 chmod OK

    def  auth(self, userx, upass, flags = "", uadd = 0):

        #print("auth()", userx, upass, flags)

        #ttt = time.time()
        self.lock.waitlock()
        #print("   auth 1 %.3f" % ((time.time() - ttt) * 1000) )

        userx = support.escape(userx)

        fields = ""; haveusr = False
        try:
            fh = open(globals.passfile, "r")
        except:
            try:
                fh = open(globals.passfile, "w+")
            except:
                self.lock.unlock()
                return -1, "Cannot open / create pass file " + globals.passfile

        passdb = fh.readlines()
        for line in passdb:
            fields = line.split(",")
            #print("fieldx", fields)
            if fields[0] == userx:
                haveusr = True
                break
        fh.close()

        #print("   auth 2 %.3f" % ((time.time() - ttt) * 1000) )

        if not haveusr:
            if uadd == USER_ADD:
                try:
                    fh2 = open(globals.passfile, "r+")
                except:
                    try:
                        fh2 = open(globals.passfile, "w+")
                    except:
                        ret = 0, "Cannot open " + globals.passfile + " for writing"
                        return ret

                fh2.seek(0, os.SEEK_END)
                upass2 = self._dblsalt(upass)

                #fh2.write(userx + "," + str(flags) + "," + upass2.decode("utf-8") + "\n")
                fh2.write(userx + "," + str(flags) + "," + upass2 + "\n")
                fh2.close()
                ret = 2, "Saved user / pass"
            else:
                ret = 3, "No such user"
        else:
            if uadd == USER_CHPASS:
                #print("Change pass", hex(flags))
                ret = self._chpass(passdb, userx, upass)

            elif uadd == USER_CHMOD:
                #print("Change mode", hex(flags))
                ret = self._chmod(passdb, userx, flags)

            elif uadd == USER_DEL:
                #c2 = self._dblsalt(upass)
                #print ("upass", c2, "org:", fields[2].rstrip().encode("utf-8"))
                if int(fields[1]) & PERM_INI == PERM_INI:
                    ret = 0, "Cannot delete uini user"
                else:
                    ret = self._deluser(passdb, userx, upass)

            elif uadd == USER_AUTH:

                ret = self._auth(passdb, userx, upass)

            elif uadd == USER_ADD:
                ret = 6, "Can not add, Duplicate User "
            else:
                ret = 0, "Bad auth command issued"
        self.lock.unlock()
        #print("   auth 3x %.3f" % ((time.time() - ttt) * 1000) )
        return ret

    def perms(self, userx):

        #ttt = time.time()
        self.lock.waitlock()
        #print("   perms 1 %.3f" % ((time.time() - ttt) * 1000) )

        fields = ""; haveusr = False
        try:
            fh = open(globals.passfile, "r")
        except:
            try:
                fh = open(globals.passfile, "w+")
            except:
                #self._unlock()
                return -1, "Cannot open / create pass file " + globals.passfile

        passdb = fh.readlines()
        #print("   perms 2 %.3f" % ((time.time() - ttt) * 1000) )

        if not passdb:
            ret = 7, "User permissions:", 0
            self.lock.unlock()
            fh.close()
            return ret

        for line in passdb:
            fields = line.split(",")
            if fields[0] == userx:
                haveusr = True
                break
            fh.close()

        #print("   perms 3 %.3f" % ((time.time() - ttt) * 1000) )

        if haveusr:
            ret = 7, "User permissions:", fields[1]
        else:
            ret = 7, "User permissions:", 0

        self.lock.unlock()
        #print("   perms 4 %.3f" % ((time.time() - ttt) * 1000) )

        return ret

passwd = Passwd()

# ------------------------------------------------------------------------
# Save key to local file. Return err code and cause.
#   kadd = 0 -> Authenticate
#   kadd = 1 -> add
#   kadd = 2 -> delete
#   kadd = 3 -> chpass
#
# Return negative for error
#        0 for key added
#        1 for key match
#        2 for duplicate
#        4 for key deleted

#def kauth(namex, keyx, kadd = False):
#
#    fields = ""; dup = False; ret = 0, ""
#    try:
#        fh = open(globals.keyfile, "r")
#    except:
#        try:
#            fh = open(globals.keyfile, "w+")
#        except:
#            return -1, "Cannot open / create key file " + globals.keyfile + " for reading"
#    keydb = fh.readlines()
#    for line in keydb:
#        fields = line.split(",")
#        if namex == fields[0]:
#            dup = True
#            break
#    if not dup:
#        if kadd == 1:
#            # Add
#            fh.close()
#            try:
#                fh2 = open(globals.keyfile, "r+")
#            except:
#                try:
#                    fh2 = open(globals.keyfile, "w+")
#                except:
#                    return -1, "Cannot open / create " + globals.keyfile + " for writing"
#            try:
#                fh2.seek(0, os.SEEK_END)
#                fh2.write(namex + "," + keyx + "\n")
#            except:
#                fh2.close()
#                return -1, "Cannot write to " + globals.keyfile
#            fh2.close()
#            ret = 0, "Key saved"
#    else:
#        if kadd == 0:
#            ret = 1, fields[1].rstrip()
#        elif kadd == 1:
#            ret = 2, "Duplicate key"
#        elif kadd == 2:
#            # Delete key
#            delok = 0
#            pname3 = globals.keyfile + ".tmp"
#            try:
#                fh3 = open(pname3, "r+")
#            except:
#                try:
#                    fh3 = open(pname3, "w+")
#                except:
#                    ret = 0, "Cannot open " + pname3 + " for writing"
#                    return ret
#            # Do not touch line 1
#            fh3.write(keydb[0])
#            for line in keydb[1:]:
#                fields = line.split(",")
#                if fields[0] == namex:
#                    delok = 1
#                    pass
#                else:
#                    fh3.write(line)
#            fh3.close()
#            # Rename
#            try:
#                os.remove(globals.keyfile)
#            except:
#                ret = -1, "Cannot remove from " + pname3
#            try:
#                os.rename(pname3, globals.passfile)
#            except:
#                ret = -1, "Cannot rename from " + pname3
#                return ret
#            if delok:
#                ret = 4, "Key deleted"
#            else:
#                ret = -1, "Key NOT deleted (possibly kini key)"
#        else:
#            ret = -1, "Invalid opcode"
#    return ret

# Return basename for key file

def pickkey(keydir):

    #print("Getting keys", keydir)
    dl = os.listdir(keydir)
    if dl == 0:
        print("No keys yet", keydir)
        raise (Valuerror("No keys generated yet"))

    dust = random.randint(0, len(dl)-1)
    eee = os.path.splitext(os.path.basename(dl[dust]))
    #print("picking key", eee[0])
    return eee[0]

# ------------------------------------------------------------------------
# Simple file system based locking system
# !!!!! does not work on Linux !!!!!
# Linux can access the filesystem differently than windosw, however the
# file based locking system work well

#def _createlock(fname, raisex = True):
#
#    ''' Open for read / write. Create if needed. '''
#
#    fp = None
#    try:
#        fp = open(fname, "wb")
#    except:
#        print("Cannot open / create ", fname, sys.exc_info())
#        if raisex:
#            raise
#    return fp
#
#def dellock(lockname):
#
#    ''' Lock removal;
#        Test for stale lock;
#    '''
#
#    try:
#        if os.path.isfile(lockname):
#            os.unlink(lockname)
#    except:
#        if pgdebug > 1:
#            print("Del lock failed", sys.exc_info())
#
#def waitlock(lockname, locktout = 30):
#
#    ''' Wait for lock file to become available. '''
#
#    cnt = 0
#    while True:
#        if os.path.isfile(lockname):
#            if pgdebug > 1:
#                print("Waiting on", lockname)
#            #if cnt == 0:
#            #    try:
#            #        fpx = open(lockname)
#            #        pid = int(fpx.read())
#            #        fpx.close()
#            #    except:
#            #        print("Exc in pid test", sys.exc_info())
#            cnt += 1
#            time.sleep(0.3)
#            if cnt > locktout:
#                # Taking too long; break in
#                if pgdebug > 1:
#                    print("Warn: main Lock held too long ... pid =", os.getpid(), cnt)
#                dellock(lockname)
#                break
#        else:
#            break
#
#    # Finally, create lock
#    xfp = _createlock(lockname)
#    xfp.write(str(os.getpid()).encode())
#    xfp.close()

# ------------------------------------------------------------------------
# Get date out of UUID

def uuid2date(uuu):

    UUID_EPOCH = 0x01b21dd213814000
    dd = datetime.datetime.fromtimestamp(\
                    (uuu.time - UUID_EPOCH)*100/1e9)
    #print(dd.timestamp())
    return dd

def uuid2timestamp(uuu):

    UUID_EPOCH = 0x01b21dd213814000
    dd = datetime.datetime.fromtimestamp(\
                    (uuu.time - UUID_EPOCH)*100/1e9)
    return dd.timestamp()

if __name__ == '__main__':
    print( "This module was not meant to be used directly.")


# EOF


