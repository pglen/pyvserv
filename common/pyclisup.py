#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, socket, datetime

from Crypto import Random

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base, '../bluepy'))
sys.path.append(os.path.join(base, '../common'))
sys.path.append(os.path.join(base,  '../../pycommon'))

import pydata, pyservsup, pypacker, crysupp
import support, comline, pywrap

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

#rbuffsize = 1024
rbuffsize = 4096

# -----------------------------------------------------------------------
# Globals

random.seed()

# ------------------------------------------------------------------------

class CliSup():

    def __init__(self, sock = None):
        self.sock = sock
        self.sess = False
        self.verbose = False
        self.comm = ""
        self.pgdebug = 0
        if self.sock != None:
            self.mydathand  = pydata.xHandler(self.sock)
            self.myhandler  = pydata.DataHandler()
        self.wr = pywrap.wrapper()
        self.pb = pypacker.packbin()

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

        if self.pgdebug > 5:
            print("sending message:", message  )

        if sys.version_info[0] < 3:
            strx = struct.pack("!h", len(message)) + message
        else:
            if type(message) == type(""):
                 message = message.encode("cp437")
            strx = struct.pack("!h", len(message)) + message

        if self.comm:
            fp = open(self.comm, "a+")

            fp.write(strx.decode("cp437"))
            fp.close()

        self.sock.send(strx)

    def recvx(self, key):
        resp = self.getreply(key)

        if self.pgdebug > 1:
            print("resp:", resp)

        response = self.pb.decode_data(resp[1])

        if self.pgdebug > 0:
            print( "    get: '%s'" % response)

        return response[0]

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
    # Receive File. Return True for success.

    def putfile(self, fname, toname, key = ""):

        if not toname:
            toname = fname

        cresp = self.client(["fput", toname], key)
        if self.verbose:
            print ("Server fput response:", cresp)

        if cresp[0] != "OK":
            if self.verbose:
                print ("Server fput response:", cresp)
            return  cresp

        fp = open(fname, "rb")
        while 1:
            try:
                buf = fp.read(rbuffsize)
                #print("sending", buf)
                dstr = self.wrapx(buf, key)
                self.sendx(dstr)
                if len(buf) == 0:
                    break
            except:
                return ["ERR", "Cannot send", sys.exc_info()]

        return ["OK", "Sent Successfully"]

    # ------------------------------------------------------------------------
    # Receive File. Return True for success.

    def getfile(self, fname, toname, key = ""):

        if self.verbose:
            print( "getting ", fname, "to", toname)

        try:
            fh = open(toname, "wb+")
        except:
            print( "Cannot create local file: '" + toname + "'")
            return

        cresp = self.client(["fget", fname], key)
        #if self.verbose:
        #    print ("Server  fget response:", cresp)

        if cresp[0] != "OK":
            return cresp

        while(True):
            response = self.recvx(key)
            if self.pgdebug > 2:
                print("resp", response)

            if self.pgdebug > 5:
                print ("got:", response[0], end=", ")

            if response[0] == "0":
                break
            try:
                fh.write(response[1])
            except:
                #if self.verbose:
                print( "Cannot write to local file: '" + toname + "'", sys.exc_info())
                fh.close()
                return
        fh.close()

        if self.verbose:
            print()

        return  cresp

    def  getreply(self, key = "", rand = True):
        response = self.myhandler.handle_one(self.mydathand)

        if self.pgdebug > 3:
            print( "Got reply:")
            print (crysupp.hexdump(response, len(response)))

        dstr = self.wr.unwrap_data(key, response)
        return dstr

    ''' Stat return values are as in python os.stat() + OK and name prefix
    "OK", fname (1),
    st_mode (2), st_ino, st_dev, st_nlink
    st_uid, st_gid, st_size (8)
    st_atime (9), st_mtime, st_ctime
    st_atime_ns
    st_mtime_ns
    st_ctime_ns '''

    def listfiles(self, hand, cresp, key = ""):

        for aa in cresp:
            #bb = support.unescape(aa)
            cresp2 = hand.client(["stat", aa], key)
            #print("cresp2", cresp2)
            if cresp2[0] != "OK":
                print("Bad entry from remote", cresp2)
            else:
                ddd = datetime.datetime.fromtimestamp(int(cresp2[10]))
                print ("%s %-24s %-8d %s" %
                    (
                    support.mode2str(int(cresp2[2])), support.unescape(cresp2[1]),
                            int(cresp2[8]), ddd)
                    )
                #int(cresp2[9]), int(cresp2[10]), int(cresp2[11])
                #print(ddd)

    # Add random stuff and wrap
    def wrapx(self, message, key):

        rstr = self.rr.read(random.randint(14, 24))
        xstr = self.rr.read(random.randint(24, 36))
        datax = [rstr, message, xstr]

        dstr = self.wr.wrap_data(key, datax)

        if self.pgdebug > 7:
            print( "   wrapped: '%s'" % dstr)

        if self.pgdebug > 8:
            dstr2 = self.wr.unwrap_data(key, dstr)
            print( "   unwrap: ", dstr2)

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

        if key == "" and self.sess:
            raise(ValueError, "Must pass session key when in session")

        dstr = self.wrapx(message, key)
        self.sendx(dstr)

        #if self.pgdebug > 0:
        #    print("    waiting for answer ...")

        response =  self.recvx(key)

        '''resp = self.getreply(key)
        if self.pgdebug > 1:
            print("resp:", resp)
        response = self.pb.decode_data(resp[1])
        if self.pgdebug > 0:
            print( "    get: '%s'" % response)
        '''
        return response

    # ------------------------------------------------------------------------
    #  Login

    def  login(self, conf, userx, passx):

        cresp = self.client(["user", userx], conf.sess_key)
        #print ("Server user response:", cresp)
        if(cresp[0] != "OK"):
            return cresp

        cresp = self.client(["pass", passx], conf.sess_key)
        #print ("Server pass response:", cresp)
        if(cresp[0] != "OK"):
            return cresp

        return cresp

    # ------------------------------------------------------------------------
    #  Starts session - exec 'akey' and 'sess'

    def start_session(self, conf):

        resp = self.client(["akey"])

        if resp[0] != "OK":
            print("Error on getting key:", resp[1])
            self.client(["quit"])
            self.close();
            sys.exit(0)

        if conf.verbose:
            #print("Got hash:", "'" + resp[1] + "'")
            pass

        hhh = SHA512.new(); hhh.update(resp[2])

        if conf.pgdebug > 3:
            print("Hash1:  '" + resp[1] + "'")
            print("Hash2:  '" + hhh.hexdigest() + "'")

        # Remember key
        if hhh.hexdigest() !=  resp[1]:
            print("Tainted key, aborting.")
            self.client(["quit"])
            self.close();
            sys.exit(0)

        self.pkey = resp[2]

        #print("Key response:", resp[0], resp[2][:32], "...")

        if conf.pgdebug > 4:
             print(self.pkey)

        if conf.pgdebug > 2:
            print ("Server response:", "'" + hhh.hexdigest() + "'")

        try:
            self.pubkey = RSA.importKey(self.pkey)
            if conf.pgdebug > 4:
                print (self.pubkey)
        except:
            print("Cannot import public key.")
            support.put_exception("import key")
            self.client(["quit"])
            self.close();
            sys.exit(0)

        if conf.pgdebug > 1:
            print("Got ", self.pubkey, "size =", self.pubkey.size())

        # Generate communication key
        conf.sess_key = Random.new().read(512)
        sss = SHA512.new(); sss.update(conf.sess_key)

        cipher = PKCS1_v1_5.new(self.pubkey)
        #print ("cipher", cipher.can_encrypt())

        if conf.pgdebug > 2:
            support.shortdump("conf.sess_key", conf.sess_key )

        if conf.sess_key:
            sess_keyx = cipher.encrypt(conf.sess_key)
            ttt = SHA512.new(); ttt.update(sess_keyx)

            if conf.pgdebug > 2:
                support.shortdump("sess_keyx", sess_keyx )
        else:
            session_keyx = ""

        #print("Key Hexdigest", ttt.hexdigest()[:16])
        resp3 = self.client(["sess", sss.hexdigest(), ttt.hexdigest(), sess_keyx], "", False)

        #print("Sess Response:", resp3[1])

        if resp3[0] != "OK":
            print("Error on setting session:", resp3[1])
            self.client(["quit"])
            self.close();
            return None

        self.sess = True
        return resp3

# EOF