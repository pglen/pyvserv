#!/usr/bin/env python

import pytest

from pygcrypt.ecurve import ECurve
from pygcrypt.gctypes.ec_point import Point

def test_get(context):
    ec = ECurve(curve='secp192r1')
    point = Point(ec.curve)

    x = context.mpi(0)

    assert point.x == x
    assert point.y == x
    assert point.z == x

def test_set(context):
    ec = ECurve(curve='secp192r1')
    point = Point(ec.curve)

    x = context.mpi(1)
    y = context.mpi(1)
    z = context.mpi(1)

    point.x = x
    point.y = y
    point.z = z

    assert point.x == x
    assert point.y == y
    assert point.z == z

def test_affine(context):
    ec = ECurve(curve='secp192r1')
    point = Point(ec.curve)

    x = context.mpi(5)
    y = context.mpi(5)

    assert point.affine(x, y) == (5, 5)

def test_mul(context):
    ec = ECurve(curve='secp192r1')
    point = Point(ec.curve)

    x = context.mpi(1)
    y = context.mpi(1)
    z = context.mpi(1)

    (point.x, point.y, point.z) = (x, y, z)

    a = context.mpi(2)

    assert ((point * a).x.value, (point * a).y.value, (point * a).z.value) == (6277101735386680763835789423207666416083908700390324961271, 6277101735386680763835789423207666416083908700390324961271, 2)
    point *= a
    assert (point.x.value, point.y.value, point.z.value) == (6277101735386680763835789423207666416083908700390324961271, 6277101735386680763835789423207666416083908700390324961271, 2)

def test_add(context):
    ec = ECurve(curve='secp192r1')
    point_a = Point(ec.curve)
    point_b = Point(ec.curve)

    x = context.mpi(1)
    y = context.mpi(1)
    z = context.mpi(1)

    (point_a.x, point_a.y, point_a.z) = (x, y, z)
    (point_b.x, point_b.y, point_b.z) = (x, y, z)

    assert ((point_a + point_b).x.value, (point_a + point_b).y.value, (point_a + point_b).z.value) == (6277101735386680763835789423207666416083908700390324961271, 6277101735386680763835789423207666416083908700390324961271, 2)
    point_a += point_b
    assert (point_a.x.value, point_a.y.value, point_a.z.value) == (6277101735386680763835789423207666416083908700390324961271, 6277101735386680763835789423207666416083908700390324961271, 2)

def test_double(context):
    ec = ECurve(curve='secp192r1')
    point = Point(ec.curve)

    x = context.mpi(1)
    y = context.mpi(1)
    z = context.mpi(1)

    (point.x, point.y, point.z) = (x, y, z)

    point.double()
    assert (point.x.value, point.y.value, point.z.value) == (6277101735386680763835789423207666416083908700390324961271, 6277101735386680763835789423207666416083908700390324961271, 2)

def test_oncurve(context):
    ec = ECurve(curve='secp192r1')
    point = Point(ec.curve)

    assert point.isoncurve() == False
    assert ec['g'].isoncurve() == True
