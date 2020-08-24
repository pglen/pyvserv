#!/usr/bin/env python

import pytest

from pygcrypt import utils

def test_setui(context):
    mpi = context.mpi(1234)
    assert mpi.value == 1234
    mpi = context.mpi(-1234)
    assert mpi.value == -1234

def test_repr(context):
    mpi_int = context.mpi(1234)
    mpi_int.fmt = 'USG'
    assert repr(mpi_int) == repr(b'\x04\xd2')
    mpi_op = context.mpi(b'Testing stuff')
    assert mpi_op.value == b'Testing stuff'
    assert repr(mpi_op) == repr(b'Testing stuff')

def test_set(context):
    mpi_a = context.mpi(1234)
    mpi_b = context.mpi(1234)
    mpi_b.mpi = mpi_a.mpi

    assert mpi_b == mpi_a

def test_copy(context):
    mpi_a = context.mpi(1234)
    mpi_b = mpi_a.copy()
    assert mpi_b == mpi_a

def test_mul(context):
    mpi = context.mpi(3)
    assert mpi * 3 == 9
    mpi *= 3
    assert mpi == 9
    assert mpi * mpi == 81
    mpi *= mpi
    assert mpi == 81

def test_add(context):
    mpi = context.mpi(3)
    assert mpi + 3 == 6
    mpi += 3
    assert mpi == 6
    assert mpi + mpi == 12
    mpi += mpi
    assert mpi == 12

def test_sub(context):
    mpi = context.mpi(12)
    assert mpi - 6 == 6
    mpi -= 6
    assert mpi == 6
    assert mpi - mpi == 0
    mpi -= mpi
    assert mpi == 0

def test_div(context):
    mpi = context.mpi(81)
    assert mpi // 9 == 9
    mpi //= 9
    assert mpi == 9
    assert mpi // mpi == 1
    mpi //= mpi
    assert mpi == 1

def test_mod(context):
    mpi = context.mpi(6)
    assert mpi % 4 == 2
    mpi %= 4
    assert mpi == 2
    assert mpi % mpi == 0
    mpi %= mpi
    assert mpi == 0

def test_addm(context):
    mpi_a = context.mpi(6)
    mpi_b = mpi_a.copy()
    mpi_c = mpi_b.copy()
    mpi_c.value = 5
    assert mpi_a.addm(mpi_b, mpi_c) == 2

def test_subm(context):
    mpi_a = context.mpi(6)
    mpi_b = mpi_a.copy()
    mpi_c = mpi_a.copy()
    mpi_c.value = 5
    assert mpi_a.subm(mpi_b, mpi_c) == 0

def test_mulm(context):
    mpi_a = context.mpi(6)
    mpi_b = mpi_a.copy()
    mpi_c = mpi_b.copy()
    mpi_c.value = 5
    assert mpi_a.mulm(mpi_b, mpi_c) == 1

def test_mul2exp(context):
    mpi = context.mpi(4)
    assert mpi.mul2exp(2) == 16

def test_powm(context):
    mpi_a = context.mpi(4)
    mpi_b = mpi_a.copy()
    mpi_c = mpi_a.copy()
    mpi_c.value = 5
    assert mpi_a.powm(mpi_b, mpi_c) == 1

def test_gcd(context):
    mpi_a = context.mpi(6)
    mpi_b = context.mpi(3)
    assert mpi_a.gcd(mpi_b) == 3

def test_invm(context):
    mpi_a = context.mpi(17)
    mpi_b = context.mpi(5)
    assert mpi_a.invm(mpi_b) == 3

def test_inv_abs(context):
    mpi = context.mpi(6)
    mpi = - mpi
    assert mpi == -6
    mpi = abs(mpi)
    assert mpi == 6

def test_swap(context):
    mpi_a = context.mpi(4)
    mpi_b = context.mpi(5)
    (mpi_a, mpi_b) = utils.swap(mpi_a, mpi_b)
    assert mpi_a == 5
    assert mpi_b == 4

def test_snatch(context):
    mpi_a = context.mpi(4)
    mpi_b = context.mpi(10)
    mpi_a = utils.snatch(mpi_b, mpi_a)
    assert mpi_a == 10

def test_isneg(context):
    mpi = context.mpi(5)
    assert utils.isneg(mpi) == False
    mpi = - mpi
    assert utils.isneg(mpi) == True

def test_eq(context):
    mpi = context.mpi(5)
    assert mpi == 5
    assert mpi == mpi.copy()

def tes_ne(context):
    mpi = context.mpi(6)
    assert mpi != 5
    mpi_b = context.mpi(5)
    assert mpi != mpi_b

def test_gt(context):
    mpi_a = context.mpi(5)
    mpi_b = context.mpi(6)
    assert mpi_b > mpi_a
    assert mpi_a > 4

def test_lt(context):
    mpi_a = context.mpi(5)
    mpi_b = context.mpi(6)
    assert mpi_a < mpi_b
    assert mpi_a < 6

def test_ge(context):
    mpi_a = context.mpi(5)
    mpi_b = context.mpi(6)
    assert mpi_b >= mpi_a
    assert mpi_a >= 4

def test_le(context):
    mpi_a = context.mpi(5)
    mpi_b = context.mpi(6)
    assert mpi_a <= mpi_b
    assert mpi_a <= 6

def test_lshift(context):
    mpi_a = context.mpi(4)
    assert mpi_a << 1 == 8
    mpi_a <<= 1
    assert mpi_a == 8

def test_rshift(context):
    mpi_a = context.mpi(4)
    assert mpi_a >> 1 == 2
    mpi_a >>= 1
    assert mpi_a == 2

def test_getbits(context):
    mpi_a = context.mpi(16) #10000
    assert mpi_a[4] == True
    assert mpi_a[1] == False

def test_setbits(context):
    mpi_a = context.mpi(16) #10000
    mpi_a[0] = True
    assert mpi_a == 17
    mpi_a[0] = False
    assert mpi_a == 16

def test_highbit(context):
    mpi_a = context.mpi(16) #10000
    mpi_a.set_highbit(3) #1000
    assert mpi_a == 8
    mpi_a.clear_highbit(3)
    assert mpi_a == 0

def test_len(context):
    mpi_a = context.mpi(16) #10000
    assert len(mpi_a) == 5

def test_flags(context):
    a = utils.randomize(512)
    a.secure = True
    assert a.secure == True
    assert a.plop == None

def test_opaque(context):
    b = b'\x98[\x8f\xc2s\x7f\x00\x00\x98[\x8f\xc2s\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\xb9w\xf6\xe5\x87\xe09\xd5\t\x99InW\t#p`\xee\xa0\x8e\x9f\xcafN\xa5\xa4\xf4\xb7\x82\xd8y\x14W?n"7\xa5\xc6\x88\xb8\x00V\xe1\xbc\x96I\xb7\xbe\xa8\x9e%~A\xd9\xeb\x99\xa8Z\x85\xafjJ:\xad\x1cY\x98\xbe\xde\x98\x05\x91\x19P\x89\xb4\xd3\xdeR7 M\x1d\xe3]\x96\xa7H\xe2t\x16\xa6mO \xda\xf5\xa5y\x9f\xaeb#t\xc5\xcc.\x9a\xe3\xcb3l\xcc\x04\x02\xce\xd4j\x0f\x9e\xb94\x06\xee\xf0\xb8O\xf6\xc4\xb7\xfd\xe3\xe0\xed\x00P\xa0\x03\xd8\x97\xc1\xe9\xb6j\x9bh#\x07\xf3\xfbA^\xd8)\x1e\x83\x89\xbd\xb1~8\xb4E]\xd0+\xb9TE\xd8U\xda\xda\x8f@\x1c+\\"W\xf06\xa4\xce\x91\xcf\t\xab\xd73\xe6s\xf4\x0bh\xd8\x8c\xfd\xb5\x97\x85\xc7\xd8F\xf5\x9d\xb2\x00\xb3/\xc0\x1a\x1br\xa6\x17ko\x9ed#f\x89%sk?"\xd9\xd1\x0f\x9a\x01\xe3\xdcm!\xda^\x13i\x0fJ\xce\xf7PH\xa6\xbe\x19\xe8S\x9c`\x15\x14\xe0>\xfa\xcf\xa4\xec\xcb\xf6\x98#<\x8d\xf4y\xbf\xc9t|\xbd\xf2\x98!2\xd1\x9cv\x1byx\xea\xa4\x1b\xb7:\x926\xa4R^\xf1b\xa6\xcd6\xc0\x05\x89Q\x97\xe8\xcc(\xf3;\xf52\x07\x9a\xcbXD\x8b\xd9\x13f\xc8\xed1\xe9J\x11\n\x1c\n\xec+\xd5k\xf98\x05\x83\x117\x1c\xfc\xd9\x97\xd0o\x9e\xcan\xd32s5\n\x00\xd3\xd3{l\'\xe9\x98\x14\x16\xd1 Z\xfe\xe83\x7f\x00]\t\xbfE\x07\xa1T(\xe5\x1a\x91R\x0fn\x7f\xd92\xd7\xb8?\x10\xbc\xee&\x9aQ%b\xe3\xce\xe7\xd7N\xf6\xd3\xf0G\xb08\x07\xf2\x02\x1cF\x13\xf0h\x82\x98\xdc\xde2u\xd6\xe5)\x96\xab\xdei\t\x82\xbcO\xffrl\xa2\xf5jD"\x01S\x82\x98j\x81a\x05K \x9b\xc15\xc1#\xb3\x176x\xf3M\xf9\xb9\xc4\x96\t\xb0"\xf7e\x18\xb6\x8egN\x1d\'\x1dW\x00\xcb\xba\x8a\xd6\x1erF{\x83\x067g\xea\x06\xbc\xa0\x02\xde\x9e\xf0\xe7\x17&=\xc7Qk\x97\xe2\xec\x86\xc7\x1c\xeeL\xff/\xd9xO\xd6\x8au\xea\x82 \xa1\x98u\xadYs\xa8\x1fY\xd2}~\xcf\xd19\xf9\xd8/\xbf;W$\xa1\x9a\xfc\xfe\x01m\x83}\x98 "\xe1\x8f6\xd6\nama\xfe\xd5w\xee\x0cCa\x0e\xabY\xd4\xf0Z\xbe\x9ca\x96!\xf0\x19\t4\xc5\xa6\x80\x02\x8a?\x8f\xa6\n\x80F&\x04\x1d\xb1\x18\x00[\xdd\xe9V\xb9\xf22\x8b \t\xd0AR\xf12\xd8\x83\xf1u7\xef\xa5NX'
    mpi_a = context.mpi(b)
    assert mpi_a.opaque == True
    assert mpi_a.value == b

def test_prime(context):
    mpi = context.mpi(3)
    assert mpi.isprime() == True
    mpi = context.mpi(4)
    assert mpi.isprime() == False
