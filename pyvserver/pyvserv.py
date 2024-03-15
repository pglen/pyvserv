#!/usr/bin/env python3

__doc__ = \
'''
Server module.
'''
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

import pyvpacker

# Create a placeholder
server = None

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
    #sys.path.append(os.path.join(sf, "pyvgui"))
    #sys.path.append(os.path.join(sf, "pyvgui", "guilib"))

except:
    base = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(base,  '..'))
    sys.path.append(os.path.join(base,  '..', "pyvcommon"))
    sys.path.append(os.path.join(base,  '..', "pyvserver"))
    #sys.path.append(os.path.join(base, "..", "pyvgui"))
    #sys.path.append(os.path.join(base, "..", "pyvgui", "guilib"))
    from pyvcommon import support

#for aa in sys.path:
#    print(aa)

print("Load:", sys.path[-1])

from pyvcommon import support, pyservsup, pyclisup
from pyvcommon import pydata, pysyslog, comline

from pyvserver import pyvstate
from pyvserver import pyvfunc

version = "1.0"

mydata = {}

# ------------------------------------------------------------------------

class InvalidArg(Exception):

    ''' Exception for bad arguments '''

    def __init__(self, message):
         self.message = message

# ------------------------------------------------------------------------

connlist = []
sem = threading.Semaphore()

def throttle(peer):

    '''  Catch clients that are connecting too fast. This is a crude
         implementation, will need serious uppdate on large volume production
    '''

    global connlist, sem
    #print("throttle", peer)

    # Throttle to 10 sec frequency
    now = time.time()
    sem.acquire()
    sss = 0; slept = False
    for aa in connlist:
        if aa[0][0] == peer[0]:
            if now - aa[1] <  pyservsup.globals.throttle:
                sss += 1
    if sss >  pyservsup.globals.instance:
        for aa in range(len(connlist)-1, -1 ,-1):
            if connlist[aa][0][0] == peer[0]:
                if now - connlist[aa][1] > pyservsup.globals.throttle:
                    del connlist[aa]
        time.sleep(5.)
        slept = True

    # Clean throtle data periodically
    if len(connlist) > pyservsup.globals.maxthdat:
        for aa in range(len(connlist)-1, -1 ,-1):
            if connlist[aa][0][0] == peer[0]:
                if now - connlist[aa][1] > pyservsup.globals.throttle:
                    del connlist[aa]
    connlist.append((peer, now))
    #print(connlist)
    sem.release()
    return slept

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    ''' Request handler. '''

    def __init__(self, a1, a2, a3):
        self.a2 = a2
        self.fname = ""
        self.user = ""
        self.cwd = os.getcwd()
        self.dir = ""
        self.ekey = ""
        self.verbose = conf.verbose

        ttt = throttle(a1.getpeername())
        if self.verbose:
            if ttt > 0:
                print ("Throttle sleep",  a1.getpeername())

        socketserver.BaseRequestHandler.__init__(self, a1, a2, a3)

    def setup(self):

        ''' Start server '''

        global mydata

        #print("thread", self)
        #print(dir(self))

        cur_thread = threading.current_thread()
        #print(dir(cur_thread))

        self.name  = str(cur_thread._native_id) #name #getName()
        #self.name  = cur_thread.name #getName()
        #print( "Logoff '" + usr + "'", cli)
        if self.verbose:
            print( "Connection from ", self.a2, "as", self.name)

        #if pgdebug > 1:
        #    put_debug("Connection from %s" % self.a2)

        self.statehandler = pyvstate.StateHandler(self)
        self.statehandler.verbose = conf.verbose
        self.statehandler.pglog = conf.pglog
        self.statehandler.pgdebug = conf.pgdebug
        self.statehandler.name    = self.name

        #print(self.request)
        mydata[self.name] = self

        #print(dir(self))
        #print(self.name)
        #if conf.verbose:
        #    print("Connected " + " " + str(self.client_address))

        self.datahandler            =  pydata.DataHandler(self.request)
        self.datahandler.pgdebug    = conf.pgdebug
        self.datahandler.pglog      = conf.pglog
        self.datahandler.verbose    = conf.verbose
        self.datahandler.par        = self

        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if conf.pglog > 0:
            pysyslog.syslog("Connected " + " " + str(self.client_address))

        response =  ["OK", "pyvserv %s ready" % version]
        # Connected, acknowledge it
        self.datahandler.putencode(response, "")

    def handle_error(request, client_address):

        ''' Placeholder '''

        print("pyvserv Error", request, client_address)

    def handle(self):

        ''' Request comes in here '''

        if conf.mem:
            tracemalloc.start()
        try:
            while 1:
                ret = self.datahandler.handle_one(self)
                if not ret: break
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

        ''' Wind down, remove globals '''

        global mydata, conf

        cli = str(mydata[self.name].client_address)
        usr = str(mydata[self.name].user)
        #print( "Logoff '" + usr + "'", cli)
        del mydata[self.name]

        if conf.verbose:
            print( "Closed socket on", self.name)

        if conf.pglog > 0:
            pysyslog.syslog("Logoff '" + usr + "' " + cli)

        #server.socket.shutdown(socket.SHUT_RDWR)
        #server.socket.close()

# ------------------------------------------------------------------------
# Override stock methods

#class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
class ThreadedTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):

    ''' Overridden socket server '''

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

    ''' signal comes in here, list current clients '''

    global mydata, server
    print("usersig", arg1, arg2)
    if conf.pglog > 0:
        pysyslog.syslog("Got user signal %d" % arg1)

    print("Current clients:")
    print( mydata)

def usersig2(arg1, arg2):

    global mydata, server
    print("usersig2", arg1, arg2)
    if conf.pglog > 0:
        pysyslog.syslog("Got user signal2 %d" % arg1)

def soft_terminate(arg1, arg2):

    ''' Terminate app.  Did not behave as expected. '''

    #global mydata, server
    ##print("soft_terminate")
    #try:
    #
    #    for aa in mydata:
    #        print(aa, mydata[aa])
    #        mydata[aa].finish()
    #except:
    #    pass
    #

    terminate(0, 0)

    #while True:
    #    print( "Dumping connection info:")
    #    print( mydata)
    #    if mydata == {}:
    #        terminate(0, 0);
    #        break
    #    time.sleep (1)

# ------------------------------------------------------------------------

def terminate(arg1, arg2):

    global mydata, server

    #print("terminate")
    #if mydata != {}:
    #    print( "Dumping connection info:")
    #    print( mydata)

    try:
        if server:
            server.socket.shutdown(socket.SHUT_RDWR)
            server.socket.close()
            server.shutdown()
    except:
        print("Exception in shutdown", sys.exc_info())
        pass

    if not conf.quiet:
        print( "Terminated", progname)

    #if conf.pglog > 0:
    #    pysyslog.syslog("Terminated Server")

    support.unlock_process(pyservsup.globals.lockfname)

    # Attempt to unhook all pending clients
    sys.exit(2)

# ------------------------------------------------------------------------
# Execute one server cycle

class serve_one():

    ''' Simplifies server for testing. '''

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

    def run(self, *argx):

        self.client, self.client_address, self.args = self.argx
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

        #print(self.request)
        #mydata[self.name] = self

        #if conf.verbose:
        #    print("Connected " + " " + str(self.client_address))

        self.datahandler =  pydata.DataHandler(self.client)
        self.datahandler.pgdebug = conf.pgdebug
        self.datahandler.pglog = conf.pglog
        self.datahandler.verbose = conf.verbose
        self.datahandler.par = self

        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if conf.pglog > 0:
            pysyslog.syslog("Connected " + " " + str(self.client_address))

        response =  ["OK", "pyvserv %s ready" % version]
        # Connected, acknowledge it
        self.datahandler.putencode(response, "")

        try:
            while 1:
                ret = self.datahandler.handle_one(self)
                if not ret: break
                ret2 = self.statehandler.run_state(ret)
                if ret2:
                    #response2 = ["err", "Too many tries, disconnecting."]
                    response2 = ["ERR", "Disconnected."]
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

        if self.verbose:
            print("ended thread", self.name)



def simple_server(HOST, PORT):

    ''' This was a test server, left it in for future refernence.
        It was marginally faster than the stock version, also less features,
         so the stock servers stayed.
    '''

    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((HOST, PORT))
        server.listen()
        while True:
            client, addr = server.accept()
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            serve_one(client, addr, args)

# ------------------------------------------------------------------------

optarr =  comline.optarrlong
optarr.append ( ["e",   "detach=",   "detach",      0,       None, "Detach from terminal"] )
optarr.append ( ["l:",  "loglevel",  "pglog",       1,       None, "Log level (0 - 10) default = 1"] )
optarr.append ( ["n:",  "host",      "host",   "127.0.0.1",  None, "Set server hostname"] )
optarr.append ( ["r:",  "dataroot=", "droot",  "pyvserver",  None, "Root for server data"] )
optarr.append ( ["m",   "mem",       "mem",         0,       None, "Show memory trace."] )
optarr.append ( ["D",   "dmode",     "dmode",       0,       None, "Dev mode (no twofa)"] )
optarr.append ( ["N",   "norepl",    "norepl",      0,       None, "No replication (for test)"] )

#print (optarr)
comline.setargs("")
comline.setfoot("Use quotes for argument separations.")

conf = comline.ConfigLong(optarr)
#conf.printvars()


def mainfunct():

    ''' Main entry point. The pip install will call this script. '''

    if sys.version_info[0] < 3:
        print("Warning! This script was meant for python 3.x")
        time.sleep(.1)
        sys.exit(0)

    args = conf.comline(sys.argv[1:])
    #print(args)

    # Print comline args
    if conf.pgdebug > 7:
        for aa in vars(conf):
            if aa != "optarr":
                print(aa, "=", getattr(conf, aa), end = "   ")
        print()

    if conf.verbose:
        pass
        #print("This script:     ", os.path.realpath(__file__))
        #print("Full path argv:  ", os.path.abspath(sys.argv[0]))
        #print("Script name:     ", __file__)
        #print("Exec argv:       ", sys.argv[0])

    pyservsup.globals  = pyservsup.Global_Vars(__file__, conf.droot)
    pyservsup.globals.conf = conf
    pyservsup.globals.lockfname += "_" + str(conf.port)  # Lock file + port
    pyservsup.globals._softmkdir(pyservsup.globals.myhome)

    # Change directory to the data dir
    os.chdir(pyservsup.globals.myhome)
    #print("cwd", os.getcwd())

    pyservsup.globals.config(pyservsup.globals.myhome, conf)

    if conf.verbose:
        #print("Script Dir:      ", pyservsup.globals._script_home)
        print("Pass Dir:        ", pyservsup.globals.passdir)
        print("Key Dir:         ", pyservsup.globals.keydir)
        print("Payload Dir:     ", pyservsup.globals.paydir)
        print("Lockfile:        ", pyservsup.globals.lockfname)
        print("Passfile:        ", pyservsup.globals.passfile)
        print("IDfile:          ", pyservsup.globals.idfile)
        #print("Keyfile:         ", pyservsup.globals .keyfile)
    try:
        keyfroot = pyservsup.pickkey(pyservsup.globals.keydir)
    except:
        #print("No keys generated yet. Please run pyvgenkey.py first.")
        exec = os.path.dirname(os.path.split(pyservsup.globals._script_home)[0]) + os.sep
        exec += "../pyvtools/pyvgenkey.py"
        print("Notice: Generating key in", "'" + pyservsup.globals.keydir + "'")
        print("For added security please generate more keys with 'pyvgenkeys'");
        if conf.pgdebug > 2:
            print("Exec:  ", exec)

        try:
            os.system("%s -q -m %s " % (exec, pyservsup.globals.myhome))
            #if conf.verbose:
                #print("exc", sys.exc_info())
                #support.put_exception("Generating keys")
        except:
            print("Could not generate key. Keydir was", pyservsup.globals.keydir)
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
    signal.signal(signal.SIGINT, soft_terminate)
    try:
        signal.signal(signal.SIGUSR1, usersig)
        signal.signal(signal.SIGUSR2, usersig2)
    except:
        print("User signal may not be available.")

    sys.stdout = support.Unbuffered(sys.stdout)
    sys.stderr = support.Unbuffered(sys.stderr)

    # Comline processed, go
    support.lock_process(pyservsup.globals.lockfname)

    pyvfunc.pgdebug = conf.pgdebug
    pyvfunc.pglog = conf.pglog

    slogfile = os.path.join(pyservsup.globals.logdir, pyservsup.logfname + ".log")
    rlogfile = os.path.join(pyservsup.globals.logdir, pyservsup.repfname +".log")

    pysyslog.init_loggers(
            ("system", slogfile), ("replic", rlogfile))
    #pysyslog.syslog("Started Server")

    # Port 0 would mean to select an arbitrary unused port
    HOST, PORT = conf.host, conf.port

    if not conf.quiet:
        try:
            import distro
            strx = distro.name()
        except:
            strx = "Win or Unkn."

        print("MainSiteID:      ", pyservsup.globals.siteid)
        print("Server running: ", "'"+HOST+"'", "Port:", PORT)
        pyver = support.list2str(sys.version_info) #[0:3], ".")
        print("Running python", platform.python_version(), "on", platform.system(), strx)

        pyvstate.init_state_table()
    try:
        global server
        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        server.allow_reuse_address = True
        ip, port = server.server_address
        server.allow_reuse_address = True
        server.verbose = conf.verbose

        # Start a thread with the server -- that thread will then start one
        # or more threads for each request
        server_thread = threading.Thread(target=server.serve_forever)

        # Exit the server thread when the main thread terminates
        server_thread.verbose = conf.verbose
        #server_thread.setDaemon(True)
        server_thread.daemon = True
        #server_thread.paydir =  pyservsup.globals.paydir
        server_thread.start()

    except:
        print( "Cannot start server. ", sys.exc_info()[1])
        if conf.pglog > 0:
            pysyslog.syslog("Cannot start server " + str(sys.exc_info()[1]) )

        #print("Try again later.")
        terminate(None, None)
        #sys.exit(1)

    #if conf.pglog > 0:
    #    pysyslog.syslog("Started Server")

    if conf.pglog > 0:
        pysyslog.syslog("Server started. Devmode %d" % conf.dmode)

    # Block
    #simple_server(HOST, PORT)
    server.serve_forever()

if __name__ == '__main__':
    mainfunct()

# EOF