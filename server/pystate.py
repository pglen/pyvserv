#!/usr/bin/env python

from __future__ import print_function

from Crypto.Hash import SHA512
import os, sys, getopt, signal, select, string, time, stat

sys.path.append('..')
sys.path.append('../bluepy')
import bluepy.bluepy

sys.path.append('../common')
import support, pyservsup, pyclisup, crysupp, pysyslog

from pysfunc import *

# Ping pong state machine

# 1.) States

initial     = 0
auth_user   = 1
auth_akey   = 2
auth_key    = 3
auth_sess   = 4
auth_pass   = 5
in_idle     = 6
got_fname   = 7
in_trans    = 8
got_file    = 9

# The commands in this state are allowed always
all_in       = 100
# The commands in this state are allowed in all states after auth
auth_in      = 110
# The commands in this state do not set new state
none_in      = 120


# Also stop timeouts
def get_exit_func(self, strx):
    #print( "get_exit_func", strx)
    self.resp.datahandler.putdata("OK Bye", self.resp.ekey)
    #self.resp.datahandler.par.shutdown(socket.SHUT_RDWR)

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

user_help  = "Usage: user logon_name"
akey_help  = "Usage: akey -- get asymmetric key"
pass_help  = "Usage: pass logon_pass"
file_help  = "Usage: file fname -- Specify name for upload"
fget_help  = "Usage: fget fname -- Download (get) file"
uadd_help  = "Usage: uadd user_name user_pass -- Create new user"
kadd_help  = "Usage: kadd key_name key_val -- Add new encryption key"
uini_help  = "Usage: uini user_name user_pass -- Create initial user. "\
                "Must be from local net."
kini_help  = "Usage: kini key_name key_pass -- Create initial key. " \
                "Must be from local net."
udel_help  = "Usage: udel user_name user_pass -- Delete user"
data_help  = "Usage: data datalen -- Specify length of file to follow"
vers_help  = "Usage: ver -- Get protocol version. alias: vers"
hello_help = "Usage: hello -- Say Hello - test connectivity."
quit_help  = "Usage: quit -- Terminate connection. alias: exit"
help_help  = "Usage: help [command] -- Offer help on command"
lsls_help  = "Usage: ls [dir] -- List files in dir"
lsls_help  = "Usage: lsd [dir] -- List dirs in dir"
lsld_help  = "Usage: help command -- Offer help on command"
cdcd_help  = "Usage: cd dir -- Change to dir. Capped to server root"
pwdd_help  = "Usage: pwd -- Show current dir"
stat_help  = "Usage: stat fname  -- Get file stat. Field list:\n"\
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
tout_help  = "Usage: tout new_val -- Set / Reset timeout in seconds"
ekey_help  = "Usage: ekey encryption_key -- Set encryption key "
sess_help  = "Usage: sess session data -- Set session key "
xxxx_help  = "Usage: no data"

# ------------------------------------------------------------------------
# Table driven server state machine.
# The table is searched for a mathing start_state, and the corresponding
# function is executed. The new state set to end_state

state_table = [
            # Command ; start_state ; end_state ; action func   ; help func
            ("user",    initial,    auth_pass,  get_user_func,  user_help),
            ("pass",    auth_pass,  none_in,    get_pass_func,  pass_help),
            ("akey",    initial,    auth_key,   get_akey_func,  akey_help),
            ("xkey",    all_in,     none_in,    get_xkey_func,  ekey_help),
            ("ekey",    all_in,     none_in,    get_ekey_func,  ekey_help),
            ("sess",    initial,    auth_sess,  get_sess_func,  sess_help),
            ("file",    in_idle,    got_fname,  get_fname_func, file_help),
            ("fget",    in_idle,    in_idle,    get_fget_func,  fget_help),
            ("data",    got_fname,  in_idle,    get_data_func,  data_help),
            ("uadd",    auth_in,    none_in,    get_uadd_func,  uadd_help),
            ("kadd",    auth_in,    none_in,    get_kadd_func,  kadd_help),
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
            #("uini",    all_in,     none_in,    get_uini_func,  uini_help),
            #("kini",    all_in,     none_in,    get_kini_func,  kini_help),
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
        pysyslog.openlog("pyserv.py")

    # --------------------------------------------------------------------
    # This is the function where outside stimulus comes in.
    # All the workings of the state protocol are handled here.
    # Return True from handlers to signal session terminate request

    def run_state(self, strx):
        ret = None
        #print("Run state: '" + strx + "'")
        try:
            ret = self._run_state(strx)
        except:
            support.put_exception("in run state:")
            #print( sys.exc_info())
        return ret

    def _run_state(self, strx):
        got = False; ret = True

        # If encrypted, process it
        if self.resp.ekey != "":
            #ddd  = strx.encode("cp437")
            ddd  = strx
            strx2 = bluepy.bluepy.decrypt(ddd, self.resp.ekey)
            bluepy.bluepy.destroy(ddd)
            strx = strx2

        comx = strx.split()
        if self.verbose:
            print( "Line: '"+ strx + "'")
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
            #self.resp.datahandler.putdata(sss.encode("cp437"), self.resp.ekey)
            self.resp.datahandler.putdata(sss, self.resp.ekey)
            # Do not quit, just signal the error
            ret = False
        return ret

# EOF















