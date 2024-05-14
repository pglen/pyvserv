#!/usr/bin/env python

from __future__ import print_function

from Crypto.Hash import SHA512
import os, sys, getopt, signal, select, string, time, stat, base64
import inspect, multiprocessing

try:
    import fcntl
except:
    fcntl = None

import pyvpacker

import pyservsup, pyclisup, support
import crysupp, pysyslog, pywrap

from pyvfunc import *

# Ping pong state machine

# 1.) States

initial     = 0
auth_akey   = 1
auth_sess   = 2
auth_user   = 3
auth_key    = 4
auth_pass   = 5
auth_twofa  = 6
in_idle     = 7
got_fname   = 8
in_trans    = 9
got_file    = 10

# The commands in this state are allowed always
all_in       = 100

# The commands in this state are allowed in all states after auth
auth_in      = 110

# The commands in this state do not set new state
none_in      = 120

# ------------------------------------------------------------------------
# Help stings

usage = "Usage:"
user_help   = usage + " user logon_name -- set session user name"
akey_help   = usage + " akey -- get asymmetric key"
pass_help   = usage + " pass logon_pass -- password"
chpass_help = usage + " chpass user  oldpass, newpass"
file_help   = usage + " file fname -- Specify name for upload"
mkdir_help  = usage + " mkdir dirname -- Specify name for new dir"
rmdir_help  = usage + " rmdir dirname -- Specify dir name to delete"
fget_help   = usage + " fget fname -- Download (get) file"
fput_help   = usage + " fput fname -- Upload (put) file"
del_help    = usage + " del  fname -- Delete file"
uadd_help   = usage + " uadd user_name user_pass -- Create new user"
uini_help   = usage + " uini user_name user_pass -- Create initial user. Loopback only."
uena_help   = usage + " uena user_name  flag -- enable / disable user"
ulist_help  = usage + " ulist flag  -- list users. Flag: user / admin / initial / disabled"
aadd_help   = usage + " aadd user_name user_pass -- create admin user"
udel_help   = usage + " udel user_name -- Delete user"
data_help   = usage + " data datalen -- Specify length of file to follow"
vers_help   = usage + " ver -- Get server version."
id_help     = usage + " id -- Get site id string"
hello_help  = usage + " hello -- Say Hello - test connectivity."
quit_help   = usage + " quit -- Terminate connection. alias: exit"
exit_help   = usage + " exit -- Terminate connection. alias: quit"
help_help   = usage + " help [command] -- Offer help on command"
lsls_help   = usage + " ls [dir] -- List files in dir"
lsld_help   = usage + " lsd [dir] -- List dirs in dir"
cdcd_help   = usage + " cd dir -- Change to dir. Capped to server root"
pwdd_help   = usage + " pwd -- Show current dir"
tout_help   = usage + " tout [val] -- Get / Set timeout value. (seconds)"
ekey_help   = usage + " ekey encryption_key -- Set encryption key "
sess_help   = usage + " sess session data -- Start session "
logout_help = usage + " logout -- log out user"
buff_help   = usage + " buff buff_size -- limited to 64k"
throt_help  = usage + " throt flag -- turn on or off throttling"
rput_help   = usage + " rcheck kind link | sum -- check records. Link check or sum check"
rtest_help  = usage + " rtest link | sum recids -- check a list of records. Link check or sum check"
rcheck_help = usage + " rput kind header, [field1, field2] ... -- put record in blockchain."
rlist_help  = usage + " rlist kind beg_date end_date -- get records from blockchain."
rcount_help = usage + " rcount kind beg_date end_date -- get record count from blockchain."
rsize_help  = usage + " rsize kind -- get total record count from blockchain."
rget_help   = usage + " rget kind header -- get record from blockchain."
rabs_help   = usage + " rabs kind pos -- get record by absolute position from blockchain."
rhave_help  = usage + " rhave kind header -- is record in blockchain."
qr_help     = usage + " qr -- get QR code image for 2fa"
twofa_help  = usage + " twofa pass -- two factor authentication credentials"
dmode_help  = usage + " dmode -- get current dmode (Developer Mode) flag"
ihost_help  = usage + " ihost -- add / del / list 'host:port' replicator host."
stat_help   = usage + " stat fname  -- Get file stat"
xxxx_help   = usage + " no data -- Template for new help"

# ------------------------------------------------------------------------
# Table driven server state machine.
# The table is searched for a mathing start_state, and the corresponding
# function is executed. The new state set to end_state

def init_state_table():

    ''' Initialize state table '''

    #print("pystate init table")
    global state_table

    # This is to develop without entering auth code every time
    if not pyservsup.globals.conf.pmode:
        minauth =  auth_pass
    else:
        minauth =  auth_twofa

    state_table = \
    [
        # Command; start_state; end_state; min_auth; action func;  help func
        ("ver",     all_in,  none_in,    initial,   get_ver_func,     vers_help),
        ("id",      all_in,  none_in,    initial,   get_id_func,      id_help),
        ("hello",   all_in,  none_in,    initial,   get_hello_func,   hello_help),
        ("helo",    all_in,  none_in,    initial,   get_hello_func,   hello_help),
        ("quit",    all_in,  none_in,    initial,   get_exit_func,    quit_help),
        ("exit",    all_in,  none_in,    initial,   get_exit_func,    exit_help),
        ("help",    all_in,  none_in,    initial,   get_help_func,    help_help),
        ("akey",    all_in,  none_in,    initial,   get_akey_func,    akey_help),
        ("uini",    all_in,  none_in,    initial,   get_uini_func,    uini_help),
        ("user",    all_in,  none_in,    initial,   get_user_func,    user_help),
        ("pass",    all_in,  auth_pass,  initial,   get_pass_func,    pass_help),
        ("logout",  all_in,  initial,    auth_pass, get_lout_func,    logout_help),
        ("sess",    all_in,  none_in,    initial,   get_sess_func,    sess_help),
        ("tout",    all_in,  none_in,    initial,   get_tout_func,    tout_help),
        ("qr",      all_in,  none_in,    initial,   get_qr_func,      qr_help),
        ("chpass",  all_in,  none_in,    auth_pass, get_chpass_func,  chpass_help),
        ("file",    all_in,  none_in,    auth_pass, put_file_func,    file_help),
        ("mkdir",   all_in,  none_in,    auth_pass, get_mkdir_func,   mkdir_help),
        ("rmdir",   all_in,  none_in,    auth_pass, get_rmdir_func,   rmdir_help),
        ("data",    all_in,  none_in,    auth_pass, put_data_func,    data_help),
        ("fget",    all_in,  none_in,    auth_pass, get_fget_func,    fget_help),
        ("fput",    all_in,  none_in,    auth_pass, get_fput_func,    fput_help),
        ("del",     all_in,  none_in,    auth_pass, get_del_func,     del_help),
        ("uadd",    all_in,  none_in,    auth_pass, get_uadd_func,    uadd_help),
        ("udel",    all_in,  none_in,    auth_pass, get_udel_func,    udel_help),
        ("uena",    all_in,  none_in,    auth_pass, get_uena_func,    uena_help),
        ("ulist",   all_in,  none_in,    auth_pass, get_ulist_func,   ulist_help),
        ("aadd",    all_in,  none_in,    auth_pass, get_aadd_func,    aadd_help),
        ("ls",      all_in,  none_in,    auth_pass, get_ls_func,      lsls_help),
        ("dir",     all_in,  none_in,    auth_pass, get_ls_func,      lsls_help),
        ("lsd",     all_in,  none_in,    auth_pass, get_lsd_func,     lsld_help),
        ("cd",      all_in,  none_in,    auth_pass, get_cd_func,      cdcd_help),
        ("pwd",     all_in,  none_in,    auth_pass, get_pwd_func,     pwdd_help),
        ("stat",    all_in,  none_in,    auth_pass, get_stat_func,    stat_help),
        ("buff",    all_in,  none_in,    auth_pass, get_buff_func,    buff_help),
        ("throt",   all_in,  none_in,    auth_pass, get_throt_func,   throt_help),
        ("twofa",   all_in,  auth_twofa, auth_pass, get_twofa_func,   twofa_help),
        ("dmode",   all_in,  none_in,    initial,   get_dmode_func,   dmode_help),
        ("ihost",   all_in,  none_in,    initial,   get_ihost_func,   ihost_help),
        ("rlist",    all_in,  none_in,   auth_pass, get_rlist_func,   rlist_help),
        ("rcount",   all_in,  none_in,   auth_pass, get_rcount_func,  rcount_help),
        ("rsize",    all_in,  none_in,   auth_pass, get_rsize_func,   rsize_help),
        ("rget",     all_in,  none_in,   auth_pass, get_rget_func,    rget_help),
        ("rabs",     all_in,  none_in,   auth_pass, get_rabs_func,    rabs_help),
        ("rhave",    all_in,  none_in,   auth_pass, get_rhave_func,   rhave_help),
        #("rtest",    all_in,  none_in,   auth_pass, get_rtest_func, rtest_help),

        # The two factor auth commands. 2FA not required during development
        ("rput",     all_in,  none_in,   minauth,   get_rput_func,   rput_help),
        ("rcheck",   all_in,  none_in,   minauth,   get_rcheck_func, rcheck_help),
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
        self.pb = pyvpacker.packbin()
        self.wr.pgdebug = 0
        self.buffsize = pyservsup.buffsize
        self.lockname = "lock.lock"
        self.fpx = None

    def waitlock(self):
        while True:
            if os.path.isfile(self.lockname):
                time.sleep(1)
            else:
                break
        try:
            self.fpx = open(self.lockname, "wb")
            if fcntl:
                fcntl.lockf(self.fpx, fcntl.LOCK_EX)
        except:
            print(sys.exc_info())
            pass

    def dellock(self):
        if fcntl:
            fcntl.lockf(self.fpx, fcntl.LOCK_EX)
        try:
            self.fpx.close()
            os.unlink(self.lockname)
        except:
            print(sys.exc_info())
            pass

    # --------------------------------------------------------------------
    # This is the function where outside stimulus comes in.
    # All the workings of the state protocol are handled here.
    # Return True from handlers to signal session terminate request

    def run_state(self, strx):

        # ------------------------------------------------------
        ret = False
        try:
            ret = self._run_state_worker(strx)
        except:
            #print("last:", support.exc_last())
            support.put_exception("run state() = " + str(self.curr_state) + ":")
            sss =  [ERR, "on processing request.", str(sys.exc_info()[1]), ]
            self.resp.datahandler.putencode(sss, self.resp.ekey)
            ret = False
        # ------------------------------------------------------

        return ret

    def _run_state_worker(self, strx):
        got = False; ret = False

        #if self.pgdebug > 8:
        #    print( "Incoming strx: \n", crysupp.hexdump(strx, len(strx)))

        dstr = ""
        try:
            dstr = self.wr.unwrap_data(self.resp.ekey, strx)
        except:
            support.put_exception("While in _run state(): "\
                                         + str(self.curr_state))
            sss =  ERR, "cannot unwrap / decode data." #, strx
            #print("pyvstate.py %s" % (sss,));
            self.resp.datahandler.putencode(sss, self.resp.ekey)
            return False

        if self.pgdebug > 6:
            #print( "Incoming data:")
            for aa in dstr[1]:
                print("Incoming:", aa)

        comx = dstr[1] #.split()

        if self.pgdebug > 3:
            print( "Com:", "'" + comx[0] + "'", "State =", self.curr_state)

        got = False; comok = False

        # Scan the state table, execute actions, set new states
        for aa in state_table:
            # Command match
            if comx[0] == aa[0]:
                comok = True
                #if self.pgdebug > 3:
                #    print("Found command, executing:", aa[0])

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
                        if aa[3] <= self.curr_state:
                            #print(aa[0], self.curr_state)
                            # Execute relevant function
                            ret2 = aa[4](self, comx)
                            #print("exec", ret2, aa[3], comx[0])
                            # Only set state if not all_in / auth_in
                            if not ret2 and aa[2] != none_in:
                                self.curr_state = aa[2]
                            got = True
                            if comx[0] == "pass":
                                if ret2:
                                    self.badpass += 1
                            elif comx[0] == "twofa":
                                if ret2:
                                    self.badpass += 1
                            else:
                                # Non pass command can terminate
                                ret = ret2

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
            self.resp.datahandler.putencode(sss, self.resp.ekey)
            # Do not quit, just signal the error
            ret = False
        return ret

    def __del(self):
        print("del state handler")
# EOF
