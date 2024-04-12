#!/bin/bash

# Updated to kill only the first occurance ; added sig arg
#echo "test" `ps xa | grep 'python3.*pyvserv'`
PROC=`ps xa | grep 'python3 ./pyvserv' | awk '{print $1}' | head -1`
#echo "proc" $PROC
if [ "$PROC" == "" ] ; then
    echo Server not running.
    exit 0
fi
kill $1 $PROC
