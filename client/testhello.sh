#!/bin/bash
# See if our server running

tsrun() {
ps xa | grep "pyserv.py" | grep python >/dev/null
ret=$?
if [ $ret == 0 ] ; then
    #echo "server running"
    return 0

else
    echo "Server NOT running, attempting to start ..."
    python ../server/pyserv.py  &
    return 0
fi
}

tsrun
# Wait for the server
sleep 1

./pycli_hello.py
./killserv.sh

# Wait for the server
sleep 1

