#!/usr/bin/env python
from ctypes.util import find_library

from .._gcrypt import ffi
from .. import errors
from .mpi import MPIint

lib = ffi.dlopen(find_library("gcrypt"))

"""
This modules is used to define Elleptic Curve points
"""

class Point(object):
    """
    An elliptic curve point is basically a tuple of MPI
    """
    def __init__(self, curve):
        """
        Initialize a Point using the MPI provided for x, y and z.
        Ctx is an elliptic curve context
        """
        self.point = lib.gcry_mpi_point_new(0)
        self.curve = curve

    def __del__(self):
        lib.gcry_mpi_point_release(self.point)

    def __repr__(self):
        """
        Print the EC Point
        """
        return "({},{},{})".format(self.x, self.y, self.z)

    def __getattr__(self, key):
        """
        Let's get the item specified by key
        """
        if key in ['x', 'y', 'z']:
            ret_mpi = MPIint()
            pointer = ret_mpi.mpi

            if key == 'x':
                lib.gcry_mpi_point_get(pointer, ffi.NULL, ffi.NULL, self.point)
            elif key == 'y':
                lib.gcry_mpi_point_get(ffi.NULL, pointer, ffi.NULL, self.point)
            elif key == 'z':
                lib.gcry_mpi_point_get(ffi.NULL, ffi.NULL, pointer, self.point)
            else:
                raise KeyError

            if pointer == ffi.NULL:
                return None
            ret_mpi.mpi = pointer
            return ret_mpi

    def __setattr__(self, key, value):
        if key == 'point':
            if self.point is not None:
                lib.gcry_mpi_point_release(self.point)

        if key == 'x':
            if not isinstance(value, MPIint):
                raise TypeError("We need an MPIint to be set as {}. {} given.".format(key, type(value)))
            lib.gcry_mpi_point_set(self.point, value.mpi, self.y.mpi, self.z.mpi)
            return
        elif key == 'y':
            if not isinstance(value, MPIint):
                raise TypeError("We need an MPIint to be set as {}. {} given.".format(key, type(value)))
            lib.gcry_mpi_point_set(self.point, self.x.mpi, value.mpi, self.z.mpi)
            return
        elif key == 'z':
            if not isinstance(value, MPIint):
                raise TypeError("We need an MPIint to be set as {}. {} given.".format(key, type(value)))
            lib.gcry_mpi_point_set(self.point, self.x.mpi, self.y.mpi, value.mpi)
            return
        super(Point, self).__setattr__(key, value)

    def affine(self, x, y):
        """
        Compute the affine coordinates from the projective coordinates in point
        and store them into x and y. If one coordinate is not required, NULL may
        be passed to x or y. curve is the context object which has been created
        using gcry_mpi_ec_new. Returns 0 on success or not 0 if point is at
        infinity. 
        """
        if not isinstance(x, MPIint) or not isinstance(y, MPIint):
            raise TypeError("MPIint must be given for x and y to store the affine coordinate")

        ret = lib.gcry_mpi_ec_get_affine(x.mpi, y.mpi, self.point, self.curve)
        return (x, y)

    def double(self):
        """
        Double the point u of the elliptic curve described by curve and store the
        result into w.
        """
        point_dest = lib.gcry_mpi_point_new(0)
        lib.gcry_mpi_ec_dup(point_dest, self.point, self.curve)
        self.point = point_dest

    def __add__(self, point):
        """
        Add the points u and v of the elliptic curve described by curve and store the result into w.
        """
        if not isinstance(point, Point):
            raise TypeError("Can only add Point to Point. Got {} instead.".format(type(point)))

        point_dest = lib.gcry_mpi_point_new(0)
        lib.gcry_mpi_ec_add(point_dest, self.point, point.point, self.curve)
        ret_point = Point(self.curve)
        ret_point.point = point_dest
        return ret_point

    def __mul__(self, mpi):
        """
        Multiply the point u of the elliptic curve described by curve by n and store the result into w.
        """
        if not isinstance(mpi, MPIint):
            raise TypeError("Can only multiply a point by a MPIint, got {} instead.".format(type(point)))

        point_dest = lib.gcry_mpi_point_new(0)
        lib.gcry_mpi_ec_mul(point_dest, mpi.mpi, self.point, self.curve)
        ret_point = Point(self.curve)
        ret_point.point = point_dest
        return ret_point

    def __eq__(self, point):
        """
        Points are equal if they have the same coordinates
        """
        if not isinstance(point, Point):
            raise TypeError("Can only compare Point to Point, got {} instead.".format(type(point)))
        return (self.x, self.y, self.z) == (point.x, point.y, point.z)

    def isoncurve(self):
        """
        Return true if point is on the elliptic curve described by curve. 
        """
        ret = lib.gcry_mpi_ec_curve_point(self.point, self.curve)
        if ret >= 1:
            return True
        return False
