#!/bin/bash

#if [ "$1" == "" ] ; then
#    echo Find and list versions of file. Sort it by date.
#    echo Usage: getfver.sh filename
#    exit
#fi

function helpme {
      echo "Get file version details from the system."
      echo -e "Usage: $(basename $0) [ -s | -v | -h ] filename"
      echo " options:"
      echo "        -s        -- sort by size instead of by date"
      echo "        -r        -- use regex for search"
      echo "        -v        -- verbose (add more -v options for more printout)"
      echo "        -V        -- Show version number"
      echo "        -h        -- Show help (this screen)"
      echo " Make sure you escape '.' (dot) in filename. (ex: file\.ext)"
}

VERSION="1.0.0"
SSS=1; RRR=0; VVV=0

while getopts 'svhr' opt;
do
  case "$opt" in
    r)
        RRR=1
      if [ "$VVV" == "1" ] ; then
        echo "Processing option 's'" $SSS
      fi
      ;;
    s)
        SSS=2
      if [ "$VVV" == "1" ] ; then
        echo "Processing option 's'" $SSS
      fi
      ;;

    h)
      helpme
      exit
     ;;
       v)
      VVV=$((VVV+1))
      #echo "Processing option 'v'" $VVV
      ;;
     V)
      echo version $VERSION
      exit
      ;;
    ?)
        #echo -e "Invalid command option. $1"
        exit 1
      ;;
   esac
done

shift $(( OPTIND - 1 ));

if [ "$1" == "" ] ; then
 echo "Must specify file name"
 exit
fi

if [ "$RRR" == "" ] ; then
    FFF=`locate $1`
else
    if [ "$VVV" == "1" ] ; then
        echo "Regex seach, will take more time"
    fi
    FFF=`locate -r -w $1`
fi

if [ "$FFF" == "" ] ; then
 echo "'$1' is not found"
 exit
fi

echo $FFF | xargs stat -c "%Y %s %n" | sort -n -k $SSS | awk \
            '{ printf("%s %s %s %s\n", strftime("%Y:%m:%d %H:%M", $1),\
                         $2, $3, $4);}'

# EOF
