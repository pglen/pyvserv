#!/bin/bash

# We use pipx for its automatic venv
EXE=`which pipx`
#echo $EXE
if  [ "$EXE" !=  "" ] ; then
    pipx install .
else
    pip install .
fi

# EOF
