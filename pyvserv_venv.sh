#!/bin/bash

python3 -m venv pip_pyvserv
cp pip_stage2.sh pip_pyvserv
cd pip_pyvserv
bash --rcfile ./bin/activate -c "./bin/pyvserv -v -d 5"
