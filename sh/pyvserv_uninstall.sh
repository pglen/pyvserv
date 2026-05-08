#!/bin/bash

# We use pipx for its automatic venv; uninstall

EXE=`which pipx`
#echo $EXE
if [ "$EXE" !=  "" ] ; then
    pipx uninstall pyvserv
else
    pip uninstall pyvserv
fi

# EOF