#!/bin/bash

echo Creating new demo data set

./pyvcli_uini.py -f
./pyvcli_ihost.py
./pyvcli_ihost.py -A test:2222
./pyvcli_rput.py

# Decorate the alt as well

./pyvcli_uini.py -f -p 5555
./pyvcli_ihost.py -p 5555 -A localhost:6666
./pyvcli_ihost.py -p 5555 -A test:2222
./pyvcli_rput.py  -p 5555

# EOF
