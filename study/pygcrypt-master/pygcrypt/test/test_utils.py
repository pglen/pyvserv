#!/usr/bin/env python

import pytest

from pygcrypt import utils

def test_keyderive(context):
    assert utils.key_derive("A passphrase is here!", "8bitsalt") == b'!\n\xe9qjQKK\x0c\xc2,\xad\x8b\x9c\x03O'
    with pytest.raises(Exception):
        # We should fail with this salt of len != 8 for the default algo
        utils.key_derive("yay, passphrase", "123")

def test_scan(context):
    mpi =  utils.scan(b"\x07\xffh\xbc'\xd0\x10\xa6Z7\xe0%kg\xd0#\xf8dN R6V\xabBel\x17?\x02k\xa4H>\xceKZ%\xe3\xd9\n\x00\xad==}\xd1\xdb\x08\x1e&\xed\x93\xca\xdc\xfa\xa1 \xa4\x86\xf9\xd0'\xfb\x14D\x0fC\xce0B)\x13\x92~\xf6\xa0\x82b\x9b\n\x005\x00\x19\xe1\xd0\x99\xc0\xc7\x0b\xb6\xa1\xe3\x84\x86\xc2\xfe\xb6\x93\x8b\xaa\xfa\xe8<z2\x01\x14BF#\xbag\x7f\x12\x00ce\x13\x9f\x151\x1a\x88\x95\xd8u|p/\xa2Z.\x1f\x88\xd1._Sc=\x9d\xd6\xc5\x82\xe6B\tS\xbd\xc96\x9d\x02\xcc-S\x16u+\x17Xc\x1b\xda\x07\xe1\x97\x04`Il\xfaWx\x0b1 r\x87?\xbe\x9a\x1e:J\xaa\xdf$\xd2j\xd2\x9c\xb4B\xceav\x06\t\xcb\xcb\xe75b\x00\x98$>3\xb5\x84\xfc<R[\x9f\x9eI\x9a)~\x8b\xd4\xcf\xa7cB\x17\xd0\xbc\xaf\x1dn\xa1\xd2\xeb\x90\xfak\xfb\x1b\xc9-\x10\x90\x0e\x07\tm\x12\xfc.\xd9\x94\xbe\x18", 'PGP')

def test_mpi_print(context):
    mpi = context.mpi(1234)
    assert utils.mpi_print(mpi, 'STD') == repr(mpi)

def test_utils_random(context):
    # Random number might start with a 0, which doesn't count in length
    assert len(utils.rand(128)) <= 128
    assert utils.rand(128) != utils.rand(128)

def test_utils_srandom(context):
    # Random number might start with a 0, which doesn't count in length
    assert len(utils.srand(128)) <= 128
    assert utils.srand(128) != utils.srand(128)
