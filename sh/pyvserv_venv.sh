#!/bin/bash

if [ "$0" != "bash" ] ; then
    echo "Please start as 'source' like 'source pyvserv_venv.sh'"
    exit 1
fi

VENV=venv
if [ ! -d $VENV ] ; then
    echo Creating: $VENV
    python3 -m venv $VENV
fi
cd $VENV
source bin/activate
echo "Type 'deactivate' to leave venv"

# EOF
