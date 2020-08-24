#!/usr/bin/env python

import pytest

from pygcrypt import hashcontext


def test_init(context):
    h = hashcontext.HashContext(algo='sha256')
    assert h.secure is True
    assert h.hmac is False
    h = hashcontext.HashContext(algo='sha256', secure=False, hmac=True)
    assert h.secure is False
    assert h.hmac is True


def test_valid(context):
    with pytest.raises(Exception):
        hashcontext.HashContext(algo='yadayada')


def test_getattr(context):
    h = hashcontext.HashContext(algo='sha256')
    assert h.algo == b'sha256'.upper()
    assert h.hashlen == 32


def test_enable(context):
    h = hashcontext.HashContext(algo='sha256')
    h.enable('sha512')

    with pytest.raises(Exception):
        h.enable('yadayada')


def test_setkey(context):
    h = hashcontext.HashContext(algo='sha256', hmac=True)
    assert h.hmac is True
    h.setkey(b'What a beautiful key')


def test_write(context):
    h = hashcontext.HashContext(algo='sha256')
    h.write("Let's write things to be hashed")


def test_read(context):
    h = hashcontext.HashContext(algo='sha256')
    h.write(b"Let's write things that will be hashed and with a long, ong text, bger than 32bytes. Stuff ike that. You know, long block of data.")
    hashed_data = h.read()
    assert hashed_data == b'\xb2m\x9a\x97\xe0\xa7\x1c\xe9\x0f<\x93\xee\rK3\x0b\x813|; q\x99\xf6\xef)\xe1\x9c\x93\xceG\xd8'
    assert len(hashed_data) == 32


def test_reset(context):
    h = hashcontext.HashContext(algo='sha256')
    h.write('tototatatiti')
    one = h.read()
    h.reset()
    h.write('tototatatiti')
    assert one == h.read()


def test_copy(context):
    h = hashcontext.HashContext(algo='sha256')
    h.write('yadayada')
    h2 = h.copy()
    assert h.read() == h2.read()


def test_issue2(context):
    """
    Test due to issue 2: https://framagit.org/okhin/pygcrypt/issues/2
    """
    def try_one():
        h = hashcontext.HashContext(algo='SHA512')
        h.write(b'testestsetsetstsststs')
        h.read()

    for i in range(1, 100):
        try_one()
