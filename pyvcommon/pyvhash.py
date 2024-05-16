#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time, copy
import struct, stat, base64, random, zlib, uuid, datetime

try:
    import psutil
except:
    psutil = None
    pass

from Crypto import Random
from Crypto.Hash import SHA256

#base = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(base, '../'))

import support, pyvpacker, crysupp

__doc__ = \
'''

    This module is responsible for the operation of the blockchain.
    The Proof of Work is in Python, but calling 'C' modules. One possible
    improvement is to call out to a specially crafted 'C' module. Please
    be forwarned that replicating the python packer function is
    going to be a doosy task.
    (calling back to PY from C would defeat the speedup)

'''

Hash     = "_Hash"
Link     = "_Link"
PrevHash = "_PrevHash"
PowRand  = "_PowRand"
Proof    = "_Proof"
Repli    = "Replicated"
PayLoad  = "PayLoad"
Header   = "header"
Now      = "now"
Stamp    = "stamp"
Iso      = "iso"

datefmt = '%a, %d %b %Y %H:%M:%S'
isostr  = "%Y-%m-%dT%H:%M:%S"

# This is the chack charater on the trailing hash
# Make sure both client and server has the same ZERO

ZERO = '0'

def DefPayload():
    return {PayLoad : { "Default": "None"}}

def DefHeader():
    return {Header : str(uuid.uuid1())}

def DefNow(dt):
    fdt = dt.strftime(datefmt)
    return {'now' : fdt}

def DefISO(dt):
    fdt = dt.isoformat()
    return {'iso' : fdt}

def DefStamp(dt):
    return {'stamp' : str(dt.timestamp())}

def DefRep():
    return {Repli : 0}

class NoProof(Exception):

    def __init__(self, strx):
        self.strx = strx
        pass
    def __repr__(self):
        return self.strx
        pass

def shahex(val):

    ''' Shorthand to exec hash op '''

    hh = USEHASH.new();
    hh.update(val)
    hhh = hh.hexdigest()
    return hhh

# Enable the bigger one if needed.
#USEHASH = SHA512
USEHASH = SHA256

class BcData():

    '''
        This class manipulates the block chain data.
        Use it to create / add / remove / modify payload.
    '''

    def __init__(self, old_data = None, pgdebug = 0, header = None):

        self.pb  = pyvpacker.packbin()
        self.rrr = Random.new()
        self.pgdebug = pgdebug
        self.hash_ignore = [Hash, PrevHash, Link, PowRand, Proof, Repli]
        self.pow_ignore = [Hash, PrevHash, Link, Proof, Repli]
        self.link_ignore = [Hash, Link, Proof, Repli]

        self.maxtry = 25000
        self.num_zeros = 4
        self.zero = ZERO
        self.cnt = 0
        self.weak = False

        #print("old_data", old_data)
        #print("type", type(old_data))
        self.datax = {}
        if type(old_data) == type(self):
            self.datax = copy.deepcopy(old_data.datax)
        elif type(old_data) == type({}):
            self.datax = copy.deepcopy(old_data)
        elif type(old_data) == type([]):
            tmpx = {}
            for aa in range(len(old_data) // 2):
                tmpx |= { old_data[aa]: old_data[aa+1], }
                self.datax = copy.deepcopy(tmpx)
        elif type(old_data) == type(None):
            self.newdata()
        else:
            raise TypeError("Cannot create class from %s" % type(old_data))

        # Propagate requested header
        if header:
            self.datax |= { Header : header }

        # Add Expected fields:
        dt = datetime.datetime.now()
        dt = dt.replace(microsecond=0)
        if not PayLoad in self.datax:
            self.datax |= DefPayload()
        if not Header in self.datax:
            self.datax |= DefHeader()

        # This is a lot of datetime variations. The rational is:
        #   a human readable
        #   a machine readable and
        #   an ISO standard date.
        # This is to assist internationalzation and possible hand count.

        if not Now in self.datax:
            self.datax |= DefNow(dt)
        if not Stamp in self.datax:
            self.datax |= DefStamp(dt)
        if not Iso in self.datax:
            self.datax |= DefISO(dt)
        if not Repli in self.datax:
            self.datax |= DefRep()

        if self.pgdebug:
            print(self.datax)

    def newdata(self):

        ''' Create default (new) data for blockchain '''

        uuu = uuid.uuid1()
        #dd = datetime.datetime.fromtimestamp(\
        #            (uuu.time - 0x01b21dd213814000)*100/1e9)
        #print(dd)
        # Has to be one payload for minimum
        self.datax = {Header : str(uuu),  PayLoad : { "Default": "None"} }

    def allarr(self, prevhash):

        ''' Exec all ops '''

        self.hasharr()
        self.powarr()
        self.hasharr()

        self.linkarr(prevhash)
        return self.datax

    def hasharr(self):

        ''' Hash a array of data '''

        # Replicate without non participating fields:
        arrx2 = [];
        for aa in sorted(self.datax.keys()):
            if aa in self.hash_ignore:
                pass
            else:
                #print("hash element", aa, arrx[aa])
                arrx2.append(self.datax[aa])

        #print("hash arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(type(ssss))
        #print(ssss)
        #ssss  = bytes(ssss) #, "utf-8")
        ssss  = ssss.encode()
        hhh = shahex(ssss)
        self.datax[Hash] = hhh

    def powarr(self):

        ''' Provide proof of work. Only payload and powerhash '''

        # Make sure we are not killing the system
        #if psutil:
        #    while True:
        #        #cpu = psutil.cpu_percent(0)
        #        #print("CPU calc", cpu)
        #        if cpu > 60:
        #            print("CPU", cpu)
        #            time.sleep(1)
        #        else:
        #            break
        # Replicate without non participating fields:
        arrx2 = {};
        arrx2[PowRand] = self.rrr.read(12)
        for aa in sorted(self.datax.keys()):
            if aa in self.pow_ignore:
                pass
            else:
                #print("hash element", aa, self.datax[aa])
                arrx2 |= {aa : self.datax[aa]}
        var = None; cnt = 0; hhh = ""
        while True:
            if cnt >= self.maxtry:
                break
            arrx2[PowRand] = self.rrr.read(12)
            arrx3 = []
            # Re arrange to array for consistency
            for aa in sorted(arrx2.keys()):
                #print("sort element", aa, arrx2[aa])
                arrx3.append(aa)
                arrx3.append(str(arrx2[aa]))

            #ssss = self.pb.encode_data("", arrx3)
            ssss = "".join(arrx3)

            #print(ssss)
            #ssss  = bytes(ssss) #, "utf-8")
            ssss  = ssss.encode("cp437")
            hhh = shahex(ssss)
            #print("powarr", cnt, "hash", hhh, self.zero * self.num_zeros)
            if hhh[-self.num_zeros:] == self.zero * self.num_zeros:
                break
            cnt += 1

        #print("Raw gen arrx3", arrx3)
        #print(cnt, hhh)
        self.cnt = cnt
        if hhh[-self.num_zeros:] == self.zero * self.num_zeros:
            #self.datax |= arrx2
            self.datax[PowRand] = arrx2[PowRand]
            self.datax[Proof] = hhh
            return True
        else:
            return False


    def linkarr(self, prevhash):

        ''' Add linked hash to previous records '''

        pow = False
        if not self.datax[Proof]:
            raise NoProof("Must have POW (Proof Of Work) first.")
            return True

        arrx2 = {};
        self.datax[PrevHash] = prevhash

        for aa in sorted(self.datax.keys()):
            if aa in self.link_ignore:
                pass
            else:
                #print("hash element", aa, self.datax[aa])
                arrx2 |= {aa : self.datax[aa]}
        var = None; cnt = 0; hhh = ""
        #print("raw arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(type(ssss))
        #print(ssss)
        #ssss  = bytes(ssss) #, "utf-8")
        ssss  = ssss.encode("cp437")

        hhh = shahex(ssss)
        #print("asave", asave)
        arrx2[Link] = hhh
        self.datax |= arrx2
        return()

    # ------------------------------------------------------------------------

    def checkhash(self):

        ''' Check record's hash against the hash filed '''

        # Early out if not hashed
        if not Hash in self.datax:
            return False

        # Replicate without non participating fields:
        arrx2 = [];
        for aa in sorted(self.datax.keys()):
            if aa in self.hash_ignore:
                pass
            else:
                #print("hash element", aa, arrx[aa])
                arrx2.append(self.datax[aa])

        #print("hash arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(type(ssss))
        #print(ssss)
        #ssss  = bytes(ssss) #, "utf-8")
        ssss  = ssss.encode("cp437")

        hhh = shahex(ssss)
        #print("chk arrx2", arrx2)
        hhh = shahex(ssss)
        #print(hhh, self.datax[Hash])
        return(hhh == self.datax[Hash])

    def getstrength(self):

        ''' Get the number of zeros as strength '''

        strength = 0

        # No proof ...
        if '_Proof' not in self.datax:
            return strength

        for aa in range(1, 8):
            if self.datax['_Proof'][-aa] != self.zero:
                break
            strength += 1
        return strength

    def checkpow(self):

        ''' Check record's proof of work against the POW filed '''

        # Early out if not hashed
        if not Proof in self.datax:
            return False

        # Replicate without non participating fields:
        arrx2 = {};
        for aa in sorted(self.datax.keys()):
            if aa in self.pow_ignore:
                pass
            else:
                #print("hash element", aa, self.datax[aa])
                arrx2 |= {aa : self.datax[aa]}
        # Re arrange to array for consistency
        arrx3 = []
        for aa in sorted(arrx2.keys()):
            arrx3.append(aa)
            arrx3.append(str(arrx2[aa]))

        var = None; cnt = 0; hhh = ""
        #print("Raw chk arrx2", arrx3)
        #ssss = self.pb.encode_data("", arrx3)
        ssss = "".join(arrx3)
        #print(ssss)
        #ssss  = bytes(ssss) #, "utf-8")
        ssss = ssss.encode("cp437")
        hhh = shahex(ssss)
        #print ("Proof", self.datax[Proof], hhh)
        return self.datax[Proof] == hhh

    def checklink(self):

        ''' Check record's link hash against the previos hash filed '''

        # Replicate without non participating fields:
        arrx2 = {};
        for aa in sorted(self.datax.keys()):
            if aa in self.link_ignore:
                pass
            else:
                #print("hash element", aa, self.datax[aa])
                arrx2 |= {aa : self.datax[aa]}
        #print("raw arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(ssss)
        #ssss  = bytes(ssss) #) #, "utf-8")
        ssss = ssss.encode("cp437")
        hhh = shahex(ssss)
        #print (hhh, self.datax[Link])
        return(hhh == self.datax[Link])

    def addpayload(self, newpay):

        '''Add new entry to payload. Override existing values. '''

        #var = self._getpayvar()
        self.datax[PayLoad] |= newpay

    def delpayload(self, paykey):

        ''' Delete key from payload. Will not delete default key '''

        if paykey == "Default":
            #print ("Cannot delete default key", "'" + paykey +"'.")
            return True
        del self.datax[PayLoad][paykey]

# EOF
