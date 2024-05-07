#!/usr/bin/env python

import sys, os, atexit

try:
    import readline
except:
    pass

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

# ------------------------------------------------------------------------
# Test client for the pyserv project.

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

# This repairs the path from local run to pip run.
try:
    from pyvcommon import support
    base = os.path.dirname(os.path.realpath(support.__file__))
    sys.path.append(os.path.join(base, "."))
except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    from pyvcommon import support

from pyvcommon import support, pycrypt, pyclisup
from pyvcommon import pysyslog, comline

__doc__ = \
''' Test unit for pyvserv. Command line interpreter. This interface is similar
    to the FTP client interface. Some functions are sent through directly,
    and some functions are interpreted via client helpers.
    All encryption functionality is exercised as the real client would.
    The command that starts with the exclamation point is executed
    in the local shell.

    ## The following commands (and more) may be issued.

    ### Type 'help' for a complete list

        user login_name                 -- Name of user to log in with
        akey                            -- Get asymmetric key
        pass login_pass                 -- Password
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
# Globals

version = "1.0.0"
progn = os.path.basename(sys.argv[0])
# ------------------------------------------------------------------------

__doc__ = '''\
The pyvserv command line client.
Usage: %s [options] [hostname]
  hostname: host to connect to. (default: 127.0.0.1)
  options:  -d level  - Debug level 0-10
            -p        - Port to use (default: 6666)
            -l login  - Login Name; default: 'user'
            -s lpass  - Login Pass; default: '1234' !!For tests Only!!
            -t        - Prompt for pass
            -x comm   - Execute command and quit
            -q        - Quiet
            -v        - Verbose
            -V        - Print version number
            -h        - Help
Prefix local commands with '!' (exclamation mark) ''' \
 % (progn)

def phelp():
    ''' Provide local help '''
    print(__doc__)
    sys.exit(0)

def pversion():

    ''' Print version string '''

    print(progn, "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function

optarr = \
    ["d:",  "pgdebug=",  "pgdebug",   0,          None],      \
    ["p:",  "port=",     "port",      6666,       None],      \
    ["l:",  "login=",    "login",     "admin",    None],      \
    ["s:",  "lpass=",    "lpass",     "1234",     None],      \
    ["x:",  "comm=",     "comm",      "",         None],      \
    ["t",   "prompt",    "prompt",    0,          None],      \
    ["v",   "verbose",   "verbose",   0,          None],      \
    ["q",   "quiet",     "quiet",     0,          None],      \
    ["V",   "verbose",   "vervose",   None,       pversion],  \
    ["h",   "help",      "help",      None,       phelp]      \

conf = comline.ConfigLong(optarr)

# ------------------------------------------------------------------------

def mainfunct():

    ''' Command line interpreter '''

    try:
        args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print("comline:", sys.exc_info())
        support.put_exception("comline")
        sys.exit(1)

    pyclisup.verbose = conf.verbose
    pyclisup.pgdebug = conf.pgdebug

    def soft_terminate(arg2, arg3):
        print("Ctrl-c pressed, exiting ...")
        sys.exit(0)

    if conf.prompt:
        signal.signal(signal.SIGINT, soft_terminate)
        import getpass
        strx = getpass.getpass("Enter Pass: ")
        if not strx:
            print("Aborting ...")
            sys.exit(0)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        conf.lpass  = strx

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

    atexit.register(pyclisup.atexit_func, hand, conf)

    resp3 = hand.client(["ver",] , "", False)
    if conf.verbose:
        print("Ver  Resp: ", resp3)

    conf.sess_key = ""
    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        sys.exit(0)

    if conf.verbose:
        resp3 = hand.client(["hello", ],  conf.sess_key, False)
        print("Hello Resp:", resp3)

    cresp = hand.login(conf.login, conf.lpass, conf)
    if cresp[0] != "OK":
        print("Error on login, exiting.", cresp)
        sys.exit(1)

    if conf.verbose:
        print ("Login resp:", cresp)

    # Start a new session for the rest of the work
    resp3 = hand.start_session(conf)
    if resp3[0] != "OK":
        print("Error on setting session:", resp3[1])
        sys.exit(0)

    # Interactive, need more time
    hand.client(["tout", "10",], conf.sess_key)

    if conf.comm:
        import shlex
        #print("exec:", conf.comm)
        commx = shlex.split(conf.comm)
        if not conf.quiet:
            print("Issued:", commx)
        resp = hand.client([*commx], conf.sess_key)
        print("resp:  ", resp)
    else:
        if not conf.quiet:
            print ("Enter commands, Ctrl-C or Ctrl-D or 'quit' to exit.")
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
                    print ("fget response:", ret2)
                    continue

                elif ss[0] == "fput":
                    if len(ss) < 2:
                        print("Use: fput fname")
                        continue
                    ret2 = hand.putfile(ss[1], "", conf.sess_key)
                    print ("fput response:", ret2)
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
                    print ("resp:", cresp)
        except:
            print(sys.exc_info())
            break

if __name__ == '__main__':
    mainfunct()

# EOF
