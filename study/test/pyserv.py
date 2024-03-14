#!/usr/bin/env python

import os, sys, getopt, signal, select, string, time
import tarfile, subprocess, commands, struct, gobject
import socket, threading, SocketServer, traceback, syslog

import pystate, pydata, pyservsup
    
verbose = False  
quiet  = False  
version = 1.0
pgdebug = 0

# Globals
mydata = {}
#; mystate = {}; myhandlers = {}
server = None

def put_debug(xstr):
    try:
        if os.isatty(sys.stdout.fileno()):
            print xstr
        else:
            syslog.syslog(xstr)
    except:
        print "Failed on debug output."
        print sys.exc_info()

# ------------------------------------------------------------------------

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def __init__(self, a1, a2, a3):
        self.a2 = a2
        #print a1 #print a2 #print a3
        SocketServer.BaseRequestHandler.__init__(self, a1, a2, a3)
        #print  SocketServer
        
    def setup(self):
        cur_thread = threading.currentThread()
        self.name = cur_thread.getName()
        if verbose:
            print "Connection from ", self.a2, "as", self.name
            
        if pgdebug > 1:
            put_debug("Connection from %s" % self.a2)
            
        self.datahandler = pydata.DataHandler()
        self.statehandler = pystate.StateHandler(self)
        
        mydata[self.name] = self 
        syslog.syslog("Connected " + " " + str(self.client_address))
            
    def handle_error(request, client_address):
        print  request, client_address
             
    def handle(self):
    
        try:
            while 1:
                ret = self.datahandler.handle_one(self)
                if not ret: break                
                ret2 = self.statehandler.run_state(ret)
                if ret2: break
        except:
            print sys.exc_info()
        
    def finish(self):
        cli = str(mydata[self.name].client_address)
        usr = str(mydata[self.name].user)
        print "Logoff '" + usr + "'", cli
        del mydata[self.name]
        if verbose:
            print "Closed socket on", self.name
        syslog.syslog("Logoff '" + usr + "' " + cli)

# ------------------------------------------------------------------------
# Override stock methods

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    
    def stop(self):
        self._BaseServer__shutdown_request = True
        if verbose:
            print "Stop called"
        pass
        
# ------------------------------------------------------------------------

def help():

    print
    print "Usage: " + os.path.basename(sys.argv[0]) + " [options]"
    print
    print "Options:    -d level  - Debug level 0-10"
    print "            -v        - Verbose"
    print "            -q        - Quiet"
    print "            -h        - Help"
    print
    sys.exit(0)

# ------------------------------------------------------------------------
        
def terminate(arg1, arg2):

    global mydata
    if mydata != {}:
        print "Dumping connection info:"
        print mydata
        
    server.stop()
    
    if not quiet:
        print "Terminated pyserv.py."
        
    syslog.syslog("Terminated Server")
    sys.exit(2)

# ------------------------------------------------------------------------

if __name__ == '__main__':

    opts = []; args = []

    syslog.openlog("pyserv.py")

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:qhvV")
    except getopt.GetoptError, err:
        print "Invalid option(s) on command line:", err
        sys.exit(1)

    #print "opts", opts, "args", args
    
    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
                if verbose:
                    print "Debug level:", pgdebug
                if pgdebug > 10 or pgdebug < 0:
                    raise(ValueError, \
                        "Debug range needs to be between 0-10")
            except:
                put_exception("Command line 1or:")
                sys.exit(3)

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-v": verbose = True            
        if aa[0] == "-q": quiet = True            
        if aa[0] == "-V": 
            print os.path.basename(sys.argv[0]), "Version", version
            sys.exit(0)
                
    # Set termination handlers
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    
    # Port 0 would mean to select an arbitrary unused port
    HOST, PORT = "", 9999
    #HOST, PORT = "localhost", 9999
    #HOST, PORT = "192.168.1.13", 9999
            
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    server.allow_reuse_address = True

    # Start a thread with the server -- that thread will then start one
    # or more threads for each request
    server_thread = threading.Thread(target=server.serve_forever)
    
    # Exit the server thread when the main thread terminates
    server_thread.setDaemon(True)
    server_thread.start()

    if not quiet:    
        print "Server running:", server.server_address

    syslog.syslog("Started Server")
     
    # Block       
    server.serve_forever()













