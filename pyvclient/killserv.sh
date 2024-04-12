#!/bin/bash

SSS="pyvserv.py"
GGG=""
WWW=0;VVV=0; TTT=0
KILLPROG="kill"

function helpme {
      echo -e "Usage: $(basename $0) [ -s server | -g sig  | -v | -t ]"
      echo " options:"
      echo "        -s server -- name of program to kill default: pyvserv.py"
      echo "        -g sig    -- signal to send (ex:-USR1) default: none (-SIGTERM)"
      echo "        -v        -- verbose (add more -v options for more printout)"
      echo "        -t        -- test (show what would be executed)"
}

while getopts 'vhtw:s:g:' opt;
do
  case "$opt" in
    w)
      WWW=$OPTARG
      if [ "$VVV" == "1" ] ; then
        echo "Processing option 'w'" $WWW
      fi
      ;;
    s)
      SSS=$OPTARG
      if [ "$VVV" == "1" ] ; then
        echo "Processing option 's'" $SSS
      fi
      ;;
    g)
      GGG=$OPTARG
      if [ "$VVV" == "1" ] ; then
        echo "Processing option 'g'" $GGG
      fi
      ;;
    v)
      VVV=$((VVV+1))
      #echo "Processing option 'v'" $VVV
      ;;
    t)
      TTT=$((TTT+1))
      #echo "Processing option 'v'" $VVV
      ;;
    h)
      helpme
      exit
     ;;
    ?)
        #echo -e "Invalid command option. $1"
        exit 1
      ;;
   esac
done

if [ "$VVV" -gt "1" ] ; then
    echo "Command:" $0 $@
fi
shift $(( OPTIND - 1 ));

# Updated to kill only the first occurance ; added sig arg, excluded grep
PROC=`ps xa | grep $SSS | grep -v "grep " | awk '{print $1}' | head -1`

if [ "$VVV" -gt "1" ] ; then
    echo "Args:" $@
fi

if [ "$VVV" -gt "0" ] ; then
    echo "Exec: kill" $GGG $PROC $@
fi

if [ "$TTT" -gt "0" ] ; then
    echo "Would exec:" $KILLPROG $GGG $PROC $@
    exit
fi

if [ "$PROC" == "" ] ; then
    echo Server "'"$SSS"'" not running.
    exit 0
fi


$KILLPROG $GGG $PROC

# EOF
