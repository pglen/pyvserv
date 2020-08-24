#!/usr/bin/env python

import pytest

import sys
print(sys.path)

from pygcrypt import ciphers

def test_init():
    """
    Let's test the initialisation of a cipher
    """
    c = ciphers.Cipher(b'AES', u'CBC')
    assert c.algo == b'AES'
    assert c.mode == 'CBC'

def test_get_info():
    """
    Let's test getting keylen or blocksize from the cipher
    """
    c = ciphers.Cipher(b'AES', u'CBC')
    assert c.keylen == 16
    assert c.blocksize == 16

def test_set_key_iv():
    """
    Let's try to set a key and an iv on a cipher.
    """
    c = ciphers.Cipher(b'AES', u'CBC')
    c.key = '0123456789ABCDEF'
    assert c.key == b'0123456789ABCDEF'
    c.iv = '0123456789ABCDEF'
    assert c.iv == b'0123456789ABCDEF'

def test_reset_cipher():
    c = ciphers.Cipher(b'AES', u'CBC')
    c.key = '0123456789ABCDEF'
    c.iv = '0123456789ABCDEF'
    c.reset()
    assert c.key == b'0123456789ABCDEF'
    assert c.iv == None

def test_encrypt_decrypt():
    c = ciphers.Cipher(b'AES', u'CBC')
    c.key = '0123456789ABCDEF'
    c.iv = '0123456789ABCDEF'
    encrypt = c.encrypt(b'0123456789ABCDEF')
    c.reset()
    c.iv = '0123456789ABCDEF'
    assert c.decrypt(encrypt) == b'0123456789ABCDEF'
