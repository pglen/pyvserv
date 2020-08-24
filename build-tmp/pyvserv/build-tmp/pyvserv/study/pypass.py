#!/usr/bin/env python

import os, crypt, getpass, pwd, spwd, sys

# ------------------------------------------------------------------------
# Authenticate from local file

def auth(userx, upass):

    pname = "passwd"; fields = ""; dup = False
    upass2 = crypt.crypt(upass)
    try:
        fh = open(pname, "r")
    except:
        ret = "Cannot open " + pname
        return ret
            
    passdb = fh.readlines()
    for line in passdb:
        fields = line.split(",")
        if fields[0] == userx:
            dup = True
            break
    if not dup:
        fh.close()
        try:
            fh2 = open(pname, "w+")
        except:
            try:
                fh2 = open(pname, "w+")
            except:
                ret = "Cannot open " + pname + " for writing"
                return ret
        fh2.seek(0, os.SEEK_END)
        fh2.write(userx + "," + upass2 + "\n")                
        fh2.close()
        ret = "Saved pass"
    else:
        c2 = crypt.crypt(upass, fields[1])
        if c2 == fields[1].rstrip():
            ret = "Authenicated"
        else:
            ret = "Bad Pass"
    fh.close()
    return ret
        
# ------------------------------------------------------------------------
if __name__ == '__main__':

    try:
        userx     = sys.argv[1]
        passx    = sys.argv[2]
    except:
        print "usage: pypass.py user_name pass_word"
        sys.exit(0)    
        
    print auth(userx, passx)
        


