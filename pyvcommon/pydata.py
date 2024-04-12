#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time, struct
import socket, threading, traceback, random

from Crypto import Random

if sys.version_info[0] < 3:
    import SocketServer
else:
    import socketserver

#base = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(base,  '../../pycommon'))
#sys.path.append(os.path.join(base,  '../../pypacker'))

import support, pycrypt, pyservsup, pyclisup, pysyslog #, pystate
import pyvpacker, pywrap

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

    def __init__(self, sock, timeout = 20):
        #print(  "DataHandler __init__")
        self.src = None; self.tout = None
        self.timeout = timeout
        self.pgdebug = 0
        self.verbose = 0
        self.pglog = 0
        self.wr = pywrap.wrapper()
        self.pb = pyvpacker.packbin()
        self.rfile = sock.makefile("rb")
        self.wfile = sock.makefile("wb")
        self.sock = sock
        self.cumm = b""
        self.timex = 0
        self.toutflag = False
        self.thread = threading.Thread(target=self.run_tout)
        self.thread.daemon = True
        self.thread.start()

    def run_tout(self, *argx):
        cur_thread = threading.current_thread()
        self.name = cur_thread.name
        while True:
            time.sleep(1)
            #print (self.timex)
            if self.sock._closed:
                break
            self.timex += 1
            if self.timex > self.timeout:
                self.handler_timeout()
                break

    def handler_timeout(self):
        try:
            #self.tout.cancel()
            if self.pgdebug > 0:
                print( "in handler_timeout %s" % self.name )

            #if self.verbose:
            #    print( "handler_timeout()")

            if self.pglog > 0:
                pysyslog.syslog("Timeout on ", str(self.par.client_address))

            #print(dir(self))
            #print(dir(self.par))

            # Forcably close ... dead already but cleanup can start
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()

        except:
            pass
        self.toutflag = True

    def putencode(self, ddd, key = "", rand = True):

        if type(ddd) == str:
            raise ValueError("Argument must be an iterable")

        if self.toutflag:
            ddd = ["ERR", "Timeout occured, disconnecting."]

        if self.pglog > 4:
            pysyslog.syslog("putencode", ddd)

        response = self.pb.encode_data("", ddd)
        self._putdata(response, key, rand)

        if self.toutflag:
            time.sleep(.1)
            self.par.request.shutdown(socket.SHUT_RDWR)

    #@support.timeit
    def _putdata(self, response, key = "", rand = True):

        ret = ""; response2 = ""

        rstr = Random.new().read(random.randint(14, 24))
        xstr = Random.new().read(random.randint(24, 36))
        datax = [rstr, response, xstr]
        #datax = [response]

        #print ("server key reply:", key[:16])
        #print ("server dats:", datax[:16])

        dstr = self.wr.wrap_data(key, datax)

        if self.pgdebug > 9:
            print ("Server reply:\n", dstr)
            pass
        ret = self.putraw(dstr)
        return ret

    def putraw(self, dstr):

        self.timex = 0

        ret = ""; response2 = ""

        try:
            if type(dstr) == type(""):
                response2 = bytes(dstr, "utf-8")
            else:
                response2 = dstr

            #if self.pgdebug > 2:
            #    print ("assemble:", type(response2), response2 )

            # Send out our special buffer (short)len + (str)message
            strx = struct.pack("!h", len(response2)) + response2

            #if self.pgdebug > 2:
            #    print ("sending: '", strx ) # + strx.decode("utf-8") + "'")

            #ret = self.par.request.send(strx)
            ret = self.wfile.write(strx)
            ret = self.wfile.flush()

            #if self.tout:
            #    self.tout.cancel()
            #self.tout = threading.Timer(self.timeout, self.handler_timeout)
            #self.tout.start()

        except:
            sss = "While in Put Raw: " + str(response2)[:24]
            support.put_exception(sss)
            #self.resp.datahandler._putdata(sss, self.statehand.resp.ekey)
            #if self.tout:
            #    self.tout.cancel()
            ret = -1
            raise

        return ret

    #@support.timeit
    def getdata(self, amount):

        self.timex = 0

        #sss = self.sock.recv(amount)
        sss = self.rfile.read(amount)

        #if self.pgdebug > 8:
        #    print("got len", amount, "got data:", sss)
        #return sss.decode("utf-8")

        return sss

    # Where the outside stimulus comes in ...
    # State 0 - initial => State 1 - len arrived => State 2 data coming
    # Receive our special buffer (short)len + (str)message

    def handle_one(self, par):

        self.par = par

        #print("Handle_one", par, par.ekey[:16])
        newarr = [] ; newdata = b""; state = 0; xlen = 2
        try:
            while 1:
                buff =  self.getdata(xlen)
                if len(buff) == 0:
                    break
                self.cumm += buff
                #print("sock", buff)
                #print("xlen", xlen)
                #print("cummlen", len(self.cumm))
                if state == 0:
                    if len(self.cumm) >= 2:
                        xlen = struct.unpack("!h", self.cumm[:2])[0]
                        self.cumm = self.cumm[2:]
                        state = 1;
                elif state == 1:
                    if len(self.cumm) >= xlen:
                        newarr.append(self.cumm[:xlen])
                        self.cumm = self.cumm[xlen:]
                        break
                else:
                    if self.pgdebug > 0:
                        print( "Unkown state")

            newdata = b"".join(newarr)
            #if self.tout:
            #    self.tout.cancel()
        except:
            support.put_exception("While in handle_one: ")

        #if self.pgdebug > 8:
        #   print(b"got data: '" + newdata + b"'")

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
