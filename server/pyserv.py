#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import tarfile, subprocess, struct
import socket, threading, psutil

if sys.version_info[0] < 3:
    import SocketServer as socketserver
else:
    import socketserver

import pystate

sys.path.append('../common')
import support, pyservsup, pyclisup, pysyslog, pydata
import pysfunc

# Globals
verbose = False
quiet  = False
version = 1.0
pgdebug = 0
mydata = {}

script_home = ""
datadir = ".pyvserv"
lockfile = datadir + "/lock"

# ------------------------------------------------------------------------

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, a1, a2, a3):
        self.a2 = a2
        #print("init", a1, a2, a3)
        socketserver.BaseRequestHandler.__init__(self, a1, a2, a3)
        #print(  SocketServer)

    def setup(self):
        cur_thread = threading.currentThread()
        self.name = cur_thread.getName()
        #print( "Logoff '" + usr + "'", cli)

        self.verbose = verbose
        if verbose:
            print( "Connection from ", self.a2, "as", self.name)

        #if pgdebug > 1:
        #    put_debug("Connection from %s" % self.a2)

        self.datahandler =  pydata.DataHandler(pgdebug)
        self.datahandler.verbose = verbose
        self.statehandler = pystate.StateHandler(self)
        self.statehandler.verbose = verbose

        mydata[self.name] = self

        if verbose:
            print("Connected " + " " + str(self.client_address))

        pysyslog.syslog("Connected " + " " + str(self.client_address))
        self.datahandler.verbose = verbose
        self.datahandler.par = self
        self.datahandler.putdata("OK pyvserv ready", "")

    def handle_error(request, client_address):
        print(  "pyvserv Error", request, client_address)

    def handle(self):
        try:
            while 1:
                ret = self.datahandler.handle_one(self)
                #print("handle got:", ret)
                if ret == "": break
                ret2 = self.statehandler.run_state(ret)
                if ret2: break
        except:
            #print( sys.exc_info())
            support.put_exception("state handler")

    def finish(self):
        cli = str(mydata[self.name].client_address)
        usr = str(mydata[self.name].user)
        #print( "Logoff '" + usr + "'", cli)
        del mydata[self.name]
        if verbose:
            print( "Closed socket on", self.name)
        pysyslog.syslog("Logoff '" + usr + "' " + cli)

        #server.socket.shutdown(socket.SHUT_RDWR)
        #server.socket.close()

# ------------------------------------------------------------------------
# Override stock methods

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    #def __init__(self):
    #    self._BaseServer__shutdown_request = True

    def stop(self):
        self._BaseServer__shutdown_request = True
        if verbose:
            print( "Stop called")

        #self.shutdown()
        #self.server_close()

        pass

# ------------------------------------------------------------------------

def help():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -v        - Verbose")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

# ------------------------------------------------------------------------

def terminate(arg1, arg2):

    global mydata, server

    if mydata != {}:
        print( "Dumping connection info:")
        print( mydata)

    try:
        server.shutdown()
    except:
        pass

    #server.socket.shutdown(socket.SHUT_RDWR)
    #server.socket.close()

    if not quiet:
        print( "Terminated pyvserv.py.")

    pysyslog.syslog("Terminated Server")
    try:
        os.unlink(lockfile)
    except:
        print("Cannot unlink lockfile.")

    sys.exit(2)


def lock_process():

    closeit = 0; pidstr = ""
    pid = os.getpid()

    try:
        fh = open(lockfile, "r")
        if fh:
            pidstr = fh.read()
            fh.close()
            closeit = 1
    except:
        pass

    if closeit:

        # Examine if it is still running:
        was = False
        if pidstr != "":
            for proc in psutil.process_iter():
                if proc.pid == int(pidstr):
                    was = True
        if not was:
            print("Lockfile active, no process ... breaking in")
            os.unlink(lockfile)
        else:
            print("Server running already.")
            if verbose:
                print("Lockfile '%s' pid '%s'" % (lockfile, pidstr))
            sys.exit(2)

    fh = open(lockfile, "w");
    fh.write( str() );
    fh.close()

# ------------------------------------------------------------------------

if __name__ == '__main__':

    global server
    opts = []; args = []

    if sys.version_info[0] < 3:
        print("Warning! This script was meant for python 3.x")
        time.sleep(1)

    #print("This script:     ", os.path.realpath(__file__))
    #print("Exec argv:       ", sys.argv[0])
    #print("Full path argv:  ", os.path.abspath(sys.argv[0]))
    #print("Executable name: ", sys.executable)
    #print("Script name:     ", os.__file__)

    script_home = os.path.dirname(os.path.realpath(__file__)) + "/../data/"

    #print ("Script home:     ", script_home)

    try:
        if not os.path.isdir(script_home):
            os.mkdir(script_home)
    except:
        print( "Cannot make script home dir", sys.exc_info())
        sys.exit(1)

    try:
        if not os.path.isdir(script_home + datadir):
            os.mkdir(script_home + datadir)
    except:
        print( "Cannot make data dir", sys.exc_info())
        sys.exit(1)

    os.chdir(script_home)
    #print("Current dir:     ", os.getcwd())


    # Set termination handlers, so lock will be deleted
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)

    sys.stdout = support.Unbuffered(sys.stdout)
    sys.stderr = support.Unbuffered(sys.stderr)

    pysyslog.openlog("pyvserv.py")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:qhvV")
    except getopt.GetoptError as err:
        print( "Invalid option(s) on command line:", err)
        sys.exit(1)

    #print( "opts", opts, "args", args)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
                if verbose:
                    print( "Debug level:", pgdebug)
                if pgdebug > 10 or pgdebug < 0:
                    raise(Exception(ValueError, \
                        "Debug range needs to be between 0-10"))
            except:
                support.put_exception("Command line for:")
                sys.exit(3)

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-v": verbose = True
        if aa[0] == "-q": quiet = True
        if aa[0] == "-V":
            print( os.path.basename(sys.argv[0]), "Version", version)
            sys.exit(0)

    lock_process()
    pysfunc.pgdebug = pgdebug

    # Port 0 would mean to select an arbitrary unused port
    HOST, PORT = "", 9999

    try:
        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    except:
        print( "Cannot start server. ", sys.exc_info()[1])
        #print("Try again later.")
        terminate(None, None)
        #sys.exit(1)

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
        print( "Server running:", server.server_address)

    pysyslog.syslog("Started Server")

    # Block
    server.serve_forever()

# EOF


