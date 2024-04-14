#!/bin/bash

echo Creating new demo data set

./pyvcli_uini.py -f
./pyvcli_ihost.py
./pyvcli_ihost.py -A test:2222
./pyvcli_rput.py

# EOF
