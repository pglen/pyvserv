#!/usr/bin/env python3

import os, sys, getopt, signal, select, string, time, struct 
import socket, threading, socketserver, traceback, random #, syslog

sys.path.append('..')

sys.path.append('../bluepy')
import bluepy.bluepy

#sys.path.append('..')
from common import support, pycrypt, pyservsup, pyclisup, syslog

# Walk thru the server (chunk) state machine 
# Chunk is our special buffer (short [16 bit])len + (str)message
# 1. Get length
# 2. Get data                                        
# 3. Reply
# Set alarm after every transaction, so timeout is monitored
#
# Transmission needs to be 16 bit clean

class DataHandler():
    
    def __init__(self, pgdebug = 0):
        #print(  "DataHandler __init__")
        self.src = None; self.tout = None
        self.timeout = 5
        self.pgdebug = pgdebug
        
    def handler_timeout(self):
        self.tout.cancel()
        if self.pgdebug > 0:
            print( "handler_timeout %s" % self.name )
            #print( self.par.client_address, self.par.server.socket)
        # Force closing connection
        self.par.request.send("Timeout occured, disconnecting.\n".encode("cp437"))
        self.par.request.shutdown(socket.SHUT_RDWR)
    
    def putdata(self, response, key, rand = True):
        if self.pgdebug > 7:
            print ("putdata '" + response + "'")
        try:
            response2 = response.encode("cp437")
            if  key != "":
                pass
                #if rand:
                #    response +=  " " * random.randint(0, 20)
                #response2 = bluepy.bluepy.encrypt(response, key)
                #response2 = response
                #bluepy.bluepy.destroy(response)
                
            if self.tout: self.tout.cancel()
            #self.tout = threading.Timer(self.timeout, self.handler_timeout)
            #self.tout.start()
            # Send out our special buffer (short)len + (str)message
            strx = struct.pack("!h", len(response2)) + response2
            #if self.pgdebug > 9:
            #    print ("sending: '", strx ) # + strx.decode("cp437") + "'")
            ret = self.par.request.send(strx)
        except:
            support.put_exception("Put Data:")
        return ret
          
    def getdata(self, amount):
        #if self.pgdebug > 7:
        #    print("getting data:", amount)
        if self.tout: self.tout.cancel()
        #self.tout = threading.Timer(self.timeout, self.handler_timeout)
        #self.tout.start()
        sss = self.par.request.recv(amount)
        #if self.pgdebug > 8:
        #    print("got len", amount, "got data:", sss)
        return sss.decode("cp437")

    # Where the outside stimulus comes in ...
    # State 0 - initial => State 1 - len arrived => State 2 data coming 
    # Receive our special buffer (short)len + (str)message
    
    def handle_one(self, par):    
        self.par = par
        try:
            cur_thread = threading.currentThread()
            self.name = cur_thread.getName()
            state = 0; xlen = 0; data = ""; ldata = ""
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
                    data2 = self.getdata(max(xlen[0]-len(data), 0))
                    if len(data2) == 0:
                        break
                    data += data2
                    #if self.pgdebug > 7:
                    #    print( "db got data, len =", len(data2))
                    if len(data) == xlen:
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
            support.put_exception("Handshake:")
            
        #if self.pgdebug > 8:
        #    print("got data: '" + data + "'")
                
        return data #.decode("cp437")

# Create a class with the needed members to send / recv
# This way we can call the same routines as the SockServer class
#

class xHandler():
    def __init__(self, socket):
        self.request = socket
        pass
























