#!/usr/bin/env python

import pytest

import pygcrypt.errors as errors
from pygcrypt.ecurve import ECurve
from pygcrypt.gctypes.mpi import MPIint
from pygcrypt.gctypes.sexpression import SExpression

def test_get(context):
    ec = ECurve(curve='secp192r1')

    assert isinstance(ec['a'], MPIint)

def test_set(context):
    ec = ECurve(curve='secp192r1')

    a = ec['a'] * 2
    ec['a'] = a
    assert ec['a'] == a

def test_getkey(context):
    sexp = SExpression(b'(public-key (ecc (curve "NIST P-256")(q #0442B927242237639A36CE9221B340DB1A9AB76DF2FE3E171277F6A4023DED146EE86525E38CCECFF3FB8D152CC6334F70D23A525175C1BCBDDE6E023B2228770E#)))')
    ec = ECurve(keyparam=sexp)

    with pytest.raises(errors.GcryptException):
        priv = ec.key(mode=u'SECKEY')
    pub = ec.key(mode=u'PUBKEY')

    assert pub.type == u'public'
