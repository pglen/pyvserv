#!/bin/bash

echo $1

# Exceptions
if [ "$1" == "u/pyvcli_uini.py" ] ; then
    exit 0
fi

export PYTHONPATH=$(pwd):$(pwd)/..:$(pwd)/../pyvcommon:$(pwd)/pyvcommon
#echo $PYTHONPATH
python3 $1

echo done
