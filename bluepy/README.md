# Python Bluepoint
## Full encryption

  The power of this encryption comes from the following primitives:
(implemented as 'C' macros)

        HECTOR(op)              use op with vector highs
        PASSLOOP(op)            use op with pass as vector
        FWLOOP(op)              forward loop traverse
        FWLOOP2(op)             forward loop variation
        BWLOOP(op)              backward loop
        BWLOOP2(op)             backward loop variation
        MIXIT(op)               mix op on first part with second part
        MIXITR(op)              mix op on first part with second part reverse
        MIXIT2(op)              mix op on first part with second part variation
        MIXIT2R(op)             mix op on first part with second part variation in reverse
        MIXIT4(op)              mix quarter length

 These are then added into encrypt / decrypt operations. Please note
that the parameter op is a mathematical / logical operation. (plus, minus, xor ...)

  The power comes from the arbitrary order of operators and the arbitrary injection
of reversible mathematical / logical operators.

 The resulting bit propagation is such high quality, that a single bit change
in the original text will change every byte in the resulting block.
(see bit description study in the code's directory)

 This beats current industrial strength encryptions, and perhaps qualifies for the
quantum challenge.

 Decryption is done by applying the ops in reverse, both by order and meaning. This is very
apparent in the functions ENCRYPT() and DECRYPT().  (see source)

TODO;

 Started the virtual machine operation, where the encryption is run through
a virtual machine stack, following a pre-made recipe or getting hints from the password.

Thu 13.Oct.2022

Warning!

 The encryption / decryption has to run with the same vector, same pass same
block length. Make sure you know what you are doing, as it is all too easy
to encrypt something into oblivion.

EOF