#!/usr/bin/env python

import os, sys, getopt, signal, select, string, time, stat 

sys.path.append('..')
sys.path.append('../bluepy')
import bluepy.bluepy

from common import support, pyservsup, pyclisup, syslog

# Globals

version = 1.0

# Ping pong state machine

# 1.) States

initial     = 0
auth_user   = 1
auth_pass   = 2
in_idle     = 3
got_fname   = 4
in_trans    = 5
got_file    = 6

# The commands in this state are allowed always
all_in       = 100
# The commands in this state are allowed in all states after auth
auth_in      = 110
# The commands in this state do not set new state
none_in      = 120

# ------------------------------------------------------------------------
# State transition and action functions

def get_lsd_func(self, strx):
    dname = ""; sss = ""
    try:
       dname = strx[1]; 
    except:
       pass
    dname2 = self.resp.cwd + "/" + self.resp.dir + "/" + dname
    dname2 = pyservsup.dirclean(dname2)
    try:
        ddd = os.listdir(dname2)
        for aa in ddd:
            if stat.S_ISDIR(os.stat(aa)[stat.ST_MODE]):
                # Escape spaces
                sss += pyservsup.escape(aa) + " "
        response = "OK " + sss
    except:
        #support.put_exception("lsd")
        response = "ERR " + str(sys.exc_info()[1] )
    self.resp.datahandler.putdata(response, self.resp.ekey)
    
def get_ls_func(self, strx):
    dname = ""; sss = ""
    try:
        dname = pyservsup.unescape(strx[1]); 
    except:
        pass   
    dname2 = self.resp.cwd + "/" + self.resp.dir + "/" + dname
    dname2 = pyservsup.dirclean(dname2)
    try:
        ddd = os.listdir(dname2)
        for aa in ddd:
            try:
                aaa = dname2 + "/" + aa
                if not stat.S_ISDIR(os.stat(aaa)[stat.ST_MODE]):
                    # Escape spaces
                    sss += pyservsup.escape(aa) + " "
            except:
                print( "Cannot stat ", aaa)
                
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
    dname2 = pyservsup.dirclean(dname2)
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
    syslog.syslog(xstr)
    
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
    dname2 = pyservsup.dirclean(dname2)
    if dname2 == "": dname2 = "/"
    response = "OK " +  dname2
    self.resp.datahandler.putdata(response, self.resp.ekey)
    
def get_ver_func(self, strx):
    response = "OK Version " + str(version)
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
            
        self.resp.dir = pyservsup.dirclean(self.resp.dir)
        dname2 = self.resp.cwd + "/" + self.resp.dir 
        dname2 = pyservsup.dirclean(dname2)
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
    if len(strx) == 1:
        self.resp.datahandler.putdata("ERR must specify user name", self.resp.ekey)
        return              
    self.resp.user = strx[1]
    self.resp.datahandler.putdata("OK Enter pass for '" + self.resp.user + "'", self.resp.ekey)
    
def get_pass_func(self, strx):
    ret = ""
    # Make sure there is a trace of the attempt
    stry = "Logon  '" + self.resp.user + "' " + \
                str(self.resp.client_address) 
    print( stry        )
    syslog.syslog(stry)
    if not os.path.isfile(pyservsup.passfile):
        ret = "ERR " + "No initial users yet"
    else:
        xret = pyservsup.auth(self.resp.user, strx[1])
        if xret[0] == 3:
            ret = "ERR No such user"
        elif xret[0] == 1:
            #self.resp.passwd = bluepy.bluepy.encrypt(strx[1], "1234")
            ret = "OK Authenticated"
            self.curr_state = in_idle
        else:
            stry = "Error on logon  '" + self.resp.user + "' " + \
                    str(self.resp.client_address) 
            print( stry        )
            syslog.syslog(stry)
            ret = "ERR " + xret[1]
    self.resp.datahandler.putdata(ret, self.resp.ekey)

def get_uadd_func(self, strx):
    if not os.path.isfile(pyservsup.passfile):
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
        response = "ERR must connect from loopback for uni"
    elif len(strx) < 3:
        response = "ERR must specify user name and pass"
    else:
        # See if there is a password file
        if os.path.isfile(pyservsup.passfile):
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
    if not os.path.isfile(pyservsup.passfile):
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
    syslog.syslog(xstr)
    self.resp.datahandler.putdata("OK Got data", self.resp.ekey)
            
def get_help_func(self, strx):
    #print( "get_help_func", strx)
    hstr = "OK "
    if len(strx) == 1:
        for aa in state_table:
            hstr += aa[0] + " "
    else:
        for aa in state_table:
            if strx[1] == aa[0]:
                hstr = "OK " + aa[4]
                break
        if hstr == "OK ":
            hstr = "ERR no help for command '" + strx[1] + "'"
            
    self.resp.datahandler.putdata(hstr, self.resp.ekey)
    
# Also stop timeouts
def get_exit_func(self, strx):
    #print( "get_exit_func", strx)
    self.resp.datahandler.putdata("OK Bye", self.resp.ekey)
    
    # Cancel **after** sending bye
    if self.resp.datahandler.tout: 
        self.resp.datahandler.tout.cancel()
    return True

def get_tout_func(self, strx):

    tout = self.resp.datahandler.timeout
    if len(strx) > 1:
        tout = int(strx[1])
        self.resp.datahandler.timeout = tout
        
    if self.resp.datahandler.tout: 
        self.resp.datahandler.tout.cancel()
        
    self.resp.datahandler.putdata("OK timeout set to " + str(tout), self.resp.ekey)
    return

# ------------------------------------------------------------------------
# Help stings

user_help = "Usage: user logon_name"
pass_help = "Usage: pass logon_pass"
file_help = "Usage: file fname -- Specify name for upload"
fget_help = "Usage: fget fname -- Download (get) file"
uadd_help = "Usage: uadd user_name user_pass -- Create new user"
kadd_help = "Usage: kadd key_name key_val -- Add new encryption key"
uini_help = "Usage: uini user_name user_pass -- Create initial user. "\
                "Must be from local net."
kini_help = "Usage: kini key_name key_pass -- Create initial key. " \
                "Must be from local net."
udel_help = "Usage: udel user_name user_pass -- Delete user"
data_help = "Usage: data datalen -- Specify length of file to follow"
vers_help = "Usage: ver -- Get protocol version. alias: vers"
hello_help = "Usage: hello -- Say Hello - test connectivity."
quit_help = "Usage: quit -- Terminate connection. alias: exit"
help_help = "Usage: help [command] -- Offer help on command"
lsls_help = "Usage: ls [dir] -- List files in dir"
lsls_help = "Usage: lsd [dir] -- List dirs in dir"
lsld_help = "Usage: help command -- Offer help on command"
cdcd_help = "Usage: cd dir -- Change to dir. Capped to server root"
pwdd_help = "Usage: pwd -- Show current dir"
stat_help = "Usage: stat fname  -- Get file stat. Field list:\n"\
"   1.  ST_MODE Inode protection mode.\n"\
"   2.  ST_INO Inode number.\n"\
"   3.  ST_DEV Device inode resides on.\n"\
"   4.  ST_NLINK  Number of links to the inode.\n"\
"   5.  ST_UID User id of the owner.\n"\
"   6.  ST_GID Group id of the owner.\n"\
"   7.  ST_SIZE Size in bytes of a plain file.\n"\
"   8.  ST_ATIME Time of last access.\n"\
"   9.  ST_MTIME Time of last modification.\n"\
"   10. ST_CTIME Time of last metadata change."
tout_help = "Usage: tout new_val -- Set / Reset timeout in seconds"
ekey_help = "Usage: ekey encryption_key -- Set encryption key "
xxxx_help = "Usage: no data"

# ------------------------------------------------------------------------
# Table driven server state machine.
# The table is searched for a mathing start_state, and the corresponding 
# function is executed. The new state set to end_state

state_table = [
            # Command ; start_state ; end_state ; action function
            ("user",    initial,    auth_pass,  get_user_func,  user_help),
            ("pass",    auth_pass,  none_in,    get_pass_func,  pass_help),
            ("file",    in_idle,    got_fname,  get_fname_func, file_help),
            ("fget",    in_idle,    in_idle,    get_fget_func,  fget_help),
            ("data",    got_fname,  in_idle,    get_data_func,  data_help),
            ("ekey",    all_in,     none_in,    get_ekey_func,  ekey_help),
            ("xkey",    all_in,     none_in,    get_xkey_func,  ekey_help),
            ("uadd",    auth_in,    none_in,    get_uadd_func,  uadd_help),
            ("kadd",    auth_in,    none_in,    get_kadd_func,  kadd_help),
            ("uini",    all_in,     none_in,    get_uini_func,  uini_help),
            ("kini",    all_in,     none_in,    get_kini_func,  kini_help),
            ("udel",    auth_in,    none_in,    get_udel_func,  udel_help),
            ("ver",     all_in,     none_in,    get_ver_func,   vers_help),
            ("vers",    all_in,     none_in,    get_ver_func,   vers_help),
            ("hello",   initial,    none_in,    get_hello_func, hello_help),
            ("quit",    all_in,     none_in,    get_exit_func,  quit_help),
            ("exit",    all_in,     none_in,    get_exit_func,  quit_help),
            ("help",    all_in,     none_in,    get_help_func,  help_help),
            ("ls",      auth_in,    none_in,    get_ls_func,    lsls_help),
            ("lsd",     auth_in,    none_in,    get_lsd_func,   lsld_help),
            ("cd",      auth_in,    none_in,    get_cd_func,    cdcd_help),
            ("pwd",     auth_in,    none_in,    get_pwd_func,   pwdd_help),
            ("stat",    auth_in,    none_in,    get_stat_func,  stat_help),
            ("tout",    auth_in,    none_in,    get_tout_func,  tout_help),
            ]
# ------------------------------------------------------------------------

class StateHandler():

    def __init__(self, resp):
        # Fill in class globals 
        self.curr_state = initial
        self.resp = resp
        self.resp.fname = ""
        self.resp.user = ""
        self.resp.cwd = os.getcwd()
        self.resp.dir = ""
        self.resp.ekey = ""
        syslog.openlog("pyserv.py")
    
    # --------------------------------------------------------------------
    # This is the function where outside stimulus comes in.
    # All the workings of the state protocol are handled here.
    # Return True from handlers to signal session terminate request

    def run_state(self, strx):
        try:
            self.run_state2(strx)
        except:
            support.put_exception("run state:")
            #print( sys.exc_info())
            
    def run_state2(self, strx):
        got = False; ret = True 
        
        # If encrypted, process it
        if self.resp.ekey != "":
            ddd  = strx.encode("cp437")
            strx2 = bluepy.bluepy.decrypt(ddd, self.resp.ekey)
            bluepy.bluepy.destroy(ddd)
            strx = strx2
            
        comx = strx.split()
        if self.verbose:
            print( "Com:", comx, "State =", self.curr_state)
        
        # Scan the state table, execute actions, set new states
        for aa in state_table:
            # See if command is in state or all_in is in effect
            # or auth_in and stat > auth is in effect -- use early out
            cond = aa[1] == self.curr_state
            if not cond:
                cond = cond or (aa[1] == auth_in and self.curr_state >= in_idle) 
            if not cond:
                cond = cond or aa[1] == all_in
            if cond:
                if comx[0] == aa[0]:
                    # Execute relevant function
                    ret = aa[3](self, comx)
                    # Only set state if not all_in / auth_in
                    if aa[2] != none_in:
                        self.curr_state = aa[2]
                    got = True
                    break
                    
        # Not found in the state table for the current state, complain
        if not got: 
            print( "Invalid or out of sequence command:", strx)
            sss =  "ERR Invalid or Out of Sequence command " + strx
            self.resp.datahandler.putdata(sss.encode("cp437"), self.resp.ekey)
            # Do not quit, just signal the error
            ret = False
        return ret          
    
# EOF



