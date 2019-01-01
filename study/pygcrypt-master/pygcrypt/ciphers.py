#!/usr/bin/env python
from ctypes.util import find_library

from ._gcrypt import ffi
from . import errors

import openlib
lib = openlib.openlib()

#lib = ffi.dlopen(find_library("gcrypt"))

class Cipher(object):
    """
    This class is mostly an implementation of the cipher handler
    as described in the documentation of libgcrypt:
      <https://www.gnupg.org/documentation/manuals/gcrypt/Working-with-cipher-handles.html>

    It is used as a member of the class Context which makes sure everything is correctly
    setup.
    """
    def __init__(self, algo, mode, flags=0):
        """
        algo is a string to be used as the algorithm name, among: https://www.gnupg.org/documentation/manuals/gcrypt/Available-ciphers.html
        mode is a string to be used as the algorithm mode, among https://www.gnupg.org/documentation/manuals/gcrypt/Available-cipher-modes.html
        flags is a bitwise int to be initialized as a OR combination of several flags:
          GCRY_CIPHER_SECURE
          GCRY_CIPHER_ENABLE_SYNC
          GCRY_CIPHER_CBC_CTS
          GCRY_CIPHER_CBC_MAC
        """
        error = ffi.cast("gcry_error_t", 0)
        self.mode = mode
        self.__algo = lib.gcry_cipher_map_name(algo)
        self.__mode = getattr(lib, u'GCRY_CIPHER_MODE_' + mode)
        self.mode = mode

        self.flags = ffi.cast("unsigned int", flags)
        self.context = ffi.new("gcry_cipher_hd_t *")

        error = lib.gcry_cipher_open(self.context, self.__algo, self.__mode, self.flags)
        if error != 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)).decode(), error)

    def __getattr__(self, item):
        if item == 'algo':
            return ffi.string(lib.gcry_cipher_algo_name(self.__algo))

        if item == 'keylen':
            # the keylen is in bytes nit in bits
            size = ffi.new('size_t *')
            size = lib.gcry_cipher_get_algo_keylen(self.__algo)
            return int(size)

        if item == 'blocksize':
            size = ffi.new('size_t *')
            size = lib.gcry_cipher_get_algo_blklen(self.__algo)
            return int(size)

    def __setattr__(self, item, value):
        error = ffi.cast("gcry_error_t", 0)
        if item == 'key':
            if not isinstance(value, bytes):
                value = value.encode()
            error = lib.gcry_cipher_setkey(self.context[0]
                    , value
                    , len(value))
            if error != 0:
                raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        if item == 'iv':
            if not isinstance(value, bytes) and value is not None:
                value = value.encode()
            if value != None:
                error = lib.gcry_cipher_setiv(self.context[0]
                        , value
                        , len(value))
                if error != 0:
                    raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        if item == 'ctr':
            if not isinstance(value, bytes):
                value = value.encode()
            error = lib.gcry_cipher_setctr(self.context[0]
                    , value
                    , len(value))
            if error != 0:
                raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        super(Cipher, self).__setattr__(item, value)

    def reset(self):
        """
        Set the given handle’s context back to the state it had after the last call to gcry_cipher_setkey and clear the initialization vector.
        Since this is a macro, we will issue the call to the functins, avoiding the macro
          #define gcry_cipher_reset(h) gcry_cipher_ctl ((h), GCRYCTL_RESET, NULL, 0)
        """
        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_cipher_ctl(self.context[0], lib.GCRYCTL_RESET, ffi.NULL, 0)
        if error != 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)
        self.iv = None

    def encrypt(self, data):
        """
        We want to encrypt data. Data should have a length f a multiple of cipher block size.
        """
        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_cipher_encrypt(self.context[0], data, ffi.cast('size_t', len(data)), ffi.NULL, 0)
        if error != 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)
        return data

    def decrypt(self, data):
        """
        We will decrypt the data received.
        """
        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_cipher_decrypt(self.context[0], data, ffi.cast('size_t', len(data)), ffi.NULL, 0)
        if error != 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)
        return data

    # The following method are used for Authenticated Encryption with Associated Data (AEAD) block cipher modes 
    # which require the handling of the authentication tag and the additional authenticated data
    def aead_authenticate(self, auth_data):
        """
        Process the buffer abuf of length abuflen as the additional authenticated data (AAD) for AEAD cipher modes.

        auth_data is a bytes like object
        """
        error = ffi.cast("gcry_error_t", 0)
        error = lib.gcry_cipher_authenticate(self.context[0]
                , auth_data
                , len(auth_data))
        if error != 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

