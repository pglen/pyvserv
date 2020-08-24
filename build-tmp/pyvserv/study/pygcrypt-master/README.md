# Pygcrypt

## What?

Pygcrypt is a library module used to interface the code provided by the
libgcrypt. Libgcrypt is the lox-level library developped for the GnuPG
project and provides a lot of cryptography primitives. The original project
and code is available on the [gnupg's git][gnupg-git].

The goal is to provide a way to use GPG code and primitives, without relying
on the gnupg environment, keyring and agents. This is intended to be used
mainly by server code.

## Install

Get the code of pygcrypt. It's actually available on the git provided by [Le
Loop][leloop-git]. Obviously, you need the library installed on your system.
For debian like system it's in the package ''libgcrypt''.

Once you get the code, you can install it by running the command in the code
repository:

    python setup.py install

It will install all the python dependencies (currently available in the
requirements.txt file, and it's mainly the [cffi][] module and the
[pytest][] test framework.

## Use

### Initialisation

Before anything, you should create a context. It is used to initialize the
libgcrypt inner system - such as creating secure-memory, initializing random
generators and the like.

    >>> from pygcrypt.context import Context
    >>> ctx = Context()

If you don't do that, you may encouter segfaults and non-expected behaviour.
This is _mandatory_ before doing anything else.

### Symmetric cryptography

Symmetric cryptography is provided through the module ciphers. You should
attach a cipher to a context, since there's a lot of mapping done from the
context to ease access to it.

    >>> from pygcrypt.ciphers import Cipher
    >>>
    >>> ciph = cipher.Cipher(b'AES', u'CBC')
    >>> ctx['cipher'] = ciph
    >>> print ctx['keylen']
    16
    >>> ctx['key'] = b'0123456789ABCDEF'
    >>> ctx['key']
    b'0123456789ABCDEF'

The encrypt() and decrypt functions takes care of padding (PKCS#11)

### Types

#### MPI

MPI (Multiple Precision Integer) is the mechanism used by libgcrypt to handle
and manage long integers necessary for cryptography operations.

There's a factory to generate MPI from a context. You can have two types of
MPI: MPIint which handle integer and math operation, and MPIobscure which can
be used to store arbitrary binary stuff.

    >>> from pygcrypt.context import Context
    >>>
    >>> ctx = Context()
    >>> mpi = ctx.mpi(4)
    >>> mpi * 2
    8
    >>> mpi >> 1
    2
    >>> mpi = ctx.mpi(b"Hello World!")
    >>> mpi
    b'Hello World!'

You can change the format used by a specific MPI by setting it's fmt
attribute.

The module utils provide a way to generate MPI to arbitrary bit length.

    >>> from utils import randomize
    >>> mpi = utils.randomize(512)

#### S-Expression

S-Expression are used by libgcrypt to describe everything, from encrypted data
to a key pr an elliptic curve. They're built from either a string, a scanf
like string and parameters or from another one.

    >>> from pygcrypt.type.sexpression import SExpression
    >>>
    >>> sexp = SExpression(b'(data "A string goes here")')
    >>> another = SExpression(b'(sexpression (data %s)(number %m))', "Hello World", utils.randomize(512))

You can access part of a S-expression using classic containers
getitem/setitem - including with a slice.

   >>> another['data']
   >>> b'(data "Hello World")\n'

A complete documentation on how the S-Expression works - and their format -
is available at [the libgcrypt][ilibgcrypt-doc] website.

#### Keys

Keys are needed for assymetric cryptography. They're basically S-Expression
with special methods (mostly encrypt/decrypt and makesign/verify)

A utility function can be used to create a random keypair. It returns a
tuple of key _(public, private)_.

Otherwise they're really just simply S-Expression.

### Hashing and HMAC

#### Hashing

The module hashingcontext allows to works with hashing functionnality. It
works a bit like the hashlib modules: you create and initiate a context, you
write data and you read them.

    >>> from pygcrypt.hashcontext import hashContext
    >>> 

[pytest]: https://pytest.org/pytest/
[cffi]: https://cffi.readthedocs.org/
[gnupg-git]: https://git.gnupg.org/cgi-bin/gitweb.cgi
[loop-git]: https://git.leloop.org/orage-io/pygcrypt
[libgcryp-doc]: https://www.gnupg.org/documentation/manuals/gcrypt/index.html
