#!/usr/bin/env python3

from __future__ import print_function

import sys

if sys.version_info[0] < 3:
    print("Python 2 is not supported as of 1/1/2020")
    sys.exit(1)

import os, getopt, signal, select, string, time
import tarfile, subprocess, struct, platform
import socket, threading, tracemalloc, inspect

if sys.version_info[0] < 3:
    import SocketServer as socketserver
else:
    import socketserver

#base = os.path.dirname(os.path.realpath(__file__))
##print("base", base)
#current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parent_dir = os.path.dirname(current_dir)
#sys.path.insert(0, parent_dir)
##print("pd", parent_dir)

# getting the name of the directory
current = os.path.dirname(os.path.realpath(__file__))
# Getting the parent directory name
parent = os.path.dirname(current)
sys.path.append(parent)

#sys.path.append(os.path.join(base, '../bluepy'))
#sys.path.append(os.path.join(base, '../common'))
#sys.path.append(os.path.join(base,  '../../pycommon'))

import pystate, support, pyservsup, pyclisup
import pysyslog, pydata, comline, pysfunc

# Globals
detach = False
verbose = False
quiet  = False
version = "1.0"

mydata = {}

# ------------------------------------------------------------------------

class InvalidArg(Exception):

    def __init__(self, message):
         self.message = message

# ------------------------------------------------------------------------

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, a1, a2, a3):
        self.a2 = a2
        self.fname = ""
        self.user = ""
        self.cwd = os.getcwd()
        self.dir = ""
        self.ekey = ""

        #print("init", a1, a2, a3)
        socketserver.BaseRequestHandler.__init__(self, a1, a2, a3)
        #print(  SocketServer)

    def setup(self):
        global mydata

        cur_thread = threading.current_thread()
        self.name = cur_thread.name #getName()
        #print( "Logoff '" + usr + "'", cli)

        self.verbose = conf.verbose

        if self.verbose:
            print( "Connection from ", self.a2, "as", self.name)

        #if pgdebug > 1:
        #    put_debug("Connection from %s" % self.a2)

        self.statehandler = pystate.StateHandler(self)
        self.statehandler.verbose = conf.verbose
        self.statehandler.pglog = conf.pglog
        self.statehandler.pgdebug = conf.pgdebug

        self.datahandler =  pydata.DataHandler()
        self.datahandler.pgdebug = conf.pgdebug
        self.datahandler.pglog = conf.pglog
        self.datahandler.verbose = conf.verbose
        self.datahandler.par = self

        mydata[self.name] = self

        #if conf.verbose:
        #    print("Connected " + " " + str(self.client_address))

        if conf.pglog > 0:
            pysyslog.syslog("Connected " + " " + str(self.client_address))
        response =  ["OK", "pyvserv %s ready" % version]
        # Connected, acknowledge
        self.datahandler.putencode(response, "")

    def handle_error(request, client_address):
        print("pyvserv Error", request, client_address)

    def handle(self):

        if conf.mem:
            tracemalloc.start()
        try:
            while 1:
                ret = self.datahandler.handle_one(self)
                if not ret: break
                ret2 = self.statehandler.run_state(ret)
                if ret2:
                    response2 = ["err", "Too many tries, disconnecting."]
                    self.datahandler.putencode(response2, self.statehandler.resp.ekey)
                    break
        except:
            #print( sys.exc_info())
            support.put_exception("state handler")

        if self.verbose:
            print( "Connection closed on", self.name)

        if conf.mem:
            #print( "Memory trace")
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            print("[ Top 10 ]")
            for stat in top_stats[:10]:
                print(stat)

        #if conf.pglog > 0:
        #    pysyslog.syslog("Disconn " + " " + str(self.client_address))

    def finish(self):

        global mydata

        cli = str(mydata[self.name].client_address)
        usr = str(mydata[self.name].user)
        #print( "Logoff '" + usr + "'", cli)
        del mydata[self.name]

        if verbose:
            print( "Closed socket on", self.name)

        if conf.pglog > 0:
            pysyslog.syslog("Logoff '" + usr + "' " + cli)

        #server.socket.shutdown(socket.SHUT_RDWR)
        #server.socket.close()

# ------------------------------------------------------------------------
# Override stock methods

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    #def __init__(self, arg1, arg2):
    #    self._BaseServer__shutdown_request = True

    def stop(self):
        self._BaseServer__shutdown_request = True
        if verbose:
            print( "Stop called")
        #self.shutdown()
        #self.server_close()
        pass


def usersig(arg1, arg2):

    global mydata, server
    #print("usersig", arg1, arg2)
    if conf.pglog > 0:
        pysyslog.syslog("Got user signal %d" % arg1)

    print("Current clients:")
    print( mydata)

# ------------------------------------------------------------------------

def terminate(arg1, arg2):

    global mydata, server

    if mydata != {}:
        print( "Dumping connection info:")
        print( mydata)

    try:
        server.socket.shutdown(socket.SHUT_RDWR)
        server.socket.close()
        server.shutdown()
    except:
        #print("Shutdown exception")
        pass

    if not quiet:
        print( "Terminated pyvserv.py.")

    if conf.pglog > 0:
        pysyslog.syslog("Terminated Server")

    support.unlock_process(pyservsup.globals.lockfname)

    # Attempt to unhook all pending clients
    sys.exit(2)

# ------------------------------------------------------------------------

optarr =  comline.optarr
optarr.append ( ["e",   "detach",      0,       None, "Detach from terminal"] )
optarr.append ( ["r:",  "dataroot",    None,    None, "Data root"] )
optarr.append ( ["l:",  "pglog",       1,       None, "Log level (0 - 10) default = 1"] )
optarr.append ( ["m",   "mem",         0,       None, "Show memory trace."] )

#print (optarr)

conf = comline.Config(optarr)

if __name__ == '__main__':

    global server

    if sys.version_info[0] < 3:
        print("Warning! This script was meant for python 3.x")
        time.sleep(.1)
        #sys.exit(0)

    args = conf.comline(sys.argv[1:])

    #for aa in vars(conf):
    #    print(aa, getattr(conf, aa))
    #, pglog, dataroot

    if conf.verbose:
        print("This script:     ", os.path.realpath(__file__))
        #print("Full path argv:  ", os.path.abspath(sys.argv[0]))
        #print("Script name:     ", __file__)
        #print("Exec argv:       ", sys.argv[0])

    parent = os.path.join(os.path.realpath(__file__),"..")
    pyservsup.globals.config(parent, conf)

    # Change directory to the data dir
    os.chdir(pyservsup.globals.script_home)

    if conf.verbose:
        print("Data Dir:        ", pyservsup.globals.datadir)
        print("Lockfile:        ", pyservsup.globals.lockfname)
        print("Passfile:        ", pyservsup.globals.passfile)
        print("Keyfile:         ", pyservsup.globals.keyfile)
        print("IDfile:          ", pyservsup.globals.idfile)
        print("Keydir:          ", pyservsup.globals.keydir)
        print("Payload:         ", pyservsup.globals.paydir)

    try:
        keyfroot = pyservsup.pickkey(pyservsup.globals.keydir)
    except:
        print("No keys generated yet. Please run ../tools/genkey.py first.")
        if conf.verbose:
            print("exc", sys.exc_info())
            print("keydir", pyservsup.globals.keydir)
        sys.exit(1)

    iii = pyservsup.create_read_idfile(pyservsup.globals.idfile)
    if not iii:
        print("Cannot read / create site ID, exiting.")
        sys.exit(1)

    pyservsup.globals.siteid = iii

    #if conf.verbose:
    #    print("Current dir:     ", os.getcwd())

    # Set termination handlers, so lock will be deleted
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    try:
        signal.signal(signal.SIGUSR1, usersig)
    except:
        print("User signal may not be available.")

    sys.stdout = support.Unbuffered(sys.stdout)
    sys.stderr = support.Unbuffered(sys.stderr)

    # Comline processed, go
    support.lock_process(pyservsup.globals.lockfname)

    pysfunc.pgdebug = conf.pgdebug
    pysfunc.pglog = conf.pglog

    if conf.pglog > 0:
        pysyslog.openlog("pyvserv.py")

    # Port 0 would mean to select an arbitrary unused port
    HOST, PORT = "", 6666

    try:
        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    except:
        print( "Cannot start server. ", sys.exc_info()[1])
        if conf.pglog > 0:
            pysyslog.syslog("Cannot start server " + str(sys.exc_info()[1]) )

        #print("Try again later.")
        terminate(None, None)
        #sys.exit(1)

    server.allow_reuse_address = True
    ip, port = server.server_address
    server.allow_reuse_address = True
    server.verbose = verbose

    # Start a thread with the server -- that thread will then start one
    # or more threads for each request
    server_thread = threading.Thread(target=server.serve_forever)

    # Exit the server thread when the main thread terminates
    server_thread.verbose = verbose
    #server_thread.setDaemon(True)
    server_thread.daemon = True
    #server_thread.paydir =  pyservsup.globals.paydir
    server_thread.start()

    if not quiet:
        strx = "Win or Unkn."
        try:
            import distro
            strx = distro.name()
        except:
            pass

        print("MainSiteID:", pyservsup.globals.siteid)

        print("Server running:", server.server_address)
        pyver = support.list2str(sys.version_info) #[0:3], ".")
        print("Running python", platform.python_version(), "on", platform.system(), strx)

    if conf.pglog > 0:
        pysyslog.syslog("Started Server")

    # Block
    server.serve_forever()

# EOF