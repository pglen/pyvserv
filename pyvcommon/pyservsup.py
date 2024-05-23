#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time, traceback, random, uuid
import datetime, base64

import multiprocessing as mp

try:
    import fcntl
except:
    fcntl = None

#base = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(base, '../pyvcommon'))

import support, pyclisup, crysupp, pysyslog

#from Crypto.Hash import SHA512
from Crypto.Hash import SHA256
from Crypto import Random

# Globals and configurables

# Update it here from setup
VERSION = "1.1.0"

# Actions
USER_AUTH  = 0;  USER_ADD = 1;   USER_DEL = 2;   USER_CHPASS = 3;
USER_CHMOD = 4;

# Permissions
PERM_NONE = 0;  PERM_INI = 1;   PERM_ADMIN = 2;   PERM_DIS = 4;
PERM_NON = 8;

# Modes
RESET_MODE = 0x80;

REPFNAME = "replic"

# ------------------------------------------------------------------------
# Globals

pgdebug = 0

#buffsize = 1024;
buffsize = 4096;

chainfname  = "initial"
repfname    = "pyvreplic"
logfname    = "pyvserver"

lock_locktout = 5
shared_logons = None

# Configure the server by customizing this class

class   Global_Vars:

    def __init__(self, scriptname, dataroot):

        # Underscore names are definitions - others are calculated

        self.verbose = 0
        # where the original script lives
        self.script_home = os.path.abspath(scriptname)
        #print("script:", self._script_home)

        self._dataroot  =   dataroot
        self._passfile  =  "passwd.secret"
        self._keyfile   =  "keys.secret"
        self._idfile    =  "pyservid.init"

        # Force relative to home
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

        # These are presets for testing, use larger values for production
        self.throt_sec        =  5    # seconds for conn frequency
        self.throt_maxsec     =  6    # seconds max life in cache
        self.throt_instances  =  5    # max instaces from one IP/host
        self.throt_maxdat     =  10   # max data length in throttle var
        self.throt_time       =  3    # throttle by this many sec

        #print("init globals");
        #global globals
        #globals = self
        pass

    def softmkdir(self, ddd):
        self._softmkdir(ddd)

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

        globals.siteid = create_read_idfile \
                        (globals.idfile)

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

class   FileLock():

    ''' A working file lock in Linux and Windows '''

    def __init__(self, lockname = ""):

        ''' Create the lock file, else just remember the name '''

        #if not lockname:
        #    raise ValueError("Must specify lockfile")

        self.lockname = lockname

        if pgdebug > 0:
            print("lockname init", self.lockname)

        if fcntl:
            if self.lockname:
                try:
                    self.fpx = open(lockname, "wb")
                except:
                    if pgdebug > 1:
                        print("Cannot create lock file")
                    raise ValueError("Cannot create lock file")

    def waitlock(self):

        # If no lockfilename specified, grab one
        if not self.lockname:
            self.lockname = globals.passfile + ".lock"

            if pgdebug > 5:
                print("lockname", self.lockname)

            try:
                self.fpx = open(self.lockname, "wb")
            except:
                if pgdebug > 1:
                    print("Cannot create lock file")

        if pgdebug > 5:
            print("Waitlock", self.lockname)

        if fcntl:
            cnt2 = 0
            while True:
                try:
                    fcntl.flock(self.fpx, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except:
                    pass
                    if pgdebug > 1:
                        print("waiting in fcntl", self.lockname,
                                            os.getpid()) #sys.exc_info())
                cnt2 += 1
                time.sleep(1)
                if cnt2 > lock_locktout:
                    # Taking too long; break in
                    if pgdebug > 1:
                        print("Lock held too long",
                                            os.getpid(), self.lockname)
                    self.unlock()
                    break
        else:
            cnt = 0
            while True:
                try:
                    if os.path.exists(self.lockname):
                        if pgdebug:
                           print("Waiting ... ", self.lockname)
                        pass
                    else:
                        fp = open(self.lockname, "wb")
                        fp.write(str(os.getpid()).encode())
                        fp.close()
                        break
                except:
                    if pgdebug:
                        print("locked",  self.lockname, cnt, sys.exc_info())
                    pass
                time.sleep(1)
                cnt += 1
                if cnt > lock_locktout:
                    if pgdebug:
                        print("breaking lock", self.lockname)
                    break

    def unlock(self):

        if pgdebug > 5:
            print("Unlock", self.lockname)

        if fcntl:
            try:
                fcntl.flock(self.fpx, fcntl.LOCK_UN | fcntl.LOCK_NB)
            except:
                pass
        else:
            try:
                os.remove(self.lockname)
            except:
                pass
                if pgdebug:
                    print("unlock", self.lockname, sys.exc_info())

    def __del__(self):

        #print("__del__ lock", self.lockname)
        try:
            if fcntl:
                # Do not remove, others may have locked it
                if hasattr(self, "fpx"):
                    fcntl.flock(self.fpx, fcntl.LOCK_UN | fcntl.LOCK_NB)
                pass

            # Always remove file
            try:
                os.remove(self.lockname)
            except:
                pass
                #print("cannot delete lock", self.lockname, sys.exc_info())
        except:
            print("exc on del (ignored)", self.lockname, sys.exc_info())
            pass

# ------------------------------------------------------------------------
# This class will maintain a passwd database, similar to
#  the system database

class Passwd():

    def __init__(self):
        self.pgdebug = 0
        self.verbose = 0
        self.lock = FileLock(globals.passfile + ".lock")

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

    def listusers(self, umode):

        self.lock.waitlock()
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
        fh.close()
        userlist = []
        if not passdb:
            self.lock.unlock()
            return userlist

        for line in passdb:
            fields = line.split(",")
            fff = int(fields[1])
            #print(fields[:2])
            if umode == 0 and fff == 0:
                userlist.append(fields[0])
            elif fff & umode:
                userlist.append(fields[0])

        self.lock.unlock()
        return userlist

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
    #print("dl:", dl)
    if not dl:
        #print("No keys yet", keydir)
        raise (ValueError("No keys generated yet"))
    dust = random.randint(0, len(dl)-1)
    eee = os.path.splitext(os.path.basename(dl[dust]))
    #print("picking key", eee[0])
    return eee[0]

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

class SharedData():

    '''  Common space for mydata for remebering connecting client data.
    '''
    def __init__(self):

        if fcntl:
            # This is for forkmixin
            self.sem  = mp.Semaphore()
            self.man  = mp.Manager()
            self.mydata = self.man.dict()
        else:
            self.sem     = threading.Semaphore()
            self.mydata = {}

    def setdat(self, newkey, newdat):

        self.sem.acquire()
        try:
            self.mydata[newkey] = newdat
        except:
            print("setdat", sys.exc_info())
        self.sem.release()

    def getdat(self, key):

        self.sem.acquire()
        ddd = None
        try:
            ddd = self.mydata[key]
        except:
            print("getdat", self.man, self.sem, sys.exc_info())
        self.sem.release()

        return ddd

    def getall(self):

        self.sem.acquire()
        ddd = None
        try:
            ddd = self.mydata.copy()
        except:
            print("getall", sys.exc_info())
        self.sem.release()

        return ddd

    def deldat(self, keyx):

        self.sem.acquire()
        try:
            del self.mydata[keyx]
        except:
            print("deldat", sys.exc_info())
        self.sem.release()
        return

# ------------------------------------------------------------------------

class Throttle():

    '''  Catch clients that are connecting too fast. This needs a serious
        upgrade if in large volume production.
    '''
    def __init__(self):

        if fcntl:
            # This is for forkmixin
            self.sem  = mp.Semaphore()
            self.man  = mp.Manager()
            self.connlist = self.man.list()
            #self.enabled = self.man.list()
            #self.enabled.append(1)
            self.enabled = self.man.Value("i", 1)
        else:
            self.sem     = threading.Semaphore()
            self.connlist = []
            self.enabled = True

    def throttle(self, peer):

        '''
            Catch clients that are connecting too fast.
            Throttle to N sec frequency, if number of connections from
            the same ip exceeds throt_instances.
        '''

        wantsleep = 0; sss = 0;
        now = time.time()

        self.sem.acquire()
        # Throttle disabled, return zero delay
        if not self.enabled.value:
        #if not self.enabled[0]:
            self.sem.release()
            return 0

        # Calculate recents
        for aa in self.connlist:
            if aa[0] == peer[0]:
                if now - aa[1] <  globals.throt_sec:
                    sss += 1

        if sss >  globals.throt_instances:
            # Clean old entries for this host
            for aa in range(len(self.connlist)-1, -1 ,-1):
                if self.connlist[aa][0] == peer[0]:
                    if now - self.connlist[aa][1] > globals.throt_sec:
                        del self.connlist[aa]
            wantsleep = globals.throt_time

        # Clean throtle data periodically
        if len(self.connlist) > globals.throt_maxdat:
            #print("Cleaning throttle list", len(self.connlist))
            for aa in range(len(self.connlist)-1, -1 ,-1):
                if now - self.connlist[aa][1] > globals.throt_maxsec:
                    del self.connlist[aa]

        # Flatten list for the multiprocessing context manager
        self.connlist.append((peer[0], now))

        #print("connlist", self.connlist)  # Make sure it cycles
        #print()

        self.sem.release()
        return wantsleep

    def setflag(self, flag):

        ''' Enable / disable throttleing '''

        #print("setting flag", flag)

        self.sem.acquire()
        #self.enabled[0] = flag
        self.enabled.value = flag
        self.sem.release()

    def getflag(self):

        ''' report throttling status '''

        self.sem.acquire()
        #self.enabled[0] = flag
        ret = self.enabled.value
        self.sem.release()
        return ret

# The one and only instance
gl_throttle = Throttle()

bool_yes = [ "on", "yes", "true", "enable" ]
bool_no = [ "off", "no", "false", "disable" ]

def str2bool(strx, default = False):

    ''' Turn a string into a boolean value.
        If value is recognized, turn it. Otherwise assume passed default.
    '''

    boolx = -1
    strx = strx.lower()
    for aa in bool_yes:
        if strx == aa:
            boolx = True
            break
    if boolx == -1:
        for aa in bool_no:
            if strx == aa:
                boolx = False
                break
    # Response not found, default it
    if boolx == -1:
        boolx = default

    return boolx

if __name__ == '__main__':
    print( "This module was not meant to be used directly.")


# EOF