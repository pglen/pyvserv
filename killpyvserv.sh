#!/bin/bash

WWW=0 ; VVV=0 ; TTT=0 ; ONE=0

GGG=""
KILLPROG="kill"
SSS="pyvserv"

function helpme {
      echo -e "Usage: $(basename $0) [ -s serv | -g sig | -k kprog | -v | -t ] "
      echo -e "           -s serv   -- name of program to kill Default: 'pyvserv.py'"
      echo -e "           -g sig    -- signal to send (ex:-USR1) Default: '-SIGTERM'"
      echo -e "           -k kprog  -- use kill program. Default: 'kill'"
      echo -e "           -v        -- verbose (add more -v options for more printout)"
      echo -e "           -t        -- test (show what would be executed)"
      echo -e "           -1        -- only kill one item (last one)"
    exit "$1"
}

while getopts ':1vhtw:s:g:k:' opt;
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
    k)
      KILLPROG=$OPTARG
      if [ "$VVV" == "1" ] ; then
        echo "Using kill program 'k'" $KILLPROG
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
    1)
      ONE=$((ONE+1))
      #echo "Processing option 'v'" $VVV
      ;;
    h)
      helpme 0
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

if [ "$1" != "" ] ; then
   SSS=$1
fi

#if [ "$VVV" -gt "1" ] ; then
#    echo "Args:" $0 $@
#fi

if [ "$VVV" -gt "1" ] ; then
    echo "SSS:  '$SSS'"
fi

#PROC2=$(ps xa | grep $SSS | grep -v killserv.sh | grep -v "grep ")
#echo "ALLPIDS:" $PROC2

# Updated to kill only the first occurance ; added sig arg, excluded grep
#PROC=`ps xa | grep $SSS | grep -v "grep " | awk '{print $1}' | head -1`

PROC=$(ps xa | grep $SSS | grep -v "grep " | \
            grep -v "killpyvserv.sh " | awk '{ printf("%s ",  $1) }' )

if [ "$VVV" -gt "0" ] ; then
    echo "KILLING PIDS:" $PROC
fi

if [ $ONE -ne 0 ] ; then
    IFS=" " ; read -ra AAA <<<$PROC ;  IFS=""
    IDX=$((${#AAA[@]}-1)) ;
    PROC=${AAA[$IDX]}
fi

if [ "$PROC" == "" ] ; then
    echo Server: "'$SSS' not running."
    #helpme 1
    exit 0
fi

if [ "$VVV" -gt "0" ] ; then
    echo "Exec: kill" $GGG $PROC
fi

if [ "$TTT" -gt "0" ] ; then
    echo "Would exec: "$KILLPROG $GGG $PROC
    exit 0
fi

#echo "Exec: $KILLPROG $GGG $PROC"
$KILLPROG $GGG $PROC

# EOF
