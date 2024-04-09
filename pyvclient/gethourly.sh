#!/bin/bash

# Get pyvserv hourly traffic for a day

if [ $# -lt 3 ]; then
    echo usage: ./gethourly.sh Year Month Day
    exit 1
fi

# Rudimentary check

if [ $1 -lt 2024 ]; then
    echo "Must be a valid year"
    exit
fi
if [ $2 -gt 13 ]; then
    echo "Must be a valid month"
    exit
fi
if [ $3 -gt 32 ]; then
    echo "Must be a valid day"
    exit
fi

# Do query
for aa in {0..23}; 	do
		echo -n "$1-$2-$3 $aa:00 " ;
		./pyvcli_rman.py -o -b $1-$2-$3+$aa:00 -i 60;
	done

# EOF
