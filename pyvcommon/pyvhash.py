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
PayLoad  = "PayLoad"

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

    def __init__(self, old_data = None):

        self.pb  = pyvpacker.packbin()
        self.rrr = Random.new()

        self.ignore = [Hash, PrevHash, Link, PowRand, Proof]

        if not old_data:
            self.newdata()
        else:
            #print("old_data", old_data)
            self.datax = copy.deepcopy(old_data.datax)

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

        arrx = self.datax
        # Replicate without non participating fields:
        arrx2 = [];
        for aa in sorted(arrx.keys()):
            if aa in self.ignore:
                pass
            else:
                #print("hash element", aa, arrx[aa])
                arrx2.append(arrx[aa])

        #print("hash arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(type(ssss))
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
        hhh = shahex(ssss)
        arrx[Hash] = hhh

    def powarr(self):

        ''' Provide proof of work. Only payload and powhash '''

        arrx = self.datax
        # Replicate without non participating fields:
        arrx2 = [];
        for aa in sorted(arrx.keys()):
            if aa in self.ignore:
                pass
            else:
                #print("hash element", aa, arrx[aa])
                arrx2.append(arrx[aa])
        rr = self.rrr.read(12)
        var = None

        cnt = 0; hhh = ""
        while True:
            arr2[PowRand] =  self.rrr.read(12)
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

        print("pow arr2x", arrx2)
        #print (cnt)
        self.datax |= arrx2

    def linkarr(self, prevhash):

        ''' Add linked hash to previous records '''

        arrx = self.datax
        pow = False
        for aa in range(len(arrx)):
            # POW already complete?
            try:
                if Proof in arrx[aa]:
                    pow = True
                    break
            except:
                pass
        if not pow:
            raise NoProof("Must have POW (Proof Of Work) first.")
            return True

        # Replicate without hash field:
        arrx2 = []; asave = []
        for aa in range(len(arrx)):
            try:
                #print("element", arrx[aa])
                if Link in arrx[aa]:
                    #print("noadd", arrx[aa])
                    pass  # no add
                elif PrevHash in arrx[aa]:
                    #print("noadd", arrx[aa])
                    pass  # no add
                elif PowRand in arrx[aa]:
                    asave.append(arrx[aa])
                elif Hash in arrx[aa]:
                    asave.append(arrx[aa])
                else:
                    arrx2.append(arrx[aa])

            except (AttributeError, TypeError, KeyError):
                arrx2.append(arrx[aa])
            except:
                print (sys.exc_info())
                pass

        arrx2.append({PrevHash: prevhash})

        #print(link, arrx2)
        ssss = self.pb.encode_data("", arrx2)

        #print(type(ssss))
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
        hhh = shahex(ssss)
        #print("asave", asave)
        arrx2 += asave
        arrx2.append({Link: hhh})

        self.datax = arrx2
        return(arrx2)

    # ------------------------------------------------------------------------

    def checkhash(self):

        ''' Check record's hash against the hash filed '''

        arrx = self.datax

        # Early out if not hashed
        if not Hash in arrx:
            return False

        # Replicate without non participating fields:
        arrx2 = [];
        for aa in sorted(arrx.keys()):
            if aa in self.ignore:
                pass
            else:
                #print("hash element", aa, arrx[aa])
                arrx2.append(arrx[aa])

        #print("hash arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(type(ssss))
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
        hhh = shahex(ssss)
        #print("chk arrx2", arrx2)
        hhh = shahex(ssss)
        #print(hhh, arrx[Hash])
        return(hhh == arrx[Hash])

    def checkpow(self):

        ''' Check record's proof of work against the POW filed '''

        arrx = self.datax
        # Replicate without hash field:
        arrx2 = []; org = ""
        for aa in range(len(arrx)):
            try:
                if PayLoad in arrx[aa]:
                    arrx2.append(arrx[aa])
                elif PowRand in arrx[aa]:
                    arrx2.append(arrx[aa])
                elif Proof in arrx[aa]:
                    org = arrx[aa][Proof]
                else:
                    pass
            except:
                print (sys.exc_info())
                pass
        #print("chk arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
        hhh = shahex(ssss)
        #print ("org", org, hhh)
        return org == hhh

    def checklink(self):

        ''' Check record's link hash against the previos hash filed '''

        arrx = self.datax

        # Replicate without hash field:
        arrx2 = []; org = ""
        for aa in range(len(arrx)):
            try:
                #print("element", arrx[aa])
                if Link in arrx[aa]:
                    org =  arrx[aa][Link]
                    pass  # no add
                elif Hash in arrx[aa]:
                    pass  # no add
                elif PowRand in arrx[aa]:
                    pass  # no add
                else:
                    arrx2.append(arrx[aa])
            except (AttributeError, TypeError, KeyError):
                arrx2.append(arrx[aa])
            except:
                print (sys.exc_info())
                pass
        #print("arrx2", arrx2)
        ssss = self.pb.encode_data("", arrx2)
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
        hhh = shahex(ssss)
        #print (hhh, org)
        return(hhh == org)

    def _getpayvar(self):

        ''' Internal: get reference to payload '''
        var = None
        for aa in range(len(self.datax)):
            #print("iter", self.datax[aa])
            if type(self.datax[aa]) == type({}):
                #print("var", self.datax[aa])
                if "PayLoad" in self.datax[aa]:
                    #print("payload")
                    var = self.datax[aa]["PayLoad"]
        if not var:
            raise ValueError("Cannot find Payload field.")
        return var

    def addpayload(self, newpay):

        '''Add new entry to payload. Override existing values. '''

        #var = self._getpayvar()
        self.datax |= newpay

    def delpayload(self, paykey):

        ''' Delete key from payload. Will not delete default key '''

        if paykey == "Default":
            print ("Cannot delete default key", "'" + paykey +"'.")
            return
        var = self._getpayvar()
        del var[paykey]

# EOF
