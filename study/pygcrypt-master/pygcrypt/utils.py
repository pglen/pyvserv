#!/usr/bin/env python
from ctypes.util import find_library
from base64 import b64encode, b64decode
from functools import partial
from io import BytesIO
import struct

from ._gcrypt import ffi
from . import errors
from .gctypes import mpi, sexpression, key

import openlib
lib = openlib.openlib()

#lib = ffi.dlopen(find_library("/mingw32/lib/libgcrypt.a"))

def scan(in_bytes, mpi_fmt):
    """
    Convert the external representation of an integer stored in buffer with a
    length of buflen into a newly created MPI returned which will be stored
    at the address of r_mpi. For certain formats the length argument is
    not required and should be passed as 0. After a successful operation
    the variable nscanned receives the number of bytes actually scanned
    unless nscanned was given as NULL. format describes the format of the
    MPI as stored in buffer:

        GCRYMPI_FMT_STD
            2-complement stored without a length header. Note that
            gcry_mpi_print stores a 0 as a string of zero length.
        GCRYMPI_FMT_PGP
            As used by OpenPGP (only defined as unsigned). This is basically
            GCRYMPI_FMT_STD with a 2 byte big endian length header.
        GCRYMPI_FMT_SSH
            As used in the Secure Shell protocol. This is GCRYMPI_FMT_STD
            with a 4 byte big endian header.
        GCRYMPI_FMT_HEX
            Stored as a string with each byte of the MPI encoded as 2 hex
            digits. Negative numbers are prefix with a minus sign and in
            addition the high bit is always zero to make clear that an
            explicit sign ist used. When using this format, buflen must be
            zero.
        GCRYMPI_FMT_USG
            Simple unsigned integer.

    Note that all of the above formats store the integer in big-endian
    format (MSB first).

    in_bytes contains the bytes describing the object.
    mpi_fmt is actually a string with the value of STD, PGP, SSH, HEX or USG.

    we will return a MPI object corresponding to our scanned bytes.
    """
    error = ffi.cast("gcry_error_t", 0)
    fmt = getattr(lib, u'GCRYMPI_FMT_' + mpi_fmt)
    b_mpi = ffi.new("gcry_mpi_t *")
    length = ffi.cast("size_t", len(in_bytes))

    error = lib.gcry_mpi_scan(b_mpi, fmt, in_bytes, length, ffi.NULL)
    if error > 0:
        raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)).decode(), error)

    # We're checking if our mpi is opaque or not
    is_opaque = lib.gcry_mpi_get_flag(b_mpi[0], lib.GCRYMPI_FLAG_OPAQUE)
    if is_opaque == 0:
        # We're not an opaque
        out_mpi = mpi.MPIint()
    else:
        out_mpi = mpi.MPIopaque()
    out_mpi.mpi = b_mpi[0]
    return out_mpi

def mpi_print(mpi, mpi_fmt):
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
    # We will first change the format
    mpi.fmt = mpi_fmt
    return repr(mpi)

def swap(u, w):
    """
    Swap the values of a and b.
    Return a tuple of the swapped values.
    """
    lib.gcry_mpi_swap(u.mpi, w.mpi)
    return(u, w)

def snatch(w, u):
    """
    Set u into w and release u. If w is NULL only u will be released. 
    """
    lib.gcry_mpi_snatch(u.mpi, w.mpi)
    return u

def isneg(w):
    """
    Test if the mpi w is negative. Return true if w is negative, return false if it's positive or 0
    """
    ret = lib.gcry_mpi_is_neg(ffi.cast("const gcry_mpi_t", w.mpi))
    if ret == 1:
        return True
    return False

def randomize(length, strength='STRONG'):
    """
    Set the multi-precision-integers w to a random non-negative number of
    nbits, using random data quality of level level. In case nbits is not a
    multiple of a byte, nbits is rounded up to the next byte boundary. When
    using a level of GCRY_WEAK_RANDOM this function makes use of
    gcry_create_nonce. 
    """
    m = mpi.MPIint()
    lib.gcry_mpi_randomize(m.mpi, length, getattr(lib, 'GCRY_{}_RANDOM'.format(strength)))
    return m

def create_keys(algo=u'rsa', nbits=4096, **kwargs):
    """
    This method is used to generate a new keypair. The default are for a rsa:4096
    keypair.

    The function will first build a SExpression used to then generate the keypair,
    then return a tuple (private, public,) of the two generated key.

    More parameters can be given on invocation for advanced use and control (such as
    setting flags, the derive-params or derive parameters, etc)
    """

    # nbits must be a multiple of 8. Can be None if algo is ecc AND curve has been
    # given in kwargs
    if nbits == None and algo != u'ecc' and u'curve' not in kwargs:
        raise KeyError("nbits is None and we either are not in ecc algo, or no curve name has been given")

    if nbits != None and nbits % 8 != 0:
        raise KeyError("nbits should be a multiple of 8, got {} instead".format(nbits))

    # Algo must be one of rsa, dsa, elg or ecc
    if algo not in ['rsa', 'dsa', 'ecc', 'elg']:
        raise KeyError("algo is unknown. Got {}".format(algo))

    # Let's build the S-expression
    sexpr_string = '(genkey ({} '.format(algo)
    if nbits != None:
        sexpr_string += '(nbits {}:{})'.format(len(str(nbits)), nbits)
    for item in kwargs:
        if isinstance(kwargs[item], int):
            sexpr_string += '({} {}:{})'.format(item, len(str(kwargs[item])), kwargs[item])
        if isinstance(kwargs[item], mpi.MPI):
            sexpr_sttring += '({} #{:x}#)'.format(item, kwargs[item].value())
        if isinstance(kwargs[item], list):
            sexpr_string += '({} {})'.format(item, ' '.join(kwargs[item]))
        if isinstance(kwargs[item], sexpression.SExpression):
            sexpr_string += '({} {})'.format(item, kwargs[item])
        else:
            sexpr_string += '({} "{}")'.format(item, kwargs[item])
    sexpr_string += '))'
    keyParam = sexpression.SExpression(sexpr_string.encode())

    # Let's generate the key
    error = ffi.cast("gcry_error_t", 0)
    keys = ffi.new("gcry_sexp_t *")
    error = lib.gcry_pk_genkey(keys, keyParam.sexp)
    if error > 0:
        raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

    # We now have the fnal SExpression
    keySexp = sexpression.SExpression(keys)

    # Let's split it in private and public keys
    private = key.Key(keySexp[b'private-key'])
    public = key.Key(keySexp[b'public-key'])
    return (private, public,)

def key_derive(passphrase, salt, keysize=128, algo=u'ITERSALTED_S2K', subalgo=u'sha256', count=1024):
    """
    Derive a key from a passphrase. keysize gives the requested size of the keys
    in octets. keybuffer is a caller provided buffer filled on success with the
    derived key. The input passphrase is taken from passphrase which is an
    arbitrary memory buffer of passphraselen octets. algo specifies the KDF
    algorithm to use; see below. subalgo specifies an algorithm used internally
    by the KDF algorithms; this is usually a hash algorithm but certain KDF
    algorithms may use it differently. salt is a salt of length saltlen octets,
    as needed by most KDF algorithms. iterations is a positive integer parameter
    to most KDFs.
    """
    if isinstance(passphrase, str):
        passphrase = passphrase.encode()
    if not isinstance(passphrase, bytes):
        raise TypeError("Passphrase should be str or bytes, got {} instead".format(type(passphrase)))
    if isinstance(salt, str):
        salt = salt.encode()
    if not isinstance(salt, bytes):
        raise TypeError("Salt should be str or bytes, got {} instead".format(type(salt)))

    if algo.upper() in ['ITERSALTED_S2K', 'SALTED_S2K']:
        if len(salt) != 8:
            raise Exception("For algorithm of type {}, we need a salt of exactly 8 bytes, got one of {} instead".format(algo, len(salt)))

    algo = getattr(lib, u'GCRY_KDF_' + algo.upper())
    subalgo_int = getattr(lib, u'GCRY_MD_' + subalgo.upper())

    if subalgo_int == 0:
        raise Exception("Sub-Algorithm name {} is unknown".format(subalgo.decode()))

    key = ffi.new("char [{}]".format(keysize))
    keysize = ffi.cast("size_t", keysize/8) # keysize is given in bytes. Most of them are given in bits by algo descriptions
    error = ffi.cast("gcry_error_t", 0)
    error = lib.gcry_kdf_derive(passphrase, ffi.cast("size_t", len(passphrase)), algo, subalgo_int, salt, ffi.cast("size_t", len(salt)), count, keysize, key)
    if error > 0:
        raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

    return ffi.buffer(key, int(keysize))[:]

def rand(length, strength='STRONG'):
    """
    Generates random bytes of length bytes, using the
    strength defined.
    """
    data = lib.gcry_random_bytes(length, getattr(lib, 'GCRY_{}_RANDOM'.format(strength)))
    return ffi.buffer(data, length)[:]

def srand(length, strength='STRONG'):
    """
    Generates random bytes of length bytes, using the
    strength defined. But using a secure routine.
    """
    data = lib.gcry_random_bytes_secure(length, getattr(lib, 'GCRY_{}_RANDOM'.format(strength)))
    return ffi.buffer(data, length)[:]

