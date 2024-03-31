#!/usr/bin/env python

import sys, os, readline, atexit

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

__doc__ = \
''' Test unit for pyvserv. Command line interpreter. This interface is similar
    to the FTP client interface. Some functions are sent through directly,
    and some functions are interpreted via client helpers.
    All encryption functionality is exercised as the real client would.
    The command that starts with the exclamation point is executed
    in the local shell.

## The following commands (and more) may be issued.

        user logon_name                 -- Name of user to log in with
        akey                            -- Get asymmetric key
        pass logon_pass                 -- Password
        chpass newpass                  -- Change pass (not tested)
        file fname                      -- Specify name for upload
        fget fname                      -- Download (get) file
        fput fname                      -- Upload (put) file
        del  fname                      -- Delete file
        uadd user_name user_pass        -- Create new user
        kadd key_name key_val           -- Add new encryption key
        uini user_name user_pass        -- Create initial user. Must be from local net.
        kini key_name key_pass          -- Create initial key.  Must be from local net.
        uena user_name  flag            -- Enable / disable user
        aadd user_name user_pass        -- Create admin user
        udel user_name                  -- Delete user
        data datalen                    -- Specify length of file to follow
        ver                             -- Get protocol version. alias: vers
        id                              -- Get site id string
        hello                           -- Say Hello - test connectivity.
        quit                            -- Terminate connection. alias: exit
        help [command]                  -- Offer help on command
        ls [dir]                        -- List files in dir
        lsd [dir]                       -- List dirs in dir
        cd dir                          -- Change to dir. Capped to server root
        pwd                             -- Show current dir
        stat fname                      -- Get file stat. See at the end of this table.
        tout new_val                    -- Set / Reset timeout in seconds
        ekey encryption_key             -- Set encryption key
        sess session data               -- Start session
        buff buff_size                  -- Limited to 64k
        rput header, field1, field2...  -- Put record in blockcain. See example code.
        rget header                     -- Get record from blockcain.
        qr                              -- Get qrcode image for 2fa
        twofa                           -- Two factor authentication
        dmode                           -- Get dmode (Developer Mode) flag
        ihave                           -- The 'i have you have' protocol entry point
        ihost                           -- Add / delete replicator host

'''

# ------------------------------------------------------------------------
# Test client for the pyserv project. Download file.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

from pyvcli_utils import *

from pyvcommon import support, pycrypt, pyclisup
from pyvcommon import pysyslog, comline

# ------------------------------------------------------------------------
# Globals

version = 1.0

# ------------------------------------------------------------------------

def phelp():

    ''' Provide local help '''

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 9999)")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -n        - No encryption (plain)")
    print( "            -h        - Help")
    print()
    sys.exit(0)

def pversion():

    ''' Print version string '''

    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
optarr = \
    ["d:",  "pgdebug",  0,      None],      \
    ["p:",  "port",     6666,   None],      \
    ["v",   "verbose",  0,      None],      \
    ["q",   "quiet",    0,      None],      \
    ["V",   None,       None,   pversion],  \
    ["h",   None,       None,   phelp]      \

conf = comline.Config(optarr)

# ------------------------------------------------------------------------

def mainfunct():

    ''' Command line interpreter '''

    args = conf.comline(sys.argv[1:])

    #print(vars(conf))

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    if len(args) == 0:
        ip = '127.0.0.1'
    else:
        ip = args[0]

    hand = pyclisup.CliSup()
    hand.verbose = conf.verbose
    hand.pgdebug = conf.pgdebug

    try:
        respc = hand.connect(ip, conf.port)
    except:
        print( "Cannot connect to:", ip + ":" + str(conf.port), sys.exc_info()[1])
        sys.exit(1)

    atexit.register(atexit_func, hand, conf)

    #resp3 = hand.client(["id",] , "", False)
    #print("ID Response:", resp3[1])

    conf.sess_key = ""
    #ret = ["OK",];  conf.sess_key = ""
    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        sys.exit(0)

    # Make a note of the session key
    #print("Sess Key ACCEPTED:",  resp3[1])

    if conf.sess_key:
        print(" ------ Post session, session key:", conf.sess_key[:12], "...")

    resp3 = hand.client(["hello", ],  conf.sess_key, False)
    print("Hello Resp:", resp3)

    # Session estabilished, try a simple command
    #resp4 = hand.client(["hello",], conf.sess_key)
    #print("Hello Response:", resp4[1])

    cresp = hand.login("admin", "1234", conf)
    print ("Login resp:", cresp)

    # Start a new session for the rest of the work
    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        sys.exit(0)

    if conf.sess_key:
        print(" ------ Post session, session key:", conf.sess_key[:12], "...")

    resp3 = hand.client(["hello", ],  conf.sess_key, False)
    print("Hello2 Resp:", resp3)

    # Interactive, need more time
    hand.client(["tout", "30",], conf.sess_key)

    print ("Enter commands, Ctrl-C or 'done' to quit. Prefix local commands with '!'")

    mainloop(conf, hand)

    sys.exit(0)


def mainloop(conf, hand):

    ''' Loop through commands and provide interpretation / execution on
    a line by line basis.
    '''
    cresp = ""
    while(True):
        try:
            onecom = input(">> ")
            #print ("'" + onecom.split() + "'")
            ss = onecom.split()
            if ss  != []:

                # process commands that need additional data

                if ss[0] == "quit":
                    break
                elif ss[0] == "sess":
                    cresp = hand.start_session(conf)
                    if conf.sess_key:
                        print("Post session, session key:", conf.sess_key[:12], "...")

                elif ss[0] == "fget":
                    if len(ss) < 2:
                        print("Use: fget fname")
                        continue
                    ret2 = hand.getfile(ss[1], ss[1] + "_local", conf.sess_key)
                    print ("Server fget response:", ret2)
                    continue

                elif ss[0] == "fput":
                    if len(ss) < 2:
                        print("Use: fput fname")
                        continue
                    ret2 = hand.putfile(ss[1], "", conf.sess_key)
                    print ("Server fput response:", ret2)
                    continue

                elif ss[0] == "file":
                    if not os.path.isfile(ss[1]):
                        print("File must exist.")
                        continue
                    cresp = hand.start_session(conf)
                    if conf.sess_key:
                        print("Post session, session key:", conf.sess_key[:12], "...")
                    continue

                elif ss[0][0] == "!":
                    #print ("local command")
                    os.system(ss[0][1:] + " " + " ".join(ss[1:]))
                    continue
                else:
                    # No wrapper needed
                    cresp = hand.client(ss, conf.sess_key)
                    # post process
                    print ("Server response:", cresp)
        except:
            print(sys.exc_info())
            break

if __name__ == '__main__':
    mainfunct()
