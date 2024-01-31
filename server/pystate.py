#!/usr/bin/env python

from __future__ import print_function

from Crypto.Hash import SHA512
import os, sys, getopt, signal, select, string, time, stat, base64
import inspect

import common.pyservsup as pyservsup, common.pyclisup as pyclisup
import common.support as support
import common.crysupp as crysupp, common.pysyslog as pysyslog
import common.pypacker as pypacker, common.pywrap as pywrap

import bluepy.bluepy as bluepy

from pysfunc import *

# Ping pong state machine

# 1.) States

initial     = 0
auth_akey   = 1
auth_sess   = 2
auth_user   = 3
auth_key    = 4
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

# ------------------------------------------------------------------------
# Help stings

user_help   = "Usage: user logon_name"
akey_help   = "Usage: akey -- get asymmetric key"
pass_help   = "Usage: pass logon_pass"
chpass_help = "Usage: chpass newpass"
file_help   = "Usage: file fname -- Specify name for upload"
fget_help   = "Usage: fget fname -- Download (get) file"
fput_help   = "Usage: fput fname -- Upload (put) file"
del_help    = "Usage: del  fname -- Delete file"
uadd_help   = "Usage: uadd user_name user_pass -- Create new user"
kadd_help   = "Usage: kadd key_name key_val -- Add new encryption key"
uini_help   = "Usage: uini user_name user_pass -- Create initial user. "\
                "Must be from local net."
kini_help  = "Usage: kini key_name key_pass -- Create initial key. " \
                "Must be from local net."
uena_help  = "Usage: uena user_name  flag --  enable / disable user"
aadd_help  = "Usage: aadd user_name user_pass -- create admin user"
udel_help  = "Usage: udel user_name -- Delete user"
data_help  = "Usage: data datalen -- Specify length of file to follow"
vers_help  = "Usage: ver -- Get protocol version. alias: vers"
id_help    = "Usage: id -- Get site id string"
hello_help = "Usage: hello -- Say Hello - test connectivity."
quit_help  = "Usage: quit -- Terminate connection. alias: exit"
help_help  = "Usage: help [command] -- Offer help on command"
lsls_help  = "Usage: ls [dir] -- List files in dir"
lsld_help  = "Usage: lsd [dir] -- List dirs in dir"
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
sess_help  = "Usage: sess session data -- Start session "
buff_help  = "Usage: buff buff_size -- limited to 64k"
xxxx_help  = "Usage: no data"

# ------------------------------------------------------------------------
# Table driven server state machine.
# The table is searched for a mathing start_state, and the corresponding
# function is executed. The new state set to end_state

state_table = [
    # Command; start_state; end_state; min_auth; action func;   help func
    ("ver",     all_in,     none_in,    none_in,  get_ver_func,   vers_help),
    ("id",      all_in,     none_in,    none_in,  get_id_func,    id_help),
    ("hello",   all_in,     none_in,    none_in,  get_hello_func, hello_help),
    ("helo",    all_in,     none_in,    none_in,  get_hello_func, hello_help),
    ("quit",    all_in,     none_in,    none_in,  get_exit_func,  quit_help),
    ("exit",    all_in,     none_in,    none_in,  get_exit_func,  quit_help),
    ("help",    all_in,     none_in,    none_in,  get_help_func,  help_help),
    ("xkey",    all_in,     none_in,    none_in,  get_xkey_func,  ekey_help),
    ("ekey",    all_in,     none_in,    none_in,  get_ekey_func,  ekey_help),
    ("akey",    all_in,     none_in,    none_in,  get_akey_func,  akey_help),
    ("tout",    all_in,     none_in,    none_in,  get_tout_func,  tout_help),
    ("uini",    auth_sess,  none_in,    none_in,  get_uini_func,  uini_help),
    ("kadd",    auth_in,    none_in,    none_in,  get_kadd_func,  kadd_help),
    ("user",    all_in,     auth_user,  none_in, get_user_func,  user_help),
    ("pass",    auth_user,  auth_pass,  none_in, get_pass_func,  pass_help),
    ("sess",    all_in,     auth_sess,  none_in,  get_sess_func,  sess_help),
    ("chpass",  all_in,  none_in,    auth_pass, get_chpass_func,  chpass_help),
    ("file",    all_in,  got_fname,  auth_pass, put_file_func, file_help),
    ("mkdir",   all_in,  none_in,    auth_pass, get_mkdir_func, file_help),
    ("data",    all_in,  none_in,    auth_pass, put_data_func,  data_help),
    ("fget",    all_in,  none_in,    auth_pass, get_fget_func,  fget_help),
    ("fput",    all_in,  none_in,    auth_pass, get_fput_func,  fput_help),
    ("del",     all_in,  none_in,    auth_pass, get_del_func,   del_help),
    ("uadd",    all_in,  none_in,    auth_pass, get_uadd_func,  uadd_help),
    ("uena",    all_in,  none_in,    auth_pass, get_uena_func,  uena_help),
    ("aadd",    all_in,  none_in,    auth_pass, get_aadd_func,  aadd_help),
    ("udel",    all_in,  none_in,    auth_pass, get_udel_func,  udel_help),
    ("ls",      all_in,  none_in,    auth_pass, get_ls_func,    lsls_help),
    ("lsd",     all_in,  none_in,    auth_pass, get_lsd_func,   lsld_help),
    ("cd",      all_in,  none_in,    auth_pass, get_cd_func,    cdcd_help),
    ("pwd",     all_in,  none_in,    auth_pass, get_pwd_func,   pwdd_help),
    ("stat",    all_in,  none_in,    auth_pass, get_stat_func,  stat_help),
    ("buff",    all_in,  none_in,    auth_pass, get_buff_func,  buff_help),
    ]
# ------------------------------------------------------------------------

class StateHandler():

    def __init__(self, resp):
        # Fill in class globals
        self.curr_state = initial
        self.resp = resp
        self.resp.fh = None
        self.badpass = 0
        self.wr = pywrap.wrapper()
        self.pb = pypacker.packbin()

        self.wr.pgdebug = 0

    # --------------------------------------------------------------------
    # This is the function where outside stimulus comes in.
    # All the workings of the state protocol are handled here.
    # Return True from handlers to signal session terminate request

    def run_state(self, strx):
        ret = None

        #if self.pgdebug > 5:
        #    print("Run state data: \n'" + crysupp.hexdump(strx, len(strx)) + "'")

        try:
            ret = self._run_state(strx)
        except:
            support.put_exception("While in run state(): " + str(self.curr_state))
            sss =  "ERR on processing request."
            self.resp.datahandler.putdata(sss, self.resp.ekey)
            ret = False
        return ret

    def _run_state(self, strx):
        got = False; ret = False

        if self.pgdebug > 8:
            print( "Incoming strx: \n", crysupp.hexdump(strx, len(strx)))

        dstr = ""
        try:
            dstr = self.wr.unwrap_data(self.resp.ekey, strx)
            #dstr = self.wr.unwrap_data("", strx)
        except:
            sss =  "ERR cannot unwrap / decode data." #, strx
            #support.put_exception("While in _run state(): " + str(self.curr_state))
            print("pystate.py %s" % (sss,));
            self.resp.datahandler.putdata(sss, self.resp.ekey)
            return False

        if self.pgdebug > 3:
            print( "Incoming Line: \n", dstr)

        comx = dstr[1] #.split()

        if self.pgdebug > 3:
            print( "Com:", "'" + comx[0] + "'", "State =", self.curr_state)

        got = False; comok = False

        # Scan the state table, execute actions, set new states
        for aa in state_table:
            # Command match
            if comx[0] == aa[0]:
                comok = True
                if self.pgdebug > 3:
                    print("Found command, executing:", aa[0])

                # See if command is in state or all_in is in effect
                # or auth_in and stat > auth is in effect -- use early out
                if aa[3] == none_in or aa[3] <= self.curr_state:
                    cond = aa[1] == self.curr_state
                    if not cond:
                        cond = aa[1] == auth_in and self.curr_state >= in_idle
                    if not cond:
                        cond = aa[1] == all_in

                    if cond:
                        # Auth?
                        authx = aa[3] >= self.curr_state
                        if not authx:
                            authx = aa[3] == none_in
                        if authx:
                            # Execute relevant function
                            ret2 = aa[4](self, comx)
                            #print("exec", ret2, aa[3], comx[0])
                            # Only set state if not all_in / auth_in
                            if not ret2 and aa[2] != none_in:
                                self.curr_state = aa[2]
                            got = True
                            ret = ret2
                            if comx[0] == "pass" and ret2:
                                self.badpass += 1
                            if self.badpass > 2:
                                ret = True
                break

        # Not found in the state table for the current state, complain
        if not got:
            #print( "Invalid command or out of sequence command ", "'" + comx[0] + "'")
            if not comok:
                sss =  ["ERR", "Invalid command issued",  comx[0]]
            else:
                sss =  ["ERR", "Out of Sequence command issued", comx[0]]
            #self.resp.datahandler.putdata(sss.encode("cp437"), self.resp.ekey)
            self.resp.datahandler.putencode(sss, self.resp.ekey)
            # Do not quit, just signal the error
            ret = False
        return ret

# EOF
