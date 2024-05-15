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

#{'header': 'ea7ac618-12b3-11ef-8947-339547f9084f',
#'PayLoad': {
#   'Default': 'None',
#   -'nuuid': 'f1a46168-1283-11ef-8947-339547f9084f',
#   -'name': 'qqq',
#   -'ndob': '1/1/1',
#   -'nnow': '2024-05-15T02:25:37',
#   -'now': '2024-05-15T08:09:01',
#   -'noper': 'admin',
#   -'uuid': 'e4919b8c-12b3-11ef-8947-339547f9084f',
#   -'vguid': '67e1d37f-7eec-46f3-ba99-fde5ebc296cf',
#   -'vouid': '40ad55ec-1281-11ef-8947-339547f9084f',
#   -'buuid': '101e4a0a-1284-11ef-8947-339547f9084f',
#   -'voper': 'admin',
#   -'bname':  'wwww',
#   -'dob': '2/2/',
#   -'vprim': '555',
#   -'vsec': '',
#   -'vnotes': '',
#   'can1': '111', 'can2': '222', 'can3': '333', 'can4': '44',
#   'can5': '555', 'can6': '666', 'can7': '77', 'can8': '88'
#},
#'now': 'Wed, 15 May 2024 08:09:01',
#'stamp': '1715774941.0', 'iso': '2024-05-15T08:09:01',
#'Replicated': 0,
#'_Hash': '013771ed35a03a423ba0f696c5c5692807b14d955854c1e144de52c8176f49e2',
#'_PowRand': b'\xf5\xfc\xcd\xd2\xc5\xb7z0V\xfa\x9f\x92', '_Proof': 'b354af

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
    pvh.addpayload({'now':  pgtests.randisodate() })
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