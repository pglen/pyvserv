#!/bin/bash

#kill `cat ../server/.pysverv/lock` 2>/dev/null

PID=`ps xa | grep "pyserv.py" | grep python |  awk {'printf "%03d\n", $0'}`

if [ "$PID" != "" ] ; then
kill $PID
fi



