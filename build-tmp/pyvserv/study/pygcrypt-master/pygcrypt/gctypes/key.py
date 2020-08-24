#!/usr/bin/env python
from binascii import b2a_hex
from struct import pack

from ctypes.util import find_library

from .._gcrypt import ffi
from .. import errors
from .sexpression import SExpression
from .mpi import MPI, MPIint, MPIopaque

lib = ffi.dlopen(find_library("gcrypt"))

"""
This module provide the key object and the necessary function to
use them.

It does not provides encrypt and decrypt functions, nor sign/verifysign
which are provided in a higher level module.
"""

class Key(object):
    """
    This object will hold most of the key system.
    """
    def __init__(self, sexp):
        """
        A key must be initiliased with a S-Expression.
        This S-expression defines algorithm, numbers
        and all other things to be used by it.
        """
        if not isinstance(sexp, SExpression):
            raise TypeError("First parameters must be a SExpression, got {} instead".format(type(sexp)))

        # Let's get the type of key we have
        try:
            sub_sexp = sexp['private-key']
            self.type = u'private'
            self.sexp = SExpression(b'(private-key %S)', sub_sexp)
        except KeyError:
            try:
                sub_sexp = sexp['protected-private-key']
                self.type = u'private'
                self.sexp = SExpression(b'(protected-private-key %S)', sub_sexp)
            except KeyError:
                try:
                    sub_sexp = sexp['public-key']
                    self.type = u'public'
                    self.sexp = SExpression(b'(public-key %S)', sub_sexp)
                except:
                    raise TypeError("The provided S-Expression does not contains key data.")
        except:
            raise

    def __len__(self):
        """
        Return what is commonly referred as the key length for the key
        """
        length = lib.gcry_pk_get_nbits(self.sexp.sexp)
        return length

    def __getattr__(self, item):
        error = ffi.cast("gcry_error_t", 0)
        if item == 'keylen':
            return len(self)

        if item == 'keygrip':
            # get the keygrip of the current key. If the 
            # algo does not support keygrip, it returns ffi.NULL
            # which is None
            ret = ffi.new("unsigned char [20]")
            lib.gcry_pk_get_keygrip(self.sexp.sexp, ret)
            if ret == ffi.NULL:
                return None
            return b2a_hex(ffi.buffer(ret, 20)[:]).decode()

        if item == 'algo':
            # The algorithm is the cadr of the key.
            algo = self.sexp.cdr.car.getstring(0)
            # We want to check if this algo is available
            usable = lib.gcry_pk_algo_info(lib.gcry_pk_map_name(algo), lib.GCRYCTL_TEST_ALGO, ffi.NULL, ffi.NULL)
            if usable != 0:
                raise Exception("Algorithm {} not usable on this platform")
            return algo.decode()

        if item == 'sign':
            # We want to know if this key can be used to sign.
            algo_int = lib.gcry_pk_map_name(self.algo.encode())
            error = ffi.cast("gcry_error_t", 0)
            error = lib.gcry_pk_algo_info(algo_int, lib.GCRYCTL_TEST_ALGO, ffi.NULL, ffi.new("size_t *", 1))
            if error < 0:
                # We have an error
                raise Exception("Oops something went wrong")
            if error != 0:
                return False
            return True

        if item == 'encr':
            # We want to know if this key can be used to encrypt.
            algo_int = lib.gcry_pk_map_name(self.algo.encode())
            error = ffi.cast("gcry_error_t", 0)
            error = lib.gcry_pk_algo_info(algo_int, lib.GCRYCTL_TEST_ALGO, ffi.NULL, ffi.new("size_t *", 2))
            if error < 0:
                # We have an error
                raise Exception("Oops something went wrong")
            if error != 0:
                return False
            return True

        return self.sexp.__getitem__(item)

    def issane(self):
        """
        Return zero if the private key key is ‘sane’, an error code otherwise.
        Note that it is not possible to check the ‘saneness’ of a public key. 
        """
        if self.type == 'private':
           error = ffi.cast("gcry_error_t", 0)
           error = lib.gcry_pk_testkey(self.sexp.sexp)
           if error > 0:
               return False
           return True
        else:
           return False

    def __repr__(self):
        """
        We want to print the key. So we gonan print the associated S-Expression.
        """
        return self.sexp.__repr__()

    def encrypt(self, data_sexp):
        """
        Obviously a public key must be provided for encryption. It is expected as an
        appropriate S-expression (see above) in pkey. The data to be encrypted can
        either be in the simple old format, which is a very simple S-expression
        consisting only of one MPI, or it may be a more complex S-expression which
        also allows to specify flags for operation, like e.g. padding rules.
        """
        # If we're not a public key, raise NotImplementedError
        if self.type != 'public':
            raise NotImplementedError

        if not isinstance(data_sexp, SExpression):
            # We must have a S-Expression coming in or fail
            raise TypeError("We do not have a SExpression to be encrypted")

        sexp_encrypted = ffi.new("gcry_sexp_t *")
        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_pk_encrypt(sexp_encrypted, data_sexp.sexp, self.sexp.sexp)
        if error > 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        encrypted = SExpression(sexp_encrypted)
        return encrypted

    def decrypt(self, encrypted, flags=b''):
        """
        Obviously a private key must be provided for decryption. It is expected as
        an appropriate S-expression (see above) in skey. The data to be decrypted
        must match the format of the result as returned by gcry_pk_encrypt, but
        should be enlarged with a flags element.
        """
        # If we're not a public key, bail out
        if self.type != 'private':
            raise NotImplementedError
        # We want to build a Sexp with the correct flags for padding removal.
        sexp_algo = encrypted[self.algo]
        if flags == b'':
            sexp_encr = SExpression(b'(enc-val (flags)(%s %S))', self.algo.encode(), sexp_algo)
        else:
            sexp_encr = SExpression(b'(enc-val (flags %s)(%s %S))', flags, self.algo.encode(), sexp_algo)

        # We have a built-in expression in input, so let's use it
        clear_sexp = ffi.new("gcry_sexp_t *")
        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_pk_decrypt(clear_sexp, sexp_encr.sexp, self.sexp.sexp)
        if error > 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        sexp_decrypted = SExpression(clear_sexp)
        return sexp_decrypted

    def makesign(self, data, algo='sha256'):
        """
        This function creates a digital signature for data using the private key
        skey and place it into the variable at the address of r_sig. data may
        either be the simple old style S-expression with just one MPI or a modern
        and more versatile S-expression which allows to let Libgcrypt handle
        padding.
        """
        # If we're not a private key, bail out
        if self.type != 'private':
            raise NotImplementedError
        # We want to build a sexp with pkcs1 padding
        if isinstance(data, str):
            data = data.encode()

        if not isinstance(data, bytes):
            raise TypeError("data should be bytes, got {} instead".format(type(data)))

        # Depending on our key algorithm, we might have different S-Expression built
        if self.algo in ('rsa', 'elg', 'ecc'):
            data_sexp = SExpression(b"(data (flags %s)(hash %s %b))", 'pkcs1', algo, len(data), data)
        elif self.algo == 'dsa':
            # Go for EdDSA, which is a better one.
            data_sexp = SExpression(b"(data (flags eddsa)(hash-algo %s)(value %b))", b'sha512', len(data), data)

        error = ffi.cast("gcry_error_t", 0)
        sig_sexp = ffi.new("gcry_sexp_t *")
        error = lib.gcry_pk_sign(sig_sexp, data_sexp.sexp, self.sexp.sexp)
        if error > 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        return SExpression(sig_sexp)

    def verify(self, signature, data, algo='sha256'):
        """
        This is used to check whether the signature sig matches the data. The
        public key pkey must be provided to perform this verification. This
        function is similar in its parameters to gcry_pk_sign with the exceptions
        that the public key is used instead of the private key and that no
        signature is created but a signature, in a format as created by
        gcry_pk_sign, is passed to the function in sig.
        """
        # if we're not a public key, bail out
        if self.type != 'public':
            raise NotImplementedError
        # We want to build a sexp with pkcs1 padding
        if isinstance(data, str):
            data = data.encode()

        if not isinstance(data, bytes):
            raise TypeError("data should be bytes, got {} instead".format(type(data)))

        # Depending on our key algorithm, we might have different S-Expression built
        if self.algo in ('rsa', 'elg', 'ecc'):
            data_sexp = SExpression(b"(data (flags %s)(hash %s %b))", 'pkcs1', algo, len(data), data)
        elif self.algo == 'dsa':
            # Go for EdDSA, which is a better one.
            data_sexp = SExpression(b"(data (flags eddsa)(hash-algo %s)(value %b))", b'sha512', len(data), data)

        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_pk_verify(signature.sexp, data_sexp.sexp, self.sexp.sexp)

        if error > 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        return True
