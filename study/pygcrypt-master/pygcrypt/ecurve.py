#!/usr/bin/env python

from ctypes.util import find_library

from ._gcrypt import ffi
from . import errors
from .gctypes.sexpression import SExpression
from .gctypes.ec_point import Point
from .gctypes.mpi import MPIint
from .gctypes.key import Key

import openlib
lib = openlib.openlib()

#lib = ffi.dlopen(find_library("gcrypt"))

class ECurve(object):
    """
    This object describes an elliptic curve. It provides methods to access points
    and mpi associated to it.

    It provides dictionnary like method to access to its member.
    """
    def __init__(self, keyparam=None, curve=None):
        """
        Let's create the context needed for the Elliptic curve calculation.
        It needs a keyparam formed like an ecc_keyparam S-Expression as a
        parameters and an optional curve-name to fill in the blank of the
        parameter.
        """
        # First we need to check if the keyparam is a valid S-Expression
        if keyparam is not None and not isinstance(keyparam, SExpression):
            raise TypeError("keyparam must be a SExpression. Got {} instead.".format(type(keyparam)))
        if keyparam is None and curve is None:
            raise TypeError("at least one of keyparam and curve must be passed to __init__")

        ec_curve = ffi.new("gcry_ctx_t *", ffi.NULL)
        error = ffi.cast("gpg_error_t", 0)
        if keyparam is None:
            keyparam_t = ffi.NULL
        else:
            keyparam_t = keyparam.sexp

        if curve == None:
            curve = ''

        error = lib.gcry_mpi_ec_new(ec_curve, keyparam_t, curve.encode())
        if error != 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)).decode(), error)

        self.curve = ec_curve[0]
        self.name = curve

    def __del__(self):
        """
        We need to release the the context associated to ourself.
        """
        lib.gcry_ctx_release(self.curve)

    def __setitem__(self, key, item):
        """
        We want to add either a Point or a MPI to our elliptic curve
        context.
        """
        error = ffi.cast("gcry_error_t", 0)

        if isinstance(item, Point):
            error = lib.gcry_mpi_ec_set_point(key.encode(), item.point, self.curve)
        elif isinstance(item, MPIint):
            error = lib.gcry_mpi_ec_set_mpi(key.encode(), item.mpi, self.curve)
        else:
            raise TypeError("Item must be Point or MPI. Got {} instead.".format(type(item)))

        if error != 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)).decode(), error)

    def __getitem__(self, key):
        """
        Let's retrieve an item from the Elliptic Curve. Item to be retrieved can only be
        in keys defined by the ecc-private key params.

        p, a, b, n and d are mpi
        g and q are points.
        """
        if key in ['p', 'a', 'b', 'n', 'd']:
            # We want to have a mpi that can be copied
            mpi = MPIint()
            pointer = lib.gcry_mpi_ec_get_mpi(key.encode(), self.curve, 1) 
            if pointer == ffi.NULL:
                return None
            mpi.mpi = pointer
            return mpi
        elif key in ['q', 'g']:
            # We want a point that can be copied
            point = Point(self.curve)
            pointer = lib.gcry_mpi_ec_get_point(key.encode(), self.curve, 1)
            if pointer == ffi.NULL:
                return None
            point.point = pointer
            return point
        else:
            raise KeyError

    def __repr__(self):
        """
        We want to print the current EC. For that we will create the S-Expression
        corresponding to the current state of the curve, and returns it in a tuple with the
        name of the curve.
        """
        return """(keyparam 
    (ecc 
        (p {})
        (a {})
        (b {})
        (n {})
        (d {})
        (q {})
        (g {})
    )
)""".format(self['p'], self['a'], self['b'], self['n'], self['d'], self['q'], self['g'])

    def key(self, mode=0):
        """
        Return an S-expression representing the context curve. Depending on the
        state of that context, the S-expression may either be a public key, a
        private key or any other object used with public key operations. On
        success 0 is returned and a new S-expression is stored at r_sexp; on
        error an error code is returned and NULL is stored at r_sexp. mode must be
        one of:
            0
                Decide what to return depending on the context. For example if the
                private key parameter is available a private key is returned, if
                not a public key is returned.
            GCRY_PK_GET_PUBKEY
                Return the public key even if the context has the private key
                parameter.
            GCRY_PK_GET_SECKEY
                Return the private key or the error GPG_ERR_NO_SECKEY if it is not
                possible.

        As of now this function supports only certain ECC operations because a
        context object is right now only defined for ECC. Over time this function
        will be extended to cover more algorithms.
        """
        if mode == u'PUBKEY':
            mode = 1
        elif mode == u'SECKEY':
            mode = 2
        error = ffi.cast("gcry_error_t", 0)
        r_sexp = ffi.new("gcry_sexp_t *")
        error = lib.gcry_pubkey_get_sexp(r_sexp, mode, self.curve)
        
        if error > 0:
            raise errors.GcryptException(ffi.string(lib.gcry_strerror(error)), error)

        return Key(SExpression(r_sexp))

