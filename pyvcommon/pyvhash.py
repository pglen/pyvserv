#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time, copy
import struct, stat, base64, random, zlib, uuid, datetime

from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.Hash import SHA256

__doc__ = \
'''

    This module is responsible for the operation of the blockchain.
    The Proof of Work is in Python, but calling 'C' modules. One possible
    improvement is to call out to a specially crafted 'C' module. Please
    be forwarned that replicating the python packer function is
    going to be a doosy task.
    (calling back to PY from C would defeat the speedup)

'''

base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base, '../'))

#sys.path.append(os.path.join(base, '../../'))
#sys.path.append(os.path.join(base,  '../../../pypacker'))

import support, pyvpacker, crysupp

Hash     = "_Hash"
Link     = "_Link"
PrevHash = "_PrevHash"
PowRand  = "_PowRand"
Proof    = "_Proof"
PayLoad  = "payload"
Header   = "header"

def DefPayload():
    return {PayLoad : { "Default": "None"}}

def DefHeader():
    return {Header : str(uuid.uuid1())}

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

# Enable the bigger one for production
#USEHASH = SHA512
USEHASH = SHA256

class BcData():

    '''
        This class manipulates the block chain data.
        Use it to create / add / remove / modify payload.
    '''

    def __init__(self, old_data = None, pgdebug = 0):

        self.pb  = pyvpacker.packbin()
        self.rrr = Random.new()
        self.pgdebug = pgdebug
        self.hash_ignore = [Hash, PrevHash, Link, PowRand, Proof]
        self.pow_ignore = [Hash, PrevHash, Link, Proof]
        self.link_ignore = [Hash, Link, Proof]

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
        # Add Expected fields:
        if not PayLoad in self.datax:
            self.datax |= DefPayload()
        if not Header in self.datax:
            self.datax |= DefHeader()

        if self.pgdebug:
            print(self.datax)

    def newdata(self):

        ''' Create default (new) data for blockchain '''

        uuu = uuid.uuid1()
        #dd = datetime.datetime.fromtimestamp(\
        #            (uuu.time - 0x01b21dd213814000)*100/1e9)
        #print(dd)
        # Has to be one payload for minimum
        self.datax = {"Header" : str(uuu),  PayLoad : { "Default": "None"} }

    def allarr(self, prevhash):

        ''' Exec all ops '''

        self.hasharr()
        self.powarr()
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
        ssss  = bytes(ssss, "utf-8")
        hhh = shahex(ssss)
        self.datax[Hash] = hhh

    def powarr(self):

        ''' Provide proof of work. Only payload and powerhash '''

        # Replicate without non participating fields:
        arrx2 = {};
        for aa in sorted(self.datax.keys()):
            if aa in self.pow_ignore:
                pass
            else:
                #print("hash element", aa, self.datax[aa])
                arrx2 |= {aa : self.datax[aa]}
        var = None
        cnt = 0; hhh = ""
        while True:
            arrx2[PowRand] =  self.rrr.read(12)
            ssss = self.pb.encode_data("", arrx2)
            #print(ssss)
            ssss  = bytes(ssss, "utf-8")
            hhh = shahex(ssss)
            cnt += 1
            if cnt >= 100000:
                break
            if hhh[-3:] == '000':
                break
            #print(hhh)

        self.datax[PowRand] = arrx2[PowRand]
        self.datax[Proof] = hhh
        #print("pow arr2x", arrx2)
        #print ("Proof", hhh)

        #print (cnt)
        self.datax |= arrx2

    def linkarr(self, prevhash):

        ''' Add linked hash to previous records '''

        pow = False
        if not self.datax[Proof]:
            raise NoProof("Must have POW (Proof Of Work) first.")
            return True

        arrx2 = {};
        for aa in sorted(self.datax.keys()):
            if aa in self.link_ignore:
                pass
            else:
                #print("hash element", aa, self.datax[aa])
                arrx2 |= {aa : self.datax[aa]}
        var = None
        cnt = 0; hhh = ""

        arrx2[PrevHash] = prevhash

        #print("arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)

        #print(type(ssss))
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
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
        ssss  = bytes(ssss, "utf-8")
        hhh = shahex(ssss)
        #print("chk arrx2", arrx2)
        hhh = shahex(ssss)
        #print(hhh, self.datax[Hash])
        return(hhh == self.datax[Hash])

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
        var = None
        cnt = 0; hhh = ""
        ssss = self.pb.encode_data("", arrx2)
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
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

        #print("arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
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
