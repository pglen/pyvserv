#!/usr/bin/env python
from ctypes.util import find_library
from sys import getsizeof
import struct

from .._gcrypt import ffi
from .. import errors

lib = ffi.dlopen(find_library("gcrypt"))

"""
This module implements the binding for gcrypt multiple
precision integer library needed for a lot of things.
"""

class MPI(object):
    """
    We want to bind into mpi lib gcrypt. This is a generic class that will be used
    as a mother class for specific MPI objects.
    """
    def __init__(self):
        raise NotImplemented

    def to_bytes(self):
        """
        Convert the MPI a into an external representation described by format 
        (see above) and store it in a newly allocated buffer which address
        will be stored in the variable buffer points to. The number of bytes
        stored in this buffer will be stored in the variable nbytes points to,
        unless nbytes is NULL.

        Even if nbytes is zero, the function allocates at least one byte and
        store a zero there. Thus with formats GCRYMPI_FMT_STD and
        GCRYMPI_FMT_USG the caller may safely set a returned length of 0 to 1
        to represent a zero as a 1 byte string.
        """
        if self.opaque:
            return self.value
        printed = ffi.new("unsigned char **")
        fmt = getattr(lib, u'GCRYMPI_FMT_' + self.fmt)
        nbytes = ffi.new("size_t *")
        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_mpi_aprint(fmt, printed, nbytes, self.mpi)
        if error > 0:
            raise error.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        repr_value = bytes(ffi.buffer(printed[0], nbytes[0]))
        return repr_value

    def __repr__(self):
        return repr(self.to_bytes())

    def copy(self):
        """
        Create a new MPI as the exact copy of a but with the constant and
        immutable flags cleared.

        We will return the copy of the mpi, which will allow us to call this
        function the same way than dict.copy()
        """
        mpi = type(self)()
        mpi.mpi = lib.gcry_mpi_copy(ffi.cast("const gcry_mpi_t", self.mpi))
        return mpi

    def __getattr__(self, attr):
        if hasattr(lib, 'GCRYMPI_FLAG_' + attr.upper()):
            res = bool(lib.gcry_mpi_get_flag(self.mpi, getattr(lib, 'GCRYMPI_FLAG_' + attr.upper())))
            return res

    def __setattr__(self, attr, value):
        if hasattr(lib, 'GCRYMPI_FLAG_' + attr.upper()):
            # We have a flag, let's check if we can set it
            if value:
                if attr.upper() not in ['SECURE', 'IMMUTABLE', 'CONST']:
                    raise TypeError("You cannot set {} on this MPI".format(attr))
                lib.gcry_mpi_set_flag(self.mpi, getattr(lib, 'GCRYMPI_FLAG_' + attr.upper()))
            else:
                if attr.upper() not in ['IMMUTABLE']:
                    raise TypeError("You cannot clear flag {} on this MPI".format(attr))
                lib.gcry_mpi_clear_flag(self.mpi, getattr(lib, 'GCRYMPI_FLAG_' + attr.upper()))
            return

        super(MPI, self).__setattr__(attr, value)

    def __dump(self):
        """
        Dump the value of a in a format suitable for debugging to Libgcrypt’s
        logging stream. Note that one leading space but no trailing space or
        linefeed will be printed. It is okay to pass NULL for a.
        """
        lib.gcry_mpi_dump(self.mpi())

    def __len__(self):
        """
        Returns the number of bits required to represent self
        """
        return lib.gcry_mpi_get_nbits(self.mpi)

    def __getitem__(self, index):
        """
        Return true if bit number n (counting from 0) is set in self, false if not.
        """
        return bool(lib.gcry_mpi_test_bit(self.mpi, ffi.cast("unsigned int", index)))

    def __setitem__(self, index, bit):
        """
        Set the index bit of self to the value of the boolean in bit
        """
        if bit is True:
            lib.gcry_mpi_set_bit(self.mpi, index)
        else:
            lib.gcry_mpi_clear_bit(self.mpi, index)

    def set_highbit(self, index):
        """
        Set index bits and clear all the bits higher than index in self
        """
        lib.gcry_mpi_set_highbit(self.mpi, index)

    def clear_highbit(self, index):
        """
        Clear bit at index position in self, as well as all higher bits
        """
        lib.gcry_mpi_clear_highbit(self.mpi, index)

    def __lshift__(self, value):
        """
        Shift the value of self by value bits to the left.
        """
        tmp_mpi = type(self)()
        lib.gcry_mpi_lshift(tmp_mpi.mpi, self.mpi, value)
        return tmp_mpi

    def __ilshift__(self, value):
        return self.__lshift__(value)

    def __rshift__(self, value):
        """
        Shift the value of self by value bits to the right.
        """
        tmp_mpi = type(self)()
        lib.gcry_mpi_rshift(tmp_mpi.mpi, self.mpi, value)
        return tmp_mpi

    def __irshift__(self, value):
        return self.__rshift__(value)

    # Comparisons function can be done even with opaque MPI
    def __cmp__(self, other):
        """
        Do a comparison between a MPI and another number. Return 0 if both are equal,
        a negative number if self < other and a positive one if self > other.
        """
        if isinstance(other, MPI):
            return lib.gcry_mpi_cmp(self.mpi, other.mpi)
        else:
            # We need to test if we compare to the correct type
            if self.opaque:
                if self.value == other:
                    return 0
                else:
                    return getsizeof(self.value) - getsizeof(other)
            else:
                if other < 0:
                    # We must check againt an unsigned int. So, we're going to check the invert
                    # of our number
                    imp = self.__invert__()
                    return lib.gcry_mpi_cmp_ui(imp.mpi, -other)
                return lib.gcry_mpi_cmp_ui(self.mpi, other)

    def __eq__(self, other):
        if self.__cmp__(other) == 0:
            return True
        return False

    def __gt__(self, other):
        if self.__cmp__(other) > 0:
            return True
        return False

    def __lt__(self, other):
        if self.__cmp__(other) < 0:
            return True
        return False

    def __ge__(self, other):
        if self.__cmp__(other) >= 0:
            return True
        return False

    def __le__(self, other):
        if self.__cmp__(other) <= 0:
            return True
        return False

class MPIint(MPI):
    """
    This class is used to manipulate classic numerical MPI - by opposition to the
    MPIobs which can handle anything.
    """
    def __init__(self, value=0, fmt=u'USG', flags=[]):
        """
        Allocate a new MPI object and initialize it to 0 and initially allocate
        enough memory for a number of at least size bits. This pre-allocation in only
        a small performance issue and not actually necessary because libgcrypt automatically
        re-allocates memory.
        The secure bit is used to create the MPI in secure memory area.
        The fmt string is used as the standard formatter for this specific MPI and defaults to
          the STD one.
        We set the MPI to the value of 'value' (defaults to 0)
        """
        value = int(value)
        self.mpi = lib.gcry_mpi_snew(ffi.cast("unsigned int", getsizeof(value) * 8)) if 'SECURE' in flags else lib.gcry_mpi_new(ffi.cast("unsigned int", getsizeof(value) * 8))

        self.fmt = fmt
        self.value = value

        for flag in flags:
            if flag != 'SECURE':
                # It has been done on initialisation
                setattr(self, flag, True)

    @property
    def value(self):
        #This will return the value of the MPI object as an int.
        error = ffi.cast("gcry_error_t", 0)
        fmt = getattr(lib, u'GCRYMPI_FMT_' + self.fmt)
        size = ffi.new("size_t *", 0)
        error = lib.gcry_mpi_print(fmt, ffi.NULL, 0, size, self.mpi)
        if error > 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)).decode(), error)

        out = ffi.new("unsigned char [{}]".format(size[0]), b'')
        error = lib.gcry_mpi_print(fmt, out, size[0], size, self.mpi)
        if error > 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)).decode(), error)

        value = 0
        for item in struct.unpack('{}B'.format(size[0]), ffi.buffer(out, size[0])):
            value <<= 8
            value ^= item
        if lib.gcry_mpi_is_neg(ffi.cast("const gcry_mpi_t", self.mpi)) == 1:
            return -value
        return value

    @value.setter
    def value(self, value):
        # We're creating a new MPI assigned with value, and then we move our current mpi value
        # to its cdata object
        if value >= 0:
            self.mpi = lib.gcry_mpi_set_ui(self.mpi, ffi.cast("unsigned long", value))
        else:
            self.mpi = lib.gcry_mpi_set_ui(self.mpi, ffi.cast("unsigned long", -value))
            self.__invert__()

    def __invert__(self):
        """
        Let's invert the sign of a mpi
        """
        if lib.gcry_mpi_is_neg(self.mpi) is True:
            # We are negative, so let's return the absolute value
            return abs(self)
        else:
            return -self

    def __neg__(self):
        """
        Set a mpi to its negative value
        We first need to copy it, in order to modify it, and then we need
        to trash the copy.
        """
        tmp_mpi = self.copy()
        lib.gcry_mpi_neg(self.mpi, tmp_mpi.mpi)
        return self

    def __abs__(self):
        """
        Clear the sign of this MPI
        """
        lib.gcry_mpi_abs(self.mpi)
        return self

    def __add__(self, other):
        """
        This is the addition operator. If other is an MPI we will call
        gcry_mpi_add. Otherwise we will cast and call gcry_mpi_add_ui.
        """
        ret_mpi = type(self)()
        if isinstance(other, MPI):
            lib.gcry_mpi_add(ret_mpi.mpi, self.mpi, other.mpi)
        else:
            value = ffi.cast("unsigned long", int(other))
            lib.gcry_mpi_add_ui(ret_mpi.mpi, self.mpi, value)
        return ret_mpi

    def __iadd__(self, increment):
        """
        This is the increment operator. increment it basically is the same as
        self.__add__(increment)
        """
        return self.__add__(increment)

    def addm(self, other, mod):
        """
        return self + other \\bmod mod
        """
        ret_mpi = type(self)()
        lib.gcry_mpi_addm(ret_mpi.mpi, self.mpi, other.mpi, mod.mpi)
        return ret_mpi

    def __sub__(self, other):
        """
        This is the substraction operator. If other is an MPI, we will call
        gcry_mpi_sub. Otherwise, we will cast and call gcry_mpi_sub_ui.
        """
        ret_mpi = type(self)()
        if isinstance(other, MPI):
            lib.gcry_mpi_sub(ret_mpi.mpi, self.mpi, other.mpi)
        else:
            value = ffi.cast("unsigned long", int(other))
            lib.gcry_mpi_sub_ui(ret_mpi.mpi, self.mpi, value)
        return ret_mpi

    def __isub__(self, decrement):
        """
        This is the decrement operator. It basically is the same as
        self.__sub__(decrement)
        """
        return self.__sub__(decrement)

    def subm(self, other, mod):
        """
        return self - other \\bmod mod
        """
        ret_mpi = type(self)()
        lib.gcry_mpi_subm(ret_mpi.mpi, self.mpi, other.mpi, mod.mpi)
        return ret_mpi

    def __mul__(self, other):
        """
        Casting as the rest of the functions.
        return self * other
        """
        ret_mpi = MPIint(0)
        if isinstance(other, MPI):
            lib.gcry_mpi_mul(ret_mpi.mpi, self.mpi, other.mpi)
        else:
            value = ffi.cast("unsigned long", int(other))
            lib.gcry_mpi_mul_ui(ret_mpi.mpi, self.mpi, value)
        return ret_mpi

    def __imul__(self, multiplier):
        """
        This is the self multiplying operator
        """
        return self.__mul__(multiplier)

    def mulm(self, other, mod):
        """
        return self * other \\bmod mod
        """
        ret_mpi = type(self)()
        lib.gcry_mpi_mulm(ret_mpi.mpi, self.mpi, other.mpi, mod.mpi)
        return ret_mpi

    def mul2exp(self, exp):
        """
        return self * 2^exp
        """
        ret_mpi = type(self)()
        lib.gcry_mpi_mul_2exp(ret_mpi.mpi, self.mpi, ffi.cast("unsigned long", int(exp)))
        return ret_mpi

    def __floordiv__(self, divisor):
        """
        Castinbg as the rest of the function. The gcrypt functions returns both mod
        and dividend. This is a floordiv since we return a MPI which is an integer.
        return self // divisor
        """
        ret_mpi = type(self)()
        if not isinstance(divisor, MPI):
            _div = divisor
            divisor = type(self)()
            divisor.value = int(_div)
        lib.gcry_mpi_div(ret_mpi.mpi, ffi.NULL, self.mpi, divisor.mpi, 0)
        return ret_mpi

    def __ifloordiv__(self, divisor):
        return self.__floordiv__(divisor)

    def __mod__(self, divisor):
        """
        Return the modulus of self and divisor
        return self % divisor
        """
        ret_mpi = type(self)()
        if not isinstance(divisor, MPI):
            _div = divisor
            divisor = type(self)()
            divisor.value = int(_div)
        lib.gcry_mpi_mod(ret_mpi.mpi, self.mpi, divisor.mpi)
        return ret_mpi

    def __imod__(self, divisor):
        return self.__mod__(divisor)

    def powm(self, other, mod):
        """
        return self ^ other \\bmod mod
        """
        ret_mpi = type(self)()
        lib.gcry_mpi_powm(ret_mpi.mpi, self.mpi, other.mpi, mod.mpi)
        return ret_mpi

    def gcd(self, other):
        """
        Compute the greatest common divisor of self and other.
        """
        ret_mpi = type(self)()
        lib.gcry_mpi_gcd(ret_mpi.mpi, self.mpi, other.mpi)
        return ret_mpi

    def invm(self, other):
        """
        return the multiplicative inverse of self \\bmod other if it
        exists.
        """
        ret_mpi = type(self)()
        lib.gcry_mpi_invm(ret_mpi.mpi, self.mpi, other.mpi)
        return ret_mpi

    def isprime(self):
        """
        Check whether the number p is prime. Returns zero in case p is indeed a
        prime, returns GPG_ERR_NO_PRIME in case p is not a prime and a different
        error code in case something went horribly wrong. 
        """
        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_prime_check(self.mpi, 0)
        if error == 0:
            return True
        elif error == 16777237:
            # This is not prime
            return False
        else:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

class MPIopaque(MPI):
    """
    This class is used to store arbitrary (ie: not numbers) into an MPI.

    Math operations can't be done on it.
    """
    def __init__(self, value=b'', fmt=u'USG', flags=[]):
        """
        Allocate a new MPI object and initialize it to 0 and initially allocate
        enough memory for a number of at least size bits. This pre-allocation in only
        a small performance issue and not actually necessary because libgcrypt automatically
        re-allocates memory.
        The secure bit is used to create the MPI in secure memory area.
        The fmt string is used as the standard formatter for this specific MPI and defaults to
          the STD one.
        We set the MPI to the value of 'value' (defaults to b'')

        set/get opaque seems to return with one \x00 at the end of the bytes passed to it.
        """
        self.mpi = lib.gcry_mpi_snew(ffi.cast("unsigned int", getsizeof(value) * 8)) if 'SECURE' in flags else lib.gcry_mpi_new(ffi.cast("unsigned int", getsizeof(value) * 8))
        self.fmt = fmt
        self.value = value

        for flag in flags:
            if flag != 'SECURE':
                # It has been done on initialisation
                self.set_flag(flag, True)

    @property
    def value(self):
        if not self.opaque:
            raise TypeError("Trying to get an opaque value from a non opaque MPI")
        bits = ffi.new("unsigned int *", 0)
        _mpi = self.mpi
        # The function return a string containing the adress of the data
        void = ffi.cast("char *", lib.gcry_mpi_get_opaque(_mpi, bits))
        nbytes = bits[0] // 8
        if bits[0] % 8 != 0:
            nbytes += 1
        ret_val = ffi.buffer(void, nbytes)[0:nbytes]
        return ret_val
    
    @value.setter
    def value(self, value):
        #Set the value of the MPI to hold the arbitrary bit pattern to be
        #a reflection of the python object opaque. The number of bits used
        #by the object is passed to the functions.
        _mpi = lib.gcry_mpi_set_opaque(self.mpi, value, ffi.cast("unsigned int", len(value)*8))
        self.mpi = _mpi
