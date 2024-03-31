#!/bin/bash

PID=`ps xa | grep "pyvserv.py" | grep python |  awk {'printf "%03d\n", $0'}`
#echo $PID
if [ "$PID" != "" ] ; then
    kill $PID
fi

# EOF
