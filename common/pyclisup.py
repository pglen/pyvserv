#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, socket
from Crypto import Random

import pydata, pyservsup, pypacker, crysupp, comline

sys.path.append('../bluepy')

import bluepy

# -----------------------------------------------------------------------
# Globals

random.seed()

# ------------------------------------------------------------------------

class CliSup():

    def __init__(self, sock = None):
        self.sock = sock
        self.verbose = False
        self.debug = False
        if self.sock != None:
            self.mydathand  = pydata.xHandler(self.sock)
            self.myhandler  = pydata.DataHandler()
        self.pb = pypacker.packbin()

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

        if sys.version_info[0] < 3:
            strx = struct.pack("!h", len(message)) + message
        else:
            if type(message) == type(str):
                 message = message.encode("cp437")
            strx = struct.pack("!h", len(message)) + message

        #print("message:", strx)
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
            if key != "":
                buff = bluepy.encrypt(buff, key)
            self.sendx(buff)
        response = self.myhandler.handle_one(self.mydathand)

        if key != "":
            response = bluepy.decrypt(response, key)
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
            #print("got data", data)
            if key != "":
                data = bluepy.decrypt(data, key)
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

    def  getreply(self):
        response = self.myhandler.handle_one(self.mydathand)
        dstr = self.pb.unwrap_data(response)
        return dstr[1]

    # ------------------------------------------------------------------------
    # Ping Pong function with encryption and padding. message is a
    # collection of data to send

    def client(self, message, key = "", rand = True):
        if self.verbose:
            print( "Sending: '%s'" % message)
            sys.stdout.flush()

        rstr = Random.new().read(random.randint(14, 24))
        xstr = Random.new().read(random.randint(24, 36))
        datax = [rstr, message, xstr]
        dstr = self.pb.wrap_data(datax)

        #print("dstr", dstr)
        #if pb.unwrap_data(dstr) != datax:
        #    print("Not decoded correctly", dstr)

        if key != "":
            pass
            #if rand:
            #    message = message + " " * random.randint(0, 20)
            #message = bluepy.encrypt(message, key).decode("cp437")
            #message = bluepy.encrypt(message, key)

        self.sendx(dstr)

        if self.verbose and key != "":
            print( "   put: '%s'" % base64.b64encode(message),)

        #print("wait for answer")
        response = self.getreply()

        if self.verbose and key != "":
            print( "get: '%s'" % base64.b64encode(response))
        if key != "":
            #response = pycrypt.xdecrypt(response, key)
            #response = bluepy.decrypt(response, key)
            pass
        if self.verbose:
            print( "Rec: '%s'" % response)
            sys.stdout.flush()

        return response

# EOF



