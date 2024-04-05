#!/home/peterglen/pgpygtk/pyvserv/pip_pyvserv/bin/python3
# coding=utf-8

import os, sys, time

from collections import OrderedDict

base = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base,  'pyvecc'))

from pyvecc.Key import Key


def test_generation_perf(n=100):
    results = OrderedDict()
    for bits in (192, 224, 256, 384, 521):
        t = time.time()
        for i in range(n):
            k = Key.generate(bits)
        t = time.time() - t
        results[bits] = t
    return results


def test_signing_perf(n=100):
    results = OrderedDict()
    for bits in (192, 224, 256, 384, 521):
        k = Key.generate(bits)
        t = time.time()
        for i in range(n):
            k.sign(b'random string')
        t = time.time() - t
        results[bits] = t
    return results


def test_verification_perf(n=100):
    results = OrderedDict()
    for bits in (192, 224, 256, 384, 521):
        k = Key.generate(bits)
        s = k.sign(b'random string')
        t = time.time()
        for i in range(n):
            k.verify(b'random string', s)
        t = time.time() - t
        results[bits] = t
    return results


def test_encryption_perf(n=100):
    results = OrderedDict()
    for bits in (192, 224, 256, 384, 521):
        k = Key.generate(bits)
        for i in range(n):
            t = time.time()
            s = k.encrypt(b'random string' * 10)
            t = time.time() - t
        results[bits] = t
    return results

def test_decryption_perf(n=100):
    results = OrderedDict()
    for bits in (192, 224, 256, 384, 521):
        k = Key.generate(bits)
        s = k.encrypt(b'random string' * 10)

        for i in range(n):
            t = time.time()
            k.decrypt(s)
            t = time.time() - t
        results[bits] = t
    return results

def print_dict(title, d, n):
    print(title)
    print('-' * len(title))
    for k, v in d.items():
        print('{} bits  {:10.5f} seconds  {:10.5f}/sec'.format(k, v, n / v))
    print('')


def mainfunc():
    n = 100

    print("Started tests, please wait.\n")

    print_dict('Key generation', test_generation_perf(n), n)
    print_dict('Signing', test_signing_perf(n), n)
    print_dict('Verifying', test_verification_perf(n), n)
    print_dict('Encrypting', test_encryption_perf(n), n)
    print_dict('Decrypting', test_decryption_perf(n), n)

if __name__ == '__main__':
    mainfunc()

