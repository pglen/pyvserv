#!/bin/bash

python3 -m venv pip_pyvserv
#cp pip_stage2.sh pip_pyvserv
cd pip_pyvserv
source  ./bin/activate
pip install pyvserv
