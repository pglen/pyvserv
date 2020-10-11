#!/usr/bin/env python3

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import tarfile, subprocess, struct, platform
import socket, threading, psutil

if sys.version_info[0] < 3:
    import SocketServer as socketserver
else:
    import socketserver

import pystate

sys.path.append('../common')

import support, pyservsup, pyclisup, pysyslog, pydata, comline

import pysfunc

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

        cur_thread = threading.currentThread()
        self.name = cur_thread.getName()
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

        response = self.statehandler.pb.encode_data("", ["OK", "pyvserv %s ready" % version])

        # Connected, acknowledge
        self.datahandler.putdata(response, "")


    def handle_error(request, client_address):
        print("pyvserv Error", request, client_address)

    def handle(self):
        try:
            while 1:
                ret = self.datahandler.handle_one(self)
                if not ret: break
                ret2 = self.statehandler.run_state(ret)
                if ret2:
                    response2 = "Too many tries, disconnecting.\n"
                    self.datahandler.putdata("ERR " + response2, self.statehandler.resp.ekey)
                    break
        except:
            #print( sys.exc_info())
            support.put_exception("state handler")

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
        print("Full path argv:  ", os.path.abspath(sys.argv[0]))
        print("Script name:     ", __file__)
        #print("Exec argv:       ", sys.argv[0])

    pyservsup.globals.script_home = os.path.dirname(os.path.realpath(__file__))
    pyservsup.globals.script_home += "/../data/"
    pyservsup.globals.script_home = os.path.realpath(pyservsup.globals.script_home)

    pyservsup.globals.verbose = conf.verbose
    pyservsup.globals.pgdebug = conf.pgdebug

    if conf.verbose:
        print("Script home:     ", pyservsup.globals.script_home)

    if conf.pgdebug:
            print ("Debug level:     ", conf.pgdebug)

    try:
        if not os.path.isdir(pyservsup.globals.script_home):
            os.mkdir(pyservsup.globals.script_home)
    except:
        print( "Cannot make script home dir", sys.exc_info())
        sys.exit(1)

    pyservsup.globals.datadir = pyservsup.globals.script_home + pyservsup.globals._datadir

    try:
        if not os.path.isdir(pyservsup.globals.datadir):
            os.mkdir(pyservsup.globals.datadir)
    except:
        print( "Cannot make data dir", pyservsup.globals.datadir, sys.exc_info())
        sys.exit(1)

    pyservsup.globals.lockfname = pyservsup.globals.datadir + "/lockfile"
    pyservsup.globals.passfile = pyservsup.globals.datadir + pyservsup.globals._passfile
    pyservsup.globals.keyfile = pyservsup.globals.datadir + pyservsup.globals._keyfile

    if conf.verbose:
        print("Data Dir:        ", pyservsup.globals.datadir)
        print("Lockfile:        ", pyservsup.globals.lockfname)
        print("Passfile:        ", pyservsup.globals.passfile)
        print("Keyfile:         ", pyservsup.globals.keyfile)

    # Change directory to the data dir
    os.chdir(pyservsup.globals.script_home)

    #if conf.verbose:
    #    print("Current dir:     ", os.getcwd())

    # Set termination handlers, so lock will be deleted
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGUSR1, usersig)

    sys.stdout = support.Unbuffered(sys.stdout)
    sys.stderr = support.Unbuffered(sys.stderr)

    # Comline processed, go
    support.lock_process(pyservsup.globals.lockfname)

    pysfunc.pgdebug = conf.pgdebug
    pysfunc.pglog = conf.pglog

    if conf.pglog > 0:
        pysyslog.openlog("pyvserv.py")

    # Port 0 would mean to select an arbitrary unused port
    HOST, PORT = "", 9999

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
    server_thread.setDaemon(True)
    server_thread.start()

    if not quiet:
        strx = ""
        import distro
        for aa in distro.linux_distribution():
            strx += str(aa) + " "
        print("Server running:", server.server_address)
        print("Running on", platform.system(), strx)

    if conf.pglog > 0:
        pysyslog.syslog("Started Server")

    # Block
    server.serve_forever()

# EOF


