#!/usr/bin/env python

from __future__ import print_function

import os, sys, getopt, signal, select, string, time
import struct, stat, base64, random, zlib

from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.Hash import SHA256

base = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(base, '../'))
sys.path.append(os.path.join(base, '../../'))
sys.path.append(os.path.join(base,  '../../../pypacker'))

import support, pypacker, crysupp

Hash     = "_Hash"
Link     = "_Link"
PrevHash = "_PrevHash"
PowRand  = "_PowRand"
Proof    = "_Proof"

pb  = pypacker.packbin()
rrr = Random.new()

class NoProof(Exception):

    def __init__(self, strx):
        self.strx = strx
        pass
    def __repr__(self):
        return self.strx
        pass

def shahex(val):

    hh = SHA512.new();
    hh.update(val)
    hhh = hh.hexdigest()
    return hhh

def hasharr(arrx):

    # Replicate without hash field:
    arrx2 = []; asave = []
    for aa in range(len(arrx)):
        #print("hash element", arrx[aa])
        try:
            if Hash in arrx[aa]:
                #print("noadd", arrx[aa])
                pass  # no add
            elif PrevHash in arrx[aa]:
                asave.append(arrx[aa])
            elif Link in arrx[aa]:
                asave.append(arrx[aa])
            elif PowRand in arrx[aa]:
                asave.append(arrx[aa])
            elif Proof in arrx[aa]:
                print("asave proof", arrx[aa])
                asave.append(arrx[aa])
            else:
                arrx2.append(arrx[aa])

        except (AttributeError, TypeError, KeyError):
            arrx2.append(arrx[aa])
        except:
            print (sys.exc_info())
            pass

    #print("arrx2", arrx2)
    ssss = pb.encode_data("", arrx2)

    #print(type(ssss))
    #print(ssss)
    ssss  = bytes(ssss, "utf-8")
    hhh = shahex(ssss)
    #print("asave", asave)
    arrx2 += asave
    arrx2.append({Hash: hhh})

    return(arrx2)

def powarr(arrx):

    # Replicate without pow and random:
    arrx2 = []; asave = []
    for aa in range(len(arrx)):
        try:
            # print("element", arrx[aa])
            if Proof in arrx[aa]:
                pass  # no add
            elif PowRand in arrx[aa]:
                pass  # no add
            elif PrevHash in arrx[aa]:
                asave.append(arrx[aa])
            elif Link in arrx[aa]:
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
    rr = rrr.read(12)
    var = None
    arrx2.append({PowRand: rr})
    for aa in range(len(arrx2)):
            try:
                if arrx2[aa][PowRand]:
                    # Mark place
                    var = arrx2[aa]
                    break
            except:
                pass

    #print("pow arr2x", arrx2)
    cnt = 0
    while True:
        ssss = pb.encode_data("", arrx2)
        #print(ssss)
        ssss  = bytes(ssss, "utf-8")
        hhh = shahex(ssss)
        cnt += 1
        if cnt >= 100000:
            break
        if hhh[-3:] == '000':
            break
        #print(hhh)
        var[PowRand] = rrr.read(12)

    #print (cnt)
    #print("asave", asave)
    arrx2 += asave
    arrx2.append({Proof: hhh})

    return(arrx2)

def linkarr(arrx, prevhash):

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

        except (AttributeError, TypeError):
            arrx2.append(arrx[aa])

        except KeyError:
            pass
        except:
            print (sys.exc_info())
            pass

    arrx2.append({PrevHash: prevhash})

    #print(link, arrx2)
    ssss = pb.encode_data("", arrx2)

    #print(type(ssss))
    #print(ssss)
    ssss  = bytes(ssss, "utf-8")
    hhh = shahex(ssss)
    #print("asave", asave)
    arrx2 += asave
    arrx2.append({Link: hhh})

    return(arrx2)

# ------------------------------------------------------------------------

def checkhash(arrx):

    # Replicate without hash field:
    arrx2 = []; org = ""
    for aa in range(len(arrx)):
        try:
            #print("element", arrx[aa])
            if Hash in arrx[aa]:
                org = arrx[aa][Hash]
                pass  # no add
            elif PowRand in arrx[aa]:
                pass  # no add
            elif Proof in arrx[aa]:
                pass  # no add
            elif Link in arrx[aa]:
                #print("noadd", arrx[aa])
                pass  # no add
            elif PrevHash in arrx[aa]:
                #print("noadd", arrx[aa])
                pass  # no add
            else:
                arrx2.append(arrx[aa])
        except (AttributeError, TypeError, KeyError):
            arrx2.append(arrx[aa])
        except:
            print (sys.exc_info())
            pass
    #print("arrx2", arrx2)
    ssss = pb.encode_data("", arrx2)
    #print(ssss)
    ssss  = bytes(ssss, "utf-8")
    hhh = shahex(ssss)
    #print (hhh, org)
    return(hhh == org)

def checkpow(arrx):

    # Replicate without hash field:
    arrx2 = []; org = ""
    for aa in range(len(arrx)):
        try:
            #print("element", arrx[aa])
            if Hash in arrx[aa]:
                pass  # no add
            elif Link in arrx[aa]:
                #print("noadd", arrx[aa])
                pass  # no add
            elif PrevHash in arrx[aa]:
                #print("noadd", arrx[aa])
                pass  # no add
            elif Proof in arrx[aa]:
                org =  arrx[aa][Proof]
                pass  # no add
            else:
                arrx2.append(arrx[aa])
        except (AttributeError, TypeError, KeyError):
            arrx2.append(arrx[aa])
        except:
            print (sys.exc_info())
            pass
    #print("arrx2", arrx2)
    ssss = pb.encode_data("", arrx2)
    #print(ssss)
    ssss  = bytes(ssss, "utf-8")
    hhh = shahex(ssss)
    #print (hhh, org)
    return(hhh == org)

def checklink(arrx):

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
    ssss = pb.encode_data("", arrx2)
    #print(ssss)
    ssss  = bytes(ssss, "utf-8")
    hhh = shahex(ssss)
    #print (hhh, org)
    return(hhh == org)

# EOF
