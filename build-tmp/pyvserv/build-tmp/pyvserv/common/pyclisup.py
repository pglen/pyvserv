#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, socket
from Crypto import Random

import pydata, pyservsup, pypacker, crysupp, comline, pywrap

# -----------------------------------------------------------------------
# Globals

random.seed()

# ------------------------------------------------------------------------

class CliSup():

    def __init__(self, sock = None):
        self.sock = sock
        self.verbose = False
        self.pgdebug = 0
        if self.sock != None:
            self.mydathand  = pydata.xHandler(self.sock)
            self.myhandler  = pydata.DataHandler()
        self.wr = pywrap.wrapper()
        #self.wr.pgdebug = 2
        self.rr = Random.new()
        # Seed random;
        for aa in range(10):
            self.rr.read(5)

    def connect(self, ip, port):
        resp2 = ""
        if self.sock != None:
            raise ValueError("Already connected.")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))

        except:
            #print( "Cannot connect to:", ip + ":" + str(port), sys.exc_info()[1])
            raise
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.mydathand  = pydata.xHandler(self.sock)
        self.myhandler  = pydata.DataHandler()

        return self.getreply()

    def close(self):
        #self.sock.shutdown(socket.SHUT_RDWR)
        #self.sock.shutdown(socket.SHUT_WR)
        #self.sock.shutdown(socket.SHUT_RD)
        self.sock.close();

    # ------------------------------------------------------------------------
    # Send out our special buffer (short)len + (str)message

    def sendx(self, message):

        if self.pgdebug > 0:
            print("sending message:", message  )

        if sys.version_info[0] < 3:
            strx = struct.pack("!h", len(message)) + message
        else:
            if type(message) == type(""):
                 message = message.encode("cp437")
            strx = struct.pack("!h", len(message)) + message

        self.sock.send(strx)

    # ------------------------------------------------------------------------
    # Set encryption key. New key returned. Raises ValuError.

    def set_key(self, newkey, oldkey):
        resp = self.client("ekey " + newkey, oldkey)
        tmp = resp.split()
        if len(tmp) < 2 or tmp[0] != "OK":
            print( "Cannot set new key", resp)
            #raise(ValueError, "Cannot set new key. ")
        return newkey

    # ------------------------------------------------------------------------
    # Set encryption key from named key. Raises ValuError.
    # Make sure you fill in key_val from local key cache.

    def set_xkey(self,  newkey, oldkey):
        resp = self.client("xkey " + newkey, oldkey)
        tmp = resp.split()
        if len(tmp) < 2 or tmp[0] != "OK":
            print( "Cannot set new key", resp)
            #raise(Exception(ValueError, "Cannot set new named key."))
        return newkey

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

            self.sendx(buff)

        response = self.myhandler.handle_one(self.mydathand)

        if self.pgdebug > 2:
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
            #print("got data", data)

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

    def  getreply(self, key = "", rand = True):
        response = self.myhandler.handle_one(self.mydathand)

        if self.pgdebug > 3:
            print( "Got reply:", response)

        dstr = self.wr.unwrap_data(key, response)
        return dstr

    # ------------------------------------------------------------------------
    # Ping Pong function with encryption and padding. message is a
    # collection of data to send

    def client(self, message, key = "", rand = True):

        if type(message) != type([]):
            raise(TypeError, "Argument one to client() must be list")

        if self.pgdebug > 0:
            print( "   message:", message)
            #print("    key",  key)

        rstr = self.rr.read(random.randint(14, 24))
        xstr = self.rr.read(random.randint(24, 36))
        datax = [rstr, message, xstr]

        dstr = self.wr.wrap_data(key, datax)

        if self.pgdebug > 7:
            print( "   put: '%s'" % dstr)

        if self.pgdebug > 8:
            dstr2 = self.wr.unwrap_data(key, dstr)
            print( "   unwrap: ", dstr2)

        self.sendx(dstr)

        #if self.pgdebug > 0:
        #    print("    waiting for answer ...")

        response = self.getreply(key)

        if self.pgdebug > 0:
            print( "    get: '%s'" % response)

        return response

# EOF




