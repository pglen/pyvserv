#!/usr/bin/env python3

# Too many misc crappers like dyn properties
# pylint: disable=E1101
# pylint: disable=C0103
# pylint: disable=C0413
# pylint: disable=C0209
# pylint: disable=W0201
# pylint: disable=W0702     # Bare exceptions
# pylint: disable=W0602     # No global assignment

__doc__ = \
'''
Server module.
'''
import sys
import os
import getopt
import signal
import time
import subprocess
import platform
import socket
import threading
import tracemalloc
import datetime
#import distro

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

try:
    import fcntl
except ImportError:
    fcntl = None
except:
    print(sys.exc_info())

if sys.version_info[0] < 3:
    import SocketServer as socketserver
else:
    import socketserver

__doc__ = ''' <pre>\
The main pyvserv excutable.
Usage: pyvserv.py [options]
options: -n   --host      host     -  Set server hostname / interface.
         -r   --dataroot  droot    -  Set data root for server.
         -l   --loglevel  pglog    -  Log level (0 - 10) default = 1
         -d   --debug     pgdebug  -  Debug level 0-10
         -p   --port      port     -  Listen on port
         -v   --verbose            -  Verbose. Show more info.
         -q   --quiet              -  Quiet. Show less info.
         -V   --version            -  Print Version string
         -h   --help               -  Show Help. (this screen)
         -P   --pmode              -  Production mode ON. (allow 2FA)
         -t   --test               -  Test mode. Allow weak hash
Use quotes for multiple option strings. </pre>'''

progname = os.path.split(sys.argv[0])[1]

# This repairs the path from local run to pip run.
# Remove pip version for local tests
try:
    from pyvcommon import support

    # Get Parent of module root
    sf = os.path.dirname(support.__file__)
    sf = os.path.dirname(sf)
    #print("sf", sf)
    sys.path.append(os.path.join(sf, "pyvcommon"))
    sys.path.append(os.path.join(sf, "pyvserver"))
except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    from pyvcommon import support

from pyvcommon import support, pyservsup
from pyvcommon import pydata, pysyslog, comline

from pyvserver import pyvstate
from pyvserver import pyvfunc

# Create a placeholders

SHARED_MYDATA   = None
gl_server       = None
args            = None

# ------------------------------------------------------------------------

class InvalidArg(Exception):

    ''' Exception for bad arguments '''

    def __init__(self, message):
        super().__init__(self)  #InvalidArg, self)
        self.message = message

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    ''' Request handler. '''

    def __init__(self, a1, a2, a3):

        self.verbose = conf.verbose
        self.pgdebug = conf.pgdebug
        self.peer = a2
        self.fname = ""
        self.user = ""
        self.preuser = ""
        self.cwd = os.getcwd()
        self.dir = ""
        self.ekey = ""

        #print("a1", a1, "a2", a2, "a3", a3)

        # Throttle for multiple connectiond from one host
        ttt = pyservsup.gl_throttle.throttle(a1.getpeername())
        if ttt > 0:
            if self.pgdebug > 2:
                print("Throttle sleep",  a1.getpeername())
            time.sleep(ttt)

        socketserver.BaseRequestHandler.__init__(self, a1, a2, a3)

    def setup(self):

        ''' Start server '''

        global SHARED_MYDATA

        #print("thread", self)
        #print(dir(self))

        cur_thread = threading.current_thread()
        #print(dir(cur_thread))

        self.name  = str(cur_thread._native_id) #name #getName()
        #self.name  = cur_thread.name #getName()
        #print( "Logoff '" + usr + "'", cli)

        if self.verbose:
            print( "Connection from ", self.peer, "as", self.name)

        self.statehandler = pyvstate.StateHandler(self)
        self.statehandler.verbose   = conf.verbose
        self.statehandler.pglog     = conf.pglog
        self.statehandler.pgdebug   = conf.pgdebug
        self.statehandler.name      = self.name

        # Remeber globally, add to shared dicrtionary
        ddd = (os.getpid(), self.peer[0], self.peer[1],  self.request)

        if conf.pgdebug > 4:
            print("Adding mydata:", ddd)
        SHARED_MYDATA.setdat(self.name, ddd)

        self.datahandler            =  pydata.DataHandler(self.request)
        self.datahandler.pgdebug    = conf.pgdebug
        self.datahandler.pglog      = conf.pglog
        self.datahandler.verbose    = conf.verbose
        self.datahandler.par        = self

        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if conf.pglog > 0:
            pysyslog.syslog("Connected " + " " + str(self.client_address))

        response =  ["OK", "pyvserv %s ready" % pyservsup.VERSION, self.name]

        # Connected, acknowledge it
        self.datahandler.putencode(response, "")

    def handle_error(self, request, client_address):

        ''' Placeholder '''

        print("pyvserv Error", request, client_address)

    def handle(self):

        ''' Request comes in here '''

        if conf.mem:
            tracemalloc.start()
        try:
            while 1:
                ret = self.datahandler.handle_one(self)
                if not ret:
                    break
                ret2 = self.statehandler.run_state(ret)
                if ret2:
                    #response2 = ["err", "Too many tries, disconnecting."]
                    response2 = ["ERR", "Disconnected."]
                    self.datahandler.putencode(response2, self.statehandler.resp.ekey)
                    #time.sleep(.1)
                    #self.datahandler.par.request.shutdown(socket.SHUT_RDWR)
                    break
        except:
            #print( sys.exc_info())
            support.put_exception("state handler")

        if self.verbose:
            print( "Connection closed on", self.peer)

        if conf.mem:
            print( "Memory trace")
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            print("[ Top 10 ]")
            for stat in top_stats[:10]:
                print(stat)

        #if conf.pglog > 0:
        #    pysyslog.syslog("Disconn " + " " + str(self.client_address))

    def finish(self):

        ''' Wind down, remove globals '''

        global SHARED_MYDATA
        if conf.pgdebug > 4:
            ddd = SHARED_MYDATA.getdat(self.name)
            print("Removing mydata:", self.name, ddd)

        SHARED_MYDATA.deldat(self.name)
        if self.statehandler.resp.user:
            pyservsup.SHARED_LOGINS.deldat(self.statehandler.resp.user)

# ------------------------------------------------------------------------
# Override stock methods. Windows has no ForkinMixin

if not fcntl:
    mixin = socketserver.ThreadingMixIn
else:
    mixin = socketserver.ForkingMixIn

# Overriding it for throttle and cleanup development !! TEST !!
#mixin = socketserver.ThreadingMixIn

class ThreadedTCPServer(mixin, socketserver.TCPServer):

    ''' Overridden socket server '''

    #def __init__(self, arg1, arg2):
    #    self._BaseServer__shutdown_request = True

    def stop(self):
        ''' breakout '''

        self._BaseServer__shutdown_request = True

        if conf.verbose:
            print( "Stop called")

        #self.shutdown()
        #self.server_close()

def usersig1(arg1, arg2):

    ''' signal comes in here, list current clients '''

    global SHARED_MYDATA, gl_server
    if conf.pgdebug > 1:
        print("usersig", arg1)

    if conf.pgdebug > 6:
        print("usersig", arg1, arg2)

    if conf.pglog > 2:
        pysyslog.syslog("Got user signal %d" % arg1)

    print("Current clients:")
    print( SHARED_MYDATA.getall())

    print("Current logins:")
    ddd = pyservsup.SHARED_LOGINS.getall()
    if ddd:
        for aa in ddd.keys():
            dt = datetime.datetime.fromtimestamp(ddd[aa])
            print("Login:", "'" + aa + "'", "Login time:", dt)

def usersig2(arg1, arg2):

    ''' respond to user signaal '''

    if conf.pgdebug > 1:
        print("usersig2", arg1)

    if conf.pgdebug > 6:
        print("usersig2", arg1, arg2)

    if conf.pglog > 2:
        pysyslog.syslog("Got user signal2 %d" % arg1)

    print("Current configuration:")
    print("Full server path:    ", pyservsup.globals.script_home)
    print("Data root:           ", pyservsup.globals.myhome)
    print("Pass Dir:            ", pyservsup.globals.passdir)
    print("Key Dir:             ", pyservsup.globals.keydir)
    print("Payload Dir:         ", pyservsup.globals.paydir)
    print("Blockchain Dir:      ", pyservsup.globals.chaindir)
    print("Log dir:             ", pyservsup.globals.logdir)
    print("Temp dir:            ", pyservsup.globals.tmpdir)
    print("Lockfile:            ", pyservsup.globals.lockfname)
    print("IDfile:              ", pyservsup.globals.idfile)
    print("Current operationals:")
    print("Server hostname:     ", pyservsup.globals.conf.host)
    print("Port listening on:   ", pyservsup.globals.conf.port)
    print("Debug level:         ", pyservsup.globals.conf.pgdebug)
    print("Verbose:             ", pyservsup.globals.conf.verbose)
    print("Loglevel:            ", pyservsup.globals.conf.pglog)
    print("Production Mode:     ", pyservsup.globals.conf.pmode)

def soft_terminate(arg1 = 0, arg2 = 0):

    # pylint: disable=unused-argument

    ''' Terminate app. Did not behave as expected ... fixed. '''

    if conf.pgdebug > 1:
        print("   soft_terminate")

    if conf.pgdebug > 1:
        print( "Dumping connection info:")
        ddd = SHARED_MYDATA.getall()
        for aa in ddd.keys():
            print(os.getpid(), ddd[aa])

    terminate() #0, 0)

# ------------------------------------------------------------------------

def terminate(arg1 = 0, arg2 = 0):

    ''' Terminate app.  Wind down all sockets. Free locks. '''

    # pylint: disable=unused-argument
    global SHARED_MYDATA, gl_server

    # Attempt to unhook all pending clients
    #print( "Closing active clients:")
    pid = os.getpid()
    ddd = SHARED_MYDATA.getall()
    if ddd:
        for aa in ddd.keys():
            if conf.pgdebug > 5:
                print( "Shared data:", ddd[aa])
            if pid == ddd[aa][0]:
                if conf.pgdebug > 1:
                    print( "Closing connection:", ddd[aa])
                try:
                    ddd[aa][3].shutdown(socket.SHUT_RDWR)
                    ddd[aa][3].close()
                except:
                    print("exc on close conn", sys.exc_info())

    if conf.pglog > 0:
        pysyslog.syslog("Terminated Server" )

    support.unlock_process(pyservsup.globals.lockfname)

    if not conf.quiet:
        print( "Terminated", progname)

    sys.exit(2)

# ------------------------------------------------------------------------
# Execute one server cycle

# pylint: disable=too-few-public-methods

class serve_one():

    ''' Simplified server for testing. Kept in case we want to
        temporarily revert.
    '''
    def __init__(self, *argx):
        self.cnt = 0
        self.fname = ""
        self.user = ""
        self.cwd = os.getcwd()
        self.dir = ""
        self.ekey = ""
        self.argx = argx
        server_thread = threading.Thread(target=self.run)
        server_thread.start()
        self.verbose = False
        self.argx = argx
        self.name = ""
        self.statehandler = None
        self.datahandler =  None

    def run(self, argx):

        ''' run '''

        self.client, self.client_address, self.args = argx
        cur_thread = threading.current_thread()
        self.name = cur_thread.name #getName()
        #print( "Logoff '" + usr + "'", cli)

        self.verbose = conf.verbose

        if self.verbose:
            print("Started thread", self.name)

        if self.verbose:
            print( "Connection from ", self.a2, "as", self.name)

        #if pgdebug > 1:
        #    put_debug("Connection from %s" % self.a2)

        self.statehandler = pyvstate.StateHandler(self)
        self.statehandler.verbose = conf.verbose
        self.statehandler.pglog = conf.pglog
        self.statehandler.pgdebug = conf.pgdebug

        #if conf.verbose:
        #    print("Connected " + " " + str(self.client_address))

        self.datahandler =  pydata.DataHandler(self.client)
        self.datahandler.pgdebug = conf.pgdebug
        self.datahandler.pglog = conf.pglog
        self.datahandler.verbose = conf.verbose
        self.datahandler.par = self

        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if conf.pglog > 0:
            pysyslog.syslog("Connected ", str(self.client_address))

        response =  ["OK", "pyvserv %s ready" % pyservsup.VERSION]
        # Connected, acknowledge it
        self.datahandler.putencode(response, "")

        try:
            while 1:
                ret = self.datahandler.handle_one(self)
                if not ret:
                    break
                ret2 = self.statehandler.run_state(ret)
                if ret2:
                    #response2 = ["err", "Too many tries, disconnecting."]
                    response2 = ["ERR", "Disconnected."]
                    self.datahandler.putencode(response2, self.statehandler.resp.ekey)
                    break
        except:
            #print( sys.exc_info())
            support.put_exception("state handler")

        if conf.mem:
            #print( "Memory trace")
            #snapshot = tracemalloc.take_snapshot()
            #top_stats = snapshot.statistics('lineno')
            pass

        if self.verbose:
            print("ended thread", self.name)

def simple_server(Host, Port):

    ''' This was a test server, left it in for future refernence.
        It was marginally faster than the stock version, also less features,
         so the stock servers stayed.
    '''

    global args

    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((Host, Port))
        server.listen()
        while True:
            client, addr = server.accept()
            client.setsockopt(socket.IPPROTO_TCP,
                            socket.TCP_NODELAY, 1)
            serve_one(client, addr, args)

# ------------------------------------------------------------------------

# Tue 02.Apr.2024 made devmode default

optarr =  []
optarr.append ( ["n:",  "hostname=",     "host",   "127.0.0.1",
            None, "Set server interface name."] )
optarr.append ( ["r:",  "dataroot=", "droot",  "pyvserver",
            None, "Set data root. default:~/pyvserver "] )
optarr.append ( ["l:",  "loglevel=", "pglog",       1,
            None, "Log level. 0=none 10=noisy default=1"] )

optarr += comline.optarrlong

optarr.append ( ["m",   "mem",       "mem",         0,
                                None, "Show memory trace. (For testing only.)"] )
optarr.append ( ["P",   "pmode",     "pmode",       0,
                            None, "Production mode ON. (allow 2FA)"] )

optarr.append ( ["t",   "test",     "test",       0,
                            None, "Test mode. Allow weak hash."] )

#optarr.append ( ["N",   "norepl",    "norepl",      0,
#                            None, "No replication. (for testing)"] )

comline.sethead("The main pyvserv excutable.")
#comline.setprog(os.path.basename(sys.argv[0]))
comline.setprog(os.path.basename(__file__) + " [options] ")
comline.setargs("[options]")
#comline.setfoot("Use quotes for multiple option strings.")

conf = comline.ConfigLong(optarr)
#conf.printvars()

def do_keys():
    ''' breakout '''
    try:
        #keyfroot =
        pyservsup.pickkey(pyservsup.globals.keydir)
    except:
        if conf.pgdebug > 4:
            print("Could pick keys", sys.exc_info())
        if conf.pgdebug > 5:
            support.put_exception("pick keys")

        #print("No keys generated yet. Please run pyvgenkey.py first.")
        print("Notice: Generating key in", "'" + pyservsup.globals.keydir + "'")
        execx = os.path.dirname(pyservsup.globals.script_home) + os.sep
        execx += "../pyvtools/pyvgenkey.py"
        try:
            if conf.pgdebug > 4:
                print("Generating keys", execx)
            # Try local
            if os.path.isfile(execx):
                rrr = [execx, "-q", "-m", pyservsup.globals.myhome]
                with subprocess.Popen(rrr):
                    pass
            else:
                # Try with full install version ... executable
                execx = "pyvgenkey"
                rrr = [execx, "-q", "-m", pyservsup.globals.myhome]
                with subprocess.Popen(rrr):
                    pass
        except:
            if conf.pgdebug > 4:
                print("Could not exec", sys.exc_info())
            if conf.pgdebug > 5:
                support.put_exception("generate keys")
            print("Could not generate key. Keydir was:", pyservsup.globals.keydir)
            print("Please try again manually with the 'pvgenkey' utility.")
        print("For added security please generate more keys with 'pyvgenkeys'")

def print_stats():

    ''' breakout '''
    if conf.verbose:
        print("Serve exe path:  ", pyservsup.globals.script_home)
        print("Data root:       ", pyservsup.globals.myhome)
        print("Pass Dir:        ", pyservsup.globals.passdir)
        print("Key Dir:         ", pyservsup.globals.keydir)
        print("Payload Dir:     ", pyservsup.globals.paydir)
        print("Lock file:       ", pyservsup.globals.lockfname)
        print("ID file:         ", pyservsup.globals.idfile)
        #print("Passfile:        ", pyservsup.globals.passfile)

def start_server():

    ''' breakout '''
    global gl_server
    try:
        gl_server = ThreadedTCPServer((conf.host, conf.port), ThreadedTCPRequestHandler)
        gl_server.allow_reuse_address = True
        #ip, port = server.server_address
        gl_server.verbose = conf.verbose

        # Start a thread with the server -- that thread will then start one
        # or more threads for each request
        server_thread = threading.Thread(target=gl_server.serve_forever)

        # Exit the server thread when the main thread terminates
        server_thread.verbose = conf.verbose
        server_thread.daemon = True
        #server_thread.paydir =  pyservsup.globals.paydir
        server_thread.start()

    except:
        print( "Cannot start server. ", sys.exc_info())
        if conf.pglog > 0:
            pysyslog.syslog("Cannot start server ", sys.exc_info())
            #print("Try again later.")
            #terminate(None, None)
            sys.exit(1)

def signon_message():

    ''' message for the terminal '''

    if not conf.quiet:
        if not pyservsup.globals.conf.pmode:
            print("Warning! DevMode  ON. Use -P to allow 2FA auth")
        if pyservsup.globals.conf.test:
            print("Warning! TestMode ON. Weak hashes are allowed")

        # Sat 04.May.2024 Dropped the distro, so can be installed on pipx
        #try:
        #    strx = distro.name()
        #except:
        #    strx = "Win or Unkn."

        print("MainSiteID:      ", pyservsup.globals.siteid)
        print("Server running: ", "'"+conf.host+"'", "Port:", conf.port)
        #pyver = support.list2str(sys.version_info) #[0:3], ".")
        print("Running python", platform.python_version(), "on", platform.system())

def set_sigs():

    '''  set up signal handlers '''
    # Set termination handlers, so lock will be deleted
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, soft_terminate)
    try:
        signal.signal(signal.SIGUSR1, usersig1)
        signal.signal(signal.SIGUSR2, usersig2)
    except:
        print("User signals may not be available.")

    sys.stdout = support.Unbuffered(sys.stdout)
    sys.stderr = support.Unbuffered(sys.stderr)

def mainfunct():

    ''' Main entry point. The pip install will call this script. '''

    global args

    if sys.version_info[0] < 3:
        print("This script was meant for python 3.x")
        time.sleep(.1)
        sys.exit(0)
    try:
        args = conf.comline(sys.argv[1:])
    except getopt.GetoptError:
        sys.exit(1)
    except SystemExit:
        sys.exit(0)
    except:
        print(sys.exc_info())
        sys.exit(1)
    #print(args)

    # Print comline args
    #if conf.pgdebug > 7:
    #    for aa in vars(conf):
    #        if aa != "_optarr":
    #            print(aa, "=", getattr(conf, aa), end = "    ")
    #    print()

    #if conf.pgdebug > 4:
    #    print("This script:     ", os.path.realpath(__file__))
    #    print("Full path argv:  ", os.path.abspath(sys.argv[0]))
    #    print("Script name:     ", __file__)
    #    print("Exec argv:       ", sys.argv[0])

    # Just for testing
    #pyservsup.pgdebug = conf.pgdebug
    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf
    pyservsup.globals.lockfname += "_" + str(conf.host) +  "_" + str(conf.port)
    pyservsup.globals.softmkdir(pyservsup.globals.myhome)

    # Change directory to the data dir
    os.chdir(pyservsup.globals.myhome)
    if conf.verbose:
        print("cwd", os.getcwd())

    # Create support objects
    pyservsup.globals.config(pyservsup.globals.myhome, conf)
    pyservsup.gl_passwd = pyservsup.Passwd()

    # This is out of process, but create a 'vote' chain directory
    # As testing will create it ... no harm
    Vd = os.path.join(pyservsup.globals.chaindir, "vote")
    pyservsup.globals.softmkdir(Vd)

    print_stats()
    do_keys()

    set_sigs()

    # Comline processed, go
    support.lock_process(pyservsup.globals.lockfname)

    pyvfunc.pgdebug = conf.pgdebug
    pyvfunc.pglog = conf.pglog

    slogfile = os.path.join(pyservsup.globals.logdir, pyservsup.logfname + ".log")
    rlogfile = os.path.join(pyservsup.globals.logdir, pyservsup.repfname +".log")

    pysyslog.init_loggers(
            ("system", slogfile), ("replic", rlogfile))
    #pysyslog.syslog("Started Server")

    signon_message()
    pyvstate.init_state_table()

    global SHARED_MYDATA
    SHARED_MYDATA = pyservsup.SharedData()
    pyservsup.SHARED_LOGINS = pyservsup.SharedData()

    start_server()

    if conf.pglog > 0:
        pysyslog.syslog("Server started. Prodmode %d" % conf.pmode)

    # Block
    gl_server.serve_forever()

if __name__ == '__main__':
    mainfunct()

# EOF
