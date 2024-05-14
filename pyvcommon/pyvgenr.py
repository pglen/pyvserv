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

import support, pyvpacker, crysupp, pyvhash

from pyvguicom import pgutils, pgtests

__doc__ = \
'''

    This module generates demo records. The basic structure below.
'''

#{'Default': 'None', 'Test': 'test', 'nuuid':
#'685eac99-112e-11ef-8e2a-d970e1627f70', 'name': 'Nuf Kklnpkjvmyl', 'ndob':
#'1983/02/01', 'nnow': '2024-05-13T09:40:48', 'noper':
#'dsdSzxc3nCYyTI7eqhrp', 'uuid': '685eac9a-112e-11ef-8e2a-d970e1627f70',
#'vguid': '685eac9b-112e-11ef-8e2a-d970e1627f70', 'vouid':
#'685eac9c-112e-11ef-8e2a-d970e1627f70', 'now': '2024-05-13T09:40:48',
#'buuid': '685eac9d-112e-11ef-8e2a-d970e1627f70', 'voper': 'MCwTzbzrfs',
#'bname': 'hy0RQw5wNClMWtQWOqnEt', 'dob': '2002/07/12', 'can1': 'f S1Jt',
#'can2': 'tyr84wVvEv', 'can3': 'LIsxW3b1', 'can4': 'LtRwUaQ koiGN0T2kb',
#'can5': 'Z4rrO7ANAvR82TmaS7BO9U', 'vprim': 'Z4rrO7ANAvR82TmaS7BO9U',
#'can6': 'Fq9V9U0epEH9Lrsq', 'can7': 'KDUG0zGoPOQoVaw5XZe', 'vsec':
#'KDUG0zGoPOQoVaw5XZe', 'can8': 'XiWH6CH77GkiK', 'vnotes': 'mO0p1vpFC1
#j7tq95rEu5qOc7'}


# Vote structure: Sun 12.May.2024

#Save_data 730f3e8a-10c2-11ef-8e2a-d970e1627f70
#{'nuuid': 'c83c6562-0867-11ef-871c-6d4329725b1a',
#'name': 'Peter Glen', 'ndob': '1959/11/20', 'nnow': '2024-05-02T05:38:53',
#'noper': 'admin', 'uuid': '730f3e8a-10c2-11ef-8e2a-d970e1627f70',
#'vguid': '57d626a8-719c-4fc0-8bfa-62c214da695c',
#'vouid': '24573422-079a-11ef-8787-539d6f89ec87',
#'now': '2024-05-12T20:48:01', 'voper': 'admin',
#'buuid': '09269680-079e-11ef-8787-539d6f89ec87',
#'bname': 'New Test Ballot', 'dob': '2024/1/2',
#'vprim': 'John Doe', 'vsec': 'test',
#'vnotes': '', 'can1': 'John Doe', 'can2': 'Jane Dow',
#'can3': 'Johan Citizen', 'can4': 'Jorge Naturez',
#'can5': 'Jill Carpenter', 'can6': 'Jack Savage',
#'can7': 'James Folie', 'can8': 'Joe Cry'}

def genvrec(putkey = None):

    pvh = pyvhash.BcData()
    # We mark this as 'test' so it can stay in the chain, if desired
    pvh.addpayload({"Test": "test" ,})
    dd = datetime.datetime.now()
    dd = dd.replace(microsecond=0)

    pvh.addpayload({'nuuid': str(uuid.uuid1()) })
    pvh.addpayload({'name': pgtests.simname(12) })
    pvh.addpayload({'ndob': pgtests.randate() })
    pvh.addpayload({'nnow': pgtests.randisodate() })
    pvh.addpayload({'noper': pgtests.randstr(random.randint(6, 22)) })
    pvh.addpayload({'uuid':  str(uuid.uuid1()) })
    pvh.addpayload({'vguid': str(uuid.uuid1()) })
    pvh.addpayload({'vouid': str(uuid.uuid1()) })

    pvh.addpayload({'now': dd.isoformat()} )

    pvh.addpayload({'buuid': str(uuid.uuid1()) })
    pvh.addpayload({'voper': pgtests.randstr(random.randint(6, 22)) })
    pvh.addpayload({'bname': pgtests.randstr(random.randint(6, 22)) })
    pvh.addpayload({'dob':   pgtests.randate()})

    lenx = 8
    randx =  random.randint(0, lenx-1)
    randy =  random.randint(0, lenx-1)
    for aa in range(lenx):
        rrr = pgtests.randstrrand(6, 22)
        pvh.addpayload({"can%d" % (aa+1)  : rrr,})

        if aa == randx:
            pvh.addpayload({'vprim': rrr, })
        if aa == randy:
            pvh.addpayload({'vsec': rrr, })

    rrr = pgtests.randstrrand(12, 32)
    pvh.addpayload({'vnotes': rrr})

    if putkey:
        pvh.datax['header'] = putkey

    return pvh

def mainfunct():
    print(genvrec().datax)

if __name__ == '__main__':
    mainfunct()

# EOF