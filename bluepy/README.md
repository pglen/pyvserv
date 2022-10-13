#                                Python Bluepoint
## 	Full encryption

  The power of this encrption comed from the following primitives,
implemented as 'C' macros.

        HECTOR(op)              use op with vector
        PASSLOOP(op)            use op with vector
        FWLOOP(op)              forward loop
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
of mathematical / logical operators.

 The resulting bit propagation is such high quality, that a single bit change
in the original text will change every byte in the resulting block.

 This beats current industrial strength encryptions, and perhaps qualifies for the
quantum challenge.





