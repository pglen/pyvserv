#!/usr/bin/env python3

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random

sys.path.append('..')
sys.path.append('../bluepy')

import bluepy.bluepy

from pyserv import pydata
from common import pyservsup
                            
# -----------------------------------------------------------------------
# Globals 

random.seed()

# ------------------------------------------------------------------------
# Handle command line. Interpret optarray and decorate the class      

class Config:

    def __init__(self, optarr):
        self.optarr = optarr
        self.verbose = False
        self.debug = False
        
    def comline(self, argv):
        optletters = ""
        for aa in self.optarr:
            optletters += aa[0]
        #print( optletters    )
        # Create defaults:
        err = 0
        for bb in range(len(self.optarr)):
            if self.optarr[bb][1]:
                # Coerse type
                if type(self.optarr[bb][2]) == type(0):
                    self.__dict__[self.optarr[bb][1]] = int(self.optarr[bb][2])
                if type(self.optarr[bb][2]) == type(""):
                    self.__dict__[self.optarr[bb][1]] = str(self.optarr[bb][2])
        try:
            opts, args = getopt.getopt(argv, optletters)
        #except getopt.GetoptError, err:
        except:
            print( "Invalid option(s) on command line:", err)
            return ()
            
        #print( "opts", opts, "args", args)
        for aa in opts:
            for bb in range(len(self.optarr)):
                if aa[0][1] == self.optarr[bb][0][0]:
                    #print( "match", aa, self.optarr[bb])
                    if len(self.optarr[bb][0]) > 1:
                        #print( "arg", self.optarr[bb][1], aa[1])
                        if self.optarr[bb][2] != None: 
                            if type(self.optarr[bb][2]) == type(0):
                                self.__dict__[self.optarr[bb][1]] = int(aa[1])
                            if type(self.optarr[bb][2]) == type(""):
                                self.__dict__[self.optarr[bb][1]] = str(aa[1])
                    else:
                        #print( "set", self.optarr[bb][1], self.optarr[bb][2])
                        if self.optarr[bb][2] != None: 
                            self.__dict__[self.optarr[bb][1]] = 1
                        #print( "call", self.optarr[bb][3])
                        if self.optarr[bb][3] != None: 
                            self.optarr[bb][3]()
        return args
    
class CliSup:

    def __init__(self, sock):
        self.sock = sock
        self.mydathand  = pydata.xHandler(sock)
        self.myhandler  = pydata.DataHandler()
        self.verbose = False
        self.debug = False
                
    # ------------------------------------------------------------------------
    # Send out our special buffer (short)len + (str)message
    
    def sendx(self, message):
        strx = struct.pack("!h", len(message)) + message.encode("cp437")
        #print("message:", strx)
        self.sock.send(strx)
    
    # ------------------------------------------------------------------------
    # Set encryption key. New key returned. Raises ValuError.
    
    def set_key(self, newkey, oldkey):
        resp = self.client("ekey " + newkey, oldkey)
        tmp = resp.split()
        if len(tmp) < 2 or tmp[0] != "OK":
            print( "Cannot set new key", resp)
            raise(ValueError, "Cannot set new key. ")
        return newkey
    
    # ------------------------------------------------------------------------
    # Set encryption key from named key. Raises ValuError.
    # Make sure you fill in key_val from local key cache.
    
    def set_xkey(self,  newkey, oldkey):
        resp = self.client("xkey " + newkey, oldkey)
        tmp = resp.split()
        if len(tmp) < 2 or tmp[0] != "OK":
            print( "Cannot set new key", resp)
            raise(Exception(ValueError, "Cannot set new named key."))
    
    # ------------------------------------------------------------------------
    # Send file. Return True for success.
    
    def sendfile(self, fname, toname,  key = ""):
    
        if self.verbose:
            print( "Sending ", fname, "to", toname)
            
        response = ""
        try:    
            flen = os.stat(fname)[stat.ST_SIZE]
            fh = open(fname)
        except:
            print( "Cannot open file", sys.exc_info()[1])
            return
        resp = client("file " + toname, key)
        tmp = resp.split()
        if len(tmp) < 2 or tmp[0] != "OK":
            print( "Cannot send file command", resp)
            return 
        resp = client("data " + str(flen), key)
        tmp = resp.split()
        if len(tmp) < 2 or tmp[0] != "OK":
            print( "Cannot send data command", resp)
            return 
        while 1:
            buff = fh.read(pyservsup.buffsize)
            if len(buff) == 0:
                break
            if key != "":
                buff = bluepy.bluepy.encrypt(buff, key)
            self.sendx(buff)
        response = self.myhandler.handle_one(self.mydathand)
        if key != "":
            response = bluepy.bluepy.decrypt(response, key)
        if self.verbose:
            print( "Received: '%s'" % response)
        return True
        
    # ------------------------------------------------------------------------
    # Receive File. Return True for success.
    
    def getfile(self, fname, toname, key = ""):
    
        if self.verbose:
            print( "getting ", fname, "to", toname)
        try:  
            fh = open(toname, "w")         
        except:
            print( "Cannot create local file: '" + toname + "'")
            return
        response = client( "fget " + fname, key)
        aaa = response.split(" ")
        if len(aaa) < 2:
            fh.close()
            if self.verbose:
                print( "Invalid response, server said: ", response)
            return 
        if aaa[0] == "ERR":
            fh.close()
            if self.verbose:
                print( "Server said: ", response)
            return 
        mylen = 0; flen = int(aaa[1])
        #print( "getting", flen,)
        while mylen < flen:
            need = min(pyservsup.buffsize,  flen - mylen)
            need = max(need, 0)
            data = self.myhandler.handle_one(self.mydathand)
            if key != "":
                data = bluepy.bluepy.decrypt(data, key)
            try:
                fh.write(data)
            except:
                if self.verbose:
                    print( "Cannot write to local file: '" + toname + "'")
                fh.close()
                return
            mylen += len(data)
            # Faulty transport, abort
            if len(data) == 0:
                break
        fh.close()
        if self.verbose:
            print( "Got data, len =", mylen)
        if  mylen != flen:
            if self.verbose:
                print( "Faulty amount of data arrived")
            return
        return True
    
    # ------------------------------------------------------------------------
    # Ping Pong function with encryption.
    
    def client(self, message, key = "", rand = True):
        if self.verbose:
            print( "Sending: '%s'" % message)
            sys.stdout.flush()
            
        if key != "":
            if rand:
                message = message + " " * random.randint(0, 20)
            message = bluepy.bluepy.encrypt(message, key).decode("cp437")
        self.sendx(message)
        if self.verbose and key != "":
            print( "   put: '%s'" % base64.b64encode(message),)
        response = self.myhandler.handle_one(self.mydathand)
        if self.verbose and key != "":
            print( "get: '%s'" % base64.b64encode(response))
        if key != "":
            #response = pycrypt.xdecrypt(response, key)
            #response = bluepy.bluepy.decrypt(response, key)
            pass
        if self.verbose:
            print( "Rec: '%s'" % response)
            sys.stdout.flush()
            
        return response
    
# EOF    













