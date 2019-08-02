#!/bin/bash

# This can remain constant
TEMPD=~/build-tmp

# The name of the project
PROJN=pyvserv

TARDIR=$TEMPD/$PROJN

#echo Building pyvserv in \'$TARDIR\'

mkdir -p $TARDIR
cp -a ./* $TARDIR

pushd `pwd` >/dev/null
cd $TARDIR
#echo "target" `pwd`

# Formulate the new package, set modes, clean keys, tests

chmod 0775 DEBIAN
rm -rf keys/*
rm -rf test
rm -f md5sums.txt

find . -type f -exec md5sum {} \; >> md5sums.txt
cp md5sums.txt DEBIAN/md5sums

# Put it into the package
cd ..
rm -f *.deb

dpkg-deb -b pyvserv
popd >/dev/null
mv $TEMPD/pyvserv.deb .
mv $TARDIR/md5sums.txt .
#rm -rf $TARDIR

