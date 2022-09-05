#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time, struct
import socket, threading, traceback, random

from Crypto import Random

if sys.version_info[0] < 3:
    import SocketServer
else:
    import socketserver

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base, '../bluepy'))
sys.path.append(os.path.join(base, '../common'))
sys.path.append(os.path.join(base, '../server'))
sys.path.append(os.path.join(base,  '../../pycommon'))

import bluepy
import support, pycrypt, pyservsup, pyclisup, pysyslog, pystate
import pypacker, pywrap

# Walk thru the server (chunk) state machine
# Chunk is our special buffer (short [16 bit])len + (str)message
# 1. Get length
# 2. Get data
# 3. Reply
# Set alarm after every transaction, so timeout is monitored
#
# Transmission needs to be 16 bit clean (2 byte boundaries)
#

class DataHandler():

    def __init__(self):
        #print(  "DataHandler __init__")
        self.src = None; self.tout = None
        self.timeout = 7
        self.pgdebug = 0
        self.pglog = 0
        self.wr = pywrap.wrapper()
        self.pb = pypacker.packbin()

    def handler_timeout(self):

        self.tout.cancel()
        if self.pgdebug > 0:
            print( "in handler_timeout %s" % self.name )

        #print( "handler_timeout log %d", self.pglog)

        if self.pglog > 0:
            pysyslog.syslog("Timeout on " + " " + str(self.par.client_address))

        #print(dir(self))
        #print(dir(self.par))

        rrr = ["ERR", "Timeout occured, disconnecting."]
        #print( self.par.client_address, self.par.server.socket)
        try:
            #print("ekey", self.par.ekey)
            self.putencode(rrr, self.par.ekey)
            #self.putdata(rrr, self.par.ekey)

        except:
            support.put_exception("putdata")

        # Force closing connection
        time.sleep(1)
        try:
            self.par.request.shutdown(socket.SHUT_RDWR)
        except:
            # Do not report error here
            #support.put_exception("on sending  timeout shutdown")
            pass

    def putencode(self, ddd, key = "", rand = True):
        if type(ddd) == str:
            raise(ValuError, "Argument must be an iterable")

        response = self.pb.encode_data("", ddd)
        self.putdata(response, key, rand)

    def putdata(self, response, key = "", rand = True):

        ret = ""; response2 = ""

        rstr = Random.new().read(random.randint(14, 24))
        xstr = Random.new().read(random.randint(24, 36))
        datax = [rstr, response, xstr]

        #print ("server key reply:", key[:16])
        #print ("server dats:", datax[:16])

        dstr = self.wr.wrap_data(key, datax)

        if self.pgdebug > 5:
            print ("Server reply:\n", dstr)
            pass

        try:
            #print ("putdata type:", type(dstr))

            if type(dstr) == type(""):
                response2 = bytes(dstr, "cp437")
            else:
                response2 = dstr

            #if self.pgdebug > 2:
            #    print ("assemble:", type(response2), response2 )

            # Send out our special buffer (short)len + (str)message
            if sys.version_info[0] < 3:
                strx = struct.pack("!h", len(response2)) + response2
            else:
                strx = struct.pack("!h", len(response2)) + response2

            #if self.pgdebug > 2:
            #    print ("sending: '", strx ) # + strx.decode("cp437") + "'")

            ret = self.par.request.send(strx)

            if self.tout:
                self.tout.cancel()
            self.tout = threading.Timer(self.timeout, self.handler_timeout)
            self.tout.start()

        except:
            sss = "While in Put Data: " + str(response)[:24]
            support.put_exception(sss)
            #self.resp.datahandler.putdata(sss, self.statehand.resp.ekey)
            if self.tout:
                self.tout.cancel()
            ret = -1
            raise

        return ret

    def getdata(self, amount):

        #if self.pgdebug > 7:
        #    print("getting data:", amount)

        if self.tout: self.tout.cancel()
        self.tout = threading.Timer(self.timeout, self.handler_timeout)
        self.tout.start()

        sss = self.par.request.recv(amount)
        #if self.pgdebug > 8:
        #    print("got len", amount, "got data:", sss)
        return sss.decode("cp437")

    # Where the outside stimulus comes in ...
    # State 0 - initial => State 1 - len arrived => State 2 data coming
    # Receive our special buffer (short)len + (str)message

    def handle_one(self, par):
        #print("Handle_one", par, par.ekey[:16])
        self.par = par
        try:
            cur_thread = threading.currentThread()
            self.name = cur_thread.getName()
            state = 0; xlen = []; newdata = ""; ldata = ""
            while 1:
                if state == 0:
                    xdata = self.getdata(max(2-len(ldata), 0))
                    if len(xdata) == 0: break
                    ldata += xdata
                    if len(ldata) == 2:
                        state = 1;
                        xlen = struct.unpack("!h", ldata.encode("cp437"))
                        #if self.pgdebug > 7:
                        #    print( "db got len =", xlen)
                elif state == 1:
                    data2 = self.getdata(max(xlen[0]-len(newdata), 0))
                    if len(data2) == 0:
                        break
                    newdata += data2
                    #if self.pgdebug > 7:
                    #    print( "db got data, len =", len(data2))
                    if len(newdata) == xlen[0]:
                        state = 3
                elif state == 3:
                    # Done, return buffer
                    state = 0
                    break
                else:
                    if self.pgdebug > 0:
                        print( "Unkown state")
            if self.tout: self.tout.cancel()
        except:
            support.put_exception("While in Handshake: ")

        #if self.pgdebug > 8:
        #    print("got data: '" + newdata + "'")

        #return newdata.encode("cp437")
        #return bytes(newdata, "cp437")
        return newdata


# Create a class with the needed members to send / recv
# This way we can call the same routines as the SockServer class
#

class xHandler():
    def __init__(self, socket, ekey = ""):
        self.request = socket
        self.ekey = ekey
        pass

# EOF
