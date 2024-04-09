#!/usr/bin/env python

#from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, socket, datetime

from pyvecc.Key import Key

import pydata, pyservsup, crysupp, support, comline, pywrap

import pyvpacker

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

from Crypto.PublicKey import ECC
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP

#rbuffsize = 1024
rbuffsize = 4096

OK  = "OK"
ERR = "ERR"

privtest = '''\
-----BEGIN PRIVATE ECC-----
ZMOOwr3Dg0sSw7oTAQAAQMOpM8O+D8O2w53ClsOjwr4KwpRxZcKmCMOVwrZ8w54/McOqY8K7w7VtD8KTBcKKwq4uwosvMHLDj3TDgMOtw6w+wrHDqRtCecO5w5vCmnE6w5jDi8KAw58Gw7vCqcKLw5XDn8KEwpsAIC56akoEOsO6w5hYwpwfADHCrcOvwrxIwqMUwrXClkXDsW8OJcO/fMOaT8O+w7c=
-----END PRVATE ECC-----
'''

# -----------------------------------------------------------------------
# Globals

random.seed()

class CliSup():

    def __init__(self, sock = None):
        self.sock = sock
        self.sess = False
        self.verbose = False
        self.comm = ""
        self.pgdebug = 0
        if self.sock != None:
            self.mydathand  = pydata.xHandler(self.sock)
            self.myhandler  = pydata.DataHandler(self.sock)
        self.wr = pywrap.wrapper()
        self.pb = pyvpacker.packbin()

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
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.mydathand  = pydata.xHandler(self.sock)
        self.myhandler  = pydata.DataHandler(self.sock, 100)

        return self.getreply()

    def close(self):
        #self.sock.shutdown(socket.SHUT_RDWR)
        #self.sock.shutdown(socket.SHUT_WR)
        #self.sock.shutdown(socket.SHUT_RD)
        self.sock.close();

    # ------------------------------------------------------------------------
    # Send out our special buffer (short)len + (str)message

    def sendx(self, message):

        if self.pgdebug > 7:
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

        self.sock.sendall(strx)

    def recvx(self, key):
        resp = self.getreply(key)
        if self.pgdebug > 5:
            print("resp:", resp[:24])
        response = self.pb.decode_data(resp[1])
        if self.pgdebug > 7:
            print( "    recvx: '%s'" % response[:24])
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
            #raise(ValueError, "Cannot set new named key.")
        return newkey

    # ------------------------------------------------------------------------
    # Send File. Return True for success.

    def putfile(self, fname, toname, key = ""):

        if self.verbose:
            print("putfile(), fname")

        if not toname:
            toname = fname
        try:
            fp = open(fname, "rb")
        except:
            if self.verbose:
                print("Cannot open file", sys.exc_info())
            cresp = ["ERR", "Cannot open", fname]
            return cresp

        cresp = self.client(["fput", toname], key)
        if self.verbose:
            print ("fput response:", cresp)

        if cresp[0] != "OK":
            return  cresp

        while 1:
            try:
                buf = fp.read(rbuffsize)
                #print("sending buffer", buf)
                dstr = self.wrapx(buf, key)
                self.sendx(dstr)
                if len(buf) == 0:
                    break
            except:
                return ["ERR", "Cannot send", sys.exc_info()]

        response = self.recvx(key)
        return response

    # ------------------------------------------------------------------------
    # Receive File. Return True for success.

    def getfile(self, fname, toname, key = ""):

        if not fname:
            cresp = ["ERR", "Must specify file name."]
            return cresp

        if not toname:
            toname = fname  #+ "_local"

        if self.verbose:
            print( "getting ", fname, "to", toname)

        try:
            fh = open(toname, "wb+")
        except:
            cresp = ["ERR", "Cannot create local file: '" + toname + "'", ]
            return cresp

        cresp = self.client(["fget", fname], key)
        if self.verbose:
            print ("fget response:", cresp)

        if cresp[0] != "OK":
            #print("remove:", toname)
            try:
                os.remove(toname)
            except:
                print(sys.exc_info())
            return cresp

        fsize = int(cresp[1])
        cipher = AES.new(key[:32], AES.MODE_CTR,
                        use_aesni=True, nonce = key[-8:])
        while(True):
            response = self.myhandler.handle_one(self.mydathand)
            if self.pgdebug > 8:
                print("getfile resp", response[:12])
            # possibly EOF
            if not response:
                break
            response = cipher.encrypt(response)
            try:
                fh.write(response)
            except:
                #if self.verbose:
                print( "Cannot write to local file: '" + toname + "'", sys.exc_info())
                fh.close()
                cresp = ["ERR" ,"Cannot write local file",]
                return cresp
            fsize -= len(response)
            # Detect the end of file bythe empty packet
            #if fsize <= 0:
            #   break
            #if not response:
            #    break
        fh.close()
        resp = self.recvx(key)
        return  resp

    def  getreply(self, key = "", rand = True):

        response = self.myhandler.handle_one(self.mydathand)
        if self.pgdebug > 6:
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

        rstr = self.rr.read(random.randint(4, 14))
        xstr = self.rr.read(random.randint(4, 16))
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

    #@support.timeit2
    def client(self, message, key = "", rand = True):

        if type(message) != type([]):
            raise TypeError("Argument one to client() must be list")

        if self.pgdebug > 5:
            cnt = 0
            for aa in message:
                try:
                    if len(aa) > 30:
                        aa = aa[:24]
                except:
                    # Not iterable
                    pass

                print( "   message %d:" % cnt, aa, end=' ')
                cnt += 1
            print()
            #print("    key",  key)

        if len(key) == 0 and self.sess:
            raise ValueError("Must pass session key when in session")

        dstr = self.wrapx(message, key)
        self.sendx(dstr)

        #if self.pgdebug > 0:
        #    print("    waiting for answer ...")

        response =  self.recvx(key)

        if self.pgdebug > 5:
            cnt = 0
            for aa in response:

                try:
                    if len(aa) > 30:
                        aa = aa[:12]
                except:
                    # Not iterable
                    pass
                print( "   response %d:" % cnt, aa, end=' ')
                cnt += 1
            print()

        '''resp = self.getreply(key)
        if self.pgdebug > 5:
            print("resp:", resp)
        response = self.pb.decode_data(resp[1])
        if self.pgdebug > 5:
            print( "    get: '%s'" % response)
        '''
        return response

    # ------------------------------------------------------------------------
    #  Login

    def  login(self, userx, passx, conf):

        if not hasattr(conf, "sess_key"):
            conf.sess_key = ""
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

    #@support.timeit
    def start_session(self, conf):

        # Patch expected variables
        if not hasattr(conf, "sess_key"):
            conf.sess_key = ""
        if not hasattr(conf, "verbose"):
            conf.verbose = 0
        if not hasattr(conf, "pgdebug"):
            conf.pgdebug = 0

        #if not hasattr(conf, "sess_key"):
        conf.sess_key2 = conf.sess_key[:]

        #if conf.verbose:
        #    print("Got akey:", resp)

        resp = self.client(["akey"], conf.sess_key2)

        if self.pgdebug > 5:
            print("Got akey:", resp)

        if resp[0] != "OK":
            print("Error on getting key:", resp)
            self.client(["quit"])
            self.close();
            sys.exit(0)

        if self.pgdebug > 5:
            print("Got hash:", "'" + resp[1] + "'")

        #hhh = SHA512.new(); hhh.update(bytes(resp[2], "cp437"))
        hhh = SHA256.new(); hhh.update(resp[2].encode())

        if self.pgdebug > 16:
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

        if self.pgdebug > 5:
             print(self.pkey)

        if self.pgdebug > 5:
            print ("Server response:", "'" + hhh.hexdigest() + "'")

        try:
            #print(self.pkey)
            #self.pubkey = RSA.importKey(self.pkey)
            #self.pubkey = ECC.import_key(self.pkey)
            self.pubkey = Key.import_pub(self.pkey)
            #print("finger", self.pubkey.fingerprint())
            #print("validate", self.pubkey.validate())

            if conf.pgdebug > 6:
                print (self.pubkey)
        except:
            print("Cannot import public key.", sys.exc_info())
            support.put_exception("import key")
            self.client(["quit"])
            self.close();
            sys.exit(0)

        #if conf.pgdebug > 1:
        #    print("Got ", self.pubkey) #, "size =", self.pubkey.size())

        # Generate communication key
        conf.sess_key = base64.b64encode(Random.new().read(128))
        sss = SHA256.new(); sss.update(conf.sess_key)

        #print("sess_key", conf.sess_key[:24])
        #cipher = PKCS1_v1_5.new(self.pubkey)
        #cipher = PKCS1_OAEP.new(self.pubkey)
        cipher = self.pubkey
        #print(dir(cipher))
        #print ("cipher", cipher.can_encrypt())

        if conf.pgdebug > 3:
            support.shortdump("conf.sess_key", conf.sess_key )

        if conf.sess_key:
            sess_keyx = cipher.encrypt(conf.sess_key)
            #print("sess_keyx", sess_keyx.encode()[:24])

            #self.privkey = Key.import_priv(privtest)
            #print("validate", self.privkey.validate())
            #print("finger", self.privkey.fingerprint())
            #sess_keyx3 = self.privkey.decrypt(sess_keyx)
            #print(sess_keyx3)

            ttt = SHA256.new(); ttt.update(sess_keyx.encode())

            if conf.pgdebug > 5:
                print("sess_keyx", crysupp.hexdump(sess_keyx.encode(), 24))
        else:
            sess_keyx = ""

        #print("Key Hexdigest", ttt.hexdigest()[:16])
        resp3 = self.client(["sess", sss.hexdigest(), ttt.hexdigest(), sess_keyx],
            conf.sess_key2,  False)
        #print("Sess Response:", resp3[1])

        if resp3[0] != "OK":
            print("Error on setting session:", resp3)
            #self.client(["quit"])
            #self.close();
            return resp3

        self.sess = True
        return resp3

def atexit_func(hand, conf):

    ''' Severe connection on exit '''

    try:
        #print("Atexit")
        cresp = hand.client(["quit", ], conf.sess_key)
        #print ("Server quit response:", cresp)
        hand.close();
    except:
        pass

def expect(val, expx, ifyes = "", context = "", ifno = "" ):

    if val == expx:
        #print(ifyes)   # silent if OK
        pass
    else:
        if not ifno:
            ifno = "Unexpected result:",
        print(ifno, "'" + val + "'"  , "!=",  "'" + expx + "'",
                        "Context:", context)

def formatstat(resp, dateidx = 0):
    #print(resp)
    ddd = datetime.datetime.fromtimestamp(int(resp[10 + dateidx]))
    retx = ("%s %-24s %-8d %s" % (
        support.mode2str(int(resp[2])), support.unescape(resp[1]),
                int(resp[8]), ddd) )
    return retx

def show_onerec(hand, aa, conf):
    dec = hand.pb.decode_data(aa[1])[0]
    if conf.pgdebug > 2:
        print("dec:", dec)
    pay = hand.pb.decode_data(dec['payload'])[0]
    if conf.verbose:
        print("pay:", pay)
    else:
        print("payload:", pay['PayLoad'])

def inter_date(begin = None, inter = None):

    dd = datetime.datetime.now()
    if not begin:
        # Beginning of today
        dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            dd = dd.strptime(begin, "%Y-%m-%d+%H:%M")
        except:
            try:
                dd = dd.strptime(begin, "%Y-%m-%d")
                dd = dd.replace(hour=0, minute=0, second=0, microsecond=0)
            except:
                try:
                    yyyy = dd.year
                    dd = dd.strptime(begin, "%m-%d+%H:%M")
                    # Merge it with this year
                    dd = dd.replace(year=yyyy, second=0, microsecond=0)
                except:
                    try:
                        yyyy = dd.year; hhh = dd.hour; mmm = dd.minute
                        dd = dd.strptime(begin, "%m-%d")
                        # Merge it with this year, reset HH:MM
                        dd = dd.replace(year=yyyy, hour=0, minute=0, second=0, microsecond=0)
                    except:
                        raise

    dd_beg = dd + datetime.timedelta(0)
    if inter:
        dd_end = dd_beg + datetime.timedelta(0, inter * 60)
    else:
        dd_end = dd_beg + datetime.timedelta(1)

    return dd_beg, dd_end

def     exit_if_err(cresp, strx = "Exiting:"):
    if cresp[0] != OK:
        print(strx, cresp)
        sys.exit(1)

# EOF