#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time, traceback, bcrypt, random, uuid, datetime, base64

base = os.path.dirname(os.path.realpath(__file__))
#print("base", base)
sys.path.append(os.path.join(base, '../bluepy'))
sys.path.append(os.path.join(base, '../common'))
sys.path.append(os.path.join(base,  '../../pycommon'))

import support, pyclisup, crysupp, pysyslog, pystate

# Globals and configurables

version = "1.0"

USER_AUTH = 0; USER_ADD = 1; USER_DEL = 2; USER_CHPASS = 3; USER_CHMOD = 4;

PERM_NONE = 0; PERM_INI = 1; PERM_ADMIN = 2; PERM_DIS = 4; PERM_NON = 8;

RESET_MODE  = 0x80;

#buffsize = 1024;
buffsize = 4096;

class   Globals:

    def __init__(self):

        self._datadir   =  os.sep + ".pyvserv" + os.sep
        self._keydir    =  os.sep + "keys"
        self._privdir   =  os.sep + "private"
        self._paydir    =  os.sep + "payload"

        self._passfile  =  "passwd.secret"
        self._keyfile   =  "keys.secret"
        self._idfile    =  "pyservid.init"
        self.siteid     =  None
        self.throttle   =  10     # seconds
        self.instance   =  2      # max instace from one IP/host
        self.maxthdat   =  100    # max data in throttle var

    def _mkdir(self, ddd, fff="data"):
        try:
            if not os.path.isdir(ddd):
                os.mkdir(ddd)
        except:
            print( "Cannot make " + fff + " dir", sys.exc_info())
            sys.exit(1)

    # --------------------------------------------------------------------

    def config(self, realp, conf):

        #pyservsup.globals.script_home = os.path.dirname(os.path.realpath(__file__))
        self.script_home = realp

        self.script_home += os.sep + ".." + os.sep + "data" + os.sep
        self.script_home = os.path.realpath(self.script_home)

        self.verbose = conf.verbose
        self.pgdebug = conf.pgdebug

        if conf.verbose:
            print("Script home:     ", self.script_home)

        if conf.pgdebug:
                print ("Debug level:     ", conf.pgdebug)

        self.datadir = self.script_home + self._datadir

        self.lockfname = self.datadir + "lockfile"
        self.passfile = self.datadir + self._passfile
        self.keyfile = self.datadir + self._keyfile
        self.idfile = self.datadir + self._idfile

        self.keydir = self.script_home + self._keydir
        self.paydir = self.script_home + self._paydir

        self._mkdir(self.script_home, "Script Home")
        self._mkdir(self.datadir, "Data dir")
        self._mkdir(self.paydir, "Payload dir")


globals = Globals()

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
            yyy = base64.b64encode(xxx.encode("cp437"))

            fp3 = open(fname + ".backup", "w+")
            fp3.write("# Server ID backup as Base64 of the two NL terminated UUIDs\n")
            fp3.write("# ID created on: " + str(nnn) + "\n\n")
            fp3.write("-------- BASE64 BEG --------\n" +
                        yyy.decode("cp437") +
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
# This class will maintain a passwd database, similar to
#  the system database

class Passwd():

    def __init__(self):
        self.pgdebug = 0
        self.verbose = 0

    def     _xjoin(self, iterx, charx):
        sss = ""
        try:
            for aa in iterx:
                if sss != "":
                    sss += charx
                if type(aa) != str:
                    aa = aa.decode("cp437")
                sss += aa
        except:
            print(sys.exc_info())
        return sss

    def     _unlock(self):
        pname4 = globals.passfile + ".lock"
        try:
            os.unlink(pname4);
        except:
            print("Cannot unlock")
            pass

    def     _lock(self):
        pname4 = globals.passfile + ".lock"
        acc = False
        cnt = 0
        while (True):
            try:
                acc = os.access(pname4, R_OK)
            except:
                pass

            if not acc:
                try:
                    acc = open(pname4, "w+b")
                    acc.close()
                    break;
                except:
                    #print("Could not open lockfile", pname4)
                    #support.put_exception("open lockfile")
                    pass

            if cnt > 5:
                print("breaking lock")
                try:
                    os.unlink(pname4);
                except:
                    #print("Could not break lock")
                    pass

            if cnt > 7:
                #print("breaking lock crunch")
                break

            cnt += 1
            time.sleep(.3)


    def     _deluser(self, passdb, userx, upass):

        delok = 0
        # Delete userx
        pname3 = globals.passfile + ".tmp"
        try:
            fh3 = open(pname3, "r+")
        except:
            try:
                fh3 = open(pname3, "w+")
            except:
                ret = 0, "Cannot open " + pname3 + " for writing"
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
            fh3 = open(pname3, "r+")
        except:
            try:
                fh3 = open(pname3, "w+")
            except:
                ret = (0, "Cannot open " + pname3 + " for writing")
                return ret

        for line in passdb:
            fields = line.split(",")
            if fields[0] == userx:
                upass2 = bcrypt.hashpw(upass.encode("cp437"), bcrypt.gensalt())
                fields[2] = upass2
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

    def     _chmod(self, passdb, userx, umode):

        modeok = 0

        # Filter onto temp file
        pname3 = globals.passfile + ".tmp"
        try:
            fh3 = open(pname3, "r+")
        except:
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
    def count(self):

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

        self._lock()

        userx = support.escape(userx)

        fields = ""; haveusr = False
        try:
            fh = open(globals.passfile, "r")
        except:
            try:
                fh = open(globals.passfile, "w+")
            except:
                self._unlock()
                return -1, "Cannot open / create pass file " + globals.passfile

        passdb = fh.readlines()
        for line in passdb:
            fields = line.split(",")
            if fields[0] == userx:
                haveusr = True
                break
            fh.close()

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
                upass2 = bcrypt.hashpw(upass.encode("cp437"), bcrypt.gensalt())
                fh2.write(userx + "," + str(flags) + "," + upass2.decode("cp437") + "\n")
                fh2.close()
                ret = 2, "Saved user / pass"
            else:
                ret = 3, "No such user"
        else:
            if uadd == USER_CHPASS:
                ret = self._chpass(passdb, userx, upass)

            elif uadd == USER_CHMOD:
                #print("Change mode", hex(flags))
                ret = self._chmod(passdb, userx, flags)
                #if flags & RESET_MODE:
                #    ret = 8, "User disabled"
                #else:
                #    ret = 8, "User Enabled"

            elif uadd == USER_DEL:
                c2 = bcrypt.hashpw(upass.encode("cp437"), fields[2].encode("cp437"))
                #print ("upass", c2, "org:", fields[2].rstrip().encode("cp437"))
                if int(fields[1]) & PERM_INI == PERM_INI:
                    ret = 0, "Cannot delete uini user"
                elif c2 == fields[2].rstrip().encode("cp437"):
                    ret = self._deluser(passdb, userx, upass)
                else:
                    ret = 0, "Bad User or Bad Pass"

            elif uadd == USER_AUTH:
                c2 = bcrypt.hashpw(upass.encode("cp437"), fields[2].encode("cp437"))
                #print ("upass", c2, "org:", fields[2].rstrip().encode("cp437"))
                if c2 == fields[2].rstrip().encode("cp437"):
                    if self.verbose:
                        print ("Auth OK for ", userx)
                    ret = 1, "Authenicated "
                else:
                    ret = 0, "Bad User or Bad Pass"
            elif uadd == USER_ADD:
                ret = 6, "Cannot add, Duplicate User "
            else:
                ret = 0, "Bad auth command issued"

        self._unlock()
        return ret

    def     perms(self, userx):

        self._lock()

        fields = ""; haveusr = False
        try:
            fh = open(globals.passfile, "r")
        except:
            try:
                fh = open(globals.passfile, "w+")
            except:
                self._unlock()
                return -1, "Cannot open / create pass file " + globals.passfile

        passdb = fh.readlines()

        if not passdb:
            ret = 7, "User permissions:", 0
            self._unlock()
            return ret

        for line in passdb:
            fields = line.split(",")
            if fields[0] == userx:
                haveusr = True
                break
            fh.close()

        ret = 7, "User permissions:", fields[1]
        self._unlock()
        return ret

passwd = Passwd()

#print("created passwd global");

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

def kauth(namex, keyx, kadd = False):

    fields = ""; dup = False; ret = 0, ""
    try:
        fh = open(globals.keyfile, "r")
    except:
        try:
            fh = open(globals.keyfile, "w+")
        except:
            return -1, "Cannot open / create key file " + globals.keyfile + " for reading"
    keydb = fh.readlines()
    for line in keydb:
        fields = line.split(",")
        if namex == fields[0]:
            dup = True
            break
    if not dup:
        if kadd == 1:
            # Add
            fh.close()
            try:
                fh2 = open(globals.keyfile, "r+")
            except:
                try:
                    fh2 = open(globals.keyfile, "w+")
                except:
                    return -1, "Cannot open / create " + globals.keyfile + " for writing"
            try:
                fh2.seek(0, os.SEEK_END)
                fh2.write(namex + "," + keyx + "\n")
            except:
                fh2.close()
                return -1, "Cannot write to " + globals.keyfile
            fh2.close()
            ret = 0, "Key saved"
    else:
        if kadd == 0:
            ret = 1, fields[1].rstrip()
        elif kadd == 1:
            ret = 2, "Duplicate key"
        elif kadd == 2:
            # Delete key
            delok = 0
            pname3 = globals.keyfile + ".tmp"
            try:
                fh3 = open(pname3, "r+")
            except:
                try:
                    fh3 = open(pname3, "w+")
                except:
                    ret = 0, "Cannot open " + pname3 + " for writing"
                    return ret
            # Do not touch line 1
            fh3.write(keydb[0])
            for line in keydb[1:]:
                fields = line.split(",")
                if fields[0] == namex:
                    delok = 1
                    pass
                else:
                    fh3.write(line)
            fh3.close()
            # Rename
            try:
                os.remove(globals.keyfile)
            except:
                ret = -1, "Cannot remove from " + pname3
            try:
                os.rename(pname3, globals.passfile)
            except:
                ret = -1, "Cannot rename from " + pname3
                return ret
            if delok:
                ret = 4, "Key deleted"
            else:
                ret = -1, "Key NOT deleted (possibly kini key)"
        else:
            ret = -1, "Invalid opcode"
    return ret

# Return basename for key file

def pickkey(keydir):

    #print("Getting keys", keydir)
    dl = os.listdir(keydir)
    if dl == 0:
        print("No keys yet")
        raise (Valuerror("No keys generated yet"))

    dust = random.randint(0, len(dl)-1)
    eee = os.path.splitext(os.path.basename(dl[dust]))
    #print("picking key", eee[0])
    return eee[0]

if __name__ == '__main__':
    print( "test")


# EOF











