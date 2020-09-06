#!/usr/bin/env python

from __future__ import print_function

import os, sys, string, time, traceback, bcrypt, random

# Globals and configurables

version = "1.0"

buffsize = 4096

class   Globals:

    def __init__(self):
        self._datadir   =  "/.pyvserv"
        self._keydir    =  "/.pyvserv"
        self._passfile  =  "/passwd.secret"
        self._keyfile   =  "/keys.secret"

globals = Globals()

#globals.dataroot = ""
#globals.script_home = ""

def _xjoin(iterx, charx):
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
        fh = open(keyfile, "r")
    except:
        try:
            fh = open(keyfile, "w+")
        except:
            return -1, "Cannot open / create key file " + keyfile + " for reading"
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
                fh2 = open(keyfile, "r+")
            except:
                try:
                    fh2 = open(keyfile, "w+")
                except:
                    return -1, "Cannot open / create " + keyfile + " for writing"
            try:
                fh2.seek(0, os.SEEK_END)
                fh2.write(namex + "," + keyx + "\n")
            except:
                fh2.close()
                return -1, "Cannot write to " + keyfile
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
            pname3 = keyfile + ".tmp"
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
                os.remove(keyfile)
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

#userflag = (
#        USER_AUTH = 0, USER_ADD = 1, USER_DEL = 2,
#)

def _chpass(passdb, userx, upass):

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
        line2 = _xjoin(fields, ",")
        fh3.write(line2)
    fh3.close()

    # Rename
    try:
        os.remove(globals.passfile)
        renok = True
    except:
        ret = 0, "Cannot remove " + globals.passfile
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
#
# Return negative for error
#        0 for user added
#        0 for bad user or bad pass
#        1 for user match
#        2 for duplicate
#        3 for no user
#        4 for user deleted
#        5 for user pass changed

def  auth(userx, upass, flags = 0, uadd = 0):

    fields = ""; dup = False
    try:
        fh = open(globals.passfile, "r")
    except:
        try:
            fh = open(globals.passfile, "w+")
        except:
            return -1, "Cannot open / create pass file " + globals.passfile

    passdb = fh.readlines()
    for line in passdb:
        fields = line.split(",")
        if fields[0] == userx:
            dup = True
            break
        fh.close()

    if not dup:
        if uadd == 1:
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
            ret = 2, "Saved pass"
        else:
            ret = 3, "No such user"
    else:
        if uadd == 3:
            ret = _chpass(passdb, userx, upass)

        elif uadd == 2:
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
            # Do not touch line 1
            fh3.write(passdb[0])
            for line in passdb[1:]:
                fields = line.split(",")
                if fields[0] == userx and (fields[1] and 0x1) != 0:
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
            try:
                os.rename(pname3, globals.passfile)
            except:
                ret = 0, "Cannot rename from " + pname3
                return ret
            if delok:
                ret = 4, "User deleted"
            else:
                ret = 0, "User NOT deleted (uini user)"
        else:
            c2 = bcrypt.hashpw(upass.encode("cp437"), fields[2].encode("cp437"))
            #print ("upass", c2, "org:", fields[2].rstrip().encode("cp437"))
            if c2 == fields[2].rstrip().encode("cp437"):
                #print ("Auth OK")
                ret = 1, "Authenicated"
            else:
                ret = 0, "Bad User or Bad Pass"
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











